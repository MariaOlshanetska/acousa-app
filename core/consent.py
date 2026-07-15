from core.texts import DEFAULT_LANG


CONSENT_PAGES = {
    "ca": {
        "science": {
            "page_title": "Informació sobre protecció de dades personals",
            "app_title": "AcousA - Ús de les dades amb finalitats científiques",
            "back_label": "Tornar a l'aplicació",
            "intro": [
                "La veu és una dada personal i, segons el contingut de l'enregistrament o el context d'ús, pot aportar informació sensible. Per això, l'aplicació aplica mesures de minimització, seudonimització, accés restringit i processament local."
            ],
            "sections": [
                {
                    "title": "Responsable del tractament",
                    "paragraphs": [
                        "Les dades personals recollides a través d'aquesta aplicació seran tractades per la Universitat de Barcelona (UB), a través del Laboratori de Fonètica.",
                        "Per a qualsevol consulta relacionada amb el tractament de les dades o amb l'exercici dels teus drets, pots escriure al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "També pots contactar amb el Delegat/da de Protecció de Dades de la Universitat de Barcelona a l'adreça protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "Quines dades es recullen?",
                    "paragraphs": [
                        "L'aplicació pot recollir les dades mínimes necessàries per dur a terme l'anàlisi: edat, sexe/gènere, especificació de gènere si s'ha indicat, tasca seleccionada, enregistrament de veu o fitxer d'àudio pujat, mesures acústiques i lingüístiques derivades de l'anàlisi, data de l'anàlisi i informació tècnica bàsica del navegador o dispositiu.",
                        "No es demanen nom, cognoms, DNI, adreça postal ni altres identificadors directes. Els fitxers es nomenen amb codis interns per reduir el risc d'identificació directa."
                    ]
                },
                {
                    "title": "Finalitat del tractament",
                    "paragraphs": [
                        "La finalitat principal és permetre la gravació, el processament automàtic i l'anàlisi de mostres de parla en el marc d'un projecte de recerca en fonètica clínica i tecnologies de la parla.",
                        "Les gravacions de veu i les dades derivades del seu anàlisi es podran utilitzar per als objectius científics del projecte, per a la verificació dels resultats, per a anàlisis estadístiques i per a la difusió científica dels resultats obtinguts.",
                        "Els resultats es tractaran de manera seudonimitzada o anonimitzada quan correspongui. En publicacions, congressos o materials de difusió científica no s'inclouran dades que permetin identificar directament les persones participants."
                    ]
                },
                {
                    "title": "Base jurídica i normativa aplicable",
                    "paragraphs": [
                        "La base jurídica del tractament per a finalitats de recerca és el consentiment de la persona participant.",
                        "El tractament es farà d'acord amb el Reglament (UE) 2016/679, Reglament General de Protecció de Dades (RGPD), i amb la Llei orgànica 3/2018, de protecció de dades personals i garantia dels drets digitals (LOPDGDD).",
                        "El tractament seguirà el principi de minimització de dades: només es recollirà la informació estrictament necessària per assolir els objectius científics del projecte.",
                        "Si la persona participant és menor d'edat o no pot prestar consentiment per si mateixa, l'ús de l'aplicació amb finalitats de recerca requereix l'autorització de la persona representant legal quan correspongui."
                    ]
                },
                {
                    "title": "Procediment d'anàlisi de les dades",
                    "paragraphs": [
                        "Segons la tasca seleccionada, les mostres de veu poden ser analitzades mitjançant Praat, R, scripts en Python i models de reconeixement automàtic de la parla basats en Whisper.",
                        "El processament es farà en servidors o equips locals gestionats per la Universitat de Barcelona o pel Laboratori de Fonètica.",
                        "No s'enviaran les gravacions a serveis comercials externs ni a plataformes públiques al núvol per al seu processament. Els proveïdors del programari utilitzat no tindran accés a les gravacions."
                    ]
                },
                {
                    "title": "Emmagatzematge i seguretat",
                    "paragraphs": [
                        "Les dades es conservaran en infraestructures informàtiques ubicades en l'entorn de la Universitat de Barcelona i protegides amb mesures de seguretat institucionals, incloent-hi accés restringit amb credencials personals, control d'accessos i protecció mitjançant tallafocs.",
                        "Només hi podrà accedir el personal investigador o tècnic autoritzat vinculat al projecte, subjecte a obligacions de confidencialitat.",
                        "S'aplicaran mesures tècniques i organitzatives per garantir la confidencialitat, integritat i disponibilitat de la informació. Qualsevol transferència fora de l'entorn segur requerirà autorització prèvia de l'investigador/a principal i l'ús de sistemes de xifrat adequats.",
                        "Es podran fer còpies de seguretat en sistemes locals protegits per garantir la recuperació de la informació en cas d'incidència o pèrdua accidental."
                    ]
                },
                {
                    "title": "Conservació de les dades",
                    "paragraphs": [
                        "Les gravacions originals de veu es podran conservar durant un període màxim de cinc anys des de la finalització del projecte de recerca, amb la finalitat de permetre la verificació i la difusió científica dels resultats.",
                        "Les dades derivades de l'anàlisi, com ara mesures acústiques o variables lingüístiques, es podran conservar durant períodes més prolongats amb finalitats científiques, sempre que estiguin adequadament seudonimitzades o anonimitzades."
                    ]
                },
                {
                    "title": "Compartició i publicació de dades",
                    "paragraphs": [
                        "Les dades derivades de l'anàlisi es podran compartir amb membres de l'equip investigador i amb institucions col·laboradores únicament per a finalitats científiques relacionades amb el projecte.",
                        "Els conjunts de dades que es facin públics en el marc de polítiques de ciència oberta es prepararan prèviament per evitar la identificació directa de les persones participants. No es publicaran enregistraments de veu identificables.",
                        "Les dades anonimitzades o agregades es podran dipositar en repositoris institucionals de recerca, com ara CORA. Repositori de Dades de Recerca, per afavorir la reproductibilitat i la reutilització científica.",
                        "El programari desenvolupat en el marc del projecte es podrà difondre mitjançant llicències obertes amb finalitats científiques i acadèmiques."
                    ]
                },
                {
                    "title": "Drets de les persones participants",
                    "paragraphs": [
                        "Pots exercir en qualsevol moment els drets d'accés, rectificació, supressió, oposició, limitació del tractament, portabilitat i, si escau, el dret a no ser objecte de decisions automatitzades, escrivint al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "També pots contactar amb el Delegat/da de Protecció de Dades de la UB a protecciodedades@ub.edu.",
                        "Si consideres que el tractament de les teves dades no s'ajusta a la normativa vigent, tens dret a presentar una reclamació davant l'autoritat de control competent."
                    ]
                }
            ],
            "disclaimer": "Aquest text és una proposta informativa per a l'aplicació i convé que sigui revisat pel Delegat/da de Protecció de Dades o pel comitè/òrgan responsable del projecte abans de publicar-lo."
        },
        "self_monitoring": {
            "page_title": "Informació sobre protecció de dades personals",
            "app_title": "AcousA - Ús només per a automonitorització",
            "back_label": "Tornar a l'aplicació",
            "intro": [
                "En aquest mode, l'aplicació processa la mostra de veu únicament per generar els resultats sol·licitats per la persona usuària. Les dades no s'incorporen a bases de dades de recerca."
            ],
            "sections": [
                {
                    "title": "Responsable del tractament",
                    "paragraphs": [
                        "Les dades personals recollides a través d'aquesta aplicació seran tractades per la Universitat de Barcelona (UB), a través del Laboratori de Fonètica.",
                        "Per a qualsevol consulta relacionada amb el tractament de les dades o amb l'exercici dels teus drets, pots escriure al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "També pots contactar amb el Delegat/da de Protecció de Dades de la Universitat de Barcelona a l'adreça protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "Quines dades es recullen?",
                    "paragraphs": [
                        "L'aplicació pot recollir les dades mínimes necessàries per prestar el servei sol·licitat: edat, sexe/gènere, especificació de gènere si s'ha indicat, tasca seleccionada, enregistrament de veu o fitxer d'àudio pujat, mesures derivades de l'anàlisi i informació tècnica bàsica del navegador o dispositiu.",
                        "No es demanen nom, cognoms, DNI, adreça postal ni altres identificadors directes."
                    ]
                },
                {
                    "title": "Finalitat del tractament",
                    "paragraphs": [
                        "La finalitat del tractament és processar automàticament la mostra de parla i generar els resultats sol·licitats per la persona usuària.",
                        "Les gravacions de veu no s'utilitzaran amb finalitats de recerca, docència, publicacions, entrenament de models d'intel·ligència artificial ni per a cap altre ús diferent del processament sol·licitat.",
                        "Els resultats obtinguts es mostren a la persona usuària com a informació d'automonitorització i no constitueixen un diagnòstic clínic."
                    ]
                },
                {
                    "title": "Base jurídica i normativa aplicable",
                    "paragraphs": [
                        "El tractament necessari per generar els resultats sol·licitats es basa en la petició expressa de la persona usuària i es limita al temps i a les dades necessàries per prestar aquest servei.",
                        "El tractament es farà d'acord amb el Reglament (UE) 2016/679, Reglament General de Protecció de Dades (RGPD), i amb la Llei orgànica 3/2018, de protecció de dades personals i garantia dels drets digitals (LOPDGDD).",
                        "El tractament seguirà el principi de minimització de dades: només es recollirà la informació estrictament necessària per completar el processament sol·licitat."
                    ]
                },
                {
                    "title": "Procediment d'anàlisi de les dades",
                    "paragraphs": [
                        "Les gravacions de veu s'envien exclusivament a servidors gestionats per la Universitat de Barcelona per al seu processament automàtic.",
                        "Segons la tasca seleccionada, el processament pot fer-se mitjançant Praat, R, scripts en Python i models de reconeixement automàtic de la parla basats en Whisper.",
                        "Tot el processament es farà en infraestructures locals o pròpies de la Universitat de Barcelona. No s'utilitzaran serveis externs ni plataformes comercials al núvol, i tercers aliens a la Universitat de Barcelona no tindran accés a les gravacions."
                    ]
                },
                {
                    "title": "Emmagatzematge i seguretat",
                    "paragraphs": [
                        "Les gravacions de veu i els fitxers intermedis es conservaran temporalment només durant el temps necessari per completar el processament i generar els resultats.",
                        "Durant aquest temps, els fitxers estaran en servidors protegits mitjançant mesures de seguretat institucionals, incloent-hi sistemes d'autenticació, control d'accés i protecció mitjançant tallafocs.",
                        "L'accés estarà restringit exclusivament al personal tècnic o investigador autoritzat de la Universitat de Barcelona, subjecte a obligacions de confidencialitat.",
                        "No s'utilitzaran serveis de núvol públic o de tercers per a l'emmagatzematge o processament de les gravacions."
                    ]
                },
                {
                    "title": "Conservació de les dades",
                    "paragraphs": [
                        "Les gravacions de veu i els fitxers intermedis es conservaran únicament durant el temps estrictament necessari per completar el processament sol·licitat i generar els resultats.",
                        "Un cop finalitzat el processament, els fitxers d'àudio i els fitxers intermedis s'eliminaran automàticament del sistema.",
                        "No es faran còpies de seguretat de les gravacions de veu ni es conservaran arxius d'àudio en bases de dades de recerca quan no s'hagi donat consentiment per a recerca."
                    ]
                },
                {
                    "title": "Cessió i comunicació de dades",
                    "paragraphs": [
                        "Les gravacions de veu no seran cedides a tercers ni compartides amb altres entitats.",
                        "Les gravacions no s'incorporaran a bases de dades de recerca ni s'utilitzaran per a l'entrenament, millora o validació de sistemes d'intel·ligència artificial.",
                        "No es publicaran dades individuals derivades d'aquest ús d'automonitorització."
                    ]
                },
                {
                    "title": "Drets de les persones usuàries",
                    "paragraphs": [
                        "Pots exercir en qualsevol moment els drets d'accés, rectificació, supressió, oposició, limitació del tractament, portabilitat i, si escau, el dret a no ser objecte de decisions automatitzades, escrivint al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "També pots contactar amb el Delegat/da de Protecció de Dades de la UB a protecciodedades@ub.edu.",
                        "Si consideres que el tractament de les teves dades no s'ajusta a la normativa vigent, tens dret a presentar una reclamació davant l'autoritat de control competent."
                    ]
                }
            ],
            "disclaimer": "Aquest text és una proposta informativa per a l'aplicació i convé que sigui revisat pel Delegat/da de Protecció de Dades o pel comitè/òrgan responsable del projecte abans de publicar-lo."
        }
    },
    "es": {
        "science": {
            "page_title": "Información sobre protección de datos personales",
            "app_title": "AcousA - Uso de los datos con fines científicos",
            "back_label": "Volver a la aplicación",
            "intro": [
                "La voz es un dato personal y, según el contenido de la grabación o el contexto de uso, puede aportar información sensible. Por eso, la aplicación aplica medidas de minimización, seudonimización, acceso restringido y procesamiento local."
            ],
            "sections": [
                {
                    "title": "Responsable del tratamiento",
                    "paragraphs": [
                        "Los datos personales recogidos a través de esta aplicación serán tratados por la Universitat de Barcelona (UB), a través del Laboratori de Fonètica.",
                        "Para cualquier consulta relacionada con el tratamiento de los datos o con el ejercicio de tus derechos, puedes escribir al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "También puedes contactar con el Delegado/a de Protección de Datos de la Universitat de Barcelona en la dirección protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "¿Qué datos se recogen?",
                    "paragraphs": [
                        "La aplicación puede recoger los datos mínimos necesarios para realizar el análisis: edad, sexo/género, especificación de género si se ha indicado, tarea seleccionada, grabación de voz o archivo de audio subido, medidas acústicas y lingüísticas derivadas del análisis, fecha del análisis e información técnica básica del navegador o dispositivo.",
                        "No se solicitan nombre, apellidos, DNI, dirección postal ni otros identificadores directos. Los archivos se nombran mediante códigos internos para reducir el riesgo de identificación directa."
                    ]
                },
                {
                    "title": "Finalidad del tratamiento",
                    "paragraphs": [
                        "La finalidad principal es permitir la grabación, el procesamiento automático y el análisis de muestras de habla en el marco de un proyecto de investigación en fonética clínica y tecnologías del habla.",
                        "Las grabaciones de voz y los datos derivados de su análisis podrán utilizarse para los objetivos científicos del proyecto, para la verificación de los resultados, para análisis estadísticos y para la difusión científica de los resultados obtenidos.",
                        "Los resultados se tratarán de forma seudonimizada o anonimizada cuando corresponda. En publicaciones, congresos o materiales de difusión científica no se incluirán datos que permitan identificar directamente a las personas participantes."
                    ]
                },
                {
                    "title": "Base jurídica y normativa aplicable",
                    "paragraphs": [
                        "La base jurídica del tratamiento con fines de investigación es el consentimiento de la persona participante.",
                        "El tratamiento se realizará de acuerdo con el Reglamento (UE) 2016/679, Reglamento General de Protección de Datos (RGPD), y con la Ley Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).",
                        "El tratamiento seguirá el principio de minimización de datos: solo se recogerá la información estrictamente necesaria para alcanzar los objetivos científicos del proyecto.",
                        "Si la persona participante es menor de edad o no puede prestar consentimiento por sí misma, el uso de la aplicación con fines de investigación requiere la autorización de su representante legal cuando corresponda."
                    ]
                },
                {
                    "title": "Procedimiento de análisis de los datos",
                    "paragraphs": [
                        "Según la tarea seleccionada, las muestras de voz pueden ser analizadas mediante Praat, R, scripts en Python y modelos de reconocimiento automático del habla basados en Whisper.",
                        "El procesamiento se realizará en servidores o equipos locales gestionados por la Universitat de Barcelona o por el Laboratori de Fonètica.",
                        "No se enviarán las grabaciones a servicios comerciales externos ni a plataformas públicas en la nube para su procesamiento. Los proveedores del software utilizado no tendrán acceso a las grabaciones."
                    ]
                },
                {
                    "title": "Almacenamiento y seguridad",
                    "paragraphs": [
                        "Los datos se conservarán en infraestructuras informáticas ubicadas en el entorno de la Universitat de Barcelona y protegidas con medidas de seguridad institucionales, incluyendo acceso restringido con credenciales personales, control de accesos y protección mediante cortafuegos.",
                        "Solo podrá acceder el personal investigador o técnico autorizado vinculado al proyecto, sujeto a obligaciones de confidencialidad.",
                        "Se aplicarán medidas técnicas y organizativas para garantizar la confidencialidad, integridad y disponibilidad de la información. Cualquier transferencia fuera del entorno seguro requerirá autorización previa del investigador/a principal y el uso de sistemas de cifrado adecuados.",
                        "Podrán realizarse copias de seguridad en sistemas locales protegidos para garantizar la recuperación de la información en caso de incidencia o pérdida accidental."
                    ]
                },
                {
                    "title": "Conservación de los datos",
                    "paragraphs": [
                        "Las grabaciones originales de voz podrán conservarse durante un período máximo de cinco años desde la finalización del proyecto de investigación, con el fin de permitir la verificación y la difusión científica de los resultados.",
                        "Los datos derivados del análisis, como medidas acústicas o variables lingüísticas, podrán conservarse durante períodos más prolongados con fines científicos, siempre que estén adecuadamente seudonimizados o anonimizados."
                    ]
                },
                {
                    "title": "Compartición y publicación de datos",
                    "paragraphs": [
                        "Los datos derivados del análisis podrán compartirse con miembros del equipo investigador y con instituciones colaboradoras únicamente para fines científicos relacionados con el proyecto.",
                        "Los conjuntos de datos que se hagan públicos en el marco de políticas de ciencia abierta se prepararán previamente para evitar la identificación directa de las personas participantes. No se publicarán grabaciones de voz identificables.",
                        "Los datos anonimizados o agregados podrán depositarse en repositorios institucionales de investigación, como CORA. Repositori de Dades de Recerca, para favorecer la reproducibilidad y la reutilización científica.",
                        "El software desarrollado en el marco del proyecto podrá difundirse mediante licencias abiertas con fines científicos y académicos."
                    ]
                },
                {
                    "title": "Derechos de las personas participantes",
                    "paragraphs": [
                        "Puedes ejercer en cualquier momento los derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento, portabilidad y, en su caso, el derecho a no ser objeto de decisiones automatizadas, escribiendo al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "También puedes contactar con el Delegado/a de Protección de Datos de la UB en protecciodedades@ub.edu.",
                        "Si consideras que el tratamiento de tus datos no se ajusta a la normativa vigente, tienes derecho a presentar una reclamación ante la autoridad de control competente."
                    ]
                }
            ],
            "disclaimer": "Este texto es una propuesta informativa para la aplicación y conviene que sea revisado por el Delegado/a de Protección de Datos o por el comité/órgano responsable del proyecto antes de publicarlo."
        },
        "self_monitoring": {
            "page_title": "Información sobre protección de datos personales",
            "app_title": "AcousA - Uso solo para automonitorización",
            "back_label": "Volver a la aplicación",
            "intro": [
                "En este modo, la aplicación procesa la muestra de voz únicamente para generar los resultados solicitados por la persona usuaria. Los datos no se incorporan a bases de datos de investigación."
            ],
            "sections": [
                {
                    "title": "Responsable del tratamiento",
                    "paragraphs": [
                        "Los datos personales recogidos a través de esta aplicación serán tratados por la Universitat de Barcelona (UB), a través del Laboratori de Fonètica.",
                        "Para cualquier consulta relacionada con el tratamiento de los datos o con el ejercicio de tus derechos, puedes escribir al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "También puedes contactar con el Delegado/a de Protección de Datos de la Universitat de Barcelona en la dirección protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "¿Qué datos se recogen?",
                    "paragraphs": [
                        "La aplicación puede recoger los datos mínimos necesarios para prestar el servicio solicitado: edad, sexo/género, especificación de género si se ha indicado, tarea seleccionada, grabación de voz o archivo de audio subido, medidas derivadas del análisis e información técnica básica del navegador o dispositivo.",
                        "No se solicitan nombre, apellidos, DNI, dirección postal ni otros identificadores directos."
                    ]
                },
                {
                    "title": "Finalidad del tratamiento",
                    "paragraphs": [
                        "La finalidad del tratamiento es procesar automáticamente la muestra de habla y generar los resultados solicitados por la persona usuaria.",
                        "Las grabaciones de voz no se utilizarán con fines de investigación, docencia, publicaciones, entrenamiento de modelos de inteligencia artificial ni para ningún otro uso distinto del procesamiento solicitado.",
                        "Los resultados obtenidos se muestran a la persona usuaria como información de automonitorización y no constituyen un diagnóstico clínico."
                    ]
                },
                {
                    "title": "Base jurídica y normativa aplicable",
                    "paragraphs": [
                        "El tratamiento necesario para generar los resultados solicitados se basa en la petición expresa de la persona usuaria y se limita al tiempo y a los datos necesarios para prestar este servicio.",
                        "El tratamiento se realizará de acuerdo con el Reglamento (UE) 2016/679, Reglamento General de Protección de Datos (RGPD), y con la Ley Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).",
                        "El tratamiento seguirá el principio de minimización de datos: solo se recogerá la información estrictamente necesaria para completar el procesamiento solicitado."
                    ]
                },
                {
                    "title": "Procedimiento de análisis de los datos",
                    "paragraphs": [
                        "Las grabaciones de voz se envían exclusivamente a servidores gestionados por la Universitat de Barcelona para su procesamiento automático.",
                        "Según la tarea seleccionada, el procesamiento puede realizarse mediante Praat, R, scripts en Python y modelos de reconocimiento automático del habla basados en Whisper.",
                        "Todo el procesamiento se realizará en infraestructuras locales o propias de la Universitat de Barcelona. No se utilizarán servicios externos ni plataformas comerciales en la nube, y terceros ajenos a la Universitat de Barcelona no tendrán acceso a las grabaciones."
                    ]
                },
                {
                    "title": "Almacenamiento y seguridad",
                    "paragraphs": [
                        "Las grabaciones de voz y los archivos intermedios se conservarán temporalmente solo durante el tiempo necesario para completar el procesamiento y generar los resultados.",
                        "Durante este tiempo, los archivos estarán en servidores protegidos mediante medidas de seguridad institucionales, incluyendo sistemas de autenticación, control de acceso y protección mediante cortafuegos.",
                        "El acceso estará restringido exclusivamente al personal técnico o investigador autorizado de la Universitat de Barcelona, sujeto a obligaciones de confidencialidad.",
                        "No se utilizarán servicios de nube pública o de terceros para el almacenamiento o procesamiento de las grabaciones."
                    ]
                },
                {
                    "title": "Conservación de los datos",
                    "paragraphs": [
                        "Las grabaciones de voz y los archivos intermedios se conservarán únicamente durante el tiempo estrictamente necesario para completar el procesamiento solicitado y generar los resultados.",
                        "Una vez finalizado el procesamiento, los archivos de audio y los archivos intermedios se eliminarán automáticamente del sistema.",
                        "No se realizarán copias de seguridad de las grabaciones de voz ni se conservarán archivos de audio en bases de datos de investigación cuando no se haya dado consentimiento para investigación."
                    ]
                },
                {
                    "title": "Cesión y comunicación de datos",
                    "paragraphs": [
                        "Las grabaciones de voz no serán cedidas a terceros ni compartidas con otras entidades.",
                        "Las grabaciones no se incorporarán a bases de datos de investigación ni se utilizarán para el entrenamiento, mejora o validación de sistemas de inteligencia artificial.",
                        "No se publicarán datos individuales derivados de este uso de automonitorización."
                    ]
                },
                {
                    "title": "Derechos de las personas usuarias",
                    "paragraphs": [
                        "Puedes ejercer en cualquier momento los derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento, portabilidad y, en su caso, el derecho a no ser objeto de decisiones automatizadas, escribiendo al Laboratori de Fonètica: laboratori.fonetica@ub.edu.",
                        "También puedes contactar con el Delegado/a de Protección de Datos de la UB en protecciodedades@ub.edu.",
                        "Si consideras que el tratamiento de tus datos no se ajusta a la normativa vigente, tienes derecho a presentar una reclamación ante la autoridad de control competente."
                    ]
                }
            ],
            "disclaimer": "Este texto es una propuesta informativa para la aplicación y conviene que sea revisado por el Delegado/a de Protección de Datos o por el comité/órgano responsable del proyecto antes de publicarlo."
        }
    },
    "en": {
        "science": {
            "page_title": "Information on personal data protection",
            "app_title": "AcousA - Use of data for scientific research",
            "back_label": "Back to the application",
            "intro": [
                "Voice is personal data and, depending on the content of the recording or the context of use, may reveal sensitive information. For this reason, the application applies data minimisation, pseudonymisation, restricted access and local processing measures."
            ],
            "sections": [
                {
                    "title": "Data controller",
                    "paragraphs": [
                        "The personal data collected through this application will be processed by the University of Barcelona (UB), through the Phonetics Laboratory.",
                        "For any query related to data processing or to the exercise of your rights, you can contact the Phonetics Laboratory: laboratori.fonetica@ub.edu.",
                        "You may also contact the Data Protection Officer of the University of Barcelona at protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "What data are collected?",
                    "paragraphs": [
                        "The application may collect the minimum data required to perform the analysis: age, sex/gender, gender specification if provided, selected task, voice recording or uploaded audio file, acoustic and linguistic measures derived from the analysis, date of the analysis and basic technical information about the browser or device.",
                        "No name, surname, ID number, postal address or other direct identifiers are requested. Files are named using internal codes to reduce the risk of direct identification."
                    ]
                },
                {
                    "title": "Purpose of processing",
                    "paragraphs": [
                        "The main purpose is to enable recording, automatic processing and analysis of speech samples within a research project in clinical phonetics and speech technologies.",
                        "Voice recordings and data derived from their analysis may be used for the scientific objectives of the project, for verification of results, for statistical analyses and for scientific dissemination of the results obtained.",
                        "Results will be processed in pseudonymised or anonymised form where appropriate. Publications, conferences or scientific dissemination materials will not include data that directly identify participants."
                    ]
                },
                {
                    "title": "Legal basis and applicable regulations",
                    "paragraphs": [
                        "The legal basis for processing for research purposes is the participant's consent.",
                        "Processing will be carried out in accordance with Regulation (EU) 2016/679, the General Data Protection Regulation (GDPR), and Spanish Organic Law 3/2018 on personal data protection and guarantee of digital rights (LOPDGDD).",
                        "Processing will follow the principle of data minimisation: only the information strictly necessary to achieve the scientific objectives of the project will be collected.",
                        "If the participant is under age or cannot provide consent by themselves, use of the application for research purposes requires authorisation from their legal representative where applicable."
                    ]
                },
                {
                    "title": "Data analysis procedure",
                    "paragraphs": [
                        "Depending on the selected task, voice samples may be analysed using Praat, R, Python scripts and automatic speech recognition models based on Whisper.",
                        "Processing will be carried out on local servers or computers managed by the University of Barcelona or by the Phonetics Laboratory.",
                        "Recordings will not be sent to external commercial services or public cloud platforms for processing. The providers of the software used will not have access to the recordings."
                    ]
                },
                {
                    "title": "Storage and security",
                    "paragraphs": [
                        "The data will be stored on IT infrastructure within the University of Barcelona environment and protected by institutional security measures, including restricted access with personal credentials, access control and firewall protection.",
                        "Access will be limited to authorised research or technical staff linked to the project and subject to confidentiality obligations.",
                        "Technical and organisational measures will be applied to ensure the confidentiality, integrity and availability of the information. Any transfer outside the secure environment will require prior authorisation from the principal investigator and the use of appropriate encryption systems.",
                        "Backups may be made on protected local systems to ensure information recovery in case of incident or accidental data loss."
                    ]
                },
                {
                    "title": "Data retention",
                    "paragraphs": [
                        "Original voice recordings may be kept for a maximum period of five years after the end of the research project, in order to allow verification and scientific dissemination of the results.",
                        "Data derived from the analysis, such as acoustic measures or linguistic variables, may be kept for longer periods for scientific purposes, provided that they are adequately pseudonymised or anonymised."
                    ]
                },
                {
                    "title": "Data sharing and publication",
                    "paragraphs": [
                        "Data derived from the analysis may be shared with members of the research team and collaborating institutions solely for scientific purposes related to the project.",
                        "Datasets made public under open science policies will be prepared in advance to avoid direct identification of participants. Identifiable voice recordings will not be published.",
                        "Anonymised or aggregated data may be deposited in institutional research repositories, such as CORA. Repositori de Dades de Recerca, to support reproducibility and scientific reuse.",
                        "Software developed within the project may be released under open licences for scientific and academic purposes."
                    ]
                },
                {
                    "title": "Participant rights",
                    "paragraphs": [
                        "You may exercise your rights of access, rectification, erasure, objection, restriction of processing, data portability and, where applicable, the right not to be subject to automated decisions at any time by contacting the Phonetics Laboratory: laboratori.fonetica@ub.edu.",
                        "You may also contact the UB Data Protection Officer at protecciodedades@ub.edu.",
                        "If you consider that the processing of your data does not comply with current regulations, you have the right to lodge a complaint with the competent supervisory authority."
                    ]
                }
            ],
            "disclaimer": "This text is a proposed information notice for the application and should be reviewed by the Data Protection Officer or by the committee/body responsible for the project before publication."
        },
        "self_monitoring": {
            "page_title": "Information on personal data protection",
            "app_title": "AcousA - Use only for self-monitoring",
            "back_label": "Back to the application",
            "intro": [
                "In this mode, the application processes the voice sample only to generate the results requested by the user. The data are not included in research databases."
            ],
            "sections": [
                {
                    "title": "Data controller",
                    "paragraphs": [
                        "The personal data collected through this application will be processed by the University of Barcelona (UB), through the Phonetics Laboratory.",
                        "For any query related to data processing or to the exercise of your rights, you can contact the Phonetics Laboratory: laboratori.fonetica@ub.edu.",
                        "You may also contact the Data Protection Officer of the University of Barcelona at protecciodedades@ub.edu."
                    ]
                },
                {
                    "title": "What data are collected?",
                    "paragraphs": [
                        "The application may collect the minimum data required to provide the requested service: age, sex/gender, gender specification if provided, selected task, voice recording or uploaded audio file, measures derived from the analysis and basic technical information about the browser or device.",
                        "No name, surname, ID number, postal address or other direct identifiers are requested."
                    ]
                },
                {
                    "title": "Purpose of processing",
                    "paragraphs": [
                        "The purpose of processing is to automatically process the speech sample and generate the results requested by the user.",
                        "Voice recordings will not be used for research, teaching, publications, training artificial intelligence models or any other purpose other than the requested processing.",
                        "The results obtained are shown to the user as self-monitoring information and do not constitute a clinical diagnosis."
                    ]
                },
                {
                    "title": "Legal basis and applicable regulations",
                    "paragraphs": [
                        "The processing required to generate the requested results is based on the user's explicit request and is limited to the time and data necessary to provide this service.",
                        "Processing will be carried out in accordance with Regulation (EU) 2016/679, the General Data Protection Regulation (GDPR), and Spanish Organic Law 3/2018 on personal data protection and guarantee of digital rights (LOPDGDD).",
                        "Processing will follow the principle of data minimisation: only the information strictly necessary to complete the requested processing will be collected."
                    ]
                },
                {
                    "title": "Data analysis procedure",
                    "paragraphs": [
                        "Voice recordings are sent exclusively to servers managed by the University of Barcelona for automatic processing.",
                        "Depending on the selected task, processing may be carried out using Praat, R, Python scripts and automatic speech recognition models based on Whisper.",
                        "All processing will be carried out on local infrastructure or infrastructure owned or managed by the University of Barcelona. No external services or commercial cloud platforms will be used, and third parties outside the University of Barcelona will not have access to the recordings."
                    ]
                },
                {
                    "title": "Storage and security",
                    "paragraphs": [
                        "Voice recordings and intermediate files will be stored temporarily only for the time necessary to complete processing and generate the results.",
                        "During this time, files will be stored on servers protected by institutional security measures, including authentication systems, access control and firewall protection.",
                        "Access will be restricted exclusively to authorised technical or research staff of the University of Barcelona, subject to confidentiality obligations.",
                        "No public cloud or third-party services will be used for storing or processing recordings."
                    ]
                },
                {
                    "title": "Data retention",
                    "paragraphs": [
                        "Voice recordings and intermediate files will be kept only for the time strictly necessary to complete the requested processing and generate the results.",
                        "Once processing has finished, audio files and intermediate files will be automatically deleted from the system.",
                        "No backups of voice recordings will be made and no audio files will be kept in research databases when consent for research has not been given."
                    ]
                },
                {
                    "title": "Data disclosure and communication",
                    "paragraphs": [
                        "Voice recordings will not be transferred to third parties or shared with other entities.",
                        "Recordings will not be included in research databases or used for training, improving or validating artificial intelligence systems.",
                        "No individual data derived from this self-monitoring use will be published."
                    ]
                },
                {
                    "title": "User rights",
                    "paragraphs": [
                        "You may exercise your rights of access, rectification, erasure, objection, restriction of processing, data portability and, where applicable, the right not to be subject to automated decisions at any time by contacting the Phonetics Laboratory: laboratori.fonetica@ub.edu.",
                        "You may also contact the UB Data Protection Officer at protecciodedades@ub.edu.",
                        "If you consider that the processing of your data does not comply with current regulations, you have the right to lodge a complaint with the competent supervisory authority."
                    ]
                }
            ],
            "disclaimer": "This text is a proposed information notice for the application and should be reviewed by the Data Protection Officer or by the committee/body responsible for the project before publication."
        }
    }
}


VALID_CONSENT_MODES = {"science", "self_monitoring"}


def get_consent_page(lang: str, mode: str = "science"):
    if lang not in CONSENT_PAGES:
        lang = DEFAULT_LANG

    if mode not in VALID_CONSENT_MODES:
        mode = "science"

    return CONSENT_PAGES[lang][mode], lang, mode
