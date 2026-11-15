# Worknotes — Group 2 (batches 7–11), primary extraction

Validator: 0 errors, 24 warnings (all `unit_converted`, expected).
Counts: Include 16 / Reference 11 / Count_only 1 (28 papers).

## Per-paper lines (PMID, Decision, basis)

### Batch 7
- 21974484, Reference — animal study (infant bats); recorded pup vocalization frequencies are observed outcomes, not set stimuli; stratum corrected A→C (see below). Candidates were the ±SD figures (4.0/1.9/2.6 kHz); the stated center frequencies 19.3 kHz (pup terminal) and 41.4 kHz (adult TF) were extracted instead.
- 20950966, Include — oddball paradigm tones 1000/2000 Hz set as stimulus parameters in preterm infants (A).
- 19206878, Include — 1 kHz detection tone set as stimulus; infants included (A).

### Batch 8
- 19757874, Include — music presented at set average levels 65/70/75 dB to preterm infants (A).
- 18345839, Reference — 1.5/2/3/4 kHz are frequencies across which recorded OAE/ABR responses were evaluated (analysis frequencies of emissions), not presented stimulus tones; fails gate (3).
- 19045786, Reference — 1.5–2.5 kHz is the analysis band in which an observed latency decrease occurred (finding), not a set stimulus; fails gate (3).
- 19062852, Reference — 0.25–0.75 / 0.75–2 / 2–6 kHz are measurement bands of wideband ATF results, not discrete set stimulus tones; fails gate (3).

### Batch 9
- 17348521, Reference — f2 = 6 kHz is explicitly attributed to a previous study (background/prior work); fails gate (3). Modeling paper reusing prior data.
- 17550168, Reference — NICU LEQ 61–63 / 55–60 dB are measured environmental sound levels (observed), not set stimuli; fails gate (3).
- 17552713, Reference — f2 = 6000 Hz is stated as previous work's finding; this study's own f2 is not restated in the abstract; fails gate (3).
- 17850998, Count_only (NO_ACOUSTIC_IN_ABSTRACT) — only candidate was 3.8 dB, an SNR *improvement* (a statistic/difference, not a sound level); click rates (50/s, 5000/s) are not values in any numeric column. Numeric cells cleared.
- 16459037, Include — tones 400/3000 Hz at 60 dB HL set as stimuli; newborns included (A). MIXED (see below).
- 16644155, Reference — 1.5/3/4 kHz are observed SOAE distribution peaks (outcomes), not set stimuli; fails gate (3).
- 16838539, Include — 1000-Hz signal tone and maskers at 60 dB SPL set as stimuli; infants included (A). The 1000 Hz was NOT in candidates_all (enumerator missed the hyphenated form "1000-Hz"); extracted from the abstract and flagged here.

### Batch 10
- 17225410, Reference — modeling/reanalysis paper; f2 = 6000 Hz appears only in a results statement about prior infant/adult DPOAE data, not presented as this study's set stimulus in the abstract; fails gate (3).
- 15574301, Reference — 0.25–6.25 kHz is the wavelet analysis band range of recorded CEOAEs, not a set stimulus; fails gate (3).
- 15807032, Reference — no human subjects (theory + water-tank); stratum corrected A→UNDETERMINED (see below). 100 dB is a modeled generated level and 20 kHz is the audible-range bound; fails gate (1)/(3).
- 15867039, Include — white noise 50–100 dB(A) presented as set stimulus range to infants (A).
- 15957767, Include — DPOAE test frequencies f2 = 1.5–8 kHz set as stimulus parameters in neonates (A).
- 16086603, Include — lullaby music presented at set loudness ranges 55–60 / 65–70 / 75–80 dB to 1-day-old infants (A).
- 16240817, Include — DPOAE suppression measured in this study at set f2 = 1500/6000 Hz; term newborn comparison group keeps stratum A.

### Batch 11
- 15139625, Include — f2 frequencies 2000/4000/6000 Hz set as stimulus parameters; infants included (A). (Candidate "4000 and 6000 Hz" normalized as a range was a discrete set; recorded as a set.)
- 15286256, Include — white noise 50–100 dB(A) presented as set stimulus range to infants (A).
- 15658708, Include — DPOAE suppression measured in this study at f2 = 6000 Hz, L1/L2 = 65/55 dB SPL; infants included (A).
- 12942974, Include — f2 = 1500/6000 Hz and primary level pairs 55-45/65-55/75-65 dB SPL set as stimuli; neonates included (A). Level pairs recorded as stated (L1-L2 pairs), not flattened.
- 14714805, Include — DPOAE suppression/I-O measured in this study at f2 = 6000 Hz; neonates included (A).
- 11386562, Include — 1000-Hz detection tone is a set stimulus parameter; infants included (A). The 1000 Hz was NOT in candidates_all (hyphenated "1000-Hz" missed by the enumerator); extracted from the abstract and flagged here. MIXED (see below).
- 11407963, Include — TEOAE burst presented at a set level of 78–83 dB SPL to newborns (A). MIXED (see below).

## Stratum corrections
- 21974484: A → C. Subjects are infant Japanese echolocating bats (animals only); shell stratum A was a first-pass error.
- 15807032: A → UNDETERMINED. No human or animal subjects (theoretical model + water-tank measurement of ultrasound scanner sound); participant age is not stated and no infant subjects were studied, so it cannot enter stratum statistics as A.

## MIXED rows (passing values recorded as Include; failing values omitted)
- MIXED 16459037 — recorded: 400 Hz, 3000 Hz, 60 dB HL (set CAEP stimuli). Omitted: 0.22 Hz presentation rate — a repetition rate, not a stimulus tone frequency (gate 2).
- MIXED 11386562 — recorded: 1000 Hz (set detection tone). Omitted: threshold *differences* of 14/7 dB (unmasked) and 10/5 dB (masked) — group-difference statistics, not set sound levels (gate 3); the signal level itself was adaptive and no set level is stated.
- MIXED 11407963 — recorded: 78–83 dB SPL (set TEOAE burst level). Omitted: 1.6/2.4/3.2/4.0 kHz — frequencies at which the emission *responses* were recorded (analysis bands of a broadband burst response), not stimulus tone frequencies (gate 2).

## Omitted scattered values (not coverable by a single contiguous quote span, or not matchable)
- 17348521 — "−16 dB" forward middle-ear transmittance difference: a model-derived relative level, not a sound level; also not in the same span as the 6 kHz quote. Not recorded.
- 17550168 — recommendation thresholds 45 dB (AAP), 50/55/70 dB (SSG) and peak exceedance >90 dB: background recommendations and a separate measured statistic, scattered outside the LEQ span. Not recorded (the measured LEQ ranges were recorded).
- 17552713 — 5700 Hz (admittance-phase frequency in one correlation result): scattered in a later paragraph, outcome-side analysis frequency. Not recorded.
- 15574301 — "4 kHz" (frequency region where development was greater): scattered near the end of the abstract, outside the analysis-band span. Not recorded.
- 21974484 — 30000 Hz (FM sweep start, "30.0 kHz"): could not be recorded because the validator's kHz-conversion check does not match whole numbers written with a trailing ".0" ("30" ≠ "30.0"); recording it would produce a number_not_in_quote ERROR. The value is present in the row's Evidence_Quote.
- 15807032 — 2000000 Hz ("2 MHz" scanner carrier): the validator only supports kHz→Hz conversion matching, so this value cannot validate against the quote; it is also a device carrier frequency rather than the audible stimulus under study. Present in the row's Evidence_Quote; not in the cell.

## Ambiguous judgments made
- 18345839 / 19062852 / 15574301 (Reference): OAE/tympanometry measurement and analysis frequency bands were treated as failing gate (3) because the abstract presents them as dimensions along which recorded responses were evaluated, not as presented stimulus tones. DPOAE primary frequencies (f2), by contrast, were treated as set stimulus parameters (Include) where the abstract states they were measured/presented in the study itself (15658708, 16240817, 14714805, 12942974, 15139625, 15957767).
- 17225410 / 17552713 / 17348521 (Reference): where the abstract attributes the test frequency to previous work or the paper is a model/reanalysis of prior data, gate (3) was judged to fail even though the same paradigm frequency presumably applied.
- 17850998 (Count_only): the sole candidate (3.8 dB SNR improvement) was judged a statistic, not an acoustic stimulus/outcome level, following the "numbers that are statistics" clause; the paper's acoustic content is noted in its Stimulus_Type/Outcome fields.
- 11386562 / 16838539: stimulus frequencies written in hyphenated form ("1000-Hz") were absent from candidates_all.csv but were extracted from the abstracts because they are unambiguous set stimulus parameters; flagged here for protocol review.
