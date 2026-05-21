# TASK-172: Optional Vision Capability Runtime And Localized Perception

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision Runtime / Optional Perception / Guided Reliability
**Estimated Effort:** Large
**Depends On:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Related:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md), [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)

## Objective

Turn the remaining "vision extension" ideas into one current-architecture task
family that:

- finishes the capability-aware runtime posture through the existing
  `TASK-140-06` owner lane
- adds one internal typed capability inventory and prerequisite-diagnostics seam
  for optional perception adapters without creating a second public capability
  system
- keeps optional heavy perception localized, packet-bounded, and advisory-only
- introduces two concrete optional adapters that can improve reference-guided
  feedback on ambiguous creature/part cases:
  - GroundingDINO / OWL-style text-conditioned part localization
  - SAM / SAM2-style local mask and landmark support
- plans reusable heavy-adapter lifecycle, TTL, and unload behavior only where
  shared local adapter ownership and real RAM/VRAM pressure justify it

This umbrella replaces the stale monolithic "171A" framing from
`_docs/Vision-extension-proposal.md` with a task family that matches the
current repo seams.

## Business Problem

The repo already has important substrate in place:

- typed `reference_understanding_summary` and additive
  `reference_orchestrator_feedback`
- optional default-off classifier and segmentation support
- packet-bounded staged compare/iterate
- capability-aware external-runtime groundwork on the OpenRouter lane
- strict boundary rules that keep optional perception advisory-only

What is still missing is not "more vision everywhere." It is the next bounded
runtime layer for optional heavy perception:

- there is no single internal view of which optional perception capabilities
  are configured, unavailable, warmable, or worth invoking
- optional-unavailable diagnostics exist in pockets, but not as one consistent
  prerequisite/enhancement story
- there is still no text-conditioned part-localization adapter that can help
  staged compare reason about ambiguous tails, ears, snouts, or limb regions
- segmentation support exists, but the next follow-on should explicitly target
  localized mask/landmark help for packet-local ambiguity rather than generic
  "turn on segmentation"
- lifecycle policy for heavy local adapters is still under-specified: the repo
  already avoids eager bootstrap loads, but reusable local heavy adapters do
  not yet have one explicit TTL/unload owner lane

If this follow-on is not split cleanly, the repo risks reintroducing the same
problem it just removed from `TASK-171`: expensive signals with weak ownership,
duplicate phase systems, or new advisory data being treated as authority.

## Business Outcome

After this family lands:

- the capability-aware external runtime started in `TASK-140-06` is finished
  and treated as the substrate for later optional-capability work
- clients and operators can tell when optional heavy perception is available,
  missing, disabled, or degraded without mistaking that state for a hard build
  blocker
- staged compare/iterate can ask for localized optional perception only on
  bounded ambiguous packets instead of defaulting to broad heavy-image passes
- one text-conditioned localization adapter and one mask/landmark sidecar can
  improve LLM feedback on reference images for attachment/seam ambiguity while
  staying support-only
- heavy local adapters have an explicit reuse and release policy where it is
  worth the complexity, while cheap or per-request branches stay simple and do
  not pay unnecessary cold-start overhead

## Non-Goals

- do not add a new public `vision_capability_registry(...)` or similar tool
- do not reuse FastMCP discovery/platform capability surfaces as runtime gate
  authority
- do not let optional localization or segmentation pass gates, unlock tools, or
  override deterministic scene truth
- do not make heavy perception default-on for normal guided sessions
- do not add a full-image heavy pass as the default correction strategy
- do not reopen the closed `TASK-171` runtime-repair family
- do not fold DINOv2 dense features into this first wave; defer them until
  localization plus masks prove insufficient for actionable feedback

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-172-01](./TASK-172-01_Internal_Vision_Capability_Inventory_And_Prerequisite_Diagnostics.md) | Add one internal typed capability inventory and consistent optional-capability diagnostics on existing runtime surfaces |
| 2 | [TASK-172-02](./TASK-172-02_Stage_Bound_Activation_Policy_And_Localized_Support_Contracts.md) | Define when RU and staged compare may invoke localized optional perception and how that support remains packet-bounded and advisory-only |
| 3 | [TASK-172-03](./TASK-172-03_GroundingDINO_Or_OWL_Localization_For_Packet_Bounded_Part_Ambiguity.md) | Add one optional text-conditioned part-localization adapter for ambiguous creature/reference regions |
| 4 | [TASK-172-04](./TASK-172-04_SAM_Or_SAM2_Local_Mask_And_Landmark_Support.md) | Extend optional segmentation into localized masks and landmarks that pair cleanly with bounded staged-compare support |
| 5 | [TASK-172-05](./TASK-172-05_Heavy_Local_Adapter_Lifecycle_TTL_And_Unload_Policy.md) | Add reusable heavy-local-adapter lifecycle ownership, including TTL/unload only where reuse and resource cost justify it |
| 6 | [TASK-172-06](./TASK-172-06_Docs_Eval_Harness_And_Closeout_For_Optional_Vision_Runtime.md) | Close the family with docs, harness/eval coverage, negative coverage, and board/changelog sync |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py` | runtime config, backend resolution, request policy, and lifecycle owners | capability-aware runtime posture, optional adapter inventory, and lifecycle/reuse behavior belong here |
| `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference.py` | RU refresh, packet compare, optional support merge, and staged public surface owners | localized perception must plug into existing RU/packet seams instead of inventing a second phase engine |
| `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py` | typed client-facing and support-evidence contracts | optional adapters need bounded typed payloads with explicit advisory-only limits |
| `server/infrastructure/config.py`, `server/infrastructure/di.py` | env/config and runtime wiring owners | optional adapters, lifecycle controls, and reuse policy must stay on shared DI/runtime seams |
| `tests/unit/adapters/mcp/`, `tests/unit/router/application/`, `tests/e2e/integration/`, `tests/e2e/vision/`, `scripts/vision_harness.py` | validation and harness owners | this family changes runtime diagnostics, compare support contracts, optional sidecar behavior, and operator guidance |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | canonical docs | docs must describe the optional-capability boundary, deployment posture, and operator-visible diagnostics consistently |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| capability inventory and prerequisite diagnostics | `test_vision_runtime_config.py`, `test_vision_runner.py`, `test_vision_external_backend.py` | typed runtime state and public diagnostics must stay bounded and non-fatal |
| stage-bound activation policy and support-only localization hooks | `test_reference_images.py`, `test_contract_payload_parity.py`, `test_guided_gate_state_transport.py` | localized optional perception must remain packet-bounded and transport-safe |
| part localization adapter | `test_reference_images.py`, targeted adapter/runtime tests, optional harness/eval coverage | text-conditioned boxes must surface as advisory support only |
| SAM/SAM2 localized masks and landmarks | `test_reference_images.py`, `test_public_surface_docs.py`, `test_guided_gate_state_transport.py` | localized segmentation support must project through existing public envelopes |
| heavy local lifecycle / TTL / unload | `test_vision_runtime_config.py`, `test_vision_runner.py`, targeted backend tests | lifecycle policy must avoid eager bootstrap loads and avoid slowing cheap branches |
| docs / harness / closeout | `git diff --check`, targeted consistency grep, `test_script_tooling.py`, optional live/eval lanes | closeout must prove docs and harness semantics stay aligned with shipped runtime boundaries |

## Acceptance Criteria

- the repo has one internal typed optional-capability inventory or equivalent
  typed diagnostics seam that covers at least:
  - external model capabilities
  - reference classifier support
  - packet-local segmentation support
  - planned part-localization support
- missing optional heavy capability yields bounded unavailable/enhancement
  diagnostics on current surfaces instead of hard build failure
- localized optional perception is invoked only on bounded RU or compare
  contexts that name the relevant packet, target part/role, or local ambiguity
- GroundingDINO / OWL-style localization and SAM / SAM2-style masks improve the
  LLM-facing feedback path for ambiguous reference-guided creature/part cases
  without becoming truth or gate authority
- reusable heavy local adapters have an explicit lifecycle policy that includes
  TTL/unload where shared ownership makes it worthwhile, while cheap or
  per-request branches stay simple

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`
- `_docs/Vision-extension-proposal.md` only if it is later retained as a live
  planning note rather than historical background

## Tests To Add/Update

- split across the execution slices above; each child task owns its exact lane

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when the first implementation slice lands
- extend or add follow-on entries as the family closes, depending on landing
  cadence

## Status / Board Update

- add `TASK-172` to the `Vision & Hybrid Loop` open board section in
  `_docs/_TASKS/README.md`
- keep the `TASK-172-0*.md` child files nested under the umbrella while this
  parent remains open

## Validation Commands

- `git diff --check`
- `rg -n "TASK-172|GroundingDINO|OWL|SAM|SAM2|TTL|unload|localized perception|prerequisite diagnostics" _docs/_TASKS/README.md _docs/_TASKS/TASK-172*.md`

## Validation Category

- planning / governance task family definition
