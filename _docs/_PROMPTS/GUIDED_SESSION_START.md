# Guided Session Start (`llm-guided`)

Use this as a short starter prefix before a real `llm-guided` modeling session,
especially when the client tends to get lost between router flow, discovery,
and hidden tools.

---

## ✅ Copy/paste prefix

```text
You are operating on the `llm-guided` shaped MCP surface.

Fail-safe rules:
- Start from the active MCP profile and currently visible/discoverable tools.
- Do not guess hidden/internal tool names.
- `call_tool(...)` is not a bypass for hidden or phase-locked tools.
- If `call_tool(...)` returns `Unknown tool`, stop guessing names and re-check the current phase/surface.
- For real build goals, start from `router_get_status()` and then `router_set_goal(...)`.
- For utility/capture requests, do not force `router_set_goal(...)`; use the guided utility path.
- If the router returns `needs_input`, answer it with a follow-up `router_set_goal(..., resolved_params={...})`.
- If the router pushes an obviously irrelevant workflow for the current task, stop and report that blocker instead of improvising with hidden tools.
- Use directly visible tools first.
- Use `search_tools(...)` / `call_tool(...)` only when discovery is actually needed.
- Do not switch mentally into `manual_tools_no_router` while still using the `llm-guided` profile.
- Do not read repo code as a substitute for the active MCP surface contract.

Recovery protocol:
1. `Unknown tool` -> re-check phase/surface, do not guess again.
2. Wrong workflow path -> stop and report the bad workflow match.
3. Missing reference path or missing required user input -> report the missing input explicitly.
4. If `guided_handoff` is present -> use `guided_handoff.direct_tools` first.
```

---

## Intended Use

This is not a replacement for the main workflow prompt. It is a short stabilizer
prefix meant to be combined with:

- `workflow_router_first`
- your concrete task prompt

Use `manual_tools_no_router` only when you intentionally switch to the manual
non-router operating mode.
