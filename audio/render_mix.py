"""Offline render of the 3-layer mix for audition.

CANONICAL PIPELINE (user decision 2026-11-18): this script is the
single source of the deliverable mixes and bed. The SoX variants
(audio/render_bed_sox.py, audio/render_mixes_sox.py) are retained
as an independent cross-check only; their outputs are never the
deliverables. The bed fades that originated in the SoX recipe were
ported here (FADE_IN_S / FADE_OUT_S below), so the canonical
render carries them natively.

Layers:
  1. Music box  -- the confirmed SuperCollider/Klank render
     (audio/musicbox_supercollider_full.wav), looped with gaps and run
     through the integrated womb transfer curve (below).
  2. Heartbeat  -- maternal heartbeat, lub-dub pair of low sine bursts.
  3. Womb flow  -- noise shaped to the integrated transfer curve
     (flat at/below 250 Hz, -6 dB/oct above) whose amplitude surges
     with each heartbeat (maternal blood flow is heartbeat-synchronous
     by design; this is NOT ocean waves). The curve integrates the
     two evidence rounds -- see audio/bed_integration_2026-11-17.md:
     the slope is Gerhardt 1990's stated 6 dB/oct (the same value the
     user's ear picked as brown in round 1), and the flat low shelf
     replaces brown's unbounded low-frequency rise. The flow level
     follows FLOW_RMS_PER_GAIN * GAIN_FLOW, so shaping changes never
     move the level. Bed gains were softened on the user's listening
     judgement (2026-11-15: -4 dB; 2026-11-17: -4 dB, then halved)
     because the bed asserted itself too much against the music box.

Parameter bases:
  HEART_BPM = 70        midpoint of the typical maternal resting range
                        60-80; user decision 2026-11-15: BPM is a
                        variable parameter, not a fixed value. The
                        entrainment curve (85 -> 65) sketched in
                        app/app.js is a later step, not applied here.
  BEAT_FREQ_HZ = 55     low sine burst in the style of measured heart
                        sounds. The user confirmed 2026-11-17 that this
                        basis is fine (an image-based choice would also
                        have been acceptable); what needed changing
                        was the bed level, not the heartbeat character.
  LUB_DUB_MS = 280      typical systolic interval at rest.
  TRANSFER_KNEE_HZ = 250  the integrated transfer curve's corner
                        (Gerhardt 1990): flat at/below, -6 dB/oct
                        above. One one-pole lowpass at this frequency
                        realizes the curve for both the flow layer
                        (shaping white noise) and the music-box layer
                        (replacing the provisional 1500 Hz, 12 dB/oct
                        womb filter). The curve's +3.5 dB low shelf is
                        a level offset, absorbed by the layer gains.
  FLOW_CUTOFF_HZ = 400  retired flow shaping (pre-2026-11-17), kept
                        only as the reference definition for
                        FLOW_RMS_PER_GAIN and audio/render_bed_variants.py.
  FADE_IN_S = 2.0, FADE_OUT_S = 3.0  linear fades on the bed
                        (heartbeat + flow), adopted from the SoX bed
                        recipe (audio/render_bed_sox.py, `fade t 2 0 3`)
                        so the bed neither starts nor stops abruptly.
                        The SoX 't' shape was measured 2026-11-18 to be
                        exactly linear, so a linear ramp reproduces it.
                        Applied to the bed only, as in the SoX chain;
                        the music stem keeps its own 1 s offset.
Noise uses a fixed seed so anyone re-running this script gets the
identical render. Python standard library only.

Usage: python -m audio.render_mix --out-dir <dir>
Outputs: mix_3layer.wav, bed_only.wav (heartbeat + flow).
With --phrases-dir <dir>: renders bed_only.wav plus one deliverable
mix_<song>.wav per <song>_klank.wav phrase found in <dir> (the
four-song deliverable set), instead of mix_3layer.wav.
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
BEAT_FREQ_HZ = 55.0  # measured-style heartbeat tone (see docstring)
FLOW_CUTOFF_HZ = 400.0
# RMS of the retired 400 Hz x3 flow per unit GAIN_FLOW: measured
# 2026-11-17 as 0.014076 at GAIN_FLOW = 0.16 (same seed and envelope),
# divided by 0.16. The shaped flow is scaled to
# FLOW_RMS_PER_GAIN * GAIN_FLOW, so GAIN_FLOW sets the level
# whatever shaping the flow layer uses.
FLOW_RMS_PER_GAIN = 0.087975
TRANSFER_KNEE_HZ = 250.0
SEED = 20261115
SURGE_SMOOTH_S = 0.025  # surge envelope smoothing (25 ms one-pole).
                        # The raw surge jumps by 0.442 at each beat
                        # wrap (measured 2026-11-17 in the SoX bed
                        # prototype); the smoothing removes that step.
                        # Same treatment as audio/render_bed_sox.py
                        # and app/app.js (SURGE_SMOOTH_S).

GAIN_HEART = 0.10  # softened on listening judgement: 0.50 -> 0.32
                   # (2026-11-15) -> 0.20 (2026-11-17, -4 dB) -> 0.10
                   # (2026-11-17, halved at the user's direction)
GAIN_FLOW = 0.05  # 0.26 -> 0.16 -> 0.10 -> 0.05, same steps as GAIN_HEART
GAIN_MUSIC = 3.31  # was 1.10 with the provisional 1500 Hz filter.
                   # Raised 2026-11-17 (x3.01, measured) to compensate
                   # the integrated transfer curve's insertion loss, so
                   # the bed/music balance settled by listening
                   # (bed -10.4 dB vs music, after the halving) is
                   # preserved while only the shape changes.
PHRASE_GAP_S = 4.5  # silence between music-box phrases
FADE_IN_S = 2.0   # bed fade-in (linear), from the SoX bed recipe
FADE_OUT_S = 3.0  # bed fade-out (linear), same source; see docstring


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
    """White noise shaped to the integrated transfer curve (one-pole
    lowpass at TRANSFER_KNEE_HZ: flat at/below 250 Hz, -6 dB/oct
    above), surging with each heartbeat. The shaped flow is scaled
    to FLOW_RMS_PER_GAIN * GAIN_FLOW, so GAIN_FLOW sets the level
    and the shape stays the integrated curve at any gain."""
    rng = random.Random(SEED)
    white = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    smooth = lowpass(white, TRANSFER_KNEE_HZ, passes=1)
    period = 60.0 / HEART_BPM
    surge_raw = []
    for i in range(n):
        t = i / SR
        phase = ((t - 0.3) % period) / period
        surge_raw.append(0.55 + 0.45 * math.exp(-phase * 4.0))  # pulse after each beat
    # Smooth the surge with a 25 ms one-pole (periodic start: the
    # filter state begins at the last sample, as in render_bed_sox.py).
    a = 1.0 - math.exp(-1.0 / (SURGE_SMOOTH_S * SR))
    surge, y = [], surge_raw[-1]
    for v in surge_raw:
        y += a * (v - y)
        surge.append(y)
    out = []
    for i, x in enumerate(smooth):
        t = i / SR
        swell = 1.0 + 0.10 * math.sin(2 * math.pi * 0.05 * t)
        out.append(x * surge[i] * swell)
    rms = math.sqrt(sum(x * x for x in out) / len(out))
    scale = FLOW_RMS_PER_GAIN * GAIN_FLOW / rms
    return [x * scale for x in out]


def bed(n: int) -> list[float]:
    """The canonical bed: heartbeat + womb flow with the linear
    FADE_IN_S / FADE_OUT_S fades applied (the fades live in the bed
    only, exactly as in the SoX recipe they were adopted from).
    Every consumer that needs the bed as it appears in the mixes
    (e.g. analysis/measure_four_songs.py) must use this function,
    never an unfaded heartbeat + flow sum."""
    out = [a + b for a, b in zip(heartbeat(n), womb_flow(n))]
    total = n / SR
    for i in range(n):
        t = i / SR
        g = min(1.0, t / FADE_IN_S, (total - t) / FADE_OUT_S)
        out[i] *= g
    return out


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
    filtered = lowpass(phrase, TRANSFER_KNEE_HZ, passes=1)  # integrated curve
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
    ap.add_argument(
        "--phrases-dir",
        default=None,
        help="render the deliverable set: bed_only.wav plus one "
             "mix_<song>.wav per <song>_klank.wav in this directory",
    )
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = int(DURATION_S * SR)
    bed_samples = bed(n)
    write_wav(out_dir / "bed_only.wav", bed_samples)
    if args.phrases_dir:
        phrases = sorted(Path(args.phrases_dir).glob("*_klank.wav"))
        if not phrases:
            raise SystemExit(f"no *_klank.wav phrases in {args.phrases_dir}")
        for p in phrases:
            song = p.name[: -len("_klank.wav")]
            phrase = read_wav_mono(p)
            mix = [a + b for a, b in zip(bed_samples, music_box(n, phrase))]
            write_wav(out_dir / f"mix_{song}.wav", mix)
            print(f"wrote {out_dir}/mix_{song}.wav ({DURATION_S:.0f}s)")
        print(f"wrote {out_dir}/bed_only.wav ({DURATION_S:.0f}s)")
    else:
        phrase = read_wav_mono(Path(args.music))
        mix = [a + b for a, b in zip(bed_samples, music_box(n, phrase))]
        write_wav(out_dir / "mix_3layer.wav", mix)
        print(f"wrote {out_dir}/mix_3layer.wav and bed_only.wav ({DURATION_S:.0f}s each)")


if __name__ == "__main__":
    main()
