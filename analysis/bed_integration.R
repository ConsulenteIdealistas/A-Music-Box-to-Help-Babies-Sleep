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
