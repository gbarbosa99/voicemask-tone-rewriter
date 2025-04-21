from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from transcribe import transcribe_audio
from rewrite import rewrite_text
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post('/process/')
async def process_audio(
    file: UploadFile = File(...),
    tone: str = Form(...)
):
    temp_path = f"temp_{file_name}"

    with open(temp_path, 'wb') as buffer:
        buffer.write(await file.read())

    transcript = transcribe_audio(temp_path)

    rewritten = rewrite_text(transcript, tone)

    os.remove(temp_path)

    return {
        "original": transcript,
        "rewritten": rewritten
    } 