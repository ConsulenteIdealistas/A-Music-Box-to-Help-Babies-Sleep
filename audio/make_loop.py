"""Make seamless loop versions of the rendered song WAVs.

The Klank renders end with a few seconds of decay into digital
silence. A loop file keeps everything up to (last audible sample +
BREATH seconds of that silence), snapped to a zero crossing, so the
loop join is silence -> first attack, exactly like the song's own
start: no click, no chopped decay, no synthetic padding.

Usage:
    python3 -m audio.make_loop --in-dir DIR --out-dir DIR
Reads every *.wav in --in-dir (except *_loop.wav) and writes
<name>_loop.wav to --out-dir. Standard library only.
"""
import argparse
import glob
import os
import wave
from array import array

THRESHOLD = 33        # int16 amplitude ~0.001 (-60 dB): last audible sample
BREATH_SEC = 1.0      # silence kept after the last audible sample


def read_wav(path):
    with wave.open(path, "rb") as w:
        params = w.getparams()
        frames = w.readframes(w.getnframes())
    samples = array("h")
    samples.frombytes(frames)
    return params, samples


def loop_end_index(samples, channels, sr):
    # last frame whose any channel exceeds the threshold
    last = -1
    for i in range(len(samples) - 1, -1, -1):
        if abs(samples[i]) > THRESHOLD:
            last = i // channels
            break
    if last < 0:
        return len(samples) // channels
    end = min(len(samples) // channels, last + int(BREATH_SEC * sr))
    # snap to a zero crossing in channel 0 within +-0.05 s
    best, best_val = end, None
    for d in range(0, int(0.05 * sr)):
        for cand in (end + d, end - d):
            if 0 <= cand < len(samples) // channels:
                v = abs(samples[cand * channels])
                if best_val is None or v < best_val:
                    best, best_val = cand, v
        if best_val == 0:
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(args.in_dir, "*.wav"))):
        name = os.path.basename(path)
        if name.endswith("_loop.wav"):
            continue
        params, samples = read_wav(path)
        channels, sr = params.nchannels, params.framerate
        end = loop_end_index(samples, channels, sr)
        out = samples[: end * channels]
        out_path = os.path.join(args.out_dir, name.replace(".wav", "_loop.wav"))
        with wave.open(out_path, "wb") as w:
            w.setparams(params)
            w.writeframes(out.tobytes())
        jump = abs(out[0] - out[-channels]) / 32768 if out else 0
        print(f"{name}: {len(samples)/channels/sr:.1f}s -> {end/sr:.1f}s "
              f"(boundary jump {jump:.5f}) -> {out_path}")


if __name__ == "__main__":
    main()
