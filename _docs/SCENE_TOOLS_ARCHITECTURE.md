# Scene Tools Architecture

Narzędzia sceny służą do zarządzania obiektami, ich selekcją oraz podglądem.
Zgodnie z przyjętą konwencją (tak jak w Modeling Tools), **każda operacja to osobny tool**.

---

# 1. scene_list_objects ✅ Done
Listuje obiekty w scenie.

Przykład:
```json
{
  "tool": "scene_list_objects",
  "args": {}
}
```

---

# 2. scene_delete_object ✅ Done
Usuwa konkretny obiekt.

Przykład:
```json
{
  "tool": "scene_delete_object",
  "args": {
    "name": "Cube.001"
  }
}
```

---

# 3. scene_clean_scene ✅ Done
Czyści scenę (domyślnie zostawia światła i kamery).

Przykład:
```json
{
  "tool": "scene_clean_scene",
  "args": {
    "keep_lights_and_cameras": true
  }
}
```

---

# 4. scene_duplicate_object ✅ Done
Duplikuje obiekt i opcjonalnie go przesuwa.

Przykład:
```json
{
  "tool": "scene_duplicate_object",
  "args": {
    "name": "Cube",
    "translation": [2.0, 0.0, 0.0]
  }
}
```

---

# 5. scene_set_active_object ✅ Done
Ustawia obiekt jako aktywny (ważne dla modyfikatorów).

Przykład:
```json
{
  "tool": "scene_set_active_object",
  "args": {
    "name": "Cube"
  }
}
```

---

# 6. scene_get_viewport ✅ Done
Pobiera podgląd sceny (obraz base64).

Przykład:
```json
{
  "tool": "scene_get_viewport",
  "args": {
    "width": 1024,
    "height": 768
  }
}
```

---

# Zasady
1. **Prefiks `scene_`**: Wszystkie narzędzia muszą zaczynać się od tego prefiksu.
2. **Atomiczność**: Jeden tool = jedna akcja. Nie grupujemy akcji w jeden tool z parametrem `action`.


