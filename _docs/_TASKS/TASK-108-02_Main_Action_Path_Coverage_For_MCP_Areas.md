# TASK-108-02: Main Action Path Coverage for MCP Areas

**Parent:** [TASK-108](./TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** TASK-101, TASK-103

---

## Objective

Add a deliberate main-path regression test for every MCP area module so the public surface is covered by behavior, not just by registration presence.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/armature.py`
- `server/adapters/mcp/areas/baking.py`
- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/curve.py`
- `server/adapters/mcp/areas/extraction.py`
- `server/adapters/mcp/areas/lattice.py`
- `server/adapters/mcp/areas/material.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/areas/system.py`
- `server/adapters/mcp/areas/text.py`
- `server/adapters/mcp/areas/uv.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `tests/unit/tools/`

---

## Planned Work

- build one coverage matrix for all area modules and mark the primary public action path per file
- add one happy-path delegation test per area module using the real public wrapper or mega-tool action
- add one representative validation or error-translation test where the area module does more than raw passthrough
- ensure registration helpers and public names stay aligned with the exercised tool path

---

## Acceptance Criteria

- every `server/adapters/mcp/areas/*.py` file is covered by at least one main public action-path test
- mega-tool areas cover action dispatch, not only registration/import behavior
- areas returning structured payloads keep deterministic dict/model outputs under test
- user-facing error or validation paths are covered wherever wrapper logic exists

## Completion Summary

The MCP area regression matrix now covers all public area modules with at least one main-path behavior test, including the previously missing:

- `modeling`
- `armature`
- `baking`
- `curve`
- `lattice`
- `sculpt`
- `text`
- `uv`
