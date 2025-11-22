# Blender Addon Documentation

Dokumentacja modułu Addona (Server Side).

## 📚 Indeks Tematyczny

- **[Architektura RPC i Wątkowość](./rpc_architecture.md)**
  - Wyjaśnienie modelu wielowątkowego.
  - Mechanizm `bpy.app.timers`.
  - Protokół JSON.

## 🛠 Dostępne Komendy (System)
- `ping`: Sprawdza połączenie. Zwraca wersję Blendera.

## 🛠 Dostępne Komendy API (Scene)
Implementacja w `blender_addon/api/scene.py`.

| Komenda RPC | Wymagane Argumenty | Opis |
|-------------|--------------------|------|
| `scene.list_objects` | *brak* | Pobiera listę obiektów z `bpy.context.scene.objects`. |
| `scene.delete_object` | `name` | Usuwa obiekt z `bpy.data.objects` używając `do_unlink=True`. |
| `scene.clean_scene` | `keep_lights_and_cameras` (bool) | Iteruje po obiektach i usuwa je. Opcjonalnie zachowuje kamery/światła. |

## 🛠 Struktura Plików
- `__init__.py`: Rejestracja Addona i handlerów RPC.
- `rpc_server.py`: Implementacja serwera socket.
- `api/`: Moduły z logiką biznesową (wrappery na `bpy`).
