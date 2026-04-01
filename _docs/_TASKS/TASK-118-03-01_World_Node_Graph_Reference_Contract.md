# TASK-118-03-01: World Node-Graph Reference Contract

**Parent:** [TASK-118-03](./TASK-118-03_World_Node_Graph_Boundary_And_Handoff.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_inspect(action="world")` and the resulting `scene_configure(action="world")` payloads now expose stable `node_graph_reference` and `node_graph_handoff` fields whenever node-based world state needs a future node-graph handoff.

---

## Objective

Define the minimal inspection/config contract needed when a world uses nodes.

---

## Design Direction

The contract should expose:

- whether nodes are in use
- world name / identity
- lightweight summary fields for quick inspection
- explicit reference/handoff fields for future node-graph reconstruction

It should not pretend that scene tools can fully serialize and rebuild arbitrary
world node graphs inside one shallow payload.

---

## Acceptance Criteria

- node-based worlds are represented consistently in read/write scene flows
- downstream node-graph work has a stable handoff point
