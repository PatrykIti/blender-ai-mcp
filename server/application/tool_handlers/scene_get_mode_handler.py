"""Application handler for the `scene_get_mode` tool."""
from __future__ import annotations

from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse
from server.domain.tools.scene_get_mode import ISceneGetModeTool, SceneModeResponse


class SceneGetModeHandler(ISceneGetModeTool):
    """Retrieves Blender context mode information via RPC."""

    def __init__(self, rpc_client: IRpcClient) -> None:
        self._rpc_client = rpc_client

    def get_mode(self) -> SceneModeResponse:
        """Return the current Blender interaction mode."""
        response: RpcResponse = self._rpc_client.send_request("scene.get_mode")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        if not isinstance(response.result, dict):
            raise RuntimeError("Blender Error: Invalid payload for scene_get_mode")
        return SceneModeResponse(**response.result)
