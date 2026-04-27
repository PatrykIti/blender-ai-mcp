# TASK-155-03-02: Compact Checkpoint Response Mode

**Parent:** [TASK-155-03](./TASK-155-03_Guided_Tool_UX_And_Response_Budget.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Add an LLM-guided compact checkpoint response path so
`reference_iterate_stage_checkpoint(...)` does not return large multi-thousand
token payloads during normal long-running guided sessions.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/infrastructure/config.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- compact mode returns top correction candidates, short next actions, compact
  truth summary, and enough target-scope information to continue safely
- rich/full payload remains available through an explicit profile or debug path
- compact mode stays deterministic and does not drop high-priority required
  seam failures
- budget metadata clearly reports when trimming was applied

## Tests To Add/Update

- Unit:
  - add compact/rich response shape tests in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - add contract parity coverage if a new contract field is introduced
  - update docs parity in `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - extend `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
    or `tests/e2e/integration/test_guided_inspect_validate_handoff.py` to
    assert compact guided checkpoint behavior

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- compact stage checkpoint responses now omit full capture records while
  retaining capture counts, preset names, truth, and correction summaries
