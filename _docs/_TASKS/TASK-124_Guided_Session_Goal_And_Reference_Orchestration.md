# TASK-124: Guided Session Goal and Reference Orchestration

**Priority:** 🔴 High  
**Category:** Product Reliability / Guided Session UX  
**Estimated Effort:** Large  
**Dependencies:** TASK-121, TASK-122  
**Status:** ⏳ To Do

## Objective

Make `llm-guided` reference-driven work session-safe and operator-safe so a
user can naturally say:

- "make me a low-poly squirrel"
- "here are two reference images"

without needing to remember the hidden ordering rules for:

- goal activation
- reference attachment
- staged compare / iterate checkpoints

The system should enforce that ordering itself, expose readiness explicitly,
and fail fast when the session state is not coherent.

## Business Problem

Today the product still leaks internal sequencing rules into the user
experience:

- `reference_images(action="attach", ...)` can attach into a pending state when
  no goal is active
- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` can be called before the session is
  truly ready
- a model may compensate by:
  - guessing recovery steps
  - reattaching references repeatedly
  - mixing `goal_override` with a session that still has no active goal
  - wasting context budget on discovery for tools it already knows

This is not a user problem. It is a product problem.

If `llm-guided` is the intended production surface, then:

- the user should not need to know the correct call ordering
- the model should not need to rediscover preconditions ad hoc
- the runtime should either:
  - automatically normalize the session into a valid state
  - or fail fast with one explicit next action

## Business Outcome

If this task is done correctly, the repo gains:

- reliable reference-driven guided sessions that survive natural-language use
- less model drift around goal/reference attachment order
- less token waste on unnecessary recovery/discovery loops
- clearer readiness diagnostics for operators and client prompts
- a more credible guided experience for any reference-driven build, not only
  squirrels

## Scope

This umbrella covers:

- explicit session readiness modeling for guided reference work
- deterministic pending-reference adoption semantics
- fail-fast preconditions on compare/iterate tools
- clearer guided handoff / status payloads for reference readiness
- regression coverage and prompt guidance for natural request flows

This umbrella does **not** cover:

- changing the underlying vision models
- changing the core truth/macro correction logic
- replacing `router_set_goal(...)` with a fully autonomous workflow engine
- broad changes to unrelated manual/no-router surfaces

## Acceptance Criteria

- a guided reference session has one explicit readiness model instead of hidden
  sequencing assumptions
- pending references are either adopted deterministically or blocked with an
  explicit reason
- compare/iterate tools fail fast when the session is not ready
- guided status/handoff payloads make the next required action obvious
- prompts/docs and regression coverage reflect the real guided flow

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_TASKS/README.md`

## Completion Update Requirements

- add a `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
- update the guided-session docs and prompt surfaces that describe reference
  attachment and staged correction loops
- add or update focused unit coverage first, and add/update E2E coverage where
  runtime behavior changes
- keep `_docs/_TASKS/README.md` and all child task statuses in sync

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-124-01](./TASK-124-01_Guided_Reference_Session_Readiness_Contract.md) | Define one explicit readiness model and precondition contract for guided reference sessions |
| 2 | [TASK-124-02](./TASK-124-02_Pending_Reference_Adoption_And_Goal_Lifecycle.md) | Make pending reference adoption and goal activation semantics deterministic |
| 3 | [TASK-124-03](./TASK-124-03_Fail_Fast_Compare_And_Iterate_Preconditions.md) | Make compare/iterate tools fail fast and operator-safe when the session is not ready |
| 4 | [TASK-124-04](./TASK-124-04_Guided_Handoff_And_Status_Readiness_UX.md) | Expose the next required action through guided status and handoff payloads |
| 5 | [TASK-124-05](./TASK-124-05_Natural_Request_Regression_Pack_And_Prompting.md) | Validate the full flow against natural user requests with reference images |
