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
        rotation: List[float] = (0.0, 0.0, 0.0)
    ) -> str:
        args = {
            "primitive_type": primitive_type,
            "radius": radius,
            "size": size,
            "location": location,
            "rotation": rotation
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
