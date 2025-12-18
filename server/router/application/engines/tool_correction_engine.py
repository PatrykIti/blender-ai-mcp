"""
Tool Correction Engine Implementation.

Fixes parameters, handles mode switching, and manages selection requirements.
"""

from typing import Dict, Any, List, Tuple, Optional

from server.router.domain.interfaces.i_correction_engine import ICorrectionEngine
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.infrastructure.config import RouterConfig


# Mode requirements by tool prefix
MODE_REQUIREMENTS: Dict[str, str] = {
    "mesh_": "EDIT",
    "modeling_": "OBJECT",
    "sculpt_": "SCULPT",
    "scene_": "OBJECT",
    "system_": "ANY",
    "export_": "OBJECT",
    "import_": "OBJECT",
    "material_": "OBJECT",
    "uv_": "EDIT",
    "curve_": "OBJECT",
    "collection_": "OBJECT",
    "bake_": "OBJECT",
    "lattice_": "OBJECT",
    "metaball_": "OBJECT",
    "skin_": "OBJECT",
}

# Parameter limits for clamping
PARAM_LIMITS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "mesh_bevel": {
        "offset": (0.001, 10.0),
        "segments": (1, 10),
    },
    "mesh_extrude_region": {
        "move": (-100.0, 100.0),
    },
    "mesh_inset": {
        "thickness": (0.001, 10.0),
        "depth": (-10.0, 10.0),
    },
    "mesh_subdivide": {
        "number_cuts": (1, 6),
    },
    "mesh_loop_cut": {
        "number_cuts": (1, 20),
    },
    "mesh_decimate": {
        "ratio": (0.01, 1.0),
    },
    "mesh_smooth": {
        "factor": (0.0, 1.0),
        "iterations": (1, 100),
    },
}

# Tools that require geometry selection
SELECTION_REQUIRED_TOOLS: List[str] = [
    "mesh_extrude_region",
    "mesh_bevel",
    "mesh_inset",
    "mesh_delete_selected",
    "mesh_duplicate_selected",
    "mesh_transform_selected",
    "mesh_dissolve",
    "mesh_bridge_edge_loops",
    "mesh_fill_holes",
    "mesh_smooth",
    "mesh_flatten",
    "mesh_shrink_fatten",
    "mesh_edge_slide",
    "mesh_vert_slide",
    "mesh_triangulate",
    "mesh_split",
    "mesh_rip",
    "mesh_spin",
    "mesh_screw",
    "mesh_edge_crease",
    "mesh_bevel_weight",
    "mesh_mark_sharp",
    "mesh_assign_to_group",
    "mesh_remove_from_group",
]


class ToolCorrectionEngine(ICorrectionEngine):
    """Implementation of tool call correction.

    Fixes parameters, handles mode switching, and manages selection requirements.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize correction engine.

        Args:
            config: Router configuration (uses defaults if None).
        """
        self._config = config or RouterConfig()

    def correct(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Tuple[CorrectedToolCall, List[CorrectedToolCall]]:
        """Correct a tool call based on context.

        Args:
            tool_name: Name of the tool to correct.
            params: Original parameters.
            context: Current scene context.

        Returns:
            Tuple of (corrected_call, pre_steps).
        """
        corrections_applied = []
        pre_steps = []
        corrected_params = dict(params) if params else {}

        # 1. Check and fix mode
        if self._config.auto_mode_switch:
            required_mode = self.get_required_mode(tool_name)
            if required_mode != "ANY" and context.mode != required_mode:
                mode_switch = self.get_mode_switch_call(required_mode)
                pre_steps.append(mode_switch)
                corrections_applied.append(f"mode_switch:{context.mode}->{required_mode}")

        # 2. Check and fix selection
        if self._config.auto_selection and self.requires_selection(tool_name):
            if not context.has_selection:
                selection_call = self.get_selection_call("all")
                pre_steps.append(selection_call)
                corrections_applied.append("auto_select_all")

        # 3. Clamp parameters
        if self._config.clamp_parameters:
            corrected_params, param_corrections = self.clamp_parameters(
                tool_name, corrected_params, context
            )
            corrections_applied.extend(param_corrections)

        # Build corrected call
        corrected_call = CorrectedToolCall(
            tool_name=tool_name,
            params=corrected_params,
            corrections_applied=corrections_applied,
            original_tool_name=tool_name,
            original_params=params,
            is_injected=False,
        )

        return corrected_call, pre_steps

    def clamp_parameters(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Clamp parameters to valid ranges.

        Args:
            tool_name: Name of the tool.
            params: Parameters to clamp.
            context: Scene context for dimension-relative clamping.

        Returns:
            Tuple of (clamped_params, corrections_applied).
        """
        clamped = dict(params)
        corrections = []

        # Get limits for this tool
        tool_limits = PARAM_LIMITS.get(tool_name, {})

        for param_name, (min_val, max_val) in tool_limits.items():
            if param_name in clamped:
                original_value = clamped[param_name]
                # Apply dimension-relative clamping for bevel
                if tool_name == "mesh_bevel" and param_name == "offset":
                    max_val = self._get_dimension_relative_max(
                        context, self._config.bevel_max_ratio
                    )

                if isinstance(original_value, (int, float)):
                    clamped_value = max(min_val, min(max_val, original_value))
                    if clamped_value != original_value:
                        clamped[param_name] = clamped_value
                        corrections.append(
                            f"clamp_{param_name}:{original_value}->{clamped_value}"
                        )
                elif (
                    isinstance(original_value, (list, tuple))
                    and all(isinstance(v, (int, float)) for v in original_value)
                ):
                    clamped_value = [
                        max(min_val, min(max_val, v)) for v in original_value
                    ]
                    if clamped_value != list(original_value):
                        clamped[param_name] = clamped_value
                        corrections.append(
                            f"clamp_{param_name}:{original_value}->{clamped_value}"
                        )

        return clamped, corrections

    def get_required_mode(self, tool_name: str) -> str:
        """Get the required Blender mode for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Required mode (OBJECT, EDIT, SCULPT, etc.) or "ANY".
        """
        for prefix, mode in MODE_REQUIREMENTS.items():
            if tool_name.startswith(prefix):
                return mode
        return "ANY"

    def requires_selection(self, tool_name: str) -> bool:
        """Check if tool requires geometry selection.

        Args:
            tool_name: Name of the tool.

        Returns:
            True if tool requires selection.
        """
        return tool_name in SELECTION_REQUIRED_TOOLS

    def get_mode_switch_call(self, target_mode: str) -> CorrectedToolCall:
        """Get a tool call to switch to target mode.

        Args:
            target_mode: Mode to switch to.

        Returns:
            CorrectedToolCall for mode switch.
        """
        return CorrectedToolCall(
            tool_name="system_set_mode",
            params={"mode": target_mode},
            corrections_applied=["injected_mode_switch"],
            is_injected=True,
        )

    def get_selection_call(self, selection_type: str = "all") -> CorrectedToolCall:
        """Get a tool call to make a selection.

        Args:
            selection_type: Type of selection ("all", "none", etc.).

        Returns:
            CorrectedToolCall for selection.
        """
        return CorrectedToolCall(
            tool_name="mesh_select",
            params={"action": selection_type},
            corrections_applied=["injected_selection"],
            is_injected=True,
        )

    def _get_dimension_relative_max(
        self,
        context: SceneContext,
        ratio: float,
    ) -> float:
        """Get max value relative to object dimensions.

        Args:
            context: Scene context with object dimensions.
            ratio: Ratio of smallest dimension.

        Returns:
            Maximum value based on dimensions.
        """
        dims = context.get_active_dimensions()
        if dims:
            min_dim = min(dims)
            return min_dim * ratio
        return 10.0  # Default if no dimensions available
