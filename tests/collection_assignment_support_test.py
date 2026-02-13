from fibery_mcp_server.fibery_client import FiberyClient
from fibery_mcp_server.tools import handle_list_tools


def _tool_by_name(tool_name):
    for tool in handle_list_tools():
        if tool.name == tool_name:
            return tool
    return None


def test_update_entity_tool_remains_available():
    assert _tool_by_name("update_entity") is not None


def test_update_collection_tool_is_registered():
    assert _tool_by_name("update_collection") is not None


def test_update_collection_tool_schema_supports_add_and_remove_operations():
    tool = _tool_by_name("update_collection")
    assert tool is not None

    schema = tool.inputSchema
    assert schema["type"] == "object"
    assert set(schema["required"]) >= {"database", "entity_id", "field", "operation", "item_ids"}

    operation = schema["properties"]["operation"]
    assert operation["type"] == "string"
    assert set(operation["enum"]) == {"add", "remove"}

    item_ids = schema["properties"]["item_ids"]
    assert item_ids["type"] == "array"
    assert item_ids["items"]["type"] == "string"


def test_fibery_client_exposes_collection_update_helpers():
    assert hasattr(FiberyClient, "add_collection_items")
    assert hasattr(FiberyClient, "remove_collection_items")
