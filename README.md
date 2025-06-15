# VoiceMask

**VoiceMask** is an AI-powered web application that transforms the tone of your speech — while keeping your voice.

## Overview

VoiceMask lets users upload an audio file (e.g., a sentence or short paragraph), choose a tone (e.g., confident, polite), and returns a rewritten version of their speech in the selected tone. The final version of the app will play this back using voice cloning, so users can hear *themselves* speaking with more confidence or professionalism.

## Key Features

* Upload your own voice as an audio clip
* Select a tone like "confident", "polite", or "encouraging"
* Transcribe using [Whisper-small](https://github.com/openai/whisper)
* Rewrite text using [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1) or GPT-3.5
* (Coming Soon) Generate rewritten speech in the **user's own voice** using [OpenVoice](https://github.com/myshell-ai/OpenVoice) or [Tortoise TTS](https://github.com/neonbjb/tortoise-tts)

## Getting Started

### Prerequisites

* Python 3.10+
* Docker
* Git

### Clone the repository

```bash
git clone https://github.com/gbarbosa99/voicemask-tone-rewriter.git
cd voicemask-tone-rewriter
```

### Option A: Run with Docker (Recommended)

```bash
cd backend
docker build -t voicemask-backend .
docker run -d -p 8000:8000 voicemask-backend
```

Visit: `http://localhost:8000/docs`

### Option B: Run Locally (Dev Mode)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m unidic download
uvicorn main:app --reload
```

## Model Weights

If you aren't using Docker, you will need to manually download the OpenVoice weights. You can find them on the [Releases](https://github.com/gbarbosa99/voicemask-tone-rewriter/releases) page.

Using Docker handles this automatically during the build step.

## Folder Structure

```bash
voicemask-tone-rewriter/
├── backend/
│   ├── main.py
│   ├── transcribe.py
│   ├── rewrite.py
│   ├── utils.py
│   ├── voice_setup.py
│   ├── voice_cloning.py
│   ├── openvoice/
│   └── Openvoice/
│       └── checkpoints/
├── frontend/
│   └── ... (Flutter app)
├── requirements.txt
└── README.md
```

## Usage Example

```bash
curl -X POST "http://localhost:8000/process/" \
  -F "file=@my_audio.wav" \
  -F "tone=confident" \
  -F "user_id=user123"
```

## Roadmap
 
* [x] Transcription & Tone Rewriting
* [ ] Voice cloning output
* [ ] iOS integration
* [ ] iMessage app extension

## Contributing

Contributions are welcome! Please open an issue or pull request if you'd like to get involved.
