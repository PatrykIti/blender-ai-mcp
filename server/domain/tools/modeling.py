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
        rotation: List[float] = (0.0, 0.0, 0.0)
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
