from abc import ABC, abstractmethod
from typing import Optional


class ISystemTool(ABC):
    """Abstract interface for system-level operations.

    System tools provide low-level control over Blender's state including
    mode switching, undo/redo, file operations, and checkpoint management.
    """

    @abstractmethod
    def set_mode(
        self,
        mode: str,
        object_name: Optional[str] = None,
    ) -> str:
        """Switches Blender mode for the active or specified object.

        Args:
            mode: Target mode (OBJECT, EDIT, SCULPT, VERTEX_PAINT, WEIGHT_PAINT, TEXTURE_PAINT, POSE)
            object_name: Object to set mode for (default: active object)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def undo(self, steps: int = 1) -> str:
        """Undoes the last operation(s).

        Args:
            steps: Number of steps to undo (default: 1, max: 10)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def redo(self, steps: int = 1) -> str:
        """Redoes previously undone operation(s).

        Args:
            steps: Number of steps to redo (default: 1, max: 10)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def save_file(
        self,
        filepath: Optional[str] = None,
        compress: bool = True,
    ) -> str:
        """Saves the current Blender file.

        Args:
            filepath: Path to save (default: current file path, or temp if unsaved)
            compress: Compress .blend file (default: True)

        Returns:
            Status message with saved file path
        """
        pass

    @abstractmethod
    def new_file(self, load_ui: bool = False) -> str:
        """Creates a new Blender file (clears current scene).

        WARNING: Unsaved changes will be lost!

        Args:
            load_ui: Load UI from startup file

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def snapshot(
        self,
        action: str,
        name: Optional[str] = None,
    ) -> str:
        """Manages quick save/restore checkpoints.

        Snapshots are stored in temp directory and cleared on Blender restart.

        Args:
            action: Operation to perform (save, restore, list, delete)
            name: Snapshot name (required for restore/delete, auto-generated for save if not provided)

        Returns:
            Status message or list of snapshots
        """
        pass

    # === Export Tools ===

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

    # === Import Tools ===

    @abstractmethod
    def import_obj(
        self,
        filepath: str,
        use_split_objects: bool = True,
        use_split_groups: bool = False,
        global_scale: float = 1.0,
        forward_axis: str = "NEGATIVE_Z",
        up_axis: str = "Y",
    ) -> str:
        """Imports OBJ file.

        Args:
            filepath: Path to OBJ file
            use_split_objects: Split by object (creates separate objects)
            use_split_groups: Split by groups
            global_scale: Scale factor for imported geometry
            forward_axis: Forward axis (NEGATIVE_Z, Z, NEGATIVE_Y, Y, etc.)
            up_axis: Up axis (Y, Z, etc.)

        Returns:
            Success message with imported object names
        """
        pass

    @abstractmethod
    def import_fbx(
        self,
        filepath: str,
        use_custom_normals: bool = True,
        use_image_search: bool = True,
        ignore_leaf_bones: bool = False,
        automatic_bone_orientation: bool = False,
        global_scale: float = 1.0,
    ) -> str:
        """Imports FBX file.

        Args:
            filepath: Path to FBX file
            use_custom_normals: Use custom normals from file
            use_image_search: Search for images in file path
            ignore_leaf_bones: Ignore leaf bones (tip bones)
            automatic_bone_orientation: Auto-orient bones
            global_scale: Scale factor for imported geometry

        Returns:
            Success message with imported object names
        """
        pass

    @abstractmethod
    def import_glb(
        self,
        filepath: str,
        import_pack_images: bool = True,
        merge_vertices: bool = False,
        import_shading: str = "NORMALS",
    ) -> str:
        """Imports GLB/GLTF file.

        Args:
            filepath: Path to GLB/GLTF file
            import_pack_images: Pack images into .blend file
            merge_vertices: Merge duplicate vertices
            import_shading: Shading mode (NORMALS, FLAT, SMOOTH)

        Returns:
            Success message with imported object names
        """
        pass

    @abstractmethod
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
        """Imports image as a textured plane.

        Args:
            filepath: Path to image file
            name: Optional name for the created plane
            location: Optional [x, y, z] location
            size: Scale of the plane
            align_axis: Alignment axis (Z+, Y+, X+, Z-, Y-, X-)
            shader: Shader type (PRINCIPLED, SHADELESS, EMISSION)
            use_transparency: Use alpha channel for transparency

        Returns:
            Success message with created plane name
        """
        pass
