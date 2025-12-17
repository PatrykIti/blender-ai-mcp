# Demo Task Prompt: Low‑Poly Medieval Well

Use this as the **user request** (`TASK:`) together with the system prompt from:
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`

---

## ✅ Copy/paste (TASK prompt)

```text
Create a low-poly medieval well with a roof (target ~1000–1500 tris, PC).

SCALE / PLACEMENT
- Units: meters.
- Place the asset on the ground: lowest point at Z=0, centered around (0,0).
- Target dimensions (you may adjust slightly, but keep it realistic):
  * outer stone rim diameter ~1.2 m
  * inner opening diameter ~0.8 m
  * stone rim height ~0.9 m
  * height to roof ridge ~2.2 m

RULES (important)
- Each element as a SEPARATE object (do not join everything into a single mesh).
- Naming: Well_<Part> (e.g., Well_StoneRim, Well_Post_L, Well_Axle, Well_Roller, Well_Crank, Well_Bucket, Well_Rope…).
- Put all objects into a single collection: Well.
- Low-poly: no subdivision, minimal segments (cylinders usually 6–8 sides; for parts that must read as round like the roller/bucket/rope, use ~8–12 sides).
- Max 3 materials: Stone / Wood / Metal (simple colors; no textures unless needed).
- Stability: build each major part once and then refine; do not repeatedly delete/recreate the stone rim.

STRUCTURE
1) Stone rim (OCTAGON)
   - Create a stone ring with an octagon outside and an octagon inside (a hollow opening).
   - Wall thickness ~0.15–0.20 m.
   - Add a small bevel/chamfer on edges for readability (still low-poly).

2) Two wooden posts with THROUGH HOLES for the winch axle
   - Two rectangular beams, symmetric on both sides of the rim.
   - EACH post must have a through hole for the axle.
   - The hole must have clearance vs the axle (e.g., axle 0.02–0.03 m, hole 0.03–0.04 m).

3) Gable roof
   - Simple gable roof supported by the posts.
   - If you add boards/shingles: keep it low-poly (few elements).

WINCH MECHANISM (must be mechanically logical)
4) Metal axle/rod
   - A rod passing through both post holes.
   - Let it protrude slightly on one side (for the crank).

5) Wooden roller ON the axle (must not touch the posts)
   - The roller sits on the axle between the posts.
   - The roller MUST be a round cylinder (circular cross-section), not a rectangular beam. Verify it in top view.
   - It must NOT touch the posts: leave clearance ~0.01–0.03 m on each side.
   - The axle passes through the roller.

6) Rope anchor/knot on the roller (safety)
   - Add a visible rope securing element on the roller: peg/knot/tie as a separate detail.

CRANK (CRITICAL — do not omit)
7) Half Z-shaped crank (NOT an L) + handle
   - The crank must have TWO 90° bends (a Z-style offset), not just one (L).
   - Goal: the handle is offset so it does not rub the post and looks mechanically correct.
   - Construction example: from axle end → offset outward → move along the axle direction → offset to the OPPOSITE side (so the top view makes a Z-like zig-zag) → handle.
   - Handle (grip) as a separate small cylinder at the end (metal or wood — choose consistently).

BUCKET + ROPE (game-ready, but with details)
8) Wooden bucket with metal bail/handle
   - Bucket must be round (cylindrical silhouette; e.g., 8–10 sides), not boxy.
   - Bucket must be hollow with an opening (no solid “cap” on top). Add wall thickness (~0.01–0.02 m) and a bottom.
   - Metal bail/handle as a separate object (thin metal rod; keep it round, not a cube).

9) Rope attached to the bucket handle
   - Rope as a separate object (cylinder 6–8 sides; do NOT use a scaled cube).
   - Rope is tied to the metal bucket handle (knot/tie).

10) Rope partially wound on the roller
   - Make at least 1–2 wraps around the roller (readable, low-poly).
   - Rope must read as a single continuous path: wraps must connect visually to the hanging rope (no disconnected floating rings).
   - The wrap diameter must match the roller (wrap sits on the roller surface, with rope thickness consistent with the hanging rope).
   - If you want to avoid a full helix: it’s OK to model a simplified “rope spool” band on the roller (Well_Rope_Spool) + a single hanging rope (Well_Rope_Down), but ensure they meet/overlap cleanly at the exit point and keep thickness consistent.
   - Then the rope goes down to the bucket.
   - The bucket must not intersect the stone; rope should look logical (taut or slightly slack).

CRITICAL: these elements MUST NOT be omitted
- Z-shaped crank (2 bends) + separate handle
- Axle through the post holes + roller on axle with clearance to posts
- Metal bucket handle
- Rope wound on the roller + visible rope anchor/knot on the roller

OUTPUT / REPORT
- Before the final report, do quick QA on critical shapes:
  * scene_isolate_object(object_name="Well_Roller") and verify in top/iso view that it is round (not boxy).
  * scene_isolate_object(object_name="Well_Bucket") and verify it is round AND visibly hollow/open.
  * For all rope parts: scene_inspect(action="topology", detailed=True, object_name=...) and fix degenerate/flat objects (Dimensions axis == 0.0) and unintended non-manifold edges.
  * scene_show_all_objects() after checks.
- At the end, provide a short YES/NO checklist for the “CRITICAL” section.
- List all objects and approximate tri count per object and total (target 1000–1500).
- If you exceed the budget: simplify roof/rope/bucket, but do NOT remove critical elements. Do not rebuild the whole asset just to hit the budget.
```
