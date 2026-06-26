# TASK-200: Mesh Bevel Mega-Tool Action

> Example task template for `blender-ai-mcp`. It follows the repository's real
> conventions (see `AGENTS.md` → Task Governance / Task Specification Standards):
> H1 is `# TASK-###[-NN]: Title` (no `# FileName:` line), slug words use
> underscores, numeric ID segments use hyphens, and `**Status:**` uses the
> canonical vocabulary. Copy this shape; do not copy the example content.

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Mesh Editing
**Created:** 2026-06-25
**Dependencies:** TASK-020 (Scene Context Mega Tool), TASK-011-X (Mode Switching)

---

## Objective

Add a deterministic `bevel` action to the `mesh_*` mega tool so an LLM client can
chamfer or round selected edges without raw `bpy` code, with inspectable results
and edit-mode selection preserved across the operation.

## Repository Touchpoints

| Path | Expected Ownership | Why In Scope |
|------|--------------------|--------------|
| `server/domain/tools/mesh.py` | Domain | Bevel action contract and typed parameter model |
| `server/application/tool_handlers/mesh_handlers.py` | Application | RPC-backed handler implementing the contract |
| `blender_addon/application/handlers/mesh_handlers.py` | Addon | `bpy`/bmesh bevel execution on the main thread |
| `blender_addon/__init__.py` | Addon | RPC action registration |
| `server/adapters/mcp/areas/mesh.py` | Adapter | Expose the action on the `mesh_*` mega tool |
| `server/adapters/mcp/dispatcher.py` | Adapter | Dispatch mapping for router/internal execution |
| `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json` | Router | Metadata so the action is router-aware |
| `tests/unit/...` | Tests | Handler/param validation with mocked RPC |
| `tests/e2e/...` | Tests | Real Blender geometry + selection-preservation check |

## Implementation Notes

Expected control flow (server handler):

```python
def bevel(self, params: MeshBevelParams) -> ToolResult:
    self._require_edit_mode()
    response = self._rpc.call("mesh.bevel", params.model_dump())
    return unwrap_mesh_result(response)
```

Error cases:

- not in edit mode -> `mesh_wrong_mode`;
- empty selection -> `mesh_no_selection`;
- invalid width/segments -> `mesh_invalid_parameters` (reject unknown fields).

## Security And Runtime Contract

- Visibility: public action on the `mesh_*` mega tool.
- Mutating: changes geometry; must preserve edit-mode selection state where
  possible (documented project goal).
- Validate parameters schema-first; reject unknown/unsupported fields.
- No external-provider egress; local Blender RPC only.

## Tests To Add/Update

- Unit: parameter validation, mode/selection guards, and RPC unwrap (mocked).
- E2E: bevel a known cube edge loop in Blender, assert resulting face/edge counts
  and that the prior selection survives.

## Docs To Update

- `_docs/AVAILABLE_TOOLS_SUMMARY.md` (tool inventory).
- `_docs/_MCP_SERVER/README.md` (surface) if exposure changes.
- `_docs/_ROUTER/TOOLS/README.md` checklist for the router-facing metadata.

## Changelog Impact

Add a `_docs/_CHANGELOG/*.md` entry referencing TASK-200 and prepend its index
row in `_docs/_CHANGELOG/README.md`.

## Acceptance Criteria

- `mesh_*` exposes a `bevel` action with typed parameters and structured errors.
- Edit-mode selection is preserved across the operation.
- Unit and E2E coverage pass; router metadata schema validation stays green.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/ -v` (run the targeted mesh tests first)
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- Update `_docs/_TASKS/README.md` board status and statistics when this advances.

## Completion Summary

To be completed by the implementer.
