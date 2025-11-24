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

Our goal is to enable AI to model complex 3D assets—from organs and biological structures to hard-surface precision parts (cars, devices).

#### ✅ Phase 1: Object & Scene Management (Completed)
Basic composition and scene understanding.
- [x] **Scene**: List, Delete, Duplicate, Set Active, Clean Scene.
- [x] **Vision**: `get_viewport` (AI sees the scene).
- [x] **Construction**: Create Lights, Cameras, Empties.
- [x] **Object Ops**: Create Primitives, Transform (Move/Rotate/Scale), Set Origin.
- [x] **Modifiers**: Add Modifier, Apply Modifier, List Modifiers.
- [x] **Structure**: Join Objects, Separate Objects, Convert to Mesh.

#### 🚧 Phase 2: Mesh Editing (Edit Mode) - *In Progress*
Critical for shaping geometry. AI needs these to actually "model" details, not just move cubes around.
- [x] `mesh_select_all`, `mesh_delete_selected`, `mesh_select_by_index`.
- [ ] `mesh_extrude` (The basis of modeling).
- [ ] `mesh_loop_cut` (Adding topology).
- [ ] `mesh_bevel` (Rounding edges).
- [ ] `mesh_inset` (Creating panels/windows).
- [ ] `mesh_boolean` (Destructive cutting).
- [ ] `mesh_merge_by_distance` (Cleaning topology).
- [ ] `mesh_smooth` / `mesh_flatten`.

#### ⏳ Phase 3: Materials & Organization
- [ ] `material_create`: Setup PBR materials.
- [ ] `material_assign`: Assign to objects/faces.
- [ ] `uv_unwrap`: Smart UV Project / Cube Projection.
- [ ] `collection_manage`: Organize hierarchy.
- [ ] `export`: Save to GLB/FBX/OBJ.

#### ⭐ Phase 4: Macro Tools (The "Magic" Layer)
High-level abstractions where one command executes hundreds of Blender operations.
- [ ] `macro_organify`: Converts blockouts to organic shapes (hearts, lungs).
- [ ] `macro_create_phone_base`: Generates smartphone chassis with accurate topology.
- [ ] `macro_human_blockout`: Generates proportional human base meshes.
- [ ] `macro_retopologize`: Automates low-poly conversion.

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
        "scene_create_light",
        "scene_create_camera",
        "scene_create_empty",
        "scene_set_mode",
        "modeling_create_primitive",
        "modeling_transform_object",
        "modeling_add_modifier",
        "modeling_apply_modifier",
        "modeling_convert_to_mesh",
        "modeling_join_objects",
        "modeling_separate_object",
        "modeling_set_origin",
        "modeling_list_modifiers",
        "mesh_select_all",
        "mesh_delete_selected",
        "mesh_select_by_index"
      ]
    }
  }
}
```

*(Note: On Linux, replace `host.docker.internal` with `127.0.0.1` and add `--network host`)*.

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
