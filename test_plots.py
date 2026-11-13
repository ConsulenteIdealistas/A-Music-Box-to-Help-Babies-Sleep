"""analysis/plots.py の自動テスト。実行: python -m unittest test_plots -v
SVG が妥当な XML であること、点の数、対数スケールの写像を固定値で確認する。"""
import unittest
import xml.etree.ElementTree as ET

from analysis import plots

NS = "{http://www.w3.org/2000/svg}"


def _circles(svg):
    root = ET.fromstring(svg)
    return root.findall(f"{NS}circle")


class DotPlotTests(unittest.TestCase):
    def test_structure_and_counts(self):
        svg = plots.dot_plot_svg(
            [("A", [100, 200, 500, 1000]), ("C", [50, 5000])],
            "Frequency_Hz by Stratum", "Frequency_Hz", log_x=True)
        self.assertEqual(len(_circles(svg)), 6)
        self.assertIn("(log scale)", svg)
        for tick in ("100", "1000", "10000"):
            self.assertIn(f">{tick}<", svg)
        self.assertIn("A (n=4)", svg)
        self.assertIn("C (n=2)", svg)

    def test_deterministic(self):
        args = ([("A", [10, 20, 30])], "t", "x")
        self.assertEqual(plots.dot_plot_svg(*args), plots.dot_plot_svg(*args))


class ScatterTests(unittest.TestCase):
    def test_structure(self):
        svg = plots.scatter_svg([(100, 40), (500, 60), (1000, 80)],
                                "dB vs Hz", "Frequency_Hz", "Sound_Level_dB",
                                log_x=True)
        self.assertEqual(len(_circles(svg)), 3)
        ET.fromstring(svg)  # 妥当な XML であること


class ScaleTests(unittest.TestCase):
    def test_log_mapping(self):
        s = plots._Scale([100, 1000], log=True, px0=0, px1=100)
        self.assertAlmostEqual(s.x(100), 0)
        self.assertAlmostEqual(s.x(1000), 100)
        self.assertAlmostEqual(s.x(10 ** 2.5), 50)

    def test_log_rejects_non_positive(self):
        with self.assertRaises(ValueError):
            plots._Scale([0, 100], log=True, px0=0, px1=100)

    def test_jitter_range_and_determinism(self):
        vals = [plots._jitter(i) for i in range(50)]
        self.assertTrue(all(-0.5 <= v <= 0.5 for v in vals))
        self.assertEqual(vals, [plots._jitter(i) for i in range(50)])


if __name__ == "__main__":
    unittest.main()
