# TASK-153: Guided Visibility Authority And Manifest Demotion

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** FastMCP Platform / Visibility Architecture
**Estimated Effort:** Large
**Follow-on After:** [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md)

## Objective

Make `build_visibility_rules(...)` the single runtime visibility authority for
`llm-guided`, while reducing `capability tags` / `capability_manifest` to
coarse/static metadata for discovery, inventory, and provider wiring.

## Business Problem

The current `llm-guided` stack still contains two conceptually overlapping
layers:

1. **Capability metadata layer**
   - `server/adapters/mcp/visibility/tags.py`
   - `server/adapters/mcp/platform/capability_manifest.py`

2. **Runtime visibility policy layer**
   - `server/adapters/mcp/transforms/visibility_policy.py`
   - `server/adapters/mcp/guided_mode.py`

This creates a persistent risk that:

- a tool appears allowed by `guided_flow_state.allowed_families`
- a tool appears enabled by `build_visibility_rules(...)`
- but some earlier metadata/phase layer silently prevents it from being
  visible or discoverable on the active `llm-guided` surface

Even when the immediate bug is fixed, this architectural overlap keeps making
new bugs cheap to create and expensive to debug.

## Current Code Baseline

The relevant code path currently spans:

- `server/adapters/mcp/visibility/tags.py`
  - `CAPABILITY_TAGS`
  - `phase_tag(...)`
  - `capability_phase_tag(...)`
- `server/adapters/mcp/platform/capability_manifest.py`
  - `CapabilityManifestEntry`
  - `CAPABILITY_MANIFEST`
- `server/adapters/mcp/guided_mode.py`
  - `_rule_matches_entry(...)`
  - `_is_capability_visible(...)`
  - `build_visibility_diagnostics(...)`
- `server/adapters/mcp/transforms/visibility_policy.py`
  - `build_visibility_rules(...)`
  - guided phase / flow specific tool sets
- `server/adapters/mcp/transforms/visibility.py`
  - runtime application of visibility rules
- `server/adapters/mcp/discovery/tool_inventory.py`
  - manifest-backed discovery/inventory helpers

This means the repo still lacks one fully explicit rule such as:

- static metadata decides what capability a tool belongs to
- runtime policy decides whether that tool is visible now
- metadata must not become a second hidden phase gate on `llm-guided`

## Acceptance Criteria

- `llm-guided` runtime visibility has one clear authority:
  `build_visibility_rules(...)` plus the session/flow state it reads
- capability tags/manifest remain useful for:
  - capability grouping
  - discovery metadata
  - inventory / docs / provider wiring
- capability tags/manifest no longer act as a second hidden runtime
  phase/visibility policy on `llm-guided`
- docs and regression coverage make the responsibility split explicit and
  durable

## Implementation Direction

1. Runtime authority path
   - `SessionPhase`, `guided_handoff`, and `guided_flow_state` feed
     `build_visibility_rules(...)`
   - that same rule model must drive:
     - FastMCP visibility transforms used by `list_tools()`
     - `router_get_status().visibility_rules`
     - guided-mode diagnostics
     - search/discovery filtering after session sync
   - no tag-only or manifest-only branch may silently veto or re-enable tools
     after the runtime rule set is built

2. Static metadata path
   - capability tags / manifest continue to own:
     - audience classification
     - entry/pinned grouping
     - provider grouping
     - public-name contracts
     - discovery categories / aliases
     - hidden-from-search defaults
   - if coarse phase labeling still matters for docs or inventory, it should
     live as metadata-only hints instead of acting as a registered runtime gate

3. Preferred refactor shape
   - prefer a shared helper that materializes the effective visible tool names
     from `build_visibility_rules(...)`
   - make `guided_mode.py`, `search_surface.py`, and regression tests consume
     that shared runtime result instead of maintaining parallel projections
   - avoid creating a second policy registry or a second manifest just for
     `llm-guided`

## Repository Touchpoints

- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Planned File Change Map

- `server/adapters/mcp/visibility/tags.py`
  - edit capability tags so runtime-facing registered tags no longer carry
    hidden `phase:*` authority on `llm-guided`
- `server/adapters/mcp/platform/capability_manifest.py`
  - edit manifest semantics to keep provider/discovery metadata useful after
    runtime demotion
- `server/adapters/mcp/guided_mode.py`
  - replace metadata-plus-policy visibility projection with a rule-driven
    projection derived from the active runtime rules
- `server/adapters/mcp/transforms/visibility_policy.py`
  - keep the single runtime authority and, if needed, expose a helper for
    materializing visible tool names from rules
- `server/adapters/mcp/transforms/visibility.py`
  - keep bootstrap visibility thin and aligned with the shared runtime policy
- `server/adapters/mcp/discovery/tool_inventory.py`
  - preserve inventory/discovery metadata without reintroducing runtime gating
- `server/adapters/mcp/discovery/search_surface.py`
  - ensure `search_tools(...)` only searches the tools allowed by the synced
    runtime visibility state
- `server/adapters/mcp/factory.py`
  - keep manifest/factory bootstrap metadata explicit and metadata-only
- `tests/unit/adapters/mcp/*.py`
  - expand unit coverage across visibility policy, diagnostics, discovery,
    inventory, factory, and docs parity
- `tests/e2e/integration/*.py`
  - expand stdio and streamable guided-session parity scenarios so every phase
    transition is transport-backed

## Planned Validation Matrix

- unit / runtime authority:
  - phase-tag demotion does not change `llm-guided` visibility semantics when
    explicit runtime rules already govern the surface
  - `build_visibility_diagnostics(...)` derives capability visibility from the
    same rule set that powers `list_tools()`
  - `search_tools(...)` does not leak runtime-hidden tools before unlock and
    does surface them after the relevant guided transition
- unit / metadata preservation:
  - provider groups, discovery categories, aliases, and pinned tools remain
    stable after manifest/tag demotion
  - factory bootstrap still exposes the same manifest scaffold across surfaces
- unit / docs parity:
  - docs say runtime visibility comes from `build_visibility_rules(...)`
  - docs say manifest/tags are discovery/inventory metadata, not a second gate
- E2E / stdio + streamable:
  - bootstrap surface
  - goal handoff into `establish_spatial_context`
  - spoofed spatial attempt that must not advance the flow
  - real spatial unlock into `create_primary_masses`
  - role-gated primary masses and secondary parts
  - spatial refresh re-arm and unlock
  - inspect/validate visibility parity
  - reconnect/new-session reset behavior

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-153-01](./TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md) | Define and document the exact responsibility split between metadata tags/manifest and runtime visibility |
| 2 | [TASK-153-02](./TASK-153-02_Runtime_Visibility_Authority_Consolidation_For_LLM_Guided.md) | Refactor `llm-guided` so runtime visibility is controlled only by visibility policy + session state |
| 3 | [TASK-153-03](./TASK-153-03_Regression_And_Docs_Closeout_For_Guided_Visibility_Authority.md) | Lock the new architecture in with regression tests, benchmarks, and docs |

## Status / Board Update

- completed on 2026-04-10 and moved from the follow-on queue into Done once
  runtime visibility authority, metadata demotion, regression coverage, and
  docs/history landed together

## Completion Summary

- demoted `phase:*` from runtime-facing capability tags into metadata-only
  manifest `phase_hints`
- kept capability tags/manifest useful for discovery, inventory, provider
  wiring, pinned defaults, and search enrichment
- rebuilt guided visibility diagnostics from the same runtime-visible tool
  membership implied by `build_visibility_rules(...)`
- updated docs and changelog so the runtime-vs-metadata ownership split is now
  explicit
