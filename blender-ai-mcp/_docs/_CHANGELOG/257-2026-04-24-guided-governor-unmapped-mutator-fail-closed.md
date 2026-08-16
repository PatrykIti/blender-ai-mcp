# 257. Guided governor unmapped mutator fail-closed

Date: 2026-04-24

## Summary

Closed a guided execution-governor bypass where mutating tools without a guided
family could run while `allowed_families` was active.

## What Changed

- in `server/adapters/mcp/transforms/visibility_policy.py`:
  - mapped bounded build mutators such as `macro_cutout_recess`,
    `modeling_add_modifier`, and `mesh_boolean` into the guided family
    vocabulary
  - expanded direct mesh-edit tool mapping to `secondary_parts` so visible build
    mutators participate in the same step governor and dirty-state family logic
- in `server/adapters/mcp/router_helper.py`:
  - added a fail-closed guard for mutating `modeling_*`, `mesh_*`, `macro_*`,
    `material_*`, and `uv_*` tools that still resolve to no guided family while
    an active flow advertises `allowed_families`
- in `tests/unit/adapters/mcp/test_visibility_policy.py` and
  `tests/unit/adapters/mcp/test_context_bridge.py`:
  - added regressions for bounded mutator family mapping and unmapped mutator
    blocking

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py -q -k "unmapped_guided_mutating_tools or bounded_build_mutators or mesh_edit_tools_resolve_to_secondary_parts_family or fail_closes_for_mesh_edit_family"`
  - result on this machine: `4 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py -q`
  - result on this machine: `41 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py -q`
  - result on this machine: `96 passed`
- `poetry run ruff check server/adapters/mcp/router_helper.py server/adapters/mcp/transforms/visibility_policy.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py`
  - result on this machine: passed
- `poetry run mypy`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3089 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
