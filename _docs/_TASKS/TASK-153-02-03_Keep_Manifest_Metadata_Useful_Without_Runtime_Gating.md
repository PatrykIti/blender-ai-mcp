# TASK-153-02-03: Keep Manifest Metadata Useful Without Runtime Gating

**Parent:** [TASK-153-02](./TASK-153-02_Runtime_Visibility_Authority_Consolidation_For_LLM_Guided.md)
**Depends On:** [TASK-153-02-02](./TASK-153-02-02_Make_Visibility_Policy_The_Single_Runtime_Source_Of_Truth.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Preserve the value of capability manifest/tags for discovery, inventory,
provider wiring, and docs after removing their runtime visibility authority.

## Repository Touchpoints

- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned Code Shape

```python
CapabilityManifestEntry(
    capability_id="scene",
    provider_group="core_tools",
    tool_names=...,
    discovery_category="scene",
    pinned_tools=(...),
    # but not as hidden runtime phase gate
)
```

## Detailed Implementation Notes

- this leaf protects the value of the existing manifest after phase/runtime
  demotion
- the manifest should remain the home for:
  - provider grouping
  - public-name contracts
  - discovery categories
  - aliases
  - pinned tools
  - hidden-from-search defaults
- the manifest should not be reinterpreted as a session-phase gate
- prefer extending existing manifest/inventory structures over adding a second
  discovery registry

## Planned File Change Map

- `server/adapters/mcp/platform/capability_manifest.py`
  - preserve metadata richness after phase-tag demotion
- `server/adapters/mcp/discovery/tool_inventory.py`
  - keep discovery inventory phase-agnostic and metadata-driven
- `server/adapters/mcp/discovery/search_surface.py`
  - keep ranking/documents manifest-backed while respecting runtime visibility
- `server/adapters/mcp/factory.py`
  - keep `_bam_capability_manifest` explicitly metadata-only
- `tests/unit/adapters/mcp/test_provider_inventory.py`
  - assert provider groups and registrars remain stable
- `tests/unit/adapters/mcp/test_tool_inventory.py`
  - assert aliases, pinned tools, categories, and metadata enrichment remain
    stable
- `tests/unit/adapters/mcp/test_surface_inventory.py`
  - assert the server still carries the shared manifest scaffold
- `tests/unit/adapters/mcp/test_server_factory.py`
  - assert surface bootstrap metadata still matches the manifest scaffold
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - assert discovery still finds runtime-allowed tools through the manifest
    catalog
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - assert the same discovery behavior over streamable transport

## Pseudocode Sketch

```python
inventory = build_discovery_inventory()
entry_map = {entry.public_name: entry for entry in inventory}

assert entry_map["browse_workflows"].provider_group == "workflow_tools"
assert entry_map["reference_images"].pinned is True
assert entry_map["router_get_status"].capability_id == "router"

# runtime visibility filters the active searchable subset later;
# the manifest itself stays phase-agnostic
```

## Planned Unit Test Scenarios

- provider/inventory/discovery helpers still work after phase-tag demotion
- pinned tools / discovery categories / public contracts remain intact
- manifest-backed discovery remains stable across bootstrap/build/inspect as a
  catalog, while runtime filtering happens later

## Planned E2E / Transport Scenarios

- stdio guided session:
  - pinned direct tools remain visible on bootstrap
  - manifest-backed search can discover newly unlocked build tools only after
    the runtime surface allows them
- streamable guided session:
  - the same manifest-backed discovery behavior survives session sync and
    reconnect

## Acceptance Criteria

- manifest remains useful and non-trivial after runtime gate demotion

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if inventory/discovery wording changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry
