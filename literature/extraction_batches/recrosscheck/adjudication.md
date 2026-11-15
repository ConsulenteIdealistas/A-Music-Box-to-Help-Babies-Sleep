# Triple-check adjudication — 2026-11-15

Blind re-read of 166 triple-check targets vs the first extraction:
53 field-level discrepancies. Each was adjudicated against the abstract.
14 changes were applied to the first extraction; the rest stand as extracted.
Full compare output: `triple_check compare` on first_targets.csv / reread_all.csv.

## Applied changes
- 25618103 (Include): Sound_Level_dB "15, 25, 40" → "15". The 25/40 are
  linear-growth bounds ("<25 / <40 dB SPL"), not set levels.
- 2808150 (Reference, C): "120, 60" → "120". 60 dB is a measured threshold
  shift (a difference), not a presented level.
- 31255105 (Include): "4, 10" → "4". 10 dB is the infant–adult MDT
  difference (outcome); 4 dB is the set modulation-depth offset.
- 4066520 (Reference, C): Frequency_Hz "1500, 4000" → "1500". 4 kHz is the
  locus of maximum threshold elevation (outcome), not a stimulus.
- 8113139 / 8226347 (Reference, C): Sound_Level_dB "120, 57" → "120"
  (57 dB threshold shift removed; same rule as 2808150).
- 8880180 (Include): Sound_Level_dB "50" → "65, 50" (L1 was in the quote
  all along; the re-read caught it).
- 4031254 (Include): Sound_Level_dB "" → "60, 40" (masker intensities in
  the existing quote; the re-read caught them).
- 8376214 (Reference): Frequency_Hz "10-80" → "10-80, 20-80, 500, 2000"
  with the re-read's single-sentence quote (AM rates + carriers together).
- 8600128 (Reference): Frequency_Hz "40, 80" → "40, 80, 500, 1000, 2000"
  with the re-read's quote.
- Strata (no subjects in the study itself → UNDETERMINED, precedent
  15807032): 17348521 (modeling), 17550168 (NICU sound surveys),
  9104019 (theory) — all A → UNDETERMINED, Decision unchanged (Reference).
- 8354755: Stratum A → B (subjects are nine pregnant women; the fetus is
  not a measured subject). Decision unchanged (Reference).

## Kept as first extracted (recurring rules)
- MIXED rule: failing values are omitted, not recorded, so the row stays
  Include — 6401088 (40 Hz response rate), 7593925 (filter cutoffs).
- Differences are not levels: 6747104 stays Reference (2/4/6 dB intensity
  increments; the re-read's Include rejected).
- Result-framed or result-selected values stay Reference: 9479751 (f2
  ranges named only in result statements), 21476616 (6 kHz singled out by
  the result), 17225410 (model fitted to prior data, no stimuli set).
- Values from the adult arm of a mixed-age paper do not enter the infant
  design population: 10867273 stays Reference (no diff surfaced; noted
  because the re-read independently chose Include in its group summary).
- Supersets verified against a single verbatim quote stand: 21974484,
  3655123 (bands as ranges, as stated), 4044425, 7928706, 8226347 (Hz),
  8789820, 9925011, 8844183 (50/70 dB SPL stimulus intensities are stated
  in the abstract's final sentences), 4086386 (50 dB IID kept as Reference).
- 3558968: first set (observed vocalization acoustics) stands; the re-read
  recorded spectrogram/sampling frequencies (16/20/40 kHz), which are
  analysis parameters.
- 2299044: infant S/N set only (−8, 0, 8, 16); the re-read's extra values
  are the adult comparison set.
- 26428839: attenuation recorded as magnitude (6) with the ± conditions
  spelled out in Stimulus_Type — the convention adopted in group 1.
- 690336: Stratum stays B (adult human skull specimens; the age class is
  determinable — distinct from no-subject papers).
- 8226331: the ">2 kHz" emission bound is a distributional bound, not a
  value; not recorded.
