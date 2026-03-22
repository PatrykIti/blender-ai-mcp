# Prompt Templates

Copy/paste-ready prompt templates for LLMs controlling Blender via this MCP server.

> Note: depending on your client, tool names may appear namespaced
> (e.g. `mcp__bleder-ai-mcp__inspect_scene`).
> On the `llm-guided` surface, prefer the public aliases used below:
> `check_scene`, `inspect_scene`, and `browse_workflows`.
> Legacy/internal surfaces may still expose the canonical internal names
> (`scene_context`, `scene_inspect`, `workflow_catalog`).
>
> `llm-guided` also starts from a small guided entry surface and expands with
> coarse session phases (`bootstrap` / `planning` / `build` / `inspect_validate`).
>
> On elicitation-capable clients, missing workflow parameters may be presented as
> structured clarification UI instead of free-form chat questions. Tool-only clients
> receive a typed `needs_input` fallback payload instead.

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
