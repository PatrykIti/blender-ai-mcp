# blender-ai-mcp  
Modular MCP Server + Blender Addon for AI-Driven 3D Modeling  
Clean Architecture • Stable Tooling • Localhost RPC • Python + Blender API

---

## 📌 Wprowadzenie

**blender-ai-mcp** to system umożliwiający precyzyjne, deterministyczne sterowanie Blenderem przez AI (LLM/MCP).  
Zamiast wykonywania surowego kodu Python generowanego przez modele (co powoduje liczne błędy), projekt dostarcza:

- MCP Server z precyzyjnymi TOOLS (API)
- Blender Addon nasłuchujący po localhost
- Clean Architecture
- Zabezpieczenia błędów kontekstu Blender
- Grupowane funkcjonalności zamiast “tool per function”

AI dzięki temu może tworzyć:

- złożone modele low poly  
- realistyczne modele techniczne (telefony, kamery, urządzenia)  
- modele medyczne (płuca, serce, organy 3D)  
- budynki, assety do gier, scenografie  

---

## 🎯 Cele projektu

- Stabilne modelowanie 3D sterowane przez AI
- Przewidywalne API bez błędów kontekstowych Blender’a
- Podział operacji na logiczne tool’e wysokiego poziomu
- Budowa Clean Architecture pozwalającej łatwo rozszerzać projekt
- Bezpieczne wykonywanie operacji w Blender

---

# 🧱 Architektura systemu

```
+------------------+        +---------------------+         +---------------------+
|     AI Model     | -----> |     MCP Server      | <-----> |   Blender Add-on    |
| (ChatGPT / LLM)  |        | (Python Fast-MCP)   |   RPC   | (bpy + RPC wrapper) |
+------------------+        +---------------------+         +---------------------+

                            Clean Architecture
                -------------------------------------------
                Domain | Application | Adapters | Infra
```

---

# 🔄 Flow działania

```
AI → MCP Server → Tool → JSON RPC → Blender Addon → bpy → wynik → MCP → AI
```

Przykład requestu:

```json
{
  "tool": "mesh.extrude",
  "args": { "distance": 0.2 }
}
```

---

# 🧰 Wymagania

- Python 3.10+
- Blender 3.6+ lub 4.x
- fastmcp (biblioteka MCP server)
- WebSocket/TCP JSON RPC
- Python API Blender (`bpy`)

---

# 📦 Instalacja

## MCP Server
```
git clone https://github.com/YOU/blender-ai-mcp.git
cd blender-ai-mcp
poetry install
```

## Blender Addon
Blender → Edit → Preferences → Add-ons → Install  
Wybierz plik:

```
blender_addon/blender_ai_mcp_addon.zip
```

Addon domyślnie nasłuchuje:
```
Host: 127.0.0.1
Port: 8765
Protocol: WebSocket JSON RPC
```

---

# 📁 Struktura katalogów (Clean Architecture)

```
blender-ai-mcp/
│
├── server/
│   ├── domain/
│   │   ├── models/           # DTO, struktury danych
│   │   ├── tools/            # interfejsy tooli
│   │
│   ├── application/
│   │   ├── tool_handlers/    # implementacje logiki tooli
│   │   ├── validators/       # walidacje argumentów
│   │
│   ├── adapters/
│   │   ├── rpc/              # komunikacja z Blender Addon
│   │   ├── mcp/              # MCP tool registry
│   │
│   └── infrastructure/
│       ├── config/
│       └── logging/
│
├── blender_addon/
│   ├── __init__.py
│   ├── rpc_server.py         # nasłuch requestów
│   ├── tool_executor.py      # wykonanie operacji w bpy
│   ├── api/                  # high-level wrappery
│   └── utils/
│
└── README.md
```

---

# 🧠 Zasady projektowania “Stable Blender Tools”

## ❌ Zła praktyka: 1 tool = 1 funkcja Blender API  
Blender posiada ponad 1200 operatorów → AI się gubi → kontekst nie działa → błędy.

## ✔ Dobra praktyka: 1 tool = 1 logiczna czynność modelowania  

Przykłady:

### ❌ Złe
- mesh.primitive_cube_add
- mesh.extrude_region_move
- mesh.bevel
- object.mode_set
- transform.translate

### ✔ Dobre
- model.create_cube(size)
- mesh.extrude(distance)
- mesh.bevel(amount)
- mesh.inset(thickness)
- model.apply_mirror(axis)
- mesh.clean_topology()

## Każdy tool:

- zarządza mode (object/edit)
- zarządza selekcją
- waliduje argumenty
- wykonuje operację
- zwraca wynik w JSON
- obsługuje wyjątki Blender context

---

# 🧩 Kategorie TOOLS

## 1) Scene Tools
- scene.list_objects
- scene.delete_object
- scene.duplicate
- scene.set_active

## 2) Modeling Tools
- model.create_cube
- model.create_sphere
- model.create_cylinder
- model.apply_mirror
- model.apply_modifier

## 3) Mesh Editing Tools
- mesh.enter_edit
- mesh.exit_edit
- mesh.extrude(distance)
- mesh.inset(thickness)
- mesh.bevel(amount)
- mesh.subdivide(level)
- mesh.merge(distance)
- mesh.clean_topology

## 4) UV Tools
- uv.smart_unwrap
- uv.project_from_view

## 5) Materials
- material.create(name, color)
- material.assign(object, name)

## 6) Export Tools
- export.glb(path)
- export.fbx(path)
- export.obj(path)

## 7) System Helpers
- system.debug_context
- system.force_mode_set
- system.reset_selection

---

# 🧪 Przykład implementacji toola (Server → Blender Addon)

## MCP Server: handlers/mesh/extrude.py

```python
class ExtrudeTool:
    def execute(self, distance: float):
        payload = {
            "cmd": "mesh_extrude",
            "args": { "distance": float(distance) }
        }
        return self.rpc.send(payload)
```

## Blender Addon: api/mesh_tools.py

```python
def extrude(distance):
    import bpy
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, distance)}
    )
    return {"status": "ok"}
```

---

# 📡 Komunikacja

Format RPC:

```
{
  "cmd": "mesh_extrude",
  "args": { "distance": 0.2 },
  "request_id": "uuid"
}
```

Odpowiedź:
```
{
  "status": "ok",
  "result": {},
  "request_id": "uuid"
}
```

---

# 🏗 Best Practices

- AI widzi tylko stabilne tool’e
- Nigdy nie odsłaniamy całego `bpy.ops`
- Każdy tool powinien być:
  - idempotentny lub przewidywalny
  - odporny na brak selekcji
  - odporny na zły mode
- Dodawaj logi JSON do debugowania AI
- Testuj każdy tool izolacyjnie w czystej scenie

---

# 🛠 Testowanie

- unittesty dla tool-handlerów
- testy integracyjne Addon + Server
- testy przepływu (flow): AI → MCP → Blender

---

# 🗺 Roadmap

- Auto-follow-up tool fixes
- High-level anatomical modeling tools
- Procedural low-poly stylizer
- Auto UV optimizer
- Full GLTF pipeline

---

# 📜 Licencja
MIT