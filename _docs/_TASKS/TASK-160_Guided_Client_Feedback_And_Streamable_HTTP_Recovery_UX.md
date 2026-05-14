# TASK-160: Guided Client Feedback And Streamable HTTP Recovery UX

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Category:** FastMCP Platform / Guided Client UX
**Estimated Effort:** Large
**Follow-on After:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Related:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md), [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Context Anchor:** [300. Guided client feedback and Streamable follow-up](../_CHANGELOG/300-2026-05-04-task-160-guided-client-feedback-and-streamable-followup.md)

## Objective

Define the long-term product direction for how `llm-guided` clients should be
informed about guided-flow transitions, visibility changes, blocked families,
reference readiness, and Streamable HTTP recovery moments without forcing every
client to rediscover those rules from a later `router_get_status(...)` call.

This task is intentionally a single umbrella analysis pass. It documents:

- what is already landed
- what problem remains
- which solution options exist
- which ownership boundaries must be preserved

It does **not** yet fully split into broad execution branches. The first narrow
runtime slice is now tracked in
[TASK-160-01](./TASK-160-01_Streamable_HTTP_Visibility_Transaction_Audit_And_Discovery_Churn_Regression.md)
to harden Streamable HTTP visibility transactions and prove whether apparent
tool disconnects come from repo-side visibility churn or from client/harness
deferred-tool handling. Broader client-contract decomposition should still
follow only after the option analysis is chosen.

## Current Baseline Already Landed

The repo already has a partial stopgap for the immediate client-feedback gap:

- [server/adapters/mcp/session_capabilities.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/session_capabilities.py)
  - stable facade for the session-capability helpers
- [server/adapters/mcp/session_capabilities_flow.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/session_capabilities_flow.py)
  - `describe_guided_flow_feedback(...)`
  - owns the concise summary when `current_step`,
    `spatial_refresh_required`, `next_actions`, `required_checks`, or
    `allowed_families` changed materially
- [server/adapters/mcp/session_capabilities_state.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/session_capabilities_state.py)
  - owns the typed guided/session state consumed by the feedback formatter
- [server/adapters/mcp/areas/modeling.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/areas/modeling.py)
  - async `modeling_create_primitive(...)`
  - async `modeling_transform_object(...)`
  - both now emit immediate `ctx_info(...)` feedback when a guided-flow update
    was just triggered by the mutation
- [server/adapters/mcp/areas/scene.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/areas/scene.py)
  - stable facade/wiring layer for the scene area
- [server/adapters/mcp/areas/scene_spatial_graph.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/areas/scene_spatial_graph.py)
  - async `scene_scope_graph(...)`
  - async `scene_relation_graph(...)`
- [server/adapters/mcp/areas/scene_view_diagnostics.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/server/adapters/mcp/areas/scene_view_diagnostics.py)
  - async `scene_view_diagnostics(...)`
  - these now append the same guided-flow feedback to `payload.message` and emit
    `ctx_info(...)` when a required spatial-check transition was actually
    completed
- [tests/e2e/integration/test_guided_streamable_spatial_support.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/tests/e2e/integration/test_guided_streamable_spatial_support.py)
  - verifies that:
    - `scene_view_diagnostics(...)` does not clear the gate before the scope is
      properly bound
    - a stale `modeling_transform_object(...)` attempt can fail cleanly without
      destroying the Streamable HTTP session
- [tests/unit/adapters/mcp/test_guided_flow_state_contract.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/tests/unit/adapters/mcp/test_guided_flow_state_contract.py)
  - covers the guided-flow feedback formatter itself
- [tests/unit/tools/test_mcp_area_main_paths.py](/Users/pciechanski/Documents/_moje_projekty/blender-ai-mcp/tests/unit/tools/test_mcp_area_main_paths.py)
  - covers `ctx_info(...)` feedback on async modeling create/transform finalizers

These landed changes improve the current operator experience, but they are still
best viewed as a tactical patch, not the final product contract.

## Business Problem

The current `llm-guided` runtime already has the right state model:

- `guided_handoff`
- `guided_flow_state`
- `guided_reference_readiness`
- visibility shaping through FastMCP platform rules
- deterministic `required_checks` / `next_actions`

The problem is how those state changes reach the client at the moment they
happen.

Recent operator transcripts exposed the failure mode clearly:

- the client reads `guided_manual_build` and `guided_reference_readiness`, but
  still attempts a now-invalid next tool because the surface changed between one
  call and the next
- the client can interpret a newly hidden or blocked tool as a disconnect or a
  mysterious transport failure instead of as “the guided flow just moved to a
  new step”
- the client can run `scene_view_diagnostics(...)` against the wrong timing or
  wrong scope and then misread the still-pending refresh gate as a runtime bug
- when Streamable HTTP or the harness actually does reconnect, the repo state is
  usually still coherent, but the operator lacks one tight explanation of what
  changed and what must happen next

In short:

- the **server knows** what happened
- the **client often learns it too late**
- and some clients then narrate a state transition as a disconnect or crash

## Observed Runtime Pattern

The most common creature-build failure pattern now looks like:

1. `router_set_goal(...)` returns `status="no_match"` together with
   `continuation_mode="guided_manual_build"` and a typed guided handoff.
2. references are attached one-by-one and `guided_reference_readiness` becomes
   `ready`.
3. primary masses such as `body_core` and `head_mass` are created.
4. the role summary completes the required primary role group and the guided
   flow moves into `place_secondary_parts`.
5. that transition re-arms `spatial_refresh_required=true`,
   `required_checks=[scope_graph, relation_graph, view_diagnostics]`, and
   `allowed_families=["spatial_context","reference_context"]`.
6. if the client still tries a build-family mutation on stale assumptions, the
   tool is now outside the allowed surface.

This pattern is correct server-side. The open question is how to make that
transition legible enough that all serious MCP clients react correctly.

## Why This Matters

If the product leaves this as implicit behavior:

- stronger clients will need repo-specific heuristics to survive ordinary guided
  state transitions
- weaker clients will continue to misreport blocked or hidden tool paths as
  transport/runtime failures
- future guided surfaces will accrete more prompt-only workarounds instead of
  one stable interaction contract

The goal is to make the guided runtime feel predictable for clients in the same
way the geometry/runtime rules are already predictable for the server.

## Option Analysis

### Option A: Immediate Feedback On Existing Tool Surfaces

Use the existing public tools and add lightweight feedback on success or state
transition.

Examples:

- append one short guided-flow delta to `payload.message`
- emit one `ctx_info(...)` summary on the active request
- keep `router_get_status(...)` as the authoritative full state dump

Pros:

- universal across tool-only clients
- fits the current FastMCP platform layer
- low-risk extension of already-landed work

Cons:

- still partly prose
- clients must parse human-readable hints unless a richer contract is added

### Option B: Structured Guided Flow Delta Contract

Add a small typed field such as `guided_flow_update` or
`guided_surface_transition` to guided mutating tools and required spatial-check
tools.

Likely contents:

- `current_step`
- `spatial_refresh_required`
- `next_actions`
- `allowed_families`
- `required_checks`
- optional `active_target_scope`

Pros:

- machine-readable and deterministic
- easiest for Claude/Codex/Gemini-style clients to consume consistently
- reduces reliance on extra `router_get_status(...)` polling

Cons:

- wider MCP contract change
- must be applied consistently across the affected guided surfaces

### Option C: FastMCP Apps / Richer Client Surface

Use newer MCP/FastMCP app-like presentation features as an optional higher-level
surface for guided sessions.

Potential uses:

- guided session panel
- “next action” chips
- explicit refresh action for spatial context
- structured status card for `guided_reference_readiness`

Pros:

- best UX for capable clients
- can make guided recovery more obvious than raw tool text

Cons:

- not all MCP clients support richer app surfaces
- cannot be the only fix for tool-only or proxy-style clients
- must remain inside the FastMCP platform responsibility boundary, not become a
  second router/runtime flow

### Option D: Client / Harness Recovery Logic Outside Repo

Leave the repo mostly as-is and rely on client-side logic:

- if a tool disappears, re-read `router_get_status(...)`
- if a tool blocks, auto-run the declared `next_actions`
- if transport reconnects, recover from session state

Pros:

- no additional server contract required

Cons:

- pushes repo-specific behavior into each client
- hardest path to make reliable across different MCP operators

## Recommended Direction

The most defensible long-term path is:

1. keep **Option A** as the current tactical stopgap
2. promote **Option B** as the primary long-term server contract
3. treat **Option C** as an optional UX layer for app-capable clients
4. treat **Option D** as helpful but non-authoritative client behavior

In other words:

- the base fix should stay server-owned and client-agnostic
- richer app surfaces may improve the experience
- but clients must not be forced to infer guided state transitions from hidden
  tool catalogs or reconnect behavior

## Apps Evaluation Boundary

Using MCP app-like capabilities is worth evaluating, but only as a presentation
layer enhancement.

This task should keep the authority split explicit:

- FastMCP platform/app surfaces may explain or present the current guided step
- the router/session state still owns the actual decision
- scene/spatial/assertion layers still own truth
- app surfaces must not become a second hidden execution path or a client-only
  fork of the guided runtime

## Non-Goals

This umbrella deliberately does not:

- change the meaning of `guided_manual_build`
- remove `guided_reference_readiness`
- replace `router_get_status(...)` as the authoritative detailed state surface
- introduce a second guided runtime
- treat app-like MCP surfaces as mandatory for all clients
- solve generic MCP server disconnects outside the repo’s own guided/runtime
  contract

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-160-01](./TASK-160-01_Streamable_HTTP_Visibility_Transaction_Audit_And_Discovery_Churn_Regression.md) | Completed narrow runtime slice that locked Streamable visibility transactions and captured the current evidence anchor for this umbrella |

No broader physical child subtree exists yet. Create the next execution leaves
only after this umbrella's option analysis is accepted.

## Repository Touchpoint Table

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/session_capabilities_flow.py`, `session_capabilities_state.py`, `session_capabilities.py` | Guided session state and stable facade | `session_capabilities.py` is now the stable facade, while the live feedback formatter and typed state owners live in the modular flow/state files |
| `server/adapters/mcp/areas/modeling.py` | Guided build mutations | Current place where create/transform mutations can emit immediate guided-flow feedback |
| `server/adapters/mcp/areas/scene_spatial_graph.py`, `scene_view_diagnostics.py`, `scene.py` | Spatial support tools and facade | the scene facade remains the public area seam, but the actual spatial-check feedback logic now lives in the modular scene area owners |
| `server/adapters/mcp/router_helper.py` | Routed execution / policy context | Candidate owner if a future structured `guided_flow_update` should be attached generically to routed tool results |
| `server/adapters/mcp/guided_mode.py` | FastMCP visibility | Defines what the visible guided surface actually is at each step |
| `server/adapters/mcp/execution_report.py` | Routed result envelope | Candidate owner if future structured transition metadata should ride on existing routed reports |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable HTTP runtime proof | Owns the integration proof for guided step transitions, stale refresh gates, and clean session survival |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | Session-state proof | Owns exact expectations for feedback text and guided step transitions |
| `tests/unit/tools/test_mcp_area_main_paths.py` | Async tool finalizer proof | Owns exact expectations for feedback emitted after async modeling mutations |
| `_docs/_MCP_SERVER/README.md` | Public transport/client guidance | Must stay aligned with any future structured feedback contract or app-surface recommendation |
| `_docs/_PROMPTS/README.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md` | Operator guidance across guided domains | this umbrella is generic guided-client substrate work, so creature and architecture prompt guidance must stay aligned with the chosen recovery contract |
| `_docs/_TASKS/README.md` | Board | Track this work as one promoted umbrella until the option analysis is chosen |
| `_docs/_CHANGELOG/` | Historical record | Record the already-landed stopgap and the umbrella creation in the same historical trail |

## Runtime / Security Contract Notes

- Visibility/platform boundary: the repo should prefer FastMCP-native discovery,
  visibility, and app/prompt presentation instead of inventing another router
  output channel.
- Transport boundary: Streamable HTTP request paths must finish guided
  finalizers before the response completes; client feedback must not rely on
  detached writes.
- Session boundary: same-session visibility/discovery stabilization may be
  added where Streamable HTTP clients can race a refresh, but the contract must
  remain session-scoped rather than becoming a cross-session/global bottleneck.
- Client contract: any new feedback must remain valid for tool-only clients
  before it becomes an app-capable enhancement.
- Truth boundary: feedback may explain state transitions, but it must not blur
  deterministic scene/spatial/assertion truth with client UX hints.

## Test Matrix

| Layer | Validation Need |
|-------|-----------------|
| Unit session state | exact feedback formatter output for step/refresh/allowed-family transitions |
| Unit async tool finalizers | create/transform flows emit feedback after the guided state actually changes |
| Unit routed policy | blocked/hidden-family cases keep their fail-closed meaning and do not regress into vague errors |
| Integration / Streamable HTTP | stale refresh gates, required spatial-check sequencing, and client-readable survival after blocked calls |
| Docs / prompts | client guidance stays aligned with the chosen contract direction and does not overclaim app-only behavior |

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- the umbrella-history entry and the `TASK-160-01` follow-on entry already
  exist; future implementation follow-ups should update or extend that indexed
  changelog trail instead of planning a duplicate “first” entry
- future implementation follow-ups should also update:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `_docs/_PROMPTS/GUIDED_SESSION_START.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`

## Changelog Impact

- add one historical changelog entry now for:
  - the already-landed guided-flow feedback stopgap
  - the new Streamable HTTP regression coverage
  - the creation of `TASK-160` as the umbrella for the long-term solution

## Acceptance Criteria

- the repo has one canonical umbrella describing the client-feedback problem,
  the currently landed stopgap, and the forward options
- the umbrella makes it explicit which parts are already implemented versus
  still under analysis
- the option analysis distinguishes repo-owned contract work from harness/client
  behavior outside the repo
- the task is actionable enough that a later implementation split can happen
  without re-deriving the problem from transcript fragments

## Status / Board Update

- promote `TASK-160` as one board-level umbrella only
- keep `TASK-160-01` as a completed narrow execution leaf under the umbrella,
  but do not promote it to its own board row in this pass
- when the option analysis is accepted, create the next physical execution
  subtree from this umbrella instead of improvising ad hoc follow-ons
