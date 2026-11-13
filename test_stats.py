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


class ParametricSupplementaryTests(unittest.TestCase):
    """補足のパラメトリック統計（2026-11-13 追加）。

    期待値は手計算と t 分布表の公知値で照合した固定値。
    位置づけは補足であり、設計値の決定には使わない（METHODOLOGY §4）。
    """

    def test_se(self):
        # [1..5]: SD=√2.5, SE = SD/√5 = √0.5
        self.assertAlmostEqual(stats.se_mean([1, 2, 3, 4, 5]),
                               0.7071067811865476)

    def test_t_critical_matches_table(self):
        # t_{0.975, df} の公知値（t 分布表）
        self.assertAlmostEqual(stats.t_critical_975(1), 12.7062047362, places=6)
        self.assertAlmostEqual(stats.t_critical_975(4), 2.7764451052, places=6)
        self.assertAlmostEqual(stats.t_critical_975(9), 2.2621571628, places=6)
        self.assertAlmostEqual(stats.t_critical_975(30), 2.0422724563, places=6)

    def test_mean_ci_95(self):
        # [1..5]: 平均3, SE=√0.5, t(df=4)=2.7764451052 → 幅 ±1.9632431615
        low, high = stats.mean_ci_95([1, 2, 3, 4, 5])
        self.assertAlmostEqual(low, 1.0367568385, places=6)
        self.assertAlmostEqual(high, 4.9632431615, places=6)
        s = stats.summarize([1, 2, 3, 4, 5])
        self.assertAlmostEqual(s["mean_ci_95"][0], low)
        self.assertAlmostEqual(s["mean_ci_95"][1], high)

    def test_geometric_mean(self):
        # 等比数列では幾何平均 = 中央の項。[1,2,4,8] は (1·2·4·8)^(1/4)=2√2
        self.assertAlmostEqual(stats.geometric_mean([1, 2, 4, 8]),
                               2.8284271247461903)
        self.assertAlmostEqual(stats.geometric_mean([100, 1000]),
                               316.22776601683796)
        with self.assertRaises(ValueError):
            stats.geometric_mean([1, 0, 2])
        # summarize では 0 以下を含むと None（落とさない）
        self.assertIsNone(stats.summarize([0, 1, 2])["geometric_mean"])

    def test_parametric_is_supplementary_under_outlier(self):
        # 外れ値で平均と CI は大きく動くが、主役の中央値は動かない。
        # 補足に留める根拠そのものの確認。
        s = stats.summarize([10, 11, 12, 13, 100])
        self.assertAlmostEqual(s["median"], 12.0)
        # 平均の CI 幅は外れ値で 98 超まで広がる（IQR は 2 のまま）
        self.assertGreater(s["mean_ci_95"][1] - s["mean_ci_95"][0], 50)
        self.assertAlmostEqual(s["iqr"], 2.0)


class SnQnTests(unittest.TestCase):
    """Sn / Qn 推定量（補足のロバスト尺度、2026-11-13 追加）。

    期待値は順序統計量を手で数えた固定値:
    - [1..5]: Sn の raw lowmed = 1 → 1.1926 × c_5(1.351)
              Qn のペア差ソート済み [1,1,1,1,2,2,2,3,3,4] の k=3 番目 = 1
              → 2.219144 × d_5(0.844)
    - [1,2,3]: Sn raw = 1 → 1.1926 × c_3(1.851)、Qn raw = 1 → 2.219144 × d_3(0.994)
    定数 2.219144 は原論文の誤植 2.2219 ではない正値を使う。
    """

    def test_fixed_values(self):
        self.assertAlmostEqual(stats.sn_estimator([1, 2, 3, 4, 5]),
                               1.1926 * 1.351)
        self.assertAlmostEqual(stats.qn_estimator([1, 2, 3, 4, 5]),
                               2.21914446598508 * 0.844)
        self.assertAlmostEqual(stats.sn_estimator([1, 2, 3]),
                               1.1926 * 1.851)
        self.assertAlmostEqual(stats.qn_estimator([1, 2, 3]),
                               2.21914446598508 * 0.994)

    def test_scale_equivariance_and_shift_invariance(self):
        x = [3, 1, 4, 1, 5, 9, 2, 6]
        self.assertAlmostEqual(stats.sn_estimator([2 * v for v in x]),
                               2 * stats.sn_estimator(x))
        self.assertAlmostEqual(stats.qn_estimator([v + 100 for v in x]),
                               stats.qn_estimator(x))

    def test_small_n(self):
        self.assertEqual(stats.sn_estimator([7]), 0.0)
        self.assertIsNone(stats.qn_estimator([7]))  # ペアが無い
        # n=2: raw はどちらも |a-b| そのもの
        self.assertAlmostEqual(stats.sn_estimator([0, 10]), 1.1926 * 0.743 * 10)
        self.assertAlmostEqual(stats.qn_estimator([0, 10]),
                               2.21914446598508 * 0.399 * 10)

    def test_in_summarize(self):
        s = stats.summarize([1, 2, 3, 4, 5])
        self.assertAlmostEqual(s["sn"], 1.1926 * 1.351)
        self.assertAlmostEqual(s["qn"], 2.21914446598508 * 0.844)


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
