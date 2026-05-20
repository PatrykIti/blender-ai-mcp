# TASK-170: Reference Target Canonicalization And Support Latency Stabilization

**Status:** ✅ Done
**Completed:** 2026-05-20
**Priority:** 🔴 High
**Category:** Guided Runtime / Vision / Transport Reliability
**Estimated Effort:** Medium
**Follow-on After:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Related:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-164](./TASK-164_Local_SigLIP2_Reference_Classifier_Sidecar_And_Operator_Scripts.md), [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)

## Objective

Close the two follow-on drifts that remained visible after `TASK-169` was
landed and verified on the squirrel front/side reference flow:

- canonicalize creature-oriented reference-understanding target labels such as
  `head`, `ears`, and `tail` into the repo-owned creature vocabulary
  (`head_mass`, `ear_pair`, `tail_mass`) before they leak into summary,
  proposal, feedback, and gate-plan seams
- reduce avoidable attach-time latency on the optional reference-classifier
  path so the first guided reference attach does not pay a cold model load in
  the foreground `reference_images(action="attach")` request

## Business Problem

The live container check on the repo-owned squirrel references showed that the
high-level recognition path was correct, but two operational drifts remained:

- the vision runtime could correctly identify a low-poly squirrel while still
  returning raw part labels like `head`, `ears`, and `tail`, which then
  created non-canonical gate ids and split the planner/feedback vocabulary
- the local SigLIP2 sidecar could be auto-started and marked healthy before
  its model was actually loaded, so the first reference attach paid that warmup
  cost inside the user-visible RU request path

Those gaps do not invalidate `TASK-169`, but they do leave one correctness
drift and one UX/performance drift on the same reference-guided entry path.

## Business Outcome

After this follow-on:

- creature RU summaries, derived proposal ids, and gate-plan ingestion all use
  one canonical creature target vocabulary
- repo-owned squirrel front/side runs no longer create avoidable `head` /
  `ears` / `tail` drift in gate-plan slices or guided feedback summaries
- auto-started classifier sidecars preload their model before the MCP server
  begins serving live attach requests, so the first attach avoids classifier
  cold-start latency
- optional support remains advisory-only; the fix changes normalization and
  launch timing, not authority

## Non-Goals

- do not widen classifier authority into gate unlock or truth authority
- do not make `reference_images(...)` asynchronous/task-mode only in this
  slice
- do not rewrite Streamable transport semantics globally under `TASK-160`
- do not introduce domain-agnostic alias rewriting that could corrupt
  building/non-creature reference labels

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-170-01](./TASK-170-01_Canonical_Creature_Target_Labels_For_Reference_Understanding.md) | Canonicalize creature RU part/proposal labels before gate intake and guided feedback consume them |
| 2 | [TASK-170-02](./TASK-170-02_Reference_Classifier_Warmup_And_Attach_Latency_Bounds.md) | Preload the auto-start classifier sidecar and tighten attach-time support-path latency without changing authority |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/parsing.py` | RU parse/normalization owner | first normalization seam for runtime payloads that currently surface raw creature labels |
| `server/adapters/mcp/areas/reference_understanding.py` | RU refresh/session owner | defensive summary/proposal normalization and optional-support sequencing live here |
| `server/adapters/mcp/contracts/quality_gates.py` | gate-plan normalization owner | canonical labels must survive ingestion into typed gate ids and blocker summaries |
| `server/adapters/mcp/areas/reference_feedback.py` | orchestrator feedback owner | pending required parts and next-step summaries key off normalized target labels |
| `server/adapters/mcp/vision/reference_support.py` | optional classifier/segmentation owner | support latency and support-path merging live here |
| `scripts/reference_classifier_sidecar.py`, `scripts/run_streamable_openrouter.sh`, `scripts/_RUN_DOCKER_MCP.md` | operator launch surface | auto-start warmup behavior and operator expectations belong here |
| `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/scripts/test_script_tooling.py` | owner proof lanes | canonical-label and sidecar-warmup regressions should be pinned on fast local tests |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| creature RU target canonicalization | `test_vision_parsing.py` + `test_reference_images.py` | proves normalization both at parse time and through session/gate ingestion |
| classifier warmup + support latency | `test_script_tooling.py` + targeted RU/support tests | proves the sidecar preloads before first live request and support-path logic still behaves |

## Acceptance Criteria

- creature RU payloads that say `body`, `head`, `ears`, `tail`, `front legs`,
  or similar canonical creature aliases are normalized into repo-owned labels
  before summary and proposal persistence
- `reference_understanding_gate_ids` and the RU-owned gate-plan slice no
  longer mint raw `required_part_head` / `required_part_ears` / `required_part_tail`
  ids for common creature runs
- the auto-start SigLIP2 sidecar preloads its zero-shot pipeline before the
  MCP container is considered ready for live RU attach traffic
- optional classifier/segmentation support remains advisory-only and does not
  change truth or gate authority semantics

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `_docs/_CHANGELOG/README.md` and one new `_docs/_CHANGELOG/*` entry

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/scripts/test_script_tooling.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when this follow-on lands

## Completion Summary

- creature RU normalization now canonicalizes common squirrel/common-quadruped
  labels such as `body`, `head`, `ears`, and `tail` before gate intake and
  guided feedback consume them
- the local SigLIP2 reference-classifier sidecar now preloads its model during
  startup, so first attach latency no longer includes classifier cold start
- optional support merging now runs classifier and segmentation support
  collection in parallel when both are enabled

## Status / Board Update

- `_docs/_TASKS/README.md` tracks `TASK-170` as a completed follow-on milestone
  after `TASK-169`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/scripts/test_script_tooling.py -q`

## Validation Category

- focused runtime / launcher follow-on proof
