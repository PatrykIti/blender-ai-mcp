# TASK-114-05-02: First Measure/Assert Code Wave Plan

**Parent:** [TASK-114-05](./TASK-114-05_Prioritized_Fix_Backlog_And_Code_Wave_Plan.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first measure/assert implementation wave is now concrete enough to start immediately once the wording-fix wave is complete.

---

## Objective

Define the first real implementation wave for the new measure/assert atomic family.

---

## Expected Scope

- choose the first small atomic set
- define the exact file touchpoints
- define the expected contracts and tests
- ensure alignment with `TASK-113-05-02`

---

## Acceptance Criteria

- the repo has a ready-to-start measure/assert implementation plan once the audit is finished

## Proposed First Atomic Set

Implement first:

1. `scene_measure_distance`
2. `scene_measure_dimensions`
3. `scene_measure_gap`
4. `scene_measure_alignment`
5. `scene_measure_overlap`

These five directly target the highest-frequency failures observed in current LLM modeling:

- wrong proportions
- bad fit between parts
- accidental gaps
- accidental intersections
- poor alignment

## Suggested Shape

Keep them small and deterministic.

Example direction:

- `scene_measure_distance`
  - between two objects, two origins, or two points
- `scene_measure_dimensions`
  - dimensions for one object or selected target
- `scene_measure_gap`
  - nearest separation between two objects / chosen faces/bounds
- `scene_measure_alignment`
  - center/min/max alignment across chosen axes
- `scene_measure_overlap`
  - whether objects/bounds intersect and by how much

## Likely File Touchpoints

- `server/domain/tools/scene.py` or a new dedicated measurement interface if cleaner
- `server/application/tool_handlers/scene_handler.py`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/scene.py` or a new dedicated measurement area if that proves cleaner
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/scene/**`
- `tests/unit/tools/scene/**`
- `tests/e2e/tools/scene/**`
- docs:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Contract Direction

Prefer small structured outputs:

- target ids
- measured value
- units
- axis context where relevant
- pass/fail or relation classification where relevant

Avoid prose-heavy responses here. These tools should become the seed of the
truth layer described in `TASK-113-05-02`.
