import unittest

from analysis.candidates import find_candidates


def vals(abstract):
    return [(c["Raw_Text"], c["Value_Normalized"], c["Column_Candidate"])
            for c in find_candidates(abstract)]


class TestFindCandidates(unittest.TestCase):
    def test_plain_hz(self):
        self.assertEqual(
            vals("tones at 500 Hz were presented"),
            [("500 Hz", "500", "Frequency_Hz")])

    def test_khz_normalized(self):
        self.assertEqual(
            vals("toward 1 kHz sound stimuli"),
            [("1 kHz", "1000", "Frequency_Hz")])

    def test_range(self):
        self.assertEqual(
            vals("modulation rates (8 and 40 Hz)"),
            [("8 and 40 Hz", "8-40", "Frequency_Hz")])
        self.assertEqual(
            vals("frequencies from 250-4000 Hz"),
            [("250-4000 Hz", "250-4000", "Frequency_Hz")])
        self.assertEqual(
            vals("between 0.5 to 4 kHz"),
            [("0.5 to 4 kHz", "500-4000", "Frequency_Hz")])

    def test_db_variants(self):
        self.assertEqual(
            vals("presented at 65 dB SPL"),
            [("65 dB SPL", "65", "Sound_Level_dB")])
        self.assertEqual(
            vals("thresholds at 20 dB HL and noise of 80 dBA"),
            [("20 dB HL", "20", "Sound_Level_dB"),
             ("80 dBA", "80", "Sound_Level_dB")])

    def test_db_per_oct_is_attenuation(self):
        self.assertEqual(
            vals("filtered with a slope of 12 dB/oct"),
            [("12 dB/oct", "12", "Attenuation_dB_oct")])

    def test_bpm(self):
        self.assertEqual(
            vals("singing a pop song 30 bpm"),
            [("30 bpm", "30", "Tempo_BPM")])

    def test_thousands_separator(self):
        self.assertEqual(
            vals("a 1,000 Hz tone"),
            [("1,000 Hz", "1000", "Frequency_Hz")])

    def test_non_acoustic_numbers_ignored(self):
        # Ages, sample sizes, statistics carry no acoustic unit.
        self.assertEqual(
            vals("27 infants aged 3 months (r = -0.497, p = 0.000)"), [])

    def test_order_preserved(self):
        got = vals("first 100 Hz then 60 dB then 2 kHz")
        self.assertEqual([g[1] for g in got], ["100", "60", "2000"])

    def test_snippet_contains_match(self):
        c = find_candidates("x" * 100 + " 500 Hz " + "y" * 100)[0]
        self.assertIn("500 Hz", c["Snippet"])


if __name__ == "__main__":
    unittest.main()
