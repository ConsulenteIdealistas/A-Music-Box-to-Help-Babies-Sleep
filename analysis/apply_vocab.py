"""Apply the controlled vocabulary to the qualitative extraction.

Non-destructive by design: literature/qualitative_extraction.csv keeps the
raw free-text values exactly as extracted. This tool joins the mapping in
literature/qualitative_vocab.csv (Column, Raw_Value -> Canonical_Value)
and writes a normalized VIEW with two added columns,
Stimulus_Canonical and Outcome_Canonical.

Completeness is enforced: any token without a mapping row aborts the run
with the unmapped tokens listed, so the vocabulary can never silently
drift out of sync with the data.

Usage:
  python -m analysis.apply_vocab \
      literature/qualitative_extraction.csv literature/qualitative_vocab.csv \
      --out literature/qualitative_extraction_normalized.csv
"""

from __future__ import annotations

import argparse
import csv
import sys

COLUMN_PAIRS = [("Stimulus_Type", "Stimulus_Canonical"),
                ("Outcome", "Outcome_Canonical")]


def load_vocab(path: str) -> dict[tuple[str, str], str]:
    vocab: dict[tuple[str, str], str] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["Column"], row["Raw_Value"])
            if key in vocab and vocab[key] != row["Canonical_Value"]:
                raise ValueError(f"conflicting mapping for {key}")
            vocab[key] = row["Canonical_Value"]
    return vocab


def normalize_value(value: str, column: str, vocab: dict) -> tuple[str, list[str]]:
    if not value or value == "N/A":
        return value, []
    out: list[str] = []
    missing: list[str] = []
    for token in value.split(";"):
        token = token.strip()
        if not token:
            continue
        canon = vocab.get((column, token))
        if canon is None:
            missing.append(token)
        elif canon not in out:
            out.append(canon)
    return "; ".join(out), missing


def run(extraction_path: str, vocab_path: str, out_path: str) -> dict:
    vocab = load_vocab(vocab_path)
    with open(extraction_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    missing_all: set[str] = set()
    for row in rows:
        for src, dst in COLUMN_PAIRS:
            canon, missing = normalize_value(row.get(src, ""), src, vocab)
            row[dst] = canon
            missing_all.update(f"{src}: {m}" for m in missing)
    if missing_all:
        raise ValueError("unmapped tokens: " + ", ".join(sorted(missing_all)))
    for _, dst in COLUMN_PAIRS:
        if dst not in fields:
            fields.append(dst)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return {"rows": len(rows), "vocab_entries": len(vocab)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("extraction")
    ap.add_argument("vocab")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        stats = run(args.extraction, args.vocab, args.out)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"normalized {stats['rows']} rows using {stats['vocab_entries']} mappings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
