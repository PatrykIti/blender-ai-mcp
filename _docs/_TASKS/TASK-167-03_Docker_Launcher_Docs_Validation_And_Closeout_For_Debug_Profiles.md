# TASK-167-03: Docker Launcher, Docs, Validation, And Closeout For Debug Profiles

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Expose the central debug selector through the supported Docker/local operator launch paths, document how each profile should be used, and close the family only after the examples, launcher wiring, and validation evidence all match the shipped contract.
**Repository Touchpoints:** `scripts/run_streamable_openrouter.sh`, `scripts/run_mcp_server.py`, `scripts/run_reference_classifier_sidecar.sh`, `README.md`, `_docs/_MCP_SERVER/README.md`, `scripts/_RUN_DOCKER_MCP.md`, `_docs/_DEV/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:**
- Docker and local launcher paths can forward the central debug selector without custom patching by operators
- docs explain when to use `all` versus targeted scopes such as `vision`, `reference`, `tools`, `visibility`, `guided_flow`, and `router`
- operator examples show the debug selector appearing in the same terminal that already streams Docker/server logs
- final closeout records the exact proof lane used for the selected profiles and keeps board/changelog/docs in sync

## Implementation Notes

- keep the launcher contract simple: one selector env passed through the current
  supported scripts
- do not create one-off launch-script flags that bypass the central server
  config contract
- document the primary operator workflows explicitly:
  - attach/compare/iterate latency -> `vision,reference`
  - proxy arg mismatch / hidden-tool drift -> `tools,visibility`
  - guided step churn -> `guided_flow,router`
  - broad incident trace -> `all`
- preserve the current sidecar log guidance where it remains useful, but make
  clear which diagnostics should now appear directly in the Docker/server
  terminal

## Pseudocode

```bash
export BLENDER_AI_DEBUG=vision,reference
./scripts/run_streamable_openrouter.sh

export BLENDER_AI_DEBUG=tools
./scripts/run_streamable_openrouter.sh
```

## Runtime / Security Contract Notes

- docs must state clearly that debug logs are diagnostic only and may be noisy
  when `all` is enabled
- examples must not encourage logging secrets or copying raw sensitive payloads
- Docker/local launch examples must preserve the current supported runtime paths
  instead of inventing a new unsupported operator entrypoint

## Tests To Add/Update

- script tests proving the debug selector is forwarded into the launched server
- docs/grep checks ensuring the accepted profile names stay aligned with the
  shared registry

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `_docs/_DEV/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- add the historical `_docs/_CHANGELOG/*` entry when the first `TASK-167`
  implementation slice ships and index it in `_docs/_CHANGELOG/README.md`

## Validation Category

- `git diff --check`
- targeted grep/audit for profile names and launcher examples
