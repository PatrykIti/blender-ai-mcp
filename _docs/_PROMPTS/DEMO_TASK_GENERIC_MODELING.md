# Demo Task Prompt: Generic Modeling Template

Use this as the **user request** (TASK prompt). Pair it with one of:
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md` (manual tool-calling)
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md` (workflow-first)

---

## Copy/paste (TASK prompt)

```text
TASK:
Model: <DESCRIBE WHAT TO MODEL IN 1-3 SENTENCES>

AUTO-ASSUMPTIONS (if I do not specify otherwise)
- Units: meters.
- Style: realistic, mid-poly, clean hard-surface where appropriate.
- Parts: separate objects; no joining unless I explicitly ask.
- Organization: put all parts into one collection named after the asset.
- Naming: <Asset>_<Part> (example: Phone_Body, Phone_Screen, Phone_ButtonPower).

WORKFLOW DISCIPLINE (important)
1) Blockout the main volumes first. Do not add small details until the base shape is approved.
2) After each major part, verify dimensions and alignment (bbox checks + quick viewport check).
3) Ask for confirmation before making destructive rebuilds or deleting existing parts.

DETAILING RULES
- Use small consistent bevels/chamfers; avoid razor-sharp 90-degree edges.
- For cutouts/recesses: use boolean cutters as separate objects; apply only if needed.
- For round parts: ensure the silhouette is actually round in top/side view.
- Keep a small, consistent clearance between parts that should not intersect.

OUTPUT / REPORT
- Summarize: assumptions made + any open questions.
- List created objects + materials.
- Call out any areas that need my approval before proceeding.
```
```

