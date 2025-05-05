import os
import subprocess
from TTS.api import TTS

# Initialize your model once
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

def synthesize_speech(text, output_path):
    base, ext = os.path.splitext(output_path)
    temp_wav = base + ".wav"

    # Save speech to temp wav file
    tts_model.tts_to_file(text=text, file_path=temp_wav)

    # Convert to user’s original format
    if ext != ".wav":
        subprocess.run(["ffmpeg", "-y", "-i", temp_wav, output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(temp_wav)
    else:
        os.rename(temp_wav, output_path)
