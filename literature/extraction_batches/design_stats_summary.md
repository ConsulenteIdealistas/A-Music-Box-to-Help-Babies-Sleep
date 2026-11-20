# Design-statistics summary — first computation, 2026-11-15

> Addendum (2026-11-17): Qn's finite-sample correction factors in
> analysis/stats.py were switched from the Croux & Rousseeuw (1992)
> approximations to robustbase's simulation-based factors (see stats.py
> header). Recomputation on the identical population below gives:
> Frequency_Hz Qn 1802 → 1803.5; Sound_Level_dB Qn unchanged at the
> displayed precision (20.95 → 20.98, shown as 21.0). All other figures
> were reproduced exactly and are unchanged.

Population: extraction rows with Stratum = A and Decision = Include
(the §3 gate), numeric cells expanded (ranges contribute both endpoints,
discrete sets contribute every value). Computed with analysis/stats.py
(summarize). Design values are the robust statistics; parametric figures
are supplements only, per METHODOLOGY §4.

## Frequency_Hz — 51 papers, 110 values (60–16000 Hz)
- Median **1500 Hz**, Q1 500, Q3 5625
- Robust SD (normalized MAD) 1987; Sn 1598; Qn 1802; IQR-based SD 3799
- Supplements: mean 3123, SD 3195, geometric mean 1531, Bowley skewness +0.61
- Modal value 1000 Hz (15% of values) — no tie collapse; MAD/Sn/Qn agree
  in order of magnitude, so the primary estimator stays normalized MAD.

## Sound_Level_dB — 30 papers, 64 values (−8 to 110 dB)
- Median **60 dB**, Q1 50, Q3 71.25
- Robust SD 14.8; Sn 23.9; Qn 21.0; IQR-based SD 15.8
- Supplements: mean 58.1, SD 26.1, Bowley +0.06
- Note: the −8 value is a signal-to-noise ratio condition (PMID 2299044),
  recorded as a set level condition; the bulk of the population is
  absolute presentation levels.

## Attenuation_dB_oct — 5 papers, 5 values (6, 6, 12, 12, 96)
- Median 12 dB/oct, Q1 6, Q3 12, robust SD 8.9
- n is far too small to fix a design value; the 96 dB/oct is a high-pass
  masking-noise slope (PMID 1880297), the rest are stimulus/filter slopes
  of 6–12 dB/oct. Reported for the record only.

## Tempo_BPM — 1 paper, 1 value (70)
- No population exists at abstract level: the only other tempo candidate
  (30 BPM, PMID 42777332) is a Reference value under the gate.
- Consequence: the working heartbeat/music tempo of 70 BPM remains a
  physiological assumption (resting maternal heart rate), NOT a
  literature statistic. Any future tempo parameter must be justified
  on other grounds and labelled as such.
- User decision (2026-11-15): BPM is NOT fixed from literature. It is
  a variable parameter — default 70 (midpoint of the resting maternal
  heart-rate range 60–80), adjustable range anchored to that same
  physiological range. The heartbeat layer already implements this
  (slider 60–90, default 70); the music-box layer's tempo stays an
  arrangement choice baked into the recordings.

## Extraction totals (498 papers)
- Decision: Include 69 / Reference 97 / Count_only 332
- Stratum (extraction sheets, after extraction-stage corrections):
  A 376 / B 32 / C 79 / UNDETERMINED 11
- Validation: 0 errors across all 498 rows. Triple-check: 166 targets
  blind-re-read, 53 field discrepancies, 14 changes applied after
  adjudication against the abstracts (see recrosscheck/adjudication.md).
