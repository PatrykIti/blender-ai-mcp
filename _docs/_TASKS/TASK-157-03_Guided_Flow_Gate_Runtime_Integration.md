# TASK-157-03: Guided Flow Gate Runtime Integration

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Guided Runtime / Flow Integration
**Estimated Effort:** Large

## Objective

Integrate gate plans and gate status into `llm-guided` runtime flow so active
gates drive next actions, visibility, checkpoint responses, and completion
blocking.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/session_capabilities.py` | Add active gate state, versioning, stale markers, blockers |
| `server/adapters/mcp/transforms/visibility_policy.py` | Expose tool families based on unresolved gates |
| `server/adapters/mcp/discovery/search_documents.py` | Bias search by gate type and correction family |
| `server/adapters/mcp/areas/reference.py` | Include gate state in compare/iterate responses |
| `server/adapters/mcp/areas/modeling.py` | Mark relevant gates stale after mutating tool calls |
| `server/adapters/mcp/areas/mesh.py` | Mark relevant gates stale after mesh edits |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Gate-driven visibility tests |
| `tests/unit/adapters/mcp/test_reference_images.py` | Checkpoint payload and completion-blocker tests |

## Implementation Notes

- Gate state should sit beside guided flow state, not replace it.
- Existing `allowed_roles`, `missing_roles`, and `required_checks` should remain
  valid; gates add quality/completion semantics above them.
- Mutating tools should mark affected gates stale when the scene changes.
- Checkpoint responses should include:
  - `active_gate_plan`
  - `gate_statuses`
  - `completion_blockers`
  - `next_gate_actions`
  - `recommended_bounded_tools`
- Final completion must fail closed when required gates are unresolved.

## Pseudocode

```python
def build_guided_response(state):
    gate_summary = summarize_gate_plan(state.gate_plan)

    if gate_summary.has_required_blockers:
        state.loop_disposition = "inspect_validate"
        state.next_actions = gate_summary.next_actions
        state.visible_families = visibility_for_gate_blockers(gate_summary)

    return response.with_gate_summary(gate_summary)


def mark_gates_stale_after_mutation(state, mutation):
    for gate in state.gate_plan.gates:
        if gate.scope_intersects(mutation.objects):
            gate.status = "stale"
            gate.stale_reason = mutation.tool_name
```

## Tests To Add/Update

- Mutating body/head/tail tools mark related gates stale.
- Required failed gate sets `loop_disposition="inspect_validate"`.
- Required missing gate blocks final completion.
- Unresolved `attachment_seam` exposes macro repair tools, not broad sculpt.
- `shape_profile` gate can expose mesh/modeling refinement tools only after
  required seam gates are stable.

## E2E Tests

- Covered by TASK-157-04 cross-domain E2E harness.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- Gate state is visible in guided checkpoint payloads.
- Required gate blockers drive next actions and visibility.
- Scene mutations invalidate affected gate statuses.
- Completion cannot bypass unresolved required gates.
