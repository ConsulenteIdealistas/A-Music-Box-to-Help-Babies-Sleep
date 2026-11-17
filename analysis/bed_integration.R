# Bed evidence integration — R replication of the group statistics
# (2026-11-17). Reads the SAME integrated dataset as
# analysis/bed_integration.py (literature/bed_transfer_evidence.csv)
# and computes the same statistics with robustbase, so the two
# implementations cross-check each other on identical input.
#
# Definitions matched to analysis/stats.py:
#   quartiles  : quantile(type = 7) — linear interpolation on (n-1)p,
#                identical to stats.py percentile().
#   robust_sd  : mad(constant = 1.4826) — stats.py MAD_TO_SD * MAD.
#   Sn / Qn    : robustbase (stats.py adopted robustbase's Qn
#                finite-sample factors on 2026-11-17).
#
# Usage: Rscript analysis/bed_integration.R
# Output: analysis/bed_integration_stats_r.csv

suppressMessages(library(robustbase))

root <- file.path(dirname(dirname(normalizePath(
  sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1])))))
ev <- read.csv(file.path(root, "literature", "bed_transfer_evidence.csv"),
               stringsAsFactors = FALSE)

fmt <- function(x) ifelse(is.na(x), NA, round(x, 4))

rows <- list()
for (g in unique(ev$group)) {
  v <- ev$value[ev$group == g]
  s <- sd(v)
  rows[[g]] <- data.frame(
    group = g, n = length(v),
    median = fmt(median(v)),
    q1 = fmt(unname(quantile(v, 0.25, type = 7))),
    q3 = fmt(unname(quantile(v, 0.75, type = 7))),
    robust_sd = fmt(mad(v, constant = 1.4826)),
    sn = fmt(Sn(v)),
    qn = fmt(Qn(v)),
    mean = fmt(mean(v)),
    sd = fmt(ifelse(length(v) > 1, s, NA)),
    min = min(v), max = max(v)
  )
}
out <- do.call(rbind, rows)
write.csv(out, file.path(root, "analysis", "bed_integration_stats_r.csv"),
          row.names = FALSE)
print(out)

# --- Round 3: curve comparison from point data ---------------------
# Same computation as curve_rows() in analysis/bed_integration.py:
# segment slopes (dB/oct) and log-linear interpolated levels at
# standard frequencies, within each source's stated range only.
cv <- read.csv(file.path(root, "literature", "bed_transfer_curves.csv"),
               stringsAsFactors = FALSE)
std_freqs <- c(125, 250, 500, 1000, 2000, 4000)
anchor_db <- function(f) ifelse(f <= 250, 3.5, 3.5 - 6 * log2(f / 250))
richards_db <- function(f) 3.7 - 2.74 * log2(f / 125)

crows <- list()
for (s in unique(cv$source)) {
  d <- cv[cv$source == s, ]
  d <- d[order(d$freq_hz), ]
  segs <- diff(d$level_db) / diff(log2(d$freq_hz))
  row <- data.frame(source = s,
                    segment_slopes = paste(sprintf("%.2f", segs),
                                           collapse = ";"),
                    overall_slope = if (nrow(d) > 1)
                      round((d$level_db[nrow(d)] - d$level_db[1]) /
                            log2(d$freq_hz[nrow(d)] / d$freq_hz[1]), 2)
                      else NA,
                    stringsAsFactors = FALSE)
  for (f in std_freqs) {
    val <- NA
    hit <- d$level_db[d$freq_hz == f]
    if (length(hit) > 0) {
      val <- hit[1]
    } else if (f > min(d$freq_hz) && f < max(d$freq_hz)) {
      i <- findInterval(f, d$freq_hz)
      t <- log2(f / d$freq_hz[i]) / log2(d$freq_hz[i + 1] / d$freq_hz[i])
      val <- round(d$level_db[i] + t * (d$level_db[i + 1] - d$level_db[i]), 2)
    }
    row[[paste0("level_", f)]] <- val
  }
  crows[[s]] <- row
}
for (lbl in c("anchor (Gerhardt, analytic)", "richards line (analytic)")) {
  fn <- if (grepl("anchor", lbl)) anchor_db else richards_db
  row <- data.frame(source = lbl, segment_slopes = "",
                    overall_slope = NA, stringsAsFactors = FALSE)
  for (f in std_freqs) row[[paste0("level_", f)]] <- round(fn(f), 2)
  crows[[lbl]] <- row
}
cout <- do.call(rbind, crows)
write.csv(cout, file.path(root, "analysis", "bed_curve_comparison_r.csv"),
          row.names = FALSE)
print(cout)
