"""
Application Layer: Baking Tool Handler

Implements IBakingTool interface using RPC calls to Blender addon.
"""

from typing import Optional
from server.domain.tools.baking import IBakingTool
from server.domain.interfaces.rpc import IRpcClient


class BakingToolHandler(IBakingTool):
    """Handler for texture baking operations via RPC."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def bake_normal_map(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        high_poly_source: Optional[str] = None,
        cage_extrusion: float = 0.1,
        margin: int = 16,
        normal_space: str = "TANGENT"
    ) -> str:
        """Bakes normal map from high-poly to low-poly or from geometry."""
        return self.rpc.send_request("baking.normal_map", {
            "object_name": object_name,
            "output_path": output_path,
            "resolution": resolution,
            "high_poly_source": high_poly_source,
            "cage_extrusion": cage_extrusion,
            "margin": margin,
            "normal_space": normal_space
        })

    def bake_ao(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        samples: int = 128,
        distance: float = 1.0,
        margin: int = 16
    ) -> str:
        """Bakes ambient occlusion map."""
        return self.rpc.send_request("baking.ao", {
            "object_name": object_name,
            "output_path": output_path,
            "resolution": resolution,
            "samples": samples,
            "distance": distance,
            "margin": margin
        })

    def bake_combined(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        samples: int = 128,
        margin: int = 16,
        use_pass_direct: bool = True,
        use_pass_indirect: bool = True,
        use_pass_color: bool = True
    ) -> str:
        """Bakes combined render (full material + lighting) to texture."""
        return self.rpc.send_request("baking.combined", {
            "object_name": object_name,
            "output_path": output_path,
            "resolution": resolution,
            "samples": samples,
            "margin": margin,
            "use_pass_direct": use_pass_direct,
            "use_pass_indirect": use_pass_indirect,
            "use_pass_color": use_pass_color
        })

    def bake_diffuse(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        margin: int = 16
    ) -> str:
        """Bakes diffuse/albedo color only."""
        return self.rpc.send_request("baking.diffuse", {
            "object_name": object_name,
            "output_path": output_path,
            "resolution": resolution,
            "margin": margin
        })
