# F0_alta estimada (F0 mitjana + 6 st) per al DSI de l'ASOS

El DSI de l'ASOS fa servir ara F0_alta = f0_mean_hz · 2^(6/12), calculada a `asos_pipeline.py`, exportada per `analyze_asos_all.R` com a `f0_high_6st_hz` i consumida per `_compute_dsi`. La nova entrada s'amaga del gràfic, el payload guarda `f0_high_method='mean_plus_6st'` i `results.html` mostra la nota de F0. Les metas antigues es descriuen amb el text de F0 màxima.

Watch for: només una diferència menor de redacció als textos legacy (confirmed).

**Verdict**: APPROVED

## High-level view

La estimació es calcula una sola vegada al pipeline i viatja per la columna nova del CSV. `_compute_dsi` retorna None si falta, així que un CSV antic no barreja definicions. El gràfic oculta la fila nova igual que f0_max i i_low.

`_localize_dsi_payload` tria els textos nous o `_f0max` segons `f0_high_method`. Les metas antigues no tenen el camp, per tant mantenen la descripció anterior i no mostren la nota de F0. Els textos nous existeixen en ca/es/en.

<details>
<summary>Issues (1)</summary>

1. **Text legacy retocat** — `asos_dsi_approx_note_f0max` (ca/es/en) no conserva literalment l'original ("tasca de fonació el més suau possible en dB SPL" ara és "tasca de fonació específica"). Restaurar el text antic si es vol fidelitat estricta (confirmed, no bloquejant).

</details>

<details><summary>Details</summary>

## Evidència de verificació

`f0high-verification.md` mostra l'execució end-to-end sobre els dos controls: DSI -0.45 i 0.91, iguals als esperats. També mostra la fila oculta, el mètode `mean_plus_6st`, un CSV antic amb DSI None, tres metas antigues amb text legacy sense nota de F0, i TestClient 200 en ca/es/en amb la nota present. No s'han tornat a executar proves.

## Metas antigues i textos legacy

El sufix `_f0max` s'aplica quan el camp falta, de manera que les metas existents conserven fórmula i llegenda amb F0 màxima. La nota d'aproximació legacy té una redacció lleugerament diferent de l'original (vegeu Issues). Els textos nous diuen que el DSI "pot sortir més baix" i que és orientatiu i no un diagnòstic, tal com es demanava; l'explicació del glissando absent és honesta.

## Comprovacions de forma

Comentaris i docstrings nous en català. `results.html` fa un diff de 3 línies amb CRLF. No hi ha commit ni push (HEAD = origin/main 7ab54e3). Els fitxers d'ASOS/controls no apareixen al diff. I_low no s'ha tocat.

</details>

<details><summary>File map</summary>

- core/texts.py: textos nous i variants `_f0max` en ca/es/en
- routers/clinica.py: `_compute_dsi`, payload, localització, fila oculta
- scripts/analyze_asos_all.R: columna `f0_high_6st_hz`
- scripts/asos_pipeline.py: càlcul i TSV
- templates/results.html: paràgraf f0_note

</details>
