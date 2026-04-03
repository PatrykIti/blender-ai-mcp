# TASK-122-03-06: Hybrid Loop Model-Aware Budget and Scope Control

**Follow-on After:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Board Tracking:** Standalone hybrid-loop follow-on kept open after
`TASK-122-03` and `TASK-122` were closed. `_docs/_TASKS/README.md` tracks it
as its own open item while the historical numbering is preserved for
continuity.  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Hybrid-loop stage compare now applies model-aware budget
control before handing truth context to the vision runtime. The first MVP uses
active runtime token/image limits plus a bounded model-name bias to trim
pairwise truth scope and ranked correction candidates when needed, and records
the result in `budget_control`. This prevents large assembled collections from
always expanding with one static payload shape.

## Objective

Prevent hybrid-loop payload blowups on assembled collections by making staged
truth/candidate scope and budget control adapt to the active model/runtime
limits instead of using one static expansion strategy.

## Business Problem

Recent real hybrid-loop runs exposed a second quality/reliability problem:

- large assembled collections can explode into too many pair checks and too
  much response payload
- `reference_iterate_stage_checkpoint(...)` can then stop with
  `input_budget_exceeded`
- the loop currently has too little runtime-aware control over:
  - how many pair checks to expand
  - how much truth detail to keep
  - how much candidate detail to emit
  - when to narrow scope automatically from collection to object-set / primary
    subset

This is especially wasteful when the active model/runtime can already tell us
its practical input/output limits.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/session_capabilities.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- hybrid-loop truth/candidate expansion can adapt to model/runtime budget
  limits instead of assuming one fixed payload envelope
- collection/object-set scope can be narrowed deterministically when the full
  pair graph would exceed the active model budget
- the loop degrades gracefully:
  - it keeps the highest-value truth findings
  - it keeps ranked correction candidates
  - it records when scope/detail was trimmed
- the resulting behavior is explicit and testable, not hidden in prompt-only
  heuristics

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py` when Blender-backed
  hybrid outputs are affected

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this follow-on changes hybrid-loop
  budget policy, scope trimming behavior, or model-aware runtime limits

## Status / Board Update

- this follow-on is closed
- `_docs/_TASKS/README.md` and the closed parent follow-on notes now point to
  the remaining open cross-domain refinement-routing follow-on
