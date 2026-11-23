# DSI adaptat: verificació

Executat des de l'arrel amb .venv/bin/python /tmp/verify.py (script efímer; sortida literal sota). Unit test: `.venv/bin/python -m unittest tests.test_dsi_adapted_reference` -> OK.

```
== 1 syntax/imports
PASS ast.parse clinica 
PASS import clinica/texts 
PASS jinja load 
== 2 numbers
PASS ref mean 1.024972 vs 1.025
PASS ref sd 0.720220 vs 0.7202
PASS ref min -0.415468 vs -0.4155
PASS ref max 2.465411 vs 2.4654
PASS n 
PASS FDB01 ~1.39 1.39
PASS missing->None 
  val 1.385 z 0.5 normal
PASS sev normal 
  val -0.776 z -2.5 mild
PASS sev mild 
  val 3.546 z 3.5 marked
PASS sev marked 
  val -1.856 z -4.0 marked
PASS sev marked 
PASS label below/within/above 
PASS _clinical_hover/_infer_unit/_clean_label 'Dsi adapted'
== 3 e2e
  FDB01_AAAM1 mpt 19.24 f0h 244.53602 jit 0.2059 i_low 63.112167
PASS FDB01_AAAM1 first row dsi_adapted 1.39 exp 1.39 z=0.51 sev=normal
PASS FDB01_AAAM1 hidden absent 
PASS FDB01_AAAM1 payload ref Dins del rang de referència dels controls (orientatiu)
PASS FDB01_AAAM1 ~1.39 
  MMR01_AAAM1 mpt 17.06 f0h 356.017193 jit 0.1112 i_low 59.493512
PASS MMR01_AAAM1 first row dsi_adapted 1.81 exp 1.81 z=1.09 sev=normal
PASS MMR01_AAAM1 hidden absent 
PASS MMR01_AAAM1 payload ref Dins del rang de referència dels controls (orientatiu)
== 4 language switch gen3
  ca | DSI adaptat | Dins del rang de referència dels controls (orientatiu) | Valor de referència provisional: derivat de 8 enregistraments de controls sans de 60 anys (mitjana 1,02, SD 0,72; rang d
PASS ca formula 
PASS ca 6 semitones/56/not validated 
PASS ca row label 
PASS ca no prediction/Hakkesteegt 
PASS ca no alteration from dsi row 
PASS ca decimal s de controls sans de 60 anys (mitjana 1,02, SD 0,72; rang de referència -0,42 a
  es | DSI adaptado | Dentro del rango de referencia de los controles (orientativo) | Valor de referencia provisional: derivado de 8 grabaciones de controles sanos de 60 años (media 1,02, DE 0,72; rango de 
PASS es formula 
PASS es 6 semitones/56/not validated 
PASS es row label 
PASS es no prediction/Hakkesteegt 
PASS es no alteration from dsi row 
PASS es decimal e controles sanos de 60 años (media 1,02, DE 0,72; rango de referencia -0,42 a 2
  en | Adapted DSI | Within the controls’ reference range (orientative) | Provisional reference value: derived from 8 recordings of healthy controls aged 60 (mean 1.02, SD 0.72; reference range 
PASS en formula 
PASS en 6 semitones/56/not validated 
PASS en row label 
PASS en no prediction/Hakkesteegt 
PASS en no alteration from dsi row 
PASS en decimal althy controls aged 60 (mean 1.02, SD 0.72; reference range -0.42 to 2.47, mean 
== 5 backward compat
PASS gen2 crafted from HEAD code ['approx_note', 'available', 'f0_high_method', 'f0_note', 'formula', 'intro', 'label', 'legend', 'norm_max', 'norm_min', 'norm_pred', 'norm_sd', 'norm_sex_bucket', 'prediction', 'prediction_note', 'range_note', 'reference_source', 'title', 'unavailable', 'value']
PASS ca gen1 f0max wording 
PASS ca gen1 old row keeps label DSI
PASS ca gen1 label legacy Qualitat vocal intermèdia (orientatiu)
PASS ca gen2 texts identical to previous release 
PASS ca gen2 prediction sentence+citation 
PASS ca gen2 old row keeps label DSI
PASS ca gen2 label legacy Qualitat vocal intermèdia (orientatiu)
PASS es gen1 f0max wording 
PASS es gen1 old row keeps label DSI
PASS es gen1 label legacy Calidad vocal intermedia (orientativo)
PASS es gen2 texts identical to previous release 
PASS es gen2 prediction sentence+citation 
PASS es gen2 old row keeps label DSI
PASS es gen2 label legacy Calidad vocal intermedia (orientativo)
PASS en gen1 f0max wording 
PASS en gen1 old row keeps label DSI
PASS en gen1 label legacy Intermediate voice quality (orientative)
PASS en gen2 texts identical to previous release 
PASS en gen2 prediction sentence+citation 
PASS en gen2 old row keeps label DSI
PASS en gen2 label legacy Intermediate voice quality (orientative)
  real saved metas localized without exception
== 6 TestClient
 app imported; routes with results: ['/results/{file_path:path}', '/clinica/results/{rid}', '/clinica/results/{rid}/audio']
PASS gen3 ca http 200
PASS gen3 es http 200
PASS gen3 en http 200
PASS gen2 ca http 200
PASS gen2 es http 200
PASS gen2 en http 200
 throwaway metas removed: True
ALL OK

--- 7. números del paper ---
mean 1.0250 True
sd 0.7202 True
min -0.4155 True
max 2.4654 True
mean 2dp True
sd 2dp True
min 2dp True
max 2dp True
{'mean': 1.025, 'sd': 0.7202, 'min': -0.4155, 'max': 2.4654, 'n_recordings': 8, 'age': 60} 347
```
