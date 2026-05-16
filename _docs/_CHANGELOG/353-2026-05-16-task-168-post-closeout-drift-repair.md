# 353. TASK-168 post-closeout drift repair

Date: 2026-05-16

## Summary

Re-audited the full `TASK-168` confinement family after closeout and repaired
the remaining runtime/docs drift found by independent passes.

The repair pass:

- mapped `scene_duplicate_object` and `scene_rename_object` into the guided
  family policy so scene-identity mutations fail closed when the active guided
  step does not allow that build family
- revalidated router-corrected multi-step dispatch against the latest guided
  session state after each executed step, including role registration from
  dispatcher-created primitives
- made fail-closed runtime-policy feedback override stale reference-strategy
  checkpoint recommendations on the existing `reference_orchestrator_feedback`
  seam
- kept `guided_register_part(...)` invalid-role errors typed and fail-closed
  instead of surfacing raw `ValueError`
- tightened active compare scope and reference selection so focus pairs and
  same-view generic references do not get dropped behind stale/target-specific
  fallback ordering
- kept `manual_tools_no_router` out of normal `llm-guided` prompt
  recommendations and limited it to the explicit legacy/manual profile
- realigned MCP docs and `TASK-168-04` with the reopened 2026-05-15 closeout
  and the current compact payload semantics

## Validation

- targeted owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - result: `220 passed`
- docs/public-surface owner proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - result: `233 passed`
- contract/parity owner proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/router/application/test_router_contracts.py -q`
  - result: `97 passed`
- broad repo unit proof outside the sandbox:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - result: `3444 passed`
- repo-supported Blender E2E runner outside the sandbox:
  - `poetry run python scripts/run_e2e_tests.py`
  - result: `477 passed, 3 skipped`
- repo-wide quality gates:
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result: passed
- diff hygiene:
  - `git diff --check`
  - result: passed
