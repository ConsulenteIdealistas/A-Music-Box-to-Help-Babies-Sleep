# Central adjudication — 2026-11-15 (coordinator pass after groups 1–8)

## Validator fix (analysis/validate_extraction.py)
`number_in_quote` compared formatted strings, so decimal tokens in quotes
("1.0 kHz", "8.0 dB SPL") never matched integer cell values, and MHz had no
conversion path. Changed to numeric comparison (float tokens) with kHz and
MHz conversion paths. Effect: group 6's 7 false ERRORs cleared; the backfills
below became recordable.

## Candidate census fix (analysis/candidates.py v1 → v3)
- v2: hyphenated adjective forms ("1000-Hz", "3.6-MHz", "50-dB") were missed
  by v1. Census 439 → 483 candidates; 8 papers surfaced (2199548, 25190427,
  2768673, 32237812, 4031254, 6747104, 7593935, 8226343) and were extracted
  as group 7; 21 already-extracted papers audited as group 8.
- v3: compound forms ("4000- and 1000-Hz") — the bare first element was
  missed by v2. Census 483 → 488; no new papers; 5 added candidates checked
  below.

## Backfills from the v3 diff
- 4031254 (Include): Frequency_Hz 1000 → "1000, 4000" (quote already covered).
- 6747104 (Reference): Sound_Level_dB "2, 6" → "2, 4, 6" (increments; quote covered).
- 8226343 (Reference, C): Frequency_Hz 40000 → "5000, 40000" (quote covered).
- 7593925 (Reference → Include): the row held recording-filter cutoffs
  (30/100 Hz, equipment parameters, gate condition 2 fails) while the paper's
  actual stimulus (500-Hz tone bursts) was unrecorded. Per the MIXED rule:
  Frequency_Hz = 500, Decision = Include, quote replaced with the stimulus
  sentence. The filter values remain documented in Stimulus_Type.
- 8969474: added candidate (15 dB) is a primary-tone level separation, not a
  level — not backfilled (consistent with group 8's verdict on the same paper).

## Backfills of validator-limited omissions (groups 2–5 notes)
- 3558957 (Reference → Include): Frequency_Hz = 1000, 4000, 8000 (probe clicks,
  set stimuli, stratum A).
- 4078175 (Reference → Include): Frequency_Hz = 1000 (ongoing tone-burst standard).
- 9119764 (Include): Frequency_Hz → "500, 1500, 4000, 8000".
- 6401088 (Include): Frequency_Hz → "500, 4000, 10000".
- 3771926 (Include): Frequency_Hz = "1000, 4000, 8000" (done by group 8).
- 4044425 (Reference, C): Frequency_Hz = "200-10000" (stimulus range; the
  1500-3000 best-frequency range is observed and stays unrecorded).
- 1559899 (Count_only → Reference, C): Frequency_Hz = "200-10000".
- 21974484 (Reference, C): Frequency_Hz → "30000, 19300, 41400".
- 15807032 (Reference, UNDETERMINED): Frequency_Hz → "20000, 2000000".
- 8226331 (Reference): Sound_Level_dB → "-2-42, 8" (mean SOAE level added).
- 1564194 (Reference): Frequency_Hz = "1000-2000, 2500-5000" (SOAE ranges).

## MHz ultrasound rule (coordinator decision, flagged to user)
- 2681313 (Count_only → Reference): Frequency_Hz = 1000000 recorded.
- 2199548 (Reference): Stratum A → UNDETERMINED (tissue-mimicking gel phantom,
  no subjects; precedent 15807032).
Rationale: MHz ultrasound tissue exposure is a carrier frequency, but outside
the audible-stimulus domain the design parameters describe — same treatment as
the pilot's modulation-rate precedent (37772774). Values are kept, never in
design statistics. Reversible on user decision.

## State after this pass
498 rows, validator 0 errors. Decisions: see final tally in the run summary.
