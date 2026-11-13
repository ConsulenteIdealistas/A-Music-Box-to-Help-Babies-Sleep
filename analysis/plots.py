"""抽出データの可視化（ドットプロット / 散布図）。Python 標準ライブラリのみ。

出力は SVG（テキスト形式）。依存ライブラリを持たず、GitHub 上でも
そのまま表示できる形にする。

設計:
- 周波数（Frequency_Hz）は対数軸が既定（対数化は確定事項）。
  dB は自体が対数尺度なので線形のまま、BPM 等も線形が既定。
  どちらも引数で切り替え可能。
- ドットプロットは群（層・パラメータ）ごとに行を分け、Q1〜Q3 の帯と
  中央値の線を重ねる。分布の非対称・同点の集中・外れ値が一目で
  分かることが目的（統計量の主役交代の判断材料）。
- ドットの縦方向のずらし（jitter）は、値のインデックスから決まる
  決定的なハッシュで作る。再生成しても同じ図になる。
- 表示上の余白や色は統計量ではない（表示の都合）として、定数は
  このモジュール内に閉じる。

使い方:
  python -m analysis.plots dot --input literature/extraction.csv \
      --value Frequency_Hz --group Stratum --out /tmp/freq_dot.svg
  python -m analysis.plots scatter --input literature/extraction.csv \
      --x Frequency_Hz --y Sound_Level_dB --out /tmp/freq_db.svg
"""
import argparse
import csv
import math
import sys
from xml.sax.saxutils import escape

from analysis import stats

WIDTH = 880
MARGIN_LEFT = 130
MARGIN_RIGHT = 30
MARGIN_TOP = 44
MARGIN_BOTTOM = 46
PALETTE = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#d97706", "#0891b2"]
LOG_DEFAULT_COLUMNS = {"Frequency_Hz"}


def _fmt(v):
    if v >= 100:
        return f"{v:.0f}"
    if v >= 10:
        return f"{v:.1f}".rstrip("0").rstrip(".")
    return f"{v:.2f}".rstrip("0").rstrip(".")


class _Scale:
    """値 → ピクセル座標の変換（log / linear）。"""

    def __init__(self, values, log, px0, px1):
        vals = [float(v) for v in values]
        if not vals:
            raise ValueError("no values to plot")
        if log:
            if any(v <= 0 for v in vals):
                raise ValueError("log scale requires all values > 0")
            lo = 10 ** math.floor(math.log10(min(vals)))
            hi = 10 ** math.ceil(math.log10(max(vals)))
            if lo == hi:
                hi = lo * 10
            self.t_lo, self.t_hi = math.log10(lo), math.log10(hi)
            self.ticks = []
            p = int(math.log10(lo))
            while 10 ** p <= hi:
                self.ticks.append((10.0 ** p, _fmt(10.0 ** p), True))
                for m in range(2, 10):
                    if 10 ** p * m < hi:
                        self.ticks.append((10.0 ** p * m, "", False))
                p += 1
        else:
            lo, hi = min(vals), max(vals)
            if lo == hi:
                lo, hi = lo - 1.0, hi + 1.0
            span = hi - lo
            raw_step = span / 5.0
            mag = 10 ** math.floor(math.log10(raw_step))
            step = next(s for s in (1, 2, 5, 10) if mag * s >= raw_step) * mag
            lo = math.floor(lo / step) * step
            hi = math.ceil(hi / step) * step
            self.t_lo, self.t_hi = lo, hi
            self.ticks = []
            v = lo
            while v <= hi + step * 0.5:
                self.ticks.append((v, _fmt(v), True))
                v += step
        self.log = log
        self.px0, self.px1 = px0, px1

    def _t(self, v):
        return math.log10(v) if self.log else float(v)

    def x(self, v):
        frac = (self._t(v) - self.t_lo) / (self.t_hi - self.t_lo)
        return self.px0 + frac * (self.px1 - self.px0)


def _jitter(i):
    """決定的 jitter（-0.5〜+0.5）。同じ入力では同じ図になる。"""
    return (((i * 2654435761) % 1000) / 1000.0) - 0.5


def dot_plot_svg(groups, title, x_label, log_x=True):
    """groups: [(label, [values...]), ...] のドットプロット SVG を返す。"""
    row_h = 58
    plot_w = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    height = MARGIN_TOP + row_h * len(groups) + MARGIN_BOTTOM
    all_values = [v for _, vs in groups for v in vs]
    scale = _Scale(all_values, log_x, MARGIN_LEFT, MARGIN_LEFT + plot_w)
    axis_y = MARGIN_TOP + row_h * len(groups) + 6

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
           f'height="{height}" font-family="sans-serif">']
    out.append(f'<rect width="{WIDTH}" height="{height}" fill="white"/>')
    out.append(f'<text x="{MARGIN_LEFT}" y="26" font-size="16" '
               f'font-weight="bold">{escape(title)}</text>')
    # 縦グリッドと軸ラベル
    for v, label, major in scale.ticks:
        x = scale.x(v)
        color = "#d1d5db" if major else "#f3f4f6"
        out.append(f'<line x1="{x:.1f}" y1="{MARGIN_TOP - 8}" x2="{x:.1f}" '
                   f'y2="{axis_y}" stroke="{color}"/>')
        if label:
            out.append(f'<text x="{x:.1f}" y="{axis_y + 18}" font-size="11" '
                       f'text-anchor="middle" fill="#374151">{escape(label)}</text>')
    out.append(f'<text x="{MARGIN_LEFT + plot_w / 2}" y="{axis_y + 38}" '
               f'font-size="11" text-anchor="middle" fill="#374151">'
               f'{escape(x_label)}{" (log scale)" if log_x else ""}</text>')
    for gi, (label, values) in enumerate(groups):
        cy = MARGIN_TOP + row_h * gi + row_h / 2
        color = PALETTE[gi % len(PALETTE)]
        out.append(f'<text x="{MARGIN_LEFT - 10}" y="{cy + 4}" font-size="12" '
                   f'text-anchor="end">{escape(label)} (n={len(values)})</text>')
        if len(values) >= 2:
            q1x, q3x = scale.x(stats.q1(values)), scale.x(stats.q3(values))
            out.append(f'<rect x="{q1x:.1f}" y="{cy - 13}" width="{q3x - q1x:.1f}" '
                       f'height="26" fill="{color}" opacity="0.15"/>')
            medx = scale.x(stats.median(values))
            out.append(f'<line x1="{medx:.1f}" y1="{cy - 15}" x2="{medx:.1f}" '
                       f'y2="{cy + 15}" stroke="{color}" stroke-width="2.5"/>')
        for i, v in enumerate(sorted(values)):
            y = cy + _jitter(i) * 26
            out.append(f'<circle cx="{scale.x(v):.1f}" cy="{y:.1f}" r="4" '
                       f'fill="{color}" opacity="0.75"/>')
    out.append("</svg>")
    return "\n".join(out)


def scatter_svg(points, title, x_label, y_label, log_x=False, log_y=False):
    """points: [(x, y), ...] の散布図 SVG を返す。"""
    plot_w = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    plot_h = 460
    height = MARGIN_TOP + plot_h + MARGIN_BOTTOM + 14
    xs = _Scale([p[0] for p in points], log_x, MARGIN_LEFT, MARGIN_LEFT + plot_w)
    # y は上が大きい向きに反転させる
    ys_raw = _Scale([p[1] for p in points], log_y, 0, plot_h)
    base_y = MARGIN_TOP + plot_h

    def y_px(v):
        return base_y - (ys_raw.x(v) - 0)  # _Scale は 0..plot_h に写像済み

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
           f'height="{height}" font-family="sans-serif">']
    out.append(f'<rect width="{WIDTH}" height="{height}" fill="white"/>')
    out.append(f'<text x="{MARGIN_LEFT}" y="26" font-size="16" '
               f'font-weight="bold">{escape(title)}</text>')
    for v, label, major in xs.ticks:
        x = xs.x(v)
        out.append(f'<line x1="{x:.1f}" y1="{MARGIN_TOP}" x2="{x:.1f}" '
                   f'y2="{base_y}" stroke="{"#d1d5db" if major else "#f3f4f6"}"/>')
        if label:
            out.append(f'<text x="{x:.1f}" y="{base_y + 18}" font-size="11" '
                       f'text-anchor="middle" fill="#374151">{escape(label)}</text>')
    for v, label, major in ys_raw.ticks:
        if not label:
            continue
        y = y_px(v)
        out.append(f'<line x1="{MARGIN_LEFT}" y1="{y:.1f}" '
                   f'x2="{MARGIN_LEFT + plot_w}" y2="{y:.1f}" stroke="#f3f4f6"/>')
        out.append(f'<text x="{MARGIN_LEFT - 8}" y="{y + 4:.1f}" font-size="11" '
                   f'text-anchor="end" fill="#374151">{escape(label)}</text>')
    out.append(f'<text x="{MARGIN_LEFT + plot_w / 2}" y="{base_y + 38}" '
               f'font-size="11" text-anchor="middle" fill="#374151">'
               f'{escape(x_label)}{" (log scale)" if log_x else ""}</text>')
    out.append(f'<text x="18" y="{MARGIN_TOP + plot_h / 2}" font-size="11" '
               f'text-anchor="middle" fill="#374151" '
               f'transform="rotate(-90 18 {MARGIN_TOP + plot_h / 2})">'
               f'{escape(y_label)}{" (log scale)" if log_y else ""}</text>')
    for x, y in points:
        out.append(f'<circle cx="{xs.x(x):.1f}" cy="{y_px(y):.1f}" r="3.5" '
                   f'fill="{PALETTE[0]}" opacity="0.75"/>')
    out.append("</svg>")
    return "\n".join(out)


def _read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _numbers(rows, column):
    vals = []
    for r in rows:
        try:
            vals.append(float(r[column]))
        except (TypeError, ValueError, KeyError):
            continue  # N/A や範囲表記は数値化できないため飛ばす（件数は呼び出し側で数える）
    return vals


def main(argv=None):
    ap = argparse.ArgumentParser(prog="analysis.plots")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dot")
    d.add_argument("--input", required=True)
    d.add_argument("--value", required=True)
    d.add_argument("--group", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--log-x", action="store_true", default=None)
    d.add_argument("--linear-x", action="store_false", dest="log_x")
    s = sub.add_parser("scatter")
    s.add_argument("--input", required=True)
    s.add_argument("--x", required=True)
    s.add_argument("--y", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--log-x", action="store_true", default=None)
    s.add_argument("--linear-x", action="store_false", dest="log_x")
    s.add_argument("--log-y", action="store_true", default=None)
    s.add_argument("--linear-y", action="store_false", dest="log_y")
    args = ap.parse_args(argv)

    rows = _read_rows(args.input)
    if args.cmd == "dot":
        log_x = args.log_x if args.log_x is not None else args.value in LOG_DEFAULT_COLUMNS
        grouped = {}
        for r in rows:
            g = (r.get(args.group) or "").strip()
            if g:
                grouped.setdefault(g, []).append(r)
        groups = [(g, _numbers(rs, args.value)) for g, rs in sorted(grouped.items())]
        groups = [(g, vs) for g, vs in groups if vs]
        svg = dot_plot_svg(groups, f"{args.value} by {args.group}", args.value, log_x)
        n = sum(len(vs) for _, vs in groups)
    else:
        log_x = args.log_x if args.log_x is not None else args.x in LOG_DEFAULT_COLUMNS
        log_y = args.log_y if args.log_y is not None else args.y in LOG_DEFAULT_COLUMNS
        points = []
        for r in rows:
            try:
                points.append((float(r[args.x]), float(r[args.y])))
            except (TypeError, ValueError, KeyError):
                continue
        svg = scatter_svg(points, f"{args.y} vs {args.x}", args.x, args.y, log_x, log_y)
        n = len(points)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {args.out} ({n} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
