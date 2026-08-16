# TASK-145-02-01: Sculpt Handoff Contract and Local Target Semantics

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md)

## Objective

Define a sculpt handoff contract that makes explicit:

- selected family
- target object / local scope
- region or local-form reason
- bounded recommended tools and argument hints

instead of relying on the current minimal `object_name`-only handoff shape.

## Implementation Notes

- Extend or compose `ReferenceRefinementHandoffContract` before adding a new
  standalone sculpt-handoff family.
- Keep `_build_refinement_handoff(...)` aligned with the contract fields:
  target object, local scope, region/local-form reason, blockers, and bounded
  recommended tools.
- Argument hints must remain compatible with actual sculpt tool signatures in
  `server/adapters/mcp/areas/sculpt.py`; do not invent hidden arguments for the
  model-facing handoff.
- The handoff should describe recommendation readiness, not TASK-157 gate
  completion.
- Pseudocode helper names such as `handoff_without_sculpt(...)`,
  `sculpt_handoff(...)`, `planner_result.target_scope`, and
  `derive_sculpt_arguments(...)` are proposed implementation shapes. They must
  either be added explicitly or folded into the current
  `_build_refinement_handoff(...)` path.

## Runtime / Security Contract

- Visibility level: this leaf is contract-local by default. It must not make any
  `sculpt_*` tool visible on `llm-guided` by itself.
- Behavior: the handoff is read-only recommendation metadata. Actual
  `sculpt_*` calls remain mutating and must stay behind existing guided
  visibility and execution gates until TASK-145-02-03 / TASK-145-03-01 wire the
  bounded sculpt subset safely.
- Session assumptions: stdio and Streamable HTTP clients should receive the same
  handoff fields through the existing reference compare / iterate responses; do
  not add a separate planner-state persistence path.
- Validation: reject or omit unsupported sculpt tools and unsupported argument
  hints instead of inventing hidden model-facing parameters.
- Side effects and recovery: this leaf must not change Blender mode, selection,
  geometry, or native MCP visibility unless a later implementation explicitly
  promotes that behavior and covers it with the guided execution gate.
- Limits and redaction: keep handoff payloads compact and avoid embedding raw
  debug payloads, provider secrets, local file contents, or unbounded image data.

## Pseudocode

```python
if route.selected_family != "sculpt_region":
    return handoff_without_sculpt(route, blockers=planner_result.blockers)

return sculpt_handoff(
    target_scope=planner_result.target_scope,
    local_reason=planner_result.local_form_reason,
    recommended_tools=bounded_sculpt_region_tools,
    arguments_hint=derive_sculpt_arguments(planner_result.target_scope),
)
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Validation Category

- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`

## Acceptance Criteria

- the sculpt handoff clearly identifies the object or narrow local target that
  sculpt would act on
- the handoff includes an explicit local-form or region reason
- recommended tools remain bounded to the deterministic sculpt-region subset
- argument hints remain compatible with actual sculpt tool shapes in
  `server/adapters/mcp/areas/sculpt.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- covered by the parent TASK-145 changelog entry:
  [_docs/_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md](../_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md)

## Completion Summary

Closed by extending `ReferenceRefinementHandoffContract` with target object,
target scope, local-form reason, handoff state, blockers, eligible sculpt
tools, and compatibility-safe `object_name` argument hints for deterministic
region tools.

## Status / Board Update

- closed under TASK-145-02
