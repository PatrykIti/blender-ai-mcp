# blender-ai-mcp

[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-lightgrey.svg)](./LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
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
1.  **Hallucinations**: AI frequently uses outdated `bpy` API methods (mixing Blender 2.8 with 5.0).
2.  **Context Errors**: Running operators requires specific context (active window, selected object, correct mode). Raw scripts often crash Blender due to `poll()` failures.
3.  **No Feedback Loop**: If a script fails, the AI doesn't know why. Our MCP server returns precise error messages.
4.  **Safety**: Executing arbitrary Python code is risky. Our tools are sandboxed endpoints with validated inputs.

**Blender AI MCP** acts as a stable *Translation Layer*, handling the complexity of Blender's internal state machine so the AI can focus on creativity.

---

## 🏗️ Architecture

This project uses a split-architecture design:
1.  **MCP Server (Python/FastMCP)**: Handles AI communication.
2.  **Blender Addon (Python/bpy)**: Executes 3D operations.

Communication happens via **JSON-RPC over TCP sockets**.

See [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive.

Current FastMCP platform baseline:

- explicit server factory and surface profiles
- reusable provider groups instead of one flat bootstrap registry
- deterministic transform pipeline scaffold
- shared session/execution bridge for later visibility, elicitation, and task features

### LLM-Guided Public Surface

The `llm-guided` surface now exposes a first cleaner public contract line on top of the same internal capabilities.

Current public tool aliases on `llm-guided`:

| Internal tool | `llm-guided` public name |
|---|---|
| `scene_context` | `check_scene` |
| `scene_inspect` | `inspect_scene` |
| `workflow_catalog` | `browse_workflows` |

Current public argument aliases on `llm-guided`:

| Tool | Internal arg | `llm-guided` public arg |
|---|---|---|
| `check_scene` | `action` | `query` |
| `inspect_scene` | `object_name` | `target_object` |
| `browse_workflows` | `workflow_name` | `name` |
| `browse_workflows` | `query` | `search_query` |

The legacy/internal names remain the canonical internal contract used by router and dispatcher internals.

### Search-First Discovery

`llm-guided` now defaults to a search-first tool surface.

Current measurable baseline:

- `legacy-flat`: `159` visible tools, about `204590` JSON bytes in `list_tools`
- `llm-guided`: `5` visible tools, about `16621` JSON bytes in `list_tools`

The visible `llm-guided` entry set is:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `search_tools`
- `call_tool`

Build and inspection tools stay discoverable on demand and remain constrained by guided visibility/session phase rules.

### Runtime Responsibility Model

The project intentionally separates four different responsibilities:

- **FastMCP platform layer**: client-facing MCP surface, discovery, visibility, prompts, elicitation, and future 3.x platform features.
- **LaBSE semantic layer**: multilingual semantic matching for workflows, modifiers, and learned parameter reuse.
- **Router policy layer**: deterministic correction, guardrails, adaptation, and execution policy.
- **Inspection / assertion layer**: source of truth for actual Blender state and future correctness checks.

Important:

- LaBSE helps answer “what did the user probably mean?”
- Router helps answer “how do we execute this safely?”
- Inspection tools answer “what is actually true in Blender right now?”

Current router policy direction:

- normalized confidence signals feed explicit `auto-fix / ask / block` decisions
- medium-confidence reinterpretation is escalated into structured clarification
- policy context is being surfaced to session state and router status for operator transparency

Current correction transparency baseline:

- corrected router-aware MCP executions carry explicit `router_disposition`, `audit_ids`, and `verification_status`
- high-risk precondition repairs for mode, selection, and active object are verified against inspection truth before the run is treated as successful
- router telemetry/logs receive the same `audit_ids`, so corrected executions can be correlated across responses and operator traces
- legacy text rendering still exists for compatibility, but the structured execution report is now the canonical audit record

### Structured Contract Baseline

Critical MCP surfaces now default to machine-readable structured contracts:

- `scene_context`
- `scene_inspect`
- `scene_snapshot_state`
- `scene_compare_snapshot`
- `mesh_inspect`
- `router_set_goal`
- `router_get_status`
- `workflow_catalog`

On structured surfaces, these tools expose native structured payloads aligned with declared schemas.
Compatibility surfaces can still preserve deterministic text fallback where explicitly required.

### Versioned Surface Baseline

Public surface evolution now has an explicit coexistence path:

- `legacy-flat` defaults to contract line `legacy-v1`
- `llm-guided` defaults to contract line `llm-guided-v2`
- `llm-guided-v1` remains selectable as a rollback / compatibility line for the guided surface

Selected public-evolution capabilities such as `scene_context`, `scene_inspect`, and `workflow_catalog`
now expose explicit component versions, while unchanged capabilities remain unversioned and shared.

### Telemetry And Timeout Baseline

Operational baseline now includes:

- optional OpenTelemetry bootstrap via `OTEL_ENABLED`, `OTEL_EXPORTER`, and `OTEL_SERVICE_NAME`
- repo-specific router spans on top of the FastMCP runtime
- explicit timeout boundaries:
  - `mcp_tool`
  - `mcp_task`
- `rpc_client`
- `addon_execution`

### Background Task Mode Baseline

The current background-task rollout now covers the first heavy-operation set plus the system import/export family on task-capable surfaces.

Adopted task-capable entrypoints:

- `scene_get_viewport`
- `extraction_render_angles`
- `workflow_catalog(action="import_finalize")`
- `export_glb`
- `export_fbx`
- `export_obj`
- `import_obj`
- `import_fbx`
- `import_glb`
- `import_image_as_plane`

Current behavior:

- adopted endpoints use explicit async MCP adapters with `TaskConfig(mode="optional")`
- task-enabled surfaces can submit these paths as background work
- non-task and compatibility surfaces keep understandable foreground fallback behavior
- Blender-backed task mode uses explicit RPC lifecycle verbs for launch, poll, cancel, and result collection
- workflow import finalization uses the same task bookkeeping on the server side without forcing Blender RPC

See [_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md](_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md).

### Session-Adaptive Guided Mode

The current `llm-guided` surface uses a coarse first-pass phase model:

- `bootstrap`
- `planning`
- `build`
- `inspect_validate`

Guided-mode behavior:

- `bootstrap` / `planning`: keep the visible surface intentionally tiny and centered on guided entry capabilities
- `build`: expose build-oriented capability groups
- `inspect_validate`: elevate inspection/validation-oriented capability groups

`router_get_status()` now exposes visibility diagnostics such as:

- current phase
- active surface profile
- visible capability ids
- visible guided entry capabilities
- hidden capability counts by category

### Structured Clarification Flow

The server now supports two missing-input modes for workflow-first interactions:

- **Native elicitation** on async-capable guided surfaces such as `llm-guided`
- **Typed fallback payloads** for tool-only / compatibility clients

Current clarification behavior:

- `router_set_goal(...)` can ask for missing workflow parameters through structured elicitation
- constrained choices support enums, booleans, and multi-select-style answers
- partial answers and pending clarification ids survive across the next request step
- `workflow_catalog` import conflicts also expose the same typed fallback clarification shape

## ✅ Support Matrix

- **Blender**: tested on **Blender 5.0** (E2E). The addon declares minimum **Blender 4.0**, but 4.x support is best-effort.
- **Python (MCP server)**: **3.11+** is the supported baseline for the FastMCP 3.x migration track and for full repo functionality.
- **OS**: macOS / Windows / Linux (Docker recommended). On Linux, use host networking or proper host resolution for `BLENDER_RPC_HOST`.
- **Memory**: Router semantic matching uses a local LaBSE model (~2GB RAM).
- **FastMCP task runtime**: supported pair is **fastmcp 3.1.1** with **pydocket 0.18.2**. Task-capable surfaces rely on this aligned pair.

## 🧪 Testing

**Unit Tests** (no Blender required):
```bash
PYTHONPATH=. poetry run pytest tests/unit/ -v
```
To see the current unit test count:
```bash
poetry run pytest tests/unit --collect-only
```

**E2E Tests** (requires Blender):
```bash
# Automated: build → install addon → start Blender → run tests → cleanup
python3 scripts/run_e2e_tests.py
```
To see the current E2E test count:
```bash
poetry run pytest tests/e2e --collect-only
```

| Type | Coverage |
|------|----------|
| Unit Tests | All tool handlers |
| E2E Tests | Blender addon integration (Scene, Mesh, Material, UV, Export, Import, Baking, System, Sculpt, Router) |

See [_docs/_TESTS/README.md](_docs/_TESTS/README.md) for detailed testing documentation.

<details>
<summary>📋 Example E2E Test Output (click to expand)</summary>

```
tests/e2e/tools/extraction/test_face_group_analysis.py ....
tests/e2e/tools/extraction/test_render_angles.py ....
tests/e2e/tools/import_tool/test_import_tools.py .........
tests/e2e/tools/knife_cut/test_knife_cut_tools.py .........
tests/e2e/tools/lattice/test_lattice_tools.py .............
tests/e2e/tools/material/test_material_tools.py ..............
tests/e2e/tools/mesh/test_mesh_cleanup.py .................
tests/e2e/tools/mesh/test_mesh_edge_weights.py ...............
tests/e2e/tools/mesh/test_mesh_symmetry_fill.py ............................
tests/e2e/tools/scene/test_camera_focus.py ....
tests/e2e/tools/scene/test_camera_orbit.py ......
tests/e2e/tools/scene/test_hide_object.py ...
tests/e2e/tools/scene/test_isolate_object.py ...
tests/e2e/tools/scene/test_rename_object.py ..
tests/e2e/tools/scene/test_scene_inspect_material_slots.py ....
tests/e2e/tools/scene/test_show_all_objects.py ...
tests/e2e/tools/scene/test_snapshot_tools.py ...
tests/e2e/tools/sculpt/test_sculpt_tools.py .............
tests/e2e/tools/system/test_system_tools.py ............
tests/e2e/tools/text/test_text_tools.py ....................
tests/e2e/tools/uv/test_uv_tools.py ................

============================= 352 passed in 46.21s ==============================
```

</details>

---

## 🗺️ Roadmap & Capabilities

> **Legend:** ✅ Done | 🚧 To Do

Our goal is to enable AI to model complex 3D assets—from organs and biological structures to hard-surface precision parts (cars, devices).

---

<details>
<summary><strong>Scene Tools (`scene_*`) — ✅</strong></summary>

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
| `scene_rename_object` | Rename object by name | ✅ |
| `scene_hide_object` | Hide/show object in viewport | ✅ |
| `scene_show_all_objects` | Show all hidden objects | ✅ |
| `scene_isolate_object` | Isolate object (hide all others) | ✅ |
| `scene_camera_orbit` | Orbit viewport around target | ✅ |
| `scene_camera_focus` | Focus viewport on object | ✅ |
| `scene_get_custom_properties` | Get object metadata/custom properties | ✅ |
| `scene_set_custom_property` | Set/delete custom property on object | ✅ |
| `scene_get_hierarchy` | Get parent-child hierarchy | ✅ |
| `scene_get_bounding_box` | Get precise bounding box corners | ✅ |
| `scene_get_origin_info` | Get origin/pivot point info | ✅ |

---

Note: `scene_get_constraints` is now internal to `scene_inspect(action="constraints")`.

</details>

<details>
<summary><strong>Modeling Tools (`modeling_*`) — ✅</strong></summary>

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

Note: `modeling_get_modifier_data` is now internal to `scene_inspect(action="modifier_data")`.

#### Lattice Deformation
| Tool | Description | Status |
|------|-------------|--------|
| `lattice_create` | Create lattice fitted to object | ✅ |
| `lattice_bind` | Bind object to lattice deformer | ✅ |
| `lattice_edit_point` | Move lattice control points | ✅ |
| `lattice_get_points` | Get lattice point positions | ✅ |

#### Text Objects
| Tool | Description | Status |
|------|-------------|--------|
| `text_create` | Create 3D text object | ✅ |
| `text_edit` | Modify text content and properties | ✅ |
| `text_to_mesh` | Convert text to mesh for export | ✅ |

#### Skin Modifier (Tubular Structures)
| Tool | Description | Status |
|------|-------------|--------|
| `skin_create_skeleton` | Create skeleton for skin modifier | ✅ |
| `skin_set_radius` | Set skin radius at vertices | ✅ |

---

</details>

<details>
<summary><strong>Mesh Tools (`mesh_*`) — ✅</strong></summary>

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

Note: Mesh introspection actions are consolidated under `mesh_inspect` (internal `mesh_get_*`).

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

#### Edge Weights & Creases
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_edge_crease` | Set crease weight for subdivision | ✅ |
| `mesh_bevel_weight` | Set bevel weight for bevel modifier | ✅ |
| `mesh_mark_sharp` | Mark/clear sharp edges | ✅ |

#### Cleanup & Optimization
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_dissolve` | Dissolve vertices/edges/faces (limited dissolve) | ✅ |
| `mesh_tris_to_quads` | Convert triangles to quads | ✅ |
| `mesh_normals_make_consistent` | Recalculate normals | ✅ |
| `mesh_decimate` | Reduce polycount on selection | ✅ |

#### Knife & Cut
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_knife_project` | Project cut from selected geometry | ✅ |
| `mesh_rip` | Rip/tear geometry at selection | ✅ |
| `mesh_split` | Split selection from mesh | ✅ |
| `mesh_edge_split` | Split mesh at selected edges | ✅ |

#### Symmetry & Fill
| Tool | Description | Status |
|------|-------------|--------|
| `mesh_symmetrize` | Make mesh symmetric | ✅ |
| `mesh_grid_fill` | Fill boundary with quad grid | ✅ |
| `mesh_poke_faces` | Poke faces (add center vertex) | ✅ |
| `mesh_beautify_fill` | Rearrange triangles uniformly | ✅ |
| `mesh_mirror` | Mirror selected geometry | ✅ |
| `mesh_set_proportional_edit` | Enable soft selection falloff | ✅ |

---

</details>

<details>
<summary><strong>Curve Tools (`curve_*`) — ✅</strong></summary>

Curve creation and conversion.

| Tool | Description | Status |
|------|-------------|--------|
| `curve_create` | Create Bezier/NURBS/Path/Circle curve | ✅ |
| `curve_to_mesh` | Convert curve to mesh | ✅ |
| `curve_get_data` | Get curve splines and settings | ✅ |

---

</details>

<details>
<summary><strong>Collection Tools (`collection_*`) — ✅</strong></summary>

Collection management and hierarchy.

| Tool | Description | Status |
|------|-------------|--------|
| `collection_list` | List all collections | ✅ |
| `collection_list_objects` | List objects in collection | ✅ |
| `collection_manage` | Create/delete/move collections | ✅ |

---

</details>

<details>
<summary><strong>Material Tools (`material_*`) — ✅</strong></summary>

Material creation and assignment.

| Tool | Description | Status |
|------|-------------|--------|
| `material_list` | List all materials | ✅ |
| `material_list_by_object` | List materials on object | ✅ |
| `material_create` | Setup PBR materials | ✅ |
| `material_assign` | Assign to objects/faces | ✅ |
| `material_set_params` | Adjust roughness, metallic, etc. | ✅ |
| `material_set_texture` | Bind image textures | ✅ |
| `material_inspect_nodes` | Inspect shader node graph | ✅ |

---

</details>

<details>
<summary><strong>UV Tools (`uv_*`) — ✅</strong></summary>

UV mapping operations.

| Tool | Description | Status |
|------|-------------|--------|
| `uv_list_maps` | List UV maps on object | ✅ |
| `uv_unwrap` | Smart UV Project / Cube Projection | ✅ |
| `uv_pack_islands` | Pack UV islands | ✅ |
| `uv_create_seam` | Mark/clear UV seams | ✅ |

---

</details>

<details>
<summary><strong>System Tools (`system_*`) — ✅</strong></summary>

Global project-level operations.

| Tool | Description | Status |
|------|-------------|--------|
| `system_set_mode` | High-level mode switching | ✅ |
| `system_undo` | Safe undo for AI | ✅ |
| `system_redo` | Safe redo for AI | ✅ |
| `system_save_file` | Save .blend file | ✅ |
| `system_new_file` | Create new file | ✅ |
| `system_snapshot` | Quick save/restore checkpoints | ✅ |

---

</details>

<details>
<summary><strong>Export Tools (`export_*`) — ✅</strong></summary>

File export operations.

| Tool | Description | Status |
|------|-------------|--------|
| `export_glb` | Export to GLB format | ✅ |
| `export_fbx` | Export to FBX format | ✅ |
| `export_obj` | Export to OBJ format | ✅ |

---

</details>

<details>
<summary><strong>Import Tools (`import_*`) — ✅</strong></summary>

File import operations.

| Tool | Description | Status |
|------|-------------|--------|
| `import_obj` | Import OBJ file | ✅ |
| `import_fbx` | Import FBX file | ✅ |
| `import_glb` | Import GLB/GLTF file | ✅ |
| `import_image_as_plane` | Import image as textured plane (reference) | ✅ |

---

</details>

<details>
<summary><strong>Baking Tools (`bake_*`) — ✅</strong></summary>

Texture baking for game dev workflows.

| Tool | Description | Status |
|------|-------------|--------|
| `bake_normal_map` | Bake normal map (high-to-low or self) | ✅ |
| `bake_ao` | Bake ambient occlusion map | ✅ |
| `bake_combined` | Bake full render to texture | ✅ |
| `bake_diffuse` | Bake diffuse/albedo color | ✅ |

---

</details>

<details>
<summary><strong>Extraction Tools (`extraction_*`) — ✅</strong></summary>

Analysis tools for the Automatic Workflow Extraction System. Enables deep topology analysis, component detection, symmetry detection, and multi-angle rendering for LLM Vision integration.

| Tool | Description | Status |
|------|-------------|--------|
| `extraction_deep_topology` | Deep topology analysis with feature detection | ✅ |
| `extraction_component_separate` | Separate mesh into loose parts | ✅ |
| `extraction_detect_symmetry` | Detect X/Y/Z symmetry planes | ✅ |
| `extraction_edge_loop_analysis` | Analyze edge loops and patterns | ✅ |
| `extraction_face_group_analysis` | Analyze face groups by normal/height | ✅ |
| `extraction_render_angles` | Multi-angle renders for LLM Vision | ✅ |

---

</details>

<details>
<summary><strong>Metaball Tools (`metaball_*`) — ✅</strong></summary>

Organic blob primitives for medical/biological modeling.

| Tool | Description | Status |
|------|-------------|--------|
| `metaball_create` | Create metaball object | ✅ |
| `metaball_add_element` | Add element (ball, capsule, ellipsoid) | ✅ |
| `metaball_to_mesh` | Convert metaball to mesh | ✅ |

---

</details>

<details>
<summary><strong>Macro Tools (`macro_*`) — 🚧</strong></summary>

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

</details>

<details>
<summary><strong>Sculpting Tools (`sculpt_*`) — ✅</strong></summary>

Organic shaping and sculpt workflows.

#### Core Brushes
| Tool | Description | Status |
|------|-------------|--------|
| `sculpt_auto` | High-level sculpt operation (mesh filters) | ✅ |
| `sculpt_brush_smooth` | Smooth brush | ✅ |
| `sculpt_brush_grab` | Grab brush | ✅ |
| `sculpt_brush_crease` | Crease brush | ✅ |

#### Organic Brushes
| Tool | Description | Status |
|------|-------------|--------|
| `sculpt_brush_clay` | Add clay-like material | ✅ |
| `sculpt_brush_inflate` | Inflate/deflate areas | ✅ |
| `sculpt_brush_blob` | Create organic bulges | ✅ |
| `sculpt_brush_snake_hook` | Pull long tendrils (vessels, nerves) | ✅ |
| `sculpt_brush_draw` | Basic sculpt draw | ✅ |
| `sculpt_brush_pinch` | Pinch geometry together | ✅ |

#### Dynamic Topology
| Tool | Description | Status |
|------|-------------|--------|
| `sculpt_enable_dyntopo` | Enable dynamic topology | ✅ |
| `sculpt_disable_dyntopo` | Disable dynamic topology | ✅ |
| `sculpt_dyntopo_flood_fill` | Apply detail level to entire mesh | ✅ |

---

</details>

<details>
<summary><strong>Armature Tools (`armature_*`) — ✅</strong></summary>

Skeletal rigging and animation.

| Tool | Description | Status |
|------|-------------|--------|
| `armature_create` | Create armature with initial bone | ✅ |
| `armature_add_bone` | Add bone to armature | ✅ |
| `armature_bind` | Bind mesh to armature (auto weights) | ✅ |
| `armature_pose_bone` | Pose armature bone | ✅ |
| `armature_weight_paint_assign` | Assign weights to vertex group | ✅ |
| `armature_get_data` | Get armature bones and hierarchy | ✅ |

---

</details>

### 🤖 Router Supervisor ✅

Intelligent Router acting as **supervisor over LLM tool calls** - not just an "intent matcher". Intercepts, corrects, expands, and overrides tool calls before execution.

**Status:** ✅ **Complete** | All 6 Phases Done | Test counts vary — see **🧪 Testing** for up-to-date numbers

> **Documentation:** See [`_docs/_ROUTER/`](_docs/_ROUTER/) for full documentation including [Quick Start](_docs/_ROUTER/QUICK_START.md), [Configuration](_docs/_ROUTER/CONFIGURATION.md), [Patterns](_docs/_ROUTER/PATTERNS.md), [API Reference](_docs/_ROUTER/API.md), and [Responsibility Boundaries](_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md).

#### Responsibility Boundaries

- **FastMCP** should own discovery, visibility, prompts, elicitation, and future 3.x client-surface shaping.
- **LaBSE** should own semantic retrieval and multilingual generalization.
- **Router** should own deterministic safety and correction policy.
- **Inspection tools** should remain the source of Blender truth; router and LaBSE are not substitutes for verification.

#### All Phases Complete ✅

| Phase | Components | Status |
|-------|------------|--------|
| **Phase 1: Foundation** | Directory structure, Domain entities, Interfaces, Metadata loader (119 JSON files), Config | ✅ |
| **Phase 2: Analysis** | Tool interceptor, Scene context analyzer, Geometry pattern detector, Proportion calculator | ✅ |
| **Phase 3: Engines** | Tool correction, Tool override, Workflow expansion, Error firewall, Intent classifier (LaBSE) | ✅ |
| **Phase 4: Integration** | SupervisorRouter orchestrator, MCP integration, Logging & telemetry | ✅ |
| **Phase 5: Workflows** | Phone workflow, Tower workflow, Screen cutout workflow, Custom YAML workflows | ✅ |
| **Phase 6: Testing & Docs** | E2E test suite (see 🧪 Testing), Complete documentation (6 guides) | ✅ |

#### Key Features

| Feature | Description |
|---------|-------------|
| **LLM Supervisor** | Intercepts and corrects LLM tool calls before execution |
| **Scene-Aware** | Analyzes Blender state via RPC for informed decisions |
| **Pattern Detection** | Recognizes 9 patterns: tower, phone, table, pillar, wheel, box, sphere, cylinder |
| **Auto-Correction** | Fixes mode violations, missing selection, invalid parameters |
| **Workflow Expansion** | Single tool → complete multi-step workflow |
| **Error Firewall** | Blocks/fixes invalid operations before they crash |
| **100% Offline** | No external API calls - LaBSE runs locally (~1.8GB RAM) |
| **Multilingual** | LaBSE supports 109 languages for intent classification |
| **Semantic Matching** | Match workflows by meaning, not just keywords (LaBSE embeddings) |
| **Generalization** | Use similar workflow when exact match missing |
| **Feedback Learning** | Improve matching from user corrections |
| **LanceDB Vector Store** | O(log N) HNSW search with metadata filtering |
| **Confidence Adaptation** | HIGH/MEDIUM/LOW confidence → full/filtered/core workflow |
| **Parametric Variables** | `$variable` syntax with `defaults` and `modifiers` for dynamic params |

> Note: Router policy is authoritative for correction and execution flow. Inspection tools are authoritative for actual scene state and result verification.

#### Workflow-First Quick Start (recommended)

Use this when you want the LLM to **prefer existing YAML workflows** and only fall back to manual tool-calling when no workflow matches.

```text
1) Optional: import external workflow YAML/JSON
   workflow_catalog(action="import", filepath="/path/to/workflow.yaml")
   workflow_catalog(action="import", content="<yaml or json>", content_type="yaml")
   workflow_catalog(action="import_init", content_type="json", source_name="chair.json", total_chunks=2)
   workflow_catalog(action="import_append", session_id="...", chunk_data="...", chunk_index=0)
   workflow_catalog(action="import_append", session_id="...", chunk_data="...", chunk_index=1)
   workflow_catalog(action="import_finalize", session_id="...", overwrite=true)
   - if status == "needs_input": repeat with overwrite=true or overwrite=false

2) Optional: preview likely workflow matches
   workflow_catalog(action="search", query="<your prompt>", top_k=5, threshold=0.0)

3) Set the goal (mandatory)
   router_set_goal(goal="<your prompt including modifiers>")

4) Handle Router response
   - status == "needs_input": call router_set_goal(goal, resolved_params={...})
   - status == "ready": proceed (workflow executes / expands into tool calls)
   - status == "no_match": switch to manual tool-calling
   - status == "error": router malfunction (fail-fast). Check logs and open a GitHub issue.
```

#### Example: LLM sends mesh tool in wrong mode

```
LLM: mesh_extrude(depth=0.5)  # In OBJECT mode, no selection

Router detects:
  - Mode: OBJECT (mesh tool needs EDIT)
  - Selection: None (extrude needs faces)
  - Pattern: phone_like

Router outputs:
  1. system_set_mode(mode="EDIT")
  2. mesh_select(action="all", mode="FACE")
  3. mesh_inset(thickness=0.03)
  4. mesh_extrude(depth=-0.02)
  5. system_set_mode(mode="OBJECT")

Result: Screen cutout created instead of crash!
```

#### Semantic Workflow Matching

```
User: "zrób krzesło" (make a chair)

Router behavior:
  → LaBSE semantic similarity search
  → Found: table_workflow (0.72), tower_workflow (0.45)
  → Uses table_workflow with inherited proportions
  → Chair has proper leg ratios from table, vertical proportions from tower
```

Note:
- LaBSE is used here as a semantic retrieval layer.
- It is not the source of truth for scene correctness, geometry state, or safe execution.

#### Parametric Variables

```yaml
# In workflow YAML:
defaults:
  leg_angle: 0.32        # A-frame legs (default)

modifiers:
  "straight legs":
    leg_angle: 0         # Override for vertical legs
  "proste nogi":         # Polish support
    leg_angle: 0

steps:
  - tool: modeling_transform_object
    params:
      rotation: [0, "$leg_angle", 0]  # Uses variable
```

```
User: "table with straight legs"
→ Modifier "straight legs" matches
→ leg_angle = 0 (vertical legs instead of A-frame)

User: "stół z proste nogi"
→ Polish modifier matches
→ Same result: vertical legs
```

#### Configuration Presets

```python
from server.router.infrastructure.config import RouterConfig

# Default (recommended)
config = RouterConfig()

# Strict mode (no auto-fixes)
config = RouterConfig(auto_mode_switch=False, auto_selection=False)

# Performance mode (longer cache)
config = RouterConfig(cache_ttl_seconds=2.0, log_decisions=False)
```

---

## 🧠 LLM Context Optimization

> Unified "mega tools" that consolidate multiple related operations to reduce LLM context usage.
> Mega tools are wrappers only; action-level handlers live as internal functions backed by Blender addon RPC.
> Standalone MCP tools are exposed only where explicitly listed.
> Router can still execute internal actions via handler mappings and per-tool JSON metadata.

<details>
<summary><strong>Mega Tools (LLM Context Optimization)</strong></summary>

### Scene Mega Tools

| Mega Tool | Actions | Savings | Status |
|-----------|---------|---------|--------|
| `scene_context` | mode, selection | -1 | ✅ |
| `scene_create` | light, camera, empty | -2 | ✅ |
| `scene_inspect` | object, topology, modifiers, materials, constraints, modifier_data | -5 | ✅ |

### Mesh Mega Tools

| Mega Tool | Actions | Savings | Status |
|-----------|---------|---------|--------|
| `mesh_select` | all, none, linked, more, less, boundary | -4 | ✅ |
| `mesh_select_targeted` | by_index, loop, ring, by_location | -3 | ✅ |
| `mesh_inspect` | vertices, edges, faces, uvs, normals, attributes, shape_keys, group_weights, summary | -7 | ✅ |

**Total:** 28 tools → 6 mega tools (**-22 definitions** for LLM context).

`mesh_inspect.summary` sources (recommended): `scene_inspect(topology)`, `uv_list_maps`, `mesh_get_shape_keys`, `mesh_get_loop_normals`, `mesh_list_groups`, `modeling_list_modifiers`.

</details>

---

## 🚀 Quick Start

### 1. Install the Blender Addon
1. Download `blender_ai_mcp.zip` from the [Releases Page](../../releases).
2. Open Blender -> Edit -> Preferences -> Add-ons.
3. Click **Install...** and select the zip file.
4. Enable the addon. It will start a local server on port `8765`.

### 2. Configure your MCP Client (Cline / Claude Code / Codex CLI)

We recommend using Docker to run the MCP Server.

<details>
<summary><strong>Cline / Claude Code — <code>cline_mcp_settings.json</code> (macOS/Windows)</strong></summary>

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
        "scene_rename_object",
        "scene_hide_object",
        "scene_show_all_objects",
        "scene_isolate_object",
        "scene_camera_orbit",
        "scene_camera_focus",
        "scene_get_custom_properties",
        "scene_set_custom_property",
        "scene_get_hierarchy",
        "scene_get_bounding_box",
        "scene_get_origin_info",
        "collection_list",
        "collection_list_objects",
        "collection_manage",
        "material_list",
        "material_list_by_object",
        "material_create",
        "material_assign",
        "material_set_params",
        "material_set_texture",
        "material_inspect_nodes",
        "uv_list_maps",
        "uv_unwrap",
        "uv_pack_islands",
        "uv_create_seam",
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
        "mesh_inspect",
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
        "mesh_edge_crease",
        "mesh_bevel_weight",
        "mesh_mark_sharp",
        "mesh_dissolve",
        "mesh_tris_to_quads",
        "mesh_normals_make_consistent",
        "mesh_decimate",
        "mesh_knife_project",
        "mesh_rip",
        "mesh_split",
        "mesh_edge_split",
        "mesh_symmetrize",
        "mesh_grid_fill",
        "mesh_poke_faces",
        "mesh_beautify_fill",
        "mesh_mirror",
        "curve_create",
        "curve_to_mesh",
        "curve_get_data",
        "text_create",
        "text_edit",
        "text_to_mesh",
        "export_glb",
        "export_fbx",
        "export_obj",
        "sculpt_auto",
        "sculpt_brush_smooth",
        "sculpt_brush_grab",
        "sculpt_brush_crease",
        "sculpt_brush_clay",
        "sculpt_brush_inflate",
        "sculpt_brush_blob",
        "sculpt_brush_snake_hook",
        "sculpt_brush_draw",
        "sculpt_brush_pinch",
        "sculpt_enable_dyntopo",
        "sculpt_disable_dyntopo",
        "sculpt_dyntopo_flood_fill",
        "metaball_create",
        "metaball_add_element",
        "metaball_to_mesh",
        "skin_create_skeleton",
        "skin_set_radius",
        "lattice_create",
        "lattice_bind",
        "lattice_edit_point",
        "lattice_get_points",
        "mesh_set_proportional_edit",
        "system_set_mode",
        "system_undo",
        "system_redo",
        "system_save_file",
        "system_new_file",
        "system_snapshot",
        "bake_normal_map",
        "bake_ao",
        "bake_combined",
        "bake_diffuse",
        "import_obj",
        "import_fbx",
        "import_glb",
        "import_image_as_plane",
        "extraction_deep_topology",
        "extraction_component_separate",
        "extraction_detect_symmetry",
        "extraction_edge_loop_analysis",
        "extraction_face_group_analysis",
        "extraction_render_angles",
        "armature_create",
        "armature_add_bone",
        "armature_bind",
        "armature_pose_bone",
        "armature_weight_paint_assign",
        "armature_get_data",
        "workflow_catalog",
        "router_set_goal",
        "router_get_status",
        "router_clear_goal"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>Cline / Claude Code — <code>cline_mcp_settings.json</code> (Linux)</strong></summary>

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
        "scene_rename_object",
        "scene_hide_object",
        "scene_show_all_objects",
        "scene_isolate_object",
        "scene_camera_orbit",
        "scene_camera_focus",
        "scene_get_custom_properties",
        "scene_set_custom_property",
        "scene_get_hierarchy",
        "scene_get_bounding_box",
        "scene_get_origin_info",
        "collection_list",
        "collection_list_objects",
        "collection_manage",
        "material_list",
        "material_list_by_object",
        "material_create",
        "material_assign",
        "material_set_params",
        "material_set_texture",
        "material_inspect_nodes",
        "uv_list_maps",
        "uv_unwrap",
        "uv_pack_islands",
        "uv_create_seam",
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
        "mesh_inspect",
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
        "mesh_edge_crease",
        "mesh_bevel_weight",
        "mesh_mark_sharp",
        "mesh_dissolve",
        "mesh_tris_to_quads",
        "mesh_normals_make_consistent",
        "mesh_decimate",
        "mesh_knife_project",
        "mesh_rip",
        "mesh_split",
        "mesh_edge_split",
        "mesh_symmetrize",
        "mesh_grid_fill",
        "mesh_poke_faces",
        "mesh_beautify_fill",
        "mesh_mirror",
        "curve_create",
        "curve_to_mesh",
        "curve_get_data",
        "text_create",
        "text_edit",
        "text_to_mesh",
        "export_glb",
        "export_fbx",
        "export_obj",
        "sculpt_auto",
        "sculpt_brush_smooth",
        "sculpt_brush_grab",
        "sculpt_brush_crease",
        "sculpt_brush_clay",
        "sculpt_brush_inflate",
        "sculpt_brush_blob",
        "sculpt_brush_snake_hook",
        "sculpt_brush_draw",
        "sculpt_brush_pinch",
        "sculpt_enable_dyntopo",
        "sculpt_disable_dyntopo",
        "sculpt_dyntopo_flood_fill",
        "metaball_create",
        "metaball_add_element",
        "metaball_to_mesh",
        "skin_create_skeleton",
        "skin_set_radius",
        "lattice_create",
        "lattice_bind",
        "lattice_edit_point",
        "lattice_get_points",
        "mesh_set_proportional_edit",
        "system_set_mode",
        "system_undo",
        "system_redo",
        "system_save_file",
        "system_new_file",
        "system_snapshot",
        "bake_normal_map",
        "bake_ao",
        "bake_combined",
        "bake_diffuse",
        "import_obj",
        "import_fbx",
        "import_glb",
        "import_image_as_plane",
        "extraction_deep_topology",
        "extraction_component_separate",
        "extraction_detect_symmetry",
        "extraction_edge_loop_analysis",
        "extraction_face_group_analysis",
        "extraction_render_angles",
        "armature_create",
        "armature_add_bone",
        "armature_bind",
        "armature_pose_bone",
        "armature_weight_paint_assign",
        "armature_get_data",
        "workflow_catalog",
        "router_set_goal",
        "router_get_status",
        "router_clear_goal"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>GitHub Copilot CLI</strong></summary>

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

</details>

<details>
<summary><strong>Codex CLI — <code>~/.codex/config.toml</code></strong></summary>

Create/update `~/.codex/config.toml`:

```toml
[mcp_servers.blender-ai-mcp]
command = "docker"
# Optional
args = [
  "run",
  "-i",
  "-v",
  "/tmp:/tmp",
  "-e",
  "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
  "-e",
  "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
  "-e",
  "ROUTER_ENABLED=true",
  "-e",
  "LOG_LEVEL=DEBUG",
  "-e",
  "BLENDER_RPC_HOST=host.docker.internal",
  "blender-ai-mcp:latest"
]

# Optional: propagate additional env vars to the MCP server.
# A default whitelist of env vars will be propagated to the MCP server.
# https://github.com/openai/codex/blob/main/codex-rs/rmcp-client/src/utils.rs#L82
env = {}

enabled_tools = [
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
  "scene_rename_object",
  "scene_hide_object",
  "scene_show_all_objects",
  "scene_isolate_object",
  "scene_camera_orbit",
  "scene_camera_focus",
  "scene_get_custom_properties",
  "scene_set_custom_property",
  "scene_get_hierarchy",
  "scene_get_bounding_box",
  "scene_get_origin_info",
  "collection_list",
  "collection_list_objects",
  "collection_manage",
  "material_list",
  "material_list_by_object",
  "material_create",
  "material_assign",
  "material_set_params",
  "material_set_texture",
  "material_inspect_nodes",
  "uv_list_maps",
  "uv_unwrap",
  "uv_pack_islands",
  "uv_create_seam",
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
  "mesh_inspect",
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
  "mesh_edge_crease",
  "mesh_bevel_weight",
  "mesh_mark_sharp",
  "mesh_dissolve",
  "mesh_tris_to_quads",
  "mesh_normals_make_consistent",
  "mesh_decimate",
  "mesh_knife_project",
  "mesh_rip",
  "mesh_split",
  "mesh_edge_split",
  "mesh_symmetrize",
  "mesh_grid_fill",
  "mesh_poke_faces",
  "mesh_beautify_fill",
  "mesh_mirror",
  "curve_create",
  "curve_to_mesh",
  "curve_get_data",
  "text_create",
  "text_edit",
  "text_to_mesh",
  "export_glb",
  "export_fbx",
  "export_obj",
  "sculpt_auto",
  "sculpt_brush_smooth",
  "sculpt_brush_grab",
  "sculpt_brush_crease",
  "sculpt_brush_clay",
  "sculpt_brush_inflate",
  "sculpt_brush_blob",
  "sculpt_brush_snake_hook",
  "sculpt_brush_draw",
  "sculpt_brush_pinch",
  "sculpt_enable_dyntopo",
  "sculpt_disable_dyntopo",
  "sculpt_dyntopo_flood_fill",
  "metaball_create",
  "metaball_add_element",
  "metaball_to_mesh",
  "skin_create_skeleton",
  "skin_set_radius",
  "lattice_create",
  "lattice_bind",
  "lattice_edit_point",
  "lattice_get_points",
  "mesh_set_proportional_edit",
  "system_set_mode",
  "system_undo",
  "system_redo",
  "system_save_file",
  "system_new_file",
  "system_snapshot",
  "bake_normal_map",
  "bake_ao",
  "bake_combined",
  "bake_diffuse",
  "import_obj",
  "import_fbx",
  "import_glb",
  "import_image_as_plane",
  "extraction_deep_topology",
  "extraction_component_separate",
  "extraction_detect_symmetry",
  "extraction_edge_loop_analysis",
  "extraction_face_group_analysis",
  "extraction_render_angles",
  "armature_create",
  "armature_add_bone",
  "armature_bind",
  "armature_pose_bone",
  "armature_weight_paint_assign",
  "armature_get_data",
  "workflow_catalog",
  "router_set_goal",
  "router_get_status",
  "router_clear_goal"
]
```

</details>

**⚠️ Important Network Configuration:**
*   **macOS/Windows:** Use `host.docker.internal` (as shown in the first config). The `--network host` option does NOT work on Docker Desktop for Mac/Windows.
*   **Linux:** Use `--network host` with `127.0.0.1` (as shown in the second config).
*   **Troubleshooting:** If the MCP server starts but cannot connect to Blender (timeout errors), ensure Blender is running with the addon enabled and that port `8765` is not blocked.

<details>
<summary><strong>Viewport Output Modes &amp; Temp Directory Mapping</strong></summary>

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

</details>

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=PatrykIti/blender-ai-mcp&type=date&legend=top-left)](https://www.star-history.com/#PatrykIti/blender-ai-mcp&type=date&legend=top-left)

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) to understand our Clean Architecture standards before submitting a Pull Request.

## 🧩 Community & Support

- Support: [SUPPORT.md](SUPPORT.md)
- Security: [SECURITY.md](SECURITY.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## 👨‍💻 Author

**Patryk Ciechański**
*   GitHub: [PatrykIti](https://github.com/PatrykIti)

## License

This project is licensed under the **Business Source License 1.1 (BSL 1.1)**  
with a custom Additional Use Grant authored by Patryk Ciechański (PatrykIti).

The license automatically converts to **Apache 2.0** on 2029-12-01.

For the full license text, see: [LICENSE](./LICENSE.md)

Change License text (Apache 2.0): [LICENSE-APACHE-2.0.txt](./LICENSE-APACHE-2.0.txt)
