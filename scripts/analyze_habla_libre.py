#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import os
import re
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
import json
from collections import Counter, defaultdict
import urllib.parse
import urllib.request
import urllib.error

import numpy as np
from faster_whisper import WhisperModel


SILENCE_LABELS = {"", "<eps>", "sil", "sp", "spn"}


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def clean_for_mfa(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[¿?¡!.,;:()\[\]{}\"“”«»]", " ", text)
    text = re.sub(r"[^a-záéíóúüñ\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def transcribe_whisper(
    audio_path: Path,
    language: str = "es",
    model_size: str = "small",
    device: str = "cpu",
    compute_type: str = "int8",
) -> str:
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        task="transcribe",
        beam_size=3,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=700,
            speech_pad_ms=200,
        ),
        condition_on_previous_text=False,
        word_timestamps=False,
    )
    text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())
    return re.sub(r"\s+", " ", text).strip()


def run_mfa(
    wav_path: Path,
    transcript: str,
    mfa_cmd: str,
    dictionary: str = "spanish_mfa",
    acoustic_model: str = "spanish_mfa",
) -> Path:
    debug_root = Path("/srv/labfon/acousa_mfa_debug")
    debug_root.mkdir(parents=True, exist_ok=True)

    tmpdir = Path(tempfile.mkdtemp(prefix="acousa_mfa_", dir=str(debug_root)))
    corpus_dir = tmpdir / "corpus"
    out_dir = tmpdir / "aligned"
    corpus_dir.mkdir()
    out_dir.mkdir()

    audio_copy = corpus_dir / "audio.wav"
    lab_file = corpus_dir / "audio.lab"

    shutil.copy2(wav_path, audio_copy)

    cleaned_transcript = clean_for_mfa(transcript)
    lab_file.write_text(cleaned_transcript, encoding="utf-8")

    if not cleaned_transcript.strip():
        raise RuntimeError(
            "La transcripción de Whisper existe, pero al limpiarla para MFA ha quedado vacía.\n"
            f"Transcripción original:\n{transcript}\n"
            f"Carpeta de depuración: {tmpdir}"
        )

    cmd = [
        mfa_cmd,
        "align",
        str(corpus_dir),
        dictionary,
        acoustic_model,
        str(out_dir),
        "--clean",
        "--overwrite",
        "--single_speaker",
        "--num_jobs", "1",
    ]

    env = os.environ.copy()
    env["PATH"] = f"{Path(mfa_cmd).parent}:{env.get('PATH', '')}"
    env["TMPDIR"] = str(tmpdir)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "MFA falló durante la alineación.\n\n"
            "COMANDO:\n"
            + " ".join(cmd)
            + "\n\nTRANSCRIPCIÓN ORIGINAL DE WHISPER:\n"
            + transcript
            + "\n\nTRANSCRIPCIÓN LIMPIA PARA MFA:\n"
            + cleaned_transcript
            + "\n\nSTDOUT MFA:\n"
            + (result.stdout or "")
            + "\n\nSTDERR MFA:\n"
            + (result.stderr or "")
            + "\n\nCARPETA DE DEPURACIÓN:\n"
            + str(tmpdir)
            + "\n"
        )

    textgrids = list(out_dir.rglob("*.TextGrid"))
    if not textgrids:
        raise RuntimeError(
            "MFA terminó sin error, pero no generó ningún TextGrid.\n"
            f"Carpeta de depuración: {tmpdir}\n"
            f"STDOUT MFA:\n{result.stdout}\n"
            f"STDERR MFA:\n{result.stderr}\n"
        )

    final_tg = Path(tempfile.mkstemp(prefix="acousa_mfa_", suffix=".TextGrid")[1])
    shutil.copy2(textgrids[0], final_tg)

    # Si todo va bien, limpiamos la carpeta temporal de debug.
    shutil.rmtree(tmpdir, ignore_errors=True)

    return final_tg


def parse_textgrid_intervals(textgrid_path: Path) -> dict[str, list[tuple[float, float, str]]]:
    tiers: list[dict] = []
    current = None
    current_interval = None

    for raw in textgrid_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()

        if line.startswith("item ["):
            if current is not None:
                tiers.append(current)
            current = {"name": "", "intervals": []}
            current_interval = None
            continue

        if current is None:
            continue

        if line.startswith("name ="):
            m = re.match(r'name\s*=\s*"(.*)"', line)
            if m:
                current["name"] = m.group(1)
            continue

        if line.startswith("intervals ["):
            current_interval = {}
            continue

        if current_interval is not None and line.startswith("xmin ="):
            current_interval["xmin"] = float(line.split("=", 1)[1].strip())
            continue

        if current_interval is not None and line.startswith("xmax ="):
            current_interval["xmax"] = float(line.split("=", 1)[1].strip())
            continue

        if current_interval is not None and line.startswith("text ="):
            m = re.match(r'text\s*=\s*"(.*)"', line)
            current_interval["text"] = m.group(1) if m else ""
            if {"xmin", "xmax", "text"}.issubset(current_interval):
                current["intervals"].append(
                    (
                        float(current_interval["xmin"]),
                        float(current_interval["xmax"]),
                        str(current_interval["text"]).strip(),
                    )
                )
            current_interval = None

    if current is not None:
        tiers.append(current)

    return {t["name"].lower(): t["intervals"] for t in tiers}


def get_word_intervals(textgrid_path: Path) -> list[tuple[float, float, str]]:
    tiers = parse_textgrid_intervals(textgrid_path)

    for name in ["words", "word"]:
        if name in tiers:
            return [
                (xmin, xmax, text)
                for xmin, xmax, text in tiers[name]
                if text.strip().lower() not in SILENCE_LABELS
            ]

    # Fallback: si MFA cambia el nombre del tier, usamos el tier con más intervalos no vacíos.
    candidates = []
    for name, intervals in tiers.items():
        non_empty = [
            (xmin, xmax, text)
            for xmin, xmax, text in intervals
            if text.strip().lower() not in SILENCE_LABELS
        ]
        if non_empty:
            candidates.append((len(non_empty), name, non_empty))

    if not candidates:
        return []

    candidates.sort(reverse=True)
    return candidates[0][2]

def get_phone_intervals(textgrid_path: Path) -> list[tuple[float, float, str]]:
    tiers = parse_textgrid_intervals(textgrid_path)

    for name in ["phones", "phone"]:
        if name in tiers:
            return [
                (xmin, xmax, text)
                for xmin, xmax, text in tiers[name]
                if text.strip().lower() not in SILENCE_LABELS
            ]

    # Fallback: busca un tier que parezca de phones
    for name, intervals in tiers.items():
        if "phone" in name:
            return [
                (xmin, xmax, text)
                for xmin, xmax, text in intervals
                if text.strip().lower() not in SILENCE_LABELS
            ]

    return []


def count_syllables_spanish_word(word: str) -> int:
    word = word.lower()
    word = re.sub(r"[^a-záéíóúüñ]", "", word)
    if not word:
        return 0

    # Estimación simple: grupos vocálicos. Suficiente para rates globales.
    groups = re.findall(r"[aeiouáéíóúü]+", word)
    return max(1, len(groups))


def estimate_syllables_spanish(text: str) -> int:
    words = clean_for_mfa(text).split()
    return sum(count_syllables_spanish_word(w) for w in words)

LEXICAL_UPOS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}

SUBORDINATE_DEPREL_PREFIXES = (
    "advcl",      # subordinada adverbial
    "ccomp",      # completiva finita
    "xcomp",      # complemento abierto / infinitivo controlado
    "acl",        # cláusula adnominal
    "csubj",      # subordinada sujeto
)


def _norm_lemma(lemma: str) -> str:
    lemma = (lemma or "").strip().lower()
    lemma = re.sub(r"\s+", " ", lemma)
    return lemma

DATAMUSE_ENDPOINT = "https://api.datamuse.com/words"

FREQ_CATEGORIES = [
    "muy frecuentes",
    "bastante frecuentes",
    "frecuencia media",
    "poco frecuentes",
    "muy raras",
]


def datamuse_frequency_category(freq_per_million: float | None) -> str:
    """
    Categorías basadas en frecuencia por millón.
    Cuanto menor la frecuencia, más raro/complejo el lema.
    """
    if freq_per_million is None:
        return "muy raras"

    if freq_per_million >= 100:
        return "muy frecuentes"
    if freq_per_million >= 10:
        return "bastante frecuentes"
    if freq_per_million >= 1:
        return "frecuencia media"
    if freq_per_million >= 0.1:
        return "poco frecuentes"
    return "muy raras"


def frequency_category_score(category: str) -> int:
    """
    Escala RLE:
      1 = lemas muy frecuentes
      5 = lemas muy poco frecuentes

    Es una medida experimental de riqueza/singularidad léxica estimada,
    no una medida clínica normativa.
    """
    mapping = {
        "muy frecuentes": 1,
        "bastante frecuentes": 2,
        "frecuencia media": 3,
        "poco frecuentes": 4,
        "muy raras": 5,
    }
    return mapping.get(category, 5)


def lexical_complexity_label_from_score(score: float | None) -> str:
    if score is None:
        return "no calculable"

    if score < 1.5:
        return "vocabulario muy frecuente"
    if score < 2.5:
        return "vocabulario bastante frecuente"
    if score < 3.5:
        return "vocabulario de frecuencia media"
    if score < 4.5:
        return "vocabulario poco frecuente"
    return "vocabulario muy poco frecuente"

def _clamp_float(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def rle_score_tail_sensitive(
    token_scores: list[int],
    unique_scores: list[int],
    lexical_ttr: float,
    lexical_tokens: int,
) -> float | None:
    """
    RLE = Riqueza Léxica Estimada, escala 1–5.

    Esta versión es sensible a textos cortos y a la cola léxica:
    no solo mira la media, sino también si aparecen lemas poco frecuentes
    o muy poco frecuentes.

    1 = vocabulario muy frecuente
    5 = vocabulario muy poco frecuente / muy marcado
    """
    if not token_scores or not unique_scores:
        return None

    token_arr = np.array(token_scores, dtype=float)
    unique_arr = np.array(unique_scores, dtype=float)

    # Normalizamos 1–5 a 0–1
    mean_unique_norm = (float(np.mean(unique_arr)) - 1.0) / 4.0

    # Cola léxica: percentil alto de rareza.
    # Esto hace que palabras muy poco frecuentes pesen más en textos cortos.
    p90_unique_norm = (float(np.percentile(unique_arr, 90)) - 1.0) / 4.0

    rare_unique_prop = float(np.mean(unique_arr >= 4.0))
    very_rare_unique_prop = float(np.mean(unique_arr >= 5.0))

    # Presión de rareza: sqrt hace que 20–30% de lemas raros ya pese bastante.
    rare_pressure = np.sqrt(rare_unique_prop)
    very_rare_pressure = np.sqrt(very_rare_unique_prop)

    # TTR léxico: en textos cortos suele ser informativo, pero no queremos que domine.
    ttr_norm = _clamp_float(float(lexical_ttr), 0.0, 1.0)

    # Fórmula experimental: más sensible a vocabulario marcado.
    rle_norm = (
        0.48 * p90_unique_norm
        + 0.18 * mean_unique_norm
        + 0.22 * rare_pressure
        + 0.07 * very_rare_pressure
        + 0.05 * ttr_norm
    )

    rle = 1.0 + 4.0 * rle_norm

    # Bonus moderado para textos cortos si tienen una proporción clara de lemas raros.
    # Esto evita que textos breves y léxicamente marcados queden artificialmente bajos.
    if lexical_tokens < 90 and rare_unique_prop >= 0.18:
        rle += 0.45
    if lexical_tokens < 60 and rare_unique_prop >= 0.25:
        rle += 0.25

    return round(_clamp_float(rle, 1.0, 5.0), 2)


def parse_datamuse_frequency(item: dict) -> float | None:
    tags = item.get("tags", []) or []
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("f:"):
            try:
                return float(tag[2:])
            except ValueError:
                return None
    return None


def get_datamuse_frequency_for_lemma(
    lemma: str,
    *,
    timeout_sec: float = 3.0,
) -> dict:
    """
    Consulta Datamuse para un lema.
    Devuelve un dict robusto, para que la app no se rompa si la API falla.
    """
    lemma = (lemma or "").strip().lower()

    if not lemma:
        return {
            "datamuse_status": "empty_lemma",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "muy raras",
        }

    params = {
        "sp": lemma,
        "qe": "sp",
        "md": "f",
        "v": "es",
        "max": "1",
    }

    url = DATAMUSE_ENDPOINT + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AcousA/0.1 lexical-frequency-analysis",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {
            "datamuse_status": f"api_error: {e}",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "muy raras",
        }
    except Exception as e:
        return {
            "datamuse_status": f"api_error: {e}",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "muy raras",
        }

    if not isinstance(data, list) or not data:
        return {
            "datamuse_status": "not_found",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "muy raras",
        }

    item = data[0]
    freq = parse_datamuse_frequency(item)
    category = datamuse_frequency_category(freq)

    return {
        "datamuse_status": "ok" if freq is not None else "found_without_frequency",
        "datamuse_word": item.get("word", ""),
        "datamuse_frequency_per_million": freq,
        "frequency_category": category,
    }


def analyze_stanza_complexity(text: str) -> tuple[dict, dict]:
    """
    Devuelve:
      - métricas sintácticas/léxicas para el CSV
      - payload detallado de lemas para guardar como JSON .txt
    """
    try:
        import stanza
    except Exception as e:
        raise RuntimeError(
            "No se pudo importar Stanza. Instala stanza en el .venv de la app."
        ) from e

    model_dir = os.getenv("STANZA_RESOURCES_DIR", "/srv/labfon/stanza_resources")

    nlp = stanza.Pipeline(
        "es",
        processors="tokenize,mwt,pos,lemma,depparse",
        model_dir=model_dir,
        download_method=None,
        use_gpu=False,
        verbose=False,
    )

    doc = nlp(text)

    sentence_count = len(doc.sentences)
    sentence_lengths = []
    total_tokens = 0
    lexical_tokens = 0
    subordinate_count = 0

    lemma_counter = Counter()
    lemma_pos_counter = defaultdict(Counter)

    for sent in doc.sentences:
        sent_token_count = 0

        for word in sent.words:
            upos = word.upos or ""
            deprel = word.deprel or ""

            if upos not in {"PUNCT", "SYM", "X"}:
                total_tokens += 1
                sent_token_count += 1

            if any(deprel.startswith(prefix) for prefix in SUBORDINATE_DEPREL_PREFIXES):
                subordinate_count += 1

            if upos in LEXICAL_UPOS:
                lemma = _norm_lemma(word.lemma or word.text)
                if lemma:
                    lexical_tokens += 1
                    lemma_counter[lemma] += 1
                    lemma_pos_counter[lemma][upos] += 1

        if sent_token_count > 0:
            sentence_lengths.append(sent_token_count)

    mean_sentence_length = (
        sum(sentence_lengths) / len(sentence_lengths)
        if sentence_lengths else 0.0
    )

    lexical_density = (
        lexical_tokens / total_tokens * 100.0
        if total_tokens > 0 else 0.0
    )

    unique_lexical_lemmas = len(lemma_counter)
    lexical_ttr = (
        unique_lexical_lemmas / lexical_tokens
        if lexical_tokens > 0 else 0.0
    )

    lemmas = []
    category_token_counts = Counter()
    category_lemma_counts = Counter()
    weighted_scores = []
    unique_scores = []
    freq_values = []

    for lemma, count in lemma_counter.most_common():
        pos_counts = dict(lemma_pos_counter[lemma])
        main_upos = max(pos_counts.items(), key=lambda x: x[1])[0] if pos_counts else ""

        datamuse_info = get_datamuse_frequency_for_lemma(lemma)
        category = datamuse_info["frequency_category"]
        score = frequency_category_score(category)

        category_token_counts[category] += count
        category_lemma_counts[category] += 1
        weighted_scores.extend([score] * count)
        unique_scores.append(score)

        freq = datamuse_info.get("datamuse_frequency_per_million")
        if freq is not None:
            freq_values.extend([freq] * count)

        lemma_entry = {
            "lemma": lemma,
            "upos": main_upos,
            "count_in_text": count,
            "relative_frequency_per_1000_lexical_tokens": (
                round(count / lexical_tokens * 1000.0, 4)
                if lexical_tokens > 0 else 0.0
            ),
            "pos_counts": pos_counts,
        }

        lemma_entry.update(datamuse_info)
        lemmas.append(lemma_entry)

    mean_rarity_score = (
        sum(weighted_scores) / len(weighted_scores)
        if weighted_scores else None
    )

    rle_score = rle_score_tail_sensitive(
        token_scores=weighted_scores,
        unique_scores=unique_scores,
        lexical_ttr=lexical_ttr,
        lexical_tokens=lexical_tokens,
    )

    lexical_complexity_index = lexical_complexity_label_from_score(rle_score)

    rare_or_very_rare_tokens = (
        category_token_counts["poco frecuentes"] + category_token_counts["muy raras"]
    )

    lexical_complexity_rare_percent = (
        rare_or_very_rare_tokens / lexical_tokens * 100.0
        if lexical_tokens > 0 else 0.0
    )

    mean_datamuse_frequency_per_million = (
        sum(freq_values) / len(freq_values)
        if freq_values else None
    )

    metrics = {
        "sentence_count": sentence_count,
        "mean_sentence_length_words": mean_sentence_length,
        "subordinate_clause_count": subordinate_count,
        "subordinates_per_sentence": (
            subordinate_count / sentence_count if sentence_count > 0 else 0.0
        ),
        "total_tokens_stanza": total_tokens,
        "lexical_tokens": lexical_tokens,
        "unique_lexical_lemmas": unique_lexical_lemmas,
        "lexical_density": lexical_density,
        "lexical_ttr": lexical_ttr,

        "lexical_complexity_index": lexical_complexity_index,
        "lexical_richness_score_1_5": rle_score if rle_score is not None else "",
        "lexical_complexity_rarity_score": rle_score if rle_score is not None else "",
        "lexical_mean_category_score_1_5": mean_rarity_score if mean_rarity_score is not None else "",
        "lexical_complexity_rare_percent": lexical_complexity_rare_percent,
        "mean_datamuse_frequency_per_million": (
            mean_datamuse_frequency_per_million
            if mean_datamuse_frequency_per_million is not None else ""
        ),
    }

    lemma_payload = {
        "language": "es",
        "source": "Whisper transcription analysed with Stanza",
        "transcription": text,
        "summary": {
            "sentence_count": sentence_count,
            "sentence_lengths_words": sentence_lengths,
            "mean_sentence_length_words": round(mean_sentence_length, 4),
            "subordinate_clause_count": subordinate_count,
            "subordinates_per_sentence": round(metrics["subordinates_per_sentence"], 4),
            "total_tokens_stanza": total_tokens,
            "lexical_tokens": lexical_tokens,
            "unique_lexical_lemmas": unique_lexical_lemmas,
            "lexical_density_percent": round(lexical_density, 4),
            "lexical_ttr": round(lexical_ttr, 4),
        },
        "lexical_complexity_index": {
            "source": "Datamuse API",
            "global_category": lexical_complexity_index,
            "rle_score_1_frequent_5_marked": (
                round(rle_score, 4)
                if rle_score is not None else None
            ),
            "mean_category_score_1_frequent_5_rare": (
                round(mean_rarity_score, 4)
                if mean_rarity_score is not None else None
            ),
            "rle_method": (
                "Índice experimental sensible a la cola léxica. Combina el percentil 90 de rareza "
                "de los lemas, la media de categorías, la proporción de lemas poco frecuentes o muy "
                "poco frecuentes, la proporción de lemas muy poco frecuentes y el TTR léxico. "
                "Está ajustado para no infraestimar textos breves."
            ),
            "rare_or_very_rare_lexical_tokens_percent": round(lexical_complexity_rare_percent, 4),
            "mean_datamuse_frequency_per_million": (
                round(mean_datamuse_frequency_per_million, 4)
                if mean_datamuse_frequency_per_million is not None else None
            ),
            "frequency_categories": {
                "muy frecuentes": ">= 100 ocurrencias por millón",
                "bastante frecuentes": "10–99.99 ocurrencias por millón",
                "frecuencia media": "1–9.99 ocurrencias por millón",
                "poco frecuentes": "0.1–0.99 ocurrencias por millón",
                "muy raras": "< 0.1 ocurrencias por millón o no encontrado",
            },
            "token_counts_by_category": dict(category_token_counts),
            "lemma_counts_by_category": dict(category_lemma_counts),
        },
        "lemmas": lemmas,
    }

    return metrics, lemma_payload


def write_json_txt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def f0_metrics(audio_path: Path) -> tuple[float | None, float | None, float | None]:
    try:
        import parselmouth
    except Exception:
        return None, None, None

    snd = parselmouth.Sound(str(audio_path))
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)
    f0 = pitch.selected_array["frequency"]
    f0 = f0[f0 > 0]

    if len(f0) == 0:
        return None, None, None

    return float(np.mean(f0)), float(np.std(f0)), float(np.max(f0) - np.min(f0))


def compute_metrics(
    wav_path: Path,
    transcript: str,
    textgrid_path: Path,
    pause_threshold: float = 0.25,
    long_pause_threshold: float = 1.0,
) -> dict:
    total_duration = wav_duration(wav_path)
    word_intervals = get_word_intervals(textgrid_path)
    phone_intervals = get_phone_intervals(textgrid_path)

    syllables = estimate_syllables_spanish(transcript)
    word_count = len(clean_for_mfa(transcript).split())
    sound_count = len(phone_intervals)

    if not phone_intervals:
        f0_mean, f0_sd, f0_range = f0_metrics(wav_path)
        return {
            "speech_duration": "",
            "articulation_duration": "",
            "speech_rate": "",
            "articulation_rate": "",
            "pause_count": "",
            "mean_pause_duration": "",
            "pause_percentage": "",
            "long_pauses": "",
            "word_count": word_count,
            "syllable_count_estimated": syllables,
            "sound_count": sound_count,
            "rate_unit": "sounds_per_second",
            "speech_intervals": len(word_intervals),
            "voice_start": "",
            "voice_end": "",
            "f0_mean": f0_mean,
            "f0_sd": f0_sd,
            "f0_range": f0_range,
            "transcription": transcript,
            "mfa_textgrid": str(textgrid_path),
        }

    phone_intervals = sorted(phone_intervals, key=lambda x: x[0])
    word_intervals = sorted(word_intervals, key=lambda x: x[0])

    voice_start = phone_intervals[0][0]
    voice_end = phone_intervals[-1][1]

    # Duración del tramo de habla: desde el primer sonido MFA hasta el último.
    # Incluye pausas internas.
    speech_duration = max(voice_end - voice_start, 0.0)

    # Tiempo articulado: suma de la duración de los sonidos no silenciosos del tier phones.
    # Excluye intervalos vacíos/silenciosos.
    articulation_duration = sum(
        max(xmax - xmin, 0.0)
        for xmin, xmax, _ in phone_intervals
    )

    # Pausas: intervalos vacíos/silenciosos del tier phones dentro del tramo de habla.
    tiers = parse_textgrid_intervals(textgrid_path)
    phone_tier = tiers.get("phones") or tiers.get("phone") or []
    gaps = [
        max(xmax - xmin, 0.0)
        for xmin, xmax, label in phone_tier
        if (
            label.strip().lower() in SILENCE_LABELS
            and xmax > voice_start
            and xmin < voice_end
            and max(xmax - xmin, 0.0) >= pause_threshold
        )
    ]

    pause_total = sum(gaps)
    pause_count = len(gaps)
    mean_pause = pause_total / pause_count if pause_count else 0.0
    pause_percentage = (pause_total / speech_duration * 100.0) if speech_duration > 0 else 0.0
    long_pauses = sum(1 for g in gaps if g >= long_pause_threshold)

    # Rates en sonidos por segundo, no sílabas por segundo.
    speech_rate = sound_count / speech_duration if speech_duration > 0 else 0.0
    articulation_rate = sound_count / articulation_duration if articulation_duration > 0 else 0.0

    f0_mean, f0_sd, f0_range = f0_metrics(wav_path)

    return {
        "speech_duration": speech_duration,
        "articulation_duration": articulation_duration,
        "speech_rate": speech_rate,
        "articulation_rate": articulation_rate,
        "pause_count": pause_count,
        "mean_pause_duration": mean_pause,
        "pause_percentage": pause_percentage,
        "long_pauses": long_pauses,
        "word_count": word_count,
        "syllable_count_estimated": syllables,
        "speech_intervals": len(word_intervals),
        "voice_start": voice_start,
        "voice_end": voice_end,
        "f0_mean": f0_mean,
        "f0_sd": f0_sd,
        "f0_range": f0_range,
        "transcription": transcript,
        "mfa_textgrid": str(textgrid_path),
        "sound_count": sound_count,
        "rate_unit": "sounds_per_second",
    }


def write_one_row_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--mfa-cmd", default=os.getenv("MFA_CMD", "mfa"))
    parser.add_argument("--language", default="es")
    parser.add_argument("--model", default=os.getenv("ACOUS_A_ASR_MODEL", "small"))
    parser.add_argument("--device", default=os.getenv("ACOUS_A_ASR_DEVICE", "cpu"))
    parser.add_argument("--compute-type", default=os.getenv("ACOUS_A_ASR_COMPUTE_TYPE", "int8"))
    parser.add_argument("--out-textgrid", default=None)
    parser.add_argument("--pause-threshold", type=float, default=0.25)
    parser.add_argument("--long-pause-threshold", type=float, default=1.0)
    parser.add_argument("--out-lemmas-json", default=None)
    args = parser.parse_args()

    audio_path = Path(args.audio)
    out_csv = Path(args.out_csv)
    out_lemmas_json = (
        Path(args.out_lemmas_json)
        if args.out_lemmas_json
        else out_csv.with_name(out_csv.stem + "_lemmas.txt")
    )
    out_textgrid = Path(args.out_textgrid) if args.out_textgrid else out_csv.with_suffix(".TextGrid")

    transcript = transcribe_whisper(
        audio_path,
        language=args.language,
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type,
    )

    if not transcript.strip():
        raise RuntimeError("Whisper no ha generado transcripción. No se puede alinear con MFA.")

    temp_tg_path = run_mfa(
        wav_path=audio_path,
        transcript=transcript,
        mfa_cmd=args.mfa_cmd,
    )

    try:
        out_textgrid.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(temp_tg_path, out_textgrid)

        metrics = compute_metrics(
            wav_path=audio_path,
            transcript=transcript,
            textgrid_path=out_textgrid,
            pause_threshold=args.pause_threshold,
            long_pause_threshold=args.long_pause_threshold,
        )

        # Guardamos la ruta final, no la temporal
        metrics["mfa_textgrid"] = str(out_textgrid)

        stanza_metrics, lemma_payload = analyze_stanza_complexity(transcript)
        metrics.update(stanza_metrics)

        metrics["lemmas_json_txt"] = str(out_lemmas_json)

        write_json_txt(out_lemmas_json, lemma_payload)
        write_one_row_csv(out_csv, metrics)

    finally:
        try:
            temp_tg_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()