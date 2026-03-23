import unittest
from typing import Any, Dict

from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse


class DummyRpc(IRpcClient):
    def __init__(self, responses: Dict[str, RpcResponse]):
        self._responses = responses
        self.calls: list[tuple[str, Dict[str, Any] | None]] = []

    def send_request(
        self,
        cmd: str,
        args: Dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> RpcResponse:
        self.calls.append((cmd, args))
        return self._responses[cmd]


class TestModelingHandlerRpcContracts(unittest.TestCase):
    def test_transform_object_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "modeling.transform_object": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={"name": "House_Walls", "location": [0, 0, 0]},
                )
            }
        )
        handler = ModelingToolHandler(rpc)

        result = handler.transform_object("House_Walls", scale=[3, 2, 1.5])

        self.assertEqual(result, "Transformed object 'House_Walls'")
        self.assertEqual(
            rpc.calls[0],
            ("modeling.transform_object", {"name": "House_Walls", "scale": [3, 2, 1.5]}),
        )


if __name__ == "__main__":
    unittest.main()
