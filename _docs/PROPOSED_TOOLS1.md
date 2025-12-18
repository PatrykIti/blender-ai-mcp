# Blender AI MCP — Proposed Missing Tools
## Priority Implementation Backlog

---

# 🔴 P0 — CRITICAL (Unlocks 80% of modeling tasks)

## mesh_transform_selected

```python
def mesh_transform_selected(
    translate: list[float] = None,  # [x, y, z] offset in local space
    scale: list[float] = None,      # [x, y, z] scale factors
    rotate: list[float] = None,     # [x, y, z] rotation in radians
    pivot: str = 'MEDIAN_POINT'     # pivot point for transform
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Transforms selected vertices/edges/faces.
    
    The most essential missing tool. Enables shaping geometry by moving, scaling, 
    and rotating selected elements. Without this, complex modeling is impossible.
    
    Args:
        translate: [x, y, z] translation offset in local coordinates
        scale: [x, y, z] scale factors (1.0 = no change)
        rotate: [x, y, z] Euler rotation in radians
        pivot: Transform pivot point:
            - 'MEDIAN_POINT': Center of selection (default)
            - 'CURSOR': 3D cursor position
            - 'INDIVIDUAL_ORIGINS': Each element's own origin
            - 'ACTIVE_ELEMENT': Active vertex/edge/face
            - 'BOUNDING_BOX_CENTER': Selection bounding box center
    
    Returns:
        Success message with transform details.
    
    Use cases:
        - Taper legs of a tower (scale top vertices toward center)
        - Position vertices precisely
        - Create curved profiles by progressive transforms
        - Rotate faces for angled cuts
    
    Example workflow (tapering):
        1. mesh_select_by_location(axis='Z', min_coord=0.8, max_coord=1.0)
        2. mesh_transform_selected(scale=[0.3, 0.3, 1.0], pivot='MEDIAN_POINT')
    """
```

---

# 🟠 P1 — HIGH PRIORITY (Core geometry operations)

## mesh_bridge_edge_loops

```python
def mesh_bridge_edge_loops(
    segments: int = 1,
    smoothness: float = 0.0,
    profile_factor: float = 0.0,
    twist_offset: int = 0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates faces between two edge loops.
    
    Connects two separate edge loops with a bridge of faces. Essential for 
    joining geometry sections, creating tubes, and connecting platforms to legs.
    
    Args:
        segments: Number of subdivisions in the bridge (1 = direct connection)
        smoothness: Interpolation smoothness (0.0 = linear, 1.0 = smooth)
        profile_factor: Shape of bridge profile (-1.0 to 1.0)
        twist_offset: Rotation offset between loops (in edge steps)
    
    Returns:
        Success message with face count created.
    
    Prerequisites:
        - Exactly 2 edge loops must be selected
        - Loops should have same vertex count for best results
    
    Use cases:
        - Connect tower legs to observation platforms
        - Create tubes from two circular edge loops
        - Join separate mesh islands
    """
```

---

## mesh_bisect

```python
def mesh_bisect(
    plane_co: list[float],          # [x, y, z] point on cutting plane
    plane_no: list[float],          # [x, y, z] plane normal vector
    clear_inner: bool = False,      # delete geometry on negative side
    clear_outer: bool = False,      # delete geometry on positive side
    fill: bool = False              # fill cut with face
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Cuts mesh geometry with infinite plane.
    
    Bisects selected geometry along a defined plane. Can optionally delete 
    geometry on either side and fill the cut with a face.
    
    Args:
        plane_co: [x, y, z] any point that lies on the cutting plane
        plane_no: [x, y, z] normal vector defining plane orientation
        clear_inner: If True, deletes geometry on negative normal side
        clear_outer: If True, deletes geometry on positive normal side
        fill: If True, creates a face to cap the cut
    
    Returns:
        Success message with operation details.
    
    Use cases:
        - Cut torus in half to create arches
        - Slice objects at precise angles
        - Create cross-sections
        - Remove parts of geometry cleanly
    
    Example (cut torus in half on Z axis):
        mesh_bisect(
            plane_co=[0, 0, 0],
            plane_no=[0, 0, 1],
            clear_outer=True,
            fill=True
        )
    """
```

---

## mesh_duplicate_selected

```python
def mesh_duplicate_selected(
    translate: list[float] = None   # [x, y, z] offset for duplicate
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Duplicates selected geometry in-place.
    
    Creates a copy of selected vertices/edges/faces within the same mesh object.
    The duplicate remains selected after operation.
    
    Args:
        translate: Optional [x, y, z] offset to move duplicate. 
                   If None, duplicate is created at same position.
    
    Returns:
        Success message with duplicated element count.
    
    Use cases:
        - Create repeated structural elements (lattice, truss)
        - Duplicate and transform for patterns
        - Copy geometry before destructive operations
    """
```

---

## mesh_separate_selected

```python
def mesh_separate_selected() -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Separates selected geometry into new object.
    
    Extracts currently selected geometry from the mesh and creates a new 
    independent object. Original mesh loses the selected geometry.
    
    Returns:
        Name of the newly created object.
    
    Use cases:
        - Extract part of model for independent manipulation
        - Split joined objects back into components
        - Isolate geometry for export
    """
```

---

# 🟡 P2 — MEDIUM PRIORITY (Advanced modeling)

## curve_create

```python
def curve_create(
    curve_type: str,                    # 'BEZIER', 'NURBS', 'POLY'
    points: list[list[float]],          # list of [x, y, z] control points
    name: str = None,                   # optional object name
    cyclic: bool = False,               # close the curve
    resolution: int = 12                # curve smoothness
) -> str:
    """
    [OBJECT MODE][SAFE] Creates curve object from control points.
    
    Essential for creating smooth arches, rails, paths, and organic shapes 
    that can later be converted to mesh or used with modifiers.
    
    Args:
        curve_type: Type of curve interpolation:
            - 'BEZIER': Smooth curves with handle control
            - 'NURBS': Mathematical smooth curves
            - 'POLY': Straight segments between points
        points: List of [x, y, z] coordinates for control points
        name: Optional name for the curve object
        cyclic: If True, connects last point to first (closed loop)
        resolution: Curve smoothness (segments between control points)
    
    Returns:
        Name of created curve object.
    
    Use cases:
        - Create arches between tower legs
        - Define paths for array modifier
        - Organic decorative elements
        - Rails for geometry extrusion
    
    Example (simple arch):
        curve_create(
            curve_type='BEZIER',
            points=[[-2, 0, 0], [0, 0, 3], [2, 0, 0]],
            name='Arch_Curve'
        )
    """
```

---

## curve_to_mesh

```python
def curve_to_mesh(
    curve_name: str,
    profile: str = None,            # optional profile curve name
    fill_mode: str = 'FULL'         # 'NONE', 'HALF', 'FULL'
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts curve to mesh geometry.
    
    Transforms curve object into editable mesh. Optionally extrudes a 
    profile shape along the curve path.
    
    Args:
        curve_name: Name of the curve object to convert
        profile: Optional name of another curve to use as cross-section profile
        fill_mode: How to fill the curve:
            - 'NONE': Open curve (no fill)
            - 'HALF': Fill one side
            - 'FULL': Fill both sides (solid)
    
    Returns:
        Name of the resulting mesh object.
    
    Use cases:
        - Convert decorative arches to mesh
        - Create tubes/pipes from curve paths
        - Finalize curve-based modeling
    """
```

---

## mesh_spin

```python
def mesh_spin(
    steps: int,                     # number of copies around axis
    angle: float,                   # total rotation in radians (2π = full circle)
    axis: str = 'Z',                # 'X', 'Y', or 'Z'
    center: list[float] = None,    # [x, y, z] center point, None = cursor
    dupli: bool = False            # duplicate instead of connect
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Spins/revolves geometry around axis.
    
    Creates rotational copies of selected geometry around specified axis.
    Can create connected geometry (lathe) or separate copies (radial array).
    
    Args:
        steps: Number of segments/copies to create
        angle: Total angle to cover in radians (2*pi = 360°)
        axis: Rotation axis ('X', 'Y', or 'Z')
        center: [x, y, z] center of rotation. If None, uses 3D cursor
        dupli: If True, creates disconnected copies. If False, creates 
               connected faces (like lathe operation)
    
    Returns:
        Success message with created geometry info.
    
    Use cases:
        - Create radial tower structure elements
        - Lathe profiles (vases, columns)
        - Radial patterns (wheel spokes, gears)
        - Rotational symmetry elements
    
    Example (8-segment full rotation):
        mesh_spin(steps=8, angle=6.28318, axis='Z')
    """
```

---

## mesh_screw

```python
def mesh_screw(
    steps: int,
    screw_offset: float,            # height per revolution
    angle: float,                   # total rotation
    axis: str = 'Z',
    iterations: int = 1             # number of full revolutions
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates helical/spiral geometry.
    
    Extrudes selected geometry in a spiral pattern. Combines rotation 
    with translation for helical structures.
    
    Args:
        steps: Segments per revolution
        screw_offset: Vertical distance per full revolution
        angle: Rotation per step in radians
        axis: Helix axis ('X', 'Y', or 'Z')
        iterations: Number of complete turns
    
    Returns:
        Success message with geometry info.
    
    Use cases:
        - Spiral staircases
        - Springs and coils
        - Helical tower structures
        - Decorative spirals
    """
```

---

## mesh_knife_project

```python
def mesh_knife_project(
    cutter_object: str,             # object to project as knife
    cut_through: bool = True        # cut all the way through
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Projects object outline as cut.
    
    Uses the silhouette of another object (from current view) to cut 
    into the selected mesh geometry.
    
    Args:
        cutter_object: Name of object whose outline will be projected
        cut_through: If True, cuts through entire mesh depth
    
    Returns:
        Success message with cut details.
    
    Use cases:
        - Cut decorative patterns into surfaces
        - Create complex cutouts
        - Project shapes onto curved surfaces
    """
```

---

# 🟢 P3 — LOWER PRIORITY (Procedural construction)

## mesh_add_vertex

```python
def mesh_add_vertex(
    position: list[float]           # [x, y, z] in local space
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Adds single vertex at specified position.
    
    Foundation for fully procedural geometry construction. Creates isolated 
    vertex that can be connected to others via edges and faces.
    
    Args:
        position: [x, y, z] coordinates in object's local space
    
    Returns:
        Index of the created vertex.
    
    Use cases:
        - Build geometry from scratch vertex by vertex
        - Add control points for manual edge creation
        - Precise vertex placement for technical models
    """
```

---

## mesh_add_edge

```python
def mesh_add_edge(
    vertex_indices: list[int]       # [v1_index, v2_index]
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Creates edge between two existing vertices.
    
    Connects two vertices with an edge. Vertices must already exist in mesh.
    
    Args:
        vertex_indices: List of exactly 2 vertex indices to connect
    
    Returns:
        Index of the created edge.
    
    Use cases:
        - Manual wireframe construction
        - Connect procedurally placed vertices
        - Build lattice structures
    """
```

---

## mesh_add_face

```python
def mesh_add_face(
    vertex_indices: list[int]       # [v1, v2, v3, ...] minimum 3
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Creates face from existing vertices.
    
    Constructs a polygon face from 3 or more vertices. Vertices must be 
    specified in correct winding order for proper normal direction.
    
    Args:
        vertex_indices: List of vertex indices (minimum 3) in order
    
    Returns:
        Index of the created face.
    
    Use cases:
        - Complete procedural geometry construction
        - Fill custom shapes
        - Create n-gons from existing vertices
    """
```

---

## mesh_select_random

```python
def mesh_select_random(
    probability: float = 0.5,       # 0.0 to 1.0
    seed: int = 0,                  # random seed for reproducibility
    mode: str = 'VERT'              # 'VERT', 'EDGE', 'FACE'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Randomly selects geometry elements.
    
    Selects elements with specified probability. Useful for adding 
    variation and randomized details to models.
    
    Args:
        probability: Chance of selecting each element (0.0-1.0)
        seed: Random seed for reproducible selections
        mode: Element type to select ('VERT', 'EDGE', 'FACE')
    
    Returns:
        Count of selected elements.
    
    Use cases:
        - Add random details to lattice structures
        - Create variation in repeated elements
        - Select subset for randomized operations
    """
```

---

## mesh_set_cursor_to_selected

```python
def mesh_set_cursor_to_selected() -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Moves 3D cursor to selection center.
    
    Positions the 3D cursor at the median point of current selection.
    Critical for setting custom pivot points for transforms.
    
    Returns:
        New cursor position [x, y, z].
    
    Use cases:
        - Set pivot for rotation/scaling
        - Mark position for later operations
        - Reference point for spin/screw operations
    """
```

---

## mesh_cursor_set_position

```python
def mesh_cursor_set_position(
    position: list[float]           # [x, y, z] world coordinates
) -> str:
    """
    [SCENE][SAFE] Sets 3D cursor to specified world position.
    
    Moves the 3D cursor to exact coordinates. Essential for precise 
    pivot point control in transforms and spin operations.
    
    Args:
        position: [x, y, z] world coordinates for cursor
    
    Returns:
        Confirmation of new cursor position.
    
    Use cases:
        - Set precise pivot point
        - Define center for radial operations
        - Position reference for vertex creation
    """
```

---

# 📊 Implementation Priority Summary

| Priority | Tool | Impact | Complexity |
|----------|------|--------|------------|
| 🔴 P0 | `mesh_transform_selected` | **Critical** — unlocks 80% of modeling | Medium |
| 🟠 P1 | `mesh_bridge_edge_loops` | High — connects geometry | Low |
| 🟠 P1 | `mesh_bisect` | High — precise cuts | Medium |
| 🟠 P1 | `mesh_duplicate_selected` | High — patterns, copies | Low |
| 🟠 P1 | `mesh_separate_selected` | Medium — isolation | Low |
| 🟡 P2 | `curve_create` | Medium — arches, paths | Medium |
| 🟡 P2 | `curve_to_mesh` | Medium — finalize curves | Low |
| 🟡 P2 | `mesh_spin` | Medium — radial structures | Medium |
| 🟡 P2 | `mesh_screw` | Low — spirals | Medium |
| 🟡 P2 | `mesh_knife_project` | Low — complex cuts | High |
| 🟢 P3 | `mesh_add_vertex` | Low — procedural base | Low |
| 🟢 P3 | `mesh_add_edge` | Low — procedural | Low |
| 🟢 P3 | `mesh_add_face` | Low — procedural | Low |
| 🟢 P3 | `mesh_select_random` | Low — variation | Low |
| 🟢 P3 | `mesh_set_cursor_to_selected` | Medium — pivot control | Low |
| 🟢 P3 | `mesh_cursor_set_position` | Medium — pivot control | Low |

---

# 🎯 Recommended Implementation Order

1. **Phase 1 (Core Transform)**
   - `mesh_transform_selected` ← START HERE
   
2. **Phase 2 (Geometry Connections)**
   - `mesh_bridge_edge_loops`
   - `mesh_bisect`
   - `mesh_duplicate_selected`

3. **Phase 3 (Curves & Radial)**
   - `curve_create`
   - `curve_to_mesh`
   - `mesh_spin`

4. **Phase 4 (Procedural Foundation)**
   - `mesh_cursor_set_position`
   - `mesh_add_vertex`
   - `mesh_add_edge`
   - `mesh_add_face`

---

*Generated for Blender AI MCP development*
*Based on Eiffel Tower modeling task requirements*
