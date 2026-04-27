# TASK-153-01-01: Audit Current Dual-Layer Visibility Decisions

**Parent:** [TASK-153-01](./TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Map every place where metadata tags/manifest and runtime visibility policy both
influence what `llm-guided` can see, list, or discover.

## Repository Touchpoints

- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/search_surface.py`

## Current Code Anchors

- `tags.py`
  - `CAPABILITY_TAGS`
  - `phase_tag(...)`
  - `capability_phase_tag(...)`
- `capability_manifest.py`
  - `CapabilityManifestEntry`
  - `CAPABILITY_MANIFEST`
- `guided_mode.py`
  - `_rule_matches_entry(...)`
  - `_is_capability_visible(...)`
  - `build_visibility_diagnostics(...)`
- `tool_inventory.py`
  - `build_discovery_inventory(...)`
- `search_surface.py`
  - `BlenderDiscoverySearchTransform._sync_visibility_if_needed(...)`
  - `BlenderDiscoverySearchTransform._search(...)`

## Planned Audit Output

- enumerate each current decision layer:
  - capability tags
  - capability manifest
  - visibility rules
  - runtime diagnostics
  - discovery/inventory helpers
- classify each as one of:
  - keep as coarse metadata
  - keep as runtime authority
  - remove or demote from runtime gating

## Planned Audit Matrix

- `server/adapters/mcp/visibility/tags.py`
  - identify which tags are pure metadata (`audience:*`, `entry:*`)
  - identify which tags currently look like phase/runtime policy (`phase:*`)
- `server/adapters/mcp/platform/capability_manifest.py`
  - identify which manifest fields are stable discovery/provider metadata
  - identify whether any tag-driven assumptions leak back into runtime
    visibility reasoning
- `server/adapters/mcp/guided_mode.py`
  - identify where diagnostics infer capability visibility from manifest/tag
    matching rather than from the actual visible tool set
- `server/adapters/mcp/transforms/visibility_policy.py`
  - identify the real runtime authority inputs:
    `surface_profile`, `phase`, `guided_handoff`, and `guided_flow_state`
- `server/adapters/mcp/transforms/visibility.py`
  - confirm this layer is a thin application of already-built rules
- `server/adapters/mcp/discovery/tool_inventory.py`
  - confirm inventory is phase-agnostic catalog metadata
- `server/adapters/mcp/discovery/search_surface.py`
  - confirm runtime filtering should happen via synced visible tools rather
    than via manifest-phase overlap

## Pseudocode Sketch

```python
audit_rows = []

for entry in get_capability_manifest():
    phase_tags = {tag for tag in entry.tags if tag.startswith("phase:")}
    for phase in (SessionPhase.BOOTSTRAP, SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE):
        rules = build_visibility_rules("llm-guided", phase)
        visible_tool_names = materialize_visible_tool_names(entry.tool_names, rules)
        audit_rows.append(
            {
                "capability_id": entry.capability_id,
                "phase_tags": sorted(phase_tags),
                "phase": phase.value,
                "visible_tool_names": sorted(visible_tool_names),
                "classification": classify_dual_layer_overlap(phase_tags, visible_tool_names),
            }
        )
```

## Planned File Change Map

- `_docs/_TASKS/TASK-153-01-01_Audit_Current_Dual_Layer_Visibility_Decisions.md`
  - record the audit output in an implementation-facing form
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - update only if the audit exposes a missing ownership boundary
- `_docs/_TASKS/TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md`
  - fold the resulting keep/demote/runtime decisions back into the parent
    subtask

## Acceptance Criteria

- the audit makes the overlap explicit enough that the implementation leaves can
  delete/demote behavior instead of guessing

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` if the audit reveals a missing
  boundary note

## Tests To Add/Update

- none directly

## Changelog Impact

- include in the parent TASK-153 changelog entry

## Completion Summary

- audited the overlap and confirmed the real remaining drift was in
  phase-shaped capability tags plus diagnostics/wording, not in the main
  runtime visibility transform path
