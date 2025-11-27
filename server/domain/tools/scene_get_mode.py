"""Domain models and interface for the `scene_get_mode` tool."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field


class SceneModeResponse(BaseModel):
    """Describes the current Blender mode and basic selection context."""

    mode: str = Field(..., description="Raw Blender context mode, e.g., OBJECT or EDIT_MESH")
    active_object: Optional[str] = Field(
        default=None, description="Name of the active object if one is set"
    )
    active_object_type: Optional[str] = Field(
        default=None, description="Type of the active object (MESH, CAMERA, etc.)"
    )
    selected_object_names: List[str] = Field(
        default_factory=list, description="Names of currently selected objects"
    )
    selection_count: int = Field(
        default=0, description="Number of selected objects in Object Mode context"
    )


class ISceneGetModeTool(ABC):
    """Contract for retrieving Blender's current interaction mode."""

    @abstractmethod
    def get_mode(self) -> SceneModeResponse:
        """Return the active Blender mode and selection summary.

        Returns:
            SceneModeResponse: Structured context data for downstream tooling.
        """

