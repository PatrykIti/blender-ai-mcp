# TASK-118-03-02: Scene Configure vs Node Graph Boundary

**Parent:** [TASK-118-03](./TASK-118-03_World_Node_Graph_Boundary_And_Handoff.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

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
