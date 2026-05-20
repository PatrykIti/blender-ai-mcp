# TASK-170-02: Reference Classifier Warmup And Attach Latency Bounds

**Parent:** [TASK-170](./TASK-170_Reference_Target_Canonicalization_And_Support_Latency_Stabilization.md)
**Status:** ✅ Done
**Completed:** 2026-05-20
**Priority:** 🔴 High
**Objective:** Remove avoidable first-attach latency from the auto-start SigLIP2 sidecar and trim unnecessary serial waiting in RU optional-support collection.
**Repository Touchpoints:** `scripts/reference_classifier_sidecar.py`, `scripts/run_streamable_openrouter.sh`, `server/adapters/mcp/vision/reference_support.py`, `tests/unit/scripts/test_script_tooling.py`, `scripts/_RUN_DOCKER_MCP.md`
**Acceptance Criteria:**
- auto-started classifier sidecars load their zero-shot pipeline before the MCP server starts serving live attach traffic
- RU optional support no longer waits for classifier and segmentation support strictly in sequence when both are enabled
- the support path remains advisory-only and keeps the same public payload shape

## Implementation Notes

- the current launcher waits only for `/health`, but the sidecar reported
  healthy before the pipeline was actually loaded; preload the pipeline inside
  the sidecar startup path
- keep the sidecar contract simple: startup may take longer, but the first live
  `reference_images(action="attach")` request should not pay that warmup cost
- run classifier and segmentation support collection concurrently; do not
  change merge semantics or provenance shape

## Pseudocode

```python
service = ReferenceClassifierService(...)
service.warmup()
server = ThreadingHTTPServer(...)

classifier_result, segmentation_result = await asyncio.gather(
    collect_classifier_support(...),
    collect_segmentation_support(...),
)
```

## Runtime / Security Contract Notes

- classifier preloading must fail fast on dependency/config issues rather than
  hanging silently in the first RU request
- support-path concurrency must not reorder or widen authority; only latency is
  being improved

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `scripts/_RUN_DOCKER_MCP.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- covered by the umbrella closeout entry when `TASK-170` lands

## Completion Summary

- the SigLIP2 sidecar now preloads its model before reporting ready
- RU optional classifier and segmentation support collection now run in
  parallel instead of always waiting serially

## Status / Board Update

- closed with parent `TASK-170`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/unit/adapters/mcp/test_reference_images.py -q`

## Validation Category

- launcher/runtime support-path proof
