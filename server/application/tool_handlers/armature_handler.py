"""
Application Handler for Armature Tools.

TASK-037: Armature & Rigging
Bridges MCP adapter to Blender addon via RPC.
"""

from typing import Optional, List

from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.armature import IArmatureTool


class ArmatureToolHandler(IArmatureTool):
    """Handler for armature/rigging operations via RPC."""

    def __init__(self, rpc_client: IRpcClient):
        """Initialize with RPC client.

        Args:
            rpc_client: Client for Blender communication.
        """
        self.rpc = rpc_client

    def create(
        self,
        name: str = "Armature",
        location: Optional[List[float]] = None,
        bone_name: str = "Bone",
        bone_length: float = 1.0
    ) -> str:
        """Creates an armature with an initial bone.

        Args:
            name: Name for the armature object.
            location: World position [x, y, z].
            bone_name: Name for the initial bone.
            bone_length: Length of the initial bone.

        Returns:
            Success message with armature details.
        """
        args = {
            "name": name,
            "location": location,
            "bone_name": bone_name,
            "bone_length": bone_length
        }
        response = self.rpc.send_request("armature.create", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def add_bone(
        self,
        armature_name: str,
        bone_name: str,
        head: List[float],
        tail: List[float],
        parent_bone: Optional[str] = None,
        use_connect: bool = False
    ) -> str:
        """Adds a new bone to an existing armature.

        Args:
            armature_name: Name of the armature object.
            bone_name: Name for the new bone.
            head: Start position [x, y, z].
            tail: End position [x, y, z].
            parent_bone: Optional parent bone name.
            use_connect: Connect to parent (no gap).

        Returns:
            Success message with bone details.
        """
        args = {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "head": head,
            "tail": tail,
            "parent_bone": parent_bone,
            "use_connect": use_connect
        }
        response = self.rpc.send_request("armature.add_bone", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def bind(
        self,
        mesh_name: str,
        armature_name: str,
        bind_type: str = "AUTO"
    ) -> str:
        """Binds a mesh to an armature with automatic weights.

        Args:
            mesh_name: Name of the mesh to bind.
            armature_name: Name of the armature.
            bind_type: Binding type (AUTO, ENVELOPE, EMPTY).

        Returns:
            Success message with binding details.
        """
        args = {
            "mesh_name": mesh_name,
            "armature_name": armature_name,
            "bind_type": bind_type
        }
        response = self.rpc.send_request("armature.bind", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def pose_bone(
        self,
        armature_name: str,
        bone_name: str,
        rotation: Optional[List[float]] = None,
        location: Optional[List[float]] = None,
        scale: Optional[List[float]] = None
    ) -> str:
        """Poses an armature bone.

        Args:
            armature_name: Name of the armature.
            bone_name: Name of the bone to pose.
            rotation: Euler rotation in degrees [x, y, z].
            location: Local position offset [x, y, z].
            scale: Scale factors [x, y, z].

        Returns:
            Success message with pose details.
        """
        args = {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "rotation": rotation,
            "location": location,
            "scale": scale
        }
        response = self.rpc.send_request("armature.pose_bone", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def weight_paint_assign(
        self,
        object_name: str,
        vertex_group: str,
        weight: float = 1.0,
        mode: str = "REPLACE"
    ) -> str:
        """Assigns weights to selected vertices.

        Args:
            object_name: Name of the mesh object.
            vertex_group: Name of the vertex group.
            weight: Weight value (0.0-1.0).
            mode: Assignment mode (REPLACE, ADD, SUBTRACT).

        Returns:
            Success message with weight details.
        """
        args = {
            "object_name": object_name,
            "vertex_group": vertex_group,
            "weight": weight,
            "mode": mode
        }
        response = self.rpc.send_request("armature.weight_paint_assign", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
