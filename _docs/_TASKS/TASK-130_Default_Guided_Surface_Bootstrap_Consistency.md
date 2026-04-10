# TASK-130: Default Guided Bootstrap And Generic Governor Reliability

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime / Production Default / Governor Reliability
**Estimated Effort:** Large
**Depends On:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md), [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md), [TASK-151](./TASK-151_Spatial_Check_Freshness_Target_Binding_And_Guided_Rearm.md), [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md), [TASK-153](./TASK-153_Guided_Visibility_Authority_And_Manifest_Demotion.md), [TASK-154](./TASK-154_Guided_Naming_Policy_And_Semantic_Object_Name_Enforcement.md)

## Objective

Turn the existing `llm-guided` runtime into a more reliable generic governor
for goal-oriented sessions, so the model is steered through the right steps,
targets, and worksets using the server-owned flow/runtime contract instead of
drifting into ad hoc tool use.

This is not a squirrel-only task.
The target outcome is a generic guided-governor posture that works for:

- `creature`
- `building`
- `generic` object/blockout flows such as a chair or other asset without a
  dedicated domain overlay yet

## Business Problem

The repo already has many of the right server-owned ingredients:

- default spatial support from TASK-149
- `guided_flow_state` / domain overlays from TASK-150
- target binding and spatial re-arm from TASK-151
- prompt/runtime alignment from TASK-152
- single runtime visibility authority from TASK-153
- naming policy from TASK-154

But a real long-running guided build can still drift badly in practice:

- the model can waste time on the wrong first step or wrong request class
- it can keep using the wrong target/workset for the current governor state
- it can search too broadly and drown in results instead of getting the next
  bounded move
- it can treat one successful low-signal check as permission to keep free-running
- it can escalate to `inspect_validate` or linger there without a good generic
  continuation discipline

The result is a system that has strong local components but still feels too
easy for the model to "wiggle out of" in a real session.

The next job is therefore composition and governor hardening:

- use the server-owned runtime pieces that already exist
- remove or replace behavior that effectively acts as legacy free-form drift
  inside `llm-guided`
- make the generic guided path more deterministic without hardcoding
  squirrel-specific workflows everywhere

## Current Runtime Baseline

The relevant existing building blocks already live in the repo:

- `server/adapters/mcp/session_capabilities.py`
  - `guided_flow_state`
  - role groups / step transitions
  - target-bound spatial checks
  - spatial freshness / re-arm
- `server/adapters/mcp/router_helper.py`
  - fail-closed guided family/role execution enforcement
- `server/adapters/mcp/transforms/visibility_policy.py`
  - runtime visibility shaping by step/domain/flow state
- `server/adapters/mcp/discovery/search_surface.py`
  - guided search-first discovery path
- `server/adapters/mcp/areas/router.py`
  - `router_set_goal(...)`
  - `router_get_status()`
  - `guided_register_part(...)`
- `server/adapters/mcp/guided_naming_policy.py`
  - guided naming warnings/blocks for role-sensitive object names

The remaining gap is not “add another brain”.
The gap is making these existing layers cooperate more tightly as one generic
governor.

## Implementation Direction

This task should explicitly **reuse and extend the current server-driven guided
stack**, not build a second planner beside it.

Preferred posture:

- keep and extend:
  - `guided_flow_state`
  - guided domain overlays
  - target-bound scope/freshness discipline
  - guided role registration and naming policy
  - runtime visibility policy
  - search-first discovery on the shaped surface
- do **not** solve this with:
  - squirrel-specific hacks
  - prompt-only patches standing in for runtime policy
  - a second legacy/free-form guided mode inside `llm-guided`
  - broad reopening of hidden/internal tools to compensate for poor sequencing

The governor should become more explicit about:

- what the current request type is
- what step is active
- what the current target/workset is
- what the next bounded move is
- which visible/discoverable tool families actually matter now
- when inspect/iterate/repair escalation is appropriate

## Scope

This umbrella covers:

- the default guided bootstrap story and first-step request triage
- step/next-action hardening for the generic guided governor
- target/workset discipline so the model operates on the right object set at
  the right time
- domain-adaptive progression rules that stay generic-first and avoid
  squirrel-only assumptions
- search/discovery shaping so current-step results are tighter and less noisy
- regression coverage and docs for the governor behavior

This umbrella does **not** cover:

- implementing a new species-specific creature recipe tree
- replacing the current guided architecture with a brand-new planner
- broad legacy-flat compatibility behavior inside `llm-guided`

## Acceptance Criteria

- the default guided bootstrap story and runtime behavior tell one coherent
  production story
- the model is more tightly constrained to valid next moves by existing
  server-owned governor state instead of prompt luck
- target/workset handling becomes more reliable and generic across
  `creature`, `building`, and fallback `generic` sessions
- search/discovery is more bounded to the current governor state and less
  likely to dump overwhelming irrelevant tool lists
- the implementation stays generic-first and domain-adaptive instead of
  hardcoding squirrel-specific paths
- docs/tests prove the governor behavior end to end

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/guided_naming_policy.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this task ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-130-01](./TASK-130-01_Default_Guided_Bootstrap_And_Request_Triage_Consistency.md) | Align the production bootstrap story and the first-step request triage contract for the guided surface |
| 2 | [TASK-130-02](./TASK-130-02_Generic_Guided_Governor_Hardening_For_Step_Target_And_Domain_Discipline.md) | Harden the generic guided governor using the existing server-owned step/target/domain mechanisms |
| 3 | [TASK-130-03](./TASK-130-03_Regression_And_Docs_Closeout_For_Generic_Guided_Governor.md) | Lock the new generic-governor behavior in with regressions, docs, and changelog closeout |

## Status / Board Update

- repurpose/expand the earlier bootstrap-consistency follow-on into the broader
  guided-governor reliability umbrella, because the real remaining product gap
  is no longer only docs/runtime bootstrap drift

## Completion Summary

- aligned the guided production story with a broader generic-governor framing
- tightened explicit-scope discipline for active spatial-gate tools
- delayed too-early inspect escalation while the current build role/workset
  slice is still incomplete
- reduced search noise for exact tool-name lookups on the shaped guided surface
- follow-on post-run reliability gaps are tracked as
  [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md) instead of
  reopening this closed umbrella
