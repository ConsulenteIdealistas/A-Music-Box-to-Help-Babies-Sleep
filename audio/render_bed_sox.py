"""Bed prototype with SoX doing what SoX can do (2026-11-17).

STATUS (2026-11-18): cross-check only. The canonical pipeline is
audio/render_mix.py (user decision 2026-11-18: Python is the single
source of the deliverable mixes and bed). The bed fades introduced
here were ported into render_mix.py, so this script's remaining
role is to verify that an independent shaping/mixdown path (SoX
`lowpass -1 250`, `sox -m`) agrees with the canonical render.
Its outputs are never the deliverables.

Motivation (user): let SoX handle the parts of the heartbeat/flow
mix it is good at, and make the bed smoother. Division of labour:

  Python  - seeded white noise (reproducibility: render_mix.py's
            fixed seed), the heartbeat stem (unchanged samples),
            and the heartbeat-synchronous surge / slow swell
            envelopes (SoX has no arbitrary-envelope tool). The
            surge envelope is smoothed with a 25 ms one-pole: the
            raw envelope steps by 0.44 at every beat wrap (an
            audible discontinuity each 0.857 s), the smoothed one
            attacks over ~25 ms instead.
  SoX     - the transfer-curve shaping (one-pole lowpass at
            250 Hz, `lowpass -1 250`, replacing the Python one-pole),
            the stem mixdown (sox -m), and fade-in/out so the bed
            no longer starts/stops abruptly.

  Tested and dropped: a gentle slow compand on the flow changed
  the measured texture roughness not at all (1.61 dB at 50 ms
  windows, 1.24 dB at 250 ms, with and without), so it is not
  part of the recipe — no unmeasurable processing.

The flow level is still set in Python to FLOW_RMS_PER_GAIN *
GAIN_FLOW after shaping, so the settled level structure is
unchanged. The script measures both beds (band regression slopes,
short-term level roughness) so the smoothing is checked, not hoped.

Usage: python -m audio.render_bed_sox --out-dir <dir>
Outputs: bed_sox.wav (and prints the comparison vs the current bed).
"""

from __future__ import annotations

import argparse
import math
import random
import struct
import subprocess
import wave
from pathlib import Path

from audio.render_mix import (FLOW_RMS_PER_GAIN, GAIN_FLOW, SEED, SR,
                              DURATION_S, HEART_BPM, heartbeat)

SOX = str(Path.home() / "workspace" / "tools" / "sox")
KNEE = "250"


def write_wav16(path: Path, samples: list[float]) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, x)) * 32767))
            for x in samples))


def read_wav16(path: Path) -> list[float]:
    with wave.open(str(path), "rb") as w:
        frames = w.readframes(w.getnframes())
        return [v / 32768.0 for v in struct.unpack(f"<{len(frames) // 2}h", frames)]


def sox(args: list[str]) -> None:
    r = subprocess.run([SOX] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"sox failed: {args}\n{r.stderr[-400:]}")


def band_slope(samples: list[float], lo: float, hi: float) -> float:
    """Octave-band regression slope (dB/oct) between band centres,
    same estimator family as the project's earlier bed checks."""
    import numpy as np
    x = np.array(samples)
    n = 8192
    win = np.hanning(n)
    acc = np.zeros(n // 2 + 1)
    cnt = 0
    for s in range(0, len(x) - n + 1, n // 2):
        acc += np.abs(np.fft.rfft(x[s:s + n] * win)) ** 2
        cnt += 1
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    power = acc / max(cnt, 1)
    centres, levels = [], []
    f = 125.0
    while f <= 6400:
        m = (freqs >= f / math.sqrt(2)) & (freqs < f * math.sqrt(2))
        centres.append(f)
        levels.append(10 * math.log10(max(power[m].sum(), 1e-20)))
        f *= 2
    pts = [(math.log2(c), l) for c, l in zip(centres, levels) if lo <= c <= hi]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    return sum((a - mx) * (b - my) for a, b in pts) / sum((a - mx) ** 2 for a in xs)


def roughness_db(samples: list[float], win_s: float = 0.05) -> float:
    """SD of short-term RMS levels (dB) — the noise texture's jitter."""
    w = int(win_s * SR)
    lv = []
    for s in range(0, len(samples) - w + 1, w):
        seg = samples[s:s + w]
        r = math.sqrt(sum(v * v for v in seg) / w)
        if r > 1e-6:
            lv.append(20 * math.log10(r))
    m = sum(lv) / len(lv)
    return math.sqrt(sum((v - m) ** 2 for v in lv) / len(lv))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_sox_tmp"
    tmp.mkdir(exist_ok=True)
    n = int(DURATION_S * SR)

    # Python: seeded white noise (same generator as render_mix).
    rng = random.Random(SEED)
    white = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    write_wav16(tmp / "white.wav", white)

    # SoX: integrated-curve shaping.
    sox([str(tmp / "white.wav"), str(tmp / "shaped.wav"),
         "lowpass", "-1", KNEE])
    shaped = read_wav16(tmp / "shaped.wav")

    # Python: surge (25 ms-smoothed) / swell envelopes + settled
    # RMS level (unchanged rule).
    period = 60.0 / HEART_BPM
    surge_raw = []
    for i in range(n):
        t = i / SR
        phase = ((t - 0.3) % period) / period
        surge_raw.append(0.55 + 0.45 * math.exp(-phase * 4.0))
    a = 1.0 - math.exp(-1.0 / (0.025 * SR))
    surge, y = [], surge_raw[-1]
    for v in surge_raw:
        y += a * (v - y)
        surge.append(y)
    env = []
    for i, x in enumerate(shaped):
        t = i / SR
        swell = 1.0 + 0.10 * math.sin(2 * math.pi * 0.05 * t)
        env.append(x * surge[i] * swell)
    rms = math.sqrt(sum(v * v for v in env) / len(env))
    scale = FLOW_RMS_PER_GAIN * GAIN_FLOW / rms
    flow = [v * scale for v in env]
    write_wav16(tmp / "flow.wav", flow)
    write_wav16(tmp / "heart.wav", heartbeat(n))

    # SoX: mixdown + fades. NOTE: sox -m scales the sum by 1/2
    # (one over the input count), so `vol 2` restores the true sum;
    # the stems' peaks (0.09 + 0.03) leave ample headroom.
    sox(["-m", str(tmp / "heart.wav"), str(tmp / "flow.wav"),
         str(out / "bed_sox.wav"), "vol", "2", "fade", "t", "2", "0", "3"])

    # Compare against the current bed (render_mix's bed_only render).
    from audio.render_mix import womb_flow
    cur_flow = womb_flow(n)
    cur = [a + b for a, b in zip(heartbeat(n), cur_flow)]
    new = read_wav16(out / "bed_sox.wav")
    for label, sig in (("current bed", cur), ("sox bed", new)):
        r = math.sqrt(sum(v * v for v in sig) / len(sig))
        print(f"{label}: RMS {r:.5f} | slope 200-800 "
              f"{band_slope(sig, 200, 800):+.2f} | 800-3200 "
              f"{band_slope(sig, 800, 3200):+.2f} dB/oct")
    # Texture roughness is judged on the flow layer alone, mid-file
    # (the heartbeat's gating and the bed's fades would confound it).
    mid = slice(int(5 * SR), int(55 * SR))
    for label, sig in (("current flow", cur_flow), ("sox flow", flow)):
        print(f"{label}: slope 200-800 {band_slope(sig, 200, 800):+.2f} | "
              f"800-3200 {band_slope(sig, 800, 3200):+.2f} dB/oct | "
              f"roughness (mid) {roughness_db(sig[mid]):.2f} dB")
    print(f"wrote {out}/bed_sox.wav")


if __name__ == "__main__":
    main()
