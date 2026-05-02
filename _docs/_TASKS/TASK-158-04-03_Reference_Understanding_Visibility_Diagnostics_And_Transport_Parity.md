# TASK-158-04-03: Reference Understanding Visibility Diagnostics And Transport Parity

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Parent:** [TASK-158-04](./TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md)
**Category:** Guided Runtime / Reference Understanding Visibility
**Estimated Effort:** Small

## Objective

Expose bounded reference-understanding hints only through the existing guided
visibility, router diagnostics, search, and transport parity seams, without
adding a public `reference_understand` or `router_apply_reference_strategy`
tool.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/transforms/visibility_policy.py` | Consume unresolved gate state plus bounded reference-understanding hints when visibility really changes |
| `server/adapters/mcp/guided_mode.py` | Keep guided visibility assembly aligned with any new hint fields |
| `server/adapters/mcp/areas/router.py` | Keep `router_get_status(...)` diagnostics aligned when hint fields become public there |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Verify bounded tool exposure still resolves through existing guided families |
| `tests/unit/adapters/mcp/test_guided_mode.py` | Verify guided visibility assembly remains deterministic |
| `tests/unit/adapters/mcp/test_router_elicitation.py` | Verify diagnostics and public router status stay aligned |
| `tests/unit/adapters/mcp/test_search_surface.py` | Verify search/discovery lanes do not drift into a parallel surface |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | Verify stdio/Streamable HTTP parity when hint fields become public |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | Verify transport-visible gate payloads stay aligned if linkage reaches public status surfaces |

## Implementation Notes

- Do not add a public `reference_understand` or
  `router_apply_reference_strategy` tool.
- Route hint-driven behavior through existing guided family gating and
  diagnostics. If no public surface changes, keep the work unit-test-only.
- Only add transport parity tests when the hint/linkage fields become visible
  on stdio or Streamable HTTP public payloads.
- Search/discovery changes are optional. If no search hints or keywords are
  added, do not widen metadata or search tests just to satisfy the task title.

## Runtime / Security Contract Notes

- Visibility level: guided/internal by default; any public diagnostic field
  requires exact contract and parity coverage.
- Read-only behavior: this slice must not mutate Blender scene state.
- Side effects: no implicit provider call, sidecar activation, model download,
  or hidden router execution.

## Tests To Add / Update

- Extend `tests/unit/adapters/mcp/test_visibility_policy.py` and
  `tests/unit/adapters/mcp/test_guided_mode.py` when bounded hint-driven
  visibility changes.
- Extend `tests/unit/adapters/mcp/test_router_elicitation.py` and
  `tests/unit/adapters/mcp/test_search_surface.py` only if diagnostics/search
  output becomes aware of the new hints.
- Run `tests/e2e/integration/test_guided_surface_contract_parity.py` and
  `tests/e2e/integration/test_guided_gate_state_transport.py` when public
  stdio/Streamable HTTP payloads change.

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if public diagnostics or compare/iterate
  payloads change
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` if the transport-visible
  surface becomes normative

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/<next-number>-...task-158-...completion.md` entry created
  during `TASK-158-03` closeout.

## Status / Board Update

- This leaf stays under `TASK-158-04`; do not create a separate board row.
- When this slice closes, record whether the work stayed internal or changed a
  public transport surface so the parent closeout can cite the correct parity
  lane.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_search_surface.py -v`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
  when public stdio/Streamable HTTP payloads change
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
  when reference-understanding linkage changes public gate/status payloads

## Acceptance Criteria

- Bounded reference-understanding hints flow only through current guided
  visibility, diagnostics, and transport seams.
- No new public `reference_understand` or `router_apply_reference_strategy`
  tool is introduced.
- Public parity tests are run whenever the hint/linkage fields become
  transport-visible.
