# AGENTS Guide

This file is the contributor guide for humans and coding agents working in `fibery-mcp-server`.
Keep this document in sync when tooling, workflows, or project structure changes.

## Project snapshot

- Project: `fibery-mcp-server`
- Purpose: MCP server that exposes Fibery operations as tools over stdio
- Runtime entrypoint: `fibery-mcp-server` (script) -> `fibery_mcp_server:main`
- Python: `>=3.10` (`.python-version` is `3.10`)
- Package manager: `uv`

## Repository layout

- `src/fibery_mcp_server/server.py`: click CLI + MCP server bootstrap
- `src/fibery_mcp_server/fibery_client.py`: Fibery HTTP client and schema/entity helpers
- `src/fibery_mcp_server/tools/`: MCP tool definitions and handlers
- `src/fibery_mcp_server/tools/descriptions/`: long-form tool behaviour prompts
- `tests/`: test suite (tool metadata/unit checks + Fibery integration tests)
- `pyproject.toml`: dependencies, lint config, pytest config, package entrypoint
- `uv.lock`: locked dependencies (must stay in sync with `pyproject.toml`)

## Required configuration

Runtime requires these environment variables:

- `FIBERY_HOST` (example: `your-domain.fibery.io`)
- `FIBERY_API_TOKEN`

Notes:

- `parse_fibery_host` strips `https://`, so either plain host or URL works.
- Never log or hardcode API tokens.

## Local development

1. Install dependencies:

```bash
uv sync --dev
```

2. Run the server locally:

```bash
uv run fibery-mcp-server --fibery-host your-domain.fibery.io --fibery-api-token your-token
```

3. Alternative module invocation:

```bash
uv run python -m fibery_mcp_server --fibery-host your-domain.fibery.io --fibery-api-token your-token
```

## Quality gates

Run these before opening a PR:

```bash
uv lock --check
uv run --frozen ruff check src tests
uv run --frozen ruff format --check src tests
uv run --frozen pytest
```

If formatting is needed:

```bash
uv run --frozen ruff format src tests
```

## Pre-commit hooks

This repository uses pre-commit with local `uv`-based hooks.

Install hooks:

```bash
uv run --frozen pre-commit install
uv run --frozen pre-commit install --hook-type commit-msg
```

Run all hooks manually:

```bash
uv run --frozen pre-commit run --all-files
```

Before committing, run pre-commit on changed files (or all files if preferred):

```bash
uv run --frozen pre-commit run --files <changed-files>
```

## Tool implementation conventions

When adding a new MCP tool:

1. Add a module under `src/fibery_mcp_server/tools/` with:
   - `<tool_name>_tool_name`
   - `<tool_name>_tool() -> mcp.types.Tool`
   - `handle_<tool_name>(...)`
2. If the description is long, add/update a text file in `src/fibery_mcp_server/tools/descriptions/` and load it in the tool factory.
3. Register the tool in both places in `src/fibery_mcp_server/tools/__init__.py`:
   - `handle_list_tools()`
   - `handle_tool_call(...)`
4. Add/adjust tests in `tests/` (schema/metadata coverage and behaviour checks).

Keep tool names and schema properties stable unless there is a deliberate breaking change.

## Fibery API interaction rules

- Use `FiberyClient` for all Fibery HTTP calls.
- Reuse existing command wrappers (`query`, `create_entity`, `update_entity`, collection helpers) instead of duplicating raw command payloads.
- For rich-text/document fields, follow existing read/write flow (`Collaboration~Documents/secret` + document command endpoints).
- Return user-safe error messages from tool handlers; avoid leaking tokens or sensitive headers.

## Testing notes

- `tests/fibery_service_test.py` hits a real Fibery workspace and is skipped unless `FIBERY_HOST` and `FIBERY_API_TOKEN` are set.
- Other tests validate tool registration and input schema shape and should run without external services.
- For test runs, use `uv run --frozen pytest` (add flags/paths as needed, for example `uv run --frozen pytest -q tests/command_safety_test.py`).

## Dependency and release hygiene

- Any dependency change in `pyproject.toml` must be followed by updating `uv.lock`.
- Build artifacts:

```bash
uv build
```

- Do not commit secrets or local `.env` files.

## Style baseline

- Follow existing repository style (type hints, simple functional modules, explicit schemas).
- Keep tool input schemas strict where practical (`additionalProperties: false` when appropriate).
- Keep line length compatible with Ruff config (`line-length = 120`).
- When answering in English, you MUST use British English and never use American English spelling or phraseology.
