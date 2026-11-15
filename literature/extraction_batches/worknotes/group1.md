# Worknotes — Group 1 (batches 2–6), primary numeric extraction

Validator (batches 2–6, 105 rows): 0 errors, 15 warnings — all
`unit_converted` (kHz→Hz), expected.

Decision counts for the 25 candidate papers in this group:
Include 9 / Reference 14 / Count_only 2.

## Per-paper lines

- 34823054 (b2) Reference — EEG rhythm band edges (theta/alpha/beta/gamma) recorded in Frequency_Hz; gate cond. 2 excludes EEG bands.
- 30612027 (b2) Reference — bat ABR tone-pip range 5–90 kHz; stratum corrected A→C (animals only), gate cond. 1.
- 31255105 (b2) Reference — 10 Hz is an AM rate (not carrier), 4/10 dB are modulation-depth / MDT-difference values, not SPL; gate cond. 2/3.
- 29534830 (b3) Include — 500 Hz AM-tone carrier presented to maternal abdomen; fetuses 31–40 wk, stratum A; all gate conditions met.
- 30077866 (b3) Include — 70 bpm is the stated tempo of the heartbeat-recording stimulus track presented to newborns (see Judgments).
- 28372113 (b3) Reference — 5–6 dB is a measured SOAE level difference (outcome), not a stimulus level; gate cond. 3.
- 28863611 (b4) Include — 70 dBA is the set babble-noise environment level of the Lombard condition (see Judgments).
- 27036239 (b4) Reference — frog call F0 values (observed call properties); stratum corrected A→C (animals only).
- 25618103 (b4) Include — 15/25/40 dB SPL are the SFOAE stimulus levels presented (see Judgments).
- 26428839 (b4) Include — ±6 dB/octave spectral tilt is a set stimulus condition; recorded as magnitude 6 in Attenuation_dB_oct (candidates had misfiled it under Sound_Level_dB).
- 26723319 (b5) Reference — 0.2–8 kHz is a measurement-procedure frequency range, not a stimulus tone frequency; gate cond. 2/3.
- 25096110 (b5) Include — MF fundamentals (160/190/200 Hz), band ranges (2500–4500, 4000–6000 Hz), −12 dB/oct filter slope (moved to Attenuation_dB_oct), 65/70 dB SPL presentation levels; all set stimulus parameters.
- 25234993 (b5) Reference — 0.5–4 kHz (+8 kHz young adults) is the DPOAE measurement range, not set stimulus frequencies; gate cond. 2/3.
- 25463830 (b5) Count_only — candidates are cardio-respiratory coupling frequency ranges (0.7–1.5, 0.15–0.45 Hz); no acoustic values at all. NO_ACOUSTIC_IN_ABSTRACT.
- 23363111 (b5) Reference — 1.5 kHz is the observed upper region of strongest MOC reflex (outcome characterisation), not a set stimulus frequency; gate cond. 3.
- 23764671 (b6) Include — IRN stimulus F0 values 167 and 200 Hz, set stimulus parameters; 8-month-olds, stratum A.
- 22280722 (b6) Include — complex-tone fundamental 240 Hz and 6 dB/octave roll-off (moved to Attenuation_dB_oct); set stimulus parameters.
- 23145607 (b6) Count_only — the only candidates (2.53/2.02 dBA) are ANN forecast-error statistics, not acoustic condition values. NO_ACOUSTIC_IN_ABSTRACT.
- 23231118 (b6) Include — MF fundamentals 160/200 Hz, masking-noise band 60–260 Hz, −12 dB/octave filter slope (moved to Attenuation_dB_oct); set stimulus parameters.
- 21144889 (b6) Reference — FM-sweep exposure range 0.1–20 kHz is a set stimulus, but stratum corrected A→C (chinchillas), gate cond. 1.
- 21147207 (b6) Reference — 10–11 dB is a measured hearing-threshold group difference (outcome); gate cond. 3.
- 21476616 (b6) Reference — 6 kHz is reported as the locus of the greatest infant–adult STC difference (a result), not as the stimulus condition set (see Judgments).
- 21568380 (b6) Reference — 64 Hz is the envelope low-pass cutoff of the processed speech stimuli, not a carrier/stimulus tone frequency; gate cond. 2 (see Judgments).
- 21568413 (b6) Reference — 0.5–4 kHz is the swept-tone measurement protocol range; gate cond. 2/3.
- 21682402 (b6) Reference — 2/4.25 kHz are the reference frequencies of measured CEOAE shift rates (outcomes); the 10/30 Hz/week rates are not Hz values and were not recorded.

## Stratum corrections

- 30612027: A → C (bats, Phyllostomus discolor, only).
- 27036239: A → C (frogs, Odorrana tormota, only).
- 21144889: A → C (chinchillas only).

## MIXED rows

None. No paper had a mix of passing and failing values where only the
passing subset was recorded.

## Omitted scattered values (not coverable by the single recorded quote span, or not the column quantity)

- 26723319: 2000 Hz ("frequency above 2 kHz of minimum absorbance") — a definitional/measured quantity in a different sentence; omitted.
- 25234993: 1000 Hz ("bend near 1 kHz") — observed outcome feature in a different sentence; omitted.
- 21568413: 1000–1500 Hz ("above ∼1–1.5 kHz" demarcation) and 1400/1000 Hz (discontinuity locations, adults/infants) — observed outcomes in different sentences; omitted, only the protocol range recorded.
- 21144889: sweep speeds 0.05 and 0.05–0.82 kHz/ms were mechanically mis-parsed as 50 / 50–820 Hz candidates; they are rates (kHz/ms), not frequencies, and were not recorded as Frequency_Hz.
- 21682402: 10 and 30 Hz/week (shift rates) — units are Hz/week, not Hz; not recorded (their reference frequencies 2000/4250 were recorded).
- 30612027: 20 kHz candidate is an interior bound of the recorded 5000–90000 range ("not only below 20 kHz but up to 90 kHz"); not recorded separately.
- 31255105: all candidates were recorded (10 Hz; 4, 10 dB) under Reference; none omitted.

## Judgments on ambiguous points

- 30077866 (Include): the 70 bpm heartbeat track is a pre-existing recording, not a synthesised tempo; judged Include because the tempo is a defining, unambiguous property of the stimulus actually presented to the newborns (unlike pilot 42777332, where 30 bpm was an observed everyday-singing value of ambiguous meaning).
- 28863611 (Include): 70 dBA babble is the acoustic environment of the Lombard recording condition rather than a stimulus presented to infants; judged Include as a set experimental acoustic condition with an unambiguous absolute level. Participants producing the measured speech are the mothers; infants (12 mo) are the IDS interaction partners, stratum A kept.
- 25618103 (Include): 15 dB SPL is the lowest stimulus level presented; the <40 (newborns) / <25 (adults) dB SPL bounds describe where growth was linear, i.e. they are partly descriptive of responses, but the values themselves are presented stimulus levels, so all three were recorded as Include.
- 26428839 / 22280722 / 25096110 / 23231118: candidates.py filed dB/octave slopes under Sound_Level_dB; they were recorded in Attenuation_dB_oct (magnitude only, as the validator's number parsing is sign-blind; the ± conditions are spelled out in Stimulus_Type).
- 21476616 (Reference): the abstract calls 6 kHz a "stimulus frequency", but the value is singled out because the group difference was greatest there — a result-selected locus, not the (unstated) set of stimulus frequencies used; judged Reference under gate cond. 3.
- 21568380 (Reference): 64 Hz is a set processing parameter of the stimuli, but it is an envelope cutoff, not the carrier/stimulus tone frequency the column defines; judged Reference under gate cond. 2 (parallel to AM-rate handling).
- 23145607 (Count_only): the paper is about NICU noise, but the abstract states no numeric acoustic condition; its only dB figures are forecast-error statistics, matching the "statistic" example in the Count_only rule.
