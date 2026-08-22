from typing import Any


class ResponseTemplates:
    """
    Generates fast deterministic responses for simple
    airport requests.

    This layer does NOT use an LLM.

    It is designed for:
    - low latency
    - predictable responses
    - factual grounding
    - multilingual support
    - mobile / voice assistant usage
    """

    def generate(
        self,
        intent: str,
        entities: dict[str, Any],
        tool_result: dict[str, Any],
        language_result: dict[str, Any],
    ) -> str | None:

        if not tool_result:
            return None

        flight = tool_result.get("flight")

        if not flight:
            return None

        flight_number = flight.get("flight_number")
        status = flight.get("status")
        gate = flight.get("gate")
        terminal = flight.get("terminal")

        primary_language = language_result.get(
            "primary_language",
            "en",
        )

        languages = language_result.get(
            "languages",
            [],
        )

        is_mixed = language_result.get(
            "is_mixed",
            False,
        )

        # ======================================================
        # MIXED LANGUAGE
        # ======================================================
        #
        # For mixed messages we avoid trying to translate
        # the entire sentence.
        #
        # We use the dominant language for the response.
        #
        # The LLM remains available for more complex mixed
        # conversations.
        # ======================================================

        if is_mixed:

            return self._generate_mixed(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
                languages=languages,
                primary_language=primary_language,
            )

        # ======================================================
        # ENGLISH
        # ======================================================

        if primary_language == "en":

            return self._generate_english(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
            )

        # ======================================================
        # FRENCH
        # ======================================================

        if primary_language == "fr":

            return self._generate_french(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
            )

        # ======================================================
        # SPANISH
        # ======================================================

        if primary_language == "es":

            return self._generate_spanish(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
            )

        # ======================================================
        # ARABIC
        # ======================================================

        if primary_language == "ar":

            return self._generate_arabic(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
            )

        # ======================================================
        # GERMAN
        # ======================================================

        if primary_language == "de":

            return self._generate_german(
                intent=intent,
                flight_number=flight_number,
                status=status,
                gate=gate,
                terminal=terminal,
            )

        # ======================================================
        # FALLBACK
        # ======================================================

        return self._generate_english(
            intent=intent,
            flight_number=flight_number,
            status=status,
            gate=gate,
            terminal=terminal,
        )

    # ==========================================================
    # ENGLISH
    # ==========================================================

    def _generate_english(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
    ) -> str:

        if intent == "GET_FLIGHT_GATE":
            return f"The gate is {gate}."

        if intent == "GET_FLIGHT_TERMINAL":
            return f"Terminal {terminal}."

        if intent == "GET_FLIGHT_STATUS":
            return (
                f"Flight {flight_number} is {self._status_en(status)}."
            )

        if intent == "GET_FLIGHT_INFORMATION":
            return (
                f"Flight {flight_number} is "
                f"{self._status_en(status)}, "
                f"at gate {gate}, Terminal {terminal}."
            )

        return (
            f"Flight {flight_number} is "
            f"{self._status_en(status)}, "
            f"at gate {gate}, Terminal {terminal}."
        )

    # ==========================================================
    # FRENCH
    # ==========================================================

    def _generate_french(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
    ) -> str:

        if intent == "GET_FLIGHT_GATE":
            return f"La porte est {gate}."

        if intent == "GET_FLIGHT_TERMINAL":
            return f"Terminal {terminal}."

        if intent == "GET_FLIGHT_STATUS":
            return (
                f"Le vol {flight_number} est "
                f"{self._status_fr(status)}."
            )

        if intent == "GET_FLIGHT_INFORMATION":
            return (
                f"Le vol {flight_number} est "
                f"{self._status_fr(status)}, "
                f"à la porte {gate}, terminal {terminal}."
            )

        return (
            f"Le vol {flight_number} est "
            f"{self._status_fr(status)}, "
            f"à la porte {gate}, terminal {terminal}."
        )

    # ==========================================================
    # SPANISH
    # ==========================================================

    def _generate_spanish(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
    ) -> str:

        if intent == "GET_FLIGHT_GATE":
            return f"La puerta es {gate}."

        if intent == "GET_FLIGHT_TERMINAL":
            return f"La terminal es la {terminal}."

        if intent == "GET_FLIGHT_STATUS":
            return (
                f"El vuelo {flight_number} está "
                f"{self._status_es(status)}."
            )

        if intent == "GET_FLIGHT_INFORMATION":
            return (
                f"El vuelo {flight_number} está "
                f"{self._status_es(status)}, "
                f"en la puerta {gate}, terminal {terminal}."
            )

        return (
            f"El vuelo {flight_number} está "
            f"{self._status_es(status)}, "
            f"en la puerta {gate}, terminal {terminal}."
        )

    # ==========================================================
    # ARABIC
    # ==========================================================

    def _generate_arabic(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
    ) -> str:

        if intent == "GET_FLIGHT_GATE":
            return f"البوابة هي {gate}."

        if intent == "GET_FLIGHT_TERMINAL":
            return f"المحطة هي {terminal}."

        if intent == "GET_FLIGHT_STATUS":
            return (
                f"الرحلة {flight_number} "
                f"{self._status_ar(status)}."
            )

        if intent == "GET_FLIGHT_INFORMATION":
            return (
                f"الرحلة {flight_number} "
                f"{self._status_ar(status)}، "
                f"البوابة {gate}، المحطة {terminal}."
            )

        return (
            f"الرحلة {flight_number} "
            f"{self._status_ar(status)}، "
            f"البوابة {gate}، المحطة {terminal}."
        )

    # ==========================================================
    # GERMAN
    # ==========================================================

    def _generate_german(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
    ) -> str:

        if intent == "GET_FLIGHT_GATE":
            return f"Das Gate ist {gate}."

        if intent == "GET_FLIGHT_TERMINAL":
            return f"Das Terminal ist {terminal}."

        if intent == "GET_FLIGHT_STATUS":
            return (
                f"Der Flug {flight_number} ist "
                f"{self._status_de(status)}."
            )

        if intent == "GET_FLIGHT_INFORMATION":
            return (
                f"Der Flug {flight_number} ist "
                f"{self._status_de(status)}, "
                f"am Gate {gate}, Terminal {terminal}."
            )

        return (
            f"Der Flug {flight_number} ist "
            f"{self._status_de(status)}, "
            f"am Gate {gate}, Terminal {terminal}."
        )

    # ==========================================================
    # MIXED LANGUAGE
    # ==========================================================

    def _generate_mixed(
        self,
        intent: str,
        flight_number: str | None,
        status: str | None,
        gate: str | None,
        terminal: str | None,
        languages: list[str],
        primary_language: str,
    ) -> str | None:

        """
        Handle simple mixed-language requests.

        We deliberately keep this conservative.

        If we can safely answer using the primary language,
        we do so.

        Complex linguistic generation remains delegated
        to the LLM.
        """

        supported_languages = {
            "en",
            "fr",
            "es",
            "ar",
            "de",
        }

        if primary_language not in supported_languages:
            return None

        if primary_language == "en":
            return self._generate_english(
                intent,
                flight_number,
                status,
                gate,
                terminal,
            )

        if primary_language == "fr":
            return self._generate_french(
                intent,
                flight_number,
                status,
                gate,
                terminal,
            )

        if primary_language == "es":
            return self._generate_spanish(
                intent,
                flight_number,
                status,
                gate,
                terminal,
            )

        if primary_language == "ar":
            return self._generate_arabic(
                intent,
                flight_number,
                status,
                gate,
                terminal,
            )

        if primary_language == "de":
            return self._generate_german(
                intent,
                flight_number,
                status,
                gate,
                terminal,
            )

        return None

    # ==========================================================
    # STATUS TRANSLATION
    # ==========================================================

    @staticmethod
    def _status_en(status: str | None) -> str:

        mapping = {
            "on_time": "on time",
            "delayed": "delayed",
            "cancelled": "cancelled",
        }

        return mapping.get(
            status,
            str(status),
        )

    @staticmethod
    def _status_fr(status: str | None) -> str:

        mapping = {
            "on_time": "à l'heure",
            "delayed": "en retard",
            "cancelled": "annulé",
        }

        return mapping.get(
            status,
            str(status),
        )

    @staticmethod
    def _status_es(status: str | None) -> str:

        mapping = {
            "on_time": "a tiempo",
            "delayed": "retrasado",
            "cancelled": "cancelado",
        }

        return mapping.get(
            status,
            str(status),
        )

    @staticmethod
    def _status_ar(status: str | None) -> str:

        mapping = {
            "on_time": "في الموعد",
            "delayed": "متأخرة",
            "cancelled": "ملغاة",
        }

        return mapping.get(
            status,
            str(status),
        )

    @staticmethod
    def _status_de(status: str | None) -> str:

        mapping = {
            "on_time": "pünktlich",
            "delayed": "verspätet",
            "cancelled": "annulliert",
        }

        return mapping.get(
            status,
            str(status),
        )

