from abc import ABC, abstractmethod
from typing import Dict, Any

class IUVTool(ABC):
    @abstractmethod
    def list_maps(self, object_name: str, include_island_counts: bool = False) -> Dict[str, Any]:
        """Lists UV maps for a specified mesh object."""
        pass
