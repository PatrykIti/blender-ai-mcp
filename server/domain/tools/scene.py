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

    @abstractmethod
    def create_light(self, type: str, energy: float, color: List[float], location: List[float], name: Optional[str] = None) -> str:
        """Creates a light source."""
        pass

    @abstractmethod
    def create_camera(self, location: List[float], rotation: List[float], lens: float = 50.0, clip_start: Optional[float] = None, clip_end: Optional[float] = None, name: Optional[str] = None) -> str:
        """Creates a camera."""
        pass

    @abstractmethod
    def create_empty(self, type: str, size: float, location: List[float], name: Optional[str] = None) -> str:
        """Creates an empty object."""
        pass

    @abstractmethod
    def set_mode(self, mode: str) -> str:
        """Sets the interaction mode (OBJECT, EDIT, SCULPT)."""
        pass

    @abstractmethod
    def get_mode(self) -> Dict[str, Any]:
        """Returns the current Blender interaction mode snapshot."""
        pass

    @abstractmethod
    def list_selection(self) -> Dict[str, Any]:
        """Returns the current selection summary for Object/Edit modes."""
        pass

    @abstractmethod
    def inspect_object(self, name: str) -> Dict[str, Any]:
        """Returns a structured report for the specified object."""
        pass

    @abstractmethod
    def snapshot_state(self, include_mesh_stats: bool = False, include_materials: bool = False) -> Dict[str, Any]:
        """Captures a lightweight JSON snapshot of the scene state."""
        pass

    @abstractmethod
    def inspect_material_slots(self, material_filter: Optional[str] = None, include_empty_slots: bool = True) -> Dict[str, Any]:
        """Audits material slot assignments across the entire scene."""
        pass

    @abstractmethod
    def inspect_mesh_topology(self, object_name: str, detailed: bool = False) -> Dict[str, Any]:
        """Reports detailed topology stats for a given mesh."""
        pass
