# TASK-157-03: Guided Flow Gate Runtime Integration

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Guided Runtime / Flow Integration
**Estimated Effort:** Large

## Objective

Integrate gate plans and gate status into `llm-guided` runtime flow so active
gates drive next actions, visibility, checkpoint responses, and completion
blocking, while spatial and vision refreshes happen at meaningful stage and
gate boundaries instead of after every single safe in-stage mutation.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/session_capabilities.py` | Add active gate state, versioning, stale markers, blockers |
| `server/adapters/mcp/contracts/guided_flow.py` | Represent spatial refresh cadence, stale-but-continuable state, and hard refresh blockers |
| `server/adapters/mcp/transforms/visibility_policy.py` | Expose tool families based on unresolved gates |
| `server/adapters/mcp/discovery/search_documents.py` | Bias search by gate type and correction family |
| `server/adapters/mcp/areas/reference.py` | Include gate state and optional reference-understanding/gate-proposal summaries in compare/iterate responses |
| `server/adapters/mcp/vision/` | Provide cached perception evidence refs at stage checkpoints without forcing external calls after every mutation |
| `server/adapters/mcp/areas/modeling.py` | Mark relevant gates stale after mutating tool calls |
| `server/adapters/mcp/areas/mesh.py` | Mark relevant gates stale after mesh edits |
| `server/adapters/mcp/router_helper.py` | Preserve mutation dirtying while allowing same-step continuation when policy permits it |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | Cadence contract and stale-versus-blocking state tests |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Gate-driven visibility tests |
| `tests/unit/adapters/mcp/test_reference_images.py` | Checkpoint payload and completion-blocker tests |

## Implementation Notes

- Gate state should sit beside guided flow state, not replace it.
- Existing `allowed_roles`, `missing_roles`, and `required_checks` should remain
  valid; gates add quality/completion semantics above them.
- Mutating tools should mark affected gates stale when the scene changes.
- Spatial staleness should not automatically hard-block every next mutation:
  the runtime should distinguish stale facts from a required refresh boundary.
- Checkpoint responses should include:
  - optional `reference_understanding` summary when available
  - `active_gate_plan`
  - `gate_statuses`
  - `completion_blockers`
  - `next_gate_actions`
  - `recommended_bounded_tools`
- When references are attached before any scene exists, the guided loop may run
  or reuse a bounded pre-build reference-understanding pass to propose a first
  gate plan and construction path. That pass must not mark gates complete.
- Final completion must fail closed when required gates are unresolved.

## Spatial Refresh Cadence Policy

`TASK-151` deliberately made spatial facts freshness-bound and re-armable.
This task must add the next layer: stale spatial facts should block decisions
that depend on spatial truth, but they should not force a full spatial triad
after every safe in-stage creation or bounded transform.

Use this cadence as the first required policy:

| Event | Required Behavior |
|-------|-------------------|
| Safe mutation inside the same allowed role batch | Mark spatial/gate facts stale, but keep the current build window open when no gate boundary is crossed |
| End of a stage, such as primary masses, tail, secondary parts, refinement, or final | Require spatial refresh and the relevant reference/vision checkpoint before advancing |
| Macro repair that changes an attachment/support relation | Require a local seam re-check, and require broader refresh before leaving the repair gate |
| Transition to a different unresolved gate | Require refresh if the next gate depends on stale spatial facts |
| Final completion | Require fresh spatial and gate evidence; stale required gates block completion |
| Pair-dependent action, such as `Head -> Body` or `TailRoot -> Body` seating | Require local pair truth when that pair verdict is the input to the next action |

The target runtime state should support three distinct states:

- `spatial_state_stale=true`: scene changed since the last check.
- `spatial_refresh_required=false`: same-step continuation is still allowed.
- `spatial_refresh_required=true`: the next action crosses a boundary that
  depends on fresh spatial truth.

For a squirrel-like creature, the intended default cadence is:

0. after `router_set_goal` and reference attach, produce or reuse
   `reference_understanding` to propose required parts, expected style,
   construction path, and gate plan
1. create `Body`, `Head`, and `Tail` primary masses
2. run the spatial triad plus reference checkpoint
3. repair `Head -> Body` and `Tail -> Body` seams
4. create `Snout`, `Ear_L`, `Ear_R`, `Eye_L`, `Eye_R`, forelegs, and hindlegs
5. run the spatial triad plus reference/vision checkpoint
6. repair failed required gates
7. run bounded low-poly form refinement
8. run final spatial and reference/vision checkpoint

This cadence should remain generic. Domain templates may name different stages,
but the server-owned rule is the same: batch-local mutation may continue with
stale facts, while gate transitions, seam repairs, and final completion require
fresh evidence.

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


def after_mutation(state, mutation):
    mark_gates_stale_after_mutation(state, mutation)
    state.spatial_state_stale = True

    if crosses_gate_boundary(state, mutation):
        state.spatial_refresh_required = True
        state.next_actions = ["refresh_spatial_context"]
    elif next_action_depends_on_stale_pair_truth(state, mutation):
        state.spatial_refresh_required = True
        state.next_actions = ["verify_active_pair_gate"]
    else:
        state.spatial_refresh_required = False
        state.next_actions = continue_current_role_batch(state)
```

## Tests To Add/Update

- Mutating body/head/tail tools mark related gates stale.
- Same-step safe mutations mark spatial facts stale without immediately
  blocking the remaining allowed roles in that batch.
- Stage boundaries promote stale spatial facts to
  `spatial_refresh_required=true`.
- Pair-dependent repair or placement gates require local pair truth before the
  next action consumes that verdict.
- Required failed gate sets `loop_disposition="inspect_validate"`.
- Required missing gate blocks final completion.
- Pre-build reference-understanding can seed a gate plan and construction
  strategy but cannot set any gate to `passed`.
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
