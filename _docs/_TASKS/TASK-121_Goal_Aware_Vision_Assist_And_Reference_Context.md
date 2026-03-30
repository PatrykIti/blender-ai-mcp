# TASK-121: Goal-Aware Vision Assist and Reference Context

**Priority:** 🔴 High  
**Category:** Vision Assist / Goal Context  
**Estimated Effort:** Large  
**Dependencies:** TASK-113, TASK-120  
**Status:** 🚧 In Progress

**Progress Update:** The repo now has the first runtime/capture scaffolding for this wave: a pluggable local/external vision backend model, lazy runtime resolution that keeps heavyweight VLM loading out of MCP bootstrap, shared vision result contracts, deterministic capture-bundle input types plus runtime preset profiles, a first macro-path integration where macro reports can carry optional `capture_bundle` artifacts when vision is enabled, MCP macro adapters now have the request-bound attachment point for `vision_assistant`, `TASK-121-02` is done with goal-scoped reference images plus the public `reference_images` lifecycle surface, `TASK-121-03` is now in progress with reference-context-aware macro vision requests, `TASK-121-04` is now in progress with real smoke-test validation plus first scored goldens for the `mlx_local` runtime path, `TASK-121-05` hardened guided utility/manual-build handoffs, `TASK-121-06` fixes the remaining guided-session recovery semantics around reference-first attach, bad workflow rejection, and utility-tool workflow bypass, `TASK-121-07` is now done with bounded checkpoint-vs-reference compare surfaces, deterministic stage checkpoint capture, correction-focused output semantics, and prompt/eval guidance for reference-driven creature work, and `TASK-121-08` adds the first session-aware auto-loop controller on top of that surface via `reference_iterate_stage_checkpoint(...)`.

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
| 5 | [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md) | Fix `llm-guided` so utility capture/scene-prep flows work naturally and do not get misrouted into build workflows |
| 6 | [TASK-121-06](./TASK-121-06_Guided_Goal_Recovery_And_Reference_Semantics.md) | Fix reference-first guided modeling, bad-workflow rejection, and utility-tool recovery semantics on `llm-guided` |
| 7 | [TASK-121-07](./TASK-121-07_Vision_Guided_Iterative_Correction_Loop.md) | Add a bounded checkpoint-vs-reference correction loop for staged manual/reference-guided work |
| 8 | [TASK-121-08](./TASK-121-08_Session_Aware_Reference_Correction_Auto_Loop.md) | Add a session-aware auto-loop controller that remembers prior correction focus and can escalate into inspect/validate |
