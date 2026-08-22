from pathlib import Path

from app.stt import FasterWhisperService


AUDIO_FILE = Path("tests/audio/test.wav")


def main():
    if not AUDIO_FILE.exists():
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    stt = FasterWhisperService(
        model_size="small",
        device="cpu",
        compute_type="int8",
    )

    text = stt.transcribe(
        str(AUDIO_FILE)
    )

    print("\n==============================")
    print("FINAL TRANSCRIPTION")
    print("==============================")
    print(text)


if __name__ == "__main__":
    main()