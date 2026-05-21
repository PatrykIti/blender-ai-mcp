# TASK-172-05: Heavy Local Adapter Lifecycle, TTL, And Unload Policy

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Introduce one explicit lifecycle owner for reusable heavy local optional adapters, including TTL/unload where it reduces resource retention without adding unnecessary cold-start penalties to cheap or per-request branches.
**Repository Touchpoints:** `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_runner.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`, `_docs/_VISION/README.md`
**Acceptance Criteria:**
- TTL/unload policy is defined only for shared local heavy adapters with real reuse and real memory cost
- cheap, lightweight, or naturally per-request branches are not slowed down by unnecessary lifecycle machinery
- unload behavior is best-effort, bounded, and safe when adapters are idle or the guided session ends

## Implementation Notes

- the current repo already avoids eager bootstrap loads; the missing gap is
  reusable heavy-adapter ownership, not "add TTL everywhere"
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
adapter = manager.acquire("sam_local")
try:
    return adapter.run(payload)
finally:
    manager.mark_used("sam_local")
    manager.release_if_idle("sam_local")
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
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- lifecycle and runtime-ownership proof
