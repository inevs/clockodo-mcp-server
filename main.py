"""
Clockodo MCP Server - Main entry point for time tracking integration.
This server provides tools and resources for managing Clockodo time entries via Claude.
"""

from logging_config import setup_logging


def main():
    """Run the Clockodo MCP server."""
    setup_logging()

    # Import within function to ensure logging is configured before server modules load
    from server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
