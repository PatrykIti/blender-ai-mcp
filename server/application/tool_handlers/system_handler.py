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

    # === Export Tools ===

    def export_glb(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        export_materials: bool = True,
        apply_modifiers: bool = True,
    ) -> str:
        """Exports scene or selected objects to GLB/GLTF format."""
        response = self.rpc.send_request(
            "export.glb",
            {
                "filepath": filepath,
                "export_selected": export_selected,
                "export_animations": export_animations,
                "export_materials": export_materials,
                "apply_modifiers": apply_modifiers,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def export_fbx(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        apply_modifiers: bool = True,
        mesh_smooth_type: str = "FACE",
    ) -> str:
        """Exports scene or selected objects to FBX format."""
        response = self.rpc.send_request(
            "export.fbx",
            {
                "filepath": filepath,
                "export_selected": export_selected,
                "export_animations": export_animations,
                "apply_modifiers": apply_modifiers,
                "mesh_smooth_type": mesh_smooth_type,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def export_obj(
        self,
        filepath: str,
        export_selected: bool = False,
        apply_modifiers: bool = True,
        export_materials: bool = True,
        export_uvs: bool = True,
        export_normals: bool = True,
        triangulate: bool = False,
    ) -> str:
        """Exports scene or selected objects to OBJ format."""
        response = self.rpc.send_request(
            "export.obj",
            {
                "filepath": filepath,
                "export_selected": export_selected,
                "apply_modifiers": apply_modifiers,
                "export_materials": export_materials,
                "export_uvs": export_uvs,
                "export_normals": export_normals,
                "triangulate": triangulate,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # === Import Tools ===

    def import_obj(
        self,
        filepath: str,
        use_split_objects: bool = True,
        use_split_groups: bool = False,
        global_scale: float = 1.0,
        forward_axis: str = "NEGATIVE_Z",
        up_axis: str = "Y",
    ) -> str:
        """Imports OBJ file."""
        response = self.rpc.send_request(
            "import.obj",
            {
                "filepath": filepath,
                "use_split_objects": use_split_objects,
                "use_split_groups": use_split_groups,
                "global_scale": global_scale,
                "forward_axis": forward_axis,
                "up_axis": up_axis,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def import_fbx(
        self,
        filepath: str,
        use_custom_normals: bool = True,
        use_image_search: bool = True,
        ignore_leaf_bones: bool = False,
        automatic_bone_orientation: bool = False,
        global_scale: float = 1.0,
    ) -> str:
        """Imports FBX file."""
        response = self.rpc.send_request(
            "import.fbx",
            {
                "filepath": filepath,
                "use_custom_normals": use_custom_normals,
                "use_image_search": use_image_search,
                "ignore_leaf_bones": ignore_leaf_bones,
                "automatic_bone_orientation": automatic_bone_orientation,
                "global_scale": global_scale,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def import_glb(
        self,
        filepath: str,
        import_pack_images: bool = True,
        merge_vertices: bool = False,
        import_shading: str = "NORMALS",
    ) -> str:
        """Imports GLB/GLTF file."""
        response = self.rpc.send_request(
            "import.glb",
            {
                "filepath": filepath,
                "import_pack_images": import_pack_images,
                "merge_vertices": merge_vertices,
                "import_shading": import_shading,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def import_image_as_plane(
        self,
        filepath: str,
        name: Optional[str] = None,
        location: Optional[list] = None,
        size: float = 1.0,
        align_axis: str = "Z+",
        shader: str = "PRINCIPLED",
        use_transparency: bool = True,
    ) -> str:
        """Imports image as a textured plane."""
        response = self.rpc.send_request(
            "import.image_as_plane",
            {
                "filepath": filepath,
                "name": name,
                "location": location,
                "size": size,
                "align_axis": align_axis,
                "shader": shader,
                "use_transparency": use_transparency,
            },
        )
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
