# Dysphonia Severity Index (DSI) summary for ASOS results

Adds a global DSI indicator to the ASOS voice-quality results, computed from measures the pipeline already produces plus one newly-emitted value (minimum intensity), and renders it in a highlighted box directly above the "Els teus resultats" results-profile. The DSI value and its Catalan/es/en texts are threaded through analyze → saved meta → re-render, so the box survives language switches and shared links. Participant age is persisted for future age-adjusted norms (not computed). The formula matches the spec exactly and the recorded math check (mpt=20, f0=400, i_low=50, jitter=0.5 → 3.53) is correct.

Watch for: the same commit bundles an unrelated audio-download error-page refactor whose new template `templates/audio_unavailable.html` is **untracked and not in the commit** (confirmed) — a latent breakage for the audio path, outside DSI scope. No blocking DSI defects.

**Verdict**: APPROVED

## High-level view

The DSI formula is implemented verbatim in `_compute_dsi` and returns `None` whenever any of the four inputs is missing or non-finite (`_safe_float` rejects NaN), so a missing measure degrades to an "unavailable" box rather than a wrong number. The four inputs map to `mpt`, `f0_max_hz`, `i_low_db`, `jitter_pct`.

The data contract is established across two scripts: `asos_pipeline.py` computes `int_min_db_praatstyle` (min of the sustained /a/ intensity contour, option A) guarded against Praat errors and writes it to the TSV fieldnames; `analyze_asos_all.R` surfaces both `f0_max_hz` and the new `i_low_db` into the web CSV. Both are annotated in Catalan explaining that I_low is an approximation that biases the score away from published reference ranges.

The value and its texts are carried through the payload that `_save_meta` persists and `show_results` re-renders. A dedicated `_localize_dsi_payload` re-derives the orientative label and refreshes the text fields from the current-language `ui` on every re-render, keeping the numeric value and availability intact — so language switches and shared links keep the box. `dsi` is initialised `None` in every non-ASOS branch, so the box only appears for ASOS.

The UI strings exist in ca/es/en with matching siblings, and the template renders a visually distinct bordered `<section>` with a real heading and `aria-labelledby`, placed immediately before the `{{ ui.plot_title }}` block, with an unavailable fallback and the option-A small-print.

The one thing outside the DSI brief: this commit also reworks `download_audio` into styled error pages via a new `audio_unavailable.html` template that was never staged.

<details>
<summary>Issues (2)</summary>

1. **Untracked audio template** — `download_audio` (reworked in this commit) renders `templates/audio_unavailable.html`, but that file is untracked and absent from the commit; the audio-download error path will fail to find its template on a clean checkout. Stage/commit the template (or split this change out). Non-blocking for DSI. *(confirmed)*
2. **Bundled unrelated change** — the audio-download error-page refactor (`_audio_failure_page`, `download_audio` rework, `&lang=` plumbing, `audio_spent_*`/`audio_unavailable_*` text keys) is unrelated to DSI and should ideally be a separate commit. *(confirmed)*

</details>

<details>
<summary>Details</summary>

### DSI formula and graceful unavailability

`_compute_dsi` reads `mpt`, `f0_max_hz`, `i_low_db`, `jitter_pct` through `_safe_float` and returns `None` if any is `None`, else `round(0.13*mpt + 0.0053*f0_high - 0.26*i_low - 1.18*jitter + 12.4, 2)` — the spec formula verbatim with the correct unit mapping (MPT seconds, F0 Hz, I_low dB, Jitter percent). `_safe_float` returns `None` for NaN, so the guard also covers non-finite inputs: a recording missing one measure yields an unavailable box, never a corrupt score. The recorded math check 3.53 reproduces by hand. *(confirmed)*

### Data contract: minimum intensity and surfaced columns

`asos_pipeline.py` computes `int_min = safe_float(call(intensity_obj, "Get minimum", 0, 0, "Parabolic"))` inside a try/except that falls back to `float("nan")`, stores it as `int_min_db_praatstyle`, and adds that name to `fieldnames`. `analyze_asos_all.R` extends the `web_row` tibble with `f0_max_hz` and `i_low_db = col_or_na(df_out, "int_min_db_praatstyle")`. Both sites carry Catalan comments stating I_low is the option-A approximation (min of the sustained-vowel contour) that biases the DSI term — matching the user's "put a comment explaining it in the script" instruction. If these columns were ever dropped, `_compute_dsi` falls back to unavailable. *(confirmed)*

### Persistence and re-render across language switch

`dsi` is built in `_build_asos_rows` (now a 5-tuple ending in `dsi_payload`), the ASOS call site unpacks it, and `dsi = None` is set in the pataka/lectura/habla_libre/else branches. `show_results` calls `_localize_dsi_payload`, which keeps `value`/`available` and refreshes the text keys from the current `ui`, so the box survives language switch and shared links. The label-derivation logic (`>5` / `<-5` thresholds) is duplicated between `_build_dsi_payload` and `_localize_dsi_payload`; they currently agree, but a future threshold change would need to touch both. *(confirmed)*

### UI strings and template

All ten `asos_dsi_*` keys are present in ca/es/en with locale-appropriate formula formatting (comma decimals in ca/es, dot in en). The template guards the box with `{% if task == "asos" and dsi %}`, renders a `<section aria-labelledby="dsi-title">` with an `<h3 id="dsi-title">`, a badge value plus label, intro/formula/legend/range-note, and the option-A `approx_note` small-print; the unavailable branch shows intro + `unavailable`. It sits immediately before the `{{ ui.plot_title }}` ("Els teus resultats") block and is more emphasized than the adjacent interpretation box (2px accent border + shadow + badge vs 1px) — the boxed, visually distinct global indicator the user asked for.

### Bundled audio-download change (outside DSI scope)

This commit also replaces the raw `HTTPException` responses in `download_audio` with styled pages via `_audio_failure_page` + a `_blocked` helper rendering `audio_unavailable.html`, adds a `lang` query param plumbed from `show_results`, and adds `audio_spent_*` / `audio_unavailable_*` text keys. But `templates/audio_unavailable.html` is **untracked** — not part of the commit — so the committed code references a template that does not exist on a clean checkout, and the audio error path would raise `TemplateNotFound` at runtime. It affects the audio feature, not DSI, so it does not block the DSI gate, but the template must be committed before this change ships. *(confirmed)*

</details>

<details>
<summary>File map</summary>

- `scripts/asos_pipeline.py` — compute/emit `int_min_db_praatstyle` (option-A I_low), guarded, added to TSV fieldnames.
- `scripts/analyze_asos_all.R` — surface `f0_max_hz` and `i_low_db` into the web CSV tibble.
- `routers/clinica.py` — `_compute_dsi`, `_build_dsi_payload`, `_localize_dsi_payload`; thread `dsi`/`age` through analyze + re-render; (bundled) audio error-page rework.
- `core/texts.py` — `asos_dsi_*` keys in ca/es/en; (bundled) `audio_spent_*`/`audio_unavailable_*` keys.
- `templates/results.html` — boxed DSI callout above "Els teus resultats".
- `templates/audio_unavailable.html` — (bundled, UNTRACKED) styled audio-download error page.

Full diff: `git show 05579b0`.

</details>
