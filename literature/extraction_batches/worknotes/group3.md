# Worknotes — extraction group 3 (batches 12, 13, 14)

Primary extraction of the 28 candidate-bearing papers in batches 12–14.
Validator on the three output files: **0 errors, 15 warnings** (all
`unit_converted`, expected). Decision counts: Include 17, Reference 10,
Count_only 1.

## Per-paper lines (PMID — Decision — basis)

### Batch 12
- 11785816 — Include — DPOAE STCs recorded at f2 = 1500, 3000, 6000 Hz in children/adults; stimulus frequencies, stratum A kept (neonate STCs from a previous study are part of the comparison dataset; see Ambiguous).
- 10748332 — Reference — 6 kHz exposure tone in kittens; stratum corrected A→C (animals only), so gate condition 1 fails.
- 10867273 — Reference — f2 range 1.7–10 kHz is stated only for the adult subgroup's stimulus-level experiment; neonatal stimulus frequencies not stated (see Ambiguous).
- 10936438 — Include — fetuses received sound trials at 90, 100, 105, 110 dB; set stimulus levels, stratum A.
- 10212420 — Include (MIXED) — DPOAE f2 = 1500, 3000, 6000 Hz recorded; the 10 dB primary level separation was omitted (see MIXED).
- 10212425 — Include — broadband noise forward masker set at 65 dB SPL; infants and adults, stratum A.
- 10452385 — Include — contralateral broad band white noise presented at 70 dB SPL to neonates; set stimulus level.
- 10530014 — Reference — 20–200 Hz is the range of fitted damping coefficients of OAE spectral lines in a modeling paper, not a stimulus frequency.
- 10575120 — Include (MIXED) — PAMR evoked with tone-bursts between 500 Hz and 16 kHz; 20 dB (relative to threshold) and the 25–200 Hz response spectrum omitted (see MIXED).
- 10195705 — Count_only (NO_ACOUSTIC_IN_ABSTRACT) — fetal heart-rate dynamics paper; the only candidate (0.04–0.15 Hz) is the low-frequency component of heart-rate variability, not an acoustic value.
- 9479751 — Reference — f2 extremes stated only in results framing ("highest/lowest frequencies assessed": 4.2–9.9 kHz, 1.5–2.1 kHz), not as a stated stimulus set; measured dB values omitted (see Omitted).

### Batch 13
- 9682815 — Include — DPOAE suppression measured at f2 = 1500 and 6000 Hz in adults, term and premature neonates; stimulus frequencies, stratum A.
- 9872134 — Include (MIXED) — ABR tone-burst range 500–8000 Hz recorded; the 7.45/1.56 dB values are between-gender threshold differences (outcomes) and were omitted (see MIXED). Stimulus range is attributed to the previous study whose data are reanalyzed (see Ambiguous).
- 9104019 — Reference — theoretical paper: 10 kHz is a frequency bound and 3/1.3 dB are predicted evanescent-wave measurement errors, not set stimulus parameters.
- 9119764 — Include (MIXED) — ABR tone-bursts 0.5, 1.5, 4.0, 8.0 kHz; cell holds 500, 1500 only (see Validator limitation); the 3–25 dB threshold elevation is an outcome difference and was omitted (see MIXED).
- 9165342 — Reference — 20 Hz / 150 Hz are model-derived functional implications for the cochlear aqueduct, not stimulus parameters. Stratum A kept per manual screening (0–1-year temporal-bone specimens included; the batch input itself flags this paper AMBIGUOUS).
- 9387986 — Reference — opossum study; stratum corrected A→C. 83/58 dB SPL are measured hearing thresholds and 13 kHz is the isolation-call spectral peak (outcome values).
- 9387991 — Reference — cat ototoxicity study; stratum corrected A→C. 2.8–8 kHz is a cochlear place-frequency estimate for the lesion region, not a stimulus.
- 9407658 — Include — pure tones of 160 and 200 Hz (and missing-fundamental complexes) presented to 7-month-olds and adults; set stimulus frequencies.

### Batch 14
- 8584373 — Include — infants exposed to 90 dB(A) white noise during REM sleep; set stimulus level, stratum A.
- 8844189 — Reference — gerbil cochlea anatomy; stratum corrected A→C. ~11.2 kHz is an example place-code frequency, not a stimulus.
- 8880180 — Include (MIXED) — DPOAE primaries L2 = 50 dB SPL and neonatal STCs at f2 = 3000, 6000 Hz recorded (quote is one long contiguous span covering both sentences); the 6 dB suppression criterion was omitted (see MIXED); L1 = 65 dB SPL missed by candidate enumeration (see Enumeration gaps).
- 8969474 — Include — two f2 frequencies investigated: 1500 and 6000 Hz, in adults and neonates. (The 10–15 dB primary level separations in the abstract are level differences, not levels, and were not candidates.)
- 7560507 — Include (MIXED) — missing-fundamental frequencies 160 and 200 Hz recorded; the 30 Hz / 20 Hz upward partial shifts are frequency increments, not stimulus tone frequencies, and were omitted (see MIXED).
- 7593925 — Reference — 100 Hz is the infant ABR spectral concentration and 30 Hz is a high-pass recording-filter setting; neither is a stimulus frequency. The actual 500-Hz tone-burst stimulus was missed by candidate enumeration (see Enumeration gaps).
- 7608394 — Include — missing-fundamental frequencies 160 and 200 Hz in 7–8-month-old infants; set stimulus values.
- 7642831 — Include — tone-pips at 1000, 4000, 8000 Hz at 50 dB nHL presented to 3-/6-month-olds and adults; set stimulus parameters.
- 7714257 — Include — notched-noise masking center frequencies ranging from 500–8000 Hz are set masker parameters; infants and adults, stratum A.

## Stratum corrections

- 10748332: A → C (5-week-old kittens only; cortical mapping after noise trauma).
- 9387986: A → C (short-tailed Brazilian opossum pups only).
- 9387991: A → C (young kittens only; neomycin ototoxicity).
- 8844189: A → C (infant and adult gerbils only; cochlear morphology).

## MIXED rows (passing values recorded as Include; failing values omitted)

- MIXED 10212420 — omitted Sound_Level candidate 10 dB: it is the level *separation* between the DPOAE primaries (L1 > L2 by 10 dB), a level difference, not a stimulus sound level (gate condition 2).
- MIXED 10575120 — omitted 20 dB (level relative to the subjective detection threshold, i.e. sensation level, not an absolute sound level) and 25–200 Hz (spectrum of the PAM *response*, an outcome property, not a stimulus frequency).
- MIXED 9872134 — omitted 7.45 dB and 1.56 dB: between-gender ABR threshold *differences* (outcome statistics), not sound levels.
- MIXED 9119764 — omitted 3–25 dB: infant ABR threshold *elevation* relative to adults (outcome difference), not a stimulus level.
- MIXED 8880180 — omitted 6 dB: the DPOAE amplitude-reduction criterion defining the suppression tuning curve, not a sound level.
- MIXED 7560507 — omitted 30 Hz (experiment 1) and 20 Hz (experiment 2): upward *shifts* applied to the partials of the tonal complexes (frequency increments), not stimulus tone frequencies.

## Omitted scattered values

- 10867273 — f2 = 3.4 and 7.0 kHz (specific values in the adult stimulus-level analysis, in a sentence separate from the recorded range) and the <4 kHz / >4 kHz category boundaries (descriptive groupings, not set values) were not recorded.
- 9479751 — 5–15 dB (measured ear-canal noise levels, an outcome), 1.5 dB (DPOAE amplitude reproducibility statistic), and ~3 kHz (boundary in an outcome comparison) were not recorded; only the two assessed-f2 ranges were kept, under Reference.

## Candidate enumeration gaps (values present in the abstract but absent from candidates_all.csv; NOT extracted, flagged for adjudication)

Pattern: candidates.py appears to miss hyphenated adjectival forms ("1000-Hz") and unit-sharing lists.

- 10212425 — the probe is a "1000-Hz" tone burst (the paper's primary stimulus); only the 65 dB SPL masker was enumerated and extracted.
- 7593925 — ABR stimuli include "500-Hz tone bursts"; not enumerated. If restored, this row would gain a passing stimulus frequency (500 Hz) alongside the Reference filter values — recheck the Decision in that case.
- 8880180 — primary level L1 = 65 dB SPL ("LI = 65 and L2 = 50 dB SPL", unit shared with L2); only L2 = 50 was enumerated and extracted.

## Validator limitation (needs a validator-side fix; flagged, not worked around silently)

- 9119764 — the abstract states tone-bursts of "4.0 and 8.0 kHz". The validator's kHz-conversion check string-matches the scaled value ("4", "8") against quote tokens ("4.0", "8.0") and fails, producing number_not_in_quote ERRORs for 4000/8000. The cell therefore holds only 500, 1500; the full set (0.5, 1.5, 4.0, 8.0 kHz) is preserved in the row's Stimulus_Type text. Suggested fix: compare numerically rather than by string equality in the converted branch of `number_in_quote`; then restore 4000, 8000 to Frequency_Hz.

## Ambiguous judgments

- 11785816 — stratum A kept: this study's own participants are school-aged children and adults; premature-neonate STCs were collected in a *previous* study and used for age comparison. If stratum A requires under-2 participants measured in the study itself, this row should move to B and its (otherwise passing) frequencies to Reference.
- 10867273 — Reference chosen: the only stated f2 range (1.7–10 kHz) belongs to the adult subgroup's level experiment; the paper is stratum A (105 neonates + 40 adults) but no neonatal stimulus frequencies are stated. Recording the range as an A-layer Include would attribute adult stimulus parameters to the infant population.
- 9872134 — Include kept: the 500–8000 Hz stimulus range is attributed to "a previous study" whose ABR data this paper reanalyzes; judged to describe the stimuli of the dataset under analysis rather than background citation.
- 10530014 — Reference (not Count_only): the 20–200 Hz damping-coefficient range is a property of acoustic (OAE) signals, so it was recorded as a Reference value even though it is neither a stimulus frequency nor a fitted stimulus parameter; a Count_only/NO_ACOUSTIC reading is also defensible.
- 9104019 — Reference (not Count_only): predicted evanescent-wave error magnitudes (3 dB adults / 1.3 dB infants below 10 kHz) are acoustic-domain quantities recorded for reference; they are theoretical predictions, not measurements or stimuli.
