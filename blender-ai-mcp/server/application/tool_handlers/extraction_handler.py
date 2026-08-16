from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import require_dict_result
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.extraction import IExtractionTool


class ExtractionToolHandler(IExtractionTool):
    """Application handler for extraction analysis tools (TASK-044).

    Bridges MCP tools to Blender via RPC for deep topology analysis,
    component detection, and symmetry detection.
    """

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def deep_topology(self, object_name: str) -> Dict[str, Any]:
        """Extended topology analysis for workflow extraction."""
        return require_dict_result(self.rpc.send_request("extraction.deep_topology", {"object_name": object_name}))

    def component_separate(self, object_name: str, min_vertex_count: int = 4) -> Dict[str, Any]:
        """Separates mesh into loose parts (components)."""
        return require_dict_result(
            self.rpc.send_request(
                "extraction.component_separate", {"object_name": object_name, "min_vertex_count": min_vertex_count}
            )
        )

    def detect_symmetry(self, object_name: str, tolerance: float = 0.001) -> Dict[str, Any]:
        """Detects symmetry planes in mesh geometry."""
        return require_dict_result(
            self.rpc.send_request("extraction.detect_symmetry", {"object_name": object_name, "tolerance": tolerance})
        )

    def edge_loop_analysis(self, object_name: str) -> Dict[str, Any]:
        """Analyzes edge loops for feature detection."""
        return require_dict_result(self.rpc.send_request("extraction.edge_loop_analysis", {"object_name": object_name}))

    def face_group_analysis(self, object_name: str, angle_threshold: float = 5.0) -> Dict[str, Any]:
        """Analyzes face groups for feature detection."""
        return require_dict_result(
            self.rpc.send_request(
                "extraction.face_group_analysis", {"object_name": object_name, "angle_threshold": angle_threshold}
            )
        )

    def render_angles(
        self,
        object_name: str,
        angles: Optional[List[str]] = None,
        resolution: int = 512,
        output_dir: str = "/tmp/extraction_renders",
    ) -> Dict[str, Any]:
        """Renders object from multiple angles for LLM Vision analysis."""
        return require_dict_result(
            self.rpc.send_request(
                "extraction.render_angles",
                {
                    "object_name": object_name,
                    "angles": angles or ["front", "back", "left", "right", "top", "iso"],
                    "resolution": resolution,
                    "output_dir": output_dir,
                },
            )
        )
