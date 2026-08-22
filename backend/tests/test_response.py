import asyncio

from app.llm.client import LLMClient
from app.response.generator import ResponseGenerator


async def main():

    # ==================================================
    # LLM CLIENT
    # ==================================================

    llm_client = LLMClient(
        provider="ollama",
        model="llama3.2:3b",
    )

    # ==================================================
    # RESPONSE GENERATOR
    # ==================================================

    response_generator = ResponseGenerator(
        llm_client=llm_client
    )

    # ==================================================
    # SIMULATED CONVERSATION
    # ==================================================

    user_text = "Where is flight AT123?"

    language_result = {
        "primary_language": "en",
        "languages": ["en"],
        "is_mixed": False,
        "confidence": 0.28,
    }

    intent = "GET_FLIGHT_INFORMATION"

    entities = {
        "flight_number": "AT123"
    }

    conversation_context = {
        "current_intent": "GET_FLIGHT_INFORMATION",
        "entities": {
            "flight_number": "AT123"
        },
        "history": [
            {
                "role": "user",
                "content": "Where is flight AT123?"
            }
        ],
    }

    # ==================================================
    # SIMULATED MCP RESULT
    # ==================================================

    tool_result = {
        "found": True,
        "flight": {
            "flight_number": "AT123",
            "status": "on_time",
            "gate": "B42",
            "terminal": "1",
        },
    }

    # ==================================================
    # GENERATE RESPONSE
    # ==================================================

    response = await response_generator.generate(
        user_text=user_text,
        intent=intent,
        entities=entities,
        tool_result=tool_result,
        conversation_context=conversation_context,
        language_result=language_result,
    )

    # ==================================================
    # DISPLAY
    # ==================================================

    print()
    print("==============================")
    print("USER")
    print("==============================")
    print(user_text)

    print()
    print("==============================")
    print("ASSISTANT")
    print("==============================")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())