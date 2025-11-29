from abc import ABC, abstractmethod
from typing import List, Optional


class ISculptTool(ABC):
    """Abstract interface for Sculpt Mode tools."""

    # ==========================================================================
    # TASK-027-1: sculpt_auto (Mesh Filters)
    # ==========================================================================

    @abstractmethod
    def auto_sculpt(
        self,
        object_name: Optional[str] = None,
        operation: str = "smooth",
        strength: float = 0.5,
        iterations: int = 1,
        use_symmetry: bool = True,
        symmetry_axis: str = "X",
    ) -> str:
        """
        High-level sculpt operation applied to entire mesh using mesh filters.

        Args:
            object_name: Target object (default: active object)
            operation: Sculpt operation type ('smooth', 'inflate', 'flatten', 'sharpen')
            strength: Operation strength 0-1
            iterations: Number of passes
            use_symmetry: Enable symmetry
            symmetry_axis: Symmetry axis (X, Y, Z)

        Returns:
            Success message describing the operation performed.
        """
        pass

    # ==========================================================================
    # TASK-027-2: sculpt_brush_smooth
    # ==========================================================================

    @abstractmethod
    def brush_smooth(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Applies smooth brush at specified location.

        Args:
            object_name: Target object (default: active object)
            location: World position [x, y, z] for brush center
            radius: Brush radius in Blender units
            strength: Brush strength 0-1

        Returns:
            Success message describing the operation performed.
        """
        pass

    # ==========================================================================
    # TASK-027-3: sculpt_brush_grab
    # ==========================================================================

    @abstractmethod
    def brush_grab(
        self,
        object_name: Optional[str] = None,
        from_location: Optional[List[float]] = None,
        to_location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Grabs and moves geometry from one location to another.

        Args:
            object_name: Target object (default: active object)
            from_location: Start position [x, y, z]
            to_location: End position [x, y, z]
            radius: Brush radius
            strength: Brush strength 0-1

        Returns:
            Success message describing the operation performed.
        """
        pass

    # ==========================================================================
    # TASK-027-4: sculpt_brush_crease
    # ==========================================================================

    @abstractmethod
    def brush_crease(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
        pinch: float = 0.5,
    ) -> str:
        """
        Creates sharp crease at specified location.

        Args:
            object_name: Target object (default: active object)
            location: World position [x, y, z]
            radius: Brush radius
            strength: Brush strength 0-1
            pinch: Pinch amount for sharper creases

        Returns:
            Success message describing the operation performed.
        """
        pass
