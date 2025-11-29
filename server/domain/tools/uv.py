from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IUVTool(ABC):
    @abstractmethod
    def list_maps(self, object_name: str, include_island_counts: bool = False) -> Dict[str, Any]:
        """Lists UV maps for a specified mesh object."""
        pass

    @abstractmethod
    def unwrap(
        self,
        object_name: Optional[str] = None,
        method: str = "SMART_PROJECT",
        angle_limit: float = 66.0,
        island_margin: float = 0.02,
        scale_to_bounds: bool = True,
    ) -> str:
        """Unwraps selected faces to UV space using specified projection method."""
        pass

    @abstractmethod
    def pack_islands(
        self,
        object_name: Optional[str] = None,
        margin: float = 0.02,
        rotate: bool = True,
        scale: bool = True,
    ) -> str:
        """Packs UV islands for optimal texture space usage."""
        pass

    @abstractmethod
    def create_seam(
        self,
        object_name: Optional[str] = None,
        action: str = "mark",
    ) -> str:
        """Marks or clears UV seams on selected edges."""
        pass
