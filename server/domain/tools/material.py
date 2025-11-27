from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IMaterialTool(ABC):
    @abstractmethod
    def list_materials(self, include_unassigned: bool = True) -> List[Dict[str, Any]]:
        """Lists all materials with shader parameters and assignment counts."""
        pass

    @abstractmethod
    def list_by_object(self, object_name: str, include_indices: bool = False) -> Dict[str, Any]:
        """Lists material slots for a given object."""
        pass
