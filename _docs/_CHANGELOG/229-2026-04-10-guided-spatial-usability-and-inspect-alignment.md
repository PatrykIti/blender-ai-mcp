# 229. Guided spatial usability and inspect alignment

Date: 2026-04-10

## Summary

Completed TASK-152 so the guided spatial contract is now easier for models to
follow in practice:

- attached references are treated as the primary grounding input
- heuristic-friendly naming is documented and abbreviated limb names are now
  recognized in creature seam heuristics
- inspect-phase visibility and allowed family semantics are aligned

## What Changed

- updated `llm-guided` surface instructions and prompt assets so they now say:
  - attached `reference_images(...)` are the primary grounding input before the
    first major blockout decisions
  - spatial tools need explicit scope and should not be called with empty scope
    as a proxy for “inspect the whole scene”
  - full semantic names such as `ForeLeg_L` / `HindLeg_R` are preferred over
    abbreviations like `ForeL` / `HindR`
  - embedded seams vs floating segment seams must be interpreted differently
- expanded limb-name heuristics in:
  - `server/application/services/spatial_graph.py`
  - `server/adapters/mcp/areas/reference.py`
  so abbreviated fore/hind limb names now still produce limb-body seam checks
- aligned inspect runtime surface by:
  - keeping bounded attachment repair available in `inspect_validate`
  - exposing attachment repair macros on the inspect surface
  - refreshing session visibility after guided iterate advances into
    `inspect_validate`
- updated task board and `TASK-152*` tree to reflect the delivered behavior

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/tools/scene/test_scene_measure_tools.py -q`
