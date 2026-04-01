# TASK-121-05: Guided Utility Capture Prep and Goal Boundary

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The router-side boundary fixes are now in place: utility/capture goals such as viewport screenshot or scene cleanup requests are intercepted before workflow execution, broad substring-based workflow keyword matching has been tightened, `screen_cutout_workflow` trigger keywords have been narrowed so `screen`-overlap prompts no longer misroute, a guided utility surface exists for bootstrap/planning, discovery tools persist across guided session visibility updates, and `router_set_goal(...)` keeps normal missing workflow params model-facing on `llm-guided`.

---

## Objective

Make `llm-guided` usable for the utility steps that are required to prepare
vision inputs, especially:

- cleaning or resetting the scene
- capturing viewport screenshots
- handling utility/capture intents without misrouting them into build workflows

---

## Business Problem

The product direction says `llm-guided` should be the normal production-facing
surface for LLM sessions. In practice, that surface currently breaks down for
simple utility requests needed to prepare vision tests and before/after
captures.

Current failure modes:

- `router_set_goal("capture viewport screenshot save to file")` can match a
  modeling workflow such as `screen_cutout_workflow` instead of recognizing
  that this is a utility/capture request
- `llm-guided` bootstrap/planning visibility does not expose a safe path for
  viewport capture or scene cleanup
- `search_tools(...)` and `call_tool(...)` cannot rescue these cases because
  the relevant tools are hidden at exactly the phase where they are needed

This makes the guided surface inconsistent with its documented role and makes
vision test preparation awkward or impossible on the intended production path.

---

## Business Outcome

If this task cluster is completed, `llm-guided` will:

- stop misclassifying utility/capture requests as modeling workflow goals
- expose a bounded guided-safe path for scene prep and viewport capture
- allow users and LLM agents to prepare before/after vision inputs without
  dropping into legacy/manual surfaces for routine utility work
- keep the surface curated, while still supporting essential capture prep for
  `TASK-121`

---

## Scope

This cluster covers:

- router goal-boundary fixes for utility/capture intents
- workflow trigger hygiene to avoid false-positive workflow matches
- guided-surface visibility and discovery for scene prep / viewport capture
- prompt/docs alignment so guided clients know when to use utility capture
  actions versus build goals

This cluster does **not** broaden `llm-guided` back into a legacy-flat surface.
It keeps the public surface curated and bounded.

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-05-01](./TASK-121-05-01_Router_Utility_Goal_Boundary_And_Workflow_Trigger_Hygiene.md) | Stop `router_set_goal` from routing utility/capture requests into unrelated build workflows |
| [TASK-121-05-02](./TASK-121-05-02_Guided_Utility_Surface_For_Scene_Prep_And_Viewport_Capture.md) | Add a guided-safe utility path for scene cleanup and viewport capture |
| [TASK-121-05-03](./TASK-121-05-03_Guided_Discovery_Prompts_And_Docs_For_Utility_Capture_Flows.md) | Align search, prompts, and docs so utility capture flows are discoverable and correctly framed |
| [TASK-121-05-04](./TASK-121-05-04_Guided_Discovery_Tool_Persistence_Across_Session_Visibility.md) | Keep discovery tools (`search_tools` / `call_tool`) visible after guided session visibility updates |
| [TASK-121-05-05](./TASK-121-05-05_Model_First_Router_Clarification_On_Guided_Surface.md) | Keep missing workflow parameters model-facing by default on `llm-guided`, with human elicitation only as a later fallback |
| [TASK-121-05-06](./TASK-121-05-06_Guided_Manual_Build_Handoff_After_Weak_Or_Irrelevant_Workflow_Match.md) | Prevent weak/irrelevant workflow matches from blocking manual guided modeling and create an explicit handoff to the curated build surface |

---

## Acceptance Criteria

- `router_set_goal(...)` no longer routes screenshot/viewport/scene-reset goals
  into unrelated modeling workflows
- `llm-guided` exposes a bounded path for scene prep and viewport capture
- guided search/discovery can reach the relevant capture-prep tools
- docs and prompts explain the expected guided utility flow clearly
