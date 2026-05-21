# TASK-171-04: Compact Repair Plan Projection On Reference Orchestrator Feedback

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Extend compact `reference_orchestrator_feedback` with one bounded actionable repair-plan surface so the controller can receive the top repair candidate with typed `arguments_hint` instead of only flattened tool-name lists and prose `correction_focus`.
**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/router.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
**Acceptance Criteria:**
- compact feedback can expose one bounded repair candidate with tool name, reason, and typed `arguments_hint`
- the top candidate can be sourced from existing truth macro candidates or repair-planner tool candidates instead of inventing a second planning path
- compact mode stays compact; full truth/planner payloads remain additive/rich surfaces rather than being duplicated wholesale

## Implementation Notes

- the current compact feedback contract is already broader than just three
  fields; it still carries status/family/gate/checkpoint/evidence/uncertainty
  data
- the actual gap on this seam is narrower:
  - actionable repair-tool selection collapses into flattened tool-name strings
  - the compact surface does not preserve the top tool + `arguments_hint`
    payload that already exists on heavier truth/planner seams
- richer actionable hints already exist on heavier seams:
  - truth macro candidates
  - planner blockers / required support tools
  - refinement handoff candidates
- the new compact field should reuse those existing sources and rank them, not
  regenerate separate macro advice in the feedback builder
- prefer one small additive contract such as a compact `recommended_repair`
  object over unstructured prose

## Pseudocode

```python
repair_candidate = rank_compact_repairs(
    truth_macro_candidates=compare_result.correction_candidates,
    planner_tools=planner_summary.required_support_tools,
)[:1]

feedback = ReferenceOrchestratorFeedbackContract(
    ...,
    recommended_repair=repair_candidate[0] if repair_candidate else None,
)
```

## Runtime / Security Contract Notes

- keep the compact contract machine-readable and bounded; do not dump the full
  nested truth bundle or planner detail into normal compact flows
- `arguments_hint` must reuse already supported public tool arguments; do not
  invent hidden macro-only parameters on the compact surface
- preserve backward compatibility where possible by making the new field
  additive rather than replacing the existing compact keys

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`

## Validation Category

- compact contract and repair-handoff proof
