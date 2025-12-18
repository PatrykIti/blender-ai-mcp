"""
Correction Engine Interface.

Abstract interface for correcting tool call parameters and context.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext


class ICorrectionEngine(ABC):
    """Abstract interface for tool call correction.

    Fixes parameters, handles mode switching, and manages selection requirements.
    """

    @abstractmethod
    def correct(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Tuple[CorrectedToolCall, List[CorrectedToolCall]]:
        """Correct a tool call based on context.

        Args:
            tool_name: Name of the tool to correct.
            params: Original parameters.
            context: Current scene context.

        Returns:
            Tuple of (corrected_call, pre_steps).
            pre_steps are additional calls to execute before the main call
            (e.g., mode switch, selection).
        """
        pass

    @abstractmethod
    def clamp_parameters(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Clamp parameters to valid ranges.

        Args:
            tool_name: Name of the tool.
            params: Parameters to clamp.
            context: Scene context for dimension-relative clamping.

        Returns:
            Tuple of (clamped_params, corrections_applied).
        """
        pass

    @abstractmethod
    def get_required_mode(self, tool_name: str) -> str:
        """Get the required Blender mode for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Required mode (OBJECT, EDIT, SCULPT, etc.) or "ANY".
        """
        pass

    @abstractmethod
    def requires_selection(self, tool_name: str) -> bool:
        """Check if tool requires geometry selection.

        Args:
            tool_name: Name of the tool.

        Returns:
            True if tool requires selection.
        """
        pass

    @abstractmethod
    def get_mode_switch_call(self, target_mode: str) -> CorrectedToolCall:
        """Get a tool call to switch to target mode.

        Args:
            target_mode: Mode to switch to.

        Returns:
            CorrectedToolCall for mode switch.
        """
        pass

    @abstractmethod
    def get_selection_call(self, selection_type: str = "all") -> CorrectedToolCall:
        """Get a tool call to make a selection.

        Args:
            selection_type: Type of selection ("all", "none", etc.).

        Returns:
            CorrectedToolCall for selection.
        """
        pass
