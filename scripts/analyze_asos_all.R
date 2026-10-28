#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(tidyverse)
  library(openxlsx)
  library(forcats)
})

# -------------------------
# Args
# -------------------------
# Usage:
#   Rscript analyze_asos_all.R <base_prefix> [out_csv] [out_png] [out_xlsx]
#
# base_prefix = path WITHOUT extension, e.g.:
#   /home/.../results/abcd1234
# which implies:
#   abcd1234.voice_quality.tsv
#   abcd1234.Spectrum
#   abcd1234.LPCSpectrum
#   abcd1234.PowerCepstrum

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("Missing <base_prefix>. E.g.: Rscript analyze_asos_all.R /path/results/abcd1234", call. = FALSE)
}

base_prefix <- args[1]
out_csv  <- if (length(args) >= 2 && nzchar(args[2])) args[2] else paste0(base_prefix, "_analysis.csv")
out_png  <- if (length(args) >= 3) args[3] else ""
out_xlsx <- if (length(args) >= 4) args[4] else ""

if (nzchar(out_xlsx)) {
  wb <- createWorkbook()
  addWorksheet(wb, "metrics")
  writeDataTable(wb, sheet = "metrics", x = df_out, withFilter = TRUE, tableStyle = "TableStyleMedium9")
  freezePane(wb, "metrics", firstRow = TRUE)
  setColWidths(wb, "metrics", cols = 1:ncol(df_out), widths = "auto")
  saveWorkbook(wb, out_xlsx, overwrite = TRUE)
}

f_vq  <- paste0(base_prefix, ".voice_quality.tsv")
f_fft <- paste0(base_prefix, ".Spectrum")
f_lpc <- paste0(base_prefix, ".LPCSpectrum")
f_cep <- paste0(base_prefix, ".PowerCepstrum")

if (!file.exists(f_vq))  stop("Does not exist: ", f_vq)
if (!file.exists(f_fft)) stop("Does not exist: ", f_fft)

# -------------------------
# Helpers: read Spectrum / PowerCepstrum (Praat text)
# -------------------------
read_praat_spectrum2 <- function(path) {
  x <- readLines(path, encoding = "UTF-8", warn = FALSE)

  nx <- as.integer(str_match(x[grepl("^nx\\s*=", x)][1], "nx\\s*=\\s*([0-9]+)")[,2])
  dx <- as.numeric(str_match(x[grepl("^dx\\s*=", x)][1], "dx\\s*=\\s*([0-9eE\\.-]+)")[,2])
  x1 <- as.numeric(str_match(x[grepl("^x1\\s*=", x)][1], "x1\\s*=\\s*([0-9eE\\.-]+)")[,2])

  re_lines <- x[grepl("^\\s*z \\[1\\] \\[[0-9]+\\] =", x)]
  im_lines <- x[grepl("^\\s*z \\[2\\] \\[[0-9]+\\] =", x)]

  re <- as.numeric(str_match(re_lines, "=\\s*([0-9eE\\.-]+)")[,2])
  im <- as.numeric(str_match(im_lines, "=\\s*([0-9eE\\.-]+)")[,2])

  re <- re[seq_len(nx)]
  im <- im[seq_len(nx)]

  mag <- sqrt(re^2 + im^2)
  amp_db <- 20 * log10(pmax(mag, .Machine$double.eps))
  freq <- x1 + (0:(nx-1)) * dx

  tibble(freq = freq, amp_db = amp_db)
}

read_praat_powercepstrum2 <- function(path) {
  x <- readLines(path, encoding = "UTF-8", warn = FALSE)

  nx <- as.integer(str_match(x[grepl("^nx\\s*=", x)][1], "nx\\s*=\\s*([0-9]+)")[,2])
  dx <- as.numeric(str_match(x[grepl("^dx\\s*=", x)][1], "dx\\s*=\\s*([0-9eE\\.-]+)")[,2])
  x1 <- as.numeric(str_match(x[grepl("^x1\\s*=", x)][1], "x1\\s*=\\s*([0-9eE\\.-]+)")[,2])

  z_lines <- x[grepl("^\\s*z \\[1\\] \\[[0-9]+\\] =", x)]
  z <- as.numeric(str_match(z_lines, "=\\s*([0-9eE\\.-]+)")[,2])
  z <- z[seq_len(nx)]

  quef <- x1 + (0:(nx-1)) * dx
  pow_db <- 10 * log10(pmax(z, .Machine$double.eps))

  tibble(quef_s = quef, pow_db = pow_db)
}

amp_at <- function(spec_df, f_hz) {
  if (!is.finite(f_hz) || f_hz <= 0 || nrow(spec_df) == 0) return(NA_real_)
  approx(spec_df$freq, spec_df$amp_db, xout = f_hz, rule = 2)$y
}

calc_cpp_simple <- function(cep_df, f0_hz, win = 0.001) {
  if (!is.finite(f0_hz) || f0_hz <= 0 || nrow(cep_df) < 50) return(NA_real_)
  q0 <- 1 / f0_hz

  peak_zone <- cep_df %>% filter(quef_s >= q0 - win, quef_s <= q0 + win)
  if (nrow(peak_zone) < 5) return(NA_real_)

  i_peak <- which.max(peak_zone$pow_db)
  q_peak <- peak_zone$quef_s[i_peak]
  peak_db <- peak_zone$pow_db[i_peak]

  base_df <- cep_df %>%
    filter(quef_s >= 0.001) %>%
    filter(!(quef_s >= q0 - win & quef_s <= q0 + win))
  if (nrow(base_df) < 30) return(NA_real_)

  fit <- lm(pow_db ~ quef_s, data = base_df)
  base_at_peak <- predict(fit, newdata = data.frame(quef_s = q_peak))

  as.numeric(peak_db - base_at_peak)
}

detect_zeroes <- function(spec_df, n = 3, fmin = 200, fmax = 5000, smooth_k = 9, bw_rise_db = 3) {
  if (nrow(spec_df) < 20) {
    return(tibble(rank = integer(), z_freq = double(), z_depth_db = double(), z_bw_hz = double()))
  }

  d <- spec_df %>%
    filter(freq >= fmin, freq <= fmax) %>%
    arrange(freq) %>%
    mutate(amp_s = as.numeric(stats::filter(amp_db, rep(1/smooth_k, smooth_k), sides = 2)))

  d$amp_s[is.na(d$amp_s)] <- d$amp_db[is.na(d$amp_s)]

  a <- d$amp_s
  is_min <- rep(FALSE, length(a))
  if (length(a) >= 3) {
    is_min[2:(length(a)-1)] <- a[2:(length(a)-1)] < a[1:(length(a)-2)] & a[2:(length(a)-1)] < a[3:length(a)]
  }

  mins <- d[is_min, ] %>% mutate(idx = row_number())
  if (nrow(mins) == 0) {
    return(tibble(rank = integer(), z_freq = double(), z_depth_db = double(), z_bw_hz = double()))
  }

  base_med <- median(d$amp_s, na.rm = TRUE)
  mins <- mins %>%
    mutate(depth_db = (base_med - amp_s)) %>%
    arrange(desc(depth_db)) %>%
    slice_head(n = n) %>%
    mutate(rank = row_number())

  out <- mins %>%
    rowwise() %>%
    mutate(
      z_freq = freq,
      z_depth_db = depth_db,
      z_bw_hz = {
        i0 <- which.min(abs(d$freq - freq))
        if (length(i0) == 0) NA_real_ else {
          thr <- d$amp_s[i0] + bw_rise_db
          iL <- i0; while (iL > 1 && d$amp_s[iL] < thr) iL <- iL - 1
          iR <- i0; while (iR < nrow(d) && d$amp_s[iR] < thr) iR <- iR + 1
          bw <- d$freq[iR] - d$freq[iL]
          if (!is.finite(bw) || bw < 0) NA_real_ else bw
        }
      }
    ) %>%
    ungroup() %>%
    select(rank, z_freq, z_depth_db, z_bw_hz)

  out
}

col_or_na <- function(df, nm) {
  if (nm %in% names(df)) as.numeric(df[[nm]][1]) else NA_real_
}

# -------------------------
# Read inputs
# -------------------------
df_raw <- {
  h <- read_tsv(f_vq, n_max = 0, show_col_types = FALSE, name_repair = "minimal", progress = FALSE)
  read_tsv(f_vq, col_select = which(!duplicated(names(h))), show_col_types = FALSE, name_repair = "minimal", progress = FALSE)
}

df <- df_raw %>% select(where(is.numeric))

spec_fft <- read_praat_spectrum2(f_fft)
spec_lpc <- if (file.exists(f_lpc)) read_praat_spectrum2(f_lpc) else tibble(freq = numeric(), amp_db = numeric())
cep      <- if (file.exists(f_cep)) read_praat_powercepstrum2(f_cep) else tibble(quef_s = numeric(), pow_db = numeric())

# Renames to follow the original script
df <- df %>%
  rename(
    h1_freq = h1_freq_hz_target,
    a1_freq = a1_freq_hz_target,
    a2_freq = a2_freq_hz_target,
    a3_freq = a3_freq_hz_target
  ) %>%
  mutate(f0_hz = f0_mid_hz)

# -------------------------
# Compute metrics
# -------------------------
df2 <- df %>%
  mutate(
    `H1-H2`       = h1_db - h2_db,
    `H2-H4`       = h2_db - h4_db,
    `H4-H2kHz`    = h4_db - a2k_db,
    `H2kHz-H5kHz` = a2k_db - a5k_db
  ) %>%
  rowwise() %>%
  mutate(
    # FFT
    H1_fft_db = amp_at(spec_fft, h1_freq),
    A1_fft_db = amp_at(spec_fft, a1_freq),
    A2_fft_db = amp_at(spec_fft, a2_freq),
    A3_fft_db = amp_at(spec_fft, a3_freq),

    # LPC envelope
    H1_lpc_db = amp_at(spec_lpc, h1_freq),
    A1_lpc_db = amp_at(spec_lpc, a1_freq),
    A2_lpc_db = amp_at(spec_lpc, a2_freq),
    A3_lpc_db = amp_at(spec_lpc, a3_freq),

    # diffs
    H1_A1_fft = H1_fft_db - A1_fft_db,
    H1_A2_fft = H1_fft_db - A2_fft_db,
    H1_A3_fft = H1_fft_db - A3_fft_db,

    H1_A1_lpc = H1_lpc_db - A1_lpc_db,
    H1_A2_lpc = H1_lpc_db - A2_lpc_db,
    H1_A3_lpc = H1_lpc_db - A3_lpc_db,

    # corrected (FFT - envelope)
    H1_corr_db = H1_fft_db - H1_lpc_db,
    A1_corr_db = A1_fft_db - A1_lpc_db,
    A2_corr_db = A2_fft_db - A2_lpc_db,
    A3_corr_db = A3_fft_db - A3_lpc_db,

    H1corr_A1corr = H1_corr_db - A1_corr_db,
    H1corr_A2corr = H1_corr_db - A2_corr_db,
    H1corr_A3corr = H1_corr_db - A3_corr_db,
  ) %>%
  ungroup()

# Spectral zeroes (if LPC is available)
z <- if (nrow(spec_lpc) > 0) detect_zeroes(spec_lpc, n = 3, fmin = 200, fmax = 5000) else tibble()
if (nrow(z) == 0) {
  z_wide <- tibble(
    z1_freq_hz = NA_real_, z1_depth_db = NA_real_, z1_bw_hz = NA_real_,
    z2_freq_hz = NA_real_, z2_depth_db = NA_real_, z2_bw_hz = NA_real_,
    z3_freq_hz = NA_real_, z3_depth_db = NA_real_, z3_bw_hz = NA_real_
  )
} else {
  z_wide <- z %>%
    distinct(rank, .keep_all = TRUE) %>%
    mutate(rank = as.character(rank)) %>%
    pivot_wider(
      names_from = rank,
      values_from = c(z_freq, z_depth_db, z_bw_hz),
      names_glue = "z{rank}_{.value}"
    )

  need <- c("z1_z_freq","z2_z_freq","z3_z_freq",
            "z1_z_depth_db","z2_z_depth_db","z3_z_depth_db",
            "z1_z_bw_hz","z2_z_bw_hz","z3_z_bw_hz")
  for (nm in need) if (!nm %in% names(z_wide)) z_wide[[nm]] <- NA_real_

  z_wide <- z_wide %>%
    rename(
      z1_freq_hz   = z1_z_freq,
      z2_freq_hz   = z2_z_freq,
      z3_freq_hz   = z3_z_freq,
      z1_depth_db  = z1_z_depth_db,
      z2_depth_db  = z2_z_depth_db,
      z3_depth_db  = z3_z_depth_db,
      z1_bw_hz     = z1_z_bw_hz,
      z2_bw_hz     = z2_z_bw_hz,
      z3_bw_hz     = z3_z_bw_hz
    )
}

df_out <- bind_cols(df2, z_wide)

# -------------------------
# Save Excel (everything)
# -------------------------
wb <- createWorkbook()
addWorksheet(wb, "metrics")
writeDataTable(wb, sheet = "metrics", x = df_out, withFilter = TRUE, tableStyle = "TableStyleMedium9")
freezePane(wb, "metrics", firstRow = TRUE)
setColWidths(wb, "metrics", cols = 1:ncol(df_out), widths = "auto")
if (nzchar(out_xlsx)) {
  saveWorkbook(wb, out_xlsx, overwrite = TRUE)
}

# -------------------------
# Summary for the web + long summary for the plot
# -------------------------
# Notes:
# - jitter/shimmer are converted to percentages to match the clinical thresholds.
# - H1-A1 is reported with the corrected version (H1corr_A1corr), more acoustically stable.
web_row <- tibble(
  mpt                       = col_or_na(df_out, "dur_local"),
  f0_mean_hz                = col_or_na(df_out, "f0_mean_hz"),
  jitter_pct                = 100 * col_or_na(df_out, "jitter_ppq5"),
  shimmer_pct               = 100 * col_or_na(df_out, "shimmer_apq11"),
  hnr_db                    = col_or_na(df_out, "hnr_mean_db"),
  voice_breaks_percent      = col_or_na(df_out, "voice_breaks_percent"),
  locally_unvoiced_percent  = col_or_na(df_out, "locally_unvoiced_percent"),
  h1_h2                     = col_or_na(df_out, "H1-H2"),
  h1_a1                     = col_or_na(df_out, "H1corr_A1corr"),
  # f0_max_hz: freqüència fonamental màxima; s'utilitza com a F0_high al DSI.
  f0_max_hz                 = col_or_na(df_out, "f0_max_hz"),
  # i_low_db: intensitat mínima APROXIMADA (opció A) = mínim del contorn d'intensitat de la
  # vocal sostinguda. S'utilitza com a I_low al DSI; és una aproximació i no coincideix
  # exactament amb la I_low clínica (fonació suau dedicada).
  i_low_db                  = col_or_na(df_out, "int_min_db_praatstyle")
)

# Robust norms placeholder (same as the original script)
plot_norms <- tribble(
  ~variable,                  ~center_robust, ~sd_robust, ~variable_label,
  "mpt",                               18,         4,  "Duration (MPT, s)",
  "f0_mean_hz",                       120,        25,  "Mean F0 (Hz)",
  "jitter_pct",                      0.15,      0.10,  "Jitter (%)",
  "shimmer_pct",                     4.00,      2.00,  "Shimmer (%)",
  "hnr_db",                            25,         5,  "HNR (dB)",
  "voice_breaks_percent",            0.00,      1.00,  "Voice breaks (%)",
  "locally_unvoiced_percent",        0.00,      5.00,  "Locally unvoiced (%)",
  "h1_h2",                            2.0,       4.0,  "H1–H2 (dB)",
  "h1_a1",                            0.0,       3.0,  "H1–A1 (dB)"
)

df_summary <- plot_norms %>%
  mutate(
    value = map_dbl(variable, ~ web_row[[.x]][1]),
    z     = (value - center_robust) / sd_robust
  )

extra_summary <- tribble(
  ~variable,                    ~variable_label,              ~value,                                      ~center_robust, ~sd_robust,
  "mpt",                        "MPT (s)",                    col_or_na(df_out, "dur_local"),              NA_real_,      NA_real_,
  "voice_breaks_percent",       "Voice breaks (%)",           col_or_na(df_out, "voice_breaks_percent"),   NA_real_,      NA_real_,
  "locally_unvoiced_percent",   "Locally unvoiced (%)",       col_or_na(df_out, "locally_unvoiced_percent"), NA_real_,    NA_real_,
  "h1_a1",                      "H1–A1 (dB)",                 col_or_na(df_out, "H1corr_A1corr"),          0,             3
)

df_summary <- bind_rows(df_summary, extra_summary) %>%
  mutate(
    z = ifelse(
      is.na(center_robust) | is.na(sd_robust) | sd_robust == 0,
      z,
      ifelse(is.na(z), (value - center_robust) / sd_robust, z)
    )
  )

k <- sum(!is.na(df_summary$z))
mahal2 <- sum(df_summary$z^2, na.rm = TRUE)
global_percentile <- pchisq(mahal2, df = k) * 100
mean_abs_z <- mean(abs(df_summary$z), na.rm = TRUE)

caption_text <- sprintf("• Multivariate percentile (χ²): %.1f%% • Mean |z|: %.2f",
                        global_percentile, mean_abs_z)

order_vars <- plot_norms$variable_label


df_plot <- df_summary %>%
  mutate(
    variable_label = factor(variable_label, levels = order_vars),
    variable_f = fct_rev(variable_label),
    y = as.numeric(variable_f)
  )

z_max <- suppressWarnings(max(abs(df_plot$z), na.rm = TRUE))
if (!is.finite(z_max)) z_max <- 3

lim <- max(3, z_max * 1.1)

p <- ggplot(df_plot, aes(x = z, y = y)) +
  geom_rect(aes(xmin = -2, xmax = 2, ymin = y - 0.4, ymax = y + 0.4),
            fill = "lightblue", alpha = 0.4, inherit.aes = FALSE) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  geom_point(color = "red", size = 3) +
  scale_x_continuous(limits = c(-lim, lim), name = NULL) +
  scale_y_continuous(breaks = df_plot$y, labels = df_plot$variable_label, name = NULL) +
  labs(
    title = "Clinical quality profile – sustained /a/",
    subtitle = "Key variables for GRBAS (standardized values)",
    caption = caption_text
  ) +
  theme_minimal(base_size = 13) +
  theme(plot.caption = element_text(size = 10, hjust = 0))

if (nzchar(out_png)) {
  ggsave(out_png, plot = p, width = 10, height = 6, dpi = 150)
}

# Single-row wide CSV: this is what the web can read directly.
write_csv(web_row, out_csv)

# Auxiliary long CSV: useful if you later want a richer table or for debugging.
out_long_csv <- paste0(base_prefix, "_summary_long.csv")

write_csv(
  df_summary %>% select(variable, variable_label, value, center_robust, sd_robust, z),
  out_long_csv
)

message("OK")
message("  CSV:  ", out_csv)
if (nzchar(out_png))  message("  PNG:  ", out_png)
if (nzchar(out_xlsx)) message("  XLSX: ", out_xlsx)
