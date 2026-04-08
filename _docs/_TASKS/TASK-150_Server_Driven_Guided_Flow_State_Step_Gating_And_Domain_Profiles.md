# TASK-150: Server-Driven Guided Flow State, Step Gating, And Domain Profiles

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Server-Driven Orchestration
**Estimated Effort:** Large
**Dependencies:** TASK-124, TASK-145, TASK-149
**Follow-on After:** [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md)

## Objective

Move `llm-guided` from a mostly advisory server surface to a more explicitly
server-driven guided flow where the MCP runtime:

- owns the current guided flow state
- exposes the current required step and next allowed moves
- gates the visible/actionable tool set by that step
- adapts the flow policy by domain profile instead of forcing one universal
  sequence onto every build

The target outcome is not "hardcode squirrel mode".
The target outcome is a generic orchestration layer with domain-adaptive
profiles such as:

- `generic`
- `creature`
- `building`

with room for later follow-on profiles without redesigning the whole guided
runtime again.

## Business Problem

The repo already has several good guided-runtime ingredients:

- `guided_handoff`
- guided phase visibility
- `recommended_prompts`
- `guided_reference_readiness`
- staged compare/iterate loops
- default spatial graph/view support

But they are still mostly advisory.
The model can still ignore them and improvise.

That creates a predictable failure mode in real sessions:

- the server returns the right guidance
- the model does not actually follow it
- the session drifts into generic tool use, wrong sequencing, and weak shape
  or placement quality

The squirrel regression is only one instance of the wider issue.
The same pattern will recur for:

- buildings
- generic product/object blockout
- future domain-specific guided flows

if the server continues to expose "good hints" without also owning the
execution contract.

This is therefore not a creature-only repair.
It is a product-level guided-orchestration gap.

## Current Runtime Baseline

The current server already controls some important parts of the interaction:

- `router_set_goal(...)` chooses a guided continuation path
- `guided_handoff` describes direct tools, supporting tools, and discovery
  tools for the next step
- `SessionPhase` shapes visibility
- `recommended_prompts` can steer prompt selection from active goal/session
  state
- compare/iterate tools already expose machine-readable loop outcomes
- spatial graph/view diagnostics are now directly visible on `llm-guided`

What is still missing is one explicit server-owned flow contract:

- what step are we on?
- what step must happen next?
- which checks are required before moving forward?
- which prompt asset(s) are required for this flow?
- which tool families are allowed now?
- which families are still premature?

Without those answers living in the server, the model still has too much room
to behave like a generic tool-caller.

## Business Outcome

If this umbrella is done correctly, the repo gains:

- a client-agnostic guided flow contract that works across Claude, Codex,
  Gemini, and other MCP clients without depending on client-specific prompt
  discipline
- deterministic server-owned sequencing for guided sessions
- a generic guided flow model with domain-specific overlays instead of one
  monolithic sequence or one-off hardcoded creature logic
- stronger control over when the model can:
  - start building
  - iterate a checkpoint
  - move to later repair/refinement stages
  - jump to inspect/validate
- a cleaner path for future reconstruction domains because the flow engine
  becomes reusable infrastructure instead of repeating prompt-only fixes

## Implementation Direction

This umbrella should be implemented as a **server-driven guided flow layer**
above the current phase/handoff model, not as a second free-form planner and
not as a full replacement for the current router/workflow system.

The intended posture is:

- keep using:
  - `router_set_goal(...)`
  - `guided_handoff`
  - session capability state
  - shaped visibility
  - compare/iterate loop contracts
- add one explicit `guided_flow_state` concept that captures:
  - `flow_id`
  - `domain_profile`
  - `current_step`
  - `completed_steps`
  - `required_checks`
  - `required_prompts`
  - `allowed_tools`
  - `blocked_families` or equivalent bounded restrictions
  - `next_action` / `next_actions`
- select the domain profile deterministically from goal, recipe, and current
  runtime state rather than from prompt wording alone
- let visibility and execution guards consult `guided_flow_state`, not only
  coarse phase

This should be **generic first**:

- one shared flow skeleton
- domain overlays for:
  - `generic`
  - `creature`
  - `building`

The domain overlays may differ in:

- step names
- required checks
- required prompt assets
- allowed tool families
- compare/iterate cadence

but they should all sit on the same contract model.

## Product Design Requirements

### Server-Driven, Not Client-Optional

- the intended flow must be represented in machine-readable server output, not
  only in prose prompt assets
- the server should make the right path easier than the wrong path by:
  - visibility shaping
  - `call_tool(...)` guardrails
  - explicit next-step state
- prompt assets should support the flow, not be the sole enforcement mechanism

### Generic Core + Domain Overlays

- define one generic guided flow model first
- domain-specific behavior should be expressed as overlays or recipe/domain
  policies, not separate unrelated orchestration systems
- first-class initial domain profiles for this wave:
  - `generic`
  - `creature`
  - `building`
- the generic profile should stay useful for tasks that do not clearly match a
  specialized domain profile

### Step Gating

- visibility should be able to depend on flow step, not only phase
- later-stage families should remain hidden or blocked until earlier required
  steps are complete
- compare/iterate and inspect/validate can become step gates where that is
  product-appropriate
- gating should stay bounded and explainable; do not create silent refusal
  paths without structured guidance

### Prompt Bundle Contract

- the server should be able to state which prompt assets are required or
  strongly preferred for the current guided flow
- domain profiles may require different prompt bundles
- clients that can use prompts should get explicit machine-readable prompt
  recommendations for the current step, not only generic catalog suggestions

### Loop Integration

- the current compare/iterate/truth/planner outputs should be inputs to flow
  transitions, not parallel advisory systems
- if a flow step requires a checkpoint iteration before continuing, the server
  should say so explicitly
- if a domain profile requires spatial graph/view checks before a later stage,
  the server should encode that requirement explicitly

## Scope

This umbrella covers:

- a typed `guided_flow_state` contract and session model
- deterministic domain-profile selection for guided sessions
- step-gated visibility and execution policy on `llm-guided`
- prompt-bundle delivery and recommendation rules per flow/domain/step
- regression coverage and docs for the server-driven flow model

This umbrella does **not** cover:

- replacing the current workflow/router architecture with a new generalized
  workflow engine
- hardcoding one special squirrel-only build mode as the only delivery
  mechanism
- turning every guided action into a hard-blocked wizard with no recovery or
  escape hatches
- adding broad new domain capability families themselves; this task governs
  flow, not the full implementation of every future domain tool

## Acceptance Criteria

- the server has one explicit machine-readable `guided_flow_state` concept
  persisted in session state
- `llm-guided` flow selection can choose between at least:
  - `generic`
  - `creature`
  - `building`
- visibility and/or `call_tool(...)` policy can enforce step-appropriate
  behavior instead of relying only on advisory prose
- prompt bundles/recommendations are tied to the current flow/domain/step
- docs and regression coverage make the server-driven flow model explicit

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/router/application/session_phase_hints.py`
- `README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/`
- `tests/e2e/router/`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-150-01](./TASK-150-01_Guided_Flow_State_Contract_And_Session_Model.md) | Define the generic server-owned guided flow state contract and persist it in session state |
| 2 | [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md) | Add deterministic domain-profile selection and define how `generic`, `creature`, and `building` overlays alter the flow |
| 3 | [TASK-150-03](./TASK-150-03_Step_Gated_Visibility_And_Execution_Policy.md) | Make visibility and execution behavior depend on flow step instead of only coarse phase |
| 4 | [TASK-150-04](./TASK-150-04_Prompt_Bundle_Delivery_And_Flow_Aligned_Recommendations.md) | Turn prompts into an explicit server-owned flow contract instead of optional side knowledge |
| 5 | [TASK-150-05](./TASK-150-05_Regression_Pack_And_Docs_For_Server_Driven_Guided_Flows.md) | Lock the server-driven flow model in with tests, docs, and troubleshooting guidance |

## Status / Board Update

- promoted as a new board-level follow-on because guided runtime quality now
  depends less on adding more tools and more on making the server own the
  sequencing contract the model follows
