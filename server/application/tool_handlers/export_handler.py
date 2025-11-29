from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.export import IExportTool


class ExportToolHandler(IExportTool):
    """Handler for export operations via RPC to Blender addon."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

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
