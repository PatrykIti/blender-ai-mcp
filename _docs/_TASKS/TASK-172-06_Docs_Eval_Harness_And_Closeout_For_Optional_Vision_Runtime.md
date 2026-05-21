# TASK-172-06: Docs, Eval Harness, And Closeout For Optional Vision Runtime

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Close the `TASK-172` family with docs, eval/harness coverage, negative coverage for unavailable optional adapters, and board/changelog synchronization.
**Repository Touchpoints:** `scripts/vision_harness.py`, `tests/unit/scripts/test_script_tooling.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/`, `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, `_docs/_CHANGELOG/*`
**Acceptance Criteria:**
- docs describe the shipped optional-capability boundary, localized-perception scope, and lifecycle policy without implying truth or gate authority
- harness/eval coverage can exercise the new localized optional-perception paths explicitly without changing the default backend-running semantics
- closeout records which lanes were real operator/live proofs versus fixture or transport proof only

## Implementation Notes

- preserve the current default harness semantics unless a new explicit opt-in
  mode is selected
- negative coverage must prove:
  - disabled optional adapter
  - unavailable optional adapter
  - timeout or empty result on optional adapter
  - no accidental promotion of support evidence into completion truth
- if localized optional perception changes client-visible compare/iterate
  payloads, keep stdio and Streamable HTTP transport parity on the same branch
- closeout should explicitly distinguish:
  - unit proof
  - transport/integration proof
  - Blender-backed proof
  - optional live-provider proof

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/` lanes only where the new support path changes real
  staged compare behavior

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- one or more `_docs/_CHANGELOG/*` entries

## Changelog Impact

- add the historical closeout entry or entries when the first `TASK-172`
  implementation slice lands and extend them as the family closes

## Status / Board Update

- close the umbrella and child-task state together; do not leave open children
  under a closed `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- optional targeted Blender-backed and live-provider lanes when the
  implementation changes real staged behavior

## Validation Category

- docs, harness, and closeout proof
