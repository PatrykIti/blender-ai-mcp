# TASK-152-02-02: Align Visibility, Allowed Families, And Blocked Guidance

**Parent:** [TASK-152-02](./TASK-152-02_Inspect_Validate_Surface_And_Attachment_Family_Alignment.md)
**Depends On:** [TASK-152-02-01](./TASK-152-02-01_Decide_Inspect_Validate_Attachment_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Implement the chosen `inspect_validate` attachment policy consistently across
visibility, `guided_flow_state.allowed_families`, and model-facing blocked
guidance.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `server/adapters/mcp/session_capabilities.py`
  - `_build_allowed_families(...)`
  - inspect step family vocabulary
- `server/adapters/mcp/transforms/visibility_policy.py`
  - `GUIDED_INSPECT_ESCAPE_HATCH_TOOLS`
  - `build_visibility_rules(...)`
- `server/adapters/mcp/router_helper.py`
  - family-based blocked guidance already passes actionable messages back to the
    client/model

## Planned Code Shape

```python
# Variant A: expose attachment macros in inspect
GUIDED_INSPECT_ESCAPE_HATCH_TOOLS += (
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_cleanup_part_intersections",
)

# Variant B: remove attachment_alignment from inspect families
inspect_allowed = ["inspect_validate", "primary_masses", "secondary_parts"]
```

## Planned Unit Test Scenarios

- inspect visibility exposes exactly the macro set implied by
  `guided_flow_state.allowed_families`
- docs parity asserts the same operator guidance

## Planned E2E Scenarios

- stdio/streamable inspect run where the model:
  - reaches `inspect_validate`
  - still needs attachment repair
  should see one coherent outcome:
  - macro visible and callable
  - or macro hidden and explicitly documented as unavailable from inspect

## Acceptance Criteria

- the model no longer sees:
  - `attachment_alignment` as allowed while the relevant macros are hidden
  - or hidden macros while docs say they are available
- blocked responses and docs point to the same next move

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
