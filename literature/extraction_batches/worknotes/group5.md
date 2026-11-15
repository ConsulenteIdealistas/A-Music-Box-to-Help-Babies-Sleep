# Group 5 worknotes — extraction batches 18, 19, 20 (primary extraction)

Validator result (batch_18/19/20): **0 errors**, 18 warnings (11 unit_converted on
extracted rows — expected; 7 no_abstract on pre-filled Count_only rows in batch 20,
not extraction rows).

Counts: Include 11 (incl. 3 MIXED), Reference 9, Count_only 0 (of the 20 candidate
papers). Stratum corrections: 2 (both A -> C, animal-only studies).

## Per-paper log (PMID — Decision — basis)

### Batch 18
- 3198866 — Include (MIXED) — Pure-tone stimulus range 250-8000 Hz recorded; infant-adult threshold differences (dB) are measured outcomes, omitted (see MIXED).
- 3558141 — Include — ABR test level 70 dB is the set stimulus level in preterm infants.
- 3558957 — Reference — Probes (1.0/4.0/8.0 kHz filtered clicks) pass the gate but cannot be recorded: validator cannot match "X.0 kHz" notation (see Validator-limited omissions). Quote kept as evidence; numeric cells empty.
- 3558968 — Reference — Observed acoustic properties of infants' own vocalizations (fricative components >=14 kHz; trill rate 16-180 Hz); no presented stimulus, so gate condition 3 fails.
- 3611513 — Include — Speech discrimination tested at three set intensity levels 50/60/70 dB SPL.
- 3624650 — Include — Pure tones at 500/1000/4000 Hz, each FDL measured at set sensation levels 40 and 80 dB SL.
- 3655123 — Include — Three set bandpass-noise conditions; the two bandpass bands (4-8, 8-12 kHz) recorded; low-pass condition noted in Stimulus_Type (see Omitted).
- 3771926 — Include — Response levels 20/40/60 dBnHL recorded; notch center frequencies omitted (validator limitation, see below).
- 3958315 — Include — Signal was a 4-kHz tone pip at 86 dB p.e.SPL, both set parameters (4000 Hz not in candidates_all but stated in the same sentence).
- 3973221 — Include (MIXED) — Standard F0 150 Hz recorded; F0 increments are frequency differences, omitted (see MIXED).
- 3989107 — Include — Harmonic complexes signaling pitch categories with fundamentals 160 and 200 Hz, set stimulus parameters.

### Batch 19
- 4029054 — Reference, stratum corrected A -> C — Sheep study (pregnant ewes, fetal lambs). 500-4000 Hz is the band over which measured attenuation of external sounds changed (observed property); Reference on stratum and gate grounds.
- 4044425 — Reference, stratum corrected A -> C — Bird middle-ear study. Recorded: stimulus levels 70-120 and 100 dB SPL; roll-off 6 and 16 dB/octave in Attenuation_dB_oct. Frequency values omitted (validator limitation / range endpoints, see below).
- 4078175 — Reference — Standard stimulus was a 1.0-kHz tone-burst train (gate-passing) but unrecordable due to validator limitation; measured DLs are outcomes and were not recorded per the MIXED rule (see Ambiguous judgments).
- 6401088 — Include (MIXED) — 500 Hz tone pip recorded; 4.0/10.0 kHz pips omitted (validator limitation); 40 Hz steady-state rate omitted as gate-failing (see MIXED / Validator-limited).
- 7096216 — Include — Filtered clicks 1/2/4/8 kHz at set intensities 30 and 50 dB HL (broadband click also 50 dB nHL).
- 7119278 — Reference — Mean f0 of infants' own vocalizations (415/445/450 Hz) are measured outcomes, no presented stimulus; gate condition 3 fails (cf. pilot PMID 42777332).

### Batch 20
- 670553 — Reference — F0 range 30-2500 Hz measured from infants'/children's own speech (observed outcome), no presented stimulus.
- 29502907 — Reference — Stratum B (children implanted at ~8.7 y). Recorded stimulus-train rates 250 Hz (click/pulse rate) and 1 Hz (train repetition). The 47.2 +/- 47.6 dB figure omitted (see Omitted).
- 20058986 — Reference — Stratum B (adult CI users). Electric stimulation rate 100 Hz recorded.

## Stratum corrections

- 4029054: A -> C. Abstract describes only pregnant ewes and fetal/neonatal lambs (animal study); no human subjects. First-pass A was a keyword artifact.
- 4044425: A -> C. Abstract describes only avian species (neonatal chick, parakeet, five bird species); no human subjects.

## MIXED rows (passing values recorded as Include; failing values listed here)

- MIXED 3198866 — Omitted Sound_Level values 10-15 dB and 15-30 dB: these are measured infant-minus-adult threshold differences (outcomes), not set stimulus levels. Gate condition 3 fails for them. Recorded: Frequency_Hz 250-8000 (Include).
- MIXED 3973221 — Omitted F0 increments 10, 20, 30 Hz (experiment 1) and 5, 10, 30 Hz (experiment 2): these are frequency *differences* relative to the standard, not stimulus tone frequencies; gate condition 2 fails for them. Recorded: the 150-Hz standard (Include).
- MIXED 6401088 — Omitted 40 Hz: the steady-state evoked-potential (response/modulation) rate on which 500 Hz thresholds were based, not a stimulus tone frequency; gate condition 2 fails. Recorded: Frequency_Hz 500 (Include). The 4.0 and 10.0 kHz pips also pass the gate but are listed under Validator-limited omissions.

## Validator-limited omissions (IMPORTANT — needs central fix + backfill)

The validator's number_in_quote() formats a converted value as an integer string
(e.g. 1000 Hz -> "1") and compares it against numeric tokens in the quote. When the
abstract writes the value as "1.0 kHz" / "4.0 kHz" / "8.0 kHz" / "10.0 kHz" / "3.0 kHz",
the quote token is "1.0"/"4.0"/... and can never match, so ANY cell value derived from
such a notation produces a false-positive ERROR (number_not_in_quote). Integer forms
("1 kHz", "4-8 kHz", "0.5 kHz") convert fine. I did not edit the validator. Affected
gate-passing stimulus values were therefore omitted from the cells and are listed here
with their evidence quotes so they can be backfilled once the matcher is fixed
(suggested fix: compare numerically, or also try the "X.0" token form):

- 3558957 — Frequency_Hz 1000, 4000, 8000. Evidence: "Probe stimuli were 1.0, 4.0, and 8.0-kHz third-octave-filtered clicks." Row currently Reference with empty numeric cells (values pass the gate; see Ambiguous judgments).
- 3771926 — Frequency_Hz 1000, 4000, 8000 (notch center frequencies). Evidence: "Notch center frequencies were set at 1.0, 4.0, and 8.0 kHz." Row is Include on the recorded levels (20/40/60 dBnHL).
- 6401088 — Frequency_Hz 4000, 10000. Evidence: "Auditory evoked-potential thresholds to 0.5, 4.0 and 10.0 kHz tone pips were measured..." Row is Include on the recorded 500 Hz.
- 4078175 — Frequency_Hz 1000 (the standard tone-burst train). Evidence: "...an ongoing train of 1.0-kHz tone bursts..." Row currently Reference with empty numeric cells (see Ambiguous judgments).
- 4044425 — Frequency_Hz range 200-10000 (measurement range; the 10000 endpoint is "10.0 kHz") and best-frequency range 1500-3000 (the 3000 endpoint is "3.0 kHz"). Evidence: "...for frequencies between 0.2 and 10.0 kHz with a capacitive probe. In both species this curve resembled a bandpass filter whose best frequency was in the range of 1.5-3.0 kHz." Partial endpoints (200, 1500) were NOT recorded alone, since as discrete cell values they would misrepresent ranges. Row is Reference (stratum C) regardless.

## Other omitted values

- 3558968 — Waveform sampling rates 20 and 40 kHz omitted: device/analysis parameters, explicitly outside gate condition 2; not acoustic stimulus or outcome values.
- 3655123 — The low-pass noise condition ("less than 4 kHz") is not written as a frequency band in the cell (its only number is the 4000 Hz cutoff, which is also the lower edge of the 4-8 kHz band); the condition is documented in Stimulus_Type. Recorded bands: 4000-8000, 8000-12000.
- 29502907 — 47.2 +/- 47.6 dB omitted: this is the mean +/- SD of the children's interaural hearing-level difference (a sample statistic), not a sound level; it also lies outside the quote span. Not recorded in Sound_Level_dB.
- 3198866 — The single frequency 8000 Hz (site of greatest threshold difference) is inside the recorded 250-8000 range; not listed separately.

## Ambiguous judgments

- 3558957 (Decision=Reference, empty numeric cells): all stimulus values pass the gate, but none can be recorded without a validator ERROR (see Validator-limited omissions). Reference was chosen over Include-with-empty-cells to flag the row for backfill; if the parent prefers, it should become Include once the values are backfilled.
- 4078175 (Decision=Reference, empty numeric cells): the only gate-passing value (1000 Hz standard) is validator-limited as above; the remaining candidates are measured difference limens (frequency DLs 11-29 and 3-5 Hz; intensity DLs 3-12 and 1-2 dB), which fail gate condition 3. Per the MIXED rule only passing values may be recorded, so no numeric values were recorded and the row is Reference pending backfill of the 1000 Hz standard.
- 29502907 / 20058986: the recorded Hz values are pulse-train *rates* (250 Hz click rate, 1 Hz train repetition; 100 Hz electric stimulation rate), i.e. temporal stimulus parameters, not carrier frequencies. Recorded in Frequency_Hz as Reference rows (stratum B), consistent with the pilot's treatment of rate-type values in Reference rows (PMID 37772774). They cannot enter design statistics.
- 4029054: 500-4000 Hz recorded as a range ("between 500 and 4000 Hz") although it is a measured attenuation-change band, not a stimulus band; Reference on stratum (C) grounds in any case.
- 3558141: the 70 dB figure is stated as the level of the ABR tests ("ABR tests at 70 dB"); judged to be the set stimulus level (the paper's thresholds are reported separately as age-dependent), hence Include.
- 3611513: abstract does not state infant ages numerically; Target_Age recorded as "infants (age not specified in abstract)".
