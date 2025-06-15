# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from enum import Enum
import os
import re
import uuid
from unidecode import unidecode  # type: ignore

from transcribe import transcribe_audio
from rewrite import rewrite_text
from utils import log_interaction, convert_to_wav
from voice_cloning import synthesize_cloned_speech
from voice_setup import router as voice_setup_router

app = FastAPI()
app.include_router(voice_setup_router, prefix="/setup") 

# Allow frontend access (you can restrict origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define tone options using Enum
class ToneEnum(str, Enum):
    confident = "confident"
    polite = "polite"
    concise = "concise"

@app.get("/tones/")
def get_tones():
    return [tone.value for tone in ToneEnum]

@app.post("/process/")
async def process_audio(
    file: UploadFile = File(...),
    tone: ToneEnum = Form(...),
    user_id: str = Form(...)
):
    ext = os.path.splitext(file.filename)[1].lower()
    temp_id = str(uuid.uuid4())
    input_path = f"temp_{temp_id}{ext}"
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    output_path = f"audio/rewritten_{temp_id}.wav"
    os.makedirs("audio", exist_ok=True)

    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())

        if ext != ".wav":
            convert_to_wav(input_path, wav_path)
            os.remove(input_path)
        else:
            wav_path = input_path

        original = transcribe_audio(wav_path)
        rewritten = rewrite_text(original, tone.value)

        safe_text = unidecode(rewritten)
        safe_text = re.sub(r"[^a-zA-Z0-9 .,?!'\"-]", "", safe_text).strip()[:300]

        synthesize_cloned_speech(wav_path, safe_text, output_path, user_id)
        log_interaction(tone.value, original, rewritten)

        return {
            "original": original,
            "rewritten": rewritten,
            "tone": tone.value,
            "audio_url": f"/files/{os.path.basename(output_path)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

@app.get("/files/{file_path:path}")
def get_audio_file(file_path: str):
    full_path = os.path.join("audio", file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = file_path.split(".")[-1].lower()
    media_type = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "mp4": "audio/mp4"
    }.get(ext, "application/octet-stream")

    return FileResponse(full_path, media_type=media_type)