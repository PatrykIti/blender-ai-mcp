# TASK-122-03-07-03: Guided Surface Sculpt Exposure and Handoff

**Parent:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Implemented the safer first product shape: recommendation-only sculpt handoff. Hybrid compare / iterate responses now expose `refinement_handoff`, which can recommend a bounded deterministic sculpt-region subset when `refinement_route` selects `sculpt_region`. The normal `llm-guided` build surface still does not auto-expose sculpt tools, so hard-surface and low-poly assembly flows are not flooded with sculpt by default.

## Objective

Decide how deterministic sculpt tools become visible or recommended on
`llm-guided` without exposing the whole sculpt family by default.

## Business Problem

The repo already has deterministic sculpt-region tools, but they are not part
of the normal guided build path. That is safe, but it also means the system can
miss a better refinement family for soft/organic cases.

The product needs a middle ground:

- sculpt should stay hidden by default
- but the system should be able to recommend or expose a narrow sculpt path
  when the selector says sculpt is the correct family

## Technical Direction

Evaluate and document one or both of these product shapes:

1. **recommendation-only handoff**

- loop emits a refinement-family recommendation and explicit sculpt candidates
- the surface still does not expose sculpt automatically

2. **progressive guided unlock**

- a bounded subset of deterministic sculpt tools becomes visible only when the
  current hybrid-loop result crosses the sculpt gate

Scope of possible sculpt tools should remain narrow, for example:

- `sculpt_deform_region`
- `sculpt_smooth_region`
- `sculpt_inflate_region`
- `sculpt_pinch_region`
- maybe `sculpt_crease_region`

Do not reopen brush/event-style sculpt setup tools.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- guided-surface sculpt behavior is explicit, bounded, and documented
- only deterministic sculpt-region tools are eligible for guided exposure
- hard-surface and low-poly assembly flows do not get sculpt spam by default

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- this leaf is closed
- the parent follow-on remains in progress for broader cross-domain regression
  and prompting work
