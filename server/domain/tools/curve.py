from abc import ABC, abstractmethod
from typing import List, Optional


class ICurveTool(ABC):
    """Interface for Curve tools."""

    # TASK-021-1: Curve Create Tool
    @abstractmethod
    def create_curve(
        self,
        curve_type: str = 'BEZIER',
        location: Optional[List[float]] = None
    ) -> str:
        """Creates a curve primitive (BEZIER, NURBS, PATH, CIRCLE)."""
        pass

    # TASK-021-2: Curve To Mesh Tool
    @abstractmethod
    def curve_to_mesh(self, object_name: str) -> str:
        """Converts a curve object to mesh geometry."""
        pass
