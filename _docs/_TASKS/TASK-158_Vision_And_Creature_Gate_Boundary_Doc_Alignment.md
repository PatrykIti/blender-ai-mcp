# TASK-158: Reference Understanding Follow-Up And Boundary Alignment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Guided Runtime / Reference Understanding Follow-Up
**Estimated Effort:** Large
**Context Anchor:** [TASK-157 docs refresh / changelog 277](../_CHANGELOG/277-2026-04-30-task-157-perception-evidence-contract-refresh.md)
**Related:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md), [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Objective

Carry the work that intentionally does not belong in `TASK-157` after the
generic gate/verifier substrate lands, while preserving the boundary cleanup
already planned for the Vision and creature docs.

`TASK-158` has two explicit scopes:

- **Scope A - Documentation and boundary alignment:** align the remaining
  Vision/reference-understanding and creature-reconstruction planning docs with
  the `TASK-157` boundary.
- **Scope B - Post-TASK-157 implementation follow-up:** implement the bounded
  reference-understanding contract, parser/prompt, guided/reference handoff,
  alias normalization, and optional-perception readiness that were kept out of
  `TASK-157`.

Both scopes must preserve these authority rules:

- Vision and perception may propose gates, relation findings, strategy hints,
  and bounded support/provenance evidence.
- Scene, spatial, mesh, assertion, and quality-gate verifier outputs own
  deterministic pass/fail truth.
- `TASK-140` provider/profile evidence remains model-capability and provenance
  evidence, not quality-gate verifier evidence.
- Draft tool and planner names from the long-form Vision plan must not read as
  current canonical families, public MCP tools, or shipped router surfaces.

Scope A is documentation-only. Scope B may change runtime code, contracts,
metadata, tests, and docs, but only after `TASK-157` supplies the generic
quality-gate substrate and only through existing reference/guided surfaces
unless a separate public-tool review promotes a new public MCP tool.

## Business Problem

`TASK-157` now states the correct generic quality-gate contract, but older
Vision and creature planning docs still contain historical wording that can
mislead implementers:

- the long-form Vision plan uses draft names such as `reference_understand(...)`
  and `router_apply_reference_strategy(...)` as if they were planned public
  runtime surfaces
- the same plan lists `mesh_edit`, `material_finish`, `mesh_shade_flat`, and
  `macro_low_poly_*` in places that read like current canonical vocabulary, and
  uses `macro_create_part` as if it were an existing create/register tool
- `TASK-135` still says `reference evidence` can decide whether a gate passed
- `TASK-135` Vision Mode wording can read as if perception defines true
  attachment or cleanup errors instead of proposing relation findings for the
  verifier
- `TASK-135-03` still uses `reference evidence requires them` for
  shape-profile child gates, which should now point to normalized gate evidence
  and verifier-backed support

Leaving these drifts in place raises the chance that a future implementation
will add a second router strategy flow, treat perception as truth, or introduce
noncanonical tool families before the existing seams are extended.

At the same time, treating `TASK-158` as documentation-only leaves important
post-`TASK-157` product work without an execution home: bounded
reference-understanding summaries, strategy normalization into guided state,
optional default-off perception evidence, and eval fixtures that can make
reference-guided reconstruction more reliable without expanding the core
quality-gate substrate.

## Business Outcome

After this task, the Vision and creature planning docs should give one
consistent implementation story:

- `TASK-157` is the generic gate/verifier substrate
- `TASK-135` and `TASK-135-03` are domain consumers of that substrate
- `TASK-140` extends model-family capability and support/provenance evidence
  without becoming a quality-gate verifier
- the long-form Vision plan is clearly marked as historical strategy material
  where it still uses pre-contract names
- future implementers know which names are aliases or candidates and which
  seams are current implementation targets

After the implementation scope, the repo should also have a bounded
reference-understanding follow-up path:

- attached references can produce typed reference-understanding summaries
  through current reference/guided seams
- those summaries can propose or support gates created by `TASK-157`, but they
  cannot mark gates passed
- draft families and macro names are normalized to current guided/reference
  family values and create/register seams
- optional SAM/CLIP/SigLIP-style adapters remain default-off follow-ons with
  explicit contracts, fixtures, and no implicit model downloads or provider
  calls

## Relationship To Existing Board Items

`TASK-158` is a promoted follow-up after the closed `TASK-157` substrate. It does
not widen `TASK-157`; instead, it holds two pieces of work that sit outside the
generic gate/verifier core:

- alignment of downstream strategy and domain-consumer docs so future
  `TASK-135`, `TASK-135-03`, and `TASK-140` implementation work does not
  contradict the generic gate/verifier contract
- implementation of reference-understanding and optional-perception support
  that consumes `TASK-157` gate contracts after they exist

The task remains one board-level row. Its child files are execution slices for
the docs cleanup and implementation follow-up and should not become separate
board rows unless this umbrella is later split.

## Execution Structure

| Order | Scope | Task | Purpose |
|-------|-------|------|---------|
| 1 | A | [TASK-158-01](./TASK-158-01_Long_Form_Vision_Plan_Surface_And_Alias_Cleanup.md) | Mark or rewrite stale long-form Vision plan references to draft public surfaces, obsolete router paths, and noncanonical family/tool names |
| 2 | A | [TASK-158-02](./TASK-158-02_Creature_Gate_Truth_Boundary_Alignment.md) | Align `TASK-135` and `TASK-135-03` with advisory Vision/perception and verifier-owned gate truth |
| 3 | B | [TASK-158-04](./TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md) | Implement the bounded reference-understanding contract, parser/prompt path, alias normalization, and guided/reference handoff after `TASK-157` exists |
| 4 | B | [TASK-158-05](./TASK-158-05_Optional_Perception_Adapter_Readiness_And_Eval_Harness.md) | Add default-off optional-perception adapter readiness and eval fixtures without making SAM/CLIP/SigLIP MVP dependencies |
| 5 | A+B | [TASK-158-03](./TASK-158-03_TASK_140_Evidence_Boundary_Audit_And_Closeout.md) | Treat `TASK-140` as the provider/profile evidence boundary anchor, run final grep/runtime validation, and close board/changelog state |

## Non-Goals

This task deliberately does not:

- implement the generic gate/verifier substrate owned by `TASK-157`
- make `TASK-135`, `TASK-135-03`, or `TASK-140` domain/provider work part of
  the generic substrate
- add a public `router_apply_reference_strategy` tool
- add a public `reference_understand` MCP tool unless a dedicated public-tool
  review promotes it; the default implementation path is an existing
  reference/guided surface or internal automatic pass
- add canonical families named `mesh_edit`, `material_finish`,
  `mesh_shade_flat`, `macro_low_poly_*`, or `macro_create_part`; they must be
  aliases, stage hints, future candidates, or mappings to current seams until
  separately shipped
- make SAM, CLIP/SigLIP, Grounding DINO, OWL-ViT, or other heavy perception
  adapters MVP dependencies or implicit runtime calls
- let reference-understanding, classifier scores, segmentation masks, or VLM
  prose mark quality gates passed
- rewrite the full long-form Vision plan from scratch
- change root `CHANGELOG.md`

## Drift Inventory

| Area | Current Drift | Required Alignment |
|------|---------------|--------------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `reference_understand(...)` and `router_apply_reference_strategy(...)` read as planned public/runtime surfaces | Mark as historical/draft strategy names or rewrite to current reference/guided-state seams; no public router strategy tool |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `server/adapters/mcp/router/...` appears as a planned location | Replace or annotate as obsolete path sketch; current router/guided/reference owners must be named from live repo seams |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `mesh_edit`, `material_finish`, `mesh_shade_flat`, `macro_low_poly_*`, and `macro_create_part` appear in allowed vocab/task examples | Map `mesh_edit` to current `modeling_mesh`, model `material_finish` as a stage/action hint or future family, map `macro_create_part` to current create/register seams, and keep low-poly macro names explicitly future/noncanonical until shipped |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | SAM/CLIP/SigLIP clusters appear as later implementation tasks | Classify as historical/future optional adapter sketches; no sidecar, model download, provider call, or runtime activation is part of TASK-158 or the MVP |
| `TASK-135` | `scene/spatial/mesh/reference evidence` decides whether a gate passed | Replace with scene/spatial/mesh/assertion/verifier truth; reference/perception may seed proposals or bounded support only |
| `TASK-135` | Vision Mode defines true attachment and cleanup errors | Vision may propose relation findings; verifier/spatial/assertion policy decides true errors and pass/fail |
| `TASK-135-03` | `reference evidence requires them` for `shape_profile` child gates | Use normalized gate evidence and verifier-backed support refs; perception remains advisory |
| `TASK-140` boundary references | Provider/profile support could be confused with quality-gate evidence if cross-linked loosely | Keep TASK-140 evidence scoped to provider capability, routing/provenance, and bounded support, not final gate verification |

## Line-Level Repair Inventory

The first implementation pass should start from this inventory instead of
rediscovering the same drift with broad grep.

| File / Range | Disposition |
|--------------|-------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:25-45` | Add or update an upfront historical/draft note so `reference_understand(...)` and `router_apply_reference_strategy(...)` do not read as current public surfaces |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:230-249` | Annotate architecture diagram references to `mesh_edit` as aliases for current `modeling_mesh` or historical strategy labels |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:279-316` | Rewrite the `reference_understand(...)` example as a draft strategy sketch or map it to existing reference/guided-state seams |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:430-466` | Annotate `mesh_edit`, `material_finish`, `mesh_shade_flat`, `macro_low_poly_finish`, and `macro_create_part` as aliases/future candidates or historical shorthand, not current canonical families/tools |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:511-518` | Rewrite allowed-family examples so `mesh_edit` maps to `modeling_mesh` and `material_finish` is a stage/action hint or future family |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:641-688` | Fix family allowlists so noncanonical names are not presented as runtime vocabulary |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:744-815` | Rewrite `reference_understand(...)`, `router_apply_reference_strategy(...)`, `mesh_edit`, and `material_finish` as draft strategy names routed through current seams |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:836-852` | Map `macro_create_part` to current `modeling_create_primitive(...)` with guided role/group auto-registration or `guided_register_part(...)` for existing objects |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:912-919` | Same as above for remaining `macro_create_part` tool-list wording |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:948-968` | Mark `mesh_shade_flat` and `macro_low_poly_*` examples as future candidates until shipped |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:1006-1012` | Same as above for finish/low-poly macro examples |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:1155-1161` | Annotate remaining `mesh_edit` / `material_finish` JSON examples as aliases or future stage hints |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:1973-1989` | Classification-only row: concept-level `reference_understanding` hits are allowed when they do not imply a current public tool or verifier authority |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2029-2043` | Classify CLIP/SigLIP and SAM sidecar phases as historical/future optional adapter sketches; no runtime activation is part of TASK-158 or the MVP |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2098-2183` | Replace obsolete proposed paths such as `server/adapters/mcp/router/...` with current owner seams or historical notes |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2186-2272` | Classification-only row: eval-pack test, fixture, and harness names may remain historical/future sketches when they do not imply current public tools or router surfaces |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2306-2316` | Reframe `reference_understand(...)` success criteria as draft shorthand routed through current reference/guided-state seams |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2438-2459` | Reframe `reference_understand` MCP surface task as historical/draft unless a future public-tool review promotes it |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2468-2476` | Replace obsolete `server/adapters/mcp/router/...` implementation paths with current owner seams or historical notes |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2518-2525` | Mark low-poly macro names as future optional candidates, not current tool names |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2553-2581` | Classify CLIP/SigLIP and SAM task blocks as future optional adapter sketches requiring their own follow-on contract/runtime task |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2588-2605` | Reframe final `reference_understand(...)` summary as draft shorthand and keep CLIP/SigLIP and SAM as optional later adapters, not MVP dependencies |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:2697-2700` | Classify CLIP/SigLIP, SAM, and related part-localization libraries as future optional adapters, not TASK-158 or MVP runtime scope |
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md:68-77` | Replace `scene/spatial/mesh/reference evidence` pass/fail authority with scene/spatial/mesh/assertion/verifier truth |
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md:162-183` | Make Vision Mode relation findings advisory until verifier/spatial/assertion policy binds them to gate status |
| `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md:90-98` | Replace standalone `reference evidence requires them` with normalized gate evidence and verifier-supported support refs |
| `_docs/_TASKS/TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md:66-72` | Canonical no-op anchor: do not rewrite unless a contradiction is introduced elsewhere |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md:14-18` | Canonical no-op anchor for provider/profile evidence reporting |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md:30-32` | Canonical no-op anchor for keeping support evidence separate from quality-gate verifier evidence |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:73-76` | Canonical no-op anchor for advisory-only Vision/perception and verifier-owned truth |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:100-108` | Canonical no-op anchor that leaves the first reference-understanding public surface undecided and forbids a public `router_apply_reference_strategy` tool |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:176-188` | Canonical no-op anchor for alias/future-tool mapping of `mesh_edit`, `material_finish`, and low-poly macro names |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:227-256` | Canonical no-op anchor that keeps SAM, CLIP/SigLIP, segmentation sidecars, and related heavy perception adapters as optional later work |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:273-277` | Canonical no-op anchor that keeps low-poly macro names out of first implementation |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:290-296` | Canonical no-op anchor that routes implementation through current reference/guided-state seams or real `server/router/` owners, not a non-existent MCP router package |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:348-355` | Canonical no-op anchor for open public-surface decisions and deciding later whether `material_finish` becomes a canonical planner family |

## Source-Of-Truth Anchors

Use these current contracts when deciding whether a term is canonical:

- `server/adapters/mcp/contracts/reference.py` owns
  `ReferencePlannerFamilyLiteral`; today it allows `macro`, `modeling_mesh`,
  `sculpt_region`, and `inspect_only`.
- `server/adapters/mcp/contracts/guided_flow.py` owns
  `GuidedFlowFamilyLiteral`; today it allows `spatial_context`,
  `reference_context`, `primary_masses`, `secondary_parts`,
  `attachment_alignment`, `checkpoint_iterate`, `inspect_validate`, `finish`,
  and `utility`.
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` is the normative bridge
  from the long-form plan to the current repo contract. Its alias/future-tool
  section should be treated as the policy baseline for this task.
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md:237-263` is the repo-level
  boundary for perception inputs, `vision_contract_profile`, spatial graph
  truth products, and Inspection/Assertion truth ownership.

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | Historical strategy doc cleanup | Remove or annotate stale public-tool, router-path, and noncanonical family wording |
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md` | Domain consumer contract | Make creature reconstruction consume `TASK-157` verifier truth without granting perception pass/fail authority |
| `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md` | Mesh refinement consumer contract | Make shape-profile/refinement gates rely on normalized verifier-backed evidence |
| `_docs/_TASKS/TASK-140*.md` | Evidence boundary audit only | Confirm provider/profile evidence stays separate from quality-gate verifier evidence; patch wording only if drift exists |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Cross-link only if needed | Add a pointer only if the long-form plan cleanup needs a normative bridge |
| `server/adapters/mcp/contracts/reference.py` | Existing reference-stage contracts | Extend or compose reference-understanding summaries without inventing a parallel public surface |
| `server/adapters/mcp/contracts/quality_gates.py` | Post-TASK-157 gate contracts | Consume normalized gate/evidence refs after `TASK-157` introduces the substrate |
| `server/adapters/mcp/areas/reference.py` | Existing reference/guided surface | Surface reference-understanding summaries and gate proposals through current reference flow when public-tool review does not promote a new tool |
| `server/adapters/mcp/session_capabilities.py` | Guided state | Store bounded reference-understanding summary ids, proposal refs, and strategy hints scoped to the current session |
| `server/adapters/mcp/vision/` | Reference-understanding parser/prompt and optional adapter readiness | Own bounded VLM/parser payloads and default-off optional adapter interfaces without making them verifier truth |
| `server/adapters/mcp/transforms/visibility_policy.py` | Guided visibility | Use `TASK-157` unresolved gate state plus reference-understanding hints to expose bounded existing tools |
| `tests/unit/adapters/mcp/` | Unit contract/parser/surface coverage | Verify schema, alias normalization, no public-tool drift, and no perception-owned pass/fail |
| `tests/fixtures/vision_eval/` | Golden fixtures | Reuse the existing eval fixture tree for reference-understanding and optional-evidence cases instead of creating a parallel fixture root |
| `_docs/_TASKS/README.md` | Board | Track this follow-on as a promoted two-scope task after `TASK-157` |
| `_docs/_CHANGELOG/` | Historical tracking | Record the task creation and later completion when docs and implementation scope are complete |

## Implementation Notes

- Execute Scope A before Scope B so the docs no longer mislead implementers
  before runtime work starts.
- Scope B is implementation work, but it must consume `TASK-157` contracts
  instead of re-implementing gate status or verifier truth.
- Do not invent a public `router_apply_reference_strategy` tool to make the old
  plan true. Strategy application is server-owned guided state, visibility, and
  gate-policy work.
- Prefer extending existing reference/guided surfaces for
  reference-understanding output. Promote a public `reference_understand` tool
  only through a separate public-tool review.
- In the long-form Vision plan, prefer a short upfront note plus local
  annotations near stale examples instead of deleting useful historical
  analysis wholesale.
- When stale names are kept for continuity, label them explicitly:
  - historical sketch
  - strategy alias
  - future optional family
  - not a current public MCP tool
  - not a current canonical planner family
- Update `TASK-135` language so the creature domain supplies templates,
  relation semantics, defaults, and target policy, while `TASK-157` verifier
  state owns completion truth.
- Update `TASK-135` Vision Mode so relation labels and mismatch descriptions
  are advisory findings until verifier/spatial/assertion policy binds them to a
  gate status.
- Update `TASK-135-03` so refinement gates cite normalized gate evidence,
  `evidence_refs`, and verifier-supported perception support instead of
  free-standing reference evidence.
- If `TASK-140` wording is touched, keep the distinction explicit:
  provider/profile evidence can explain model capability, routing choice,
  confidence, and support provenance; it does not replace quality-gate verifier
  evidence.
- Treat the `TASK-140` anchors listed above as canonical references. Do not
  rewrite them during this cleanup; use them to evaluate other `TASK-140*` hits.
- Every remaining `mesh_edit`, `material_finish`, `mesh_shade_flat`,
  `macro_low_poly_*`, and `macro_create_part` hit must be rewritten or
  annotated against the live create/register seams, live
  `ReferencePlannerFamilyLiteral`, live `GuidedFlowFamilyLiteral`, and the
  Vision roadmap alias policy.
- Every remaining SAM, CLIP/SigLIP, Grounding DINO, OWL-ViT, or segmentation
  sidecar hit must stay explicitly future optional and must not trigger a
  sidecar, model download, provider call, or runtime activation under
  `TASK-158`.
- Any optional adapter implementation must be default-off, bounded by config,
  covered by fixtures, and represented as proposal/support evidence only.

## Rewrite Pattern

Use this pattern when converting older wording:

```text
Before:
reference evidence decides whether the gate passed

After:
scene/spatial/mesh/assertion evidence, evaluated by the quality-gate verifier,
decides whether the gate passed; reference and perception outputs may seed
proposals or attach bounded support refs when the verifier strategy accepts
them.
```

```text
Before:
router_apply_reference_strategy(...) chooses the build path

After:
existing reference/guided-state seams normalize the strategy into current
guided flow state and visibility/search hints; no public router strategy tool
is introduced by this docs cleanup.
```

```text
Before:
allowed families include mesh_edit and material_finish

After:
`mesh_edit` is a strategy alias for current `modeling_mesh`; `material_finish`
is a stage/action hint or future family until implemented and documented as a
canonical surface.
```

```text
Before:
macro_create_part builds each creature part.

After:
`macro_create_part` is historical shorthand. Use current
`modeling_create_primitive(...)` with guided role/group auto-registration for
new objects, or `guided_register_part(...)` for existing objects, until a future
macro surface is explicitly designed and shipped.
```

```text
Before:
Vision defines true attachment errors and true cleanup/intersection errors.

After:
Vision records advisory relation-mismatch candidates; verifier, spatial, and
assertion policy bind those findings to attachment or cleanup gate status.
```

```text
Before:
shape-profile child gates apply where reference evidence requires them.

After:
shape-profile child gates come from normalized gate evidence and
verifier-supported support refs, not standalone reference evidence.
```

## Test Matrix

| Layer | Validation |
|-------|------------|
| Docs patch hygiene | `git diff --check` |
| Long-form plan drift | Public-surface and noncanonical-family grep commands from `TASK-158-01` |
| Creature task drift | Truth-boundary grep commands from `TASK-158-02` |
| Unit contracts | Reference-understanding schema, alias normalization, proposal refs, and reject-unknown behavior from `TASK-158-04` |
| Unit parser/prompt | Bounded parser repair, unsupported family rejection, redaction, and no pass/fail authority from `TASK-158-04` |
| Unit guided/reference surface | Existing reference/checkpoint responses include summary/proposal refs without adding a router strategy tool |
| Unit optional adapter readiness | Default-off SAM/CLIP/SigLIP adapter contracts and fixture loading from `TASK-158-05` |
| Router/metadata | Existing metadata/search/visibility paths expose only bounded existing tools and keep schema validation green |
| E2E / Blender | Add only after `TASK-157` verifier slices exist; prove reference-understanding can propose but not complete gates |
| TASK-140 boundary | Canonical-anchor audit and contradiction grep from `TASK-158-03` |
| Board / changelog | `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, and the new TASK-158 completion changelog entry stay in sync |

## Tests / Validation

Validation is scope-dependent. Scope A proves the repaired docs no longer
contradict the `TASK-157` boundary. Scope B proves the implementation consumes
`TASK-157` gate contracts, keeps reference/perception advisory, and does not
introduce unreviewed public tools or implicit heavy-model side effects.

| Layer | Validation |
|-------|------------|
| Whitespace / markdown patch hygiene | `git diff --check` |
| Public-tool drift | `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router" _docs/blender-ai-mcp-vision-reference-understanding-plan.md` and manually classify every remaining hit as historical/draft or rewrite it |
| Noncanonical family/tool drift | `rg -n "mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_TASKS/TASK-135*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` and verify no hit presents the name as a current canonical family/tool |
| Heavy perception adapter drift | `rg -n "SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md _docs/_TASKS/TASK-157*.md _docs/_TASKS/TASK-158*.md` and verify every hit is future optional, default-off, or explicitly out of MVP scope |
| Truth-boundary drift | `rg -n "reference evidence|true attachment errors|true cleanup/intersection errors|decides whether the gate passed|quality-gate verifier evidence" _docs/_TASKS/TASK-135*.md _docs/_TASKS/TASK-140*.md _docs/blender-ai-mcp-vision-reference-understanding-plan.md` and verify authority remains with scene/spatial/mesh/assertion/verifier evidence |
| Contract/parser unit tests | Extend current vision prompt/parser owners first: `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py -v`, or split focused `test_reference_understanding_*` files only if the shared owners become too large |
| Reference/guided integration tests | Update current reference/checkpoint, session, search, and router owner tests after `TASK-158-04`, then add a transport/integration lane when new summary fields or hint-driven visibility become client-facing |
| Optional adapter readiness tests | Focused unit tests for default-off adapter registry/config, explicit disabled/unavailable support envelopes, existing `vision_eval` fixtures, and any explicit opt-in harness mode after `TASK-158-05` |
| Router metadata/schema | Run metadata/schema validation when new search hints, keywords, or optional `gate_families`-style metadata are added |
| Board / changelog | Confirm `_docs/_TASKS/README.md` and `_docs/_CHANGELOG/README.md` stay in sync with added or completed task docs |

## Docs To Update

- `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md`
- `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md`
- `_docs/_TASKS/TASK-140*.md` only if the audit finds concrete wording drift
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` only if a cross-link or
  normative note is needed
- `_docs/_MCP_SERVER/README.md` when reference/checkpoint payloads or public
  surface behavior change
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` only if the implementation
  reveals a new boundary rule, not for wording churn
- `_docs/_TESTS/README.md` if fixture/test architecture materially changes
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Changelog Impact

- Creation is already recorded in changelog 278.
- On completion, add a new `_docs/_CHANGELOG/<next-number>-...task-158-...completion.md`
  entry with final grep results, implementation summary, focused test results,
  and any intentionally deferred optional adapters. Refresh
  `_docs/_CHANGELOG/README.md`. Leave changelog 278 as the creation/plan entry.

## Status / Board Update

`TASK-158` is tracked as a promoted To Do row in the Vision & Hybrid Loop lane
of `_docs/_TASKS/README.md`. When both scopes are complete, update this file's
status, move or close the board row according to board scope, refresh the board
counts, and record validation commands in the completion summary. Child tasks
`TASK-158-01`, `TASK-158-02`, `TASK-158-03`, `TASK-158-04`, and `TASK-158-05`
should be closed with the parent or explicitly superseded if the implementation
consolidates them.

## Acceptance Criteria

- The long-form Vision plan no longer reads as if `reference_understand(...)`
  or `router_apply_reference_strategy(...)` are current public MCP/runtime
  surfaces.
- The long-form Vision plan no longer presents `mesh_edit`,
  `material_finish`, `mesh_shade_flat`, `macro_low_poly_*`, or
  `macro_create_part` as current canonical families/tools.
- The long-form Vision plan no longer lets SAM, CLIP/SigLIP, segmentation
  sidecars, or related heavy perception adapters read as `TASK-158` or MVP
  implementation requirements.
- `TASK-135` and `TASK-135-03` state that Vision/perception/reference evidence
  is advisory/proposal/support context unless a server-owned verifier maps it
  into bounded evidence refs.
- Scene/spatial/mesh/assertion/verifier evidence remains the only authority for
  gate pass/fail and final completion.
- `TASK-140` provider/profile evidence remains separate from quality-gate
  verifier evidence.
- `TASK-158-04` implements a bounded reference-understanding contract/parser
  and current reference/guided handoff that can propose or support gates
  without passing them.
- `TASK-158-05` implements default-off optional adapter readiness and fixtures
  without making SAM/CLIP/SigLIP or similar adapters MVP dependencies.
- Existing reference/guided surfaces remain the default public path; any new
  public MCP tool is gated by a separate public-tool review.
- `_docs/_TASKS/README.md` tracks this task as a board-level follow-up after
  the closed `TASK-157` substrate.
- Validation commands from this task are run and recorded in the completion
  summary.
