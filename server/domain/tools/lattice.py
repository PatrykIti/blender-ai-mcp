from abc import ABC, abstractmethod
from typing import List, Optional


class ILatticeTool(ABC):
    """Abstract interface for lattice deformation tools."""

    @abstractmethod
    def lattice_create(
        self,
        name: str = "Lattice",
        target_object: Optional[str] = None,
        location: Optional[List[float]] = None,
        points_u: int = 2,
        points_v: int = 2,
        points_w: int = 2,
        interpolation: str = "KEY_LINEAR",
    ) -> str:
        """
        Creates a lattice object for non-destructive deformation.

        Args:
            name: Name for the lattice object
            target_object: If provided, fit lattice to object bounds
            location: World position [x, y, z]
            points_u: Resolution along U axis (2-64)
            points_v: Resolution along V axis (2-64)
            points_w: Resolution along W axis (2-64)
            interpolation: KEY_LINEAR, KEY_CARDINAL, KEY_CATMULL_ROM, KEY_BSPLINE

        Returns:
            Success message with lattice name and dimensions.
        """
        pass

    @abstractmethod
    def lattice_bind(
        self,
        object_name: str,
        lattice_name: str,
        vertex_group: Optional[str] = None,
    ) -> str:
        """
        Binds an object to a lattice using Lattice modifier.

        Args:
            object_name: Name of the object to deform
            lattice_name: Name of the lattice object
            vertex_group: Optional vertex group to limit deformation

        Returns:
            Success message confirming binding.
        """
        pass

    @abstractmethod
    def lattice_edit_point(
        self,
        lattice_name: str,
        point_index: int | List[int],
        offset: List[float],
        relative: bool = True,
    ) -> str:
        """
        Moves lattice control points programmatically.

        Args:
            lattice_name: Name of the lattice object
            point_index: Single index or list of indices to move
            offset: [x, y, z] offset or absolute position
            relative: If True, offset from current position; if False, set absolute

        Returns:
            Success message with updated point positions.
        """
        pass
