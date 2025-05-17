# voice_cloning_cli.py
from voice_cloning import synthesize_cloned_speech
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    synthesize_cloned_speech(args.ref, args.text, args.out)
