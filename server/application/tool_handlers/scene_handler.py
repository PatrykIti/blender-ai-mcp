from typing import List, Dict, Any, Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.scene import ISceneTool

class SceneToolHandler(ISceneTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_objects(self) -> List[Dict[str, Any]]:
        response = self.rpc.send_request("scene.list_objects")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def delete_object(self, name: str) -> str:
        response = self.rpc.send_request("scene.delete_object", {"name": name})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Successfully deleted object: {name}"

    def clean_scene(self, keep_lights_and_cameras: bool) -> str:
        response = self.rpc.send_request("scene.clean_scene", {"keep_lights_and_cameras": keep_lights_and_cameras})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Scene cleaned. (Kept lights/cameras: {keep_lights_and_cameras})"

    def duplicate_object(self, name: str, translation: Optional[List[float]] = None) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.duplicate_object", {"name": name, "translation": translation})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def set_active_object(self, name: str) -> str:
        response = self.rpc.send_request("scene.set_active_object", {"name": name})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Successfully set active object to: {name}"

    def get_viewport(self, width: int = 1024, height: int = 768, shading: str = "SOLID", camera_name: Optional[str] = None, focus_target: Optional[str] = None) -> str:
        # Note: Large base64 strings might be heavy.
        args = {
            "width": width,
            "height": height,
            "shading": shading,
            "camera_name": camera_name,
            "focus_target": focus_target
        }
        response = self.rpc.send_request("scene.get_viewport", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def create_light(self, type: str, energy: float, color: List[float], location: List[float], name: Optional[str] = None) -> str:
        args = {
            "type": type,
            "energy": energy,
            "color": color,
            "location": location,
            "name": name
        }
        response = self.rpc.send_request("scene.create_light", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def create_camera(self, location: List[float], rotation: List[float], lens: float = 50.0, clip_start: Optional[float] = None, clip_end: Optional[float] = None, name: Optional[str] = None) -> str:
        args = {
            "location": location,
            "rotation": rotation,
            "lens": lens,
            "clip_start": clip_start,
            "clip_end": clip_end,
            "name": name
        }
        response = self.rpc.send_request("scene.create_camera", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def create_empty(self, type: str, size: float, location: List[float], name: Optional[str] = None) -> str:
        args = {
            "type": type,
            "size": size,
            "location": location,
            "name": name
        }
        response = self.rpc.send_request("scene.create_empty", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def set_mode(self, mode: str) -> str:
        response = self.rpc.send_request("scene.set_mode", {"mode": mode})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def get_mode(self) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.get_mode")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for scene_get_mode")
        return response.result

    def list_selection(self) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.list_selection")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for scene_list_selection")
        return response.result

    def inspect_object(self, name: str) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.inspect_object", {"name": name})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for scene_inspect_object")
        return response.result

    def snapshot_state(self, include_mesh_stats: bool = False, include_materials: bool = False) -> Dict[str, Any]:
        args = {
            "include_mesh_stats": include_mesh_stats,
            "include_materials": include_materials
        }
        response = self.rpc.send_request("scene.snapshot_state", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for scene_snapshot_state")
        return response.result

    def inspect_material_slots(self, material_filter: Optional[str] = None, include_empty_slots: bool = True) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.inspect_material_slots", {
            "material_filter": material_filter,
            "include_empty_slots": include_empty_slots
        })
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def inspect_mesh_topology(self, object_name: str, detailed: bool = False) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.inspect_mesh_topology", {
            "object_name": object_name,
            "detailed": detailed
        })
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def inspect_modifiers(self, object_name: Optional[str] = None, include_disabled: bool = True) -> Dict[str, Any]:
        response = self.rpc.send_request("scene.inspect_modifiers", {
            "object_name": object_name,
            "include_disabled": include_disabled
        })
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
