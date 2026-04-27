# TASK-147: Guided Build Cleanup Recovery Hatch And Prompt Alignment

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime UX / Recovery Hatches
**Estimated Effort:** Medium
**Dependencies:** TASK-130, TASK-146

**Completion Summary:** Completed on 2026-04-07. Shipped
`scene_clean_scene(...)` as an explicit build-phase recovery hatch on the
`llm-guided` surface, kept the cleanup-first recommendation for pre-goal
utility flow, and updated prompt/docs/tests so operators and models know both:
clean the scene before `router_set_goal(...)` when possible, and use the same
tool as a visible recovery hatch if scene drift is discovered after entering
`guided_manual_build`.

## Objective

Repair one concrete guided-session usability failure:

- after entering `guided_manual_build`, the model can discover that the scene
  still needs cleanup
- but `scene_clean_scene(...)` was previously phase-locked away from the build
  surface even though it remained one of the most practical recovery actions

The goal is to make cleanup behavior match real operator needs without
reopening the broad legacy surface.

## Business Problem

The intended guided operating model already says:

- perform cleanup as a utility step before the goal when possible

But real sessions often discover late that the scene still contains:

- the default cube
- stale blockout parts
- unwanted leftovers from prior attempts

When that happens inside build phase, hiding `scene_clean_scene(...)` creates a
bad product outcome:

- the tool exists
- the model/operator knows the correct tool name
- but the shaped surface rejects it as unavailable

That drives needless drift:

- guessing other tool names
- awkward workarounds around the default cube
- confusion about whether the tool exists at all

## Scope

This repair covers:

- exposing `scene_clean_scene(...)` on the guided build surface as an explicit
  recovery hatch
- preserving the guidance that cleanup should still happen before the goal
  whenever possible
- aligning search/call behavior, prompt assets, README/MCP docs, and regression
  coverage with that product rule

This repair does **not** broaden the build surface into a general system/debug
surface and does not make save/undo a blanket addition to build phase.

## Acceptance Criteria

- `scene_clean_scene(...)` remains a guided utility tool on bootstrap/planning
- `scene_clean_scene(...)` is also available on the guided build surface as a
  bounded recovery hatch
- prompt/docs clearly state:
  - cleanup before goal is preferred
  - build-phase cleanup is still allowed when recovery is needed
- unit and E2E coverage protect:
  - build-phase visibility/search for the cleanup hatch
  - transport-backed guided use after manual/no-match handoff

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `_docs/_PROMPTS/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this repair ships

## Status / Board Update

- completed directly in the same branch as the repair
- tracked as a finished follow-on after TASK-146
