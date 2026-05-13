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
- If you want to experiment with a different model, override
  `REFERENCE_CLASSIFIER_MODEL` or `VISION_REFERENCE_CLASSIFIER_MODEL`.
- `BLENDER_AI_DEBUG` accepts `off`, `all`, or one or more of
  `vision`, `reference`, `tools`, `transport`, `visibility`, `guided_flow`,
  `router`.
