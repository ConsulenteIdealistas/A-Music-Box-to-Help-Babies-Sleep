import unittest

from analysis.apply_vocab import normalize_value

VOCAB = {
    ("Stimulus_Type", "click"): "click",
    ("Stimulus_Type", "clicks"): "click",
    ("Stimulus_Type", "music"): "music_general",
    ("Outcome", "heart rate"): "heart_rate",
}


class TestNormalizeValue(unittest.TestCase):
    def test_maps_and_dedupes(self):
        self.assertEqual(
            normalize_value("click; clicks", "Stimulus_Type", VOCAB),
            ("click", []))

    def test_multi_value(self):
        self.assertEqual(
            normalize_value("click; music", "Stimulus_Type", VOCAB),
            ("click; music_general", []))

    def test_na_passthrough(self):
        self.assertEqual(normalize_value("N/A", "Outcome", VOCAB), ("N/A", []))
        self.assertEqual(normalize_value("", "Outcome", VOCAB), ("", []))

    def test_missing_reported(self):
        canon, missing = normalize_value("unknown thing", "Outcome", VOCAB)
        self.assertEqual(missing, ["unknown thing"])


if __name__ == "__main__":
    unittest.main()
