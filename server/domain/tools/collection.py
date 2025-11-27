from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ICollectionTool(ABC):
    @abstractmethod
    def list_collections(self, include_objects: bool = False) -> List[Dict[str, Any]]:
        """Lists all collections with hierarchy and metadata."""
        pass
