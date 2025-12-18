from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IMaterialTool(ABC):
    """Interface for Material Tools.

    Provides operations for managing Blender materials including
    creation, assignment, parameter modification, and texture binding.
    """

    @abstractmethod
    def list_materials(self, include_unassigned: bool = True) -> List[Dict[str, Any]]:
        """Lists all materials with shader parameters and assignment counts."""
        pass

    @abstractmethod
    def list_by_object(self, object_name: str, include_indices: bool = False) -> Dict[str, Any]:
        """Lists material slots for a given object."""
        pass

    # TASK-023-1: material_create
    @abstractmethod
    def create_material(
        self,
        name: str,
        base_color: Optional[List[float]] = None,
        metallic: float = 0.0,
        roughness: float = 0.5,
        emission_color: Optional[List[float]] = None,
        emission_strength: float = 0.0,
        alpha: float = 1.0,
    ) -> str:
        """Creates a new PBR material with Principled BSDF shader.

        Args:
            name: Material name.
            base_color: RGBA color [0-1] (default: [0.8, 0.8, 0.8, 1.0]).
            metallic: Metallic value 0-1.
            roughness: Roughness value 0-1.
            emission_color: Emission RGB [0-1].
            emission_strength: Emission strength.
            alpha: Alpha/opacity 0-1.

        Returns:
            Success message with created material name.
        """
        pass

    # TASK-023-2: material_assign
    @abstractmethod
    def assign_material(
        self,
        material_name: str,
        object_name: Optional[str] = None,
        slot_index: Optional[int] = None,
        assign_to_selection: bool = False,
    ) -> str:
        """Assigns material to object or selected faces.

        Args:
            material_name: Name of existing material.
            object_name: Target object (default: active object).
            slot_index: Material slot index (default: auto).
            assign_to_selection: If True and in Edit Mode, assign to selected faces.

        Returns:
            Success message with assignment details.
        """
        pass

    # TASK-023-3: material_set_params
    @abstractmethod
    def set_material_params(
        self,
        material_name: str,
        base_color: Optional[List[float]] = None,
        metallic: Optional[float] = None,
        roughness: Optional[float] = None,
        emission_color: Optional[List[float]] = None,
        emission_strength: Optional[float] = None,
        alpha: Optional[float] = None,
    ) -> str:
        """Modifies parameters of existing material.

        Only provided parameters are changed; others remain unchanged.

        Args:
            material_name: Name of material to modify.
            base_color: New RGBA color [0-1].
            metallic: New metallic value 0-1.
            roughness: New roughness value 0-1.
            emission_color: New emission RGB [0-1].
            emission_strength: New emission strength.
            alpha: New alpha/opacity 0-1.

        Returns:
            Success message with modified parameters.
        """
        pass

    # TASK-023-4: material_set_texture
    @abstractmethod
    def set_material_texture(
        self,
        material_name: str,
        texture_path: str,
        input_name: str = "Base Color",
        color_space: str = "sRGB",
    ) -> str:
        """Binds image texture to material input.

        Automatically creates Image Texture node and connects to Principled BSDF.

        Args:
            material_name: Target material name.
            texture_path: Path to image file.
            input_name: BSDF input ('Base Color', 'Roughness', 'Normal', 'Metallic', 'Emission Color').
            color_space: Color space ('sRGB' for color, 'Non-Color' for data maps).

        Returns:
            Success message with connection details.
        """
        pass

    # TASK-045-6: material_inspect_nodes
    @abstractmethod
    def inspect_nodes(
        self,
        material_name: str,
        include_connections: bool = True,
    ) -> Dict[str, Any]:
        """Inspects material shader node graph.

        Returns all nodes in the material's node tree with their types,
        parameters, and connections.

        Args:
            material_name: Name of the material to inspect.
            include_connections: Include node connections/links (default True).

        Returns:
            Dictionary with node graph information.
        """
        pass
