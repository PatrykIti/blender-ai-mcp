# TASK-114-01-01: Area Module Docstring and Product Wording Audit

**Parent:** [TASK-114-01](./TASK-114-01_Public_Tool_Semantics_And_Docstring_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** MCP area-module wording drift has been identified at the area level. The first pass shows that some existing docstrings still encode old product assumptions, especially around “preferred method”, “ALT TO”, setup-only semantics, and broad tool-role framing.

---

## Objective

Review MCP area module docstrings for wording that still encodes the old product model.

---

## Exact Audit Targets

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/areas/material.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/areas/router.py`

---

## Focus

- “preferred method” language that may now be outdated
- “mega tool” framing that is too broad or too old
- wording that implies a tool is a full workflow when it is only one step
- wording that does not reflect `atomic / macro / workflow` distinctions
- wording that implies visual intuition without verification

---

## Acceptance Criteria

- each area gets an audit list of docstring rewrites and rationale

## Audit Result

### Areas with Highest Drift

- `server/adapters/mcp/areas/modeling.py`
  - legacy “Preferred method…” / `ALT TO` phrasing
  - needs review against the new macro/workflow/verification model

- `server/adapters/mcp/areas/router.py`
  - still carries older framing around “LLM communicates intent to router”
  - needs a cleaner product wording pass after `TASK-113`

- `server/adapters/mcp/areas/sculpt.py`
  - internal/setup-only brush tools still exist and need a later wording cleanup so internal helper semantics are clearly distinguished from public production tools

### Areas with Lower Drift

- `scene.py`
  - mostly aligned, but still uses legacy “internal function exposed via mega tool” comments that are implementation-level rather than product-level

- `mesh.py`
  - same issue: internal comments and some historical mega-tool framing remain, though public semantics are generally closer to current policy

### Fix Priorities

- `P0`: modeling + router wording
- `P1`: sculpt internal helper wording and remaining public semantics cleanup
- `P2`: implementation-level comments that can be normalized later
