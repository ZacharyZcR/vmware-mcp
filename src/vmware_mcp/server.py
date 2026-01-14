"""VMware MCP Server - Core server implementation."""

from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("vmware-mcp")


def main():
    """Entry point for the MCP server."""
    import asyncio
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
