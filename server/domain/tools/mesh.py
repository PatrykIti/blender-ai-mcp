from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IMeshTool(ABC):
    @abstractmethod
    def select_all(self, deselect: bool = False) -> str:
        """Selects or deselects all geometry elements."""
        pass

    @abstractmethod
    def delete_selected(self, type: str = 'VERT') -> str:
        """Deletes selected geometry elements (VERT, EDGE, FACE)."""
        pass

    @abstractmethod
    def select_by_index(self, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
        """
        Selects specific geometry elements by their index.
        selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect).
        """
        pass

    @abstractmethod
    def extrude_region(self, move: Optional[List[float]] = None) -> str:
        """Extrudes selected region and optionally moves it."""
        pass

    @abstractmethod
    def fill_holes(self) -> str:
        """Fills holes in the mesh (creates faces)."""
        pass

    @abstractmethod
    def bevel(self, offset: float, segments: int = 1, profile: float = 0.5, affect: str = 'EDGES') -> str:
        """Bevels selected edges or vertices."""
        pass

    @abstractmethod
    def loop_cut(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        """Adds a loop cut to the mesh."""
        pass

    @abstractmethod
    def inset(self, thickness: float, depth: float = 0.0) -> str:
        """Insets selected faces."""
        pass
