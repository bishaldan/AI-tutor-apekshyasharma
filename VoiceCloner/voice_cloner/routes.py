from flask import Blueprint, render_template, request, url_for, jsonify, send_from_directory
from voice_cloner.tts_model import synthesize_voice
from voice_cloner.utils import ensure_wav, save_upload
import os
import uuid
import shutil  # added

main = Blueprint("main", __name__)

# Use absolute paths rooted at the project directory (one level up from this file)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
LATEST_REFERENCE_PATH = os.path.join(UPLOAD_FOLDER, "latest_reference.wav")

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@main.route("/", methods=["GET"])
def index():
    # Serve UI
    return render_template("index.html")


@main.route("/upload_audio", methods=["POST"])
def upload_audio():
    """
    Accepts a recorded audio blob (e.g., webm/ogg/wav), optional text, emotion, task, language.
    Returns JSON with a URL to the generated audio.
    """
    try:
        if "audio" not in request.files:
            return jsonify({"ok": False, "error": "Missing 'audio' file field"}), 400

        file = request.files["audio"]
        text = request.form.get("text") or "Hello! This is your cloned voice."
        emotion = request.form.get("emotion")
        task = request.form.get("task") or "default"
        language = request.form.get("language") or "en"

        # Save upload and ensure WAV for the model
        saved_path = save_upload(file, UPLOAD_FOLDER)
        wav_input = ensure_wav(saved_path)

        # Always store latest recorded voice as the reference
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        shutil.copyfile(wav_input, LATEST_REFERENCE_PATH)

        # Generate unique output filename
        out_name = f"cloned_{uuid.uuid4().hex}.wav"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Synthesize using the just-recorded reference
        synthesize_voice(
            input_audio_path=wav_input,
            output_path=out_path,
            text=text,
            emotion=emotion,
            task=task,
            language=language,
        )

        audio_url = url_for("main.serve_output", filename=out_name)
        return jsonify({"ok": True, "audioUrl": audio_url}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/generate_text", methods=["POST"])
def generate_text():
    """
    Accepts JSON: { text, emotion?, task?, language? }
    Uses the latest recorded reference voice for multi-speaker TTS.
    """
    try:
        data = request.get_json(force=True, silent=False) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "Field 'text' is required"}), 400

        # Validate stored reference first
        if not os.path.exists(LATEST_REFERENCE_PATH):
            return jsonify({"ok": False, "error": "Please record your voice first."}), 400

        emotion = data.get("emotion")
        task = data.get("task") or "default"
        language = data.get("language") or "en"

        out_name = f"tts_{uuid.uuid4().hex}.wav"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Always use the stored reference voice for text synthesis
        synthesize_voice(
            input_audio_path=LATEST_REFERENCE_PATH,
            output_path=out_path,
            text=text,
            emotion=emotion,
            task=task,
            language=language,
        )

        audio_url = url_for("main.serve_output", filename=out_name)
        return jsonify({"ok": True, "audioUrl": audio_url}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@main.route("/outputs/<path:filename>", methods=["GET"])
def serve_output(filename: str):
    """
    Serve generated audio files.
    """
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False, mimetype="audio/wav")