# TASK-175: Vision Contract Field Descriptions And Stage Read-Order

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / Contract Self-Description
**Estimated Effort:** Small
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)

## Relationship To Existing Board Items

- `TASK-171` already shipped the structured creature vision handoff
  (`ReferenceOrchestratorFeedbackContract`, attachment-first reference
  understanding, compact repair projection), but those contracts still ship as
  bare `BaseModel` field lists with no per-field self-description, so the
  orchestrating LLM must guess the role of each near-synonymous string list.
- `TASK-172` already shipped the optional vision runtime seam and the advisory
  localized-support contracts, so this family must reuse that boundary posture
  verbatim and must not reopen the optional-runtime substrate or the
  `TASK-140-06` provider-capability layer.
- `TASK-166` defined the hierarchical compare / packet transparency contracts
  (`compare_diagnostics`, `support_evidence`, `budget_control`,
  `ReferenceComparePacketContract`) whose status axes (`extraction_status`,
  `ranking_status`, `packet_status`, `ranking_recommendation`) are exactly the
  near-synonymous fields this family must make distinguishable from the schema
  alone.
- `TASK-160` owns the guided-client feedback and discovery-doc surface that the
  stage read-order guidance must stay consistent with.
- This umbrella is a STANDALONE, purely additive contract-self-description
  family. It does not change any runtime behavior, transport path, or gate
  authority; it only improves how legible the existing vision/reference output
  is to the orchestrating LLM.

## Objective

Make the LLM-facing vision and reference result contracts self-describing so the
orchestrating model can disambiguate the contract from the schema alone instead
of inferring intent from field names. Concretely:

- add concise, accurate `Field(description=...)` to every LLM-facing vision /
  reference result contract (`VisionAssistContract` and its nested contracts,
  `ReferenceOrchestratorFeedbackContract`, `ReferenceComparePacketContract`, the
  silhouette / metric contracts) so the ~7 near-synonymous string lists and the
  3-4 packet-status axes are distinguishable;
- mark `confidence` non-authoritative inline at every field where it appears,
  not only via the boolean buried in `VisionBoundaryPolicyContract`;
- expand the reference stage / compare / iterate tool docstrings to enumerate
  the key returned fields, state authoritative-vs-advisory precedence, and
  instruct an explicit client read-order: read
  `reference_orchestrator_feedback` first, then deterministic truth, then
  advisory vision.

This is documentation-as-contract: no behavior change, no new fields, no removed
fields, no gate or visibility change.

## Business Problem

The grounded gap is verifiable in the current code:

- `MCPContract` is a bare `pydantic` `BaseModel` with only
  `model_config = ConfigDict(extra="forbid")` and no `Field(description=...)`
  anywhere
  (`server/adapters/mcp/contracts/base.py:13-16`). Every structured contract
  that subclasses it therefore ships to the client as a name-only schema.
- `VisionAssistContract`
  (`server/adapters/mcp/sampling/result_types.py:149-171`) forces the
  orchestrating LLM to disambiguate roughly seven near-synonymous `list[str]`
  fields by name alone: `visible_changes`, `shape_mismatches`,
  `proportion_mismatches`, `correction_focus`, `next_corrections`,
  `goal_summary`, `reference_match_summary`. Nothing in the schema explains how
  `correction_focus` differs from `next_corrections`, or that
  `visible_changes` is descriptive while `shape_mismatches` /
  `proportion_mismatches` are reference-relative.
- The packet status axes on `ReferenceComparePacketContract`
  (`server/adapters/mcp/contracts/reference.py:532-555`) expose three or four
  near-synonymous status fields (`extraction_status`, `ranking_status`,
  `packet_status`, `ranking_recommendation`) plus `localized_support_reason`
  and `status_reason`, again with no field-level disambiguation.
- `confidence` is non-authoritative, but the only place that is stated is the
  `confidence_is_non_authoritative: bool = True` boolean on
  `VisionBoundaryPolicyContract`
  (`server/adapters/mcp/sampling/result_types.py:123`). The actual `confidence`
  fields (`VisionAssistContract.confidence`,
  `ReferenceCompareSupportEvidenceContract.confidence`, the reference
  understanding contracts at `contracts/reference.py:117/125/144/529/775`) carry
  no inline caveat.
- The reference stage tool docstrings are thin and never enumerate the ~40
  returned fields, never state authoritative-vs-advisory precedence, and never
  tell the client what to read first: `reference_images`
  (`server/adapters/mcp/areas/reference.py:2208`),
  `reference_compare_checkpoint` (`:2237`),
  `reference_compare_current_view` (`:2284`),
  `reference_compare_stage_checkpoint` (`:2325`),
  `reference_iterate_stage_checkpoint` (`:2362`).

The downstream effect: the orchestrating LLM treats advisory VLM prose and
deterministic truth as interchangeable, and may read the rich vision narrative
before the compact `reference_orchestrator_feedback`, which inverts the intended
authority order.

## Business Outcome

After this umbrella lands:

- the orchestrating LLM can read each LLM-facing vision / reference contract and
  understand, from the schema alone, what each field means, how near-synonymous
  fields differ, and which fields are advisory vs deterministic;
- `confidence` is visibly non-authoritative at every field it appears on, not
  just via a buried boolean;
- the stage / compare / iterate tool docstrings tell the client the explicit
  read-order (`reference_orchestrator_feedback` first, then deterministic truth,
  then advisory vision) and the authoritative-vs-advisory precedence, reducing
  the chance the model elevates VLM prose above scene truth;
- because the change is purely additive (descriptions and docstrings only), no
  existing client integration, payload shape, or test fixture breaks.

## Non-Goals

- Do not change any runtime behavior, payload shape, field set, default value,
  gate authority, tool visibility, or transport path. This family is additive
  description text only.
- Vision stays ADVISORY. The new descriptions must keep restating
  `not_truth_source` / `requires_deterministic_checks_for_correctness`;
  deterministic inspection / assertion / silhouette own scene truth. No
  description may imply vision can mark a gate complete or unlock a tool.
- Magnitudes described in any field stay PROPORTIONAL RATIOS vs a trusted
  reference anchor, never authoritative absolute measurements (VLMs land roughly
  37% within 2x on metric tasks); descriptions must phrase magnitude fields as
  reference-relative ratios, never as metric ground truth.
- Do not promote heavier perception sidecars (SAM / SAM2 / GroundingDINO /
  Depth-Anything / CLIP / DINO embeddings) into default-on behavior; they stay
  DEFAULT-OFF, advisory-only, packet-bounded per the `TASK-172` optional-runtime
  seam. Descriptions may name those optional fields but must not change their
  posture, and this family must not reopen the `TASK-140-06`
  provider-capability substrate.
- Do not introduce raw coordinate tokens as primary evidence in any new
  description (raw coordinates degrade LLM spatial reasoning: 3DGraphLLM
  50.1 -> 42.6; Text-Scene relations 59.4 vs coords 18.4). Descriptions should
  point the client at symbolic relations + ratios and keep coordinates as
  on-demand secondary evidence.
- Do not add VLM-side chain-of-thought for spatial judgments (VSI-Bench
  regression -1..-21%); reasoning stays in the orchestrator and the stage
  docstrings must keep that division of labor.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-175-01](./TASK-175-01_Field_Level_Descriptions_For_Vision_And_Reference_Contracts.md) | Field-Level Descriptions For Vision And Reference Contracts |
| 2 | [TASK-175-02](./TASK-175-02_Stage_Docstring_Read_Order_And_Authoritative_Precedence.md) | Stage Docstring Read-Order And Authoritative Precedence |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/contracts/base.py` | shared contract base | `MCPContract` (`:13`) is the bare `BaseModel`; the family must confirm `Field(description=...)` is compatible with `extra="forbid"` and add a docstring note that LLM-facing contracts should self-describe |
| `server/adapters/mcp/sampling/result_types.py` | vision result contracts | `VisionAssistContract` (`:149`) plus its nested `VisionIssueContract`, `VisionRecommendedCheckContract`, `VisionInputSummaryContract`, `VisionBoundaryPolicyContract`, `VisionPacketStatusContract`, `VisionCapabilitySummaryContract` carry the ~7 near-synonymous lists and the `confidence` field that need inline descriptions |
| `server/adapters/mcp/contracts/reference.py` | reference result contracts | `ReferenceOrchestratorFeedbackContract` (`:336`), `ReferenceComparePacketContract` (`:532`), `ReferenceCompareSupportEvidenceContract` (`:515`), `ReferenceSilhouetteMetricContract` (`:699`), `ReferenceSilhouetteAnalysisContract` (`:748`), `ReferenceActionHintContract` (`:718`) own the status axes, silhouette/metric magnitude fields, and `confidence` fields that need inline non-authoritative wording |
| `server/adapters/mcp/areas/reference.py` | reference stage tool docstrings | the five stage/compare/iterate tool docstrings (`:2208/2237/2284/2325/2362`) must enumerate key fields, state precedence, and instruct read-order |
| `server/adapters/mcp/areas/reference_feedback.py` | orchestrator feedback builder | the read-order text must match what this builder actually assembles into `ReferenceOrchestratorFeedbackContract`, so the docstring guidance stays accurate |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/adapters/mcp/test_contract_docs.py` | contract + docs regression lanes | adding descriptions must not break existing parity payloads; new assertions confirm descriptions and read-order text are present |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | canonical docs | docs must describe the self-describing contract posture and the explicit read-order so operators and prompts stay aligned |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| field-level descriptions present and non-breaking | `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_contract_docs.py` | the representative handler-shaped payloads must still validate after descriptions are added, and a new assertion can confirm the JSON schema now carries `description` for the disambiguated fields |
| stage docstring read-order and precedence | `tests/unit/adapters/mcp/test_public_surface_docs.py` | this lane already asserts substrings inside `areas/reference.py` source and the docs, so it is the natural home for read-order / precedence assertions |
| advisory-boundary wording stays intact | `tests/unit/adapters/mcp/test_contract_payload_parity.py` | descriptions must keep restating `not_truth_source` / non-authoritative confidence; a schema-level assertion guards against accidental authoritative wording |

## Acceptance Criteria

- the JSON schema emitted for `VisionAssistContract`,
  `ReferenceOrchestratorFeedbackContract`, and `ReferenceComparePacketContract`
  carries a non-empty `description` for each near-synonymous field
  (`visible_changes`, `shape_mismatches`, `proportion_mismatches`,
  `correction_focus`, `next_corrections`; `extraction_status`,
  `ranking_status`, `packet_status`, `ranking_recommendation`);
- every `confidence` field on the LLM-facing contracts carries an inline
  description stating it is non-authoritative and must not drive correctness
  decisions;
- magnitude-bearing fields (silhouette deltas, support-evidence
  `observed_value` / `delta`) describe their values as reference-relative
  proportions, never as authoritative absolute measurements;
- the five reference stage/compare/iterate tool docstrings enumerate the key
  returned fields, state authoritative-vs-advisory precedence, and instruct the
  client read-order: `reference_orchestrator_feedback` first, then deterministic
  truth, then advisory vision;
- all existing contract-parity and public-surface-docs tests still pass with no
  payload, field, or behavior change;
- RESEARCH CAVEAT: the cited benchmarks (Descrip3D arXiv:2507.14555; Structured
  Interfaces / GraphRAG schema framing arXiv:2510.16643; plus the spatial-token
  and chain-of-thought benchmarks named in Non-Goals) are indoor-scan / synthetic
  and NOT Blender-vs-reference; any claimed orchestration-legibility gain must be
  re-measured on the `tests/fixtures/vision_eval` golden fixtures before this
  family is promoted as a win.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-175` as a promoted open item on
  the Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-175|Vision Contract Field Descriptions And Stage Read-Order|Field-Level Descriptions For Vision And Reference Contracts|Stage Docstring Read-Order And Authoritative Precedence" _docs/_TASKS/TASK-175*.md`

## Validation Category

- planning / governance / task-family definition
