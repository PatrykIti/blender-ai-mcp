# TASK-172-05: Heavy Local Adapter Lifecycle, TTL, And Unload Policy

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Introduce one explicit shared-owner lifecycle policy for reusable heavy in-process local optional adapters, and add TTL/unload only if this leaf first establishes real shared backend reuse worth managing.
**Repository Touchpoints:** `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py`, `server/infrastructure/config.py`, `server/infrastructure/di.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_runner.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`, `tests/unit/adapters/mcp/test_vision_local_backend.py`, `_docs/_VISION/README.md`
**Acceptance Criteria:**
- this leaf names one concrete first shipping owner class for heavy in-process
  optional adapters, or explicitly closes with a documented
  `request_scoped_only` verdict if no such owner is justified yet
- TTL/unload is introduced only when that first owner actually reuses loaded
  adapter state across requests or packets
- cheap, lightweight, or naturally per-request branches are not routed through
  the shared-owner lifecycle path
- unload behavior, when implemented, is best-effort, bounded, and safe when the
  chosen shared owner is idle or the guided session ends

## Implementation Notes

- the current repo already avoids eager bootstrap loads; the missing gap is
  reusable heavy-adapter ownership, not "add TTL everywhere"
- first concrete ownership decision must choose one of:
  - `request_scoped_only`
  - `resolver_owned_shared_local`
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
  - `unload_on_session_end`
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
- targeted backend/unit tests for manager behavior if a dedicated lifecycle
  helper is introduced

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` only if operator-facing
  lifecycle toggles become real config

## Changelog Impact

- include lifecycle/reuse policy in the `TASK-172` changelog entry when a
  shared heavy-local adapter owner actually ships

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_local_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- lifecycle and runtime-ownership proof
