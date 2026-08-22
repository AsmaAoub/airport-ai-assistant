from lingua import LanguageDetectorBuilder


class LanguageLayer:
    """
    Language analysis layer.

    Responsibilities:
    - Detect the primary language.
    - Detect multiple languages.
    - Identify potential code-switching.
    """

    def __init__(self):
        self.detector = (
            LanguageDetectorBuilder
            .from_all_languages()
            .build()
        )

    def detect(self, text: str) -> dict:
        """
        Analyze the language composition of a user message.
        """

        text = text.strip()

        if not text:
            return {
                "primary_language": "unknown",
                "languages": [],
                "is_mixed": False,
                "confidence": 0.0,
            }

        # --------------------------------------------------
        # 1. Detect primary language
        # --------------------------------------------------

        primary_language = self.detector.detect_language_of(text)

        if primary_language is None:
            return {
                "primary_language": "unknown",
                "languages": [],
                "is_mixed": False,
                "confidence": 0.0,
            }

        primary_code = self._language_to_code(primary_language)

        # --------------------------------------------------
        # 2. Calculate confidence
        # --------------------------------------------------

        confidence_values = (
            self.detector.compute_language_confidence_values(text)
        )

        confidence = 0.0

        for value in confidence_values:
            if value.language == primary_language:
                confidence = value.value
                break

        # --------------------------------------------------
        # 3. Detect languages in segments
        # --------------------------------------------------

        detected_languages = self._detect_languages_in_segments(text)

        # Always include the primary language
        if primary_code not in detected_languages:
            detected_languages.insert(0, primary_code)

        # Remove duplicates while preserving order
        detected_languages = list(dict.fromkeys(detected_languages))

        # --------------------------------------------------
        # 4. Determine whether the message is mixed
        # --------------------------------------------------

        is_mixed = len(detected_languages) > 1

        return {
            "primary_language": primary_code,
            "languages": detected_languages,
            "is_mixed": is_mixed,
            "confidence": round(confidence, 4),
        }

    def _detect_languages_in_segments(self, text: str) -> list[str]:
        """
        Detect languages by analyzing small segments of text.

        This is an initial code-switching detection strategy.
        """

        # Split on common punctuation and separators.
        separators = [
            ",",
            ".",
            "!",
            "?",
            ";",
            ":",
            "\n",
        ]

        segments = [text]

        for separator in separators:
            new_segments = []

            for segment in segments:
                new_segments.extend(segment.split(separator))

            segments = new_segments

        detected_languages = []

        for segment in segments:
            segment = segment.strip()

            # Ignore extremely short segments.
            if len(segment) < 3:
                continue

            language = self.detector.detect_language_of(segment)

            if language is None:
                continue

            code = self._language_to_code(language)

            if code not in detected_languages:
                detected_languages.append(code)

        return detected_languages

    @staticmethod
    def _language_to_code(language) -> str:
        """
        Convert Lingua language names to ISO 639-1 codes.
        """

        language_codes = {
            "AFRIKAANS": "af",
            "ALBANIAN": "sq",
            "ARABIC": "ar",
            "ARMENIAN": "hy",
            "AZERBAIJANI": "az",
            "BASQUE": "eu",
            "BELARUSIAN": "be",
            "BENGALI": "bn",
            "BOSNIAN": "bs",
            "BULGARIAN": "bg",
            "CATALAN": "ca",
            "CHINESE": "zh",
            "CROATIAN": "hr",
            "CZECH": "cs",
            "DANISH": "da",
            "DUTCH": "nl",
            "ENGLISH": "en",
            "ESTONIAN": "et",
            "FINNISH": "fi",
            "FRENCH": "fr",
            "GEORGIAN": "ka",
            "GERMAN": "de",
            "GREEK": "el",
            "GUJARATI": "gu",
            "HEBREW": "he",
            "HINDI": "hi",
            "HUNGARIAN": "hu",
            "ICELANDIC": "is",
            "INDONESIAN": "id",
            "IRISH": "ga",
            "ITALIAN": "it",
            "JAPANESE": "ja",
            "KANNADA": "kn",
            "KAZAKH": "kk",
            "KOREAN": "ko",
            "LATIN": "la",
            "LATVIAN": "lv",
            "LITHUANIAN": "lt",
            "MACEDONIAN": "mk",
            "MALAY": "ms",
            "MARATHI": "mr",
            "MONGOLIAN": "mn",
            "NORWEGIAN": "no",
            "PERSIAN": "fa",
            "POLISH": "pl",
            "PORTUGUESE": "pt",
            "PUNJABI": "pa",
            "ROMANIAN": "ro",
            "RUSSIAN": "ru",
            "SERBIAN": "sr",
            "SLOVAK": "sk",
            "SLOVENIAN": "sl",
            "SOMALI": "so",
            "SPANISH": "es",
            "SWAHILI": "sw",
            "SWEDISH": "sv",
            "TAGALOG": "tl",
            "TAMIL": "ta",
            "TELUGU": "te",
            "THAI": "th",
            "TURKISH": "tr",
            "UKRAINIAN": "uk",
            "URDU": "ur",
            "VIETNAMESE": "vi",
            "WELSH": "cy",
        }

        return language_codes.get(
            language.name,
            language.name.lower(),
        )