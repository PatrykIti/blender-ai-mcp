# TASK-144-02-01: Visibility Verdict Taxonomy And Report Schema

**Parent:** [TASK-144-02](./TASK-144-02_Visibility_Report_Contract_And_Read_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-144-01-01](./TASK-144-01-01_View_Query_Selector_And_Projection_Contract.md)

**Completion Summary:** Completed on 2026-04-07. Finalized the bounded schema
and verdict vocabulary for view-space diagnostics: the shipped contract now
distinguishes `visible`, `partially_visible`, `fully_occluded`,
`outside_frame`, and `unavailable` without blurring those view-space states
with truth-space contact or attachment semantics.

## Objective

Define one bounded typed schema for reporting view-space visibility diagnostics.

The schema must make it explicit:

- which object/scope the verdict applies to
- whether it is visible, partially visible, occluded, or off-frame
- what compact projection/frame evidence supports that verdict
- whether the report is about a named camera or the current live viewport

## Implementation Direction

- treat this as a report schema and verdict vocabulary leaf, not a runtime leaf
- keep visibility verdicts distinct from raw projection facts and from
  truth-space attachment/contact semantics
- include provenance and availability fields so downstream code can tell when a
  report is degraded or unavailable
- keep the payload compact enough for on-demand guided use

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Acceptance Criteria

- the visibility report schema defines explicit verdict vocabulary for
  visible, partially visible, occluded, and off-frame states
- the schema carries compact supporting evidence such as projected extent,
  center, and frame coverage
- the schema clearly distinguishes view-space reporting from truth-space
  correctness
- the response remains bounded and machine-readable

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_contracts.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with the TASK-144 visibility wave
- tracked as completed through the closed parent/subtask state
