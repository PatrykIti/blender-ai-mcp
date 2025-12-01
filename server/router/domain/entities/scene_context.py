"""
Scene Context Entity.

Data class for representing Blender scene state.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ObjectInfo:
    """Information about a single Blender object.

    Attributes:
        name: Object name.
        type: Object type (MESH, CURVE, etc.).
        location: World location [x, y, z].
        dimensions: Object dimensions [x, y, z].
        selected: Whether the object is selected.
        active: Whether the object is the active object.
    """

    name: str
    type: str
    location: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    dimensions: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    selected: bool = False
    active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "dimensions": self.dimensions,
            "selected": self.selected,
            "active": self.active,
        }


@dataclass
class TopologyInfo:
    """Mesh topology information.

    Attributes:
        vertices: Number of vertices.
        edges: Number of edges.
        faces: Number of faces.
        triangles: Number of triangles (after triangulation).
        selected_verts: Number of selected vertices (in edit mode).
        selected_edges: Number of selected edges (in edit mode).
        selected_faces: Number of selected faces (in edit mode).
    """

    vertices: int = 0
    edges: int = 0
    faces: int = 0
    triangles: int = 0
    selected_verts: int = 0
    selected_edges: int = 0
    selected_faces: int = 0

    @property
    def has_selection(self) -> bool:
        """Check if any geometry is selected."""
        return self.selected_verts > 0 or self.selected_edges > 0 or self.selected_faces > 0

    @property
    def total_selected(self) -> int:
        """Total number of selected elements."""
        return self.selected_verts + self.selected_edges + self.selected_faces

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vertices": self.vertices,
            "edges": self.edges,
            "faces": self.faces,
            "triangles": self.triangles,
            "selected_verts": self.selected_verts,
            "selected_edges": self.selected_edges,
            "selected_faces": self.selected_faces,
        }


@dataclass
class ProportionInfo:
    """Calculated proportions of an object.

    Attributes:
        aspect_xy: Width / Height ratio.
        aspect_xz: Width / Depth ratio.
        aspect_yz: Height / Depth ratio.
        is_flat: Object is flat (z < min(x, y) * 0.2).
        is_tall: Object is tall (z > max(x, y) * 2).
        is_wide: Object is wide (x > max(y, z) * 2).
        is_cubic: Object is roughly cubic (max/min < 1.5).
        dominant_axis: Largest axis ("x", "y", or "z").
        volume: Approximate volume.
        surface_area: Approximate surface area.
    """

    aspect_xy: float = 1.0
    aspect_xz: float = 1.0
    aspect_yz: float = 1.0
    is_flat: bool = False
    is_tall: bool = False
    is_wide: bool = False
    is_cubic: bool = True
    dominant_axis: str = "x"
    volume: float = 1.0
    surface_area: float = 6.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "aspect_xy": self.aspect_xy,
            "aspect_xz": self.aspect_xz,
            "aspect_yz": self.aspect_yz,
            "is_flat": self.is_flat,
            "is_tall": self.is_tall,
            "is_wide": self.is_wide,
            "is_cubic": self.is_cubic,
            "dominant_axis": self.dominant_axis,
            "volume": self.volume,
            "surface_area": self.surface_area,
        }


@dataclass
class SceneContext:
    """Complete scene context for router decision making.

    Attributes:
        mode: Current Blender mode (OBJECT, EDIT, SCULPT, etc.).
        active_object: Name of active object (if any).
        selected_objects: List of selected object names.
        objects: Detailed info about relevant objects.
        topology: Topology info for active mesh object.
        proportions: Proportion info for active object.
        materials: List of material names on active object.
        modifiers: List of modifier names on active object.
        timestamp: When context was captured.
    """

    mode: str = "OBJECT"
    active_object: Optional[str] = None
    selected_objects: List[str] = field(default_factory=list)
    objects: List[ObjectInfo] = field(default_factory=list)
    topology: Optional[TopologyInfo] = None
    proportions: Optional[ProportionInfo] = None
    materials: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_active_object(self) -> bool:
        """Check if there's an active object."""
        return self.active_object is not None

    @property
    def has_selection(self) -> bool:
        """Check if anything is selected."""
        if self.mode == "EDIT" and self.topology:
            return self.topology.has_selection
        return len(self.selected_objects) > 0

    @property
    def is_edit_mode(self) -> bool:
        """Check if in edit mode."""
        return self.mode == "EDIT"

    @property
    def is_object_mode(self) -> bool:
        """Check if in object mode."""
        return self.mode == "OBJECT"

    @property
    def active_object_type(self) -> Optional[str]:
        """Get type of active object."""
        for obj in self.objects:
            if obj.active:
                return obj.type
        return None

    def get_active_dimensions(self) -> Optional[List[float]]:
        """Get dimensions of active object."""
        for obj in self.objects:
            if obj.active:
                return obj.dimensions
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mode": self.mode,
            "active_object": self.active_object,
            "selected_objects": self.selected_objects,
            "objects": [obj.to_dict() for obj in self.objects],
            "topology": self.topology.to_dict() if self.topology else None,
            "proportions": self.proportions.to_dict() if self.proportions else None,
            "materials": self.materials,
            "modifiers": self.modifiers,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def empty(cls) -> "SceneContext":
        """Create empty scene context."""
        return cls()
