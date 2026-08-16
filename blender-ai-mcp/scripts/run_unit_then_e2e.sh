#!/usr/bin/env bash
set -euo pipefail

UNIT_TARGET="${1:-tests/unit}"
E2E_TARGET="${2:-tests/e2e}"

echo "[1/2] Running unit tests separately: ${UNIT_TARGET}"
PYTHONPATH=. poetry run pytest "${UNIT_TARGET}" -q

echo "[2/2] Running E2E tests separately: ${E2E_TARGET}"
PYTHONPATH=. poetry run pytest "${E2E_TARGET}" -vs -rA
