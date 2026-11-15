# Group 8 — Backfill audit for hyphenated-form candidates (2026-11-15)

Scope: the candidate enumerator missed hyphenated forms (e.g. "1000-Hz"); after
the fix, candidates_all.csv was regenerated (483 candidates). 21 already-extracted
papers gained new candidates. Each was audited: added candidates (new vs the old
census in /tmp/candidates_old.csv, keyed on PMID + Raw_Text + Value_Normalized)
were checked against the current output row and the group1–6 worknotes.

Outcome summary: 21 papers checked; 3 rows backfilled (10212425, 1880297,
3771926); 9 papers already reflected the added values; 6 papers' added values
judged not to belong (reasons below); 3 papers FLAGGED for central adjudication
because a backfill would change the row's Decision (3558957, 4078175, 7593925).
Final validator run over all output batches: 498 rows, 0 errors (only WARNs,
incl. expected unit_converted for kHz-notation matches).

Note on the validator: it now matches "X.0 kHz" cell values against quotes via
the unit-conversion path (WARN unit_converted, not ERROR). The
"validator-limited omissions" recorded in group5.md are therefore technically
backfillable now; where the row's Decision logic blocks it, this is flagged
below instead of applied.

## Backfilled

- **10212425** (batch_12, Include, A) — Added: "1000-Hz" (1000 Hz). Was missing:
  the row recorded only the 65 dB SPL masker; group3.md already noted the probe
  is a 1000-Hz tone burst, the paper's primary stimulus. Gate passes (A stratum,
  stimulus tone frequency, set stimulus, unambiguous). Backfilled
  Frequency_Hz=1000 and replaced Evidence_Quote with one contiguous span from
  "Listeners detected a repeated 1000-Hz probe…" through "…broadband noise
  masker at 65 dB SPL.", which contains both cell numbers (1000, 65).

- **1880297** (batch_21, Include, A) — Added: "60-dB" (60, Sound_Level_dB). Was
  missing: the row recorded only Attenuation_dB_oct=96; the click level (fixed
  at 60 dB sensation level) sits in the same quoted sentence but was never
  recorded (it was not an old candidate; group6's MIXED note addresses only the
  derived-band CFs). It is a set stimulus presentation level; relative level
  scales are recorded in Sound_Level_dB elsewhere in this project (dBnHL in
  3771926, dB S/N in 2299044). Backfilled Sound_Level_dB=60; quote unchanged
  (already contains 60 and 96).

- **3771926** (batch_18, Include, A) — Added: "1.0-kHz" (1000 Hz). The row
  recorded the response levels (20/40/60 dBnHL) but no frequencies; group5.md
  listed notch center frequencies 1000/4000/8000 as recordable values omitted
  only because the validator could not match "1.0 kHz" notation. That
  limitation no longer applies (matches as unit_converted WARN). Backfilled
  Frequency_Hz="1000, 4000, 8000"; quote unchanged (the existing quote already
  contains the notch sentence and the levels sentence contiguously).

## Already reflected (no change)

- **11386562** (batch_11, Include) — "1000-Hz" already recorded (Frequency_Hz=
  1000; extractor caught it manually, group2.md). 
- **16838539** (batch_9, Include) — "1000-Hz" already recorded (Frequency_Hz=
  1000; group2.md).
- **18345867** (batch_22, Reference) — "33-MHz" already recorded (33000000;
  group6.md).
- **1960280** (batch_17, Include) — "1000-Hz" already recorded (Frequency_Hz=
  1000, taken from the abstract by the extractor, group4.md).
- **3958315** (batch_18, Include) — "4-kHz" already recorded (4000; group5.md).
- **3973221** (batch_18, Include) — two added occurrences of "150-Hz"; the
  150 Hz standard is already recorded (Frequency_Hz=150). (The F0 increments
  remain excluded as frequency differences, per group5 MIXED.)
- **8226352** (batch_15, Reference) — "500-Hz" already recorded (500, with the
  15/25 dB levels; the added candidate is the same masker sentence already
  quoted).
- **8376210** (batch_16, Include) — "8-kHz" already recorded (8000, from the
  "1, 4, and 8 kHz" tone-pip quote).
- **9925011** (batch_21, Reference) — "20-kHz", "2-kHz", "500-Hz" are later
  mentions of the same cochlear-place best frequencies already recorded
  (500, 2000, 20000, 25000) and covered by the existing quote.
- **7593925, 100-Hz occurrences only** (batch_14, Reference) — both added
  "100-Hz" candidates are the high-pass filter value already recorded
  (Frequency_Hz="30, 100"). The third added candidate (500-Hz) is flagged
  separately below.

## Added values judged not to belong (no backfill)

- **2299044** (batch_17, Include) — Added: "3-dB" (adaptive-procedure step
  size: a procedural increment, not a presented sound level) and "5.8-dB"
  (group mean threshold difference: an outcome statistic; group4.md MIXED
  already excluded it on exactly this ground).
- **3558968** (batch_18, Reference) — Added: "16-kHz" (spectrogram sampling
  rate: an analysis/device parameter; gate condition 2 excludes sampling
  rates, and group5.md omitted the 20/40 kHz sampling rates on the same
  ground). The row documents observed vocalization acoustics, a different kind
  of value.
- **6401088** (batch_19, Include) — Added: "5-dB" (step size for threshold
  search: a procedural increment; no presented level is stated). Not a
  Sound_Level_dB value.
- **8120247** (batch_15, Reference) — Added: "2-6-kHz" (the two-peak resonance
  structure observed in results). The row documents the 125-10700 Hz
  measurement range; group4.md already decided observed ear-canal/concha
  resonance frequencies are not recorded (observed outcomes, not the
  measurement-range value the row documents).
- **8270739** (batch_16, Reference) — Added: "2-4-kHz" (a concluding
  recommendation that measurements in this range are a useful clinical tool).
  Not a set stimulus and not the study's measurement range (125-10700 Hz,
  already recorded); a recommendation drawn from results.
- **8969474** (batch_14, Include) — Added: "15-dB", "5-dB", "10-dB" (primary
  tone level separations L1>L2 and the 5-dB separation step interval). These
  are level *differences*, not absolute sound levels; group3.md already
  excluded the 10–15 dB separations on this ground, consistent with the
  difference exclusions in 2299044 (5.8 dB) and 3973221 (F0 increments).

## FLAGGED for central adjudication (backfill would change Decision — not applied)

- **3558957** (batch_18, currently Reference, numeric cells empty) — Added:
  "8.0-kHz" ×2 and "1.0-kHz". The probe frequencies 1000/4000/8000 pass the
  gate (set stimulus probes, A stratum) and are now validator-matchable
  (unit_converted). group5.md chose Reference *because* the cells had to stay
  empty and stated the row should become Include once the values are
  backfilled. Backfilling therefore entails a Decision change
  (Reference → Include) — flagged, not applied.
- **4078175** (batch_19, currently Reference, numeric cells empty) — Added:
  "1.0-kHz". Same situation: the 1000 Hz standard tone-burst train passes the
  gate and is now validator-matchable; group5.md holds the row as Reference
  pending backfill of exactly this value. Backfilling entails a Decision
  change (Reference → Include) — flagged, not applied.
- **7593925** (batch_14, currently Reference) — Added: "500-Hz" (the tone-burst
  ABR stimulus). Unlike the row's recorded values (30/100 Hz recording-filter
  settings, documented as Reference), 500 Hz is a gate-passing stimulus
  frequency; group3.md explicitly said the Decision must be rechecked if this
  value is restored. Adding it would change the row's Decision basis —
  flagged, not applied. (A single contiguous quote span covering 500 Hz
  together with the current results-sentence quote was not attempted, since
  the Decision question must be settled first.)

## Side observation (outside the added-candidate scope)

- **6401088**: group5.md also listed Frequency_Hz 4000/10000 (the 4.0 and
  10.0 kHz tone pips) as validator-limited omissions. Those were *old*
  candidates, not added ones, so they are outside this audit's scope and were
  not touched — but the validator now matches the kHz notation, so a future
  backfill pass could restore them without a Decision change (row is already
  Include). Left for central to schedule.
