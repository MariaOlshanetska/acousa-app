# Implementation Plan — Dysphonia Severity Index (DSI) for ASOS

Goal: add a global DSI summary indicator to the ASOS voice-quality results, shown in a
highlighted/boxed callout directly above the "Els teus resultats" ({{ui.plot_title}})
results-profile section. Compute DSI from values the pipeline already produces, plus one
new value (minimum intensity). Wire the participant age through so a future age-adjusted
norm can use it. Do NOT compute age norms. Do NOT fetch the paywalled reference article.

DSI formula (implement exactly):
`DSI = 0.13 * MPT + 0.0053 * F0_high - 0.26 * I_low - 1.18 * Jitter + 12.4`
with MPT in seconds, F0_high in Hz, I_low in dB, Jitter in percent.

Language rule: all NEW comments, docstrings and user-facing strings in CATALAN (primary);
add es/en siblings only where the UI dict already has es/en siblings (core/texts.py).

Data-source decisions already made (do not re-decide):
- MPT = `mpt` (from `dur_local`), already in the web CSV. Available.
- Jitter = `jitter_pct` (= `100 * jitter_ppq5`), already in the web CSV. Available.
- F0_high = `f0_max_hz`: computed in the pipeline and written to the TSV, but dropped by
  the R script. Must be surfaced into the web CSV (item 2).
- I_low = minimum intensity (dB): NOT currently computed. Decision (option A, user-approved):
  approximate it as the minimum of the intensity contour of the existing sustained /a/
  segment. This biases the DSI's I_low term, so scores will not line up exactly with
  published reference ranges; this is accepted and documented in a Catalan comment and in
  the UI small-print.

No automated test suite exists in this repo (no pytest, no test files). Verification therefore
relies on: (a) Python byte-compilation / import, (b) a syntax parse of the R script, (c) a
Jinja2 template parse, and (d) a one-time end-to-end manual ASOS run. The implement step must
not add a test framework for this task; use the verification commands given per item.

Run every command from the repo root `/home/labfon/Documentos/acousa-app` with the project
venv active (`.venv`). Order is strict: item N depends on item N-1's output being in the CSV
contract. Each item leaves the codebase importable/parseable.

---

- [ ] 1. Compute and emit `int_min_db_praatstyle` (minimum intensity, dB) in the ASOS pipeline.
      In `scripts/asos_pipeline.py`, the main flow already builds
      `intensity_obj = to_intensity_robust(seg, time_step=0.0, minimum_pitch=100.0, subtract_mean="yes")`
      at ~line 860. Right after it, compute the minimum of that intensity contour with Praat,
      guarded so a failure yields NaN, e.g.:
      `try: int_min = safe_float(call(intensity_obj, "Get minimum", 0, 0, "Parabolic"))`
      `except Exception: int_min = float("nan")`.
      Store it into the `row` dict (the dict literal that already holds `dur_local`, `h1_db`, …,
      at ~line 928) as `"int_min_db_praatstyle": float(int_min)`. Then add the string
      `"int_min_db_praatstyle"` to the `fieldnames` list (~line 980), immediately next to
      `"int_mid_db_praatstyle", "int_mean_db_praatstyle"`, so it is written to the TSV.
      Add a CATALAN comment at the computation site explaining this is an APPROXIMATION of the
      DSI's I_low (option A): the clinically correct I_low is the softest intensity in a
      dedicated soft-phonation task; here it is approximated with the minimum of the sustained
      /a/ intensity contour, which biases the DSI term so scores will not match published
      reference ranges exactly, and noting this is taken into account during analysis.
      Files: scripts/asos_pipeline.py
      Verify: `python -c "import ast; ast.parse(open('scripts/asos_pipeline.py').read())"` exits 0.
      Then confirm the field is emitted: run the pipeline once on an existing ASOS wav/TextGrid
      (reuse one under `results/` or `uploads/`) and grep the produced `*.voice_quality.tsv`
      header for `int_min_db_praatstyle`. If no sample pair is readily available, defer this
      runtime check to the item 6 end-to-end run and confirm only the `ast.parse` here.

- [ ] 2. Surface `f0_max_hz` and the new `i_low_db` into the web CSV from the R script.
      In `scripts/analyze_asos_all.R`, extend the `web_row <- tibble(...)` (~line 302) by adding
      two columns using the existing `col_or_na(df_out, ...)` helper:
      `f0_max_hz = col_or_na(df_out, "f0_max_hz")` and
      `i_low_db  = col_or_na(df_out, "int_min_db_praatstyle")`.
      Add the comma to the currently-last tibble line (`h1_a1 = col_or_na(df_out, "H1corr_A1corr")`)
      so the tibble stays valid. Add a CATALAN comment noting that `i_low_db` is the approximate
      minimum intensity per option A (minimum of the sustained-vowel intensity contour), used by
      the DSI, and that `f0_max_hz` is the maximum fundamental frequency used as F0_high.
      The web CSV is written unchanged by `write_csv(web_row, out_csv)` (~line 394).
      Files: scripts/analyze_asos_all.R
      Verify: `Rscript -e "invisible(parse('scripts/analyze_asos_all.R'))"` exits 0 (syntax OK).
      Confirm the two new columns appear in a produced web CSV during the item 6 end-to-end run.

- [ ] 3. Compute DSI in `routers/clinica.py` and thread `dsi`/`age` through render + persistence.
      3a. Add a helper `_compute_dsi(row0: dict) -> float | None` near `_build_asos_rows`
          (~line 1556). Read `mpt = _safe_float(row0.get("mpt"))`,
          `f0_high = _safe_float(row0.get("f0_max_hz"))`,
          `i_low = _safe_float(row0.get("i_low_db"))`,
          `jitter = _safe_float(row0.get("jitter_pct"))`. If any is None, return None; otherwise
          return `round(0.13*mpt + 0.0053*f0_high - 0.26*i_low - 1.18*jitter + 12.4, 2)`.
          (`_safe_float` already rejects NaN, so finite-ness is covered.) CATALAN docstring.
      3b. Add a helper that builds the `dsi_payload` dict from `ui` and the computed value, with
          keys: `value` (number or None), `available` (bool = value is not None),
          `title` (`ui["asos_dsi_title"]`), `intro` (`asos_dsi_intro`),
          `formula` (`asos_dsi_formula`), `legend` (`asos_dsi_legend`),
          `range_note` (`asos_dsi_range_note`), `unavailable` (`asos_dsi_unavailable`),
          `approx_note` (`asos_dsi_approx_note`), and a coarse `label` classifying the score:
          `> 5` -> good/no-dysphonia label; `-5 <= value <= 5` -> intermediate label;
          `< -5` -> severe label (short Catalan labels, orientative not diagnostic — reuse new UI
          keys `asos_dsi_label_good`, `asos_dsi_label_mid`, `asos_dsi_label_severe`; `label` is ""
          when unavailable). Read keys defensively with the existing `_ui_text` helper.
      3c. Change `_build_asos_rows` to also return `dsi_payload`: its signature/return currently
          ends with `f0_summary_text`; make it return
          `rows, interpretation_global, interpretation_comment, f0_summary_text, dsi_payload`
          (build `dsi_payload` from `_compute_dsi(row0)` just before the return). Update the type
          hint accordingly.
      3d. Update the single call site in the `elif task == "asos":` branch (~line 2251):
          `rows, interpretation_global, interpretation_comment, f0_summary_text, dsi = _build_asos_rows(csv_path, final_gender, ui)`.
          Initialise `dsi = None` in every other task branch (alongside `f0_summary_text = ""`)
          so non-ASOS tasks pass `None` — add `dsi = None` to the pataka, lectura, habla_libre,
          and else branches.
      3e. In the `payload = { ... }` dict (~line 2429) add `"dsi": dsi`. `"age": age` is already
          present — add a CATALAN comment that `age` is surfaced here for future age-adjusted DSI
          norms (not computed yet). `_save_meta(rid, payload)` already persists the whole payload,
          so `dsi` and `age` survive to the re-render route automatically.
      3f. In `show_results` (~line 1910), after `_load_meta`, the whole `payload` is passed to the
          template, so `payload["dsi"]` and `payload["age"]` are already available on re-render /
          language switch / shared links. Confirm no key is stripped. If DSI text must follow the
          language of the re-render (like habla_libre does via `_localize_*`), the minimum
          contract is: the number and box survive a re-render. Since `dsi_payload` text comes from
          `ui` at analyze time, add — mirroring `_localize_habla_libre_payload` — a small
          re-localisation so that on `show_results` the ASOS `dsi` dict's text fields are refreshed
          from the current-language `ui` when `payload.get("task") == "asos"` and
          `payload.get("dsi")` is a dict (keep `value`/`available`/`label`, replace the text keys
          from `ui`). If this proves awkward, fall back to persisting the computed text as-is; the
          number and box must survive regardless.
      Files: routers/clinica.py
      Verify: `python -c "import ast; ast.parse(open('routers/clinica.py').read())"` exits 0, then
      `python -c "import routers.clinica"` imports without error. Functional check deferred to item 6.

- [ ] 4. Add the DSI UI strings to `core/texts.py` in ca/es/en.
      Add these keys in the `ca` block near `plot_title` (~line 67): `asos_dsi_title`,
      `asos_dsi_intro`, `asos_dsi_formula`, `asos_dsi_legend`, `asos_dsi_range_note`,
      `asos_dsi_unavailable`, `asos_dsi_approx_note`, `asos_dsi_label_good`,
      `asos_dsi_label_mid`, `asos_dsi_label_severe`. Add matching siblings near `plot_title` in
      the `es` block (~line 464) and the `en` block (~line 856). Use the exact Catalan copy below
      for `ca`; provide faithful es/en translations (mirroring how plot_title / asos_* keys are
      translated per language).
      ca values:
      - asos_dsi_title: "Índex de Severitat de la Disfonia (DSI)"
      - asos_dsi_intro: "L’Índex de Severitat de la Disfonia (DSI) és un indicador global de la
        qualitat vocal calculat a partir de les mesures acústiques i aerodinàmiques enregistrades.
        La puntuació permet estimar el grau de severitat de la disfonia: els valors més alts
        indiquen una millor qualitat vocal i els valors més baixos, una alteració vocal més
        important. En l’escala de referència original, els valors se situen aproximadament entre
        +5 (veu sense disfonia) i −5 (disfonia greu). Tanmateix, com que els paràmetres individuals
        poden presentar un rang ampli de valors, també són possibles puntuacions fora d’aquest
        interval."
      - asos_dsi_formula: "DSI = 0,13 · MPT + 0,0053 · F0_màx − 0,26 · I_mín − 1,18 · Jitter + 12,4"
      - asos_dsi_legend: "MPT: temps màxim de fonació (durada, en segons). · F0_màx: freqüència
        fonamental màxima (Hz). · I_mín: intensitat mínima (dB). · Jitter: jitter percentual (%)."
        (If a list is preferred for rendering, store as a Python list of the four items; keep the
        chosen type consistent with how the template reads it in item 5.)
      - asos_dsi_range_note: "Interpretació orientativa (de moment, sense valors normatius per
        edat): ~+5 indica absència de disfonia i ~−5 una disfonia greu; valors > 5 suggereixen una
        bona qualitat vocal i valors < 5, una qualitat vocal pitjor. En el futur s’incorporaran
        valors de referència adaptats per edat i sexe."
      - asos_dsi_unavailable: "No s’ha pogut calcular el DSI en aquest enregistrament perquè falta
        alguna de les mesures necessàries (MPT, F0 màxima, intensitat mínima o jitter)."
      - asos_dsi_approx_note: "Nota: la I_mín s’aproxima a partir del mínim del contorn
        d’intensitat de la vocal sostinguda, de manera que el valor pot no coincidir exactament
        amb les escales de referència clàssiques."
      - asos_dsi_label_good: "Qualitat vocal bona (orientatiu)"
      - asos_dsi_label_mid: "Qualitat vocal intermèdia (orientatiu)"
      - asos_dsi_label_severe: "Alteració vocal marcada (orientatiu)"
      Files: core/texts.py
      Verify: `python -c "import ast; ast.parse(open('core/texts.py').read())"` exits 0, then
      `python -c "from core.texts import LANG_TEXTS; [print(l, 'asos_dsi_title' in LANG_TEXTS[l]) for l in ('ca','es','en')]"`
      prints True for all three.

- [ ] 5. Render the highlighted DSI callout in `templates/results.html`, above "Els teus resultats".
      Insert the block IMMEDIATELY BEFORE the results-profile section, i.e. before the
      `{% if row_groups %} … {% elif rows %} … {% endif %}` plot-wrap block that is headed by
      `{{ ui.plot_title }}` (~lines 224–245, inside `results-card`, after the
      `{# RLE … #}` comment). Guard with `{% if task == "asos" and dsi %}`.
      Render a visually distinct, bordered/shaded box (clearly more emphasized than the per-measure
      cards and than the interpretation_global box at ~line 191): reuse that box's inline-style
      idiom (`border-radius`, `border:1px solid rgba(242,189,160,0.6)`, `background:#fffaf7`) but
      make it its own emphasized block — stronger border/accent and a badge-like value. Contents:
      a semantic heading (`<h3>` or `<h2>`) with `{{ dsi.title }}`; then
      `{% if dsi.available %}` a large DSI number `{{ dsi.value }}` styled as a badge plus the short
      `{{ dsi.label }}`, the `{{ dsi.intro }}` paragraph, the `{{ dsi.formula }}`, the
      `{{ dsi.legend }}` variable legend (iterate if it is a list; else print the string), the
      `{{ dsi.range_note }}` interpretation note, and a small-print `{{ dsi.approx_note }}`.
      `{% else %}` render the same box with `{{ dsi.intro }}` and `{{ dsi.unavailable }}` instead of
      a number. Ensure sufficient contrast and a real heading for accessibility.
      Files: templates/results.html
      Verify:
      `python -c "from jinja2 import Environment, FileSystemLoader; Environment(loader=FileSystemLoader('templates')).get_template('results.html')"`
      exits 0 (template parses). Visual/behavioural check deferred to item 6.

- [ ] 6. End-to-end verification of the full DSI path (depends on items 1–5).
      Start the app (`uvicorn main:app` from repo root with the venv active; confirm the entry in
      `main.py` if the module path differs) and run one ASOS recording through `/clinica` so the
      Python pipeline + R script + router all execute on real input. Confirm:
      (a) the produced `*.voice_quality.tsv` header contains `int_min_db_praatstyle`;
      (b) the web CSV produced by the R script contains `f0_max_hz` and `i_low_db`;
      (c) the ASOS results page shows the highlighted DSI box ABOVE "Els teus resultats", with a
          numeric DSI (verify it equals
          `0.13*mpt + 0.0053*f0_max_hz - 0.26*i_low_db - 1.18*jitter_pct + 12.4` rounded to 2
          decimals using the row's own values), the Catalan intro/formula/legend/range note and
          the I_mín approximation small-print;
      (d) reloading the results URL / switching language still shows the box and number
          (re-render from saved meta), and the box does not appear for a non-ASOS task;
      (e) when a required measure is missing (e.g. force one of the four to NaN in the CSV), the
          box renders with the `asos_dsi_unavailable` text instead of a number.
      Files: none (verification only).
      Verify: all of (a)–(e) hold. Remove any temporary/sample files created for this check.

---

## Verification run (first iteration — implemented)

Commands run from repo root with `.venv` Python; all passed:
- `import ast; ast.parse(...)` on `scripts/asos_pipeline.py`, `routers/clinica.py`, `core/texts.py` → `py ok`.
- `python -c "import routers.clinica, core.texts"` → `import ok`.
- `Rscript -e "parse('scripts/analyze_asos_all.R')"` → `R ok` (Rscript is installed; syntax valid).
- UI keys present in ca/es/en (`asos_dsi_*`) → `True` for all three.
- Jinja parse of `templates/results.html` → `jinja ok`.
- DSI math: `_compute_dsi({mpt:20, f0_max_hz:400, i_low_db:50, jitter_pct:0.5})` = `3.53` (expected 3.53);
  missing-input case returns `None`. Throwaway script removed after.

Decisions kept least-invasive: `dsi` is `None` for non-ASOS tasks; DSI text is re-localized on
`show_results` via `_localize_dsi_payload` while value/availability survive the re-render; `age` is
persisted in the payload with a Catalan comment marking it for future age-adjusted norms (not computed).

Notes / assumptions:
- `asos_dsi_legend` is specified as a single string with " · " separators; if the implementer
  prefers a list for cleaner markup, store a Python list and iterate in the template — keep
  texts.py and results.html consistent. Either is acceptable.
- The reference article for future age/sex norms is paywalled; it is NOT fetched and
  age-adjusted norms are out of scope. Only the `age` value is wired through (already in the
  payload) for future use, with a Catalan comment marking the intent.
- `_compute_dsi` relies on the CSV column contract established by items 1–2 (`f0_max_hz`,
  `i_low_db`); if item 2 is skipped, `f0_high`/`i_low` are None and DSI shows as unavailable,
  which is the correct graceful fallback.
