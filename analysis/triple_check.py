"""三層目: 絞った対象への独立再読と突き合わせ。

二重ろ過（抽出 → validate_extraction の機械照合）では捕まえられない
「引用は正しいが数字の意味を取り違えた」ミスへの対策。全件ではなく
対象を絞る（2026-11-13 決定）:

  1. A 層で数値を持つ行（設計パラメータに直接効く）— 全件
  2. バリデータで値に関する WARN が付いた行
     （unit_converted / implausible_value / no_abstract。
     undecided は抽出途中の印なので対象にしない）
  3. 残りからの無作為サンプル（ミス率の推定用）

サンプル数の根拠: 標本中にミスが 0 件なら真のミス率の 95% 上限は
約 3/n（rule of three、Hanley & Lippman-Hand 1983）。上限を 5% に
抑えるには n ≥ 60 が必要で、これをサンプル数とする（母数が
60 未満なら全件）。抽出は決定的シードで再現可能にする。

再読は一次抽出の値を見せない（blind）で行い、本ツールの compare で
突き合わせる。不一致は裁定（どちらが正しいか抄録で確認）するまで
統合しない。

使い方:
  python -m analysis.triple_check select \
      --inputs "literature/extraction_batches/output/*.csv" \
      --out literature/extraction_batches/recrosscheck/targets.csv
  python -m analysis.triple_check compare \
      --first literature/extraction.csv --reread reread.csv
"""
import argparse
import csv
import glob
import math
import random
import sys

from analysis import validate_extraction as ve

SAMPLE_TARGET_UPPER = 0.05   # ミス率の 95% 上限の目標
SAMPLE_SEED = 20261113       # 決定的サンプリング用
WARN_CODES_FOR_RECHECK = {"unit_converted", "implausible_value", "no_abstract"}
COMPARE_COLUMNS = ve.NUMERIC_COLUMNS + ["Decision", "Stratum"]


def sample_size(population):
    """rule of three: 上限 5% を狙う n = ceil(3 / 0.05) = 60。母数上限。"""
    return min(population, math.ceil(3.0 / SAMPLE_TARGET_UPPER))


def _has_numeric(row):
    return any(ve._cell_numbers(row.get(c)) for c in ve.NUMERIC_COLUMNS)


def select_targets(rows, abstracts):
    """対象リスト [(row, reason), ...] を返す。"""
    warn_pmids = {}
    for issue in ve.validate_rows(rows, abstracts):
        if issue.level == "WARN" and issue.code in WARN_CODES_FOR_RECHECK:
            warn_pmids.setdefault(issue.pmid, set()).add(issue.code)

    targets = {}
    rest = []
    for r in rows:
        pmid = (r.get("PMID") or "").strip()
        if not _has_numeric(r):
            continue  # 数値の無い行に意味の取り違えは起きない
        if (r.get("Stratum") or "").strip() == "A":
            targets[pmid] = "A_numeric"
        elif pmid in warn_pmids:
            targets[pmid] = "warn:" + ",".join(sorted(warn_pmids[pmid]))
        else:
            rest.append(r)
    n = sample_size(len(rest))
    rng = random.Random(SAMPLE_SEED)
    for r in rng.sample(rest, n) if n else []:
        targets[(r.get("PMID") or "").strip()] = "sample"
    by_pmid = {(r.get("PMID") or "").strip(): r for r in rows}
    return [(by_pmid[p], targets[p]) for p in sorted(targets)]


def _num_set(cell):
    return sorted(ve._cell_numbers(cell))


def compare(first_rows, reread_rows):
    """一次抽出と再読の不一致リスト [(pmid, column, first, reread)]。"""
    first = {(r.get("PMID") or "").strip(): r for r in first_rows}
    reread = {(r.get("PMID") or "").strip(): r for r in reread_rows}
    diffs = []
    for pmid in sorted(set(first) | set(reread)):
        if pmid not in reread:
            diffs.append((pmid, "(row)", "present", "missing in reread"))
            continue
        if pmid not in first:
            diffs.append((pmid, "(row)", "missing in first", "present"))
            continue
        for col in COMPARE_COLUMNS:
            a, b = first[pmid].get(col, ""), reread[pmid].get(col, "")
            if col in ve.NUMERIC_COLUMNS:
                if _num_set(a) != _num_set(b):
                    diffs.append((pmid, col, a, b))
            elif (a or "").strip() != (b or "").strip():
                diffs.append((pmid, col, a, b))
    return diffs


def _read_csvs(patterns):
    rows = []
    for pat in patterns:
        for path in sorted(glob.glob(pat)) or [pat]:
            with open(path, newline="", encoding="utf-8") as f:
                rows += list(csv.DictReader(f))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(prog="analysis.triple_check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--inputs", nargs="+", required=True)
    s.add_argument("--bibliography", default="literature/bibliography_all.csv")
    s.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--first", required=True)
    c.add_argument("--reread", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "select":
        rows = _read_csvs(args.inputs)
        abstracts = ve.load_abstracts(args.bibliography)
        targets = select_targets(rows, abstracts)
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["PMID", "Reason"])
            for r, reason in targets:
                w.writerow([(r.get("PMID") or "").strip(), reason])
        print(f"selected {len(targets)} targets -> {args.out}")
        return 0
    first = _read_csvs([args.first])
    reread = _read_csvs([args.reread])
    diffs = compare(first, reread)
    for pmid, col, a, b in diffs:
        print(f"DIFF PMID={pmid} {col}: first={a!r} reread={b!r}")
    print(f"{len(diffs)} discrepancies")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
