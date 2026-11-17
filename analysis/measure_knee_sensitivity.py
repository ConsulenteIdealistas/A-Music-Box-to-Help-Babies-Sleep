"""Knee sensitivity: what moves when the integrated-curve knee moves.

Applies the project's one-pole lowpass (audio/render_mix.py lowpass:
alpha = 1 - exp(-2*pi*f/SR), single pass, y starts at 0) at knee =
200 / 250 / 315 Hz to the four raw Klank stems and to bed_only.wav,
and measures each result with the same definitions as
analysis/measure_audit_metrics.py (imported, not re-implemented):
LUFS-I from ffmpeg ebur128 on a 16-bit WAV of the filtered signal,
spectral centroid and 1/3-octave band levels from the mean power
spectrum of that same 16-bit signal.

Caveat: the Klank stems are unfiltered, so for them the numbers are
the sensitivity of the music layer's knee itself. bed_only.wav is
the finished bed (its flow layer already passed the 250 Hz curve),
so for the bed this measures one additional pass, not the design
operation.

Outputs: analysis/knee_sensitivity_2026-11-17.csv
Usage: python -m analysis.measure_knee_sensitivity
"""

from __future__ import annotations

import csv
import struct
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis.measure_audit_metrics import ebur128, read_wav_mono, spectral  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FILES = Path.home() / "workspace" / "your_files" / "lullaby-4songs"

TARGETS = [
    "klank/brahms_wiegenlied_klank.wav",
    "klank/moldau_theme_klank.wav",
    "klank/vissi_darte_klank.wav",
    "klank/yurikago_no_uta_klank.wav",
    "bed_only.wav",
]
KNEES = [200, 250, 315]
BANDS = ["band_250hz_db_rel_total", "band_500hz_db_rel_total",
         "band_1000hz_db_rel_total", "band_2000hz_db_rel_total"]


def one_pole_lowpass(x: np.ndarray, sr: int, cutoff_hz: float) -> np.ndarray:
    a = 1.0 - float(np.exp(-2.0 * np.pi * cutoff_hz / sr))
    try:
        from scipy.signal import lfilter
        # y[n] = a*x[n] + (1-a)*y[n-1]  ==  y += a*(x - y), y0 = 0
        return lfilter([a], [1.0, -(1.0 - a)], x)
    except ImportError:
        y = 0.0
        out = np.empty_like(x)
        for i, v in enumerate(x):
            y += a * (v - y)
            out[i] = y
        return out


def write_wav16(path: Path, x: np.ndarray, sr: int) -> None:
    clipped = np.clip(x, -1.0, 32767.0 / 32768.0)
    ints = np.round(clipped * 32768.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(ints.tobytes())


def main() -> None:
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for name in TARGETS:
            src = FILES / name
            x, sr = read_wav_mono(src)
            for knee in KNEES:
                y = one_pole_lowpass(x, sr, knee)
                tmp = Path(td) / f"tmp_{knee}.wav"
                write_wav16(tmp, y, sr)
                loud = ebur128(tmp)
                q, sr2 = read_wav_mono(tmp)  # same 16-bit signal for C layer
                spec = spectral(q, sr2)
                row = {"file": name, "knee_hz": knee,
                       "lufs_i": loud["lufs_i"],
                       "centroid_hz": spec["centroid_hz"]}
                for b in BANDS:
                    row[b] = spec[b]
                rows.append(row)
                print(f"{name} @ {knee} Hz: LUFS-I {row['lufs_i']}, "
                      f"centroid {row['centroid_hz']} Hz, "
                      f"1k band {row['band_1000hz_db_rel_total']} dB")
    out = ROOT / "analysis" / "knee_sensitivity_2026-11-17.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out)


if __name__ == "__main__":
    main()
