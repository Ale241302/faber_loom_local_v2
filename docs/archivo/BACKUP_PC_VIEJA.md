# Checklist — Qué guardar antes de entregar la PC vieja
> MWT / Rana Walk · Álvaro · 2026-04-10

---

## FASE 1 — Credenciales y secretos (CRÍTICO)
- [ ] Exportar vault de gestor de contraseñas (1Password / Bitwarden → `.csv` o `.json`)
- [ ] Copiar archivo `.env` de todos los proyectos/repos
- [ ] Anotar / exportar claves de API activas:
  - `ANTHROPIC_API_KEY`
  - `SP_API_CLIENT_ID / SECRET / REFRESH_TOKEN`
  - Webhooks activos de n8n
  - Cualquier API key de Helium 10, MWS, etc.
- [ ] Exportar SSH keys: `~/.ssh/` completo (id_rsa, id_ed25519, known_hosts)
- [ ] Exportar GPG keys si usas firma de commits

---

## FASE 2 — Código y KB
- [ ] `git status` en todos los repos → commit y push todo pendiente
- [ ] Verificar que KB MWT esté 100% pusheada: `bash ~/mnt/MWT\ KB/git_push.sh "pre-migration backup"`
- [ ] Listar repos locales que no están en GitHub/remote → subir o comprimir
- [ ] Exportar configuración de Claude Code (`~/.claude/` o equivalente en Windows)

---

## FASE 3 — n8n
- [ ] Exportar TODOS los workflows: Settings → Export → All workflows (`.json`)
- [ ] Exportar credenciales de n8n (Settings → Credentials → Export)
- [ ] Anotar variables de entorno de n8n si corría en Docker
- [ ] Guardar el volumen de Docker si tenía ejecuciones/historial importante

---

## FASE 4 — Apps instaladas (inventario)
Abrir PowerShell y correr:
```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select DisplayName, DisplayVersion | Sort DisplayName | Export-Csv "$env:USERPROFILE\Desktop\apps_instaladas.csv" -NoTypeInformation
```
- [ ] Guardar `apps_instaladas.csv` en Drive
- [ ] Anotar apps de la Microsoft Store que uses
- [ ] Anotar extensiones de Chrome (o sincronizar con cuenta Google)
- [ ] Licencias de software pagado que no son por suscripción

---

## FASE 5 — Configuraciones de desarrollo
- [ ] Exportar configuración de VS Code: `Settings Sync` activado con cuenta GitHub/Microsoft
- [ ] Copiar `~/.gitconfig`
- [ ] Copiar configuraciones de terminal (WSL `~/.bashrc`, `~/.zshrc`)
- [ ] Copiar `~/.npmrc`, `~/.pip/pip.conf` si tienen configs custom
- [ ] Exportar snippets, themes, o configs de cualquier editor

---

## FASE 6 — Archivos de negocio
- [ ] Verificar que TODO esté en Google Drive (no solo en local)
- [ ] Carpetas de Descargas → revisar si hay algo sin subir
- [ ] Documentos de Marluvas / Tecmater → en Drive o email
- [ ] Facturas, contratos, documentos legales → Drive
- [ ] Reportes de Amazon / Helium 10 descargados → Drive

---

## FASE 7 — Browser y comunicaciones
- [ ] Chrome sincronizado con cuenta Google (bookmarks, contraseñas, historial)
- [ ] Exportar bookmarks adicionales si hay perfiles sin sync
- [ ] Gmail / Calendar → en la nube, no hay riesgo
- [ ] WhatsApp Web → no guarda historial local, OK
- [ ] Slack → en la nube, OK

---

## FASE 8 — Verificación final antes de entregar
- [ ] Hacer búsqueda en `C:\Users\[tu_usuario\]` por `*.env`, `*.pem`, `*.key` → eliminar o guardar
- [ ] Verificar que la carpeta `MWT KB` local coincide con el remoto
- [ ] Hacer reset de fábrica de Windows (Settings → Recovery → Reset this PC → Remove everything)
- [ ] Confirmar que el gestor de contraseñas está accesible desde otro dispositivo antes del reset

---

## Orden si el tiempo apremia
**1 (secretos) → 2 (código/KB) → 3 (n8n) → 6 (archivos) → 5 (configs) → 4 (inventario apps) → 8 (reset)**
