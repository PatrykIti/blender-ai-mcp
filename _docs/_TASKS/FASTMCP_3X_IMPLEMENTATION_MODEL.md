# FastMCP 3.x Implementation Model for Blender AI MCP

Canonical implementation model for TASK-083 through TASK-097.

Use this document to keep the FastMCP platform work aligned with the actual product goal of this repository:

- give LLMs a small, relevant action space
- preserve reliable structured Blender state
- make corrections explicit and verifiable
- keep compatibility while reshaping the public surface

---

## Product Goal

For this project, the FastMCP platform is not cosmetic infrastructure.
It is part of the core reliability story for LLM-driven Blender work:

- the model must discover tools without drowning in the full catalog
- the model must read scene and mesh state through structured payloads
- the model must understand what changed after each operation
- the model must be able to recover safely when context, mode, or selection drift
- the model must retain enough visibility into long-running work to stay oriented

The platform layer exists to make Blender state and tool semantics easier for an LLM to manage, not to add another abstract control plane for its own sake.

---

## Canonical Terms

### Protocol Naming Rule

- MCP spec versions are date-based (for example `2025-11-25`), not “MCP 3.x”.
- “3.x” in this document always refers to **FastMCP**.
- When protocol behavior matters, cite the MCP spec revision and/or SEP directly.

### Capability

One underlying business capability such as `scene_inspect`, `mesh_inspect`, `router_set_goal`, or `workflow_catalog`.

### Surface Profile

Bootstrap-time server composition preset.

Profiles define which providers, transforms, renderers, and visibility defaults are active.
Profiles are not versions.

Recommended profile set for this repo:

- `legacy-flat`
- `llm-guided`
- `internal-debug`
- `code-mode-pilot`

### Contract Version

FastMCP component version of a public contract for a capability.

Examples:

- `router_set_goal` v`1.x` legacy payload
- `router_set_goal` v`2.x` structured-first payload

Versions are selected through FastMCP versioning and `VersionFilter`.
They are not the same as profiles.

### Session Phase

Per-session runtime state used to adapt what is visible or emphasized.

Recommended baseline phases:

- `bootstrap`
- `planning`
- `workflow_resolution`
- `build`
- `inspect_validate`
- `repair`
- `export_handoff`

### Renderer

Adapter-side response presentation policy.

Recommended renderer set:

- `structured`
- `structured_plus_summary`
- `legacy_text`

---

## Single Source of Truth

The platform layer needs one canonical manifest.

Recommended ownership:

- `server/adapters/mcp/platform/...`
  - canonical platform manifest
  - audience tags
  - phase tags
  - public aliases
  - pinned defaults
  - response renderer defaults
  - contract-line/version policy references
- `server/router/infrastructure/tools_metadata/...`
  - router safety and semantic metadata
  - mode requirements
  - selection needs
  - routing hints
  - correction-related metadata

Do not make router metadata the primary discovery, audience, or visibility registry.

Search can enrich from docstrings and router metadata, but ownership of exposure belongs to the platform manifest.

---

## Transform Strategy

Prefer built-in FastMCP 3.x capabilities wherever they already fit the problem.

Use:

- shared `LocalProvider` instances for reusable capability sets
- built-in `ToolTransform` / `ArgTransform` for public aliasing
- built-in visibility controls and session visibility APIs
- built-in `BM25SearchTransform` for `llm-guided` discovery
- built-in `Prompts as Tools` bridge where needed
- built-in `VersionFilter` for public contract coexistence
- built-in `CodeMode` only on explicit experimental surfaces

Avoid building parallel custom mechanisms unless the built-in behavior is insufficient for a repo-specific requirement.

---

## Recommended Transform Order

Surface composition should follow this order:

1. Provider composition
2. Contract version filtering
3. Public tool and argument reshaping
4. Prompt/resource bridging for tool-only surfaces
5. Static visibility filtering by audience/profile/risk
6. Search or Code Mode discovery transform

Important consequences:

- search should operate on the already-versioned and already-reshaped public surface
- prompt bridge tools must exist before search if they should be discoverable
- session visibility changes should layer on top of the composed surface and must be reflected in search results

---

## Discovery Model

For this repo, the default `llm-guided` discovery model should be:

- `BM25SearchTransform`
- a very small pinned visible set
- native synthetic `search_tools` and `call_tool`

Recommended pinned visible set:

- `router_set_goal`
- `router_get_status`
- `workflow_catalog`
- prompt bridge entry tools when the surface is tool-only

Do not manually add `search_tools` and `call_tool` to the pinned list.
The search transform creates them.

Do not add a custom discovery proxy unless there is a proven gap in the built-in `call_tool` behavior.

---

## Structured Output Model

This repo already has many handlers returning `dict`-like state.
Keep that direction.

Recommended layering:

- domain/application handlers return structured data whenever the capability is state-heavy
- adapter contracts validate and normalize the payload
- renderer chooses:
  - pure structured
  - structured plus summary
  - legacy text fallback

High-priority structured-first areas:

- `scene_context`
- `scene_inspect`
- `mesh_inspect`
- `scene_snapshot_state`
- `scene_compare_snapshot`
- `router_set_goal`
- `router_get_status`
- `workflow_catalog`
- router execution and correction reports

---

## Elicitation Model

Use native elicitation on surfaces that support it.
Use a typed `needs_input` fallback on surfaces that do not.

Recommended split:

- `llm-guided`
  - async-aware router entry tools
  - native `ctx.elicit(...)`
- `legacy-flat`
  - no hard dependency on elicitation support
  - return stable typed fallback payloads with `request_id`, `questions`, and partial state

Do not force the whole server async in one migration.
Convert the interaction-heavy entry points first.

---

## Background Task Model

Use two layers together:

- FastMCP background tasks for client-facing task UX
- addon/server-side job registry for Blender work that must outlive a single blocking RPC wait

This repo cannot rely only on FastMCP `task=True` while the Blender addon still depends on one blocking request-response result queue.

Needed separation:

- task launch
- task progress
- task polling/result retrieval
- task cancellation

---

## Sampling Model

Sampling is server-orchestrated but client-mediated.

For this repo:

- sampling is optional
- sampling must be request-bound
- sampling must never become the authority for Blender truth or safety
- sampling outputs should be typed and bounded

Good fits:

- inspection summarization
- repair suggestion drafting
- compact analysis of large structured diagnostics

Bad fits:

- hidden geometry-destructive autonomy
- post-hoc background reasoning detached from an active client request

---

## Observability Model

FastMCP 3.x already emits native OpenTelemetry spans for MCP operations.
Use that as the base.

Then add repo-specific spans and attributes for:

- router phase
- correction policy decisions
- workflow match and adaptation path
- addon job identifiers
- contract line / surface profile

Do not rebuild base tool tracing from scratch if the runtime already provides it.

---

## Pagination Model

Treat these as two separate problems:

### Component Pagination

FastMCP `list_page_size` for:

- `tools/list`
- `prompts/list`
- `resources/list`

### Payload Pagination

Domain-specific `offset` / `limit` or cursor contracts for large tool payloads such as:

- mesh vertices / edges / faces / normals / attributes
- workflow catalog listings and import diagnostics

Do not collapse these into one implementation task without explicitly separating them.

---

## Recommended Delivery Order

1. Platform composition root, providers, and shared manifest
2. Search-first discovery
3. Session visibility and guided surfaces
4. Public surface reshaping and argument simplification
5. Structured elicitation and background task foundations
6. Structured output contracts and renderers
7. Versioned public contracts
8. Telemetry, timeouts, and diagnostics
9. Sampling assistants and Code Mode experiments
10. Confidence policy and correction audit hardening

### Blocking Migration Gates Before TASK-084+

After step 1, enforce two explicit gates before broad rollout of TASK-084 through TASK-097:

- **Gate A (post TASK-083-03): Composition Root Ready**
  - factory bootstrap is the runtime source of truth
  - profile selection is explicit and test-covered
  - global side-effect registration is no longer required for default startup
- **Gate B (post TASK-083-04): Transform Pipeline Ready**
  - transform order is deterministic and regression-tested
  - naming, visibility, and version shaping are transform-driven
  - provider-level vs server-level transform layering is documented and verified

If either gate fails, downstream implementation tasks should be limited to planning/docs only.
