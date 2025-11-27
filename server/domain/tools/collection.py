from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ICollectionTool(ABC):
    @abstractmethod
    def list_collections(self, include_objects: bool = False) -> List[Dict[str, Any]]:
        """Lists all collections with hierarchy and metadata."""
        pass

    @abstractmethod
    def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False) -> Dict[str, Any]:
        """Lists all objects within a specified collection."""
        pass
