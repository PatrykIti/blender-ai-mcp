# 335. TASK-166 super-complex packet scheduling

Date: 2026-05-10
Task: `TASK-166-04-02`

## Summary

- threaded the effective runtime image budget into staged compare packet
  planning before packet-local vision requests execute
- split super-complex same-view reference sets into bounded packet-local
  reference slices so 6-12 image compare runs stay within `VISION_MAX_IMAGES`
- preserved focused captures before optional context captures under tight image
  budgets and surfaced the scheduling decision through
  `compare_diagnostics.budget_notes`
- marked mixed clean vs corrective/uncertain packet synthesis as explicit
  conflict uncertainty instead of silently collapsing the packet evidence

## Runtime / Contract Notes

- public MCP tool names and staged compare / iterate response families are
  unchanged
- `compare_diagnostics` remains additive; budget slicing and mixed packet-status
  conflict notes are exposed through the existing diagnostics surface
- the packet scheduler only bounds vision request shape; scene truth still comes
  from deterministic inspection/assertion layers

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k "super_complex_packets or deterministic_stage_set or packet_local_target"`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run python scripts/run_e2e_tests.py`
- `poetry run ruff check server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_planner.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py`
- `git diff --check`
