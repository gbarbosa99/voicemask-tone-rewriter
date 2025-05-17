import os
import torch
import hashlib

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS as MeloTTS


def synthesize_cloned_speech(ref_audio, text, output_path):
    # === 0. Setup ===
    ckpt_converter = 'checkpoints_v2/converter'
    device = "cuda" if torch.cuda.is_available() else "cpu"

    os.makedirs("audio/se", exist_ok=True)
    os.makedirs("audio/temp", exist_ok=True)

    # === 1. Cache speaker embedding based on reference audio ===
    with open(ref_audio, "rb") as f:
        audio_hash = hashlib.sha256(f.read()).hexdigest()[:12]
    se_path = f"audio/se/{audio_hash}.pth"

    if not os.path.exists(se_path):
        print("==> Extracting new speaker embedding")
        tone_color_converter_tmp = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        tone_color_converter_tmp.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        target_se, _ = se_extractor.get_se(ref_audio, tone_color_converter_tmp, vad=True)
        torch.save(target_se, se_path)
    else:
        print(f"==> Reusing cached speaker embedding: {se_path}")

    # === 2. Generate neutral base speech with MeloTTS ===
    print("==> Generating neutral base voice")
    tts_path = "audio/temp/neutral.wav"
    melo = MeloTTS(language="EN", device=device)
    speaker_ids = melo.hps.data.spk2id
    default_speaker_id = list(speaker_ids.values())[0]
    melo.tts_to_file(text, default_speaker_id, tts_path, speed=1.0)

    # === 3. Voice Cloning using ToneColorConverter ===
    print("==> Performing voice cloning")
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    tone_color_converter.convert(
        audio_src_path=tts_path,
        src_se_path=f'{ckpt_converter}/example_se.pth',  # base voice
        tgt_se_path=se_path,                             # user's voice
        output_path=output_path
    )

    print(f"✅ Voice cloning complete: {output_path}")