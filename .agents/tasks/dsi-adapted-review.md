# Adapted DSI replaces the ASOS DSI with a control-referenced provisional index

Replaces the ASOS DSI with `0.13*MPT + 0.0053*F0_alta - 1.18*Jitter - 2.16` (I-low fixed at 56 dB, F0_alta = mean F0 + 6 st), compared against mean ± 2*SD (ddof=1) of 8 control recordings. The chart row is `dsi_adapted` and payloads carry `dsi_method: "adapted_v1"`. Saved results from the two earlier generations keep their original wording through preserved `_v2` and `_f0max` text keys. Watch for: the reference rests on 8 recordings of one age and unknown sex (documented as provisional in app and paper; possible, non-blocking); the 56 dB constant is cited to Hakkesteegt Table 2, which I did not re-check against the source (possible).

**Verdict**: APPROVED

## High-level view

The formula, coefficients, fixed I-low and reference constants live only in `core/dsi_adapted.py`. `routers/clinica.py` imports them, and `scripts/compute_dsi_adapted_reference.py` plus a unit test recompute the constants from the controls CSV, so drift fails a test.

Payload localization branches on generation. Gen3 (`dsi_method == adapted_v1`) uses the new texts. Gen2 (`mean_plus_6st`, no `dsi_method`) and gen1 (no `f0_high_method`) use legacy keys and a legacy ±5 label function, so their wording stays as shown at the time. Old chart rows with variable `dsi` keep their 'DSI' label; the new row is `dsi_adapted`.

The texts consistently say the index is adapted, provisional and not the validated DSI. They state that the ±5 scale does not apply and that the result is not a diagnosis. They give no speaker count. The template shows the method in a collapsible `<details>` and keeps legacy rendering for older payloads.

## Issues (non-blocking)

1. **Reference size** (possible) — 8 recordings, one age, unknown sex. Documented in app and paper; update when more controls exist.
2. **56 dB source** (possible) — the constant is attributed to Hakkesteegt 2006 Table 2 total. Confirm against the paper before submission (already listed under paper "items to confirm").
3. **Untracked `tests/__pycache__`** (confirmed, cosmetic) — do not commit it.

<details><summary>Details</summary>

### Single source of truth
`core/dsi_adapted.py` defines coefficients, `DSI_ADAPTED_I_LOW_FIXED_DB = 56`, the reference dict and `compute_dsi_adapted` (returns None on missing or non-finite input). The coefficients give 12.4 - 0.26*56 = -2.16, matching the displayed formula. The clinica router wraps it in `_compute_dsi_adapted` and rounds to 2 decimals. The script reads `mpt_s`, `f0_high_6st_hz` and `jitter_pct` from the controls CSV and uses `statistics.stdev` (ddof=1). The test asserts n and the four constants to 4 decimals, and skips if the git-ignored `ASOS/` is absent. The evidence file shows mean 1.0250, SD 0.7202, min -0.4155 and max 2.4654.

### Three payload generations
`_localize_dsi_payload` dispatches on `dsi_method`. The legacy path uses `_dsi_label_legacy` (±5), `*_v2` keys for gen2 and `*_f0max` keys for gen1, and `_dsi_norm_texts` for the Hakkesteegt prediction. It blanks the new fields (`subtitle`, `method`, `method_title`, `reference`), so the template does not crash on old metas. The evidence shows gen2 texts identical to the previous release, gen1 and gen2 row labels still 'DSI', and HTTP 200 for gen3 and gen2 in ca/es/en. Rows hidden by `_ASOS_HIDDEN_ROWS` are untouched, and the `dsi` row from old metas is kept.

### Alteration comments and helper safety
`_clinical_hover` returns "" for both `dsi` and `dsi_adapted`, so the new row adds nothing to `alteration_comments`. The evidence confirms `_clinical_hover`, `_infer_unit` and `_clean_label` handle the key and give 'Dsi adapted' as the fallback label. The row z is `(value - mean)/SD`, consistent with the ±2 SD band and `_severity_from_z`. The evidence records z 0.5 → normal, -2.5 → mild and ±3.5/-4 → marked.

### Texts and template
`texts.py` removed lines are only the `asos_dsi_*` keys, which were renamed to `_v2` with identical content. No unrelated keys changed. New keys exist in ca, es and en, with a language-specific decimal separator. Wording is orientative and non-diagnostic. The method is explained in a collapsible list. The reference sentence gives n, age, mean, SD and band, with no speaker count. `results.html` keeps CRLF (checked with `file` on both HEAD and working tree). The diff is about 23 lines, with the title subtitle, the reference paragraph, the `<details>` block and `not dsi.method` guards for legacy rendering.

### Scope
`git status` shows no change to `scripts/asos_pipeline.py` or `scripts/analyze_asos_all.R`. `ASOS/` is git-ignored, and the controls files have mtimes from before this work. No commit was made (HEAD unchanged). New comments and docstrings are in Catalan. The `clinica.py` line-count stat is inflated by the removed normative block and the legacy dispatcher, but the content is within scope (the `_dsi_normative` constants are removed because gen3 does not use age or sex; legacy rendering uses stored `norm_*` fields).

### Paper paragraph
`ASOS/DSI_adapted_methods_paragraph.md` quotes mean 1.02/1.0250, SD 0.72/0.7202 and band -0.42 to 2.47 (-0.4155 to 2.4654), all matching the constants (evidence item 7). The tone is honest: not validated, not comparable to Wuyts/Hakkesteegt, no diagnosis. It includes a Limitations section and an Items to confirm list (speaker count, jitter definition, software citations, references), and it makes no speaker count claim.

### Evidence completeness
`dsi-adapted-verification.md` contains all 7 items (syntax/imports, numbers, e2e, language switch, backward compat, TestClient, paper numbers). I did not re-run it.

</details>

<details><summary>File map</summary>

- core/dsi_adapted.py (new): formula and reference constants
- scripts/compute_dsi_adapted_reference.py (new): recomputes reference from controls CSV
- tests/test_dsi_adapted_reference.py (new): constants vs CSV
- routers/clinica.py: adapted DSI compute, label, payload, row, three-generation localization
- core/texts.py: new ca/es/en strings, legacy `_v2` keys
- templates/results.html: subtitle, reference, method details block
- ASOS/DSI_adapted_methods_paragraph.md (git-ignored): paper draft

</details>
