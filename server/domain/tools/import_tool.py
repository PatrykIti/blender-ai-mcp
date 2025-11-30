from abc import ABC, abstractmethod


class IImportTool(ABC):
    """Abstract interface for import operations."""

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
        name: str | None = None,
        location: list[float] | None = None,
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
