from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.import_tool import IImportTool


class ImportToolHandler(IImportTool):
    """Handler for import operations via RPC to Blender addon."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

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
        name: str | None = None,
        location: list[float] | None = None,
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
