from typing import Any


class ResponseGenerator:
    """
    Hybrid response generator.

    Architecture:

        Dynamic / deterministic request
                    ↓
                   MCP
                    ↓
             Tool result
                    ↓
          Deterministic response

        Conversational / generative request
                    ↓
                   LLM

    IMPORTANT:

    If a tool result exists, the LLM is NEVER used to
    retrieve or invent airport data.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client

    # ======================================================
    # GENERATE
    # ======================================================

    async def generate(
        self,
        user_text: str,
        intent: str | None,
        entities: dict[str, Any],
        tool_result: Any,
        conversation_context: dict[str, Any],
        language_result: dict[str, Any],
    ) -> str:

        # ==================================================
        # MCP RESULT EXISTS
        # ==================================================

        if tool_result is not None:

            print(
                "[RESPONSE GENERATOR] "
                "Tool result available."
            )

            print(
                "[RESPONSE GENERATOR] "
                "Using tool data as source of truth."
            )

            # IMPORTANT:
            # We do NOT call the LLM here.
            #
            # The response is generated directly
            # from the MCP result.

            response = self._generate_tool_response(
                intent=intent,
                entities=entities,
                tool_result=tool_result,
                language_result=language_result,
            )

            if response is not None:
                return response

        # ==================================================
        # LLM PATH
        # ==================================================

        print(
            "[RESPONSE GENERATOR] "
            "No usable tool result."
        )

        print(
            "[RESPONSE GENERATOR] "
            "Using LLM for conversational request."
        )

        prompt = self._build_prompt(
            user_text=user_text,
            intent=intent,
            entities=entities,
            tool_result=tool_result,
            conversation_context=conversation_context,
            language_result=language_result,
        )

        response = await self.llm_client.generate(
            prompt=prompt,
        )

        return response.strip()

    # ======================================================
    # TOOL RESPONSE
    # ======================================================

    def _generate_tool_response(
        self,
        intent: str | None,
        entities: dict[str, Any],
        tool_result: Any,
        language_result: dict[str, Any],
    ) -> str | None:

        # --------------------------------------------------
        # UNWRAP MCP RESULT
        # --------------------------------------------------

        data = tool_result

        if hasattr(data, "data"):
            data = data.data

        elif hasattr(data, "structured_content"):
            data = data.structured_content

        # --------------------------------------------------
        # SOMETIMES MCP RETURNS WRAPPED DATA
        # --------------------------------------------------

        if isinstance(data, dict):

            if "structured_content" in data:
                data = data["structured_content"]

        # --------------------------------------------------
        # INVALID RESULT
        # --------------------------------------------------

        if not isinstance(data, dict):

            return (
                "Je n'ai pas pu récupérer "
                "les informations demandées."
            )

        # --------------------------------------------------
        # FLIGHT NOT FOUND
        # --------------------------------------------------

        if data.get("found") is False:

            flight_number = (
                data.get("flight_number")
                or entities.get("flight_number")
                or "ce vol"
            )

            language = language_result.get(
                "primary_language",
                "fr",
            )

            if language == "en":

                return (
                    f"I couldn't find information "
                    f"for flight {flight_number}."
                )

            if language == "es":

                return (
                    f"No pude encontrar información "
                    f"para el vuelo {flight_number}."
                )

            if language == "ar":

                return (
                    f"لم أتمكن من العثور على معلومات "
                    f"عن الرحلة {flight_number}."
                )

            return (
                f"Je n'ai pas trouvé d'informations "
                f"pour le vol {flight_number}."
            )

        # --------------------------------------------------
        # FLIGHT
        # --------------------------------------------------

        flight = data.get("flight")

        if not isinstance(flight, dict):

            return (
                "Je n'ai pas pu récupérer "
                "les informations du vol."
            )

        flight_number = flight.get(
            "flight_number",
            entities.get(
                "flight_number",
                "",
            ),
        )

        status = flight.get("status")
        gate = flight.get("gate")
        terminal = flight.get("terminal")

        language = language_result.get(
            "primary_language",
            "fr",
        )

        # ==================================================
        # ENGLISH
        # ==================================================

        if language == "en":

            if intent == "GET_FLIGHT_GATE":

                return (
                    f"Flight {flight_number} "
                    f"is at gate {gate}."
                )

            if intent == "GET_FLIGHT_TERMINAL":

                return (
                    f"Flight {flight_number} "
                    f"is at terminal {terminal}."
                )

            if intent == "GET_FLIGHT_STATUS":

                return (
                    f"Flight {flight_number} is "
                    f"{self._translate_status(status, 'en')}."
                )

            return (
                f"Flight {flight_number} is "
                f"{self._translate_status(status, 'en')}. "
                f"Gate {gate}, terminal {terminal}."
            )

        # ==================================================
        # SPANISH
        # ==================================================

        if language == "es":

            if intent == "GET_FLIGHT_GATE":

                return (
                    f"El vuelo {flight_number} "
                    f"está en la puerta {gate}."
                )

            if intent == "GET_FLIGHT_TERMINAL":

                return (
                    f"El vuelo {flight_number} "
                    f"está en la terminal {terminal}."
                )

            if intent == "GET_FLIGHT_STATUS":

                return (
                    f"El vuelo {flight_number} está "
                    f"{self._translate_status(status, 'es')}."
                )

            return (
                f"El vuelo {flight_number} está "
                f"{self._translate_status(status, 'es')}. "
                f"Puerta {gate}, terminal {terminal}."
            )

        # ==================================================
        # ARABIC
        # ==================================================

        if language == "ar":

            if intent == "GET_FLIGHT_GATE":

                return (
                    f"رحلتك {flight_number} "
                    f"في البوابة {gate}."
                )

            if intent == "GET_FLIGHT_TERMINAL":

                return (
                    f"رحلتك {flight_number} "
                    f"في المحطة {terminal}."
                )

            if intent == "GET_FLIGHT_STATUS":

                return (
                    f"الرحلة {flight_number} "
                    f"{self._translate_status(status, 'ar')}."
                )

            return (
                f"الرحلة {flight_number} "
                f"{self._translate_status(status, 'ar')}. "
                f"البوابة {gate}، المحطة {terminal}."
            )

        # ==================================================
        # FRENCH DEFAULT
        # ==================================================

        if intent == "GET_FLIGHT_GATE":

            return (
                f"Le vol {flight_number} "
                f"est à la porte {gate}."
            )

        if intent == "GET_FLIGHT_TERMINAL":

            return (
                f"Le vol {flight_number} "
                f"est au terminal {terminal}."
            )

        if intent == "GET_FLIGHT_STATUS":

            return (
                f"Le vol {flight_number} est "
                f"{self._translate_status(status, 'fr')}."
            )

        return (
            f"Le vol {flight_number} est "
            f"{self._translate_status(status, 'fr')}. "
            f"Porte {gate}, terminal {terminal}."
        )

    # ======================================================
    # STATUS TRANSLATION
    # ======================================================

    def _translate_status(
        self,
        status: str | None,
        language: str,
    ) -> str:

        translations = {

            "en": {
                "on_time": "on time",
                "delayed": "delayed",
                "cancelled": "cancelled",
            },

            "fr": {
                "on_time": "à l'heure",
                "delayed": "en retard",
                "cancelled": "annulé",
            },

            "es": {
                "on_time": "a tiempo",
                "delayed": "retrasado",
                "cancelled": "cancelado",
            },

            "ar": {
                "on_time": "في الموعد",
                "delayed": "متأخرة",
                "cancelled": "ملغاة",
            },
        }

        if language in translations:

            return translations[language].get(
                status,
                status.replace("_", " ")
                if status
                else "unknown",
            )

        return (
            status.replace("_", " ")
            if status
            else "unknown"
        )

    # ======================================================
    # LLM PROMPT
    # ======================================================

    def _build_prompt(
        self,
        user_text: str,
        intent: str | None,
        entities: dict[str, Any],
        tool_result: Any,
        conversation_context: dict[str, Any],
        language_result: dict[str, Any],
    ) -> str:

        return f"""
You are an AI conversational assistant specialized
in airport passenger assistance.

Answer the user's request naturally and concisely.

IMPORTANT RULES:

- Respect the language of the current message.
- The user may mix several languages.
- Understand code-switching naturally.
- Never invent airport information.
- Never invent flight information.
- If dynamic flight or airport information is required,
  it must come from an available tool result.
- Never guess missing flight information.
- Use conversation context for follow-up questions.
- Keep the answer short and natural for voice interaction.
- Do not mention tools, MCP, LLMs or internal architecture.

CURRENT USER MESSAGE:
{user_text}

LANGUAGE:
{language_result}

INTENT:
{intent}

ENTITIES:
{entities}

CONVERSATION:
{conversation_context}

TOOL RESULT:
{tool_result}

Answer only the user's request.
"""
