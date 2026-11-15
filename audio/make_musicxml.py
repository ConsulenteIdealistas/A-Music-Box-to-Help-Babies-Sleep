"""Generate MusicXML scores (the canonical score store) for the four
repertoire pieces, in audio/scores/.

The note data below IS the transcription record. Sources:
  brahms   -- LilyPond in Wikipedia "Wiegenlied (Brahms)" (Eb major),
              transposed to C major +8va for the music box.
  yurikago -- published kalimba score (C major); rhythm regularised
              into 4/4 bars (the tab itself is not strictly metered).
  moldau   -- LilyPond in Wikipedia "Ma vlast" (E minor, 6/8 theme);
              the source excerpt's final bar is incomplete (3 eighths)
              and is completed here to a full bar (noted in the file).
  vissi    -- Ricordi 1910 vocal score (IMSLP plate 113189), vocal
              staff transcribed from the scan; Gb major, 2/4, first
              section only.
Regenerate with: python -m audio.make_musicxml
The renderers (render_songs / render_klank) read these XML files;
they hold no note data of their own.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

DIV = 12  # divisions per quarter note
T = 1 / 3  # triplet eighth, in quarters

# (step, alter) helpers -------------------------------------------------
def pitch_xml(name: str):
    step = name[0]
    rest = name[1:]
    alter = 0
    if rest.startswith("b"):
        alter, rest = -1, rest[1:]
    elif rest.startswith("#"):
        alter, rest = 1, rest[1:]
    return step, alter, int(rest)


def duration_units(quarters: float) -> int:
    return int(round(quarters * DIV))


def note_type_and_dots(units: int):
    table = {
        48: ("whole", 0), 36: ("half", 1), 24: ("half", 0),
        18: ("quarter", 1), 12: ("quarter", 0), 9: ("eighth", 1),
        6: ("eighth", 0), 4: ("eighth", 0), 3: ("16th", 0),
    }
    if units not in table:
        raise ValueError(f"unsupported duration units {units}")
    return table[units]


def add_note(measure, name, quarters, tie=None):
    units = duration_units(quarters)
    n = ET.SubElement(measure, "note")
    if name == "R":
        ET.SubElement(n, "rest")
    else:
        step, alter, octave = pitch_xml(name)
        p = ET.SubElement(n, "pitch")
        ET.SubElement(p, "step").text = step
        if alter:
            ET.SubElement(p, "alter").text = str(alter)
        ET.SubElement(p, "octave").text = str(octave)
    ET.SubElement(n, "duration").text = str(units)
    if tie:
        ET.SubElement(n, "tie", {"type": tie})
    typ, dots = note_type_and_dots(units)
    ET.SubElement(n, "type").text = typ
    for _ in range(dots):
        ET.SubElement(n, "dot")
    if units == 4:  # triplet eighth
        tm = ET.SubElement(n, "time-modification")
        ET.SubElement(tm, "actual-notes").text = "3"
        ET.SubElement(tm, "normal-notes").text = "2"


def add_harmony(measure, root_name, kind):
    h = ET.SubElement(measure, "harmony")
    r = ET.SubElement(h, "root")
    step = root_name[0]
    alter = -1 if root_name.endswith("b") else (1 if root_name.endswith("#") else 0)
    ET.SubElement(r, "root-step").text = step
    if alter:
        ET.SubElement(r, "root-alter").text = str(alter)
    ET.SubElement(h, "kind").text = kind


def build(song) -> ET.ElementTree:
    root = ET.Element("score-partwise", {"version": "4.0"})
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = song["title"]
    ident = ET.SubElement(root, "identification")
    creator = ET.SubElement(ident, "creator", {"type": "composer"})
    creator.text = song["composer"]
    rights = ET.SubElement(ident, "rights")
    rights.text = "Melody: public domain. Transcription: see audio/SONGS.md"
    misc = ET.SubElement(ident, "miscellaneous")
    field = ET.SubElement(misc, "miscellaneous-field", {"name": "source"})
    field.text = song["source"]
    part_list = ET.SubElement(root, "part-list")
    sp = ET.SubElement(part_list, "score-part", {"id": "P1"})
    ET.SubElement(sp, "part-name").text = "Music box"
    part = ET.SubElement(root, "part", {"id": "P1"})
    for i, (chord, notes) in enumerate(song["measures"]):
        m = ET.SubElement(part, "measure", {"number": str(i + 1)})
        if i == 0:
            attrs = ET.SubElement(m, "attributes")
            ET.SubElement(attrs, "divisions").text = str(DIV)
            key = ET.SubElement(attrs, "key")
            ET.SubElement(key, "fifths").text = str(song["fifths"])
            time_el = ET.SubElement(attrs, "time")
            ET.SubElement(time_el, "beats").text = str(song["beats"])
            ET.SubElement(time_el, "beat-type").text = str(song["beat_type"])
            clef = ET.SubElement(attrs, "clef")
            ET.SubElement(clef, "sign").text = "G"
            ET.SubElement(clef, "line").text = "2"
            if song.get("pickup"):
                m.set("implicit", "yes")
        if chord:
            add_harmony(m, chord[0], chord[1])
        for item in notes:
            if isinstance(item, tuple) and item[0] == "TIE":
                _, name, q1, q2 = item
                add_note(m, name, q1, tie="start")
                add_note(m, name, q2, tie="stop")
            else:
                add_note(m, item[0], item[1])
    return ET.ElementTree(root)


# --- song data: measures of (chord, [(name, quarters), ...]) ----------
BRAHMS = {
    "file": "brahms_wiegenlied.musicxml",
    "title": "Wiegenlied (Brahms' Lullaby), Op. 49 No. 4",
    "composer": "Johannes Brahms",
    "source": "LilyPond score in Wikipedia 'Wiegenlied (Brahms)' (Eb major); transposed to C major, +8va",
    "fifths": 0, "beats": 3, "beat_type": 4, "pickup": True,
    "measures": [
        (None, [("E5", .5), ("E5", .5)]),
        (("C", "major"), [("G5", 1.5), ("E5", .5), ("E5", 1)]),
        (("C", "major"), [("G5", 1), ("R", 1), ("E5", .5), ("G5", .5)]),
        (("C", "major"), [("C6", 1), ("B5", 1.5), ("A5", .5)]),
        (("F", "major"), [("A5", 1), ("G5", 1), ("D5", .5), ("E5", .5)]),
        (("C", "major"), [("F5", 1), ("D5", 1), ("D5", .5), ("E5", .5)]),
        (("F", "major"), [("F5", 1), ("R", 1), ("D5", .5), ("F5", .5)]),
        (("C", "major"), [("B5", .5), ("A5", .5), ("G5", 1), ("B5", 1)]),
        (("C", "major"), [("C6", 1), ("R", 1), ("C5", .5), ("C5", .5)]),
        (("F", "major"), [("C6", 2), ("A5", .5), ("F5", .5)]),
        (("C", "major"), [("G5", 2), ("E5", .5), ("C5", .5)]),
        (("F", "major"), [("F5", 1), ("G5", 1), ("A5", 1)]),
        (("C", "major"), [("G5", 2), ("C5", .5), ("C5", .5)]),
        (("F", "major"), [("C6", 2), ("A5", .5), ("F5", .5)]),
        (("C", "major"), [("G5", 2), ("E5", .5), ("C5", .5)]),
        (("C", "major"), [("F5", 1), ("E5", 1), ("D5", 1)]),
        (("C", "major"), [("C5", 3)]),
    ],
}

YURIKAGO = {
    "file": "yurikago_no_uta.musicxml",
    "title": "Yurikago no Uta",
    "composer": "Shin Kusakawa (lyrics: Hakushu Kitahara)",
    "source": "Published kalimba score (Ehon Biyori, class101 PDF), melody line; rhythm regularised to 4/4",
    "fifths": 0, "beats": 4, "beat_type": 4, "pickup": False,
    "measures": [
        (("C", "major"), [("G5", 2), ("A5", 1), ("G5", 1)]),
        (("C", "major"), [("E5", 2), ("C5", 2)]),
        (("C", "major"), [("E5", 1), ("D5", 3)]),
        (("F", "major"), [("A4", 2), ("C5", 1), ("A4", 1)]),
        (("C", "major"), [("G4", 2), ("C5", 2)]),
        (("C", "major"), [("E5", 2), ("G5", 1), ("E5", 1)]),
        (("F", "major"), [("D5", 3), ("C5", 1)]),
        (("C", "major"), [("E5", 2), ("E5", 1), ("E5", 1)]),
        (("C", "major"), [("D5", 1), ("E5", 1), ("G5", 1), ("A5", 1)]),
        (("C", "major"), [("G5", 2), ("E5", 2)]),
        (("F", "major"), [("G5", 1), ("E5", 1), ("D5", 2)]),
        (("C", "major"), [("C5", 4)]),
    ],
}

_MOLDAU_BARS = [
    (("E", "minor"), [("E5", 1), ("F#5", .5), ("G5", 1), ("A5", .5)]),
    (("E", "minor"), [("B5", 1), ("B5", .5), ("B5", 1.5)]),
    (("E", "minor"), [("C6", 1.5), ("C6", 1.5)]),
    (("E", "minor"), [("TIE", "B5", 1.5, 1.0), ("B5", .5)]),
    (("E", "minor"), [("A5", 1.5), ("A5", 1), ("A5", .5)]),
    (("E", "minor"), [("G5", 1), ("A5", .5), ("G5", 1), ("G5", .5)]),
    (("E", "minor"), [("F#5", 1.5), ("F#5", 1), ("F#5", .5)]),
    (("E", "minor"), [("E5", 1.5), ("R", 1.5)]),
]
MOLDAU = {
    "file": "moldau_theme.musicxml",
    "title": "Vltava (The Moldau) - main theme",
    "composer": "Bedrich Smetana",
    "source": "LilyPond score in Wikipedia 'Ma vlast' (E minor, 6/8); final bar completed by the arranger (source excerpt ends mid-bar); theme played twice",
    "fifths": 1, "beats": 6, "beat_type": 8, "pickup": True,
    "measures": [(None, [("B4", .5)])] + _MOLDAU_BARS + _MOLDAU_BARS,
}

VISSI = {
    "file": "vissi_darte.musicxml",
    "title": "Vissi d'arte (Tosca, Act II)",
    "composer": "Giacomo Puccini",
    "source": "Ricordi vocal score, Milan 1910, plate 113189 (IMSLP); vocal staff transcribed from scan; first section only",
    "fifths": -6, "beats": 2, "beat_type": 4, "pickup": False,
    "measures": [
        (("Gb", "major"), [("Eb5", 1), ("Db5", 1)]),
        (("Gb", "major"), [("Bb4", 1), ("Ab4", 1)]),
        (("Gb", "major"), [("Eb5", 1), ("Db5", .75), ("Bb4", .25)]),
        (("Cb", "major"), [("Bb4", 1), ("Ab4", 1)]),
        (("Gb", "major"), [("Cb5", 1), ("Ab4", T), ("Bb4", T), ("Cb5", T)]),
        (("Eb", "minor"), [("F4", T), ("Gb4", T), ("F4", T), ("Ab4", T), ("F4", T), ("Ab4", T)]),
        (("Ab", "minor"), [("Eb4", T), ("Eb4", T), ("R", T), ("R", 1)]),
        (("Gb", "major"), [("Eb5", 1), ("Db5", .75), ("Bb4", .25)]),
        (("Gb", "major"), [("Bb4", 1), ("Ab4", 1)]),
        (("Cb", "major"), [("Ab5", 1), ("Gb5", .5), ("Gb5", .5)]),
        (("Gb", "major"), [("Ab5", T), ("Gb5", T), ("Eb5", T), ("Eb5", T), ("Db5", T), ("Cb5", T)]),
        (("Eb", "minor"), [("Db5", T), ("Cb5", T), ("Bb4", T), ("R", 1)]),
        (("Gb", "major"), [("R", 2)]),
    ],
}

SONGS = [BRAHMS, YURIKAGO, MOLDAU, VISSI]


def main() -> None:
    out_dir = Path(__file__).with_name("scores")
    out_dir.mkdir(exist_ok=True)
    for song in SONGS:
        tree = build(song)
        ET.indent(tree, space="  ")
        tree.write(out_dir / song["file"], encoding="utf-8", xml_declaration=True)
        print("wrote", out_dir / song["file"])


if __name__ == "__main__":
    main()
