"""Generate analysis/bed_curves.html — the transfer-curve comparison
as a single self-contained HTML file with an inline SVG plot.

Data: literature/bed_transfer_curves.csv (point data, kinds kept
visible in the plot) plus the two analytic curves from
analysis/bed_integration.py (Gerhardt anchor, Richards endpoint
line). Re-runnable: python -m analysis.make_bed_curves_html
"""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURVES = ROOT / "literature" / "bed_transfer_curves.csv"
OUT = ROOT / "analysis" / "bed_curves.html"

# 引用レジストリ（analysis/citation_discipline.md）: 出典表示には
# reference_id を併記し、ID がレジストリに無ければ生成を止める。
_REFS = {}
with open(ROOT / "analysis" / "evidence_references.csv", encoding="utf-8") as _f:
    for _row in csv.DictReader(_f):
        _REFS[_row["reference_id"]] = _row


def ref_suffix(reference_id: str) -> str:
    assert reference_id in _REFS, f"reference_id がレジストリにありません: {reference_id}"
    return f"reference_id: {reference_id}"

W, H = 760, 470
ML, MR, MT, MB = 58, 130, 34, 46
X0, X1 = 125.0, 4000.0          # Hz, log2 scale
Y0, Y1 = 6.0, -30.0              # dB level change


def sx(f: float) -> float:
    return ML + (math.log2(f / X0) / math.log2(X1 / X0)) * (W - ML - MR)


def sy(v: float) -> float:
    return MT + ((Y0 - v) / (Y0 - Y1)) * (H - MT - MB)


def anchor(f: float) -> float:
    return 3.5 if f <= 250.0 else 3.5 - 6.0 * math.log2(f / 250.0)


def richards(f: float) -> float:
    return 3.7 - 2.74 * math.log2(f / 125.0)


def main() -> None:
    pts: dict[str, list[tuple[float, float]]] = {}
    with open(CURVES, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pts.setdefault(row["source"], []).append(
                (float(row["freq_hz"]), float(row["level_db"])))
    rich = sorted(pts["Richards 1992 (PMID 1635729)"])
    quer = sorted(next(v for k, v in pts.items() if k.startswith("Querleu")))
    gerh = sorted(pts["Gerhardt 1990 (PMID 2301503)"])

    s: list[str] = []
    # gridlines: octaves + 5 dB steps
    for f in (125, 250, 500, 1000, 2000, 4000):
        s.append(f'<line x1="{sx(f):.1f}" y1="{MT}" x2="{sx(f):.1f}" '
                 f'y2="{H - MB}" stroke="#ddd"/>')
        s.append(f'<text x="{sx(f):.1f}" y="{H - MB + 18}" font-size="11" '
                 f'text-anchor="middle" fill="#555">{f:g}</text>')
    for v in range(5, -31, -5):
        c = "#999" if v == 0 else "#eee"
        s.append(f'<line x1="{ML}" y1="{sy(v):.1f}" x2="{W - MR}" '
                 f'y2="{sy(v):.1f}" stroke="{c}"/>')
        s.append(f'<text x="{ML - 6}" y="{sy(v) + 4:.1f}" font-size="11" '
                 f'text-anchor="end" fill="#555">{v:+d}</text>')
    s.append(f'<text x="{(ML + W - MR) / 2}" y="{H - 6}" font-size="11" '
             f'text-anchor="middle" fill="#555">周波数 (Hz)</text>')
    s.append(f'<text x="14" y="{(MT + H - MB) / 2}" font-size="11" '
             f'text-anchor="middle" fill="#555" '
             f'transform="rotate(-90 14 {(MT + H - MB) / 2})">レベル変化 (dB)</text>')

    def poly(fn, f_from, f_to, color, width, dash=""):
        steps = 60
        coords = []
        for i in range(steps + 1):
            f = f_from * (f_to / f_from) ** (i / steps)
            coords.append(f"{sx(f):.1f},{sy(fn(f)):.1f}")
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{" ".join(coords)}" fill="none" '
                f'stroke="{color}" stroke-width="{width}"{d}/>')

    def markers(points, color, fill, r=4.5):
        return "".join(
            f'<circle cx="{sx(f):.1f}" cy="{sy(v):.1f}" r="{r}" '
            f'fill="{fill}" stroke="{color}" stroke-width="2"/>'
            for f, v in points)

    def seg(points, color, dash):
        coords = " ".join(f"{sx(f):.1f},{sy(v):.1f}" for f, v in points)
        return (f'<polyline points="{coords}" fill="none" stroke="{color}" '
                f'stroke-width="2" stroke-dasharray="{dash}"/>')

    # Richards endpoint line (derived) + stated endpoints
    s.append(poly(richards, 125, 4000, "#2a7f2a", 2, "7 4"))
    s.append(markers(rich, "#2a7f2a", "#2a7f2a"))
    # Querleu points (secondary corroborated) + dotted segments
    s.append(seg(quer, "#c0392b", "2 3"))
    s.append(markers(quer, "#c0392b", "white"))
    # Gerhardt anchor (analytic) + stated 4 kHz point
    s.append(poly(anchor, 125, 4000, "#2456a6", 3))
    s.append(markers(gerh, "#2456a6", "#2456a6", r=5))
    # bracket at 1000 Hz: Richards -4.52 .. Querleu -20
    bx = sx(1000) + 10
    s.append(f'<line x1="{bx:.1f}" y1="{sy(-4.52):.1f}" x2="{bx:.1f}" '
             f'y2="{sy(-20):.1f}" stroke="#888" stroke-width="1.5"/>')
    s.append(f'<text x="{bx + 5:.1f}" y="{sy(-12):.1f}" font-size="11" '
             f'fill="#666">ヒト同士の開き 15.5 dB</text>')

    lx = W - MR + 12
    legend = [
        ("#2456a6", "錨 Gerhardt (ヒツジ)", "250 Hz 以下 +3.5、以上 −6 dB/oct / " + ref_suffix("gerhardt_1990")),
        ("#2a7f2a", "Richards 1992 (ヒト)", "端点は一次明記、線は計算 / " + ref_suffix("richards_1992")),
        ("#c0392b", "Querleu 1988 (ヒト)", "二次裏付け・一次未確認 / " + ref_suffix("querleu_1988")),
    ]
    ly = MT + 6
    for color, name, note in legend:
        s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 22}" y2="{ly}" '
                 f'stroke="{color}" stroke-width="3"/>')
        s.append(f'<text x="{lx}" y="{ly + 16}" font-size="11.5" '
                 f'fill="#222">{html.escape(name)}</text>')
        s.append(f'<text x="{lx}" y="{ly + 31}" font-size="10" '
                 f'fill="#666">{html.escape(note)}</text>')
        ly += 52
    s.append(f'<text x="{lx}" y="{ly + 4}" font-size="10.5" fill="#666">'
             f'Querleu 区間傾斜: 250→500 は −12、</text>')
    s.append(f'<text x="{lx}" y="{ly + 19}" font-size="10.5" fill="#666">'
             f'500 Hz 超は −6 dB/oct (錨と同じ)</text>')

    doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>胎内伝達曲線の比較 (第3弾まで)</title>
<style>body{{font-family:sans-serif;margin:16px;color:#222;max-width:820px}}
svg{{width:100%;height:auto}}p{{font-size:13px;line-height:1.6;color:#444}}</style>
</head><body>
<h2 style="font-size:17px">胎内伝達曲線の比較 — 錨とヒト2曲線</h2>
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{''.join(s)}
</svg>
<p>青い太線が設計の錨 (Gerhardt 1990、ヒツジ実測)。緑は Richards 1992
(ヒト、端点2つは一次明記・線は端点を結んだ計算値)。赤は Querleu 1988
(ヒト、独立した二次源3件が一致したが一次源では未確認のため設計には
使っていない)。錨は全周波数で2つのヒト曲線の間に来る。1000 Hz では
ヒト同士の開き (15.5 dB) が錨と近い方との距離 (4.0 dB) より大きく、
不確かさの本体は種差ではなくヒト研究間のばらつき。
根拠と探索記録: literature/bed_literature_round3_human.md、
数値: literature/bed_transfer_curves.csv と
analysis/bed_curve_comparison.csv (Python × R 完全一致)。
引用レジストリ: analysis/evidence_references.csv
（各曲線の reference_id は凡例に併記）。</p>
</body></html>"""
    _tmp = OUT.with_suffix(".html.tmp")
    _tmp.write_text(doc, encoding="utf-8")
    _tmp.replace(OUT)  # 原子的に置き換える（Issue #12）
    print("wrote", OUT)
    print("check: anchor(1000) =", anchor(1000), "| richards(1000) =",
          round(richards(1000), 2), "| querleu pts:", quer)


if __name__ == "__main__":
    main()
