# voice_cloning_cli.py

import argparse
import os
import sys
from voice_cloning import synthesize_cloned_speech

def validate_file(path):
    if not os.path.isfile(path):
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)

def validate_folder(output_path):
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[INFO] Created output folder: {folder}")

def main():
    parser = argparse.ArgumentParser(description="Voice cloning CLI")
    parser.add_argument("--ref", required=True, help="Reference audio file (your voice)")
    parser.add_argument("--text", required=True, help="Text to speak in your voice")
    parser.add_argument("--out", required=True, help="Path to save output audio")

    args = parser.parse_args()

    validate_file(args.ref)
    validate_folder(args.out)

    try:
        synthesize_cloned_speech(args.ref, args.text, args.out)
    except Exception as e:
        print(f"[ERROR] Voice cloning failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
