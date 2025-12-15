# 111 - 2025-12-15: modeling_add_modifier BOOLEAN supports object name

**Status**: ✅ Completed  
**Type**: Bug Fix / Tooling UX  
**Task**: [TASK-062](../_TASKS/TASK-062_Modeling_Add_Modifier_Boolean_Object_Reference.md)

---

## Summary

Fixed `modeling_add_modifier` so `BOOLEAN` modifiers can reliably set the target/cutter object when callers pass the object **by name** (string) via `properties.object` (or `properties.object_name`).

This unblocks a common asset workflow: create cutter → Boolean difference → apply modifier.

---

## Changes

- Addon: `ModelingHandler.add_modifier()` resolves Boolean `properties.object` / `object_name` from a string into `bpy.data.objects[<name>]` and assigns it to `BooleanModifier.object`.
- Validation: missing target object now raises a clear `ValueError` (instead of silently leaving `object=None`).
- Docs/metadata: clarified how to pass Boolean target object by name.
- Tests: added unit coverage for both `object` and `object_name` forms + missing-object error case.

---

## Files Modified (high level)

- Addon:
  - `blender_addon/application/handlers/modeling.py`
- MCP:
  - `server/adapters/mcp/areas/modeling.py`
- Router metadata:
  - `server/router/infrastructure/tools_metadata/modeling/modeling_add_modifier.json`
- Tests:
  - `tests/unit/tools/modeling/test_modeling_tools.py`
- Docs:
  - `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Validation

```bash
poetry run pytest tests/unit/tools/modeling -q
```

