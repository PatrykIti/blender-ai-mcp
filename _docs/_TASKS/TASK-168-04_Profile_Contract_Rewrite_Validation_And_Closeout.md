# TASK-168-04: Profile Contract Rewrite, Validation, And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Objective:** Close the confinement umbrella only after the `llm-guided` contract, prompt assets, docs, board/changelog state, and proof lanes confirm that external controllers are held inside the current profile boundaries.
**Repository Touchpoints:** `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_PROMPTS/README.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_ROUTER/README.md`, `_docs/_TASKS/README.md`, `_docs/_TASKS/TASK-168*.md`, `_docs/_CHANGELOG/README.md`, new `_docs/_CHANGELOG/*`, `tests/unit/`, `tests/e2e/integration/`, `tests/e2e/router/`, `tests/e2e/vision/`
**Acceptance Criteria:**
- docs explain the hard profile contract and the compact feedback semantics consistently
- the board and changelog state match the final implementation status
- the final proof includes both focused controller-regression lanes and the repo-standard broad validation bundle

## Implementation Notes

- do not close this family on prompt edits alone; runtime enforcement and proof must both be real
- use squirrel/controller regressions as explicit proof surfaces:
  - no false workflow heuristic under guided manual no-match
  - no late/stale compare payload contract failures
  - no `guided_role="eye_pair"` guided-role drift
  - no continued free-form mutation through `checkpoint_iterate` without allowed exception

## Runtime / Security Contract Notes

- docs must make it clear that prompt assets support the runtime contract; they do not replace it
- examples must not teach legacy payload fields or invalid role patterns

## Tests To Add/Update

- final closeout must inherit the focused owner-lane commands from:
  - `TASK-168-01`
  - `TASK-168-02`
  - `TASK-168-02-01`
  - `TASK-168-02-02`
  - `TASK-168-03`
- plus the broad repo bundle:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - `poetry run python scripts/run_e2e_tests.py`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_ROUTER/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_TASKS/TASK-168*.md`
- `_docs/_CHANGELOG/README.md`
- new `_docs/_CHANGELOG/*`

## Changelog Impact

- add the historical `_docs/_CHANGELOG/*` entry when the family is ready to close

## Status / Board Update

- remains nested under `TASK-168`
- owns the final closeout bookkeeping for this confinement umbrella

## Validation Commands

- `git diff --check`
- focused owner-lane unit tests after implementation:
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_handler_parameters.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_workflow_triggerer.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_supervisor_router.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- repo-standard proof bundle:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- final repo-standard proof bundle for a runtime/prompt confinement family
- `git diff --check`
