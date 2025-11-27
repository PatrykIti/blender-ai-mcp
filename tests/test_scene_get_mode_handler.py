import unittest
from typing import Dict, Any

from server.application.tool_handlers.scene_get_mode_handler import SceneGetModeHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse


class DummyRpc(IRpcClient):
    def __init__(self, payload: RpcResponse):
        self._payload = payload
        self.last_cmd: str | None = None
        self.last_args: Dict[str, Any] | None = None

    def send_request(self, cmd: str, args: Dict[str, Any] | None = None) -> RpcResponse:
        self.last_cmd = cmd
        self.last_args = args
        return self._payload


class TestSceneGetModeHandler(unittest.TestCase):
    def test_get_mode_success(self):
        response = RpcResponse(
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
        handler = SceneGetModeHandler(DummyRpc(response))

        result = handler.get_mode()

        self.assertEqual(result.mode, "OBJECT")
        self.assertEqual(result.active_object, "Cube")
        self.assertEqual(result.selection_count, 1)

    def test_get_mode_error(self):
        response = RpcResponse(request_id="abc", status="error", error="oops")
        handler = SceneGetModeHandler(DummyRpc(response))

        with self.assertRaises(RuntimeError):
            handler.get_mode()


if __name__ == "__main__":
    unittest.main()
