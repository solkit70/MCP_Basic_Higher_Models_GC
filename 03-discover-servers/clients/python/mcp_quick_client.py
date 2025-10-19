"""
Minimal MCP client using official SDK over stdio.
Spawns the local fastmcp_quick_server.py and:
- initialize
- list tools
- call health tool
Prints machine-readable JSON for logs.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    server_path = repo_root / "03-discover-servers" / "servers" / "fastmcp_quick_server.py"
    if not server_path.exists():
        print(json.dumps({"error": f"Server script not found: {server_path}"}))
        return 2

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=dict(os.environ),
    )

    out: dict = {"tools": [], "health": None}

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            out["tools"] = [t.name for t in tools.tools]

            # Call health tool if present
            if any(t.name == "health" for t in tools.tools):
                res = await session.call_tool("health", arguments={})
                # Prefer structured content if available
                out["health"] = getattr(res, "structuredContent", None)
                if not out["health"] and res.content:
                    # Fallback: read first text content
                    from mcp import types as _types

                    for c in res.content:
                        if isinstance(c, _types.TextContent):
                            out["health"] = {"text": c.text}
                            break

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
