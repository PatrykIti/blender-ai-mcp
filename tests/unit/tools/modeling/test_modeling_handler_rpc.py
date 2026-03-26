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

    def test_get_modifiers_accepts_list_of_dicts_payload(self):
        rpc = DummyRpc(
            {
                "modeling.get_modifiers": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result=[{"name": "Bevel", "type": "BEVEL"}],
                )
            }
        )
        handler = ModelingToolHandler(rpc)

        result = handler.get_modifiers("House_Walls")

        self.assertEqual(result, [{"name": "Bevel", "type": "BEVEL"}])
        self.assertEqual(rpc.calls[0], ("modeling.get_modifiers", {"name": "House_Walls"}))

    def test_add_modifier_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "modeling.add_modifier": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={"modifier": "Subsurf"},
                )
            }
        )
        handler = ModelingToolHandler(rpc)

        result = handler.add_modifier("House_Walls", "SUBSURF", {"levels": 1})

        self.assertEqual(result, "Added modifier 'SUBSURF' to 'House_Walls'")
        self.assertEqual(
            rpc.calls[0],
            ("modeling.add_modifier", {"name": "House_Walls", "modifier_type": "SUBSURF", "properties": {"levels": 1}}),
        )

    def test_apply_modifier_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "modeling.apply_modifier": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={"applied_modifier": "Bevel", "object": "House_Walls"},
                )
            }
        )
        handler = ModelingToolHandler(rpc)

        result = handler.apply_modifier("House_Walls", "Bevel")

        self.assertEqual(result, "Applied modifier 'Bevel' to 'House_Walls'")
        self.assertEqual(
            rpc.calls[0],
            ("modeling.apply_modifier", {"name": "House_Walls", "modifier_name": "Bevel"}),
        )

    def test_get_modifiers_rejects_non_dict_items(self):
        rpc = DummyRpc(
            {
                "modeling.get_modifiers": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result=["Bevel"],
                )
            }
        )
        handler = ModelingToolHandler(rpc)

        with self.assertRaisesRegex(RuntimeError, "Expected a list of objects in RPC result"):
            handler.get_modifiers("House_Walls")


if __name__ == "__main__":
    unittest.main()
