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

    def bevel(self, offset: float, segments: int = 1, profile: float = 0.5, affect: str = 'EDGES') -> str:
        args = {"offset": offset, "segments": segments, "profile": profile, "affect": affect}
        response = self.rpc.send_request("mesh.bevel", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def loop_cut(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        response = self.rpc.send_request("mesh.loop_cut", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def inset(self, thickness: float, depth: float = 0.0) -> str:
        args = {"thickness": thickness, "depth": depth}
        response = self.rpc.send_request("mesh.inset", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def boolean(self, operation: str, solver: str = 'FAST') -> str:
        args = {"operation": operation, "solver": solver}
        response = self.rpc.send_request("mesh.boolean", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def merge_by_distance(self, distance: float = 0.001) -> str:
        args = {"distance": distance}
        response = self.rpc.send_request("mesh.merge_by_distance", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def subdivide(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        response = self.rpc.send_request("mesh.subdivide", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def smooth_vertices(self, iterations: int = 1, factor: float = 0.5) -> str:
        args = {"iterations": iterations, "factor": factor}
        response = self.rpc.send_request("mesh.smooth_vertices", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def flatten_vertices(self, axis: str) -> str:
        args = {"axis": axis}
        response = self.rpc.send_request("mesh.flatten_vertices", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def list_groups(self, object_name: str, group_type: str = 'VERTEX') -> dict:
        args = {"object_name": object_name, "group_type": group_type}
        response = self.rpc.send_request("mesh.list_groups", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_loop(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        response = self.rpc.send_request("mesh.select_loop", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_ring(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        response = self.rpc.send_request("mesh.select_ring", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_linked(self) -> str:
        response = self.rpc.send_request("mesh.select_linked")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
