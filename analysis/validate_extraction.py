"""抽出数値の照合バリデータ（むぎの抽出 → テストで照合、の二重ろ過の後段）。

抽出 CSV（extraction_sheet_template.csv と同じ列）を bibliography_all.csv
の抄録と突き合わせ、スクレイピング/転記ミスを機械的に検出する。

検査項目:
  ERROR（混入を止める）:
    - スキーマ不一致、PMID が書誌に存在しない、PMID の重複行
    - 数値があるのに Evidence_Quote が空
    - Evidence_Quote が抄録に verbatim（空白正規化後）で存在しない
    - 数値セルの数値が引用文の中に見つからない（単位換算の候補も含め）
    - Decision / Stratum の値が不正、Exclude なのに Exclude_Reason が空
  WARN（止めないが人間の目視キューに載せる）:
    - 抄録が無い論文（照合不能）
    - 数値が引用文中の kHz 表記からの換算でのみ一致（換算の発生を記録）
    - 物理的な妥当域の外側（動物の超音波・高曝露実験など正当な場合も
      あるため却下はしない。域は下記 PLAUSIBLE に根拠付きで置く）
    - Decision が未記入（抽出途中の殻を許すため）

使い方:
  python -m analysis.validate_extraction literature/extraction_batches/output/batch_1.csv
  終了コード: ERROR が1件でもあれば 1、なければ 0。
"""
import argparse
import csv
import glob
import re
import sys
from collections import namedtuple

Issue = namedtuple("Issue", ["level", "pmid", "code", "message"])

NUMERIC_COLUMNS = ["Frequency_Hz", "Attenuation_dB_oct", "Sound_Level_dB", "Tempo_BPM"]
VALID_STRATA = {"A", "B", "C", "UNDETERMINED", ""}
VALID_DECISIONS = {"Include", "Exclude", ""}

# 妥当域（WARN 専用、却下には使わない）。
# 周波数: ヒト可聴域 20Hz–20kHz が中心だが、動物層（C）では齧歯類・
# コウモリ等の超音波（〜200kHz）があり得るため上限は広く取る。
# 音圧: 140dB は痛覚域の上限側。実験曝露でも通常これを超えない。
# テンポ: 心拍・音楽テンポの生理的範囲を大きく外れたら転記ミスを疑う。
PLAUSIBLE = {
    "Frequency_Hz": (1.0, 200000.0),
    "Sound_Level_dB": (-10.0, 140.0),
    "Tempo_BPM": (20.0, 300.0),
    "Attenuation_dB_oct": (0.0, 100.0),
}

_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


def _norm_ws(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def _fmt_num(v):
    """500.0 -> '500'、0.5 -> '0.5' のように引用照合用の表記を作る。"""
    if v == int(v):
        return str(int(v))
    return ("%f" % v).rstrip("0").rstrip(".")


def _cell_numbers(cell):
    return [float(m) for m in _NUMBER_RE.findall((cell or "").replace(",", ""))]


def number_in_quote(value, quote):
    """数値が引用文に在るか。戻り値: 'verbatim' / 'converted' / None。

    converted は Hz セルに対する kHz 表記（値を 1/1000 した表記が
    引用にあり、かつ引用に kHz の記載がある）場合のみ認める。
    換算を認めた事実は呼び出し側で WARN として記録する。
    """
    q = quote.replace(",", "")
    if _fmt_num(value) in _NUMBER_RE.findall(q):
        return "verbatim"
    if "khz" in q.lower():
        scaled = _fmt_num(value / 1000.0)
        if scaled in _NUMBER_RE.findall(q):
            return "converted"
    return None


def load_abstracts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["PMID"]: r.get("Abstract", "") for r in csv.DictReader(f)}


def validate_rows(rows, abstracts):
    issues = []
    seen = {}
    for r in rows:
        pmid = (r.get("PMID") or "").strip()
        tag = pmid or "(no PMID)"
        if pmid in seen:
            issues.append(Issue("ERROR", tag, "duplicate_pmid",
                                "同じ PMID の行が複数ある"))
        seen[pmid] = True
        if pmid not in abstracts:
            issues.append(Issue("ERROR", tag, "unknown_pmid",
                                "書誌 (bibliography_all.csv) に無い PMID"))
            continue
        abstract = abstracts[pmid]
        quote = _norm_ws(r.get("Evidence_Quote"))
        numerics = {c: _cell_numbers(r.get(c)) for c in NUMERIC_COLUMNS}
        has_numeric = any(numerics[c] for c in NUMERIC_COLUMNS)

        if (r.get("Stratum") or "").strip() not in VALID_STRATA:
            issues.append(Issue("ERROR", tag, "bad_stratum",
                                f"Stratum が不正: {r.get('Stratum')!r}"))
        decision = (r.get("Decision") or "").strip()
        if decision not in VALID_DECISIONS:
            issues.append(Issue("ERROR", tag, "bad_decision",
                                f"Decision が不正: {decision!r}"))
        if decision == "":
            issues.append(Issue("WARN", tag, "undecided", "Decision が未記入"))
        if decision == "Exclude" and not (r.get("Exclude_Reason") or "").strip():
            issues.append(Issue("ERROR", tag, "exclude_no_reason",
                                "Exclude なのに Exclude_Reason が空"))

        if has_numeric and not quote:
            issues.append(Issue("ERROR", tag, "numeric_without_quote",
                                "数値があるのに Evidence_Quote が空"))
        if quote:
            if not abstract:
                issues.append(Issue("WARN", tag, "no_abstract",
                                    "抄録が無いため引用の照合ができない"))
            elif quote not in _norm_ws(abstract):
                issues.append(Issue("ERROR", tag, "quote_not_verbatim",
                                    "Evidence_Quote が抄録に verbatim で存在しない"))
            for col in NUMERIC_COLUMNS:
                for v in numerics[col]:
                    hit = number_in_quote(v, quote)
                    if hit is None:
                        issues.append(Issue(
                            "ERROR", tag, "number_not_in_quote",
                            f"{col}={_fmt_num(v)} が引用文に見つからない"))
                    elif hit == "converted":
                        issues.append(Issue(
                            "WARN", tag, "unit_converted",
                            f"{col}={_fmt_num(v)} は引用の kHz 表記からの換算で一致"))
        for col in NUMERIC_COLUMNS:
            lo, hi = PLAUSIBLE[col]
            for v in numerics[col]:
                if not (lo <= v <= hi):
                    issues.append(Issue(
                        "WARN", tag, "implausible_value",
                        f"{col}={_fmt_num(v)} が妥当域 [{lo}, {hi}] の外"))
    return issues


def validate_files(paths, bibliography):
    abstracts = load_abstracts(bibliography)
    all_issues = []
    total = 0
    for path in paths:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total += len(rows)
        all_issues += validate_rows(rows, abstracts)
    return total, all_issues


def main(argv=None):
    ap = argparse.ArgumentParser(prog="analysis.validate_extraction")
    ap.add_argument("inputs", nargs="+", help="抽出 CSV（glob 可）")
    ap.add_argument("--bibliography", default="literature/bibliography_all.csv")
    args = ap.parse_args(argv)
    paths = []
    for pat in args.inputs:
        paths += sorted(glob.glob(pat)) or [pat]
    total, issues = validate_files(paths, args.bibliography)
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]
    for i in issues:
        print(f"{i.level} PMID={i.pmid} [{i.code}] {i.message}")
    print(f"checked {total} rows: {len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
