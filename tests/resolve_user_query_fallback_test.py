import json
from typing import Any

from fibery_mcp_server.fibery_client import CommandResponse, Schema
from fibery_mcp_server.tools.resolve_user import handle_resolve_user


class _FakeResolveUserClient:
    def __init__(self, schema: Schema, query_results: dict[str, list[dict[str, Any]]]) -> None:
        self._schema = schema
        self._query_results = query_results
        self.queried_databases: list[str] = []

    async def get_schema(self) -> Schema:
        return self._schema

    async def query(self, query: dict[str, Any], params: dict[str, Any] | None) -> CommandResponse:
        del params
        database_name = str(query["q/from"])
        self.queried_databases.append(database_name)
        return CommandResponse(True, self._query_results.get(database_name, []))


def _raw_schema_with_user_name_only_and_contact_email_only() -> dict[str, Any]:
    return {
        "fibery/types": [
            {
                "fibery/name": "People/User Profile",
                "fibery/meta": {},
                "fibery/fields": [
                    {"fibery/name": "fibery/id", "fibery/type": "fibery/id"},
                    {"fibery/name": "People/Name", "fibery/type": "fibery/text"},
                ],
            },
            {
                "fibery/name": "Directory/Contact",
                "fibery/meta": {},
                "fibery/fields": [
                    {"fibery/name": "fibery/id", "fibery/type": "fibery/id"},
                    {"fibery/name": "Directory/Email", "fibery/type": "fibery/text"},
                ],
            },
        ]
    }


async def test_resolve_user_email_lookup_uses_fallback_database_with_email_only_field() -> None:
    schema = Schema(_raw_schema_with_user_name_only_and_contact_email_only())
    client = _FakeResolveUserClient(
        schema,
        {
            "Directory/Contact": [
                {
                    "Id": "user-1",
                    "Email": "alex@example.com",
                }
            ]
        },
    )

    response = await handle_resolve_user(client, {"email": "alex@example.com"})
    resolved_users = json.loads(response[0].text)

    assert "Directory/Contact" in client.queried_databases
    assert resolved_users == [{"fibery/id": "user-1", "email": "alex@example.com", "name": None}]
