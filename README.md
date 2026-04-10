# blender-ai-mcp

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://github.com/PatrykIti/blender-ai-mcp/pkgs/container/blender-ai-mcp)
[![CI Status](https://github.com/PatrykIti/blender-ai-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/PatrykIti/blender-ai-mcp/actions)
[![GitHub Stars](https://img.shields.io/github/stars/PatrykIti/blender-ai-mcp?style=social)](https://github.com/PatrykIti/blender-ai-mcp/stargazers)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/PatrykIti?style=social)](https://github.com/sponsors/PatrykIti)

**A production-shaped MCP server for Blender.**

`blender-ai-mcp` lets Claude, ChatGPT, Codex, and other MCP clients control Blender through a stable tool API instead of ad-hoc Python generation. The result is a safer, smaller, and more reliable surface for real modeling work: goal-first routing, curated public tools, deterministic inspection, and verification that does not depend on guesswork.

<a href="https://youtu.be/BaJj8gAtttw">
  <img src="https://img.youtube.com/vi/BaJj8gAtttw/hqdefault.jpg" alt="Watch demo video on YouTube" style="max-width: 100%;">
</a>

## Why This Exists

Most "AI + Blender" setups still ask the model to write raw `bpy` scripts. That breaks exactly where production work gets interesting:

1. Blender APIs drift across versions.
2. Context-sensitive operators fail when the active object, mode, or selection is wrong.
3. Raw scripts give weak feedback when something goes wrong.
4. Vision can describe a result, but it cannot be trusted as the final authority.

`blender-ai-mcp` takes the opposite approach: treat Blender control as a product surface, not a code-generation stunt.

## Why This MCP Server Instead of Raw Python

- **Stable contracts over script synthesis.** The model calls tools with validated parameters instead of improvising Blender code.
- **Goal-first orchestration.** Normal guided sessions start from `router_set_goal(...)`, so the system knows what the model is trying to build before it starts calling low-level actions.
- **Small public surface.** The default `llm-guided` profile exposes a tiny, search-first bootstrap layer instead of flooding the model with the whole runtime inventory.
- **Truth-first verification.** Inspection, measurement, and assertion tools determine what is actually true in Blender.
- **Safe execution boundaries.** The Blender addon executes operations on Blender's main thread while the MCP server handles routing, validation, discovery, and structured responses.

## The Product Approach

The business idea formalized in `TASK-113` is simple:

- **Atomic tools** are the implementation substrate. They stay small, precise, and mostly hidden from the normal public surface.
- **Macro tools** are the preferred LLM-facing layer for meaningful task-sized work.
- **Workflow tools** are bounded multi-step process tools with explicit reporting, not open-ended "do anything" endpoints.
- **Goal-first orchestration** keeps sessions anchored to an active intent instead of making the model rediscover context on every turn.
- **Vision assists interpretation**, while deterministic measurement and assertions provide the final truth layer.
- **Pluggable vision runtimes** now cover local MLX plus external OpenRouter and Google AI Studio / Gemini provider paths, with model-family-specific external contract profiles for prompt/schema/parser behavior.

This is what turns the project from "Blender tools exposed over MCP" into a usable AI control product for modeling pipelines.

## LLM-Guided Public Surface

`llm-guided` is the default production-oriented surface. It is intentionally small, search-first, and designed around goal-aware sessions.

Normal guided flow:

1. `router_set_goal(...)`
2. `browse_workflows`, `search_tools`, or `call_tool`
3. use grouped/public tools such as `check_scene`, `inspect_scene`, or `configure_scene`
4. verify with inspection plus `scene_measure_*` and `scene_assert_*`

Prompting rule:

- use the prompt-library assets in [_docs/_PROMPTS/README.md](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/_docs/_PROMPTS/README.md) as the canonical guided operating instructions
- when a client drifts, prepend `guided_session_start` as the generic search-first stabilizer
- if a tool is not already directly visible on the current surface/phase, use `search_tools(...)` before `call_tool(...)`

When a bounded modeling intent matches, the default public working layer should be the macro layer:

- `macro_cutout_recess` for recesses, openings, and cutter-driven cutouts
- `macro_relative_layout` for align/place/contact-gap part layout
- `macro_attach_part_to_surface` for seating one part onto another object's surface/body
- `macro_align_part_with_contact` for minimal repair nudges on pairs that almost fit
- `macro_place_symmetry_pair` for mirrored pair placement/correction around an explicit mirror plane
- `macro_place_supported_pair` for mirrored pair placement/correction against one shared support surface
- `macro_cleanup_part_intersections` for bounded pairwise overlap cleanup without free-form collision solving
- `macro_adjust_relative_proportion` for bounded ratio repair between related objects
- `macro_adjust_segment_chain_arc` for bounded arc adjustment on ordered segment chains
- `macro_finish_form` for preset-driven bevel/subdivision/solidify finishing
- `reference_images` for goal-scoped reference intake before bounded visual comparison
- `reference_guided_creature_build` as a native prompt asset for staged generic creature work on `llm-guided`
- `recommended_prompts` can now steer creature-oriented guided sessions toward that prompt path by using active goal/session context
- `guided_reference_readiness` on `router_set_goal`, `router_get_status`, and staged reference compare/iterate payloads so clients can see whether reference-driven stage work is actually ready
- `reference_compare_stage_checkpoint` for deterministic multi-view stage comparison against attached references during manual iterative work
- `reference_iterate_stage_checkpoint` for a session-aware staged correction loop that remembers prior focus, can escalate into inspect/validate when the same correction repeats, and can now target one object, many objects, a collection, or the full assembled silhouette
- stage compare/iterate now also expose deterministic `silhouette_analysis` metrics, typed `action_hints`, and an advisory-only `part_segmentation` placeholder that stays disabled unless a separate sidecar is explicitly enabled
- `scene_scope_graph` for one explicit read-only structural scope artifact with anchor/core/accessory role hints
- `scene_relation_graph` for one explicit read-only pair-relation artifact derived from the current truth layer
- `scene_view_diagnostics` for one explicit read-only view-space artifact with projected extent, frame coverage, centering, and visible/partial/occluded/off-frame verdicts for named cameras or `USER_PERSPECTIVE`
- those spatial graph/view diagnostics tools are now part of the default visible `llm-guided` support set so the model can keep one explicit 3D orientation layer available instead of inferring spatial state only from names, screenshots, or partial loop payloads

Current guided bootstrap surface:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `reference_images`
- `scene_scope_graph`
- `scene_relation_graph`
- `scene_view_diagnostics`
- `search_tools`
- `call_tool`
- `list_prompts`
- `get_prompt`

Current guided utility prep path:

- bootstrap/planning search can now reach:
  - `scene_get_viewport`
  - `scene_clean_scene`
- these utility actions stay bounded and do not reopen the full legacy surface
- the canonical guided discovery wrapper is `call_tool(name=..., arguments=...)`
- the canonical cleanup argument shape on `llm-guided` is
  `keep_lights_and_cameras`; older split flags are compatibility-only and
  should not be used as the documented public form
- `reference_images(action="attach", source_path=...)` is one-reference-per-call;
  batch-like shapes now fail with guided recovery guidance instead of raw schema noise
- `collection_manage(action=..., collection_name=...)` stays the canonical
  public form; legacy `name` is only a narrow compatibility alias
- `modeling_create_primitive(...)` stays limited to `primitive_type`,
  `radius`/`size`, `location`, `rotation`, and optional `name`; unsupported
  shortcuts such as `scale`, `segments`, `rings`, `subdivisions`, or
  primitive-time `collection_name` now fail with actionable guidance on both
  direct and proxy guided paths
- build goals should still start from `router_set_goal(...)`, but screenshot /
  viewport / scene-reset requests should use the guided utility path instead
- if stale scene state is discovered only after entering the guided build
  surface, `scene_clean_scene(...)` is also available there as a bounded
  recovery hatch; cleanup before the goal is still the preferred path
- build-phase cleanup is still allowed when recovery is needed

Current public aliases on `llm-guided`:

| Internal tool | `llm-guided` public name | Public arg changes |
|---|---|---|
| `scene_context` | `check_scene` | `action` -> `query` |
| `scene_inspect` | `inspect_scene` | `object_name` -> `target_object` |
| `scene_configure` | `configure_scene` | `settings` -> `config` |
| `workflow_catalog` | `browse_workflows` | `workflow_name` -> `name`, `query` -> `search_query` |

Why that matters:

- the guided profile starts from 8 visible tools instead of the full catalog
- grouped/public tools stay easy to discover
- hidden atomic tools remain available as infrastructure, not as the default public mental model
- specialist families stay out of the normal guided entry layer until the macro surface is broader

## Atomic Foundations And Docs

The root `README.md` is intentionally **not** the full tool catalog anymore.

The detailed tool inventory and atomic family docs should stay in docs, not on the front page. That is the right long-term structure after `TASK-113`.

Use these docs depending on what you need:

- [Tool Layering Policy](./_docs/_MCP_SERVER/TOOL_LAYERING_POLICY.md)
  - Canonical policy for `atomic / macro / workflow`, hidden atomic tools, goal-first usage, and vision/assert boundaries.
- [MCP Server Docs](./_docs/_MCP_SERVER/README.md)
  - Surface profiles, guided aliases, versioned contracts, and runtime/platform guidance.
- [MCP Client Config Examples](./_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md)
  - Ready-to-paste local MCP client config examples for guided/manual surfaces plus MLX, OpenRouter, and Gemini vision variants.
- [Vision Layer Docs](./_docs/_VISION/README.md)
  - Runtime/backends, capture bundles, reference images, macro/workflow vision integration notes, and repo-tracked real viewport eval bundles for both direct user-view and fixed camera-perspective captures.
- [LLM Guide v2](./_docs/LLM_GUIDE_V2.md)
  - Strategy doc for a typed spatial-intelligence layer, compact relation state, and bounded next-step handoffs for guided operation.
- [Spatial Intelligence Research Brief](./_docs/FEATURES_LLM_GUIDE_V1.md)
  - External research handoff for LLM/VLM spatial reasoning, multi-view reasoning, and geometry-aware planning.
- [Spatial Intelligence Upgrade Proposal](./_docs/Spacial-intelligence-upgrades-for-blender-ai-mcp.md)
  - Research-driven upgrade proposal for scene graphs, symbolic relation notation, and supporting geometry-library choices.
- [Available Tools Summary](./_docs/AVAILABLE_TOOLS_SUMMARY.md)
  - Full inventory and grouped/public tool overview.
- [Tool Architecture Index](./_docs/TOOLS/README.md)
  - Maintainer-facing map of the tool families underneath the MCP surface.

If you want to see the atomic families the server is built on, start here:

- [Scene Tool Architecture](./_docs/TOOLS/SCENE_TOOLS_ARCHITECTURE.md)
- [Modeling Tool Architecture](./_docs/TOOLS/MODELING_TOOLS_ARCHITECTURE.md)
- [Mesh Tool Architecture](./_docs/TOOLS/MESH_TOOLS_ARCHITECTURE.md)
- [Mega Tool Architecture](./_docs/TOOLS/MEGA_TOOLS_ARCHITECTURE.md)

Recommended interpretation:

- keep `/_docs/TOOLS/` as the maintainer-facing atomic/grouped architecture map
- keep `README.md` product-facing and compact
- keep `/_docs/AVAILABLE_TOOLS_SUMMARY.md` as the runtime inventory

## Provider Notes

Current short version:

- **Local default:** `mlx_local` with a Qwen VL 4B-class model path; current repo-validated baseline is `mlx-community/Qwen3-VL-4B-Instruct-4bit`
- **External iterative compare candidate:** OpenRouter with `x-ai/grok-4.20-multi-agent`
- **External Google-family compare path:** OpenRouter-hosted Google-family models plus Google AI Studio / Gemini now share the same narrow staged-compare contract through resolved `vision_contract_profile` routing

External vision runtime note:

- `VISION_EXTERNAL_PROVIDER` selects the transport/provider branch
- `VISION_EXTERNAL_CONTRACT_PROFILE` optionally overrides the prompt/schema/parser contract for external compare flows
- when the override is unset, the runtime auto-matches Google-family model ids such as `gemma` / `gemini` / `learnlm`, then falls back to provider defaults

Detailed per-provider table:

- [Vision Layer Docs -> Provider Notes](./_docs/_VISION/README.md#provider-notes)

## Architecture

The system is split on purpose:

- **MCP server (`server/`)**: FastMCP surface, public tool definitions, transforms, discovery, and response contracts.
- **Router (`server/router/`)**: goal interpretation, safety/correction policy, workflow matching, session context, and guided execution behavior.
- **Blender addon (`blender_addon/`)**: actual `bpy` execution, RPC handlers, and Blender main-thread-safe operation scheduling.

Communication happens through JSON-RPC over TCP sockets.

More detail:

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [Router Docs](./_docs/_ROUTER/README.md)
- [Runtime Responsibility Boundaries](./_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md)
- [Addon Docs](./_docs/_ADDON/README.md)

## Structured Contract Baseline

The server is moving critical surfaces toward machine-readable payloads instead of prose-heavy JSON strings.

Current structured-contract baseline includes:

- `macro_cutout_recess`
- `macro_finish_form`
- `macro_attach_part_to_surface`
- `macro_align_part_with_contact`
- `macro_place_supported_pair`
- `macro_cleanup_part_intersections`
- `macro_relative_layout`
- `scene_create`
- `scene_configure`
- `mesh_select`
- `mesh_select_targeted`
- `mesh_inspect`
- `scene_snapshot_state`
- `scene_compare_snapshot`
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
- `router_set_goal`
- `router_get_status`
- `workflow_catalog`

That is important for automation, auditing, and future macro/workflow composition.

## Contact Truth Semantics

For contact-sensitive checks on curved or rounded forms, the truth layer now
distinguishes:

- mesh-surface contact/gap semantics when a bounded mesh-aware path is
  available
- bbox fallback semantics when a mesh-aware path is not available

That means a pair can still show bbox contact while the main measured relation
remains `separated` if the real mesh surfaces still have a visible gap. Guided
hybrid truth follow-up now carries that distinction forward in operator-facing
summaries instead of collapsing it into a generic "contact passed/failed"
claim.

When the mesh-aware path finds a real overlap, the main measured relation also
stays `overlapping`, so overlap rejection in `scene_assert_contact(...)` still
works as a separate truth condition instead of collapsing into plain contact.

## Structured Clarification Flow

The guided surface supports missing-input handling as part of the product contract, not as an afterthought.

- **Model-first clarification** is the default for `router_set_goal(...)` on `llm-guided`: missing workflow parameters return a typed `needs_input` payload to the outer model first.
- **Typed fallback payloads** keep the same flow usable on tool-only or compatibility clients.
- Human/native clarification is reserved for later/fallback policy rather than the default first step of workflow execution.
- `router_set_goal(...)` can ask for constrained choices, booleans, enums, or workflow confirmation.
- `partial answers` survive across follow-up turns.
- `workflow_catalog` import conflicts reuse the same clarification model.

## Guided Handoff Contract

The guided surface now treats workflow fallback as an explicit typed contract instead of a phase side effect hidden in prose.

- `router_set_goal(...)` returns `guided_handoff` on bounded continuation paths such as `continuation_mode="guided_manual_build"` and `continuation_mode="guided_utility"`.
- `guided_handoff` names the `target_phase`, `direct_tools`, `supporting_tools`, and `discovery_tools` for the next step on `llm-guided`.
- `workflow_import_recommended` stays `False` on these fallback paths unless the user explicitly asks for workflow import/create behavior.
- `router_get_status(...)` preserves the active `guided_handoff` in session diagnostics so clients can recover the intended continuation path.

## Server-Driven Guided Flow State

The guided surface now carries one explicit machine-readable `guided_flow_state`
contract in addition to `guided_handoff`.

- `router_set_goal(...)`, `router_get_status(...)`,
  `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)` can expose `guided_flow_state`
  for the active `llm-guided` session
- `guided_flow_state` reports:
  - `flow_id`
  - `domain_profile`
  - `current_step`
  - `completed_steps`
  - `active_target_scope`
  - `spatial_scope_fingerprint`
  - `spatial_state_version`
  - `spatial_state_stale`
  - `last_spatial_check_version`
  - `spatial_refresh_required`
  - `required_checks`
  - `next_actions`
  - `blocked_families`
  - `allowed_families`
  - `allowed_roles`
  - `completed_roles`
  - `missing_roles`
  - `required_role_groups`
  - `required_prompts`
  - `preferred_prompts`
  - `step_status`
- current domain overlays are:
  - `generic`
  - `creature`
  - `building`
- early guided build sessions now start from a step-gated spatial-context
  phase instead of exposing the whole build surface immediately
- `scene_scope_graph(...)` now binds the active guided target scope for the
  spatial gate; unrelated view checks such as
  `scene_view_diagnostics(target_object="Camera", ...)` do not satisfy a
  creature/building spatial check by themselves
- if reference images are attached for the active guided goal, treat them as
  the primary grounding input before deciding the first body/head/tail masses
  and rough silhouette
- use full semantic object names such as `Body`, `Head`, `Tail`,
  `ForeLeg_L`, and `HindLeg_R` instead of opaque abbreviations like `ForeL`
  / `HindR`, because guided seam/role heuristics are more reliable on readable
  names
- on `llm-guided`, the server can now warn on weak role-sensitive names and
  block clearly opaque placeholder names such as `Sphere` / `Object` when they
  are used as semantic part names
- do not call `scene_scope_graph(...)`, `scene_relation_graph(...)`, or
  `scene_view_diagnostics(...)` with no explicit scope and assume that means
  “inspect the whole scene”
- during an active guided spatial gate or spatial refresh re-arm, all three of
  those spatial helpers should be treated as explicit-scope tools, not as
  whole-scene probes
- after material scene changes such as `scene_clean_scene(...)`,
  `modeling_create_primitive(...)`, `modeling_transform_object(...)`, or
  bounded attachment/alignment macros, the guided runtime can mark the spatial
  layer stale and re-arm the required checks
- when `guided_flow_state.spatial_refresh_required == true`, treat
  `next_actions=["refresh_spatial_context"]` as authoritative server state,
  not advisory prose; refresh with `scene_scope_graph(...)` first, then rerun
  the remaining required spatial checks on the same target scope
- if stage compare/iterate finds important issues while the current guided
  role/workset slice is still incomplete, the governor can now keep the session
  in bounded build continuation instead of escalating too early into
  `inspect_validate`
- for creature blockout seams, `intersecting` can still be acceptable for
  embedded ear/head or snout/head placement, but `floating_gap` on head/body,
  tail/body, or limb/body remains actionable
- if a needed tool family is hidden/blocked-by-flow, inspect
  `router_get_status().guided_flow_state`, complete the listed
  `required_checks`, and follow `next_actions` instead of guessing hidden tool
  names into `call_tool(...)`
- exact tool-name searches on the guided surface are now shaped to return a
  tighter, smaller result set instead of flooding the model with a full
  expanded payload for simple lookups
- for role-sensitive build steps, treat `allowed_roles` and `missing_roles` as
  part of the execution contract, not as advisory prose
- use `guided_register_part(object_name=..., role=...)` as the canonical
  way to tell the server what semantic part one object represents; optional
  `guided_role=...` hints on build tools are convenience-only
- if the server warns or blocks on guided naming, rename or create the object
  using one of the suggested semantic names instead of retrying the same weak
  abbreviation
- the `required prompt bundle` and `preferred prompt bundle` named in
  `guided_flow_state` are prompt asset names, not a replacement for the
  server-driven flow; prompts support the flow, they do not become the flow

## Guided Reference Readiness

Reference-driven staged work now has one explicit readiness contract instead of
hidden ordering assumptions.

- `router_set_goal(...)` and `router_get_status(...)` expose `guided_reference_readiness`.
- the payload reports `attached_reference_count`, `pending_reference_count`,
  `compare_ready`, `iterate_ready`, plus machine-readable `blocking_reason` and
  `next_action`
- `reference_images(action="attach", source_path=...)` can stay pending until the guided
  goal session is actually ready, then adopt automatically
- if the same goal already has active refs and new ones are staged during
  `needs_input`, the staged refs stay separate from the already-active goal
  references until readiness returns
- if a ready session still carries explicit pending refs for another goal,
  `reference_images(action="list"| "remove"| "clear", ...)` now treats that
  merged visible set consistently instead of leaving broken pending records
- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` now fail fast when the session is
  not ready, and echo the same `guided_reference_readiness` payload
- if `reference_iterate_stage_checkpoint(...)` returns
  `loop_disposition="inspect_validate"`, stop free-form modeling and switch to
  inspect/measure/assert immediately
- if staged compare degrades but strong deterministic truth findings still
  exist, use the same inspect/measure/assert handoff instead of improvising
  another large free-form correction
- for staged compare/iterate, `goal_override` is no longer a session
  substitute; use an active guided goal session instead

## Session Diagnostics

Guided/runtime payloads now expose explicit MCP session metadata:

- `router_set_goal(...)` includes `session_id` and `transport`
- `router_get_status(...)` includes `session_id` and `transport`
- `reference_compare_stage_checkpoint(...)` includes `session_id` and `transport`
- `reference_iterate_stage_checkpoint(...)` includes `session_id` and `transport`

Current runtime guidance:

- stateful `streamable` HTTP is the recommended transport for longer guided
  runs and for debugging session-aware reference / checkpoint flows
- recent guided-session hardening removed the known router bookkeeping path
  that could clobber active goal/reference session state during routed tool
  execution
- if you investigate a future state-loss incident, compare `session_id` and
  `transport` first to distinguish:
  - transport/session reconnects
  - application-level goal resets
  - normal guided readiness blockers such as missing goal or references

## Server-Side Sampling Assistants Baseline

The MCP server now has a bounded analytical assistant layer inside an active request.

Current use cases:

- optional `assistant_summary` on inspection-heavy paths such as `scene_snapshot_state`, `scene_compare_snapshot`, `scene_get_hierarchy`, `scene_get_bounding_box`, and `scene_get_origin_info`
- bounded `repair_suggestion` on `router_set_goal`, `router_get_status`, and `workflow_catalog`

Explicit assistant terminal states:

- `success`
- `unavailable`
- `masked_error`
- `rejected_by_policy`

The rule is strict: assistants may help summarize or suggest, but they do not override scene truth or router policy.

## Versioned Surface Baseline

Public surface evolution is versioned explicitly:

| Surface profile | Default contract line |
|---|---|
| `legacy-manual` | `legacy-v1` |
| `legacy-flat` | `legacy-v1` |
| `llm-guided` | `llm-guided-v2` |

Compatibility note:

- `llm-guided-v1` remains selectable as a rollback line
- `workflow_catalog`, `scene_context`, and `scene_inspect` participate in the guided surface evolution story

## Code Mode Decision

Current benchmark baselines:

- `legacy-flat`
- `llm-guided`
- `code-mode-pilot`

Current decision:

- Go decision: keep `code-mode-pilot` as an experimental read-only surface
- Do not make Code Mode the default path for write-heavy or geometry-destructive Blender work

## Support Matrix

- **Blender**: tested on **Blender 5.0** in E2E coverage; addon minimum remains **Blender 4.0+** on a best-effort basis.
- **Python**: **3.11+**
- **FastMCP task runtime**: **fastmcp 3.1.1** + **pydocket 0.18.2**
- **OS**: macOS / Windows / Linux
- **Memory**: router semantic features rely on a local LaBSE model and related vector infrastructure

## Quick Start

### 1. Install the Blender addon

1. Download `blender_ai_mcp.zip` from the [Releases page](../../releases) or build it locally with `python scripts/build_addon.py`.
2. Open Blender -> Edit -> Preferences -> Add-ons.
3. Click **Install...** and select the zip file.
4. Enable the addon. It starts the local Blender RPC server on port `8765`.

### 2. Run the MCP server on the guided profile

Recommended defaults:

- `ROUTER_ENABLED=true`
- `MCP_SURFACE_PROFILE=llm-guided`
- map `/tmp` if you want host-visible image/file outputs

Example Docker command:

```bash
docker run -i --rm \
  -v /tmp:/tmp \
  -e BLENDER_AI_TMP_INTERNAL_DIR=/tmp \
  -e BLENDER_AI_TMP_EXTERNAL_DIR=/tmp \
  -e ROUTER_ENABLED=true \
  -e MCP_SURFACE_PROFILE=llm-guided \
  -e BLENDER_RPC_HOST=host.docker.internal \
  ghcr.io/patrykiti/blender-ai-mcp:latest
```

```bash
docker run --rm \
  -p 8000:8000 \
  -v /tmp:/tmp \
  -e BLENDER_AI_TMP_INTERNAL_DIR=/tmp \
  -e BLENDER_AI_TMP_EXTERNAL_DIR=/tmp \
  -e ROUTER_ENABLED=true \
  -e MCP_SURFACE_PROFILE=llm-guided \
  -e MCP_TRANSPORT_MODE=streamable \
  -e MCP_HTTP_HOST=0.0.0.0 \
  -e MCP_HTTP_PORT=8000 \
  -e MCP_STREAMABLE_HTTP_PATH=/mcp \
  -e BLENDER_RPC_HOST=host.docker.internal \
  ghcr.io/patrykiti/blender-ai-mcp:latest
```

Example generic MCP client config:

```json
{
  "mcpServers": {
    "blender-ai-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/tmp:/tmp",
        "-e", "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
        "-e", "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
        "-e", "ROUTER_ENABLED=true",
        "-e", "MCP_SURFACE_PROFILE=llm-guided",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ]
    }
  }
}
```

Network notes:

- **macOS / Windows:** use `host.docker.internal`
- **Linux:** prefer `--network host` with `BLENDER_RPC_HOST=127.0.0.1`
- `MCP_TRANSPORT_MODE=stdio` keeps the current subprocess/stdio MCP mode
- `MCP_TRANSPORT_MODE=streamable` starts a stateful Streamable HTTP MCP server

For broader profile/config examples, use:

- [MCP Server Docs](./_docs/_MCP_SERVER/README.md)
- [MCP Client Config Examples](./_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md)
- [`.env.example`](./.env.example) for the full tracked runtime/config variable set

## Testing

Unit tests:

```bash
PYTHONPATH=. poetry run pytest tests/unit/ -v
```

Unit collection count:

```bash
poetry run pytest tests/unit --collect-only
```

E2E tests:

```bash
python3 scripts/run_e2e_tests.py
```

E2E collection count:

```bash
poetry run pytest tests/e2e --collect-only
```

Pre-commit:

```bash
poetry run pre-commit install --hook-type pre-commit --hook-type pre-push
poetry run pre-commit run --all-files
```

More detail:

- [Test Docs](./_docs/_TESTS/README.md)
- [Development Docs](./_docs/_DEV/README.md)

## Documentation Map

- [Architecture](./ARCHITECTURE.md)
- [MCP Server Docs](./_docs/_MCP_SERVER/README.md)
- [Vision Layer Docs](./_docs/_VISION/README.md)
- [Router Docs](./_docs/_ROUTER/README.md)
- [Router Responsibility Boundaries](./_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md)
- [Addon Docs](./_docs/_ADDON/README.md)
- [LLM Guide v2](./_docs/LLM_GUIDE_V2.md)
- [Spatial Intelligence Research Brief](./_docs/FEATURES_LLM_GUIDE_V1.md)
- [Spatial Intelligence Upgrade Proposal](./_docs/Spacial-intelligence-upgrades-for-blender-ai-mcp.md)
- [Available Tools Summary](./_docs/AVAILABLE_TOOLS_SUMMARY.md)
- [Tool Architecture Index](./_docs/TOOLS/README.md)
- [Prompts](./_docs/_PROMPTS/README.md)
- [Tasks](./_docs/_TASKS/README.md)

## Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a PR. The repo enforces Clean Architecture boundaries, typed Python, router metadata rules, and pre-commit validation.

## Community And Support

If `blender-ai-mcp` is useful in your workflow, consider sponsoring its long-term development.

Sponsorship helps fund maintenance, docs, testing, and the higher-level reliability work that makes this repo different from raw Blender code generation: goal-first routing, curated tools, deterministic verification, and production-shaped workflow support.

[Become a sponsor](https://github.com/sponsors/PatrykIti)

- [SUPPORT.md](./SUPPORT.md)
- [SECURITY.md](./SECURITY.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [GitHub Sponsors](https://github.com/sponsors/PatrykIti)
- [Buy me a coffee](https://buymeacoffee.com/PatrykIti)

## Author

**Patryk Ciechański**

- GitHub: [PatrykIti](https://github.com/PatrykIti)

## License

This project is licensed under the **Apache License 2.0**.

See:

- [LICENSE.md](./LICENSE.md)
- [NOTICE](./NOTICE)
