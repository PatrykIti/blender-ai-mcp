# TASK-145: Spatial Repair Planner and Sculpt Handoff Context

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime UX / Spatial Repair Planning
**Estimated Effort:** Large
**Dependencies:** TASK-122-03-07, TASK-143, TASK-144
**Follow-on After:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md)

## Objective

Turn the current guided loop from "ranked findings plus loose next-step hints"
into a stronger spatial repair planner that can:

- choose the right bounded repair family from typed spatial state
- explain why that family is appropriate
- expose when sculpt is appropriate, and when it is still too early

The end goal is a better LLM operator that understands not only **what is
wrong**, but also **what kind of correction is now justified**.

## Business Problem

The repo already has:

- `truth_followup`
- `correction_candidates`
- `refinement_route`
- `refinement_handoff`

That is already much better than a prompt-only loop, but it is still not the
same as a real spatial repair planner.

Today the model can still struggle with questions like:

- is this a macro repair, a mesh/local-form issue, or a sculpt problem?
- should I fix support/contact first, or shape first?
- is the target region visible and stable enough for sculpt?
- is sculpt appropriate on this scope, or would that just hide a relation error?

Without a stronger planner surface:

- sculpt can be reached too early or too broadly
- the model can still choose the wrong family from partially overlapping hints
- bounded handoff remains more "best effort" than "explicit execution contract"

There is also an important product constraint here:

- `llm-guided` must stay small and legible
- the planner layer must not turn into another broad default tool family
- the current guided loop contracts are already dense, so planner quality
  should not be achieved by simply attaching a large new payload everywhere

This umbrella must improve planner quality and sculpt timing without
reintroducing the large-catalog or heavy-payload failure modes that `llm-guided`
was designed to avoid.

## Current Runtime Baseline

The repo already has the key ingredients this umbrella should refine:

- deterministic `refinement_route`
- bounded `refinement_handoff`
- current `macro` / `modeling_mesh` / `sculpt_region` family vocabulary
- typed `correction_candidates` and truth evidence
- typed `scene_scope_graph`, `scene_relation_graph`, and
  `scene_view_diagnostics` artifacts from the completed TASK-143 / TASK-144
  work
- current staged compare/iterate loop

This follow-on should therefore strengthen the planner and sculpt handoff
contracts, not replace them with a free-form agent planner.

It should also preserve the current product model:

- small guided-facing default exposure
- bounded machine-readable handoff
- richer planner detail available on demand when the current goal/phase
  justifies it

## Current Code Alignment

The real implementation baseline for this umbrella already lives in the staged
reference loop:

- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` assemble the current compare /
  iterate payload
- `_build_correction_candidates(...)` merges truth, macro, and vision evidence
- `_select_refinement_route(...)` emits the current bounded family selector
- `_build_refinement_handoff(...)` emits the current recommendation-only
  sculpt handoff
- `ReferenceHybridBudgetControlContract` already guards payload size for
  compare / iterate responses
- `build_visibility_rules(...)` and `build_visibility_diagnostics(...)`
  currently keep sculpt hidden on the default `llm-guided` surface
- prompt docs already mention `refinement_route` / `refinement_handoff`, but
  current planner-first operating guidance is still partial and inconsistent

That means TASK-145 should evolve existing compare / iterate contracts and
guided-surface policy into a stronger planner layer. It should not introduce a
second autonomous workflow engine beside the current reference loop.

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit spatial repair-planner layer on top of the current guided loop
- stronger family-selection reasoning grounded in scope, relation, and
  view-space state
- a safer and more useful sculpt handoff story
- less accidental sculpt usage on problems that are still really:
  - attachment
  - support
  - overlap
  - proportion
  - framing

## Implementation Direction

This umbrella should be implemented primarily as a **contract and policy
improvement** over the current guided loop, not as a geometry-library wave.

The intended posture is:

- start from the repo's current planner and handoff substrates:
  - `truth_followup`
  - `correction_candidates`
  - `refinement_route`
  - `refinement_handoff`
  - current visibility shaping and guided prompts
- use the existing spatial-state/view-state modules from `TASK-143` and
  `TASK-144` as inputs to better planner outputs
- keep the first version focused on:
  - typed planner payloads
  - better family selection
  - better sculpt gating
  - better guided adoption

For the first wave, the implementation should therefore be framed as:

- **v1 baseline**:
  - existing planner/handoff contracts plus current guided loop
- **no heavy-library requirement for v1**:
  - most value here is in contracts, policy, disclosure, and regression scope
- **later extensions only if justified**:
  - richer planner modules that depend on additional spatial graph inputs

This umbrella should not be blocked on adding new heavy geometry libraries.

## Architecture Ownership Boundary

TASK-145 should extend the existing staged reference loop, but it should not
make `server/adapters/mcp/areas/reference.py` the permanent owner of growing
planner policy.

The intended ownership split is:

- `server/adapters/mcp/contracts/reference.py` owns the response contracts and
  typed planner/handoff shapes exposed through MCP.
- `server/adapters/mcp/areas/reference.py` remains the stage-checkpoint
  assembler: it gathers the current evidence, calls the planner policy, and
  attaches the bounded result.
- `server/application/services/repair_planner.py` or an equivalent
  framework-free policy helper should own non-trivial family-selection,
  blocker, and sculpt-suppression rules once the rules outgrow the current
  private helper shape.
- Any application-layer planner helper must preserve Clean Architecture
  direction. It should expose framework-free DTOs or typed policy results; it
  must not import MCP adapter contracts. `server/adapters/mcp/areas/reference.py`
  remains responsible for translating planner results into `Reference*Contract`
  payloads.
- `server/application/services/spatial_graph.py` and scene graph contracts
  remain the owners of spatial truth facts; TASK-145 consumes their evidence
  instead of recomputing scene truth.
- View/framing truth should continue to come from the existing
  `SceneToolHandler.get_view_diagnostics(...)` and `scene_view_diagnostics(...)`
  path. The planner consumes those typed results; it does not create a new
  camera or visibility truth pass.
- FastMCP visibility/search layers expose or hide bounded artifacts; they do
  not become the planner's reasoning authority.

Do not introduce a second autonomous routing loop, a LaBSE-backed planner, or
an independent state machine. Any separately retrievable planner detail must
be a read-only derivative of the current compare/iterate state and the same
policy result that the compact stage response uses.

## Dependency Policy

- if a new tool, grouped surface, or bounded macro is needed to make the
  planner or sculpt handoff materially clearer, that is acceptable
- but planner-quality improvements should be achieved first through better
  contracts and policy, not through a large dependency wave
- any new planner-related tools should remain bounded and should not
  automatically become bootstrap-visible on `llm-guided`
- `LLM_GUIDE_V2.md` is the supporting design document for these choices; this
  umbrella remains the canonical delivery direction

## Coordination With TASK-157

TASK-145 feeds TASK-157 but does not implement quality-gate ownership.

- TASK-145 may emit local planner blockers, sculpt suppression reasons, and
  bounded next-family recommendations.
- TASK-157 owns gate-plan declaration, gate status, completion blocking, and
  guided runtime cadence for required quality gates.
- TASK-145 wording should avoid treating planner preconditions as final gate
  pass/fail status. The planner can say "sculpt is blocked by unresolved
  relation evidence"; TASK-157 decides whether an active required gate blocks
  final completion.

## Product Design Requirements

### Lightweight Guided Exposure

- keep the default `llm-guided` visible surface small
- do not expose a broad planner-specific family of new tools on bootstrap by
  default
- prefer one small number of planner-facing entry artifacts or modules
- planner detail should expand on demand instead of becoming a mandatory
  default payload on every guided step
- new atomics, grouped tools, or bounded macros are allowed when they provide:
  - one stable planner-relevant spatial fact
  - or one bounded planner-relevant corrective action
  but those building blocks must not automatically become default
  bootstrap-visible on `llm-guided`

### Goal-Aware Planner Disclosure

- planner output should adapt to the active guided goal and shaped handoff
- example:
  - creature work may need attachment/support-first gating before sculpt
  - architecture or landmark work may need framing/symmetry/proportion-first
    gating before local-form refinement
- goal-aware shaping should remain deterministic and metadata-driven where
  possible

### Delivery Model

- the planner and sculpt-handoff context should be exposed as explicit bounded
  products of the existing stage-checkpoint state instead of hidden inside a
  large default payload
- the guided loop may attach a compact planner summary inline, but the summary
  must be derived from the same planner policy used for any richer detail path
- any richer planner detail must be opt-in/read-only and must not start a
  detached secondary workflow, routing loop, or persistence model

### Repair Planner

- planner output should remain bounded, typed, and machine-readable
- planner reasoning should combine:
  - current scope
  - current relation state
  - current visibility/view-space state
  - current truth evidence
- planner output should answer:
  - what family should own the next step?
  - what object/scope should that family act on?
  - what preconditions still block that family?

### Sculpt Handoff Context

- sculpt should remain recommendation-only until the current state justifies it
- the handoff should make explicit:
  - target object
  - intended region/local-form reason
  - required visibility / framing preconditions
  - required relation-state preconditions
  - required proportion-stability preconditions
- the handoff should discourage broad blind sculpt edits on unresolved
  attachment/support failures

### Guided Adoption

- the planner should plug into the current compare/iterate loop instead of
  becoming a detached secondary workflow
- prompt/docs guidance should teach the model to read planner output before
  jumping to lower-level tools
- default loop payload growth should stay tightly bounded; prefer separate
  planner access over unconditional payload expansion

## Scope

This umbrella covers:

- strengthening the current repair-planner payloads
- strengthening family-selection policy from spatial state
- one lightweight guided-facing delivery model for planner and sculpt-handoff
  context
- goal-aware and phase-aware disclosure for planner context on `llm-guided`
- explicit sculpt-handoff context and preconditions
- guided-loop adoption, docs, and regressions for the planner path

This umbrella does **not** cover:

- adding brand-new sculpt tool families
- turning the planner into an unrestricted autonomous workflow engine
- making vision the authority for planner decisions
- replacing the current macro and mesh families
- exposing a broad new default planner family on `llm-guided` bootstrap
- turning `reference_compare_*` / `reference_iterate_*` into the default home
  for a full heavyweight planner payload

## Acceptance Criteria

- the repo has one stronger machine-readable repair-planner surface for guided
  spatial correction
- planner output makes family selection more explicit than today's loose hint
  combination
- the delivery model keeps `llm-guided` small:
  - no large new bootstrap-visible planner family
  - no default heavyweight planner embedding into the current stage-checkpoint
    payloads
- sculpt handoff is explicitly gated by spatial state and preconditions
- planner and sculpt-handoff detail can adapt to the active guided goal / phase
  instead of staying one fixed heavy payload for every domain
- guided docs teach planner-first interpretation before broader free-form edits
- focused regression coverage protects the planner and sculpt handoff contract

## Repository Touchpoint Table

| Path / Module | Expected Ownership | Why In Scope |
|---------------|--------------------|--------------|
| `server/adapters/mcp/contracts/reference.py` | Response contract owner | Add bounded planner / handoff fields without inventing a second response family. |
| `server/application/services/repair_planner.py` or equivalent helper | Planner policy owner | Keep non-trivial family-selection and blocker rules outside thin MCP adapters while returning framework-free DTOs/results, not MCP adapter contracts. |
| `server/adapters/mcp/areas/reference.py` | Stage response assembler | Reuse `truth_followup`, `correction_candidates`, `budget_control`, `refinement_route`, and `refinement_handoff` in compare / iterate. |
| `server/adapters/mcp/contracts/scene.py` | Spatial evidence contract owner | Consume existing scope, relation, and view contracts as evidence instead of duplicating truth. |
| `server/adapters/mcp/areas/scene.py` | Spatial read-tool adapter | Preserve current `scene_scope_graph`, `scene_relation_graph`, and `scene_view_diagnostics` behavior. |
| `server/application/services/spatial_graph.py` | Spatial truth service | Remains the source for scope/relation facts used by planner policy. |
| `server/application/tool_handlers/scene_handler.py` | View diagnostics application owner | Preserve the RPC-backed `get_view_diagnostics(...)` path as the runtime source for view/framing facts. |
| `server/adapters/mcp/areas/sculpt.py` | Sculpt tool surface owner | Keep recommended sculpt tools aligned with real deterministic region tool signatures. |
| `server/adapters/mcp/transforms/visibility_policy.py` | Runtime visibility owner | Keep planner/sculpt exposure phase-aware and prevent broad bootstrap visibility. |
| `server/adapters/mcp/guided_mode.py` | Guided profile owner | Keep `llm-guided` small while allowing bounded handoff-driven discovery. |
| `server/adapters/mcp/platform/capability_manifest.py` | Public capability inventory | Keep public metadata aligned with any bounded planner/sculpt capability exposure. |
| `server/adapters/mcp/prompts/prompt_catalog.py` | Prompt ordering owner | Teach planner-first interpretation without exposing hidden tools. |
| `server/router/infrastructure/tools_metadata/scene/` | Search metadata for evidence tools | Keep scope/relation/view discovery aligned with planner evidence needs. |
| `server/router/infrastructure/tools_metadata/sculpt/` | Search metadata for sculpt tools | Limit guided sculpt discovery to the bounded deterministic subset. |
| `server/router/infrastructure/tools_metadata/reference/` | Search metadata for reference loop | Surface planner semantics through existing reference-stage discovery. |
| `tests/unit/adapters/mcp/test_reference_images.py` | Reference-loop unit coverage | Assert candidates, route, handoff, budget, and planner policy behavior. |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py` | Contract shape coverage | Lock compact/rich planner payload parity. |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Visibility policy coverage | Guard against broad planner/sculpt overexposure. |
| `tests/unit/adapters/mcp/test_guided_mode.py` | Guided profile coverage | Prove planner/sculpt handoff does not bloat default guided profile. |
| `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py` | Catalog-size regression coverage | Keep guided build/inspect footprints bounded. |
| `tests/unit/adapters/mcp/test_search_surface.py` | Search/discovery coverage | Prove bounded artifacts are discoverable only when appropriate. |
| `tests/unit/adapters/mcp/test_prompt_catalog.py` | Prompt catalog coverage | Prove planner-first prompt ordering. |
| `tests/unit/adapters/mcp/test_public_surface_docs.py` | Docs/public contract coverage | Keep public docs aligned with shipped surface. |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | Stage-loop E2E coverage | Exercise truth-driven assembly handoff and compact planner payload behavior. |
| `tests/e2e/vision/test_reference_guided_creature_comparison.py` | Guided creature E2E coverage | Prove planner behavior in a realistic guided reconstruction scenario. |
| `tests/e2e/tools/sculpt/test_sculpt_tools.py` | Blender sculpt E2E coverage | Prove recommended sculpt subset matches real Blender-side behavior. |
| `_docs/LLM_GUIDE_V2.md` | Operator design guide | Keep planner-first operating model documented. |
| `_docs/_PROMPTS/README.md` | Prompt surface docs | Keep client prompt guidance aligned with planner adoption. |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Creature prompt docs | Show planner/sculpt handoff order for creature runs. |
| `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md` | Regression/eval docs | Track family-selection evidence and scenarios. |
| `_docs/_VISION/README.md` | Vision loop docs | Keep vision as advisory evidence, not planner truth authority. |

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md) | Turn the current `refinement_route` baseline into a real bounded repair-planner contract with explicit payload shape, provenance, and family-selection policy |
| 2 | [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md) | Upgrade the current recommendation-only sculpt handoff into a typed local-context / precondition model without widening sculpt into a default family |
| 3 | [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md) | Deliver planner-first adoption on `llm-guided` through visibility, prompts, docs, and regression coverage while keeping the surface small |

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Test Matrix

| Layer | Tests To Add / Update |
|-------|------------------------|
| Unit contracts | `tests/unit/adapters/mcp/test_contract_payload_parity.py` for compact/rich planner and handoff shapes. |
| Unit reference loop | `tests/unit/adapters/mcp/test_reference_images.py` for correction candidates, route policy, planner summary, budget trimming, and sculpt blockers. |
| Unit visibility/search | `tests/unit/adapters/mcp/test_visibility_policy.py`, `test_guided_mode.py`, `test_guided_surface_benchmarks.py`, and `test_search_surface.py` for phase-aware bounded exposure. |
| Unit prompt/docs | `tests/unit/adapters/mcp/test_prompt_catalog.py` and `test_public_surface_docs.py` for planner-first wording and public contract alignment. |
| Integration/router | Existing router metadata/search validation plus focused guided visibility refresh coverage when planner/handoff state changes native MCP visibility. |
| E2E / Blender | `tests/e2e/vision/test_reference_stage_truth_handoff.py`, `tests/e2e/vision/test_reference_guided_creature_comparison.py`, and focused sculpt-handoff coverage in `tests/e2e/tools/sculpt/`. |
| Docs / regression fixtures | `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`, `_docs/_VISION/README.md`, `_docs/_PROMPTS/*`, and `_docs/_TESTS/README.md` when test architecture changes. |

## Validation Commands

- Unit reference loop: `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- Visibility/search/prompt lane: `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- E2E/Blender lane when runtime behavior changes: `poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_guided_creature_comparison.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q`
- Preflight docs/code hygiene: `git diff --check`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Status / Board Update

- `_docs/_TASKS/README.md` already tracks TASK-145 as a promoted open
  board-level item.
- Child/subtask documentation changes do not require a board-count change while
  the promoted parent remains `⏳ To Do`.
- When this umbrella closes, or if a follow-on remains open after closure,
  update `_docs/_TASKS/README.md`, parent/child statuses, docs, changelog, and
  validation notes in the same branch.
