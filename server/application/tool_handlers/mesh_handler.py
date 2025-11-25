from typing import List
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.mesh import IMeshTool

class MeshToolHandler(IMeshTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def select_all(self, deselect: bool = False) -> str:
        response = self.rpc.send_request("mesh.select_all", {"deselect": deselect})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def delete_selected(self, type: str = 'VERT') -> str:
        response = self.rpc.send_request("mesh.delete_selected", {"type": type})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_by_index(self, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
        response = self.rpc.send_request("mesh.select_by_index", {"indices": indices, "type": type, "selection_mode": selection_mode})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def extrude_region(self, move: List[float] = None) -> str:
        args = {"move": move} if move else {}
        response = self.rpc.send_request("mesh.extrude_region", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def fill_holes(self) -> str:
        response = self.rpc.send_request("mesh.fill_holes")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
