# TASK-122-02: Creature Correction Macro Tool Wave

**Parent:** [TASK-122](./TASK-122_Hybrid_Vision_Truth_And_Correction_Macro_Wave.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The first macro leaf is now complete. `macro_attach_part_to_surface` is available as a bounded surface-attachment macro built on the existing relative-layout/contact verification stack, and the remaining creature-correction macro leaves stay open under this in-progress wave.

## Objective

Add bounded correction macros for the most common assembled-creature fixes that
vision/truth can detect but current atomics make too awkward to repair.

## Business Problem

The current macro layer is strong for hard-surface layout and finishing, but
creature/reference correction still lacks direct tools for:

- attaching parts onto a surface/body
- forcing contact/alignment
- pairing symmetric parts
- correcting head/body ratio
- shaping a tail arc
- posing simple limbs
- cleaning up part intersections

## Acceptance Criteria

- the correction loop has a usable bounded macro layer for assembled creatures
- repeated fixes do not require ad hoc atomics every time
- the macros are narrow and composable, not free-form mega tools

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `blender_addon/application/handlers/`
- `blender_addon/__init__.py`
- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`

## Completion Update Requirements

- every shipped macro leaf must update all required tool layers, docs, and tests for that macro
- add unit coverage for bounded macro contract/parameter behavior and E2E coverage when geometry or placement behavior changes
- add the historical `_docs/_CHANGELOG/*` entry and sync `_docs/_TASKS/README.md` when promoted board state changes

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-02-01](./TASK-122-02-01_macro_attach_part_to_surface.md) | Attach or seat a part onto another object’s surface/body |
| 2 | [TASK-122-02-02](./TASK-122-02-02_macro_align_part_with_contact.md) | Align one part and enforce practical contact/gap constraints |
| 3 | [TASK-122-02-03](./TASK-122-02-03_macro_place_symmetry_pair.md) | Place or correct mirrored part pairs such as ears/eyes/limbs |
| 4 | [TASK-122-02-04](./TASK-122-02-04_macro_adjust_head_body_proportion.md) | Correct large body-part ratio issues such as head/body scale |
| 5 | [TASK-122-02-05](./TASK-122-02-05_macro_adjust_tail_arc.md) | Correct segmented tail shape/arc/placement |
| 6 | [TASK-122-02-06](./TASK-122-02-06_macro_pose_simple_limbs.md) | Correct simple limb/foot placement and grounded posing |
| 7 | [TASK-122-02-07](./TASK-122-02-07_macro_cleanup_part_intersections.md) | Resolve or reduce obvious part intersections in a bounded way |
