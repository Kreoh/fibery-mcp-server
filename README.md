# Fibery MCP Server
[![smithery badge](https://smithery.ai/badge/@Fibery-inc/fibery-mcp-server)](https://smithery.ai/server/@Fibery-inc/fibery-mcp-server)
<a href="https://github.com/Fibery-inc/fibery-mcp-server/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" /></a>

This MCP (Model Context Protocol) server provides integration between Fibery and any LLM provider supporting the MCP protocol (e.g., Claude for Desktop), allowing you to interact with your Fibery workspace using natural language.

## ✨ Features
- Discover available Fibery databases and inspect their fields
- Query Fibery entities with flexible `q/from`, `q/select`, `q/where`, ordering, and pagination
- Create entities individually or in batch
- Update existing entities, including rich-text document fields
- Add or remove items in collection relation fields
- Use a date helper tool for ISO 8601 timestamps in workflows and prompts

## 📦 Installation

### Installing via Smithery

To install Fibery MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@Fibery-inc/fibery-mcp-server):

```bash
npx -y @smithery/cli install @Fibery-inc/fibery-mcp-server --client claude
```

### Installing via UV
#### Pre-requisites:
- A Fibery account with an API token
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv)

#### Installation Steps:
1. Install the tool using uv:
```bash
uv tool install fibery-mcp-server
```

2. Then, add this configuration to your MCP client config file. In Claude Desktop, you can access the config in **Settings → Developer → Edit Config**:
```json
{
    "mcpServers": {
        "fibery-mcp-server": {
            "command": "uv",
            "args": [
                 "tool",
                 "run",
                 "fibery-mcp-server",
                 "--fibery-host",
                 "your-domain.fibery.io",
                 "--fibery-api-token",
                 "your-api-token"
            ]
        }
    }
}
```
Note: If "uv" command does not work, try absolute path (i.e. /Users/username/.local/bin/uv)

**For Development:**

```json
{
    "mcpServers": {
        "fibery-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/cloned/fibery-mcp-server",
                "run",
                "fibery-mcp-server",
                "--fibery-host",
                 "your-domain.fibery.io",
                 "--fibery-api-token",
                 "your-api-token"
            ]
        }
    }
}
```

## 🚀 Available Tools

#### 1. Current Date (`current_date`)

Returns the current date/time in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS.000Z`).

#### 2. List Databases (`list_databases`)

Retrieves a list of all databases available in your Fibery workspace.

#### 3. Describe Database (`describe_database`)

Provides a detailed breakdown of a specific database's structure, showing all fields with their titles, names, and types.

#### 4. Query Database (`query_database`)

Provides flexible access to Fibery data through `fibery.entity/query` (including filters, sorting, pagination, and params).

#### 5. Create Entity (`create_entity`)

Creates new entities in your Fibery workspace with specified field values.

#### 6. Create Entities (`create_entities_batch`)

Creates multiple new entities in your Fibery workspace with specified field values.

#### 7. Update Entity (`update_entity`)

Updates existing entities in your Fibery workspace with new field values.

#### 8. Update Collection (`update_collection`)

Adds or removes relation items in collection fields (for example, assigning or unassigning related entities).

## 🧪 Development and Quality Checks

Install dependencies:

```bash
uv sync --dev
```

Run quality gates:

```bash
uv lock --check
uv run --frozen ruff check src tests
uv run --frozen ruff format --check src tests
uv run --frozen pytest
```

Install pre-commit hooks:

```bash
uv run --frozen pre-commit install
uv run --frozen pre-commit install --hook-type commit-msg
```
