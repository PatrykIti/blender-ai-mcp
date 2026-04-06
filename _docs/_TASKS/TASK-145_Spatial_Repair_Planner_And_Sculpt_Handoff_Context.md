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
- current staged compare/iterate loop

This follow-on should therefore strengthen the planner and sculpt handoff
contracts, not replace them with a free-form agent planner.

It should also preserve the current product model:

- small guided-facing default exposure
- bounded machine-readable handoff
- richer planner detail available on demand when the current goal/phase
  justifies it

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
- use the new spatial-state/view-state modules from `TASK-143` and `TASK-144`
  as inputs to better planner outputs
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

## Dependency Policy

- if a new tool, grouped surface, or bounded macro is needed to make the
  planner or sculpt handoff materially clearer, that is acceptable
- but planner-quality improvements should be achieved first through better
  contracts and policy, not through a large dependency wave
- any new planner-related tools should remain bounded and should not
  automatically become bootstrap-visible on `llm-guided`
- `LLM_GUIDE_V2.md` is the supporting design document for these choices; this
  umbrella remains the canonical delivery direction

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

- the planner and sculpt-handoff context should be retrievable as explicit
  bounded products instead of being hidden as another large default payload
- the guided loop may reference or call planner artifacts when needed, but the
  planner module itself should remain conceptually separate from the baseline
  compare/iterate contract
- if a lightweight planner summary is later added inline to loop responses, it
  should be a compact derivative of the planner module rather than the full
  planner context

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

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `server/router/infrastructure/tools_metadata/reference/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- focused sculpt-handoff regression coverage in `tests/e2e/tools/sculpt/`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Execution Structure

Planned execution slices:

- Slice A: repair-planner payload, family-selection policy, and lightweight delivery model
- Slice B: goal-aware disclosure plus sculpt-handoff context and precondition model
- Slice C: guided-loop adoption, regression pack, and docs

## Status / Board Update

- promote this as a board-level umbrella for planner-quality guided correction
  and safer sculpt handoff
- keep board tracking on `_docs/_TASKS/README.md` until planner, sculpt
  preconditions, docs, and regressions are aligned
