# TASK-114-01-01: Area Module Docstring and Product Wording Audit

**Parent:** [TASK-114-01](./TASK-114-01_Public_Tool_Semantics_And_Docstring_Audit.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

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
