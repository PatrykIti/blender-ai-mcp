# TASK-163: Vision Orchestrator Feedback, Strategy Normalization, And Optional Perception Adapters

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Category:** Vision / Guided Runtime / Orchestrator Feedback
**Estimated Effort:** Large
**Follow-on After:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Related:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md), [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Context Anchor:** [318. TASK-163 reference orchestrator feedback core](../_CHANGELOG/318-2026-05-05-task-163-reference-orchestrator-feedback-core.md)

## Objective

Turn the current Vision/reference-understanding seams into one stronger,
orchestrator-facing feedback layer without creating a second public discovery or
router strategy flow.

This umbrella owns:

- server-owned normalization from `reference_understanding_summary` into a
  session-scoped strategy state
- one compact `reference_orchestrator_feedback` read model on existing
  `reference_images(...)`, `router_*`, and staged checkpoint surfaces
- deterministic lightweight reference-image metrics that complement VLM output
- default-off follow-ons for optional CLIP/SigLIP-style classification and
  segmentation-sidecar linkage

This umbrella does **not** own the first low-poly squirrel refinement stage or
future low-poly macros. Those remain with `TASK-135-03`.

## Business Problem

The repo already has strong bounded compare/iterate payloads, but the LLM still
has to assemble its next step from several separate pieces:

- `reference_understanding_summary`
- `guided_flow_state`
- `active_gate_plan`
- `planner_summary`
- `truth_followup` / `correction_candidates`

That is workable for maintainers, but too fragmented for a generic
orchestrator. The current pre-build understanding is also still light on
server-owned image evidence and on stable, compact “what do I do next?” output.

## Business Outcome

After this umbrella finishes:

- reference-guided sessions expose one compact, typed read model for the next
  bounded action
- server-owned `reference_strategy_state` preserves normalized
  `construction_path` / family policy in session state
- lightweight CV metrics complement VLM reference understanding without
  becoming truth authority
- optional classifier and segmentation adapters remain default-off and
  advisory-only

## Non-Goals

- do not introduce a public `reference_understand(...)` tool
- do not introduce a public `router_apply_reference_strategy(...)` tool
- do not make optional classifier or segmentation adapters default-on
- do not move low-poly creature refinement-stage ownership out of `TASK-135-03`
- do not let server-owned image metrics, classifier scores, or segmentation
  artifacts become gate pass/fail authority

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-163-01](./TASK-163-01_Reference_Understanding_Contract_Expansion_And_Provenance.md) | Expand the typed RU contract with server-owned views and lightweight evidence slots |
| 2 | [TASK-163-02](./TASK-163-02_Construction_Path_Policy_And_Session_Strategy_State.md) | Normalize RU into a session-owned strategy state without adding a new router tool |
| 3 | [TASK-163-03](./TASK-163-03_Unified_Orchestrator_Feedback_Contract_On_Existing_Surfaces.md) | Project one compact read model on reference/router/checkpoint surfaces |
| 4 | [TASK-163-04](./TASK-163-04_Lightweight_CV_Reference_Evidence.md) | Add deterministic lightweight image metrics that stay advisory-only |
| 5 | [TASK-163-05](./TASK-163-05_Default_Off_CLIP_Or_SigLIP_Classification_Support.md) | Add default-off support evidence for optional classifier adapters |
| 6 | [TASK-163-06](./TASK-163-06_Default_Off_Segmentation_Sidecar_And_Artifact_Linkage.md) | Add default-off RU segmentation artifact linkage without changing truth ownership |
| 7 | [TASK-163-07](./TASK-163-07_Harness_Live_Backend_Coverage_Docs_And_Closeout.md) | Close the umbrella with live backend proof lanes, docs, and board/changelog updates |

## Repository Touchpoints

| Path / Module | Why It Is In Scope |
|---------------|--------------------|
| `server/adapters/mcp/contracts/reference.py` | RU, strategy, and orchestrator-facing contracts |
| `server/adapters/mcp/areas/reference_understanding.py` | RU refresh, augmentation, and strategy persistence |
| `server/adapters/mcp/areas/reference.py` | Stage compare/iterate projection and compact feedback read model |
| `server/adapters/mcp/areas/reference_images_runtime.py` | Attach/remove/clear/list responses on existing public reference surface |
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)` / `router_get_status(...)` projection |
| `server/adapters/mcp/session_capabilities_state.py` | Session-owned strategy persistence |
| `server/adapters/mcp/vision/prompting.py`, `vision/parsing.py` | Shared RU prompt/schema/parser vocabulary |
| `tests/unit/adapters/mcp/`, `tests/unit/router/application/`, `tests/e2e/integration/` | Contract, session, transport, and reference facade owner lanes |
| `_docs/_VISION/`, `_docs/_MCP_SERVER/`, `_docs/_TESTS/`, `_docs/_TASKS/README.md` | Canonical repo-facing documentation and board state |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| RU contract/provenance expansion | unit prompt/parser/reference lanes | strict payload vocabulary and server-owned augmentation live here |
| session strategy state | unit session/reference lanes | persistence and same-goal carry-forward are session-owned |
| compact orchestrator feedback | unit facade/router lanes plus transport and Blender-backed E2E | this is client-facing runtime contract work |
| lightweight CV metrics | unit reference-image lanes plus RU transport/Blender-backed E2E | the new metrics must stay advisory-only and schema-safe |
| optional adapters follow-ons | future unit/runtime/harness lanes per adapter | heavy/default-off follow-ons must prove readiness separately |

## Acceptance Criteria

- existing public surfaces remain the default delivery path
- no public `reference_understand(...)` or `router_apply_reference_strategy(...)`
  tool is introduced
- the LLM can read one compact orchestrator-facing contract instead of manually
  stitching together multiple payload fragments
- server-owned image metrics and optional adapters stay advisory-only
- consumer work such as low-poly mesh-form refinement remains owned by
  `TASK-135-03`

## Progress Notes

- 2026-05-05: `TASK-163-01` through `TASK-163-04` landed as the first delivery
  wave:
  - RU contract now carries `views` and `visual_metrics`
  - session state now persists `reference_strategy_state`
  - existing reference/router/checkpoint surfaces now expose
    `reference_orchestrator_feedback`
  - lightweight CV metrics now augment RU on the server-owned path
- 2026-05-05: `TASK-163-05` and `TASK-163-06` landed as the optional
  support-adapter wave:
  - typed default-off `reference_classifier` runtime/config support now exists
  - RU can merge support-only `classification_scores` and
    `segmentation_artifacts` through explicit sidecars
  - optional-adapter failures now degrade to provenance notes instead of
    breaking guided sessions
- 2026-05-05: `TASK-163-07` remains open for the live-backend harness proof,
  final docs sweep, and umbrella closeout
