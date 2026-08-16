# TASK-108-01: Contract Payload Parity Across MCP Contracts

**Parent:** [TASK-108](./TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** TASK-089, TASK-107

---

## Objective

Prove that every structured MCP contract still accepts the payload shapes actually returned by the current handlers and MCP adapters.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/base.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/mesh.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/contracts/workflow_catalog.py`
- `server/adapters/mcp/contracts/correction_audit.py`
- `tests/unit/tools/scene/`
- `tests/unit/tools/mesh/`
- `tests/unit/router/application/`
- `tests/unit/adapters/mcp/`

---

## Planned Work

- map each contract file to the public tool/action paths that produce its payload
- replace hand-crafted toy payloads with fixtures or inline samples that mirror real handler output
- add parity tests for paging fields, assistant payloads, clarification payloads, and summary variants where applicable
- add explicit failure-path tests for missing or unexpected fields on the highest-risk contracts

---

## Acceptance Criteria

- each contract module has at least one success-path parity test based on a real handler-shaped payload
- contract validation covers both structured-first and compatibility-sensitive paths where the surface supports both
- known drift-prone top-level fields such as pagination and summary metadata are pinned by tests
- contract failures remain explicit and localized to the violated field set

## Completion Summary

Added an explicit parity matrix for representative payloads across:

- `scene`
- `mesh`
- `router`
- `workflow_catalog`
- `correction_audit`

The contract suite now validates both direct construction paths and MCP-returned response envelopes for the current structured surface.
