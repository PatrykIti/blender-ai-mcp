#!/usr/bin/env bash

set -euo pipefail

SEGMENTATION_SIDECAR_HOST="${SEGMENTATION_SIDECAR_HOST:-0.0.0.0}"
SEGMENTATION_SIDECAR_PORT="${SEGMENTATION_SIDECAR_PORT:-9100}"
SEGMENTATION_SIDECAR_MODEL="${SEGMENTATION_SIDECAR_MODEL:-${VISION_SEGMENTATION_MODEL:-sam-sidecar-v1}}"
SEGMENTATION_SIDECAR_DEVICE="${SEGMENTATION_SIDECAR_DEVICE:-auto}"
SEGMENTATION_SIDECAR_MAX_PARTS="${SEGMENTATION_SIDECAR_MAX_PARTS:-${VISION_SEGMENTATION_MAX_PARTS:-16}}"

echo "Starting local segmentation sidecar on http://${SEGMENTATION_SIDECAR_HOST}:${SEGMENTATION_SIDECAR_PORT}"
echo "Model: ${SEGMENTATION_SIDECAR_MODEL}"
echo "Device: ${SEGMENTATION_SIDECAR_DEVICE}"
echo "Max parts: ${SEGMENTATION_SIDECAR_MAX_PARTS}"
echo "Local MCP endpoint:  http://127.0.0.1:${SEGMENTATION_SIDECAR_PORT}/segment"
echo "Docker MCP endpoint: http://host.docker.internal:${SEGMENTATION_SIDECAR_PORT}/segment"
echo "Mode: foreground sidecar-only helper. This script does not start the FastMCP server."
echo "For combined launch use ./scripts/run_mcp_server.sh or scripts/run_streamable_openrouter.sh."
echo "Remember to install optional vision deps first: poetry install --with vision"
echo "First launch downloads the configured model weights automatically."

exec poetry run python scripts/segmentation_sidecar.py \
  --host "${SEGMENTATION_SIDECAR_HOST}" \
  --port "${SEGMENTATION_SIDECAR_PORT}" \
  --model "${SEGMENTATION_SIDECAR_MODEL}" \
  --device "${SEGMENTATION_SIDECAR_DEVICE}" \
  --max-parts "${SEGMENTATION_SIDECAR_MAX_PARTS}"
