# TASK-168-02: Typed Orchestrator Feedback Contract And Emission Points

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Extend the existing `reference_orchestrator_feedback` public seam so external controllers receive explicit next-step guidance without inventing a parallel public feedback contract or replacing the current live vocabulary.
**Repository Touchpoints:** `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/scene_guided_runtime.py`, `server/adapters/mcp/guided_mode.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:**
- existing guided public responses can carry one short typed
  `reference_orchestrator_feedback` contract without introducing a second
  public field or removing the current live names
- the contract stays grounded in the shipped owner seam, including fields such
  as:
  - `blocking_reasons`
  - `next_actions`
  - `next_checkpoint_tool`
  - `recommended_support_tools`
  - `uncertainty_notes`
  - `correction_focus`
  - `loop_disposition`
- if richer controller-facing aliases are still needed, they land as
  additive/versioned fields rather than replacing the current public
  vocabulary
- the same contract can point the controller at the current active fragment,
  compare scope, or correction focus instead of forcing whole-response reads
- the server emits this feedback at the critical moments:
  - on `reference_images(...)` attach/list/remove/clear when guided/reference
    state changes
  - after `router_set_goal(...)`
  - after `router_get_status(...)` refreshes an active guided/reference
    session
  - after deny/rewrite/fail-closed responses
  - after staged compare / iterate
- the feedback stays compact and does not require prose parsing to recover the next step

## Implementation Notes

- build on the current `reference_orchestrator_feedback` owner seam instead of
  introducing a second public `orchestrator_feedback` field
- preserve the current typed vocabulary and transport shape; if new
  controller-facing aliases are needed, ship them additively/versioned instead
  of replacing the live field names
- keep the field short and deterministic; do not turn it into a second essay surface
- build the feedback from runtime state and policy decisions, not from prompt text
- emission points should align with the already-shipped guided/reference
  surfaces:
  - `reference_images(...)`
  - `router_set_goal(...)`
  - `router_get_status(...)`
  - reference compare / iterate
  - guided spatial gate refresh / deny
  - pre-dispatch shield denials
- squirrel regression anchor examples to encode:
  - `checkpoint_iterate` -> do compare/support now by default; do not create
    new semantic parts unless the live guided state still exposes the
    active-workset / required-role exception
  - `guided_role="eye_pair"` -> will not work; `eye_pair` is a quality-gate target, not a guided role
  - staged compare legacy args -> use `checkpoint_label`, not `label` / `notes`
- this task intentionally does **not** stop at one small response field. It
  should coordinate with:
  - [TASK-168-02-01](./TASK-168-02-01_Active_Workset_Compare_Scope_And_Coarse_To_Fine_Iteration.md)
  - [TASK-168-02-02](./TASK-168-02-02_Selective_Disclosure_Minimal_Control_Payloads_And_Gist_Followups.md)
  so the controller gets both the *right scope* and the *right amount of detail*

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-168-02-01](./TASK-168-02-01_Active_Workset_Compare_Scope_And_Coarse_To_Fine_Iteration.md) | Make the feedback point to the active workset/fragment and current compare scope |
| 2 | [TASK-168-02-02](./TASK-168-02-02_Selective_Disclosure_Minimal_Control_Payloads_And_Gist_Followups.md) | Make compact outputs truly compact and keep heavy compare detail out of the default controller path |

## Pseudocode

```python
feedback = ReferenceOrchestratorFeedback(
    current_guided_step=current_step,
    selected_family="modeling_mesh",
    blocking_reasons=["checkpoint_iterate is active; compare/support loop owns the next move"],
    next_actions=["run_reference_iterate_stage_checkpoint"],
    next_checkpoint_tool="reference_iterate_stage_checkpoint",
    recommended_support_tools=["scene_view_diagnostics"],
    uncertainty_notes=["`eye_pair` is a quality-gate target, not a guided role"],
    correction_focus=["legs_stage"],
)
```

## Runtime / Security Contract Notes

- feedback must reflect the live runtime truth, not stale historical hints
- compact structured feedback outranks controller-local memory and stale prompt assumptions
- do not expose hidden/internal tool ids in `next_actions` or
  `recommended_support_tools`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)

## Status / Board Update

- remains nested under `TASK-168`
- should close only after the shield slice plus both output-shaping leaves can
  supply real block/next-step data on a bounded fragment scope

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- focused Blender-backed owner lanes to cover under the repo-supported runner:
  - `tests/e2e/integration/test_guided_gate_state_transport.py`
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused unit / contract tests plus repo-supported Blender E2E proof
- `git diff --check`
