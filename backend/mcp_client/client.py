from fastmcp import Client


class MCPClient:
    """
    Client responsible for communicating
    with the Airport MCP Server.
    """

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8001/mcp",
    ):
        self.server_url = server_url

        print()
        print("=" * 60)
        print("[MCP CLIENT] Initialized")
        print(
            f"[MCP CLIENT] Server: "
            f"{self.server_url}"
        )
        print("=" * 60)
        print()

    # ======================================================
    # LIST TOOLS
    # ======================================================

    async def list_tools(self):

        print(
            "[MCP CLIENT] Listing tools..."
        )

        async with Client(
            self.server_url
        ) as client:

            tools = await client.list_tools()

            print(
                "[MCP CLIENT] Available tools:"
            )

            for tool in tools:

                print(
                    f"  - {tool.name}"
                )

            return tools

    # ======================================================
    # CALL TOOL
    # ======================================================

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):

        print()
        print("=" * 60)
        print("[MCP CLIENT] CALL TOOL")
        print("=" * 60)

        print(
            f"[MCP CLIENT] Server: "
            f"{self.server_url}"
        )

        print(
            f"[MCP CLIENT] Tool: "
            f"{tool_name}"
        )

        print(
            f"[MCP CLIENT] Arguments: "
            f"{arguments}"
        )

        try:

            async with Client(
                self.server_url
            ) as client:

                print(
                    "[MCP CLIENT] Connected."
                )

                result = await client.call_tool(
                    tool_name,
                    arguments,
                )

                print(
                    "[MCP CLIENT] Tool executed."
                )

                print(
                    f"[MCP CLIENT] Raw result: "
                    f"{result}"
                )

                print("=" * 60)
                print()

                return result

        except Exception as error:

            print()
            print("=" * 60)
            print("[MCP CLIENT] ERROR")
            print("=" * 60)

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            print("=" * 60)
            print()

            raise