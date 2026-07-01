#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/infra"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Review it before continuing."
fi

docker compose up -d

echo "Waiting for PostgreSQL to be healthy..."
until docker compose exec postgres pg_isready -U faberloom_app -d faberloom >/dev/null 2>&1; do
    sleep 1
done

echo "Services are up. Run migrations with:"
echo "  cd foundation_beta/backend && source ../.venv/Scripts/activate && python manage.py migrate && python manage.py init_rls"
