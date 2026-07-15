TASKS = {
    "pataka": {
        "praat_script": "analyze_pataka.praat",
        "label": {
            "es": "articulación (diadococinesia)",
            "ca": "articulació (diadococinèsia)",
            "en": "articulation (diadochokinesis)",
        },
        "instructions": {
            "es": "Coge aire y repite «pataka» lo más rápido que puedas, todas las veces posibles con una sola inspiración. Recuerda parar la grabación al terminar.",
            "ca": "Agafa aire i repeteix «pataka» tan ràpid com puguis, tantes vegades com puguis amb una sola inspiració. Recorda aturar la gravació en acabar.",
            "en": "Take a deep breath and repeat “pataka” as fast as you can, as many times as possible on a single breath. Remember to stop the recording.",
        },
    },
    "asos": {
        "python_script": "asos_pipeline.py",
        "r_script": "analyze_asos_all.R",
        "label": {        
            "es": "calidad vocal",
            "ca": "qualitat vocal",
            "en": "vocal quality",
        },
        "instructions": {
            "es": "Coge aire y mantén la vocal «a» todo lo larga que puedas, a un volumen cómodo.",
            "ca": "Agafa aire i mantén la vocal «a» tan llarga com puguis, a un volum còmode.",
            "en": "Take a deep breath and sustain the vowel “a” for as long as you can, at a comfortable loudness.",
        }
    },
    "lectura": {
        "pipeline": "acoustic_lectura",
        "prosody_script": "analyze_lectura.py",
        "reference_texts": {
            "es": "El viento Norte y el Sol discutían sobre cuál de ellos era el más fuerte, cuando pasó un extraño viajero envuelto en unas ropas muy abrigadas. Convinieron en que quien antes lograra obligarlo al transeúnte a quitarse el abrigo sería considerado más poderoso. El viento sopló con gran furia, pero cuanto más soplaba, más se ceñía el hombre su ropa al cuerpo. Entonces se dio por vencido, y el sol empezó a brillar con mucha fuerza. Inmediatamente el viajero se despojó de su abrigo; y así ya quedó claro que el sol tenía superioridad respecto del viento",
            "ca": "Un dia, de sobte, el vent de la tramuntana i el sol discutien fortament, per decidir el millor dels dos. Per atzar, veuen un viatger sense calçat i amb un abric roig passejant tranquil per un terreny. Decidiren que qui aconseguís que el senyor es tragués una capa es quedaria el cel aquella temporada. La tramuntana bufà amb moltíssimes ganes que la notessin, no obstant, com més bufava, l'home més s'abrigava, i decidí deixar-ho estar. El sol sortí al cap de res, de sobte, l'home es tragué la capa perquè s'acalorava molt, i doncs, la tramuntana confessà que era una fluixa",
            "en": "Un dia, de sobte, el vent de la tramuntana i el sol discutien fortament, per decidir el millor dels dos. Per atzar, veuen un viatger sense calçat i amb un abric roig passejant tranquil per un terreny. Decidiren que qui aconseguís que el senyor es tragués una capa es quedaria el cel aquella temporada. La tramuntana bufà amb moltíssimes ganes que la notessin, no obstant, com més bufava, l'home més s'abrigava, i decidí deixar-ho estar. El sol sortí al cap de res, de sobte, l'home es tragué la capa perquè s'acalorava molt, i doncs, la tramuntana confessà que era una fluixa",
        },
        "label": {
            "es": "lectura en voz alta",
            "ca": "lectura en veu alta",
            "en": "reading aloud",
        },
        "instructions": {
            "es": "Lee en voz alta el texto indicado a un ritmo cómodo y natural, con una voz clara y en un entorno silencioso.",
            "ca": "Llegeix en veu alta el text indicat a un ritme còmode i natural, amb una veu clara i en un entorn silenciós.",
            "en": "Read the displayed text aloud at a comfortable, natural pace, with a clear voice and in a quiet environment.",
        },
    },
    "habla_libre": {
        "pipeline": "habla_libre",
        "python_script": "analyze_habla_libre.py",
        "label": {
            "es": "habla espontánea",
            "ca": "parla espontània en castellà",
            "en": "spontaneous speech in Spanish",
        },
        "instructions": {
            "es": "Explica paso a paso como te lavas los dientes.",
            "ca": "Explica pas a pas com et rentes les dents en espanyol.",
            "en": "Explain step by step how do you brush your teeth in Spanish.",
        },
    },
}
