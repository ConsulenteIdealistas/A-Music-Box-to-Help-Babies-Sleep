"""analysis/validate_extraction.py の自動テスト。
実行: python -m unittest test_validate_extraction -v
正常系1件と、各 ERROR/WARN コードに対応する異常系を固定する。"""
import unittest

from analysis import validate_extraction as ve

ABSTRACTS = {
    "111": "Stimuli were tones of 500 Hz presented at 60 dB SPL to infants aged 3 months.",
    "222": "The cutoff was 0.5 kHz with attenuation of 12 dB per octave in fetal sheep.",
    "333": "",  # 抄録なし
    "444": "Heart rate was 140 beats per minute during exposure to 115 dB noise.",
}

BASE = {
    "PMID": "111", "Title": "t", "Journal": "j", "Stratum": "A",
    "Target_Age": "", "Stimulus_Type": "", "Frequency_Hz": "",
    "Attenuation_dB_oct": "", "Sound_Level_dB": "", "Tempo_BPM": "",
    "Outcome": "", "Evidence_Quote": "", "Decision": "Include",
    "Exclude_Reason": "",
}


def row(**kw):
    r = dict(BASE)
    r.update(kw)
    return r


def codes(issues):
    return {(i.level, i.code) for i in issues}


class ValidateTests(unittest.TestCase):
    def test_good_row_passes_clean(self):
        r = row(Frequency_Hz="500", Sound_Level_dB="60",
                Evidence_Quote="tones of 500 Hz presented at 60 dB SPL")
        self.assertEqual(ve.validate_rows([r], ABSTRACTS), [])

    def test_quote_not_verbatim(self):
        r = row(Frequency_Hz="500",
                Evidence_Quote="tones of 500 Hz presented at 61 dB SPL")
        self.assertIn(("ERROR", "quote_not_verbatim"),
                      codes(ve.validate_rows([r], ABSTRACTS)))

    def test_number_not_in_quote(self):
        r = row(Frequency_Hz="250",
                Evidence_Quote="tones of 500 Hz presented at 60 dB SPL")
        self.assertIn(("ERROR", "number_not_in_quote"),
                      codes(ve.validate_rows([r], ABSTRACTS)))

    def test_numeric_without_quote(self):
        r = row(Frequency_Hz="500")
        self.assertIn(("ERROR", "numeric_without_quote"),
                      codes(ve.validate_rows([r], ABSTRACTS)))

    def test_khz_conversion_warns_but_passes(self):
        r = row(PMID="222", Stratum="C", Frequency_Hz="500",
                Attenuation_dB_oct="12",
                Evidence_Quote="The cutoff was 0.5 kHz with attenuation of 12 dB per octave")
        got = codes(ve.validate_rows([r], ABSTRACTS))
        self.assertIn(("WARN", "unit_converted"), got)
        self.assertNotIn(("ERROR", "number_not_in_quote"), got)

    def test_unknown_pmid_and_duplicate(self):
        rows = [row(PMID="999"), row(PMID="111"), row(PMID="111")]
        got = codes(ve.validate_rows(rows, ABSTRACTS))
        self.assertIn(("ERROR", "unknown_pmid"), got)
        self.assertIn(("ERROR", "duplicate_pmid"), got)

    def test_no_abstract_warns(self):
        r = row(PMID="333", Frequency_Hz="100",
                Evidence_Quote="some quote that cannot be checked")
        self.assertIn(("WARN", "no_abstract"),
                      codes(ve.validate_rows([r], ABSTRACTS)))

    def test_exclude_without_reason(self):
        r = row(Decision="Exclude")
        self.assertIn(("ERROR", "exclude_no_reason"),
                      codes(ve.validate_rows([r], ABSTRACTS)))

    def test_implausible_warns_not_errors(self):
        r = row(PMID="444", Sound_Level_dB="115", Tempo_BPM="140",
                Evidence_Quote="Heart rate was 140 beats per minute during exposure to 115 dB noise.")
        got = ve.validate_rows([r], ABSTRACTS)
        self.assertEqual([i for i in got if i.level == "ERROR"], [])
        r2 = row(Frequency_Hz="999999",
                 Evidence_Quote="tones of 500 Hz presented at 60 dB SPL")
        got2 = codes(ve.validate_rows([r2], ABSTRACTS))
        self.assertIn(("WARN", "implausible_value"), got2)

    def test_range_cell_numbers_all_checked(self):
        # "200-500" のような範囲表記は両端とも引用に必要
        r = row(Frequency_Hz="200-500",
                Evidence_Quote="tones of 500 Hz presented at 60 dB SPL")
        self.assertIn(("ERROR", "number_not_in_quote"),
                      codes(ve.validate_rows([r], ABSTRACTS)))


if __name__ == "__main__":
    unittest.main()
