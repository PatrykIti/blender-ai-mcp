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
    def place_symmetry_pair(
        self,
        left_object: str,
        right_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        anchor_object: str = "auto",
        tolerance: float = 0.0001,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Place or correct one mirrored pair around a bounded mirror plane."""
        pass

    @abstractmethod
    def place_supported_pair(
        self,
        left_object: str,
        right_object: str,
        support_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        support_axis: str = "Z",
        support_side: str = "positive",
        anchor_object: str = "auto",
        gap: float = 0.0,
        tolerance: float = 0.0001,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Place or correct one mirrored pair against a shared support surface."""
        pass

    @abstractmethod
    def adjust_relative_proportion(
        self,
        primary_object: str,
        reference_object: str,
        expected_ratio: float,
        primary_axis: str = "X",
        reference_axis: str = "X",
        scale_target: str = "primary",
        tolerance: float = 0.01,
        uniform_scale: bool = True,
        max_scale_delta: float = 0.5,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Repair one cross-object proportion/ratio with a bounded scale adjustment."""
        pass

    @abstractmethod
    def adjust_segment_chain_arc(
        self,
        segment_objects: List[str],
        rotation_axis: str = "Y",
        total_angle: float = 30.0,
        direction: str = "positive",
        segment_spacing: Optional[float] = None,
        apply_rotation: bool = True,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Adjust one ordered segment chain into a bounded planar arc."""
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
