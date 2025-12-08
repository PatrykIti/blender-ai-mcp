"""
Router Tool Handler.

Application layer handler for Router control tools.
Implements IRouterTool interface.

TASK-046: Extended with semantic matching methods.
TASK-055: Extended with parameter resolution methods.
"""

import json
from typing import Dict, Any, List, Optional, Tuple

from server.domain.tools.router import IRouterTool


class RouterToolHandler(IRouterTool):
    """Handler for Router control tools.

    Unlike other handlers, this does NOT use RPC to communicate with Blender.
    It manages internal Router Supervisor state.

    Attributes:
        _router: SupervisorRouter instance (lazy-loaded).
        _enabled: Whether router is enabled in config.
    """

    def __init__(self, router=None, enabled: bool = True):
        """Initialize router handler.

        Args:
            router: Optional SupervisorRouter instance.
                   If not provided, will be obtained from DI.
            enabled: Whether router is enabled.
        """
        self._router = router
        self._enabled = enabled

    def _get_router(self):
        """Get router instance (lazy loading).

        Returns:
            SupervisorRouter instance or None.
        """
        if self._router is None:
            from server.infrastructure.di import get_router
            self._router = get_router()
        return self._router

    def set_goal(self, goal: str) -> str:
        """Set current modeling goal.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Confirmation message with matched workflow (if any).
        """
        if not self._enabled:
            return "Router is disabled. Goal noted but no workflow optimization available."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        matched_workflow = router.set_current_goal(goal)

        if matched_workflow:
            return (
                f"Goal set: '{goal}'\n"
                f"Matched workflow: {matched_workflow}\n\n"
                f"Proceeding with your next tool call will trigger this workflow automatically."
            )
        else:
            return (
                f"Goal set: '{goal}'\n"
                f"No specific workflow matched. Router will use heuristics to assist.\n\n"
                f"You can proceed with modeling - router will still help with mode switching and error prevention."
            )

    def get_status(self) -> str:
        """Get router status and statistics.

        Returns:
            Formatted status string.
        """
        if not self._enabled:
            return "Router Supervisor is DISABLED.\nSet ROUTER_ENABLED=true to enable."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        goal = router.get_current_goal()
        stats = router.get_stats()
        components = router.get_component_status()

        lines = [
            "=== Router Supervisor Status ===",
            f"Current goal: {goal or '(not set)'}",
            f"Pending workflow: {router.get_pending_workflow() or '(none)'}",
            "",
            "Statistics:",
            f"  Total calls processed: {stats.get('total_calls', 0)}",
            f"  Corrections applied: {stats.get('corrections_applied', 0)}",
            f"  Workflows expanded: {stats.get('workflows_expanded', 0)}",
            f"  Blocked calls: {stats.get('blocked_calls', 0)}",
            "",
            "Components:",
        ]

        for name, status in components.items():
            status_str = "OK" if status else "NOT READY"
            lines.append(f"  {name}: {status_str}")

        return "\n".join(lines)

    def clear_goal(self) -> str:
        """Clear current modeling goal.

        Returns:
            Confirmation message.
        """
        if not self._enabled:
            return "Router is disabled."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        router.clear_goal()
        return "Goal cleared. Ready for new modeling task."

    def get_goal(self) -> Optional[str]:
        """Get current modeling goal.

        Returns:
            Current goal or None.
        """
        if not self._enabled:
            return None

        router = self._get_router()
        if router is None:
            return None

        return router.get_current_goal()

    def get_pending_workflow(self) -> Optional[str]:
        """Get workflow matched from current goal.

        Returns:
            Workflow name or None.
        """
        if not self._enabled:
            return None

        router = self._get_router()
        if router is None:
            return None

        return router.get_pending_workflow()

    def is_enabled(self) -> bool:
        """Check if router is enabled.

        Returns:
            True if router is enabled and ready.
        """
        if not self._enabled:
            return False

        router = self._get_router()
        return router is not None

    # --- Semantic Matching Methods (TASK-046) ---

    def find_similar_workflows(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find workflows similar to a prompt.

        Uses LaBSE semantic embeddings to find workflows that match
        the meaning of the prompt, not just keywords.

        Args:
            prompt: Description of what to build.
            top_k: Number of similar workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        if not self._enabled:
            return []

        router = self._get_router()
        if router is None:
            return []

        return router.find_similar_workflows(prompt, top_k=top_k)

    def get_inherited_proportions(
        self,
        workflow_names: List[str],
        dimensions: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Get inherited proportions from workflows.

        Combines proportion rules from multiple workflows.

        Args:
            workflow_names: List of workflow names to inherit from.
            dimensions: Optional object dimensions [x, y, z].

        Returns:
            Dictionary with inherited proportion data.
        """
        if not self._enabled:
            return {"error": "Router is disabled"}

        router = self._get_router()
        if router is None:
            return {"error": "Router not initialized"}

        # Convert workflow names to (name, 1.0) tuples for equal weighting
        similar_workflows = [(name, 1.0) for name in workflow_names]

        return router.get_inherited_proportions(similar_workflows, dimensions)

    def record_feedback(
        self,
        prompt: str,
        correct_workflow: str,
    ) -> str:
        """Record user feedback for workflow matching.

        Call this when the router matched the wrong workflow.

        Args:
            prompt: Original prompt/description.
            correct_workflow: The workflow that should have matched.

        Returns:
            Confirmation message.
        """
        if not self._enabled:
            return "Router is disabled. Feedback not recorded."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        router.record_feedback_correction(prompt, correct_workflow)

        return (
            f"Feedback recorded. Thank you!\n"
            f"Prompt: '{prompt[:50]}...'\n"
            f"Correct workflow: {correct_workflow}\n\n"
            f"This will help improve future matching."
        )

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics.

        Returns:
            Dictionary with feedback statistics.
        """
        if not self._enabled:
            return {"error": "Router is disabled"}

        router = self._get_router()
        if router is None:
            return {"error": "Router not initialized"}

        return router.get_feedback_statistics()

    def find_similar_workflows_formatted(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> str:
        """Find similar workflows and return formatted string.

        Args:
            prompt: Description of what to build.
            top_k: Number of similar workflows to return.

        Returns:
            Formatted string with similar workflows.
        """
        similar = self.find_similar_workflows(prompt, top_k)

        if not similar:
            return (
                f"No similar workflows found for: '{prompt}'\n\n"
                f"This could mean:\n"
                f"- The prompt doesn't match any known workflow patterns\n"
                f"- LaBSE embeddings haven't been loaded yet\n"
                f"- The router is not enabled"
            )

        lines = [
            f"Similar workflows for: '{prompt}'",
            "",
        ]

        for i, (name, score) in enumerate(similar, 1):
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"{i}. {name}: {bar} {score:.1%}")

        return "\n".join(lines)

    def get_proportions_formatted(
        self,
        workflow_names: List[str],
        dimensions: Optional[List[float]] = None,
    ) -> str:
        """Get inherited proportions and return formatted string.

        Args:
            workflow_names: List of workflow names to inherit from.
            dimensions: Optional object dimensions [x, y, z].

        Returns:
            Formatted string with proportions.
        """
        result = self.get_inherited_proportions(workflow_names, dimensions)

        if "error" in result:
            return result["error"]

        lines = [
            "=== Inherited Proportions ===",
            f"Sources: {', '.join(result.get('sources', []))}",
            f"Total weight: {result.get('total_weight', 0):.2f}",
            "",
            "Proportions:",
        ]

        proportions = result.get("proportions", {})
        for name, value in sorted(proportions.items()):
            lines.append(f"  {name}: {value:.4f}")

        if "applied_values" in result:
            lines.append("")
            lines.append("Applied values (with dimensions):")
            for name, value in sorted(result["applied_values"].items()):
                lines.append(f"  {name}: {value:.4f}")

        return "\n".join(lines)

    # --- Parameter Resolution Methods (TASK-055) ---

    def _get_parameter_resolver(self):
        """Get parameter resolver instance (lazy loading).

        Returns:
            ParameterResolver instance or None.
        """
        from server.infrastructure.di import get_parameter_resolver
        return get_parameter_resolver()

    def _get_parameter_store(self):
        """Get parameter store instance (lazy loading).

        Returns:
            ParameterStore instance or None.
        """
        from server.infrastructure.di import get_parameter_store
        return get_parameter_store()

    def _get_workflow_loader(self):
        """Get workflow loader instance (lazy loading).

        Returns:
            WorkflowLoader instance.
        """
        from server.router.infrastructure.workflow_loader import get_workflow_loader
        return get_workflow_loader()

    def store_parameter_value(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ) -> str:
        """Store a resolved parameter value for future reuse.

        Args:
            context: The natural language context that triggered this value.
            parameter_name: Name of the parameter being resolved.
            value: The resolved value.
            workflow_name: Name of the workflow this parameter belongs to.

        Returns:
            Confirmation message or error message if validation fails.
        """
        if not self._enabled:
            return "Router is disabled. Parameter not stored."

        resolver = self._get_parameter_resolver()
        if resolver is None:
            return "Parameter resolver not initialized."

        # Try to get parameter schema for validation
        schema = None
        try:
            loader = self._get_workflow_loader()
            workflow = loader.get_workflow(workflow_name)
            if workflow and workflow.parameters:
                schema_data = workflow.parameters.get(parameter_name)
                if schema_data:
                    # Schema might be ParameterSchema or dict
                    if hasattr(schema_data, "validate_value"):
                        schema = schema_data
                    else:
                        from server.router.domain.entities.parameter import ParameterSchema
                        schema = ParameterSchema.from_dict(
                            {"name": parameter_name, **schema_data}
                        )
        except Exception:
            # Continue without schema validation
            pass

        return resolver.store_resolved_value(
            context=context,
            parameter_name=parameter_name,
            value=value,
            workflow_name=workflow_name,
            schema=schema,
        )

    def list_parameter_mappings(
        self,
        workflow_name: Optional[str] = None,
    ) -> str:
        """List stored parameter mappings.

        Args:
            workflow_name: Optional filter by workflow name.

        Returns:
            Formatted list of stored mappings.
        """
        if not self._enabled:
            return "Router is disabled."

        store = self._get_parameter_store()
        if store is None:
            return "Parameter store not initialized."

        mappings = store.list_mappings(workflow_name=workflow_name)

        if not mappings:
            if workflow_name:
                return f"No parameter mappings found for workflow '{workflow_name}'."
            return "No parameter mappings stored yet."

        lines = [
            "=== Stored Parameter Mappings ===",
            f"Total mappings: {len(mappings)}",
            "",
        ]

        # Group by workflow
        by_workflow: Dict[str, list] = {}
        for mapping in mappings:
            wf = mapping.workflow_name
            if wf not in by_workflow:
                by_workflow[wf] = []
            by_workflow[wf].append(mapping)

        for wf_name, wf_mappings in sorted(by_workflow.items()):
            lines.append(f"Workflow: {wf_name}")
            for m in wf_mappings:
                lines.append(
                    f"  '{m.context}' → {m.parameter_name}={m.value} "
                    f"(used {m.usage_count}x)"
                )
            lines.append("")

        return "\n".join(lines)

    def delete_parameter_mapping(
        self,
        context: str,
        parameter_name: str,
        workflow_name: str,
    ) -> str:
        """Delete a stored parameter mapping.

        Args:
            context: The context string of the mapping to delete.
            parameter_name: Parameter name.
            workflow_name: Workflow name.

        Returns:
            Confirmation or error message.
        """
        if not self._enabled:
            return "Router is disabled."

        store = self._get_parameter_store()
        if store is None:
            return "Parameter store not initialized."

        success = store.delete_mapping(
            context=context,
            parameter_name=parameter_name,
            workflow_name=workflow_name,
        )

        if success:
            return (
                f"Deleted mapping: '{context}' → {parameter_name} "
                f"(workflow: {workflow_name})"
            )
        else:
            return (
                f"Mapping not found: '{context}' → {parameter_name} "
                f"(workflow: {workflow_name})"
            )

    def set_goal_interactive(
        self,
        goal: str,
    ) -> Dict[str, Any]:
        """Set goal with interactive parameter resolution.

        Similar to set_goal, but returns detailed information about
        unresolved parameters that need LLM/user input.

        TASK-055-6: This method:
        1. Matches the goal to a workflow
        2. Resolves parameters using the three-tier system
        3. Returns unresolved parameters for LLM interaction

        Args:
            goal: User's modeling goal.

        Returns:
            Dictionary with workflow and parameter resolution info.
        """
        if not self._enabled:
            return {
                "error": "Router is disabled",
                "workflow_name": None,
                "resolved_parameters": {},
                "unresolved_parameters": [],
                "resolution_sources": {},
            }

        router = self._get_router()
        if router is None:
            return {
                "error": "Router not initialized",
                "workflow_name": None,
                "resolved_parameters": {},
                "unresolved_parameters": [],
                "resolution_sources": {},
            }

        # Step 1: Set goal and get matched workflow
        matched_workflow = router.set_current_goal(goal)

        if not matched_workflow:
            return {
                "workflow_name": None,
                "resolved_parameters": {},
                "unresolved_parameters": [],
                "resolution_sources": {},
                "message": f"No workflow matched for goal: '{goal}'",
            }

        # Step 2: Get workflow definition and its parameters
        loader = self._get_workflow_loader()
        workflow = loader.get_workflow(matched_workflow)

        if not workflow or not workflow.parameters:
            # Workflow has no parameters - all resolved
            return {
                "workflow_name": matched_workflow,
                "resolved_parameters": {},
                "unresolved_parameters": [],
                "resolution_sources": {},
                "message": f"Workflow '{matched_workflow}' has no interactive parameters",
            }

        # Step 3: Get existing modifiers from ensemble matching
        # Router stores modifiers in _pending_modifiers after set_current_goal
        existing_modifiers = getattr(router, '_pending_modifiers', {}) or {}

        # Step 4: Resolve parameters using three-tier system
        resolver = self._get_parameter_resolver()
        if resolver is None:
            return {
                "workflow_name": matched_workflow,
                "resolved_parameters": existing_modifiers,
                "unresolved_parameters": [],
                "resolution_sources": {k: "yaml_modifier" for k in existing_modifiers},
                "message": "Parameter resolver not available, using modifiers only",
            }

        # Convert workflow.parameters to ParameterSchema objects if needed
        from server.router.domain.entities.parameter import ParameterSchema

        param_schemas: Dict[str, ParameterSchema] = {}
        for name, schema_data in workflow.parameters.items():
            if hasattr(schema_data, "validate_value"):
                # Already a ParameterSchema
                param_schemas[name] = schema_data
            else:
                # Dict - convert to ParameterSchema
                param_schemas[name] = ParameterSchema.from_dict(
                    {"name": name, **schema_data}
                )

        # Resolve parameters
        result = resolver.resolve(
            prompt=goal,
            workflow_name=matched_workflow,
            parameters=param_schemas,
            existing_modifiers=existing_modifiers,
        )

        # Format unresolved parameters for LLM
        unresolved_list = []
        for unresolved in result.unresolved:
            unresolved_list.append({
                "name": unresolved.name,
                "type": unresolved.schema.type,
                "description": unresolved.schema.description,
                "range": list(unresolved.schema.range) if unresolved.schema.range else None,
                "default": unresolved.schema.default,
                "context": unresolved.context,
                "relevance": unresolved.relevance,
                "semantic_hints": unresolved.schema.semantic_hints,
            })

        return {
            "workflow_name": matched_workflow,
            "resolved_parameters": result.resolved,
            "unresolved_parameters": unresolved_list,
            "resolution_sources": result.resolution_sources,
            "needs_llm_input": result.needs_llm_input,
            "is_complete": result.is_complete,
        }

    def set_goal_interactive_formatted(
        self,
        goal: str,
    ) -> str:
        """Set goal with interactive parameter resolution (formatted output).

        Args:
            goal: User's modeling goal.

        Returns:
            Formatted string with resolution results.
        """
        result = self.set_goal_interactive(goal)

        if "error" in result:
            return result["error"]

        lines = []

        if result["workflow_name"]:
            lines.append(f"Matched workflow: {result['workflow_name']}")
            lines.append("")
        else:
            lines.append(f"No workflow matched for: '{goal}'")
            return "\n".join(lines)

        # Show resolved parameters
        if result["resolved_parameters"]:
            lines.append("Resolved parameters:")
            for name, value in sorted(result["resolved_parameters"].items()):
                source = result["resolution_sources"].get(name, "unknown")
                lines.append(f"  {name} = {value} ({source})")
            lines.append("")

        # Show unresolved parameters
        if result["unresolved_parameters"]:
            lines.append("Unresolved parameters (need your input):")
            for param in result["unresolved_parameters"]:
                lines.append(f"  {param['name']}:")
                lines.append(f"    Description: {param['description']}")
                if param['range']:
                    lines.append(f"    Range: {param['range'][0]} to {param['range'][1]}")
                lines.append(f"    Default: {param['default']}")
                lines.append(f"    Context: \"{param['context']}\"")
                lines.append("")

            lines.append("Use router_store_parameter() to provide values for these parameters.")
        else:
            lines.append("All parameters resolved! Workflow is ready to execute.")

        return "\n".join(lines)
