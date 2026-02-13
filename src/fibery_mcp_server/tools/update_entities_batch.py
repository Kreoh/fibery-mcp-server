import json
import os
from dataclasses import asdict
from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient

update_entities_batch_tool_name = "update_entities_batch"


def update_entities_batch_tool() -> mcp.types.Tool:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "update_entities_batch"),
        "r",
    ) as file:
        description = file.read()

    return mcp.types.Tool(
        name=update_entities_batch_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "database": {
                    "type": "string",
                    "description": "Fibery Database where entities will be updated.",
                },
                "entities": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 50,
                    "items": {
                        "type": "object",
                        "properties": {
                            "fibery/id": {
                                "type": "string",
                            }
                        },
                        "required": ["fibery/id"],
                        "additionalProperties": True,
                    },
                    "description": "List of entities to update. Each item must include fibery/id.",
                },
                "confirm_batch": {
                    "type": "boolean",
                    "description": "Explicit confirmation for batch updates. Must be true.",
                },
                "fail_fast": {
                    "type": "boolean",
                    "default": True,
                    "description": "If true, return as soon as a failed nested update is detected.",
                },
            },
            "required": ["database", "entities", "confirm_batch"],
        },
    )


async def handle_update_entities_batch(
    fibery_client: FiberyClient, arguments: Dict[str, Any]
) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    entities: List[Dict[str, Any]] = arguments.get("entities")
    confirm_batch: bool = arguments.get("confirm_batch", False)
    fail_fast: bool = arguments.get("fail_fast", True)

    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    if not entities or len(entities) == 0:
        return [mcp.types.TextContent(type="text", text="Error: entities is not provided.")]

    if len(entities) > 50:
        return [mcp.types.TextContent(type="text", text="Error: entities cannot contain more than 50 items.")]

    if confirm_batch is not True:
        return [
            mcp.types.TextContent(
                type="text",
                text="Error: confirm_batch must be true to execute a batch update.",
            )
        ]

    missing_ids = [index for index, entity in enumerate(entities) if not entity.get("fibery/id")]
    if len(missing_ids) > 0:
        missing_ids_str = ", ".join(map(str, missing_ids))
        return [
            mcp.types.TextContent(
                type="text",
                text=f"Error: every entity must include fibery/id. Missing in items: {missing_ids_str}.",
            )
        ]

    update_batch_result = await fibery_client.update_entities_batch(database_name, entities)
    if not update_batch_result.success:
        return [mcp.types.TextContent(type="text", text=json.dumps(asdict(update_batch_result)))]

    if isinstance(update_batch_result.result, list):
        failed_nested_results = [result for result in update_batch_result.result if not result.get("success", False)]
        if len(failed_nested_results) > 0:
            if fail_fast:
                return [
                    mcp.types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "success": False,
                                "result": failed_nested_results[0],
                            }
                        ),
                    )
                ]
            return [
                mcp.types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "success": False,
                            "result": failed_nested_results,
                        }
                    ),
                )
            ]

    updated_count = len(update_batch_result.result) if isinstance(update_batch_result.result, list) else len(entities)
    return [mcp.types.TextContent(type="text", text=f"{updated_count} entities updated successfully.")]
