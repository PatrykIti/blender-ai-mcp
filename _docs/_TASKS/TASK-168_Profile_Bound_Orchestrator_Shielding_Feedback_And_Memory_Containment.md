# TASK-168: Profile-Bound Orchestrator Shielding, Feedback, And Memory Containment

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime / FastMCP Platform / External Agent Safety
**Estimated Effort:** Large
**Follow-on After:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Related:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Context Anchor:** [355. TASK-168 guided registry final drift repair](../_CHANGELOG/355-2026-05-16-task-168-guided-registry-final-drift-repair.md)

## Objective

Closed on 2026-05-14, reclosed after runtime drift repair on 2026-05-15,
and repaired through the 2026-05-16 post-commit drift passes:

- `llm-guided` now enforces one fail-closed runtime contract across direct and
  router-corrected mutators: explicit phase/state gating, role/role-group
  validation, `checkpoint_iterate` mutation shields, and no-match guided-manual
  heuristic suppression
- staged compare / iterate now stay controller-sized by default through the
  existing packet scope, `compare_diagnostics`, and
  `reference_orchestrator_feedback` seams, escalating only when richer detail
  or wider scope is actually needed
- `router_get_status().surface_profile` / `contract_version` plus the live
  `guided_flow_state` / `reference_orchestrator_feedback` projection are now
  documented as the runtime authority line over stale external memory and old
  tool schemas, and the full closeout proof bundle is green
- compact staged compare/iterate now keeps heavy truth/candidate/planner detail
  out of normal controller payloads while still allowing additive
  `compare_diagnostics` for packet provenance, multi-packet synthesis,
  model-budget pressure, uncertainty, hard failures, or rich delivery

Turn `llm-guided` from a prompt-soft operating mode into a runtime-hard
orchestration contract for external controllers such as Claude Code, Codex,
Gemini, and similar MCP clients.

This umbrella must define and then implement one server-owned confinement stack
that keeps external agents inside strict per-profile boundaries even when they:

- carry stale `memory.md` heuristics
- keep old tool schemas in context
- misread guided phase transitions
- continue mutating during `checkpoint_iterate`
- infer new semantic roles or workflow routes that the current profile does not
  allow

The desired end state is not “write better prompts and hope.” It is:

- one explicit guided state graph
- one pre-dispatch action shield
- one active-workset / fragment-scoped compare strategy instead of defaulting to whole-model payloads
- one coarse-to-fine compare/verify policy that escalates only when local evidence is insufficient
- one compact `reference_orchestrator_feedback`-based contract on the existing
  guided public seams
- one selective-disclosure response policy where the controller stays on the
  additive compact path by default and only receives heavier packet detail when
  `preset_profile="rich"`, uncertainty, error, or hard-failure handling requires it
- one runtime-owned profile/session authority line on the existing
  router-status / guided-flow / feedback seams that outranks stale external
  memory
- one validation bundle proving the server can keep external agents inside the
  current public surface contract

## Business Problem

Recent live squirrel sessions showed the same failure class across multiple
external controllers:

- the controller attached references and even completed bounded
  `reference_understanding`, but still built too long without entering compare
  early enough
- the controller continued mutating after the server had already moved into
  `checkpoint_iterate`
- the controller reused stale tool-shape memories such as `label` / `notes` on
  `reference_compare_stage_checkpoint(...)`
- the controller invented role/tool arguments like `guided_role="eye_pair"` or
  passed `macro_align_part_with_contact(...)` arguments such as
  `contact_axis` / `contact_side` or signed `normal_axis` values like `-Y`
- low-confidence heuristics or stale mental models could still re-open
  irrelevant workflow paths during guided manual builds

The server already has useful ingredients:

- visibility shaping
- guided phases
- role gates
- reference compare / iterate
- deterministic inspection/assertion tools
- router correction policy

What is still missing is the higher-level confinement layer that tells the
controller, at the exact right moment:

- what it may do next
- what it must not do next
- what will fail right now
- what exact action unblocks progress

## Business Outcome

After this umbrella lands:

- `llm-guided` has a server-owned phase graph that can fail closed on
  out-of-phase mutating calls
- staged compare / iterate can default to the active workset, focus pair, or
  blocker cluster instead of forcing the controller to read whole-model detail
- compare/iterate can stay coarse and compact by default, then escalate to
  larger scope or richer detail only when the current blocker remains ambiguous
- external controllers receive one compact typed
  `reference_orchestrator_feedback`-based contract instead of reconstructing
  policy from prose, stale memory, or hidden-tool errors
- no-match guided manual sessions preserve explicit goal context strongly enough
  that unrelated workflow heuristics stay suppressed until the goal is cleared
- staged compare / iterate phases can insist on compare/support actions before
  more modeling
- compact control outputs can stop the controller from loading huge packet/truth
  dumps into its own context unless there is real uncertainty
- prompt assets and dynamic recommendations become supporting guidance layered
  on top of the runtime contract instead of the only defense against drift

## Non-Goals

- do not solve external agent memory globally for every host product; this
  umbrella only defines what our MCP server can do from its side of the
  boundary
- do not create a second public modeling surface parallel to `llm-guided`
- do not rely on prompt text alone as the primary enforcement mechanism
- do not widen public tool discovery just to make drift “less likely”
- do not hardcode squirrel-specific geometry logic into the generic shield; the
  squirrel sessions are regression anchors, not the whole design
- do not replace deterministic inspection/assertion truth with VLM or planner
  prose

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-168-01](./TASK-168-01_Guided_State_Graph_And_Pre_Dispatch_Action_Shields.md) | Define the hard guided phase graph plus pre-dispatch action shields for profile-bound tool use |
| 2 | [TASK-168-02](./TASK-168-02_Typed_Orchestrator_Feedback_Contract_And_Emission_Points.md) | Add one compact typed feedback contract that tells controllers what to do, not do, and what will fail |
| 3 | [TASK-168-02-01](./TASK-168-02-01_Active_Workset_Compare_Scope_And_Coarse_To_Fine_Iteration.md) | Make compare/iterate target the active fragment/workset first, then escalate only when needed |
| 4 | [TASK-168-02-02](./TASK-168-02-02_Selective_Disclosure_Minimal_Control_Payloads_And_Gist_Followups.md) | Keep controller-facing outputs short by default and expose heavier packet detail only when rich mode, uncertainty, error, or hard-failure handling requires it |
| 5 | [TASK-168-03](./TASK-168-03_Session_Manifest_Prompt_Priority_And_Memory_Drift_Containment.md) | Surface a runtime-owned profile/session authority line on the existing status and feedback seams plus a prompt-priority model that outranks stale external memory |
| 6 | [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md) | Rewrite the relevant prompt/surface docs and close with focused plus repo-standard proof lanes |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/surfaces.py` | session contract, status surface, and static profile instruction owners | session-owned contract fields live in typed session/router state, while `surfaces.py` still shapes the static profile instructions many external agents read first |
| `server/adapters/mcp/transforms/visibility_policy.py` | profile visibility owner | visibility shaping already does action masking and is the natural place for phase-bound tool exposure rules |
| `server/adapters/mcp/guided_mode.py` | visibility diagnostics owner | it already computes the live visible surface and can expose the authoritative state snapshot |
| `server/adapters/mcp/router_helper.py` | routed execution and guard owner | corrected calls, deferred finalizers, and guided mutation tracking already converge here |
| `server/adapters/mcp/session_capabilities_flow.py`, `session_capabilities_registry.py`, `session_capabilities_runtime_glue.py`, `session_capabilities_bootstrap.py` | guided state machine owners | they already own current_step, required_checks, allowed_families, allowed_roles, and state transitions |
| `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/guided_flow.py` | typed response owners | `reference_orchestrator_feedback`, router status contracts, and guided flow state must stay on typed owner seams rather than ad hoc prose |
| `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/scene_guided_runtime.py` | user-facing guided response owners | these are the current public seams where controllers already receive compact next-step guidance and where the confinement family must extend the live contract |
| `server/adapters/mcp/guided_contract.py` | call-shape normalization owner | this is the current contract-hardening seam for legacy aliases and actionable failures |
| `server/adapters/mcp/prompts/*`, `_docs/_PROMPTS/*` | prompt asset owners | prompt assets must reinforce the runtime contract and stop teaching stale patterns |
| `tests/unit/adapters/mcp/`, `tests/unit/router/application/`, `tests/e2e/integration/`, `tests/e2e/router/`, `tests/e2e/vision/` | proof lanes | the confinement stack must prove itself on the real guided/reference/runtime paths, not only in prose |
| `_docs/_MCP_SERVER/README.md`, `_docs/_ROUTER/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/*` | canonical docs / governance owners | the public contract and task history must stay aligned with the implementation |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| guided phase graph and action shield | unit router/guided/runtime tests plus guided Streamable integration tests | this is where out-of-phase mutators and corrected-call drift must be stopped |
| typed orchestrator feedback | unit router/reference/scene guided lanes plus transport integration proof | clients need machine-readable “do/don't/won't/unblock” guidance on existing public seams |
| active workset / fragment compare | unit reference packet/planner lanes plus guided vision/runtime E2E | this is where huge whole-model outputs must become local, blocker-scoped compares |
| selective disclosure / minimal payloads | unit reference contract/planner lanes plus client-surface parity tests | compact mode must become truly compact for external controllers |
| prompt-priority and status authority projection | session/router contract tests plus prompt/provider/rendering tests | this is the repo-owned answer to stale `memory.md` and old prompt drift, and the session-owned contract already lives on router/session state seams |
| squirrel regression cases | guided manual handoff E2E plus reference-guided vision/runtime surfaces | the motivating failures must become pinned regressions |
| full profile closeout | pre-commit, repo-wide unit suite, repo-supported Blender E2E runner | the confinement layer is cross-cutting and must prove itself end to end |

## Acceptance Criteria

- `llm-guided` mutating calls outside the active phase/role envelope fail closed
  with explicit next-step guidance instead of silent drift
- a no-match guided manual goal can suppress unrelated workflow heuristics until
  the goal is cleared
- external controllers receive one short typed feedback contract on the
  relevant guided public seams that extends the shipped
  `reference_orchestrator_feedback` vocabulary instead of replacing it
- the feedback stays machine-readable and compact while still surfacing:
  - blocking reasons
  - next actions
  - next checkpoint / support path
  - exact unblock guidance
- staged compare / iterate phases can require compare/support actions before
  more modeling
- staged compare / iterate can stay local to the active fragment/workset by
  default and escalate to richer/full-scope output only when the current
  blocker still remains unresolved
- runtime-owned profile/session contract fields clearly outrank stale external
  memory and old prompt assumptions
- the squirrel regression family no longer reproduces the observed failures:
  - late compare entry
  - stale compare payload shape
  - invented `eye_pair` guided role
  - unrelated workflow heuristic trigger during guided manual build

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-168-04](./TASK-168-04_Profile_Contract_Rewrite_Validation_And_Closeout.md)
- latest post-closeout drift repair is tracked in
  [355. TASK-168 guided registry final drift repair](../_CHANGELOG/355-2026-05-16-task-168-guided-registry-final-drift-repair.md)

## Status / Board Update

- `TASK-168` is closed as `✅ Done` on the promoted board
- nested `TASK-168-*` execution slices are closed administratively under this
  umbrella closeout; any future work must be tracked as standalone follow-on
  tasks rather than reopened child leaves under the closed parent
- keep the overlap boundary with still-open `TASK-160` historical: `TASK-160`
  continues to own adjacent client-feedback/recovery UX, while `TASK-168`
  closed the profile-bound confinement contract layered on the shipped
  `reference_orchestrator_feedback` seam

## Validation Commands

- focused owner-lane unit proof:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
  (`108 passed`)
- repo-wide unit proof:
  `PYTHONPATH=. poetry run pytest ./tests/unit` (`3457 passed`)
- repo-wide pre-commit proof:
  `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  (passed)
- repo-supported Blender E2E proof:
  `poetry run python scripts/run_e2e_tests.py` (`477 passed, 3 skipped`)
- docs-only post-pass drift validation:
  `git diff --check` plus targeted consistency grep for stale
  legacy detail-disclosure wording and stale closeout text

## Validation Category

- runtime confinement repair with focused owner-lane, repo-wide unit,
  pre-commit, and Blender-backed E2E proof
- docs-only post-pass closeout wording validation
