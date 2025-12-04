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

    @abstractmethod
    def inspect_modifiers(self, object_name: Optional[str] = None, include_disabled: bool = True) -> Dict[str, Any]:
        """Audits modifier stacks for a specific object or the entire scene."""
        pass

    # TASK-043: Scene Utility Tools
    @abstractmethod
    def rename_object(self, old_name: str, new_name: str) -> str:
        """Renames an object in the scene."""
        pass

    @abstractmethod
    def hide_object(self, object_name: str, hide: bool = True, hide_render: bool = False) -> str:
        """Hides or shows an object in the viewport and/or render."""
        pass

    @abstractmethod
    def show_all_objects(self, include_render: bool = False) -> str:
        """Shows all hidden objects in the scene."""
        pass

    @abstractmethod
    def isolate_object(self, object_names: List[str]) -> str:
        """Isolates object(s) by hiding all others."""
        pass

    @abstractmethod
    def camera_orbit(self, angle_horizontal: float = 0.0, angle_vertical: float = 0.0,
                     target_object: Optional[str] = None, target_point: Optional[List[float]] = None) -> str:
        """Orbits viewport camera around target."""
        pass

    @abstractmethod
    def camera_focus(self, object_name: str, zoom_factor: float = 1.0) -> str:
        """Focuses viewport camera on object."""
        pass

    # TASK-045: Object Inspection Tools
    @abstractmethod
    def get_custom_properties(self, object_name: str) -> Dict[str, Any]:
        """Gets custom properties (metadata) from an object."""
        pass

    @abstractmethod
    def set_custom_property(
        self,
        object_name: str,
        property_name: str,
        property_value: Any,
        delete: bool = False
    ) -> str:
        """Sets or deletes a custom property on an object."""
        pass

    @abstractmethod
    def get_hierarchy(
        self,
        object_name: Optional[str] = None,
        include_transforms: bool = False
    ) -> Dict[str, Any]:
        """Gets parent-child hierarchy for objects."""
        pass

    @abstractmethod
    def get_bounding_box(self, object_name: str, world_space: bool = True) -> Dict[str, Any]:
        """Gets bounding box corners for an object."""
        pass

    @abstractmethod
    def get_origin_info(self, object_name: str) -> Dict[str, Any]:
        """Gets origin (pivot point) information for an object."""
        pass
