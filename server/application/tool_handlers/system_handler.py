from typing import Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.system import ISystemTool


class SystemToolHandler(ISystemTool):
    """Application handler for system-level operations.

    Implements ISystemTool by delegating to the Blender addon via RPC.
    """

    def __init__(self, rpc_client: IRpcClient):
        """Initialize the handler with an RPC client.

        Args:
            rpc_client: Client for communicating with Blender addon
        """
        self.rpc = rpc_client

    def set_mode(
        self,
        mode: str,
        object_name: Optional[str] = None,
    ) -> str:
        """Switches Blender mode for the active or specified object."""
        response = self.rpc.send_request(
            "system.set_mode",
            {"mode": mode, "object_name": object_name},
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def undo(self, steps: int = 1) -> str:
        """Undoes the last operation(s)."""
        response = self.rpc.send_request("system.undo", {"steps": steps})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def redo(self, steps: int = 1) -> str:
        """Redoes previously undone operation(s)."""
        response = self.rpc.send_request("system.redo", {"steps": steps})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def save_file(
        self,
        filepath: Optional[str] = None,
        compress: bool = True,
    ) -> str:
        """Saves the current Blender file."""
        response = self.rpc.send_request(
            "system.save_file",
            {"filepath": filepath, "compress": compress},
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def new_file(self, load_ui: bool = False) -> str:
        """Creates a new Blender file (clears current scene)."""
        response = self.rpc.send_request("system.new_file", {"load_ui": load_ui})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def snapshot(
        self,
        action: str,
        name: Optional[str] = None,
    ) -> str:
        """Manages quick save/restore checkpoints."""
        response = self.rpc.send_request(
            "system.snapshot",
            {"action": action, "name": name},
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
