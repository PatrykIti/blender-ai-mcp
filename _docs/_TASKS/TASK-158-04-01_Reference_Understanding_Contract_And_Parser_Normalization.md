# TASK-158-04-01: Reference Understanding Contract And Parser Normalization

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158-04](./TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md)
**Category:** Guided Runtime / Reference Understanding Contract
**Estimated Effort:** Small

## Objective

Add the first bounded reference-understanding contract on the shared vision
path: typed result fields, alias normalization, and prompt/parser/backend
updates that keep reference-understanding advisory and do not invent a second
runtime flow.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/reference.py` | Add or compose the typed reference-understanding result contract and use `understanding_id` consistently with the roadmap |
| `server/adapters/mcp/vision/prompting.py` | Extend the shared prompt contract for bounded reference-understanding output |
| `server/adapters/mcp/vision/parsing.py` | Extend the shared parsing/repair contract and alias normalization path |
| `server/adapters/mcp/vision/backends.py` | Keep provider payload normalization on the existing backend path |
| `tests/unit/adapters/mcp/test_vision_prompting.py` | Cover schema/prompt shape and prompt redaction rules |
| `tests/unit/adapters/mcp/test_vision_parsing.py` | Cover bounded parsing, alias normalization, and reject-unknown behavior |

## Implementation Notes

- Use `understanding_id` as the stable identifier to stay aligned with
  `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`.
- Normalize draft names on parse:
  - `mesh_edit` -> `modeling_mesh`
  - `material_finish` -> stage/action hint or future family
  - `macro_create_part` -> current create/register seams
  - `mesh_shade_flat` and `macro_low_poly_*` -> future candidates only
- Parser output may propose strategy hints, part candidates, and gate seeds,
  but it must not emit passed/final-completion truth, hidden/internal tool
  names, raw Blender code, or provider secrets.
- Keep shared ownership in `vision/prompting.py`, `vision/parsing.py`, and
  `vision/backends.py` first. Split into `reference_understanding*.py` helpers
  only if the shared modules become too large and one backend contract is
  preserved.

## Pseudocode

```python
summary = parse_reference_understanding_payload(
    provider_payload,
    vision_contract_profile=runtime.active_vision_contract_profile,
)
summary = normalize_reference_aliases(summary)
proposal = build_quality_gate_proposal_from_reference_understanding(summary)

assert summary.understanding_id
assert proposal.source == "reference_understanding"
assert all(gate.status == "pending" for gate in proposal.gates)
```

## Runtime / Security Contract Notes

- Visibility level: internal/guided-reference by default; no new public MCP
  tool is introduced here.
- Read-only behavior: this slice does not mutate Blender scene state.
- Validation: reject unknown fields and unsupported aliases; preserve explicit
  compatibility adapters only where documented.
- Logging: persist redacted provider/model/profile metadata only; no raw image
  bytes, provider keys, or full debug payloads.

## Tests To Add / Update

- Extend `tests/unit/adapters/mcp/test_vision_prompting.py` for bounded prompt
  shape, redaction, and no-public-tool wording.
- Extend `tests/unit/adapters/mcp/test_vision_parsing.py` for alias
  normalization, reject-unknown behavior, and no pass/fail authority.
- Add focused `test_reference_understanding_*` files only if the shared vision
  owners become too large.

## Docs To Update

- `_docs/_PROMPTS/README.md` if prompt guidance changes
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` if the implemented
  contract needs a normative field update

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/<next-number>-...task-158-...completion.md` entry created
  during `TASK-158-03` closeout.

## Status / Board Update

- This leaf stays under `TASK-158-04`; no separate board row is created.
- Record the final contract field names and alias policy in the `TASK-158-04`
  and `TASK-158` closeout summaries.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py -v`
- `rg -n "reference_understand|router_apply_reference_strategy|status=\\\"passed\\\"|final_completion" server/adapters/mcp/vision server/adapters/mcp/contracts/reference.py tests/unit/adapters/mcp`

## Acceptance Criteria

- Reference-understanding output is typed, strict, and bounded.
- `understanding_id` is used consistently with the roadmap.
- Draft family names are normalized to current seams or future candidates.
- No parser/prompt/backend path grants pass/fail authority to reference or
  perception output.
