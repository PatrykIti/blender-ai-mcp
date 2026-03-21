# TASK-090-01-01: Core Prompt Asset Inventory and Taxonomy

**Parent:** [TASK-090-01](./TASK-090-01_Prompt_Asset_Inventory_and_Taxonomy.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Implement the core code changes for **Prompt Asset Inventory and Taxonomy**.

---

## Repository Touchpoints

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/*.md`

---

## Planned Work

- create `server/adapters/mcp/prompts/prompt_catalog.py`
- classify prompts for:
  - onboarding
  - router-first use
  - manual-tool use
  - validation
  - troubleshooting
---

## Acceptance Criteria

- every prompt asset has ownership, tags, and a target operating mode
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
