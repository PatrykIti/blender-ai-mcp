# TASK-120-02: First Macro Wave, Form, Cutout, and Layout

**Parent:** [TASK-120](./TASK-120_Macro_Tool_Layer_And_Guided_Surface_Collapse.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The first two concrete macro tools, `macro_cutout_recess` and `macro_relative_layout`, are now implemented end-to-end. The remaining work in this cluster is `macro_finish_form`, plus harmonizing how the first macro wave changes guided discovery/visibility assumptions.

---

## Objective

Implement the first bounded macro families that most directly reduce dependence
on low-level atomics during hard-surface modeling sessions.

---

## Repository Touchpoints

- `server/domain/`
- `server/application/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/infrastructure/di.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/tools/`
- `tests/e2e/tools/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-120-02-01](./TASK-120-02-01_Macro_Cutout_Recess_Tool.md) | Bounded macro for cutter creation, rounding, boolean application, and cleanup |
| [TASK-120-02-02](./TASK-120-02-02_Macro_Relative_Layout_Tool.md) | Bounded macro for align/place/offset/contact-ready layout between parts |
| [TASK-120-02-03](./TASK-120-02-03_Macro_Finish_Form_Tool.md) | Bounded macro for controlled form finishing (bevel/subsurf/solidify/smoothing presets) |

---

## Acceptance Criteria

- first macro tools each own one bounded family of modeling intent
- macro tools reduce low-level decision count without becoming generic workflow shells
