from pathlib import Path
import wave

from piper import PiperVoice

from app.tts.base import TTSService


class PiperTTSService(TTSService):
    """
    Piper TTS service.

    Converts text into a WAV audio file using Piper.
    """

    def __init__(self, voice_path: str):
        self.voice_path = Path(voice_path)

        if not self.voice_path.exists():
            raise FileNotFoundError(
                f"Piper voice model not found: {self.voice_path}"
            )

        print(
            f"[TTS] Loading Piper voice: "
            f"{self.voice_path}"
        )

        self.voice = PiperVoice.load(
            str(self.voice_path)
        )

        print("[TTS] Piper voice loaded.")

    def synthesize(
        self,
        text: str,
        output_path: str,
    ) -> str:

        if not text or not text.strip():
            raise ValueError(
                "Cannot synthesize empty text."
            )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"[TTS] Synthesizing: {text}"
        )

        # Piper writes a WAV file.
        # We must provide a wave.Wave_write object,
        # not a normal BufferedWriter.
        with wave.open(
            str(output_path),
            "wb",
        ) as wav_file:

            self.voice.synthesize_wav(
                text,
                wav_file,
            )

        print(
            f"[TTS] Audio generated: "
            f"{output_path}"
        )

        return str(output_path)