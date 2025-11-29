import unittest
from typing import Dict, Any

from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse


class DummyRpc(IRpcClient):
    def __init__(self, responses: Dict[str, RpcResponse]):
        self._responses = responses

    def send_request(self, cmd: str, args: Dict[str, Any] | None = None) -> RpcResponse:
        return self._responses[cmd]


class TestSceneGetModeAndSelectionHandlers(unittest.TestCase):
    def test_get_mode_success(self):
        rpc = DummyRpc(
            {
                "scene.get_mode": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "mode": "OBJECT",
                        "active_object": "Cube",
                        "active_object_type": "MESH",
                        "selected_object_names": ["Cube"],
                        "selection_count": 1,
                    },
                )
            }
        )
        handler = SceneToolHandler(rpc)

        result = handler.get_mode()

        self.assertEqual(result["mode"], "OBJECT")
        self.assertEqual(result["active_object"], "Cube")
        self.assertEqual(result["selection_count"], 1)

    def test_list_selection_success(self):
        rpc = DummyRpc(
            {
                "scene.list_selection": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "mode": "EDIT_MESH",
                        "selected_object_names": ["Cube"],
                        "selection_count": 1,
                        "edit_mode_vertex_count": 10,
                        "edit_mode_edge_count": 5,
                        "edit_mode_face_count": 2,
                    },
                )
            }
        )
        handler = SceneToolHandler(rpc)

        summary = handler.list_selection()
        self.assertEqual(summary["mode"], "EDIT_MESH")
        self.assertEqual(summary["edit_mode_vertex_count"], 10)

    def test_inspect_object_success(self):
        rpc = DummyRpc(
            {
                "scene.inspect_object": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={"object_name": "Cube", "type": "MESH"},
                )
            }
        )
        handler = SceneToolHandler(rpc)

        report = handler.inspect_object("Cube")
        self.assertEqual(report["object_name"], "Cube")

    def test_get_mode_error(self):
        rpc = DummyRpc(
            {
                "scene.get_mode": RpcResponse(request_id="abc", status="error", error="oops")
            }
        )
        handler = SceneToolHandler(rpc)

        with self.assertRaises(RuntimeError):
            handler.get_mode()

    def test_inspect_object_error(self):
        rpc = DummyRpc(
            {
                "scene.inspect_object": RpcResponse(request_id="abc", status="error", error="missing")
            }
        )
        handler = SceneToolHandler(rpc)

        with self.assertRaises(RuntimeError):
            handler.inspect_object("Cube")


if __name__ == "__main__":
    unittest.main()
