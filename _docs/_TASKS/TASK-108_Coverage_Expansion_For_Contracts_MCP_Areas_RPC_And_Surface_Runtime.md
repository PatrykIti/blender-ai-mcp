# TASK-108: Coverage Expansion for Contracts, MCP Areas, RPC Alignment, and Surface Runtime

**Priority:** 🟡 Medium  
**Category:** Testing / Coverage Hardening  
**Estimated Effort:** Medium  
**Dependencies:** TASK-089, TASK-093, TASK-101, TASK-103, TASK-105, TASK-106, TASK-107  
**Status:** 🚧 In Progress

---

## Objective

Close the next high-value coverage gaps across the MCP-facing product surface and the server-side RPC boundary.

This wave focuses on four areas that still have a high regression risk relative to their product importance:

- contract models in `server/adapters/mcp/contracts/*.py` vs real handler payloads
- MCP area modules in `server/adapters/mcp/areas/*.py` for main public action paths
- server-side handlers in `server/application/tool_handlers/` where RPC result types must stay aligned
- FastMCP surface behavior for profiles, `list_tools`, pagination, and visibility

---

## Problem

The repo already has broad unit coverage, but these slices can still drift in ways that are expensive to catch late:

- structured MCP contracts can reject real payloads that handlers already return
- thin MCP wrappers can look covered while their primary action path or error translation stays untested
- RPC result helpers enforce strict string/dict/list expectations, so one addon/server mismatch can break otherwise successful operations
- surface-shaping behavior can regress at runtime even if individual policy helpers still pass

Recent fixes in TASK-105 through TASK-107 show that these are not hypothetical risks.

---

## Business Outcome

Turn the remaining high-risk test gaps into explicit regression matrices so the repo catches:

- contract drift before it hits clients
- handler/addon result mismatches before runtime failures
- area-wrapper regressions before they leak into public MCP behavior
- surface-profile visibility/listing regressions before they change discovery UX

## Progress Update

The first implementation batch is now in place:

- direct unit coverage for `_rpc_utils.py`
- representative server-side RPC alignment tests for `scene`, `collection`, `material`, and `uv` handlers
- additional MCP area main-path tests for `armature`, `baking`, `curve`, `lattice`, `sculpt`, `text`, and `uv`
- regression coverage for workflow-catalog chunk-progress payloads, correction-audit nested contract payloads, and phase-shaped search results

---

## Implementation Constraints

Follow the repo boundaries already established in AGENTS.md:

- contract tests must validate real or handler-shaped payloads instead of toy-only data
- MCP area tests should keep adapters thin and focus on delegation, output shape, and user-facing error behavior
- RPC alignment tests must preserve current `RpcResponse` semantics and exercise the explicit narrowing helpers
- surface runtime tests must keep FastMCP platform responsibilities separate from router policy responsibilities

Keep component pagination and payload pagination distinct, consistent with TASK-093.

---

## Scope

This task covers:

- contract payload parity
- main MCP action-path coverage
- RPC result type alignment on the server side
- runtime surface/profile/listing/visibility regression coverage

This task does not cover:

- new tool implementation
- Blender E2E geometry behavior outside existing tool surfaces
- router semantic matching or workflow-quality changes

---

## Success Criteria

- every contract module has at least one parity test against a real handler-shaped payload
- every MCP area module has at least one main-path regression test on its public surface
- RPC result helper expectations are explicitly covered for representative handlers
- surface profiles keep their expected listing, visibility, and pagination behavior under unit-test coverage

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Build a contract-to-payload parity matrix across all structured MCP contracts.
2. Fill main-path coverage gaps across MCP area registration and dispatch wrappers.
3. Harden server-side handler tests around strict RPC result narrowing.
4. Expand the FastMCP runtime matrix for profiles, `list_tools`, pagination, and visibility.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-108-01](./TASK-108-01_Contract_Payload_Parity_Across_MCP_Contracts.md) | Validate contracts against real handler payload shapes |
| 2 | [TASK-108-02](./TASK-108-02_Main_Action_Path_Coverage_For_MCP_Areas.md) | Cover main action paths for all MCP area modules |
| 3 | [TASK-108-03](./TASK-108-03_RPC_Result_Type_Alignment_For_Server_Handlers.md) | Harden server-side handlers against RPC result drift |
| 4 | [TASK-108-04](./TASK-108-04_Surface_Profile_List_Tools_Pagination_And_Visibility_Matrix.md) | Expand runtime coverage for profiles, listings, and visibility |
