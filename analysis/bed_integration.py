"""Bed evidence integration: statistics + song comparison (2026-11-17).

Two independent evidence rounds exist for the womb bed / transfer:

  Round 1 (extraction): the 498-paper extraction's design statistics
  (literature/extraction_batches/design_stats_summary.md). Frequency
  median 1500 Hz, level median 60 dB, and an Attenuation population
  too small to fix a slope (6, 6, 12, 12, 96) — so brown vs pink was
  settled by listening (brown adopted 2026-11-17).

  Round 2 (primary literature): a targeted reinforcement collection
  on intrauterine transfer (literature/bed_literature_reinforcement.xml,
  13 papers checked, values verbatim-verified 38/38). Its anchor is
  Gerhardt 1990: +2..+5 dB below 250 Hz, attenuation increasing at
  6 dB/oct above 250 Hz, 20 dB average at 4 kHz.

This script works on the integrated, quantity-labelled dataset
(literature/bed_transfer_evidence.csv):

  1. Robust statistics per evidence group, via analysis/stats.py
     (the project's summarize()). The same CSV is fed to
     analysis/bed_integration.R (robustbase) and the two outputs are
     cross-checked — two implementations, one dataset.
  2. The four songs (Klank renders) measured with the project's usual
     spectrum method (8192-point Hann, 50% overlap) and passed
     analytically through the integrated transfer curves, so each
     song can be compared against the integrated target.

Integrated transfer curves (level change inside minus outside, dB):
  anchor (Gerhardt 1990, sheep):  +3.5 dB at/below 250 Hz (midpoint of
     the stated +2..+5 range), then -6 dB/oct. At 4 kHz this gives
     -20.5 dB, within 0.5 dB of Gerhardt's stated 20 dB average —
     the curve reproduces its own source's endpoint.
  human bound (Richards 1992): straight line between the two stated
     endpoints, +3.7 dB at 125 Hz and -10.0 dB at 4000 Hz
     (2.74 dB/oct). The sheep/human difference is unresolved in the
     literature; the anchor is the design curve, Richards is the
     gentler sensitivity bound.

  Round 3 (2026-11-17, human only): Richards' full text and the
  Querleu primaries were not openly accessible, so no new primary
  values exist. The Querleu band points (2/14/20/26 dB at
  250/500/1000/2000 Hz) are corroborated by three independent
  secondary sources and stored in literature/bed_transfer_curves.csv
  as kind=secondary_corroborated — used for curve comparison only,
  never pooled with stated values (see
  literature/bed_literature_round3_human.md). curve_rows() below
  tabulates the point sources against the anchor and Richards lines.

Song WAVs live outside the repo (they are binaries):
  ~/workspace/your_files/lullaby-klank/{brahms_wiegenlied,
  moldau_theme, vissi_darte, yurikago_no_uta}_klank.wav
  ~/workspace/your_files/lullaby-mix/bed_only_brown_soft.wav
  ~/workspace/your_files/lullaby-bed-literature/bed_literature.wav

Usage: python -m analysis.bed_integration
Outputs: analysis/bed_integration_stats_python.csv,
         analysis/song_transfer_comparison.csv,
         analysis/bed_curve_comparison.csv
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from analysis.stats import summarize

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "literature" / "bed_transfer_evidence.csv"
YOUR_FILES = Path.home() / "workspace" / "your_files"

SONGS = {
    "brahms": YOUR_FILES / "lullaby-klank" / "brahms_wiegenlied_klank.wav",
    "moldau": YOUR_FILES / "lullaby-klank" / "moldau_theme_klank.wav",
    "vissi_darte": YOUR_FILES / "lullaby-klank" / "vissi_darte_klank.wav",
    "yurikago": YOUR_FILES / "lullaby-klank" / "yurikago_no_uta_klank.wav",
    "bed_brown (round 1)": YOUR_FILES / "lullaby-mix" / "bed_only_brown_soft.wav",
    "bed_literature (round 2)": YOUR_FILES / "lullaby-bed-literature" / "bed_literature.wav",
}

BAND_CENTERS = [125, 250, 500, 1000, 2000, 4000, 8000]


def anchor_db(f: float) -> float:
    if f <= 250.0:
        return 3.5
    return 3.5 - 6.0 * math.log2(f / 250.0)


def richards_db(f: float) -> float:
    return 3.7 - 2.74 * math.log2(f / 125.0)


# ---------------------------------------------------------------- stats

def group_stats() -> list[dict]:
    groups: dict[str, list[float]] = {}
    with open(EVIDENCE, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            groups.setdefault(row["group"], []).append(float(row["value"]))
    out = []
    for name, vals in groups.items():
        s = summarize(vals)
        out.append({
            "group": name, "n": s["n"],
            "median": s["median"], "q1": s["q1"], "q3": s["q3"],
            "robust_sd": s["robust_sd"], "sn": s["sn"], "qn": s["qn"],
            "mean": s["mean"], "sd": s["sd"],
            "min": s["min"], "max": s["max"],
        })
    return out


# -------------------------------------------------------------- spectra

def read_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    import struct
    import wave
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        vals = np.array(struct.unpack(f"<{len(frames) // 2}h", frames),
                        dtype=np.float64) / 32768.0
        if w.getnchannels() == 2:
            vals = vals[::2]
        return vals, sr


def avg_power_spectrum(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    """Project's usual method: 8192-point Hann window, 50% overlap,
    mean power spectrum (numpy implementation)."""
    n = 8192
    win = np.hanning(n)
    acc = np.zeros(n // 2 + 1)
    count = 0
    for start in range(0, len(x) - n + 1, n // 2):
        seg = x[start:start + n] * win
        acc += np.abs(np.fft.rfft(seg)) ** 2
        count += 1
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    return freqs, acc / max(count, 1)


def band_levels(freqs: np.ndarray, power: np.ndarray) -> dict[int, float]:
    """Octave-band power summed per band, in dB (absolute scale shared
    across files, so bands are comparable between songs)."""
    levels = {}
    for c in BAND_CENTERS:
        lo, hi = c / math.sqrt(2), c * math.sqrt(2)
        mask = (freqs >= lo) & (freqs < hi)
        levels[c] = 10.0 * math.log10(max(power[mask].sum(), 1e-20))
    return levels


def apply_transfer(freqs: np.ndarray, power: np.ndarray, fn) -> np.ndarray:
    gains = np.array([10.0 ** (fn(max(f, 1.0)) / 10.0) for f in freqs])
    return power * gains


def metrics(freqs: np.ndarray, power: np.ndarray) -> dict:
    total = power[1:].sum()
    centroid = float((freqs[1:] * power[1:]).sum() / total)
    hi = power[freqs >= 1500].sum() / total * 100.0
    return {"centroid_hz": centroid, "share_ge_1500_pct": hi}


def song_rows() -> list[dict]:
    rows = []
    for name, path in SONGS.items():
        x, sr = read_wav_mono(path)
        freqs, power = avg_power_spectrum(x, sr)
        bands = band_levels(freqs, power)
        row: dict = {"name": name}
        for c in BAND_CENTERS:
            row[f"band_{c}"] = round(bands[c], 1)
        m0 = metrics(freqs, power)
        row["centroid_raw"] = round(m0["centroid_hz"])
        row["share1500_raw_pct"] = round(m0["share_ge_1500_pct"], 1)
        for label, fn in (("anchor", anchor_db), ("richards", richards_db)):
            post = apply_transfer(freqs, power, fn)
            m1 = metrics(freqs, post)
            loss = 10.0 * math.log10(post[1:].sum() / power[1:].sum())
            row[f"centroid_{label}"] = round(m1["centroid_hz"])
            row[f"share1500_{label}_pct"] = round(m1["share_ge_1500_pct"], 1)
            row[f"loss_{label}_db"] = round(loss, 1)
            pb = band_levels(freqs, post)
            for c in BAND_CENTERS:
                row[f"band_{c}_{label}"] = round(pb[c], 1)
        rows.append(row)
    return rows


# --------------------------------------------------------------- curves

CURVES = ROOT / "literature" / "bed_transfer_curves.csv"
STD_FREQS = [125, 250, 500, 1000, 2000, 4000]


def curve_rows() -> list[dict]:
    """Point-source curves: segment slopes (dB/oct of the level curve)
    and log-linear interpolated levels at standard frequencies, only
    within each source's stated range. The analytic anchor and the
    Richards endpoint line are appended for comparison."""
    sources: dict[str, list[tuple[float, float]]] = {}
    with open(CURVES, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sources.setdefault(row["source"], []).append(
                (float(row["freq_hz"]), float(row["level_db"])))
    rows = []
    for source, pts in sources.items():
        pts.sort()
        segs = [(l2 - l1) / math.log2(f2 / f1)
                for (f1, l1), (f2, l2) in zip(pts, pts[1:])]
        row: dict = {"source": source}
        row["segment_slopes"] = ";".join(f"{s:.2f}" for s in segs)
        row["overall_slope"] = (round((pts[-1][1] - pts[0][1])
                                / math.log2(pts[-1][0] / pts[0][0]), 2)
                                if len(pts) > 1 else "")
        for f in STD_FREQS:
            val: float | str = ""
            for pf, pl in pts:
                if f == pf:
                    val = pl
            if val == "":
                for (f1, l1), (f2, l2) in zip(pts, pts[1:]):
                    if f1 < f < f2:
                        t = math.log2(f / f1) / math.log2(f2 / f1)
                        val = round(l1 + t * (l2 - l1), 2)
                        break
            row[f"level_{f}"] = val
        rows.append(row)
    for label, fn in (("anchor (Gerhardt, analytic)", anchor_db),
                      ("richards line (analytic)", richards_db)):
        row = {"source": label, "segment_slopes": "", "overall_slope": ""}
        for f in STD_FREQS:
            row[f"level_{f}"] = round(fn(float(f)), 2)
        rows.append(row)
    return rows


def main() -> None:
    curves = curve_rows()
    with open(ROOT / "analysis" / "bed_curve_comparison.csv", "w",
              newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(curves[0].keys()))
        w.writeheader()
        w.writerows(curves)
    print("== transfer curves from point data (round 3) ==")
    for r in curves:
        lv = ", ".join(f"{f} Hz {r[f'level_{f}']:+.2f}" if r[f"level_{f}"] != ""
                       else f"{f} Hz n/a" for f in STD_FREQS)
        print(f"{r['source'][:52]:52s} {lv}")
        if r["segment_slopes"]:
            print(f"{'':52s} segment slopes {r['segment_slopes']} dB/oct, "
                  f"overall {r['overall_slope']:+.2f}")
    print()

    stats = group_stats()
    with open(ROOT / "analysis" / "bed_integration_stats_python.csv", "w",
              newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(stats[0].keys()))
        w.writeheader()
        for r in stats:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v)
                        for k, v in r.items()})
    print("== evidence-group statistics (Python, analysis/stats.py) ==")
    def f3(x):
        return f"{x:.3f}" if isinstance(x, (int, float)) else "n/a"
    for r in stats:
        print(f"{r['group']:24s} n={r['n']} median={r['median']} "
              f"Q1={r['q1']} Q3={r['q3']} robustSD={f3(r['robust_sd'])} "
              f"Sn={f3(r['sn'])} Qn={f3(r['qn'])} mean={f3(r['mean'])} "
              f"SD={f3(r['sd'])} range={r['min']}..{r['max']}")

    rows = song_rows()
    with open(ROOT / "analysis" / "song_transfer_comparison.csv", "w",
              newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n== songs through the integrated transfer ==")
    for r in rows:
        print(f"{r['name']:26s} centroid {r['centroid_raw']} -> "
              f"{r['centroid_anchor']} Hz (anchor), "
              f"share>=1500Hz {r['share1500_raw_pct']}% -> "
              f"{r['share1500_anchor_pct']}%, loss {r['loss_anchor_db']} dB; "
              f"Richards: centroid {r['centroid_richards']} Hz, "
              f"loss {r['loss_richards_db']} dB")


if __name__ == "__main__":
    main()
