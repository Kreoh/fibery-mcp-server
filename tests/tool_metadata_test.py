from fibery_mcp_server.tools.create_entities_batch import create_entities_batch_tool
from fibery_mcp_server.tools.current_date import current_date_tool
from fibery_mcp_server.tools.query import query_tool


def _input_schema(tool_factory):
    return tool_factory().inputSchema


def test_query_schema_exposes_core_query_fields():
    schema = _input_schema(query_tool)

    assert schema["type"] == "object"
    for name in ("q_from", "q_select", "q_where", "q_order_by", "q_limit", "q_offset", "q_params"):
        assert name in schema["properties"]


def test_query_where_schema_is_array_with_items():
    schema = _input_schema(query_tool)

    q_where = schema["properties"]["q_where"]
    assert q_where["type"] == "array"
    assert q_where["items"] == {}


def test_query_description_does_not_claim_arbitrary_command_execution():
    description = query_tool().description.lower()

    assert "run any fibery api command" not in description


def test_query_schema_disallows_unknown_top_level_parameters():
    schema = _input_schema(query_tool)

    assert schema.get("additionalProperties") is False


def test_query_schema_requires_only_from_and_select():
    schema = _input_schema(query_tool)

    required = set(schema["required"])
    assert required == {"q_from", "q_select"}


def test_create_entities_batch_entities_is_array_of_objects():
    schema = _input_schema(create_entities_batch_tool)

    entities = schema["properties"]["entities"]
    assert entities["type"] == "array"
    assert entities["items"]["type"] == "object"


def test_create_entities_batch_requires_database_and_entities():
    schema = _input_schema(create_entities_batch_tool)

    assert set(schema["required"]) == {"database", "entities"}


def test_current_date_description_matches_iso_8601_shape():
    description = current_date_tool().description

    assert "YYYY-MM-DDTHH:MM:SS.000Z" in description
