# TASK-150-04-02: Flow, Domain, Step To Prompt Mapping And Guidance

**Parent:** [TASK-150-04](./TASK-150-04_Prompt_Bundle_Delivery_And_Flow_Aligned_Recommendations.md)
**Depends On:** [TASK-150-04-01](./TASK-150-04-01_Required_Prompt_Bundle_Contract_And_Provider_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Map concrete flow/domain/step combinations onto prompt bundles and explain the
operator/model guidance those mappings imply.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Planned File Work

- Modify:
  - `server/adapters/mcp/prompts/prompt_catalog.py`
  - `_docs/_PROMPTS/README.md`
  - `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Detailed Implementation Notes

- capture the mapping in code, not only in docs
- docs should explain:
  - what prompt bundle the server expects
  - when a step can continue without another prompt refresh
  - when a domain overlay changes the required prompt bundle

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - prompt docs mention flow/domain/step mapping explicitly
- Create `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
  - generic mapping
  - creature mapping
  - building mapping
  - fallback behavior when no specialized profile applies

## Acceptance Criteria

- prompt mappings exist for at least generic/creature/building
- mappings can vary by current step
- docs explain how those bundles support the server-driven flow instead of
  replacing it

## Pseudocode Sketch

```python
PROMPT_BUNDLES = {
    ("creature", "establish_spatial_context"): ("guided_session_start", "reference_guided_creature_build"),
    ("building", "establish_spatial_context"): ("guided_session_start", "workflow_router_first"),
    ("generic", "checkpoint_iterate"): ("guided_session_start",),
}
```

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- prompt/provider tests as needed

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
