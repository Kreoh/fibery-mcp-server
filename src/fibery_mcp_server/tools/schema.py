from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient, Schema, Database

schema_tool_name = "list_databases"


def schema_tool() -> mcp.types.Tool:
    return mcp.types.Tool(
        name=schema_tool_name,
        description="Get list of all databases (their names) in user's Fibery workspace (schema)",
        inputSchema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "include_system_databases": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include internal/system databases (such as fibery/* and workflow/*).",
                }
            },
        },
    )


async def handle_schema(
    fibery_client: FiberyClient, arguments: Dict[str, Any] | None = None
) -> List[mcp.types.TextContent]:
    include_system_databases = bool(arguments.get("include_system_databases", False)) if arguments else False

    schema: Schema = await fibery_client.get_schema()
    db_list: List[Database] = schema.include_databases_from_schema(include_system_databases=include_system_databases)

    if not db_list:
        content = "No databases found in this Fibery workspace."
    else:
        content = "Databases in Fibery workspace:\n\n"
        for i, db in enumerate(db_list, 1):
            content += f"{i}. {db.name}\n"

    return [mcp.types.TextContent(type="text", text=content)]
