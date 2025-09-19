"""
Clockodo MCP Server - Main entry point for time tracking integration.
This server provides tools and resources for managing Clockodo time entries via Claude.
"""

from logging_config import setup_logging

# Configure logging first
setup_logging()

# Import server object at module level for MCP CLI compatibility
from server import mcp


def main():
    """Run the Clockodo MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
