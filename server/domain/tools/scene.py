from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISceneTool(ABC):
    @abstractmethod
    def list_objects(self) -> List[Dict[str, Any]]:
        """Lists all objects in the scene."""
        pass

    @abstractmethod
    def delete_object(self, name: str) -> str:
        """Deletes an object by name."""
        pass

    @abstractmethod
    def clean_scene(self, keep_lights_and_cameras: bool) -> str:
        """Cleans the scene."""
        pass
