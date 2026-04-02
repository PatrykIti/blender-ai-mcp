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
        capture_profile: Optional[str] = None,
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
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Place one object relative to another using bounded bbox alignment/contact rules."""
        pass

    @abstractmethod
    def attach_part_to_surface(
        self,
        part_object: str,
        surface_object: str,
        surface_axis: str,
        surface_side: str = "positive",
        align_mode: str = "center",
        gap: float = 0.0,
        offset: Optional[List[float]] = None,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Seat one part onto another object's surface/body with bounded contact placement."""
        pass

    @abstractmethod
    def align_part_with_contact(
        self,
        part_object: str,
        reference_object: str,
        target_relation: str = "contact",
        gap: float = 0.0,
        align_mode: str = "none",
        normal_axis: Optional[str] = None,
        preserve_side: bool = True,
        max_nudge: float = 0.5,
        offset: Optional[List[float]] = None,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Repair one already-related pair with a bounded contact/gap-aware nudge."""
        pass

    @abstractmethod
    def finish_form(
        self,
        target_object: str,
        preset: str = "rounded_housing",
        bevel_width: Optional[float] = None,
        bevel_segments: Optional[int] = None,
        subsurf_levels: Optional[int] = None,
        thickness: Optional[float] = None,
        solidify_offset: float = 0.0,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply one bounded finishing preset stack to an object."""
        pass
