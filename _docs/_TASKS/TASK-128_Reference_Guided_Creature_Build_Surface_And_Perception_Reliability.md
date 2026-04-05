# TASK-128: Reference-Guided Creature Build Surface and Perception Reliability

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Category:** Product Reliability / Guided Creature UX
**Estimated Effort:** Large
**Dependencies:** TASK-120, TASK-121, TASK-122, TASK-124

## Objective

Make `llm-guided` creature building materially more reliable by tightening the
prompted/build surface first, then adding deterministic silhouette-driven
feedback, and only after that evaluating an optional part-segmentation sidecar.

## Business Problem

The current repo already has a strong hybrid-loop foundation for reference
comparison, truth follow-up, and bounded macros, but creature work still hits a
quality ceiling in practice:

- the best creature-specific prompt exists in docs, but is not exposed as a
  curated MCP prompt asset
- `guided_manual_build` remains broad and somewhat macro-biased for organic
  blockout work
- tool discovery/search metadata does not sufficiently bias the model toward
  creature-relevant blockout tools and search phrases
- current vision output is still too prose-heavy when shape profiling needs
  deterministic contour and ratio signals

The result is predictable: the model spends too much effort rediscovering tools
and not enough effort making correct shape decisions.

## Current Runtime Baseline

The audit baseline for this umbrella is no longer "no guided creature path at
all". The repo already has:

- `llm-guided` search-first bootstrap plus prompt bridge tools
- typed `guided_handoff` and `guided_reference_readiness`
- staged reference compare / iterate tools with bounded loop semantics
- truth-first hybrid loop outputs such as `truth_followup`,
  `correction_candidates`, `refinement_route`, and `refinement_handoff`

That baseline matters because Slice A/B/C should extend the current product
surface, not redesign the platform work that already shipped under earlier
tasks.

## Current Drift To Resolve

The remaining gap is now mostly one of shaped creature UX and task/runtime
alignment:

- the best creature prompt still exists as docs content instead of a real MCP
  prompt asset
- `recommended_prompts` is still phase/profile-aware only
- `guided_manual_build` remains broader and more macro-first than the desired
  creature blockout recipe
- search metadata still under-ranks creature blockout queries
- Slice B metrics / typed `action_hints` are still not shipped
- Slice C sidecar work is still planning-only and must remain explicitly
  optional

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one generic creature-build prompt path instead of squirrel-only operator lore
- clearer low-poly and mid-poly creature handoff/tool recipes on
  `llm-guided`
- better discovery/search bias for ears, snout, tail, silhouette, and
  proportion work
- a deterministic silhouette-analysis layer that feeds typed corrective hints
- a later, optional path for part-aware segmentation without forcing a heavy
  runtime on the default product path

## Scope

This umbrella covers:

- prompt-catalog and recommendation improvements for generic creature work
- domain-aware guided handoff/tool recipe narrowing for creature blockout
- metadata/search-hint enrichment for creature modeling tools
- deterministic silhouette/per-part measurement planning
- optional part-segmentation sidecar planning as a later stage

This umbrella does **not** cover:

- making vision the source of scene truth
- forcing SAM 3 or any GPU-heavy model into the default runtime
- reopening the full public surface for unrestricted tool exposure
- adding squirrel-specific public prompts as the default strategy

## Acceptance Criteria

- the repo has one promoted generic creature-build prompt path for
  `llm-guided`
- creature-oriented guided handoff narrows tool choice instead of relying on
  broad generic build exposure
- discovery/search hints materially improve ranking for creature blockout
  requests
- the next perception layer is defined as deterministic silhouette analysis
  before heavyweight segmentation
- any future segmentation module remains optional and boundary-safe
- task files, docs, runtime behavior, and regression coverage describe the same
  shipped public story; docs-only exposure does not count as delivered product
  behavior

## Repository Touchpoints

- `server/adapters/mcp/prompts/`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/router/infrastructure/tools_metadata/`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`
- `_docs/_PROMPTS/`
- `_docs/_VISION/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- task board/task files under `_docs/_TASKS/`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/router/`
- `tests/e2e/vision/` as later slices land

## Changelog Impact

- add a `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
  when a meaningful implementation slice under this umbrella is completed

## Status / Board Update

- keep this umbrella promoted on `_docs/_TASKS/README.md` while Slice A/B/C are
  open
- keep [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
  promoted as the active execution slice until the prompt, handoff, and search
  drifts identified by the audit are closed
- promote each execution slice on the board only when it is ready for actual
  implementation sequencing

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md) | Expose the right generic creature prompt, narrow the guided tool recipe, and bias discovery toward creature blockout work |
| 2 | [TASK-128-02](./TASK-128-02_Deterministic_Silhouette_Analysis_And_Typed_Action_Hints.md) | Add deterministic silhouette analysis and typed action hints before introducing heavier segmentation |
| 3 | [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md) | Evaluate an optional part-segmentation sidecar that stays outside the default runtime path |
