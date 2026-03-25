# TASK-120-01-01: Macro Candidate Extraction and Selection Rubric

**Parent:** [TASK-120-01](./TASK-120-01_Macro_Candidate_Matrix_And_Shared_Contract.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first macro-wave candidates are now selected from the current workflow library: `macro_cutout_recess`, `macro_relative_layout`, and `macro_finish_form`. Full asset generators such as tables/houses remain workflow-only, and specialist maintenance paths remain atomic/internal for now.

---

## Objective

Select the first macro families using a repeatable rubric based on real workflow
usage and public-surface pain points.

---

## Implementation Direction

- analyze existing custom workflows and grouped-tool usage patterns
- rank candidates by:
  - frequency
  - boundedness
  - value on `llm-guided`
  - compatibility with deterministic verification
  - ability to replace multiple low-level decisions
- explicitly separate:
  - good macro candidates
  - still-atomic actions
  - still-workflow-only flows

## Candidate Matrix

| Candidate | Source workflows / repeated patterns | Why it fits the macro layer | Decision |
|---|---|---|---|
| `macro_cutout_recess` | `screen_cutout.yaml`, multiple recess/cutter sequences in `feature_phone.yaml` | Frequent, bounded, verification-friendly, replaces many low-level boolean/cutter steps without becoming a whole-asset workflow | **Wave 1** |
| `macro_relative_layout` | repeated table leg/bench placement offsets in `simple_table.yaml`, `x_leg_table.yaml`, `picnic_table.yaml`; frequent scene placement/offset work in manual flows | High-value for part placement, bounded around align/place/offset intent, pairs naturally with measure/assert follow-up | **Wave 1** |
| `macro_finish_form` | repeated bevel/subsurf/solidify/rounding patterns in `feature_phone.yaml` and common hard-surface finishing | Good mid-layer between raw modifiers and full workflows; bounded enough for preset-driven finishing | **Wave 1** |
| full table generators | `simple_table.yaml`, `x_leg_table.yaml`, `picnic_table.yaml` | Too broad and asset-specific; better left as workflow-level generation | **Workflow-only** |
| full house generator | `simple_house.yaml` | Asset-level composition, not one bounded task responsibility | **Workflow-only** |
| specialist maintenance/debug paths | armature/sculpt/text/system families | Valuable internally, but poor first macro candidates for the public guided layer | **Not in Wave 1** |

## Selection Notes

- `macro_cutout_recess` is the strongest first implementation target because it already appears as a repeated bounded sequence across multiple workflows.
- `macro_relative_layout` is the strongest second candidate because it can absorb a large amount of manual object-placement decision overhead while remaining verification-friendly.
- `macro_finish_form` is intentionally third because it needs preset discipline to avoid collapsing into an unbounded “modifier kitchen sink”.

---

## Repository Touchpoints

- `server/router/application/workflows/custom/*.yaml`
- `_docs/_PROMPTS/*.md`
- `tests/e2e/router/`
- `_docs/_TASKS/TASK-113-04_Macro_And_Workflow_Tool_Design_Rules.md`

---

## Acceptance Criteria

- the first macro wave has an explicit candidate matrix and rejection rationale
- candidate selection is reproducible later for the second macro wave
