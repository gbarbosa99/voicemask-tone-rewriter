# transcribe.py
import whisper
import os

# Lazy-loaded model (initialized as None)
model = None
WHISPER_MODEL_SIZE = "tiny"  # or "base" — smaller models for t2.micro

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes speech from a WAV audio file into text.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: The transcribed text.
    """
    global model

    if model is None:
        print(f"[INFO] Loading Whisper model ({WHISPER_MODEL_SIZE}) ...")
        model = whisper.load_model(WHISPER_MODEL_SIZE)
        print(f"[INFO] Model loaded.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[INFO] Transcribing {audio_path} ...")
    result = model.transcribe(audio_path)
    text = result.get("text", "").strip()

    print(f"[INFO] Transcription complete: {text}")
    return text
