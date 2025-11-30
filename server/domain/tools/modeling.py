from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IModelingTool(ABC):
    @abstractmethod
    def create_primitive(
        self, 
        primitive_type: str, 
        radius: float = 1.0, 
        size: float = 2.0, 
        location: List[float] = (0.0, 0.0, 0.0), 
        rotation: List[float] = (0.0, 0.0, 0.0),
        name: Optional[str] = None
    ) -> str:
        """Creates a primitive object (cube, sphere, etc)."""
        pass

    @abstractmethod
    def transform_object(
        self, 
        name: str, 
        location: Optional[List[float]] = None, 
        rotation: Optional[List[float]] = None, 
        scale: Optional[List[float]] = None
    ) -> str:
        """Transforms an object (move, rotate, scale)."""
        pass

    @abstractmethod
    def add_modifier(
        self, 
        name: str, 
        modifier_type: str, 
        properties: Dict[str, Any] = None
    ) -> str:
        """Adds a modifier to an object."""
        pass

    @abstractmethod
    def apply_modifier(self, name: str, modifier_name: str) -> str:
        """Applies a modifier to an object, making its changes permanent to the mesh."""
        pass

    @abstractmethod
    def convert_to_mesh(self, name: str) -> str:
        """Converts a non-mesh object (e.g., Curve, Text, Surface) to a mesh."""
        pass

    @abstractmethod
    def join_objects(self, object_names: List[str]) -> str:
        """Joins multiple mesh objects into a single mesh object."""
        pass

    @abstractmethod
    def separate_object(self, name: str, type: str = "LOOSE") -> List[str]:
        """Separates a mesh object into new objects based on type (LOOSE, SELECTED, MATERIAL)."""
        pass

    @abstractmethod
    def set_origin(self, name: str, type: str) -> str:
        """Sets the origin point of an object using Blender's origin_set operator types.
        Examples for 'type': 'ORIGIN_GEOMETRY_TO_CURSOR', 'ORIGIN_CURSOR_TO_GEOMETRY', 'ORIGIN_GEOMETRY_TO_MASS'.
        """
        pass

    @abstractmethod
    def get_modifiers(self, name: str) -> List[Dict[str, Any]]:
        """Returns a list of modifiers on the specified object."""
        pass

    # ==========================================================================
    # TASK-038-1: Metaball Tools
    # ==========================================================================

    @abstractmethod
    def metaball_create(
        self,
        name: str = "Metaball",
        location: Optional[List[float]] = None,
        element_type: str = "BALL",
        radius: float = 1.0,
        resolution: float = 0.2,
        threshold: float = 0.6,
    ) -> str:
        """
        Creates a metaball object.

        Args:
            name: Name for the metaball object
            location: World position [x, y, z]
            element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
            radius: Initial element radius
            resolution: Surface resolution (lower = higher quality)
            threshold: Merge threshold for elements

        Returns:
            Success message with object name.
        """
        pass

    @abstractmethod
    def metaball_add_element(
        self,
        metaball_name: str,
        element_type: str = "BALL",
        location: Optional[List[float]] = None,
        radius: float = 1.0,
        stiffness: float = 2.0,
    ) -> str:
        """
        Adds element to existing metaball.

        Args:
            metaball_name: Name of target metaball object
            element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
            location: Position relative to metaball origin [x, y, z]
            radius: Element radius
            stiffness: How strongly it merges with other elements

        Returns:
            Success message with element count.
        """
        pass

    @abstractmethod
    def metaball_to_mesh(
        self,
        metaball_name: str,
        apply_resolution: bool = True,
    ) -> str:
        """
        Converts metaball to mesh.

        Args:
            metaball_name: Name of metaball to convert
            apply_resolution: Whether to apply current resolution

        Returns:
            Success message with new mesh name.
        """
        pass

    # ==========================================================================
    # TASK-038-6: Skin Modifier Workflow
    # ==========================================================================

    @abstractmethod
    def skin_create_skeleton(
        self,
        name: str = "Skeleton",
        vertices: List[List[float]] = None,
        edges: Optional[List[List[int]]] = None,
        location: Optional[List[float]] = None,
    ) -> str:
        """
        Creates skeleton mesh for Skin modifier.

        Args:
            name: Name for skeleton object
            vertices: List of vertex positions [[x,y,z], ...]
            edges: List of edge connections [[v1, v2], ...] (auto-connect if None)
            location: World position [x, y, z]

        Returns:
            Success message with object name.
        """
        pass

    @abstractmethod
    def skin_set_radius(
        self,
        object_name: str,
        vertex_index: Optional[int] = None,
        radius_x: float = 0.25,
        radius_y: float = 0.25,
    ) -> str:
        """
        Sets skin radius at vertices.

        Args:
            object_name: Name of object with skin modifier
            vertex_index: Specific vertex index (None = all selected)
            radius_x: X radius for elliptical cross-section
            radius_y: Y radius for elliptical cross-section

        Returns:
            Success message.
        """
        pass
