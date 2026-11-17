# Four songs — R cross-check and across-song robust summary.
# Reads analysis/four_songs_measurements.csv (Python spectra +
# SoX statistics, one row per song) and:
#   1. verifies Python vs SoX RMS agreement on identical files;
#   2. summarises the per-song outcomes across the four songs with
#      the project's usual robust statistics (median, type-7
#      quartiles, MAD-based robust SD, Sn, Qn via robustbase).
# The four songs went through the identical pipeline, so each
# column below is one quantity measured four times — the setting
# Sn/Qn are for.
#
# Usage: Rscript analysis/four_songs_stats.R
# Output: analysis/four_songs_stats_r.csv

suppressMessages(library(robustbase))

root <- file.path(dirname(dirname(normalizePath(
  sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1])))))
m <- read.csv(file.path(root, "analysis", "four_songs_measurements.csv"),
              stringsAsFactors = FALSE)

# 1. Python vs SoX RMS agreement (same files, two implementations)
for (t in c("raw", "mix")) {
  d <- abs(m[[paste0("rms_", t, "_py")]] - m[[paste0("rms_", t, "_sox")]])
  cat(sprintf("RMS py-vs-sox (%s): max abs diff = %.6f\n", t, max(d)))
}

# 2. Across-song summaries
m$centroid_shift <- m$centroid_mix - m$centroid_raw
for (b in c(1000, 2000, 4000)) {
  m[[paste0("banddiff_", b)]] <- m[[paste0("band_", b, "_mix")]] -
    m[[paste0("band_", b, "_raw")]]
}
fmt <- function(x) ifelse(is.na(x), NA, round(x, 4))
cols <- c("centroid_raw", "centroid_mix", "centroid_shift",
          "share1500_raw", "share1500_mix",
          "banddiff_1000", "banddiff_2000", "banddiff_4000",
          "balance_bed_music_db", "balance_active_db")
rows <- list()
for (cl in cols) {
  v <- m[[cl]]
  rows[[cl]] <- data.frame(
    quantity = cl, n = length(v),
    median = fmt(median(v)),
    q1 = fmt(unname(quantile(v, 0.25, type = 7))),
    q3 = fmt(unname(quantile(v, 0.75, type = 7))),
    robust_sd = fmt(mad(v, constant = 1.4826)),
    sn = fmt(Sn(v)), qn = fmt(Qn(v)),
    min = min(v), max = max(v))
}
out <- do.call(rbind, rows)
write.csv(out, file.path(root, "analysis", "four_songs_stats_r.csv"),
          row.names = FALSE)
print(out)
