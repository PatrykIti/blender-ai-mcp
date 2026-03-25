from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IMacroTool(ABC):
    @abstractmethod
    def cutout_recess(
        self,
        target_object: str,
        width: float,
        height: float,
        depth: float,
        face: str = "front",
        offset: Optional[List[float]] = None,
        mode: str = "recess",
        bevel_width: Optional[float] = None,
        bevel_segments: int = 2,
        cleanup: str = "delete",
        cutter_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a bounded cutter-based recess/cutout on one target object."""
        pass

    @abstractmethod
    def relative_layout(
        self,
        moving_object: str,
        reference_object: str,
        x_mode: str = "center",
        y_mode: str = "center",
        z_mode: str = "none",
        contact_axis: Optional[str] = None,
        contact_side: str = "positive",
        gap: float = 0.0,
        offset: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Place one object relative to another using bounded bbox alignment/contact rules."""
        pass
