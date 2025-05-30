# voice_setup.py (updated to respect consent)
import os
import shutil
import torch
from typing import Optional
from datetime import datetime
from pydub import AudioSegment
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import FileResponse
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from utils import convert_to_wav, ensure_dir
from voice_cloning import synthesize_cloned_speech

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINTS_DIR = os.path.join(BASE_DIR, "OpenVoice", "checkpoints")
SE_DIR = os.path.join(BASE_DIR, "se_cache")
USER_AUDIO_DIR = os.path.join(BASE_DIR, "audio_cache", "users")
PREVIEWS_DIR = os.path.join(BASE_DIR, "audio_cache", "previews")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
CONSENT_LOG = os.path.join(BASE_DIR, "consent_log.txt")

os.makedirs(SE_DIR, exist_ok=True)
os.makedirs(USER_AUDIO_DIR, exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load model once
converter = ToneColorConverter(
    config_path=os.path.join(CHECKPOINTS_DIR, "converter", "config.json"),
    device="cuda" if torch.cuda.is_available() else "cpu"
)
converter.load_ckpt(os.path.join(CHECKPOINTS_DIR, "converter", "checkpoint.pth"))

@router.post("/consent")
def store_user_consent(user_id: str = Form(...), consent: Optional[bool] = Form(False)):
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not given")

    try:
        with open(CONSENT_LOG, "a") as f:
            f.write(f"{user_id},{datetime.now().isoformat()}\n")
        return {"message": "Consent recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record consent: {str(e)}")

@router.post("/voice")
async def upload_prompt_audio(
    user_id: str = Form(...),
    prompt_id: str = Form(...),
    file: UploadFile = File(...)
):
    user_dir = os.path.join(USER_AUDIO_DIR, user_id)
    ensure_dir(user_dir)

    file_path = os.path.join(user_dir, f"{prompt_id}.wav")
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save {prompt_id}: {str(e)}")

    return {"message": f"{prompt_id} saved for {user_id}"}

@router.post("/complete")
async def finalize_embedding(user_id: str = Form(...), consent: Optional[bool] = Form(False)):
    user_dir = os.path.join(USER_AUDIO_DIR, user_id)
    audio_paths = [os.path.join(user_dir, f) for f in sorted(os.listdir(user_dir)) if f.endswith(".wav")]

    if not audio_paths:
        raise HTTPException(status_code=400, detail="No prompt audio found")

    try:
        # Concatenate all prompt files
        combined = AudioSegment.empty()
        for wav_file in audio_paths:
            combined += AudioSegment.from_wav(wav_file)

        combined_path = os.path.join(user_dir, "combined.wav")
        combined.export(combined_path, format="wav")

        # Extract speaker embedding
        print(f"[INFO] Extracting SE for {user_id}...")
        se = se_extractor.get_se(combined_path, from_path=True)

        # Conditionally save embedding and log consent
        if consent:
            se_path = os.path.join(SE_DIR, f"{user_id}_se.pth")
            torch.save(se, se_path)
            with open(CONSENT_LOG, "a") as f:
                f.write(f"{user_id},{datetime.now().isoformat()}\n")

        # Generate preview audio
        preview_path = os.path.join(PREVIEWS_DIR, f"{user_id}.wav")
        dummy_text = "This is a preview of your cloned voice."

        synthesize_cloned_speech(
            reference_speaker=se,
            text=dummy_text,
            output_path=preview_path,
            converter=converter
        )

        return {"message": "Speaker embedding created", "preview": f"/preview/{user_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@router.get("/preview/{user_id}")
def serve_voice_preview(user_id: str):
    preview_path = os.path.join(PREVIEWS_DIR, f"{user_id}.wav")
    if not os.path.exists(preview_path):
        raise HTTPException(status_code=404, detail="Preview not found")

    return FileResponse(preview_path, media_type="audio/wav")

@router.get("/has-setup")
def has_voice_setup(user_id: str = Query(...)):
    path = os.path.join(SE_DIR, f"{user_id}_se.pth")
    if os.path.exists(path):
        return {"user_id": user_id, "has_voice_setup": True}
    return {"user_id": user_id, "has_voice_setup": False}
