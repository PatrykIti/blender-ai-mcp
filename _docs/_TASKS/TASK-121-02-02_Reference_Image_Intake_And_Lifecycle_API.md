# TASK-121-02-02: Reference Image Intake and Lifecycle API

**Parent:** [TASK-121-02](./TASK-121-02_Goal_And_Reference_Context_Session_Model.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Add the first reference-image intake surface for session-scoped use.

---

## Implementation Direction

- add a bounded tool family for actions such as:
  - attach/import reference image
  - list current references
  - remove one reference
  - clear session references
- accept practical inputs such as:
  - local file path
  - uploaded file handle / attachment reference when client/runtime supports it
- store reference metadata plus resolved temp storage paths in a stable session-aware structure

---

## Repository Touchpoints

- likely new MCP area under `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/infrastructure/tmp_paths.py`
- `tests/unit/adapters/mcp/`
- `_docs/_MCP_SERVER/README.md`

---

## Acceptance Criteria

- users can attach reference images to the active session without needing a full persistent asset system
- reference intake/lifecycle is structured, inspectable, and reversible
