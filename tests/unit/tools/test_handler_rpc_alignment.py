from __future__ import annotations

from typing import Any

import pytest
from server.application.tool_handlers.collection_handler import CollectionToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse


class DummyRpc(IRpcClient):
    def __init__(self, responses: dict[str, RpcResponse]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    def send_request(
        self,
        cmd: str,
        args: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> RpcResponse:
        self.calls.append((cmd, args))
        return self._responses[cmd]


def _ok(result: object) -> RpcResponse:
    return RpcResponse(request_id="req-1", status="ok", result=result)


def test_scene_list_objects_requires_list_of_dicts_payload():
    handler = SceneToolHandler(DummyRpc({"scene.list_objects": _ok([{"name": "Cube", "type": "MESH"}])}))

    result = handler.list_objects()

    assert result == [{"name": "Cube", "type": "MESH"}]


def test_collection_list_collections_rejects_non_dict_items():
    handler = CollectionToolHandler(DummyRpc({"collection.list": _ok(["Environment"])}))

    with pytest.raises(RuntimeError, match="Expected a list of objects in RPC result"):
        handler.list_collections()


def test_material_list_materials_aligns_with_list_of_dict_payload_and_args():
    rpc = DummyRpc(
        {
            "material.list": _ok(
                [
                    {"name": "Steel", "users": 2},
                    {"name": "Glass", "users": 1},
                ]
            )
        }
    )
    handler = MaterialToolHandler(rpc)

    result = handler.list_materials(include_unassigned=False)

    assert result[0]["name"] == "Steel"
    assert rpc.calls == [("material.list", {"include_unassigned": False})]


def test_uv_list_maps_aligns_with_object_payload_and_args():
    rpc = DummyRpc(
        {
            "uv.list_maps": _ok(
                {
                    "object_name": "Wall",
                    "uv_map_count": 1,
                    "uv_maps": [{"name": "UVMap", "is_active": True}],
                }
            )
        }
    )
    handler = UVToolHandler(rpc)

    result = handler.list_maps(object_name="Wall", include_island_counts=True)

    assert result["uv_map_count"] == 1
    assert rpc.calls == [("uv.list_maps", {"object_name": "Wall", "include_island_counts": True})]
