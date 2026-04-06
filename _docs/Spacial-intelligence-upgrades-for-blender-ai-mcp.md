# Spatial intelligence upgrades for blender-ai-mcp

**The most impactful upgrade is not a new library — it's a structured scene graph with precomputed spatial relationships, served to the LLM in compact JSON using Chain-of-Symbol notation.** Research across robotics, embodied AI, and LLM spatial benchmarks converges on one finding: LLMs reason about 3D space far more accurately when given explicit coordinates, typed relationships, and symbolic notation than when given natural language descriptions or rendered images alone. Chain-of-Symbol prompting alone yields **+60.8% accuracy** on spatial tasks while reducing token usage by 65%. Combined with a deterministic spatial graph built from trimesh, scipy, and networkx on the MCP server side — and Blender's native BVHTree/bmesh on the addon side — this creates a truth-grounded context layer that transforms LLM spatial competence without touching the existing assertion layer.

---

## 1. The library stack: three tiers by implementation priority

### Tier 1 — implement first (maximum impact, easy integration)

**trimesh** (`pip install trimesh`) is the single highest-value addition to the MCP server. It offers the most Pythonic API of any geometry library, with lazy-computed mesh properties and a built-in scene graph. Key capabilities for blender-ai-mcp: `trimesh.proximity.closest_point()` for contact detection, `mesh.contains()` for containment testing, `trimesh.collision.CollisionManager` for multi-object collision queries (via FCL), `mesh.bounding_box_oriented` for OBB computation, and `mesh.is_watertight` / `mesh.is_winding_consistent` for mesh validity checks. The `trimesh.Scene` class provides a transform tree that maps cleanly to Blender's hierarchy. Install trimesh with optional extras (`pip install trimesh[easy]`) for pyembree-accelerated raycasting and Manifold3D boolean operations. The library's minimal core dependency is numpy alone, and it already uses scipy.spatial.cKDTree and rtree internally.

**scipy.spatial** (`pip install scipy`) provides the foundational spatial math: `KDTree` for nearest-neighbor queries between object centroids (answering "which objects are near which?"), `ConvexHull` for quick convexity analysis, `distance.cdist` for full pairwise distance matrices, and `transform.Rotation` for rotation validation and conversion. Since scipy is already a dependency of trimesh and most scientific Python stacks, it adds zero overhead.

**networkx** (`pip install networkx`) is the scene graph representation layer. Pure Python, runs on both addon and server side. The pattern: build a `nx.DiGraph()` where nodes are objects (with position, bbox, type attributes) and edges are typed spatial relationships (contact, support, containment, proximity, alignment). Serialize with `nx.node_link_data(G)` for JSON output. NetworkX's `connected_components()`, `descendants()`, and `ancestors()` answer structural queries like "what supports this object?" and "which objects form a connected group?"

### Tier 2 — implement next (high value, moderate complexity)

**Open3D** (`pip install open3d`, ~200MB) adds Intel Embree-powered `RaycastingScene` — the fastest available option for multi-mesh signed distance queries, occupancy testing, and closest-point-with-geometry-ID queries. The killer feature: `scene.compute_closest_points(query_points)` returns both the closest surface point and the geometry ID identifying *which* mesh was hit. This enables precise "what's the nearest object to this point?" queries across entire scenes. Also provides `get_oriented_bounding_box()` for OBB and `get_surface_area()`/`get_volume()` for mesh metrics. MCP server side only — too large for the Blender addon.

**rtree** (`pip install rtree`) provides O(log n) spatial indexing for bounding-box queries. For scenes with 10–1000 objects, `idx.intersection(bbox)` finds candidate overlaps in microseconds — essential as a pre-filter before expensive trimesh/Open3D geometric checks. Trimesh uses rtree internally, so it may already be installed.

**shapely** (`pip install shapely`) enables 2D footprint analysis by projecting 3D bounding boxes to XY-plane polygons. Its DE-9IM spatial predicates (`touches()`, `overlaps()`, `within()`, `covers()`) answer layout questions: "do these two objects' footprints overlap?" and "what's the clearance between them?" This is surprisingly useful for furniture placement and architectural layout tasks.

### Tier 3 — specialized, implement as needed

**libigl** (`pip install libigl`, v2.6.2) fills a niche no other library covers: `igl.winding_number()` provides robust containment testing even for **non-watertight meshes** (where trimesh's `contains()` fails). Also offers `igl.gaussian_curvature()`, `igl.principal_curvature()`, and `igl.exact_geodesic()` for shape analysis. The Python bindings are still beta-quality with limited Python version support, so treat this as optional.

**PyTorch3D** (`pip install pytorch3d`, Meta/FAIR, v0.7.9) provides `chamfer_distance()` for before/after mesh comparison, `mesh_laplacian_smoothing()` for quality scoring, and `mesh_normal_consistency()` for detecting flipped faces. These metrics are genuinely useful but come with a painful installation process (exact CUDA/PyTorch version matching required). For most use cases, equivalent metrics can be computed with numpy/scipy at lower dependency cost.

### Libraries to skip

**pyvista** and **vedo** (VTK-based) duplicate capabilities already covered by trimesh and Open3D with larger dependencies and more verbose APIs. **polyscope** is visualization-only — useful during development but not in production. **MinkowskiEngine** and **SparseConvNet** solve the wrong problem (RGB-D scan understanding, not Blender scene analysis). **numpy-stl** is superseded by trimesh's superior I/O.

---

## 2. Deep learning adds value in exactly two places

Classical geometry algorithms handle **95% of spatial reasoning** in a Blender automation context. Blender already knows what every object is, where it is, and how it's connected. Deep learning adds genuine value only for semantic understanding that has no deterministic solution.

**OpenShape** (NeurIPS 2023) or **Uni3D** (ICLR 2024 Spotlight) provide zero-shot 3D object classification by aligning point cloud embeddings with CLIP's text/image space. OpenShape achieves 46.8% accuracy on 1,156-category Objaverse-LVIS — orders of magnitude better than any fixed-category classifier. The pipeline: sample 10K points from a Blender mesh → normalize to unit sphere → encode with OpenShape → compute cosine similarity against any text label. **~100ms per object on GPU, ~500ms on CPU.** This answers "what is this unnamed imported mesh?" without a fixed vocabulary. Install requires MinkowskiEngine + PyTorch, so package as an optional module.

**PointNet++ part segmentation** (pretrained on ShapeNetPart) labels sub-object parts across 16 common categories — chair legs, table tops, lamp bases, airplane wings. Achieves ~85% mIoU. Inference is lightweight (~15ms GPU, ~100ms CPU, <1GB VRAM). This enables instructions like "select the chair legs" on imported geometry. The limitation: ShapeNetPart covers only 16 object categories with 50 part labels. For broader coverage, consider fine-tuning on PartNet (26,671 shapes, 24 categories).

Everything else — VoteNet, 3DETR, FCAF3D (3D object detection), SAM3D (3D segmentation), MinkowskiEngine (sparse convolution) — solves the inverse problem of understanding real-world captures. Blender already has the ground-truth scene graph. These models add complexity without meaningful capability for this use case.

---

## 3. What the research papers reveal about scene representations

### SceneCraft is the closest architectural precedent

**SceneCraft** (Hu et al., ICML 2024 Oral) is the most directly relevant paper. It converts text instructions into a **scene graph blueprint**, then generates Blender-executable Python scripts, then renders and visually verifies, then refines. The architecture: text → scene graph → spatial constraints → Blender code → visual verification → refinement, with a dual-loop structure — inner loop for per-scene iterative improvement using VLM feedback, outer loop for library learning (accumulating reusable script functions). This is essentially blender-ai-mcp's architecture with an additional library-learning mechanism.

**ConceptGraphs** (Gu et al., ICRA 2024) demonstrates the pipeline from structured scene graph to LLM-based task planning. Objects carry CLIP embeddings and text captions; edges are inferred by prompting an LLM with adjacent node descriptions. The graph serializes to text for the LLM planner. This "scene graph → text → LLM" pattern is the consensus approach across robotics and embodied AI.

**3DSSG** (Wald et al., CVPR 2020, IJCV 2022) establishes the relationship taxonomy: 41 edge types across support (standing_on, lying_on, hanging_on), attachment (attached_to, connected_to), spatial (above, below, close_to, next_to), comparison (bigger_than, same_material), and containment (inside). This taxonomy is directly implementable as edge types in a networkx scene graph.

### The robotics community converged on scene graphs plus constraint solvers

**SayPlan** (Rana et al., CoRL 2023) uses hierarchical 3D scene graphs for LLM-based task planning — the LLM searches a collapsed scene graph to find relevant subgraphs, then plans within that context. **Holodeck** (Yang et al., CVPR 2024) generates spatial layouts by having GPT-4 produce relational constraints ("bookshelf against wall," "desk near window") fed to an optimization solver. **VoxPoser** (Huang et al., CoRL 2023) has LLMs write Python code that composes 3D value maps rather than specifying coordinates directly. The consistent pattern: **LLMs should specify spatial intent as constraints, not coordinates**. A solver or deterministic system handles the geometry.

### LLMs fail at spatial reasoning in predictable ways

GPT-4o achieves only **27.5% accuracy** on left/right viewpoint questions. Performance on compositional spatial reasoning never exceeds **50%** even for frontier models. LLMs show "spatial hallucination" with coordinates and have static understanding of metric terms like "near" and "far." Symmetric/inverse relations (if A is left of B, then B is right of A) are regularly confused. Multi-hop spatial reasoning degrades rapidly with hop count.

**Chain-of-Symbol (CoS) prompting** (Hu et al., COLM 2023) is the single highest-impact mitigation: replacing natural language spatial descriptions with symbolic notation (`A → B [on_top], B → C [left_of]`) yields **+60.8% accuracy** (from 31.8% to 92.6% on Brick World) while reducing tokens by **65.8%**. The DSPy neural-symbolic pipeline (Wang et al., 2024) achieves **82–93%** on StepGame by separating semantic parsing (LLM) from logical inference (ASP solver).

---

## 4. Concrete tools and schemas to add

### `scene_get_spatial_graph` — the highest-priority new tool

This tool should return a precomputed spatial relationship graph in JSON. The computation pipeline: (1) Blender addon exports object transforms and bounding boxes, (2) MCP server computes pairwise relationships using trimesh proximity + scipy KDTree + bounding box analysis, (3) networkx builds and serializes the graph.

```json
{
  "meta": {
    "coordinate_system": "blender_world_z_up",
    "units": "meters",
    "timestamp": 1712400000,
    "object_count": 5
  },
  "nodes": [
    {
      "id": "Table",
      "type": "MESH",
      "position": [2.0, 0.0, 0.45],
      "dimensions": [1.2, 0.8, 0.9],
      "bbox_min": [1.4, -0.4, 0.0],
      "bbox_max": [2.6, 0.4, 0.9],
      "volume": 0.864,
      "parent": null,
      "collection": "Furniture"
    },
    {
      "id": "Lamp",
      "type": "MESH",
      "position": [2.1, 0.1, 1.15],
      "dimensions": [0.3, 0.3, 0.5],
      "bbox_min": [1.95, -0.05, 0.9],
      "bbox_max": [2.25, 0.25, 1.4],
      "volume": 0.045,
      "parent": null,
      "collection": "Furniture"
    }
  ],
  "edges": [
    {
      "subject": "Lamp",
      "predicate": "supported_by",
      "object": "Table",
      "contact_gap": 0.0,
      "overlap_xy": 0.09
    },
    {
      "subject": "Chair",
      "predicate": "adjacent_to",
      "object": "Table",
      "min_distance": 0.15,
      "facing": true
    }
  ]
}
```

**Relationship predicates to compute** (ordered by implementation priority):

- **supported_by / supports**: subject.bbox_min.z ≈ object.bbox_max.z AND XY overlap > threshold. Computed from bounding boxes alone — fast and reliable.
- **adjacent_to**: minimum distance between bounding boxes < threshold (0.1–0.5m depending on scale). Use rtree for candidate finding, trimesh for precise distance.
- **contains / inside**: subject fully within object's bounding box, confirmed by trimesh `mesh.contains()` or libigl winding number.
- **attached_to**: zero-distance contact between meshes (trimesh collision detection).
- **above / below / left_of / right_of**: axis-aligned bounding box center comparisons with margin thresholds.
- **aligned_with**: parallel axes or coplanar faces (dot product of principal axes > 0.95).
- **symmetric_with**: matching dimensions and mirrored positions across an axis.

### `scene_get_part_hierarchy` — enriched hierarchy tool

Extend existing hierarchy with computed semantic roles:

```json
{
  "root": "Chair",
  "children": [
    {"name": "Chair_Seat", "role": "support_surface", "bbox_relative": [0, 0, 0.4]},
    {"name": "Chair_Back", "role": "backrest", "bbox_relative": [0, -0.2, 0.7]},
    {"name": "Chair_Leg_FL", "role": "support_leg", "bbox_relative": [-0.2, 0.2, 0.0]}
  ],
  "canonical_frame": {
    "front": [0, 1, 0],
    "up": [0, 0, 1],
    "right": [1, 0, 0]
  }
}
```

Roles can be inferred heuristically: the lowest child is a "support_leg," the highest horizontal surface is a "support_surface," the vertical surface behind the seat is a "backrest." For unknown geometry, fall back to PointNet++ part segmentation if available.

### New assertion and quality tools

**`scene_assert_manifold(object_name)`**: Uses bmesh on the addon side to check `edge.is_manifold` for all edges, detect boundary edges, loose vertices, and degenerate faces. Returns pass/fail with specific problem locations.

**`scene_assert_clearance(obj_a, obj_b, min_distance)`**: Computes minimum distance between two meshes using trimesh proximity on the MCP server side. Asserts distance ≥ threshold.

**`scene_measure_surface_quality(object_name)`**: Returns polygon distribution (min/max/mean face area, aspect ratio histogram), edge length statistics, dihedral angle range, and normals consistency score. Computed via bmesh on addon side for topology, numpy on server side for statistics.

**`scene_measure_convexity(object_name)`**: Ratio of mesh volume to convex hull volume (via trimesh). Values near 1.0 indicate convex shapes; low values indicate complex concavities.

### Enriched bounding box: OBB over AABB

The existing `scene_get_bounding_box` should be upgraded to return both AABB and OBB. Oriented bounding boxes (OBB) from Open3D's `get_oriented_bounding_box()` or trimesh's `bounding_box_oriented` capture elongated objects far more accurately. The OBB center, extents, and rotation matrix give the LLM a much better sense of object shape and orientation:

```json
{
  "aabb": {"min": [1.4, -0.4, 0.0], "max": [2.6, 0.4, 0.9]},
  "obb": {
    "center": [2.0, 0.0, 0.45],
    "extents": [1.2, 0.8, 0.9],
    "rotation": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
  }
}
```

---

## 5. Router and prompting improvements grounded in research

### Chain-of-Symbol notation for scene context

The router's system prompt should adopt CoS-style symbolic scene descriptions instead of verbose natural language. Research shows this format is both more accurate for the LLM and more token-efficient:

```
SCENE STATE (Z-up, meters):
  Table @ [2.0, 0.0, 0.45] dims [1.2, 0.8, 0.9]
  Lamp @ [2.1, 0.1, 1.15] dims [0.3, 0.3, 0.5]
  Chair @ [3.2, 0.0, 0.40] dims [0.5, 0.5, 0.8]
RELATIONS:
  Lamp [supported_by] Table (gap=0.00)
  Chair [adjacent_to] Table (dist=0.15)
```

This format at ~50 tokens per object versus ~150+ for natural language descriptions lets the router maintain awareness of larger scenes within its context window.

### Spatial reasoning rules in the system prompt

Embed explicit spatial definitions to prevent the most common LLM failures:

```
SPATIAL RULES:
- "on top of" → subject.bbox_min.z == target.bbox_max.z AND XY overlap
- "centered on" → subject.center_xy == target.center_xy (±tolerance)
- "next to" → adjacent with gap ≤ scale_factor * 0.1
- "inside" → subject bbox fully within target bbox
- Always INSPECT before MOVE. Always VERIFY after MOVE.
- Compute target coordinates with explicit arithmetic, never estimate.
```

### Multi-step decomposition with mandatory verification

The router should decompose spatial commands into an INSPECT → COMPUTE → EXECUTE → VERIFY cycle. Research on plan verification (Hariharan et al., 2025) shows **96.5% of spatial errors are caught within 3 iterations**:

1. **INSPECT**: Call `scene_inspect` + `scene_measure_dimensions` to get current state with exact numbers
2. **COMPUTE**: Calculate target coordinates using explicit arithmetic in the reasoning trace (e.g., `target_z = base_bbox_max_z + part_height/2`)
3. **EXECUTE**: Call the manipulation tool with computed coordinates
4. **VERIFY**: Call `scene_assert_contact` / `scene_measure_distance` / `scene_assert_dimensions` to confirm the result matches intent
5. **CORRECT**: If verification fails, compute delta and retry (converges in 1–2 corrections typically)

### When to use which context modality

Research shows that **structured JSON with coordinates outperforms both natural language and rendered images** for precise spatial reasoning. However, rendered viewports add unique value for aesthetic and composition judgments. The router should follow this decision logic:

- **Numeric context** (`scene_measure_*`, `scene_assert_*`): For all placement, alignment, and distance tasks. This is the primary modality.
- **Structured text** (`scene_inspect`, `scene_get_spatial_graph`): For understanding scene structure, relationships, and planning multi-object operations.
- **Visual context** (`reference_compare_stage_checkpoint`): For aesthetic assessment, composition checks, and verifying that the overall scene "looks right" — tasks where the deterministic truth layer cannot help.

The ~1,500 token sweet spot identified in OpenEQA research means scene context should be compact by default and expanded only for the objects relevant to the current task.

---

## 6. Architecture split: what lives where

### Blender addon side (bpy main thread)

Everything requiring live Blender state or C-speed mesh access stays here:

- **BVHTree operations**: Raycasting, overlap detection between evaluated meshes (with modifiers applied). Uses `mathutils.bvhtree.BVHTree.FromObject()`. This is Blender's optimized C implementation and is faster than any external library for in-process queries.
- **KDTree queries**: Nearest-vertex queries via `mathutils.kdtree`. Build from mesh vertices, query in microseconds.
- **bmesh topology**: Non-manifold detection (`edge.is_manifold`), boundary edges, face connectivity, dihedral angles, vertex groups. Requires edit-mode or evaluated mesh access.
- **Scene graph extraction**: Object hierarchy (`obj.parent`, `obj.children`), collection membership, transform matrices (`obj.matrix_world`), bounding boxes (`obj.bound_box`), modifier stacks.
- **Bulk vertex export**: Use `mesh.vertices.foreach_get("co", array)` for numpy-speed extraction (~13.8M vertices/sec). This is the data bridge to the MCP server.

### MCP server side (external Python process)

Everything compute-intensive or library-dependent lives here:

- **Spatial relationship computation**: Pairwise distance matrices (scipy.spatial.cdist), bounding box intersection (rtree), contact detection (trimesh proximity), support graph inference. This would block Blender's UI thread if run addon-side.
- **Mesh analysis**: Watertight validation, volume/CoM computation, convex hull ratio, signed distance fields (trimesh). These need libraries unavailable in Blender's bundled Python.
- **Scene graph construction**: Build networkx graph from Blender-exported transforms + computed spatial relationships. Serialize to JSON for LLM consumption.
- **Persistent caching**: Store per-object analysis results keyed by mesh data hash (vertex count + modification timestamp). Avoid re-analyzing unchanged objects across multiple tool calls.
- **Token budgeting**: Compute how much scene context fits in the LLM's context window. Prune distant/irrelevant objects. Generate compact vs. full descriptions on demand.

### The scene context serializer pattern

The critical new component is a **lightweight serializer in the Blender addon** that exports a rich scene snapshot on demand:

```
Blender addon (foreach_get + obj properties)
    → JSON scene descriptor (transforms, bboxes, hierarchy, mesh stats)
    → TCP/JSON-RPC → MCP server
    → MCP enriches with spatial relations (trimesh/scipy/networkx)
    → Cached spatial graph
    → Compact CoS format → LLM context
```

Scene metadata serialization (transforms, bounding boxes, hierarchy for 100 objects) takes **<5ms** as JSON. Mesh vertex data for detailed analysis should use binary numpy `.npy` files written to a temp directory — the MCP server loads these into trimesh when needed. Shared memory (`multiprocessing.SharedMemory` by name) is an optimization for meshes exceeding 100K vertices, but TCP + temp files are sufficient initially.

**Cache invalidation**: Hash the scene state as `hash(object_count, sum_of_world_matrices, sum_of_mesh_vertex_counts)`. When the hash changes, re-export. Per-object mesh analysis caches invalidate on `mesh.is_updated` or vertex count change.

---

## 7. Key research papers informing these recommendations

The following papers most directly shaped these recommendations. **SceneCraft** (Hu et al., ICML 2024) demonstrates the complete text → scene graph → Blender code → visual verify → refine pipeline with library learning. **ConceptGraphs** (Gu et al., ICRA 2024) proves that text-serialized scene graphs are the most practical bridge between 3D scenes and LLM planners. **Chain-of-Symbol** (Hu et al., COLM 2023) shows symbolic spatial notation outperforms natural language by 60+ percentage points. **Inner Monologue** (Huang et al., CoRL 2022) establishes the closed-loop feedback pattern where scene state is re-inspected after every action. **SayPlan** (Rana et al., CoRL 2023) demonstrates hierarchical scene graph search for LLM task planning. **3DSSG** (Wald et al., CVPR 2020) provides the spatial relationship taxonomy. **Holodeck** (Yang et al., CVPR 2024) shows that constraint-based layout specification outperforms direct coordinate generation. **BlenderLLM** (Du et al., arXiv 2024) and **LL3M** (2025) confirm that iterative self-improvement with visual feedback dramatically improves Blender code generation accuracy. **VoxPoser** (Huang et al., CoRL 2023) establishes the code-as-spatial-reasoning pattern. **VADAR** (Marsili et al., CVPR 2025) demonstrates dynamic tool generation for spatial tasks. The IJCAI 2025 survey "How to Enable LLM with 3D Capacity?" provides a comprehensive taxonomy of the entire field.

---

## Prioritized implementation roadmap

**Phase 1 (weeks 1–3): Scene context layer — highest impact, lowest risk.**  
Add the scene context serializer to the Blender addon (export transforms, bboxes, hierarchy as JSON). Add `scene_get_spatial_graph` to the MCP server (compute support/adjacency/containment relationships using scipy KDTree + bounding box math). Integrate networkx for graph construction and serialization. Adopt CoS notation in the router system prompt. Add explicit spatial reasoning rules and the INSPECT→COMPUTE→EXECUTE→VERIFY decomposition pattern. These changes require only scipy and networkx (pure Python, zero dependency risk) and will transform the LLM's spatial reasoning accuracy.

**Phase 2 (weeks 4–6): Geometric analysis engine.**  
Add trimesh to the MCP server for mesh-level analysis: watertight validation, volume computation, proximity queries, OBB computation, convex hull ratio. Add `scene_assert_manifold`, `scene_assert_clearance`, `scene_measure_surface_quality`, `scene_measure_convexity`. Implement binary mesh transfer (foreach_get → .npy → trimesh). Add per-object analysis caching with hash-based invalidation.

**Phase 3 (weeks 7–9): Advanced spatial queries.**  
Add Open3D's RaycastingScene for multi-mesh distance queries and occupancy testing. Add rtree for bounding-box spatial indexing in large scenes. Add shapely for 2D footprint analysis. Implement the full spatial relationship taxonomy (support, containment, alignment, symmetry, facing) with configurable distance thresholds.

**Phase 4 (weeks 10–12): Optional semantic layer.**  
Package OpenShape or Uni3D as an optional module for zero-shot object classification on unnamed geometry. Add PointNet++ part segmentation for sub-object labeling. These are opt-in dependencies — the system works fully without them. Only relevant when the agent encounters imported or unnamed meshes.

## Conclusion

The research points to a counterintuitive insight: **the LLM doesn't need to "see" the 3D scene better — it needs to receive a more structured, symbolic description of spatial relationships it can reason about accurately.** The gap is not in perception but in representation. A precomputed spatial graph with typed edges (support, contact, containment, proximity), served in compact symbolic notation, eliminates the classes of spatial reasoning errors that plague current LLM orchestrators. The existing truth/assertion layer in blender-ai-mcp is architecturally correct and should remain the foundation. The upgrade path adds a structured context layer *above* the truth layer — not replacing deterministic checks but giving the LLM the structured spatial understanding it needs to call those checks intelligently. Classical geometry libraries (trimesh, scipy, networkx) deliver 95% of the value; deep learning adds marginal semantic enrichment for edge cases involving unknown geometry.
