from fastmcp import FastMCP

from tools.flight import FlightTool


# ==========================================================
# MCP SERVER
# ==========================================================

mcp = FastMCP(
    "Airport Flight Server",
)


# ==========================================================
# FLIGHT TOOL
# ==========================================================

flight_tool = FlightTool()


@mcp.tool()
async def get_flight(flight_number: str) -> dict:
    """
    Retrieve information about an airport flight.

    Args:
        flight_number: Flight number such as AT123 or AF456.

    Returns:
        Flight information including status, gate and terminal.
    """

    return await flight_tool.get_flight(
        flight_number
    )


# ==========================================================
# SERVER ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )