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
    def select_by_index(self, indices: List[int], type: str = 'VERT', deselect: bool = False) -> str:
        """Selects specific geometry elements by their index."""
        pass

    @abstractmethod
    def extrude_region(self, move: Optional[List[float]] = None) -> str:
        """Extrudes selected region and optionally moves it."""
        pass

    @abstractmethod
    def fill_holes(self) -> str:
        """Fills holes in the mesh (creates faces)."""
        pass
