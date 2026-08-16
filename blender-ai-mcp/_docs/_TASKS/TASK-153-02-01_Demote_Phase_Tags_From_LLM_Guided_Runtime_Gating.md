# TASK-153-02-01: Demote Phase Tags From LLM Guided Runtime Gating

**Parent:** [TASK-153-02](./TASK-153-02_Runtime_Visibility_Authority_Consolidation_For_LLM_Guided.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Stop `phase:*` capability tags from acting as an implicit runtime gate for
`llm-guided`.

## Repository Touchpoints

- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `tags.py`
  - `CAPABILITY_TAGS`
  - `phase_tag(...)`
  - `capability_phase_tag(...)`
- `guided_mode.py`
  - `_rule_matches_entry(...)`
  - `_is_capability_visible(...)`

## Planned Code Shape

```python
# before
CAPABILITY_TAGS["scene"] = ("audience:...", "phase:planning", "phase:build", ...)

# after
CAPABILITY_TAGS["scene"] = ("audience:...",)

# optional coarse phase metadata moves into a metadata-only helper instead:
CAPABILITY_PHASE_HINTS["scene"] = ("planning", "build", "inspect_validate")

# runtime phase checks stay only in:
build_visibility_rules(...)
```

## Detailed Implementation Notes

- the preferred shape is:
  - keep `audience:*` and `entry:*` tags as registered FastMCP tags
  - remove `phase:*` from runtime-facing capability tags on `llm-guided`
  - if docs or inventory still need phase labeling, preserve it as
    metadata-only hints instead of registered runtime tags
- update the shared tag source (`get_capability_tags(...)`) rather than
  patching every area module independently
- `guided_mode.py` must stop interpreting manifest/tag overlap as runtime phase
  authority once phase tags are demoted

## Planned File Change Map

- `server/adapters/mcp/visibility/tags.py`
  - edit `CAPABILITY_TAGS`
  - optionally add metadata-only phase-hint helpers
- `server/adapters/mcp/platform/capability_manifest.py`
  - preserve any needed coarse phase metadata without making it a runtime gate
- `server/adapters/mcp/guided_mode.py`
  - remove any remaining reliance on phase-tag overlap for runtime visibility
- `tests/unit/adapters/mcp/test_visibility_policy.py`
  - replace phase-tag assertions with metadata-only expectations
- `tests/unit/adapters/mcp/test_guided_mode.py`
  - prove diagnostics still match runtime rules after tag demotion
- `tests/unit/adapters/mcp/test_provider_inventory.py`
  - prove provider grouping/public contracts remain intact
- `tests/unit/adapters/mcp/test_tool_inventory.py`
  - prove discovery inventory remains useful after phase-tag demotion
- `tests/unit/adapters/mcp/test_surface_inventory.py`
  - prove the factory manifest snapshot remains stable as metadata
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - prove stdio runtime behavior is unchanged by tag demotion
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - prove streamable runtime behavior is unchanged by tag demotion

## Pseudocode Sketch

```python
def get_capability_tags(capability_id: str) -> tuple[str, ...]:
    return CAPABILITY_TAGS[capability_id]  # audience / entry only


def get_capability_phase_hints(capability_id: str) -> tuple[str, ...]:
    return CAPABILITY_PHASE_HINTS.get(capability_id, ())


CapabilityManifestEntry(
    capability_id="scene",
    tags=get_capability_tags("scene"),
    phase_hints=get_capability_phase_hints("scene"),
    ...
)
```

## Planned Unit Test Scenarios

- removing/demoting phase tags does not change coarse capability grouping
- `llm-guided` visibility remains governed by explicit rules, not tag overlap
- registered tools keep audience/entry tags but no longer depend on `phase:*`
  for guided runtime exposure
- manifest/inventory still expose enough metadata for discovery and provider
  wiring

## Planned E2E / Transport Scenarios

- stdio guided session keeps the same bounded bootstrap/build/inspect behavior
  after tag demotion
- streamable guided session keeps the same unlock/re-arm behavior after tag
  demotion

## Acceptance Criteria

- phase tags are no longer required for `llm-guided` runtime visibility

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry

## Completion Summary

- removed `phase:*` from runtime-facing capability tags returned by
  `get_capability_tags(...)`
- preserved phase context as metadata-only `CAPABILITY_PHASE_HINTS` /
  manifest `phase_hints`
