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
