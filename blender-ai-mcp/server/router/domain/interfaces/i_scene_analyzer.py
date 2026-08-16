"""
Scene Analyzer Interface.

Abstract interface for analyzing Blender scene state.
"""

from abc import ABC, abstractmethod
from typing import Optional

from server.router.domain.entities.scene_context import SceneContext


class ISceneAnalyzer(ABC):
    """Abstract interface for scene analysis.

    Analyzes current Blender scene state for router decision making.
    """

    @abstractmethod
    def analyze(self, object_name: Optional[str] = None) -> SceneContext:
        """Analyze current scene context.

        Args:
            object_name: Specific object to focus on (uses active if None).

        Returns:
            SceneContext with current scene state.
        """
        pass

    @abstractmethod
    def get_cached(self) -> Optional[SceneContext]:
        """Get cached scene context if still valid.

        Returns:
            Cached SceneContext or None if cache expired/invalid.
        """
        pass

    @abstractmethod
    def invalidate_cache(self) -> None:
        """Invalidate the scene context cache."""
        pass

    @abstractmethod
    def get_mode(self) -> str:
        """Get current Blender mode.

        Returns:
            Mode string (OBJECT, EDIT, SCULPT, etc.).
        """
        pass

    @abstractmethod
    def has_selection(self) -> bool:
        """Check if anything is selected.

        Returns:
            True if there's a selection in current context.
        """
        pass
