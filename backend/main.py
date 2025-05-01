from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from transcribe import transcribe_audio
from rewrite import rewrite_text
from tts_speech import synthesize_speech
from utils import log_interaction, convert_to_wav
import os
import shutil
import uuid
from dotenv import load_dotenv
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI()

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

@app.get("/files/{filename}")
def get_audio_file(filename: str):
    file_path = f"./{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/wav")

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
    input_path = f"temp_{temp_id}_{file.filename}"
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    output_audio_path = f"rewritten_{temp_id}.wav"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if not input_path.endswith(".wav"):
            convert_to_wav(input_path, wav_path)
            os.remove(input_path)
        else:
            wav_path = input_path

        transcript = transcribe_audio(wav_path)
        rewritten = rewrite_text(transcript, tone.value)
        synthesize_speech(rewritten, output_audio_path)
        log_interaction(tone.value, transcript, rewritten)

        return {
            "original": transcript,
            "rewritten": rewritten,
            "tone": tone.value,
            "audio_url": f"/files/{output_audio_path}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
