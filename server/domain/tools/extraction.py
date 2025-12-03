from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IExtractionTool(ABC):
    """Interface for extraction analysis tools (TASK-044).

    These tools support the Automatic Workflow Extraction System by providing
    deep topology analysis, component detection, and symmetry detection.
    """

    @abstractmethod
    def deep_topology(self, object_name: str) -> Dict[str, Any]:
        """Extended topology analysis for workflow extraction.

        Returns detailed analysis including vertex/edge/face counts,
        edge loop detection, face coplanarity groups, and feature indicators.
        """
        pass

    @abstractmethod
    def component_separate(self, object_name: str, min_vertex_count: int = 4) -> Dict[str, Any]:
        """Separates mesh into loose parts (components).

        Creates separate objects for each disconnected mesh island.
        Returns list of created component names and their stats.
        """
        pass

    @abstractmethod
    def detect_symmetry(self, object_name: str, tolerance: float = 0.001) -> Dict[str, Any]:
        """Detects symmetry planes in mesh geometry.

        Checks for symmetry along X, Y, Z axes by comparing vertex positions.
        Returns symmetry confidence for each axis.
        """
        pass

    @abstractmethod
    def edge_loop_analysis(self, object_name: str) -> Dict[str, Any]:
        """Analyzes edge loops for feature detection.

        Detects parallel edge loops, spacing patterns, support loops,
        and chamfered edges to identify bevels and subdivisions.
        """
        pass

    @abstractmethod
    def face_group_analysis(self, object_name: str, angle_threshold: float = 5.0) -> Dict[str, Any]:
        """Analyzes face groups for feature detection.

        Groups faces by normal direction, height, and connectivity.
        Detects inset faces, extruded regions, and planar regions.
        """
        pass

    @abstractmethod
    def render_angles(
        self,
        object_name: str,
        angles: Optional[List[str]] = None,
        resolution: int = 512,
        output_dir: str = "/tmp/extraction_renders"
    ) -> Dict[str, Any]:
        """Renders object from multiple angles for LLM Vision analysis.

        Renders the object from predefined angles (front, back, left, right, top, iso).
        Returns paths to rendered images.
        """
        pass
