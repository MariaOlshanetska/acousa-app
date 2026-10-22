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
            "The Whisper transcription exists, but after cleaning it for MFA it became empty.\n"
            f"Original transcription:\n{transcript}\n"
            f"Debug folder: {tmpdir}"
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
            "MFA failed during alignment.\n\n"
            "COMMAND:\n"
            + " ".join(cmd)
            + "\n\nORIGINAL WHISPER TRANSCRIPTION:\n"
            + transcript
            + "\n\nCLEANED TRANSCRIPTION FOR MFA:\n"
            + cleaned_transcript
            + "\n\nMFA STDOUT:\n"
            + (result.stdout or "")
            + "\n\nMFA STDERR:\n"
            + (result.stderr or "")
            + "\n\nDEBUG FOLDER:\n"
            + str(tmpdir)
            + "\n"
        )

    textgrids = list(out_dir.rglob("*.TextGrid"))
    if not textgrids:
        raise RuntimeError(
            "MFA finished without error, but did not generate any TextGrid.\n"
            f"Debug folder: {tmpdir}\n"
            f"MFA STDOUT:\n{result.stdout}\n"
            f"MFA STDERR:\n{result.stderr}\n"
        )

    final_tg = Path(tempfile.mkstemp(prefix="acousa_mfa_", suffix=".TextGrid")[1])
    shutil.copy2(textgrids[0], final_tg)

    # If everything goes well, clean up the temporary debug folder.
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

    # Fallback: if MFA changes the tier name, use the tier with the most non-empty intervals.
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

    # Fallback: look for a tier that looks like a phones tier
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

    # Simple estimate: vowel groups. Enough for global rates.
    groups = re.findall(r"[aeiouáéíóúü]+", word)
    return max(1, len(groups))


def estimate_syllables_spanish(text: str) -> int:
    words = clean_for_mfa(text).split()
    return sum(count_syllables_spanish_word(w) for w in words)

LEXICAL_UPOS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}

SUBORDINATE_DEPREL_PREFIXES = (
    "advcl",      # adverbial clause
    "ccomp",      # finite complement clause
    "xcomp",      # open complement / controlled infinitive
    "acl",        # adnominal clause
    "csubj",      # clausal subject
)


def _norm_lemma(lemma: str) -> str:
    lemma = (lemma or "").strip().lower()
    lemma = re.sub(r"\s+", " ", lemma)
    return lemma

DATAMUSE_ENDPOINT = "https://api.datamuse.com/words"

FREQ_CATEGORIES = [
    "very frequent",
    "quite frequent",
    "medium frequency",
    "infrequent",
    "very rare",
]


def datamuse_frequency_category(freq_per_million: float | None) -> str:
    """
    Categories based on frequency per million.
    The lower the frequency, the rarer/more complex the lemma.
    """
    if freq_per_million is None:
        return "very rare"

    if freq_per_million >= 100:
        return "very frequent"
    if freq_per_million >= 10:
        return "quite frequent"
    if freq_per_million >= 1:
        return "medium frequency"
    if freq_per_million >= 0.1:
        return "infrequent"
    return "very rare"


def frequency_category_score(category: str) -> int:
    """
    RLE scale:
      1 = very frequent lemmas
      5 = very infrequent lemmas

    It is an experimental measure of estimated lexical richness/singularity,
    not a normative clinical measure.
    """
    mapping = {
        "very frequent": 1,
        "quite frequent": 2,
        "medium frequency": 3,
        "infrequent": 4,
        "very rare": 5,
    }
    return mapping.get(category, 5)


def lexical_complexity_label_from_score(score: float | None) -> str:
    if score is None:
        return "not calculable"

    if score < 1.5:
        return "very frequent vocabulary"
    if score < 2.5:
        return "quite frequent vocabulary"
    if score < 3.5:
        return "medium-frequency vocabulary"
    if score < 4.5:
        return "infrequent vocabulary"
    return "very infrequent vocabulary"

def _clamp_float(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def rle_score_tail_sensitive(
    token_scores: list[int],
    unique_scores: list[int],
    lexical_ttr: float,
    lexical_tokens: int,
) -> float | None:
    """
    RLE = Estimated Lexical Richness, scale 1-5.

    This version is sensitive to short texts and to the lexical tail:
    it does not only look at the mean, but also at whether infrequent
    or very infrequent lemmas appear.

    1 = very frequent vocabulary
    5 = very infrequent / highly marked vocabulary
    """
    if not token_scores or not unique_scores:
        return None

    token_arr = np.array(token_scores, dtype=float)
    unique_arr = np.array(unique_scores, dtype=float)

    # Normalize 1-5 to 0-1
    mean_unique_norm = (float(np.mean(unique_arr)) - 1.0) / 4.0

    # Lexical tail: high percentile of rarity.
    # This makes very infrequent words weigh more in short texts.
    p90_unique_norm = (float(np.percentile(unique_arr, 90)) - 1.0) / 4.0

    rare_unique_prop = float(np.mean(unique_arr >= 4.0))
    very_rare_unique_prop = float(np.mean(unique_arr >= 5.0))

    # Rarity pressure: sqrt makes 20-30% of rare lemmas already weigh quite a lot.
    rare_pressure = np.sqrt(rare_unique_prop)
    very_rare_pressure = np.sqrt(very_rare_unique_prop)

    # Lexical TTR: in short texts it is usually informative, but we do not want it to dominate.
    ttr_norm = _clamp_float(float(lexical_ttr), 0.0, 1.0)

    # Experimental formula: more sensitive to marked vocabulary.
    rle_norm = (
        0.48 * p90_unique_norm
        + 0.18 * mean_unique_norm
        + 0.22 * rare_pressure
        + 0.07 * very_rare_pressure
        + 0.05 * ttr_norm
    )

    rle = 1.0 + 4.0 * rle_norm

    # Moderate bonus for short texts if they have a clear proportion of rare lemmas.
    # This prevents short, lexically marked texts from ending up artificially low.
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
    Queries Datamuse for a lemma.
    Returns a robust dict so the app does not break if the API fails.
    """
    lemma = (lemma or "").strip().lower()

    if not lemma:
        return {
            "datamuse_status": "empty_lemma",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "very rare",
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
            "frequency_category": "very rare",
        }
    except Exception as e:
        return {
            "datamuse_status": f"api_error: {e}",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "very rare",
        }

    if not isinstance(data, list) or not data:
        return {
            "datamuse_status": "not_found",
            "datamuse_word": "",
            "datamuse_frequency_per_million": None,
            "frequency_category": "very rare",
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
    Returns:
      - syntactic/lexical metrics for the CSV
      - detailed lemma payload to save as JSON .txt
    """
    try:
        import stanza
    except Exception as e:
        raise RuntimeError(
            "Could not import Stanza. Install stanza in the app's .venv."
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
        category_token_counts["infrequent"] + category_token_counts["very rare"]
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
                "Experimental index sensitive to the lexical tail. It combines the 90th percentile of "
                "lemma rarity, the mean of categories, the proportion of infrequent or very infrequent "
                "lemmas, the proportion of very infrequent lemmas and the lexical TTR. "
                "It is tuned so as not to underestimate short texts."
            ),
            "rare_or_very_rare_lexical_tokens_percent": round(lexical_complexity_rare_percent, 4),
            "mean_datamuse_frequency_per_million": (
                round(mean_datamuse_frequency_per_million, 4)
                if mean_datamuse_frequency_per_million is not None else None
            ),
            "frequency_categories": {
                "very frequent": ">= 100 occurrences per million",
                "quite frequent": "10-99.99 occurrences per million",
                "medium frequency": "1-9.99 occurrences per million",
                "infrequent": "0.1-0.99 occurrences per million",
                "very rare": "< 0.1 occurrences per million or not found",
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

    # Speech segment duration: from the first MFA sound to the last.
    # Includes internal pauses.
    speech_duration = max(voice_end - voice_start, 0.0)

    # Articulated time: sum of the duration of the non-silent sounds in the phones tier.
    # Excludes empty/silent intervals.
    articulation_duration = sum(
        max(xmax - xmin, 0.0)
        for xmin, xmax, _ in phone_intervals
    )

    # Pauses: empty/silent intervals in the phones tier within the speech segment.
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

    # Rates in sounds per second, not syllables per second.
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
        raise RuntimeError("Whisper did not generate a transcription. Cannot align with MFA.")

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

        # Save the final path, not the temporary one
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