# TASK-121-05-06: Guided Manual Build Handoff After Weak or Irrelevant Workflow Match

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The guided manual-build fallback path is now explicit at the
product surface. Obvious meta build/capture goals can bypass irrelevant workflow
routing into `status="no_match"` with `continuation_mode="guided_manual_build"`,
and `router_set_goal()` now adds a typed `guided_handoff` contract that names
the target phase plus first-choice tools. Prompt/docs and regression coverage
have been aligned around that behavior.

---

## Objective

Ensure `llm-guided` can continue into a sane guided manual-build path when
workflow matching is weak, irrelevant, or simply not helpful for the current
task.

---

## Business Problem

Real usage exposed a distinct failure mode beyond utility/capture prep:

- the model submits a goal that is partly a build request and partly meta-test
  context
- the router returns an irrelevant workflow match or a `needs_input` response
  for the wrong workflow
- the model then tries to continue manually, but the guided surface does not
  provide a clean, explicit handoff into the curated build layer

Example symptom:

- a low-poly squirrel test goal drifts into `feature_phone_workflow`
- the model decides the workflow is wrong
- but then cannot simply continue building on the guided surface in a clean,
  intended way

This produces a bad product loop:

- weak workflow match
- awkward clarification
- no clean guided manual fallback
- model starts guessing, over-searching, or trying tool names that are hidden

---

## Business Outcome

If this subtask is completed, `llm-guided` will:

- reject or downgrade obviously irrelevant workflow matches more reliably
- let the model continue with manual guided modeling when workflow help is not
  useful
- avoid pushing the model toward workflow import/create when the user simply
  wants to build an object that does not fit the current workflow catalog

---

## Scope

This subtask covers:

- stronger router-side rejection of weak/irrelevant workflow matches for
  guided sessions
- an explicit handoff into manual guided build when workflow routing is not a
  good fit
- docs/prompts that explain how the model should continue after `no_match`
  without collapsing into legacy-flat behavior

This subtask does **not** aim to expose the entire internal catalog or make
workflow import the default escape hatch.

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-05-06-01](./TASK-121-05-06-01_Router_No_Match_And_Irrelevant_Workflow_Guard.md) | Make the router more willing to return `no_match` instead of weak/irrelevant workflow paths for guided modeling goals |
| [TASK-121-05-06-02](./TASK-121-05-06-02_Explicit_Manual_Guided_Build_Handoff.md) | Add a clean guided-manual handoff instead of forcing workflow import/create or random tool-guessing |
| [TASK-121-05-06-03](./TASK-121-05-06-03_Prompts_And_Tests_For_Guided_Manual_No_Match_Flow.md) | Align prompts/tests so models handle `no_match` as a legitimate guided build continuation path |

---

## Acceptance Criteria

- weak or irrelevant workflow matches do not trap the model in the wrong
  workflow path
- `no_match` can lead to a clean guided manual-build continuation
- prompts/tests clearly describe the intended behavior after workflow mismatch
