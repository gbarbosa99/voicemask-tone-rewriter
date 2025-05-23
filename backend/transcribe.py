# transcribe.py
import whisper
import os

# Load model once
model = whisper.load_model("base")  # or "medium", "large", etc.

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes speech from a WAV audio file into text.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: The transcribed text.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[INFO] Transcribing {audio_path} ...")
    result = model.transcribe(audio_path)
    text = result.get("text", "").strip()

    print(f"[INFO] Transcription complete: {text}")
    return text
