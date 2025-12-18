# TASK-061: Router – MCP API alignment, mega-tools, offline/test stability

**Status**: ✅ DONE (changes in repo, no PR)  
**Priority**: P1  
**Created**: 2025-12-12  
**Related**: TASK-049 (dispatcher mapping), TASK-048 (DI/LaBSE), TASK-041 (workflows), TASK-055-FIX (ensemble/modifiers)

---

> **Note (2025-12-17):** The MCP tool `vector_db_manage` was removed and replaced by `workflow_catalog` (read-only workflow browsing/search/inspection). This task remains as historical context for the LanceDB/LaBSE integration.

## Goal

Quick sanity-check of the router (Supervisor Layer) regarding:
- consistency with the actual MCP tools API,
- executability of the “mega-tools” (`mesh_select*`) by the dispatcher,
- stability of tests/offline (no LaBSE/HF downloads in pytest).

## Why this matters

The router is a “supervisor” over LLM tool-calls. If the router:
- emits tool-calls incompatible with MCP (wrong tool/parameter names),
- relies on metadata that do not match real tools,
- or in tests touches the network / downloads models,

then the whole “safety” layer works only seemingly: it looks good on paper, but in practice it cannot be executed or is unstable in CI/offline.

---

## Observations (what was wrong)

### 1) API drift: Router/docs vs real MCP tools

In several places the router (engines + examples in `_docs/_ROUTER`) used old parameter / tool names:
- `mesh_bevel.width` vs current `mesh_bevel.offset`
- `mesh_extrude_region.depth` vs current `mesh_extrude_region.move`
- examples with `mesh_extrude` (tool does not exist in MCP; there is `mesh_extrude_region`)
- override rules for `mesh_select_targeted` used non-existent parameters (`location`/`threshold`) instead of `axis/min_coord/max_coord/...`

Effect: the router could generate tool-calls that the server could not execute (or that made no sense).

### 2) Router emitted mega-tools that the dispatcher did not map

The router in auto-fixes and workflows used `mesh_select` / `mesh_select_targeted`, but the dispatcher had mappings mainly for legacy names (`mesh_select_all`, etc.). In practice some of the router’s “fixes” were not executable.

### 3) Metadata drift (tools_metadata)

`server/router/infrastructure/tools_metadata/*` contained definitions not synchronized with the real MCP:
- param `width` in `mesh_bevel.json` (should be `offset`)
- references to non-existent tool `mesh_extrude` (JSON + some docs)

This is a natural “drift” when metadata are maintained manually.

### 4) Tests hung (LaBSE / network)

`test_supervisor_router.py` could hang due to lazy init of the ensemble matcher, which in the background tried to load `SentenceTransformer("LaBSE")` (under restricted network this leads to download attempts/timeouts).

Conclusion: unit tests must not depend on downloading large models or on the internet.

### 5) Workflow source of truth: docs vs runtime

The repo contains full workflow YAMLs in `_docs/_ROUTER/WORKFLOWS/*`, but the runtime loader only loads from `server/router/application/workflows/custom/*.yaml`.

Side effect: tests (and users) may assume existence of workflows from docs that the runtime does not see at all.

---

## Design decision

Instead of adding aliases/backward compatibility in the router (e.g. accept `depth` and map to `move`), we chose:
- to tighten the router to the current MCP API,
- and to update the most important docs/tests.

Reason: the router is a “supervisor” layer — it should emit exactly what MCP can execute; aliasing in the supervisor easily hides drift and makes detecting regressions harder.

---

## What was fixed (what + why + where)

Below is a list of changes with justification. (Paths refer to the workspace.)

### Runtime / server code

- `server/adapters/mcp/dispatcher.py`
  - What: added mappings for mega-tools `mesh_select` and `mesh_select_targeted`.
  - Why: the router generates `mesh_select*` in auto-fixes; without mapping the dispatcher could not execute them → router fixes were “dead”.

- `server/router/application/engines/tool_correction_engine.py`
  - What: unified parameter limits to current names (`mesh_bevel.offset`, `mesh_extrude_region.move`), clamping of vectors/lists (clamp per component).
  - Why: the router clamped/fixed parameters in the old format (`width`, `depth`), and `move` is a vector (requires different clamping).

- `server/router/application/engines/error_firewall.py`
  - What: bevel rule operates on `offset` instead of `width`.
  - Why: firewall should block realistically dangerous parameters, not parameters unknown to MCP.

- `server/router/application/engines/tool_override_engine.py`
  - What: fixed overrides to correct MCP signatures:
    - phone-like: `mesh_extrude_region.move` instead of `depth`
    - tower-like: correct parameters for `mesh_select_targeted` (`axis/min_coord/max_coord/...`)
  - Why: override engine must generate executable sequences; previously some overrides were semantically incorrect.

- `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json`
  - What: `width`→`offset`, added `profile`, updated descriptions/related_tools.
  - Why: metadata feed the classifier and docs; drift causes incorrect suggestions and wrong embeddings.

- `server/router/infrastructure/tools_metadata/mesh/mesh_inset.json`
  - What: removed non-existent parameter `use_boundary`.
  - Why: you cannot document/classify parameters that the MCP tool does not accept.

- `server/router/infrastructure/tools_metadata/mesh/mesh_extrude.json`
  - What: removed.
  - Why: the `mesh_extrude` tool does not exist in MCP; keeping this definition generated false paths and drift in docs.

- `server/infrastructure/di.py`
  - What: under pytest LaBSE is not loaded; in offline mode (`HF_HUB_OFFLINE`) `local_files_only` is used.
  - Why: unit tests must not try to download models (restricted network) – it caused timeouts/hangs.

- `server/router/application/classifier/intent_classifier.py`
- `server/router/application/classifier/workflow_intent_classifier.py`
  - What: analogous safeguard as above (pytest skip + `local_files_only`).
  - Why: even if DI returns `None`, the classifier could still try to download a model in its `_load_model()` path.

- `server/router/application/matcher/modifier_extractor.py`
  - What: semantic matching respects `similarity_threshold` also on the avg similarity level; per-word threshold derived from `similarity_threshold`.
  - Why: behavior was intended to be configurable via `similarity_threshold`; previously it was partially hardcoded.

- `server/router/application/workflows/registry.py`
  - What: for custom workflows `$CALCULATE(...)` also sees `dimensions` from context (we do not lose context when resetting evaluator context).
  - Why: without this `min_dim` was “Unknown variable”, even though the workflow had `dimensions` in context.

- `server/router/application/workflows/custom/picnic_table.yaml`
  - What: added a minimal `picnic_table_workflow` with defaults and a modifier `"straight legs"` and usage of `$leg_angle_*` in steps.
  - Why: tests/feature assume existence of a runtime-loadable workflow; workflows in `_docs/_ROUTER/WORKFLOWS` are not automatically loaded by the application.

### Docs (the most “front-facing”)

- `_docs/_ROUTER/QUICK_START.md`, `_docs/_ROUTER/API.md`
  - What: examples for `mesh_extrude_region` rewritten to use `move` instead of `depth`.
  - Why: Quick Start/API are the first places people copy examples from.

- `_docs/_ROUTER/README.md`
  - What: “extrude” scenario rewritten from `mesh_extrude(depth)` to `mesh_extrude_region(move)` and removal of non-existent `mode: FACE` in `mesh_select`.
  - Why: README should describe working flows and real parameters.

- `_docs/_ROUTER/PATTERNS.md`
  - What: `inherit_params: ["depth"]` → `inherit_params: ["move"]` in an override example.
  - Why: consistency with the current API.

### Tests

Router and workflow system tests were updated to:
- use current parameter names (`offset`, `move`),
- reflect current behavior of the ensemble/modifier extractor (confidence normalization, “modifiers only”),
- and not assume presence of workflows only in `_docs`.

---

## Validation / how to check

Commands:
```bash
poetry run pytest tests/unit/router -q
```

---

## Risks / compatibility notes

- If some external client still sends `mesh_bevel.width` or `mesh_extrude_region.depth`, that is not compatible with the current MCP API (that is drift on the client side). The router should not “mask” this without an explicit compatibility policy.

---

## Recommendations (next steps)

1) Doc sweep: `_docs/_ROUTER` still has many references to `mesh_extrude`/`depth`/`width` (e.g. `ROUTER_HIGH_LEVEL_OVERVIEW.md`, some `IMPLEMENTATION/*`). It's worth doing a global update and/or a generator.

2) Anti-drift guard:
- add a simple test/script in CI comparing:
  - tool signatures in `server/adapters/mcp/areas/*` vs `server/router/infrastructure/tools_metadata/*`
  - and a sanity-check that the router does not emit non-existent tool names.

3) Offline mode consistently across the repo:
- `vector_db_manage` also loads `SentenceTransformer("LaBSE")` without `local_files_only`; unify it with DI.

---

## Summary of implemented recommendations (2025-12-12)

### 1) Doc sweep (`_docs/_ROUTER`)

- Global update of workflow examples to current API:
  - `mesh_bevel.width` → `mesh_bevel.offset`
  - `mesh_extrude_region.depth` → `mesh_extrude_region.move`
  - removal of legacy `mesh_extrude`
- Most important files updated in this round:
  - `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`
  - `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md`
  - `_docs/_ROUTER/WORKFLOWS/README.md`
  - `_docs/_ROUTER/WORKFLOWS/expression-reference.md`

### 2) Anti-drift guard (test/CI)

- Added test: `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
  - compares `server/adapters/mcp/areas/*.py` vs `server/router/infrastructure/tools_metadata/**/*.json`
  - also verifies constants `tool_name="..."` emitted by the router
- Along the way fixed real drifts detected by the test:
  - `modeling_create_primitive`: `type` → `primitive_type`
  - `scene_list_objects`: removed non-existent parameter `filter_type`
  - `text_create`/`text_edit`: `content` → `text`

### 3) Offline mode (vector_db_manage)

- `server/adapters/mcp/areas/vector_db.py` now uses a shared `get_labse_model()` (DI), so:
  - under pytest it does not try to load/download LaBSE
  - with `HF_HUB_OFFLINE=1` it uses local-only (no network)
  - returns a clear error when embeddings are unavailable

### Changelog

- Added: `_docs/_CHANGELOG/109-2025-12-12-router-api-alignment-offline-guards.md`
- Updated index: `_docs/_CHANGELOG/README.md`

### Validation

```bash
poetry run pytest tests/unit/router -q
```
Result: `1377 passed, 2 skipped`.
