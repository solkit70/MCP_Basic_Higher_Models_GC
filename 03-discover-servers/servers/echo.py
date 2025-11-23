"""
FastMCP Echo Server

Source: https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/fastmcp/echo.py
License: MIT (from modelcontextprotocol/python-sdk)

This is a minimal MCP server that demonstrates:
- Tool: echo_tool(text) - echoes back the input text
- Resources: static and templated echo resources
- Prompt: echo prompt function
"""

from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text


@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"


@mcp.resource("echo://{text}")
def echo_template(text: str) -> str:
    """Echo the input text"""
    return f"Echo: {text}"


@mcp.prompt("echo")
def echo_prompt(text: str) -> str:
    return text


if __name__ == "__main__":
    # Run over stdio so clients can spawn us easily
    mcp.run(transport="stdio")
