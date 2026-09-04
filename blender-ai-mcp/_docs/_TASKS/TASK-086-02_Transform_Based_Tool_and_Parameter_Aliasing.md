# TASK-086-02: Transform-Based Tool and Parameter Aliasing

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md)

---

## Objective

Apply tool-name and parameter-name aliasing through the transform pipeline instead of duplicating handler logic or forking the business layer.

## Completion Summary

This slice is now closed.

- tool aliases and argument aliases are applied through transforms
- hidden/expert-only arguments are hidden on `llm-guided`
- parity now covers direct public calls, discovered calls, and versioned public lines

---

## Planned Work

- create:
  - `server/adapters/mcp/transforms/naming.py`
  - `server/adapters/mcp/transforms/public_params.py`
  - `tests/unit/adapters/mcp/test_aliasing_transform.py`

### FastMCP Mechanism

Prefer built-in FastMCP `ToolTransform` with `ArgTransform`-style argument reshaping.
Custom code in this repo should mostly translate manifest rules into transform configuration.

---

## Pseudocode

```python
alias_map = {
    "scene_inspect": PublicToolAlias(
        public_name="inspect_scene",
        param_aliases={"object_name": "target_object"},
    )
}
```

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-086-02-01](./TASK-086-02-01_Core_Transform_Parameter_Aliasing.md) | Core Transform-Based Tool and Parameter Aliasing | Core implementation layer |
| [TASK-086-02-02](./TASK-086-02-02_Tests_Transform_Parameter_Aliasing.md) | Tests and Docs Transform-Based Tool and Parameter Aliasing | Tests, docs, and QA |

---

## Acceptance Criteria

- aliases are applied at the public surface layer
- internal handler signatures remain stable

---

## Atomic Work Items

1. Map manifest aliases into FastMCP tool transforms.
2. Map public argument aliases and hidden defaults into argument transforms.
3. Add parity tests for direct calls, search-discovered calls, and versioned calls.
