DEFAULT_LANG = "ca"

LANG_TEXTS = {'ca': {'app_title': 'AcousA - Anàlisi de la parla',
        'page_title': 'AcousA - Anàlisi de la parla',
        'upload_title': "També pots pujar un fitxer d'àudio",
        'upload_help': "Pots pujar un fitxer d'àudio (WAV, MP3, etc.) per analitzar-lo.",
        'upload_label': "Fitxer d'àudio",
        'record_title': 'Gravar des del navegador',
        'submit_button': 'Analitzar',
        'result_title': "Resultat de l'anàlisi",
        'file_analyzed': 'Fitxer analitzat:',
        'col_measure': 'Mesura',
        'col_value': 'Valor',
        'col_lower': 'Rang mínim',
        'col_upper': 'Rang màxim',
        'back_link': '⟵ Tornar a fer una altra anàlisi',
        'lang_label': 'Llengua de la interfície',
        'msg_unsupported': '⚠️ El teu navegador no permet accedir al micròfon. Prova amb un navegador més recent.',
        'msg_supported': 'Pots gravar directament des del navegador en la majoria de pcs, Android i iPhone.',
        'msg_recording': '🔴 Gravant... parla ara.',
        'msg_processing': 'Processant la gravació...',
        'msg_ready': 'Gravació llesta. Ara pots pitjar «Analitzar». Fitxer: {file}',
        'task_label': 'Vull evaluar la meva...',
        'task_result_label': 'Tasca',
        'preinfo_title': 'Abans de gravar',
        'age_label': 'La teva edat',
        'age_placeholder': 'Anys',
        'age_help': "En el futur adaptarem els valors de referència als diferents grups d'edat.",
        'consent_label': 'Ús de les dades amb finalitats científiques',
        'consent_yes': "Sí, autoritzo que les dades d'aquesta gravació s'utilitzin de manera anonimitzada amb "
                       'finalitats de recerca científica.',
        'consent_no': "No, prefereixo que les dades d'aquesta gravació s'utilitzin només per a la meva "
                      'automonitorització.',
        'consent_info_yes': 'Gràcies per la teva col·laboració.',
        'consent_info_no': "Les teves dades no s'utilitzaran amb finalitats científiques. Pots continuar utilitzant "
                           "l'aplicació només per a automonitoritzar-te.",
        'task_instructions_label': 'Instruccions:',
        'msg_audio_quality_fail': 'L’enregistrament no compleix els requisits mínims de qualitat per a l’anàlisi '
                                  '(durada mínima: 3 s; contrast veu–soroll: ≥ 30 dB). Si us plau, grava en un entorn '
                                  'silenciós, parla amb una veu clara i prou alta i assegura’t que l’enregistrament '
                                  'duri almenys 3 segons.',
        'download_csv': 'Descarregar CSV',
        'sex_label': 'Sexe / gènere',
        'sex_male': 'Home',
        'sex_female': 'Dona',
        'sex_nb': 'No binari',
        'sex_other': 'Altres (especifica)',
        'sex_other_specify': 'Especifica',
        'sex_other_placeholder': 'Especifica (si has triat «Altres»)',
        'sex_help': 'S’utilitzarà només per adaptar valors de referència per grups.',
        'interpretation_title': 'Interpretació',
        'interpretation_fallback': 'No s’ha pogut calcular una interpretació automàtica d’aquest resultat.',
        'pataka_comment_normal': 'Els teus resultats estan dins dels valors de normalitat per a la velocitat de la '
                                 'parla.',
        'pataka_comment_fast': 'Els teus resultats suggereixen una velocitat de parla més aviat ràpida (per sobre del '
                               'que és habitual).',
        'pataka_comment_slow_or_badrec': 'Els teus resultats suggereixen una velocitat de parla més aviat lenta (per '
                                         'sota del que és habitual). Si et sorprèn, és possible que l’enregistrament '
                                         'no sigui òptim (soroll, talls, distància al micròfon).',
        'asos_comment_normal': 'Els teus resultats (jitter i shimmer) estan dins dels valors de normalitat.',
        'asos_comment_unstable': 'Els teus resultats mostren jitter i/o shimmer per sobre de l’esperat, cosa que '
                                 'sovint indica més irregularitat en la vibració de la veu. Si estaves refredada/da o '
                                 'cansada/da, podria influir.',
        'asos_comment_below': 'Els teus resultats mostren jitter i/o shimmer per sota del que és habitual. Normalment '
                              'no és preocupant; a vegades reflecteix una senyal molt estable o condicions '
                              'd’enregistrament especialment bones.',
        'plot_title': 'Els teus resultats',
        'resources_title': 'Recursos',
        'resources_intro': 'Enllaços útils per a fonetistes i eines relacionades.',
        'back_home': 'Inici',
        'msg_rec_target': 'Objectiu mínim recomanat: 10 s',
        'msg_rec_breath_cue': '💨 Agafa aire!',
        'msg_rec_silence_auto_stopped': 'Processant l’anàlisi...',
        'msg_rec_badge_recording': 'Gravant…',
        'msg_rec_badge_complete': '✅ durada suficient',
        'msg_rec_badge_finished': 'Gravació acabada',
        'msg_rec_error': 'Error: {error}',
        'msg_rec_invalid': "La gravació no s'ha generat correctament. Torna-la a gravar.",
        'pataka_not_comparable': 'No s’ha pogut comparar aquesta mesura amb la normalitat.',
        'pataka_speech_rate_high': 'La velocitat articulatòria està molt per sobre del rang esperat. En Pablo Hasél '
                                   'n’estaria orgullós.',
        'pataka_speech_rate_low': 'La velocitat articulatòria apareix reduïda respecte del rang de referència.',
        'pataka_speech_rate_normal': 'La velocitat articulatòria se situa dins del rang esperat.',
        'pataka_percentage_v_normal': 'La proporció vocàlica se situa dins de la normalitat.',
        'pataka_percentage_v_low': 'La proporció vocàlica apareix reduïda respecte del patró esperat.',
        'pataka_percentage_v_high': 'La proporció vocàlica apareix augmentada respecte del patró esperat.',
        'pataka_temporal_var_normal': 'La variabilitat temporal d’aquest paràmetre se situa dins del rang esperat.',
        'pataka_temporal_var_low': 'La variabilitat temporal d’aquest paràmetre apareix reduïda.',
        'pataka_temporal_var_high': 'La variabilitat temporal d’aquest paràmetre apareix augmentada.',
        'pataka_vdist_mean_normal': 'La distància mitjana entre nuclis vocàlics està dins del rang esperat.',
        'pataka_vdist_mean_low': 'La distància mitjana entre nuclis vocàlics apareix reduïda.',
        'pataka_vdist_mean_high': 'La distància mitjana entre nuclis vocàlics apareix augmentada.',
        'pataka_generic_out': 'Aquest paràmetre es desvia del rang de referència.',
        'pataka_generic_normal': 'Aquest paràmetre se situa dins de la normalitat.',
        'pataka_global_no_comparison_title': 'No s’ha pogut calcular la comparació amb la normalitat.',
        'pataka_global_no_comparison_body': 'No hi havia prou valors comparables amb l’arxiu de referència.',
        'pataka_global_normal_title': 'El teu rendiment articulatori se situa dins de la normalitat.',
        'pataka_global_normal_body': 'No s’observen desviacions rellevants en els paràmetres temporals analitzats de '
                                     'la tasca de diadococinèsia.',
        'pataka_global_marked_title': 'S’observen alteracions clares en alguns paràmetres de ritme articulatori.',
        'pataka_global_marked_body': 'Les desviacions més destacades apareixen en {labels}. Això suggereix un patró '
                                     'temporal diferent de l’esperat i convé interpretar-ho conjuntament amb '
                                     'l’avaluació clínica.',
        'pataka_global_mild_title': 'S’observen desviacions lleus en alguns paràmetres de ritme articulatori.',
        'pataka_global_mild_body': 'Els paràmetres que més s’allunyen de la referència són {labels}. El patró global '
                                   'no és necessàriament patològic, però sí diferent del grup normatiu.',
        'download_audio': 'Descarregar àudio',
        'plot_alt': 'Gràfic de comparació amb la normalitat',
        'reading_reference_title': 'Text de lectura',
        'detected_transcript_title': 'Transcripció detectada',
        'msg_habla_libre_slow': 'L’anàlisi de parla lliure pot trigar una mica més que les altres tasques, perquè '
                                'inclou transcripció automàtica, generació de TextGrid, alineament amb Montreal Forced '
                                'Aligner, anàlisi lingüística amb Stanza i consulta lèxica amb Datamuse.',
        'automatic_transcription_title': 'Transcripció automàtica',
        'automatic_transcription_note': "Transcripció generada automàticament amb Whisper: model mitjà d'espanyol.",
        'textgrid_title': 'TextGrid generat amb MFA',
        'textgrid_view': 'Veure TextGrid',
        'results_plot_note_habla_libre': 'Barres = rang de referència provisional. Punt = resultat de '
                                         "l'enregistrament. RLE = riquesa lèxica estimada.",
        'measures_guide_title': 'Guia de mesures',
        'measures_guide_intro': "Desplega cada mesura per veure què significa i com s'ha calculat.",
        'download_textgrid': 'Descarregar TextGrid',
        'download_lemmas_json': 'Descarregar lemes JSON',
        'plot_hover_value': 'Valor',
        'plot_hover_scale': 'Escala',
        'results_unavailable': 'Els resultats ja no estan disponibles.',
        'hl_unit_sounds_per_second': 'sons/s',
        'hl_group_intonation': 'Entonació',
        'hl_group_complejidad_lexica': 'Complexitat lèxica',
        'hl_group_complejidad_sintactica': 'Complexitat sintàctica',
        'hl_group_fluencia': 'Fluència',
        'hl_label_speech_duration': 'Durada',
        'hl_label_articulation_duration': 'Temps articulat',
        'hl_label_speech_rate': 'Speech rate',
        'hl_label_articulation_rate': 'Articulation rate',
        'hl_label_pause_count': 'Pauses',
        'hl_label_mean_pause_duration': 'Pausa mitjana',
        'hl_label_pause_percentage': '% pausa',
        'hl_label_f0_mean': 'F0 mitjana',
        'hl_label_f0_sd': 'Variabilitat F0',
        'hl_label_f0_range': 'Rang F0',
        'hl_label_unique_lexical_lemmas': 'Lemes lèxics',
        'hl_label_lexical_density': 'Densitat lèxica',
        'hl_label_lexical_ttr': 'TTR lèxic',
        'hl_label_lexical_richness_score_1_5': 'RLE 1–5',
        'hl_label_lexical_complexity_rare_percent': '% lemes poc freqüents',
        'hl_label_mean_datamuse_frequency_per_million': 'Freq. mitjana',
        'hl_label_subordinate_clause_count': 'Subordinades',
        'hl_label_subordinates_per_sentence': 'Subordinades/oració',
        'hl_label_long_pauses': 'Pauses llargues',
        'hl_label_sentence_count': 'Oracions',
        'hl_label_mean_sentence_length_words': "Longitud mitjana d'oració",
        'hl_label_sound_count': 'Sons detectats',
        'hl_help_speech_duration': "Durada entre la primera i l'última paraula alineada. Exclou el silenci inicial i "
                                   'final.',
        'hl_help_articulation_duration': 'Suma de la durada dels sons no silenciosos del tier phones de MFA. Exclou '
                                         'intervals buits o silenciosos.',
        'hl_help_sound_count': 'Nombre de sons no silenciosos detectats al tier phones del TextGrid de MFA.',
        'hl_help_speech_rate': 'Nombre de sons no silenciosos del tier phones de MFA dividit per la durada del tram de '
                               "parla espontània. S'expressa en sons per segon.",
        'hl_help_articulation_rate': 'Nombre de sons no silenciosos del tier phones de MFA dividit pel temps '
                                     "articulat, és a dir, la suma de durada dels sons no silenciosos. S'expressa en "
                                     'sons per segon.',
        'hl_help_pause_count': 'Nombre de pauses detectades entre paraules alineades. Es compten com a pauses els '
                               "buits superiors al llindar definit a l'script.",
        'hl_help_mean_pause_duration': 'Durada mitjana de les pauses detectades entre paraules.',
        'hl_help_pause_percentage': 'Percentatge del tram de parla espontània ocupat per pauses.',
        'hl_help_long_pauses': "Nombre de pauses llargues. Actualment es consideren llargues les pauses d'1 segon o "
                               'més.',
        'hl_help_f0_mean': 'Mitjana de la freqüència fonamental estimada amb Parselmouth.',
        'hl_help_f0_sd': 'Desviació estàndard de la F0. Aproxima la variabilitat melòdica.',
        'hl_help_f0_range': 'Diferència entre la F0 màxima i la F0 mínima detectades.',
        'hl_help_sentence_count': "Nombre d'oracions detectades automàticament per Stanza a partir de la transcripció "
                                  'de Whisper.',
        'hl_help_mean_sentence_length_words': 'Nombre mitjà de paraules per oració.',
        'hl_help_subordinate_clause_count': 'Nombre aproximat de subordinades detectades amb Stanza mitjançant '
                                            'relacions de dependència com advcl, ccomp, xcomp, acl o csubj. És una '
                                            'mesura automàtica i orientativa.',
        'hl_help_subordinates_per_sentence': "Nombre de subordinades dividit pel nombre total d'oracions.",
        'hl_help_unique_lexical_lemmas': 'Nombre de lemes lèxics diferents. Es compten noms, verbs, adjectius, '
                                         'adverbis i noms propis.',
        'hl_help_lexical_density': 'Percentatge de tokens lèxics respecte del total de tokens analitzats per Stanza.',
        'hl_help_lexical_ttr': 'Type-token ratio lèxic: lemes lèxics diferents dividits pels tokens lèxics totals.',
        'hl_help_lexical_richness_score_1_5': 'RLE significa Riquesa Lèxica Estimada. Es calcula amb les freqüències '
                                              'de Datamuse: 1 indica vocabulari molt freqüent i 5 vocabulari molt poc '
                                              'freqüent. És una mesura experimental, no normativa.',
        'hl_help_lexical_complexity_rare_percent': 'Percentatge de tokens lèxics classificats com a poc freqüents o '
                                                   'molt poc freqüents segons Datamuse.',
        'hl_help_mean_datamuse_frequency_per_million': 'Mitjana ponderada de les freqüències Datamuse dels lemes '
                                                       'lèxics. Si un lema apareix diverses vegades, contribueix '
                                                       'diverses vegades a la mitjana.',
        'hl_norm_missing_file': "No s'ha trobat la taula normativa de parla espontània. {help_text}",
        'hl_norm_missing_measure': 'No hi ha referència normativa per a aquesta mesura. {help_text}',
        'hl_norm_missing_group': 'No hi ha referència per al grup {age_group} / {gender_token}. {help_text}',
        'hl_ref_exact': 'Referència {age_group} / {gender_token}',
        'hl_ref_age_only': 'Referència {age_group}, gènere agregat',
        'hl_ref_gender_only': 'Referència gènere {gender_token}, edat agregada',
        'hl_ref_global': 'Referència global',
        'hl_ref_available': 'Referència provisional disponible',
        'hl_status_below': 'per sota del rang provisional',
        'hl_status_above': 'per sobre del rang provisional',
        'hl_status_inside': 'dins del rang provisional',
        'hl_norm_message': '{ref_txt}: {normal_min}–{normal_max}{unit_txt}. El teu valor està {status}.',
        'hl_norm_n': ' n={n}.',
        'hl_norm_warning': ' Referència provisional: convé ampliar-la amb més controls.',
        'hl_ref_note_fallback': "S'ha utilitzat la referència provisional disponible per a cada mesura. La taula "
                                'normativa actual no conté una referència específica per a {age_group} / '
                                '{gender_token}.',
        'hl_ref_note_group': "S'ha utilitzat la referència disponible per al grup {age_group} / {gender_token}.",
        'hl_global_completed_title': 'Anàlisi de parla espontània completada.',
        'hl_global_no_comparison_body': "No s'ha pogut comparar amb la normalitat perquè no hi ha cap referència "
                                        'disponible per al grup {age_group} / {gender_token}.',
        'hl_global_normal_title': 'Perfil de parla espontània dins del rang provisional.',
        'hl_global_normal_body': 'Les mesures comparables se situen dins del rang de referència. {ref_note} Aquests '
                                 'valors són descriptius i provisionals si el grup normatiu encara té pocs controls.',
        'hl_global_altered_title': "Algunes mesures s'allunyen del rang provisional.",
        'hl_global_altered_body': "Les mesures que més s'aparten de la referència disponible són: {labels}. {ref_note} "
                                  'Interpreta-ho com a cribratge descriptiu, no com a diagnòstic clínic tancat.',
        'hl_table_normative': 'Taula normativa: {filename}.',
        'hl_unit_words': 'paraules',
        'lectura_measure_labels': {
        'total_duration': 'Durada total',
        'speech_rate': 'Speech rate',
        'articulation_rate': 'Articulation rate',
        'pause_count': 'Nombre de pauses',
        'mean_pause_duration': 'Durada mitjana de pausa',
        'pause_percentage': '% temps en pausa',
        'long_pauses': 'Pauses llargues',
        'f0_mean': 'F0 mitjana',
        'f0_sd': 'Variabilitat de F0',
        'f0_range': 'Rang de F0',
        },

        'lectura_norm_missing_file': "No s'ha trobat la taula de normalitat de lectura.",
        'lectura_norm_missing_measure': 'No hi ha rang de normalitat per a aquesta mesura de lectura.',
        'lectura_norm_missing_generic': 'No hi ha cap referència disponible per a aquesta mesura.',
        'lectura_status_below': 'per sota del rang provisional',
        'lectura_status_above': 'per sobre del rang provisional',
        'lectura_status_inside': 'dins del rang provisional',
        'lectura_hover_message': 'Referència global provisional: {normal_min}–{normal_max}{unit_txt}. El teu valor està {status}.',
        'lectura_norm_n': ' n={n}.',
        'lectura_table_note': ' Taula normativa: {filename}.',
        'lectura_not_stratified': ' Referència no estratificada per edat ni gènere.',

        'lectura_global_completed_title': 'Anàlisi de lectura completada.',
        'lectura_global_no_comparison_body': "No s'ha pogut comparar amb la normalitat perquè no s'ha trobat cap referència per a les mesures de lectura.",
        'lectura_global_normal_title': 'Perfil de lectura dins del rang provisional.',
        'lectura_global_normal_body': 'Les mesures comparables se situen dins de la referència global disponible. Aquests rangs són provisionals i no estan estratificats per edat ni gènere.{table_note}',
        'lectura_global_altered_title': "Algunes mesures de lectura s'allunyen del rang provisional.",
        'lectura_global_altered_body': "Les mesures que més s'aparten de la referència global disponible són: {labels}. Interpreta-ho com a cribratge descriptiu, no com a diagnòstic clínic tancat. Aquests rangs són provisionals i no estan estratificats per edat ni gènere.{table_note}",

        'lexical_complexity_not_calculable': 'no calculable',
        'lexical_complexity_rare_comment': 'Lemes poc freqüents o molt poc freqüents: {rare_percent} %.',
        'lexical_complexity_mean_freq_comment': 'Freqüència mitjana Datamuse: {mean_freq} ocurrències per milió.',
        'lexical_complexity_method': (
              'RLE significa Riquesa Lèxica Estimada. És una mesura experimental en escala 1–5: '
              '1 indica vocabulari molt freqüent i 5 indica vocabulari menys freqüent, més marcat '
              'o més singular. Primer s’extreuen els lemes lèxics amb Stanza '
              '(noms, verbs, adjectius, adverbis i noms propis). Després es consulta la freqüència '
              'de cada lema a Datamuse. La versió actual no utilitza una mitjana simple: dona més pes '
              'a la cua lèxica, és a dir, a la presència de lemes poc freqüents o molt poc freqüents. '
              'Això la fa més sensible en textos curts, on poques paraules marcades poden canviar molt '
              'el perfil lèxic. Un valor més alt indica una singularitat lèxica estimada més gran.'
        ),
        'clinical_measure_labels': {
              'mpt': 'MPT o durada',
              'f0_mean_hz': 'F0 mitjana',
              'jitter_pct': 'Jitter',
              'shimmer_pct': 'Shimmer',
              'hnr_db': 'HNR',
              'voice_breaks_percent': 'Interrupcions de la fonació',
              'locally_unvoiced_percent': 'Trams sense sonoritat',
              'h1_h2': 'H1–H2',
              'h1_a1': 'H1–A1',
              },
        'mpt_reduced': "Capacitat de fonació reduïda, compatible amb debilitat vocal.",
        'mpt_slightly_reduced': "Capacitat de fonació lleugerament reduïda.",

        'f0_high_tense': "Veu aguda, compatible amb tensió.",
        'f0_low_weak': "Veu greu, compatible amb debilitat vocal.",
        'jitter_irregular': "Veu tremolosa o irregular.",
        'shimmer_instability': "Inestabilitat en la intensitat.",
        'hnr_noise': "Excés de soroll vocal.",
        'voice_breaks': "Es detecten interrupcions de la fonació.",
        'locally_unvoiced': "Pèrdua de sonoritat en alguns trams.",
        'h1_h2_breathy': "Veu airejada.",
        'h1_h2_tense_hoarse': "Veu tensa o ronca.",
        'h1_a1_nasality': "H1–A1 també s’ha relacionat amb la nasalitat; per això s’ha d’interpretar conjuntament amb la resta de paràmetres.",
        'h1_a1_breathy_air_leak': "Veu airejada, amb escapament d’aire durant la fonació. H1–A1 també s’ha relacionat amb la nasalitat, de manera que no s’ha d’interpretar de manera aïllada.",
        'asos_global_comment_with_findings': (
            "En conjunt, aquests paràmetres descriuen diferents aspectes de la qualitat vocal: "
            "l’estabilitat de la fonació, la quantitat relativa de soroll i la distribució d’energia "
            "entre harmònics i formants. En aquest enregistrament destaquen aquests punts: {findings} "
            "La lectura és orientativa i no constitueix un diagnòstic tancat."
        ),
        'asos_global_comment_no_findings': (
            "En conjunt, les mesures comparables no mostren desviacions rellevants. "
            "Això suggereix una fonació acústicament estable en aquest enregistrament, tot i que "
            "la interpretació continua sent orientativa i depèn de la qualitat de l’àudio."
        ),
        'asos_breathy_pattern_body': (
            "A més, la combinació d’H1–H2 i H1–A1 elevats amb un HNR baix pot ser compatible "
            "amb una veu més aviat airejada (breathy), perquè apunta a més energia relativa en el "
            "primer harmònic i a més component de soroll. Tot i així, no és un criteri determinant "
            "per si sol i cal interpretar-ho amb prudència."
        ),
        'many_flags': "O bé l’enregistrament no és correcte, o bé la qualitat de la teva veu no és idònia.",
        'optimal': "La qualitat de la teva veu és òptima.",
        'no_relevant_alterations': "No s’han detectat alteracions rellevants en els paràmetres analitzats.",
        'f0_mean_with_note': "La teva freqüència mitjana és de {hz} Hz, cosa que equival a {note}.",
        'f0_mean': "La teva freqüència mitjana és de {hz} Hz.",
       },
 'es': {'app_title': 'AcousA - Análisis de voz',
        'page_title': 'AcousA - Análisis de voz',
        'upload_title': 'También puedes subir un archivo de audio',
        'upload_help': 'Puedes subir un archivo de audio (WAV, MP3, etc.) para analizarlo.',
        'upload_label': 'Archivo de audio',
        'record_title': 'Grabar desde el navegador',
        'submit_button': 'Analizar',
        'result_title': 'Resultado del análisis',
        'file_analyzed': 'Archivo analizado:',
        'col_measure': 'Medida',
        'col_value': 'Valor',
        'col_lower': 'Rango mínimo',
        'col_upper': 'Rango máximo',
        'back_link': '⟵ Volver a realizar otro análisis',
        'lang_label': 'Idioma de la interfaz',
        'msg_unsupported': '⚠️ Tu navegador no permite acceder al micrófono. Prueba con un navegador más reciente.',
        'msg_supported': 'Puedes grabar directamente desde el navegador en la mayoría de ordenadores, Android y '
                         'iPhone.',
        'msg_recording': '🔴 Grabando... habla ahora.',
        'msg_processing': 'Procesando grabación...',
        'msg_ready': 'Grabación lista. Ahora puedes pulsar «Analizar». Archivo: {file}',
        'task_label': 'Quiero evaluar mi...',
        'task_result_label': 'Tarea',
        'preinfo_title': 'Antes de grabar',
        'age_label': 'Tu edad',
        'age_placeholder': 'Años',
        'age_help': 'En el futuro adaptaremos los valores de referencia a diferentes grupos de edad.',
        'consent_label': 'Uso de los datos con fines científicos',
        'consent_yes': 'Sí, autorizo que los datos de esta grabación se utilicen de forma anonimizada con fines de '
                       'investigación científica.',
        'consent_no': 'No, prefiero que los datos de esta grabación se utilicen únicamente para mi automonitorización.',
        'consent_info_yes': 'Gracias por tu colaboración.',
        'consent_info_no': 'Tus datos no se utilizarán con fines científicos. Puedes seguir utilizando la aplicación '
                           'solo para tu automonitorización.',
        'task_instructions_label': 'Instrucciones:',
        'msg_audio_quality_fail': 'La grabación no cumple los requisitos mínimos de calidad para el análisis (duración '
                                  'mínima: 3 s; contraste voz–ruido: ≥ 30 dB). Por favor, graba en un entorno '
                                  'silencioso, habla con voz alta y clara y asegúrate de que la grabación dure al '
                                  'menos 3 segundos.',
        'download_csv': 'Descargar CSV',
        'sex_label': 'Sexo / género',
        'sex_male': 'Hombre',
        'sex_female': 'Mujer',
        'sex_nb': 'No binario',
        'sex_other': 'Otro (especificar)',
        'sex_other_specify': 'Especifica',
        'sex_other_placeholder': 'Especifica (opcional si elegiste «Otro»)',
        'sex_help': 'Se usará solo para adaptar valores de referencia por grupos.',
        'interpretation_title': 'Interpretación',
        'interpretation_fallback': 'No se pudo calcular una interpretación automática para este resultado.',
        'pataka_comment_normal': 'Tus resultados están dentro de los valores de normalidad para la velocidad del '
                                 'habla.',
        'pataka_comment_fast': 'Tus resultados sugieren una velocidad del habla más bien rápida (por encima de lo '
                               'habitual).',
        'pataka_comment_slow_or_badrec': 'Tus resultados sugieren una velocidad del habla más bien lenta (por debajo '
                                         'de lo habitual). Si te sorprende, es posible que la grabación no sea óptima '
                                         '(ruido, cortes, distancia al micrófono).',
        'asos_comment_normal': 'Tus resultados (jitter y shimmer) están dentro de los valores de normalidad.',
        'asos_comment_unstable': 'Tus resultados muestran jitter y/o shimmer por encima de lo esperado, lo que suele '
                                 'indicar mayor irregularidad en la vibración de la voz. Si estabas resfriada/o o '
                                 'cansada/o, podría influir.',
        'asos_comment_below': 'Tus resultados muestran jitter y/o shimmer por debajo de lo habitual. No suele ser '
                              'preocupante; a veces refleja una señal muy estable o condiciones de grabación '
                              'especialmente buenas.',
        'plot_title': 'Tus resultados',
        'resources_title': 'Recursos',
        'resources_intro': 'Enlaces útiles para fonetistas y herramientas relacionadas.',
        'back_home': 'Inicio',
        'msg_rec_target': 'Objetivo mínimo recomendado: 10 s',
        'msg_rec_breath_cue': '💨 ¡Coge aire!',
        'msg_rec_silence_auto_stopped': 'Procesando el análisis...',
        'msg_rec_badge_recording': 'Grabando…',
        'msg_rec_badge_complete': '✅ duración suficiente',
        'msg_rec_badge_finished': 'Grabación terminada',
        'msg_rec_error': 'Error: {error}',
        'msg_rec_invalid': 'La grabación no se ha generado correctamente. Vuelve a grabarla.',
        'pataka_not_comparable': 'No se ha podido comparar esta medida con la normalidad.',
        'pataka_speech_rate_high': 'La velocidad articulatoria está muy por encima del rango esperado. Kase.O estaría '
                                   'orgulloso.',
        'pataka_speech_rate_low': 'La velocidad articulatoria aparece reducida respecto al rango de referencia.',
        'pataka_speech_rate_normal': 'La velocidad articulatoria se sitúa dentro del rango esperado.',
        'pataka_percentage_v_normal': 'La proporción vocálica se sitúa dentro de la normalidad.',
        'pataka_percentage_v_low': 'La proporción vocálica aparece reducida respecto al patrón esperado.',
        'pataka_percentage_v_high': 'La proporción vocálica aparece aumentada respecto al patrón esperado.',
        'pataka_temporal_var_normal': 'La variabilidad temporal de este parámetro se sitúa dentro del rango esperado.',
        'pataka_temporal_var_low': 'La variabilidad temporal de este parámetro aparece reducida.',
        'pataka_temporal_var_high': 'La variabilidad temporal de este parámetro aparece aumentada.',
        'pataka_vdist_mean_normal': 'La distancia media entre núcleos vocálicos está dentro del rango esperado.',
        'pataka_vdist_mean_low': 'La distancia media entre núcleos vocálicos aparece reducida.',
        'pataka_vdist_mean_high': 'La distancia media entre núcleos vocálicos aparece aumentada.',
        'pataka_generic_out': 'Este parámetro se desvía del rango de referencia.',
        'pataka_generic_normal': 'Este parámetro se sitúa dentro de la normalidad.',
        'pataka_global_no_comparison_title': 'No se ha podido calcular la comparación con normalidad.',
        'pataka_global_no_comparison_body': 'No había suficientes valores comparables con el archivo de referencia.',
        'pataka_global_normal_title': 'Tu rendimiento articulatorio se sitúa dentro de la normalidad.',
        'pataka_global_normal_body': 'No se observan desviaciones relevantes en los parámetros temporales analizados '
                                     'de la tarea de diadococinesia.',
        'pataka_global_marked_title': 'Se observan alteraciones claras en algunos parámetros de ritmo articulatorio.',
        'pataka_global_marked_body': 'Las desviaciones más llamativas aparecen en {labels}. Esto sugiere un patrón '
                                     'temporal distinto del esperado y conviene interpretarlo junto con la evaluación '
                                     'clínica.',
        'pataka_global_mild_title': 'Se observan desviaciones leves en algunos parámetros de ritmo articulatorio.',
        'pataka_global_mild_body': 'Los parámetros que más se apartan de la referencia son {labels}. El patrón global '
                                   'no es necesariamente patológico, pero sí diferente del grupo normativo.',
        'download_audio': 'Descargar audio',
        'plot_alt': 'Gráfico de comparación con la normalidad',
        'reading_reference_title': 'Texto de lectura',
        'detected_transcript_title': 'Transcripción detectada',
        'msg_habla_libre_slow': 'El análisis de habla libre puede tardar un poco más que las otras tareas, porque '
                                'incluye transcripción automática, generación de TextGrid, alineamiento con Montreal '
                                'Forced Aligner, análisis lingüístico con Stanza y consulta léxica con Datamuse.',
        'automatic_transcription_title': 'Transcripción automática',
        'automatic_transcription_note': 'Transcripción generada automáticamente con Whisper: modelo español mediano.',
        'textgrid_title': 'TextGrid generado con MFA',
        'textgrid_view': 'Ver TextGrid',
        'results_plot_note_habla_libre': 'Barras = rango de referencia provisional. Punto = resultado de la grabación. '
                                         'RLE = riqueza léxica estimada.',
        'measures_guide_title': 'Guía de medidas',
        'measures_guide_intro': 'Despliega cada medida para ver qué significa y cómo se ha calculado.',
        'download_textgrid': 'Descargar TextGrid',
        'download_lemmas_json': 'Descargar lemas JSON',
        'plot_hover_value': 'Valor',
        'plot_hover_scale': 'Escala',
        'results_unavailable': 'Los resultados ya no están disponibles.',
        'hl_unit_sounds_per_second': 'sonidos/s',
        'hl_group_intonation': 'Entonación',
        'hl_group_complejidad_lexica': 'Complejidad léxica',
        'hl_group_complejidad_sintactica': 'Complejidad sintáctica',
        'hl_group_fluencia': 'Fluencia',
        'hl_label_speech_duration': 'Duración',
        'hl_label_articulation_duration': 'Tiempo articulado',
        'hl_label_speech_rate': 'Speech rate',
        'hl_label_articulation_rate': 'Articulation rate',
        'hl_label_pause_count': 'Pausas',
        'hl_label_mean_pause_duration': 'Pausa media',
        'hl_label_pause_percentage': '% pausa',
        'hl_label_f0_mean': 'F0 media',
        'hl_label_f0_sd': 'Variabilidad F0',
        'hl_label_f0_range': 'Rango F0',
        'hl_label_unique_lexical_lemmas': 'Lemas léxicos',
        'hl_label_lexical_density': 'Densidad léxica',
        'hl_label_lexical_ttr': 'TTR léxico',
        'hl_label_lexical_richness_score_1_5': 'RLE 1–5',
        'hl_label_lexical_complexity_rare_percent': '% lemas poco frecuentes',
        'hl_label_mean_datamuse_frequency_per_million': 'Freq. media',
        'hl_label_subordinate_clause_count': 'Subordinadas',
        'hl_label_subordinates_per_sentence': 'Subordinadas/oración',
        'hl_label_long_pauses': 'Pausas largas',
        'hl_label_sentence_count': 'Oraciones',
        'hl_label_mean_sentence_length_words': 'Longitud media oración',
        'hl_label_sound_count': 'Sonidos detectados',
        'hl_help_speech_duration': 'Duración entre la primera y la última palabra alineada. Excluye el silencio '
                                   'inicial y final.',
        'hl_help_articulation_duration': 'Suma de la duración de los sonidos no silenciosos del tier phones de MFA. '
                                         'Excluye intervalos vacíos o silenciosos.',
        'hl_help_sound_count': 'Número de sonidos no silenciosos detectados en el tier phones del TextGrid de MFA.',
        'hl_help_speech_rate': 'Número de sonidos no silenciosos del tier phones de MFA dividido por la duración del '
                               'tramo de habla espontánea. Se expresa en sonidos por segundo.',
        'hl_help_articulation_rate': 'Número de sonidos no silenciosos del tier phones de MFA dividido por el tiempo '
                                     'articulado, es decir, la suma de duración de los sonidos no silenciosos. Se '
                                     'expresa en sonidos por segundo.',
        'hl_help_pause_count': 'Número de pausas detectadas entre palabras alineadas. Se cuentan como pausas los '
                               'huecos superiores al umbral definido en el script.',
        'hl_help_mean_pause_duration': 'Duración media de las pausas detectadas entre palabras.',
        'hl_help_pause_percentage': 'Porcentaje del tramo de habla espontánea ocupado por pausas.',
        'hl_help_long_pauses': 'Número de pausas largas. Actualmente se consideran largas las pausas de 1 segundo o '
                               'más.',
        'hl_help_f0_mean': 'Media de la frecuencia fundamental estimada con Parselmouth.',
        'hl_help_f0_sd': 'Desviación estándar de la F0. Aproxima la variabilidad melódica.',
        'hl_help_f0_range': 'Diferencia entre la F0 máxima y la F0 mínima detectadas.',
        'hl_help_sentence_count': 'Número de oraciones detectadas automáticamente por Stanza a partir de la '
                                  'transcripción de Whisper.',
        'hl_help_mean_sentence_length_words': 'Número medio de palabras por oración.',
        'hl_help_subordinate_clause_count': 'Número aproximado de subordinadas detectadas con Stanza mediante '
                                            'relaciones de dependencia como advcl, ccomp, xcomp, acl o csubj. Es una '
                                            'medida automática y orientativa.',
        'hl_help_subordinates_per_sentence': 'Número de subordinadas dividido por el número total de oraciones.',
        'hl_help_unique_lexical_lemmas': 'Número de lemas léxicos distintos. Se cuentan nombres, verbos, adjetivos, '
                                         'adverbios y nombres propios.',
        'hl_help_lexical_density': 'Porcentaje de tokens léxicos respecto al total de tokens analizados por Stanza.',
        'hl_help_lexical_ttr': 'Type-token ratio léxico: lemas léxicos distintos divididos por tokens léxicos totales.',
        'hl_help_lexical_richness_score_1_5': 'RLE significa Riqueza Léxica Estimada. Se calcula con las frecuencias '
                                              'de Datamuse: 1 indica vocabulario muy frecuente y 5 vocabulario muy '
                                              'poco frecuente. Es una medida experimental, no normativa.',
        'hl_help_lexical_complexity_rare_percent': 'Porcentaje de tokens léxicos clasificados como poco frecuentes o '
                                                   'muy poco frecuentes según Datamuse.',
        'hl_help_mean_datamuse_frequency_per_million': 'Media ponderada de las frecuencias Datamuse de los lemas '
                                                       'léxicos. Si un lema aparece varias veces, contribuye varias '
                                                       'veces a la media.',
        'hl_norm_missing_file': 'No se ha encontrado la tabla normativa de habla espontánea. {help_text}',
        'hl_norm_missing_measure': 'No hay referencia normativa para esta medida. {help_text}',
        'hl_norm_missing_group': 'No hay referencia para el grupo {age_group} / {gender_token}. {help_text}',
        'hl_ref_exact': 'Referencia {age_group} / {gender_token}',
        'hl_ref_age_only': 'Referencia {age_group}, género agregado',
        'hl_ref_gender_only': 'Referencia género {gender_token}, edad agregada',
        'hl_ref_global': 'Referencia global',
        'hl_ref_available': 'Referencia provisional disponible',
        'hl_status_below': 'por debajo del rango provisional',
        'hl_status_above': 'por encima del rango provisional',
        'hl_status_inside': 'dentro del rango provisional',
        'hl_norm_message': '{ref_txt}: {normal_min}–{normal_max}{unit_txt}. Tu valor está {status}.',
        'hl_norm_n': ' n={n}.',
        'hl_norm_warning': ' Referencia provisional: conviene ampliarla con más controles.',
        'hl_ref_note_fallback': 'Se ha usado la referencia provisional disponible para cada medida. La tabla normativa '
                                'actual no contiene una referencia específica para {age_group} / {gender_token}.',
        'hl_ref_note_group': 'Se ha usado la referencia disponible para el grupo {age_group} / {gender_token}.',
        'hl_global_completed_title': 'Análisis de habla espontánea completado.',
        'hl_global_no_comparison_body': 'No se ha podido comparar con normalidad porque no hay referencia disponible '
                                        'para el grupo {age_group} / {gender_token}.',
        'hl_global_normal_title': 'Perfil de habla espontánea dentro del rango provisional.',
        'hl_global_normal_body': 'Las medidas comparables se sitúan dentro del rango de referencia. {ref_note} Estos '
                                 'valores son descriptivos y provisionales si el grupo normativo aún tiene pocos '
                                 'controles.',
        'hl_global_altered_title': 'Algunas medidas se alejan del rango provisional.',
        'hl_global_altered_body': 'Las medidas que más se apartan de la referencia disponible son: {labels}. '
                                  '{ref_note} Interprétalo como cribado descriptivo, no como diagnóstico clínico '
                                  'cerrado.',
        'hl_table_normative': 'Tabla normativa: {filename}.',
        'hl_unit_words': 'palabras',
        'lectura_measure_labels': {
              'total_duration': 'Duración total',
              'speech_rate': 'Speech rate',
              'articulation_rate': 'Articulation rate',
              'pause_count': 'Número de pausas',
              'mean_pause_duration': 'Duración media de pausa',
              'pause_percentage': '% tiempo en pausa',
              'long_pauses': 'Pausas largas',
              'f0_mean': 'F0 media',
              'f0_sd': 'Variabilidad de F0',
              'f0_range': 'Rango de F0',
              },

        'lectura_norm_missing_file': 'No se ha encontrado la tabla de normalidad de lectura.',
        'lectura_norm_missing_measure': 'No hay rango de normalidad para esta medida de lectura.',
        'lectura_norm_missing_generic': 'No hay referencia disponible para esta medida.',
        'lectura_status_below': 'por debajo del rango provisional',
        'lectura_status_above': 'por encima del rango provisional',
        'lectura_status_inside': 'dentro del rango provisional',
        'lectura_hover_message': 'Referencia global provisional: {normal_min}–{normal_max}{unit_txt}. Tu valor está {status}.',
        'lectura_norm_n': ' n={n}.',
        'lectura_table_note': ' Tabla normativa: {filename}.',
        'lectura_not_stratified': ' Referencia no estratificada por edad ni género.',

        'lectura_global_completed_title': 'Análisis de lectura completado.',
        'lectura_global_no_comparison_body': 'No se ha podido comparar con normalidad porque no se ha encontrado una referencia para las medidas de lectura.',
        'lectura_global_normal_title': 'Perfil de lectura dentro del rango provisional.',
        'lectura_global_normal_body': 'Las medidas comparables se sitúan dentro de la referencia global disponible. Estos rangos son provisionales y no están estratificados por edad ni género.{table_note}',
        'lectura_global_altered_title': 'Algunas medidas de lectura se alejan del rango provisional.',
        'lectura_global_altered_body': 'Las medidas que más se apartan de la referencia global disponible son: {labels}. Interprétalo como cribado descriptivo, no como diagnóstico clínico cerrado. Estos rangos son provisionales y no están estratificados por edad ni género.{table_note}',

        'lexical_complexity_not_calculable': 'no calculable',
        'lexical_complexity_rare_comment': 'Lemas poco frecuentes o muy poco frecuentes: {rare_percent} %.',
        'lexical_complexity_mean_freq_comment': 'Frecuencia media Datamuse: {mean_freq} ocurrencias por millón.',
        'lexical_complexity_method': (
              'RLE significa Riqueza Léxica Estimada. Es una medida experimental en escala 1–5: '
              '1 indica vocabulario muy frecuente y 5 indica vocabulario menos frecuente, más marcado '
              'o más singular. Primero se extraen los lemas léxicos con Stanza '
              '(nombres, verbos, adjetivos, adverbios y nombres propios). Después se consulta la frecuencia '
              'de cada lema en Datamuse. La versión actual no usa una media simple: da más peso a la cola '
              'léxica, es decir, a la presencia de lemas poco frecuentes o muy poco frecuentes. Esto la hace '
              'más sensible en textos cortos, donde pocas palabras marcadas pueden cambiar mucho el perfil '
              'léxico. Un valor más alto indica mayor singularidad léxica estimada.'
        ),
        'clinical_measure_labels': {
              'mpt': 'MPT o duración',
              'f0_mean_hz': 'F0 media',
              'jitter_pct': 'Jitter',
              'shimmer_pct': 'Shimmer',
              'hnr_db': 'HNR',
              'voice_breaks_percent': 'Interrupciones de la fonación',
              'locally_unvoiced_percent': 'Tramos sin sonoridad',
              'h1_h2': 'H1–H2',
              'h1_a1': 'H1–A1',
              },
        'mpt_reduced': "Capacidad de fonación reducida, compatible con debilidad vocal.",
        'mpt_slightly_reduced': "Capacidad de fonación ligeramente reducida.",
        'f0_high_tense': "Voz aguda, compatible con tensión.",
        'f0_low_weak': "Voz grave, compatible con debilidad vocal.",
        'jitter_irregular': "Voz temblorosa o irregular.",
        'shimmer_instability': "Inestabilidad en intensidad.",
        'hnr_noise': "Exceso de ruido vocal.",
        'voice_breaks': "Se detectan interrupciones de la fonación.",
        'locally_unvoiced': "Pérdida de sonoridad en algunos tramos.",
        'h1_h2_breathy': "Voz aireada.",
        'h1_h2_tense_hoarse': "Voz tensa o ronca.",
        'h1_a1_nasality': "H1–A1 también se ha relacionado con la nasalidad; por eso conviene interpretarlo junto con el resto de parámetros.",
        'h1_a1_breathy_air_leak': "Voz aireada, con escape de aire durante la fonación. H1–A1 también se ha relacionado con la nasalidad, así que no debe interpretarse de forma aislada.",
        'asos_global_comment_with_findings': (
            "En conjunto, estos parámetros describen distintos aspectos de la calidad vocal: "
            "la estabilidad de la fonación, la cantidad relativa de ruido y la distribución de energía "
            "entre armónicos y formantes. En esta grabación destacan estos puntos: {findings} "
            "La lectura es orientativa y no constituye un diagnóstico cerrado."
        ),
        'asos_global_comment_no_findings': (
            "En conjunto, las medidas comparables no muestran desviaciones relevantes. "
            "Esto sugiere una fonación acústicamente estable en esta grabación, aunque "
            "la interpretación sigue siendo orientativa y depende de la calidad del audio."
        ),
        'asos_breathy_pattern_body': (
            "Además, la combinación de H1–H2 y H1–A1 elevados con un HNR bajo puede ser compatible "
            "con una voz más bien aireada (breathy), porque apunta a más energía relativa en el "
            "primer armónico y a mayor componente de ruido. Aun así, no es un criterio determinante "
            "por sí solo y debe interpretarse con prudencia."
        ),
        'many_flags': "O bien la grabación no es correcta, o bien la calidad de tu voz no es idónea.",
        'optimal': "La calidad de tu voz es óptima.",
        'no_relevant_alterations': "No se han detectado alteraciones relevantes en los parámetros analizados.",
        'f0_mean_with_note': "Tu frecuencia media es de {hz} Hz, lo que equivale a {note}.",
        'f0_mean': "Tu frecuencia media es de {hz} Hz.",
       },
 'en': {'app_title': 'AcousA - Speech analysis',
        'page_title': 'AcousA - Speech analysis',
        'upload_title': 'You can also upload an audio file',
        'upload_help': 'You can upload an audio file (WAV, MP3, etc.) to analyse.',
        'upload_label': 'Audio file',
        'record_title': 'Record in the browser',
        'submit_button': 'Analyse',
        'result_title': 'Analysis result',
        'file_analyzed': 'File analysed:',
        'col_measure': 'Measure',
        'col_value': 'Value',
        'col_lower': 'Lower bound',
        'col_upper': 'Upper bound',
        'back_link': '⟵ Go back and analyse another file',
        'lang_label': 'Interface language',
        'msg_unsupported': '⚠️ Your browser does not allow microphone access. Please try a more recent browser.',
        'msg_supported': 'You can record directly in the browser on most desktops, Android and iPhone.',
        'msg_recording': '🔴 Recording... please speak now.',
        'msg_processing': 'Processing recording...',
        'msg_ready': 'Recording ready. You can now click “Analyse”. File: {file}',
        'task_label': 'I want to assess my...',
        'task_result_label': 'Task',
        'preinfo_title': 'Before recording',
        'age_label': 'Your age',
        'age_placeholder': 'Age',
        'age_help': 'In the future we will adapt the reference values to different age groups.',
        'consent_label': 'Use of your data for scientific research',
        'consent_yes': 'Yes, I authorise the anonymised use of this recording for scientific research purposes.',
        'consent_no': 'No, I prefer my data to be used only for self-monitoring.',
        'consent_info_yes': 'Thank you for your collaboration.',
        'consent_info_no': 'Your data will not be used for scientific research. You can continue using the application '
                           'only for your own self-monitoring.',
        'task_instructions_label': 'Instructions:',
        'msg_audio_quality_fail': 'The recording does not meet the minimum quality requirements for analysis (minimum '
                                  'duration: 3 s; voice-to-noise contrast: ≥ 30 dB). Please record in a quiet '
                                  'environment, speak clearly and loudly, and make sure the recording is at least 3 '
                                  'seconds long.',
        'download_csv': 'Download CSV',
        'sex_label': 'Sex / gender',
        'sex_male': 'Male',
        'sex_female': 'Female',
        'sex_nb': 'Non-binary',
        'sex_other': 'Other (specify)',
        'sex_other_specify': 'Specify',
        'sex_other_placeholder': 'Specify (if you selected “Other”)',
        'sex_help': 'Used only to adapt reference values by groups.',
        'interpretation_title': 'Interpretation',
        'interpretation_fallback': 'An automatic interpretation could not be computed for this result.',
        'pataka_comment_normal': 'Your result is within the typical (normal) range for speech rate.',
        'pataka_comment_fast': 'Your result suggests a rather fast speech rate (above the typical range).',
        'pataka_comment_slow_or_badrec': 'Your result suggests a rather slow speech rate (below the typical range). If '
                                         'this surprises you, the recording quality might not be optimal (noise, cuts, '
                                         'microphone distance).',
        'asos_comment_normal': 'Your results (jitter and shimmer) are within typical (normal) ranges.',
        'asos_comment_unstable': 'Your results show jitter and/or shimmer above the expected range, which often '
                                 'indicates more irregular vocal fold vibration. Fatigue or a cold can influence this.',
        'asos_comment_below': 'Your results show jitter and/or shimmer below the typical range. This is usually not '
                              'concerning and may reflect a very stable signal or excellent recording conditions.',
        'plot_title': 'Your results',
        'resources_title': 'Resources',
        'resources_intro': 'Useful links for phoneticians and related tools.',
        'back_home': 'Home',
        'msg_rec_target': 'Recommended minimum target: 10 s',
        'msg_rec_breath_cue': '💨 Take a breath!',
        'msg_rec_silence_auto_stopped': 'Processing analysis...',
        'msg_rec_badge_recording': 'Recording…',
        'msg_rec_badge_complete': '✅ sufficient duration',
        'msg_rec_badge_finished': 'Recording finished',
        'msg_rec_error': 'Error: {error}',
        'msg_rec_invalid': 'The recording was not generated correctly. Please record it again.',
        'pataka_not_comparable': 'This measure could not be compared with the normative reference.',
        'pataka_speech_rate_high': 'Articulatory rate is far above the expected range. Kendrick Lamar would be proud.',
        'pataka_speech_rate_low': 'Articulatory rate appears reduced compared with the reference range.',
        'pataka_speech_rate_normal': 'Articulatory rate falls within the expected range.',
        'pataka_percentage_v_normal': 'Vocalic proportion falls within the normal range.',
        'pataka_percentage_v_low': 'Vocalic proportion appears reduced compared with the expected pattern.',
        'pataka_percentage_v_high': 'Vocalic proportion appears increased compared with the expected pattern.',
        'pataka_temporal_var_normal': 'The temporal variability of this parameter falls within the expected range.',
        'pataka_temporal_var_low': 'The temporal variability of this parameter appears reduced.',
        'pataka_temporal_var_high': 'The temporal variability of this parameter appears increased.',
        'pataka_vdist_mean_normal': 'The mean distance between vowel nuclei falls within the expected range.',
        'pataka_vdist_mean_low': 'The mean distance between vowel nuclei appears reduced.',
        'pataka_vdist_mean_high': 'The mean distance between vowel nuclei appears increased.',
        'pataka_generic_out': 'This parameter deviates from the reference range.',
        'pataka_generic_normal': 'This parameter falls within the normal range.',
        'pataka_global_no_comparison_title': 'Comparison with the normative reference could not be calculated.',
        'pataka_global_no_comparison_body': 'There were not enough comparable values in the reference file.',
        'pataka_global_normal_title': 'Your articulatory performance falls within the normal range.',
        'pataka_global_normal_body': 'No relevant deviations were observed in the temporal parameters analysed in the '
                                     'diadochokinesis task.',
        'pataka_global_marked_title': 'Clear alterations are observed in some articulatory rhythm parameters.',
        'pataka_global_marked_body': 'The most striking deviations appear in {labels}. This suggests a temporal '
                                     'pattern that differs from the expected one and should be interpreted together '
                                     'with the clinical evaluation.',
        'pataka_global_mild_title': 'Mild deviations are observed in some articulatory rhythm parameters.',
        'pataka_global_mild_body': 'The parameters that deviate most from the reference are {labels}. The overall '
                                   'pattern is not necessarily pathological, but it does differ from the normative '
                                   'group.',
        'download_audio': 'Download audio',
        'plot_alt': 'Normality comparison plot',
        'reading_reference_title': 'Reading text',
        'detected_transcript_title': 'Detected transcript',
        'msg_habla_libre_slow': 'Free-speech analysis may take a little longer than other tasks because it includes '
                                'automatic transcription, TextGrid generation, Montreal Forced Aligner alignment, '
                                'linguistic analysis with Stanza and lexical lookup with Datamuse.',
        'automatic_transcription_title': 'Automatic transcription',
        'automatic_transcription_note': 'Transcription automatically generated with Whisper: medium Spanish model.',
        'textgrid_title': 'TextGrid generated with MFA',
        'textgrid_view': 'View TextGrid',
        'results_plot_note_habla_libre': 'Bars = provisional reference range. Dot = recording result. RLE = estimated '
                                         'lexical richness.',
        'measures_guide_title': 'Measure guide',
        'measures_guide_intro': 'Open each measure to see what it means and how it was calculated.',
        'download_textgrid': 'Download TextGrid',
        'download_lemmas_json': 'Download lemmas JSON',
        'plot_hover_value': 'Value',
        'plot_hover_scale': 'Scale',
        'results_unavailable': 'The results are no longer available.',
        'hl_unit_sounds_per_second': 'sounds/s',
        'hl_group_intonation': 'Intonation',
        'hl_group_complejidad_lexica': 'Lexical complexity',
        'hl_group_complejidad_sintactica': 'Syntactic complexity',
        'hl_group_fluencia': 'Fluency',
        'hl_label_speech_duration': 'Duration',
        'hl_label_articulation_duration': 'Articulated time',
        'hl_label_speech_rate': 'Speech rate',
        'hl_label_articulation_rate': 'Articulation rate',
        'hl_label_pause_count': 'Pauses',
        'hl_label_mean_pause_duration': 'Mean pause',
        'hl_label_pause_percentage': '% pause',
        'hl_label_f0_mean': 'Mean F0',
        'hl_label_f0_sd': 'F0 variability',
        'hl_label_f0_range': 'F0 range',
        'hl_label_unique_lexical_lemmas': 'Lexical lemmas',
        'hl_label_lexical_density': 'Lexical density',
        'hl_label_lexical_ttr': 'Lexical TTR',
        'hl_label_lexical_richness_score_1_5': 'RLE 1–5',
        'hl_label_lexical_complexity_rare_percent': '% low-frequency lemmas',
        'hl_label_mean_datamuse_frequency_per_million': 'Mean frequency',
        'hl_label_subordinate_clause_count': 'Subordinate clauses',
        'hl_label_subordinates_per_sentence': 'Subordinates/sentence',
        'hl_label_long_pauses': 'Long pauses',
        'hl_label_sentence_count': 'Sentences',
        'hl_label_mean_sentence_length_words': 'Mean sentence length',
        'hl_label_sound_count': 'Detected sounds',
        'hl_help_speech_duration': 'Duration between the first and last aligned word. Initial and final silence are '
                                   'excluded.',
        'hl_help_articulation_duration': 'Sum of the duration of non-silent sounds in the MFA phones tier. Empty or '
                                         'silent intervals are excluded.',
        'hl_help_sound_count': 'Number of non-silent sounds detected in the MFA TextGrid phones tier.',
        'hl_help_speech_rate': 'Number of non-silent sounds in the MFA phones tier divided by the duration of the '
                               'spontaneous-speech segment. Expressed as sounds per second.',
        'hl_help_articulation_rate': 'Number of non-silent sounds in the MFA phones tier divided by articulated time, '
                                     'that is, the summed duration of non-silent sounds. Expressed as sounds per '
                                     'second.',
        'hl_help_pause_count': 'Number of pauses detected between aligned words. Gaps above the threshold defined in '
                               'the script are counted as pauses.',
        'hl_help_mean_pause_duration': 'Mean duration of the pauses detected between words.',
        'hl_help_pause_percentage': 'Percentage of the spontaneous-speech segment occupied by pauses.',
        'hl_help_long_pauses': 'Number of long pauses. Pauses of 1 second or more are currently considered long.',
        'hl_help_f0_mean': 'Mean fundamental frequency estimated with Parselmouth.',
        'hl_help_f0_sd': 'Standard deviation of F0. It approximates melodic variability.',
        'hl_help_f0_range': 'Difference between the maximum and minimum detected F0.',
        'hl_help_sentence_count': 'Number of sentences automatically detected by Stanza from the Whisper '
                                  'transcription.',
        'hl_help_mean_sentence_length_words': 'Mean number of words per sentence.',
        'hl_help_subordinate_clause_count': 'Approximate number of subordinate clauses detected with Stanza using '
                                            'dependency relations such as advcl, ccomp, xcomp, acl or csubj. This is '
                                            'an automatic and indicative measure.',
        'hl_help_subordinates_per_sentence': 'Number of subordinate clauses divided by the total number of sentences.',
        'hl_help_unique_lexical_lemmas': 'Number of distinct lexical lemmas. Nouns, verbs, adjectives, adverbs and '
                                         'proper nouns are counted.',
        'hl_help_lexical_density': 'Percentage of lexical tokens relative to all tokens analysed by Stanza.',
        'hl_help_lexical_ttr': 'Lexical type-token ratio: distinct lexical lemmas divided by total lexical tokens.',
        'hl_help_lexical_richness_score_1_5': 'RLE means Estimated Lexical Richness. It is calculated from Datamuse '
                                              'frequencies: 1 indicates very frequent vocabulary and 5 very '
                                              'low-frequency vocabulary. It is an experimental, non-normative measure.',
        'hl_help_lexical_complexity_rare_percent': 'Percentage of lexical tokens classified as low-frequency or very '
                                                   'low-frequency according to Datamuse.',
        'hl_help_mean_datamuse_frequency_per_million': 'Weighted mean of the Datamuse frequencies of lexical lemmas. '
                                                       'If a lemma appears several times, it contributes several times '
                                                       'to the mean.',
        'hl_norm_missing_file': 'The spontaneous-speech normative table was not found. {help_text}',
        'hl_norm_missing_measure': 'There is no normative reference for this measure. {help_text}',
        'hl_norm_missing_group': 'There is no reference for group {age_group} / {gender_token}. {help_text}',
        'hl_ref_exact': 'Reference {age_group} / {gender_token}',
        'hl_ref_age_only': 'Reference {age_group}, aggregated gender',
        'hl_ref_gender_only': 'Reference gender {gender_token}, aggregated age',
        'hl_ref_global': 'Global reference',
        'hl_ref_available': 'Available provisional reference',
        'hl_status_below': 'below the provisional range',
        'hl_status_above': 'above the provisional range',
        'hl_status_inside': 'within the provisional range',
        'hl_norm_message': '{ref_txt}: {normal_min}–{normal_max}{unit_txt}. Your value is {status}.',
        'hl_norm_n': ' n={n}.',
        'hl_norm_warning': ' Provisional reference: it should be expanded with more controls.',
        'hl_ref_note_fallback': 'The available provisional reference has been used for each measure. The current '
                                'normative table does not contain a specific reference for {age_group} / '
                                '{gender_token}.',
        'hl_ref_note_group': 'The available reference for group {age_group} / {gender_token} has been used.',
        'hl_global_completed_title': 'Spontaneous-speech analysis completed.',
        'hl_global_no_comparison_body': 'Comparison with normality was not possible because no reference is available '
                                        'for group {age_group} / {gender_token}.',
        'hl_global_normal_title': 'Spontaneous-speech profile within the provisional range.',
        'hl_global_normal_body': 'The comparable measures fall within the reference range. {ref_note} These values are '
                                 'descriptive and provisional if the normative group still has few controls.',
        'hl_global_altered_title': 'Some measures fall outside the provisional range.',
        'hl_global_altered_body': 'The measures that deviate most from the available reference are: {labels}. '
                                  '{ref_note} Interpret this as descriptive screening, not as a definitive clinical '
                                  'diagnosis.',
        'hl_table_normative': 'Normative table: {filename}.',
        'hl_unit_words': 'words',
        'lectura_measure_labels': {
              'total_duration': 'Total duration',
              'speech_rate': 'Speech rate',
              'articulation_rate': 'Articulation rate',
              'pause_count': 'Number of pauses',
              'mean_pause_duration': 'Mean pause duration',
              'pause_percentage': '% time in pauses',
              'long_pauses': 'Long pauses',
              'f0_mean': 'Mean F0',
              'f0_sd': 'F0 variability',
              'f0_range': 'F0 range',
              },

        'lectura_norm_missing_file': 'The reading normality table was not found.',
        'lectura_norm_missing_measure': 'There is no normality range for this reading measure.',
        'lectura_norm_missing_generic': 'No reference is available for this measure.',
        'lectura_status_below': 'below the provisional range',
        'lectura_status_above': 'above the provisional range',
        'lectura_status_inside': 'within the provisional range',
        'lectura_hover_message': 'Provisional global reference: {normal_min}–{normal_max}{unit_txt}. Your value is {status}.',
        'lectura_norm_n': ' n={n}.',
        'lectura_table_note': ' Normative table: {filename}.',
        'lectura_not_stratified': ' Reference not stratified by age or gender.',

        'lectura_global_completed_title': 'Reading analysis completed.',
        'lectura_global_no_comparison_body': 'Comparison with normality was not possible because no reference was found for the reading measures.',
        'lectura_global_normal_title': 'Reading profile within the provisional range.',
        'lectura_global_normal_body': 'The comparable measures fall within the available global reference. These ranges are provisional and are not stratified by age or gender.{table_note}',
        'lectura_global_altered_title': 'Some reading measures fall outside the provisional range.',
        'lectura_global_altered_body': 'The measures that deviate most from the available global reference are: {labels}. Interpret this as descriptive screening, not as a definitive clinical diagnosis. These ranges are provisional and are not stratified by age or gender.{table_note}',

        'lexical_complexity_not_calculable': 'not computable',
        'lexical_complexity_rare_comment': 'Low-frequency or very low-frequency lemmas: {rare_percent} %.',
        'lexical_complexity_mean_freq_comment': 'Mean Datamuse frequency: {mean_freq} occurrences per million.',
        'lexical_complexity_method': (
              'RLE stands for Estimated Lexical Richness. It is an experimental measure on a 1–5 scale: '
              '1 indicates very frequent vocabulary and 5 indicates less frequent, more marked '
              'or more distinctive vocabulary. First, lexical lemmas are extracted with Stanza '
              '(nouns, verbs, adjectives, adverbs and proper nouns). Then the frequency of each lemma '
              'is queried in Datamuse. The current version does not use a simple mean: it gives more weight '
              'to the lexical tail, that is, to the presence of low-frequency or very low-frequency lemmas. '
              'This makes it more sensitive in short texts, where a few marked words can substantially change '
              'the lexical profile. A higher value indicates greater estimated lexical distinctiveness.'
        ),
        'clinical_measure_labels': {
              'mpt': 'MPT or duration',
              'f0_mean_hz': 'F0 mean',
              'jitter_pct': 'Jitter',
              'shimmer_pct': 'Shimmer',
              'hnr_db': 'HNR',
              'voice_breaks_percent': 'Voice breaks',
              'locally_unvoiced_percent': 'Locally unvoiced',
              'h1_h2': 'H1–H2',
              'h1_a1': 'H1–A1',
              },
        'mpt_reduced': "Reduced phonation capacity, compatible with vocal weakness.",
        'mpt_slightly_reduced': "Slightly reduced phonation capacity.",
        'f0_high_tense': "High-pitched voice, compatible with vocal tension.",
        'f0_low_weak': "Low-pitched voice, compatible with vocal weakness.",
        'jitter_irregular': "Tremulous or irregular voice.",
        'shimmer_instability': "Instability in intensity.",
        'hnr_noise': "Excess vocal noise.",
        'voice_breaks': "Phonation breaks are detected.",
        'locally_unvoiced': "Loss of voicing in some segments.",
        'h1_h2_breathy': "Breathy voice.",
        'h1_h2_tense_hoarse': "Tense or hoarse voice.",
        'h1_a1_nasality': "H1–A1 has also been related to nasality, so it should be interpreted together with the other parameters.",
        'h1_a1_breathy_air_leak': "Breathy voice, with air leakage during phonation. H1–A1 has also been related to nasality, so it should not be interpreted in isolation.",
        'asos_global_comment_with_findings': (
            "Overall, these parameters describe different aspects of voice quality: "
            "phonatory stability, the relative amount of noise and the distribution of energy "
            "across harmonics and formants. In this recording, the following points stand out: {findings} "
            "This interpretation is indicative and does not constitute a definitive diagnosis."
        ),
        'asos_global_comment_no_findings': (
            "Overall, the comparable measures do not show relevant deviations. "
            "This suggests acoustically stable phonation in this recording, although "
            "the interpretation remains indicative and depends on the quality of the audio."
        ),
        'asos_breathy_pattern_body': (
            "In addition, the combination of high H1–H2 and H1–A1 with low HNR may be compatible "
            "with a rather breathy voice, because it points to relatively greater first-harmonic energy "
            "and a larger noise component. However, this is not a determining criterion on its own "
            "and should be interpreted with caution."
        ),
        'many_flags': "Either the recording is not suitable, or your voice quality is not optimal.",
        'optimal': "Your voice quality is optimal.",
        'no_relevant_alterations': "No relevant alterations were detected in the analysed parameters.",
        'f0_mean_with_note': "Your mean frequency is {hz} Hz, which corresponds to {note}.",
        'f0_mean': "Your mean frequency is {hz} Hz.",
        
       }}


def get_texts(lang: str):
    if lang not in LANG_TEXTS:
        lang = DEFAULT_LANG
    return LANG_TEXTS[lang], lang
