import re


class AirportNormalizer:
    """
    Normalizes user input before airport NLP processing.
    """

    def normalize(self, text: str) -> str:
        """
        Normalize text while preserving its meaning.
        """

        text = text.strip()

        # Normalize spaces
        text = re.sub(r"\s+", " ", text)

        return text