# TASK-146: Guided Runtime Guardrails, Vision Profile, And Prompting Hardening

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime Reliability / Product Surface
**Estimated Effort:** Large
**Dependencies:** TASK-130, TASK-141, TASK-142, TASK-143, TASK-144

**Completion Summary:** Completed on 2026-04-07. Hardened the guided runtime
after the TASK-141/142/143/144 wave: heuristic workflow triggering now stays
off explicit no-match/manual-goal sessions, Qwen/OpenRouter compare requests
use a more doc-aligned structured-output posture, Docker/runtime packaging now
keeps Pillow on the main runtime path, `call_tool(...)` gives stronger
search-first guidance on unknown tools, and the prompt-library/main-instruction
surfaces now push models/operators more explicitly toward `_docs/_PROMPTS/`
and `GUIDED_SESSION_START.md`.

## Objective

Stabilize the current post-TASK-141/142/143/144 guided runtime so the product
behaves more like a disciplined operator surface and less like a partially
guarded free-form tool sandbox.

This umbrella exists to fix the concrete failure modes now visible in real
guided sessions:

- workflow trigger heuristics firing on ordinary direct tool calls
- insufficient unit/E2E coverage around phase-locked or shaped-surface MCP logic
- Docker runtime images missing packages that guided/vision flows expect
- external Qwen/OpenRouter structured-output drift on compare/iterate paths
- prompt/instruction surfaces not pushing the model strongly enough toward:
  - `search_tools(...)` before speculative `call_tool(...)`
  - direct use of prompt-library assets in `_docs/_PROMPTS/`

## Business Problem

The recent guided runtime work improved truth-space state, relation graphs,
view diagnostics, and repair guidance. But real operator sessions still show a
different class of failures:

- false workflow triggering
- guessed hidden tools
- contract-drifted direct calls
- missing perception sidecar dependencies inside the deployed runtime
- external vision models returning prose instead of the required JSON
- prompt surfaces not reinforcing the intended guided operating model strongly
  enough

These are not "future feature" problems. They are repair and hardening work on
the current product path.

If left unresolved:

- real guided sessions keep paying avoidable failure tax
- the server appears flaky even when the underlying deterministic tools work
- prompt-library assets remain underused even though they were shipped to
  reduce drift
- external model support looks weaker than it may really be because the
  contract/profile path is under-verified

## Scope

This umbrella covers:

- workflow trigger boundary hardening for direct tool calls
- stronger unit/E2E coverage for shaped-surface MCP decision logic
- Docker dependency alignment with guided/vision runtime expectations
- official-doc verification and hardening for Qwen/OpenRouter structured JSON
  output on the active compare path
- stronger search-first guided prompting and `_PROMPTS/` usage guidance

This umbrella does **not** cover:

- new reconstruction capability families
- broad router redesign
- a new vision backend family
- replacing the current guided surface model

## Acceptance Criteria

- direct guided calls no longer spuriously trigger unrelated workflows such as
  `phone_workflow`
- coverage is materially stronger for the MCP/runtime logic that governs:
  - trigger decisions
  - shaped-surface tool exposure
  - guided direct-call behavior
  - recovery paths around hidden/phase-locked tools
- the Docker runtime includes the packages required by the intended guided
  vision/perception path, or installs them from the right Poetry groups in a
  deliberate and documented way
- the Qwen/OpenRouter structured-output path is verified against official docs
  and aligned in config/profile code rather than guessed from ad hoc behavior
- prompt-library assets and main instruction surfaces more strongly enforce:
  - search-first discovery
  - `_docs/_PROMPTS/` as the canonical operating library
  - reduced speculative `call_tool(...)` guessing

## Repository Touchpoints

- `server/router/application/triggerer/`
- `server/adapters/mcp/`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/`
- `server/infrastructure/config.py`
- `Dockerfile`
- `pyproject.toml`
- `_docs/_PROMPTS/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/`
- `tests/unit/router/adapters/`
- `tests/unit/router/application/triggerer/`
- `tests/unit/scripts/`
- `tests/e2e/router/`
- `tests/e2e/vision/`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Execution Structure

| Order | Subtask | Depends On | Purpose |
|------|---------|------------|---------|
| 1 | [TASK-146-01](./TASK-146-01_Workflow_Trigger_Boundaries_And_MCP_Guardrail_Coverage.md) | TASK-141, TASK-144 | Stop spurious workflow triggering and expand coverage around shaped-surface MCP/runtime decisions |
| 2 | [TASK-146-02](./TASK-146-02_Docker_Dependency_Group_And_Runtime_Packaging_Alignment.md) | TASK-121, TASK-128 | Ensure deployed Docker runtimes include the packages the guided vision/perception path actually expects |
| 3 | [TASK-146-03](./TASK-146-03_Qwen_OpenRouter_Structured_Output_Verification_And_Profile_Hardening.md) | TASK-140 | Verify official structured-output requirements and harden the active Qwen/OpenRouter profile path |
| 4 | [TASK-146-04](./TASK-146-04_Search_First_Prompt_Library_And_Instruction_Surface_Hardening.md) | TASK-130, TASK-141 | Push the guided operator surface harder toward `_PROMPTS/`, `search_tools(...)`, and lower speculative `call_tool(...)` usage |

## Status / Board Update

- closed on 2026-04-07 in the same branch as the implementation
- kept separate from TASK-145 so planner/sculpt evolution does not get
  conflated with current runtime hardening
