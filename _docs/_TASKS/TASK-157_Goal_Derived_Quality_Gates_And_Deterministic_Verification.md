# TASK-157: Goal-Derived Quality Gates And Deterministic Verification

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Cross-Domain Quality Gates
**Estimated Effort:** Large
**Dependencies:** TASK-117, TASK-122, TASK-143, TASK-145, TASK-150

## Objective

Introduce a generic quality-gate system where an LLM can propose flexible
domain-specific gates from the active goal and references, while the server
normalizes those gates into typed contracts and verifies completion with
deterministic inspection, assertion, spatial truth, or bounded vision evidence.

This is the cross-domain substrate for:

- [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
- [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
- future organ, biped, fantasy-character, prop, and reconstruction domains

## Business Problem

The guided runtime currently has useful domain flows, role gates, spatial
checks, and repair macros, but the quality bar is still too static and too easy
for an LLM to satisfy with prose.

Recent guided creature evidence shows the failure clearly:

- the model created named parts, but the result remained primitive blobs
- the assistant claimed completion despite missing eyes
- several required seams visually floated
- cleanup of intersections was treated as equivalent to attachment
- the LLM invented a "memory pattern" and reset the guided goal instead of
  following a stable gate contract

The same failure class will appear in building reconstruction if gates are
hardcoded per domain:

- not every building has the same roof, openings, supports, or facade rhythm
- not every creature has the same appendages or proportions
- not every guided goal needs the same stage sequence

The product therefore needs dynamic gates, but dynamic gates cannot mean
"whatever the LLM says is done." The LLM should help declare the gate plan; the
server must own normalization, verification, and final completion status.

## Business Outcome

When this umbrella is complete, the repo can support flexible guided quality
plans without turning every domain into a hardcoded workflow:

- LLMs can propose gates such as "curved tail", "roof seated on walls",
  "window grid aligned", or "eye pair present"
- the server maps those proposals into a small generic vocabulary
- deterministic checks decide whether each gate is `pending`, `blocked`,
  `passed`, or `failed`
- guided visibility and search can open the right bounded tools for the next
  unresolved gate
- final completion is blocked by failed required gates, not by prose summaries

## Non-Goals

This umbrella deliberately does not:

- make VLM prose, `reference_understanding`, SAM, CLIP/SigLIP,
  Grounding DINO, or provider-profile confidence authoritative for gate
  pass/fail status
- ship SAM, CLIP/SigLIP, Grounding DINO, or any similar heavy perception
  adapter as part of the first `TASK-157` implementation
- create a creature-only, building-only, or other domain-hardcoded completion
  flow; domain tasks consume this generic gate substrate
- replace `TASK-140`; external model-family evidence remains provider/profile
  support evidence unless a server-owned verifier maps a bounded payload into a
  supported gate evidence type
- introduce a parallel discovery, visibility, or public router-strategy flow
  when existing FastMCP visibility, guided state, router metadata, and
  reference-stage contracts can be extended

## Generic Gate Vocabulary

The first vocabulary should be deliberately small and cross-domain:

| Gate Type | Purpose | Example Domains |
|-----------|---------|-----------------|
| `required_part` | A required object/role must exist and be registered | creature body/head/eyes, building walls/roof |
| `attachment_seam` | One part must be seated or embedded on another part | tail/body, roof/wall, snout/head |
| `support_contact` | One part must be supported by or rest on another | post/beam, leg/body, stair/base |
| `symmetry_pair` | A left/right or mirrored pair must be complete and placed | ears, eyes, facade towers |
| `proportion_ratio` | A size/position ratio must be within tolerance | head/body, roof height/wall height |
| `shape_profile` | A target shape/profile must be approximated | curved tail, roof pitch, arched opening |
| `opening_or_cut` | A void/recess/opening must exist in a target surface | windows, doors, sockets |
| `refinement_stage` | A bounded modeling/mesh refinement pass is required | low-poly form profiling, facade detail |
| `final_completion` | All required gates must be passed or explicitly waived | every guided reconstruction domain |

## Responsibility Boundaries

- LLMs may propose gates from user intent, references, prompt assets, and
  visible tool state.
- The server normalizes proposals into typed gate records and rejects unsupported
  or unsafe gate shapes.
- The server verifies gate status through scene/spatial/mesh/assertion truth
  plus bounded reference/perception evidence only when a verifier strategy
  explicitly supports that evidence class.
- LaBSE/search may help find candidate tools, but cannot mark gates complete.
- Vision output may recommend gates or provide bounded evidence, but scene truth
  and assertion tools remain authoritative for object existence, contacts,
  measurements, and final completion.

## Perception Evidence Extension Points

`TASK-145` gives the reference loop a typed repair-planner handoff, but it does
not make visual feedback a gate-status authority. This umbrella is where that
handoff becomes usable for quality gates.

The gate contract should accept proposal and evidence provenance from existing
perception surfaces without making those surfaces responsible for completion:

| Input / Evidence Source | Contract Role | Authority Boundary |
|-------------------------|---------------|--------------------|
| `reference_understanding` | Optional model-readable summary of what attached references depict, expected style, likely parts, and construction path | May propose gates and default correction families; cannot pass gates |
| `silhouette_analysis` | Deterministic reference/viewport shape metrics from the existing perception layer | May support `shape_profile` and `proportion_ratio` evidence when scoped and fresh |
| `part_segmentation` | Optional default-off segmentation sidecar output when configured | May provide target masks or part-region hints; cannot prove Blender object existence or attachment |
| `classification_score` | Future CLIP-style or model-family classification evidence | May select a domain profile or construction strategy; cannot prove gate completion |
| VLM compare/iterate findings | Bounded visual mismatch or action-hint payloads from the active vision contract profile | May recommend gates, blockers, or tool families; must remain advisory unless mapped to a verifier-supported evidence type |
| scene/spatial/mesh/assertion tools | Blender truth evidence | Own object existence, contact, measurement, spatial relation, and final completion decisions |

The first implementation should reserve explicit fields for:

- `proposal_sources`: ordered provenance for why a gate exists, such as
  `llm_goal`, `reference_understanding`, `domain_template`,
  `silhouette_analysis`, `part_segmentation`, or `operator_override`
- `evidence_requirements`: the verifier-supported evidence types needed before
  the gate may pass
- `evidence_refs`: concrete verifier outputs used for the current status
- `verification_strategy`: repo-owned enum, not free prose
- `allowed_correction_families`: bounded tool families that may address the
  unresolved gate
- `source_provenance`: provider/model/profile metadata where a proposal came
  from a VLM or future perception classifier

SAM, CLIP, Grounding DINO, or similar heavier perception modules are not part of
the first `TASK-157` implementation. They should plug in later by producing the
same bounded evidence/proposal records through the vision/perception layer.

## Execution Structure

| Order | Task | Purpose |
|-------|------|---------|
| 1 | [TASK-157-01](./TASK-157-01_Gate_Declaration_Schema_Normalization_And_Policy_Bounds.md) | Define the gate schema, LLM proposal intake, normalization, policy bounds, and domain template merge rules |
| 2 | [TASK-157-01-01](./TASK-157-01-01_LLM_Proposed_Gate_Intake_And_Policy_Bounds.md) | Implement the first narrow intake contract for model-proposed gates without trusting model completion claims |
| 3 | [TASK-157-02](./TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md) | Build the verifier/status model that binds gates to spatial, assertion, object, and bounded vision evidence |
| 4 | [TASK-157-02-01](./TASK-157-02-01_Attachment_Support_And_Contact_Gate_Verifier.md) | Ship the first seam/contact verifier for `attachment_seam` and `support_contact` gates |
| 5 | [TASK-157-03](./TASK-157-03_Guided_Flow_Gate_Runtime_Integration.md) | Integrate gate state into guided flow, visibility, search, checkpoints, and completion blocking |
| 6 | [TASK-157-03-01](./TASK-157-03-01_Gate_Driven_Visibility_Search_And_Recovery_Policy.md) | Make unresolved gates open the right bounded tool families without broad catalog exposure |
| 7 | [TASK-157-04](./TASK-157-04_Cross_Domain_E2E_Gate_Regression_Harness.md) | Add cross-domain E2E/regression coverage for creature and building-style gate behavior |

## Repository Touchpoint Table

| Path / Module | Scope | Why It Is In Scope |
|---------------|-------|--------------------|
| `server/adapters/mcp/contracts/` | New gate contracts | Typed MCP-facing models for proposed gates, normalized gates, verifier status, and completion blockers |
| `server/adapters/mcp/session_capabilities.py` | Guided state | Store active gate plan, statuses, required gates, waivers, and next gate actions |
| `server/adapters/mcp/areas/reference.py` | Checkpoint loop | Include gate status in compare/iterate outputs and block final completion on failed required gates |
| `server/adapters/mcp/contracts/reference.py` | Perception handoff | Reference gate proposals and evidence refs must point at existing reference/vision payload fields instead of duplicating them |
| `server/adapters/mcp/vision/` | Perception evidence | Existing silhouette/action-hint and optional segmentation outputs may feed gate proposals/evidence through typed refs only |
| `server/adapters/mcp/areas/scene.py` | Spatial and macro tools | Feed seam/contact/support verification and macro follow-up hints |
| `server/application/services/spatial_graph.py` | Truth evidence | Reuse relation graph verdicts for seam/support gate status |
| `server/router/infrastructure/tools_metadata/` | Discovery metadata | Add gate-oriented search hints and tool family metadata |
| `server/adapters/mcp/discovery/search_documents.py` | Search shaping | Bias search toward tools that satisfy unresolved gate families |
| `server/adapters/mcp/transforms/visibility_policy.py` | Visibility | Expose bounded tools for the active unresolved gate, not the whole catalog |
| `server/adapters/mcp/prompts/` | Prompt assets | Teach clients how to propose gates and consume server-verified gate state |
| `_docs/_ROUTER/` | Runtime design docs | Document the LLM-proposes/server-verifies boundary |
| `_docs/_MCP_SERVER/README.md` | MCP contract docs | Document gate payloads, status model, and client guidance |
| `_docs/_TASKS/README.md` | Board | Track this umbrella as the generic substrate for domain reconstruction |

## Runtime / Security Contract Notes

- Visibility level: the first implementation should extend existing guided and
  reference-stage surfaces; any new public MCP tool needs the full public-tool
  review from `AGENTS.md`.
- Read-only vs mutating behavior: proposal intake and verifier status reporting
  are server/session state operations; only existing Blender mutating tools or
  macros may change scene state, and those mutations must mark affected gates
  stale before completion can pass.
- Session/auth assumptions: gate plans are scoped to the current stdio or
  Streamable HTTP MCP session state and must not leak across sessions.
- Parameter validation: normalized gate contracts must reject unknown gate
  types, hidden/internal tool names, unsupported statuses, raw Blender code, and
  completion claims without verifier evidence.
- Side-effect limits: optional perception sources and external providers remain
  bounded by existing vision runtime limits, timeouts, and disabled/unavailable
  statuses.
- Secret handling: provider keys, sidecar keys, local paths, and debug payloads
  must not be copied into gate evidence refs or client-facing logs; carry stable
  ids and redacted provider/model metadata instead.

## Test Matrix

| Layer | Tests To Add / Update |
|-------|------------------------|
| Unit contracts | Gate schema validation, unsupported gate rejection, required/optional/waived status behavior |
| Unit guided state | Session gate plan persistence, status transitions, required gate completion blockers |
| Unit reference loop | Compare/iterate payload includes gate state and does not mark completion while required gates fail |
| Unit perception refs | Perception-derived proposals stay advisory and carry source provenance without marking gates passed |
| Unit spatial truth | `attachment_seam` and `support_contact` gates map relation graph verdicts correctly |
| Unit visibility/search | Active unresolved gates expose only bounded relevant tool families |
| Router/integration | `router_set_goal` and checkpoint flows preserve gate state across guided phases |
| E2E creature | Squirrel-like blockout without eyes or seated seams cannot complete |
| E2E architecture | Building-style shell with floating roof/opening drift cannot complete until gates pass |
| Docs tests | Public docs mention gate proposal, normalization, verification, and completion semantics |

## Pseudocode

```python
proposal = GateProposal.from_llm(
    goal=current_goal,
    references=attached_references,
    suggested_gates=model_output.gates,
)

normalized = gate_normalizer.normalize(
    proposal,
    domain_profile=session.domain_profile,
    templates=domain_gate_templates.for_profile(session.domain_profile),
)

session.gate_plan = gate_policy.apply_bounds(normalized)

for gate in session.gate_plan.required_open_gates():
    evidence = gate_verifier.collect_evidence(gate, scene_scope=session.active_target_scope)
    status = gate_verifier.evaluate(gate, evidence)
    session.gate_plan.update(gate.gate_id, status)

if session.gate_plan.has_failed_required_gates():
    return GuidedLoopResult(
        loop_disposition="inspect_validate",
        completion_blockers=session.gate_plan.blockers(),
        next_actions=gate_planner.next_actions(session.gate_plan),
    )

return maybe_advance_or_complete()
```

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- Add a dedicated `_docs/_CHANGELOG/*` entry when the first gate contract or
  runtime integration slice ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_reference_images.py -v`
- `python3 scripts/run_e2e_tests.py` for implementation slices that change real
  Blender scene state, geometry, transport behavior, or final completion
  semantics.

## Acceptance Criteria

- The repo has a typed cross-domain quality-gate contract.
- LLM-proposed gates are accepted only through normalized and policy-bounded
  server contracts.
- Deterministic verification, not LLM prose, owns gate pass/fail status.
- Guided checkpoints expose active gates, blockers, next actions, and required
  verification evidence.
- Final completion is blocked while required gates fail.
- Creature and architecture tasks can consume the same substrate with
  domain-specific templates rather than separate hardcoded flows.
