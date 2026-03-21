# TASK-090-01: Prompt Asset Inventory and Taxonomy

**Parent:** [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Inventory the existing prompt assets and assign each one to an operating mode, audience, and session phase.

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
