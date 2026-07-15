library(readtextgrid)
library(janitor)
library(openxlsx)
library(tidyverse)

TARGET_VARS <- c(
  "delta_c",
  "delta_v",
  "npvi_c",
  "npvi_v",
  "percentage_v",
  "rpvi_c",
  "rpvi_v",
  "speech_rate",
  "varco_c",
  "varco_v",
  "vdist_cent_mean",
  "vdist_cent_sd"
)

read_textgrid_file <- function(textgrid_file) {
  encoding <- guess_encoding(textgrid_file) %>%
    dplyr::filter(confidence == 1) %>%
    pluck("encoding")

  df <- textgrid_file %>%
    read_lines(locale = locale(encoding = encoding)) %>%
    read_textgrid_lines(file = textgrid_file) %>%
    remove_constant(na.rm = FALSE) %>%
    rename(num = annotation_num)

  df %>%
    dplyr::filter(xmin != min(xmin) & xmax != max(xmax)) %>%
    mutate(text = text %>% str_squish() %>% str_to_lower()) %>%
    dplyr::filter(text != "") %>%
    # Excluye las pausas largas (>300 ms) marcadas como "<p>" en el TextGrid de pataka.
    # Estos intervalos se anotan pero no deben entrar en los cálculos V/C.
    dplyr::filter(text != "<p>") %>%
    remove_constant(na.rm = FALSE) %>%
    mutate(num = dplyr::row_number()) %>%
    mutate(dur = xmax - xmin, .after = xmax) %>%
    mutate(midpoint = (xmax + xmin) / 2, .after = xmax) %>%
    rename(type = text) %>%
    dplyr::select(
      type,
      dplyr::contains("num"),
      dplyr::contains("xmin"),
      dplyr::contains("xmax"),
      dplyr::contains("midpoint"),
      dplyr::contains("dur")
    )
}

add_rhythm_metrics <- function(df) {
  rpvi_diffs <- function(x) { abs(x - dplyr::lead(x)) }
  npvi_diffs <- function(x) { abs((x - dplyr::lead(x)) / ((x + dplyr::lead(x)) / 2)) }

  df %>%
    mutate(n = length(dur)) %>%
    mutate(speech_dur = sum(dur, na.rm = TRUE)) %>%
    group_by(type) %>%
    nest() %>%
    mutate(sum = map_dbl(data, ~ sum(.x$dur, na.rm = TRUE))) %>%
    mutate(delta = map_dbl(data, ~ sd(.x$dur, na.rm = TRUE))) %>%
    mutate(mean = map_dbl(data, ~ mean(.x$dur, na.rm = TRUE))) %>%
    mutate(data = map(data, ~ .x %>% mutate(rpvi_diff = rpvi_diffs(dur)))) %>%
    mutate(data = map(data, ~ .x %>% mutate(npvi_diff = npvi_diffs(dur)))) %>%
    mutate(rpvi = map_dbl(data, ~ mean(.x$rpvi_diff, na.rm = TRUE))) %>%
    mutate(npvi = map_dbl(data, ~ mean(.x$npvi_diff, na.rm = TRUE) * 100)) %>%
    unnest(data) %>%
    ungroup() %>%
    mutate(speech_rate = n / speech_dur) %>%
    mutate(percentage = sum / speech_dur) %>%
    mutate(varco = (delta * 100) / mean) %>%
    arrange(num) %>%
    select(num, xmin, xmax, midpoint, dur, n, speech_dur, speech_rate, type, everything())
}

add_distance_metrics <- function(df) {
  dist_cent <- function(x) { abs(x - dplyr::lead(x)) }
  dist_lims <- function(x, y) { abs(x - dplyr::lead(y)) }

  sdist_cent <- df %>%
    select(num, midpoint) %>%
    distinct() %>%
    mutate(sdist = dist_cent(midpoint)) %>%
    mutate(
      sdist_cent_mean = mean(sdist, na.rm = TRUE),
      sdist_cent_sd = sd(sdist, na.rm = TRUE)
    )

  vdist_cent <- df %>%
    select(num, type, midpoint) %>%
    filter(type == "v") %>%
    select(-type) %>%
    distinct() %>%
    mutate(vdist = dist_cent(midpoint)) %>%
    mutate(
      vdist_cent_mean = mean(vdist, na.rm = TRUE),
      vdist_cent_sd = sd(vdist, na.rm = TRUE)
    )

  vdist_lims <- df %>%
    select(num, type, xmin, xmax) %>%
    filter(type == "v") %>%
    select(-type) %>%
    distinct() %>%
    mutate(vlims = dist_lims(xmax, xmin)) %>%
    mutate(
      vdist_lims_mean = mean(vlims, na.rm = TRUE),
      vdist_lims_sd = sd(vlims, na.rm = TRUE)
    )

  df %>%
    left_join(sdist_cent, by = "num") %>%
    left_join(vdist_cent, by = "num") %>%
    left_join(vdist_lims, by = "num")
}

summarise_by_type_wide <- function(df) {
  vars_to_mean <- df %>%
    select(contains("_dur"), contains("spvi"), contains("vpvi"), contains("dist")) %>%
    colnames()

  df_summ <- df %>%
    group_by(num) %>%
    mutate(across(all_of(vars_to_mean), ~ mean(., na.rm = TRUE), .names = "{.col}")) %>%
    ungroup() %>%
    mutate(across(all_of(vars_to_mean), ~ mean(., na.rm = TRUE), .names = "{.col}")) %>%
    select(
      type, n, speech_dur, dur, sum, delta, mean, speech_rate,
      percentage, varco, rpvi, npvi, contains("vpvi"), contains("spvi"), contains("dist")
    ) %>%
    distinct() %>%
    select(-dur) %>%
    distinct()

  df_summ %>%
    pivot_wider(
      names_from = type,
      values_from = c(sum, delta, mean, percentage, varco, rpvi, npvi)
    )
}

analyze_pataka <- function(textgrid_file) {
  df <- read_textgrid_file(textgrid_file) %>%
    add_rhythm_metrics() %>%
    add_distance_metrics() %>%
    summarise_by_type_wide()

  keep <- intersect(TARGET_VARS, names(df))
  df %>% select(all_of(keep))
}

analyze_asos <- function(textgrid_file) {
  read_textgrid_file(textgrid_file) %>%
    add_rhythm_metrics() %>%
    summarise_by_type_wide()
}

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("Cal passar (1) la ruta al fitxer .TextGrid i (2) la ruta del .csv de sortida.")
}

textgrid_file <- args[1]
csv_out <- args[2]
task <- if (length(args) >= 3) args[3] else "pataka"

if (task == "pataka") {
  df_textgrid <- analyze_pataka(textgrid_file)
} else if (task == "asos") {
  df_textgrid <- analyze_asos(textgrid_file)
} else {
  stop(paste("Tasca desconeguda:", task))
}

write.csv(df_textgrid, file = csv_out, row.names = FALSE)