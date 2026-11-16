# Verificació DSI normatiu

Ordres (des de l'arrel, `PYTHONPATH=. .venv/bin/python`): /tmp/verify.py i /tmp/e2e.py (TestClient amb meta temporal `zz_e2e_test`, esborrada després).

```
ast ok
import ok
34 dona {'pred': 4.63, 'min': 0.61, 'max': 8.65, 'sd': 2.01, 'sex_bucket': 'f'}
50 home {'pred': 3.46, 'min': -0.42, 'max': 7.34, 'sd': 1.94, 'sex_bucket': 'm'}
50 altre {'pred': 3.645, 'min': -0.355, 'max': 7.645, 'sd': 2.0, 'sex_bucket': 'other'}
normative ok
ca -2.63 mild La predicció del DSI segons la teva edat i sexe és: 4.63 (rang de normalitat: 0.61 a 8.65).
 La referència ajustada per edat i sexe només està disponible per a edats entre 20 i 79 anys; per això aquest resultat s’interpreta només amb la referència general.
True ['display_max', 'display_min', 'help_text', 'hover_msg', 'label', 'normal_max', 'normal_max_rel', 'normal_min', 'normal_min_rel', 'severity', 'unit', 'value', 'value_rel', 'variable', 'z']
es -2.63 mild La predicción del DSI según tu edad y sexo es: 4.63 (rango de normalidad: 0.61 a 8.65).
 La referencia ajustada por edad y sexo solo está disponible para edades entre 20 y 79 años; por eso este resultado se interpreta solo con la referencia general.
en -2.63 mild The DSI prediction for your age and sex is: 4.63 (normal range: 0.61 to 8.65).
 The age- and sex-adjusted reference is only available for ages 20 to 79, so this result is interpreted with the general reference only.
ca DSI | Índex de Severitat de la Disfonia (DSI): indicador | La predicció del DSI segons la teva edat i sexe és: 4.63 (rang de normalitat: 0.61 a 8.65).
ca old ok; note: La referència ajustada per edat i sexe només està 
es DSI | Índice de Severidad de la Disfonía (DSI): indicado | La predicción del DSI según tu edad y sexo es: 4.63 (rango de normalidad: 0.61 a 8.65).
es old ok; note: La referencia ajustada por edad y sexo solo está d
en DSI | Dysphonia Severity Index (DSI): a global voice-qua | The DSI prediction for your age and sex is: 4.63 (normal range: 0.61 to 8.65).
en old ok; note: The age- and sex-adjusted reference is only availa
jinja ok
ca 200 True True True True
es 200 True True True True
en 200 True True True True
```

Nota: z=-2,63 -> severity 'mild' (2<=|z|<3) per _severity_from_z; DSI fora de banda.

## Iteració de revisió
- results.html: restaurat CRLF; diff vs HEAD~1 = 9 insercions. Jinja carrega la plantilla (ok).
- Nota no bloquejant (prediction_note amb edat absent): es manté, el text és neutre.
