from abc import ABC, abstractmethod
from typing import List, Optional, Literal


class ITextTool(ABC):
    """Interface for text and typography operations."""

    @abstractmethod
    def create(
        self,
        text: str = "Text",
        name: str = "Text",
        location: Optional[List[float]] = None,
        font: Optional[str] = None,
        size: float = 1.0,
        extrude: float = 0.0,
        bevel_depth: float = 0.0,
        bevel_resolution: int = 0,
        align_x: str = "LEFT",
        align_y: str = "BOTTOM_BASELINE",
    ) -> str:
        """
        Creates a 3D text object.

        Args:
            text: The text content to display
            name: Name for the text object
            location: World position [x, y, z]
            font: Path to .ttf/.otf font file (None for default)
            size: Text size
            extrude: Depth/extrusion amount
            bevel_depth: Bevel depth for rounded edges
            bevel_resolution: Bevel resolution (segments)
            align_x: Horizontal alignment (LEFT, CENTER, RIGHT, JUSTIFY, FLUSH)
            align_y: Vertical alignment (TOP, TOP_BASELINE, CENTER, BOTTOM_BASELINE, BOTTOM)

        Returns:
            Success message with object name.
        """
        pass

    @abstractmethod
    def edit(
        self,
        object_name: str,
        text: Optional[str] = None,
        size: Optional[float] = None,
        extrude: Optional[float] = None,
        bevel_depth: Optional[float] = None,
        bevel_resolution: Optional[int] = None,
        align_x: Optional[str] = None,
        align_y: Optional[str] = None,
    ) -> str:
        """
        Edits an existing text object.

        Only provided parameters are modified, others remain unchanged.

        Args:
            object_name: Name of the text object to edit
            text: New text content
            size: New text size
            extrude: New extrusion depth
            bevel_depth: New bevel depth
            bevel_resolution: New bevel resolution
            align_x: New horizontal alignment
            align_y: New vertical alignment

        Returns:
            Success message with modified properties.
        """
        pass

    @abstractmethod
    def to_mesh(
        self,
        object_name: str,
        keep_original: bool = False,
    ) -> str:
        """
        Converts a text object to mesh geometry.

        Args:
            object_name: Name of the text object to convert
            keep_original: If True, keeps the original text object

        Returns:
            Success message with new mesh name.
        """
        pass
