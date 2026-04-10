# TASK-152-03: Regression And Docs Closeout For Guided Spatial Usability

**Parent:** [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md)
**Depends On:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md), [TASK-152-02](./TASK-152-02_Inspect_Validate_Surface_And_Attachment_Family_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Lock in the revised model-facing spatial contract with parity tests and
operator-facing docs closeout.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- docs parity tests assert the new spatial-scope and seam-verdict guidance
- visibility/integration tests assert the final `inspect_validate` policy
- board/changelog/docs are updated in the same branch when TASK-152 ships

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when TASK-152 ships
