# Worknotes — Group 6 (batches 21–24), primary numeric extraction

32 candidate papers processed. Decisions: Include 1 / Reference 29 / Count_only 2.
All Evidence_Quotes are single contiguous verbatim spans taken from the
bibliography abstract; every quoted span passed the verbatim check.

## Per-paper lines (PMID — Decision — basis)

### Batch 21
- 9925011 — Reference — Cat organ-of-Corti morphometry; recorded cochlear-place best frequencies (500, 2000, 20000, 25000 Hz) are anatomical place values, not stimuli; stratum corrected B→C (cats only).
- 9557980 — Reference — Tammar wallaby ABR development; tone-burst frequency ranges (500-1500, 4000-12000, 16000 Hz) recorded; stratum corrected B→C (wallabies only).
- 8789820 — Reference — Gerbil place-frequency map; map frequencies (300-31900, 500, 4000, 6000 Hz) are fiber characteristic frequencies, not set stimuli; stratum corrected B→C (gerbils only).
- 8567420 — Reference — Quail/chick octave-band noise exposure 1500 Hz at 116 dB SPL is a genuine set stimulus, but stratum corrected B→C (birds only), so gate condition 1 fails.
- 8647737 — Reference — Opossum BAEP ontogeny; hearing range 5000-20000 Hz and lowest thresholds 60 dB SPL at 8000-12000 Hz are measured outcomes; stratum corrected B→C (opossum only).
- 1880297 — Include (MIXED, see below) — Human derived-response ABR; stratum corrected B→A (subjects span 29 weeks conceptional age to 49 years, i.e. includes under-2). Only the passing value (masking-noise slope 96 dB/oct) recorded.

### Batch 22
- 3610862 — Reference — Kitten auditory nerve/CN development; 1500 Hz is the measured clustering of tuning-curve center frequencies (outcome), not a set stimulus; stratum corrected B→C (kittens only).
- 4086386 — Reference — Adult cats with unilateral atresia; 50 dB is a relative interaural intensity difference (outcome), not an absolute level; stratum corrected B→C (cats only).
- 690336 — Reference — Human skull acoustics (specimens, stratum B kept); ultrasound measurement range 250000-6000000 Hz and the 2200000 Hz upper limit of most studies recorded. See validator note below (MHz conversion ERRORs).
- 40652664 — Reference — Adult mice (TRPA1); 8000 Hz tone burst eliciting rCM recorded; C stratum.
- 40816165 — Reference — Mouse earplug deprivation; 30-40 dB is the earplug-induced threshold elevation (manipulation magnitude), not a presented sound level; C stratum.
- 35131579 — Reference — Mouse CMV model; ABR tonal stimuli recorded as the full stated set 8000, 16000, 32000 Hz (candidates had captured only "16 and 32 kHz"); C stratum.
- 36306607 — Reference — Cat cochlear-implant model; enhanced acoustic environment 80 dB SPL recorded; C stratum. Other candidates omitted (see below).
- 34311267 — Reference — Rat developmental noise exposure, 125 dB SPL broad-band noise at P14 (set stimulus); C stratum.
- 26386286 — Reference — Rat single-sided deafness; 95 dB is a relative ABR threshold criterion (deafened ear vs normal ear), not an absolute level; C stratum.
- 18345867 — Reference — Rat cervix ultrasound; 33-MHz transducer center frequency recorded (33000000 Hz). See judged-items section: this value was NOT in candidates_all.csv, and the two dB candidates were not recorded.

### Batch 23
- 15219315 — Reference — Guinea-pig DPOAE; primary-tone f2 range 2000-8000 Hz and L2 range 15-60 dB SPL recorded; the "41 dB SPL" formula constant (L1 = 0.46·L2 + 41) was not recorded as a level (see judged items); C stratum.
- 12062768 — Reference — Guinea-pig placental-insufficiency ABR; tone-pip stimuli recorded as the full stated set 2000, 4000, 8000, 16000, 32000 Hz (candidates had captured only "16 and 32 kHz"); C stratum.
- 10392547 — Reference — Gerbil cisplatin study; 8000 Hz is a result-region bound ("frequencies below 8 kHz"), not a set stimulus frequency; C stratum.
- 9387996 — Reference — Fetal sheep filtered-noise exposure; tone bursts 500, 1000, 2000 Hz and noise level 120 dB recorded (cut-off 1000 Hz is the same 1000 value). See validator note below ("1.0/2.0 kHz" conversion ERRORs).
- 8844183 — Reference — Neonatal rat DPE/ABR; frequencies 3000, 8000 Hz and stimulus intensities 50, 70 dB SPL recorded in one contiguous span covering both mentions; C stratum.
- 8040092 — Reference — Fetal sheep noise exposure; broadband noise 120 dB SPL and ABR tone bursts 500, 1000, 2000, 4000 Hz recorded; the 8 dB threshold elevation (outcome) omitted (see below); C stratum.
- 8226345 — Reference — Neonatal rat ABR; maximal BC level 55 and AC level 80 recorded — note both are in dB HL (relative to adult rat ABR threshold), not dB SPL; C stratum.
- 1774201 — Count_only (NO_ACOUSTIC_IN_ABSTRACT) — Chicken auditory-nerve study; the only candidate ("10dB") comes from the metric name "Q10dB" (tuning-curve bandwidth index), not a sound level; no numeric acoustic value stated.

### Batch 24
- 1880073 — Reference — Chick pure-tone overstimulation; 1500 and 2200 Hz at 124 dB SPL recorded; C stratum.
- 2076984 — Count_only (NO_ACOUSTIC_IN_ABSTRACT) — Neonatally deafened cats; the study uses intracochlear ELECTRICAL stimulation only. The dB candidates (2 dB, 6 dB) are electrical stimulation levels relative to EABR threshold, not acoustic sound levels, so no acoustic value was recorded.
- 2312410 — Reference — Rat DPOAE development; primary-tone geometric-mean range 4000-11300 Hz recorded; C stratum.
- 3793640 — Reference — Chick middle-ear admittance; measurement frequencies 660-1800 Hz recorded; C stratum.
- 4066520 — Reference — Chick pure-tone trauma; exposure 1500 Hz at 125 dB SPL recorded, plus 4000 Hz (frequency of maximum threshold elevation — an outcome, flagged here); C stratum.
- 6619005 — Reference — Rat neonatal hypothyroidism; 60-70 dB SPL is the measured elevated BAER threshold range (outcome), not a presented level; C stratum.
- 512209 — Reference — Mouse in-utero ultrasound; this study's exposure frequency 2000000 Hz (2 MHz) recorded. See validator note below (MHz conversion ERROR) and omitted values (1 MHz prior work).
- 670550 — Reference — Hearing-handicap model/review, no subjects; 24 dB is the model value at which class-D auditory handicap begins (a stated hearing-loss level, not a stimulus); stratum UNDETERMINED kept (no ages stated).

## Stratum corrections (shell → corrected, all flagged per instructions)

- 1880297: B → A. Human subjects aged 29 weeks conceptional age to 49 years; includes under-2 participants. This correction is what makes the row Include-eligible (see MIXED).
- 9925011: B → C. Subjects are cats (kittens and adults) only.
- 9557980: B → C. Subjects are tammar wallabies only.
- 8789820: B → C. Subjects are Mongolian gerbils only.
- 8567420: B → C. Subjects are quail and chicks only.
- 8647737: B → C. Subjects are Monodelphis domestica (opossum) only.
- 3610862: B → C. Subjects are kittens only.
- 4086386: B → C. Subjects are cats only.
- Kept as-is: 690336 = B (adult human skull specimens — human material, no live subjects); 670550 = UNDETERMINED (no subjects/ages stated); all batch 23/24 shells were already C and matched their abstracts.

Note: the B→C corrections do not change any Decision (B and C both fail gate
condition 1); only the 1880297 B→A correction affects a Decision.

## MIXED rows

- MIXED 1880297 (Include): recorded Attenuation_dB_oct = 96 (slope of the
  high-pass masking noise — a set experimental stimulus parameter, correct
  physical quantity for the column, stratum A after correction).
  Failing values NOT recorded: Frequency_Hz 11300 and 5700 (center frequencies
  of the derived-response octave bands). The actual stimuli were clicks plus
  high-pass noise; the band CFs are analysis bands of the derived-response
  technique, not stimulus tone frequencies, so they fail gate condition 2.

## Omitted scattered values (not coverable / not recorded, with reasons)

- 690336: 500000-1000000 Hz ("appropriate frequencies (0.5-1.0 MHz)") — a
  concluding recommendation in the final sentence, not coverable in the same
  span as the measurement range; the recorded span covers the measurement
  range and the 2.2 MHz limit.
- 36306607: 2000 Hz ("residual hearing, typically in the low frequency range
  (<2 kHz)") — background about human CI recipients, not this experiment's
  stimulus; 4000 Hz ("high frequency hearing loss (>4 kHz)") — describes the
  cat model's induced hearing loss, not a stimulus. Only the actual acoustic
  stimulus (80 dB SPL babble) was recorded.
- 8040092: 8 dB — measured ABR threshold elevation after exposure (outcome),
  not a presented sound level; omitted from Sound_Level_dB.
- 512209: 1000000 Hz (1 MHz) — exposure parameters of a PRIOR study (Curto
  1976) quoted for comparison, not this study's exposure; fails gate
  condition 3 (background/prior work). Only this study's 2 MHz recorded.

## Judged / ambiguous items

- VALIDATOR LIMITATION (affects 4 papers, 7 ERRORs — values are correct):
  analysis.validate_extraction.number_in_quote matches numbers as strings
  and only supports the kHz→Hz conversion when the scaled value's string
  form appears among the quote's number tokens. It therefore cannot match
  (a) MHz→Hz conversions at all ("MHz" quotes contain no "khz"), and
  (b) integer-valued decimal kHz forms ("1.0 kHz" → token "1.0" vs scaled
  string "1"). The affected values ARE present in the quotes in their
  original units and the Hz conversions are arithmetically correct:
  690336: 250000, 6000000, 2200000 (from 0.25-6 MHz, 2.2 MHz);
  18345867: 33000000 (33-MHz); 9387996: 1000, 2000 (1.0, 2.0 kHz);
  512209: 2000000 (2 MHz). These rows were left with the values recorded
  rather than dropping genuine stimulus data; a numeric (float) comparison
  in number_in_quote would clear all 7 ERRORs. The MHz values additionally
  raise implausible_value WARNs (above the 200 kHz plausibility cap), which
  is expected for ultrasound studies.
- 18345867: the 33-MHz transducer frequency was NOT enumerated in
  candidates_all.csv (enumerator miss); it was recorded from the abstract
  because it is the paper's one genuine acoustic frequency. The two dB
  candidates (0.6, 0.4) are the ± error terms of attenuation-slope results
  (2.6±0.6 and 2.5±0.4 dB/cm-MHz) — an attenuation slope in dB/cm-MHz is
  not a sound level and has no matching column, so they were not recorded.
- 35131579 and 12062768: candidates captured only the trailing pair
  ("16 and 32 kHz"); the abstracts state the full discrete stimulus sets
  (8, 16, 32 kHz and 2, 4, 8, 16, 32 kHz), which were recorded in full —
  every recorded number appears in the single quoted sentence.
- 15219315: the constant 41 in "L1=0.46 L2 + 41 dB SPL" is a formula
  intercept for computing L1, not a presented level; only the stated L2
  range (15-60 dB SPL) was recorded in Sound_Level_dB.
- 4086386 (50 dB), 26386286 (95 dB), 40816165 (30-40 dB), 8226345 (55/80 dB
  HL): recorded in Sound_Level_dB as stated, but each is a relative or
  reference-based quantity (interaural difference / threshold-difference
  criterion / threshold elevation / dB HL), not an absolute presented SPL.
  All are Reference rows, so none can enter design statistics.
- 4066520: 4000 Hz recorded alongside the exposure frequency because it is
  stated in the same span, but it is an outcome (frequency of maximum
  threshold elevation), not a stimulus parameter.
- 9925011 / 8789820 / 3610862: recorded frequencies are cochlear place /
  characteristic / tuning values (anatomical or measured), not stimulus
  frequencies — recorded as Reference data with the basis noted above.
