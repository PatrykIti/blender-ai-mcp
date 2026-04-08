# Prompt Templates

Copy/paste-ready prompt templates for LLMs controlling Blender via this MCP server.

`_docs/_PROMPTS/` is the canonical prompt library for this repo's MCP-facing
operating model. When a client tends to drift, start from these assets instead
of improvising a new instruction stack from scratch.

> Note: depending on your client, tool names may appear namespaced
> (e.g. `mcp__bleder-ai-mcp__inspect_scene`).
> On the `llm-guided` surface, prefer the public aliases used below:
> `check_scene`, `inspect_scene`, `configure_scene`, and `browse_workflows`.
> Legacy/internal surfaces may still expose the canonical internal names
> (`scene_context`, `scene_inspect`, `scene_configure`, `workflow_catalog`).
>
> `llm-guided` also starts from a small guided entry surface and expands with
> coarse session phases (`bootstrap` / `planning` / `build` / `inspect_validate`).
> The current guided entry surface is:
> `router_set_goal`, `router_get_status`, `browse_workflows`, `reference_images`,
> `search_tools`, `call_tool`, `list_prompts`, and `get_prompt`.
> On production-oriented surfaces, start from `router_set_goal(...)` first for
> real build/workflow goals and treat the rest of the public surface in the
> context of that active goal.
> Treat the separate read-only spatial artifacts
> `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
> `scene_view_diagnostics(...)` as standard guided 3D orientation support tools.
> Use them instead of trying to infer anchor/pair structure or
> framing/occlusion state from prose alone.
> For utility/capture requests such as viewport screenshots or scene cleanup,
> do **not** force `router_set_goal(...)`; use the guided utility path instead:
> `search_tools(...)` -> `call_tool(name="scene_get_viewport"| "scene_clean_scene", ...)`.
> If you discover stale scene state only after entering build phase,
> `scene_clean_scene(...)` is also an allowed guided recovery hatch; cleanup
> before the goal is still preferred, but build-phase cleanup is no longer
> treated as "tool does not exist".
> When a needed tool is already directly visible on the current surface/phase,
> call it directly instead of routing through `search_tools(...)` / `call_tool(...)`.
> Use `reference_images(...)` to attach/list/remove/clear goal-scoped reference
> images before asking the bounded vision layer to compare visible change.
> If the goal is not active yet, or if `router_set_goal(...)` is still blocked
> on `needs_input`, `reference_images(action="attach", ...)` can now stage
> pending references that will be adopted automatically when the guided goal
> session becomes ready. If the same blocked goal already has active refs, the
> new staged refs stay separate until readiness returns; do not reattach old
> refs just to keep them visible.
> If a ready session still lists explicit pending refs for another goal, you
> may remove/clear them from the same `reference_images(...)` surface; that
> cleanup now updates pending state as well instead of leaving broken records.
> Use `guided_reference_readiness` from `router_set_goal(...)` or
> `router_get_status(...)` before calling
> `reference_compare_stage_checkpoint(...)` /
> `reference_iterate_stage_checkpoint(...)`. If `compare_ready` /
> `iterate_ready` is `false`, follow `next_action` instead of improvising
> recovery steps.
> Use `search_tools` / `call_tool` only when discovery is actually needed on the
> shaped public surface, and use `manual_tools_no_router` when you explicitly
> want a manual non-router operating mode.
> If a tool is not already directly visible and you did not just discover it
> through `search_tools(...)`, do not send its guessed name to `call_tool(...)`.
> `call_tool(...)` is not a bypass for hidden or phase-locked tools: if a tool
> is not currently exposed/discoverable on the shaped surface, guessing its name
> will still fail.
> The canonical `call_tool(...)` wrapper is `name=...` plus `arguments=...`.
> Legacy `tool=...` / `params=...` aliases are compatibility-only and should
> not be the documented default form.
> `manual_tools_no_router` is a different operating mode, not an escape hatch
> for the active `llm-guided` shaped surface mid-session.
> The same guided contract hardening now applies on directly visible tools as
> well as through `call_tool(...)`: batch-like `reference_images(...)` attach
> drift, legacy `collection_manage(..., name=...)`, legacy cleanup split flags,
> and unsupported primitive shortcuts now return actionable guidance instead of
> raw schema noise on the guided surface.
> Prefer workflow/macro tools over raw low-level atomics, and treat
> before/after capture plus deterministic verification as the normal way to
> judge whether a change is actually correct.
> For bounded recess/opening work, prefer `macro_cutout_recess` over manually
> creating and placing cutters plus boolean cleanup.
> For bounded relative placement/alignment work, prefer `macro_relative_layout`
> over transform-by-transform placement.
> For bounded finishing stacks, prefer `macro_finish_form` over manually
> chaining `modeling_add_modifier(...)` calls.
> `reference_images(action="attach", ...)` is one-reference-per-call on the
> public guided surface. Use one `source_path` per attach call; do not pass
> batch shapes such as `images=[...]` or `source_paths=[...]`.
> `collection_manage(...)` uses `collection_name` as the canonical public
> target name, not `name`.
> `modeling_create_primitive(...)` uses the public arguments
> `primitive_type`, `radius`/`size`, `location`, `rotation`, and optional
> `name`. For non-uniform scale, create the primitive first and then use
> `modeling_transform_object(scale=...)`. For collection placement, move/link
> the created object with `collection_manage(...)` after creation.
>
> On elicitation-capable clients, missing workflow parameters may be presented as
> structured clarification UI instead of free-form chat questions. Tool-only clients
> receive a typed `needs_input` fallback payload instead.
>
> For normal production usage, prefer workflow/macro tools over raw low-level
> atomics, and treat before/after capture plus deterministic verification as the
> standard way to judge whether a change is actually correct.

## How to use (Claude / ChatGPT)

**Recommended:** put the chosen template into your client’s **System Prompt** / **Project Instructions** / **Custom Instructions** area.
Then, in the chat, send only the actual request (what you want to model).

**If you don’t have a System Prompt field:** paste the template as the **first part** of your message, and put your request at the end under a clear marker, e.g.:

```text
<PASTE TEMPLATE HERE>

TASK:
Model a smartphone with separate parts: body, screen, camera bump, 3 lenses, power + volume buttons. Realistic size.
```

## 📚 Index

- **Manual tool-calling (no Router / no workflows)** → [`MANUAL_TOOLS_NO_ROUTER.md`](./MANUAL_TOOLS_NO_ROUTER.md)
- **Short fail-safe starter for `llm-guided`** → [`GUIDED_SESSION_START.md`](./GUIDED_SESSION_START.md)
- **Workflow-first (Router Supervisor)** → [`WORKFLOW_ROUTER_FIRST.md`](./WORKFLOW_ROUTER_FIRST.md)
- **Reference-guided creature build** → [`REFERENCE_GUIDED_CREATURE_BUILD.md`](./REFERENCE_GUIDED_CREATURE_BUILD.md)
- **Demo task: low-poly medieval well** → [`DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`](./DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md)
- **Demo task: generic modeling template** → [`DEMO_TASK_GENERIC_MODELING.md`](./DEMO_TASK_GENERIC_MODELING.md)

Interpretation:

- normal production LLM usage should prefer the workflow-first path
- when the client tends to drift on `llm-guided`, prepend `guided_session_start`
  before the main workflow prompt; this is the generic search-first stabilizer
  asset for the shaped surface
- manual/no-router mode is an explicit exception, not the default product model
- `recommended_prompts` now uses the active phase/profile plus explicit
  session goal context, so creature-oriented guided goals can surface the
  native `reference_guided_creature_build` prompt asset without separate docs-only lookup
- practical `llm-guided` operating model:
  - build/workflow goal:
    `router_get_status(...)` -> `router_set_goal(...)` -> handle typed `needs_input` if present -> use visible build tools / macros
  - utility/capture request:
    do **not** force `router_set_goal(...)`; use the guided utility path instead
- vision-assisted build:
    `router_set_goal(...)` -> `reference_images(...)` -> macros / build tools -> `vision_assistant` on macro reports -> inspect/measure/assert confirmation
- staged manual/reference-guided build:
    checkpoint capture -> `reference_compare_checkpoint(...)`, `reference_compare_current_view(...)`, `reference_compare_stage_checkpoint(...)`, or `reference_iterate_stage_checkpoint(...)` -> use bounded mismatch/correction hints for the next iteration
    only call staged compare/iterate when `guided_reference_readiness.compare_ready == true`
    prioritize `loop_disposition`, then `refinement_route`, then `refinement_handoff`, then `correction_candidates`, then `truth_followup`, then `action_hints`, then `correction_focus`, then `silhouette_analysis`
    keep `scene_scope_graph(...)`, `scene_relation_graph(...)`, and `scene_view_diagnostics(...)` in the normal working set for 3D orientation during active guided goals
    if the next correction still depends on knowing the structural anchor or explicit pair relations, call `scene_scope_graph(...)` and/or `scene_relation_graph(...)` instead of overloading the checkpoint payload
    if the next correction still depends on whether the target is off-frame, poorly centered, or occluded from the active camera/viewport, call `scene_view_diagnostics(...)` instead of guessing from the screenshot alone
    if `reference_iterate_stage_checkpoint(...)` returns `loop_disposition="inspect_validate"`, stop free-form modeling and switch to inspect/measure/assert before continuing
    if staged compare degrades but strong deterministic truth findings still remain, use the same inspect/measure/assert handoff instead of improvising another large free-form correction
- if a tool is already directly visible on the current phase/surface, call it directly
- if a tool is not already directly visible, run `search_tools(...)` before
  `call_tool(...)`
- only use `search_tools(...)` / `call_tool(...)` when discovery is actually needed
- `call_tool(...)` cannot summon hidden internal tools by guessed name; `Unknown tool`
  on `llm-guided` usually means the current phase/surface is wrong
- do not switch to `manual_tools_no_router` mentally while still using the
  `llm-guided` shaped profile; if you need manual/no-router behavior, use the
  matching manual profile/session intentionally
- a typical guided macro flow is:
  `router_set_goal(...)` -> `browse_workflows(...)` / `search_tools(...)` -> `macro_finish_form` -> `inspect_scene(...)` + measure/assert verification
- a typical guided utility capture flow is:
  `search_tools(query="viewport screenshot save file")` -> `call_tool(name="scene_get_viewport", arguments={...})`
- a typical guided utility scene-prep flow is:
  `search_tools(query="clean reset fresh scene")` -> `call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})`
- if stale scene state is discovered only after entering build/manual phase,
  `scene_clean_scene(...)` remains a valid recovery hatch on the shaped build
  surface; prefer using it directly when it is already visible
- build-phase cleanup is still allowed when recovery is needed
- use `keep_lights_and_cameras` as the canonical public cleanup flag; the older
  split `keep_lights` / `keep_cameras` form is legacy compatibility only
- use one `reference_images(action="attach", source_path=...)` call per
  reference image; do not send `images=[...]` batches on the guided surface
- use `collection_manage(action=..., collection_name=...)`, not
  `collection_manage(..., name=...)`, as the canonical public form
- use `modeling_create_primitive(primitive_type=..., radius|size=..., location=..., rotation=..., name=...)`
  as the public primitive shape; if you need non-uniform scale, apply it in a
  second step with `modeling_transform_object(scale=...)`
- other first-choice bounded macro paths include:
  `search_tools(...)` -> `macro_cutout_recess` for recess/cutout/opening work
  `search_tools(...)` -> `macro_relative_layout` for align/place/contact-gap work
- if `router_set_goal(...)` returns `guided_handoff`, treat it as the typed continuation contract for what to call next on the current guided surface
- if hybrid loop responses expose `refinement_route` / `refinement_handoff`,
  treat those as the bounded family-selection hints for whether to stay on
  macro/modeling/mesh or move into a narrow sculpt-region path
- `guided_flow_state` is the server-driven guided flow contract for the active
  session; prompts support it, but do not replace it
- before broad build actions, inspect:
  - `guided_flow_state.domain_profile`
  - `guided_flow_state.current_step`
  - `guided_flow_state.required_checks`
  - `guided_flow_state.next_actions`
- use the `required prompt bundle` and `preferred prompt bundle` named in
  `guided_flow_state` as prompt asset selection guidance
- current server-driven guided flow domain overlays are:
  - `generic`
  - `creature`
  - `building`

## `llm-guided` Flow Summary

Use this summary when you need the shortest mental model for the production
guided surface:

1. If the request is a real build/workflow goal, start from `router_set_goal(...)`.
2. If the router returns `needs_input`, keep that clarification model-facing and
   answer with a follow-up `router_set_goal(..., resolved_params={...})`.
   If the suggested workflow is clearly wrong and the payload is asking for
   `workflow_confirmation`, you may answer with `guided_manual_build` to decline
   that workflow and continue manually on the guided build surface.
3. If the router returns `ready`, prefer:
   - visible direct tools
   - macro tools
   - `search_tools(...)` / `call_tool(...)` only when discovery is needed
4. If the request is utility/capture/scene-prep, skip `router_set_goal(...)`
   and use the guided utility path directly.
5. If the router returns `no_match` with `continuation_mode="guided_manual_build"`,
   continue on the guided build surface instead of inventing or importing a workflow.
   Use `guided_handoff.direct_tools` first and only fall back to `guided_handoff.discovery_tools` when direct tools are insufficient.
   If `guided_handoff.recipe_id == "low_poly_creature_blockout"`, treat that as
   a smaller modeling/mesh-first creature blockout surface rather than the broad generic build phase.
6. If vision should support the build, attach `reference_images(...)`, prefer
   macro paths that emit `capture_bundle`, and treat inspection/measure/assert
   as the truth layer after visual interpretation.
7. Before staged compare/iterate, check `guided_reference_readiness`:
   - if `compare_ready` / `iterate_ready` is `true`, proceed
   - otherwise follow `next_action` and do not use `goal_override` as a staged
     session substitute

## Guided Flow State And Prompt Bundles

On `llm-guided`, prompt templates are no longer the only place where guided
sequencing lives. The server now owns a machine-readable `guided_flow_state`
contract.

- if a needed build tool is missing, call `router_get_status()` and inspect
  `guided_flow_state` before guessing names into `call_tool(...)`
- if `guided_flow_state.step_status == "blocked"`, complete
  `guided_flow_state.required_checks` first and follow
  `guided_flow_state.next_actions`
- the server may keep build visibility step-gated during
  `establish_spatial_context`, so prompt text must not override that gating
- `required_prompts` = required prompt bundle names for the current
  flow/domain/step
- `preferred_prompts` = strong recommendations for the current flow/domain/step
- prompt bundles support the server-driven guided flow instead of replacing it
