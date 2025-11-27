from typing import List, Dict, Any
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.material import IMaterialTool


class MaterialToolHandler(IMaterialTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_materials(self, include_unassigned: bool = True) -> List[Dict[str, Any]]:
        response = self.rpc.send_request("material.list", {"include_unassigned": include_unassigned})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def list_by_object(self, object_name: str, include_indices: bool = False) -> Dict[str, Any]:
        args = {
            "object_name": object_name,
            "include_indices": include_indices
        }
        response = self.rpc.send_request("material.list_by_object", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
