# voice_cloning.py
import os
import torch
from melo.api import TTS as MeloTTS
from openvoice.api import ToneColorConverter
from openvoice import se_extractor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINTS_DIR = "/home/gbarbosa9/OpenVoice/checkpoints"
SE_DIR = os.path.join(BASE_DIR, "se_cache")

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
tone_color_converter = ToneColorConverter(
    os.path.join(CHECKPOINTS_DIR, "converter", "config.json"), device=device
)
tone_color_converter.load_ckpt(os.path.join(CHECKPOINTS_DIR, "converter", "checkpoint.pth"))

melo_tts = MeloTTS(language="EN", device=device)


def synthesize_cloned_speech(ref_audio_path, text, output_path, user_id=None, setup_only=False):
    try:
        # Load or extract speaker embedding
        se_path = os.path.join(SE_DIR, f"{user_id}_se.pth") if user_id else None
        if user_id and os.path.exists(se_path):
            print(f"[INFO] Using cached speaker embedding for user_id={user_id}")
            target_se = torch.load(se_path, map_location=device)
        else:
            print("[INFO] Extracting speaker embedding...")
            target_se, _ = se_extractor.get_se(ref_audio_path, tone_color_converter, vad=True)
            if user_id:
                os.makedirs(SE_DIR, exist_ok=True)
                torch.save(target_se, se_path)

        if setup_only:
            print("[INFO] Setup only: SE cached without synthesis")
            return

        print(f"[INFO] Synthesizing cloned speech to: {output_path}")

        # Generate neutral voice
        temp_base_path = output_path.replace(".m4a", "_base.wav")
        speaker_ids = melo_tts.hps.data.spk2id
        speaker_id = list(speaker_ids.values())[0]
        melo_tts.tts_to_file(text, speaker_id, temp_base_path, speed=1.0)

        # Tone conversion
        tone_color_converter.convert(
            audio_src_path=temp_base_path,
            src_se=None,
            tgt_se=target_se,
            output_path=output_path,
            message="@MyShell"
        )

        if os.path.exists(temp_base_path):
            os.remove(temp_base_path)

    except Exception as e:
        print("[ERROR] Voice cloning failed:", str(e))
        raise e
