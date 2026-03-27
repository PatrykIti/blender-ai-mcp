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
> Use `reference_images(...)` to attach/list/remove/clear goal-scoped reference
> images before asking the bounded vision layer to compare visible change.
> Use `search_tools` / `call_tool` to discover and invoke tools on the shaped
> public surface, and use `manual_tools_no_router` when you explicitly want a
> manual non-router operating mode.
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
- a typical guided macro flow is:
  `router_set_goal(...)` -> `browse_workflows(...)` / `search_tools(...)` -> `macro_finish_form` -> `inspect_scene(...)` + measure/assert verification
- a typical guided utility capture flow is:
  `search_tools(query="viewport screenshot save file")` -> `call_tool(name="scene_get_viewport", arguments={...})`
- a typical guided utility scene-prep flow is:
  `search_tools(query="clean reset fresh scene")` -> `call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})`
- other first-choice bounded macro paths include:
  `search_tools(...)` -> `macro_cutout_recess` for recess/cutout/opening work
  `search_tools(...)` -> `macro_relative_layout` for align/place/contact-gap work
