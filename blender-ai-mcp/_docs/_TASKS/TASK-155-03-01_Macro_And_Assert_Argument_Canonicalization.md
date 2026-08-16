# TASK-155-03-01: Macro And Assert Argument Canonicalization

**Parent:** [TASK-155-03](./TASK-155-03_Guided_Tool_UX_And_Response_Budget.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Reduce raw Pydantic validation noise for natural guided mistakes such as
`reference_object` on `macro_attach_part_to_surface`, `surface_axis="+Z"`, or
`scene_assert_proportion(axis="Z")`.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/compat.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/scene/macro_attach_part_to_surface.json`
- `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`

## Acceptance Criteria

- `reference_object` can be safely canonicalized to `surface_object` for
  `macro_attach_part_to_surface(...)`, or the error message tells the model the
  exact replacement
- `surface_axis="+Z"` canonicalizes to `surface_axis="Z"` plus positive side
  semantics when safe
- proportion assertion argument mistakes return guided actionable errors or
  safe aliases without changing the product contract silently
- raw schema errors are still available for debug/internal surfaces where
  appropriate

## Tests To Add/Update

- Unit:
  - add macro alias/canonicalization tests in
    `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
  - add assertion argument UX tests in
    `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
  - add structured-delivery expectations in
    `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- E2E:
  - extend `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
    for `+Z`/side canonicalization if implemented at the public tool layer

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- normalized `reference_object` / signed-axis macro slips and the
  `scene_assert_proportion(axis=...)` alias on the guided call proxy path
