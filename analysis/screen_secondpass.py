#!/usr/bin/env python3
"""Second-pass screening assist for the lullaby literature (563 papers).

Non-destructive: reads literature/screening_firstpass.csv and writes
literature/screening_secondpass.csv with NEW columns only. First-pass
columns are copied verbatim so any later pass can be compared against them.

NOT final screening. Fixes known first-pass weaknesses:
  1. singular-only word-boundary keywords missed plurals
     (fetuses, infants, newborns, babies, neonates);
  2. "animal + under-2 co-mention" REVIEW bucket was mostly animal studies
     whose under-2 token modifies the animal (fetal sheep, neonatal rat);
  3. numeric subject ages were not used at all.
Deterministic rules (title + abstract). Ambiguous rows stay REVIEW, and
rows the second pass cannot positively reclassify keep their first-pass
stratum (no demotion without positive contrary evidence).

Usage: python3 analysis/screen_secondpass.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "literature" / "screening_firstpass.csv"
DST = ROOT / "literature" / "screening_secondpass.csv"
SUMMARY = ROOT / "literature" / "screening_secondpass_summary.md"

UNDER2 = [
    r"\bfetal\b", r"\bfetus(?:es)?\b", r"\bnewborns?\b", r"\bneonat\w*\b",
    r"\binfants?\b", r"\binfancy\b", r"\bbab(?:y|ies)\b", r"\bpreterm\b",
    r"\bpremature\b", r"\bNICU\b", r"\bin utero\b",
]
HUMAN_UNDER2 = [
    r"\bhuman infants?\b", r"\binfant (?:participants|subjects|listeners|children|babies)\b",
    r"\bnewborn (?:infants|babies|humans|children)\b",
    r"\b\d+ (?:infants|newborns|babies)\b", r"\bpreterm infants?\b",
    r"\bpremature infants?\b",
]
OLDER = [r"\badults?\b", r"\badolescents?\b", r"\bteenagers?\b"]
ANIMAL_SUBJECT = [
    r"\brats?\b", r"\bmice\b", r"\bmouse\b", r"\brabbits?\b", r"\bsheep\b",
    r"\bpigs?\b", r"\bmonkeys?\b", r"\brodents?\b", r"\bcanine\b", r"\bfeline\b",
    r"\bgerbils?\b", r"\bkittens?\b", r"\bcats\b", r"\bguinea pigs?\b",
]
DIAG_HINTS = [
    r"\bcochlear implant", r"\bhearing loss\b", r"\bdiagnos(?:is|e|ed)\b",
]

AGED_MONTHS = re.compile(r"\baged?\s+([\d,\s]+(?:and\s+[\d,\s]+)?)\s*months\b", re.I)
MONTH_OLD = re.compile(r"\b(\d+)\s*(?:-| )months?[- ]old\b", re.I)
MONTHS_OF_AGE = re.compile(r"\b(\d+)\s+months?\s+of age\b", re.I)
BETWEEN_MONTHS = re.compile(r"\bbetween\s+(\d+)\s+and\s+(\d+)\s+months\b", re.I)
AGE_YEARS = re.compile(r"\bages?\s*(?:at\s+)?(\d+(?:\.\d+)?)\s+years\b", re.I)
YEAR_OLD = re.compile(r"\b(\d+(?:\.\d+)?)[ -]years?[- ]old\b", re.I)
BIRTH_SPAN = re.compile(r"\b(?:from\s+)?birth\s+to\s+\d+\s+years\b", re.I)


def hits(patterns, text):
    return any(re.search(p, text, re.I) for p in patterns)


def numeric_age(text):
    """Return 'under2', 'older', 'mixed' or None from explicit subject ages."""
    vals_m, vals_y = [], []
    for m in AGED_MONTHS.findall(text):
        vals_m += [int(x) for x in re.findall(r"\d+", m)]
    vals_m += [int(x) for x in MONTH_OLD.findall(text)]
    vals_m += [int(x) for x in MONTHS_OF_AGE.findall(text)]
    for lo, hi in BETWEEN_MONTHS.findall(text):
        vals_m += [int(lo), int(hi)]
    vals_y += [float(x) for x in AGE_YEARS.findall(text)]
    vals_y += [float(x) for x in YEAR_OLD.findall(text)]
    under2 = any(v < 24 for v in vals_m) or any(v < 2 for v in vals_y)
    older = (vals_m and all(v >= 24 for v in vals_m)) or (
        vals_y and all(v >= 2 for v in vals_y))
    if under2 and older:
        return "mixed"
    if under2:
        return "under2"
    if older:
        return "older"
    if BIRTH_SPAN.search(text):
        return "mixed"
    return None


# Abstracts read by hand during second-pass QA (2026-11-12). Each override
# records the stratum a deterministic rule got wrong, with the reason.
MANUAL_OVERRIDES = {
    "21110530": ("A", "manual_abstract_infants_subject_sheep_is_example"),
    "8819861": ("REVIEW", "manual_abstract_mixed_evidence_review"),
    "25499127": ("REVIEW", "manual_abstract_historical_review_one_animal_experiment"),
    "9165342": ("A", "manual_abstract_specimens_include_0_to_1_year"),
    "36995776": ("A", "manual_abstract_review_children_birth_to_5y"),
    "1880297": ("A", "manual_abstract_humans_29w_conceptional_to_49y"),
}


def classify(title, abstract, firstpass, pmid=""):
    if pmid in MANUAL_OVERRIDES:
        stratum, reason = MANUAL_OVERRIDES[pmid]
        return stratum, reason, hits(DIAG_HINTS, f"{title} {abstract}")
    text = f"{title} {abstract}"
    under2 = hits(UNDER2, text)
    human_under2 = hits(HUMAN_UNDER2, text)
    animal = hits(ANIMAL_SUBJECT, text)
    older_word = hits(OLDER, text)
    age = numeric_age(text)
    diag = hits(DIAG_HINTS, text)

    if human_under2:
        return "A", "human_under2_subject", diag
    if animal:
        # under-2 token here modifies the animal (fetal sheep, neonatal rat)
        return "C", "animal_subject", diag
    if under2:
        return "A", "under2_subject_plural_fixed", diag
    if age == "under2":
        return "A", "under2_numeric_age", diag
    if age == "mixed":
        return "A", "mixed_age_span_includes_under2", diag
    if age == "older":
        return "B", "older_numeric_age", diag
    if older_word:
        return "B", "older_subject_only", diag
    if firstpass in ("A", "B", "C"):
        return firstpass, "keep_firstpass_no_contrary_evidence", diag
    return "REVIEW", "no_age_evidence", diag


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    fields = list(rows[0].keys()) + [
        "Stratum_secondpass", "Stratum_reason_secondpass",
        "Diagnosis_only_possible_secondpass", "Decision_secondpass",
    ]
    out = []
    for r in rows:
        stratum, reason, diag = classify(r["Title"], r["Abstract"] or "",
                                         r["Stratum_firstpass"], r["PMID"])
        decision = "Manual_review" if stratum == "REVIEW" else "Include_for_review"
        if diag and stratum != "REVIEW":
            decision = "Include_for_review_diag_flag"
        out.append({**r,
                    "Stratum_secondpass": stratum,
                    "Stratum_reason_secondpass": reason,
                    "Diagnosis_only_possible_secondpass": str(bool(diag)).lower(),
                    "Decision_secondpass": decision})
    _dst_tmp = DST.with_suffix(".csv.tmp")
    with open(_dst_tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    _dst_tmp.replace(DST)  # 原子的に置き換える（Issue #12）

    from collections import Counter
    c2, c1 = Counter(r["Stratum_secondpass"] for r in out), Counter(r["Stratum_firstpass"] for r in out)
    moved = [r for r in out if r["Stratum_firstpass"] != r["Stratum_secondpass"]]
    cm = Counter((r["Stratum_firstpass"], r["Stratum_secondpass"]) for r in moved)
    lines = ["# Screening second-pass (deterministic assist, NOT final screening)", "",
             f"Total N={len(out)}. First-pass columns copied verbatim; new columns only.", "",
             "## By stratum (first pass -> second pass)"]
    for k in ("A", "B", "C", "REVIEW"):
        lines.append(f"- {k}: {c1.get(k,0)} -> {c2.get(k,0)}")
    lines += ["", "## Moves (first pass -> second pass)", ""]
    for (a, b), n in sorted(cm.items()):
        lines.append(f"- {a} -> {b}: {n}")
    lines += ["", "## Rules changed vs first pass", "",
              "- Plural-aware under-2 keywords (fetuses/infants/newborns/babies/neonates/neonatal).",
              "- Explicit human under-2 subjects -> A even when animals also appear; otherwise animal subjects -> C (fetal sheep / neonatal rat tokens modify the animal).",
              "- Numeric subject ages only (aged X months, X-month-old, X months of age, between X and Y months, age X years): <24mo/<2y -> A, mixed span -> A, >=24mo/>=2y -> B.",
              "- Adult/adolescent/teenager subjects with no under-2 evidence -> B.",
              "- No demotion without positive evidence: unreclassified A/B/C keep first-pass stratum.",
              "- Diagnosis-only is only flagged, never excluded here; exclusion needs a human abstract read per METHODOLOGY.md.",
              "- REVIEW remains Manual_review. Extraction still requires an explicit Evidence_Quote, N/A otherwise.",
              "",
              "## Manual abstract reads (QA overrides)", "",
              "Six abstracts were read in full and override the rules above (PMID: stratum): "
              + ", ".join(f"{p}={s}" for p, (s, _) in MANUAL_OVERRIDES.items()) + ". "
              "Reasons are recorded per row in Stratum_reason_secondpass."]
    _sum_tmp = SUMMARY.with_suffix(".md.tmp")
    _sum_tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _sum_tmp.replace(SUMMARY)  # 原子的に置き換える（Issue #12）
    print(f"wrote {DST} ({len(out)} rows); moved={len(moved)}")
    print(c2)


if __name__ == "__main__":
    main()
