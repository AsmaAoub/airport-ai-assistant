import re

from app.airport.intents import AirportIntent
from app.airport.entities import AirportEntities
from app.airport.normalizer import AirportNormalizer


class AirportNLP:
    """
    Airport-specific Natural Language Processing layer.

    Responsibilities:
    - Normalize user input
    - Detect airport-related intent
    - Extract airport-related entities

    IMPORTANT:
    This layer does NOT decide whether to use MCP or LLM.
    It only analyzes the user's request.
    """

    def __init__(self):
        self.normalizer = AirportNormalizer()

    def analyze(self, text: str) -> dict:
        """
        Analyze a user message.
        """

        normalized_text = self.normalizer.normalize(text)

        intent = self._detect_intent(normalized_text)

        entities = self._extract_entities(normalized_text)

        return {
            "intent": intent.value,
            "entities": entities,
        }

    # ==========================================================
    # INTENT DETECTION
    # ==========================================================

    def _detect_intent(self, text: str) -> AirportIntent:

        text_lower = text.lower()

        # ------------------------------------------------------
        # FLIGHT GATE
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "gate",
                "boarding gate",
                "porte",
                "porte d'embarquement",
                "porte embarquement",
                "puerta",
                "puerta de embarque",
                "boarding",
                "boarding door",
                "gates",
            ]
        ):
            return AirportIntent.GET_FLIGHT_GATE

        # ------------------------------------------------------
        # FLIGHT STATUS
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "status",
                "flight status",
                "statut",
                "statut du vol",
                "état du vol",
                "etat du vol",
                "retard",
                "retardé",
                "retarde",
                "delay",
                "delayed",
                "retraso",
                "retrasado",
                "estado del vuelo",
                "stato del volo",
            ]
        ):
            return AirportIntent.GET_FLIGHT_STATUS

        # ------------------------------------------------------
        # TERMINAL
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "terminal",
                "terminal number",
                "numéro de terminal",
                "numero de terminal",
            ]
        ):
            return AirportIntent.GET_FLIGHT_TERMINAL

        # ------------------------------------------------------
        # GENERAL FLIGHT INFORMATION
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "flight",
                "flight number",
                "vol",
                "vol numéro",
                "informations sur le vol",
                "information sur le vol",
                "infos sur le vol",
                "info sur le vol",
                "informations du vol",
                "informations concernant le vol",
                "vuelo",
                "información del vuelo",
                "informacion del vuelo",
                "informazioni sul volo",
                "flug",
            ]
        ):
            return AirportIntent.GET_FLIGHT_INFORMATION

        # ------------------------------------------------------
        # BAGGAGE
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "baggage",
                "luggage",
                "bagage",
                "bagages",
                "valise",
                "valises",
                "maleta",
                "maletas",
                "equipaje",
                "suitcase",
            ]
        ):
            return AirportIntent.GET_BAGGAGE

        # ------------------------------------------------------
        # PARKING
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "parking",
                "car park",
                "stationnement",
                "parquer",
                "où garer",
                "ou garer",
            ]
        ):
            return AirportIntent.GET_PARKING

        # ------------------------------------------------------
        # CHECK-IN
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "check-in",
                "check in",
                "checkin",
                "enregistrement",
                "registro",
            ]
        ):
            return AirportIntent.GET_CHECKIN

        # ------------------------------------------------------
        # SECURITY
        # ------------------------------------------------------

        if any(
            keyword in text_lower
            for keyword in [
                "security",
                "security check",
                "sécurité",
                "securite",
                "contrôle de sécurité",
                "controle de securite",
                "seguridad",
            ]
        ):
            return AirportIntent.GET_SECURITY

        # ------------------------------------------------------
        # UNKNOWN
        # ------------------------------------------------------

        return AirportIntent.UNKNOWN

    # ==========================================================
    # ENTITY EXTRACTION
    # ==========================================================

    def _extract_entities(self, text: str) -> dict:

        entities = AirportEntities()

        # ------------------------------------------------------
        # FLIGHT NUMBER
        # ------------------------------------------------------

        flight_match = re.search(
            r"\b[A-Z]{2}[- ]?\d{1,4}\b",
            text.upper(),
        )

        if flight_match:

            flight_number = (
                flight_match.group(0)
                .replace("-", "")
                .replace(" ", "")
            )

            entities.flight_number = flight_number

        # ------------------------------------------------------
        # GATE
        # ------------------------------------------------------

        gate_match = re.search(
            r"\b([A-Z]\d{1,3})\b",
            text.upper(),
        )

        if gate_match:
            entities.gate = gate_match.group(1)

        # ------------------------------------------------------
        # TERMINAL
        # ------------------------------------------------------

        terminal_match = re.search(
            r"terminal\s+(\d+)",
            text,
            re.IGNORECASE,
        )

        if terminal_match:
            entities.terminal = terminal_match.group(1)

        # ------------------------------------------------------
        # RETURN
        # ------------------------------------------------------

        return {
            key: value
            for key, value in {
                "flight_number": entities.flight_number,
                "gate": entities.gate,
                "terminal": entities.terminal,
            }.items()
            if value is not None
        }