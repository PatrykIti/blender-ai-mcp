"""
Workflow Expansion Engine Implementation.

Transforms single tool calls into multi-step workflows.
"""

from typing import Dict, Any, Optional, List

from server.router.domain.interfaces.i_expansion_engine import IExpansionEngine
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.infrastructure.config import RouterConfig


# Predefined workflows
PREDEFINED_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "phone_workflow": {
        "description": "Complete phone/tablet modeling workflow",
        "trigger_pattern": "phone_like",
        "trigger_keywords": ["phone", "smartphone", "tablet", "mobile"],
        "steps": [
            {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
            {"tool": "modeling_transform_object", "params": {"scale": [0.4, 0.8, 0.05]}},
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_bevel", "params": {"width": 0.02, "segments": 3}},
            {"tool": "mesh_select", "params": {"action": "none"}},
            {"tool": "mesh_select_targeted", "params": {"action": "by_location", "location": [0, 0, 1]}},
            {"tool": "mesh_inset", "params": {"thickness": 0.03}},
            {"tool": "mesh_extrude_region", "params": {"depth": -0.02}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ],
    },
    "tower_workflow": {
        "description": "Tower/pillar modeling workflow with taper",
        "trigger_pattern": "tower_like",
        "trigger_keywords": ["tower", "pillar", "column", "obelisk"],
        "steps": [
            {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
            {"tool": "modeling_transform_object", "params": {"scale": [0.3, 0.3, 2.0]}},
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_subdivide", "params": {"number_cuts": 3}},
            {"tool": "mesh_select", "params": {"action": "none"}},
            {"tool": "mesh_select_targeted", "params": {"action": "by_location", "location": [0, 0, 1]}},
            {"tool": "mesh_transform_selected", "params": {"scale": [0.7, 0.7, 1.0]}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ],
    },
    "screen_cutout_workflow": {
        "description": "Screen/display cutout sub-workflow",
        "trigger_pattern": "phone_like",
        "trigger_keywords": ["screen", "display", "cutout"],
        "steps": [
            {"tool": "mesh_select_targeted", "params": {"action": "by_location", "location": [0, 0, 1]}},
            {"tool": "mesh_inset", "params": {"thickness": 0.05}},
            {"tool": "mesh_extrude_region", "params": {"depth": -0.02}},
            {"tool": "mesh_bevel", "params": {"width": 0.005, "segments": 2}},
        ],
    },
    "bevel_all_edges_workflow": {
        "description": "Bevel all edges of object",
        "trigger_keywords": ["bevel all", "round edges", "smooth edges"],
        "steps": [
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_bevel", "params": {"width": "$width", "segments": "$segments"}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ],
    },
}


class WorkflowExpansionEngine(IExpansionEngine):
    """Implementation of workflow expansion.

    Transforms single tool calls into multi-step workflows.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize expansion engine.

        Args:
            config: Router configuration (uses defaults if None).
        """
        self._config = config or RouterConfig()
        self._workflows: Dict[str, Dict[str, Any]] = dict(PREDEFINED_WORKFLOWS)

    def expand(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> Optional[List[CorrectedToolCall]]:
        """Expand a tool call into a workflow if applicable.

        Args:
            tool_name: Name of the tool to potentially expand.
            params: Original parameters.
            context: Current scene context.
            pattern: Detected geometry pattern (if any).

        Returns:
            List of expanded tool calls, or None if no expansion.
        """
        if not self._config.enable_workflow_expansion:
            return None

        # Check if pattern suggests a workflow
        if pattern and pattern.suggested_workflow:
            workflow_name = pattern.suggested_workflow
            if workflow_name in self._workflows:
                return self.expand_workflow(workflow_name, params)

        return None

    def get_workflow(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get a workflow definition by name.

        Args:
            workflow_name: Name of the workflow.

        Returns:
            Workflow steps definition, or None if not found.
        """
        workflow = self._workflows.get(workflow_name)
        if workflow:
            return workflow.get("steps", [])
        return None

    def register_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        trigger_pattern: Optional[str] = None,
        trigger_keywords: Optional[List[str]] = None,
    ) -> None:
        """Register a new workflow.

        Args:
            name: Unique workflow name.
            steps: List of workflow steps.
            trigger_pattern: Pattern that triggers this workflow.
            trigger_keywords: Keywords that trigger this workflow.
        """
        self._workflows[name] = {
            "description": f"Custom workflow: {name}",
            "trigger_pattern": trigger_pattern,
            "trigger_keywords": trigger_keywords or [],
            "steps": steps,
        }

    def get_available_workflows(self) -> List[str]:
        """Get names of all registered workflows.

        Returns:
            List of workflow names.
        """
        return list(self._workflows.keys())

    def expand_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any],
    ) -> List[CorrectedToolCall]:
        """Expand a named workflow with parameters.

        Args:
            workflow_name: Name of the workflow to expand.
            params: Parameters to pass to workflow steps.

        Returns:
            List of expanded tool calls.
        """
        workflow = self._workflows.get(workflow_name)
        if not workflow:
            return []

        steps = workflow.get("steps", [])
        expanded_calls = []

        for i, step in enumerate(steps):
            resolved_params = self._resolve_step_params(step.get("params", {}), params)

            call = CorrectedToolCall(
                tool_name=step["tool"],
                params=resolved_params,
                corrections_applied=[f"workflow:{workflow_name}:step_{i+1}"],
                is_injected=True,
            )
            expanded_calls.append(call)

        return expanded_calls

    def _resolve_step_params(
        self,
        step_params: Dict[str, Any],
        original_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve step parameters with inheritance.

        Args:
            step_params: Parameters defined in workflow step.
            original_params: Original parameters from LLM call.

        Returns:
            Resolved parameters dictionary.
        """
        resolved = {}

        for key, value in step_params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Inherit from original params
                orig_key = value[1:]
                if orig_key in original_params:
                    resolved[key] = original_params[orig_key]
                # Skip if not found in original (use defaults)
            else:
                resolved[key] = value

        return resolved

    def get_workflow_for_pattern(
        self,
        pattern: DetectedPattern,
    ) -> Optional[str]:
        """Get workflow name for a detected pattern.

        Args:
            pattern: Detected geometry pattern.

        Returns:
            Workflow name or None.
        """
        pattern_name = pattern.name

        for name, workflow in self._workflows.items():
            if workflow.get("trigger_pattern") == pattern_name:
                return name

        return None

    def get_workflow_for_keywords(
        self,
        keywords: List[str],
    ) -> Optional[str]:
        """Find workflow matching keywords.

        Args:
            keywords: Keywords to match.

        Returns:
            Workflow name or None.
        """
        keywords_lower = [k.lower() for k in keywords]

        for name, workflow in self._workflows.items():
            trigger_keywords = workflow.get("trigger_keywords", [])
            for kw in trigger_keywords:
                if kw.lower() in " ".join(keywords_lower):
                    return name

        return None
