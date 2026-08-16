# 131 - 2026-03-23: Coverage expansion for extraction handler, system MCP area, and tooling scripts

## Summary

Added the second coverage wave focused on the remaining high-value weak spots from the previous report:

- addon extraction handler internals
- MCP `system` wrappers
- MCP `material` formatting/error branches
- the E2E runner script
- the docs translation script

This batch converted several old placeholder tests into real behavior checks and pushed the repo-wide unit coverage baseline from `72%` to `75%`.

## Updated files

- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/tools/material/test_material_mcp_tools.py`
- `tests/unit/tools/system/test_system_mcp_tools.py`
- `tests/unit/tools/extraction/test_extraction_handler_coverage.py`
- `_docs/_TASKS/TASK-102_Coverage_Expansion_For_Extraction_System_And_Scripts.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Validation

```bash
poetry run pytest tests/unit -q
poetry run pytest tests/unit -q --cov=server --cov=blender_addon --cov=scripts --cov-report=term-missing:skip-covered
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files
```

Result:

- unit tests: `2420 passed`
- total coverage (`server + blender_addon + scripts`): `75%`

Selected improvements:

- `blender_addon/application/handlers/extraction.py`: `76%`
- `server/adapters/mcp/areas/material.py`: `82%`
- `server/adapters/mcp/areas/system.py`: `80%`
- `scripts/run_e2e_tests.py`: `73%`
- `scripts/translate_docs.py`: `71%`
