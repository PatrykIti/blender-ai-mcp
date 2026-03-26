# TASK-121: Goal-Aware Vision Assist and Reference Context

**Priority:** 🔴 High  
**Category:** Vision Assist / Goal Context  
**Estimated Effort:** Large  
**Dependencies:** TASK-113, TASK-120  
**Status:** 🚧 In Progress

**Progress Update:** The repo now has the first runtime/capture scaffolding for this wave: a pluggable local/external vision backend model, lazy runtime resolution that keeps heavyweight VLM loading out of MCP bootstrap, shared vision result contracts, and deterministic capture-bundle input types prepared for later scene/macro integration.

---

## Objective

Add a goal-aware lightweight vision-assist layer with reference-image context so
macro/workflow paths can reason about visible change without treating vision as
the truth source.

---

## Business Problem

Deterministic inspection and assertion tools can tell the system whether
dimensions, contact, or alignment are correct, but they do not answer:

- does the visible change actually move the build toward the goal?
- does the result visually resemble the intended reference?
- which visible issues are likely worth checking next?

The product needs a bounded visual interpretation layer, especially once macro
and workflow tools produce before/after changes and users begin attaching
reference images to goals.

---

## Business Outcome

If this wave is done correctly, the repo gains:

- request-bound vision assistance attached to goal-aware macro/workflow paths
- session-scoped reference image support
- deterministic before/after capture bundles for visual comparison
- a pluggable vision backend path supporting both local and external runtimes
- a visual interpretation layer that complements, but does not replace, truth tools

---

## Scope

This umbrella covers:

- one lightweight vision-assist contract and boundary model
- goal-scoped reference-image session state
- reference image intake and lifecycle
- before/after capture packaging with deterministic wide and object-focused views
- macro/workflow integration
- runtime/model selection and evaluation for the vision layer, including local and external backend options

This umbrella does **not** turn vision into the truth source or router policy owner.
It also does **not** make a heavyweight vision model a mandatory always-loaded
server dependency in the core MCP bootstrap path.

---

## Success Criteria

- vision assistance is bounded, goal-aware, and request-scoped
- reference images can be attached to the active modeling goal
- macro/workflow reports can include visual interpretation and recommended next checks
- vision quality does not depend on ad hoc single viewport screenshots; it runs on deterministic capture bundles plus truth summaries
- the main MCP server remains usable without loading a heavyweight vision model at startup
- deterministic inspection/assertion remains the source of correctness

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-121-01](./TASK-121-01_Vision_Assistant_Boundary_And_Delivery_Contract.md) | Define the vision-assistant contract and keep it within the correct product boundary |
| 2 | [TASK-121-02](./TASK-121-02_Goal_And_Reference_Context_Session_Model.md) | Add goal-scoped reference-image context and intake/lifecycle APIs |
| 3 | [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md) | Add capture bundles and integrate vision assistance into macro/workflow paths |
| 4 | [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md) | Choose the lightweight runtime/model path and add evaluation/safety coverage |
