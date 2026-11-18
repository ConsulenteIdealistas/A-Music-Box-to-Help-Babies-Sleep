"""Measure the four finished songs: Python spectra + SoX statistics.

Pipeline that produced the files (each tool in its project role):
  SuperCollider/Klank  - the four music-box phrases, rendered from
                         the MusicXML scores (audio/render_klank.py)
  Python               - the 3-layer mixes (audio/render_mix.py:
                         integrated transfer curve on the music,
                         heartbeat + flow bed at the settled gains)
  SoX                  - independent level statistics on the same
                         files (this script shells out to sox stat)
  R (robustbase)       - analysis/four_songs_stats.R cross-checks
                         the Python/SoX agreement and summarises
                         across songs

Measurements here (Python, numpy): octave-band levels and spectral
centroid of each raw phrase and each final mix (project method:
8192-point Hann, 50% overlap), time-domain RMS of both, and the
bed/music stem balance recomputed from render_mix's own layer
functions (same seed, so the stems are the ones in the mixes).

Outputs: analysis/four_songs_measurements.csv
Usage: python -m analysis.measure_four_songs
"""

from __future__ import annotations

import csv
import math
import re
import subprocess
from pathlib import Path

import numpy as np

from analysis.bed_integration import (BAND_CENTERS, avg_power_spectrum,
                                      band_levels, metrics, read_wav_mono)
from audio.render_mix import SR, bed, music_box

ROOT = Path(__file__).resolve().parent.parent
FILES = Path.home() / "workspace" / "your_files" / "lullaby-4songs"
SOX = str(Path.home() / "workspace" / "tools" / "sox")
SONGS = ["brahms_wiegenlied", "moldau_theme", "vissi_darte", "yurikago_no_uta"]


def sox_stat(path: Path) -> dict:
    out = subprocess.run([SOX, str(path), "-n", "stat"],
                         capture_output=True, text=True).stderr
    got = {}
    for key, pat in (("peak", r"Maximum amplitude:\s+([\d.]+)"),
                     ("rms", r"RMS\s+amplitude:\s+([\d.eE+-]+)"),
                     ("length_s", r"Length \(seconds\):\s+([\d.]+)")):
        m = re.search(pat, out)
        got[key] = float(m.group(1)) if m else float("nan")
    return got


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2)))


def main() -> None:
    n = int(60.0 * SR)
    bed_rms = rms(np.array(bed(n)))  # canonical bed (fades included)
    rows = []
    for name in SONGS:
        raw_path = FILES / "klank" / f"{name}_klank.wav"
        mix_path = FILES / f"mix_{name}.wav"
        raw, sr = read_wav_mono(raw_path)
        mix, _ = read_wav_mono(mix_path)
        row: dict = {"song": name}
        for label, sig in (("raw", raw), ("mix", mix)):
            freqs, power = avg_power_spectrum(sig, sr)
            bands = band_levels(freqs, power)
            for c in BAND_CENTERS:
                row[f"band_{c}_{label}"] = round(bands[c], 2)
            m = metrics(freqs, power)
            row[f"centroid_{label}"] = round(m["centroid_hz"])
            row[f"share1500_{label}"] = round(m["share_ge_1500_pct"], 2)
            row[f"rms_{label}_py"] = round(rms(sig), 5)
        phrase, _ = read_wav_mono(raw_path)
        stem = np.array(music_box(n, list(phrase)))
        row["rms_musicstem_py"] = round(rms(stem), 5)
        row["rms_bed_py"] = round(bed_rms, 5)
        row["balance_bed_music_db"] = round(
            20 * math.log10(bed_rms / rms(stem)), 2)
        # Balance while the music is actually sounding: the stem's
        # 4.5 s phrase gaps dilute its full-window RMS, so also
        # measure over the phrase windows only (same placement as
        # render_mix.music_box: start 1.0 s, step = phrase + gap).
        from audio.render_mix import PHRASE_GAP_S
        mask = np.zeros(n, dtype=bool)
        pos = int(1.0 * SR)
        step = len(phrase) + int(PHRASE_GAP_S * SR)
        while pos < n:
            mask[pos:min(n, pos + len(phrase))] = True
            pos += step
        row["balance_active_db"] = round(
            20 * math.log10(bed_rms / rms(stem[mask])), 2)
        for label, p in (("raw", raw_path), ("mix", mix_path)):
            st = sox_stat(p)
            row[f"peak_{label}_sox"] = st["peak"]
            row[f"rms_{label}_sox"] = round(st["rms"], 5)
        rows.append(row)
        print(f"{name}: centroid {row['centroid_raw']} -> "
              f"{row['centroid_mix']} Hz, balance "
              f"{row['balance_bed_music_db']} dB, "
              f"rms py/sox mix {row['rms_mix_py']}/{row['rms_mix_sox']}")
    out = ROOT / "analysis" / "four_songs_measurements.csv"
    tmp = out.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(out)  # 原子的に置き換える（Issue #12）
    print("wrote", out)


if __name__ == "__main__":
    main()
