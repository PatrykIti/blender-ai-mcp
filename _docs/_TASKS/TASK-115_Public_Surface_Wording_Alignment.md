# TASK-115: Public Surface Wording Alignment

**Priority:** 🔴 High  
**Category:** Product Wording / Surface Semantics  
**Estimated Effort:** Small  
**Dependencies:** TASK-114  
**Status:** ✅ Done

**Completion Summary:** The first public-surface wording cleanup wave is now complete. The highest-signal docs and MCP adapter docstrings no longer lead with the old “mega tools / LLM context optimization” framing, `modeling_add_modifier` is described as a controlled object-level non-destructive tool, and `router_*` wording now reflects goal-first session bootstrap and diagnostics semantics.

---

## Objective

Apply the first concrete wording/semantics fixes identified by `TASK-114` to the highest-signal public surface docs and MCP adapter docstrings.

---

## Scope

This wave covers the first P0 wording fixes:

- user-facing “mega tools / LLM context optimization” framing
- `modeling_add_modifier` wording cluster
- `router_*` wording cluster

This wave does **not** yet implement new measure/assert tools.

---

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/router.py`

---

## Success Criteria

- public docs stop leading with the old “mega tools for LLM context optimization” framing
- `modeling_add_modifier` wording is updated to the new layered product model
- router MCP tool wording aligns with goal-first production semantics

## Result

- public grouped-tool framing replaced the old “LLM context optimization / mega tools” language in the highest-signal docs
- `modeling_add_modifier` wording now aligns better with the new layered product model
- router MCP tool wording now describes goal-first session/bootstrap semantics more directly
