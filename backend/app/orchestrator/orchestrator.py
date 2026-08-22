
import uuid
import time
from typing import Any

from app.language.detector import LanguageLayer
from app.conversation.manager import ConversationManager
from app.airport.nlp import AirportNLP
from app.response.generator import ResponseGenerator
from app.llm.client import LLMClient

from mcp_client.client import MCPClient
from tools.router import ToolRouter


class Orchestrator:
    """
    Central coordinator of the Airport AI Assistant.

    Architecture:

        User
          ↓
        Language Layer
          ↓
        Airport NLP
          ↓
        Conversation Manager
          ↓
        Tool Router
          ↓
        ┌───────────────────────┐
        │                       │
        │ Tool required?        │
        │                       │
        ├── YES → MCP → Tool    │
        │                       │
        └── NO  → LLM           │
                                │
        MCP result → Response   │
        """

    def __init__(self):

        # ==================================================
        # LANGUAGE
        # ==================================================

        self.language_layer = LanguageLayer()

        # ==================================================
        # CONVERSATION
        # ==================================================

        self.conversation_manager = ConversationManager()

        # ==================================================
        # AIRPORT NLP
        # ==================================================

        self.airport_nlp = AirportNLP()

        # ==================================================
        # MCP CLIENT
        # ==================================================

        self.mcp_client = MCPClient(
            server_url="http://127.0.0.1:8001/mcp"
        )

        # ==================================================
        # TOOL ROUTER
        # ==================================================

        self.tool_router = ToolRouter(
            mcp_client=self.mcp_client
        )

        # ==================================================
        # LLM
        # ==================================================

        self.llm_client = LLMClient(
            provider="ollama",
            model="qwen2.5:1.5b",
            timeout=15.0,
            max_tokens=60,
            temperature=0.2,
            keep_alive="10m",
        )

        # ==================================================
        # RESPONSE GENERATOR
        # ==================================================

        self.response_generator = ResponseGenerator(
            llm_client=self.llm_client
        )

        print()
        print("=" * 60)
        print("[ORCHESTRATOR] Initialized")
        print("[ORCHESTRATOR] MCP server:")
        print("http://127.0.0.1:8001/mcp")
        print("=" * 60)
        print()

    # ======================================================
    # PROCESS CONVERSATION
    # ======================================================

    async def process(
        self,
        text: str,
        conversation_id: str | None = None,
    ) -> dict:

        total_start = time.perf_counter()

        print()
        print("=" * 60)
        print("[ORCHESTRATOR] PROCESS")
        print("=" * 60)

        print(
            f"[ORCHESTRATOR] User: {text}"
        )

        # ==================================================
        # 1. CONVERSATION ID
        # ==================================================

        stage_start = time.perf_counter()

        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        context = self.conversation_manager.get_or_create(
            conversation_id
        )

        conversation_time = (
            time.perf_counter() - stage_start
        )

        # ==================================================
        # 2. STORE USER MESSAGE
        # ==================================================

        self.conversation_manager.add_message(
            context,
            role="user",
            content=text,
        )

        # ==================================================
        # 3. LANGUAGE ANALYSIS
        # ==================================================

        stage_start = time.perf_counter()

        language_result = self.language_layer.detect(text)
        print()
        print("=" * 60)
        print("[LANGUAGE DEBUG]")
        print("=" * 60)
        print(f"Text              : {text}")
        print(f"Primary language  : {language_result.get('primary_language')}")
        print(f"Languages         : {language_result.get('languages')}")
        print(f"Is mixed          : {language_result.get('is_mixed')}")
        print(f"Confidence        : {language_result.get('confidence')}")
        print("=" * 60)
        print()

        language_time = (
            time.perf_counter() - stage_start
        )

        print(
            f"[ORCHESTRATOR] Language: "
            f"{language_result}"
        )

        self.conversation_manager.update_language(
            context,
            language_result,
        )

        # ==================================================
        # 4. AIRPORT NLP
        # ==================================================

        stage_start = time.perf_counter()

        airport_result = self.airport_nlp.analyze(text)

        nlp_time = (
            time.perf_counter() - stage_start
        )

        intent = airport_result.get(
            "intent",
            "UNKNOWN",
        )

        entities = airport_result.get(
            "entities",
            {},
        )

        print(
            f"[ORCHESTRATOR] Intent: {intent}"
        )

        print(
            f"[ORCHESTRATOR] Entities: {entities}"
        )

        # ==================================================
        # 5. UPDATE INTENT
        # ==================================================

        self.conversation_manager.update_intent(
            context,
            intent,
        )

        # ==================================================
        # 6. ENRICH ENTITIES
        # ==================================================

        stage_start = time.perf_counter()

        enriched_entities = (
            self.conversation_manager.enrich_entities(
                context,
                entities,
            )
        )

        self.conversation_manager.update_entities(
            context,
            enriched_entities,
        )

        context_time = (
            time.perf_counter() - stage_start
        )

        print(
            f"[ORCHESTRATOR] Enriched entities: "
            f"{enriched_entities}"
        )

        # ==================================================
        # 7. TOOL ROUTING
        # ==================================================

        stage_start = time.perf_counter()

        print()
        print("=" * 60)
        print("[ORCHESTRATOR] TOOL ROUTING")
        print("=" * 60)

        print(
            f"[ORCHESTRATOR] Intent: {intent}"
        )

        print(
            f"[ORCHESTRATOR] Entities: "
            f"{enriched_entities}"
        )

        tool_result = None

        try:

            tool_result = await self.tool_router.execute(
                intent=intent,
                entities=enriched_entities,
            )

        except Exception as error:

            print(
                f"[ORCHESTRATOR] MCP ERROR: {error}"
            )

            raise

        mcp_time = (
            time.perf_counter() - stage_start
        )

        # ==================================================
        # 8. DECIDE ROUTE
        # ==================================================

        if tool_result is not None:

            route = "mcp"

            print(
                "[ORCHESTRATOR] Route: MCP"
            )

        else:

            route = "llm"

            print(
                "[ORCHESTRATOR] Route: LLM"
            )

        print("=" * 60)
        print()

        # ==================================================
        # 9. EXTRACT MCP DATA
        # ==================================================

        stage_start = time.perf_counter()

        tool_data: Any = None

        if tool_result is not None:

            print(
                "[ORCHESTRATOR] MCP result received"
            )

            if hasattr(tool_result, "data"):

                tool_data = tool_result.data

            elif hasattr(
                tool_result,
                "structured_content",
            ):

                tool_data = (
                    tool_result.structured_content
                )

            else:

                tool_data = tool_result

        extraction_time = (
            time.perf_counter() - stage_start
        )

        print(
            f"[ORCHESTRATOR] Tool data: "
            f"{tool_data}"
        )

        # ==================================================
        # 10. BUILD CONVERSATION CONTEXT
        # ==================================================

        stage_start = time.perf_counter()

        conversation_context = {
            "conversation_id": context.conversation_id,
            "history": context.history,
            "last_language": context.last_language,
            "active_languages": context.active_languages,
            "current_intent": context.current_intent,
            "entities": context.entities,
        }

        context_build_time = (
            time.perf_counter() - stage_start
        )

        # ==================================================
        # 11. RESPONSE
        # ==================================================

        stage_start = time.perf_counter()

        # ==================================================
        # MCP PATH
        # ==================================================

        if route == "mcp":

            print(
                "[ORCHESTRATOR] Generating response "
                "from MCP data..."
            )

            response = await self.response_generator.generate(
                user_text=text,
                intent=intent,
                entities=enriched_entities,
                tool_result=tool_data,
                conversation_context=conversation_context,
                language_result=language_result,
            )

        # ==================================================
        # LLM PATH
        # ==================================================

        else:

            print(
                "[ORCHESTRATOR] Calling LLM..."
            )

            response = await self.response_generator.generate(
                user_text=text,
                intent=intent,
                entities=enriched_entities,
                tool_result=None,
                conversation_context=conversation_context,
                language_result=language_result,
            )

        response_time = (
            time.perf_counter() - stage_start
        )

        print(
            f"[ORCHESTRATOR] Response: "
            f"{response}"
        )

        # ==================================================
        # 12. STORE ASSISTANT RESPONSE
        # ==================================================

        self.conversation_manager.add_message(
            context,
            role="assistant",
            content=response,
        )

        # ==================================================
        # 13. TOTAL
        # ==================================================

        total_time = (
            time.perf_counter() - total_start
        )

        # ==================================================
        # LATENCY LOG
        # ==================================================

        print()
        print("=" * 60)
        print("LATENCY")
        print("=" * 60)

        print(
            f"Conversation       : "
            f"{conversation_time:.4f}s"
        )

        print(
            f"Language detection : "
            f"{language_time:.4f}s"
        )

        print(
            f"Airport NLP        : "
            f"{nlp_time:.4f}s"
        )

        print(
            f"Context management : "
            f"{context_time:.4f}s"
        )

        print(
            f"MCP                : "
            f"{mcp_time:.4f}s"
        )

        print(
            f"MCP extraction     : "
            f"{extraction_time:.4f}s"
        )

        print(
            f"Context building   : "
            f"{context_build_time:.4f}s"
        )

        print(
            f"Response generation: "
            f"{response_time:.4f}s"
        )

        print("-" * 60)

        print(
            f"ROUTE              : "
            f"{route.upper()}"
        )

        print(
            f"TOTAL              : "
            f"{total_time:.4f}s"
        )

        print("=" * 60)
        print()

        # ==================================================
        # 14. RETURN RESULT
        # ==================================================

        return {
            "status": "success",

            "conversation_id": conversation_id,

            "input": text,

            "response": response,

            "language": language_result,

            "airport": {
                "intent": intent,
                "entities": enriched_entities,
            },

            "route": route,

            "tool_result": tool_data,

            "conversation": {
                "last_language": context.last_language,
                "active_languages": context.active_languages,
                "current_intent": context.current_intent,
                "entities": context.entities,
                "history_length": len(
                    context.history
                ),
            },

            "latency": {
                "conversation": round(
                    conversation_time,
                    4,
                ),

                "language_detection": round(
                    language_time,
                    4,
                ),

                "airport_nlp": round(
                    nlp_time,
                    4,
                ),

                "context_management": round(
                    context_time,
                    4,
                ),

                "mcp": round(
                    mcp_time,
                    4,
                ),

                "mcp_extraction": round(
                    extraction_time,
                    4,
                ),

                "context_building": round(
                    context_build_time,
                    4,
                ),

                "response_generation": round(
                    response_time,
                    4,
                ),

                "total": round(
                    total_time,
                    4,
                ),
            },
        }

