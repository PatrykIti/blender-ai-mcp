# TASK-112: Programmatic Sculpt Region Tools

**Priority:** 🟡 Medium  
**Category:** Sculpt / LLM Reliability  
**Estimated Effort:** Medium  
**Dependencies:** None  
**Status:** ⏳ To Do

---

## Objective

Introduce a deterministic sculpt-like tool family that can be used programmatically by LLM clients without relying on Blender UI brush-stroke event paths.

---

## Problem

The current sculpt surface mixes two very different kinds of capability:

- `sculpt_auto`, which is actually programmatic and deterministic
- `sculpt_brush_*`, which mostly configure brush state and depend on manual interaction for real stroke execution

This is a poor fit for LLM automation:

- brush tools look like geometry-changing actions
- actual behavior depends on Blender UI/event context
- stroke replay is difficult to test and hard to make deterministic

---

## Product Direction

Do **not** make UI-brush stroke emulation the main LLM path.

Instead:

- keep `sculpt_auto` as-is
- keep existing `sculpt_brush_*` as compatibility/manual-assist tools
- add a new family of **programmatic region sculpt tools** for LLM use

The new family should become the preferred write-side sculpt surface for LLM workflows.

Current `sculpt_brush_*` tools should not be hard-removed immediately. They should remain available for compatibility/manual setups, but they should no longer be treated as the primary path for automated sculpting.

---

## Proposed First-Wave Tool Family

- `sculpt_deform_region`
  - deterministic “grab/move” replacement
  - deforms vertices in a radius around a center using a delta vector and falloff
- `sculpt_smooth_region`
  - local smoothing with deterministic iteration/strength controls
- `sculpt_inflate_region`
  - local normal-based expansion/contraction
- `sculpt_pinch_region`
  - local contraction toward a center/curve line

Possible later extensions:

- `sculpt_mask_region`
- `sculpt_flatten_region`
- `sculpt_layer_region`
- `sculpt_noise_region`

---

## Architectural Constraints

- tool contract must be deterministic and geometry-oriented, not viewport/event oriented
- implementation may live behind `sculpt_*` names even if the Blender-side algorithm uses mesh/BMesh operations instead of true sculpt brush operators
- keep Clean Architecture boundaries:
  - domain interfaces in `server/domain/tools/`
  - server handlers in `server/application/tool_handlers/`
  - Blender implementation in `blender_addon/application/handlers/`
  - MCP wrappers thin in `server/adapters/mcp/areas/`
- verification should use existing inspection tools where possible (`mesh_inspect`, `scene_snapshot_state`, `scene_compare_snapshot`)

---

## Repository Touchpoints

- `server/domain/tools/sculpt.py`
- `server/application/tool_handlers/sculpt_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/infrastructure/di.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/sculpt/*.json`
- `tests/unit/tools/sculpt/`
- `tests/e2e/tools/sculpt/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Work Breakdown

1. [TASK-112-01](./TASK-112-01_Deterministic_Region_Falloff_Engine.md)  
   deterministic region selection, falloff, symmetry, and shared parameter model

2. [TASK-112-02](./TASK-112-02_Programmatic_Deform_And_Grab_Replacement.md)  
   `sculpt_deform_region` as the true programmatic replacement for `sculpt_brush_grab`

3. [TASK-112-03](./TASK-112-03_Programmatic_Smooth_Inflate_Pinch_Tools.md)  
   local smooth/inflate/pinch tools built on the shared region engine

4. [TASK-112-04](./TASK-112-04_Surface_Metadata_Docs_And_Compatibility_Boundary.md)  
   metadata, docs, routing hints, and compatibility posture for old `sculpt_brush_*`

5. [TASK-112-05](./TASK-112-05_Tests_For_Programmatic_Sculpt_Tools.md)  
   unit + e2e coverage for deterministic sculpt region tools

---

## Acceptance Criteria

- the repo has at least one deterministic, LLM-safe sculpt deformation tool (`sculpt_deform_region`)
- local sculpt operations no longer depend on hidden manual brush interaction for core LLM use cases
- old `sculpt_brush_*` tools remain explicitly documented as manual/setup-only where applicable
- docs, metadata, and tests reflect the new recommended sculpt path
