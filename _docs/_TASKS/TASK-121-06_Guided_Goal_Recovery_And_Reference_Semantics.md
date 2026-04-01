# TASK-121-06: Guided Goal Recovery and Reference Semantics

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Guided sessions now recover more cleanly when workflow
matching is weak or wrong: reference-guided low-poly animal goals can hand off
directly into `guided_manual_build`, pending `workflow_confirmation` can be
explicitly declined into manual build, `scene_*` utility/read-side tools no
longer execute unrelated pending workflows, and `reference_images(...)` can now
stage attachments before the active goal exists and adopt them automatically on
the next goal set.

---

## Objective

Fix the remaining guided-session semantic gaps that made real reference-driven
modeling and vision preparation feel brittle.

---

## Business Problem

Real guided usage exposed four linked failures:

- reference-guided squirrel/manual-build goals drifted into unrelated workflows
- `reference_images(...)` before `router_set_goal(...)` had no clean product path
- utility scene tools could still execute an unrelated pending workflow
- there was no explicit, product-level way to reject a bad workflow suggestion
  and continue manually

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-06-01](./TASK-121-06-01_Reference_Guided_Manual_Build_Goal_Boundary.md) | Route reference-guided low-poly squirrel/organic build goals into `guided_manual_build` instead of irrelevant workflows |
| [TASK-121-06-02](./TASK-121-06-02_Pending_Reference_Attach_Before_Goal.md) | Allow `reference_images(...)` to stage pending references before the goal is active and adopt them automatically |
| [TASK-121-06-03](./TASK-121-06-03_Utility_Tool_Router_Bypass_For_Guided_Sessions.md) | Prevent `scene_*` utility/read-side calls from accidentally executing unrelated pending workflows |
| [TASK-121-06-04](./TASK-121-06-04_Explicit_Workflow_Rejection_Into_Guided_Manual_Build.md) | Let model-facing workflow confirmation decline cleanly into `guided_manual_build` |

---

## Acceptance Criteria

- reference-guided squirrel/manual-build goals no longer drift into irrelevant
  workflow families by default
- attaching references before the goal is active is a supported product path
- `scene_clean_scene` / viewport / scene helper tools do not execute unrelated
  pending workflows
- the model can explicitly reject a bad workflow match and continue on the
  guided build surface
