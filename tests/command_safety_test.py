from typing import Any
from unittest.mock import AsyncMock

from pytest import MonkeyPatch

from fibery_mcp_server.fibery_client import FiberyClient


def _client() -> FiberyClient:
    return FiberyClient("example.fibery.io", "test-token")


async def test_execute_command_blocks_top_level_delete_command(monkeypatch: MonkeyPatch) -> None:
    client = _client()
    fetch_mock = AsyncMock(side_effect=AssertionError("Delete commands should be blocked before API calls"))
    monkeypatch.setattr(client, "fetch_from_fibery", fetch_mock)

    response = await client.execute_command(
        "fibery.entity/delete",
        {
            "type": "Product Management/Feature",
            "entity": {"fibery/id": "entity-1"},
        },
    )

    assert response.success is False
    assert "delete" in str(response.result).lower()
    fetch_mock.assert_not_awaited()


async def test_execute_command_blocks_batch_with_disallowed_nested_command(monkeypatch: MonkeyPatch) -> None:
    client = _client()
    fetch_mock = AsyncMock(side_effect=AssertionError("Disallowed nested commands should be blocked before API calls"))
    monkeypatch.setattr(client, "fetch_from_fibery", fetch_mock)

    response = await client.execute_command(
        "fibery.command/batch",
        {
            "commands": [
                {
                    "command": "fibery.entity/create",
                    "args": {
                        "type": "Product Management/Feature",
                        "entity": {"Product Management/Name": "New Feature"},
                    },
                },
                {
                    "command": "fibery.entity/delete",
                    "args": {
                        "type": "Product Management/Feature",
                        "entity": {"fibery/id": "entity-2"},
                    },
                },
            ]
        },
    )

    assert response.success is False
    assert "fibery.entity/delete" in str(response.result)
    fetch_mock.assert_not_awaited()


async def test_execute_command_allows_batch_with_nested_create_and_update(monkeypatch: MonkeyPatch) -> None:
    client = _client()
    observed_request: dict[str, Any] = {}

    async def fake_fetch(
        url: str,
        method: str = "GET",
        json_data: Any | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        observed_request["url"] = url
        observed_request["method"] = method
        observed_request["json_data"] = json_data
        observed_request["params"] = params
        return {"data": [{"success": True, "result": {"ok": True}}]}

    monkeypatch.setattr(client, "fetch_from_fibery", fake_fetch)

    response = await client.execute_command(
        "fibery.command/batch",
        {
            "commands": [
                {
                    "command": "fibery.entity/create",
                    "args": {
                        "type": "Product Management/Feature",
                        "entity": {"Product Management/Name": "Create in batch"},
                    },
                },
                {
                    "command": "fibery.entity/update",
                    "args": {
                        "type": "Product Management/Feature",
                        "entity": {
                            "fibery/id": "entity-3",
                            "Product Management/Name": "Update in batch",
                        },
                    },
                },
            ]
        },
    )

    assert response.success is True
    assert response.result == {"ok": True}

    payload = observed_request["json_data"][0]
    nested_commands = payload["args"]["commands"]
    assert payload["command"] == "fibery.command/batch"
    assert [nested["command"] for nested in nested_commands] == ["fibery.entity/create", "fibery.entity/update"]
