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
