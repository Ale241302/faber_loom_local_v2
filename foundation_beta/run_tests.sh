#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
source .venv/Scripts/activate

export PYTHONPATH=backend
export TESTING=True

echo "Running unit tests..."
python -m pytest tests/test_m16_unit.py -p no:django

echo ""
echo "Running cross-tenant integration tests (requires PostgreSQL + Redis)..."
python -m pytest tests/test_m16_tenant_isolation.py

echo ""
echo "All tests passed."
