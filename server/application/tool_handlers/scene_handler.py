from typing import List, Dict, Any
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
