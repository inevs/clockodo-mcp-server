"""
Clockodo MCP Server - Main entry point for time tracking integration.
This server provides tools and resources for managing Clockodo time entries via Claude.
"""

from server import mcp

def main():
    """Run the Clockodo MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
