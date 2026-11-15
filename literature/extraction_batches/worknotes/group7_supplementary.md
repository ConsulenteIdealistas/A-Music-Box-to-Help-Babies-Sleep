# Group 7 supplementary extraction — hyphenated-form candidates missed by candidates.py v1

Candidates regenerated with candidates.py v2 (hyphenated forms like "1000-Hz"
now enumerated). Eight papers previously held qualitative Count_only fills
despite having numeric candidates; their output rows were replaced with proper
extractions. One row per paper; values taken from the paper's rows in
candidates_all.csv; every quote is a single contiguous verbatim span.

Validator (batches 2, 5, 14, 17, 19, 23): 126 rows, 0 errors. WARNs on these
rows are unit_converted (kHz/MHz) and one implausible_value (PMID 2199548,
3.6 MHz vs the 200 kHz plausibility cap) — both expected.

## Per-paper results

### PMID 32237812 — batch_2 — Decision: Reference — ⚠ STRATUM CHANGED A → B
- Frequency_Hz = 1000 (1000-Hz FM tone, detection thresholds estimated adaptively).
- Basis: the value itself passes the gate (stimulus tone frequency, set
  experimentally), but the abstract states the thresholds were "obtained from
  adults"; infants appear only as the background motivation for the procedure.
  No under-2 (or child) participants were tested, which clearly contradicts
  stratum A, so Stratum was corrected to B and the row is Reference (B-layer
  rule). Target_Age also corrected from the qualitative fill "infants" to
  "adults".

### PMID 25190427 — batch_5 — Decision: Include
- Sound_Level_dB = 50 (50-dB SPL noise band presented to 7–9-month-old infants
  in a two-interval forced-choice detection procedure).
- Basis: stratum A; the value is the sound level of the presented stimulus
  (the column's quantity); set as the experimental stimulus; unambiguous in
  the quote.

### PMID 7593935 — batch_14 — Decision: Include
- Frequency_Hz = 500 (500-Hz Gaussian-enveloped tone pips, gap detection;
  listeners 6.5 months–21 years, includes under-2).
- Basis: stratum A; carrier/stimulus tone frequency; set experimentally;
  unambiguous.

### PMID 2199548 — batch_17 — Decision: Reference — ⚠ special case (MHz ultrasound)
- Frequency_Hz = 3600000 (3.6-MHz focused ultrasonic beams applied to a
  sample of tissue-mimicking gel; outcome = temperature rise).
- Basis: per the special-case rule, MHz-range ultrasound tissue-exposure
  values are Reference even if other gate conditions pass — outside the
  audible-stimulus domain the design parameters describe.
- Flag: no human subjects (phantom/gel study; the fetus appears only as the
  scanning context). Stratum kept at the sheet value (A) per the
  keep-unless-clearly-contradicted instruction; the Reference decision makes
  the stratum moot for design statistics.

### PMID 2768673 — batch_17 — Decision: Include
- Frequency_Hz = 1000 (1.0-kHz pulsed-tone standard for frequency-transition
  DLs in 6- to 9-month-old infants; the same value recurs four times in the
  abstract, recorded once).
- Basis: stratum A; standard stimulus tone frequency; set experimentally;
  unambiguous.

### PMID 4031254 — batch_19 — Decision: Include — ⚠ enumerator miss flagged
- Frequency_Hz = 1000 (1000-Hz filtered-click stimuli; ABR masking profiles in
  three-month-old infants).
- Basis: stratum A; stimulus (filtered-click) frequency; set experimentally;
  unambiguous.
- ⚠ Flag: the same quote span also states "4000- and 1000-Hz filtered-click
  stimuli". The bare "4000-" form (hyphen not followed by the unit) was NOT
  enumerated in candidates_all.csv v2, so per candidate-driven extraction
  only 1000 was recorded. The 4000-Hz stimulus is real and visible in the
  stored quote; a global decision (enumerator v3 for the "N- and M-unit"
  pattern, or a manual addendum) is needed rather than a local fix.

### PMID 6747104 — batch_19 — Decision: Reference
- Sound_Level_dB = 2, 6 (2-dB and 6-dB intensity increments in a synthetic
  CVC syllable; infants 5–11 months).
- Basis: gate condition (2) fails — the values are intensity *increment*
  sizes (level differences), not absolute sound levels, which is the quantity
  Sound_Level_dB defines. Recording them as sound levels would contaminate
  the design population. Values and quote kept as Reference.
- ⚠ Flag: the same span also states a "4- and 6-dB" pair; the bare "4-"
  form was not enumerated in candidates_all.csv v2 (same miss pattern as
  PMID 4031254), so only the enumerated 2 and 6 were recorded.

### PMID 8226343 — batch_23 — Decision: Reference
- Frequency_Hz = 40000 (40-kHz test tone; rat auditory thresholds by reflex
  modification audiometry).
- Basis: stratum C (animal study) — Reference by the layer rule.
- ⚠ Flag: the same span also states "5- and 40-kHz tones"; the bare "5-"
  form was not enumerated in candidates_all.csv v2 (same miss pattern), so
  only 40000 was recorded.

## Cross-cutting flag for the parent

candidates.py v2 still misses the bare-hyphen first element of compound
forms — "4000- and 1000-Hz", "4- and 6-dB", "5- and 40-kHz" — where only the
last element carries the unit. Three of the eight papers here are affected
(4031254, 6747104, 8226343). This pattern may also occur in papers extracted
by other groups; a v3 pattern for "N- and M<unit>" (and "N-, M-, and K<unit>")
plus a re-scan of all abstracts would close it deterministically.
