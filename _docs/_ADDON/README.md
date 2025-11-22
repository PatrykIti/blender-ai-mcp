# Blender Addon Documentation

Dokumentacja modułu Addona (Server Side).

## 📚 Indeks Tematyczny

- **[Architektura RPC i Wątkowość](./rpc_architecture.md)**
  - Wyjaśnienie modelu wielowątkowego i `bpy.app.timers`.

## 🛠 Struktura (Clean Architecture)

Addon jest podzielony na warstwy, aby odseparować logikę Blendera od mechanizmów sieciowych.

### 1. Entry Point (`__init__.py`)
Punkt wejścia. Odpowiada za:
- Rejestrację w Blenderze (`bl_info`).
- Tworzenie instancji handlerów aplikacji.
- Rejestrację handlerów w serwerze RPC.
- Uruchomienie serwera w osobnym wątku.

### 2. Application (`application/handlers/`)
Logika biznesowa ("Jak to zrobić w Blenderze").
- `scene.py`: `SceneHandler` (Lista obiektów, usuwanie).
- `modeling.py`: `ModelingHandler` (Tworzenie, transformacje, modyfikatory).

### 3. Infrastructure (`infrastructure/`)
Szczegóły techniczne.
- `rpc_server.py`: Implementacja serwera TCP.

## 🛠 Dostępne Komendy API

### Scene (`application/handlers/scene.py`)
| Komenda RPC | Metoda | Opis |
|-------------|--------|------|
| `scene.list_objects` | `list_objects` | Lista obiektów na scenie. |
| `scene.delete_object` | `delete_object` | Usunięcie obiektu. |
| `scene.clean_scene` | `clean_scene` | Wyczyszczenie sceny. |

### Modeling (`application/handlers/modeling.py`)
| Komenda RPC | Metoda | Opis |
|-------------|--------|------|
| `modeling.create_primitive` | `create_primitive` | Tworzy prymityw (Cube, Sphere, etc.). |
| `modeling.transform_object` | `transform_object` | Przesuwa, obraca lub skaluje obiekt. |
| `modeling.add_modifier` | `add_modifier` | Dodaje modyfikator do obiektu. |
