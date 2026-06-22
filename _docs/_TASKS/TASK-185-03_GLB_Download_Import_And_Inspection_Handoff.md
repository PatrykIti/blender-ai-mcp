# TASK-185-03: GLB Download, Import, And Inspection Handoff

**Parent:** [TASK-185](./TASK-185_Optional_Generative_3D_Seed_Asset_Intake.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Import a generated seed asset into Blender through a bounded, main-thread-safe path and hand it to deterministic inspection/cleanup before guided workflows consume it.

**Repository Touchpoints:** `blender_addon/application/handlers/`, `blender_addon/infrastructure/rpc_server.py`, `server/application/tool_handlers/`, `server/adapters/rpc/`, `tests/e2e/`, `_docs/_ADDON/README.md`

## Implementation Notes

- Start with a local fixture GLB/OBJ proof before any live provider artifact.
- Enforce file size, extension, content-type, temporary-path, and cleanup
  constraints.
- After import, return created object names, collection, mesh statistics, and
  inspection hints; do not treat the import as final reconstruction.

## Runtime / Security Contract Notes

- import is mutating and must report Blender mode/selection impact
- imported assets are untrusted until inspected
- destructive cleanup must be a separate explicit action

## Tests To Add/Update

- Blender E2E fixture import and inspection handoff
- negative tests for missing file, unsupported extension, oversize artifact, and
  failed import

## Docs To Update

- `_docs/_ADDON/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- one local fixture asset can be imported through the supported Blender runner
- import returns deterministic inspection handoff data
- invalid artifacts fail with meaningful errors and no partial hidden state

## Validation Commands

- `git diff --check`
- `poetry run python scripts/run_e2e_tests.py`
