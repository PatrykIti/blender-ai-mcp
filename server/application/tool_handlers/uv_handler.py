from typing import Dict, Any
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.uv import IUVTool

class UVToolHandler(IUVTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_maps(self, object_name: str, include_island_counts: bool = False) -> Dict[str, Any]:
        args = {
            "object_name": object_name,
            "include_island_counts": include_island_counts
        }
        response = self.rpc.send_request("uv.list_maps", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for uv_list_maps")
        return response.result
