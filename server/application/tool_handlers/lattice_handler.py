from typing import List, Optional, Union
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.lattice import ILatticeTool


class LatticeToolHandler(ILatticeTool):
    """Handler for lattice deformation tools. Sends RPC requests to Blender addon."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def lattice_create(
        self,
        name: str = "Lattice",
        target_object: Optional[str] = None,
        location: Optional[List[float]] = None,
        points_u: int = 2,
        points_v: int = 2,
        points_w: int = 2,
        interpolation: str = "KEY_LINEAR",
    ) -> str:
        """Creates a lattice object for non-destructive deformation."""
        args = {
            "name": name,
            "target_object": target_object,
            "location": location or [0, 0, 0],
            "points_u": points_u,
            "points_v": points_v,
            "points_w": points_w,
            "interpolation": interpolation,
        }
        response = self.rpc.send_request("lattice.create", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def lattice_bind(
        self,
        object_name: str,
        lattice_name: str,
        vertex_group: Optional[str] = None,
    ) -> str:
        """Binds an object to a lattice using Lattice modifier."""
        args = {
            "object_name": object_name,
            "lattice_name": lattice_name,
            "vertex_group": vertex_group,
        }
        response = self.rpc.send_request("lattice.bind", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def lattice_edit_point(
        self,
        lattice_name: str,
        point_index: Union[int, List[int]],
        offset: List[float],
        relative: bool = True,
    ) -> str:
        """Moves lattice control points programmatically."""
        args = {
            "lattice_name": lattice_name,
            "point_index": point_index,
            "offset": offset,
            "relative": relative,
        }
        response = self.rpc.send_request("lattice.edit_point", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
