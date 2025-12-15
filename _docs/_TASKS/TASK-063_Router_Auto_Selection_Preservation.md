# TASK-063: Router – prevent destructive `auto_select_all` for selection‑based mesh tools

**Status:** 🚨 To Do  
**Priority:** 🔴 High  
**Category:** Router / Safety / UX  
**Estimated Effort:** Medium  
**Created:** 2025-12-15  
**Dependencies:** TASK-039 (Router Supervisor), TASK-061 (API alignment)

---

## Overview

`ToolCorrectionEngine` may inject `mesh_select(action="all")` before selection‑based mesh tools (e.g. `mesh_extrude_region`, `mesh_bevel`). If the router’s `SceneContext.has_selection` is stale/incorrect, this overwrites the user’s explicit edit‑mode selection and applies operations to the whole mesh.

This is a correctness + UX + safety issue because it can silently destroy topology.

---

## Repro (observed)

In a fast sequence (Edit Mode):
1. Select a subset (boundary edges / faces).
2. Run a selection‑based tool (`mesh_extrude_region`, `mesh_bevel`, …).
3. Router prepends `mesh_select(action="all")` → tool runs on entire mesh.

This can happen even when selection exists due to cached scene context (`SceneContextAnalyzer` TTL) and quickly changing edit‑mode selection.

---

## Root Cause

- `server/router/application/engines/tool_correction_engine.py` injects `mesh_select(all)` when `not context.has_selection`.
- `server/router/application/analyzers/scene_context_analyzer.py` can return cached `SceneContext` for up to `cache_ttl` seconds, including stale edit‑mode selection counts.
- Result: false `has_selection=False` → destructive selection overwrite.

---

## Proposed Fix (preferred)

Make auto-selection **non-destructive by default**:

1. Refresh selection state whenever it is used for correction:
   - In `SceneContextAnalyzer.analyze()`: if returning cached context, refresh edit‑mode selection counts (via `scene.list_selection` and/or `scene.inspect_mesh_topology`) when `mode == EDIT`.
   - Keep heavy context cached (objects/dimensions/materials), but treat selection as “hot” data.
2. Adjust correction policy:
   - Only inject `mesh_select(all)` when selection is confidently empty.
   - If selection state is unknown/uncertain, do **not** change selection; let the tool run (or fail) and fix reactively based on the error.

Optional: introduce a router config knob (`auto_select_strategy: never|if_empty|always`) defaulting to `if_empty`.

---

## Acceptance Criteria

- [ ] Router never injects `mesh_select(action="all")` when there is an edit‑mode selection (`selected_verts|edges|faces > 0`).
- [ ] Selection state is accurate even for rapid sequences (select → tool call within <1s).
- [ ] When selection is truly empty, router behavior is still helpful (either inject select‑all safely or return an actionable error).
- [ ] Regression tests cover the stale-selection case.

---

## Implementation Checklist

- [ ] Update `SceneContextAnalyzer` to refresh selection data even when returning cached context (or cache selection separately with TTL=0).
- [ ] Update `ToolCorrectionEngine.correct()` selection logic to treat “uncertain selection” as “do not auto‑select”.
- [ ] Add unit tests:
  - [ ] `tests/unit/router/application/test_scene_context_analyzer.py`: cached context still reflects updated selection.
  - [ ] `tests/unit/router/application/test_tool_correction_engine.py`: no injection when selection exists.
- [ ] Add E2E test (optional) reproducing “select subset → extrude/bevel → selection preserved”.
- [ ] Update docs/examples that imply router will “helpfully select all” before selection‑based tools.

---

## Files to Modify

| Area | File | Change |
|------|------|--------|
| Router | `server/router/application/analyzers/scene_context_analyzer.py` | Refresh selection despite cache |
| Router | `server/router/application/engines/tool_correction_engine.py` | Safer auto‑selection policy |
| Router | `server/router/application/config/router_config.py` | (Optional) config knob for policy |
| Tests | `tests/unit/router/application/test_scene_context_analyzer.py` | Add cache/selection regression |
| Tests | `tests/unit/router/application/test_tool_correction_engine.py` | Ensure no `mesh_select(all)` injection |
| Docs | `_docs/_ROUTER/README.md` | Clarify router selection correction strategy |

---

## Documentation Updates Required (after completion)

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-063_Router_Auto_Selection_Preservation.md` | Mark ✅ Done + add completion date |
| `_docs/_TASKS/README.md` | Move task to ✅ Done + update statistics |
| `_docs/_ROUTER/README.md` | Describe non‑destructive selection behavior |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Recommend explicit selection calls; note selection preservation |
| `_docs/_CHANGELOG/*` | Add entry describing behavioral change |

