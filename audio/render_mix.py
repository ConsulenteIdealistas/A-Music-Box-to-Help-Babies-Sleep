"""Offline render of the 3-layer mix for audition (PROVISIONAL parameters).

Layers:
  1. Music box  -- the confirmed SuperCollider/Klank render
     (audio/musicbox_supercollider_full.wav), looped with gaps and run
     through the provisional womb filter.
  2. Heartbeat  -- maternal heartbeat, lub-dub pair of low sine bursts.
  3. Womb flow  -- brown noise whose amplitude surges with each
     heartbeat (maternal blood flow is heartbeat-synchronous by design;
     this is NOT ocean waves). Brown (-6 dB/oct) was adopted on
     2026-11-17 by the user's listening decision: the extraction could
     not settle brown vs pink (Attenuation n=5), so the slope is a
     design judgement, not a literature value -- see
     audio/noise_target_2026-11-16.md. The flow level is matched to
     the previous (400 Hz x3 lowpass) flow, so adoption changed only
     the spectrum, not the level.

Parameter bases:
  HEART_BPM = 70        midpoint of the typical maternal resting range
                        60-80; user decision 2026-11-15: BPM is a
                        variable parameter, not a fixed value. The
                        entrainment curve (85 -> 65) sketched in
                        app/app.js is a later step, not applied here.
  BEAT_FREQ_HZ = 55     image-based choice (user decision 2026-11-17):
                        the heartbeat tone does NOT have to reproduce
                        measured heart-sound spectra; it is set by the
                        intended womb image and listening impression.
  LUB_DUB_MS = 280      typical systolic interval at rest.
  WOMB_FILTER_HZ = 1500, 12 dB/oct -- the standing provisional womb
                        filter for the music-box layer.
  FLOW_CUTOFF_HZ = 400  retired flow shaping (pre-2026-11-17), kept
                        only as the reference definition for
                        FLOW_REF_RMS and audio/render_bed_variants.py.
Noise uses a fixed seed so anyone re-running this script gets the
identical render. Python standard library only.

Usage: python -m audio.render_mix --out-dir <dir>
Outputs: mix_3layer.wav, bed_only.wav (heartbeat + flow).
"""

from __future__ import annotations

import argparse
import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
DURATION_S = 60.0

HEART_BPM = 70.0
LUB_DUB_MS = 280.0
BEAT_FREQ_HZ = 55.0  # image-based (see docstring), not a measured value
FLOW_CUTOFF_HZ = 400.0
# RMS of the retired 400 Hz x3 flow (same seed, envelope and gains),
# measured 2026-11-17. The brown flow is scaled to this so adopting
# brown changed the spectrum only, not the level.
FLOW_REF_RMS = 0.014076
WOMB_FILTER_HZ = 1500.0
SEED = 20261115

GAIN_HEART = 0.32  # bed softened 2026-11-15 after first audition (was 0.50)
GAIN_FLOW = 0.16  # was 0.26
GAIN_MUSIC = 1.10
PHRASE_GAP_S = 4.5  # silence between music-box phrases


def one_pole_alpha(cutoff_hz: float) -> float:
    return 1.0 - math.exp(-2.0 * math.pi * cutoff_hz / SR)


def lowpass(samples: list[float], cutoff_hz: float, passes: int = 1) -> list[float]:
    a = one_pole_alpha(cutoff_hz)
    out = samples
    for _ in range(passes):
        res = []
        y = 0.0
        for x in out:
            y += a * (x - y)
            res.append(y)
        out = res
    return out


def heartbeat(n: int) -> list[float]:
    out = [0.0] * n
    period = 60.0 / HEART_BPM
    t = 0.3  # first beat offset
    while t < DURATION_S:
        for delay, amp in ((0.0, 1.0), (LUB_DUB_MS / 1000.0, 0.55)):
            start = int((t + delay) * SR)
            length = int(0.16 * SR)
            for i in range(length):
                if start + i >= n:
                    break
                tt = i / SR
                env = math.exp(-tt * 22.0)
                out[start + i] += amp * env * math.sin(2 * math.pi * BEAT_FREQ_HZ * tt)
        t += period
    return [x * GAIN_HEART for x in out]


def womb_flow(n: int) -> list[float]:
    """Brown noise (-6 dB/oct) by leaky integration of white noise,
    surging with each heartbeat. Scaled to FLOW_REF_RMS so the level
    matches the retired lowpassed flow; only the spectrum changed
    when brown was adopted (2026-11-17)."""
    rng = random.Random(SEED)
    white = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    smooth = []
    y = 0.0
    for x in white:
        y = 0.999 * y + x  # leak keeps the random walk bounded
        smooth.append(y)
    period = 60.0 / HEART_BPM
    out = []
    for i, x in enumerate(smooth):
        t = i / SR
        phase = ((t - 0.3) % period) / period
        surge = 0.55 + 0.45 * math.exp(-phase * 4.0)  # pulse after each beat
        swell = 1.0 + 0.10 * math.sin(2 * math.pi * 0.05 * t)
        out.append(x * surge * swell * GAIN_FLOW * 2.2)
    rms = math.sqrt(sum(x * x for x in out) / len(out))
    scale = FLOW_REF_RMS / rms
    return [x * scale for x in out]


def read_wav_mono(path: Path) -> list[float]:
    with wave.open(str(path), "rb") as w:
        assert w.getsampwidth() == 2 and w.getframerate() == SR
        frames = w.readframes(w.getnframes())
        vals = struct.unpack(f"<{len(frames) // 2}h", frames)
        ch = w.getnchannels()
        if ch == 2:
            vals = vals[::2]
        return [v / 32768.0 for v in vals]


def music_box(n: int, phrase: list[float]) -> list[float]:
    filtered = lowpass(phrase, WOMB_FILTER_HZ, passes=2)  # ~12 dB/oct
    out = [0.0] * n
    step = len(filtered) + int(PHRASE_GAP_S * SR)
    pos = int(1.0 * SR)
    while pos < n:
        for i, x in enumerate(filtered):
            if pos + i >= n:
                break
            out[pos + i] += x * GAIN_MUSIC
        pos += step
    return out


def write_wav(path: Path, samples: list[float]) -> None:
    peak = max(1e-9, max(abs(x) for x in samples))
    scale = min(1.0, 0.89 / peak)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, x * scale)) * 32767))
            for x in samples
        )
        w.writeframes(frames)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--music",
        default=str(Path(__file__).with_name("musicbox_supercollider_full.wav")),
    )
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = int(DURATION_S * SR)
    bed = [a + b for a, b in zip(heartbeat(n), womb_flow(n))]
    phrase = read_wav_mono(Path(args.music))
    mix = [a + b for a, b in zip(bed, music_box(n, phrase))]
    write_wav(out_dir / "bed_only.wav", bed)
    write_wav(out_dir / "mix_3layer.wav", mix)
    print(f"wrote {out_dir}/mix_3layer.wav and bed_only.wav ({DURATION_S:.0f}s each)")


if __name__ == "__main__":
    main()
