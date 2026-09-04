# TASK-109: Scene Camera Parameter UX Clarification

**Priority:** 🟡 Medium  
**Category:** MCP / LLM UX  
**Estimated Effort:** Small  
**Dependencies:** None  
**Status:** ✅ Done

**Completion Summary:** Clarified the public parameter naming around the scene camera helpers so LLM clients stop mixing `scene_camera_focus(object_name=...)` with `scene_camera_orbit(target_object=...)` and `scene_get_viewport(focus_target=...)`.

---

## Objective

Reduce avoidable parameter-name confusion in the public scene camera tool family.

---

## Problem

The public scene camera helpers use three similar but distinct target parameters:

- `scene_camera_focus(object_name=...)`
- `scene_camera_orbit(target_object=... | target_point=...)`
- `scene_get_viewport(focus_target=...)`

This is valid API design, but the distinction was not called out strongly enough in the public tool description and docs, which made it easy for LLM clients to generate invalid calls such as `scene_camera_focus(target=...)`.

---

## Solution

Clarify the parameter map in the MCP tool description and public docs/prompts, then add regression coverage at the real `tools/list` surface.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py`

---

## Acceptance Criteria

- `scene_camera_focus` explicitly documents that it uses `object_name`
- public docs/prompts distinguish `object_name`, `target_object`, and `focus_target`
- regression coverage checks the real public `tools/list` description seen by MCP clients
