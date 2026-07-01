# Checklist — Setup PC Nueva (Windows)
> MWT / Rana Walk · Álvaro · Actualizado 2026-04-10

---

## FASE 1 — Base del sistema
- [ ] Windows Update completo (reiniciar hasta que no haya pendientes)
- [ ] Activar Windows (verificar licencia)
- [ ] Configurar idioma, zona horaria → **UTC-6, Costa Rica**
- [ ] Instalar [Chrome](https://chrome.google.com) + sincronizar perfil Google (recupera extensiones)
- [ ] Instalar [1Password](https://1password.com) o gestor de contraseñas → recuperar vault

---

## FASE 2 — Dev environment (WSL2 + toolchain)
> Claude Code requiere entorno Unix. WSL2 es el path en Windows.

- [ ] Activar WSL2: `wsl --install` (PowerShell como Admin) → reiniciar
- [ ] Instalar Ubuntu 22.04 desde Microsoft Store
- [ ] Dentro de WSL: actualizar `sudo apt update && sudo apt upgrade -y`
- [ ] Instalar **Git**: `sudo apt install git -y`
- [ ] Configurar Git: `git config --global user.name "Alvaro"` y `user.email`
- [ ] Instalar **Node.js** (via nvm): `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash` → `nvm install --lts`
- [ ] Instalar **Python 3.11+**: `sudo apt install python3 python3-pip -y`
- [ ] Instalar **uv** (gestor Python rápido): `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## FASE 3 — Claude Code + Cowork
- [ ] Instalar Claude desktop app (Windows) → [claude.ai/download](https://claude.ai/download)
- [ ] Login con cuenta Anthropic
- [ ] Instalar Claude Code en WSL: `npm install -g @anthropic/claude-code`
- [ ] Verificar: `claude --version`
- [ ] Conectar Google Drive en Cowork (MCP)
- [ ] Conectar Gmail en Cowork (MCP)
- [ ] Conectar Google Calendar en Cowork (MCP)
- [ ] Reinstalar plugins de Cowork (productivity, data, etc.)

---

## FASE 4 — KB MWT (recuperar workspace)
- [ ] Crear carpeta de trabajo: `mkdir -p ~/workspace` en WSL
- [ ] Clonar repo KB: `git clone <URL_REPO_KB> "MWT KB"`
- [ ] Verificar que `RW_ROOT.md` y `DASHBOARD_SNAPSHOT.md` carguen correctamente
- [ ] Probar `bash ~/mnt/MWT\ KB/git_push.sh "test"` → confirmar push funciona
- [ ] Seleccionar carpeta `MWT KB` como workspace en Cowork

---

## FASE 5 — n8n
- [ ] Instalar Docker Desktop para Windows → habilitar integración WSL2
- [ ] Pull imagen n8n: `docker pull n8nio/n8n`
- [ ] Restaurar workflows desde backup (`.json` exports o volumen Docker)
- [ ] Verificar credenciales reconectadas (webhooks, Gmail, etc.)
- [ ] Testear workflow crítico más importante primero

---

## FASE 6 — Herramientas de negocio
- [ ] **Helium 10** → instalar extensión Chrome + login
- [ ] **Amazon Seller Central** → login, verificar 2FA
- [ ] **SP-API** → restaurar credenciales en `.env` (nunca hardcodeadas)
  - `SP_API_CLIENT_ID`
  - `SP_API_CLIENT_SECRET`
  - `SP_API_REFRESH_TOKEN`
- [ ] **Marluvas / Tecmater** — documentos y contactos accesibles via Drive
- [ ] Google Drive app de escritorio (opcional, si usas sync local)

---

## FASE 7 — Seguridad y variables de entorno
- [ ] Crear archivo `~/.env` o usar gestor (doppler / direnv) — NUNCA commitear
- [ ] Configurar variables críticas:
  - `ANTHROPIC_API_KEY`
  - `SP_API_*` (ver Fase 6)
  - Cualquier webhook secret de n8n
- [ ] Verificar que `.gitignore` excluye `.env` en todos los repos
- [ ] Activar 2FA en: Google, Amazon, Anthropic

---

## FASE 8 — Verificación final
- [ ] `claude` abre correctamente en WSL
- [ ] Cowork conecta a KB sin errores
- [ ] n8n ejecuta workflow de prueba OK
- [ ] `git push` desde KB funciona
- [ ] SP-API responde a llamada de prueba
- [ ] Helium 10 muestra datos de Rana Walk

---

## Orden recomendado si todo está en paralelo
**1 → 2 → 4 → 3 → 7 → 5 → 6 → 8**
(Base → Dev → KB → Claude → Seguridad → n8n → Negocio → Verificar)
