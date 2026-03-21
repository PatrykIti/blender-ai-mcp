# TASK-089-01: Contract Catalog and Response Guidelines

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Define the shared contract catalog and the rules for when tools return:

- pure structured payloads
- structured payloads plus a human summary
- legacy text-only output as a compatibility fallback

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/__init__.py`
  - `server/adapters/mcp/contracts/base.py`
  - `server/adapters/mcp/contracts/serializers.py`
  - `server/adapters/mcp/contracts/renderers.py`
  - `tests/unit/adapters/mcp/test_contract_base.py`

---

## Acceptance Criteria

- the adapter layer has one shared response-design policy instead of per-tool conventions

---

## Atomic Work Items

1. Define the base contract envelope and serializer rules.
2. Add the shared renderer set: `structured`, `structured_plus_summary`, `legacy_text`.
3. Add tests proving the same payload can be rendered differently by profile.
