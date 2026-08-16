# TASK-111: Modeling Modifier RPC Alignment and Sculpt Grab Boundary

**Priority:** 🟡 Medium  
**Category:** MCP / RPC Alignment / LLM UX  
**Estimated Effort:** Small  
**Dependencies:** None  
**Status:** ✅ Done

**Completion Summary:** Fixed the server-side RPC result mismatch for `modeling_add_modifier` and clarified that `sculpt_brush_grab` is a brush-setup tool, not an executed geometry-changing stroke.

---

## Objective

Remove one real runtime bug and one misleading product semantic around modeling/sculpt interactions.

---

## Problem

Two separate issues were exposed in real MCP usage:

- `modeling_add_modifier` succeeded in Blender but failed on the server because the addon returned a dict payload while the server-side handler still expected a plain string
- `sculpt_brush_grab` presented itself like a geometry-changing sculpt action even though the current implementation only configures the Grab brush and requires manual interaction to perform a stroke

---

## Solution

- Treat `modeling.add_modifier` like the structured addon RPC it already is
- Keep the public MCP response text for compatibility, but consume the structured dict result on the server
- Reword `sculpt_brush_grab` across addon, MCP adapter, router metadata, and docs so it explicitly states that no geometry is modified by the tool itself

---

## Repository Touchpoints

- `server/application/tool_handlers/modeling_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/router/infrastructure/tools_metadata/sculpt/sculpt_brush_grab.json`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/tools/modeling/test_modeling_handler_rpc.py`
- `tests/unit/tools/sculpt/test_sculpt_tools.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

---

## Acceptance Criteria

- `modeling_add_modifier` no longer fails on successful dict payloads from the addon
- `sculpt_brush_grab` no longer implies that geometry was changed when it only configured the brush
- user-facing docs and router metadata stay aligned with the actual behavior
- regression coverage exists for both the RPC alignment and the grab-brush semantic boundary
