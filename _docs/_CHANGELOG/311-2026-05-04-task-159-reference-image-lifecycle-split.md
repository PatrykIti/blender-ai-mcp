# 311. TASK-159 reference image lifecycle split

Date: 2026-05-04

## Summary

- completed `TASK-159-01-04` by extracting the reference-image lifecycle and
  staged-session branch from `server/adapters/mcp/areas/reference.py` into
  `server/adapters/mcp/areas/reference_images_runtime.py`
- kept `reference.py` as the stable MCP facade for `reference_images(...)`
  while preserving:
  - local-path validation and suffix allowlist
  - bounded file copy/delete behavior
  - active versus pending reference-session semantics
  - attach/remove/clear flows and staged adoption updates
- reused the same extracted path validator from the public facade so checkpoint
  and reference-image local file handling do not fork into separate rules

## Validation

- `python3 -m py_compile server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_images_runtime.py`
- `poetry run ruff check server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_images_runtime.py`
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_images_runtime.py`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `81 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -rs`
  - result on this machine: `14 passed`
