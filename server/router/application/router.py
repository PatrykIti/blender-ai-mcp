"""
Supervisor Router.

Main orchestrator that processes LLM tool calls through the router pipeline.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from server.router.infrastructure.config import RouterConfig
from server.router.infrastructure.logger import RouterLogger
from server.router.domain.entities.tool_call import (
    InterceptedToolCall,
    CorrectedToolCall,
    ToolCallSequence,
)
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.domain.entities.firewall_result import FirewallAction
from server.router.application.interceptor.tool_interceptor import ToolInterceptor
from server.router.application.analyzers.scene_context_analyzer import SceneContextAnalyzer
from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
from server.router.application.engines.tool_correction_engine import ToolCorrectionEngine
from server.router.application.engines.tool_override_engine import ToolOverrideEngine
from server.router.application.engines.workflow_expansion_engine import WorkflowExpansionEngine
from server.router.application.engines.error_firewall import ErrorFirewall
from server.router.application.classifier.intent_classifier import IntentClassifier
from server.router.application.triggerer.workflow_triggerer import WorkflowTriggerer


class SupervisorRouter:
    """Main router orchestrator.

    Processes LLM tool calls through an intelligent pipeline that
    corrects, expands, and validates operations before execution.

    Pipeline:
        1. Intercept → capture LLM tool call
        2. Analyze → read scene context
        3. Detect → identify geometry patterns
        4. Correct → fix params/mode/selection
        5. Trigger → check for workflow trigger (goal or heuristics)
        6. Override → check for better alternatives (if no trigger)
        7. Expand → transform to workflow if needed
        8. Build → build final tool sequence
        9. Firewall → validate each tool
        10. Execute → return final tool list

    Attributes:
        config: Router configuration.
        interceptor: Tool call interceptor.
        analyzer: Scene context analyzer.
        detector: Geometry pattern detector.
        correction_engine: Tool correction engine.
        override_engine: Tool override engine.
        expansion_engine: Workflow expansion engine.
        firewall: Error firewall.
        classifier: Intent classifier.
        triggerer: Workflow triggerer.
        logger: Router logger.
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        rpc_client: Optional[Any] = None,
        classifier: Optional[IntentClassifier] = None,
    ):
        """Initialize supervisor router.

        Args:
            config: Router configuration. Uses defaults if not provided.
            rpc_client: RPC client for Blender communication.
            classifier: Optional shared IntentClassifier instance.
                        If not provided, creates a new one.
                        Use this to share the LaBSE model (~1.8GB) between
                        multiple router instances in tests.
        """
        self.config = config or RouterConfig()
        self._rpc_client = rpc_client

        # Initialize components
        self.interceptor = ToolInterceptor()
        self.analyzer = SceneContextAnalyzer(
            rpc_client=rpc_client,
            cache_ttl=self.config.cache_ttl_seconds,
        )
        self.detector = GeometryPatternDetector()
        self.correction_engine = ToolCorrectionEngine(config=self.config)
        self.override_engine = ToolOverrideEngine(config=self.config)
        self.expansion_engine = WorkflowExpansionEngine(config=self.config)
        self.firewall = ErrorFirewall(config=self.config)
        self.classifier = classifier or IntentClassifier(config=self.config)
        self.triggerer = WorkflowTriggerer()
        self.logger = RouterLogger()

        # Tracking
        self._last_context: Optional[SceneContext] = None
        self._last_pattern: Optional[DetectedPattern] = None
        self._processing_stats: Dict[str, int] = {
            "total_calls": 0,
            "corrections_applied": 0,
            "overrides_triggered": 0,
            "workflows_expanded": 0,
            "blocked_calls": 0,
        }

        # Goal tracking (set via router_set_goal MCP tool)
        self._current_goal: Optional[str] = None
        self._pending_workflow: Optional[str] = None

    def set_rpc_client(self, rpc_client: Any) -> None:
        """Set the RPC client for Blender communication.

        Args:
            rpc_client: RPC client instance.
        """
        self._rpc_client = rpc_client
        self.analyzer.set_rpc_client(rpc_client)

    def process_llm_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process an LLM tool call through the router pipeline.

        This is the main entry point for processing tool calls from the LLM.
        The call goes through the full pipeline: intercept, analyze, detect,
        correct, override, expand, and firewall.

        Args:
            tool_name: Name of the tool called by LLM.
            params: Parameters passed to the tool.
            prompt: Original user prompt (if available).

        Returns:
            List of corrected/expanded tool calls to execute.
            Each item is a dict with 'tool' and 'params' keys.
        """
        self._processing_stats["total_calls"] += 1

        # Step 1: Intercept - capture the tool call
        intercepted = self.interceptor.intercept(tool_name, params, prompt)
        self.logger.log_intercept(tool_name, params, prompt)

        # Step 2: Analyze - read scene context
        context = self._analyze_scene()

        # Step 3: Detect - identify geometry patterns
        pattern = self._detect_pattern(context)

        # Step 4: Correct - fix params/mode/selection
        corrected, pre_steps = self._correct_tool_call(tool_name, params, context)

        # Step 5: Check workflow trigger (from goal or heuristics)
        triggered_workflow = self._check_workflow_trigger(
            tool_name, params, context, pattern
        )

        # Step 6: Override - check for better alternatives (skip if workflow triggered)
        override_result = None
        if not triggered_workflow:
            override_result = self._check_override(tool_name, params, context, pattern)

        # Step 7: Expand - transform to workflow if needed
        expanded = None
        if triggered_workflow:
            expanded = self._expand_triggered_workflow(triggered_workflow, params, context)
        elif not override_result:
            expanded = self._expand_workflow(tool_name, params, context, pattern)

        # Step 8: Build final tool sequence
        final_tools = self._build_tool_sequence(
            corrected=corrected,
            pre_steps=pre_steps,
            override_tools=override_result,
            expanded_tools=expanded,
        )

        # Step 9: Firewall - validate each tool
        validated_tools = self._validate_tools(final_tools, context)

        # Convert to output format
        return self._format_output(validated_tools)

    def route(self, prompt: str) -> List[str]:
        """Route a natural language prompt to tools (offline).

        Uses intent classification to determine which tools
        should handle a given prompt.

        Args:
            prompt: Natural language prompt.

        Returns:
            List of tool names that match the intent.
        """
        if not self.classifier.is_loaded():
            return []

        results = self.classifier.predict_top_k(prompt, k=3)
        return [tool_name for tool_name, confidence in results]

    def process_batch(
        self,
        tool_calls: List[Dict[str, Any]],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process a batch of tool calls.

        Args:
            tool_calls: List of tool calls with 'tool' and 'params'.
            prompt: Original user prompt (if available).

        Returns:
            List of corrected/expanded tool calls.
        """
        all_results = []

        for call in tool_calls:
            tool_name = call.get("tool", "")
            params = call.get("params", {})
            results = self.process_llm_tool_call(tool_name, params, prompt)
            all_results.extend(results)

        return all_results

    def _analyze_scene(self) -> SceneContext:
        """Analyze current scene context.

        Returns:
            SceneContext with current state.
        """
        if self.config.cache_scene_context:
            cached = self.analyzer.get_cached()
            if cached:
                self._last_context = cached
                return cached

        context = self.analyzer.analyze()
        self._last_context = context
        return context

    def _detect_pattern(self, context: SceneContext) -> Optional[DetectedPattern]:
        """Detect geometry patterns in context.

        Args:
            context: Scene context.

        Returns:
            Best matching pattern or None.
        """
        pattern = self.detector.get_best_match(context)
        self._last_pattern = pattern
        return pattern

    def _correct_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> tuple[CorrectedToolCall, List[CorrectedToolCall]]:
        """Apply corrections to tool call.

        Args:
            tool_name: Tool name.
            params: Tool parameters.
            context: Scene context.

        Returns:
            Tuple of (corrected_call, pre_steps).
        """
        corrected, pre_steps = self.correction_engine.correct(
            tool_name, params, context
        )

        if corrected.corrections_applied:
            self._processing_stats["corrections_applied"] += 1
            self.logger.log_correction(
                tool_name,
                corrected.corrections_applied,
                [{"tool": corrected.tool_name, "params": corrected.params}],
            )

        return corrected, pre_steps

    def _check_override(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern],
    ) -> Optional[List[CorrectedToolCall]]:
        """Check if tool should be overridden.

        Args:
            tool_name: Tool name.
            params: Tool parameters.
            context: Scene context.
            pattern: Detected pattern.

        Returns:
            List of replacement tools or None.
        """
        if not self.config.enable_overrides:
            return None

        decision = self.override_engine.check_override(
            tool_name, params, context, pattern
        )

        if decision.should_override:
            self._processing_stats["overrides_triggered"] += 1

            # Convert ReplacementTool objects to CorrectedToolCall
            replacement_calls = []
            for replacement in decision.replacement_tools:
                # Resolve inherited params
                resolved_params = dict(replacement.params)
                for inherit_key in replacement.inherit_params:
                    if inherit_key in params:
                        resolved_params[inherit_key] = params[inherit_key]

                call = CorrectedToolCall(
                    tool_name=replacement.tool_name,
                    params=resolved_params,
                    corrections_applied=[f"override:{decision.reasons[0].rule_name}"],
                    is_injected=True,
                )
                replacement_calls.append(call)

            self.logger.log_override(
                tool_name,
                decision.reasons[0].description if decision.reasons else "",
                [{"tool": c.tool_name, "params": c.params} for c in replacement_calls],
            )

            return replacement_calls

        return None

    def _expand_workflow(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern],
    ) -> Optional[List[CorrectedToolCall]]:
        """Expand tool to workflow if applicable.

        Args:
            tool_name: Tool name.
            params: Tool parameters.
            context: Scene context.
            pattern: Detected pattern.

        Returns:
            List of workflow steps or None.
        """
        if not self.config.enable_workflow_expansion:
            return None

        expanded = self.expansion_engine.expand(
            tool_name, params, context, pattern
        )

        if expanded:
            self._processing_stats["workflows_expanded"] += 1

        return expanded

    def _check_workflow_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern],
    ) -> Optional[str]:
        """Check if a workflow should be triggered.

        Priority:
        1. Pending workflow from goal (set via router_set_goal)
        2. WorkflowTriggerer heuristics

        Args:
            tool_name: Tool being called.
            params: Tool parameters.
            context: Scene context.
            pattern: Detected pattern.

        Returns:
            Workflow name to trigger, or None.
        """
        if not self.config.enable_workflow_expansion:
            return None

        # Priority 1: Use pending workflow from goal
        if self._pending_workflow:
            self.logger.log_info(
                f"Using pending workflow from goal: {self._pending_workflow}"
            )
            return self._pending_workflow

        # Priority 2: Check triggerer heuristics
        workflow_name = self.triggerer.determine_workflow(
            tool_name, params, context, pattern
        )

        if workflow_name:
            self.logger.log_info(
                f"Workflow triggered by heuristics: {workflow_name}"
            )

        return workflow_name

    def _expand_triggered_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Optional[List[CorrectedToolCall]]:
        """Expand a triggered workflow by name.

        Args:
            workflow_name: Name of workflow to expand.
            params: Original tool parameters.
            context: Scene context.

        Returns:
            List of workflow steps or None.
        """
        from server.router.application.workflows.registry import get_workflow_registry

        registry = get_workflow_registry()
        registry.ensure_custom_loaded()

        # Build evaluation context for $CALCULATE expressions (TASK-041-9)
        eval_context = self._build_eval_context(context, params)

        # Expand workflow with context
        calls = registry.expand_workflow(workflow_name, params, eval_context)

        if calls:
            self._processing_stats["workflows_expanded"] += 1
            self.logger.log_info(
                f"Expanded workflow '{workflow_name}' to {len(calls)} steps"
            )
            # Clear pending workflow after expansion
            self._pending_workflow = None

        return calls

    def _build_eval_context(
        self,
        context: SceneContext,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build evaluation context for expression evaluator.

        Combines scene context (dimensions, proportions, mode) with
        tool parameters for use in $CALCULATE expressions.

        Args:
            context: Current scene context.
            params: Tool parameters.

        Returns:
            Dictionary with all available variables for expressions.
        """
        eval_context: Dict[str, Any] = {
            "mode": context.mode,
        }

        # Add tool parameters
        if params:
            eval_context.update(params)

        # Add dimensions from active object
        active_dims = context.get_active_dimensions()
        if active_dims and len(active_dims) >= 3:
            eval_context["dimensions"] = active_dims
            eval_context["width"] = active_dims[0]
            eval_context["height"] = active_dims[1]
            eval_context["depth"] = active_dims[2]
            eval_context["min_dim"] = min(active_dims[:3])
            eval_context["max_dim"] = max(active_dims[:3])

        # Add proportions
        if context.proportions:
            eval_context["proportions"] = context.proportions.to_dict()
            # Add flat proportions as direct variables
            props_dict = context.proportions.to_dict()
            for key, value in props_dict.items():
                if isinstance(value, (int, float)):
                    eval_context[f"proportions_{key}"] = value

        # Add selection info
        if context.topology:
            eval_context["selected_verts"] = context.topology.selected_verts
            eval_context["selected_edges"] = context.topology.selected_edges
            eval_context["selected_faces"] = context.topology.selected_faces
            eval_context["has_selection"] = context.topology.has_selection

        return eval_context

    def _build_tool_sequence(
        self,
        corrected: CorrectedToolCall,
        pre_steps: List[CorrectedToolCall],
        override_tools: Optional[List[CorrectedToolCall]],
        expanded_tools: Optional[List[CorrectedToolCall]],
    ) -> List[CorrectedToolCall]:
        """Build final sequence of tools to execute.

        Priority:
        1. If override tools provided, use those
        2. Else if expanded workflow, use that
        3. Otherwise, use corrected call with pre-steps

        Args:
            corrected: Corrected tool call.
            pre_steps: Pre-execution steps.
            override_tools: Override replacement tools.
            expanded_tools: Expanded workflow tools.

        Returns:
            Final sequence of tool calls.
        """
        # Override takes highest priority
        if override_tools:
            return list(pre_steps) + list(override_tools)

        # Workflow expansion comes next
        if expanded_tools:
            return list(pre_steps) + list(expanded_tools)

        # Default: pre-steps + corrected call
        return list(pre_steps) + [corrected]

    def _validate_tools(
        self,
        tools: List[CorrectedToolCall],
        context: SceneContext,
    ) -> List[CorrectedToolCall]:
        """Validate tool calls through firewall.

        Args:
            tools: List of tool calls to validate.
            context: Scene context.

        Returns:
            List of validated/modified tool calls.
        """
        if not self.config.block_invalid_operations:
            return tools

        validated = []
        current_context = context

        for tool in tools:
            result = self.firewall.validate(tool, current_context)

            self.logger.log_firewall(
                tool.tool_name,
                result.action.value,
                result.message,
            )

            if result.action == FirewallAction.BLOCK:
                self._processing_stats["blocked_calls"] += 1
                continue  # Skip blocked tools

            elif result.action == FirewallAction.AUTO_FIX:
                # Add pre-steps from firewall
                for pre_step in result.pre_steps:
                    pre_call = CorrectedToolCall(
                        tool_name=pre_step["tool"],
                        params=pre_step.get("params", {}),
                        corrections_applied=["firewall_auto_fix"],
                        is_injected=True,
                    )
                    validated.append(pre_call)

                # Add modified call if provided
                if result.modified_call:
                    modified = CorrectedToolCall(
                        tool_name=result.modified_call["tool"],
                        params=result.modified_call.get("params", {}),
                        corrections_applied=tool.corrections_applied + ["firewall_modified"],
                        original_tool_name=tool.tool_name,
                        original_params=tool.params,
                    )
                    validated.append(modified)
                else:
                    validated.append(tool)

            elif result.action == FirewallAction.MODIFY:
                if result.modified_call:
                    modified = CorrectedToolCall(
                        tool_name=result.modified_call["tool"],
                        params=result.modified_call.get("params", {}),
                        corrections_applied=tool.corrections_applied + ["firewall_modified"],
                        original_tool_name=tool.tool_name,
                        original_params=tool.params,
                    )
                    validated.append(modified)
                else:
                    validated.append(tool)

            else:  # ALLOW
                validated.append(tool)

            # Update simulated context for next iteration
            # (mode switches affect subsequent validations)
            current_context = self._simulate_context_change(
                current_context, tool
            )

        return validated

    def _simulate_context_change(
        self,
        context: SceneContext,
        tool: CorrectedToolCall,
    ) -> SceneContext:
        """Simulate context change after tool execution.

        Args:
            context: Current context.
            tool: Tool that will be executed.

        Returns:
            Updated context (simulation).
        """
        # Simple simulation: update mode if mode switch
        if tool.tool_name == "system_set_mode":
            new_mode = tool.params.get("mode", context.mode)
            return SceneContext(
                mode=new_mode,
                active_object=context.active_object,
                selected_objects=context.selected_objects,
                objects=context.objects,
                topology=context.topology,
                proportions=context.proportions,
                materials=context.materials,
                modifiers=context.modifiers,
                timestamp=context.timestamp,
            )

        # Selection changes
        if tool.tool_name == "mesh_select":
            action = tool.params.get("action")
            if action == "all":
                # Simulate having selection
                if context.topology:
                    from server.router.domain.entities.scene_context import TopologyInfo
                    new_topo = TopologyInfo(
                        vertices=context.topology.vertices,
                        edges=context.topology.edges,
                        faces=context.topology.faces,
                        triangles=context.topology.triangles,
                        selected_verts=context.topology.vertices,
                        selected_edges=context.topology.edges,
                        selected_faces=context.topology.faces,
                    )
                    return SceneContext(
                        mode=context.mode,
                        active_object=context.active_object,
                        selected_objects=context.selected_objects,
                        objects=context.objects,
                        topology=new_topo,
                        proportions=context.proportions,
                        materials=context.materials,
                        modifiers=context.modifiers,
                        timestamp=context.timestamp,
                    )
            elif action == "none":
                # Simulate no selection
                if context.topology:
                    from server.router.domain.entities.scene_context import TopologyInfo
                    new_topo = TopologyInfo(
                        vertices=context.topology.vertices,
                        edges=context.topology.edges,
                        faces=context.topology.faces,
                        triangles=context.topology.triangles,
                        selected_verts=0,
                        selected_edges=0,
                        selected_faces=0,
                    )
                    return SceneContext(
                        mode=context.mode,
                        active_object=context.active_object,
                        selected_objects=context.selected_objects,
                        objects=context.objects,
                        topology=new_topo,
                        proportions=context.proportions,
                        materials=context.materials,
                        modifiers=context.modifiers,
                        timestamp=context.timestamp,
                    )

        return context

    def _format_output(
        self,
        tools: List[CorrectedToolCall],
    ) -> List[Dict[str, Any]]:
        """Format tool calls for output.

        Args:
            tools: List of corrected tool calls.

        Returns:
            List of dicts with 'tool' and 'params' keys.
        """
        return [
            {"tool": t.tool_name, "params": t.params}
            for t in tools
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics.

        Returns:
            Dictionary with processing stats.
        """
        return dict(self._processing_stats)

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self._processing_stats = {
            "total_calls": 0,
            "corrections_applied": 0,
            "overrides_triggered": 0,
            "workflows_expanded": 0,
            "blocked_calls": 0,
        }

    def get_last_context(self) -> Optional[SceneContext]:
        """Get last analyzed scene context.

        Returns:
            Last SceneContext or None.
        """
        return self._last_context

    def get_last_pattern(self) -> Optional[DetectedPattern]:
        """Get last detected pattern.

        Returns:
            Last DetectedPattern or None.
        """
        return self._last_pattern

    def invalidate_cache(self) -> None:
        """Invalidate scene context cache."""
        self.analyzer.invalidate_cache()
        self._last_context = None
        self._last_pattern = None

    def load_tool_metadata(self, metadata: Dict[str, Any]) -> None:
        """Load tool metadata for intent classification.

        Args:
            metadata: Tool metadata dictionary.
        """
        self.classifier.load_tool_embeddings(metadata)

    def is_ready(self) -> bool:
        """Check if router is ready for processing.

        Returns:
            True if router is fully initialized.
        """
        return self._rpc_client is not None

    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all components.

        Returns:
            Dictionary with component status.
        """
        return {
            "interceptor": True,
            "analyzer": self._rpc_client is not None,
            "detector": True,
            "correction_engine": True,
            "override_engine": True,
            "expansion_engine": True,
            "firewall": True,
            "classifier": self.classifier.is_loaded(),
        }

    def get_config(self) -> RouterConfig:
        """Get current router configuration.

        Returns:
            Current RouterConfig.
        """
        return self.config

    def update_config(self, **kwargs: Any) -> None:
        """Update router configuration.

        Args:
            **kwargs: Configuration options to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    # --- Goal Management ---

    def set_current_goal(self, goal: str) -> Optional[str]:
        """Set current modeling goal and find matching workflow.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Name of matched workflow, or None.
        """
        self._current_goal = goal

        # Try to find matching workflow
        from server.router.application.workflows.registry import get_workflow_registry

        registry = get_workflow_registry()
        workflow_name = registry.find_by_keywords(goal)

        if workflow_name:
            self._pending_workflow = workflow_name
            self.logger.log_info(f"Goal '{goal}' matched workflow: {workflow_name}")
        else:
            self._pending_workflow = None
            self.logger.log_info(f"Goal '{goal}' set (no matching workflow)")

        return workflow_name

    def get_current_goal(self) -> Optional[str]:
        """Get current modeling goal.

        Returns:
            Current goal string or None if not set.
        """
        return self._current_goal

    def get_pending_workflow(self) -> Optional[str]:
        """Get pending workflow (set by goal).

        Returns:
            Pending workflow name or None.
        """
        return self._pending_workflow

    def clear_goal(self) -> None:
        """Clear current goal (after workflow completion)."""
        self._current_goal = None
        self._pending_workflow = None
        self.logger.log_info("Goal cleared")
