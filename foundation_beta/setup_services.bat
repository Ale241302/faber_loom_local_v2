@echo off
setlocal

cd /d "%~dp0infra"

if not exist .env (
    copy .env.example .env
    echo Created .env from .env.example. Review it before continuing.
)

docker compose up -d

echo Waiting for PostgreSQL to be healthy...
:loop
docker compose exec postgres pg_isready -U faberloom_app -d faberloom >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto loop
)

echo Services are up. Run migrations with:
echo   cd foundation_beta\backend ^&^& .venv\Scripts\python manage.py migrate ^&^& .venv\Scripts\python manage.py init_rls
