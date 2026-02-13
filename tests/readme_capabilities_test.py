from pathlib import Path


def _readme_text() -> str:
    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    return readme_path.read_text(encoding="utf-8").lower()


def test_readme_mentions_update_collection_as_add_only() -> None:
    readme = _readme_text()

    assert "update_collection" in readme
    assert ("add-only" in readme) or ("add only" in readme)


def test_readme_mentions_unlink_collection_for_removals() -> None:
    readme = _readme_text()

    assert "unlink_collection" in readme


def test_readme_mentions_update_entities_batch_tool() -> None:
    readme = _readme_text()

    assert "update_entities_batch" in readme


def test_readme_mentions_resolve_user_tool() -> None:
    readme = _readme_text()

    assert "resolve_user" in readme


def test_readme_explicitly_states_delete_is_not_exposed() -> None:
    readme = _readme_text()

    assert "delete is not exposed" in readme
