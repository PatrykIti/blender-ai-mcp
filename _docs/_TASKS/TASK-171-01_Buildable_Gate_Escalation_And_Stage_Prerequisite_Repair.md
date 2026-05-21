# TASK-171-01: Buildable Gate Escalation And Stage Exit Prerequisite Repair

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Make creature stage-exit and iterate escalation consistent so `tail_mass` and `snout_mass` cannot silently carry forward past their intended wave-exit criteria, while buildable gate-only blockers such as `eye_pair` stay on a bounded build path until hard inspection authority is actually needed.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_context_bridge.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`
**Acceptance Criteria:**
- the runtime makes one explicit decision about `tail_mass` wave-exit ownership and keeps flow, prompt docs, and tests aligned with that decision
- the runtime makes one explicit decision about `snout_mass` wave-exit ownership and keeps flow, prompt docs, and tests aligned with that decision
- gate-only buildable blockers such as `eye_pair` can keep `loop_disposition="continue_build"` when the runtime still has a valid bounded create/repair lane
- hard seam/support/truth blockers, repeated stagnation, and explicit inspect-only escalations still transition into `inspect_validate`

## Implementation Notes

- the current runtime already exposes the intended high-level creature stage
  order on prompt and `allowed_roles` surfaces:
  - `body_core + head_mass + tail_mass` are already primary-wave roles
  - `snout_mass + ear_pair + foreleg_pair + hindleg_pair` are already
    secondary-wave roles
- the still-open mismatch is narrower:
  - stage-exit / build-hold decisions still treat `tail_mass` and
    `snout_mass` as late carry-forward roles rather than explicit wave-exit
    prerequisites
  - gate-only buildable blockers such as `eye_pair` still do not participate in
    the current `missing_roles`-based hold-in-build path
- `eye_pair` is intentionally gate-only, not a guided role; do not “fix” this
  by silently making it visible in `allowed_roles`
- the actual early-escalation issue is that build-hold logic currently keys off
  `missing_roles`, while gate-only buildable blockers never appear there
- the task must pick one explicit bounded policy for buildable gate blockers:
  - either extend the hold-in-build decision to include buildable
    `required_part` blockers with live create/repair recommendations
  - or add another typed blocker-classification seam that distinguishes
    buildable missing-part blockers from hard inspect-only blockers
- preserve the existing inspect/measure/assert authority line for:
  - attachment seam failures
  - support-contact failures
  - truth-only escalation
  - repeated stagnation

## Pseudocode

```python
missing_primary = required_primary_exit_roles(contract) - completed_roles(contract)
missing_secondary = required_secondary_exit_roles(contract) - completed_roles(contract)
buildable_part_blockers = [
    blocker
    for blocker in completion_blockers
    if blocker.gate_type == "required_part" and blocker_has_build_lane(blocker)
]

if current_step == "create_primary_masses" and missing_primary:
    stay_in_build()
elif current_step == "place_secondary_parts" and missing_secondary:
    stay_in_build()
elif buildable_part_blockers and not hard_truth_or_seam_blocker and not stagnating:
    loop_disposition = "continue_build"
else:
    loop_disposition = existing_escalation_policy(...)
```

## Runtime / Security Contract Notes

- `eye_pair` remains gate-only unless a separate public-surface task explicitly
  changes that decision
- `inspect_validate` must remain authoritative for hard truth/seam/support
  blockers; this slice only narrows premature escalation
- do not widen hidden build tools globally; visibility changes must follow the
  same bounded guided/family rules already in the repo

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- guided stage machine and compact iterate policy proof
