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
- `scene.py`: Klasa `SceneHandler`. Metody takie jak `list_objects`, `delete_object`. Używa `bpy` bezpośrednio.

### 3. Infrastructure (`infrastructure/`)
Szczegóły techniczne.
- `rpc_server.py`: Implementacja serwera TCP. Nie zna logiki biznesowej, jedynie przyjmuje żądania JSON i przekazuje je do zarejestrowanych funkcji callback.

## 🛠 Dostępne Komendy API (Scene)
Zdefiniowane w `application/handlers/scene.py`.

| Komenda RPC | Metoda Handlera | Opis |
|-------------|-----------------|------|
| `scene.list_objects` | `list_objects` | Lista obiektów na scenie. |
| `scene.delete_object` | `delete_object` | Usunięcie obiektu. |
| `scene.clean_scene` | `clean_scene` | Wyczyszczenie sceny. |