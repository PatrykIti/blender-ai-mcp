# TASK-172-05: Heavy Local Adapter Lifecycle, TTL, And Unload Policy

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Depends On:** [TASK-172-03-02](./TASK-172-03-02_Compare_Time_Localization_Projection_And_Transport.md)
**Status:** ✅ Done
**Completed:** 2026-05-23
**Priority:** 🟠 High
**Objective:** Decide whether the first shipped in-process optional adapter family justifies shared reuse on current repo seams, and add TTL/unload only if that post-integration decision proves real shared backend pressure worth managing. External-provider and sidecar-process lifecycle stays operator-managed unless a later task explicitly promotes it into the server runtime.
**Repository Touchpoints:** `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py`, `server/infrastructure/config.py`, `server/infrastructure/di.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_runner.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`, `tests/unit/adapters/mcp/test_vision_local_backend.py`, `_docs/_VISION/README.md`
**Acceptance Criteria:**
- one concrete owner mode is documented for the first reusable in-process
  optional adapter family: `request_scoped_only` or
  `resolver_owned_shared_local`
- if `resolver_owned_shared_local` is selected, one shared owner exposes
  bounded acquire/release behavior and optional TTL/unload controls
- if `request_scoped_only` is selected, no shared lifecycle path is introduced
  and the closeout notes explicitly record that verdict
- cheap or per-request branches remain outside the shared-owner path

## Implementation Notes

- the current repo already avoids eager bootstrap loads; the missing gap is
  reusable heavy-adapter ownership, not "add TTL everywhere"
- this leaf is a post-provider optimization rather than a prerequisite for
  sidecar-only shipping; external or sidecar process lifecycle remains
  operator-managed unless a later task promotes it into the server runtime
- first concrete ownership decision must choose one of:
  - `request_scoped_only`
  - `resolver_owned_shared_local`
- the first concrete owner choice in this family must be limited to an
  in-process adapter introduced by `TASK-172-03-02` or `TASK-172-04`;
  sidecar-only branches do not qualify for TTL/unload ownership in this leaf
- likely owner seam if shared reuse is justified:
  - `LazyVisionBackendResolver.resolve(...)`
  - `LazyVisionBackendResolver.resolve_default(...)`
  - a sibling helper owned by `vision/runtime.py` plus DI wiring in
    `server/infrastructure/di.py`
- if the runtime remains request-scoped for the relevant heavy adapter family,
  this leaf should close as policy/owner clarification plus docs/tests rather
  than forcing artificial TTL state into per-request code
- add lifecycle policy only where all of the following are true:
  - adapter load cost is material
  - adapter instances are reused across requests or packets
  - RAM/VRAM retention is a real issue
- do not force lifecycle management onto:
  - external provider calls
  - cheap config-only capability lookups
  - lightweight sidecars that are already process-external and request-bounded
- if a heavy local adapter is still instantiated per request with no shared
  owner, create that ownership seam first before adding TTL knobs
- expected policy controls may include:
  - `reuse_policy`
  - `ttl_seconds`
  - `release_on_last_consumer`
  - `process_idle_unload`
  - `max_memory_class`
  - `release_if_idle`

## Pseudocode

```python
owner = resolve_shared_optional_adapter_owner("sam_local")
if owner.mode == "request_scoped_only":
    return run_request_scoped(payload)

lease = owner.acquire()
try:
    return lease.backend.run(payload)
finally:
    owner.mark_used()
    owner.release_if_idle()
```

## Runtime / Security Contract Notes

- lifecycle state must stay internal; do not expose raw process/model handles
- unload is best-effort and must not make public compare/iterate correctness
  depend on exact timing
- session-end release should not interfere with in-flight packet work

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py` when shared
  lifecycle logic touches external/runtime selection seams
- `tests/unit/adapters/mcp/test_vision_local_backend.py` when shared local
  backend ownership or reset semantics change
- `tests/unit/infrastructure/test_vision_di.py`
- targeted backend/unit tests for manager behavior if a dedicated lifecycle
  helper is introduced

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` only if operator-facing
  lifecycle toggles become real config

## Changelog Impact

- include lifecycle/reuse policy in the `TASK-172` changelog entry when a
  shared heavy-local adapter owner actually ships

## Completion Summary

- current `TASK-172` ships only operator-managed sidecar/external optional
  support branches; no reusable in-process heavy-local adapter family was
  introduced
- this leaf therefore closes with the explicit `request_scoped_only` verdict:
  no shared TTL/unload owner was added, and later in-process reuse can reopen
  as its own follow-on only if a real qualifying adapter lands

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_local_backend.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_vision_di.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- lifecycle and runtime-ownership proof
