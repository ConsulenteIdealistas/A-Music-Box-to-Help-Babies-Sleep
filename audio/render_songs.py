"""Music-box audition renders of the four repertoire candidates.

Synthesis: Python additive model of a music-box tine (inharmonic
partials 1 : 6.27 : 17.5 : 34.4, higher partials decaying faster) --
the same design as the earlier synth demo. This is an AUDITION engine;
the final engine decision (SuperCollider/Klank vs recorded) is separate.

Melody sources (see audio/SONGS.md for detail):
  brahms   -- Mutopia vocal line via musictheoryprint (Eb major),
              transposed to C major for the music box.
  yurikago -- published kalimba score (C major), melody line only.
  moldau   -- transcription trial by the AI (ear), E minor theme.
  vissi    -- transcription trial by the AI (ear), opening phrase.
Transcription trials are explicitly provisional: they stand or fall by
the user's ear check.

Usage: python -m audio.render_songs --out-dir <dir>
"""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path

SR = 44100
PARTIALS = [(1.0, 1.0, 2.8), (6.27, 0.32, 0.9), (17.5, 0.12, 0.35), (34.4, 0.05, 0.15)]

NOTE = {}
_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
for _oct in range(2, 8):
    for _i, _n in enumerate(_names):
        NOTE[f"{_n}{_oct}"] = 12 * (_oct + 1) + _i
NOTE.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})


def freq(name: str) -> float:
    if name.endswith("b") and len(name) > 2 or (len(name) == 2 and name[1] == "b"):
        base, octv = name[:-1], int(name[-1]) if name[-1].isdigit() else None
    midi = None
    if name in NOTE:
        midi = NOTE[name]
    else:  # e.g. "Eb5"
        letter, octv = name[:-1], int(name[-1])
        semis = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[letter[0]]
        if letter.endswith("b"):
            semis -= 1
        if letter.endswith("#"):
            semis += 1
        midi = 12 * (octv + 1) + semis
    return 440.0 * 2 ** ((midi - 69) / 12)


def add_note(buf: list[float], start_s: float, name: str, gain: float) -> None:
    f0 = freq(name)
    start = int(start_s * SR)
    dur = int(3.2 * SR)
    for ratio, amp, decay in PARTIALS:
        f = f0 * ratio
        if f > 16000:
            continue
        for i in range(dur):
            if start + i >= len(buf):
                return
            t = i / SR
            buf[start + i] += gain * amp * math.exp(-t / decay) * math.sin(2 * math.pi * f * t)


def render(events: list[tuple[float, str, float]], total_s: float) -> list[float]:
    buf = [0.0] * int(total_s * SR)
    for start, name, gain in events:
        add_note(buf, start, name, gain)
    return buf


def seq(notes: list[tuple[str, float]], beat_s: float, gain: float = 0.5):
    """notes: (name, beats). Returns (events, total_beats)."""
    events, t = [], 0.0
    for name, beats in notes:
        if name != "R":
            events.append((t * beat_s, name, gain))
        t += beats
    return events, t


def bass_line(chords: list[tuple[str, str]], bar_beats: float, beat_s: float):
    """One soft root+fifth arpeggio per bar."""
    events = []
    for i, (root, fifth) in enumerate(chords):
        t0 = i * bar_beats * beat_s
        events.append((t0, root, 0.16))
        events.append((t0 + bar_beats * beat_s * 0.5, fifth, 0.10))
    return events


# --- Brahms, Wiegenlied (Eb source transposed to C major, 3/4) ---
# Source pitch sequence (scale degrees in Eb): 
# 3 3 5 3 | 3 5 3 5 1' 7 6 | 6 5 2' 3' 4' 2' | 2' 3' 4' 2' 4' 7 6 5 7 |
# 1' 1' 1' 1' 6 4' 5 3 1' 4' 5 6 | 5 1' 1' 1' 6 4' 5 3 1' 4' 3 2 1
BRAHMS = [
    ("E5", 1), ("E5", 1), ("G5", 1), ("E5", 1), ("E5", 1), ("G5", 1),
    ("E5", 1), ("G5", 1), ("C6", 1.5), ("B5", 0.5), ("A5", 1),
    ("A5", 1), ("G5", 1), ("D6", 1), ("E6", 1), ("F6", 1), ("D6", 1),
    ("D6", 1), ("E6", 1), ("F6", 1), ("D6", 1), ("F6", 1), ("B5", 1), ("A5", 1), ("G5", 1), ("B5", 1),
    ("C6", 1), ("C6", 1), ("C6", 1), ("C6", 1), ("A5", 1), ("F6", 1), ("G5", 1), ("E5", 1), ("C6", 1), ("F6", 1), ("G5", 1), ("A5", 1),
    ("G5", 1), ("C6", 1), ("C6", 1), ("C6", 1), ("A5", 1), ("F6", 1), ("G5", 1), ("E5", 1), ("C6", 1), ("F6", 1), ("E5", 1), ("D5", 1), ("C5", 2),
]
BRAHMS_CHORDS = [("C4", "G4"), ("C4", "G4"), ("F4", "C5"), ("C4", "G4"),
                 ("F4", "C5"), ("C4", "G4"), ("C4", "G4"), ("F4", "C5"),
                 ("C4", "G4"), ("F4", "C5"), ("C4", "G4"), ("C4", "G4")]

# --- Yurikago no Uta (C major, 4/4; kalimba score melody) ---
YURIKAGO = [
    ("G5", 2), ("A5", 1), ("G5", 1), ("E5", 2), ("C5", 2),
    ("E5", 1), ("D5", 3),
    ("A4", 2), ("C5", 1), ("A4", 1), ("G4", 2), ("C5", 2),
    ("E5", 2), ("G5", 1), ("E5", 1), ("D5", 3), ("C5", 1),
    ("E5", 2), ("E5", 1), ("E5", 1), ("D5", 1), ("E5", 1), ("G5", 1), ("A5", 1), ("G5", 2),
    ("E5", 2), ("G5", 1), ("E5", 1), ("D5", 2), ("C5", 3),
]
YURIKAGO_CHORDS = [("C4", "G4"), ("C4", "G4"), ("F4", "C5"), ("C4", "G4"),
                   ("C4", "G4"), ("F4", "C5"), ("C4", "G4"), ("C4", "G4")]

# --- Moldau theme (E minor, 6/8; AI transcription trial) ---
MOLDAU = [
    ("B4", 1),
    ("E5", 2), ("F#5", 1), ("G5", 2), ("A5", 2), ("G5", 1), ("F#5", 2),
    ("E5", 2), ("F#5", 1), ("G5", 2), ("A5", 2), ("G5", 1), ("F#5", 2),
    ("E5", 2), ("D#5", 1), ("E5", 2), ("F#5", 2), ("D#5", 1), ("B4", 2),
    ("E5", 2), ("F#5", 1), ("G5", 2), ("A5", 2), ("B5", 1), ("A5", 2),
    ("G5", 2), ("F#5", 1), ("E5", 2), ("F#5", 2), ("D#5", 1), ("E5", 3),
]
MOLDAU_CHORDS = [("E3", "B3"), ("E3", "B3"), ("E3", "B3"), ("E3", "B3"),
                 ("A3", "E4"), ("E3", "B3"), ("E3", "B3"), ("E3", "B3")]

# --- Vissi d'arte (Eb major opening; AI transcription trial, in Eb) ---
VISSI = [
    ("Bb4", 2), ("C5", 1), ("D5", 1), ("Eb5", 3), ("D5", 1),
    ("C5", 2), ("D5", 1), ("Bb4", 2), ("C5", 1),
    ("Eb5", 2), ("D5", 1), ("C5", 1), ("D5", 2), ("Bb4", 2),
    ("Eb5", 2), ("F5", 1), ("Eb5", 1), ("D5", 2), ("C5", 1), ("D5", 1),
    ("Eb5", 4), ("R", 2),
]
VISSI_CHORDS = [("Eb3", "Bb3"), ("Eb3", "Bb3"), ("Ab3", "Eb4"), ("Eb3", "Bb3"),
                ("Eb3", "Bb3"), ("Ab3", "Eb4")]

SONGS = {
    "brahms": (BRAHMS, BRAHMS_CHORDS, 3, 60 / 63),
    "yurikago": (YURIKAGO, YURIKAGO_CHORDS, 4, 60 / 60),
    "moldau": (MOLDAU, MOLDAU_CHORDS, 6, 60 / 104),
    "vissi": (VISSI, VISSI_CHORDS, 4, 60 / 52),
}


def write_wav(path: Path, samples: list[float]) -> None:
    peak = max(1e-9, max(abs(x) for x in samples))
    scale = min(1.0, 0.89 / peak)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, x * scale)) * 32767))
            for x in samples))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (melody, chords, bar_beats, beat_s) in SONGS.items():
        events, total_beats = seq(melody, beat_s)
        events += bass_line(chords, bar_beats, beat_s)
        total_s = total_beats * beat_s + 3.5
        write_wav(out / f"{name}_musicbox.wav", render(events, total_s))
        print(f"{name}: {total_s:.0f}s")


if __name__ == "__main__":
    main()
