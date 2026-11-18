# Bed literature round 3 — human measurements only (2026-11-17)

Scope set by the user: reinforce only the human side, narrowly. The round-2
reservations were (a) the anchor is sheep (Gerhardt 1990) while the product is
for human babies, and the human side rested on Richards 1992's two abstract
endpoints plus Benzaquen's background bounds; (b) band values attributed to
the Querleu group by secondary sources (2 dB at 250 Hz, 14 at 500, 20 at
1000, 26 at 2000) were unverified in any primary source.

Rules kept from rounds 1–2: design values come only from primary sources,
verbatim quotes recorded, derived values labelled, secondary-review summary
numbers are NOT adopted as extracted data.

## What was searched and what was found

### 1. Richards et al. 1992 full text (Obstet Gynecol 80(2):186-190)
- **Not obtained.** The journal is paywalled (LWW); no open author manuscript
  or PDF was found. Searches surfaced only the abstract (already extracted in
  round 2) and secondary discussions quoting the same two endpoints.
- One additional detail circulates secondarily: Spence & Freeman 1996
  (Infant Behav Dev 19:199-212) write that in Richards et al. 1992
  "one-third-octave bands with center frequencies below 250 Hz were enhanced
  up to 5 dB" and that the maternal voice was measured at 77 dB in utero,
  "amplified about 5 dB above the measurement in air" (the +5.2 dB voice
  figure is in the abstract; the "up to 5 dB below 250 Hz" band detail is
  not). Recorded here as a secondary lead only — it is consistent with
  Gerhardt's stated +2 to +5 dB low-frequency range, but it does not enter
  the dataset.
- Consequence: Richards' intermediate one-third-octave band values remain
  unextracted. The endpoint line (2.74 dB/oct, derived) stays a derived
  sensitivity bound, exactly as in round 2.

### 2. Querleu group primaries
- Primary reports: Querleu, Renard & Crépin 1981 (Med Hyg 39:2101-2110,
  "Les perceptions auditives du foetus humain"), Querleu et al. 1981
  (J Gynecol Obstet Biol Reprod, "Perception auditive et réactivité foetale
  aux stimulations sonores"), Querleu et al. 1988 (Rev Fr Gynecol Obstet,
  "La transmission intra-amniotique des voix humaines"), and the group's
  English review (Eur J Obstet Gynecol Reprod Biol 29:191-212, 1988).
  **None was openly accessible in full text in this search** (French
  journals / Elsevier paywall), so the band values could NOT be confirmed
  in a primary source. Their status is unchanged in kind — but the
  corroboration is now documented from three independent secondaries:
  - Muenssinger et al. 2013 (Front Hum Neurosci 7:917, PMC3876038),
    verified verbatim in the full text: "Using a hydrophone near the fetal
    head at the beginning of labor and after amniotomy, Querleu et al.
    (1988) recorded an attenuation of 2 dB at 250 Hz, 14 dB at 500 Hz,
    20 dB at 1000 Hz, and 26 dB at 2000 Hz."
  - Spence & Freeman 1996 attribute two of the points to Querleu et al. 1981:
    a 250 Hz tone attenuated 2 dB and a 1000 Hz tone attenuated 20 dB.
  - Busnel, Granier-Deferre & Lecanuet, "Fetal audition" (Ann NY Acad Sci)
    synthesize the group's human recordings as: "Pressure loss is
    negligible in the low frequencies: 0 to 2 dB SPL at and below 250 Hz.
    It increases as a function of frequency to about 20 dB SPL at 1000 Hz
    and does not exceed 40 dB SPL for higher frequencies in the human
    audible range." The same review states the animal values are LOWER
    than those measured in women: in sheep/goats the loss is "negligible,
    0 to 5 dB SPL, at frequencies up to 500 Hz; pressure loss then
    increases by 6 dB/octave up to 4 kHz".
- The four points are stored in literature/bed_transfer_curves.csv with
  kind=secondary_corroborated. They are used only for the curve comparison
  in the integration memo — never pooled with stated primary values, and
  they do not move the design anchor.

### 3. Unresolved items retried
- Nyman et al. 1991 (Obstet Gynecol 78:803-806): abstract still not
  retrieved. Bibliographically resolved via the group's follow-up
  (Nyman, Barr & Westgren 1992, BJOG 99:685-688): the 1991 study measured
  in-utero levels from a Servox artificial larynx (contact source,
  99 dB in air at 2 cm, maximum 129 dB recorded in utero, spectrum peaking
  at 500 Hz). A contact-source level, not airborne band transfer — the
  same class as Gerhardt 1988. Not usable for the transfer curve.
- Walker et al. 1971 (4th Sound & Vibration Conference proceedings):
  primary text still not accessible. Unchanged.

## Bottom line of round 3
- No new primary stated values were obtained, so no design number changes.
- What changed is the shape of the uncertainty: the human evidence now
  brackets the sheep anchor from both sides (Richards gentler, Querleu
  steeper), and the Querleu points themselves run at 6 dB/oct above
  500 Hz — the same slope as the anchor. See the round-3 section of
  audio/bed_integration_2026-11-17.md for the numbers.

## Correction (2026-11-18)

Earlier versions of this memo attributed the statements in §1–§2 to
"Moon & Fifer 1996". That attribution was wrong: the document read in
round 3 was Spence & Freeman, "Newborn Infants Prefer the Maternal
Low-Pass Filtered Voice, But Not the Maternal Whispered Voice",
Infant Behav Dev 19:199-212 (1996), DOI 10.1016/S0163-6383(96)90019-3.
Verified 2026-11-18 against the publicly available scan (Docsity):
authors (Melanie J. Spence and Mark S. Freeman) and title on p.199,
and both passages quoted in §1–§2 present verbatim on p.200. The
likely source of the confusion is the DeCasper & Fifer (1980)
citation on p.199 and the topical closeness. The attributions in
§1–§2 have been corrected in place; no values or conclusions change.
Registry: spence_freeman_1996 (the old ID moon_fifer_1996 is retired
and will not be reused).
