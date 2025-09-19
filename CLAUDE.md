# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal MCP (Model Context Protocol) server demo project built with Python. The project uses UV for dependency management and is set up as a basic Python package with MCP CLI dependencies.

## Development Commands

### Environment Management
- **Install dependencies**: `uv sync`
- **Add new dependencies**: `uv add <package-name>`

### Running the Clockodo MCP Server
- **Development mode with MCP Inspector**: `uv run mcp dev main.py`
- **Direct execution**: `uv run python main.py`
- **Install for Claude Desktop**: `uv run mcp install main.py --name "Clockodo Time Tracker"`

### Configuration
- **Copy environment template**: `cp .env.example .env`
- **Required environment variables**:
  - `CLOCKODO_EMAIL`: Your Clockodo login email
  - `CLOCKODO_API_KEY`: Your API key from Clockodo (found in "Personal data")

## Project Structure

```
clockodo-mcp-server/
├── main.py              # Entry point for Clockodo MCP server
├── server.py            # FastMCP server with tools and resources
├── clockodo_client.py   # Async HTTP client for Clockodo API
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock             # UV lockfile for reproducible builds
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore patterns (includes .env)
├── README.md           # Comprehensive documentation
└── CLAUDE.md           # This file
```

## Key Dependencies

- **mcp[cli]**: Model Context Protocol with CLI support (>=1.14.1)
- **httpx**: Async HTTP client for Clockodo API (>=0.24.0)
- **python-dotenv**: Environment variable management (>=1.0.0)
- **Python**: Requires Python 3.13 or higher

## Architecture Notes

This is a fully functional MCP server for Clockodo time tracking integration:

### Core Components
- **ClockodoClient**: Async HTTP client with authentication for Clockodo REST API
- **FastMCP Server**: Tools and resources for time tracking operations
- **Environment Management**: Secure API credential handling via .env files

### Available Tools
- `start_time_tracking()`: Start time tracking for customer/project
- `stop_time_tracking()`: Stop current time tracking
- `get_running_entry()`: Get currently running time entry
- `create_time_entry()`: Create manual time entries
- `get_work_summary()`: Get work summary by period

### Available Resources
- `entries://{period}`: Time entries for today/yesterday/week/month
- `customers://all`: All customers
- `projects://{customer_name}`: Projects for specific customer
- `services://all`: All available services

### Claude Desktop Integration
Use Claude to manage time tracking with natural language:
- "Start time tracking for customer XYZ"
- "How many hours did I work this week?"
- "Create a 2-hour entry for development yesterday"

## References
- **Clockodo API Documentation**: https://www.clockodo.com/en/api/