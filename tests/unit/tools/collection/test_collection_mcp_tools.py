from __future__ import annotations

from unittest.mock import MagicMock


def test_collection_list_formats_visibility_and_objects(monkeypatch):
    from server.adapters.mcp.areas.collection import collection_list

    handler = MagicMock()
    handler.list_collections.return_value = [
        {
            "name": "Props",
            "parent": None,
            "object_count": 2,
            "child_count": 1,
            "hide_viewport": True,
            "hide_render": False,
            "hide_select": True,
            "objects": ["Cube", "Sphere"],
        }
    ]

    monkeypatch.setattr("server.adapters.mcp.areas.collection.get_collection_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.collection.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.collection.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = collection_list(MagicMock(), include_objects=True)

    assert "Collections (1):" in result
    assert "Props" in result
    assert "hidden-viewport" in result
    assert "unselectable" in result
    assert "Cube, Sphere" in result


def test_collection_list_objects_guides_when_collection_missing(monkeypatch):
    from server.adapters.mcp.areas.collection import collection_list_objects

    handler = MagicMock()
    handler.list_objects.side_effect = RuntimeError("Collection 'Missing' not found")

    monkeypatch.setattr("server.adapters.mcp.areas.collection.get_collection_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.collection.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.collection.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = collection_list_objects(MagicMock(), collection_name="Missing")

    assert "Use collection_list to see available collections" in result


def test_collection_manage_returns_handler_result(monkeypatch):
    from server.adapters.mcp.areas.collection import collection_manage

    handler = MagicMock()
    handler.manage_collection.return_value = "Moved object"

    monkeypatch.setattr("server.adapters.mcp.areas.collection.get_collection_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.collection.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.collection.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = collection_manage(
        MagicMock(),
        action="move_object",
        collection_name="Props",
        object_name="Cube",
    )

    handler.manage_collection.assert_called_once_with(
        action="move_object",
        collection_name="Props",
        new_name=None,
        parent_name=None,
        object_name="Cube",
    )
    assert result == "Moved object"
