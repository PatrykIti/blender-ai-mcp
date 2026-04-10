# TASK-153-01-02: Document The Single Runtime Visibility Authority

**Parent:** [TASK-153-01](./TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md)
**Depends On:** [TASK-153-01-01](./TASK-153-01-01_Audit_Current_Dual_Layer_Visibility_Decisions.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Write down the intended rule that `llm-guided` runtime exposure is controlled
by visibility policy plus session state, not by a second hidden phase gate in
tags/manifest.

## Repository Touchpoints

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`

## Planned Doc Shape

```text
Static metadata:
- capability grouping
- audience classification
- discovery/inventory categories
- provider wiring

Runtime authority on llm-guided:
- build_visibility_rules(...)
- session phase / guided_handoff / guided_flow_state
- visibility application transforms
```

## Detailed Documentation Targets

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - add a clear statement that `build_visibility_rules(...)` is the runtime
    visibility authority on `llm-guided`
  - explicitly forbid tag/manifest-based hidden phase gating
- `_docs/_MCP_SERVER/README.md`
  - explain that:
    - `router_get_status().visibility_rules`
    - `list_tools()`
    - `search_tools(...)`
    are expected to tell one coherent runtime story
- code-adjacent docstrings/comments
  - `tags.py`: tags are coarse metadata, not guided runtime policy
  - `capability_manifest.py`: manifest is inventory/provider metadata
  - `guided_mode.py`: diagnostics mirror runtime visibility rather than define
    it independently

## Pseudocode Sketch

```python
catalog_metadata = get_capability_manifest()
runtime_rules = build_visibility_rules(
    surface_profile="llm-guided",
    phase=current_phase,
    guided_handoff=guided_handoff,
    guided_flow_state=guided_flow_state,
)

assert catalog_metadata_is_used_for(
    "provider_group",
    "public_contracts",
    "discovery_category",
    "pinned_tools",
)
assert runtime_rules_are_used_for(
    "list_tools",
    "search_tools",
    "router_get_status.visibility_rules",
    "guided_mode_diagnostics",
)
```

## Planned File Change Map

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - add the authoritative runtime-vs-metadata split
- `_docs/_MCP_SERVER/README.md`
  - add operator-facing explanation of the single runtime visibility authority
- `server/adapters/mcp/visibility/tags.py`
  - tighten the module docstring if runtime-phase semantics are removed
- `server/adapters/mcp/platform/capability_manifest.py`
  - tighten the module/docstring wording around metadata-only usage
- `server/adapters/mcp/guided_mode.py`
  - tighten docstrings/comments so diagnostics are documented as a mirror of
    runtime policy

## Planned Unit Test Scenarios

- docs parity tests assert that the public docs describe runtime visibility as
  rule-driven
- docs parity tests assert that manifest/tags are described as discovery and
  inventory metadata only

## Acceptance Criteria

- docs explicitly say phase tags/manifests must not act as a second hidden
  visibility policy on `llm-guided`

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
  once the runtime implementation leaves land

## Changelog Impact

- include in the parent TASK-153 changelog entry
