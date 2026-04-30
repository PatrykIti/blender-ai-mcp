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
| `server/adapters/mcp/session_capabilities.py` | Add active gate state, versioning, stale markers, blockers, and centralized gate dirtying metadata |
| `server/adapters/mcp/contracts/guided_flow.py` | Represent spatial refresh cadence, stale-but-continuable state, and hard refresh blockers |
| `server/adapters/mcp/contracts/reference.py` | Add strict response fields to `ReferenceCompareStageCheckpointResponseContract` and `ReferenceIterateStageCheckpointResponseContract`; current `MCPContract` payloads forbid undeclared extras |
| `server/adapters/mcp/transforms/visibility_policy.py` | Expose tool families based on unresolved gates |
| `server/adapters/mcp/discovery/search_documents.py` | Bias search by gate type and correction family |
| `server/adapters/mcp/areas/reference.py` | Include gate state and optional reference-understanding/gate-proposal summaries in compare/iterate responses |
| `server/adapters/mcp/vision/` | Provide cached perception evidence refs at stage checkpoints without forcing external calls after every mutation |
| `server/adapters/mcp/router_helper.py` | Extend routed/finalizer dirtying so mutating tools invalidate gates while allowing same-step continuation when policy permits it |
| `server/adapters/mcp/areas/modeling.py` | Add explicit mutation metadata only when centralized dirtying cannot infer affected gate scopes |
| `server/adapters/mcp/areas/mesh.py` | Add explicit mutation metadata only when centralized dirtying cannot infer affected gate scopes |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | Cadence contract and stale-versus-blocking state tests |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py` | Checkpoint/iterate response contract parity for new gate fields |
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
  a future bounded pre-build reference-understanding pass, or reuse one once the
  reference-understanding/gate-proposal contract has shipped, to propose a first
  gate plan and construction path. That pass must not mark gates complete.
- Final completion must fail closed when required gates are unresolved.

## Runtime / Security Contract Notes

- Visibility level: gate state should shape existing `llm-guided` visibility
  and reference checkpoint responses rather than creating a second catalog
  authority.
- Read-only vs mutating behavior: checkpoint and gate-summary responses are
  read-only; existing modeling, mesh, scene, and macro tools remain the only
  mutating Blender paths and must mark relevant gates stale.
- Streamable HTTP / stdio: guided state updates, visibility refreshes, and
  spatial/gate finalizers must complete through the active request path so
  `list_tools()` and checkpoint responses observe the same session state.
- External providers: pre-build reference understanding is optional and bounded
  by the existing vision runtime config, provider-key redaction, token/image
  limits, and disabled/unavailable statuses.
- Completion safety: final completion must fail closed when required gates are
  `pending`, `blocked`, `failed`, or `stale`, even if the LLM summary says the
  build is complete.

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

0. after `router_set_goal` and reference attach, once the future
   reference-understanding contract exists, produce or reuse
   `reference_understanding` to propose required parts, expected style,
   construction path, and gate plan
1. create `Body`, `Head`, and `Tail` primary masses
2. run the spatial triad plus reference checkpoint
3. repair `Head -> Body` and `Tail -> Body` seams
4. create `Snout`, `Ear_L`, `Ear_R`, `Eye_L`, `Eye_R`, forelegs, and hindlegs
5. run the spatial triad plus reference/vision checkpoint
6. repair unresolved required gates
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
    checkpoint_loop_disposition = "continue_build"
    updated_flow_state = state.guided_flow_state

    if gate_summary.has_required_blockers:
        checkpoint_loop_disposition = "inspect_validate"
        updated_flow_state = replace_guided_flow_fields(
            updated_flow_state,
            next_actions=gate_summary.next_actions,
            allowed_families=visibility_for_gate_blockers(gate_summary),
        )

    return response.with_gate_summary(
        gate_summary,
        guided_flow_state=updated_flow_state,
        loop_disposition=checkpoint_loop_disposition,
    )


def mark_gates_stale_after_mutation(gate_plan, mutation):
    return gate_plan.with_stale_scopes(
        objects=mutation.objects,
        reason=mutation.tool_name,
    )


def after_mutation(current, mutation):
    updated_gate_plan = mark_gates_stale_after_mutation(current.gate_plan, mutation)
    updated_flow_state = mark_guided_spatial_state_stale_for_mutation(
        current.guided_flow_state,
        mutation,
    )

    if crosses_gate_boundary(updated_gate_plan, mutation):
        updated_flow_state = replace_guided_flow_fields(
            updated_flow_state,
            spatial_refresh_required=True,
            next_actions=["refresh_spatial_context"],
        )
    elif next_action_depends_on_stale_pair_truth(updated_gate_plan, mutation):
        updated_flow_state = replace_guided_flow_fields(
            updated_flow_state,
            spatial_refresh_required=True,
            next_actions=["verify_active_pair_gate"],
        )
    else:
        updated_flow_state = replace_guided_flow_fields(
            updated_flow_state,
            spatial_refresh_required=False,
            next_actions=continue_current_role_batch(updated_flow_state),
        )

    return replace(
        current,
        gate_plan=updated_gate_plan,
        guided_flow_state=updated_flow_state,
    )
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

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when guided gate state, visibility shaping,
  or completion-blocking behavior ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -v`
- `python3 scripts/run_e2e_tests.py` for any implementation slice that changes
  Streamable HTTP/stdio guided state, Blender scene state, or final completion
  blocking.

## Acceptance Criteria

- Gate state is visible in guided checkpoint payloads.
- Required gate blockers drive next actions and visibility.
- Scene mutations invalidate affected gate statuses.
- Completion cannot bypass unresolved required gates.
