import os
from TTS.api import TTS

# Load the model once at startup
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", gpu=False)

# Default language for the multilingual model
DEFAULT_LANGUAGE = "en"

# Supported languages for the loaded YourTTS model and some aliases
SUPPORTED_LANGS = {"en", "fr-fr", "pt-br"}
LANGUAGE_ALIASES = {
    "fr": "fr-fr",
    "fr_fr": "fr-fr",
    "fr-fr": "fr-fr",
    "fr-FR": "fr-fr",
    "pt": "pt-br",
    "pt_br": "pt-br",
    "pt-br": "pt-br",
    "pt-BR": "pt-br",
    "en": "en",
    "en-us": "en",
    "en-us": "en",
    "en-gb": "en",
    "en-GB": "en",
    # Fallback mappings for unsupported languages
    "es": "en",
    "de": "en",
    "it": "en",
}


def _normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE
    key = language.strip().lower().replace(" ", "").replace("_", "-")
    # Try alias map, then accept only supported; fallback to default
    lang = LANGUAGE_ALIASES.get(key, key)
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANGUAGE


def _apply_style(text: str, emotion: str | None, task: str | None) -> str:
    """
    Prefix the text with simple cues that can help guide prosody.
    Example: "[happy][assistant] Hello world"
    """
    cues = ""
    if emotion:
        cues += f"[{emotion.strip()}]"
    if task and task != "default":
        cues += f"[{task.strip()}]"
    return f"{cues} {text}".strip()


def synthesize_voice(
    input_audio_path: str | None,
    output_path: str,
    text: str,
    emotion: str | None = None,
    task: str | None = "default",
    language: str | None = DEFAULT_LANGUAGE,
):
    """
    Generate speech using Coqui YourTTS.

    - If input_audio_path is provided, perform voice cloning using it as speaker_wav.
    - If input_audio_path is None, select a default built-in speaker (e.g., "p273").
    - Emotion and task are added as bracketed cues to influence style.

    Args:
        input_audio_path: Path to reference audio for cloning, or None.
        output_path: Destination WAV path.
        text: Text to synthesize.
        emotion: Optional emotion cue (e.g., 'happy', 'sad', ...).
        task: Optional task cue (e.g., 'assistant', 'storytelling', ...).
        language: ISO language code for multilingual model (default "en").
    """
    styled_text = _apply_style(text, emotion, task)
    lang = _normalize_language(language)

    # Validate file paths when a reference is provided
    if input_audio_path is not None and not os.path.exists(input_audio_path):
        raise FileNotFoundError(f"Reference voice not found at: {input_audio_path}")

    tts.tts_to_file(
        text=styled_text,
        file_path=output_path,
        speaker_wav=input_audio_path if input_audio_path else None,
        speaker="p273" if input_audio_path is None else None,
        language=lang,
    )

    return output_path
