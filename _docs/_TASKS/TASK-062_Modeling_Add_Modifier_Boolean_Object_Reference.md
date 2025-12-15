# TASK-062: Fix `modeling_add_modifier` BOOLEAN object reference handling

**Status:** 🚨 To Do  
**Priority:** 🔴 High  
**Category:** Modeling Tools / Bug Fix  
**Estimated Effort:** Small  
**Created:** 2025-12-15  
**Dependencies:** None

---

## Overview

`modeling_add_modifier(..., modifier_type="BOOLEAN", properties={...})` currently cannot set the Boolean target when `properties["object"]` is passed as a string (object name). In Blender, `BooleanModifier.object` is a pointer to `bpy.types.Object`, so the modifier ends up with `object=None`. Applying the modifier can then fail with:

> `Modifier is disabled, skipping apply`

This blocks a very common game‑asset workflow: create cutter → Boolean difference → apply.

---

## Repro (current behavior)

1. Create `Well_Outer` and `Well_Cutter`.
2. Call:
   ```json
   modeling_add_modifier(
     name="Well_Outer",
     modifier_type="BOOLEAN",
     properties={"operation":"DIFFERENCE","object":"Well_Cutter","solver":"EXACT"}
   )
   ```
3. `scene_inspect(action="modifiers")` shows `object=None`.
4. `modeling_apply_modifier("Well_Outer", "BOOLEAN")` fails or does nothing.

---

## Root Cause

`blender_addon/application/handlers/modeling.py:ModelingHandler.add_modifier()` applies `properties` via:

```python
setattr(mod, prop, value)
```

For BOOLEAN:
- `prop="object"` expects an Object pointer, not a name string.
- the assignment fails (or is ignored), leaving the modifier without a target object.

---

## Proposed Fix

1. Resolve Boolean modifier object references in the addon handler:
   - If `properties["object"]` is `str`, resolve `bpy.data.objects.get(name)` and assign to `mod.object`.
   - Optionally accept alias `properties["object_name"]` (string) and map it to `mod.object` (clearer for MCP users).
2. Fail fast with a helpful error if the referenced object does not exist.
3. Keep the generic `setattr` path for non-pointer properties (`operation`, `solver`, …).

Optional extension (future): implement a generic resolver for RNA pointer properties (not only BOOLEAN).

---

## Acceptance Criteria

- [ ] Passing `properties={"object":"SomeObjectName"}` correctly sets `BooleanModifier.object`.
- [ ] `modeling_apply_modifier()` works when Boolean target exists.
- [ ] Clear validation error when `properties.object` references a missing object.
- [ ] Router metadata + docs explicitly describe the supported form.

---

## Implementation Checklist

- [ ] Add Boolean object-name resolution in `ModelingHandler.add_modifier()`.
- [ ] Update `server/adapters/mcp/areas/modeling.py` docstring for `modeling_add_modifier` (document Boolean `properties.object` as object name).
- [ ] Update router metadata: `server/router/infrastructure/tools_metadata/modeling/modeling_add_modifier.json` (examples + param description).
- [ ] Add unit test for Boolean object resolution in `tests/unit/tools/modeling/test_modeling_tools.py`.
- [ ] Add E2E test (optional) that confirms Boolean actually changes topology (face/vertex count changes).
- [ ] Add changelog entry under `_docs/_CHANGELOG/` (new file).

---

## Files to Modify

| Area | File | Change |
|------|------|--------|
| Addon | `blender_addon/application/handlers/modeling.py` | Resolve `properties.object` / `object_name` to `bpy.data.objects[...]` for BOOLEAN |
| MCP | `server/adapters/mcp/areas/modeling.py` | Docstring clarification (properties schema) |
| Router | `server/router/infrastructure/tools_metadata/modeling/modeling_add_modifier.json` | Metadata example + param description |
| Tests | `tests/unit/tools/modeling/test_modeling_tools.py` | Add unit test for BOOLEAN object resolution |
| Tests | `tests/e2e/...` | Add integration test (optional) |
| Docs | `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md` | Document Boolean modifier “object by name” behavior |

---

## Documentation Updates Required (after completion)

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-062_Modeling_Add_Modifier_Boolean_Object_Reference.md` | Mark ✅ Done + add completion date |
| `_docs/_TASKS/README.md` | Move task to ✅ Done + update statistics |
| `_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md` | Add an explicit BOOLEAN example for `properties.object` |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Align any boolean examples / expectations (if present) |
| `_docs/_CHANGELOG/*` | Add entry describing the fix and user‑visible behavior |

