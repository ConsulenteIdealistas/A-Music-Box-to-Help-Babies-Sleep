# Extraction work notes — group 4 (batches 15, 16, 17)

32 candidate papers extracted. Decisions: Include 8 / Reference 18 / Count_only 6.
Validator (batch_15+16+17): 0 errors, 25 warnings (all unit_converted, expected).

## Per-paper lines

### Batch 15
- 8600128 | Reference | A kept. Only coherent values are AM rates (40, 80 Hz); AM rates are not carrier frequencies (gate 2).
- 8647727 | Include | 1 kHz tone set as stimulus for infants 8-11 mo and adults; dB differences not recorded (see MIXED).
- 7928706 | Reference | Bat study (stratum corrected to C). Adult/newborn hearing ranges and 90 dB SPL ceiling recorded.
- 7928741 | Include | 4 and 8 kHz tone pips set as stimuli in 3-/6-month-olds and adults.
- 8040097 | Reference | Cat study (stratum corrected to C). FFR test tone 500 Hz; electrical stimulation 2 dB above ABR threshold.
- 8120247 | Reference | Human infants 1-24 mo, but 125-10700 Hz is a measurement range, not a set stimulus parameter (gate 3).
- 8157500 | Count_only | Guinea-pig fetus study (stratum corrected to C). No stimulus frequency/level stated; 20 dB is an outcome difference.
- 8113139 | Reference | Chick study (stratum corrected to C). Exposure tone 0.9 kHz at 120 dB SPL; 57 dB is the resulting threshold loss.
- 8226331 | Reference | Human newborns; SOAE levels are observed emissions, not set stimuli (gate 3). Level range -2 to 42 dB SPL recorded.
- 8226347 | Reference | Chick study (stratum corrected to C). Exposure 0.9 kHz / 120 dB SPL; test/probe frequency ranges and 57 dB threshold shift recorded.
- 8226352 | Reference | Newborn chicken study (stratum corrected to C). 500-Hz masker at 15/25 dB above threshold.

### Batch 16
- 8270739 | Reference | Human infants + adults, but 125-10,700 Hz is a measurement range (gate 3).
- 8300947 | Reference | Tree shrew study (stratum corrected to C). Behavioral test range 0.3-60 kHz recorded.
- 8354755 | Reference | Pregnant women; 10-500 Hz is a mechanical shaker vibration range, not an airborne acoustic stimulus (gate 2/3 judgment).
- 8376210 | Include | Tone pips at 1, 4, 8 kHz set as stimuli in 3-/6-month-olds and adults.
- 8376214 | Reference | AM rates 10-80 Hz recorded; AM rates are not carrier frequencies (gate 2).
- 8509307 | Include | Click levels 75/45/15 dBnHL set as stimuli in newborns (26-43 weeks gestation).
- 1464577 | Include | 500 Hz signal + 500 Hz-centred masker set as stimuli in 7-10-month-old infants.
- 1490906 | Reference | Cat study (stratum corrected to C). Electrical stimulation intensities 2 and 6 dB above EABR threshold.
- 1506534 | Count_only | No stimulus frequency/level stated; the only dB value (7 dB) is an observed near/far difference, not a set level.
- 1559899 | Count_only | Chick study (stratum corrected to C). See "Ambiguous / format-limited" below.
- 1564194 | Reference | Human neonates + adults; SOAE levels are observed emissions (gate 3). Levels -2.6 (adults) and 8.5 (infants) dB SPL recorded.

### Batch 17
- 1938628 | Reference | Cat study (stratum corrected to C). FFR test 500 Hz; electrical stimulation 6 dB above ABR threshold.
- 1938629 | Reference | Cat study (stratum corrected to C). Electrical stimulation 6 dB above EABR threshold.
- 1960280 | Include | 1000-Hz tone bursts set as stimulus in 3-/6-month-olds and adults; candidate dB values are outcome statistics (see MIXED).
- 2061219 | Reference | Newborn chick study (stratum corrected to C). Background-tone frequencies 500-608 Hz.
- 2299044 | Include | Infant S/N conditions -8, 0, 8, 16 dB recorded; adult comparison set not recorded (see MIXED).
- 2358411 | Count_only | Newborn chicken study (stratum corrected to C). Stimulus frequencies/levels not stated; 6 dB is an outcome slope (threshold decrease per duration doubling).
- 2681313 | Count_only | In vitro human fetal bone; 1 MHz exposure cannot be recorded in Frequency_Hz (see "Ambiguous / format-limited"). Stratum A kept per screening note (fetal human tissue).
- 2768086 | Count_only | Cat study (stratum corrected to C). No stimulus frequency/level stated; 3.05/2.89 dB values are outcome slopes vs blood oxygen.
- 2808150 | Reference | Chick study (stratum corrected to C). Exposure 0.9 kHz at 120 dB; 60 dB is the resulting threshold shift.
- 2808922 | Include | Octave-band noise center frequencies 0.4-10 kHz and masker levels 0/10 dB/cycle set as stimuli; includes listeners from 6.5 months (stratum A kept).

## Stratum corrections (shell A -> C, animals only)

- 7928706 (bat, Carollia perspicillata)
- 8040097 (cats/kittens)
- 8157500 (guinea-pig fetuses)
- 8113139 (neonatal chicks)
- 8226347 (neonatal chicks)
- 8226352 (newborn chickens)
- 8300947 (tree shrews)
- 1490906 (neonatally deafened cats)
- 1559899 (chicks)
- 1938628 (neonatally deafened cats)
- 1938629 (neonatally deafened cats)
- 2061219 (newborn chicks)
- 2358411 (newborn chickens)
- 2768086 (cats)
- 2808150 (one-day-old chicks)

No corrections to B or UNDETERMINED. 2681313 kept at A (in vitro human fetal tissue, per the screening note in the input file). 2808922 kept at A (listeners from 6.5 months). 8354755 kept at A (adult pregnant women; shell value retained, but the row is Reference on gate 2/3 grounds).

## MIXED rows (passing values recorded as Include; failing values dropped)

- MIXED 8647727: recorded 1000 Hz (Include). Dropped: 12 dB (infant-adult behavioral threshold difference), 8 dB (MML difference / sensory portion), 4 dB (non-sensory portion) — all measured outcome differences, not set sound levels (gate 3).
- MIXED 1960280: recorded 1000 Hz (Include; taken from the abstract text "1000-Hz, 16-ms tone bursts" — this stimulus frequency was NOT in the candidate list, whose only candidates were dB values). Dropped: 5 dB and 10 dB (between-block threshold changes) and 5 dB (effect of excluding high-false-alarm infants) — outcome statistics, not set levels (gate 3).
- MIXED 2299044: recorded infant S/N conditions -8, 0, 8, 16 dB (Include). Not recorded: adult comparison S/N set (-12, -8, -4, 0 dB) — set conditions, but for the adult comparison group, not the infant subjects this row targets; and 5.8 dB (group mean threshold difference, an outcome).

## Omitted scattered values (not coverable by the chosen single quote span, or not validatable)

- 8600128: carrier frequencies 500, 1000, 2000 Hz appear later in the abstract (EFR threshold results sentence), outside the span covering the AM rates; not recorded.
- 8120247: observed ear-canal resonance frequencies (4.4 -> 2.9 kHz) and concha resonance frequencies (5.5 -> 4.5 kHz) are in later sentences, outside the span covering the 125-10700 Hz measurement range; not recorded (they are observed outcomes in any case).
- 8354755: observed abdominal resonance 28 +/- 16 Hz is in a later sentence, outside the shaker-range span; not recorded.
- 8226331: mean SOAE level 8.0 dB SPL not recorded — the validator's number matching cannot match "8.0" in the quote to the cell value 8 (integer formatting), so it would ERROR. The -2 to 42 dB SPL range is recorded instead. The "above 2 kHz" emission-frequency bound was also not recorded (a distributional bound, not a value set).
- 1564194: SOAE frequency ranges (adults 1.0-2.0 kHz; neonates 2.5-5.0 kHz) not recorded — the validator cannot match the "1.0"/"5.0" decimal tokens to normalized values 1000/5000, so entering them would ERROR. Levels were recorded.
- 8113139: the 15 dB recovered threshold-loss value (12 days post-exposure) lies in the same span but was not entered; the 57 dB initial loss represents the outcome measure.
- 8226347: Q10 dB candidate "10 dB" is part of a metric name (Q10 dB), not a sound level; not recorded.

## Ambiguous / format-limited judgments

- 1559899 (Count_only, flagged): the abstract DOES state a stimulus/measurement frequency range (0.2-10.0 kHz) and an 11 dB low-frequency sensitivity increase, but the range cannot be entered: the validator cannot match the "10.0" kHz token to the normalized value 10000 (it only accepts exact token or kHz-scaled integer formatting), so entering "200-10000" produces a number_not_in_quote ERROR (verified empirically). The 11 dB value is an outcome change, not a level. Rather than truncate the range to 200 Hz (which would falsify it), the row is Count_only with NO_ACOUSTIC_IN_ABSTRACT, the range is written into Stimulus_Type, and the quote documents it. Needs a parent decision if this convention is not acceptable.
- 2681313 (Count_only, flagged): the abstract states a clear stimulus condition (1 MHz continuous-wave ultrasound), but the validator has no MHz->Hz conversion path (only kHz), so entering 1000000 ERRORs (verified empirically). Followed the existing in-file precedent of PMID 2199548 (3.6-MHz ultrasound, same batch), which is Count_only with the MHz value written into Stimulus_Type. Flagged for parent awareness.
- 1960280: stimulus frequency (1000 Hz) extracted from the abstract although absent from candidates_all.csv; the paper was in the candidate list (for its dB values), so it was in scope.
- 2299044: Sound_Level_dB holds signal-to-noise ratios (dB S/N), the only level-like set conditions in the abstract; no absolute stimulus level is stated. The negative value -8 parses as 8 in the validator and matched the quote verbatim.
- 2808922: masker levels recorded as "0, 10" (dB/cycle as stated). Center frequencies include the 1/3-octave-band noise at 10 kHz, already in the set.
- 7928706: Frequency_Hz holds two ranges (adult 7000-110000 and newborn 8000-76000) comma-separated in one cell.
- 8226331: level range written "-2-42" (from "between -2 and 42 dB SPL"); the leading minus is not parsed by the validator but both endpoints matched.
- 8509307: click presentation rates (10/s, 55/s, 80/s) are not candidates and were not recorded (no Tempo_BPM — they are stimulus repetition rates for evoked potentials, not musical tempo; left unrecorded rather than forced into a column).
