# 245. Guided multi-step registration and canonical pair names

Date: 2026-04-22

## Summary

Aligned guided execution with the current public modeling surface by fixing:

- guided-role convenience registration after router-inserted corrective steps
- canonical pair-name acceptance under the stricter guided naming policy
- public primitive heuristics on title-cased `primitive_type` inputs

## What Changed

- in `server/adapters/mcp/areas/modeling.py`:
  - guided-role convenience registration now recognizes successful
    create/transform results even when the router prepends corrective steps and
    returns a multi-step legacy text payload
- in `server/adapters/mcp/guided_naming_policy.py`:
  - strong semantic-name matching now accepts canonical pair names such as
    `ForeLeg_L`, `ForeLeg_R`, and `ForeLegPair`
- in `server/router/application/triggerer/workflow_triggerer.py`:
  - heuristic matching for `modeling_create_primitive(...)` now accepts the
    canonical public title-cased `primitive_type` values (`Cube`, `Sphere`, ...)
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the guided naming / convenience-registration story matches the shipped
  behavior

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3040 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
