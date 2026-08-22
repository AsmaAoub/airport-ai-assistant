import asyncio

from mcp_client.client import MCPClient


async def main():

    client = MCPClient()

    print("\n==============================")
    print("MCP TOOL DISCOVERY")
    print("==============================")

    tools = await client.list_tools()

    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print()

    print("\n==============================")
    print("MCP TOOL CALL")
    print("==============================")

    result = await client.call_tool(
        "get_flight",
        {
            "flight_number": "AT123"
        },
    )

    print("Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())