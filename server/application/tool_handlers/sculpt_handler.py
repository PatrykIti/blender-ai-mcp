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

    # ==========================================================================
    # TASK-038-2: Core Sculpt Brushes
    # ==========================================================================

    def brush_clay(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Clay brush for adding material."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_clay", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_inflate(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Inflate brush for pushing geometry outward."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_inflate", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_blob(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Blob brush for creating rounded organic bulges."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_blob", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # ==========================================================================
    # TASK-038-3: Detail Sculpt Brushes
    # ==========================================================================

    def brush_snake_hook(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Snake Hook brush for pulling geometry like taffy."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_snake_hook", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_draw(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Draw brush for basic sculpting."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_draw", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def brush_pinch(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """Sets up Pinch brush for pulling geometry toward center."""
        args = {
            "object_name": object_name,
            "radius": radius,
            "strength": strength,
        }
        response = self.rpc.send_request("sculpt.brush_pinch", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # ==========================================================================
    # TASK-038-4: Dynamic Topology (Dyntopo)
    # ==========================================================================

    def enable_dyntopo(
        self,
        object_name: Optional[str] = None,
        detail_mode: str = "RELATIVE",
        detail_size: float = 12.0,
        use_smooth_shading: bool = True,
    ) -> str:
        """Enables Dynamic Topology for automatic geometry addition."""
        args = {
            "object_name": object_name,
            "detail_mode": detail_mode,
            "detail_size": detail_size,
            "use_smooth_shading": use_smooth_shading,
        }
        response = self.rpc.send_request("sculpt.enable_dyntopo", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def disable_dyntopo(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """Disables Dynamic Topology."""
        args = {
            "object_name": object_name,
        }
        response = self.rpc.send_request("sculpt.disable_dyntopo", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def dyntopo_flood_fill(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """Applies current detail level to entire mesh."""
        args = {
            "object_name": object_name,
        }
        response = self.rpc.send_request("sculpt.dyntopo_flood_fill", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
