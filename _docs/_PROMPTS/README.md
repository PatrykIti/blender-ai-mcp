# Prompt Templates

Copy/paste-ready prompt templates for LLMs controlling Blender via this MCP server.

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
> For utility/capture requests such as viewport screenshots or scene cleanup,
> do **not** force `router_set_goal(...)`; use the guided utility path instead:
> `search_tools(...)` -> `call_tool(name="scene_get_viewport"| "scene_clean_scene", ...)`.
> When a needed tool is already directly visible on the current surface/phase,
> call it directly instead of routing through `search_tools(...)` / `call_tool(...)`.
> Use `reference_images(...)` to attach/list/remove/clear goal-scoped reference
> images before asking the bounded vision layer to compare visible change.
> Use `search_tools` / `call_tool` only when discovery is actually needed on the
> shaped public surface, and use `manual_tools_no_router` when you explicitly
> want a manual non-router operating mode.
> `call_tool(...)` is not a bypass for hidden or phase-locked tools: if a tool
> is not currently exposed/discoverable on the shaped surface, guessing its name
> will still fail.
> `manual_tools_no_router` is a different operating mode, not an escape hatch
> for the active `llm-guided` shaped surface mid-session.
> Prefer workflow/macro tools over raw low-level atomics, and treat
> before/after capture plus deterministic verification as the normal way to
> judge whether a change is actually correct.
> For bounded recess/opening work, prefer `macro_cutout_recess` over manually
> creating and placing cutters plus boolean cleanup.
> For bounded relative placement/alignment work, prefer `macro_relative_layout`
> over transform-by-transform placement.
> For bounded finishing stacks, prefer `macro_finish_form` over manually
> chaining `modeling_add_modifier(...)` calls.
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
- **Workflow-first (Router Supervisor)** → [`WORKFLOW_ROUTER_FIRST.md`](./WORKFLOW_ROUTER_FIRST.md)
- **Demo task: low-poly medieval well** → [`DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`](./DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md)
- **Demo task: generic modeling template** → [`DEMO_TASK_GENERIC_MODELING.md`](./DEMO_TASK_GENERIC_MODELING.md)

Interpretation:

- normal production LLM usage should prefer the workflow-first path
- manual/no-router mode is an explicit exception, not the default product model
- practical `llm-guided` operating model:
  - build/workflow goal:
    `router_get_status(...)` -> `router_set_goal(...)` -> handle typed `needs_input` if present -> use visible build tools / macros
  - utility/capture request:
    do **not** force `router_set_goal(...)`; use the guided utility path instead
- vision-assisted build:
    `router_set_goal(...)` -> `reference_images(...)` -> macros / build tools -> `vision_assistant` on macro reports -> inspect/measure/assert confirmation
- if a tool is already directly visible on the current phase/surface, call it directly
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
- other first-choice bounded macro paths include:
  `search_tools(...)` -> `macro_cutout_recess` for recess/cutout/opening work
  `search_tools(...)` -> `macro_relative_layout` for align/place/contact-gap work
- if `router_set_goal(...)` returns `guided_handoff`, treat it as the typed continuation contract for what to call next on the current guided surface

## `llm-guided` Flow Summary

Use this summary when you need the shortest mental model for the production
guided surface:

1. If the request is a real build/workflow goal, start from `router_set_goal(...)`.
2. If the router returns `needs_input`, keep that clarification model-facing and
   answer with a follow-up `router_set_goal(..., resolved_params={...})`.
3. If the router returns `ready`, prefer:
   - visible direct tools
   - macro tools
   - `search_tools(...)` / `call_tool(...)` only when discovery is needed
4. If the request is utility/capture/scene-prep, skip `router_set_goal(...)`
   and use the guided utility path directly.
5. If the router returns `no_match` with `continuation_mode="guided_manual_build"`,
   continue on the guided build surface instead of inventing or importing a workflow.
   Use `guided_handoff.direct_tools` first and only fall back to `guided_handoff.discovery_tools` when direct tools are insufficient.
6. If vision should support the build, attach `reference_images(...)`, prefer
   macro paths that emit `capture_bundle`, and treat inspection/measure/assert
   as the truth layer after visual interpretation.
