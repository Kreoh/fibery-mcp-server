import json
import os
from typing import Any, Dict, List

import mcp

from fibery_mcp_server.fibery_client import Database, FiberyClient, Schema

resolve_user_tool_name = "resolve_user"


def resolve_user_tool() -> mcp.types.Tool:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "resolve_user"),
        "r",
    ) as file:
        description = file.read()

    return mcp.types.Tool(
        name=resolve_user_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User email to match exactly.",
                },
                "name": {
                    "type": "string",
                    "description": "User name to match using contains.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of identities to return.",
                },
            },
        },
    )


def _find_email_field(field_names: List[str]) -> str | None:
    if "fibery/email" in field_names:
        return "fibery/email"

    for field_name in field_names:
        lower_field_name = field_name.lower()
        if lower_field_name.endswith("/email") or "email" in lower_field_name:
            return field_name
    return None


def _find_name_field(field_names: List[str]) -> str | None:
    if "fibery/name" in field_names:
        return "fibery/name"

    for field_name in field_names:
        if field_name.lower().endswith("/name"):
            return field_name
    return None


def _candidate_user_databases(schema: Schema, require_email: bool, require_name: bool) -> List[Database]:
    user_databases: List[Database] = []
    fallback_databases: List[Database] = []

    for database in schema.databases:
        field_names = list(database.fields_by_name().keys())
        if "fibery/id" not in field_names:
            continue

        email_field = _find_email_field(field_names)
        name_field = _find_name_field(field_names)
        if require_email and email_field is None:
            continue
        if require_name and name_field is None:
            continue
        if not require_email and not require_name and email_field is None and name_field is None:
            continue

        if "user" in database.name.lower():
            user_databases.append(database)
        else:
            fallback_databases.append(database)

    return user_databases + fallback_databases


async def handle_resolve_user(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    email: str | None = arguments.get("email")
    name: str | None = arguments.get("name")
    limit: int = arguments.get("limit", 10)

    if email is None and name is None:
        return [mcp.types.TextContent(type="text", text="Error: either email or name must be provided.")]

    if limit < 1:
        return [mcp.types.TextContent(type="text", text="Error: limit must be at least 1.")]

    schema: Schema = await fibery_client.get_schema()
    candidate_databases = _candidate_user_databases(
        schema,
        require_email=email is not None,
        require_name=name is not None,
    )
    if len(candidate_databases) == 0:
        return [mcp.types.TextContent(type="text", text="Error: unable to identify a user database in this workspace.")]

    users: List[Dict[str, Any]] = []
    seen_user_ids: set[str] = set()

    for database in candidate_databases:
        if len(users) >= limit:
            break

        field_names = list(database.fields_by_name().keys())
        email_field = _find_email_field(field_names)
        name_field = _find_name_field(field_names)

        query_conditions: List[Any] = []
        query_params: Dict[str, Any] = {}
        if email is not None:
            if email_field is None:
                continue
            query_conditions.append(["=", [email_field], "$email"])
            query_params["$email"] = email
        if name is not None:
            if name_field is None:
                continue
            query_conditions.append(["q/contains", [name_field], "$name"])
            query_params["$name"] = name

        q_select: Dict[str, Any] = {"Id": "fibery/id"}
        if email_field is not None:
            q_select["Email"] = email_field
        if name_field is not None:
            q_select["Name"] = name_field

        query: Dict[str, Any] = {
            "q/from": database.name,
            "q/select": q_select,
            "q/limit": limit - len(users),
        }
        if len(query_conditions) == 1:
            query["q/where"] = query_conditions[0]
        elif len(query_conditions) > 1:
            query["q/where"] = ["q/and", *query_conditions]

        query_result = await fibery_client.query(query, query_params)
        if not query_result.success or not isinstance(query_result.result, list):
            continue

        for entity in query_result.result:
            if not isinstance(entity, dict):
                continue

            user_id = entity.get("Id")
            if not isinstance(user_id, str):
                continue
            if user_id in seen_user_ids:
                continue

            users.append(
                {
                    "fibery/id": user_id,
                    "email": entity.get("Email"),
                    "name": entity.get("Name"),
                }
            )
            seen_user_ids.add(user_id)

            if len(users) >= limit:
                break

    return [mcp.types.TextContent(type="text", text=json.dumps(users))]
