from typing import Any, Callable
from unittest.mock import AsyncMock

from pytest import MonkeyPatch

from fibery_mcp_server.fibery_client import FiberyClient
from fibery_mcp_server.tools.create_entities_batch import create_entities_batch_tool, handle_create_entities_batch
from fibery_mcp_server.tools.create_entity import create_entity_tool
from fibery_mcp_server.tools.update_entity import update_entity_tool


def _input_schema(tool_factory: Callable[[], Any]) -> dict[str, Any]:
    return tool_factory().inputSchema


def test_create_entity_schema_disallows_unknown_top_level_parameters() -> None:
    schema = _input_schema(create_entity_tool)

    assert schema.get("additionalProperties") is False


def test_update_entity_schema_disallows_unknown_top_level_parameters() -> None:
    schema = _input_schema(update_entity_tool)

    assert schema.get("additionalProperties") is False


def test_create_entities_batch_schema_is_strict_and_bounded() -> None:
    schema = _input_schema(create_entities_batch_tool)
    entities = schema["properties"]["entities"]

    assert schema.get("additionalProperties") is False
    assert entities.get("minItems") == 1
    assert entities.get("maxItems") == 50


def test_create_entities_batch_schema_exposes_optional_confirm_batch() -> None:
    schema = _input_schema(create_entities_batch_tool)

    assert "confirm_batch" in schema["properties"]
    assert schema["properties"]["confirm_batch"]["type"] == "boolean"
    assert "confirm_batch" not in schema["required"]


async def test_create_entities_batch_requires_confirmation_for_large_batches(monkeypatch: MonkeyPatch) -> None:
    client = FiberyClient("example.fibery.io", "test-token")
    get_schema_mock = AsyncMock(side_effect=AssertionError("Large batch should be rejected before schema lookup"))
    monkeypatch.setattr(client, "get_schema", get_schema_mock)

    arguments = {
        "database": "Product Management/Feature",
        "entities": [{"Product Management/Name": f"Feature {index}"} for index in range(11)],
    }

    response = await handle_create_entities_batch(client, arguments)

    assert len(response) == 1
    assert "confirm_batch" in response[0].text.lower()
    get_schema_mock.assert_not_awaited()


async def test_create_entities_batch_rejects_more_than_fifty_entities_before_schema_lookup(
    monkeypatch: MonkeyPatch,
) -> None:
    client = FiberyClient("example.fibery.io", "test-token")
    get_schema_mock = AsyncMock(
        side_effect=AssertionError("Entity count limit should be enforced before schema lookup")
    )
    monkeypatch.setattr(client, "get_schema", get_schema_mock)

    arguments = {
        "database": "Product Management/Feature",
        "entities": [{"Product Management/Name": f"Feature {index}"} for index in range(51)],
        "confirm_batch": True,
    }

    response = await handle_create_entities_batch(client, arguments)

    assert len(response) == 1
    assert "50" in response[0].text
    get_schema_mock.assert_not_awaited()
