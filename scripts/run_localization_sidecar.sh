#!/usr/bin/env bash

set -euo pipefail

LOCALIZATION_SIDECAR_HOST="${LOCALIZATION_SIDECAR_HOST:-0.0.0.0}"
LOCALIZATION_SIDECAR_PORT="${LOCALIZATION_SIDECAR_PORT:-9300}"
LOCALIZATION_SIDECAR_MODEL="${LOCALIZATION_SIDECAR_MODEL:-${VISION_LOCALIZATION_MODEL:-grounding-sidecar-v1}}"
LOCALIZATION_SIDECAR_DEVICE="${LOCALIZATION_SIDECAR_DEVICE:-auto}"
LOCALIZATION_SIDECAR_MAX_CANDIDATES="${LOCALIZATION_SIDECAR_MAX_CANDIDATES:-${VISION_LOCALIZATION_MAX_CANDIDATES:-8}}"
LOCALIZATION_SIDECAR_THRESHOLD="${LOCALIZATION_SIDECAR_THRESHOLD:-0.1}"

echo "Starting local localization sidecar on http://${LOCALIZATION_SIDECAR_HOST}:${LOCALIZATION_SIDECAR_PORT}"
echo "Model: ${LOCALIZATION_SIDECAR_MODEL}"
echo "Device: ${LOCALIZATION_SIDECAR_DEVICE}"
echo "Max candidates: ${LOCALIZATION_SIDECAR_MAX_CANDIDATES}"
echo "Threshold: ${LOCALIZATION_SIDECAR_THRESHOLD}"
echo "Local MCP endpoint:  http://127.0.0.1:${LOCALIZATION_SIDECAR_PORT}/localize"
echo "Docker MCP endpoint: http://host.docker.internal:${LOCALIZATION_SIDECAR_PORT}/localize"
echo "Mode: foreground sidecar-only helper. This script does not start the FastMCP server."
echo "For combined launch use ./scripts/run_mcp_server.sh or scripts/run_streamable_openrouter.sh."
echo "Remember to install optional vision deps first: poetry install --with vision"
echo "First launch downloads the configured model weights automatically."

exec poetry run python scripts/localization_sidecar.py \
  --host "${LOCALIZATION_SIDECAR_HOST}" \
  --port "${LOCALIZATION_SIDECAR_PORT}" \
  --model "${LOCALIZATION_SIDECAR_MODEL}" \
  --device "${LOCALIZATION_SIDECAR_DEVICE}" \
  --max-candidates "${LOCALIZATION_SIDECAR_MAX_CANDIDATES}" \
  --threshold "${LOCALIZATION_SIDECAR_THRESHOLD}"
