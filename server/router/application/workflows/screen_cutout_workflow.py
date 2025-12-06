"""
Screen/Display Cutout Workflow.

Sub-workflow for creating screen or display cutouts on surfaces.
TASK-039-21
"""

from typing import Dict, Any, Optional, List

from .base import BaseWorkflow, WorkflowStep


class ScreenCutoutWorkflow(BaseWorkflow):
    """Workflow for creating screen/display cutouts.

    Creates an inset and extruded area on a selected face,
    typically used for screens, displays, or buttons.

    This is often used as a sub-workflow within larger workflows
    like the phone workflow.
    """

    # Default parameters
    DEFAULT_INSET_THICKNESS = 0.05
    DEFAULT_EXTRUDE_DEPTH = 0.02
    DEFAULT_BEVEL_WIDTH = 0.005
    DEFAULT_BEVEL_SEGMENTS = 2

    @property
    def name(self) -> str:
        return "screen_cutout_workflow"

    @property
    def description(self) -> str:
        return "Screen/display cutout sub-workflow for creating inset displays"

    @property
    def trigger_pattern(self) -> Optional[str]:
        return "phone_like"  # Often triggered on phone-like objects

    @property
    def trigger_keywords(self) -> List[str]:
        return [
            "screen",
            "display",
            "cutout",
            "inset",
            "button",
            "panel",
            "lcd",
            "monitor",
        ]

    @property
    def sample_prompts(self) -> List[str]:
        """Sample prompts for LaBSE semantic matching.

        Includes variations in multiple languages for cross-lingual matching.
        """
        return [
            # English
            "add a screen cutout",
            "create a display area",
            "make an inset for the screen",
            "add a button recess",
            "create a panel indentation",
            "make a display hole",
            "add monitor screen area",
            "inset the face for a screen",
            # Polish
            "dodaj wycięcie na ekran",
            "stwórz obszar wyświetlacza",
            "zrób wgłębienie na przycisk",
            # German
            "Bildschirmaussparung hinzufügen",
            "Display-Bereich erstellen",
            "Taste einsetzen",
            # French
            "ajouter une découpe d'écran",
            "créer une zone d'affichage",
            "faire un enfoncement pour bouton",
            # Spanish
            "agregar recorte de pantalla",
            "crear área de visualización",
            "hacer un hueco para botón",
        ]

    def get_steps(self, params: Optional[Dict[str, Any]] = None) -> List[WorkflowStep]:
        """Generate workflow steps with optional parameter customization.

        Args:
            params: Optional parameters:
                - face_location: Location to select face (default [0, 0, 1] = top)
                - inset_thickness: Border thickness (default 0.05)
                - extrude_depth: Screen depth (default 0.02)
                - bevel_width: Edge bevel width (default 0.005)
                - bevel_segments: Bevel segments (default 2)
                - add_bevel: Whether to add bevel (default True)

        Returns:
            List of workflow steps.
        """
        params = params or {}

        # Extract parameters with defaults
        face_location = params.get("face_location", [0, 0, 1])
        inset_thickness = params.get("inset_thickness", self.DEFAULT_INSET_THICKNESS)
        extrude_depth = params.get("extrude_depth", self.DEFAULT_EXTRUDE_DEPTH)
        bevel_width = params.get("bevel_width", self.DEFAULT_BEVEL_WIDTH)
        bevel_segments = params.get("bevel_segments", self.DEFAULT_BEVEL_SEGMENTS)
        add_bevel = params.get("add_bevel", True)

        steps = [
            # Step 1: Select target face by location
            WorkflowStep(
                tool="mesh_select_targeted",
                params={"action": "by_location", "location": face_location},
                description=f"Select face at location {face_location}",
            ),
            # Step 2: Inset for border
            WorkflowStep(
                tool="mesh_inset",
                params={"thickness": inset_thickness},
                description=f"Inset face for border (thickness={inset_thickness})",
            ),
            # Step 3: Extrude inward
            WorkflowStep(
                tool="mesh_extrude_region",
                params={"depth": -extrude_depth},
                description=f"Extrude inward for screen depth ({-extrude_depth})",
            ),
        ]

        # Optional bevel for smooth edges
        if add_bevel:
            steps.append(
                WorkflowStep(
                    tool="mesh_bevel",
                    params={"width": bevel_width, "segments": bevel_segments},
                    description=f"Bevel screen edges (width={bevel_width})",
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
            "phone_screen": {
                "face_location": [0, 0, 1],
                "inset_thickness": 0.03,
                "extrude_depth": 0.02,
                "add_bevel": True,
            },
            "button": {
                "inset_thickness": 0.01,
                "extrude_depth": 0.005,
                "bevel_width": 0.002,
                "bevel_segments": 1,
            },
            "display_panel": {
                "inset_thickness": 0.08,
                "extrude_depth": 0.01,
                "bevel_width": 0.003,
                "add_bevel": True,
            },
            "deep_recess": {
                "inset_thickness": 0.05,
                "extrude_depth": 0.1,
                "add_bevel": False,
            },
        }
        return variants.get(variant_name)


# Singleton instance
screen_cutout_workflow = ScreenCutoutWorkflow()
