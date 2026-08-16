from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import (
    require_dict_result,
    require_list_of_dicts_result,
    require_str_result,
)
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.material import IMaterialTool


class MaterialToolHandler(IMaterialTool):
    """Application service for Material Tools.

    Bridges MCP layer with Blender addon via RPC.
    """

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_materials(self, include_unassigned: bool = True) -> List[Dict[str, Any]]:
        return require_list_of_dicts_result(
            self.rpc.send_request("material.list", {"include_unassigned": include_unassigned})
        )

    def list_by_object(self, object_name: str, include_indices: bool = False) -> Dict[str, Any]:
        args = {"object_name": object_name, "include_indices": include_indices}
        return require_dict_result(self.rpc.send_request("material.list_by_object", args))

    # TASK-023-1: material_create
    def create_material(
        self,
        name: str,
        base_color: Optional[List[float]] = None,
        metallic: float = 0.0,
        roughness: float = 0.5,
        emission_color: Optional[List[float]] = None,
        emission_strength: float = 0.0,
        alpha: float = 1.0,
    ) -> str:
        args = {
            "name": name,
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength,
            "alpha": alpha,
        }
        return require_str_result(self.rpc.send_request("material.create", args))

    # TASK-023-2: material_assign
    def assign_material(
        self,
        material_name: str,
        object_name: Optional[str] = None,
        slot_index: Optional[int] = None,
        assign_to_selection: bool = False,
    ) -> str:
        args = {
            "material_name": material_name,
            "object_name": object_name,
            "slot_index": slot_index,
            "assign_to_selection": assign_to_selection,
        }
        return require_str_result(self.rpc.send_request("material.assign", args))

    # TASK-023-3: material_set_params
    def set_material_params(
        self,
        material_name: str,
        base_color: Optional[List[float]] = None,
        metallic: Optional[float] = None,
        roughness: Optional[float] = None,
        emission_color: Optional[List[float]] = None,
        emission_strength: Optional[float] = None,
        alpha: Optional[float] = None,
    ) -> str:
        args = {
            "material_name": material_name,
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength,
            "alpha": alpha,
        }
        return require_str_result(self.rpc.send_request("material.set_params", args))

    # TASK-023-4: material_set_texture
    def set_material_texture(
        self,
        material_name: str,
        texture_path: str,
        input_name: str = "Base Color",
        color_space: str = "sRGB",
    ) -> str:
        args = {
            "material_name": material_name,
            "texture_path": texture_path,
            "input_name": input_name,
            "color_space": color_space,
        }
        return require_str_result(self.rpc.send_request("material.set_texture", args))

    # TASK-045-6: material_inspect_nodes
    def inspect_nodes(
        self,
        material_name: str,
        include_connections: bool = True,
    ) -> Dict[str, Any]:
        args = {
            "material_name": material_name,
            "include_connections": include_connections,
        }
        return require_dict_result(self.rpc.send_request("material.inspect_nodes", args))
