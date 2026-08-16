# TASK-101: Coverage Expansion for Tooling Scripts, Addon Bootstrap, and MCP Areas

**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-100](./TASK-100_Router_Metadata_Schema_Alignment.md)

---

## Objective

Raise unit-test coverage for the lowest-covered repo slices that still matter to day-to-day developer reliability:

- repo tooling scripts under `scripts/`
- addon bootstrap/registration in `blender_addon/__init__.py`
- MCP adapter areas for `collection`, `material`, and `extraction`

---

## Repository Touchpoints

- `scripts/build_addon.py`
- `scripts/run_e2e_tests.py`
- `scripts/translate_docs.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/material.py`
- `server/adapters/mcp/areas/extraction.py`
- `tests/unit/scripts/`
- `tests/unit/addon/`
- `tests/unit/tools/collection/`
- `tests/unit/tools/material/`
- `tests/unit/tools/extraction/`
- `_docs/_TESTS/README.md`

---

## Planned Work

- add script-level unit tests for build/archive helpers and local parsing utilities
- cover the addon `register()` / `unregister()` bootstrap path with mocked handler classes and RPC server
- add MCP area tests that validate formatted output, handler delegation, and user-facing error guidance
- rerun unit suite + coverage to measure the effect of the new tests

## Acceptance Criteria

- new tests exist for the previously weakest coverage slices
- the unit suite stays green
- coverage improves for `scripts/*`, addon bootstrap, and the selected MCP area adapters
- test docs reflect the new unit-test count and coverage baseline

## Completion Summary

- added unit tests for:
  - `scripts/build_addon.py`
  - `scripts/run_e2e_tests.py`
  - `scripts/translate_docs.py`
  - `blender_addon/__init__.py`
  - `server/adapters/mcp/areas/collection.py`
  - `server/adapters/mcp/areas/material.py`
  - `server/adapters/mcp/areas/extraction.py`
- full unit suite increased to `2389` passing tests
- repo-wide unit coverage for `server + blender_addon + scripts` reached `72%`
- targeted weak spots improved notably:
  - `blender_addon/__init__.py`: `15% -> 98%`
  - `scripts/build_addon.py`: `0% -> 94%`
  - `scripts/run_e2e_tests.py`: `0% -> 37%`
  - `scripts/translate_docs.py`: `0% -> 32%`
  - `server/adapters/mcp/areas/collection.py`: `16% -> 67%`
  - `server/adapters/mcp/areas/extraction.py`: `29% -> 53%`

## Validation

```bash
poetry run pytest tests/unit -q
poetry run pytest tests/unit -q --cov=server --cov=blender_addon --cov=scripts --cov-report=term-missing:skip-covered
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files
```
