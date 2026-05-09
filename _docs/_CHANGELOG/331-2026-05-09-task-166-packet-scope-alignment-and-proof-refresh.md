# 331. TASK-166 packet scope alignment and proof refresh

Date: 2026-05-09

## Summary

- tightened staged compare packet locality so scope packets now reuse
  packet-local reference slices and pass packet-local focus targets into the
  bounded vision requests instead of always reusing the root staged target
- fixed the recoverable iterate-setup path so
  `loop_disposition="continue_build"` no longer returns the contradictory
  `continue_recommended=false` signal
- added owner-lane tests for:
  - packet-local scope/reference routing
  - low-information packets caused by missing target-view captures
  - blocked packets caused by missing packet-local reference slices
  - compact iterate responses that keep top-level `compare_diagnostics` while
    omitting nested compact debug payloads
- refreshed the canonical `TASK-166*` docs family so closed leaves/parents,
  live validation lanes, and the promoted board row match the shipped code

## Runtime / Contract Notes

- public compare / iterate tool names stay unchanged; this slice only tightens
  the internal packet execution path and the consistency of the staged
  response semantics
- scope packets now preserve packet-local target/reference ownership deeper
  into the request assembly lane, which better matches the original TASK-166
  contract for scope-first packet compare
- the task family no longer points at the removed
  `tests/unit/router/application/test_router_contracts.py` validation path;
  packet/contract proof now stays on the live unit owner lanes

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k 'scope_local_refs or missing_front_capture or missing_tail_reference or preserves_flow_on_recoverable_reference_setup_error or compact_path'`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
