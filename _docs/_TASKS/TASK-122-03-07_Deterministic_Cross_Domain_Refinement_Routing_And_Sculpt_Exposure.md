# TASK-122-03-07: Deterministic Cross-Domain Refinement Routing and Sculpt Exposure

**Follow-on After:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Board Tracking:** Standalone hybrid-loop follow-on kept open after
`TASK-122-03` and `TASK-122` were closed. `_docs/_TASKS/README.md` tracks it
as its own open item while the historical numbering is preserved for
continuity.  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The first two leaves are now complete. The hybrid loop has
an explicit refinement taxonomy and a deterministic `refinement_route`
selector, but guided-surface sculpt exposure policy and broader cross-domain
regression/prompting work remain open.

## Objective

Teach the hybrid correction loop to choose the **right refinement family**
deterministically across many Blender domains, instead of biasing almost
everything toward mesh/modeling primitives and never surfacing sculpt when
sculpt would be the correct bounded next step.

This follow-on is about **routing and exposure policy**, not about making
sculpt universal by default.

The target is a deterministic system that can work across:

- buildings / architectural massing
- hard-surface props and electronics
- garments and soft-surface accessories
- organs and other biological forms
- characters and creature anatomy
- stylized low-poly assembled models

## Business Problem

Current hybrid-loop behavior is still skewed:

- it is strong at mesh/modeling/macro correction for assembled low-poly and
  hard-surface-style workflows
- it can now emit ranked `correction_candidates`, truth-driven escalation, and
  bounded macro suggestions
- but on the normal `llm-guided` surface it still does **not** have a strong,
  deterministic path for deciding:
  - when mesh/modeling remains the best family
  - when bounded macros remain the best family
  - when deterministic sculpt-region tools should become the next recommended
    family

That creates two product risks:

1. **Under-suggestion risk**

- the system can keep pushing mesh/modeling fixes on problems that are really
  local shape-refinement problems
- this especially hurts creatures, characters, organs, cloth-like forms, and
  other soft/organic silhouettes

2. **Over-exposure risk**

- if sculpt is simply exposed everywhere, the LLM can overuse it on hard-
  surface, low-poly, or assembly problems where sculpt is the wrong tool
- that would reduce determinism, increase geometry noise, and weaken the
  product's bounded-correction story

The business requirement is therefore:

- **automatic**
- **deterministic**
- **cross-domain**
- **bounded**

The system should not ask the model to invent a refinement family ad hoc.
It should infer and gate that choice from explicit rules plus bounded signals.

## Product Direction

The intended product behavior is:

1. hybrid loop gathers vision, truth, and correction candidates
2. system classifies the current correction need into a refinement family
3. guided surfaces expose or recommend only the family/tools that are safe and
   appropriate for that case
4. the LLM receives a bounded next-step path:
   - stay on macro/modeling/mesh
   - or unlock a narrow deterministic sculpt path
   - or stop and inspect

The long-term product contract should be:

- hard-surface / assembly / low-poly proportion issues should still prefer:
  - macros
  - modeling
  - mesh
- organic or local-form refinement issues should be able to prefer:
  - deterministic sculpt-region tools
- this choice should be explainable from the payload, not hidden in prompt-only
  guesswork

## Scope

This follow-on covers:

- deterministic refinement-family selection
- sculpt recommendation / exposure policy on `llm-guided`
- cross-domain rules for when sculpt is appropriate
- prompt and regression guidance for those rules

This follow-on does **not** mean:

- exposing the whole sculpt family unconditionally on the guided build surface
- reverting to UI-brush/event-style sculpt workflows
- making sculpt the default answer for all shape mismatch

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/application/tool_handlers/router_handler.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/e2e/vision/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- hybrid-loop output can determine a bounded refinement-family direction from
  explicit rules, not ad hoc prose
- deterministic sculpt-region tools can be recommended or exposed when the
  current correction need is local organic/soft-form refinement
- hard-surface, low-poly, and assembly-oriented cases do not regress into
  overusing sculpt
- the policy works in a general cross-domain way rather than being hand-tuned
  only for squirrels or only for one content type
- docs and regression coverage make the policy understandable and repeatable

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if guided-surface exposure changes
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/e2e/vision/` for hybrid-loop routing/eval coverage when runtime policy changes

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this follow-on changes refinement-
  family routing, sculpt exposure policy, or cross-domain hybrid-loop guidance

## Status / Board Update

- keep this task open as a standalone follow-on after the closed `TASK-122-03`
  subtree
- if it is completed, update `_docs/_TASKS/README.md` and refresh the closed
  parent follow-on notes

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-03-07-01](./TASK-122-03-07-01_Refinement_Taxonomy_And_Domain_Boundaries.md) | Define one cross-domain taxonomy for refinement families and hard/soft/organic boundaries |
| 2 | [TASK-122-03-07-02](./TASK-122-03-07-02_Deterministic_Refinement_Family_Selector.md) | Turn hybrid-loop signals into a deterministic refinement-family selector |
| 3 | [TASK-122-03-07-03](./TASK-122-03-07-03_Guided_Surface_Sculpt_Exposure_And_Handoff.md) | Decide how sculpt becomes visible or recommended on guided surfaces without overexposure |
| 4 | [TASK-122-03-07-04](./TASK-122-03-07-04_Cross_Domain_Regression_Pack_And_Prompting.md) | Validate the policy across buildings, electronics, garments, organs, characters, and animals |
