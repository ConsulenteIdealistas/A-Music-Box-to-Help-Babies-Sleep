"""Render the repertoire with SuperCollider/Klank (the engine that won
the 2026-11-12 audition) in non-realtime mode.

Imports the note data from audio.render_songs, generates one .scd per
song, and runs sclang headless. Klank spec is the confirmed one from
the original demo: partial ratios 1 : 6.267 : 17.548 : 34.386,
amps 1 : 0.32 : 0.12 : 0.05, ring times 4.0 / 0.45 / 0.18 / 0.09 s.

Usage: python -m audio.render_klank --out-dir <dir>
Requires: sclang + scsynth on PATH (see TOOLS.md for the install recipe).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from audio.render_songs import SONGS, freq  # noqa: E402

DEF = """(
var defsDir = "/tmp/scdef_klank";
File.mkdir(defsDir);
SynthDef(\\mbox, { arg freq = 1318, amp = 0.4;
    var sig = Klank.ar(`[[1, 6.267, 17.548, 34.386], [1.0, 0.32, 0.12, 0.05], [4.0, 0.45, 0.18, 0.09]],
        Impulse.ar(0), freqscale: freq);
    Out.ar(0, sig * amp);
}).writeDefFile(defsDir);
Score.recordNRT(
    [
        [0.0, ['/d_load', defsDir +/+ "mbox.scsyndef"]],
EVENTS
        [ENDTIME, ['/c_set', 0, 0]]
    ],
    "/tmp/score_klank.osc",
    "OUTFILE",
    headerFormat: "WAV",
    sampleRate: 44100,
    options: ServerOptions.new.numOutputBusChannels_(1)
);
"RENDER_DONE".postln;
0.exit;
)
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, song in SONGS.items():
        lines, node = [], 1000
        for start, note, gain in sorted(song["events"]):
            g = gain * 0.76 if gain > 0.2 else gain * 0.8
            lines.append(
                f"        [{start:.3f}, ['/s_new', 'mbox', {node}, 0, 0, "
                f"'freq', {freq(note):.2f}, 'amp', {g:.3f}]],"
            )
            node += 1
        total_s = song["total_s"] + 1.5
        scd = (
            DEF.replace("EVENTS", "\n".join(lines))
            .replace("ENDTIME", f"{total_s:.2f}")
            .replace("OUTFILE", str(out / f"{name}_klank.wav"))
        )
        scd_path = Path(f"/tmp/render_{name}.scd")
        scd_path.write_text(scd)
        env = {"QT_QPA_PLATFORM": "offscreen", "QTWEBENGINE_DISABLE_SANDBOX": "1"}
        import os

        r = subprocess.run(
            ["sclang", str(scd_path)],
            capture_output=True, text=True, timeout=600,
            env={**os.environ, **env},
        )
        ok = (out / f"{name}_klank.wav").exists()
        print(f"{name}: {'ok' if ok else 'FAILED'}")
        if not ok:
            print(r.stdout[-500:], r.stderr[-500:])


if __name__ == "__main__":
    main()
