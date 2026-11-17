"""Deterministic enumeration of numeric candidates in abstracts.

Purpose (division of labour, METHODOLOGY section 3):
- Simple, mechanical extraction is done by CODE so that anyone (e.g. a
  graduate student) can reproduce byte-identical candidate lists from the
  same bibliography file.
- Interpretation -- which candidate is a stimulus frequency, a level, a
  tempo, or none of those -- is NOT done here. That stays with the AI
  extractor and the user's adjudication.

What counts as a candidate: a number (single value or range) written
together with an acoustic unit that maps to an extraction column:
  Hz / kHz / MHz        -> Frequency_Hz (normalized to Hz)
  dB (incl. dBA, dB SPL, dB HL, dB nHL, dB/oct) -> Sound_Level_dB or
                           Attenuation_dB_oct (interpretation decides)
  BPM / bpm             -> Tempo_BPM
Numbers without these units are not candidates here; ages, sample sizes
and statistics are interpretation-free noise for this step.

Output is sorted by (PMID, position in abstract) and carries the raw
matched text plus a context snippet, so every candidate can be traced
back to its exact place in the abstract. A JSON manifest with the
SHA-256 of the input file makes each run verifiable.

Usage:
  python -m analysis.candidates literature/bibliography_all.csv \
      --pmids literature/extraction_batches/output \
      --out literature/extraction_batches/candidates_all.csv \
      --manifest literature/extraction_batches/candidates_all.manifest.json
--pmids accepts CSV files or a directory of CSVs whose PMID column
restricts the scan (e.g. the extraction shells). Omit it to scan all rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path

TOOL_VERSION = "candidates/3"

# A number: 1,000 / 0.5 / .5 / 30 ; a range joins two with -, –, —, or "to".
_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|\.\d+)"
_RANGE_SEP = r"(?:\s*[-–—]\s*|\s+to\s+|\s+and\s+)"
_UNIT = (
    r"(?P<unit>kHz|MHz|Hz|dB\s?/oct|dBA|dB\s?SPL|dB\s?HL|dB\s?nHL|dB|BPM|bpm)"
)
# 単位の直前のハイフン（"1000-Hz" のような形容詞形）も許す。
# v1 はこの形を取りこぼした（2026-11-15 の本抽出で発覚、8件）。
_PATTERN = re.compile(
    rf"(?P<first>{_NUM})(?:{_RANGE_SEP}(?P<second>{_NUM}))?\s*-?\s*{_UNIT}\b"
)
# 複合形 "4000- and 1000-Hz" の先行要素（単位は後続要素が担う）。
# v2 は後続要素しか拾えなかった（同日発覚）。
_PATTERN_COMPOUND = re.compile(
    rf"(?P<first>{_NUM})\s*-\s*(?:and|or)\s+{_NUM}\s*-?\s*{_UNIT}\b"
)

_UNIT_KIND = {
    "Hz": ("Frequency_Hz", 1.0),
    "kHz": ("Frequency_Hz", 1_000.0),
    "MHz": ("Frequency_Hz", 1_000_000.0),
    "BPM": ("Tempo_BPM", 1.0),
    "bpm": ("Tempo_BPM", 1.0),
}


def _unit_info(unit_raw: str) -> tuple[str, float]:
    u = re.sub(r"\s+", " ", unit_raw).strip()
    if u in _UNIT_KIND:
        return _UNIT_KIND[u]
    if u.replace(" ", "") == "dB/oct":
        return ("Attenuation_dB_oct", 1.0)
    if u.startswith("dB"):
        return ("Sound_Level_dB", 1.0)
    raise ValueError(f"unknown unit: {unit_raw!r}")


def _to_float(text: str) -> float:
    return float(text.replace(",", ""))


def _fmt(value: float) -> str:
    return str(int(value)) if value == int(value) else str(value)


def find_candidates(abstract: str) -> list[dict]:
    """All unit-bearing numeric mentions, in order of appearance."""
    abstract = abstract or ""
    out = []
    for m in _PATTERN.finditer(abstract):
        column, factor = _unit_info(m.group("unit"))
        first = _to_float(m.group("first")) * factor
        if m.group("second"):
            second = _to_float(m.group("second")) * factor
            value = f"{_fmt(first)}-{_fmt(second)}"
        else:
            value = _fmt(first)
        start = max(0, m.start() - 60)
        end = min(len(abstract), m.end() + 60)
        out.append(
            {
                "Raw_Text": m.group(0),
                "Value_Normalized": value,
                "Column_Candidate": column,
                "Position": m.start(),
                "Snippet": abstract[start:end].replace("\n", " "),
            }
        )
    for m in _PATTERN_COMPOUND.finditer(abstract):
        column, factor = _unit_info(m.group("unit"))
        value = _fmt(_to_float(m.group("first")) * factor)
        start = max(0, m.start() - 60)
        end = min(len(abstract), m.end() + 60)
        out.append(
            {
                "Raw_Text": m.group(0),
                "Value_Normalized": value,
                "Column_Candidate": column,
                "Position": m.start(),
                "Snippet": abstract[start:end].replace("\n", " "),
            }
        )
    out.sort(key=lambda c: c["Position"])
    return out


def load_pmids(paths: list[str]) -> set[str] | None:
    pmids: set[str] = set()
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        files.extend(sorted(path.glob("*.csv")) if path.is_dir() else [path])
    if not files:
        return None
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("PMID"):
                    pmids.add(row["PMID"])
    return pmids


def run(bib_path: str, pmid_paths: list[str]) -> tuple[list[dict], dict]:
    raw = Path(bib_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    wanted = load_pmids(pmid_paths) if pmid_paths else None
    rows: list[dict] = []
    scanned = 0
    with open(bib_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pmid = row.get("PMID", "")
            if wanted is not None and pmid not in wanted:
                continue
            scanned += 1
            for cand in find_candidates(row.get("Abstract", "")):
                rows.append({"PMID": pmid, **cand})
    rows.sort(key=lambda r: (int(r["PMID"]), r["Position"]))
    manifest = {
        "tool": TOOL_VERSION,
        "input_file": bib_path,
        "input_sha256": digest,
        "pmid_filter_files": pmid_paths,
        "abstracts_scanned": scanned,
        "candidates_found": len(rows),
        "pmids_with_candidates": len({r["PMID"] for r in rows}),
    }
    return rows, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bibliography")
    ap.add_argument("--pmids", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest")
    args = ap.parse_args(argv)
    rows, manifest = run(args.bibliography, args.pmids)
    fields = ["PMID", "Raw_Text", "Value_Normalized", "Column_Candidate", "Position", "Snippet"]
    tmp_out = args.out + ".tmp"
    with open(tmp_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp_out, args.out)  # 原子的に置き換える（Issue #12）
    if args.manifest:
        mp = Path(args.manifest)
        mtmp = mp.with_suffix(mp.suffix + ".tmp")
        mtmp.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        mtmp.replace(mp)
    print(
        f"scanned {manifest['abstracts_scanned']} abstracts: "
        f"{manifest['candidates_found']} candidates in "
        f"{manifest['pmids_with_candidates']} papers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
