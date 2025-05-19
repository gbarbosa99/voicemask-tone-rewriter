from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from transcribe import transcribe_audio
from rewrite import rewrite_text
from utils import log_interaction, convert_to_wav
import os
import re
import subprocess
from datetime import datetime
import shutil
import uuid
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from unidecode import unidecode

load_dotenv()

app = FastAPI()

def synthesize_cloned_voice_subprocess(ref_audio, text, output_audio_path):
    subprocess.run([
        "conda", "run", "-n", "openvoice", "python", "voice_cloning_cli.py",
        "--ref", ref_audio,
        "--text", text,
        "--out", output_audio_path
    ])


# Allow frontend access (you can restrict origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define tone options using Enum for type safety + Swagger UI dropdown support
class ToneEnum(str, Enum):
    confident = "confident"
    polite = "polite"
    concise = "concise"

# Expose tone options to Flutter app
@app.get("/tones/")
def get_tones():
    return [tone.value for tone in ToneEnum]

@app.post("/process/")
async def process_audio(
    file: UploadFile = File(...),
    tone: ToneEnum = Form(...)
):
    allowed_extensions = (".wav", ".mp3", ".m4a", ".mp4")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format. Use .wav, .mp3, .m4a, or .mp4"
        )

    temp_id = str(uuid.uuid4())

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    AUDIO_DIR = os.path.join(BASE_DIR, "audio")
    os.makedirs(AUDIO_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1].lower()
    input_path = f"temp_{temp_id}{ext}"
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"

    os.makedirs("audio", exist_ok=True)
    output_audio_path = os.path.join(AUDIO_DIR, f"rewritten_{temp_id}.wav")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if ext != ".wav":
            convert_to_wav(input_path, wav_path)
            os.remove(input_path)
        else:
            wav_path = input_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        print("==> Running transcription")
        transcript = transcribe_audio(wav_path)
        print("Transcription result:", transcript)

        print("==> Running rewrite")
        rewritten = rewrite_text(transcript, tone.value)
        print("Rewritten result:", rewritten)

        print("==> Sanitizing text for TTS")
        safe_text = unidecode(rewritten)
        safe_text = re.sub(r"[^a-zA-Z0-9 .,?!'\"-]", "", safe_text)
        safe_text = safe_text.strip()[:300]
        print("Sanitized text for TTS:", safe_text)

        try:
            synthesize_cloned_voice_subprocess(wav_path, safe_text, output_audio_path)
            audio_url = f"/files/audio/rewritten_{temp_id}.wav"

        except Exception as e:
            print("TTS failed:", e)
            audio_url = None

        print("==> Logging interaction and returning response")
        log_interaction(tone.value, transcript, rewritten)

        return {
            "original": transcript,
            "rewritten": rewritten,
            "tone": tone.value,
            "audio_url": audio_url
        }

    except Exception as e:
        print("Error in /process/:", str(e))  # <-- this will print the actual backend error
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

@app.get("/files/{file_path:path}")
def get_audio_file(file_path: str):
    file_path = os.path.join("audio", file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = file_path.split(".")[-1].lower()
    media_type = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "mp4": "audio/mp4"
    }.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type)
