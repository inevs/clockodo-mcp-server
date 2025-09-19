# Repository Guidelines

## Project Structure & Module Organization
All Python sources live at the repository root. `main.py` bootstraps the MCP server by delegating to `server.py`, which defines FastMCP tools and resources. `clockodo_client.py` contains the async HTTP client that wraps the Clockodo REST API. Configuration lives in `pyproject.toml`, with locked versions in `uv.lock`. Place new integration helpers beside the related module, and add any future unit tests under a top-level `tests/` package (create it when needed) that mirrors the module layout.

## Build, Test, and Development Commands
Use `uv sync` to install or refresh dependencies from `pyproject.toml`. During development run `uv run mcp dev main.py` to launch the inspector-friendly MCP server. For a headless server session execute `uv run python main.py`. Install the agent into Claude Desktop via `uv run mcp install main.py --name "Clockodo Time Tracker"`. When environment variables are required, provide them with `uv run mcp install main.py -f .env` after copying `.env.example`.

## Coding Style & Naming Conventions
Target Python 3.13 and follow PEP 8: four-space indentation, `snake_case` for functions/resources, and `PascalCase` for dataclasses. Maintain module-level docstrings and type hints, as seen in the existing tools, to keep MCP schemas explicit. Prefer descriptive variable names (e.g., `customers_id`) and keep async functions side-effect free beyond API interactions. Run a formatter such as `uv run python -m black .` before committing if you introduce broader edits.

## Testing Guidelines
A formal test suite is not yet present; add `pytest`-based tests under `tests/`, naming files `test_<module>.py`. Mock HTTP calls to `ClockodoClient` so tests remain fast and offline. Aim to cover new behaviors and error paths (authentication failures, empty results). Execute `uv run pytest` locally and capture the summary in your pull request.

## Commit & Pull Request Guidelines
Existing history favors short, present-tense messages (`Add retry for Clockodo client`). Group related changes per commit and avoid bundling secrets. Pull requests should summarize user-facing effects, note any environment variable changes, and include the test command output. Link relevant issues or task IDs and attach screenshots only when they clarify UX flows in Claude Desktop.

## Configuration & Security Notes
Never commit `.env` files. Populate `CLOCKODO_EMAIL` and `CLOCKODO_API_KEY` locally, and rotate keys if the server reports authentication failures. Validate that `.gitignore` captures additional secrets you introduce, and document new configuration flags in `README.md` alongside update instructions for Claude users.
