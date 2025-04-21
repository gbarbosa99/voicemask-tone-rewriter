import whisper

# Load Whisper model once
model = whisper.load_model("base")  # You can change to "tiny" for speed

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]
