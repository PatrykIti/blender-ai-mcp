from typing import Any, Dict, Optional

from server.application.tool_handlers._rpc_utils import require_dict_result, require_str_result
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.uv import IUVTool


class UVToolHandler(IUVTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_maps(self, object_name: str, include_island_counts: bool = False) -> Dict[str, Any]:
        args = {"object_name": object_name, "include_island_counts": include_island_counts}
        return require_dict_result(self.rpc.send_request("uv.list_maps", args))

    def unwrap(
        self,
        object_name: Optional[str] = None,
        method: str = "SMART_PROJECT",
        angle_limit: float = 66.0,
        island_margin: float = 0.02,
        scale_to_bounds: bool = True,
    ) -> str:
        """Unwraps selected faces to UV space using specified projection method."""
        args = {
            "object_name": object_name,
            "method": method,
            "angle_limit": angle_limit,
            "island_margin": island_margin,
            "scale_to_bounds": scale_to_bounds,
        }
        return require_str_result(self.rpc.send_request("uv.unwrap", args))

    def pack_islands(
        self,
        object_name: Optional[str] = None,
        margin: float = 0.02,
        rotate: bool = True,
        scale: bool = True,
    ) -> str:
        """Packs UV islands for optimal texture space usage."""
        args = {
            "object_name": object_name,
            "margin": margin,
            "rotate": rotate,
            "scale": scale,
        }
        return require_str_result(self.rpc.send_request("uv.pack_islands", args))

    def create_seam(
        self,
        object_name: Optional[str] = None,
        action: str = "mark",
    ) -> str:
        """Marks or clears UV seams on selected edges."""
        args = {
            "object_name": object_name,
            "action": action,
        }
        return require_str_result(self.rpc.send_request("uv.create_seam", args))
