from typing import Any

from fibery_mcp_server.tools import handle_list_tools


def _tool_by_name(tool_name: str) -> Any | None:
    for tool in handle_list_tools():
        if tool.name == tool_name:
            return tool
    return None


def test_resolve_user_tool_is_registered() -> None:
    assert _tool_by_name("resolve_user") is not None


def test_resolve_user_schema_is_strict_and_exposes_identity_filters() -> None:
    tool = _tool_by_name("resolve_user")
    assert tool is not None

    schema = tool.inputSchema
    assert schema["type"] == "object"
    assert schema.get("additionalProperties") is False

    properties = schema["properties"]
    assert set(properties) >= {"email", "name", "limit"}
    assert properties["email"]["type"] == "string"
    assert properties["name"]["type"] == "string"
    assert properties["limit"]["type"] == "integer"
    assert properties["limit"].get("minimum", 1) >= 1


def test_resolve_user_description_mentions_normalised_identity_fields() -> None:
    tool = _tool_by_name("resolve_user")
    assert tool is not None

    description = tool.description.lower()
    assert "fibery/id" in description
    assert "email" in description
    assert "name" in description
