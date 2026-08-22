from abc import ABC, abstractmethod


class TTSService(ABC):

    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str,
    ) -> str:
        """
        Convert text into speech.

        Args:
            text: Text to synthesize.
            output_path: Destination audio file.

        Returns:
            Path to the generated audio file.
        """
        pass