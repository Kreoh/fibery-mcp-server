from typing import Any, Callable

from fibery_mcp_server.tools.create_entities_batch import create_entities_batch_tool
from fibery_mcp_server.tools.create_entity import create_entity_tool
from fibery_mcp_server.tools.resolve_user import resolve_user_tool
from fibery_mcp_server.tools.unlink_collection import unlink_collection_tool
from fibery_mcp_server.tools.update_collection import update_collection_tool
from fibery_mcp_server.tools.update_entities_batch import update_entities_batch_tool
from fibery_mcp_server.tools.update_entity import update_entity_tool


def _input_schema(tool_factory: Callable[[], Any]) -> dict[str, Any]:
    return tool_factory().inputSchema


def test_write_tool_schemas_disallow_unknown_top_level_parameters() -> None:
    write_tool_factories: dict[str, Callable[[], Any]] = {
        "create_entity": create_entity_tool,
        "create_entities_batch": create_entities_batch_tool,
        "update_entity": update_entity_tool,
        "update_collection": update_collection_tool,
        "unlink_collection": unlink_collection_tool,
        "update_entities_batch": update_entities_batch_tool,
    }

    for tool_name, tool_factory in write_tool_factories.items():
        schema = _input_schema(tool_factory)
        assert schema["type"] == "object"
        assert schema.get("additionalProperties") is False, f"{tool_name} schema should be strict"


def test_update_collection_schema_is_add_only() -> None:
    schema = _input_schema(update_collection_tool)

    operation = schema["properties"]["operation"]
    assert operation["type"] == "string"
    assert set(operation["enum"]) == {"add"}


def test_unlink_collection_schema_requires_confirm_unlink() -> None:
    schema = _input_schema(unlink_collection_tool)

    assert set(schema["required"]) == {"database", "entity_id", "field", "item_ids", "confirm_unlink"}
    assert schema["properties"]["confirm_unlink"]["type"] == "boolean"

    item_ids = schema["properties"]["item_ids"]
    assert item_ids["type"] == "array"
    assert item_ids["items"]["type"] == "string"


def test_update_entities_batch_schema_requires_ids_and_confirmation() -> None:
    schema = _input_schema(update_entities_batch_tool)

    assert set(schema["required"]) == {"database", "entities", "confirm_batch"}
    assert schema["properties"]["confirm_batch"]["type"] == "boolean"
    assert schema["properties"]["fail_fast"]["type"] == "boolean"
    assert schema["properties"]["fail_fast"]["default"] is True

    entities = schema["properties"]["entities"]
    assert entities["type"] == "array"
    assert entities["minItems"] == 1
    assert entities["maxItems"] == 50

    entity_item = entities["items"]
    assert entity_item["type"] == "object"
    assert entity_item["required"] == ["fibery/id"]
    assert entity_item["properties"]["fibery/id"]["type"] == "string"


def test_resolve_user_schema_is_top_level_object_without_any_of() -> None:
    schema = _input_schema(resolve_user_tool)

    assert schema["type"] == "object"
    assert schema.get("additionalProperties") is False
    assert "anyOf" not in schema

    assert schema["properties"]["email"]["type"] == "string"
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["limit"]["type"] == "integer"
    assert schema["properties"]["limit"]["minimum"] == 1
