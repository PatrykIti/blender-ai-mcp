# Export Tools Architecture

Export tools enable AI to save 3D content to various file formats for use in game engines, web applications, and other 3D software.

---

## 1. export_glb ✅ Done

Exports scene or selected objects to GLB/GLTF format.

**Tags:** `[OBJECT MODE][SCENE][SAFE]`

### Description
GLB is the binary variant of GLTF - ideal for web, game engines (Unity, Unreal, Godot). Supports PBR materials, animations, and skeletal rigs.

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filepath` | str | required | Output file path (must end with .glb or .gltf) |
| `export_selected` | bool | False | Export only selected objects (default: entire scene) |
| `export_animations` | bool | True | Include animations |
| `export_materials` | bool | True | Include materials and textures |
| `apply_modifiers` | bool | True | Apply modifiers before export |

### Example
```json
{
  "tool": "export_glb",
  "args": {
    "filepath": "/tmp/model.glb",
    "export_selected": false,
    "export_animations": true,
    "export_materials": true,
    "apply_modifiers": true
  }
}
```

### Behavior
- Auto-adds `.glb` extension if missing
- Creates directories if they don't exist
- Uses `GLB` format for `.glb` extension, `GLTF_SEPARATE` for `.gltf`

---

## 2. export_fbx ✅ Done

Exports scene or selected objects to FBX format.

**Tags:** `[OBJECT MODE][SCENE][SAFE]`

### Description
FBX is the industry standard for game engines and DCC interchange. Supports animations, armatures, blend shapes, and materials.

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filepath` | str | required | Output file path (must end with .fbx) |
| `export_selected` | bool | False | Export only selected objects |
| `export_animations` | bool | True | Include animations and armature |
| `apply_modifiers` | bool | True | Apply modifiers before export |
| `mesh_smooth_type` | str | "FACE" | Smoothing export method: OFF, FACE, EDGE |

### Example
```json
{
  "tool": "export_fbx",
  "args": {
    "filepath": "/tmp/model.fbx",
    "export_selected": false,
    "export_animations": true,
    "apply_modifiers": true,
    "mesh_smooth_type": "FACE"
  }
}
```

### Behavior
- Auto-adds `.fbx` extension if missing
- Creates directories if they don't exist
- Optimized bone axis settings for game engines (Y primary, X secondary)
- `add_leaf_bones` disabled for cleaner skeleton exports

---

## 3. export_obj ✅ Done

Exports scene or selected objects to OBJ format.

**Tags:** `[OBJECT MODE][SCENE][SAFE]`

### Description
OBJ is a simple, universal mesh format supported by virtually all 3D software. Creates .obj (geometry) and optionally .mtl (materials) files.

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filepath` | str | required | Output file path (must end with .obj) |
| `export_selected` | bool | False | Export only selected objects |
| `apply_modifiers` | bool | True | Apply modifiers before export |
| `export_materials` | bool | True | Export .mtl material file |
| `export_uvs` | bool | True | Include UV coordinates |
| `export_normals` | bool | True | Include vertex normals |
| `triangulate` | bool | False | Convert quads/ngons to triangles |

### Example
```json
{
  "tool": "export_obj",
  "args": {
    "filepath": "/tmp/model.obj",
    "export_selected": false,
    "apply_modifiers": true,
    "export_materials": true,
    "export_uvs": true,
    "export_normals": true,
    "triangulate": false
  }
}
```

### Behavior
- Auto-adds `.obj` extension if missing
- Creates directories if they don't exist
- Uses Blender's native `wm.obj_export` operator (Blender 3.3+)

---

## Format Comparison

| Feature | GLB/GLTF | FBX | OBJ |
|---------|----------|-----|-----|
| **PBR Materials** | ✅ Full | ✅ Partial | ❌ Basic |
| **Animations** | ✅ Yes | ✅ Yes | ❌ No |
| **Skeletal Rigs** | ✅ Yes | ✅ Yes | ❌ No |
| **File Size** | Small (binary) | Medium | Large (text) |
| **Web Support** | ✅ Excellent | ❌ No | ⚠️ Limited |
| **Game Engines** | ✅ All modern | ✅ Industry std | ✅ Universal |
| **Human Readable** | GLTF only | ❌ Binary | ✅ Text |

## Use Cases

### Web / Three.js / WebGL
→ Use `export_glb` - smallest file size, full PBR support

### Unity / Unreal Engine
→ Use `export_fbx` - industry standard, animation support

### 3D Printing / Legacy Software
→ Use `export_obj` - universal compatibility, simple format

### Asset Libraries / Archival
→ Use `export_glb` or `export_fbx` - preserve materials and animations

---

## Rules

1. **Prefix `export_`**: All export tools start with this prefix.
2. **Auto-extension**: Missing file extensions are added automatically.
3. **Directory Creation**: Parent directories are created if needed.
4. **Safe Operation**: Export does not modify the scene state.
5. **Object Mode**: Export works in Object Mode (will not change current mode).
