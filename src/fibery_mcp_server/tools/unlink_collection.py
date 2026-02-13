import json
import os
from dataclasses import asdict
from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient

unlink_collection_tool_name = "unlink_collection"


def unlink_collection_tool() -> mcp.types.Tool:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "unlink_collection"),
        "r",
    ) as file:
        description = file.read()

    return mcp.types.Tool(
        name=unlink_collection_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "database": {
                    "type": "string",
                    "description": "Fibery Database where the entity is stored.",
                },
                "entity_id": {
                    "type": "string",
                    "description": "fibery/id of the entity to update.",
                },
                "field": {
                    "type": "string",
                    "description": "Collection relation field name (for example, assignments/assignees).",
                },
                "item_ids": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "List of related entity fibery/id values to unlink.",
                },
                "confirm_unlink": {
                    "type": "boolean",
                    "description": "Explicit confirmation for unlink/removal operations. Must be true.",
                },
            },
            "required": ["database", "entity_id", "field", "item_ids", "confirm_unlink"],
        },
    )


async def handle_unlink_collection(
    fibery_client: FiberyClient, arguments: Dict[str, Any]
) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    entity_id: str = arguments.get("entity_id")
    field: str = arguments.get("field")
    item_ids: List[str] = arguments.get("item_ids")
    confirm_unlink: bool = arguments.get("confirm_unlink", False)

    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    if not entity_id:
        return [mcp.types.TextContent(type="text", text="Error: entity_id is not provided.")]

    if not field:
        return [mcp.types.TextContent(type="text", text="Error: field is not provided.")]

    if not item_ids or len(item_ids) == 0:
        return [mcp.types.TextContent(type="text", text="Error: item_ids is not provided.")]

    if confirm_unlink is not True:
        return [
            mcp.types.TextContent(
                type="text",
                text="Error: confirm_unlink must be true to remove relation items.",
            )
        ]

    update_result = await fibery_client.remove_collection_items(database_name, entity_id, field, item_ids)

    if not update_result.success:
        return [mcp.types.TextContent(type="text", text=json.dumps(asdict(update_result)))]

    return [
        mcp.types.TextContent(
            type="text",
            text=(
                "Collection items unlinked successfully. "
                f'Database: "{database_name}", Entity: "{entity_id}", Field: "{field}".'
            ),
        )
    ]
