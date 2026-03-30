# blender-ai-mcp

[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-lightgrey.svg)](./LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://github.com/PatrykIti/blender-ai-mcp/pkgs/container/blender-ai-mcp)
[![CI Status](https://github.com/PatrykIti/blender-ai-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/PatrykIti/blender-ai-mcp/actions)

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

This is what turns the project from "Blender tools exposed over MCP" into a usable AI control product for modeling pipelines.

## LLM-Guided Public Surface

`llm-guided` is the default production-oriented surface. It is intentionally small, search-first, and designed around goal-aware sessions.

Normal guided flow:

1. `router_set_goal(...)`
2. `browse_workflows`, `search_tools`, or `call_tool`
3. use grouped/public tools such as `check_scene`, `inspect_scene`, or `configure_scene`
4. verify with inspection plus `scene_measure_*` and `scene_assert_*`

When a bounded modeling intent matches, the default public working layer should be the macro layer:

- `macro_cutout_recess` for recesses, openings, and cutter-driven cutouts
- `macro_relative_layout` for align/place/contact-gap part layout
- `macro_finish_form` for preset-driven bevel/subdivision/solidify finishing
- `reference_images` for goal-scoped reference intake before bounded visual comparison
- `reference_compare_stage_checkpoint` for deterministic multi-view stage comparison against attached references during manual iterative work
- `reference_iterate_stage_checkpoint` for a session-aware staged correction loop that remembers prior focus, can escalate into inspect/validate when the same correction repeats, and can now target one object, many objects, a collection, or the full assembled silhouette

Current guided bootstrap surface:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `reference_images`
- `search_tools`
- `call_tool`
- `list_prompts`
- `get_prompt`

Current guided utility prep path:

- bootstrap/planning search can now reach:
  - `scene_get_viewport`
  - `scene_clean_scene`
- these utility actions stay bounded and do not reopen the full legacy surface
- build goals should still start from `router_set_goal(...)`, but screenshot /
  viewport / scene-reset requests should use the guided utility path instead

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
- [Vision Layer Docs](./_docs/_VISION/README.md)
  - Runtime/backends, capture bundles, reference images, macro/workflow vision integration notes, and repo-tracked real viewport eval bundles for both direct user-view and fixed camera-perspective captures.
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

For broader profile/config examples, use [MCP Server Docs](./_docs/_MCP_SERVER/README.md).

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
- [Router Docs](./_docs/_ROUTER/README.md)
- [Router Responsibility Boundaries](./_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md)
- [Addon Docs](./_docs/_ADDON/README.md)
- [Available Tools Summary](./_docs/AVAILABLE_TOOLS_SUMMARY.md)
- [Tool Architecture Index](./_docs/TOOLS/README.md)
- [Prompts](./_docs/_PROMPTS/README.md)
- [Tasks](./_docs/_TASKS/README.md)

## Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a PR. The repo enforces Clean Architecture boundaries, typed Python, router metadata rules, and pre-commit validation.

## Community And Support

- [SUPPORT.md](./SUPPORT.md)
- [SECURITY.md](./SECURITY.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [GitHub Sponsors](https://github.com/sponsors/PatrykIti)
- [Buy me a coffee](https://buymeacoffee.com/PatrykIti)

## Author

**Patryk Ciechański**

- GitHub: [PatrykIti](https://github.com/PatrykIti)

## License

This project is licensed under the **Business Source License 1.1 (BUSL 1.1)**.

This means the repository is **source-available, not Open Source** in the OSI
sense. The full legal terms are in [LICENSE.md](./LICENSE.md). The summary
below is informational only; if there is any conflict, `LICENSE.md` controls.

Allowed without a separate commercial license:

- non-production use such as evaluation, development, testing, and research
- internal organizational use, including production use, as long as you are not
  offering the Licensed Work itself to third parties on a hosted or embedded
  basis as a competing product
- internal use to create outputs for clients, such as assets, renders, or
  reports, without giving clients access to the Licensed Work itself

Commercial license required:

- offering this repository, or its functionality, to third parties on a
  hosted basis in order to operate a competing offering
- embedding or bundling this repository into a product that is offered to third
  parties in order to operate a competing offering

Practical examples:

- `Hosted` means a third party can use your deployed MCP/API surface over the
  network without obtaining their own copy of this repository
- `Embedded` means your product includes this repository's source or binaries,
  or depends on them being installed/accessed/downloaded for the product to
  operate
- if you use the repo internally inside your studio/company to produce Blender
  deliverables for clients, that is described in [LICENSE.md](./LICENSE.md) as
  not being a competing offering

Change License:

- the current `LICENSE.md` names **Apache License 2.0** as the Change License;
  see [LICENSE-APACHE-2.0.txt](./LICENSE-APACHE-2.0.txt)
- the current Change Date in `LICENSE.md` is **2029-12-01**
- under BUSL 1.1, the Change License also takes effect on the fourth
  anniversary of the first public distribution of a specific version, whichever
  comes first

If you need rights beyond the Additional Use Grant, including operating a
competing hosted or embedded offering, use the contact in
[LICENSE.md](./LICENSE.md).
