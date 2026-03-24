import unittest
from typing import Any, Dict

from server.application.tool_handlers.sculpt_handler import SculptToolHandler
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


class TestSculptHandlerRpcContracts(unittest.TestCase):
    def test_deform_region_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "sculpt.deform_region": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "object_name": "Head",
                        "affected_vertices": 42,
                        "radius": 0.35,
                        "strength": 1.0,
                        "falloff": "SMOOTH",
                    },
                )
            }
        )
        handler = SculptToolHandler(rpc)

        result = handler.deform_region(
            object_name="Head",
            center=[0.0, 0.0, 1.0],
            radius=0.35,
            delta=[0.0, 0.0, 0.2],
            strength=1.0,
            falloff="SMOOTH",
        )

        self.assertIn("Deformed region on 'Head'", result)
        self.assertIn("affected_vertices=42", result)
        self.assertEqual(
            rpc.calls[0],
            (
                "sculpt.deform_region",
                {
                    "object_name": "Head",
                    "center": [0.0, 0.0, 1.0],
                    "radius": 0.35,
                    "delta": [0.0, 0.0, 0.2],
                    "strength": 1.0,
                    "falloff": "SMOOTH",
                    "use_symmetry": False,
                    "symmetry_axis": "X",
                },
            ),
        )

    def test_smooth_region_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "sculpt.smooth_region": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "object_name": "Head",
                        "affected_vertices": 18,
                        "iterations": 2,
                        "radius": 0.4,
                        "falloff": "SMOOTH",
                    },
                )
            }
        )
        handler = SculptToolHandler(rpc)

        result = handler.smooth_region(
            object_name="Head",
            center=[0.0, 0.0, 1.0],
            radius=0.4,
            strength=0.6,
            iterations=2,
        )

        self.assertIn("Smoothed region on 'Head'", result)
        self.assertIn("iterations=2", result)

    def test_inflate_region_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "sculpt.inflate_region": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "object_name": "Head",
                        "affected_vertices": 12,
                        "amount": 0.2,
                        "radius": 0.4,
                        "falloff": "LINEAR",
                    },
                )
            }
        )
        handler = SculptToolHandler(rpc)

        result = handler.inflate_region(
            object_name="Head",
            center=[0.0, 0.0, 1.0],
            radius=0.4,
            amount=0.2,
            falloff="LINEAR",
        )

        self.assertIn("Inflated region on 'Head'", result)
        self.assertIn("amount=0.2", result)

    def test_pinch_region_accepts_dict_payload_from_addon(self):
        rpc = DummyRpc(
            {
                "sculpt.pinch_region": RpcResponse(
                    request_id="abc",
                    status="ok",
                    result={
                        "object_name": "Head",
                        "affected_vertices": 12,
                        "amount": 0.15,
                        "radius": 0.4,
                        "falloff": "SHARP",
                    },
                )
            }
        )
        handler = SculptToolHandler(rpc)

        result = handler.pinch_region(
            object_name="Head",
            center=[0.0, 0.0, 1.0],
            radius=0.4,
            amount=0.15,
            falloff="SHARP",
        )

        self.assertIn("Pinched region on 'Head'", result)
        self.assertIn("amount=0.15", result)


if __name__ == "__main__":
    unittest.main()
