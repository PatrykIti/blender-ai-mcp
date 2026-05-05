# TASK-162: Guided Hidden-Tool Error Semantics And Recovery Clarity

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** FastMCP Platform / Guided Client UX
**Estimated Effort:** Large
**Follow-on After:** [TASK-153](./TASK-153_Guided_Visibility_Authority_And_Manifest_Demotion.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Related:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)

## Objective

Turn one recurring guided-runtime failure mode into an explicit product contract:
when the client tries to call a tool through the guided discovery / `call_tool`
path, or retries a now-hidden direct guided tool after the surface changed, and
that tool is hidden by guided visibility or blocked by
`spatial_refresh_required`, the MCP surface should return a deterministic,
phase-aware recovery explanation instead of a generic `Unknown tool` story that
can be misread as a transport disconnect.

This umbrella covers the narrow, transcript-backed failure family observed on
the active `llm-guided` surface:

- the model receives a valid `guided_manual_build` handoff
- the flow later re-arms spatial refresh and narrows `allowed_families`
- the client still calls a now-hidden build/repair tool through `call_tool(...)`
- the server currently answers with a generic unknown-tool/proxy error
- the client can narrate that as “Blender disconnected” even though the MCP
  session is still healthy and returning `200 OK`
- the client can also see attachment-repair macros during `inspect_validate`,
  attempt to use them for a concrete geometry fix such as seating `Head`
  against `Body`, and then hit fail-closed guided family blocking once
  `spatial_refresh_required` narrows the allowed families again
- the client can also re-read `router_get_status(...)` after visibility narrows
  and still see the persisted `guided_handoff` alongside freshly recomputed
  `visibility_rules`, which can make historical handoff guidance look more
  current than it really is unless status semantics stay explicit

The delivery target is not broader “guided UX polish.” The target is a strict,
typed, repo-owned recovery contract for this exact hidden-tool / stale-context
path.

## Selected Direction

The product direction for this family is explicitly:

- **Option 2: hide tools that are not currently usable**

For this repo, that means:

- if guided execution policy will fail-close a mutating family during
  `spatial_refresh_required`, the shaped surface should stop exposing those
  mutators as directly visible tools for that moment
- the bounded refresh/support surface remains visible, including the read-only
  spatial helpers plus the already-supported recovery/workset tools that the
  current repo intentionally keeps during refresh (for example
  `collection_manage(...)`, `scene_clean_scene(...)`, and `reference_images(...)`)
- recovery messaging still matters, but the first UX fix is to avoid showing the
  model a tempting tool that the runtime will reject anyway

The motivating transcript is the current guided creature-build path where the
operator/model can still see repair macros such as
`macro_align_part_with_contact(...)` while trying to seat `Head` to `Body`
during `inspect_validate`, even though the active flow state has already
re-armed spatial refresh and the same macro can then fail closed.

## Business Problem

Recent guided creature-build transcripts show the same confusion loop:

1. `router_set_goal(...)` returns `continuation_mode="guided_manual_build"`
   together with `guided_handoff.direct_tools`, `supporting_tools`, and
   `guided_reference_readiness`.
2. The client correctly creates primary masses such as `Body` and `Head`.
3. The guided flow advances into a later step and sets
   `spatial_refresh_required=true`.
4. Visibility shaping hides build-family mutators until the required spatial
   checks are re-run.
5. The client still tries one of:
   - a stale tool name through `call_tool(...)`
   - a direct tool from an earlier handoff snapshot
   - a legacy/stale argument shape on a still-visible tool
6. The active MCP transport remains healthy, but the client can interpret the
   resulting tool error as a disconnect or session loss.

The current repo also has a sharper version of this problem on the
`inspect_validate` path:

- the shaped surface can still expose attachment-alignment macros in
  `GUIDED_INSPECT_ESCAPE_HATCH_TOOLS`
- the guided flow can then re-arm `spatial_refresh_required`
- execution policy can still fail-close `attachment_alignment` because
  `allowed_families` were narrowed for refresh

That is worse than a generic error-message issue because the model is shown a
repair path that the runtime already knows it should not allow.

This is a product problem because the runtime already knows the real recovery
path through `guided_flow_state.required_checks`, but the current failure
surface does not always communicate that path tightly enough at the exact moment
the client needs it. On the current creature build path that often includes
`scene_scope_graph(...)`, `scene_relation_graph(...)`, and
`scene_view_diagnostics(...)`; other domain/step combinations can expose a
narrower required-check set.

## Business Outcome

After this umbrella ships:

- repo-owned guided hidden-tool failures distinguish “tool is not visible right
  now” from “tool name does not exist”
- recovery instructions explicitly point to the next spatial-context tools when
  `spatial_refresh_required` is the cause
- mutating attachment-repair tools are hidden during `inspect_validate`
  refresh-barrier states whenever guided execution policy would fail-close
  `attachment_alignment`, instead of remaining visible and inviting retries
- `router_get_status(...)` preserves the persisted `guided_handoff` as
  historical intent, but no longer lets that persisted handoff contradict the
  currently authoritative live `visibility_rules`
- guided handoff / status semantics stay aligned with the repo’s already-landed
  search-first guidance, so stale persisted guidance does not undercut the live
  shaped surface after it changes
- integration tests prove that ordinary guided state transitions no longer look
  like disconnects to a well-behaved MCP client

## Explicit Non-Goals

- do not widen guided visibility just to reduce error frequency
- do not auto-run `scene_scope_graph(...)`, `scene_relation_graph(...)`, or
  `scene_view_diagnostics(...)` behind the client’s back
- do not create a parallel discovery mechanism outside FastMCP search/call-tool
  contracts
- do not treat real transport failures and ordinary tool-contract failures as
  the same class of event
- do not loosen strict argument validation for macros or scene tools only to
  hide client mistakes
- do not redesign direct top-level hidden-tool errors outside the guided
  discovery / `call_tool(...)` seam in this umbrella; broader client-surface
  work stays with `TASK-160`
- do not keep attachment-alignment tools visible during a refresh barrier just
  to “teach the client” via fail-closed errors; the chosen strategy is hiding,
  not visible-but-blocked nudging

## Relationship To Existing Board Work

- [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)
  is the broader umbrella for long-term guided client feedback and recovery UX.
- `TASK-162` is a narrow, transcript-backed corrective consumer inside that
  broader space.
- `TASK-162` should not wait for all of `TASK-160` because the hidden-tool /
  stale-context failure family is already concrete, localized, and testable in
  the current checkout.
- This umbrella must preserve the same responsibility split documented in
  `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`: FastMCP/discovery owns search,
  visibility, and client-surface semantics; the router owns deterministic flow
  policy; inspection tools remain the truth source.

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-162-01](./TASK-162-01_Guided_Hidden_Tool_Error_Classification_And_Recovery_Hints.md) | Classify guided hidden-tool/proxy failures in `search_surface.py` and emit deterministic recovery hints when `spatial_refresh_required` or phase visibility is the real cause |
| 2 | [TASK-162-02](./TASK-162-02_Guided_Handoff_And_Discovery_Contract_Clarification.md) | Align handoff/discovery wording and shaped-surface semantics so `direct_tools`, `supporting_tools`, and `call_tool(...)` do not encourage stale-name guessing after visibility changes, and hide mutating repair tools whenever a refresh barrier would fail-close them |
| 3 | [TASK-162-03](./TASK-162-03_Guided_Disconnect_Misclassification_Regression_Pack.md) | Add integration/docs regression coverage proving that hidden-tool and stale-argument paths surface as recoverable guided contract errors, not apparent disconnects, and that visible-vs-usable drift is gone on the transcript-backed creature path |

## Repository Touchpoint Table

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/discovery/search_surface.py` | FastMCP search/call proxy | Current owner of `call_tool(...)` proxy errors and the first place where generic `Unknown tool` semantics are produced |
| `server/adapters/mcp/transforms/visibility_policy.py` | Guided surface shaping | Owns the direct/supporting/discovery tool sets and the shaped visibility contract the client sees |
| `server/adapters/mcp/session_capabilities_flow.py` | Guided flow recovery semantics | Owns required spatial-check sets and step/family transitions that need to be reflected in the recovery message |
| `server/adapters/mcp/router_helper.py` | Guided execution fail-closed policy | Owns the final family gating that currently blocks visible-but-no-longer-allowed mutators during refresh barriers |
| `server/adapters/mcp/transforms/visibility_policy.py` | Guided handoff payload | Builds the `guided_handoff` contract, including direct/supporting/discovery tool sets and phase-specific messages |
| `server/adapters/mcp/areas/router.py` | Router adapter response assembly | Attaches the handoff payload and guided status details to the MCP-facing router response |
| `server/adapters/mcp/surfaces.py` | Live guided surface instructions | Owns the runtime surface text FastMCP clients actually read about `search_tools(...)` and `call_tool(...)` |
| `server/application/tool_handlers/router_handler.py` | Guided no-match shell | Still owns continuation mode / no-match goal semantics, but not the final adapter-owned handoff payload |
| `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py` | Search-first proxy regressions | Existing proof lane for “search first” behavior; must expand to hidden-tool recovery clarity |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | Guided surface parity | Existing end-to-end contract lane for `guided_manual_build` visibility and discovery |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable guided recovery | Existing lane for stale spatial context and reconnect-safe behavior |
| `tests/e2e/router/test_guided_manual_handoff.py` | Guided handoff baseline | Existing router-facing proof lane for initial `guided_manual_build` persistence; if this family changes status semantics, extend it with a later post-transition divergence case |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Handoff owner unit lane | Existing owner lane for guided handoff payload construction and visibility family shaping |
| `tests/unit/adapters/mcp/test_session_phase.py` | Session-state persistence lane | Existing owner lane for `guided_handoff` persistence and same-goal session state transitions |
| `tests/unit/adapters/mcp/test_router_elicitation.py` | Status/handoff exposure lane | Existing owner lane for baseline `router_get_status(...)` exposure; if this family changes live-vs-persisted semantics, extend it with a post-transition divergence case |
| `tests/unit/adapters/mcp/test_public_surface_docs.py` | Public docs parity | Existing owner lane for hard-checked guided doc wording and examples |
| `_docs/_MCP_SERVER/README.md` | Public MCP contract | Must document the distinction between unknown tools, hidden tools, stale guided surface transitions, and search-first recovery |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Tool discovery wording | Must stay aligned with shaped-surface discovery and macro recovery guidance |
| `_docs/_TASKS/README.md` | Board sync | Track the new umbrella on the active board while the corrective work is open |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|-------|-------------------------|-----|
| hidden-tool error classification | targeted unit + search-surface integration | the contract change lives in discovery/proxy behavior and must stay deterministic |
| guided handoff/discovery wording | unit + integration + docs parity | the shaped surface and the docs must say the same thing about direct vs discovery paths |
| disconnect-misclassification regressions | integration on stdio + Streamable HTTP | the observed failure mode is client-facing transport narration, not only unit semantics |
| docs/board updates | `git diff --check` + consistency grep | task/board/public docs must not drift once the corrective contract is documented |

## Runtime / Security Contract Notes

- Visibility levels remain authoritative. A tool hidden by guided visibility
  must not become callable merely because the proxy can name it.
- Visibility and execution policy must agree on mutating tool availability
  during refresh barriers. If execution policy would fail-close a family such as
  `attachment_alignment`, the shaped surface should not keep those tools
  directly visible at the same moment.
- Recovery hints may explain why the tool is unavailable and what to run next,
  but they must not reveal hidden mutating families beyond the current guided
  contract.
- The hidden-tool error path must stay safe across stdio and Streamable HTTP.
  Transport/session assumptions should not leak implementation-specific internals
  or stack traces to the operator.
- Compatibility shims for legacy `call_tool(tool=..., params=...)` should remain
  explicit and bounded; they must not become a loophole around shaped-surface
  visibility or strict argument validation.
- Recovery wording should stay deterministic and structured enough for reliable
  client handling across both discovery/proxy and repo-owned direct guided
  hidden-tool seams, but this umbrella does not require a brand-new typed error
  envelope beyond the existing `ToolError` surface.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`
- area-specific guided client docs only when the final contract changes their
  normative examples

## Changelog Impact

- add one dedicated `_docs/_CHANGELOG/*` entry when the implementation ships
- describe the change as guided error/recovery contract hardening, not as a
  transport rewrite

## Acceptance Criteria

- proxy-side hidden guided-tool failures no longer surface as a generic
  unknown-tool path when the server can deterministically explain that
  visibility or spatial refresh is the real reason
- the recovery path explicitly points to the current pending `required_checks`
  when `spatial_refresh_required` is active, rather than a hard-coded static
  tool list
- on the transcript-backed creature path during `inspect_validate`, tools such as
  `macro_align_part_with_contact(...)` and
  `macro_cleanup_part_intersections(...)` are no longer visible during
  refresh-barrier states where guided execution would fail-close
  `attachment_alignment`
- `router_get_status(...)` no longer lets persisted `guided_handoff` guidance
  contradict the currently authoritative live `visibility_rules` when the
  client re-checks status after a visibility transition
- shaped-surface handoff/status semantics stay aligned with the repo’s existing
  search-first guidance after the surface changes; the remaining delta is stale
  persisted guidance versus the live surface, not a repo-wide discovery-doc
  reversal
- integration coverage proves that a healthy MCP session returning tool errors is
  not misrepresented by the repo contract as a disconnect condition on the
  guided discovery / `call_tool(...)` seam, and that the transcript-backed
  direct-path failure is prevented earlier by hiding the invalid mutators
  where the transport/session harness makes that observable
- the final task docs leave implementation ownership, tests, and docs updates
  explicit enough that a future implementer does not need the original Claude
  transcript to understand the failure family

## Status / Board Update

- promote `TASK-162` on `_docs/_TASKS/README.md` as an active FastMCP / guided
  client UX umbrella
- keep execution details in the nested subtasks while the umbrella remains the
  board-level owner
