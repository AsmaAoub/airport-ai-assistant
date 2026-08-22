from typing import Any

from mcp_client.client import MCPClient


class ToolRouter:
    """
    Routes airport requests to MCP tools.

    IMPORTANT:

    The router decides whether an airport request requires
    access to external/dynamic data.

    For flight-related requests, if a flight number is known,
    the MCP flight tool is used.

    The LLM must never invent flight information.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
    ):
        self.mcp_client = mcp_client

        # ==================================================
        # INTENT -> MCP TOOL
        # ==================================================

        self.intent_to_tool = {
            "GET_FLIGHT_INFORMATION": "get_flight",
            "GET_FLIGHT_STATUS": "get_flight",
            "GET_FLIGHT_GATE": "get_flight",
            "GET_FLIGHT_TERMINAL": "get_flight",
        }

    # ======================================================
    # EXECUTE
    # ======================================================

    async def execute(
        self,
        intent: str | None,
        entities: dict[str, Any],
    ) -> Any:

        print()
        print("[TOOL ROUTER] --------------------------------")
        print(f"[TOOL ROUTER] Intent   : {intent}")
        print(f"[TOOL ROUTER] Entities : {entities}")

        # ==================================================
        # FLIGHT NUMBER
        # ==================================================

        flight_number = entities.get(
            "flight_number"
        )

        # ==================================================
        # FIND TOOL
        # ==================================================

        tool_name = self.intent_to_tool.get(intent)

        # ==================================================
        # FLIGHT REQUEST
        # ==================================================

        if tool_name == "get_flight":

            if not flight_number:

                print(
                    "[TOOL ROUTER] Flight request detected "
                    "but no flight number is available."
                )

                return {
                    "found": False,
                    "error": "Flight number is missing.",
                }

            print(
                "[TOOL ROUTER] Flight request detected."
            )

            print(
                f"[TOOL ROUTER] Calling MCP tool: "
                f"{tool_name}"
            )

            print(
                f"[TOOL ROUTER] Arguments: "
                f"flight_number={flight_number}"
            )

            result = await self.mcp_client.call_tool(
                tool_name,
                {
                    "flight_number": flight_number,
                },
            )

            print(
                "[TOOL ROUTER] MCP call completed."
            )

            print(
                f"[TOOL ROUTER] Result: {result}"
            )

            return result

        # ==================================================
        # NO TOOL
        # ==================================================

        print(
            "[TOOL ROUTER] No MCP tool required."
        )

        print(
            "[TOOL ROUTER] --------------------------------"
        )

        return None