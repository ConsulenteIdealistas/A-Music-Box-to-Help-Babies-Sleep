"""analysis/triple_check.py の自動テスト。
実行: python -m unittest test_triple_check -v
対象選定（A層数値・WARN・サンプル）と突き合わせの固定ケース。"""
import unittest

from analysis import triple_check as tc

ABSTRACTS = {
    "1": "Tones of 500 Hz at 60 dB were presented.",
    "2": "Tones of 500 Hz at 60 dB were presented.",
    "3": "Tones of 500 Hz at 60 dB were presented.",
    "4": "Tones of 500 Hz at 60 dB were presented.",
    "5": "",  # 抄録なし → no_abstract WARN
}

BASE = {
    "Title": "t", "Journal": "j", "Target_Age": "", "Stimulus_Type": "",
    "Frequency_Hz": "", "Attenuation_dB_oct": "", "Sound_Level_dB": "",
    "Tempo_BPM": "", "Outcome": "", "Evidence_Quote": "",
    "Decision": "Include", "Exclude_Reason": "",
}
QUOTE = "Tones of 500 Hz at 60 dB were presented."


def row(pmid, stratum, **kw):
    r = dict(BASE, PMID=pmid, Stratum=stratum)
    r.update(kw)
    return r


class SelectTests(unittest.TestCase):
    def test_a_numeric_always_selected(self):
        rows = [row("1", "A", Frequency_Hz="500", Evidence_Quote=QUOTE)]
        got = tc.select_targets(rows, ABSTRACTS)
        self.assertEqual([(r["PMID"], why) for r, why in got],
                         [("1", "A_numeric")])

    def test_no_numeric_never_selected(self):
        rows = [row("1", "A")]
        self.assertEqual(tc.select_targets(rows, ABSTRACTS), [])

    def test_warn_row_selected(self):
        rows = [row("5", "C", Frequency_Hz="500", Evidence_Quote="anything")]
        got = tc.select_targets(rows, ABSTRACTS)
        self.assertEqual(len(got), 1)
        self.assertTrue(got[0][1].startswith("warn:"))

    def test_sample_is_deterministic_and_capped(self):
        rows = [row(str(100 + i), "B", Frequency_Hz="500",
                    Evidence_Quote=QUOTE) for i in range(10)]
        abstracts = {str(100 + i): ABSTRACTS["1"] for i in range(10)}
        a = tc.select_targets(rows, abstracts)
        b = tc.select_targets(rows, abstracts)
        self.assertEqual([r["PMID"] for r, _ in a], [r["PMID"] for r, _ in b])
        self.assertTrue(all(why == "sample" for _, why in a))
        self.assertEqual(tc.sample_size(10), 10)   # 母数が小さい時は全件
        self.assertEqual(tc.sample_size(500), 60)  # rule of three で 60


class CompareTests(unittest.TestCase):
    def test_identical_no_diffs(self):
        rows = [row("1", "A", Frequency_Hz="500", Evidence_Quote=QUOTE)]
        self.assertEqual(tc.compare(rows, [dict(r) for r in rows]), [])

    def test_numeric_mismatch_detected(self):
        a = [row("1", "A", Frequency_Hz="500")]
        b = [row("1", "A", Frequency_Hz="250")]
        diffs = tc.compare(a, b)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0][1], "Frequency_Hz")

    def test_missing_row_detected(self):
        a = [row("1", "A", Frequency_Hz="500")]
        self.assertEqual(len(tc.compare(a, [])), 1)

    def test_number_format_variants_match(self):
        a = [row("1", "A", Frequency_Hz="500")]
        b = [row("1", "A", Frequency_Hz="500.0")]
        self.assertEqual(tc.compare(a, b), [])


if __name__ == "__main__":
    unittest.main()
