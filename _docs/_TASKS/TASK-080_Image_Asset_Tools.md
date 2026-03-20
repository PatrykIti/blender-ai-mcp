# TASK-080: Image Asset Tools (List, Load, Export, Pack)

**Priority:** 🟡 Medium  
**Category:** Material/Asset Reconstruction  
**Estimated Effort:** Medium  
**Dependencies:** TASK-023  
**Status:** ⬜ To Do

---

## 🎯 Objective

Add tools to enumerate and manage image assets referenced by materials, so texture-driven appearance can be reconstructed 1:1.

---

## 📝 Documentation Updates

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-080_Image_Asset_Tools.md` | Track status and sub-tasks |
| `_docs/_TASKS/README.md` | Add to task list + stats |
| `_docs/_MCP_SERVER/README.md` | Add `image_manage` tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add `image_manage` |
| `_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md` | Document `image_manage` actions |
| `README.md` | Update tools tables |

---

## 🔧 Design

```python
@mcp.tool()
def image_manage(
    ctx: Context,
    action: Literal["list", "load", "export", "pack", "unpack", "set_colorspace"],
    image_name: Optional[str] = None,
    filepath: Optional[str] = None,
    output_path: Optional[str] = None,
    colorspace: Optional[str] = None,
) -> str:
    """
    [IMAGE][SAFE] Manage texture images used by materials.
    """
```

### Actions

- `list`: list all images with filepath, size, colorspace, users.
- `load`: load image from disk into Blender (create datablock).
- `export`: save image datablock to file for external use.
- `pack` / `unpack`: manage packed images.
- `set_colorspace`: set colorspace for a given image.

### Rules

- `list` should include `is_packed`, `source`, `colorspace_settings.name`.
- `export` should support overriding file format based on extension.
- Keep data transfer small; do not inline image bytes.

---

## 🧩 Implementation Checklist

| Layer | File | What to Add |
|------|------|-------------|
| Domain | `server/domain/tools/material.py` or new `image.py` | Image management interface |
| Application | `server/application/tool_handlers/*` | RPC wrappers |
| Adapter | `server/adapters/mcp/areas/image.py` | `image_manage` mega tool |
| Addon | `blender_addon/application/handlers/image.py` | Blender image handlers |
| Addon Init | `blender_addon/__init__.py` | Register RPC routes |
| Dispatcher | `server/adapters/mcp/dispatcher.py` | Tool map entry |
| Router Metadata | `server/router/infrastructure/tools_metadata/image/image_manage.json` | Tool metadata |
| Tests | `tests/unit/tools/image/test_image_manage.py` | Unit tests for list/load/export |

---

## ✅ Success Criteria

- Texture assets can be listed, loaded, and exported reliably.
- Colorspace and packing state are preserved for round-trip reconstruction.
