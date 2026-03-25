# TASK-118: Scene Render, World, and Configuration Wave

**Priority:** 🟡 Medium  
**Category:** Scene Surface Expansion  
**Estimated Effort:** Medium  
**Dependencies:** TASK-113, TASK-114, TASK-117  
**Status:** 🚧 In Progress

**Progress Update:** The grouped read/write scene-state surface is now in place: `scene_inspect` supports `render`, `color_management`, and `world`, and `scene_configure` now replays bounded render/color/world settings from structured payloads. The remaining work is the explicit world/node-graph boundary handoff and Blender-backed roundtrip coverage.

---

## Objective

Rewrite the old scene render/world intent under the new layered tool model so
scene-level appearance can be inspected and configured deterministically.

---

## Business Problem

The repo can already inspect objects and geometry well, but it still lacks a
clean modern surface for scene-level appearance:

- render settings
- color-management settings
- world/background state
- deterministic write-side scene configuration

The old business intent existed in superseded `TASK-081`, but it must now be
reframed through grouped public tools and hidden/internal implementation layers.

---

## Business Outcome

If this wave is done correctly, the repo gains:

- read-side inspection for render/color/world state
- a grouped write-side scene configuration tool
- explicit world/node-graph boundary rules
- a modern replacement for the older scene-config reconstruction intent

---

## Scope

This umbrella covers:

- extending `scene_inspect` for render/color/world inspection
- a grouped `scene_configure` write-side tool
- world/node-graph boundary and handoff rules
- metadata, docs, and roundtrip coverage

---

## Success Criteria

- scene-level appearance can be inspected and applied deterministically
- the public surface follows grouped-tool rules instead of reviving old flat patterns
- render/world configuration is documented as a modern scene-surface wave

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-118-01](./TASK-118-01_Read_Side_Scene_State_Expansion.md) | Add read-side render/color/world inspection |
| 2 | [TASK-118-02](./TASK-118-02_Grouped_Scene_Configure_Tool.md) | Add grouped write-side scene configuration |
| 3 | [TASK-118-03](./TASK-118-03_World_Node_Graph_Boundary_And_Handoff.md) | Define world/node-graph boundaries and handoff rules |
| 4 | [TASK-118-04](./TASK-118-04_Metadata_Docs_And_Roundtrip_Coverage.md) | Deliver metadata, docs, and roundtrip regression coverage |
