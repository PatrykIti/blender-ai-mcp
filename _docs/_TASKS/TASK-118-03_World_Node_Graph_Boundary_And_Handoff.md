# TASK-118-03: World Node-Graph Boundary and Handoff

**Parent:** [TASK-118](./TASK-118_Scene_Render_World_And_Configuration_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Define what the scene-config surface owns and what should be handed off to the
future node-graph reconstruction track.

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-118-03-01](./TASK-118-03-01_World_Node_Graph_Reference_Contract.md) | Stable reference shape for node-based world inspection |
| [TASK-118-03-02](./TASK-118-03-02_Scene_Configure_Vs_Node_Graph_Boundary.md) | Explicit rule split between grouped scene config and node-graph tooling |

---

## Acceptance Criteria

- scene config tools do not blur into full node-graph rebuild behavior
- world inspection/config payloads clearly signal when node-graph handoff is required
