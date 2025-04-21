from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transcribe import transcribe_audio
from rewrite import rewrite_text
import os
from dotenv import load_dotenv
from utils import log_interaction, convert_to_wav
from typing import List
import shutil
import uuid

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TONES = ["confident", "polite", "concise"]

@app.post("/process/")
async def process_audio(
    file: UploadFile = File(...),
    tone: str = Form(...)
):
    if tone.lower() not in ALLOWED_TONES:
        raise HTTPException(status_code=400, detail=f"Invalid tone: {tone}. Allowed tones: {ALLOWED_TONES}")

    if not file.filename.endswith((".wav", ".mp3", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported audio format. Use .wav, .mp3, or .m4a")

    temp_id = str(uuid.uuid4())
    input_path = f"temp_{temp_id}_{file.filename}"
    wav_path = input_path.replace(".m4a", ".wav")

    try:
        # Save uploaded audio
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert if necessary
        if input_path.endswith(".m4a"):
            convert_to_wav(input_path, wav_path)
            os.remove(input_path)
        else:
            wav_path = input_path

        # Transcribe
        transcript = transcribe_audio(wav_path)

        # Rewrite
        rewritten = rewrite_text(transcript, tone)

        # Log this request
        log_interaction(tone, transcript, rewritten)

        return {
            "original": transcript,
            "rewritten": rewritten,
            "tone": tone
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
