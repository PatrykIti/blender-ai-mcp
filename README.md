# blender-ai-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://github.com/PatrykIti/blender-ai-mcp/pkgs/container/blender-ai-mcp)
[![CI Status](https://github.com/PatrykIti/blender-ai-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/PatrykIti/blender-ai-mcp/actions)

> **💡 Support the Project**
>
> This project is currently developed after hours as a passion project. Creating a stable bridge between AI and Blender's complex API requires significant time and effort.
>
> If you find this tool useful or want to accelerate the development of advanced features (like *Edit Mode tools*, *Auto-Rigging*, or *Macro Generators*), please consider supporting the project. Your sponsorship allows me to dedicate more time to:
> *   Implementing critical **Mesh Editing Tools** (Extrude, Bevel, Loop Cut).
> *   Creating high-level **Macro Tools** (e.g., "Create Human Blockout", "Organify").
> *   Ensuring day-one support for new Blender versions.
>
> [**💖 Sponsor on GitHub**](https://github.com/sponsors/PatrykIti) | [**☕ Buy me a coffee**](https://buymeacoffee.com/PatrykIti)

**Modular MCP Server + Blender Addon for AI-Driven 3D Modeling.**

Enable LLMs (Claude, ChatGPT) to control Blender reliably. Built with **Clean Architecture** for stability and scalability.

<video src="demo-mcp-server.mp4" controls="controls" style="max-width: 100%;">
  <a href="demo-mcp-server.mp4">Watch demo video</a>
</video>

---

## 🚀 Why use this MCP Server instead of raw Python code?

Most AI solutions for Blender rely on asking the LLM to "write a Python script". This often fails because:
1.  **Hallucinations**: AI frequently uses outdated `bpy` API methods (mixing Blender 2.8 with 4.0).
2.  **Context Errors**: Running operators requires specific context (active window, selected object, correct mode). Raw scripts often crash Blender due to `poll()` failures.
3.  **No Feedback Loop**: If a script fails, the AI doesn't know why. Our MCP server returns precise error messages.
4.  **Safety**: Executing arbitrary Python code is risky. Our tools are sandboxed endpoints with validated inputs.

**Blender AI MCP** acts as a stable *Translation Layer*, handling the complexity of Blender's internal state machine so the AI can focus on creativity.

---

## 🗺️ Roadmap & Capabilities

> **Legend:** ✅ Done | 🚧 To Do

Our goal is to enable AI to model complex 3D assets—from organs and biological structures to hard-surface precision parts (cars, devices).

---

### Scene Tools (`scene_*`)

Object Mode operations for scene management and inspection.

| Tool | Description | Status |
|------|-------------|--------|
| `scene_list_objects` | List all objects in scene | ✅ |
| `scene_delete_object` | Delete object by name | ✅ |
| `scene_clean_scene` | Remove all objects | ✅ |
| `scene_duplicate_object` | Duplicate object | ✅ |
| `scene_set_active_object` | Set active object | ✅ |
| `scene_get_viewport` | Capture viewport image (AI vision) | ✅ |
| `scene_get_mode` | Report current Blender mode | ✅ |
| `scene_list_selection` | List selected objects/components | ✅ |
| `scene_inspect_object` | Detailed object info | ✅ |
| `scene_snapshot_state` | Capture scene snapshot | ✅ |
| `scene_compare_snapshot` | Compare two snapshots | ✅ |
| `scene_inspect_material_slots` | Material slot assignments | ✅ |
| `scene_inspect_mesh_topology` | Topology stats | ✅ |
| `scene_inspect_modifiers` | Modifier stack info | ✅ |

---

### Modeling Tools (`modeling_*`)

Object Mode operations for creating and transforming objects.

| Tool | Description | Status |
|------|-------------|--------|
| `modeling_create_primitive` | Create cube, sphere, cylinder, etc. | ✅ |
| `modeling_transform_object` | Move, rotate, scale objects | ✅ |
| `modeling_add_modifier` | Add modifier to object | ✅ |
| `modeling_apply_modifier` | Apply (bake) modifier | ✅ |
| `modeling_list_modifiers` | List modifiers on object | ✅ |
| `modeling_convert_to_mesh` | Convert curve/text to mesh | ✅ |
| `modeling_join_objects` | Join multiple objects | ✅ |
| `modeling_separate_object` | Separate by loose parts/material | ✅ |
| `modeling_set_origin` | Set object origin point | ✅ |

---

### Mesh Tools (`mesh_*`)

Edit Mode operations for geometry manipulation.

#### Selection
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_select_all` | Select/deselect all geometry | ✅ |
| `mesh_select_by_index` | Select by vertex/edge/face index | ✅ |
| `mesh_select_linked` | Select connected geometry | ✅ |
| `mesh_select_more` | Grow selection | ✅ |
| `mesh_select_less` | Shrink selection | ✅ |
| `mesh_select_boundary` | Select boundary edges | ✅ |
| `mesh_select_loop` | Select edge loop | ✅ |
| `mesh_select_ring` | Select edge ring | ✅ |
| `mesh_select_by_location` | Select by 3D position | ✅ |
| `mesh_get_vertex_data` | Get vertex positions | ✅ |

#### Core Operations
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_extrude_region` | Extrude selected faces | ✅ |
| `mesh_delete_selected` | Delete selected geometry | ✅ |
| `mesh_fill_holes` | Fill holes with faces | ✅ |
| `mesh_bevel` | Bevel edges/vertices | ✅ |
| `mesh_loop_cut` | Add loop cuts | ✅ |
| `mesh_inset` | Inset faces | ✅ |
| `mesh_boolean` | Boolean operations | ✅ |
| `mesh_merge_by_distance` | Merge nearby vertices | ✅ |
| `mesh_subdivide` | Subdivide geometry | ✅ |

#### Transform & Geometry
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_transform_selected` | Move/rotate/scale selected geometry | ✅ |
| `mesh_bridge_edge_loops` | Bridge two edge loops | ✅ |
| `mesh_duplicate_selected` | Duplicate selected geometry | ✅ |

#### Deformation
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_smooth` | Smooth vertices | ✅ |
| `mesh_flatten` | Flatten to plane | ✅ |
| `mesh_randomize` | Randomize vertex positions | ✅ |
| `mesh_shrink_fatten` | Move along normals | ✅ |

#### Precision Tools
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_bisect` | Cut mesh with plane | ✅ |
| `mesh_edge_slide` | Slide edges along topology | ✅ |
| `mesh_vert_slide` | Slide vertices along edges | ✅ |
| `mesh_triangulate` | Convert to triangles | ✅ |
| `mesh_remesh_voxel` | Voxel remesh | ✅ |

#### Procedural
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_spin` | Spin/lathe geometry around axis | ✅ |
| `mesh_screw` | Create spiral/helix geometry | ✅ |
| `mesh_add_vertex` | Add single vertex | ✅ |
| `mesh_add_edge_face` | Create edge/face from selection | ✅ |

#### Vertex Groups
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_list_groups` | List vertex groups | ✅ |
| `mesh_create_vertex_group` | Create new vertex group | ✅ |
| `mesh_assign_to_group` | Assign vertices to group | ✅ |
| `mesh_remove_from_group` | Remove vertices from group | ✅ |

---

### Curve Tools (`curve_*`)

Curve creation and conversion.

| Tool | Description | Status |
|------|-------------|--------|
| `curve_create` | Create Bezier/NURBS/Path/Circle curve | ✅ |
| `curve_to_mesh` | Convert curve to mesh | ✅ |

---

### Collection Tools (`collection_*`)

Collection management and hierarchy.

| Tool | Description | Status |
|------|-------------|--------|
| `collection_list` | List all collections | ✅ |
| `collection_list_objects` | List objects in collection | ✅ |
| `collection_manage` | Create/delete/move collections | 🚧 |

---

### Material Tools (`material_*`)

Material creation and assignment.

| Tool | Description | Status |
|------|-------------|--------|
| `material_list` | List all materials | ✅ |
| `material_list_by_object` | List materials on object | ✅ |
| `material_create` | Setup PBR materials | 🚧 |
| `material_assign` | Assign to objects/faces | 🚧 |
| `material_set_params` | Adjust roughness, metallic, etc. | 🚧 |
| `material_set_texture` | Bind image textures | 🚧 |

---

### UV Tools (`uv_*`)

UV mapping operations.

| Tool | Description | Status |
|------|-------------|--------|
| `uv_list_maps` | List UV maps on object | ✅ |
| `uv_unwrap` | Smart UV Project / Cube Projection | 🚧 |
| `uv_pack_islands` | Pack UV islands | 🚧 |

---

### System Tools (`system_*`)

Global project-level operations.

| Tool | Description | Status |
|------|-------------|--------|
| `system_set_mode` | High-level mode switching | 🚧 |
| `system_undo` | Safe undo for AI | 🚧 |
| `system_redo` | Safe redo for AI | 🚧 |
| `system_save_file` | Save .blend file | 🚧 |
| `system_new_file` | Create new file | 🚧 |
| `system_snapshot` | Quick save/restore checkpoints | 🚧 |

---

### Export Tools (`export_*`)

File export operations.

| Tool | Description | Status |
|------|-------------|--------|
| `export_glb` | Export to GLB format | 🚧 |
| `export_fbx` | Export to FBX format | 🚧 |
| `export_obj` | Export to OBJ format | 🚧 |

---

### Macro Tools (`macro_*`)

High-level abstractions where one command executes hundreds of Blender operations.

| Tool | Description | Status |
|------|-------------|--------|
| `macro_organify` | Convert blockouts to organic shapes | 🚧 |
| `macro_create_phone_base` | Generate smartphone chassis | 🚧 |
| `macro_human_blockout` | Generate proportional human mesh | 🚧 |
| `macro_retopologize` | Automate low-poly conversion | 🚧 |
| `macro_panel_cut` | Hard-surface panel cutting | 🚧 |
| `macro_lowpoly_convert` | Reduce polycount preserving silhouette | 🚧 |
| `macro_cleanup_all` | Scene-wide mesh cleanup | 🚧 |

---

### Sculpting Tools (`sculpt_*`)

Organic shaping and sculpt workflows.

| Tool | Description | Status |
|------|-------------|--------|
| `sculpt_auto` | High-level sculpt macro | 🚧 |
| `sculpt_brush_smooth` | Smooth brush | 🚧 |
| `sculpt_brush_grab` | Grab brush | 🚧 |
| `sculpt_brush_crease` | Crease brush | 🚧 |

---

## 🧠 LLM Context Optimization

> Unified "mega tools" that consolidate multiple related operations to reduce LLM context usage.

### Scene Mega Tools

| Mega Tool | Actions | Savings | Status |
|-----------|---------|---------|--------|
| `scene_context` | mode, selection | -1 | ✅ |
| `scene_create` | light, camera, empty | -2 | ✅ |
| `scene_inspect` | object, topology, modifiers, materials | -3 | ✅ |

### Mesh Mega Tools

| Mega Tool | Actions | Savings | Status |
|-----------|---------|---------|--------|
| `mesh_select` | all, none, linked, more, less, boundary | -4 | ✅ |
| `mesh_select_targeted` | by_index, loop, ring, by_location | -3 | ✅ |

**Total:** 18 tools → 5 mega tools (**-13 definitions** for LLM context)

---

## 🚀 Quick Start

### 1. Install the Blender Addon
1. Download `blender_ai_mcp.zip` from the [Releases Page](../../releases).
2. Open Blender -> Edit -> Preferences -> Add-ons.
3. Click **Install...** and select the zip file.
4. Enable the addon. It will start a local server on port `8765`.

### 2. Configure your MCP Client (Cline / Claude Code)

We recommend using Docker to run the MCP Server.

**Cline Configuration (`cline_mcp_settings.json`):**

**For macOS/Windows:**
```json
{
  "mcpServers": {
    "blender-ai-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ],
      "disabled": false,
      "autoApprove": [
        "scene_list_objects",
        "scene_delete_object",
        "scene_clean_scene",
        "scene_duplicate_object",
        "scene_set_active_object",
        "scene_get_viewport",
        "scene_set_mode",
        "scene_context",
        "scene_create",
        "scene_inspect",
        "scene_snapshot_state",
        "scene_compare_snapshot",
        "collection_list",
        "collection_list_objects",
        "material_list",
        "material_list_by_object",
        "uv_list_maps",
        "modeling_create_primitive",
        "modeling_transform_object",
        "modeling_add_modifier",
        "modeling_apply_modifier",
        "modeling_convert_to_mesh",
        "modeling_join_objects",
        "modeling_separate_object",
        "modeling_set_origin",
        "modeling_list_modifiers",
        "mesh_select",
        "mesh_select_targeted",
        "mesh_delete_selected",
        "mesh_extrude_region",
        "mesh_fill_holes",
        "mesh_bevel",
        "mesh_loop_cut",
        "mesh_inset",
        "mesh_boolean",
        "mesh_merge_by_distance",
        "mesh_subdivide",
        "mesh_smooth",
        "mesh_flatten",
        "mesh_list_groups",
        "mesh_get_vertex_data",
        "mesh_randomize",
        "mesh_shrink_fatten",
        "mesh_create_vertex_group",
        "mesh_assign_to_group",
        "mesh_remove_from_group",
        "mesh_bisect",
        "mesh_edge_slide",
        "mesh_vert_slide",
        "mesh_triangulate",
        "mesh_remesh_voxel",
        "mesh_transform_selected",
        "mesh_bridge_edge_loops",
        "mesh_duplicate_selected",
        "mesh_spin",
        "mesh_screw",
        "mesh_add_vertex",
        "mesh_add_edge_face",
        "curve_create",
        "curve_to_mesh"
      ]
    }
  }
}
```

**For Linux:**
```json
{
  "mcpServers": {
    "blender-ai-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "host",
        "-e", "BLENDER_RPC_HOST=127.0.0.1",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ],
      "disabled": false,
      "autoApprove": [
        "scene_list_objects",
        "scene_delete_object",
        "scene_clean_scene",
        "scene_duplicate_object",
        "scene_set_active_object",
        "scene_get_viewport",
        "scene_set_mode",
        "scene_context",
        "scene_create",
        "scene_inspect",
        "scene_snapshot_state",
        "scene_compare_snapshot",
        "collection_list",
        "collection_list_objects",
        "material_list",
        "material_list_by_object",
        "uv_list_maps",
        "modeling_create_primitive",
        "modeling_transform_object",
        "modeling_add_modifier",
        "modeling_apply_modifier",
        "modeling_convert_to_mesh",
        "modeling_join_objects",
        "modeling_separate_object",
        "modeling_set_origin",
        "modeling_list_modifiers",
        "mesh_select",
        "mesh_select_targeted",
        "mesh_delete_selected",
        "mesh_extrude_region",
        "mesh_fill_holes",
        "mesh_bevel",
        "mesh_loop_cut",
        "mesh_inset",
        "mesh_boolean",
        "mesh_merge_by_distance",
        "mesh_subdivide",
        "mesh_smooth",
        "mesh_flatten",
        "mesh_list_groups",
        "mesh_get_vertex_data",
        "mesh_randomize",
        "mesh_shrink_fatten",
        "mesh_create_vertex_group",
        "mesh_assign_to_group",
        "mesh_remove_from_group",
        "mesh_bisect",
        "mesh_edge_slide",
        "mesh_vert_slide",
        "mesh_triangulate",
        "mesh_remesh_voxel",
        "mesh_transform_selected",
        "mesh_bridge_edge_loops",
        "mesh_duplicate_selected",
        "mesh_spin",
        "mesh_screw",
        "mesh_add_vertex",
        "mesh_add_edge_face",
        "curve_create",
        "curve_to_mesh"
      ]
    }
  }
}
```

**For GitHub Copilot CLI:**
Copilot uses a slightly different config structure. Ensure you map the temp directory properly if you want file outputs.

```json
{
  "mcpServers": {
    "blender-ai-mcp": {
      "type": "local",
      "command": "docker",
      "tools": [
        "*"
      ],
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/tmp:/tmp",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ],
      "env": {
        "BLENDER_AI_TMP_INTERNAL_DIR": "/tmp",
        "BLENDER_AI_TMP_EXTERNAL_DIR": "/tmp",
        "BLENDER_RPC_HOST": "host.docker.internal"
      }
    }
  }
}
```

**⚠️ Important Network Configuration:**
*   **macOS/Windows:** Use `host.docker.internal` (as shown in the first config). The `--network host` option does NOT work on Docker Desktop for Mac/Windows.
*   **Linux:** Use `--network host` with `127.0.0.1` (as shown in the second config).
*   **Troubleshooting:** If the MCP server starts but cannot connect to Blender (timeout errors), ensure Blender is running with the addon enabled and that port `8765` is not blocked.

### Viewport Output Modes & Temp Directory Mapping

The `scene_get_viewport` tool supports multiple output modes via the `output_mode` argument:
* `IMAGE` (default): returns a FastMCP `Image` resource (best for Cline / clients with native image support).
* `BASE64`: returns the raw base64-encoded JPEG string for direct Vision-module consumption.
* `FILE`: writes the image to a temp directory and returns a message with **host-visible** file paths.
* `MARKDOWN`: writes the image and returns rich markdown with an inline `data:` URL plus host-visible paths.

When running in Docker, map the internal temp directory to a host folder and configure env vars:

```bash
# Example volume & env mapping
docker run -i --rm \
  -v /host/tmp/blender-ai-mcp:/tmp/blender-ai-mcp \
  -e BLENDER_RPC_HOST=host.docker.internal \
  -e BLENDER_AI_TMP_INTERNAL_DIR=/tmp/blender-ai-mcp \
  -e BLENDER_AI_TMP_EXTERNAL_DIR=/host/tmp/blender-ai-mcp \
  ghcr.io/patrykiti/blender-ai-mcp:latest
```

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=PatrykIti/blender-ai-mcp&type=date&legend=top-left)](https://www.star-history.com/#PatrykIti/blender-ai-mcp&type=date&legend=top-left)

---

## 🏗️ Architecture

This project uses a split-architecture design:
1.  **MCP Server (Python/FastMCP)**: Handles AI communication.
2.  **Blender Addon (Python/bpy)**: Executes 3D operations.

Communication happens via **JSON-RPC over TCP sockets**.

See [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive.

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) to understand our Clean Architecture standards before submitting a Pull Request.

## 👨‍💻 Author

**Patryk Ciechański**
*   GitHub: [PatrykIti](https://github.com/PatrykIti)

## 📜 License

MIT License.
