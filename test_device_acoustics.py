"""端末スピーカー一次情報コレクションのスキーマテスト。
実行: python -m unittest test_device_acoustics -v
devices.csv の列定義と母集団（対象機種リスト）の最低条件を固定する。"""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "literature", "device_acoustics", "devices.csv")

EXPECTED_COLUMNS = [
    "Device", "Maker", "Release_Year", "Device_Class",
    "DXOMARK_URL", "GSMArena_URL", "Notebookcheck_URL", "RTINGS_URL",
    "Status", "Notes",
]
EXPECTED_CLASSES = {
    "iphone", "iphone_budget", "android_flagship", "android_mid",
    "android_budget", "external_speaker",
}


class DevicesCsvTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))

    def test_columns(self):
        self.assertEqual(list(self.rows[0].keys()), EXPECTED_COLUMNS)

    def test_roster_size_and_classes(self):
        self.assertGreaterEqual(len(self.rows), 20)
        classes = {r["Device_Class"] for r in self.rows}
        self.assertEqual(classes, EXPECTED_CLASSES)

    def test_no_duplicate_devices(self):
        names = [r["Device"] for r in self.rows]
        self.assertEqual(len(names), len(set(names)))

    def test_unlocated_rows_have_no_urls(self):
        url_cols = ["DXOMARK_URL", "GSMArena_URL", "Notebookcheck_URL", "RTINGS_URL"]
        for r in self.rows:
            if r["Status"] == "To_located":
                self.assertTrue(all(r[c] == "" for c in url_cols), r["Device"])


if __name__ == "__main__":
    unittest.main()
