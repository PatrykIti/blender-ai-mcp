from typing import List, Dict, Any, Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.modeling import IModelingTool

class ModelingToolHandler(IModelingTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def create_primitive(
        self, 
        primitive_type: str, 
        radius: float = 1.0, 
        size: float = 2.0, 
        location: List[float] = (0.0, 0.0, 0.0), 
        rotation: List[float] = (0.0, 0.0, 0.0),
        name: Optional[str] = None
    ) -> str:
        args = {
            "primitive_type": primitive_type,
            "radius": radius,
            "size": size,
            "location": location,
            "rotation": rotation,
            "name": name
        }
        response = self.rpc.send_request("modeling.create_primitive", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Created {primitive_type} named '{response.result['name']}'"

    def transform_object(
        self, 
        name: str, 
        location: Optional[List[float]] = None, 
        rotation: Optional[List[float]] = None, 
        scale: Optional[List[float]] = None
    ) -> str:
        args = {"name": name}
        if location: args["location"] = location
        if rotation: args["rotation"] = rotation
        if scale: args["scale"] = scale
        
        response = self.rpc.send_request("modeling.transform_object", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Transformed object '{name}'"

    def add_modifier(
        self, 
        name: str, 
        modifier_type: str, 
        properties: Dict[str, Any] = None
    ) -> str:
        args = {"name": name, "modifier_type": modifier_type, "properties": properties or {}}
        response = self.rpc.send_request("modeling.add_modifier", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Added modifier '{modifier_type}' to '{name}'"

    def apply_modifier(self, name: str, modifier_name: str) -> str:
        args = {"name": name, "modifier_name": modifier_name}
        response = self.rpc.send_request("modeling.apply_modifier", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Applied modifier '{modifier_name}' to '{name}'"

    def convert_to_mesh(self, name: str) -> str:
        args = {"name": name}
        response = self.rpc.send_request("modeling.convert_to_mesh", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Object '{name}' converted to mesh (or was already mesh). Status: {response.result['status']}"

    def join_objects(self, object_names: List[str]) -> str:
        args = {"object_names": object_names}
        response = self.rpc.send_request("modeling.join_objects", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Objects {', '.join(object_names)} joined into '{response.result['name']}'. Joined count: {response.result['joined_count']}"

    def separate_object(self, name: str, type: str = "LOOSE") -> List[str]:
        args = {"name": name, "type": type}
        response = self.rpc.send_request("modeling.separate_object", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result["separated_objects"]

    def set_origin(self, name: str, type: str) -> str:
        args = {"name": name, "type": type}
        response = self.rpc.send_request("modeling.set_origin", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Origin for object '{name}' set to type '{type}' (Status: {response.result['status']})";

    def get_modifiers(self, name: str) -> List[Dict[str, Any]]:
        args = {"name": name}
        response = self.rpc.send_request("modeling.get_modifiers", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # ==========================================================================
    # TASK-038-1: Metaball Tools
    # ==========================================================================

    def metaball_create(
        self,
        name: str = "Metaball",
        location: Optional[List[float]] = None,
        element_type: str = "BALL",
        radius: float = 1.0,
        resolution: float = 0.2,
        threshold: float = 0.6,
    ) -> str:
        """Creates a metaball object."""
        args = {
            "name": name,
            "location": location or [0, 0, 0],
            "element_type": element_type,
            "radius": radius,
            "resolution": resolution,
            "threshold": threshold,
        }
        response = self.rpc.send_request("modeling.metaball_create", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def metaball_add_element(
        self,
        metaball_name: str,
        element_type: str = "BALL",
        location: Optional[List[float]] = None,
        radius: float = 1.0,
        stiffness: float = 2.0,
    ) -> str:
        """Adds element to existing metaball."""
        args = {
            "metaball_name": metaball_name,
            "element_type": element_type,
            "location": location or [0, 0, 0],
            "radius": radius,
            "stiffness": stiffness,
        }
        response = self.rpc.send_request("modeling.metaball_add_element", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def metaball_to_mesh(
        self,
        metaball_name: str,
        apply_resolution: bool = True,
    ) -> str:
        """Converts metaball to mesh."""
        args = {
            "metaball_name": metaball_name,
            "apply_resolution": apply_resolution,
        }
        response = self.rpc.send_request("modeling.metaball_to_mesh", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # ==========================================================================
    # TASK-038-6: Skin Modifier Workflow
    # ==========================================================================

    def skin_create_skeleton(
        self,
        name: str = "Skeleton",
        vertices: List[List[float]] = None,
        edges: Optional[List[List[int]]] = None,
        location: Optional[List[float]] = None,
    ) -> str:
        """Creates skeleton mesh for Skin modifier."""
        args = {
            "name": name,
            "vertices": vertices or [[0, 0, 0], [0, 0, 1]],
            "edges": edges,
            "location": location or [0, 0, 0],
        }
        response = self.rpc.send_request("modeling.skin_create_skeleton", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def skin_set_radius(
        self,
        object_name: str,
        vertex_index: Optional[int] = None,
        radius_x: float = 0.25,
        radius_y: float = 0.25,
    ) -> str:
        """Sets skin radius at vertices."""
        args = {
            "object_name": object_name,
            "vertex_index": vertex_index,
            "radius_x": radius_x,
            "radius_y": radius_y,
        }
        response = self.rpc.send_request("modeling.skin_set_radius", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
