# MCP Server Documentation

Documentation for the MCP Server (Client Side).

## 📚 Topic Index

- **[Clean Architecture](./clean_architecture.md)**
  - Detailed description of layers and control flow (DI).
  - Dependency separation principles implemented in version 0.1.5.
- **[FastMCP 3.x Migration Matrix](./fastmcp_3x_migration_matrix.md)**
  - Maps the current flat/runtime-coupled MCP server to the target provider/factory/transform model for TASK-083 through TASK-097.
- **[Runtime Baseline Matrix](./runtime_baseline_matrix.md)**
  - Defines the supported Python and FastMCP baseline for the migration series, including 3.1+ feature gates.
- **[FastMCP 3.x Composition Model](./fastmcp_3x_composition.md)**
  - Documents provider groups, surface profiles, transform ordering, and the platform regression harness added during TASK-083.
- **[Tool Layering Policy](./TOOL_LAYERING_POLICY.md)**
  - Canonical policy for layered tools, small public surfaces, hidden atomic tools, `set_goal`-first orchestration, and vision/assert boundaries.
- **[Router / Runtime Responsibility Boundaries](../_ROUTER/RESPONSIBILITY_BOUNDARIES.md)**
  - Defines the role split between FastMCP platform features, LaBSE semantics, router safety policy, and inspection/assertion truth.
  - Use this before changing discovery, semantic matching, correction logic, or structured validation behavior.

## Canonical Tool Policy

The canonical policy for:

- layered tools (`atomic` / `macro` / `workflow`)
- small public LLM-facing catalogs
- hidden atomic tools
- `router_set_goal(...)` as the default production entrypoint
- vision vs measure/assert boundaries

lives here:

- [Tool Layering Policy](./TOOL_LAYERING_POLICY.md)

This README is a surface/runtime reference doc. If it conflicts with the policy
doc above, the policy doc wins.

## FastMCP 3.x Migration Baseline

The MCP server is in the middle of a platform migration tracked by `TASK-083` through `TASK-097`.

For this task series:

- the task-capable runtime baseline is **FastMCP 3.1.1 + pydocket 0.18.2**
- the supported server baseline is **Python 3.11+**
- **FastMCP 3.1+** remains the line required for built-in Tool Search / BM25, Code Mode work, and the current task-capable surfaces
- the current runtime inventory lives in `server/adapters/mcp/platform/runtime_inventory.py`

The migration matrix and runtime matrix linked above are the canonical audit docs for Gate 0.
The composition document linked above is the canonical reference for the current factory/provider/transform baseline.

## LLM-Guided Public Surface Baseline

The first `llm-guided` public contract line is now available on top of the canonical internal tool surface.

Current public tool aliases:

| Internal tool | `llm-guided` public name |
|---|---|
| `scene_context` | `check_scene` |
| `scene_inspect` | `inspect_scene` |
| `scene_configure` | `configure_scene` |
| `workflow_catalog` | `browse_workflows` |

Current public argument aliases:

| Tool | Internal arg | `llm-guided` public arg |
|---|---|---|
| `check_scene` | `action` | `query` |
| `inspect_scene` | `object_name` | `target_object` |
| `configure_scene` | `settings` | `config` |
| `browse_workflows` | `workflow_name` | `name` |
| `browse_workflows` | `query` | `search_query` |

Current hidden/expert-only arguments on `llm-guided` include:

- `inspect_scene`: `detailed`, `include_disabled`, `modifier_name`, `assistant_summary`, and other backend-only inspection flags
- `mesh_inspect`: `selected_only`, `uv_layer`, `include_deltas`, `assistant_summary`
- `scene_snapshot_state`, `scene_compare_snapshot`, `scene_get_hierarchy`, `scene_get_bounding_box`, and `scene_get_origin_info`: `assistant_summary`
- `browse_workflows`: `top_k`, `threshold`, chunk/session import internals, and related expert-only knobs

Router and dispatcher internals still operate on canonical internal names.
The public alias layer is a transform concern, not a second business-logic path.

## Surface Exposure Matrix

High-level intended posture:

| Surface | Public Layer | Goal-First | Use |
|---|---|---|---|
| `legacy-manual` | broad manual/control | no | maintainer/manual direct usage |
| `legacy-flat` | compatibility/control | optional | compatibility and broad control |
| `llm-guided` | small curated public catalog | yes | normal production LLM usage |
| `internal-debug` | debug/maintainer | optional | maintainer/debug |
| `code-mode-pilot` | experimental read-only analytical surface | no | analytical experiments |

For the governing rules behind this matrix, use the canonical policy doc above.

## Hidden Atomic Layer And Escape Hatches

Production-oriented public surfaces should not behave as though every internal
tool is a normal public discovery candidate.

Current governing rules:

- atomic tools are primarily the implementation substrate
- macro/workflow tools should dominate the public LLM-facing action space
- discovery should not leak hidden atomic tools into normal bootstrap usage
- any public single-purpose atomic tools should be explicit escape hatches, not
  the default surface model

Typical public escape hatches that remain acceptable:

- `router_set_goal`
- `router_get_status`
- truth/inspection essentials
- explicit measure/assert tools as they are introduced

On `llm-guided`, the phased escape-hatch layer is intentionally narrower than
the full runtime inventory. Specialist families such as armature, sculpt, text,
baking, and similar maintainer-oriented areas stay off the normal guided
surface until a stronger macro layer exists.

The canonical policy file above governs this rule set.

## Goal-First Requirement

For normal production-oriented LLM surfaces, the expected interaction model is:

1. `router_set_goal(...)`
2. use the shaped public surface in the context of that goal
3. perform verification and before/after analysis against the active goal

Current exception surfaces:

- `legacy-manual`
- `internal-debug`
- `code-mode-pilot`

These may intentionally skip strict goal-first usage, but they are not the
default product path for normal LLM operation.

## Session Context Contract

Once a goal is set, downstream layers should be able to rely on:

- active goal / user intent
- current modeling phase
- current target object/component when known
- expected verification criteria
- the frame of reference for before/after visual interpretation

This context model is part of the current architecture direction and should be
preserved as later tool and vision waves are added.

## Macro vs Workflow Tool Rules

Current product direction:

- **macro tools** are the preferred default LLM-facing layer
- **workflow tools** are bounded process tools, not catch-all “do anything” tools

Macro tools should:

- represent one meaningful task responsibility
- orchestrate atomic tools internally when needed
- return task-relevant structured outputs

Workflow tools should:

- remain bounded
- orchestrate macro tools, atomic tools, rule checks, and verification
- return structured reports that answer:
  - what changed
  - what passed
  - what failed
  - what to do next if verification failed

## Vision, Measurement, and Assertion

The intended verification model is:

- vision = interpretation support
- measurement/assertion = truth layer

Preferred before/after analysis contract:

1. before capture
2. action/change
3. after capture
4. structured compare/summary

Expected standard view set when visual comparison matters:

- front
- side
- top
- iso
- focus-target view when needed

The first implemented deterministic verification slice now includes:

- `scene_measure_dimensions`
- `scene_measure_distance`
- `scene_measure_gap`
- `scene_measure_overlap`
- `scene_measure_alignment`

The broader truth layer should continue to expand with:

- proportion
- symmetry
- containment

Lightweight vision models are acceptable for:

- summarizing visual change
- localizing likely issues
- comparing before/after imagery

They should not override deterministic measure/assert results.

## Search-First Discovery Rollout

The default `llm-guided` surface now runs search-first discovery by default.

Current visible entry set on `llm-guided`:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `list_prompts`
- `get_prompt`
- `search_tools`
- `call_tool`

Measured baseline from the current unit suite:

- `legacy-manual`: `162` visible tools, router/workflow capabilities omitted from the namespace
- `legacy-flat`: `169` visible tools, now fitting in one `tools/list` page by default for compatibility clients
- `llm-guided`: `7` visible tools

Search-first behavior now respects guided visibility:

- hidden tools do not appear in bootstrap-phase search results
- hidden tools cannot be invoked through `call_tool`
- direct public calls and discovered `call_tool` calls share the same guided-surface router failure behavior

## Session-Adaptive Visibility Baseline

The `llm-guided` surface now has a first complete guided-mode visibility baseline:

- canonical coarse phases: `bootstrap`, `planning`, `build`, `inspect_validate`
- guided entry surface at bootstrap/planning centered on `router_*` and `workflow_catalog`
- deterministic phase/profile visibility rules owned by FastMCP platform code, not by router metadata
- native FastMCP session visibility application via `enable_components`, `disable_components`, and `reset_visibility`
- operator-facing visibility diagnostics exposed through `router_get_status()`

This visibility baseline is complete for guided-mode surface shaping.
Search-first default rollout remains a separate TASK-084 concern.

## Structured Elicitation Baseline

Missing-input handling is now a first-class interaction layer:

- `router_set_goal` uses native FastMCP elicitation on async-capable guided surfaces
- non-elicitation / tool-only clients receive a typed `needs_input` fallback payload
- fallback payloads carry stable `question_set_id`, field ids, and optional `request_id`
- session state persists pending clarification identity, partial answers, and last elicitation action
- `workflow_catalog` import conflicts reuse the same typed clarification payload shape for compatibility mode

## Structured Contract Baseline

The structured-contract layer now covers the high-value state-heavy MCP surfaces:

- `macro_cutout_recess`
- `scene_context`
- `scene_inspect`
- `scene_create`
- `scene_configure`
- `mesh_select`
- `mesh_select_targeted`
- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_custom_properties`
- `scene_get_hierarchy`
- `scene_get_bounding_box`
- `scene_get_origin_info`
- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`
- `scene_assert_contact`
- `scene_assert_dimensions`
- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`
- `mesh_inspect`
- `router_set_goal`
- `router_get_status`
- `workflow_catalog`

These tools return native structured payloads on contract-enabled paths and use the shared contract helpers/output-schema policy instead of prose-first JSON-string wrappers.

## Server-Side Sampling Assistants Baseline

The MCP adapter layer now has a bounded sampling-assistant baseline for analytical/recovery helpers inside one active MCP request.

Current assistant-enabled paths:

- `scene_inspect(..., assistant_summary=True)` on internal/expert paths
- `mesh_inspect(..., assistant_summary=True)` on internal/expert paths
- `scene_snapshot_state(..., assistant_summary=True)` on internal/expert paths
- `scene_compare_snapshot(..., assistant_summary=True)` on internal/expert paths
- `scene_get_hierarchy(..., assistant_summary=True)` on internal/expert paths
- `scene_get_bounding_box(..., assistant_summary=True)` on internal/expert paths
- `scene_get_origin_info(..., assistant_summary=True)` on internal/expert paths
- `router_set_goal()` when the goal flow ends in `no_match` or `error`
- `router_get_status()` when the latest router/session diagnostics indicate a recovery path
- `workflow_catalog()` when import-oriented flows enter `needs_input`, `skipped`, or explicit error states

Current typed assistant statuses:

- `success`
- `unavailable`
- `masked_error`
- `rejected_by_policy`

Governance notes:

- assistants are request-bound and reject background-task execution
- assistants are adapter-scoped helpers, not a fifth truth/policy authority
- assistants may summarize inspection contracts or draft repair guidance from diagnostics
- assistants must not replace router safety policy or inspection truth

## Versioned Client Surface Baseline

The repo now has an explicit contract-line matrix on top of the existing surface profiles:

| Surface Profile | Default Contract Line |
|---|---|
| `legacy-manual` | `legacy-v1` |
| `legacy-flat` | `legacy-v1` |
| `llm-guided` | `llm-guided-v2` |
| `internal-debug` | `llm-guided-v2` |
| `code-mode-pilot` | `llm-guided-v2` |

Current guided-surface rollback/coexistence path:

- `llm-guided-v1` = earlier guided public line
- `llm-guided-v2` = current guided public line

Bootstrap/config can override the default contract line through `MCP_DEFAULT_CONTRACT_LINE`.
Version filtering is applied in the transform pipeline; profile selection and contract-line selection remain separate axes.

## Telemetry And Timeout Foundations

The platform now has the first operations baseline for telemetry and timeout policy:

- optional OTEL bootstrap through `OTEL_ENABLED`, `OTEL_EXPORTER`, and `OTEL_SERVICE_NAME`
- repo-specific router spans emitted on top of the current MCP runtime
- explicit timeout policy object attached at factory bootstrap
- canonical timeout boundary names:
  - `mcp_tool`
  - `mcp_task`
  - `rpc_client`
  - `addon_execution`
- `router_get_status()` now exposes:
  - active surface/profile
  - active contract line
  - timeout policy snapshot
  - task runtime pair
  - telemetry bootstrap state
  - background job counts and job summaries

## Pagination Baseline

Pagination is now split explicitly between:

- component pagination via surface `list_page_size`
- payload pagination via structured contract fields such as `offset`, `limit`, `returned`, `total`, and `has_more`

Current payload-pagination coverage includes:

- `mesh_inspect`
- `workflow_catalog(action="list")`
- `workflow_catalog(action="search")`

## Prompt Layer Baseline

The prompt layer is now part of the MCP product surface:

- native prompt components expose curated prompt assets from `_docs/_PROMPTS`
- tool-only clients can use:
  - `list_prompts`
  - `get_prompt`
- `recommended_prompts` provides phase/profile-aware recommendations

## Code Mode Pilot Baseline

The repo now has a first experimental `code-mode-pilot` surface.

Current guardrails:

- the pilot is explicit, opt-in, and profile-scoped
- the pilot uses FastMCP `CodeMode` on top of the existing composed MCP surface
- the pilot keeps a read-only allowlist by visibility policy before Code Mode collapses the catalog
- the sandbox dependency fails fast if `pydantic-monty` is unavailable
- prompt bridge tools remain available (`list_prompts`, `get_prompt`) alongside Code Mode meta-tools

Current pilot meta-tool surface:

- `search`
- `get_schema`
- `tags`
- `execute`
- `list_prompts`
- `get_prompt`

Current benchmark baselines for the experiment:

- `legacy-flat`
- `llm-guided`
- `code-mode-pilot`

Current recommendation:

- keep `legacy-manual` as the direct manual surface with no router/workflow exposure
- keep `code-mode-pilot` as an experimental read-only surface
- keep `llm-guided` as the primary production baseline
- do not promote Code Mode to the default execution path for write/destructive Blender work

## Background Task Mode Baseline

The current task-mode rollout now covers the initial heavy-operation slice plus the system import/export family on task-capable surfaces.

Adopted endpoints:

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

Current product semantics:

- adopted tools register explicit `TaskConfig(mode="optional")`
- task-capable surfaces can submit them as background work without changing canonical tool names
- legacy/foreground clients keep a synchronous fallback path
- Blender-backed task mode now uses explicit RPC verbs for launch, poll, cancel, and collect
- workflow import finalization uses the same MCP-side task bookkeeping without requiring addon RPC

Task-capable profile guidance is now included directly in the surface instructions for:

- `llm-guided`
- `internal-debug`
- `code-mode-pilot`

## Correction Audit Exposure Baseline

Router-aware MCP execution now exposes a correction-transparency baseline on top of the FastMCP 3.x platform work:

- structured execution reports carry `router_disposition`, `audit_events`, `audit_ids`, and `verification_status`
- corrected execution paths expose correlatable audit ids both in MCP-facing response contracts and in router telemetry/logging
- high-risk precondition fixes use inspection-based verification for `mode`, `selection`, and `active_object`
- legacy string rendering remains available for compatibility, but audit/report fields are the canonical machine-readable record

## Runtime Baseline

The current support policy for the migration track is:

- **Supported task-capable pair**: Python `3.11+` with `fastmcp 3.1.1` and `pydocket 0.18.2`
- **Required line for current platform work**: FastMCP `3.1.x`
- **Not supported for TASK-083+ migration work**: Python `3.10`

This keeps the runtime policy aligned with the repo's practical dependency set (`sentence-transformers`, `lancedb`, `pyarrow`) and with the now-shipped task-mode surfaces.

## 🚀 Running (Docker)

The server can be run in a Docker container for environment isolation.

### 1. Build Image
```bash
docker build -t blender-ai-mcp .
```

### 2. Run
To allow the container server to connect to Blender on the host, configure the network properly.

**MacOS / Windows:**
```bash
docker run -i --rm -e BLENDER_RPC_HOST=host.docker.internal blender-ai-mcp
```

**Linux:**
```bash
docker run -i --rm --network host -e BLENDER_RPC_HOST=127.0.0.1 blender-ai-mcp
```

*(The `-i` flag is crucial for the interactive stdio communication used by MCP)*.

## 🛠 Available Tools

### 🧠 Grouped Public Tools

These grouped tools are part of the current public working layer.
They should now be understood through the layered policy in
`TOOL_LAYERING_POLICY.md`: grouped public tools above a hidden/internal atomic
layer.

| Grouped Tool | Actions | Description |
|-----------|---------|-------------|
| `scene_context` | `mode`, `selection` | Quick context queries (mode, selection state). |
| `scene_create` | `light`, `camera`, `empty` | Creates scene helper objects. |
| `scene_inspect` | `object`, `topology`, `modifiers`, `materials`, `constraints`, `modifier_data`, `render`, `color_management`, `world` | Detailed inspection queries for objects plus scene-level render/color/world state, including node-graph handoff fields for node-based worlds. |
| `scene_configure` | `render`, `color_management`, `world` | Applies grouped render, color-management, and bounded world/background settings from structured input. Full node-graph rebuild stays outside this tool. |
| `mesh_select` | `all`, `none`, `linked`, `more`, `less`, `boundary` | Simple selection operations. |
| `mesh_select_targeted` | `by_index`, `loop`, `ring`, `by_location` | Targeted selection with parameters. |
| `mesh_inspect` | `summary`, `vertices`, `edges`, `faces`, `uvs`, `normals`, `attributes`, `shape_keys`, `group_weights` | Mesh introspection with summary and raw data. |

**Current grouped public set:** 7 high-frequency grouped tools.

### Scene Tools
Managing objects at the scene level.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `scene_configure` | `action` (`render`/`color_management`/`world`), `settings` (object) | Applies grouped scene appearance settings. `world` is intentionally bounded, surfaces explicit node-graph handoff fields, and does not author arbitrary world node graphs. |
| `scene_list_objects` | *none* | Returns a list of all objects in the scene with their type and position. |
| `scene_delete_object` | `name` (str) | Deletes the specified object. Returns error if object does not exist. |
| `scene_clean_scene` | `keep_lights_and_cameras` (bool, default True) | Deletes objects from scene. If `True`, preserves cameras and lights. If `False`, cleans the project completely ("hard reset"). |
| `scene_duplicate_object` | `name` (str), `translation` ([x,y,z]) | Duplicates an object and optionally moves it. |
| `scene_set_active_object` | `name` (str) | Sets the active object (crucial for context-dependent operations). |
| `scene_set_mode` | `mode` (str) | Sets interaction mode (OBJECT, EDIT, SCULPT, etc.). |
| `scene_snapshot_state` | `include_mesh_stats` (bool), `include_materials` (bool) | Captures a structured JSON snapshot of scene state with SHA256 hash for change detection. |
| `scene_compare_snapshot` | `baseline_snapshot` (str), `target_snapshot` (str), `ignore_minor_transforms` (float) | Compares two snapshots and returns diff summary (added/removed/modified objects). |
| `scene_camera_orbit` | `angle_horizontal` (float), `angle_vertical` (float), `target_object` (str, optional), `target_point` ([x,y,z], optional) | Orbits the viewport around a target object or point. |
| `scene_camera_focus` | `object_name` (str), `zoom_factor` (float) | Focuses the viewport on one object. Use `object_name` here, not `target`, `target_object`, or `focus_target`. |
| `scene_get_viewport` | `width` (int), `height` (int), `shading` (str), `camera_name` (str), `focus_target` (str), `output_mode` (str) | Returns a rendered image. `shading`: WIREFRAME/SOLID/MATERIAL. `camera_name`: specific cam or "USER_PERSPECTIVE". `focus_target`: object to frame. `output_mode`: IMAGE (default Image resource), BASE64 (raw string), FILE (host-visible path), MARKDOWN (inline preview + path). |
| `scene_get_custom_properties` | `object_name` (str) | Gets custom properties (metadata) from an object. Returns object_name, property_count, and properties dict. |
| `scene_set_custom_property` | `object_name` (str), `property_name` (str), `property_value` (str/int/float/bool), `delete` (bool) | Sets or deletes a custom property on an object. |
| `scene_get_hierarchy` | `object_name` (str, optional), `include_transforms` (bool) | Gets parent-child hierarchy for specific object or full scene tree. |
| `scene_get_bounding_box` | `object_name` (str), `world_space` (bool) | Gets bounding box corners, min/max, center, dimensions, and volume. |
| `scene_get_origin_info` | `object_name` (str) | Gets origin (pivot point) information relative to geometry and bounding box. |
| `scene_measure_distance` | `from_object` (str), `to_object` (str), `reference` (str) | Measures origin-to-origin or bbox-center distance between two objects. |
| `scene_measure_dimensions` | `object_name` (str), `world_space` (bool) | Measures object dimensions and volume from its bounding box. |
| `scene_measure_gap` | `from_object` (str), `to_object` (str), `tolerance` (float) | Measures nearest world-space bbox gap/contact state between two objects. |
| `scene_measure_alignment` | `from_object` (str), `to_object` (str), `axes` (array), `reference` (str), `tolerance` (float) | Measures bbox alignment deltas on chosen axes using CENTER/MIN/MAX references. |
| `scene_measure_overlap` | `from_object` (str), `to_object` (str), `tolerance` (float) | Measures bbox overlap/touching state plus intersection dimensions and volume. |
| `scene_assert_contact` | `from_object` (str), `to_object` (str), `max_gap` (float), `allow_overlap` (bool) | Asserts pass/fail contact relation from measured gap and overlap state. |
| `scene_assert_dimensions` | `object_name` (str), `expected_dimensions` (array), `tolerance` (float), `world_space` (bool) | Asserts pass/fail dimensions against an expected vector within tolerance. |
| `scene_assert_containment` | `inner_object` (str), `outer_object` (str), `min_clearance` (float), `tolerance` (float) | Asserts pass/fail containment plus measured clearance/protrusion details. |
| `scene_assert_symmetry` | `left_object` (str), `right_object` (str), `axis` (str), `mirror_coordinate` (float), `tolerance` (float) | Asserts mirrored symmetry between two objects across a chosen axis. |
| `scene_assert_proportion` | `object_name` (str), `axis_a` (str), `expected_ratio` (float), `axis_b` (str), `reference_object` (str), `reference_axis` (str), `tolerance` (float), `world_space` (bool) | Asserts pass/fail ratio/proportion against the expected value. |
> **Note:** Tools like `scene_get_mode`, `scene_list_selection`, `scene_inspect_*`, and `scene_create_*` have been consolidated into grouped public tools. Use `scene_context`, `scene_inspect`, and `scene_create` instead.
> `scene_get_constraints` is now internal to `scene_inspect(action="constraints")` for MCP clients.

### Collection Tools
Organizational tools for managing Blender collections.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within a collection, optionally recursive through child collections. |
| `collection_manage` | `action` (create/delete/rename/move_object/link_object/unlink_object), `collection_name`, `new_name`, `parent_name`, `object_name` | Manages collections: create, delete, rename, and move/link/unlink objects between collections. |

### Material Tools
Material and shader management.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `material_list` | `include_unassigned` (bool) | Lists all materials with Principled BSDF parameters and object assignment counts. |
| `material_list_by_object` | `object_name` (str), `include_indices` (bool) | Lists material slots for a specific object. |
| `material_create` | `name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Creates new PBR material with Principled BSDF shader. |
| `material_assign` | `material_name`, `object_name`, `slot_index`, `assign_to_selection` | Assigns material to object or selected faces (Edit Mode). |
| `material_set_params` | `material_name`, `base_color`, `metallic`, `roughness`, `emission_color`, `emission_strength`, `alpha` | Modifies existing material parameters. |
| `material_set_texture` | `material_name`, `texture_path`, `input_name`, `color_space` | Binds image texture to material input (supports Normal maps). |
| `material_inspect_nodes` | `material_name` (str), `include_connections` (bool) | Inspects material shader node graph, returns nodes with types, inputs, outputs, and connections. |

### UV Tools
Texture coordinate mapping operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `uv_list_maps` | `object_name` (str), `include_island_counts` (bool) | Lists UV maps for a mesh object with active flags and loop counts. |
| `uv_unwrap` | `object_name` (str), `method` (str), `angle_limit` (float), `island_margin` (float), `scale_to_bounds` (bool) | Unwraps selected faces to UV space using projection methods (SMART_PROJECT, CUBE, CYLINDER, SPHERE, UNWRAP). |
| `uv_pack_islands` | `object_name` (str), `margin` (float), `rotate` (bool), `scale` (bool) | Packs UV islands for optimal texture space usage. |
| `uv_create_seam` | `object_name` (str), `action` (str) | Marks or clears UV seams on selected edges ('mark' or 'clear'). |

### Macro Tools
Bounded multi-step tools above the atomic layer and below full workflows.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `macro_cutout_recess` | `target_object` (str), `width` (float), `height` (float), `depth` (float), `face` (str), `offset` ([x,y,z]), `mode` (str), `bevel_width` (float), `bevel_segments` (int), `cleanup` (str), `cutter_name` (str) | Creates one bounded recess/cutout by orchestrating cutter creation, placement, optional bevel, boolean application, and helper cleanup on a target object. |

### Modeling Tools
Geometry creation and editing.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `modeling_create_primitive` | `primitive_type` (str), `size` (float), `location` ([x,y,z]), `rotation` ([x,y,z]) | Creates a simple 3D object (Cube, Sphere, Cylinder, Plane, Cone, Torus, Monkey). |
| `modeling_transform_object` | `name` (str), `location` (opt), `rotation` (opt), `scale` (opt) | Changes position, rotation, or scale of an existing object. |
| `modeling_add_modifier` | `name` (str), `modifier_type` (str), `properties` (dict) | Adds a non-destructive object modifier (e.g., `SUBSURF`, `BEVEL`). Successful addon responses use structured modifier metadata under the hood. |
| `modeling_apply_modifier` | `name` (str), `modifier_name` (str) | Applies a modifier, permanently changing the mesh geometry. |
| `modeling_convert_to_mesh` | `name` (str) | Converts a non-mesh object (e.g., Curve, Text, Surface) to a mesh. |
| `modeling_join_objects` | `object_names` (list[str]) | Joins multiple mesh objects into a single one. |
| `modeling_separate_object` | `name` (str), `type` (str) | Separates a mesh object into new objects (LOOSE, SELECTED, MATERIAL). |
| `modeling_set_origin` | `name` (str), `type` (str) | Sets the origin point of an object (e.g., ORIGIN_GEOMETRY_TO_CURSOR). |
| `modeling_list_modifiers` | `name` (str) | Lists all modifiers currently on the specified object. |
| `metaball_create` | `name`, `location`, `element_type`, `radius`, `resolution`, `threshold` | Creates a metaball object for organic blob shapes. |
| `metaball_add_element` | `metaball_name`, `element_type`, `location`, `radius`, `stiffness` | Adds element to existing metaball for merging. |
| `metaball_to_mesh` | `metaball_name`, `apply_resolution` | Converts metaball to mesh for editing. |
| `skin_create_skeleton` | `name`, `vertices`, `edges`, `location` | Creates skeleton mesh with Skin modifier for tubular structures. |
| `skin_set_radius` | `object_name`, `vertex_index`, `radius_x`, `radius_y` | Sets skin radius at vertices for varying thickness. |

> **Note:** `modeling_get_modifier_data` is now internal to `scene_inspect(action="modifier_data")` for MCP clients.

### Mesh Tools (Edit Mode)
Low-level geometry manipulation.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `mesh_delete_selected` | `type` (str) | Deletes selected elements ('VERT', 'EDGE', 'FACE'). |
| `mesh_extrude_region` | `move` (list[float]) | Extrudes selected region and optionally translates it. |
| `mesh_fill_holes` | *none* | Creates faces from selection (F key). |
| `mesh_bevel` | `offset`, `segments` | Bevels selected geometry. |
| `mesh_loop_cut` | `number_cuts` | Adds cuts (subdivides) to selection. |
| `mesh_inset` | `thickness`, `depth` | Insets selected faces. |
| `mesh_boolean` | `operation`, `solver='EXACT'` | Boolean op (Unselected - Selected). Note: FAST solver removed in Blender 5.0+. |
| `mesh_merge_by_distance` | `distance` | Remove doubles / merge vertices. |
| `mesh_subdivide` | `number_cuts`, `smoothness` | Subdivides selected geometry. |
| `mesh_smooth` | `iterations`, `factor` | Smooths selected vertices using Laplacian smoothing. |
| `mesh_flatten` | `axis` | Flattens selected vertices to plane (X/Y/Z). |
| `mesh_list_groups` | `object_name`, `group_type` | Lists vertex groups or face maps/attributes. |
| `mesh_randomize` | `amount`, `uniform`, `normal`, `seed` | Randomizes vertex positions for organic surfaces. |
| `mesh_shrink_fatten` | `value` | Moves vertices along their normals (inflate/deflate). |
| `mesh_create_vertex_group` | `object_name`, `name` | Creates a new vertex group on mesh object. |
| `mesh_assign_to_group` | `object_name`, `group_name`, `weight` | Assigns selected vertices to vertex group. |
| `mesh_remove_from_group` | `object_name`, `group_name` | Removes selected vertices from vertex group. |
| `mesh_bisect` | `plane_co`, `plane_no`, `clear_inner`, `clear_outer`, `fill` | Cuts mesh along a plane. |
| `mesh_edge_slide` | `value` | Slides selected edges along mesh topology. |
| `mesh_vert_slide` | `value` | Slides selected vertices along connected edges. |
| `mesh_triangulate` | *none* | Converts selected faces to triangles. |
| `mesh_remesh_voxel` | `voxel_size`, `adaptivity` | Remeshes object using Voxel algorithm (Object Mode). |
| `mesh_transform_selected` | `translate`, `rotate`, `scale`, `pivot` | Transforms selected geometry (move/rotate/scale). **CRITICAL** |
| `mesh_bridge_edge_loops` | `number_cuts`, `interpolation`, `smoothness`, `twist` | Bridges two edge loops with faces. |
| `mesh_duplicate_selected` | `translate` | Duplicates selected geometry within the same mesh. |
| `mesh_spin` | `steps`, `angle`, `axis`, `center`, `dupli` | Spins/lathes selected geometry around an axis. |
| `mesh_screw` | `steps`, `turns`, `axis`, `center`, `offset` | Creates spiral/screw geometry from selected profile. |
| `mesh_add_vertex` | `position` | Adds a single vertex at the specified position. |
| `mesh_add_edge_face` | *none* | Creates edge or face from selected vertices (F key). |
| `mesh_edge_crease` | `crease_value` | Sets crease weight on selected edges (0.0-1.0) for Subdivision Surface control. |
| `mesh_bevel_weight` | `weight` | Sets bevel weight on selected edges (0.0-1.0) for selective beveling. |
| `mesh_mark_sharp` | `action` | Marks ('mark') or clears ('clear') sharp edges for Smooth by Angle (5.0+). |
| `mesh_dissolve` | `dissolve_type`, `angle_limit`, `use_face_split`, `use_boundary_tear` | Dissolves geometry (limited/verts/edges/faces) while preserving shape. |
| `mesh_tris_to_quads` | `face_threshold`, `shape_threshold` | Converts triangles to quads based on angle thresholds. |
| `mesh_normals_make_consistent` | `inside` | Recalculates normals to face consistently outward (or inward if inside=True). |
| `mesh_decimate` | `ratio`, `use_symmetry`, `symmetry_axis` | Reduces polycount while preserving shape (Edit Mode). |
| `mesh_knife_project` | `cut_through` | Projects cut from selected geometry (requires view angle). |
| `mesh_rip` | `use_fill` | Rips (tears) geometry at selected vertices. |
| `mesh_split` | *none* | Splits selection from mesh (disconnects without separating). |
| `mesh_edge_split` | *none* | Splits mesh at selected edges (creates seams). |
| `mesh_set_proportional_edit` | `enabled`, `falloff_type`, `size`, `use_connected` | Configures proportional editing mode for organic deformations. |
| `mesh_symmetrize` | `direction`, `threshold` | Makes mesh symmetric by mirroring one side to the other. |
| `mesh_grid_fill` | `span`, `offset`, `use_interp_simple` | Fills boundary with a grid of quads (superior to triangle fill). |
| `mesh_poke_faces` | `offset`, `use_relative_offset`, `center_mode` | Pokes faces (adds vertex at center, creates triangle fan). |
| `mesh_beautify_fill` | `angle_limit` | Rearranges triangles to more uniform triangulation. |
| `mesh_mirror` | `axis`, `use_mirror_merge`, `merge_threshold` | Mirrors selected geometry within the same object. |

> **Note:** Mesh introspection tools (`mesh_get_*`) are consolidated into `mesh_inspect` for MCP clients. Router can still call internal actions via handler metadata.

> **Note:** Selection tools (`mesh_select_all`, `mesh_select_by_index`, `mesh_select_loop`, etc.) have been consolidated into grouped public tools. Use `mesh_select` and `mesh_select_targeted` instead.

### Curve Tools
Curve creation and conversion.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `curve_create` | `curve_type`, `location` | Creates curve primitive (BEZIER, NURBS, PATH, CIRCLE). |
| `curve_to_mesh` | `object_name` | Converts curve object to mesh geometry. |
| `curve_get_data` | `object_name` | Returns curve splines, points, and settings. |

### Text Tools
3D typography and text annotations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `text_create` | `text`, `name`, `location`, `font`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Creates 3D text object with optional extrusion and bevel. |
| `text_edit` | `object_name`, `text`, `size`, `extrude`, `bevel_depth`, `bevel_resolution`, `align_x`, `align_y` | Edits existing text object content and properties. |
| `text_to_mesh` | `object_name`, `keep_original` | Converts text to mesh for game export and editing. |

### Sculpt Tools
Sculpt Mode operations for organic shape manipulation.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `sculpt_auto` | `operation` (smooth/inflate/flatten/sharpen), `strength`, `iterations`, `use_symmetry`, `symmetry_axis` | High-level sculpt operation using mesh filters. Applies to entire mesh. Recommended for AI workflows. |
| `sculpt_deform_region` | `center`, `radius`, `delta`, `strength`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically deforms a local mesh region. Programmatic replacement for brush-style grab behavior. |
| `sculpt_crease_region` | `center`, `radius`, `depth`, `pinch`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically creates a local crease/groove region. Programmatic replacement for brush-style crease behavior. |
| `sculpt_smooth_region` | `center`, `radius`, `strength`, `iterations`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically smooths a local mesh region using edge-adjacency averaging. |
| `sculpt_inflate_region` | `center`, `radius`, `amount`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically inflates or deflates a local mesh region. |
| `sculpt_pinch_region` | `center`, `radius`, `amount`, `falloff`, `use_symmetry`, `symmetry_axis` | Deterministically pinches a local mesh region toward the influence center. |
| `sculpt_enable_dyntopo` | `detail_mode`, `detail_size`, `use_smooth_shading` | Enables Dynamic Topology for automatic geometry addition. |
| `sculpt_disable_dyntopo` | *none* | Disables Dynamic Topology. |
| `sculpt_dyntopo_flood_fill` | *none* | Applies current detail level to entire mesh. |

> **Note:** For reliable AI workflows, use `sculpt_auto`, `sculpt_deform_region`, `sculpt_crease_region`, `sculpt_smooth_region`, `sculpt_inflate_region`, and `sculpt_pinch_region`.

### Export Tools
File export operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `export_glb` | `filepath`, `export_selected`, `export_animations`, `export_materials`, `apply_modifiers` | Exports to GLB/GLTF format (web, game engines). |
| `export_fbx` | `filepath`, `export_selected`, `export_animations`, `apply_modifiers`, `mesh_smooth_type` | Exports to FBX format (industry standard). |
| `export_obj` | `filepath`, `export_selected`, `apply_modifiers`, `export_materials`, `export_uvs`, `export_normals`, `triangulate` | Exports to OBJ format (universal mesh). |

### Import Tools
File import operations.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `import_obj` | `filepath`, `use_split_objects`, `use_split_groups`, `global_scale`, `forward_axis`, `up_axis` | Imports OBJ file (geometry, UVs, normals). |
| `import_fbx` | `filepath`, `use_custom_normals`, `use_image_search`, `ignore_leaf_bones`, `automatic_bone_orientation`, `global_scale` | Imports FBX file (geometry, materials, animations). |
| `import_glb` | `filepath`, `import_pack_images`, `merge_vertices`, `import_shading` | Imports GLB/GLTF file (PBR materials, animations). |
| `import_image_as_plane` | `filepath`, `name`, `location`, `size`, `align_axis`, `shader`, `use_transparency` | Imports image as textured plane (reference images). |

### Lattice Tools
Non-destructive shape deformation using control point cages.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `lattice_create` | `name`, `target_object`, `location`, `points_u`, `points_v`, `points_w`, `interpolation` | Creates lattice object, auto-fits to target object bounds. |
| `lattice_bind` | `object_name`, `lattice_name`, `vertex_group` | Binds object to lattice via Lattice modifier. |
| `lattice_edit_point` | `lattice_name`, `point_index`, `offset`, `relative` | Moves lattice control points to deform bound objects. |
| `lattice_get_points` | `object_name` | Returns lattice point positions and resolution. |

### Armature Tools
Skeletal rigging and pose utilities.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `armature_create` | `name`, `location`, `bone_name`, `bone_length` | Creates armature with initial bone. |
| `armature_add_bone` | `armature_name`, `bone_name`, `head`, `tail`, `parent_bone`, `use_connect` | Adds bone to existing armature with optional parenting. |
| `armature_bind` | `mesh_name`, `armature_name`, `bind_type` | Binds mesh to armature (AUTO/ENVELOPE/EMPTY). |
| `armature_pose_bone` | `armature_name`, `bone_name`, `rotation`, `location`, `scale` | Poses bone in Pose Mode. |
| `armature_weight_paint_assign` | `object_name`, `vertex_group`, `weight`, `mode` | Assigns weights to selected vertices. |
| `armature_get_data` | `object_name`, `include_pose` | Returns armature bones and hierarchy (optional pose data). |

### System Tools
System-level operations for mode switching, undo/redo, and file management.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `system_set_mode` | `mode`, `object_name` | Switches Blender mode (OBJECT/EDIT/SCULPT/POSE/...) with optional object selection. |
| `system_undo` | `steps` | Undoes last operation(s), max 10 steps per call. |
| `system_redo` | `steps` | Redoes previously undone operation(s), max 10 steps per call. |
| `system_save_file` | `filepath`, `compress` | Saves current .blend file. Auto-generates temp path if unsaved. |
| `system_new_file` | `load_ui` | Creates new file (resets scene to startup). |
| `system_snapshot` | `action`, `name` | Manages quick save/restore checkpoints (save/restore/list/delete). |

### Baking Tools
Texture baking operations using Cycles renderer. Critical for game development workflows.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `bake_normal_map` | `object_name`, `output_path`, `resolution`, `high_poly_source`, `cage_extrusion`, `margin`, `normal_space` | Bakes normal map from geometry or high-poly to low-poly. Supports TANGENT/OBJECT space. |
| `bake_ao` | `object_name`, `output_path`, `resolution`, `samples`, `distance`, `margin` | Bakes ambient occlusion map with configurable samples. |
| `bake_combined` | `object_name`, `output_path`, `resolution`, `samples`, `margin`, `use_pass_direct`, `use_pass_indirect`, `use_pass_color` | Bakes full render (material + lighting) to texture. |
| `bake_diffuse` | `object_name`, `output_path`, `resolution`, `margin` | Bakes diffuse/albedo color only (no lighting). |

### Extraction Tools
Analysis tools for the Automatic Workflow Extraction System (TASK-042). Enables deep topology analysis, component detection, symmetry detection, and multi-angle rendering for LLM Vision integration.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `extraction_deep_topology` | `object_name`, `include_feature_detection` | Deep topology analysis with base primitive detection (CUBE/PLANE/CYLINDER/SPHERE/CUSTOM) and feature detection (bevels, insets, extrusions). |
| `extraction_component_separate` | `object_name`, `analyze_components` | Separates mesh into loose parts for individual analysis. Returns component bounding boxes and centroids. |
| `extraction_detect_symmetry` | `object_name`, `tolerance`, `axes` | Detects X/Y/Z symmetry planes using KDTree with confidence scores (0.0-1.0). |
| `extraction_edge_loop_analysis` | `object_name`, `include_parallel_detection` | Analyzes edge loops, boundary/manifold/non-manifold edges, parallel loop groups, and chamfer edge detection. |
| `extraction_face_group_analysis` | `object_name`, `normal_tolerance`, `height_tolerance` | Analyzes face groups by normal direction, height levels, and inset/extrusion pattern detection. |
| `extraction_render_angles` | `object_name`, `output_dir`, `resolution`, `angles` | Multi-angle renders (front, back, left, right, top, iso) for LLM Vision semantic analysis. |

### Workflow Catalog Tools
Tools for browsing and importing workflow definitions (no execution).

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `workflow_catalog` | `action` (list/get/search/import/import_init/import_append/import_finalize/import_abort), `workflow_name`, `query`, `top_k`, `threshold`, `filepath`, `overwrite`, `content`, `content_type`, `source_name`, `session_id`, `chunk_data`, `chunk_index`, `total_chunks` | Lists/searches/inspects workflows and imports YAML/JSON via file path, inline content, or chunked sessions. Returns `needs_input` when overwrite confirmation is required. |

### Router Tools
Tools for managing the Router Supervisor and executing matched workflows.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `router_set_goal` | `goal` (str), `resolved_params` (dict, optional) | Sets the active build goal for the router session. Returns status (ready/needs_input/no_match/disabled/error), matched workflow info, resolved params with sources, and any unresolved inputs for follow-up calls. |
| `router_get_status` | *none* | Returns current router session state, visibility diagnostics, pending clarification info, and router/component stats. |
| `router_clear_goal` | *none* | Clears the current modeling goal. |

## 🛠 Key Components

### Entry Point (`server/main.py`)
Minimalist entry point.

### Dependency Injection (`server/infrastructure/di.py`)
Set of "Providers" (factory functions). Injects configuration from `server/infrastructure/config.py`.

### Configuration (`server/infrastructure/config.py`)
Environment variable handling (e.g., Blender IP address).

### Application Handlers (`server/application/tool_handlers/`)
Concrete tool logic implementations.
- `scene_handler.py`: Scene operations.
- `modeling_handler.py`: Modeling operations.

### Interfaces (`server/domain/`)
Abstract definitions of system contracts.
- `interfaces/rpc.py`: Contract for RPC client.
- `tools/scene.py`: Contract for scene tools.
- `tools/modeling.py`: Contract for modeling tools.
