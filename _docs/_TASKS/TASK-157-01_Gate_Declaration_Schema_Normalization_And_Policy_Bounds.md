# TASK-157-01: Gate Declaration Schema, Normalization, And Policy Bounds

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Guided Runtime / Gate Contracts
**Estimated Effort:** Medium

## Objective

Define the first typed gate declaration contract and normalization path for
goal-derived quality gates.

This task creates the model that lets an LLM propose flexible gates while the
server keeps final authority over supported gate shapes, required/optional
classification, cardinality, safety bounds, and domain template merging.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/quality_gates.py` | Own the v1 gate contracts, domain-template contracts, and `templates_for_domain_profile(profile)` helper |
| `server/adapters/mcp/contracts/reference.py` | Reuse reference/vision payload identifiers for proposal provenance and evidence refs |
| `server/adapters/mcp/session_capabilities.py` | Add gate-plan fields to session capability state |
| `server/adapters/mcp/areas/reference.py` | Include normalized gate plan in goal/checkpoint payloads |
| `server/adapters/mcp/vision/` | Treat silhouette/action-hint/segmentation outputs as proposal or evidence sources, not as gate state |
| `server/adapters/mcp/prompts/` | Add model-facing guidance for gate proposal shape |
| `tests/unit/adapters/mcp/` | Add contract/session serialization tests |
| `_docs/_MCP_SERVER/README.md` | Document the proposal and normalized gate contract |

## Implementation Notes

- Add separate models for:
  - `GateProposalContract`
  - `NormalizedQualityGateContract`
  - `GatePlanContract`
  - `GateEvidenceRequirementContract`
  - `GateEvidenceRefContract`
  - `GatePolicyWarningContract`
- Gate proposals may include LLM-supplied labels and rationale, but normalized
  gates must use repo-owned enums for type, priority, verification strategy,
  required/optional status, and allowed correction families.
- Gate proposals may also come from `reference_understanding`,
  `silhouette_analysis`, optional `part_segmentation`, future
  `classification_scores`, VLM compare/iterate checkpoint payloads, domain
  templates, or operator input. Those sources should be represented as
  provenance, not as trusted pass/fail status.
- Normalized gates should reserve fields for:
  - `proposal_sources`
  - `source_provenance`
  - `evidence_requirements`
  - `evidence_refs`
  - `verification_strategy`
  - `allowed_correction_families`
- Domain templates may add required gates not present in the LLM proposal.
- Policy bounds must reject:
  - unsupported gate types
  - hidden tool names as gate requirements
  - broad free-form code or raw Blender instructions
  - completion claims without evidence
  - gates that require unavailable reference inputs
  - perception-derived claims that attempt to set `passed`, `failed`, or
    `waived` directly instead of becoming verifier input

## Runtime / Security Contract Notes

- Visibility level: this slice defines contracts and optional guided/reference
  payload fields; it must not expose a new public tool without the public MCP
  surface review required by `AGENTS.md`.
- Read-only vs mutating behavior: schema normalization is read-only with
  respect to Blender scene state, but it may persist normalized gate plans in
  session state.
- Parameter validation: the owning contract must use strict enums and reject
  unknown or unsupported gate/status/tool-family values rather than accepting
  free-form tool names.
- Compatibility: any legacy or partial proposal payload must pass through an
  explicit adapter; do not duplicate gate defaults in MCP wrappers.
- Secret/debug handling: proposal provenance may include provider/model/profile
  ids and reference ids, but must not include provider keys or unbounded raw
  external payloads.

## Pseudocode

```python
class GateType(StrEnum):
    REQUIRED_PART = "required_part"
    ATTACHMENT_SEAM = "attachment_seam"
    SUPPORT_CONTACT = "support_contact"
    SYMMETRY_PAIR = "symmetry_pair"
    PROPORTION_RATIO = "proportion_ratio"
    SHAPE_PROFILE = "shape_profile"
    OPENING_OR_CUT = "opening_or_cut"
    REFINEMENT_STAGE = "refinement_stage"
    FINAL_COMPLETION = "final_completion"


class GateProposalSource(StrEnum):
    LLM_GOAL = "llm_goal"
    REFERENCE_UNDERSTANDING = "reference_understanding"
    DOMAIN_TEMPLATE = "domain_template"
    SILHOUETTE_ANALYSIS = "silhouette_analysis"
    PART_SEGMENTATION = "part_segmentation"
    CLASSIFICATION_SCORES = "classification_scores"
    REFERENCE_CHECKPOINT = "reference_checkpoint"
    OPERATOR_OVERRIDE = "operator_override"


def normalize_gate_plan(proposal, *, domain_profile, templates):
    normalized = []
    for raw_gate in proposal.gates:
        gate = normalize_one_gate(raw_gate)
        gate = apply_policy_bounds(gate)
        normalized.append(gate)

    normalized.extend(template.required_gates_missing_from(normalized))
    return GatePlanContract(gates=dedupe_and_rank(normalized))
```

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
  - accepts supported gate types
  - rejects unsupported gate types
  - rejects hidden/internal tool names in proposed actions
  - preserves LLM rationale as advisory only
  - preserves reference/perception proposal provenance as advisory only
  - preserves VLM compare/iterate checkpoint provenance as advisory only
  - rejects perception-derived proposal statuses that claim gate completion
  - serializes evidence requirements and empty evidence refs before verification
  - serializes/deserializes session gate plan state
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - includes gate plan fields without breaking existing guided state payloads

## E2E Tests

- No Blender-backed E2E is required for this schema-only slice.
- Add E2E in later verifier/runtime integration tasks where gate status depends
  on actual scene state.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_PROMPTS/README.md`

## Changelog Impact

- Add changelog entry if this schema is shipped independently.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files server/adapters/mcp/contracts/reference.py server/adapters/mcp/session_capabilities.py`
- Include `server/adapters/mcp/contracts/quality_gates.py` in that
  pre-commit file list once the implementation slice creates it.

## Acceptance Criteria

- The repo has a typed gate proposal and normalized gate-plan contract.
- Domain templates can merge required gates with LLM-proposed gates.
- Unsupported or unsafe gate declarations fail with actionable errors.
- Existing guided state tests remain backward compatible.
