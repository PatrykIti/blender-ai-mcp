"""
LoopExpander (TASK-058).

Responsible for:
- loop expansion (range/values, single + nested)
- string interpolation `{var}` (strict, with escaping via `{{` / `}}`)
  across workflow strings: params/description/condition/id/depends_on (+ dynamic attrs)
- interleaving expansion for consecutive steps sharing the same loop.group
- preserving WorkflowStep fields and dynamic attributes
"""

import dataclasses
import itertools
import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.application.workflows.base import WorkflowStep

logger = logging.getLogger(__name__)


class LoopExpander:
    """Expands WorkflowStep loops and applies `{var}` interpolation."""

    _PLACEHOLDER_PATTERN = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")
    _ESC_LBRACE = "__LOOP_EXPANDER_LBRACE__"
    _ESC_RBRACE = "__LOOP_EXPANDER_RBRACE__"

    def __init__(self, max_expanded_steps: int = 2000):
        self._max_expanded_steps = max_expanded_steps
        self._evaluator = UnifiedEvaluator()
        self._step_field_names = {f.name for f in dataclasses.fields(WorkflowStep)}

    def expand(self, steps: List[WorkflowStep], context: Dict[str, Any]) -> List[WorkflowStep]:
        """Expand loops + interpolate `{var}`.

        - Steps without loop: interpolation only.
        - Steps with loop but no group: expanded step-by-step.
        - Consecutive steps sharing loop.group: expanded per-iteration (interleaved).
        """
        expanded: List[WorkflowStep] = []

        i = 0
        while i < len(steps):
            step = steps[i]
            loop_cfg = step.loop or {}
            group = loop_cfg.get("group")

            if group:
                block = self._consume_group_block(steps, i, group)
                expanded.extend(self._expand_group_block(block, context))
                i += len(block)
            else:
                expanded.extend(self._expand_step(step, context))
                i += 1

            if len(expanded) > self._max_expanded_steps:
                raise ValueError(
                    f"Loop expansion produced {len(expanded)} steps "
                    f"(limit={self._max_expanded_steps})."
                )

        return expanded

    def _consume_group_block(
        self, steps: Sequence[WorkflowStep], start_index: int, group: str
    ) -> List[WorkflowStep]:
        block: List[WorkflowStep] = []
        i = start_index
        while i < len(steps):
            loop_cfg = steps[i].loop or {}
            if loop_cfg.get("group") != group:
                break
            block.append(steps[i])
            i += 1
        return block

    def _expand_group_block(self, steps: Sequence[WorkflowStep], ctx: Dict[str, Any]) -> List[WorkflowStep]:
        if not steps:
            return []

        first_loop = steps[0].loop or {}
        group = first_loop.get("group")
        if not group:
            raise ValueError("Loop group block missing 'loop.group'.")

        iteration_space = dict(first_loop)
        iteration_space.pop("group", None)

        for step in steps:
            loop_cfg = step.loop or {}
            if loop_cfg.get("group") != group:
                raise ValueError("Loop group block contains steps with different loop.group values.")
            other_space = dict(loop_cfg)
            other_space.pop("group", None)
            if other_space != iteration_space:
                raise ValueError(
                    f"Loop group '{group}' has mismatched iteration space across steps: "
                    f"{iteration_space} vs {other_space}"
                )

        out: List[WorkflowStep] = []
        for iter_ctx in self._iter_loop_contexts(iteration_space, ctx):
            for step in steps:
                concrete = self._clone_step(step, loop=None)
                out.append(self._interpolate_step(concrete, iter_ctx))
        return out

    def _expand_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> List[WorkflowStep]:
        if step.loop is None:
            concrete = self._clone_step(step)
            return [self._interpolate_step(concrete, ctx)]

        out: List[WorkflowStep] = []
        for iter_ctx in self._iter_loop_contexts(step.loop, ctx):
            concrete = self._clone_step(step, loop=None)
            out.append(self._interpolate_step(concrete, iter_ctx))
        return out

    def _iter_loop_contexts(self, loop_cfg: Dict[str, Any], ctx: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        cfg = dict(loop_cfg)
        cfg.pop("group", None)

        # Single variable + range
        if "variable" in cfg and "range" in cfg:
            var = cfg["variable"]
            if not isinstance(var, str) or not var:
                raise ValueError(f"Invalid loop.variable: {var!r}")
            for v in self._resolve_range(cfg["range"], ctx):
                yield {**ctx, var: v}
            return

        # Single variable + values
        if "variable" in cfg and "values" in cfg:
            var = cfg["variable"]
            if not isinstance(var, str) or not var:
                raise ValueError(f"Invalid loop.variable: {var!r}")
            values = cfg["values"]
            if not isinstance(values, (list, tuple)):
                raise ValueError(f"Invalid loop.values (expected list): {values!r}")
            for v in values:
                yield {**ctx, var: v}
            return

        # Nested loops
        if "variables" in cfg and "ranges" in cfg:
            vars_ = cfg["variables"]
            ranges_spec = cfg["ranges"]
            if not isinstance(vars_, (list, tuple)) or not vars_:
                raise ValueError(f"Invalid loop.variables (expected non-empty list): {vars_!r}")
            if not isinstance(ranges_spec, (list, tuple)) or not ranges_spec:
                raise ValueError(f"Invalid loop.ranges (expected non-empty list): {ranges_spec!r}")
            if len(vars_) != len(ranges_spec):
                raise ValueError(
                    f"loop.variables and loop.ranges length mismatch: {len(vars_)} vs {len(ranges_spec)}"
                )

            vars_list = list(vars_)
            if any((not isinstance(v, str) or not v) for v in vars_list):
                raise ValueError(f"Invalid loop.variables values: {vars_list!r}")
            if len(set(vars_list)) != len(vars_list):
                raise ValueError(f"loop.variables must be unique: {vars_list!r}")

            resolved_ranges = [list(self._resolve_range(r, ctx)) for r in ranges_spec]
            for combo in itertools.product(*resolved_ranges):
                yield {**ctx, **dict(zip(vars_list, combo))}
            return

        raise ValueError(f"Invalid loop config: {loop_cfg}")

    def _resolve_range(self, range_spec: Any, ctx: Dict[str, Any]) -> range:
        # Static [start, end] (inclusive)
        if isinstance(range_spec, (list, tuple)) and len(range_spec) == 2:
            start, end = range_spec
            start_i = int(start)
            end_i = int(end)
            if end_i < start_i:
                raise ValueError(f"Invalid range: start={start_i} > end={end_i}")
            return range(start_i, end_i + 1)

        # "start..end" (inclusive) — start/end may be expressions
        if isinstance(range_spec, str) and ".." in range_spec:
            start_expr, end_expr = [p.strip() for p in range_spec.split("..", 1)]
            if not start_expr or not end_expr:
                raise ValueError(f"Invalid range spec: {range_spec!r}")
            start = self._eval_int(start_expr, ctx)
            end = self._eval_int(end_expr, ctx)
            if end < start:
                raise ValueError(f"Invalid range: start={start} > end={end}")
            return range(start, end + 1)

        raise ValueError(f"Invalid range spec: {range_spec!r}")

    def _eval_int(self, expr: str, ctx: Dict[str, Any]) -> int:
        self._evaluator.set_context(ctx)
        value = self._evaluator.evaluate_as_float(expr)
        rounded = int(round(value))
        if abs(value - float(rounded)) > 1e-9:
            raise ValueError(f"Range bound '{expr}' evaluated to non-integer: {value}")
        return rounded

    def _interpolate_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> WorkflowStep:
        step.params = self._interpolate_value(step.params, ctx)

        if step.description is not None:
            step.description = self._interpolate_string(step.description, ctx)

        if step.condition is not None:
            step.condition = self._interpolate_string(step.condition, ctx)

        if step.id is not None:
            step.id = self._interpolate_string(step.id, ctx)

        if step.depends_on:
            if not isinstance(step.depends_on, list):
                raise ValueError(f"depends_on must be a list, got: {type(step.depends_on).__name__}")
            step.depends_on = [self._interpolate_string(dep, ctx) for dep in step.depends_on]

        for attr_name, attr_value in self._iter_dynamic_attrs(step):
            if isinstance(attr_value, (str, list, dict)):
                setattr(step, attr_name, self._interpolate_value(attr_value, ctx))

        return step

    def _interpolate_value(self, value: Any, ctx: Dict[str, Any]) -> Any:
        if isinstance(value, str):
            return self._interpolate_string(value, ctx)
        if isinstance(value, list):
            return [self._interpolate_value(v, ctx) for v in value]
        if isinstance(value, tuple):
            return tuple(self._interpolate_value(v, ctx) for v in value)
        if isinstance(value, dict):
            return {k: self._interpolate_value(v, ctx) for k, v in value.items()}
        return value

    def _interpolate_string(self, value: str, ctx: Dict[str, Any]) -> str:
        if "{" not in value and "}" not in value:
            return value

        escaped = value.replace("{{", self._ESC_LBRACE).replace("}}", self._ESC_RBRACE)

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in ctx:
                raise ValueError(f"Unknown placeholder '{{{name}}}' in '{value}'")
            return str(ctx[name])

        interpolated = self._PLACEHOLDER_PATTERN.sub(replace, escaped)
        return interpolated.replace(self._ESC_LBRACE, "{").replace(self._ESC_RBRACE, "}")

    def _clone_step(self, step: WorkflowStep, **overrides: Any) -> WorkflowStep:
        data: Dict[str, Any] = {name: getattr(step, name) for name in self._step_field_names}

        # Shallow copy mutable containers to avoid accidental aliasing
        data["params"] = dict(data.get("params") or {})
        data["tags"] = list(data.get("tags") or [])
        data["depends_on"] = list(data.get("depends_on") or [])
        if data.get("loop") is not None:
            data["loop"] = dict(data["loop"])

        data.update(overrides)

        cloned = WorkflowStep(**data)

        for attr_name, attr_value in self._iter_dynamic_attrs(step):
            setattr(cloned, attr_name, attr_value)

        return cloned

    def _iter_dynamic_attrs(self, step: WorkflowStep) -> Iterable[tuple[str, Any]]:
        for name, value in step.__dict__.items():
            if name.startswith("_"):
                continue
            if name in self._step_field_names:
                continue
            yield name, value

