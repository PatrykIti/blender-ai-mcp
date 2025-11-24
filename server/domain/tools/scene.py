from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

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

    @abstractmethod
    def duplicate_object(self, name: str, translation: Optional[List[float]] = None) -> Dict[str, Any]:
        """Duplicates an object and optionally moves it."""
        pass

    @abstractmethod
    def set_active_object(self, name: str) -> str:
        """Sets the active object."""
        pass

    @abstractmethod
    def get_viewport(self, width: int = 1024, height: int = 768, shading: str = "SOLID", camera_name: Optional[str] = None, focus_target: Optional[str] = None) -> str:
        """Returns a base64 encoded image of the viewport."""
        pass
