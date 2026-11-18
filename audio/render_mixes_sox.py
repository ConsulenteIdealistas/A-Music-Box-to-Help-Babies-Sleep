"""Full mixes on the SoX bed (2026-11-17, expanding the Brahms
prototype in audio/render_bed_sox.py to all four songs).

STATUS (2026-11-18): cross-check only. The canonical pipeline is
audio/render_mix.py (user decision 2026-11-18: Python is the single
source of the deliverable mixes and bed). These SoX mixes exist to
verify the canonical renders against an independent mixdown path;
they are never the deliverables.

Recipe (identical for every song, Brahms included):
  bed    -- bed_sox.wav from audio/render_bed_sox.py (SoX-shaped
            flow + unchanged heartbeat stem, SoX mixdown, 2 s / 3 s
            fades). The fades live in the bed only; the music stem
            starts after 1 s of silence by construction, so the mix
            head is never abrupt.
  music  -- audio/render_mix.py's music_box() stem (Klank phrase
            looped with gaps, integrated transfer curve, GAIN_MUSIC),
            written unnormalised so the settled levels carry over.
  mix    -- `sox -m bed music` with `vol 2` (sox -m halves the sum),
            then render_mix.write_wav's peak rule: if the peak
            exceeds 0.89 the whole mix is scaled to 0.89, so the
            levels match the auditioned Python mixes exactly in
            rule. Only Vissi d'arte triggers it (raw peak 0.947);
            without the rule it would sit +0.53 dB above the
            Python mix the user auditioned.

Verification built in: the Brahms mix is rebuilt and compared
against the prototype file (peak / RMS / max sample difference),
and every mix is compared against the Python-bed mix of the same
song. The surge smoothing (2026-11-17) and the bed fades
(2026-11-18) were both ported back into render_mix.py, so the beds
now differ only in the shaping/mixdown implementation (SoX
`lowpass -1 250` and `sox -m` vs the Python one-pole and sum),
and the mixes should agree closely.

Usage: python -m audio.render_mixes_sox --dir <lullaby-4songs dir>
Expects <dir>/bed_sox.wav, <dir>/klank/<song>_klank.wav and the
Python mixes <dir>/mix_<song>.wav; writes <dir>/mix_<short>_sox.wav.
"""

from __future__ import annotations

import argparse
import math
import struct
import subprocess
import wave
from pathlib import Path

from audio.render_mix import DURATION_S, SR, music_box, read_wav_mono

SOX = str(Path.home() / "workspace" / "tools" / "sox")

SONGS = [
    ("brahms_wiegenlied", "brahms"),
    ("moldau_theme", "moldau"),
    ("vissi_darte", "vissi_darte"),
    ("yurikago_no_uta", "yurikago"),
]


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


def peak_rms(samples: list[float]) -> tuple[float, float]:
    peak = max(abs(x) for x in samples)
    rms = math.sqrt(sum(x * x for x in samples) / len(samples))
    return peak, rms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    args = ap.parse_args()
    d = Path(args.dir)
    tmp = d / "_sox_tmp"
    tmp.mkdir(exist_ok=True)
    n = int(DURATION_S * SR)
    bed = d / "bed_sox.wav"

    for song, short in SONGS:
        phrase = read_wav_mono(d / "klank" / f"{song}_klank.wav")
        stem = tmp / f"music_{short}.wav"
        write_wav16(stem, music_box(n, phrase))
        out = d / f"mix_{short}_sox.wav"
        rebuilt = None
        if short == "brahms" and out.exists():
            rebuilt = tmp / "mix_brahms_sox_rebuilt.wav"
        # NOTE: sox -m scales the sum by 1/2; `vol 2` restores it.
        target = rebuilt or out
        sox(["-m", str(bed), str(stem), str(target), "vol", "2"])
        # render_mix.write_wav's peak rule (see docstring).
        pk, _ = peak_rms(read_wav16(target))
        if pk > 0.89:
            scaled = tmp / f"mix_{short}_scaled.wav"
            sox([str(target), str(scaled), "vol", f"{0.89 / pk:.6f}"])
            scaled.replace(target)
        if rebuilt is not None:
            a, b = read_wav16(out), read_wav16(rebuilt)
            diff = max(abs(x - y) for x, y in zip(a, b))
            pa, ra = peak_rms(a)
            print(f"brahms prototype check: peak {pa:.4f} | RMS {ra:.5f} "
                  f"| max sample diff vs rebuilt {diff:.5f}")
            rebuilt.replace(out)
        p, r = peak_rms(read_wav16(out))
        pp, rp = peak_rms(read_wav16(d / f"mix_{song}.wav"))
        print(f"{short}: sox peak {p:.4f} RMS {r:.5f} | "
              f"python peak {pp:.4f} RMS {rp:.5f} | "
              f"RMS diff {20 * math.log10(r / rp):+.2f} dB")
    print("done")


if __name__ == "__main__":
    main()
