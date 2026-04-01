# TASK-118-03-02: Scene Configure vs Node Graph Boundary

**Parent:** [TASK-118-03](./TASK-118-03_World_Node_Graph_Boundary_And_Handoff.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_configure(action="world")` now accepts only bounded world settings (`world_name`, `use_nodes`, `color`, simple `background` updates) and rejects explicit graph-topology payloads, leaving arbitrary world-node rebuilds to the future `node_graph` track.

---

## Objective

Set the boundary between grouped scene configuration and the later node-graph
rebuild surface.

---

## Required Rule Split

`scene_configure` should own:

- scene-level settings
- simple world/background changes
- render/color-management updates

Future `node_graph`-style tooling should own:

- full world node creation
- arbitrary node topology rebuild
- complex shader graph reconstruction

---

## Acceptance Criteria

- scene tool scope stays bounded
- future node-graph work is not blocked by scene-surface ambiguity
