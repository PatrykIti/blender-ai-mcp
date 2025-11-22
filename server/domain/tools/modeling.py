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
