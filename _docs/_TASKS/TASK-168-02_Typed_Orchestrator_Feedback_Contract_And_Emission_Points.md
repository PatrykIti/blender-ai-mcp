# TASK-168-02: Typed Orchestrator Feedback Contract And Emission Points

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Add one compact, machine-readable feedback contract on the existing guided public seams so external controllers are told exactly what to do now, not do now, and what will fail now.
**Repository Touchpoints:** `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/scene_guided_runtime.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/context_utils.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`
**Acceptance Criteria:**
- existing guided public responses can carry one short typed contract such as `orchestrator_feedback`
- the contract includes at minimum:
  - `do_now`
  - `dont_do`
  - `wont_work`
  - `why_blocked`
  - `unblock_by`
- the same contract can point the controller at the current active fragment,
  compare scope, or packet/gist handle instead of forcing whole-response reads
- the server emits this feedback at the critical moments:
  - after `router_set_goal(...)`
  - after guided state-step transitions
  - after deny/rewrite/fail-closed responses
  - after staged compare / iterate
- the feedback stays compact and does not require prose parsing to recover the next step

## Implementation Notes

- keep the field short and deterministic; do not turn it into a second essay surface
- build the feedback from runtime state and policy decisions, not from prompt text
- emission points should be explicit and few:
  - router goal/set status
  - reference compare / iterate
  - guided spatial gate refresh / deny
  - pre-dispatch shield denials
- squirrel regression anchor examples to encode:
  - `checkpoint_iterate` -> do compare/support now, do not create new parts
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
feedback = OrchestratorFeedback(
    phase=current_phase,
    do_now=["reference_iterate_stage_checkpoint(checkpoint_label='legs_stage')"],
    dont_do=["modeling_create_primitive", "guided_role='eye_pair'"],
    wont_work=["reference_compare_stage_checkpoint(label=..., notes=...)"],
    why_blocked="checkpoint_iterate is active; compare/support loop owns the next move",
    unblock_by=["run reference_iterate_stage_checkpoint(...)", "or finish required_checks"],
)
```

## Runtime / Security Contract Notes

- feedback must reflect the live runtime truth, not stale historical hints
- compact structured feedback outranks controller-local memory and stale prompt assumptions
- do not expose hidden/internal tool ids in `do_now`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`

## Validation Category

- focused unit / integration contract tests
- `git diff --check`
