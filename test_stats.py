"""analysis/stats.py の自動テスト。実行: python -m unittest test_stats test_data -v
期待値は手計算（および独立計算）で確認した固定値を用いる。"""
import unittest

from analysis import stats


class SummarizeTests(unittest.TestCase):
    def test_odd_n(self):
        s = stats.summarize([1, 2, 3, 4, 5])
        self.assertEqual(s["n"], 5)
        self.assertAlmostEqual(s["mean"], 3.0)
        self.assertAlmostEqual(s["sd"], 1.5811388300841898)
        self.assertAlmostEqual(s["median"], 3.0)
        self.assertAlmostEqual(s["q1"], 2.0)
        self.assertAlmostEqual(s["q3"], 4.0)
        self.assertAlmostEqual(s["iqr"], 2.0)
        self.assertAlmostEqual(s["mad"], 1.0)
        self.assertAlmostEqual(s["robust_sd"], 1.4826)
        self.assertEqual(s["min"], 1.0)
        self.assertEqual(s["max"], 5.0)

    def test_even_n(self):
        s = stats.summarize([1, 2, 3, 4])
        self.assertAlmostEqual(s["mean"], 2.5)
        self.assertAlmostEqual(s["sd"], 1.2909944487358056)
        self.assertAlmostEqual(s["median"], 2.5)
        self.assertAlmostEqual(s["q1"], 1.75)
        self.assertAlmostEqual(s["q3"], 3.25)
        self.assertAlmostEqual(s["robust_sd"], 1.4826)

    def test_outlier_moves_mean_not_median(self):
        # §4 の前提確認: 外れ値は平均と通常SD を大きく動かし、
        # 中央値とロバストSD はほとんど動かない。
        s = stats.summarize([10, 11, 12, 13, 100])
        self.assertAlmostEqual(s["mean"], 29.2)
        self.assertAlmostEqual(s["sd"], 39.594191493197584)
        self.assertAlmostEqual(s["median"], 12.0)
        self.assertAlmostEqual(s["robust_sd"], 1.4826)
        self.assertGreater(s["sd_ratio"], 10)

    def test_unsorted_input_is_accepted(self):
        self.assertEqual(stats.summarize([5, 1, 4, 2, 3]),
                         stats.summarize([1, 2, 3, 4, 5]))


class EdgeCaseTests(unittest.TestCase):
    def test_single_value(self):
        s = stats.summarize([42])
        self.assertEqual(s["n"], 1)
        self.assertIsNone(s["sd"])  # ddof=1 では定義できない
        self.assertEqual(s["median"], 42.0)
        self.assertEqual(s["q1"], 42.0)
        self.assertEqual(s["q3"], 42.0)
        self.assertEqual(s["robust_sd"], 0.0)
        self.assertIsNone(s["sd_ratio"])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            stats.summarize([])

    def test_percentile_bounds(self):
        self.assertEqual(stats.percentile([1, 2, 3], 0.0), 1.0)
        self.assertEqual(stats.percentile([1, 2, 3], 1.0), 3.0)
        with self.assertRaises(ValueError):
            stats.percentile([1, 2, 3], 1.5)


if __name__ == "__main__":
    unittest.main()
