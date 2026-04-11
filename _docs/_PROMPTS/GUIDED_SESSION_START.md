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
- Treat `_docs/_PROMPTS/` prompt assets as the canonical operating library for this surface.
- Do not guess hidden/internal tool names.
- `call_tool(...)` is not a bypass for hidden or phase-locked tools.
- If a tool is not already directly visible and you did not just discover it through `search_tools(...)`, do not send it to `call_tool(...)`.
- If `call_tool(...)` returns `Unknown tool`, stop guessing names and re-check the current phase/surface.
- For real build goals, start from `router_get_status()` and then `router_set_goal(...)`.
- For utility/capture requests, do not force `router_set_goal(...)`; use the guided utility path.
- Cleanup rule: prefer `scene_clean_scene(...)` before `router_set_goal(...)`, but if scene drift is discovered after entering build phase, the same tool is an allowed recovery hatch on the guided build surface.
- If the router returns `needs_input`, answer it with a follow-up `router_set_goal(..., resolved_params={...})`.
- If `guided_flow_state` is present, treat `current_step`, `allowed_families`, `allowed_roles`, `missing_roles`, and `next_actions` as the active execution contract.
- If `reference_images(...)` are attached for the active guided goal, treat them as the primary grounding input before deciding the first primary masses, silhouette, and placement.
- Use full semantic object names such as `Body`, `Head`, `Tail`, `ForeLeg_L`, and `HindLeg_R`; avoid opaque abbreviations like `ForeL` / `HindR`.
- On `llm-guided`, the server may warn on weak role-sensitive names and block clearly opaque placeholder names such as `Sphere` / `Object`; when that happens, rename or create the object using one of the suggested semantic names.
- Do not call `scene_scope_graph(...)`, `scene_relation_graph(...)`, or `scene_view_diagnostics(...)` with no explicit scope and assume that means “inspect the whole scene”.
- Do not treat a default placeholder like `Cube` or the root `Collection` as a meaningful guided target/workset by itself.
- Treat the initial spatial gate as meaningful only after a real target scope exists, e.g. primary masses already exist or the build collection already exists.
- If the scene is empty after cleanup, follow `bootstrap_primary_workset` /
  `create_primary_workset` and create the first semantic primary masses before
  trying to satisfy spatial checks.
- If the server says the current step is `create_primary_masses`, do not jump ahead to ears, paws, facade openings, polish, or finish work.
- For role-sensitive build calls, use either `guided_register_part(object_name=..., role=...)` or `guided_role=...` on the build tool call.
- If the session has already moved to a later guided step, the server may still allow bounded refinement of already-created primary masses or utility/workset operations when they remain part of the same active workset.
- If a spatial graph/view response says it was read-only but did not satisfy
  the active guided scope, rerun that same check with the expected scope from
  the message before continuing.
- If the router pushes an obviously irrelevant workflow for the current task, stop and report that blocker instead of improvising with hidden tools.
- Use directly visible tools first.
- Default to `search_tools(...)` before `call_tool(...)` for any non-entry tool that is not already directly visible.
- Use `search_tools(...)` / `call_tool(...)` only when discovery is actually needed.
- Do not switch mentally into `manual_tools_no_router` while still using the `llm-guided` profile.
- Do not read repo code as a substitute for the active MCP surface contract.

Recovery protocol:
1. `Unknown tool` -> re-check phase/surface, do not guess again.
2. Wrong workflow path -> stop and report the bad workflow match.
3. Missing reference path or missing required user input -> report the missing input explicitly.
4. If `guided_handoff` is present -> use `guided_handoff.direct_tools` first.
5. If a build call is blocked by family/role policy -> inspect `allowed_families`, `allowed_roles`, and `missing_roles` instead of retrying with guessed tool names.
6. If spatial tools are needed, provide explicit scope with `target_object=...`, `target_objects=[...]`, or `collection_name=...`.
```

---

## Intended Use

This is not a replacement for the main workflow prompt. It is a short stabilizer
prefix meant to be combined with:

- `workflow_router_first`
- your concrete task prompt

Use `manual_tools_no_router` only when you intentionally switch to the manual
non-router operating mode.
