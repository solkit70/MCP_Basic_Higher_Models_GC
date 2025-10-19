"""
Minimal MCP server using official SDK (FastMCP) over stdio.

Exposes:
- tool: ping() -> str
- tool: health() -> dict
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("GC Demo Server")


@mcp.tool()
def ping() -> str:
    """Simple ping tool."""
    return "pong"


@mcp.tool()
def health() -> dict[str, str]:
    """Return basic health info."""
    return {"status": "ok"}


if __name__ == "__main__":
    # Run over stdio so clients can spawn us easily
    mcp.run(transport="stdio")
