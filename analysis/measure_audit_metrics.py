"""Audit metrics for the ten finished WAVs: B (loudness) + C (spectral).

Implements the B and C layers of the measurement spec in
analysis/acoustic_evidence_audit_plan_2026-11-17.md (測定指標).
The A layer (device SPL) is not covered: it needs a calibrated
sound level meter, which the project does not have.

Pinned definitions (conventions, fixed here so the numbers are
reproducible; the audit plan requires the implementation parameters
of spectral metrics to be part of the definition):

B layer - ffmpeg ebur128 (ITU-R BS.1770 / EBU R128), peak=true:
  - LUFS-I, LRA and the true peak (dBTP) are taken from the
    filter's final Summary block.
  - max LUFS-M / max LUFS-S are the maxima of the per-frame log
    values over the whole file, fade-in/out included. Frames are
    logged every ~100 ms; M is the 400 ms momentary window and S
    the 3 s short-term window, both as computed by ffmpeg.
C layer - numpy:
  - WAV read as mono float64, 16-bit samples / 32768 (same reader
    convention as analysis.bed_integration.read_wav_mono).
  - STFT: 4096-sample Hann window (numpy.hanning), hop 2048
    (50% overlap), power spectrum |rFFT|^2 per frame; the frame
    power spectra are averaged over the whole file (mean power
    spectrum) and every spectral aggregate below uses it.
  - The DC bin is excluded from all spectral aggregates (project
    convention, see bed_integration.metrics).
  - 1/3-octave bands: nominal centres 25 Hz to 16 kHz, edges at
    centre * 2**(+-1/6). Band level = 10*log10(band power / total
    power) in dB, where total power is the mean power spectrum
    summed over all non-DC bins - i.e. the band levels are power
    shares and are independent of window length and file level.
  - Spectral centroid / bandwidth: power-weighted mean / standard
    deviation of frequency over the mean power spectrum.
  - Spectral flatness: geometric mean / arithmetic mean of the
    mean power spectrum over non-DC bins (0 = pure tone, 1 = white
    noise-like).
  - Roll-off frequency: smallest frequency at which the cumulative
    power reaches 85% of the total. The 85% figure is a convention
    (the librosa default), pinned here because the audit plan
    requires the percentage to be fixed before measuring.
  - Crest factor: 20*log10(sample peak / RMS), whole file.
  - RMS and sample peak are whole-file time-domain values.

Outputs: analysis/audit_metrics_2026-11-17.csv
Usage: python -m analysis.measure_audit_metrics
"""

from __future__ import annotations

import csv
import math
import re
import struct
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FILES = Path.home() / "workspace" / "your_files" / "lullaby-4songs"

TARGETS = [
    "mix_brahms_sox.wav",
    "mix_moldau_sox.wav",
    "mix_vissi_darte_sox.wav",
    "mix_yurikago_sox.wav",
    "mix_brahms_wiegenlied.wav",
    "mix_moldau_theme.wav",
    "mix_vissi_darte.wav",
    "mix_yurikago_no_uta.wav",
    "bed_only.wav",
    "bed_sox.wav",
]

FFT_N = 4096
HOP = FFT_N // 2
ROLLOFF_FRACTION = 0.85
BAND_CENTRES = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315,
                400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,
                4000, 5000, 6300, 8000, 10000, 12500, 16000]


def read_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        vals = np.array(struct.unpack(f"<{len(frames) // 2}h", frames),
                        dtype=np.float64) / 32768.0
        if w.getnchannels() == 2:
            vals = vals[::2]
        return vals, sr


def ebur128(path: Path) -> dict:
    """Run ffmpeg's ebur128 scanner and parse its stderr log."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    summary = out.split("Summary:", 1)[1]
    got = {}
    for key, pat in (("lufs_i", r"I:\s+(-?[\d.]+) LUFS"),
                     ("lra_lu", r"LRA:\s+(-?[\d.]+) LU"),
                     ("true_peak_dbtp", r"Peak:\s+(-?[\d.]+) dBFS")):
        m = re.search(pat, summary)
        got[key] = float(m.group(1)) if m else float("nan")
    frames = re.findall(r"M:\s*(-inf|-?[\d.]+)\s+S:\s*(-inf|-?[\d.]+)", out)
    mvals = [float(a) for a, _ in frames]
    svals = [float(b) for _, b in frames]
    got["lufs_m_max"] = max(mvals) if mvals else float("nan")
    got["lufs_s_max"] = max(svals) if svals else float("nan")
    return got


def mean_power_spectrum(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    win = np.hanning(FFT_N)
    acc = np.zeros(FFT_N // 2 + 1)
    count = 0
    for start in range(0, len(x) - FFT_N + 1, HOP):
        seg = x[start:start + FFT_N] * win
        acc += np.abs(np.fft.rfft(seg)) ** 2
        count += 1
    freqs = np.fft.rfftfreq(FFT_N, 1.0 / sr)
    return freqs, acc / max(count, 1)


def band_column(centre: float) -> str:
    label = str(centre).replace(".5", "p5").rstrip("0").rstrip(".") \
        if centre != int(centre) else str(int(centre))
    return f"band_{label}hz_db_rel_total"


def spectral(x: np.ndarray, sr: int) -> dict:
    freqs, power = mean_power_spectrum(x, sr)
    f, p = freqs[1:], power[1:]  # DC excluded
    total = p.sum()
    got = {}
    for c in BAND_CENTRES:
        lo, hi = c * 2 ** (-1 / 6), c * 2 ** (1 / 6)
        band = p[(f >= lo) & (f < hi)].sum()
        got[band_column(c)] = round(10.0 * math.log10(max(band / total, 1e-20)), 2)
    centroid = float((f * p).sum() / total)
    got["centroid_hz"] = round(centroid, 1)
    got["bandwidth_hz"] = round(float(np.sqrt(((f - centroid) ** 2 * p).sum() / total)), 1)
    got["flatness"] = round(float(np.exp(np.mean(np.log(np.maximum(p, 1e-300))))
                                  / np.mean(p)), 4)
    cum = np.cumsum(p)
    idx = int(np.searchsorted(cum, ROLLOFF_FRACTION * total))
    got["rolloff85_hz"] = round(float(f[min(idx, len(f) - 1)]), 1)
    return got


def main() -> None:
    rows = []
    for name in TARGETS:
        path = FILES / name
        x, sr = read_wav_mono(path)
        peak = float(np.max(np.abs(x)))
        rms = float(np.sqrt(np.mean(x ** 2)))
        row: dict = {"file": name,
                     "duration_s": round(len(x) / sr, 2),
                     "sample_rate_hz": sr}
        row.update(ebur128(path))
        row["sample_peak"] = round(peak, 5)
        row["sample_peak_dbfs"] = round(20 * math.log10(peak), 2)
        row["rms"] = round(rms, 5)
        row["rms_dbfs"] = round(20 * math.log10(rms), 2)
        row["crest_factor_db"] = round(20 * math.log10(peak / rms), 2)
        row.update(spectral(x, sr))
        rows.append(row)
        print(f"{name}: LUFS-I {row['lufs_i']}, dBTP {row['true_peak_dbtp']}, "
              f"rms {row['rms']}, peak {row['sample_peak']}, "
              f"centroid {row['centroid_hz']} Hz, rolloff85 {row['rolloff85_hz']} Hz")
    out = ROOT / "analysis" / "audit_metrics_2026-11-17.csv"
    tmp = out.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(out)  # 原子的に置き換える（Issue #12）
    print("wrote", out)


if __name__ == "__main__":
    main()
