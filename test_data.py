"""literature/ のデータ整合性テスト。実行: python -m unittest test_stats test_data -v
母集団の件数は METHODOLOGY.md のクエリ v1 実測値（2026-11-12）と一致すること。
クエリを変更したら METHODOLOGY とこのテストを一緒に更新する。"""
import csv
import os
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
LIT = os.path.join(ROOT, "literature")

EXPECTED_COUNTS = {
    "pediatrics": 17,
    "early_human_development": 40,
    "infant_behavior_development": 21,
    "jasa": 258,
    "hearing_research": 196,
    "journal_of_music_therapy": 31,
}
EXPECTED_TOTAL = 563
EXPECTED_NO_ABSTRACT = 15

TEMPLATE_COLUMNS = [
    "PMID", "Title", "Journal", "Stratum", "Target_Age", "Stimulus_Type",
    "Frequency_Hz", "Attenuation_dB_oct", "Sound_Level_dB", "Tempo_BPM",
    "Outcome", "Evidence_Quote", "Decision", "Exclude_Reason",
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class BibliographyTests(unittest.TestCase):
    def test_per_journal_counts_match_methodology(self):
        for key, expected in EXPECTED_COUNTS.items():
            rows = read_csv(os.path.join(LIT, f"bibliography_{key}.csv"))
            self.assertEqual(len(rows), expected, key)

    def test_pmids_unique_within_journal(self):
        for key in EXPECTED_COUNTS:
            rows = read_csv(os.path.join(LIT, f"bibliography_{key}.csv"))
            pmids = [r["PMID"] for r in rows]
            self.assertEqual(len(pmids), len(set(pmids)), key)

    def test_all_csv_is_union_of_journals(self):
        all_rows = read_csv(os.path.join(LIT, "bibliography_all.csv"))
        self.assertEqual(len(all_rows), EXPECTED_TOTAL)
        union = set()
        for key in EXPECTED_COUNTS:
            union |= {r["PMID"] for r in read_csv(os.path.join(LIT, f"bibliography_{key}.csv"))}
        self.assertEqual({r["PMID"] for r in all_rows}, union)

    def test_required_fields_and_abstract_flags(self):
        rows = read_csv(os.path.join(LIT, "bibliography_all.csv"))
        for r in rows:
            self.assertTrue(r["PMID"])
            self.assertTrue(r["Title"])
            self.assertIn(r["Has_Abstract"], ("yes", "no"))
        no_abs = sum(1 for r in rows if r["Has_Abstract"] == "no")
        self.assertEqual(no_abs, EXPECTED_NO_ABSTRACT)


class TemplateAndScreeningTests(unittest.TestCase):
    def test_extraction_template_columns(self):
        with open(os.path.join(LIT, "extraction_sheet_template.csv"),
                  newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        self.assertEqual(header, TEMPLATE_COLUMNS)

    def test_firstpass_screening_shape(self):
        rows = read_csv(os.path.join(LIT, "screening_firstpass.csv"))
        self.assertEqual(len(rows), EXPECTED_TOTAL)
        strata = {r["Stratum_firstpass"] for r in rows}
        self.assertTrue(strata <= {"A", "B", "C", "REVIEW"}, strata)


if __name__ == "__main__":
    unittest.main()
