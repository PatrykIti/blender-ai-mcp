# Script run_streamable_openrouter.sh



# Typical Flows

## 1. Local MCP + local sidecar

```bash
poetry install --with vision
export VISION_REFERENCE_CLASSIFIER_ENABLED=true
export VISION_REFERENCE_CLASSIFIER_PROVIDER=generic_sidecar
export VISION_REFERENCE_CLASSIFIER_ENDPOINT=http://127.0.0.1:9200/classify
./scripts/run_reference_classifier_sidecar.sh
poetry run python -m server.main
```

## 2. Docker-guided MCP + auto-start sidecar

```bash
poetry install --with vision
export OPENROUTER_API_KEY=...
export VISION_REFERENCE_CLASSIFIER_ENABLED=true
export VISION_REFERENCE_CLASSIFIER_PROVIDER=generic_sidecar
export VISION_REFERENCE_CLASSIFIER_MODEL=google/siglip2-base-patch16-224
export BLENDER_AI_DEBUG=vision,reference,transport
./scripts/run_streamable_openrouter.sh
```

## 2a. Docker-guided MCP + auto-start classifier + segmentation + localization

```bash
poetry install --with vision
export OPENROUTER_API_KEY=...
export VISION_REFERENCE_CLASSIFIER_ENABLED=true
export VISION_REFERENCE_CLASSIFIER_PROVIDER=generic_sidecar
export VISION_REFERENCE_CLASSIFIER_MODEL=google/siglip2-base-patch16-224
export VISION_SEGMENTATION_ENABLED=true
export VISION_SEGMENTATION_PROVIDER=generic_sidecar
export VISION_SEGMENTATION_MODEL=sam-sidecar-v1
export VISION_LOCALIZATION_ENABLED=true
export VISION_LOCALIZATION_PROVIDER=generic_sidecar
export VISION_LOCALIZATION_MODEL=grounding-sidecar-v1
./scripts/run_streamable_openrouter.sh
```

## 3. Docker-guided MCP + remote classifier endpoint

```bash
export OPENROUTER_API_KEY=...
export VISION_REFERENCE_CLASSIFIER_ENABLED=true
export VISION_REFERENCE_CLASSIFIER_PROVIDER=generic_sidecar
export REFERENCE_CLASSIFIER_AUTO_START=false
export VISION_REFERENCE_CLASSIFIER_ENDPOINT=http://my-remote-host:9200/classify
export BLENDER_AI_DEBUG=router,guided_flow,transport
./scripts/run_streamable_openrouter.sh
```

## Notes

- The sidecar is support-only. It does not become gate or tool-unlock authority.
- The initial implementation targets local SigLIP2 via `transformers` + `torch`.
- With `REFERENCE_CLASSIFIER_AUTO_START=true`, the sidecar now preloads the
  classifier pipeline before the MCP container is treated as ready, so the
  first live reference attach does not absorb model cold-start time.
- With `SEGMENTATION_SIDECAR_AUTO_START=true` or
  `LOCALIZATION_SIDECAR_AUTO_START=true`, the launcher starts the local SAM /
  localization helpers before the MCP container and derives
  `VISION_SEGMENTATION_ENDPOINT` / `VISION_LOCALIZATION_ENDPOINT`
  automatically for Docker.
- The first launch of the local localization or segmentation helpers downloads
  the configured model weights automatically from Hugging Face.
- If you want to experiment with a different model, override
  `REFERENCE_CLASSIFIER_MODEL`, `SEGMENTATION_SIDECAR_MODEL`, or
  `LOCALIZATION_SIDECAR_MODEL`.
- `BLENDER_AI_DEBUG` accepts `off`, `all`, or one or more of
  `vision`, `reference`, `tools`, `transport`, `visibility`, `guided_flow`,
  `router`.
