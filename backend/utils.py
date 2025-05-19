from pydub import AudioSegment
from datetime import datetime
import json

def convert_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format='wav')

def log_interaction(tone, input_text, output_text, path="history.jsonl"):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "tone": tone,
        "input": input_text,
        "output": output_text
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")