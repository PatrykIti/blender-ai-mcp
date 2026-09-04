# 130 - 2026-03-23: Coverage expansion for tooling scripts, addon bootstrap, and MCP areas

## Summary

Added focused unit tests for the weakest developer-facing reliability slices identified in the previous coverage run:

- repo tooling scripts
- addon bootstrap registration
- MCP collection/material/extraction adapters

This pass was intentionally aimed at practical confidence, not synthetic coverage inflation. The new tests exercise:

- archive creation and ignore rules in the addon build script
- local control flow and helper behavior in the E2E runner script
- local parsing/utility helpers in the docs translation script
- addon `register()` / `unregister()` wiring
- formatted MCP output and error guidance for `collection`, `material`, and `extraction`

## Updated files

- `tests/unit/scripts/test_script_tooling.py`
- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/collection/test_collection_mcp_tools.py`
- `tests/unit/tools/material/test_material_mcp_tools.py`
- `tests/unit/tools/extraction/test_extraction_mcp_tools.py`
- `_docs/_TASKS/TASK-101_Coverage_Expansion_For_Tooling_And_MCP_Areas.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Validation

```bash
poetry run pytest tests/unit -q
poetry run pytest tests/unit -q --cov=server --cov=blender_addon --cov=scripts --cov-report=term-missing:skip-covered
```

Result:

- unit tests: `2389 passed`
- total coverage (`server + blender_addon + scripts`): `72%`

Selected improvements:

- `blender_addon/__init__.py`: `98%`
- `scripts/build_addon.py`: `94%`
- `scripts/run_e2e_tests.py`: `37%`
- `scripts/translate_docs.py`: `32%`
- `server/adapters/mcp/areas/collection.py`: `67%`
- `server/adapters/mcp/areas/extraction.py`: `53%`
