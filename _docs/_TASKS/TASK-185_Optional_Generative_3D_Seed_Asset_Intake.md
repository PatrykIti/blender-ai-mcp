# TASK-185: Optional Generative 3D Seed Asset Intake

**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Category:** Reconstruction / External 3D Asset Intake / Provider Boundary
**Estimated Effort:** Extra Large
**Follow-on After:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md), [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)

## Objective

Define a default-off intake lane for optional generated 3D seed assets, such as
provider-produced GLB/OBJ meshes, without treating any vendor claim or generated
asset as deterministic scene truth.

This task is intentionally provider-boundary first. Before implementation, the
chosen provider path must be re-verified against current official API, licensing,
privacy, and content terms.

## Business Problem

The repo has strong Blender-side inspection, guided reconstruction, and
reference-compare loops, but no explicit task for importing a generated 3D seed
asset from an external provider or local sidecar. Ad hoc support would risk:

- leaking provider keys or reference assets
- importing licensed or provenance-unknown meshes without operator visibility
- bypassing deterministic inspection and cleanup
- confusing generated seed geometry with verified target reconstruction

## Business Outcome

After this task lands, operators can optionally request a seed asset from a
reviewed provider path, import it into Blender, run deterministic inspection and
cleanup, and then hand it to the normal guided reconstruction/part-registration
flow.

## Non-Goals

- do not make any external generative provider default-on
- do not bypass Blender inspection, cleanup, or measurement after import
- do not claim provider output is accurate to the reference
- do not choose a vendor based on stale documentation; verify current official
  docs and terms before implementation

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/infrastructure/config.py`, `server/infrastructure/di.py` | provider config and dependency wiring | provider keys and optional runtime setup must be centralized |
| `server/application/tool_handlers/`, `server/adapters/mcp/areas/` | future MCP-facing intake surface | import/generation requests need typed contracts and bounded visibility |
| `blender_addon/application/handlers/`, `blender_addon/infrastructure/rpc_server.py` | Blender import and post-import inspection | imported assets must be created through Blender-side main-thread-safe handlers |
| `_docs/_MCP_SERVER/README.md`, `_docs/_ADDON/README.md`, `_docs/_TASKS/README.md` | operator/public contract docs | provider auth, side effects, and local file handling must be explicit |

## Runtime / Security Contract Notes

- visibility level must be public only after an explicit product review; until
  then it should be hidden/internal or guided-phase-only
- generation/import is mutating and must report Blender mode/selection impact
- provider keys must be read from approved config/env only and redacted from
  logs/debug payloads
- downloads must enforce timeout, file size, extension, and content-type limits
- generated files must be treated as untrusted input and inspected before guided
  workflows consume them

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| provider contract and current-doc verification | docs checklist plus official-source links captured in implementation notes | provider capabilities and terms can change |
| config and secret handling | unit tests for config validation and redaction | prevents provider-key leakage |
| async job lifecycle | unit/integration tests for queued, running, failed, timeout, and completed states | generation can be slow or fail externally |
| Blender import | E2E with local fixture asset first | proves import side effects and inspection handoff before any live provider path |

## Acceptance Criteria

- implementation notes identify the exact provider or sidecar path and cite
  current official docs reviewed during that implementation
- provider auth, timeout, file-size, and cleanup policy are documented before
  code lands
- imported assets are inspected and handed to normal deterministic/guided flows
  instead of being treated as complete reconstruction

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`
- `_docs/_TASKS/README.md`
- provider/operator setup docs if a concrete provider is selected

## Changelog Impact

- add a `_docs/_CHANGELOG/*` entry when implementation lands

## Validation Commands

- `git diff --check`
- provider implementation must add targeted unit tests and a fixture-backed
  Blender import proof before any live-provider smoke is considered
