"""Generate analysis/four_songs.html — the four finished mixes with
their evidence, as one self-contained HTML file.

Reads analysis/four_songs_measurements.csv (Python + SoX) and
analysis/four_songs_stats_r.csv (R). Band charts show each file's
octave-band shares (band power relative to the file's own
125-8000 Hz total), raw phrase vs final mix.

Usage: python -m analysis.make_four_songs_html
"""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "four_songs.html"
BANDS = [125, 250, 500, 1000, 2000, 4000, 8000]

# 引用レジストリ（analysis/citation_discipline.md）: 出典表示には
# reference_id を併記し、ID がレジストリに無ければ生成を止める。
_REFS = {}
with open(ROOT / "analysis" / "evidence_references.csv", encoding="utf-8") as _f:
    for _row in csv.DictReader(_f):
        _REFS[_row["reference_id"]] = _row


def ref_suffix(reference_id: str) -> str:
    assert reference_id in _REFS, f"reference_id がレジストリにありません: {reference_id}"
    return f"reference_id: {reference_id}"

NAMES = {
    "brahms_wiegenlied": ("ブラームスの子守歌", "楽譜は二重チェック済み"),
    "moldau_theme": ("モルダウ主題", "楽譜は二重チェック済み"),
    "vissi_darte": ("歌に生き、愛に生き (Vissi d'arte)",
                     "転記は冒頭部分のみ (二重チェック済み)。中間部以降は未転記"),
    "yurikago_no_uta": ("ゆりかごのうた", "公開カリンバ譜からの編曲 (完全転記ではない)"),
}


def shares(row: dict, label: str) -> list[float]:
    lv = [float(row[f"band_{c}_{label}"]) for c in BANDS]
    tot = 10 * math.log10(sum(10 ** (v / 10) for v in lv))
    return [round(v - tot, 1) for v in lv]


def band_chart(row: dict) -> str:
    raw, mix = shares(row, "raw"), shares(row, "mix")
    w, h, base, top = 340, 150, 118, 8
    bw = 16
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:420px;height:auto">']
    parts.append(f'<line x1="26" y1="{base}" x2="{w - 4}" y2="{base}" stroke="#999"/>')
    for i, c in enumerate(BANDS):
        x = 34 + i * 44
        for j, (vals, color) in enumerate(((raw, "#bbb"), (mix, "#2456a6"))):
            v = vals[i]
            bh = max(1.0, (v + 40) / 40 * (base - top))
            parts.append(f'<rect x="{x + j * (bw + 1)}" y="{base - bh:.0f}" '
                         f'width="{bw}" height="{bh:.0f}" fill="{color}"/>')
        parts.append(f'<text x="{x + bw}" y="{base + 14}" font-size="9.5" '
                     f'text-anchor="middle" fill="#555">{c}</text>')
    parts.append(f'<rect x="34" y="{h - 12}" width="10" height="7" fill="#bbb"/>'
                 f'<text x="48" y="{h - 5}" font-size="9.5" fill="#555">素のオルゴール</text>')
    parts.append(f'<rect x="150" y="{h - 12}" width="10" height="7" fill="#2456a6"/>'
                 f'<text x="164" y="{h - 5}" font-size="9.5" fill="#555">完成ミックス</text>')
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    with open(ROOT / "analysis" / "four_songs_measurements.csv",
              newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(ROOT / "analysis" / "four_songs_stats_r.csv",
              newline="", encoding="utf-8") as fh:
        stats = {r["quantity"]: r for r in csv.DictReader(fh)}

    sec = []
    for r in rows:
        name, note = NAMES[r["song"]]
        sec.append(f"""
<section>
<h3>{html.escape(name)}</h3>
<p class="note">{html.escape(note)}。ファイル: mix_{r['song']}.wav (60秒)</p>
<audio controls src="mix_{r['song']}.wav" style="width:100%"></audio>
{band_chart(r)}
<table>
<tr><th>スペクトル重心</th><td>{r['centroid_raw']} Hz → {r['centroid_mix']} Hz</td></tr>
<tr><th>1500 Hz 以上の割合</th><td>{r['share1500_raw']}% → {r['share1500_mix']}%</td></tr>
<tr><th>ベッド/音楽比 (実測)</th><td>全長 {r['balance_bed_music_db']} dB / 発音中 {r['balance_active_db']} dB</td></tr>
<tr><th>RMS (Python / SoX)</th><td>素 {r['rms_raw_py']} / {r['rms_raw_sox']} ・ ミックス {r['rms_mix_py']} / {r['rms_mix_sox']}</td></tr>
<tr><th>ピーク (SoX)</th><td>ミックス {r['peak_mix_sox']}</td></tr>
</table>
</section>""")

    def srow(key: str, label: str, unit: str) -> str:
        s = stats[key]
        return (f"<tr><td>{label}</td><td>{s['median']}</td>"
                f"<td>[{s['q1']}, {s['q3']}]</td><td>{s['sn']}</td>"
                f"<td>{s['qn']}</td><td>{s['min']} 〜 {s['max']}</td>"
                f"<td>{unit}</td></tr>")

    doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>4曲の完成ミックスとエビデンス</title>
<style>
body{{font-family:sans-serif;margin:16px;color:#222;max-width:860px}}
section{{border-top:1px solid #ddd;padding:10px 0}}
table{{border-collapse:collapse;font-size:13px;margin:6px 0}}
th,td{{border:1px solid #ccc;padding:3px 8px;text-align:left}}
th{{background:#f4f6fa;font-weight:normal;color:#444}}
p{{font-size:13px;line-height:1.65;color:#444}} .note{{color:#666;font-size:12px}}
h2{{font-size:17px}} h3{{font-size:15px;margin:8px 0 2px}}
</style></head><body>
<h2>4曲の完成ミックスとエビデンス (2026-11-17)</h2>
<p>4曲すべてを、確定した設計で3層ミックス (オルゴール+心音+血流ベッド)
として描き出した。各道具の担当はプロジェクトの役割分担どおり:
<b>SuperCollider</b> (Klank でオルゴールを生成、MusicXML が正本) →
<b>Python</b> (render_mix.py でミックス。音楽と血流に統合伝達曲線、
心音 70 BPM) → <b>SoX</b> (完成ファイルのレベル統計を独立に測定) →
<b>R</b> (robustbase で Python/SoX の一致検証と4曲の要約統計)。
帯域図は各ファイル自身の 125–8000 Hz 合計に対する帯域シェア (dB)。</p>

<p><b>設計の根拠</b>: 伝達曲線は Gerhardt 1990 (ヒツジ実測) の錨 —
250 Hz 以下 +3.5 dB、それ以上 −6 dB/oct (曲線図は bed_curves.html)。
引用は {ref_suffix("gerhardt_1990")}、レジストリは
analysis/evidence_references.csv。
心音 70 BPM (母体安静時心拍 60–80 の中央、可変パラメータ)、55 Hz は
実測スタイルの音色。ゲインは試聴で2段階弱めた確定値 (心音 0.10 /
血流 0.05 / 音楽 3.31 = 統合曲線の挿入損失を実測 ×3.01 で補償)。
ベッド/音楽比は較正用の短いフレーズでは −10.4 dB だったが、実際の
4曲で測ると中央値 −15.8 dB になった (曲ごとにフレーズの鳴っている
割合が違うため。ゲイン自体は変えていない)。</p>

{''.join(sec)}

<h3>4曲の要約 (R / robustbase)</h3>
<table>
<tr><th>量</th><th>中央値</th><th>[Q1, Q3]</th><th>Sn</th><th>Qn</th><th>範囲</th><th></th></tr>
{srow('centroid_mix', '完成ミックスの重心', 'Hz')}
{srow('centroid_shift', '重心の低下', 'Hz')}
{srow('banddiff_1000', '1000 Hz 帯域の変化', 'dB')}
{srow('banddiff_2000', '2000 Hz 帯域の変化', 'dB')}
{srow('banddiff_4000', '4000 Hz 帯域の変化', 'dB')}
{srow('balance_bed_music_db', 'ベッド/音楽比 (全長)', 'dB')}
</table>
<p><b>相互検証</b>: 同一ファイルの RMS を Python と SoX で独立に測り、
最大差 0.00001 (丸め水準)。Klank の再レンダーは前回とピーク・長さが
完全一致 (決定的レンダー)。数値の正本は
analysis/four_songs_measurements.csv と four_songs_stats_r.csv、
伝達曲線の照合は audio/bed_integration_2026-11-17.md。</p>
</body></html>"""
    _tmp = OUT.with_suffix(".html.tmp")
    _tmp.write_text(doc, encoding="utf-8")
    _tmp.replace(OUT)  # 原子的に置き換える（Issue #12）
    print("wrote", OUT)


if __name__ == "__main__":
    main()
