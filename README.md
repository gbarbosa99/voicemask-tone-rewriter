# VoiceMask
**VoiceMask** is an AI-powered web application that transforms the tone of your speech — while keeping your voice.

## Overview

VoiceMask lets users upload an audio file (e.g., a sentence or short paragraph), choose a tone (e.g., confident, polite), and returns a rewritten version of their speech in the selected tone. The final version of the app will play this back using voice cloning, so users can hear *themselves* speaking with more confidence or professionalism.

## Key Features

- 🎙 Upload your own voice as an audio clip
- Select a tone like "confident", "polite", or "encouraging"
- Transcribe using [Whisper-small](https://github.com/openai/whisper)
- Rewrite text using [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1) or GPT-3.5
- (Coming Soon) Generate rewritten speech in the **user's own voice** using [OpenVoice](https://github.com/myshell-ai/OpenVoice) or [Tortoise TTS](https://github.com/neonbjb/tortoise-tts)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Flutter Web |
| Backend | FastAPI (Python 3.10) |
| Transcription | Whisper-small |
| Tone Rewriting | Mistral-7B / GPT-3.5 |
| TTS (Planned) | OpenVoice / Tortoise TTS |

## Folder Structure

