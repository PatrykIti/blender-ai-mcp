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
- **[Vision Layer Docs](../_VISION/README.md)**
  - Working notes for vision runtime choices, capture bundles, reference context, and macro/workflow integration.
  - Includes provider/model notes plus the external `vision_contract_profile` model, so transport provider selection stays separate from prompt/schema/parser routing.
- **[LLM Guide v2](../LLM_GUIDE_V2.md)**
  - Strategy doc for typed spatial state, relation/view graphs, and bounded guided handoffs for stronger LLM spatial reasoning.
- **[Spatial Intelligence Research Brief](../FEATURES_LLM_GUIDE_V1.md)**
  - External research handoff describing the current MCP surface plus open questions for LLM/VLM spatial reasoning and geometry-aware planning.
- **[Spatial Intelligence Upgrade Proposal](../Spacial-intelligence-upgrades-for-blender-ai-mcp.md)**
  - Research-derived proposal for scene graphs, Chain-of-Symbol notation, and supporting geometry-library options.
- **[MCP Client Config Examples](./MCP_CLIENT_CONFIG_EXAMPLES.md)**
  - Ready-to-paste local MCP client config examples for `llm-guided`, legacy surfaces, MLX vision, OpenRouter, and Gemini, including optional external contract-profile overrides.
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

Canonical operator guidance for this surface now lives in `_docs/_PROMPTS/`.
When a client drifts on `llm-guided`, treat `GUIDED_SESSION_START.md` as the generic search-first stabilizer and prefer `_PROMPTS/` assets over ad hoc instruction text.

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

Current contract direction for macro/workflow reports:

- macro report contracts are now being prepared to carry optional
  `capture_bundle` and `vision_assistant` artifacts
- this keeps visual interpretation attached to bounded reports instead of
  exposing vision first as a detached free-floating tool
- current runtime scaffolding can already attach deterministic `capture_bundle`
  artifacts to macro reports when vision is enabled, even before full model
  inference is wired into those paths
- MCP macro adapters now have the request-bound attachment point for
  `vision_assistant` once a macro report already carries a capture bundle

## Vision, Measurement, and Assertion

The intended verification model is:

- vision = interpretation support
- measurement/assertion = truth layer

Preferred before/after analysis contract:

1. before capture
2. action/change
3. after capture
4. structured compare/summary

Current scaffold direction:

- the default deterministic `compact` capture profile uses a small preset mix the runtime can already produce reliably:
  - `context_wide`
  - `target_front`
  - `target_side`
  - `target_top`
- a richer `rich` preset profile is also scaffolded for deeper comparison bundles:
  - `context_wide`
  - `target_focus`
  - `target_oblique_left`
  - `target_oblique_right`
  - `target_front`
  - `target_side`
  - `target_top`
  - `target_detail`
- broader canonical view sets such as front/side/top/iso remain the target direction as the scene capture path grows
- capture bundles should carry truth summaries alongside images before the vision layer interprets them

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

Current runtime direction for the vision layer:

- treat vision as an optional adopted capability, not a mandatory bootstrap dependency
- keep local/external backend choice pluggable
- prefer deterministic capture bundles plus truth summaries over one ad hoc viewport image
- keep heavyweight local VLM loading lazy/on-demand instead of tying MCP server startup to it

They should not override deterministic measure/assert results.

## Search-First Discovery Rollout

The default `llm-guided` surface now runs search-first discovery by default.

Current visible entry set on `llm-guided`:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `reference_images`
- `list_prompts`
- `get_prompt`
- `search_tools`
- `call_tool`

Measured baseline from the current unit suite:

- `legacy-manual`: `179` visible tools, router/workflow capabilities omitted from the namespace
- `legacy-flat`: `186` visible tools, now fitting in one `tools/list` page by default for compatibility clients
- `llm-guided`: `8` visible tools

Search-first behavior now respects guided visibility:

- hidden tools do not appear in bootstrap-phase search results
- hidden tools cannot be invoked through `call_tool`
- direct public calls and discovered `call_tool` calls share the same guided-surface router failure behavior
- if a tool is not already directly visible, the intended operator path is
  `search_tools(...)` before `call_tool(...)`, not speculative name guessing
- read-only spatial graph tools such as `scene_scope_graph` and
  `scene_relation_graph`, plus the view-space artifact
  `scene_view_diagnostics`, are now directly visible on `llm-guided` as the
  default spatial-orientation support layer instead of remaining hidden
  bootstrap-only discovery targets

Current guided utility prep path:

- the direct bootstrap surface now includes the default spatial-orientation
  support tools in addition to the core guided goal/discovery entry tools
- bootstrap/planning search can now surface a small guided-safe utility set:
  - `scene_get_viewport`
  - `scene_clean_scene`
- this utility path is intended for screenshot/capture/scene-prep requests
  and should be used instead of forcing those requests through
  `router_set_goal(...)`
- the canonical public cleanup flag is `keep_lights_and_cameras`
- cleanup before `router_set_goal(...)` is still the preferred path, but
  `scene_clean_scene(...)` is now also exposed on the guided build surface as a
  bounded recovery hatch when stale scene state is discovered later
- guided `call_tool(...)` now also tolerates the older
  `keep_lights` / `keep_cameras` split form only when both values are provided
  and agree; mixed split values are rejected with a deterministic contract error
- guided `call_tool(...)` preserves the same failure semantics as a direct tool
  call; proxied validation/runtime errors still surface as tool failures
  instead of being flattened into apparent success text
- the canonical guided `call_tool(...)` wrapper is `name=...` plus
  `arguments=...`; legacy `tool=...` / `params=...` aliases are compatibility-
  only
- the same contract hardening now also applies on directly visible guided tools
  instead of only through the proxy path:
  - direct `scene_clean_scene(...)` accepts legacy split cleanup flags only in
    the same narrow compatible form
  - direct `reference_images(...)` attach catches batch-like `images=[...]` /
    `source_paths=[...]` drift with actionable guidance
  - direct `collection_manage(...)` keeps `collection_name` canonical while
    tolerating the narrow legacy `name` alias
  - direct `modeling_create_primitive(...)` rejects `scale`, `segments`,
    `rings`, `subdivisions`, and primitive-time `collection_name` shortcuts
    with actionable guidance instead of raw FastMCP schema noise

Goal-scoped reference intake is now part of the guided entry layer:

- `reference_images(action="attach", source_path=...)`
- `reference_images(action="list")`
- `reference_images(action="remove", reference_id=...)`
- `reference_images(action="clear")`
- attach is one-reference-per-call on the guided public surface; do not send
  `images=[...]` or `source_paths=[...]` batch shapes

For staged/manual reference-guided work, the guided build/inspect surface now
also exposes a bounded checkpoint comparison tool:

- `reference_compare_checkpoint(checkpoint_path=..., target_object=..., target_view=...)`
- `reference_compare_current_view(target_object=..., target_view=..., camera_name=... or USER_PERSPECTIVE)`
- `reference_compare_stage_checkpoint(target_object=..., preset_profile="compact" or "rich")`
- `reference_iterate_stage_checkpoint(target_object=..., checkpoint_label=...)`

For assembled multi-part targets, the stage/iterate surfaces can now also use:

- `target_objects=[...]`
- `collection_name="..."`
- or no target scope at all for a full-scene/full-silhouette compare

Reference intake can now also stage pending attachments before the active goal
exists or while the goal is still blocked on `needs_input`. In those cases, the
next ready/no-match `router_set_goal(...)` adopts those references onto the
active guided goal automatically instead of forcing the model to reattach them.
If the same blocked goal already has active refs, staged refs stay in separate
pending storage until adoption returns the session to ready/no-match. The
public `list` / `remove` / `clear` path now exposes one combined visible set
without copying active records into pending storage or orphaning active
`stored_path` metadata during cleanup.
The same visible-set contract now also stays consistent on ready sessions that
still carry explicit pending refs for another goal: if those refs are visible,
`remove` / `clear` update pending state as well instead of deleting only the
files behind those pending records.

## Session-Adaptive Visibility Baseline

The `llm-guided` surface now has a first complete guided-mode visibility baseline:

- canonical coarse phases: `bootstrap`, `planning`, `build`, `inspect_validate`
- guided entry surface at bootstrap/planning centered on `router_*` and `workflow_catalog`
- guided utility prep path at bootstrap/planning for screenshot/capture/scene cleanup
- deterministic phase/profile visibility rules owned by FastMCP platform code, not by router metadata
- native FastMCP session visibility application via `enable_components`, `disable_components`, and `reset_visibility`
- operator-facing visibility diagnostics exposed through `router_get_status()`
- `build_visibility_rules(...)` plus session state are now the single runtime
  visibility authority on `llm-guided`
- capability tags and `capability_manifest` remain coarse metadata for
  discovery, inventory, provider wiring, pinned defaults, and metadata-only
  phase hints; they are no longer treated as a second hidden runtime gate
- guided visibility diagnostics now derive capability visibility from the same
  runtime-visible tool membership that shapes the actual surface
- the same runtime-visible tool membership now drives capability diagnostics
  instead of inferring runtime state from manifest/tag overlap alone

This visibility baseline is complete for guided-mode surface shaping.
Search-first default rollout remains a separate TASK-084 concern.

## Structured Elicitation Baseline

Missing-input handling is now a first-class interaction layer:

- `router_set_goal` now keeps normal workflow parameter clarification model-facing by default on `llm-guided`
- non-elicitation / tool-only clients receive a typed `needs_input` fallback payload
- fallback payloads carry stable `question_set_id`, field ids, and optional `request_id`
- session state persists pending clarification identity, partial answers, and last elicitation action
- `workflow_catalog` import conflicts reuse the same typed clarification payload shape for compatibility mode

## Structured Contract Baseline

The structured-contract layer now covers the high-value state-heavy MCP surfaces:

- `macro_cutout_recess`
- `macro_finish_form`
- `macro_attach_part_to_surface`
- `macro_align_part_with_contact`
- `macro_place_symmetry_pair`
- `macro_place_supported_pair`
- `macro_cleanup_part_intersections`
- `macro_adjust_relative_proportion`
- `macro_adjust_segment_chain_arc`
- `macro_relative_layout`
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

## Guided Handoff Contract

On `llm-guided`, `router_set_goal()` now exposes explicit typed continuation metadata when workflow matching is not the intended next step.

- `guided_handoff` is returned for bounded guided continuations such as `guided_manual_build` and `guided_utility`
- it names `target_phase`, `direct_tools`, `supporting_tools`, and `discovery_tools`
- creature-oriented manual-build handoffs can also expose a stable
  `recipe_id`, currently `low_poly_creature_blockout`, so session visibility
  and search shaping can narrow to the smaller creature recipe instead of the
  broad generic build surface
- `workflow_import_recommended` remains `false` on these paths unless the user explicitly asks for workflow import/create behavior
- `router_get_status()` re-exposes the active `guided_handoff` from session state for recovery/debugging

## Server-Driven Guided Flow State

On `llm-guided`, guided sequencing is no longer represented only by prose
prompting and phase-level visibility. The server now owns one explicit
`guided_flow_state` envelope.

Current machine-readable `guided_flow_state` fields:

| Field | Meaning |
|---|---|
| `flow_id` | Stable flow identifier for the current guided runtime contract |
| `domain_profile` | Current guided overlay: `generic`, `creature`, or `building` |
| `current_step` | Active guided step such as `understand_goal`, `establish_spatial_context`, `create_primary_masses`, `checkpoint_iterate`, or `inspect_validate` |
| `completed_steps` | Steps already completed in the current guided run |
| `active_target_scope` | Compact target scope identity the guided spatial checks currently apply to |
| `spatial_scope_fingerprint` | Deterministic fingerprint for the active guided target scope |
| `spatial_state_version` | Monotonic version for scene-changing guided mutations that can stale spatial facts |
| `spatial_state_stale` | Whether the last trusted spatial facts are stale relative to the current scene version |
| `last_spatial_check_version` | The scene spatial version last validated by the required spatial checks |
| `spatial_refresh_required` | Whether the server has explicitly re-armed the spatial gate for the current step |
| `required_checks` | Structured checks that must complete before the next family unlocks |
| `next_actions` | Next machine-readable move(s) the client/model should take |
| `blocked_families` | Bounded tool-family restrictions still active for the current step |
| `required_prompts` | Required prompt bundle names for the current flow/domain/step |
| `preferred_prompts` | Strongly preferred prompt bundle names for the current flow/domain/step |
| `allowed_roles` | Role names currently expected or permitted for the active step |
| `completed_roles` | Roles already registered/completed in the current guided session summary |
| `missing_roles` | Roles still missing for the active step summary |
| `required_role_groups` | Coarse role-group milestones the current step is trying to complete |
| `step_status` | Coarse status such as `ready`, `blocked`, or `needs_validation` |

Current guided-flow behavior:

- `router_set_goal()`, `router_get_status()`,
  `guided_register_part()`,
  `reference_compare_stage_checkpoint()`, and
  `reference_iterate_stage_checkpoint()` can expose `guided_flow_state`
- domain overlays are deterministic and currently include:
  - `generic`
  - `creature`
  - `building`
- step-gated visibility now consults `guided_flow_state.current_step`, not
  only coarse `SessionPhase`
- during `establish_spatial_context`, the visible guided build surface stays
  bounded to spatial-context / inspection / reference-support tools until the
  required checks complete
- `scene_scope_graph(...)` now binds the active guided target scope.
- `scene_scope_graph(...) now binds the active guided target scope`.
- `scene_scope_graph(...)` now binds the active guided target scope for the
  spatial gate; later `scene_relation_graph(...)` /
  `scene_view_diagnostics(...)` completions must match that scope instead of
  satisfying the gate on arbitrary unrelated objects
- the spatial tools do not treat “no scope” as “whole scene”; use
  `target_object`, `target_objects`, or `collection_name`
- during an active spatial gate / spatial-refresh re-arm, this explicit-scope
  rule now applies consistently to:
  - `scene_scope_graph(...)`
  - `scene_relation_graph(...)`
  - `scene_view_diagnostics(...)`
- default placeholder scopes such as a stock `Cube` or the generic root
  `Collection` no longer count as meaningful guided target/workset bindings by
  themselves
- but for the earlier “is this scene already non-empty?” bootstrap decision,
  ordinary mesh objects with default primitive names such as `Cube` or
  `Sphere` still count as an existing rough blockout instead of forcing an
  empty-scene primary-workset jump
- the special-case empty-scene bootstrap still treats Blender's stock startup
  scene as empty when the only non-helper mesh is one default placeholder
  primitive such as `Cube`; multiple placeholder meshes still count as a real
  rough blockout worth inspecting
- helper-only scopes such as a single `Camera` do not initialize or satisfy a
  creature/building spatial gate by themselves
- when the scene has no meaningful target/workset objects yet, the guided flow
  can enter `bootstrap_primary_workset` and expose primary-mass creation before
  requiring target-bound spatial checks
- if guided references are already attached, they should be treated as the
  primary grounding input for the first blockout masses and placement
- full semantic object names such as `ForeLeg_L`, `ForeLeg_R`, `HindLeg_L`,
  and `HindLeg_R` are preferred over abbreviations like `ForeL` / `HindR`
  because seam/role heuristics classify them more reliably
- the guided runtime now has one explicit naming-policy layer for role-sensitive registration/build paths:
  - weak abbreviations can warn on weak role-sensitive names with suggested semantic names
  - clearly opaque placeholder names such as `Sphere` / `Object` can be
    blocked until the object uses a semantic role-shaped name
- after material scene changes such as `scene_clean_scene(...)`,
  `scene_rename_object(...)`, `modeling_create_primitive(...)`,
  `modeling_transform_object(...)`, `modeling_join_objects(...)`,
  `modeling_separate_object(...)`, or bounded attachment/alignment cleanup
  macros, the runtime can mark the spatial layer stale and re-arm the
  required checks
- support/symmetry-aware relation pairs now preserve support and symmetry
  annotations even when they share the same `(from_object, to_object)` key as a
  generic primary-target pair, so downstream planners still see
  support/symmetry semantics instead of only a generic edge
- healthy support/symmetry pairs no longer count as failing just because their
  centers differ or they are not literal contact pairs; only `unsupported` /
  `asymmetric` support/symmetry verdicts count as failures there
- when `spatial_refresh_required=true`, the server expects a fresh
  `scene_scope_graph(...)` rebind first, then the remaining required spatial
  checks on that same target scope
- `scene_view_diagnostics(...)` only satisfies that guided spatial gate when it
  returns real available view-space evidence; a headless/unavailable probe
  remains read-only and does not complete the check by itself
- if a read-only spatial check uses a different scope while refresh is active,
  it can still return its payload, but the response message says it did not
  satisfy the active guided scope and shows the expected rerun scope
- the machine-readable next action for this path is
  `refresh_spatial_context`
- on the guided inspect surface, bounded attachment repair macros and spatial
  re-check tools remain aligned with the inspect family policy instead of
  advertising one surface through `allowed_families` and another through tool
  visibility
- guided execution policy can now fail closed when a call resolves to the
  wrong shared family or an explicit guided role that is not allowed for the
  current step
- for role-sensitive build families, `modeling_create_primitive(...)` and
  `modeling_transform_object(...)` now require either:
  - an explicit `guided_role=...`
  - or a previously registered role in the session part registry
- `required_prompts` and `preferred_prompts` are stable prompt asset names;
  they support the server-driven flow instead of replacing it with prompt-only
  policy
- role/family summaries are intentionally compact public fields; the full
  internal part registry remains session-scoped implementation state
- role summaries now include compact cardinality diagnostics:
  - `role_counts`
  - `role_cardinality`
  - `role_objects`
  so pair roles such as `ear_pair`, `foreleg_pair`, and `hindleg_pair` remain
  available until both left/right sibling objects are registered
- `guided_register_part(object_name=..., role=...)` is the canonical guided
  surface for telling the server that an existing object now counts as one
  semantic role such as `body_core`, `head_mass`, or `roof_mass`
- `guided_register_part(...)` now validates that the named Blender object
  actually exists before updating guided role completion; a typo does not
  populate `completed_roles`
- if guided object validation cannot read the Blender scene at all,
  `guided_register_part(...)` now fails clearly instead of mutating guided
  session state from an unverified object name
- explicit target names passed into `scene_scope_graph(...)` / scope-building
  paths now follow the same Blender-truth validation rule before the guided
  scope can bind
- `modeling_create_primitive(...)` and `modeling_transform_object(...)` may
  also carry an optional `guided_role` convenience hint on guided surfaces, but
  `guided_register_part(...)` remains the canonical explicit registration path
- those `guided_role=...` convenience hints only auto-register when the
  session already has an active `guided_flow_state`; outside an active guided
  flow they do not create persistent guided role state on their own
- a failed create call now stays non-mutating for guided role state as well:
  if `modeling_create_primitive(...)` returns a failure string, the requested
  role is not auto-registered just because a semantic `name` was supplied
- on `modeling_create_primitive(...)`, the convenience path now also requires
  an explicit semantic `name`; guided create does not allow auto-generated
  Blender names to become semantic part registrations
- if the router prepends corrective steps such as `scene_set_mode(...)`, the
  guided-role convenience path still registers against the final successful
  modeling step instead of dropping the role hint just because the call became
  multi-step
- guided-role convenience registration now also handles valid object names
  containing apostrophes, such as `King's Crown`, instead of truncating the
  stored object name
- canonical pair names such as `ForeLeg_L`, `ForeLeg_R`, and `ForeLegPair`
  now count as strong semantic names for pair roles instead of warning or
  blocking under the stricter naming policy
- for `modeling_create_primitive(...)`, the convenience path registers the
  real created object name returned by Blender/tool execution, not the raw
  requested primitive token, so role state remains correct for names such as
  `Cube.001` or Blender defaults such as `Suzanne`
- successful `scene_rename_object(...)` calls now keep the guided part
  registry aligned with the renamed object so later role-sensitive calls can
  still recover the stored role/role_group
- successful `scene_rename_object(...)` calls also mark guided spatial state
  stale so the name-bound target scope can be rebound on the next required
  spatial refresh
- failed plain-string mutation results such as `Object 'Missing' not found`
  now stay non-mutating for guided session state; they do not re-arm spatial
  checks or rewrite guided role registration just because the wrapper returned
  a string payload
- `scene_clean_scene(...)` now clears the guided part registry and returns the
  guided flow to `bootstrap_primary_workset`, so empty-scene resets do not
  keep stale completed parts from an earlier workset
- starting a different guided goal in the same session now resets guided part
  registration for that new flow instead of carrying completed roles forward
  from the previous object
- destructive identity/topology changes such as `modeling_join_objects(...)`
  and `modeling_separate_object(...)` now remove stale guided part
  registrations; re-register the resulting object(s) explicitly when they
  should still count toward guided role completion
- those same destructive topology changes also re-arm guided spatial checks,
  because previously captured scope/view facts are no longer trustworthy after
  objects were merged away or split apart
- for macro capture/vision artifacts, `macro_attach_part_to_surface(...)` now
  refreshes its post-action capture bundle after the extra mesh-surface nudge,
  so attached images and truth summary describe the final seated pose instead
  of the pre-nudge intermediate pose
- if the optional segmentation sidecar is enabled on runtime config but not yet
  executed on the current compare path, staged compare/iterate responses now
  report `part_segmentation.status="unavailable"` instead of silently staying
  `disabled`
- after newly created blockout parts during `checkpoint_iterate`, bounded
  initial transforms can remain available before the next checkpoint instead
  of immediately forcing a spatial refresh on every small adjustment
- if guided naming returns warnings or blocks, replace the weak name with one of the suggested semantic names instead of retrying the same placeholder or opaque abbreviation unchanged
- guided naming and guided spatial role inference now use token-boundary style
  matches instead of raw substring hits, so names such as `Heart` or
  `TruthBodyAnchorHead` do not become accidental semantic ear/body/head roles
- stage compare/iterate may now keep the session in bounded build continuation
  when the current guided role/workset slice is still incomplete, instead of
  escalating too early into `inspect_validate`
- later guided steps may still keep missing primary masses available when those
  masses are part of the same bounded workset and are not yet complete
- exact tool-name searches on the shaped guided surface now return a tighter,
  smaller result shape to reduce noisy discovery dumps during the active build
  loop
- for overlays that use primary-mass role groups, registering the required
  primary roles can now move the flow from `create_primary_masses` into
  `place_secondary_parts`
- overlays that use secondary-part role groups can likewise move from
  `place_secondary_parts` into `checkpoint_iterate` when the required
  secondary roles are complete
- later guided steps may still keep earlier corrective build families
  available for already-created masses, so the runtime can support bounded
  in-place refinement without reopening the entire generic build surface
- `collection_manage(...)` remain utility-family actions and should not be blocked just because the moved object was registered under an earlier semantic role
- collection_manage(...) remain utility-family actions for guided workset housekeeping.

## Guided Flow Troubleshooting

If a needed tool is not visible or a build tool seems to have disappeared on
`llm-guided`, diagnose the session in this order:

1. Call `router_get_status()` and inspect `guided_flow_state`.
2. If `guided_flow_state` is `null`, the session is not on an active guided
   flow yet. Set or re-set the goal first.
3. Check `domain_profile`:
   - `generic` = fallback build/object flow
   - `creature` = creature/manual blockout overlay
   - `building` = building/facade/structural overlay
4. Check `current_step`, `required_checks`, and `next_actions`.
5. If `step_status == "blocked"`, complete the required step instead of
   guessing hidden tool names.
6. If `spatial_refresh_required == true`, treat that as an explicit stale
   spatial-state re-arm:
   - call `scene_scope_graph(...)` first to bind/rebind the active target
     scope
   - then rerun the remaining `required_checks` on that same scope
7. If `scene_view_diagnostics(target_object="Camera", ...)` or another
   unrelated helper scope appears to “work” but the flow did not advance, that
   is expected. Read-only payloads can still succeed even when they do not
   satisfy the active guided spatial gate.
8. If a family is hidden/blocked-by-flow, do not treat `call_tool(...)` as a
   bypass. Follow the flow gate, then re-check visibility/search.
9. If an explicit goal is active but the router stayed on the manual/no-match
   path, a strong pattern-suggested workflow may still expand; what stays
   suppressed there is the lower-confidence heuristic reopening path.
10. If the server rejects a call with a guided family/role error, do not retry
   the same action under a different hidden/internal tool name; inspect the
   current `allowed_families` and `allowed_roles` first.
11. For creature blockout naming, prefer full semantic names such as
    `ForeLeg_L` / `HindLeg_R`; abbreviations like `ForeL` / `HindR` can weaken
   seam inference unless the heuristic layer explicitly supports them.

## Guided Reference Readiness Contract

On `llm-guided`, staged reference work now has one explicit readiness payload
instead of hidden sequencing assumptions.

- `router_set_goal()`, `router_get_status()`,
  `reference_compare_stage_checkpoint()`, and
  `reference_iterate_stage_checkpoint()` expose `guided_reference_readiness`
- the payload reports:
  - `attached_reference_count`
  - `pending_reference_count`
  - `compare_ready`
  - `iterate_ready`
  - machine-readable `blocking_reason`
  - machine-readable `next_action`
- `pending_reference_count` reflects pending refs still relevant to the active
  guided goal/session; stale pending refs for another goal do not block a ready
  staged compare/iterate path by themselves
- staged compare/iterate now fail fast when the readiness payload is blocked
- `loop_disposition="inspect_validate"` is a stop-and-check branch:
  pause free-form modeling and switch to inspect/measure/assert immediately
- if staged compare degrades but deterministic truth findings remain strong,
  the same inspect/measure/assert handoff stays authoritative instead of
  dropping the run back into ad hoc free-form modeling
- `goal_override` is not a substitute for an active staged guided session on
  `reference_compare_stage_checkpoint()` / `reference_iterate_stage_checkpoint()`;
  use lower-level checkpoint/current-view compare only when you intentionally
  need request-local comparison outside the staged session flow

## Session Diagnostics

Guided/runtime payloads now expose explicit MCP session diagnostics:

- `router_set_goal()`
  - `session_id`
  - `transport`
- `router_get_status()`
  - `session_id`
  - `transport`
- `reference_compare_stage_checkpoint()`
  - `session_id`
  - `transport`
- `reference_iterate_stage_checkpoint()`
  - `session_id`
  - `transport`

Use those fields first when diagnosing whether state loss came from a new MCP
session/transport lifecycle instead of Blender-scene changes.

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
- native prompt asset names now include `reference_guided_creature_build`
- `recommended_prompts` now uses phase/profile plus explicit session goal and
  guided-handoff context to steer creature sessions toward the creature prompt path

## Deterministic Silhouette Guidance

Stage compare/iterate responses now expose one deterministic perception layer
alongside the existing vision/truth outputs:

- `silhouette_analysis`
  - typed silhouette metrics such as IoU, contour drift, aspect-ratio delta,
    band-width deltas, and side-profile projection deltas
- `action_hints`
  - typed corrective tool suggestions derived from those metrics
- `part_segmentation`
  - a vendor-neutral, advisory-only sidecar payload that defaults to
    `status="disabled"` on the normal guided runtime

Consumption order:

- `correction_candidates` and `truth_followup` stay ahead of perception hints
- `action_hints` complement `correction_focus`; they do not replace truth or router policy
- `vision_contract_profile` remains prompt/schema/parser routing only and is
  not itself evidence, truth, or policy

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

Current transport selection is explicit:

- `MCP_TRANSPORT_MODE=stdio`
- `MCP_TRANSPORT_MODE=streamable`

For `streamable`, the current supported knobs are:

- `MCP_HTTP_HOST`
- `MCP_HTTP_PORT`
- `MCP_STREAMABLE_HTTP_PATH`

Example Streamable HTTP Docker run:

```bash
docker run --rm \
  -p 8000:8000 \
  -e MCP_TRANSPORT_MODE=streamable \
  -e MCP_HTTP_HOST=0.0.0.0 \
  -e MCP_HTTP_PORT=8000 \
  -e MCP_STREAMABLE_HTTP_PATH=/mcp \
  -e BLENDER_RPC_HOST=host.docker.internal \
  blender-ai-mcp
```

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
| `reference_compare_checkpoint` | `checkpoint_path` (str), `checkpoint_label` (str, optional), `target_object` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional) | Compares one current checkpoint image against the active goal plus attached reference images and returns bounded vision interpretation for the next correction step. |
| `reference_compare_current_view` | `checkpoint_label` (str, optional), `target_object` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), viewport/camera args | Captures one current viewport/camera checkpoint using the bounded `scene_get_viewport` semantics, then compares it against the active goal plus attached reference images. |
| `reference_compare_stage_checkpoint` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `checkpoint_label` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), `preset_profile` (`compact`/`rich`) | Captures one deterministic multi-view stage checkpoint for a target object, object set, collection, or full assembled scene, then compares that view-set against the active goal plus attached reference images. Fails fast when `guided_reference_readiness.compare_ready` is false. |
| `reference_iterate_stage_checkpoint` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `checkpoint_label` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), `preset_profile` (`compact`/`rich`) | Runs one session-aware checkpoint iteration: capture deterministic stage views, compare them to the references, remember the previous correction focus, and return whether to continue building, inspect/validate, or stop. Fails fast when `guided_reference_readiness.iterate_ready` is false. |
Invalid target-scope inputs such as an unavailable `collection_name` now return
structured error payloads on the stage-compare path instead of failing again
while building the error response.
Stage compare/iterate responses now also expose `guided_reference_readiness`, `assembled_target_scope`, `truth_bundle`, `truth_followup`, `correction_candidates`, `budget_control`, `refinement_route`, `refinement_handoff`, `silhouette_analysis`, `action_hints`, and `part_segmentation`, so assembled-model correction flows can consume explicit session readiness, a structured target scope, correction-oriented truth findings, loop-ready follow-up items, an explicitly ranked merged correction list, explicit trimming metadata, a deterministic refinement-family decision, typed perception metrics/tool hints, and an optional advisory-only sidecar placeholder instead of inferring everything from loose `target_object` / `target_objects` / `collection_name` fields. On `reference_iterate_stage_checkpoint(...)`, the loop-facing `correction_focus` now prefers ranked `correction_candidates` summaries when they are present, and high-priority deterministic truth findings can also move `loop_disposition` to `inspect_validate` instead of waiting only for repeated vision focus. `action_hints` complement that loop by exposing deterministic silhouette-driven tool suggestions, while `part_segmentation` stays disabled unless an operator explicitly enables the separate sidecar path. Collection/object-set targeting now also avoids obviously accessory-first primary anchors when a more structural target is present, expands supported creature scopes into deterministic `required_creature_seams`, keeps multiple failing required seams live together in `truth_followup` / `correction_candidates`, normalizes vision-side `recommended_checks` to canonical MCP tool ids or drops them, applies model-aware budget control when the active runtime profile is too small for the full payload, and exposes `refinement_route` for bounded family choices such as `macro`, `modeling_mesh`, `sculpt_region`, or `inspect_only`. At this stage sculpt stays hidden on the normal guided surface; `refinement_handoff` is recommendation-only.
Compact stage compare/iterate responses keep `capture_count`, `preset_names`,
truth, and correction summaries, but omit the full capture list to reduce
normal guided response size. Rich/debug capture detail remains available through
the richer profile path. During active assembled-workset checkpointing, the
requested `target_object` / `target_objects` / `collection_name` must still
cover the active guided workset; narrowing to a single safe object returns an
actionable scope error instead of advancing the loop.
Compact iterate responses also slim the nested `compare_result` debug payload:
top-level iterate fields keep the actionable truth, candidate, hint, and route
summaries, while duplicated nested `truth_bundle`, `truth_followup`, full
candidate evidence, full silhouette metrics, and action hints are omitted from
`compare_result`. Use the rich/debug path when a maintainer needs the full
nested compare payload.

The full scope/relation graphs stay separate from those default stage payloads.
When a guided step needs richer spatial state instead of just the current
checkpoint handoff, call the explicit read-only artifacts:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_view_diagnostics(...)`

`reference_compare_current_view(...)` may also emit compact
`view_diagnostics_hints` when the current framing or occlusion state makes the
captured checkpoint a weak basis for the next correction step. That hint is
recommendation-only and does not embed a heavyweight view graph into the
default compare payload.

For the guided creature path specifically, pair truth now carries one explicit
attachment verdict for each required seam:

- `seated_contact`
- `floating_gap`
- `intersecting`
- `misaligned_attachment`
| `scene_camera_orbit` | `angle_horizontal` (float), `angle_vertical` (float), `target_object` (str, optional), `target_point` ([x,y,z], optional) | Orbits the viewport around a target object or point. |
| `scene_camera_focus` | `object_name` (str), `zoom_factor` (float) | Focuses the viewport on one object. Use `object_name` here, not `target`, `target_object`, or `focus_target`. |
| `scene_get_viewport` | `width` (int), `height` (int), `shading` (str), `camera_name` (str), `focus_target` (str), `view_name` (str, optional), `orbit_horizontal` (float, optional), `orbit_vertical` (float, optional), `zoom_factor` (float, optional), `persist_view` (bool, optional), `output_mode` (str) | Returns a rendered image. `shading`: WIREFRAME/SOLID/MATERIAL. `camera_name`: specific cam or "USER_PERSPECTIVE". `USER_PERSPECTIVE` follows the live active 3D viewport; named cameras follow render visibility. `view_name`/`orbit_*`/`zoom_factor`/`persist_view` apply only to bounded `USER_PERSPECTIVE` capture adjustments. `focus_target`: object to frame. `output_mode`: IMAGE (default Image resource), BASE64 (raw string), FILE (host-visible path), MARKDOWN (inline preview + path). |
| `scene_hide_object` | `object_name` (str), `hide` (bool), `hide_render` (bool) | Hides an object in the viewport. If hiding with `hide_render=True`, it is also hidden from named-camera/render capture. Showing the object restores render visibility as well. |
| `scene_show_all_objects` | `include_render` (bool) | Restores viewport visibility for all objects. If `include_render=True`, also restores render visibility for objects hidden from named-camera/render capture. |
| `scene_isolate_object` | `object_name` (str or array) | Keeps only the named object(s) visible and hides all others in both viewport and render, so named-camera capture matches the isolated set. |
| `scene_get_custom_properties` | `object_name` (str) | Gets custom properties (metadata) from an object. Returns object_name, property_count, and properties dict. |
| `scene_set_custom_property` | `object_name` (str), `property_name` (str), `property_value` (str/int/float/bool), `delete` (bool) | Sets or deletes a custom property on an object. |
| `scene_get_hierarchy` | `object_name` (str, optional), `include_transforms` (bool) | Gets parent-child hierarchy for specific object or full scene tree. |
| `scene_get_bounding_box` | `object_name` (str), `world_space` (bool) | Gets bounding box corners, min/max, center, dimensions, and volume. |
| `scene_get_origin_info` | `object_name` (str) | Gets origin (pivot point) information relative to geometry and bounding box. |
| `scene_scope_graph` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional) | Returns one compact read-only structural scope artifact for a target object/object set/collection, including the inferred anchor plus bounded object-role hints. Intended for on-demand guided spatial reasoning rather than bootstrap exposure. |
| `scene_relation_graph` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `goal_hint` (str, optional) | Returns one compact read-only pair-relation graph derived from current gap/alignment/overlap/contact truth, including bounded attachment/support/symmetry interpretations where justified. Intended for on-demand guided spatial reasoning rather than bootstrap exposure. |
| `scene_view_diagnostics` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `camera_name` (str, optional), `focus_target` (str, optional), `view_name` (str, optional), `orbit_horizontal` (float, optional), `orbit_vertical` (float, optional), `zoom_factor` (float, optional), `persist_view` (bool, optional) | Returns one compact read-only view-space diagnostics artifact with projected extent, frame coverage, centering, and visible/partial/occluded/off-frame verdicts for a named camera or the live `USER_PERSPECTIVE` path. This is view-space only and does not replace truth-space measure/assert semantics. |
| `scene_measure_distance` | `from_object` (str), `to_object` (str), `reference` (str) | Measures origin-to-origin or bbox-center distance between two objects. |
| `scene_measure_dimensions` | `object_name` (str), `world_space` (bool) | Measures object dimensions and volume from its bounding box. |
| `scene_measure_gap` | `from_object` (str), `to_object` (str), `tolerance` (float) | Measures nearest gap/contact state between two objects. For mesh pairs it now prefers a mesh-surface path and exposes `measurement_basis` plus bbox fallback diagnostics. |
| `scene_measure_alignment` | `from_object` (str), `to_object` (str), `axes` (array), `reference` (str), `tolerance` (float) | Measures bbox alignment deltas on chosen axes using CENTER/MIN/MAX references. |
| `scene_measure_overlap` | `from_object` (str), `to_object` (str), `tolerance` (float) | Measures overlap/touching state between two objects. For mesh pairs it now prefers mesh-surface overlap/contact semantics and reports bbox fallback diagnostics separately. |
| `scene_assert_contact` | `from_object` (str), `to_object` (str), `max_gap` (float), `allow_overlap` (bool) | Asserts pass/fail contact relation from the current truth path. For mesh pairs this now prefers mesh-surface contact semantics instead of bbox-touching alone. |

For contact-sensitive truth on curved or rounded objects, the product now distinguishes:

- mesh-surface contact/gap semantics when a bounded mesh-aware path is available
- bbox fallback semantics when a mesh-aware path is not available

This means a pair can still have `bbox_relation="contact"` while the main
`relation` reports `separated` if the actual mesh surfaces remain visibly
gapped.

When the mesh-aware path detects a true overlap, that main `relation` remains
`overlapping`, so `scene_assert_contact(..., allow_overlap=false)` still rejects
the pair even if the bbox-level view would otherwise look like simple contact.
That also applies to thin/planar mesh cases where BVH overlap exists but bbox
overlap volume alone would be an unreliable gate.

Macro verification and hybrid truth-followup payloads now also surface that
split in their operator-facing summaries, so bbox-touching but still visibly gapped
pairs are called out explicitly instead of being flattened into a generic
contact success/failure phrase.
| `scene_assert_dimensions` | `object_name` (str), `expected_dimensions` (array), `tolerance` (float), `world_space` (bool) | Asserts pass/fail dimensions against an expected vector within tolerance. |
| `scene_assert_containment` | `inner_object` (str), `outer_object` (str), `min_clearance` (float), `tolerance` (float) | Asserts pass/fail containment plus measured clearance/protrusion details. |
| `scene_assert_symmetry` | `left_object` (str), `right_object` (str), `axis` (str), `mirror_coordinate` (float), `tolerance` (float) | Asserts mirrored symmetry between two objects across a chosen axis. |
| `scene_assert_proportion` | `object_name` (str), `axis_a` (str), `expected_ratio` (float), `axis_b` (str), `reference_object` (str), `reference_axis` (str), `tolerance` (float), `world_space` (bool) | Asserts pass/fail ratio/proportion against the expected value. |
| `reference_compare_checkpoint` | `checkpoint_path` (str), `checkpoint_label` (str, optional), `target_object` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional) | Compares one current checkpoint image against the active goal plus attached reference images and returns bounded vision interpretation for the next correction step. |
| `reference_compare_current_view` | `checkpoint_label` (str, optional), `target_object` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), viewport/camera args | Captures one current viewport/camera checkpoint using the bounded `scene_get_viewport` semantics, then compares it against the active goal plus attached reference images. |
| `reference_compare_stage_checkpoint` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `checkpoint_label` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), `preset_profile` (`compact`/`rich`) | Captures one deterministic multi-view stage checkpoint for a target object, object set, collection, or full assembled scene, then compares that view-set against the active goal plus attached reference images. |
| `reference_iterate_stage_checkpoint` | `target_object` (str, optional), `target_objects` (array, optional), `collection_name` (str, optional), `checkpoint_label` (str, optional), `target_view` (str, optional), `goal_override` (str, optional), `prompt_hint` (str, optional), `preset_profile` (`compact`/`rich`) | Runs one session-aware checkpoint iteration: capture deterministic stage views, compare them to the references, remember the previous correction focus, and return whether to continue building, inspect/validate, or stop. |
> **Note:** Tools like `scene_get_mode`, `scene_list_selection`, `scene_inspect_*`, and `scene_create_*` have been consolidated into grouped public tools. Use `scene_context`, `scene_inspect`, and `scene_create` instead.
> `scene_get_constraints` is now internal to `scene_inspect(action="constraints")` for MCP clients.

### Collection Tools
Organizational tools for managing Blender collections.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `collection_list` | `include_objects` (bool) | Lists all collections with hierarchy, object counts, and visibility flags. |
| `collection_list_objects` | `collection_name` (str), `recursive` (bool), `include_hidden` (bool) | Lists objects within a collection, optionally recursive through child collections. |
| `collection_manage` | `action` (create/delete/rename/move_object/link_object/unlink_object), `collection_name`, `new_name`, `parent_name`, `object_name` | Manages collections: create, delete, rename, and move/link/unlink objects between collections. Canonical public target name is `collection_name`; legacy `name` is compatibility-only on the guided proxy path. |

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
| `macro_finish_form` | `target_object` (str), `preset` (str), `bevel_width` (float), `bevel_segments` (int), `subsurf_levels` (int), `thickness` (float), `solidify_offset` (float) | Applies one bounded finishing stack to an object using a preset such as `rounded_housing`, `panel_finish`, `shell_thicken`, or `smooth_subdivision` instead of hand-building the modifier chain. |
| `macro_attach_part_to_surface` | `part_object` (str), `surface_object` (str), `surface_axis` (`X`/`Y`/`Z`), `surface_side` (`positive`/`negative`), `align_mode` (`none`/`center`/`min`/`max`), `gap` (float), `max_mesh_nudge` (float), `offset` ([x,y,z]) | Seats one part onto another object's surface/body using one explicit surface axis, one side, shared tangential alignment, optional gap, and one deterministic transform. Use `align_mode="none"` to preserve tangential offsets while seating along the surface normal. |
| `macro_align_part_with_contact` | `part_object` (str), `reference_object` (str), `target_relation` (`contact`/`gap`), `gap` (float), `align_mode` (`none`/`center`/`min`/`max`), `normal_axis` (`X`/`Y`/`Z`, optional), `preserve_side` (bool), `max_nudge` (float), `offset` ([x,y,z]) | Repairs an already-related pair with a bounded minimal nudge. It reads the current truth state, infers a repair axis/side when possible, preserves the current side by default, and refuses broader moves once the required nudge exceeds `max_nudge`. |
| `macro_place_symmetry_pair` | `left_object` (str), `right_object` (str), `axis` (`X`/`Y`/`Z`), `mirror_coordinate` (float), `anchor_object` (`auto`/`left`/`right`), `tolerance` (float) | Places or corrects one mirrored pair around an explicit mirror plane by preserving one anchor object and moving the follower object to the mirrored center position. |
| `macro_place_supported_pair` | `left_object` (str), `right_object` (str), `support_object` (str), `axis` (`X`/`Y`/`Z`), `mirror_coordinate` (float), `support_axis` (`X`/`Y`/`Z`), `support_side` (`positive`/`negative`), `anchor_object` (`auto`/`left`/`right`), `gap` (float), `tolerance` (float) | Places or corrects one mirrored pair against a shared support surface by combining explicit mirror placement with explicit support contact. It blocks when those constraints would require materially different support coordinates and stays outside rigging or free-form posing. |
| `macro_cleanup_part_intersections` | `part_object` (str), `reference_object` (str), `gap` (float), `normal_axis` (`X`/`Y`/`Z`, optional), `preserve_side` (bool), `max_push` (float) | Separates one overlapping pair with a bounded push toward contact or a small gap. It reads overlap truth first, infers a stable cleanup axis/side when possible, and blocks when the required push exceeds `max_push`. |
| `macro_adjust_relative_proportion` | `primary_object` (str), `reference_object` (str), `expected_ratio` (float), `primary_axis` (`X`/`Y`/`Z`), `reference_axis` (`X`/`Y`/`Z`), `scale_target` (`primary`/`reference`), `tolerance` (float), `uniform_scale` (bool), `max_scale_delta` (float) | Repairs cross-object proportion drift with a bounded scale adjustment. It reads the current ratio, scales one target object within `max_scale_delta`, and re-checks the result with `scene_assert_proportion`. |
| `macro_adjust_segment_chain_arc` | `segment_objects` (array), `rotation_axis` (`X`/`Y`/`Z`), `total_angle` (float), `direction` (`positive`/`negative`), `segment_spacing` (float, optional), `apply_rotation` (bool) | Adjusts an ordered chain of existing segment objects into a bounded planar arc by applying deterministic per-segment placement and optional progressive rotation around one explicit rotation axis. |
| `macro_relative_layout` | `moving_object` (str), `reference_object` (str), `x_mode` (str), `y_mode` (str), `z_mode` (str), `contact_axis` (str), `contact_side` (str), `gap` (float), `offset` ([x,y,z]) | Places one object relative to another with bounded bbox alignment rules, optional outside-face contact/gap placement, and one deterministic transform. |

Example guided macro flow for finishing:

1. `browse_workflows(action="search", search_query="rounded housing finish")`
2. `router_set_goal(goal="give the housing a rounded finish while keeping the overall size close to the current blockout")`
3. `search_tools(query="finish housing bevel subdivision shell")`
4. `call_tool(name="macro_finish_form", arguments={"target_object":"Housing","preset":"rounded_housing"})`
5. verify with `inspect_scene(action="object", target_object="Housing")`
6. then discover and call the right truth-layer check, for example:
   - `search_tools(query="measure dimensions assert dimensions viewport")`
   - `call_tool(name="scene_measure_dimensions", arguments={"object_name":"Housing","world_space":true})`

If `macro_finish_form` matches the user's intent, prefer it over manually chaining `modeling_add_modifier(...)` calls.
If the task is specifically "seat/attach this part onto that surface/body", prefer `macro_attach_part_to_surface` over the more general `macro_relative_layout`.
If the pair is already almost correct and only needs a small repair nudge, prefer `macro_align_part_with_contact` over a full re-placement macro.
On the guided creature path, embedded seams such as snout/head or nose/snout
prefer `macro_attach_part_to_surface`, while head/body, tail/body, and
limb/body seams prefer `macro_align_part_with_contact`.
When a rounded organic segment seam such as head/body, tail/body, or limb/body
is already intersecting, the planner should prefer `macro_attach_part_to_surface`
over a blind bbox side-push. `macro_align_part_with_contact` remains best for
small non-overlapping contact/gap nudges; using an explicit normal axis on a
rounded overlapping part can still produce bbox contact while mesh-surface
truth reports a residual gap.
If the task is specifically "place or correct this mirrored pair", prefer `macro_place_symmetry_pair` over manual mirrored transforms.
If the task is specifically "keep this mirrored pair symmetric while seating both parts on the same support", prefer `macro_place_supported_pair` over manually combining symmetry and per-part contact moves.
If the task is specifically "separate these two overlapping parts with a bounded fix", prefer `macro_cleanup_part_intersections` over ad hoc manual transform cleanup.
On required creature seams, overlap removal alone does not count as success if
the attachment verdict is still `floating_gap`, `intersecting`, or
`misaligned_attachment`.
If the main issue is cross-object size/ratio drift, prefer `macro_adjust_relative_proportion` over ad hoc scale guessing or open-ended sculpting.
If the task is to reshape an ordered segment chain into a cleaner arc, prefer `macro_adjust_segment_chain_arc` over manual per-segment transform chaining.
If the task is bounded relative placement/alignment, prefer `macro_relative_layout` over manual transform-by-transform placement.
If the task is a bounded recess/opening, prefer `macro_cutout_recess` over hand-building the cutter/boolean sequence.

Workflow clarification note:

- if `router_set_goal(...)` returns a model-facing `workflow_confirmation`
  clarification for a weak match, the model may now answer with
  `guided_manual_build` to decline that workflow and continue on the guided
  build surface instead

### Modeling Tools
Geometry creation and editing.

| Tool Name | Arguments | Description |
|-----------|-----------|-------------|
| `modeling_create_primitive` | `primitive_type` (str), `radius` (float), `size` (float), `location` ([x,y,z]), `rotation` ([x,y,z]), `name` (str, optional) | Creates a simple 3D object (Cube, Sphere, Cylinder, Plane, Cone, Torus, Monkey). Use `radius` for sphere/cylinder/cone, `size` for coarse primitive size, then `modeling_transform_object(scale=...)` for non-uniform scale. Collection placement happens after creation via `collection_manage(...)`, not via a `collection_name` primitive argument. |
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
| `router_set_goal` | `goal` (str), `resolved_params` (dict, optional) | Sets the active build goal for the router session. Returns status (ready/needs_input/no_match/disabled/error), matched workflow info, resolved params with sources, any unresolved inputs for follow-up calls, explicit `guided_handoff` metadata when the intended path is guided manual build/utility continuation instead of workflow execution, machine-readable `guided_flow_state` for the current guided step/domain/required checks, and `guided_reference_readiness` for staged reference work. |
| `router_get_status` | *none* | Returns current router session state, visibility diagnostics, pending clarification info, active `guided_handoff` when present, `guided_flow_state`, `guided_reference_readiness`, and router/component stats. |
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
