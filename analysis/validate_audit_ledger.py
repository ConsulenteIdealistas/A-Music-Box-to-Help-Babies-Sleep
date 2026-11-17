#!/usr/bin/env python3
"""監査台帳の形式検証（Python 標準ライブラリのみ）。

対象:
  analysis/acoustic_evidence_audit.json
    - parameters の全エントリに必須フィールドが揃っていること
    - parameter_id が空でなく一意であること
    - decision が許容値のいずれかであること
  analysis/evidence_references.csv
    - 期待どおりの見出し行で CSV として解釈できること
    - 各行の列数が見出しと一致すること

問題があれば一覧を表示して終了コード 1、なければ OK を表示して 0。
台帳の中身（値・判断）は変更しない、読み取り専用の検証。
"""

import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEDGER = BASE / "acoustic_evidence_audit.json"
REFS = BASE / "evidence_references.csv"

REQUIRED_FIELDS = [
    "parameter_id", "parameter_name", "value_class", "current_value",
    "proposed_value", "unit", "definition", "implementation",
    "evidence_grade", "source_doi", "source_url", "source_conditions",
    "applicability", "safety_status", "decision", "decision_reason",
    "revision", "sensitivity", "borrowed_from",
]
ALLOWED_DECISIONS = {"", "pending", "keep", "experiment", "hold", "change"}
EXPECTED_HEADER = [
    "reference_id", "title", "doi", "url", "source_conditions",
    "applicability", "linked_parameters", "notes",
    "verification_status", "verified_on",
]


def check_ledger(problems):
    try:
        data = json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception as e:  # 読めない・JSON でない場合はここで止める
        problems.append(f"{LEDGER.name}: 読み込みに失敗しました: {e}")
        return
    params = data.get("parameters")
    if not isinstance(params, list):
        problems.append(f"{LEDGER.name}: parameters が配列ではありません")
        return
    seen = {}
    for i, entry in enumerate(params):
        where = f"{LEDGER.name} parameters[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: オブジェクトではありません")
            continue
        pid = entry.get("parameter_id")
        label = pid if isinstance(pid, str) and pid else f"#{i}"
        missing = [k for k in REQUIRED_FIELDS if k not in entry]
        if missing:
            problems.append(f"{where} ({label}): 必須フィールドが不足: {', '.join(missing)}")
        if not isinstance(pid, str) or not pid:
            problems.append(f"{where}: parameter_id が空です")
        elif pid in seen:
            problems.append(f"{where}: parameter_id \"{pid}\" が重複しています（{seen[pid]} 件目と同一）")
        else:
            seen[pid] = i + 1
        decision = entry.get("decision")
        if decision not in ALLOWED_DECISIONS:
            problems.append(
                f"{where} ({label}): decision \"{decision}\" は許容値"
                f"（{' / '.join(sorted(ALLOWED_DECISIONS))}）にありません"
            )


def check_references(problems):
    try:
        text = REFS.read_text(encoding="utf-8")
    except Exception as e:
        problems.append(f"{REFS.name}: 読み込みに失敗しました: {e}")
        return
    try:
        rows = list(csv.reader(text.splitlines()))
    except csv.Error as e:
        problems.append(f"{REFS.name}: CSV として解釈できません: {e}")
        return
    if not rows:
        problems.append(f"{REFS.name}: 空です")
        return
    if rows[0] != EXPECTED_HEADER:
        problems.append(
            f"{REFS.name}: 見出しが期待と違います: {rows[0]}（期待: {EXPECTED_HEADER}）"
        )
    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        if len(row) != len(EXPECTED_HEADER):
            problems.append(f"{REFS.name} {i} 行目: 列数が {len(row)} で見出しの {len(EXPECTED_HEADER)} と一致しません")


def main():
    problems = []
    check_ledger(problems)
    check_references(problems)
    if problems:
        print("NG: 監査台帳に問題があります")
        for p in problems:
            print(" -", p)
        return 1
    print("OK: acoustic_evidence_audit.json と evidence_references.csv の形式は正しいです")
    return 0


if __name__ == "__main__":
    sys.exit(main())
