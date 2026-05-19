# TASK-169-05-01: Transcript-State And Packet-Priority Regression Cases

**Parent:** [TASK-169-05](./TASK-169-05_Squirrel_Reference_Guided_Drift_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Encode the observed squirrel session as typed regressions for goal/no-match, one-ref then two-ref RU refresh, packet-local compare narrowing, `eye_pair` misuse, and viewport alias drift.
**Repository Touchpoints:** `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `server/application/tool_handlers/router_handler.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/guided_contract.py`, `_docs/_TEST_IMAGES/squirrel-front.png`, `_docs/_TEST_IMAGES/squirrel-side.png`
**Acceptance Criteria:**
- the squirrel regression facts are encoded as deterministic tests
- packet-local compare narrowing can be asserted separately from Blender visual quality
- controller misuse of `eye_pair` and `scene_get_viewport(output_mode=\"IMAGE_PATH\")` stays pinned as contract-level drift

## Implementation Notes

- re-anchor the regression to the current shipped seams, not to raw copied
  Claude transcript blobs
- likely cases:
  - `router_set_goal(...)` returns `no_match` but still preserves creature
    reference context
  - attach front ref then side ref refreshes RU from one-reference to
    two-reference state deterministically
  - early creature compare prefers a broad scope before later ear/limb-local
    packets
  - gate-only `eye_pair` no longer tempts the public guided role path
  - `IMAGE_PATH` fails safe or normalizes to `FILE`, depending on the final
    slice decision
- keep the leaf anchored on current helpers/contracts rather than a prose-only
  session reenactment:
  - `RouterToolHandler._no_match_response(...)`
  - `refresh_reference_understanding_summary(...)`
  - `resolve_active_compare_scope(...)`
  - `canonicalize_scene_get_viewport_arguments(...)`

## Runtime / Security Contract Notes

- public MCP/runtime contract drift should be asserted on typed responses and
  canonicalization errors, not on informal text-only checks
- repo-owned squirrel fixtures should be used instead of ad hoc operator temp
  files where a deterministic regression can be pinned locally

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Docs To Update

- none by default; update only if the regression vocabulary becomes public

## Changelog Impact

- covered by the umbrella closeout entry when the regression pack lands

## Status / Board Update

- keep nested under `TASK-169-05`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py -q`

## Validation Category

- transcript-state and contract regression proof
