# Modeling Tools (NOT GROUPABLE – high precision topology operations)

Narzędzia modelowania są destrukcyjne lub wpływają na topologię, dlatego:
**NIE WOLNO ich grupować w jeden tool.**
Każda operacja musi mieć osobny tool, aby AI nie mieszało kontekstu ani trybów.

---

# 1. modeling.add_modifier (GROUPABLE – jedyna grupa w modeling) ✅ Done
Bezpieczne modyfikatory, które AI może stosować z parametrami.

Dozwolone typy:

## Hard-Surface Modifiers:
- BEVEL  
- SUBSURF  
- MIRROR  
- ARRAY  
- SOLIDIFY  
- BOOLEAN  

## Organic Modifiers:
- SMOOTH  
- REMESH  
- DISPLACE  
- SIMPLE_DEFORM  
- SHRINKWRAP (opcjonalne)

## Utility / Low Poly:
- DECIMATE  
- TRIANGULATE  

Przykład:
```json
{
  "tool": "modeling.add_modifier",
  "args": {
    "name": "PhoneBody",
    "modifier_type": "BEVEL",
    "width": 0.02,
    "segments": 2
  }
}
```

---

# 2. modeling.apply_modifier ✅ Done
Zatwierdzanie modyfikatorów.

Operacje:
- apply (pojedynczy)
- apply_all (wszystkie)
- apply_condition (opcjonalnie)

---

# 3. modeling.convert_to_mesh ✅ Done
Konwersja z obiektów typu Curve, Text, Surface → Mesh.

Przykład:
```json
{
  "tool": "modeling.convert_to_mesh",
  "args": { "name": "BezierCurve" }
}
```

---

# 4. modeling.join_objects ✅ Done
Łączenie wielu obiektów w jeden Mesh.

Args:
- objects: [lista nazw]

---

# 5. modeling.separate ✅ Done
Oddzielenie siatki na nowe obiekty.

Typy:
- MATERIAL
- SELECTION
- LOOSE_PARTS

---

# 6. modeling.set_origin ✅ Done
Ustawienie punktu origin obiektu.

Metody:
- GEOMETRY
- CENTER_OF_MASS
- CURSOR

---

# 7. modeling.list_modifiers ✅ Done (Dodane)
Listowanie modyfikatorów na obiekcie.

Args:
- name: nazwa obiektu

---

# 8. modeling.create_primitive (object-level creation) ✅ Done
Tworzenie podstawowych brył (powiązane z modeling, ale oddzielne od mesh tools).

Typy:
- cube
- sphere
- plane
- cylinder
- cone

---

# SEPARATE MESH-EDIT TOOLS (ABSOLUTELY NOT GROUPABLE)

## mesh.extrude
- distance
- axis (opcjonalnie)

## mesh.inset
- thickness

## mesh.bevel
- amount
- segments

## mesh.subdivide
- levels
- smoothness

## mesh.loop_cut
- count
- ratio

## mesh.boolean (destructive mode)
- operation: DIFFERENCE / UNION / INTERSECT
- target
- cutter

## mesh.merge_by_distance
- distance

## mesh.triangulate
(no args)

## mesh.remesh_voxel
- voxel_size

## mesh.smooth
- iterations

## mesh.delete_selected
(no args)

---

# RULES FOR MODELING CATEGORY

1. **Modeling NIE MOŻE być grupowane.**  
   Powód: topologia, selekcje, tryby, destrukcja.

2. **Jedyny wyjątek: modeling.add_modifier**  
   (bo modifiers są parametryczne i stabilne)

3. **mesh.* ZAWSZE osobnymi toolami**  
   (extrude, bevel, inset, loop_cut itd.)

4. **Wszystkie operacje wpływające na geometrię siatki → MUST BE SEPARATE**

5. **modeling.* operuje na obiektach (Object Mode)**  
   **mesh.* operuje na geometrii (Edit Mode)**

