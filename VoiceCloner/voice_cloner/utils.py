import os
from typing import Optional
from werkzeug.utils import secure_filename
import soundfile as sf

try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None  # Optional fallback if pydub/ffmpeg is not available

# New: detect ffmpeg/ffprobe and configure pydub, especially for Conda on Windows
from shutil import which


def _configure_pydub_for_ffmpeg():
    """
    Ensure pydub knows where ffmpeg and ffprobe are.
    Tries PATH first; if missing, tries to resolve from the current Conda env.
    """
    if not AudioSegment:
        return

    def exists(p: Optional[str]) -> bool:
        return bool(p) and os.path.isfile(p)

    has_ffmpeg = which("ffmpeg") is not None or exists(getattr(AudioSegment, "converter", None))
    has_ffprobe = which("ffprobe") is not None or exists(getattr(AudioSegment, "ffprobe", None))

    if has_ffmpeg and has_ffprobe:
        return

    # Try to locate in Conda env (Windows: <env>\Library\bin\ffmpeg.exe)
    conda_prefix = os.environ.get("CONDA_PREFIX") or os.environ.get("VIRTUAL_ENV")
    if conda_prefix:
        ffmpeg_path = os.path.join(conda_prefix, "Library", "bin", "ffmpeg.exe")
        ffprobe_path = os.path.join(conda_prefix, "Library", "bin", "ffprobe.exe")
        if exists(ffmpeg_path):
            AudioSegment.converter = ffmpeg_path
        if exists(ffprobe_path):
            AudioSegment.ffprobe = ffprobe_path


# Configure once on import
_configure_pydub_for_ffmpeg()


def convert_to_wav(input_file: str, output_file: str):
    """Convert an audio file to WAV using soundfile; fallback to pydub if needed."""
    try:
        data, samplerate = sf.read(input_file)
        sf.write(output_file, data, samplerate)
    except Exception:
        if not AudioSegment:
            raise RuntimeError(
                "Audio conversion failed and pydub is unavailable. Install pydub and ffmpeg."
            )
        # Ensure pydub has ffmpeg/ffprobe configured
        _configure_pydub_for_ffmpeg()

        def _exists(p: Optional[str]) -> bool:
            return bool(p) and os.path.isfile(p)

        has_ffmpeg = which("ffmpeg") is not None or _exists(getattr(AudioSegment, "converter", None))
        has_ffprobe = which("ffprobe") is not None or _exists(getattr(AudioSegment, "ffprobe", None))
        if not (has_ffmpeg and has_ffprobe):
            raise RuntimeError(
                "Audio conversion requires ffmpeg and ffprobe. "
                "Install via: conda install -c conda-forge ffmpeg, or add them to PATH, then restart the app."
            )

        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav")


def ensure_wav(input_path: str) -> str:
    """Return a WAV path for the given audio, converting if necessary."""
    _, ext = os.path.splitext(input_path)
    if ext.lower() == ".wav":
        return input_path
    wav_path = os.path.splitext(input_path)[0] + ".wav"
    convert_to_wav(input_path, wav_path)
    return wav_path


def save_upload(file_storage, dest_dir: str) -> str:
    """Save an uploaded file safely with a unique name and return its path."""
    os.makedirs(dest_dir, exist_ok=True)
    base = secure_filename(file_storage.filename or "recording")
    name, ext = os.path.splitext(base)
    if not ext:
        ext = ".webm"  # default for MediaRecorder blobs
    filename = f"{name}_{os.getpid()}_{str(abs(hash(base)))[:6]}{ext}"
    path = os.path.join(dest_dir, filename)
    file_storage.save(path)
    return path
