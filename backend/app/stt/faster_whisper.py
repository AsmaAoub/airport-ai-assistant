import os
import tempfile

import noisereduce as nr
import soundfile as sf
from faster_whisper import WhisperModel

from app.stt.base import STTService


class FasterWhisperService(STTService):

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        print(f"[STT] Loading Whisper model: {model_size}")

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

        print("[STT] Whisper model loaded.")

    def _remove_noise(
        self,
        audio_path: str,
    ) -> str:

        print("[STT] Starting noise suppression...")

        # --------------------------------------------------
        # Load audio
        # --------------------------------------------------

        audio, sample_rate = sf.read(
            audio_path,
            dtype="float32",
        )

        # --------------------------------------------------
        # Stereo -> Mono
        # --------------------------------------------------

        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        # --------------------------------------------------
        # Noise reduction
        # --------------------------------------------------

        cleaned_audio = nr.reduce_noise(
            y=audio,
            sr=sample_rate,
            prop_decrease=0.8,
        )

        # --------------------------------------------------
        # Temporary cleaned file
        # --------------------------------------------------

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        )

        temp_file.close()

        sf.write(
            temp_file.name,
            cleaned_audio,
            sample_rate,
        )

        print(
            f"[STT] Noise-suppressed audio: "
            f"{temp_file.name}"
        )

        return temp_file.name

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> str:

        cleaned_audio_path = None

        try:

            # ==================================================
            # 1. NOISE SUPPRESSION
            # ==================================================

            cleaned_audio_path = self._remove_noise(
                audio_path
            )

            # ==================================================
            # 2. WHISPER
            # ==================================================

            segments, info = self.model.transcribe(
                cleaned_audio_path,
                language=language,
                vad_filter=True,
            )

            # ==================================================
            # 3. BUILD TRANSCRIPTION
            # ==================================================

            text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

            detected_language = info.language

            print(
                f"[STT] Detected language: "
                f"{detected_language}"
            )

            print(
                f"[STT] Transcription: {text}"
            )

            return text

        finally:

            # ==================================================
            # 4. CLEAN TEMPORARY FILE
            # ==================================================

            if (
                cleaned_audio_path
                and os.path.exists(cleaned_audio_path)
            ):
                os.remove(cleaned_audio_path)

                print(
                    "[STT] Temporary cleaned audio "
                    "deleted."
                )

