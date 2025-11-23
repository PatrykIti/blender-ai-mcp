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

    def get_viewport(self, width: int = 1024, height: int = 768) -> str:
        # Note: Large base64 strings might be heavy.
        response = self.rpc.send_request("scene.get_viewport", {"width": width, "height": height})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
