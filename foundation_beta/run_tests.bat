@echo off
setlocal

cd /d "%~dp0"
call .venv\Scripts\activate.bat

set PYTHONPATH=backend
set TESTING=True

echo Running unit tests...
python -m pytest tests\test_m16_unit.py -p no:django
if errorlevel 1 exit /b 1

echo.
echo Running cross-tenant integration tests (requires PostgreSQL + Redis)...
python -m pytest tests\test_m16_tenant_isolation.py
if errorlevel 1 exit /b 1

echo.
echo All tests passed.
