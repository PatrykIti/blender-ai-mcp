# 352. TASK-168 runtime confinement reopen and closeout

Date: 2026-05-15

## Summary

Reopened `TASK-168` after an implementation audit showed that the task family
was closed in docs before the subtask-defined runtime contract was fully
landed in code.

The reopen/repair pass completed the missing confinement slices:

- added one explicit guided action-policy seam on the existing owner path so
  guided mutators are evaluated before dispatch under one runtime decision
  point
- hardened `checkpoint_iterate` to fail closed on new mutating build work by
  default, while still allowing the bounded missing-role exception for the
  active guided workset
- rejected invalid guided roles such as `guided_role="eye_pair"` as runtime
  errors instead of letting them drift through creature sessions
- persisted the last fail-closed guided action block in session state and
  projected it back onto `router_get_status().reference_orchestrator_feedback`
  so external controllers receive typed unblock guidance on the existing
  public seam
- added a runtime-owned `resolve_active_compare_scope(...)` path for lazy
  compare callers, preferring gate-blocker clusters, then last affected
  objects, then the active guided workset before falling back to whole-scene
  scope

## Runtime Surface

- guided action-policy hardening lives on the existing owner seams:
  - `server/adapters/mcp/router_helper.py`
  - `server/adapters/mcp/guided_naming_policy.py`
  - `server/adapters/mcp/session_capabilities_runtime_glue.py`
  - `server/adapters/mcp/session_capabilities_state.py`
  - `server/adapters/mcp/session_capabilities_bootstrap.py`
- deny-path feedback projection and lazy compare-scope routing live on:
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/areas/reference_feedback.py`
  - `server/adapters/mcp/areas/reference.py`

## Task And Board State

- moved `TASK-168` back to `In Progress` during the repair pass so the board
  matched the real code state
- closed `TASK-168` and its nested `TASK-168-*` execution slices again after
  the runtime contract, targeted proof lanes, and repo-standard validation all
  went green

## Validation

- focused owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
    - result: `47 passed`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
    - result: `131 passed`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
    - result: `20 passed`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
    - result: `26 passed`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/router/application/test_workflow_triggerer.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
    - result: `82 passed`
- additional targeted regression pass:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/router/application/test_router_contracts.py -q`
  - result: `151 passed`
- broad repo unit proof:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - result: `3438 passed`
- repo-wide quality gates:
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result: passed
- repo-supported Blender E2E runner:
  - `poetry run python scripts/run_e2e_tests.py`
  - result: `477 passed, 3 skipped`
