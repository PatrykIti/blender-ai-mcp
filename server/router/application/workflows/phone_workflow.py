"""
Phone/Tablet Modeling Workflow.

Complete workflow for creating smartphone/tablet-like objects.
TASK-039-19
"""

from typing import Dict, Any, Optional, List

from .base import BaseWorkflow, WorkflowStep


class PhoneWorkflow(BaseWorkflow):
    """Workflow for creating phone/tablet 3D models.

    Creates a rounded rectangular shape with screen inset,
    typical for smartphones and tablets.

    Default proportions: 0.4 × 0.8 × 0.05 (landscape phone)
    """

    # Default parameters
    DEFAULT_WIDTH = 0.4
    DEFAULT_HEIGHT = 0.8
    DEFAULT_DEPTH = 0.05
    DEFAULT_BEVEL_WIDTH = 0.02
    DEFAULT_BEVEL_SEGMENTS = 3
    DEFAULT_SCREEN_INSET = 0.03
    DEFAULT_SCREEN_DEPTH = 0.02

    @property
    def name(self) -> str:
        return "phone_workflow"

    @property
    def description(self) -> str:
        return "Complete phone/tablet modeling workflow with rounded edges and screen cutout"

    @property
    def trigger_pattern(self) -> Optional[str]:
        return "phone_like"

    @property
    def trigger_keywords(self) -> List[str]:
        return [
            "phone",
            "smartphone",
            "tablet",
            "mobile",
            "cellphone",
            "iphone",
            "android",
            "device",
        ]

    def get_steps(self, params: Optional[Dict[str, Any]] = None) -> List[WorkflowStep]:
        """Generate workflow steps with optional parameter customization.

        Args:
            params: Optional parameters:
                - width: Phone width (default 0.4)
                - height: Phone height (default 0.8)
                - depth: Phone depth/thickness (default 0.05)
                - bevel_width: Edge bevel width (default 0.02)
                - bevel_segments: Bevel smoothness (default 3)
                - screen_inset: Screen border width (default 0.03)
                - screen_depth: Screen depth (default 0.02)

        Returns:
            List of workflow steps.
        """
        params = params or {}

        # Extract parameters with defaults
        width = params.get("width", self.DEFAULT_WIDTH)
        height = params.get("height", self.DEFAULT_HEIGHT)
        depth = params.get("depth", self.DEFAULT_DEPTH)
        bevel_width = params.get("bevel_width", self.DEFAULT_BEVEL_WIDTH)
        bevel_segments = params.get("bevel_segments", self.DEFAULT_BEVEL_SEGMENTS)
        screen_inset = params.get("screen_inset", self.DEFAULT_SCREEN_INSET)
        screen_depth = params.get("screen_depth", self.DEFAULT_SCREEN_DEPTH)

        return [
            # Step 1: Create base cube
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"type": "CUBE"},
                description="Create base cube primitive",
            ),
            # Step 2: Scale to phone proportions
            WorkflowStep(
                tool="modeling_transform_object",
                params={"scale": [width, height, depth]},
                description=f"Scale to phone proportions ({width}×{height}×{depth})",
            ),
            # Step 3: Enter Edit mode
            WorkflowStep(
                tool="system_set_mode",
                params={"mode": "EDIT"},
                description="Enter Edit mode for edge operations",
            ),
            # Step 4: Select all geometry
            WorkflowStep(
                tool="mesh_select",
                params={"action": "all"},
                description="Select all geometry for bevel",
            ),
            # Step 5: Bevel all edges for rounded corners
            WorkflowStep(
                tool="mesh_bevel",
                params={"width": bevel_width, "segments": bevel_segments},
                description=f"Bevel edges (width={bevel_width}, segments={bevel_segments})",
            ),
            # Step 6: Deselect all
            WorkflowStep(
                tool="mesh_select",
                params={"action": "none"},
                description="Deselect all geometry",
            ),
            # Step 7: Select top face for screen area
            WorkflowStep(
                tool="mesh_select_targeted",
                params={"action": "by_location", "location": [0, 0, 1]},
                description="Select top face (screen area)",
            ),
            # Step 8: Inset for screen border
            WorkflowStep(
                tool="mesh_inset",
                params={"thickness": screen_inset},
                description=f"Inset face for screen border (thickness={screen_inset})",
            ),
            # Step 9: Extrude inward for screen depth
            WorkflowStep(
                tool="mesh_extrude_region",
                params={"depth": -screen_depth},
                description=f"Extrude screen inward (depth={-screen_depth})",
            ),
            # Step 10: Return to Object mode
            WorkflowStep(
                tool="system_set_mode",
                params={"mode": "OBJECT"},
                description="Return to Object mode",
            ),
        ]

    def get_variant(self, variant_name: str) -> Optional[Dict[str, Any]]:
        """Get predefined variant parameters.

        Args:
            variant_name: Name of the variant.

        Returns:
            Parameters for the variant, or None if not found.
        """
        variants = {
            "smartphone": {
                "width": 0.07,
                "height": 0.15,
                "depth": 0.008,
                "bevel_width": 0.003,
                "screen_inset": 0.005,
            },
            "tablet": {
                "width": 0.18,
                "height": 0.24,
                "depth": 0.008,
                "bevel_width": 0.005,
                "screen_inset": 0.01,
            },
            "laptop_screen": {
                "width": 0.35,
                "height": 0.22,
                "depth": 0.01,
                "bevel_width": 0.005,
                "screen_inset": 0.015,
            },
        }
        return variants.get(variant_name)


# Singleton instance
phone_workflow = PhoneWorkflow()
