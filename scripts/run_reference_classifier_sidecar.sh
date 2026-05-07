#!/usr/bin/env bash

set -euo pipefail

REFERENCE_CLASSIFIER_HOST="${REFERENCE_CLASSIFIER_HOST:-0.0.0.0}"
REFERENCE_CLASSIFIER_PORT="${REFERENCE_CLASSIFIER_PORT:-9200}"
REFERENCE_CLASSIFIER_MODEL="${REFERENCE_CLASSIFIER_MODEL:-${VISION_REFERENCE_CLASSIFIER_MODEL:-google/siglip2-base-patch16-224}}"
REFERENCE_CLASSIFIER_DEVICE="${REFERENCE_CLASSIFIER_DEVICE:-auto}"
REFERENCE_CLASSIFIER_TOP_K="${REFERENCE_CLASSIFIER_TOP_K:-${VISION_REFERENCE_CLASSIFIER_MAX_LABELS:-5}}"

echo "Starting local reference classifier sidecar on http://${REFERENCE_CLASSIFIER_HOST}:${REFERENCE_CLASSIFIER_PORT}"
echo "Model: ${REFERENCE_CLASSIFIER_MODEL}"
echo "Device: ${REFERENCE_CLASSIFIER_DEVICE}"
echo "Top K: ${REFERENCE_CLASSIFIER_TOP_K}"
echo "Local MCP endpoint:  http://127.0.0.1:${REFERENCE_CLASSIFIER_PORT}/classify"
echo "Docker MCP endpoint: http://host.docker.internal:${REFERENCE_CLASSIFIER_PORT}/classify"
echo "Remember to install optional vision deps first: poetry install --with vision"

exec poetry run python scripts/reference_classifier_sidecar.py \
  --host "${REFERENCE_CLASSIFIER_HOST}" \
  --port "${REFERENCE_CLASSIFIER_PORT}" \
  --model "${REFERENCE_CLASSIFIER_MODEL}" \
  --device "${REFERENCE_CLASSIFIER_DEVICE}" \
  --top-k "${REFERENCE_CLASSIFIER_TOP_K}"
