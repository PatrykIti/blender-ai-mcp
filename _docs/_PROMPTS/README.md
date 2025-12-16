# Prompt Templates

Copy/paste-ready prompt templates for LLMs controlling Blender via this MCP server.

> Note: depending on your client, tool names may appear namespaced (e.g. `mcp__bleder-ai-mcp__scene_inspect`)
> but the underlying tool identifiers match the ones referenced below (e.g. `scene_inspect`).

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
