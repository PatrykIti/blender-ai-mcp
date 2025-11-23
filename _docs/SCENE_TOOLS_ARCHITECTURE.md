# Structure proposal

scene
│
├── list_objects
├── delete_object
├── clean_scene
├── duplicate_object
├── set_active
│
├── get_viewport
│     ├── shading: SOLID / MATERIAL / WIREFRAME / RENDERED
│     ├── camera: CameraName
│     ├── background_color
│     ├── overlays: ON/OFF
│     ├── xray: ON/OFF
│     ├── clipping_region
│     ├── matcap: string
│     ├── render_type: preview / eevee / cycles
│
└── get_viewport_image
      ├── width
      ├── height
      ├── shading
      ├── camera

# Examples

## Simple view

{
  "tool": "scene",
  "args": {
    "action": "get_viewport",
    "width": 1024,
    "height": 1024
  }
}

## View with shading and camera

{
  "tool": "scene",
  "args": {
    "action": "get_viewport",
    "width": 1024,
    "height": 1024,
    "shading": "MATERIAL",
    "camera": "Cam_1"
  }
}


## Viewport setup without image generation

{
  "tool": "scene",
  "args": {
    "action": "set_viewport",
    "shading": "WIREFRAME",
    "background_color": [0.1, 0.1, 0.1],
    "xray": true
  }
}

## One action - set camera

{
  "tool": "scene",
  "args": {
    "action": "get_viewport_image",
    "camera": "CameraCloseup",
    "shading": "RENDERED",
    "width": 512,
    "height": 512
  }
}


