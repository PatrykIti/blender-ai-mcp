from typing import List, Optional

from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.sculpt import ISculptTool


class SculptToolHandler(ISculptTool):
    """Application service for Sculpt Mode operations via RPC."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def auto_sculpt(
        self,
        object_name: Optional[str] = None,
        operation: str = "smooth",
        strength: float = 0.5,
        iterations: int = 1,
        use_symmetry: bool = True,
        symmetry_axis: str = "X",
    ) -> str:
        """High-level sculpt operation using mesh filters."""
        args = {
            "object_name": object_name,
            "operation": operation,
            "strength": strength,
            "iterations": iterations,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        response = self.rpc.send_request("sculpt.auto", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_smooth(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Applies smooth brush at specified location."""
        args = {
            "object_name": object_name,
            "location": location,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_smooth", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_grab(
        self,
        object_name: Optional[str] = None,
        from_location: Optional[List[float]] = None,
        to_location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Grabs and moves geometry from one location to another."""
        args = {
            "object_name": object_name,
            "from_location": from_location,
            "to_location": to_location,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_grab", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_crease(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
        pinch: float = 0.5,
    ) -> str:
        """Creates sharp crease at specified location."""
        args = {
            "object_name": object_name,
            "location": location,
            "radius": radius,
            "strength": strength,
            "pinch": pinch,
        }
        response = self.rpc.send_request("sculpt.brush_crease", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
