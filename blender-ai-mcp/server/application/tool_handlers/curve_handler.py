from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import require_str_result
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.curve import ICurveTool


class CurveToolHandler(ICurveTool):
    """Application service for Curve operations."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    # TASK-021-1: Curve Create Tool
    def create_curve(self, curve_type: str = "BEZIER", location: Optional[List[float]] = None) -> str:
        args: Dict[str, Any] = {"curve_type": curve_type}
        if location:
            args["location"] = location
        return require_str_result(self.rpc.send_request("curve.create_curve", args))

    # TASK-021-2: Curve To Mesh Tool
    def curve_to_mesh(self, object_name: str) -> str:
        args = {"object_name": object_name}
        return require_str_result(self.rpc.send_request("curve.curve_to_mesh", args))

    # TASK-073-1: Curve Get Data Tool
    def get_data(self, object_name: str) -> str:
        args = {"object_name": object_name}
        return require_str_result(self.rpc.send_request("curve.get_data", args))
