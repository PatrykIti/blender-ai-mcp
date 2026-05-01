# TASK-158-04: Reference Understanding Internal Contract And Guided Handoff

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Guided Runtime / Reference Understanding
**Estimated Effort:** Medium

## Objective

Implement the bounded reference-understanding follow-up that was intentionally
kept out of `TASK-157`: a typed summary contract, parser/prompt path, alias
normalization, and handoff into existing reference/guided surfaces after the
generic quality-gate substrate exists.

This slice must let reference understanding propose gate inputs or support refs
for `TASK-157` gates, but it must not own gate pass/fail truth.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/reference.py` | Add or compose reference-understanding summary/result contracts without duplicating gate status contracts |
| `server/adapters/mcp/contracts/quality_gates.py` | Consume `TASK-157` proposal/evidence refs after that file exists; do not re-create the substrate here |
| `server/adapters/mcp/vision/reference_understanding.py` | Add bounded parser/orchestration helpers if split from `reference.py` is justified |
| `server/adapters/mcp/vision/reference_understanding_prompt.py` | Prompt/schema text for extracting subject, style, likely parts, construction path, and advisory findings |
| `server/adapters/mcp/vision/reference_understanding_parser.py` | Strict parsing, repair, alias mapping, and reject-unknown behavior |
| `server/adapters/mcp/areas/reference.py` | Surface summaries/proposal refs through existing reference/checkpoint flow unless a separate public-tool review promotes a new tool |
| `server/adapters/mcp/session_capabilities.py` | Store summary ids, provenance, proposal refs, and guided handoff hints scoped to the current session |
| `server/adapters/mcp/transforms/visibility_policy.py` | Use unresolved gate state plus reference-understanding hints to expose bounded existing tools |
| `tests/unit/adapters/mcp/` | Add contract, parser, prompt-shape, reference-surface, and guided-session tests |

## Implementation Notes

- Default public path: existing reference/guided surfaces. Do not add a public
  `reference_understand` MCP tool unless a separate public-tool review promotes
  it.
- Do not add `router_apply_reference_strategy`. Strategy application belongs to
  server-owned guided state, visibility, and `TASK-157` gate policy.
- Normalize draft family names:
  - `mesh_edit` -> current `modeling_mesh`
  - `material_finish` -> stage/action hint or future family, not canonical here
  - `macro_create_part` -> `modeling_create_primitive(...)` with guided
    role/group auto-registration for new objects, or `guided_register_part(...)`
    for existing objects
  - `mesh_shade_flat` and `macro_low_poly_*` -> future optional candidates
- Parser output may include proposed gate seeds, likely parts, construction
  path, style hints, relation candidates, and support provenance.
- Parser output must not include `status=passed`, `final_completion=true`, raw
  tool names outside the allowlist, hidden/internal tools, raw Blender code, or
  provider secrets.
- Gate proposal refs must be normalized by `TASK-157` contracts before they
  affect guided state.

## Pseudocode

```python
summary = parse_reference_understanding(provider_payload)
summary = normalize_reference_aliases(summary)
proposal_refs = quality_gates.normalize_proposals(
    summary.proposed_gates,
    source="reference_understanding",
)
guided_state.attach_reference_summary(summary.id, proposal_refs)
return reference_checkpoint_response.with_reference_understanding(
    summary=summary.public_view(),
    proposal_refs=proposal_refs,
)
```

## Runtime / Security Contract Notes

- Visibility level: internal/guided-reference by default; public tool exposure
  requires a separate public MCP review.
- Read-only vs mutating behavior: this slice is read-only and session-state
  oriented. It must not mutate Blender scene state.
- Session/auth assumptions: summaries and proposal refs stay scoped to the
  active stdio or Streamable HTTP MCP session.
- Validation: reject unknown fields and unsupported aliases; preserve explicit
  compatibility adapters only where documented.
- Side effects: no implicit provider call, sidecar activation, model download,
  or hidden router execution.
- Logging: carry redacted provider/model/profile metadata and stable ids, not
  raw image bytes, provider keys, local private paths, or full debug payloads.

## Tests To Add / Update

- `tests/unit/adapters/mcp/test_reference_understanding_contract.py`
- `tests/unit/adapters/mcp/test_reference_understanding_parser.py`
- Focused tests for reference/checkpoint response fields if `reference.py`
  payloads change.
- Focused guided-session tests for storing summary ids and proposal refs.
- Metadata/search tests only if this slice adds new search hints or schema
  fields.

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if reference/checkpoint payloads change.
- `_docs/_PROMPTS/README.md` if prompting guidance changes.
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` with the final implemented
  surface and any deferred public-tool decision.
- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  completion summary.

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/279-...task-158-...completion.md` entry created during
  `TASK-158-03` closeout.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_understanding_contract.py tests/unit/adapters/mcp/test_reference_understanding_parser.py -v`
- Add the focused reference/guided-session unit test command once the exact
  test files exist.
- `rg -n "router_apply_reference_strategy|status=\\\"passed\\\"|final_completion" server/adapters/mcp/vision server/adapters/mcp/contracts tests/unit/adapters/mcp`

## Acceptance Criteria

- Reference-understanding output is typed, strict, and bounded.
- Reference-understanding can seed `TASK-157` gate proposals/support refs but
  cannot pass gates.
- Existing reference/guided surfaces are the default exposure path.
- No public `reference_understand` or `router_apply_reference_strategy` tool is
  introduced by this slice.
- Alias normalization maps draft names to current seams or future candidates.
