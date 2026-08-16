# TASK-121-02-02: Reference Image Intake and Lifecycle API

**Parent:** [TASK-121-02](./TASK-121-02_Goal_And_Reference_Context_Session_Model.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The repo now has a first bounded reference-image intake surface via `reference_images(action=attach|list|remove|clear)`: local image paths are copied into session-scoped temp storage, normalized into one stable metadata shape, and kept reversible through remove/clear actions.

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
- normalize intake into one session-safe internal representation instead of making downstream backends parse arbitrary URLs or one-off file formats
- store reference metadata plus resolved temp storage paths in a stable session-aware structure
- keep backend loading separate from reference intake:
  - reference images resolve to normalized local temp paths / session metadata
  - model/runtime configuration is handled separately under the vision backend policy

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
