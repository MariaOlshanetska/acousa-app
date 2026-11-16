# DSI normatiu per edat i sexe a l'ASOS

Afegeix la predicció del DSI segons Hakkesteegt 2006 (pred ± 2·SD, només 20-79 anys, sense extrapolació) i una fila 'dsi' al principi del perfil de resultats ASOS, amb la mateixa estructura que la resta de files.

Watch for: la SD és la del grup, no la residual de la regressió (possible, documentat al docstring); el z de la fila usa centre = punt mig i SD = amplada/4, coherent amb les altres mesures.

**Verdict**: APPROVED

## High-level view
`_dsi_normative(age, gender_value)` calcula predicció i banda amb els tres paràmetres (f/m/other) i retorna None fora de 20-79. `_build_asos_rows` rep `age` des d'`analyze`, insereix la fila 'dsi' en primera posició via `_range_payload` amb `hover_msg` buit (no afecta `alteration_comments` ni la interpretació global; `_clinical_hover('dsi')` retorna buit). El payload desa camps numèrics `norm_*` i `_dsi_norm_texts` regenera frase, nota i cita en ca/es/en; les metas antigues no fallen. La plantilla mostra predicció, nota i cita només si no són buides. Els canvis són a core/texts.py, routers/clinica.py i templates/results.html.

<details>
<summary>Issues (1)</summary>

1. **SD de grup** — possible; la banda usa la SD de la taula, no la residual; ja documentat, sense acció.

</details>

<details><summary>Details</summary>

## Verificació
.agents/tasks/dsi-norm-verification.md conté l'execució: exemple 34 anys dona -> pred 4.63, banda [0.61, 8.65], z -2.63 (mild); home 50 i altre 50 correctes; textos ca/es/en; meta antiga ok; Jinja carrega; TestClient end-to-end executat amb 200 en ca/es/en. No s'ha tornat a executar.

## Neteja i abast
S'han eliminat el paràgraf 'FEINA FUTURA (edat)' i el comentari de l'edat 'encara no es calcula'; els comentaris nous són en català. `asos_dsi_range_note` ja no diu que les normes són feina futura i `asos_dsi_approx_note` és coherent. Només 3 fitxers tocats. El commit b070d8d restaura CRLF a results.html (diff net: 9 insercions). Cap push (main 2 per davant d'origin).

</details>

## File map
- core/texts.py: claus noves ca/es/en i notes actualitzades
- routers/clinica.py: `_dsi_normative`, fila 'dsi', localització, paràmetre age
- templates/results.html: predicció, nota i cita condicionals
