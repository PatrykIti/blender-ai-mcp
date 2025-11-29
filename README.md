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

> **Legend:** ✅ Completed | 🚧 In Progress

> **Progress:** ████████████░░░░░░░░ ~40% (Phase 1 ✅, Phase 2 🚧, Phase 3-6 🚧, Phase 7 ✅)

Our goal is to enable AI to model complex 3D assets—from organs and biological structures to hard-surface precision parts (cars, devices).

#### ✅ Phase 1: Object & Scene Management (Completed)
Basic composition and scene understanding.
- [x] **Scene**: List, Delete, Duplicate, Set Active, Clean Scene.
- [x] **Vision**: `get_viewport` (AI sees the scene).
- [x] **Construction**: Create Lights, Cameras, Empties.
- [x] **Object Ops**: Create Primitives, Transform (Move/Rotate/Scale), Set Origin.
- [x] **Modifiers**: Add Modifier, Apply Modifier, List Modifiers.
- [x] **Structure**: Join Objects, Separate Objects, Convert to Mesh.

#### 🚧 Phase 2: Mesh Editing (Edit Mode)
Critical for shaping geometry. AI needs these to actually "model" details, not just move cubes around.

**2.0 Core Edit Mode** ✅
- [x] `mesh_select_all`, `mesh_delete_selected`, `mesh_select_by_index`
- [x] `mesh_extrude_region`, `mesh_fill_holes`
- [x] `mesh_loop_cut`, `mesh_bevel`, `mesh_inset`
- [x] `mesh_boolean`, `mesh_merge_by_distance`, `mesh_subdivide`
- [x] `mesh_smooth`, `mesh_flatten`

**2.1 Advanced Selection** ✅
- [x] `mesh_get_vertex_data`, `mesh_select_by_location`, `mesh_select_boundary` 🔴 CRITICAL
- [x] `mesh_select_linked`, `mesh_select_loop`, `mesh_select_ring`
- [x] `mesh_select_more`, `mesh_select_less`

**2.2 Organic & Deform** ✅
- [x] `mesh_randomize`, `mesh_shrink_fatten`

**2.3 Vertex Groups** ✅
- [x] `mesh_create_vertex_group`, `mesh_assign_to_group`, `mesh_remove_from_group`

**2.4 Core Transform & Geometry** 🔴 HIGH PRIORITY
- [ ] `mesh_transform_selected` **CRITICAL - unlocks 80% of modeling tasks**
- [ ] `mesh_bridge_edge_loops`, `mesh_duplicate_selected`

**2.5 Advanced Precision** ✅
- [x] `mesh_bisect`, `mesh_edge_slide`, `mesh_vert_slide`
- [x] `mesh_triangulate`, `mesh_remesh_voxel`

**2.6 Curves & Procedural**
- [ ] `curve_create`, `curve_to_mesh`
- [ ] `mesh_spin`, `mesh_screw`
- [ ] `mesh_add_vertex`, `mesh_add_edge`, `mesh_add_face`

#### 🚧 Phase 3: Materials & Organization
- [ ] `material_create`: Setup PBR materials.
- [ ] `material_assign`: Assign to objects/faces.
- [ ] `material_set_params`: Adjust roughness, metallic, emission, alpha.
- [ ] `material_set_texture`: Bind image textures to materials.
- [ ] `uv_unwrap`: Smart UV Project / Cube Projection.
- [ ] `uv_pack_islands`: Pack islands for efficient texture space usage.
- [ ] `collection_manage`: Organize hierarchy.
- [ ] `export`: Save to GLB/FBX/OBJ.

#### 🚧 Phase 4: Macro Tools (The "Magic" Layer)
High-level abstractions where one command executes hundreds of Blender operations.
- [ ] `macro_organify`: Converts blockouts to organic shapes (hearts, lungs).
- [ ] `macro_create_phone_base`: Generates smartphone chassis with accurate topology.
- [ ] `macro_human_blockout`: Generates proportional human base meshes.
- [ ] `macro_retopologize`: Automates low-poly conversion.
- [ ] `macro_panel_cut`: Hard-surface panel cutting for devices and robots.
- [ ] `macro_lowpoly_convert`: Global polycount reduction while preserving silhouette.
- [ ] `macro_cleanup_all`: Scene-wide cleanup (remove doubles, recalc normals, fix manifold).

#### 🚧 Phase 5: Sculpting & Voxel Tools
Organic shaping and high-level sculpt workflows.
- [ ] `mesh_remesh_voxel`: Voxel remesh for uniform density.
- [ ] `mesh_sculpt_auto`: High-level sculpt macro (smooth / grab / inflate / draw regions).
- [ ] Future `sculpt_brush_*` tools for direct brush control (smooth, grab, crease, etc.).

#### 🚧 Phase 6: System & Session Management
Global project-level operations and undo-safe workflows.
- [ ] `system_set_mode`: High-level alias over scene/mode tools.
- [ ] `system_undo` / `system_redo`: Safe history navigation for AI.
- [ ] `system_save_file` / `system_new_file`: File-level save and reset.
- [ ] `system_snapshot`: Optional quick save/restore checkpoints for complex modeling sessions.

#### ✅ Phase 7: Introspection & Listing APIs (Completed)
Read-only inspection tools giving AI a structured view of scene, assets, and geometry.
- **Scene & System:**
  - [x] `scene_get_mode`: Report current Blender mode for context-aware ops.
  - [x] `scene_list_selection`: List currently selected objects/components.
  - [x] `scene_inspect_object`: Detailed info about a single object (type, modifiers, materials, polycount).
  - [x] `scene_snapshot_state`: Capture structured snapshot of scene state.
  - [x] `scene_compare_snapshot`: Compare two snapshots to summarize changes.
- **Collections:**
  - [x] `collection_list`: List all collections and their hierarchy.
  - [x] `collection_list_objects`: List objects inside a given collection.
- **Materials:**
  - [x] `material_list`: List all materials with key parameters.
  - [x] `material_list_by_object`: Materials and slots used by a specific object.
  - [x] `scene_inspect_material_slots`: Detailed slot/material assignments per object.
- **UV & Geometry:**
  - [x] `uv_list_maps`: List UV maps for an object.
  - [x] `mesh_list_groups`: List vertex/face groups or selection sets (if modeled).
  - [x] `scene_inspect_mesh_topology`: Provide topology stats (verts/edges/faces, non-manifold data).
  - [x] `scene_inspect_modifiers`: Enumerate modifiers with statuses/settings.

---

## 🧠 LLM Context Optimization

> Unified "mega tools" that consolidate multiple related operations to reduce LLM context usage.

| Mega Tool | Replaces | Savings | Status |
|-----------|----------|---------|--------|
| `scene_context` | mode, selection | -1 | ✅ Done |
| `scene_create` | light, camera, empty | -2 | ✅ Done |
| `scene_inspect` | object, topology, modifiers, materials | -3 | ✅ Done |
| `mesh_select` | all, none, linked, more, less, boundary | -4 | ✅ Done |
| `mesh_select_targeted` | by_index, loop, ring, by_location | -3 | ✅ Done |

**Implemented:** 18 tools → 5 mega tools (**-13 definitions** for LLM context)

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
        "mesh_remesh_voxel"
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
        "mesh_remesh_voxel"
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
