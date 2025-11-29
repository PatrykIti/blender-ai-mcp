from abc import ABC, abstractmethod


class IExportTool(ABC):
    """Abstract interface for export operations."""

    @abstractmethod
    def export_glb(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        export_materials: bool = True,
        apply_modifiers: bool = True,
    ) -> str:
        """Exports scene or selected objects to GLB/GLTF format.

        Args:
            filepath: Output file path (must end with .glb or .gltf)
            export_selected: Export only selected objects (default: entire scene)
            export_animations: Include animations
            export_materials: Include materials and textures
            apply_modifiers: Apply modifiers before export

        Returns:
            Success message with file path
        """
        pass

    @abstractmethod
    def export_fbx(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        apply_modifiers: bool = True,
        mesh_smooth_type: str = "FACE",
    ) -> str:
        """Exports scene or selected objects to FBX format.

        Args:
            filepath: Output file path (must end with .fbx)
            export_selected: Export only selected objects
            export_animations: Include animations and armature
            apply_modifiers: Apply modifiers before export
            mesh_smooth_type: Smoothing export method ('OFF', 'FACE', 'EDGE')

        Returns:
            Success message with file path
        """
        pass

    @abstractmethod
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
        """Exports scene or selected objects to OBJ format.

        Args:
            filepath: Output file path (must end with .obj)
            export_selected: Export only selected objects
            apply_modifiers: Apply modifiers before export
            export_materials: Export .mtl material file
            export_uvs: Include UV coordinates
            export_normals: Include vertex normals
            triangulate: Convert quads/ngons to triangles

        Returns:
            Success message with file path
        """
        pass
