from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ICollectionTool(ABC):
    @abstractmethod
    def list_collections(self, include_objects: bool = False) -> List[Dict[str, Any]]:
        """Lists all collections with hierarchy and metadata."""
        pass

    @abstractmethod
    def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False) -> Dict[str, Any]:
        """Lists all objects within a specified collection."""
        pass

    @abstractmethod
    def manage_collection(
        self,
        action: str,
        collection_name: str,
        new_name: Optional[str] = None,
        parent_name: Optional[str] = None,
        object_name: Optional[str] = None,
    ) -> str:
        """Manages collections: create, delete, rename, move/link/unlink objects.

        Args:
            action: Operation to perform ('create', 'delete', 'rename',
                    'move_object', 'link_object', 'unlink_object')
            collection_name: Target collection name
            new_name: New name for 'rename' action
            parent_name: Parent collection for 'create' action
            object_name: Object to move/link/unlink
        """
        pass
