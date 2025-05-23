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
    parser.add_argument("--text", required=False, help="Text to speak in your voice")
    parser.add_argument("--out", required=True, help="Path to save output audio")
    parser.add_argument("--user_id", required=False)
    parser.add_argument("--setup_only", action="store_true", help="Run in setup-only mode")

    args = parser.parse_args()

    validate_file(args.ref)
    validate_folder(args.out)

    if args.setup_only:
        print("[INFO] Running in setup-only mode. No text required.")
        text = None  # Skip text processing
    else:
        if not args.text:
            print("[ERROR] --text is required unless --setup_only is enabled.")
            sys.exit(1)
        text = args.text

    try:
        synthesize_cloned_speech(args.ref, text, args.out, args.user_id, setup_only=args.setup_only)
        print("[SUCCESS] Voice cloning process completed.")
    except Exception as e:
        print(f"[ERROR] Voice cloning failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()