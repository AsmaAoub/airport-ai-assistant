from pathlib import Path

from app.tts.piper import PiperTTSService


class VoiceManager:
    """
    Manages multilingual Piper TTS voices.

    Supported languages are automatically registered
    from the available voice models.
    """

    def __init__(
        self,
        voices_directory: str = "voices",
    ):
        self.voices_directory = Path(
            voices_directory
        )

        self.services: dict[str, PiperTTSService] = {}

        print(
            f"[TTS] Voice directory: "
            f"{self.voices_directory.resolve()}"
        )

        self._load_default_voices()

        print(
            "[TTS] Available languages: "
            f"{self.available_languages()}"
        )

    # ==================================================
    # LOAD VOICES
    # ==================================================

    def _load_default_voices(self) -> None:
        """
        Register the available Piper voices.
        """

        voices = {
            "fr": "fr_FR-siwis-medium.onnx",

            "en": "en_GB-alan-low.onnx",

            "es": "es_ES-carlfm-x_low.onnx",

            "it": "it_IT-riccardo-x_low.onnx",
        }

        for language, filename in voices.items():

            voice_path = (
                self.voices_directory / filename
            )

            if not voice_path.exists():

                print(
                    f"[TTS] Voice not found: "
                    f"{voice_path}"
                )

                continue

            try:

                self.register_voice(
                    language=language,
                    voice_path=str(voice_path),
                )

            except Exception as error:

                print(
                    f"[TTS] Failed to load "
                    f"{language}: {error}"
                )

    # ==================================================
    # REGISTER
    # ==================================================

    def register_voice(
        self,
        language: str,
        voice_path: str,
    ) -> None:

        language = (
            language
            .lower()
            .strip()
        )

        service = PiperTTSService(
            voice_path
        )

        self.services[language] = service

        print(
            f"[TTS] Registered voice: "
            f"{language}"
        )

    # ==================================================
    # CHECK
    # ==================================================

    def has_voice(
        self,
        language: str,
    ) -> bool:

        language = (
            language
            .lower()
            .strip()
        )

        return language in self.services

    # ==================================================
    # GET VOICE
    # ==================================================

    def get_voice(
        self,
        language: str,
    ) -> PiperTTSService | None:

        language = (
            language
            .lower()
            .strip()
        )

        return self.services.get(
            language
        )

    # ==================================================
    # SYNTHESIZE
    # ==================================================

    def synthesize(
        self,
        text: str,
        language: str,
        output_path: str,
    ) -> str:

        language = (
            language
            .lower()
            .strip()
        )

        service = self.get_voice(
            language
        )

        if service is None:

            raise ValueError(
                "No TTS voice available "
                f"for language: {language}"
            )

        return service.synthesize(
            text=text,
            output_path=output_path,
        )

    # ==================================================
    # AVAILABLE LANGUAGES
    # ==================================================

    def available_languages(
        self,
    ) -> list[str]:

        return list(
            self.services.keys()
        )