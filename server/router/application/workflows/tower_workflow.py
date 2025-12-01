"""
Tower/Pillar Modeling Workflow.

Workflow for creating tower, pillar, and column-like structures.
TASK-039-20
"""

from typing import Dict, Any, Optional, List

from .base import BaseWorkflow, WorkflowStep


class TowerWorkflow(BaseWorkflow):
    """Workflow for creating tower/pillar 3D models.

    Creates a tall rectangular structure with optional taper effect.
    Suitable for towers, pillars, columns, obelisks.

    Default proportions: 0.3 × 0.3 × 2.0 (tall cube)
    """

    # Default parameters
    DEFAULT_BASE_SIZE = 0.3
    DEFAULT_HEIGHT = 2.0
    DEFAULT_SUBDIVISIONS = 3
    DEFAULT_TAPER_FACTOR = 0.7

    @property
    def name(self) -> str:
        return "tower_workflow"

    @property
    def description(self) -> str:
        return "Tower/pillar modeling workflow with subdivisions and taper effect"

    @property
    def trigger_pattern(self) -> Optional[str]:
        return "tower_like"

    @property
    def trigger_keywords(self) -> List[str]:
        return [
            "tower",
            "pillar",
            "column",
            "obelisk",
            "spire",
            "minaret",
            "chimney",
            "post",
        ]

    def get_steps(self, params: Optional[Dict[str, Any]] = None) -> List[WorkflowStep]:
        """Generate workflow steps with optional parameter customization.

        Args:
            params: Optional parameters:
                - base_size: Base X/Y size (default 0.3)
                - height: Tower height (default 2.0)
                - subdivisions: Number of loop cuts (default 3)
                - taper_factor: Top scale factor (default 0.7)
                - add_taper: Whether to add taper (default True)

        Returns:
            List of workflow steps.
        """
        params = params or {}

        # Extract parameters with defaults
        base_size = params.get("base_size", self.DEFAULT_BASE_SIZE)
        height = params.get("height", self.DEFAULT_HEIGHT)
        subdivisions = params.get("subdivisions", self.DEFAULT_SUBDIVISIONS)
        taper_factor = params.get("taper_factor", self.DEFAULT_TAPER_FACTOR)
        add_taper = params.get("add_taper", True)

        steps = [
            # Step 1: Create base cube
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"type": "CUBE"},
                description="Create base cube primitive",
            ),
            # Step 2: Scale to tower proportions
            WorkflowStep(
                tool="modeling_transform_object",
                params={"scale": [base_size, base_size, height]},
                description=f"Scale to tower proportions ({base_size}×{base_size}×{height})",
            ),
            # Step 3: Enter Edit mode
            WorkflowStep(
                tool="system_set_mode",
                params={"mode": "EDIT"},
                description="Enter Edit mode for subdivisions",
            ),
            # Step 4: Subdivide for segments
            WorkflowStep(
                tool="mesh_subdivide",
                params={"number_cuts": subdivisions},
                description=f"Add {subdivisions} subdivision cuts for segments",
            ),
        ]

        # Optional taper effect
        if add_taper:
            steps.extend(
                [
                    # Step 5: Deselect all
                    WorkflowStep(
                        tool="mesh_select",
                        params={"action": "none"},
                        description="Deselect all geometry",
                    ),
                    # Step 6: Select top vertices/edges
                    WorkflowStep(
                        tool="mesh_select_targeted",
                        params={"action": "by_location", "location": [0, 0, 1]},
                        description="Select top geometry for taper",
                    ),
                    # Step 7: Scale down for taper
                    WorkflowStep(
                        tool="mesh_transform_selected",
                        params={"scale": [taper_factor, taper_factor, 1.0]},
                        description=f"Scale top for taper effect (factor={taper_factor})",
                    ),
                ]
            )

        # Final step: Return to Object mode
        steps.append(
            WorkflowStep(
                tool="system_set_mode",
                params={"mode": "OBJECT"},
                description="Return to Object mode",
            )
        )

        return steps

    def get_variant(self, variant_name: str) -> Optional[Dict[str, Any]]:
        """Get predefined variant parameters.

        Args:
            variant_name: Name of the variant.

        Returns:
            Parameters for the variant, or None if not found.
        """
        variants = {
            "obelisk": {
                "base_size": 0.2,
                "height": 3.0,
                "subdivisions": 5,
                "taper_factor": 0.4,
            },
            "pillar": {
                "base_size": 0.4,
                "height": 2.5,
                "subdivisions": 2,
                "taper_factor": 0.9,  # Slight taper only
            },
            "chimney": {
                "base_size": 0.5,
                "height": 4.0,
                "subdivisions": 4,
                "add_taper": False,
            },
            "spire": {
                "base_size": 0.15,
                "height": 2.0,
                "subdivisions": 6,
                "taper_factor": 0.1,  # Sharp point
            },
        }
        return variants.get(variant_name)


# Singleton instance
tower_workflow = TowerWorkflow()
