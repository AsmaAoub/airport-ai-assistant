
from typing import Any


class ResponsePolicy:
    """
    Decides whether a passenger request can be answered
    deterministically or requires LLM generation.

    The policy is intentionally independent from:
    - Ollama
    - Qwen
    - Llama
    - any specific LLM provider

    This keeps the architecture flexible and allows the
    LLM to be replaced or fine-tuned later.
    """

    # ==========================================================
    # INTENTS THAT CAN CURRENTLY BE ANSWERED DETERMINISTICALLY
    # ==========================================================

    DETERMINISTIC_INTENTS = {
        "GET_FLIGHT_INFORMATION",
        "GET_FLIGHT_STATUS",
        "GET_FLIGHT_GATE",
        "GET_FLIGHT_TERMINAL",
    }

    def should_use_llm(
        self,
        intent: str | None,
        entities: dict[str, Any],
        tool_result: Any,
        language_result: dict[str, Any],
    ) -> bool:
        """
        Decide whether the LLM is required.

        Returns:
            True  -> use LLM
            False -> deterministic response
        """

        # ------------------------------------------------------
        # 1. Unknown intent
        # ------------------------------------------------------

        if not intent:
            return True

        if intent == "UNKNOWN":
            return True

        # ------------------------------------------------------
        # 2. Intent not supported by deterministic layer
        # ------------------------------------------------------

        if intent not in self.DETERMINISTIC_INTENTS:
            return True

        # ------------------------------------------------------
        # 3. Required entity missing
        # ------------------------------------------------------

        if not entities.get("flight_number"):
            return True

        # ------------------------------------------------------
        # 4. Tool result missing
        # ------------------------------------------------------

        if tool_result is None:
            return True

        # ------------------------------------------------------
        # 5. Tool did not find the requested flight
        # ------------------------------------------------------

        if isinstance(tool_result, dict):

            if tool_result.get("found") is False:
                return True

        # ------------------------------------------------------
        # 6. Mixed-language messages
        # ------------------------------------------------------
        #
        # IMPORTANT:
        #
        # We do NOT automatically send every mixed-language
        # request to the LLM.
        #
        # Simple airport requests such as:
        #
        #   "Where is flight AT123? ¿Y la puerta?"
        #
        # can still be answered deterministically.
        #
        # The language layer will be used by the response
        # builder to select the appropriate formulation.
        #
        # Therefore mixed language alone is NOT a reason
        # to invoke the LLM.
        # ------------------------------------------------------

        return False

