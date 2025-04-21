from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from transcribe import transcribe_audio
from rewrite import rewrite_text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("DEBUG:", os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Flutter web origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process/")
async def process_audio(
    file: UploadFile = File(...),
    tone: str = Form(...)
):
    temp_path = f"temp_{file.filename}"

    # Save uploaded audio file
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Step 1: Transcribe audio with Whisper
        transcript = transcribe_audio(temp_path)

        # Step 2: Rewrite using GPT
        rewritten = rewrite_text(transcript, tone)

        # Step 3: Return the results
        return {
            "original": transcript,
            "rewritten": rewritten
        }

    finally:
        # Always delete the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
