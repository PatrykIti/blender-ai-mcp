"""
Domain Interface for Armature Tools.

TASK-037: Armature & Rigging
"""

from abc import ABC, abstractmethod
from typing import Optional, List


class IArmatureTool(ABC):
    """Abstract interface for armature/rigging operations."""

    @abstractmethod
    def create(
        self,
        name: str = "Armature",
        location: Optional[List[float]] = None,
        bone_name: str = "Bone",
        bone_length: float = 1.0
    ) -> str:
        """Creates an armature with an initial bone."""
        pass

    @abstractmethod
    def add_bone(
        self,
        armature_name: str,
        bone_name: str,
        head: List[float],
        tail: List[float],
        parent_bone: Optional[str] = None,
        use_connect: bool = False
    ) -> str:
        """Adds a new bone to an existing armature."""
        pass

    @abstractmethod
    def bind(
        self,
        mesh_name: str,
        armature_name: str,
        bind_type: str = "AUTO"
    ) -> str:
        """Binds a mesh to an armature with automatic weights."""
        pass

    @abstractmethod
    def pose_bone(
        self,
        armature_name: str,
        bone_name: str,
        rotation: Optional[List[float]] = None,
        location: Optional[List[float]] = None,
        scale: Optional[List[float]] = None
    ) -> str:
        """Poses an armature bone (rotation/location/scale)."""
        pass

    @abstractmethod
    def weight_paint_assign(
        self,
        object_name: str,
        vertex_group: str,
        weight: float = 1.0,
        mode: str = "REPLACE"
    ) -> str:
        """Assigns weights to selected vertices for a vertex group."""
        pass

    @abstractmethod
    def get_data(
        self,
        object_name: str,
        include_pose: bool = False
    ) -> str:
        """Returns armature bones and hierarchy (optional pose data)."""
        pass
