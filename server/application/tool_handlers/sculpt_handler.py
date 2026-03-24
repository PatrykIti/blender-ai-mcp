from typing import List, Optional

from server.application.tool_handlers._rpc_utils import require_dict_result, require_str_result
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
        return require_str_result(self.rpc.send_request("sculpt.auto", args))

    def deform_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        delta: Optional[List[float]] = None,
        strength: float = 1.0,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> str:
        """Deterministically deforms a local region of mesh vertices."""
        args = {
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "delta": delta,
            "strength": strength,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        result = require_dict_result(self.rpc.send_request("sculpt.deform_region", args))
        return (
            f"Deformed region on '{result['object_name']}' "
            f"(affected_vertices={result['affected_vertices']}, radius={result['radius']}, "
            f"falloff={result['falloff']}, strength={result['strength']})"
        )

    def crease_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        depth: float = 0.1,
        pinch: float = 0.5,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> str:
        """Deterministically create a local crease/groove region."""
        args = {
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "depth": depth,
            "pinch": pinch,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        result = require_dict_result(self.rpc.send_request("sculpt.crease_region", args))
        return (
            f"Creased region on '{result['object_name']}' "
            f"(affected_vertices={result['affected_vertices']}, depth={result['depth']}, "
            f"pinch={result['pinch']}, radius={result['radius']}, falloff={result['falloff']})"
        )

    def smooth_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        strength: float = 0.5,
        iterations: int = 1,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> str:
        """Deterministically smooth a local region of mesh vertices."""
        args = {
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "strength": strength,
            "iterations": iterations,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        result = require_dict_result(self.rpc.send_request("sculpt.smooth_region", args))
        return (
            f"Smoothed region on '{result['object_name']}' "
            f"(affected_vertices={result['affected_vertices']}, iterations={result['iterations']}, "
            f"radius={result['radius']}, falloff={result['falloff']})"
        )

    def inflate_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        amount: float = 0.2,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> str:
        """Deterministically inflate or deflate a local region."""
        args = {
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "amount": amount,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        result = require_dict_result(self.rpc.send_request("sculpt.inflate_region", args))
        return (
            f"Inflated region on '{result['object_name']}' "
            f"(affected_vertices={result['affected_vertices']}, amount={result['amount']}, "
            f"radius={result['radius']}, falloff={result['falloff']})"
        )

    def pinch_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        amount: float = 0.2,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> str:
        """Deterministically pinch a local region toward the influence center."""
        args = {
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "amount": amount,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        }
        result = require_dict_result(self.rpc.send_request("sculpt.pinch_region", args))
        return (
            f"Pinched region on '{result['object_name']}' "
            f"(affected_vertices={result['affected_vertices']}, amount={result['amount']}, "
            f"radius={result['radius']}, falloff={result['falloff']})"
        )

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
        return require_str_result(self.rpc.send_request("sculpt.brush_smooth", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_grab", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_crease", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_clay", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_inflate", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_blob", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_snake_hook", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_draw", args))

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
        return require_str_result(self.rpc.send_request("sculpt.brush_pinch", args))

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
        return require_str_result(self.rpc.send_request("sculpt.enable_dyntopo", args))

    def disable_dyntopo(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """Disables Dynamic Topology."""
        args = {
            "object_name": object_name,
        }
        return require_str_result(self.rpc.send_request("sculpt.disable_dyntopo", args))

    def dyntopo_flood_fill(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """Applies current detail level to entire mesh."""
        args = {
            "object_name": object_name,
        }
        return require_str_result(self.rpc.send_request("sculpt.dyntopo_flood_fill", args))
