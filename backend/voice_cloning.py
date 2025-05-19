import os
import torch
import tempfile

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS as MeloTTS


# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Resolve base directory (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute paths to checkpoints
CHECKPOINTS_DIR = "/home/gbarbosa9/OpenVoice/checkpoints"

CONVERTER_DIR = os.path.join(CHECKPOINTS_DIR, "converter")
BASE_SPEAKER_SE_DIR = os.path.join(CHECKPOINTS_DIR, "base_speakers", "ses")

print("[DEBUG] Checking path:", os.path.join(CONVERTER_DIR, "config.json"))

assert os.path.exists(os.path.join(CONVERTER_DIR, "config.json")), "config.json not found"
assert os.path.exists(os.path.join(CONVERTER_DIR, "checkpoint.pth")), "checkpoint.pth not found"

# Load tone color converter
tone_color_converter = ToneColorConverter(
    os.path.join(CONVERTER_DIR, "config.json"),
    device=device
)
tone_color_converter.load_ckpt(os.path.join(CONVERTER_DIR, "checkpoint.pth"))

# Optional: cache speaker embeddings
SE_CACHE = {}

def synthesize_cloned_speech(ref_audio_path, text, output_path):
    print(f"[INFO] Synthesizing cloned speech to: {output_path}")
    
    # Get target speaker embedding
    if ref_audio_path in SE_CACHE:
        print("[INFO] Using cached speaker embedding.")
        target_se = SE_CACHE[ref_audio_path]
    else:
        print("[INFO] Extracting speaker embedding...")
        target_se, _ = se_extractor.get_se(
            ref_audio_path,
            tone_color_converter,
            target_dir=os.path.join(BASE_DIR, "processed"),
            vad=True
        )
        SE_CACHE[ref_audio_path] = target_se

    # Use MeloTTS to create base neutral voice
    print("[INFO] Synthesizing base neutral voice...")
    base_tts = MeloTTS(language="EN", device=device)
    speaker_ids = base_tts.hps.data.spk2id
    speaker_key = list(speaker_ids.keys())[0]  # Use default speaker
    speaker_id = speaker_ids[speaker_key]

    # Create a temporary file for neutral audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        tmp_path = tmp_wav.name

    base_tts.tts_to_file(text, speaker_id, tmp_path, speed=1.0)

    # Run voice cloning
    print("[INFO] Applying tone color conversion...")
    tone_color_converter.convert(
        audio_src_path=tmp_path,
        src_se=None,
        tgt_se=target_se,
        output_path=output_path,
        message="@MyShell"
    )

    print(f"[SUCCESS] Cloned voice saved at: {output_path}")

    # Clean up
    if os.path.exists(tmp_path):
        os.remove(tmp_path)