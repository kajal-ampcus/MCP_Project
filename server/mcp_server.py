from mcp.server.fastmcp import FastMCP

from server.config import HOST, PORT


mcp = FastMCP(
    "Weather MCP Server",
    host=HOST,
    port=PORT,
)
