# TASK-102: Coverage Expansion for Extraction Handler, System MCP Area, and Tooling Scripts

**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-101](./TASK-101_Coverage_Expansion_For_Tooling_And_MCP_Areas.md)

---

## Objective

Push the next coverage wave into the remaining high-value weak spots after TASK-101:

- `blender_addon/application/handlers/extraction.py`
- `server/adapters/mcp/areas/material.py`
- `server/adapters/mcp/areas/system.py`
- `scripts/run_e2e_tests.py`
- `scripts/translate_docs.py`

---

## Repository Touchpoints

- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/tools/material/test_material_mcp_tools.py`
- `tests/unit/tools/system/test_system_mcp_tools.py`
- `tests/unit/tools/extraction/test_extraction_handler_coverage.py`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

---

## Planned Work

- extend script tests to cover CLI flow, subprocess branches, retry helpers, and output/log persistence
- add MCP area tests for direct/background system wrappers and for material formatting/error paths
- replace extraction test placeholders with real mocked geometry scenarios
- rerun full unit suite, coverage, and full `pre-commit`

## Acceptance Criteria

- the selected modules show measurable coverage gains
- the full unit suite remains green
- `pre-commit run --all-files` remains green after the new tests land
- docs reflect the new unit-test count and coverage baseline

## Completion Summary

- added concrete tests for:
  - script helper branches in `run_e2e_tests.py`
  - translation/retry/main flow helpers in `translate_docs.py`
  - direct and background MCP wrappers in `server/adapters/mcp/areas/system.py`
  - additional formatting/error branches in `server/adapters/mcp/areas/material.py`
  - real geometry/mock-driven helper paths in `ExtractionHandler`
- repo-wide unit suite increased to `2420` passing tests
- repo-wide coverage (`server + blender_addon + scripts`) increased to `75%`
- targeted improvements from this batch:
  - `blender_addon/application/handlers/extraction.py`: `20% -> 76%`
  - `server/adapters/mcp/areas/material.py`: `48% -> 82%`
  - `scripts/run_e2e_tests.py`: `37% -> 73%`
  - `scripts/translate_docs.py`: `32% -> 71%`
  - `server/adapters/mcp/areas/system.py`: `35% -> 80%`

## Validation

```bash
poetry run pytest tests/unit -q
poetry run pytest tests/unit -q --cov=server --cov=blender_addon --cov=scripts --cov-report=term-missing:skip-covered
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files
```
