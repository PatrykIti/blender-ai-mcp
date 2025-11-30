from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IMeshTool(ABC):
    @abstractmethod
    def select_all(self, deselect: bool = False) -> str:
        """Selects or deselects all geometry elements."""
        pass

    @abstractmethod
    def delete_selected(self, type: str = 'VERT') -> str:
        """Deletes selected geometry elements (VERT, EDGE, FACE)."""
        pass

    @abstractmethod
    def select_by_index(self, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
        """
        Selects specific geometry elements by their index.
        selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect).
        """
        pass

    @abstractmethod
    def extrude_region(self, move: Optional[List[float]] = None) -> str:
        """Extrudes selected region and optionally moves it."""
        pass

    @abstractmethod
    def fill_holes(self) -> str:
        """Fills holes in the mesh (creates faces)."""
        pass

    @abstractmethod
    def bevel(self, offset: float, segments: int = 1, profile: float = 0.5, affect: str = 'EDGES') -> str:
        """Bevels selected edges or vertices."""
        pass

    @abstractmethod
    def loop_cut(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        """Adds a loop cut to the mesh."""
        pass

    @abstractmethod
    def inset(self, thickness: float, depth: float = 0.0) -> str:
        """Insets selected faces."""
        pass

    @abstractmethod
    def boolean(self, operation: str, solver: str = 'FAST') -> str:
        """Performs a boolean operation on selected geometry (Edit Mode)."""
        pass

    @abstractmethod
    def merge_by_distance(self, distance: float = 0.001) -> str:
        """Merges vertices that are close to each other (cleanup)."""
        pass

    @abstractmethod
    def subdivide(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        """Subdivides selected geometry."""
        pass

    @abstractmethod
    def smooth_vertices(self, iterations: int = 1, factor: float = 0.5) -> str:
        """Smooths selected vertices using Laplacian smoothing."""
        pass

    @abstractmethod
    def flatten_vertices(self, axis: str) -> str:
        """Flattens selected vertices along specified axis (X, Y, or Z)."""
        pass

    @abstractmethod
    def list_groups(self, object_name: str, group_type: str = 'VERTEX') -> Dict[str, Any]:
        """Lists vertex/face groups defined on a mesh object."""
        pass

    @abstractmethod
    def select_loop(self, edge_index: int) -> str:
        """Selects an edge loop based on the target edge index."""
        pass

    @abstractmethod
    def select_ring(self, edge_index: int) -> str:
        """Selects an edge ring based on the target edge index."""
        pass

    @abstractmethod
    def select_linked(self) -> str:
        """Selects all geometry linked to current selection (connected islands)."""
        pass

    @abstractmethod
    def select_more(self) -> str:
        """Grows the current selection by one step."""
        pass

    @abstractmethod
    def select_less(self) -> str:
        """Shrinks the current selection by one step."""
        pass

    @abstractmethod
    def get_vertex_data(self, object_name: str, selected_only: bool = False) -> Dict[str, Any]:
        """Returns vertex positions and selection states for programmatic analysis."""
        pass

    @abstractmethod
    def select_by_location(self, axis: str, min_coord: float, max_coord: float, mode: str = 'VERT') -> str:
        """Selects geometry within coordinate range on specified axis."""
        pass

    @abstractmethod
    def select_boundary(self, mode: str = 'EDGE') -> str:
        """Selects boundary edges (1 adjacent face) or boundary vertices."""
        pass

    # TASK-016-1: Mesh Randomize Tool
    @abstractmethod
    def randomize(self, amount: float = 0.1, uniform: float = 0.0, normal: float = 0.0, seed: int = 0) -> str:
        """Randomizes vertex positions for organic surface variations."""
        pass

    # TASK-016-2: Mesh Shrink/Fatten Tool
    @abstractmethod
    def shrink_fatten(self, value: float) -> str:
        """Moves vertices along their normals (Shrink/Fatten)."""
        pass

    # TASK-017-1: Mesh Create Vertex Group Tool
    @abstractmethod
    def create_vertex_group(self, object_name: str, name: str) -> str:
        """Creates a new vertex group on the specified object."""
        pass

    # TASK-017-2: Mesh Assign/Remove Vertex Group Tools
    @abstractmethod
    def assign_to_group(self, object_name: str, group_name: str, weight: float = 1.0) -> str:
        """Assigns selected vertices to a vertex group with specified weight."""
        pass

    @abstractmethod
    def remove_from_group(self, object_name: str, group_name: str) -> str:
        """Removes selected vertices from a vertex group."""
        pass

    # TASK-018-1: Mesh Bisect Tool
    @abstractmethod
    def bisect(self, plane_co: List[float], plane_no: List[float], clear_inner: bool = False, clear_outer: bool = False, fill: bool = False) -> str:
        """Cuts mesh along a plane defined by point and normal."""
        pass

    # TASK-018-2: Mesh Edge/Vertex Slide Tools
    @abstractmethod
    def edge_slide(self, value: float = 0.0) -> str:
        """Slides selected edges along the mesh topology."""
        pass

    @abstractmethod
    def vert_slide(self, value: float = 0.0) -> str:
        """Slides selected vertices along connected edges."""
        pass

    # TASK-018-3: Mesh Triangulate Tool
    @abstractmethod
    def triangulate(self) -> str:
        """Converts selected faces to triangles."""
        pass

    # TASK-018-4: Mesh Remesh Voxel Tool
    @abstractmethod
    def remesh_voxel(self, voxel_size: float = 0.1, adaptivity: float = 0.0) -> str:
        """Performs voxel remesh on the object (Object Mode operation)."""
        pass

    # TASK-019-1: Mesh Transform Selected Tool
    @abstractmethod
    def transform_selected(
        self,
        translate: Optional[List[float]] = None,
        rotate: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        pivot: str = 'MEDIAN_POINT'
    ) -> str:
        """Transforms selected geometry (move/rotate/scale) in Edit Mode."""
        pass

    # TASK-019-2: Mesh Bridge Edge Loops Tool
    @abstractmethod
    def bridge_edge_loops(
        self,
        number_cuts: int = 0,
        interpolation: str = 'LINEAR',
        smoothness: float = 0.0,
        twist: int = 0
    ) -> str:
        """Bridges two edge loops with faces."""
        pass

    # TASK-019-3: Mesh Duplicate Selected Tool
    @abstractmethod
    def duplicate_selected(self, translate: Optional[List[float]] = None) -> str:
        """Duplicates selected geometry within the same mesh."""
        pass

    # TASK-021-3: Mesh Spin Tool
    @abstractmethod
    def spin(
        self,
        steps: int = 12,
        angle: float = 6.283185,
        axis: str = 'Z',
        center: Optional[List[float]] = None,
        dupli: bool = False
    ) -> str:
        """Spins/lathes selected geometry around an axis."""
        pass

    # TASK-021-4: Mesh Screw Tool
    @abstractmethod
    def screw(
        self,
        steps: int = 12,
        turns: int = 1,
        axis: str = 'Z',
        center: Optional[List[float]] = None,
        offset: float = 0.0
    ) -> str:
        """Creates spiral/screw geometry from selected profile."""
        pass

    # TASK-021-5: Mesh Add Geometry Tools
    @abstractmethod
    def add_vertex(self, position: List[float]) -> str:
        """Adds a single vertex at the specified position."""
        pass

    @abstractmethod
    def add_edge_face(self) -> str:
        """Creates an edge or face from selected vertices."""
        pass

    # TASK-029-1: Mesh Edge Crease Tool
    @abstractmethod
    def edge_crease(self, crease_value: float = 1.0) -> str:
        """Sets crease weight on selected edges for subdivision surface control."""
        pass

    # TASK-029-2: Mesh Bevel Weight Tool
    @abstractmethod
    def bevel_weight(self, weight: float = 1.0) -> str:
        """Sets bevel weight on selected edges for bevel modifier control."""
        pass

    # TASK-029-3: Mesh Mark Sharp Tool
    @abstractmethod
    def mark_sharp(self, action: str = "mark") -> str:
        """Marks or clears sharp edges for auto-smooth and edge split."""
        pass

    # TASK-030-1: Mesh Dissolve Tool
    @abstractmethod
    def dissolve(
        self,
        dissolve_type: str = "limited",
        angle_limit: float = 5.0,
        use_face_split: bool = False,
        use_boundary_tear: bool = False
    ) -> str:
        """Dissolves selected geometry while preserving shape."""
        pass

    # TASK-030-2: Mesh Tris To Quads Tool
    @abstractmethod
    def tris_to_quads(
        self,
        face_threshold: float = 40.0,
        shape_threshold: float = 40.0
    ) -> str:
        """Converts triangles to quads where possible."""
        pass

    # TASK-030-3: Mesh Normals Make Consistent Tool
    @abstractmethod
    def normals_make_consistent(self, inside: bool = False) -> str:
        """Recalculates normals to face consistently outward."""
        pass

    # TASK-030-4: Mesh Decimate Tool
    @abstractmethod
    def decimate(
        self,
        ratio: float = 0.5,
        use_symmetry: bool = False,
        symmetry_axis: str = "X"
    ) -> str:
        """Reduces polycount while preserving shape."""
        pass

    # TASK-032-1: Mesh Knife Project Tool
    @abstractmethod
    def knife_project(self, cut_through: bool = True) -> str:
        """Projects cut from selected geometry (requires view angle)."""
        pass

    # TASK-032-2: Mesh Rip Tool
    @abstractmethod
    def rip(self, use_fill: bool = False) -> str:
        """Rips (tears) geometry at selected vertices."""
        pass

    # TASK-032-3: Mesh Split Tool
    @abstractmethod
    def split(self) -> str:
        """Splits selected geometry from the rest of the mesh."""
        pass

    # TASK-032-4: Mesh Edge Split Tool
    @abstractmethod
    def edge_split(self) -> str:
        """Splits mesh at selected edges to create sharp boundaries."""
        pass

    # TASK-038-5: Proportional Editing
    @abstractmethod
    def set_proportional_edit(
        self,
        enabled: bool = True,
        falloff_type: str = "SMOOTH",
        size: float = 1.0,
        use_connected: bool = False,
    ) -> str:
        """
        Configures proportional editing settings.

        Args:
            enabled: Whether to enable proportional editing
            falloff_type: SMOOTH, SPHERE, ROOT, INVERSE_SQUARE, SHARP, LINEAR, CONSTANT, RANDOM
            size: Influence radius
            use_connected: Only affect connected geometry

        Returns:
            Success message.
        """
        pass
