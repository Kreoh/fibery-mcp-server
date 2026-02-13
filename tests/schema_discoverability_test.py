from typing import Any

from fibery_mcp_server.fibery_client import Schema
from fibery_mcp_server.tools.schema import handle_schema, schema_tool


class _FakeFiberyClient:
    def __init__(self, schema: Schema) -> None:
        self._schema = schema

    async def get_schema(self) -> Schema:
        return self._schema


def _raw_schema() -> dict[str, Any]:
    return {
        "fibery/types": [
            {
                "fibery/name": "Product Management/Feature",
                "fibery/meta": {},
                "fibery/fields": [
                    {"fibery/name": "fibery/id", "fibery/type": "fibery/id"},
                    {"fibery/name": "Product Management/Name", "fibery/type": "fibery/text"},
                ],
            },
            {
                "fibery/name": "fibery/user",
                "fibery/meta": {},
                "fibery/fields": [
                    {"fibery/name": "fibery/id", "fibery/type": "fibery/id"},
                    {"fibery/name": "fibery/name", "fibery/type": "fibery/text"},
                ],
            },
            {
                "fibery/name": "workflow/workflow",
                "fibery/meta": {},
                "fibery/fields": [{"fibery/name": "fibery/id", "fibery/type": "fibery/id"}],
            },
        ]
    }


def test_include_databases_from_schema_default_excludes_system_databases() -> None:
    schema = Schema(_raw_schema())

    names = [database.name for database in schema.include_databases_from_schema()]
    assert names == ["Product Management/Feature"]


def test_include_databases_from_schema_can_include_system_databases() -> None:
    schema = Schema(_raw_schema())

    names = [database.name for database in schema.include_databases_from_schema(include_system_databases=True)]
    assert set(names) == {"Product Management/Feature", "fibery/user", "workflow/workflow"}


def test_schema_tool_exposes_include_system_databases_option() -> None:
    input_schema = schema_tool().inputSchema

    assert input_schema["type"] == "object"
    assert input_schema.get("additionalProperties") is False
    assert "include_system_databases" in input_schema["properties"]

    include_system_databases = input_schema["properties"]["include_system_databases"]
    assert include_system_databases["type"] == "boolean"
    assert include_system_databases.get("default") is False


async def test_handle_schema_includes_system_databases_when_requested() -> None:
    schema = Schema(_raw_schema())
    client = _FakeFiberyClient(schema)

    response = await handle_schema(client, {"include_system_databases": True})
    content = response[0].text

    assert "Product Management/Feature" in content
    assert "fibery/user" in content
    assert "workflow/workflow" in content


async def test_handle_schema_treats_string_false_as_disabled_for_system_databases() -> None:
    schema = Schema(_raw_schema())
    client = _FakeFiberyClient(schema)

    response = await handle_schema(client, {"include_system_databases": "false"})
    content = response[0].text

    assert "Product Management/Feature" in content
    assert "fibery/user" not in content
    assert "workflow/workflow" not in content
