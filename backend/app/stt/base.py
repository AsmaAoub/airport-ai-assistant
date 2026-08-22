from abc import ABC, abstractmethod


class STTService(ABC):

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> str:
        """
        Transcribe an audio file into text.

        Args:
            audio_path: Path to the audio file.
            language: Optional language code.

        Returns:
            Transcribed text.
        """
        pass