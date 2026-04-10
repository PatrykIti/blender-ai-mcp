# TASK-153-03-03: Docs And Historical Closeout For Guided Visibility Authority

**Parent:** [TASK-153-03](./TASK-153-03_Regression_And_Docs_Closeout_For_Guided_Visibility_Authority.md)
**Depends On:** [TASK-153-03-01](./TASK-153-03-01_Unit_Regression_Matrix_For_Single_Runtime_Visibility_Authority.md), [TASK-153-03-02](./TASK-153-03-02_Transport_Parity_For_Guided_Runtime_Visibility_Authority.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Update the operator/public docs, docs parity tests, changelog history, and task
board state so the shipped architecture is documented and historically tracked
in the same branch.

## Repository Touchpoints

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Detailed Implementation Notes

- do this only after the runtime behavior and regressions are settled
- docs should describe the final shipped contract, not an intermediate plan
- board/changelog updates belong in the same branch as the runtime/docs closeout

## Planned File Change Map

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - codify the runtime-vs-metadata authority split
- `_docs/_MCP_SERVER/README.md`
  - explain how status/list/search reflect the single runtime authority
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - assert the new wording and examples
- `_docs/_CHANGELOG/*.md`
  - add one historical entry for TASK-153
- `_docs/_CHANGELOG/README.md`
  - index the new changelog entry
- `_docs/_TASKS/README.md`
  - update the board when TASK-153 changes promoted state

## Pseudocode Sketch

```python
docs = read_public_docs()

assert "build_visibility_rules(...)" in docs.runtime_authority_section
assert "tags/manifest" in docs.metadata_section
assert "second hidden phase gate" not in docs.ambiguous_contract_language
```

## Planned Unit Test Scenarios

- docs parity tests assert that runtime visibility is described as rule-driven
- docs parity tests assert that tags/manifest are described as metadata-only on
  `llm-guided`

## Acceptance Criteria

- docs and docs parity tests describe the same final architecture
- changelog and board state are updated when TASK-153 ships

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- add the parent TASK-153 historical entry here
