# Verificació F0_alta (mitjana + 6 st)

## Execució end-to-end, canvi de llengua i dades antigues (/tmp/f0v/run.py)
```
20220201_T161859_FDB01_AAAM1 TSV f0_high_6st 244.536020 f0_mean 172.913078 | CSV {'mpt': '19.24', 'f0_mean_hz': '172.913078', 'f0_high_6st_hz': '244.53602', 'f0_max_hz': '206.597892', 'i_low_db': '63.112167', 'jitter_pct': '0.2059'}
 DSI -0.45 expected -0.45 rows[0] dsi hidden absent True method mean_plus_6st
20220211_T141502_MMR01_AAAM1 TSV f0_high_6st 356.017193 f0_mean 251.742172 | CSV {'mpt': '17.06', 'f0_mean_hz': '251.742172', 'f0_high_6st_hz': '356.017193', 'f0_max_hz': '264.885774', 'i_low_db': '59.493512', 'jitter_pct': '0.1112'}
 DSI 0.91 expected 0.91 rows[0] dsi hidden absent True method mean_plus_6st
ca | DSI = 0,13 · MPT + 0,0053 · F0_alta − 0,26 · I_mín − 1,18 · Jitter + 12,4 | MPT: temps màxim de fonació (durada, en segons). · F0_alta: freqüència fonamental alta estimada = F0 mitjana + 6 semitons (Hz). · I_mín: intensitat mínima aproximada (dB). · Jitter: jitter percentual (%). 
  F0NOTE: Per què F0_alta s’estima? El DSI original fa servir la freqüència més alta que s’assoleix en un glissando ascendent, una prova que aquesta tasca no inclou. Per això estimem F0_alta com la F0 mitjana de la teva vocal a to còmode més 6 semitons (l’interval que sol caldre per pujar el to en una pregunta en veu de pit parlada), és a dir, multiplicant-la per aprox. 1,41. 
  APPROX: Nota: aquest DSI usa dues aproximacions. La F0_alta és una estimació (F0 mitjana + 6 semitons), no la F0 màxima mesurada, i la I_mín s’obté del mínim d’intensitat de la vocal /a/ sostinguda, en dB no calibrats, no d’una tasca de fonació específica com als estudis de referència. Per això el DSI pot sortir més baix que els valors de referència de l’article. És una punt
es | DSI = 0,13 · MPT + 0,0053 · F0_alta − 0,26 · I_mín − 1,18 · Jitter + 12,4 | MPT: tiempo máximo de fonación (duración, en segundos). · F0_alta: frecuencia fundamental alta estimada = F0 media + 6 semitonos (Hz). · I_mín: intensidad mínima aproximada (dB). · Jitter: jitter porcentual (%). 
  F0NOTE: ¿Por qué se estima F0_alta? El DSI original usa la frecuencia más alta que se alcanza en un glissando ascendente, una prueba que esta tarea no incluye. Por eso estimamos F0_alta como la F0 media de tu vocal a tono cómodo más 6 semitonos (el intervalo que suele hacer falta para subir el tono en una pregunta en voz de pecho hablada), es decir, multiplicándola por aprox. 1,41. 
  APPROX: Nota: este DSI usa dos aproximaciones. La F0_alta es una estimación (F0 media + 6 semitonos), no la F0 máxima medida, y la I_mín se obtiene del mínimo de intensidad de la vocal /a/ sostenida, en dB no calibrados, no de una tarea de fonación específica como en los estudios de referencia. Por ello el DSI puede salir más bajo que los valores de referencia del artículo. Es una puntua
en | DSI = 0.13 · MPT + 0.0053 · F0_high − 0.26 · I_min − 1.18 · Jitter + 12.4 | MPT: maximum phonation time (duration, in seconds). · F0_high: estimated highest fundamental frequency = mean F0 + 6 semitones (Hz). · I_min: approximate minimum intensity (dB). · Jitter: jitter percentage (%). 
  F0NOTE: Why is F0_high estimated? The original DSI uses the highest pitch reached in an upward pitch sweep, which this task does not include. We therefore estimate F0_high as the mean F0 of your comfortable-pitch vowel plus 6 semitones (the interval usually needed to raise pitch for a spoken question in chest voice), i.e. multiplied by about 1.41. 
  APPROX: Note: this DSI uses two approximations. F0_high is an estimate (mean F0 + 6 semitones), not the measured maximum F0, and I_min is taken from the minimum intensity of the sustained /a/, in uncalibrated dB, not from a dedicated phonation task as in the reference studies. The DSI may therefore come out lower than the paper’s reference values. It is an orientative score, not a diagnosis.
OLD csv: dsi value None available False method mean_plus_6st rows ['mpt', 'f0_mean_hz', 'jitter_pct']
asos metas with dsi: 8
results/_meta/cb9fc99ebbb84f53b6b9450679c81324.json has f0_high_method: None
   ca DSI = 0,13 · MPT + 0,0053 · F0_màx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   es DSI = 0,13 · MPT + 0,0053 · F0_máx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   en DSI = 0.13 · MPT + 0.0053 · F0_max − 0.26 · I_min − 1.18 · J | f0_note= ''
results/_meta/0f81442336474a7086da526d05c25613.json has f0_high_method: None
   ca DSI = 0,13 · MPT + 0,0053 · F0_màx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   es DSI = 0,13 · MPT + 0,0053 · F0_máx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   en DSI = 0.13 · MPT + 0.0053 · F0_max − 0.26 · I_min − 1.18 · J | f0_note= ''
results/_meta/143f0aaadbca488fb88a81147da4c3b4.json has f0_high_method: None
   ca DSI = 0,13 · MPT + 0,0053 · F0_màx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   es DSI = 0,13 · MPT + 0,0053 · F0_máx − 0,26 · I_mín − 1,18 · J | f0_note= ''
   en DSI = 0.13 · MPT + 0.0053 · F0_max − 0.26 · I_min − 1.18 · J | f0_note= ''
LEGACY ca DSI = 0,13 · MPT + 0,0053 · F0_màx − 0,26 · I_mín − 1,18 · Jitter + 12,4 | MPT: temps màxim de fonació (durada, en segons). · F0_màx: freqüència fonamental màxima (H | note ''
LEGACY es DSI = 0,13 · MPT + 0,0053 · F0_máx − 0,26 · I_mín − 1,18 · Jitter + 12,4 | MPT: tiempo máximo de fonación (duración, en segundos). · F0_máx: frecuencia fundamental m | note ''
LEGACY en DSI = 0.13 · MPT + 0.0053 · F0_max − 0.26 · I_min − 1.18 · Jitter + 12.4 | MPT: maximum phonation time (duration, in seconds). · F0_max: maximum fundamental frequenc | note ''
```

## TestClient (/clinica/results/<rid>?lang=ca|es|en, meta temporal esborrada)
```
ca 200 f0_note in html: True dsi value present: True
es 200 f0_note in html: True dsi value present: True
en 200 f0_note in html: True dsi value present: True
deleted True
```

ast.parse, Rscript parse, import i Jinja (via TestClient) OK; results.html i analyze_asos_all.R mantenen CRLF (diff de 3 línies).
