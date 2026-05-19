# TASK-169-03-02: Creature Reference Target Normalization For Paired Details

**Parent:** [TASK-169-03](./TASK-169-03_Creature_Quality_Bar_Gate_Normalization_And_Advisory_Support_Evidence.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Normalize frequent creature reference targets such as `ears` into the shipped role/gate vocabulary so paired-detail gates and verifier scope matching stay coherent.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_gates.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
**Acceptance Criteria:**
- frequent paired-detail target labels no longer leak avoidable ambiguity such as `ears` vs `ear_pair`
- normalization stays explicit and typed on current parser/gate/verifier seams
- paired-detail regressions are covered without introducing fuzzy semantic matching

## Implementation Notes

- keep this on the current typed seams:
  - RU/reference proposal parsing
  - normalized gate proposal intake
  - verifier target matching
- likely targets include ears and similar paired-detail vocabulary where the
  shipped role/gate contract already has a canonical label

## Pseudocode

```python
target_label = normalize_creature_reference_target(raw_target_label)
proposal = proposal.model_copy(update={"target_label": target_label})
```

## Runtime / Security Contract Notes

- normalization must be deterministic, bounded, and explicit
- do not broaden into generic semantic similarity in the verifier

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- keep nested under `TASK-169-03`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`

## Validation Category

- target-normalization proof
