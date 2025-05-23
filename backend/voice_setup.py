# voice_setup.py
import os
import shutil
import uuid
import torch
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from utils import convert_to_wav

router = APIRouter()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINTS_DIR = "/home/gbarbosa9/OpenVoice/checkpoints"
SE_DIR = os.path.join(BASE_DIR, "se_cache")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
USER_AUDIO_DIR = os.path.join(BASE_DIR, "audio_cache", "users")
os.makedirs(SE_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(USER_AUDIO_DIR, exist_ok=True)

# Load the tone color converter once
tone_color_converter = ToneColorConverter(
    config_path=os.path.join(CHECKPOINTS_DIR, "converter", "config.json"),
    device="cuda" if torch.cuda.is_available() else "cpu"
)
tone_color_converter.load_ckpt(os.path.join(CHECKPOINTS_DIR, "converter", "checkpoint.pth"))

# Upload prompt audio files for multi-sentence setup
@router.post("/voice")
async def upload_prompt_audio(
    user_id: str = Form(...),
    prompt_id: str = Form(...),
    file: UploadFile = File(...)
):
    user_dir = os.path.join(USER_AUDIO_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, f"{prompt_id}.wav")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"{prompt_id} saved for {user_id}"}

# Finalize the embedding from recorded prompts
@router.post("/complete")
async def finalize_embedding(user_id: str = Form(...)):
    user_dir = os.path.join(USER_AUDIO_DIR, user_id)
    audio_paths = [os.path.join(user_dir, f) for f in os.listdir(user_dir) if f.endswith(".wav")]
    audio_paths.sort()  # optional consistency

    if not audio_paths:
        raise HTTPException(status_code=400, detail="No prompt audio found")

    try:
        se_path = os.path.join(SE_DIR, f"{user_id}_se.pth")
        print(f"[INFO] Extracting SE for {user_id}...")
        se, _ = se_extractor.get_se(audio_paths, tone_color_converter, vad=True)
        torch.save(se, se_path)

        preview_path = os.path.join(AUDIO_DIR, f"preview_{user_id}.wav")
        dummy_text = "This is a preview of your cloned voice."

        from voice_cloning import synthesize_cloned_speech
        synthesize_cloned_speech(
            ref_audio_path=audio_paths[0],  # or average, or concat
            text=dummy_text,
            output_path=preview_path,
            user_id=user_id,
            setup_only=True
        )

        return {"message": "Speaker embedding created", "preview": f"/voice-preview/{user_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

# Serve preview audio
@router.get("/preview/{user_id}")
def serve_voice_preview(user_id: str):
    preview_path = os.path.join(AUDIO_DIR, f"preview_{user_id}.wav")
    if not os.path.exists(preview_path):
        raise HTTPException(status_code=404, detail="Preview not found")

    return FileResponse(preview_path, media_type="audio/wav")

# Check if a user has a speaker embedding
@router.get("/has-setup")
def has_voice_setup(user_id: str):
    se_path = os.path.join(SE_DIR, f"{user_id}_se.pth")
    return {"user_id": user_id, "has_voice_setup": os.path.exists(se_path)}
