# ENT_PLAT_NIGHTLY_AUDITOR — Agente Nocturno: KB Health + Amazon Pricing + Key Rotation
id: ENT_PLAT_NIGHTLY_AUDITOR
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: DRAFT — 2026-03-26
refs: POL_HEALTH_CHECK, PLB_AUDIT, health_check.sh, DASHBOARD_SNAPSHOT, ENT_PLAT_INFRA,
      ENT_PLAT_SEGURIDAD, ENT_PLAT_LLM_ROUTING, PLB_OPS_AMAZON, ENT_COMERCIAL_PRICING,
      ENT_MKT_COMPETENCIA, ENT_GOB_KPI
classification: ENTITY — Data pura inyectable. Sin instrucciones de output.
planned_sprint: S21 (Monitor/Activity Feed) — item adicional de observabilidad
aplica_a: [MWT]

---

## A. Propósito

Especificación completa de un agente autónomo que corre cada noche en el servidor Hostinger. Ejecuta 3 jobs modulares en un solo container Docker y entrega un reporte consolidado por email al CEO.

| Job | Qué hace | Dependencia para activar |
|-----|----------|--------------------------|
| **JOB-1: KB Health** | Audita la knowledge base con criterio PLB_AUDIT §D | Git repo en servidor (ya existe) |
| **JOB-2: Amazon Price Watch** | Monitorea precios propios y de competidores en Amazon | SP-API credentials (CEO decisión #2) |
| **JOB-3: Key & Secret Rotation** | Verifica antigüedad de API keys, SSL certs, secrets | Acceso a .env y Docker inspect |

Cada job se activa independientemente. JOB-1 corre desde día 1. JOB-2 y JOB-3 se activan cuando sus dependencias estén resueltas — el script simplemente los salta si faltan credenciales.

El agente NO modifica archivos ni datos. Solo lee, evalúa, y reporta. Las correcciones las ejecuta el CEO, AG-01, o AG-02 en la siguiente sesión.

---

## B. Arquitectura

```
┌─────────────────────────────────────────────────┐
│  Servidor Hostinger (KVM 8)                     │
│                                                 │
│  ┌──────────────────────┐                       │
│  │ mwt-nightly-auditor  │ ← Docker container    │
│  │ (Claude Code CLI)    │                       │
│  │                      │                       │
│  │  1. git pull         │                       │
│  │  2. health_check.sh  │                       │
│  │  3. claude -p SKILL  │ ──→ Anthropic API     │
│  │  4. guardar reporte  │                       │
│  │  5. enviar email     │                       │
│  └──────────┬───────────┘                       │
│             │                                   │
│             ▼                                   │
│  /opt/mwt-knowledge/docs (Git repo, read-only)  │
│  /opt/mwt-nightly/reports/ (output)             │
│  /opt/mwt-nightly/logs/ (logs)                  │
│                                                 │
│  Cron: 0 3 * * * (3:00 AM Costa Rica = UTC-6)  │
└─────────────────────────────────────────────────┘
```

### B1. Recursos estimados

| Recurso | Uso | Impacto en headroom |
|---------|-----|---------------------|
| RAM | ~256 MB (Node.js CLI) | 22 GB → 21.7 GB disponibles |
| CPU | 0.1 core (picos durante API call) | Negligible a las 3 AM |
| Disco | ~100 MB (container + reportes) | Negligible |
| Red | ~100-200 KB por corrida (API call) | Negligible |
| API tokens | ~50-80K input + ~5K output por corrida | ~$0.15-0.25 USD/noche |
| Costo mensual | ~$5-8 USD en tokens API | Incluido en presupuesto operativo |

### B2. Dependencias de infraestructura

| Dependencia | Estado actual | Requerido |
|-------------|--------------|-----------|
| Git repo `mwt-knowledge-base` | ✅ Existe (273+ commits) | Clone en servidor |
| Docker en servidor | ✅ Existe (12 containers) | Agregar 1 container |
| Node.js en container | Se instala en Dockerfile | — |
| ANTHROPIC_API_KEY | [PENDIENTE — CEO proveer] | Variable de entorno |
| SMTP / email sending | [PENDIENTE — CEO-28] | Para entrega del reporte |
| health_check.sh | ✅ Existe en repo | Disponible vía git mount |

---

## C. Dockerfile

```dockerfile
# =============================================================
# mwt-nightly-auditor — Claude Code CLI para auditoría nocturna
# Build: docker build -t mwt-nightly-auditor .
# Run: se invoca via cron, no corre como daemon
# =============================================================

FROM node:20-slim

# Usuario non-root
RUN useradd -m -u 1001 auditor

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    curl \
    msmtp \
    msmtp-mta \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Claude Code CLI (native installer)
RUN curl -fsSL https://claude.ai/install.sh | bash \
    || npm install -g @anthropic-ai/claude-code

# Directorios de trabajo
RUN mkdir -p /workspace /reports /logs \
    && chown -R auditor:auditor /workspace /reports /logs

# Copiar scripts del agente
COPY --chown=auditor:auditor run_audit.sh /usr/local/bin/run_audit.sh
COPY --chown=auditor:auditor SKILL_NIGHTLY_AUDIT.md /opt/skill/SKILL_NIGHTLY_AUDIT.md
COPY --chown=auditor:auditor send_report.sh /usr/local/bin/send_report.sh
RUN chmod +x /usr/local/bin/run_audit.sh /usr/local/bin/send_report.sh

USER auditor
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/run_audit.sh"]
```

---

## D. Script principal: run_audit.sh

```bash
#!/bin/bash
# =============================================================
# MWT Nightly Auditor — Script principal
# Ejecutado por cron cada noche a las 3:00 AM
# =============================================================

set -euo pipefail

TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/logs/audit_${TIMESTAMP}.log"
REPORT_FILE="/reports/NIGHTLY_AUDIT_${TODAY}.md"
KB_DIR="/workspace/docs"
SKILL_FILE="/opt/skill/SKILL_NIGHTLY_AUDIT.md"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================="
echo "  MWT Nightly Auditor"
echo "  Fecha: $TODAY"
echo "  Inicio: $(date)"
echo "========================================="

# ─── PASO 1: Actualizar repo ───
echo ""
echo ">>> Paso 1: git pull..."
cd /workspace
if [ -d ".git" ]; then
  git pull --ff-only origin main 2>&1 || {
    echo "⚠️ git pull falló. Usando versión local."
  }
else
  echo "⚠️ No es un repo git. Usando archivos montados."
fi

# ─── PASO 2: Health check básico ───
echo ""
echo ">>> Paso 2: health_check.sh..."
cd "$KB_DIR"
HEALTH_OUTPUT=$(bash health_check.sh 2>&1) || true
HEALTH_SCORE=$(echo "$HEALTH_OUTPUT" | grep -oP 'SCORE FINAL: \K\d+' || echo "?")
echo "$HEALTH_OUTPUT"
echo ""
echo "Health Score: $HEALTH_SCORE/10"

# ─── PASO 3: Auditoría con Claude Code ───
echo ""
echo ">>> Paso 3: Auditoría profunda con Claude Code..."

# Preparar contexto: listado de archivos + health output + muestras
FILE_LIST=$(ls -1 "$KB_DIR"/*.md 2>/dev/null | wc -l)
STATUS_SUMMARY=$(grep -c "^status: VIGENTE\|^status: ACTIVO" "$KB_DIR"/ENT_*.md "$KB_DIR"/PLB_*.md "$KB_DIR"/POL_*.md 2>/dev/null || echo "0")
DRAFT_COUNT=$(grep -cl "^status: DRAFT" "$KB_DIR"/ENT_*.md "$KB_DIR"/PLB_*.md 2>/dev/null | wc -l)
STUB_COUNT=$(grep -cl "^status: STUB" "$KB_DIR"/ENT_*.md "$KB_DIR"/PLB_*.md 2>/dev/null | wc -l)

# Verificaciones adicionales que health_check.sh no cubre
echo ""
echo ">>> Checks extendidos..."

# E1: DRAFTs estancados (>30 días sin cambio en changelog)
STALE_DRAFTS=""
for f in "$KB_DIR"/ENT_*.md "$KB_DIR"/PLB_*.md; do
  st=$(grep -oP '^status: \K.*' "$f" 2>/dev/null | head -1)
  if [ "$st" = "DRAFT" ]; then
    last_date=$(grep -oP '\d{4}-\d{2}-\d{2}' "$f" 2>/dev/null | sort | tail -1)
    if [ -n "$last_date" ]; then
      days_ago=$(( ($(date +%s) - $(date -d "$last_date" +%s 2>/dev/null || echo $(date +%s))) / 86400 ))
      if [ "$days_ago" -gt 30 ]; then
        STALE_DRAFTS="$STALE_DRAFTS\n  - $(basename $f): última fecha $last_date ($days_ago días)"
      fi
    fi
  fi
done

# E2: POLs próximas a vencer
EXPIRING_POLS=""
WARN_DATE=$(date -d "+30 days" +%Y-%m-%d 2>/dev/null || date -v+30d +%Y-%m-%d 2>/dev/null || echo "")
for f in "$KB_DIR"/POL_*.md; do
  VENC=$(grep -ioP '[Vv]encimiento: \K\d{4}-\d{2}-\d{2}' "$f" 2>/dev/null)
  if [ -n "$VENC" ] && [ -n "$WARN_DATE" ]; then
    if [[ "$VENC" < "$WARN_DATE" ]] && [[ "$VENC" > "$TODAY" ]]; then
      EXPIRING_POLS="$EXPIRING_POLS\n  - $(basename $f): vence $VENC"
    fi
  fi
done

# E3: Archivos sin id: que deberían tenerlo
MISSING_ID=$(grep -rL "^id:" "$KB_DIR"/ENT_*.md "$KB_DIR"/PLB_*.md "$KB_DIR"/POL_*.md "$KB_DIR"/SCH_*.md "$KB_DIR"/LOC_*.md 2>/dev/null | xargs -I{} basename {} || echo "")

# E4: Conteo canónico vs DASHBOARD_SNAPSHOT
ACTUAL_COUNT=$(ls "$KB_DIR"/*.md "$KB_DIR"/*.json "$KB_DIR"/*.sh "$KB_DIR"/*.html 2>/dev/null | wc -l)
DASHBOARD_COUNT=$(grep -oP 'Archivos totales \| \K\d+' "$KB_DIR"/DASHBOARD_SNAPSHOT.md 2>/dev/null || echo "?")

# E5: RW_ROOT version vs DASHBOARD version
RW_VER=$(grep -oP 'v\d+\.\d+(\.\d+)?' "$KB_DIR"/RW_ROOT.md 2>/dev/null | tail -1 || echo "?")
DASH_RW_VER=$(grep -A1 'RW_ROOT' "$KB_DIR"/DASHBOARD_SNAPSHOT.md 2>/dev/null | grep -oP 'v\d+\.\d+(\.\d+)?' | head -1 || echo "?")

# Construir prompt con contexto
AUDIT_CONTEXT=$(cat <<CTXEOF
# Contexto para auditoría nocturna — $TODAY

## Health Check Score: $HEALTH_SCORE/10
$HEALTH_OUTPUT

## Métricas KB
- Archivos .md: $FILE_LIST
- Archivos VIGENTE/ACTIVO: $STATUS_SUMMARY
- Archivos DRAFT: $DRAFT_COUNT
- Archivos STUB: $STUB_COUNT
- Conteo canónico real: $ACTUAL_COUNT
- Conteo en DASHBOARD: $DASHBOARD_COUNT
- RW_ROOT version: $RW_VER
- DASHBOARD RW_ROOT version: $DASH_RW_VER

## Checks Extendidos
### DRAFTs estancados (>30 días sin actividad):
$(if [ -n "$STALE_DRAFTS" ]; then echo -e "$STALE_DRAFTS"; else echo "  Ninguno."; fi)

### POLs próximas a vencer (30 días):
$(if [ -n "$EXPIRING_POLS" ]; then echo -e "$EXPIRING_POLS"; else echo "  Ninguna."; fi)

### Archivos sin id: (ENT/PLB/POL/SCH/LOC):
$(if [ -n "$MISSING_ID" ]; then echo "  $MISSING_ID"; else echo "  Ninguno."; fi)

### Drift de conteo (real vs DASHBOARD):
$(if [ "$ACTUAL_COUNT" != "$DASHBOARD_COUNT" ]; then echo "  ⚠️ DRIFT: real=$ACTUAL_COUNT vs dashboard=$DASHBOARD_COUNT"; else echo "  ✅ Sincronizados."; fi)

### Drift de versión RW_ROOT:
$(if [ "$RW_VER" != "$DASH_RW_VER" ]; then echo "  ⚠️ DRIFT: RW_ROOT=$RW_VER vs DASHBOARD=$DASH_RW_VER"; else echo "  ✅ Sincronizados."; fi)
CTXEOF
)

# Guardar contexto temporal
echo "$AUDIT_CONTEXT" > /tmp/audit_context.md

# Ejecutar Claude Code en modo headless
cd "$KB_DIR"
claude -p "$(cat "$SKILL_FILE")

---
CONTEXTO DE ESTA CORRIDA:
$(cat /tmp/audit_context.md)" \
  --output-format text \
  --allowedTools Read,Grep,Glob \
  --dangerously-skip-permissions \
  > "$REPORT_FILE" 2>> "$LOG_FILE" || {
    echo "⚠️ Claude Code falló. Generando reporte básico..."
    # Fallback: reporte con solo los datos del shell
    cat > "$REPORT_FILE" <<FALLBACK
# NIGHTLY AUDIT — $TODAY (modo fallback)

Claude Code no pudo ejecutar la auditoría profunda. Reporte básico:

## Health Check: $HEALTH_SCORE/10
$HEALTH_OUTPUT

## Checks Extendidos
$AUDIT_CONTEXT

---
Generado en modo fallback (sin análisis LLM).
FALLBACK
}

echo ""
echo ">>> Reporte generado: $REPORT_FILE"

# ─── PASO 4: Enviar por email ───
echo ""
echo ">>> Paso 4: Enviando reporte por email..."
/usr/local/bin/send_report.sh "$REPORT_FILE" "$TODAY" "$HEALTH_SCORE" 2>> "$LOG_FILE" || {
  echo "⚠️ Email falló. Reporte disponible en: $REPORT_FILE"
}

# ─── PASO 5: Limpieza ───
# Mantener últimos 30 reportes
ls -t /reports/NIGHTLY_AUDIT_*.md 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null || true
ls -t /logs/audit_*.log 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null || true

echo ""
echo "========================================="
echo "  Auditoría completada: $(date)"
echo "  Score: $HEALTH_SCORE/10"
echo "========================================="
```

---

## E. Prompt del Agente: SKILL_NIGHTLY_AUDIT.md

```markdown
# MWT KB Nightly Auditor — SKILL

Eres el auditor nocturno de la knowledge base MWT / Rana Walk.
Tu trabajo es evaluar el estado de salud de la KB y generar un plan de acción
priorizado para mantener el health score en 10/10.

## Qué eres
- Un auditor independiente. No creaste estos archivos — solo los evalúas.
- Aplicas criterio PLB_AUDIT §D: Corrección > Completitud > Consistencia > Ejecutabilidad > Claridad.
- No inventas datos (R1). No modificas archivos. Solo reportas.

## Qué evalúas (en orden de prioridad)

### HARD (bloquean trabajo)
1. **Health check score <10**: Cada H-check fallido es un item de acción con fix concreto.
2. **Referencias rotas (H6)**: Listar cada una con archivo fuente y fix.
3. **Policies vencidas (H9)**: Listar con fecha de vencimiento y impacto.
4. **Drift de datos**: Conteos en DASHBOARD_SNAPSHOT vs realidad. Versiones RW_ROOT desincronizadas.

### SOFT (reportar, no bloquean)
5. **DRAFTs estancados >30 días**: Candidatos a promover, completar, o deprecar.
6. **STUBs huérfanos**: Sin contenido y sin plan de llenado visible.
7. **Headers incompletos**: Archivos sin id:/version:/status:/visibility:/domain:.
8. **POLs próximas a vencer**: 30 días de anticipación.
9. **Deuda técnica nueva**: Comparar con DASHBOARD_SNAPSHOT.deuda_conocida — si algo nuevo aparece, flaggearlo.
10. **Duplicación detectada**: Datos que aparecen en más de un lugar.

### INFO (observación)
11. **Tendencia**: Comparar con reporte de ayer si existe (mismo directorio).
12. **Resumen ejecutivo**: 3 líneas máximo con lo más importante.

## Formato del reporte

```
# NIGHTLY AUDIT — {FECHA}
## Score: {health_score}/10

## Resumen Ejecutivo
[3 líneas máximo. Lo más importante primero.]

## Acciones HARD (bloquean trabajo)
| # | Problema | Archivo | Fix concreto | Ref |
|---|----------|---------|-------------|-----|
[Numeradas. Fix concreto, no vago.]

## Acciones SOFT (mejora continua)
| # | Problema | Archivo | Recomendación | Prioridad |
|---|----------|---------|--------------|-----------|
[Prioridad: ALTA/MEDIA/BAJA]

## Observaciones
[Tendencias, patterns, cosas que notar.]

## Métricas
| Métrica | Valor |
|---------|-------|
| Archivos totales | {N} |
| VIGENTE/ACTIVO | {N} |
| DRAFT | {N} |
| STUB | {N} |
| DRAFTs estancados | {N} |
| POLs por vencer | {N} |
| Drift detectado | Sí/No |

---
Generado por MWT Nightly Auditor v1.0
Modelo: claude-sonnet-4-6
Tokens estimados: ~{N}K input
```

## Reglas
- Score numérico obligatorio.
- Cada problema tiene fix concreto (no "considerar mejorar").
- Máximo 15 items SOFT (los más importantes). No listar todo.
- Si health_check.sh = 10/10 y no hay drift ni DRAFTs estancados:
  reporte corto, 5 líneas, "KB sana, sin acciones requeridas".
- NUNCA inventar datos. Si no puedes verificar algo, decir "no verificable sin acceso a [X]".
```

---

## F. Script de email: send_report.sh

```bash
#!/bin/bash
# =============================================================
# Envía el reporte nocturno por email via msmtp
# Uso: send_report.sh <reporte.md> <fecha> <score>
# =============================================================

REPORT_FILE="$1"
DATE="$2"
SCORE="$3"
CEO_EMAIL="${CEO_EMAIL:-[PENDIENTE — CEO proveer]}"

if [ -z "$CEO_EMAIL" ] || [ "$CEO_EMAIL" = "[PENDIENTE — CEO proveer]" ]; then
  echo "⚠️ CEO_EMAIL no configurado. Saltando envío."
  exit 1
fi

# Determinar emoji por score
if [ "$SCORE" = "10" ]; then
  EMOJI="✅"
  URGENCY=""
elif [ "$SCORE" -ge "8" ] 2>/dev/null; then
  EMOJI="⚠️"
  URGENCY=""
else
  EMOJI="🔴"
  URGENCY="[URGENTE] "
fi

SUBJECT="${URGENCY}${EMOJI} MWT KB Audit — ${DATE} — Score: ${SCORE}/10"

# Enviar con msmtp
{
  echo "Subject: $SUBJECT"
  echo "From: auditor@mwt.one"
  echo "To: $CEO_EMAIL"
  echo "Content-Type: text/plain; charset=UTF-8"
  echo ""
  cat "$REPORT_FILE"
} | msmtp "$CEO_EMAIL"

echo "✅ Email enviado a $CEO_EMAIL"
```

---

## G. docker-compose.yml (fragmento para agregar al stack existente)

```yaml
  # Agregar a docker-compose.yml existente
  # NO es un servicio persistente — se invoca via cron
  nightly-auditor:
    build:
      context: ./nightly-auditor
      dockerfile: Dockerfile
    container_name: mwt-nightly-auditor
    volumes:
      - /opt/mwt-knowledge/docs:/workspace/docs:ro
      - nightly-reports:/reports
      - nightly-logs:/logs
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CEO_EMAIL=${CEO_EMAIL}
    env_file:
      - .env
    restart: "no"  # NO daemon — se invoca via cron
    profiles:
      - tools  # No se levanta con docker-compose up normal

volumes:
  nightly-reports:
  nightly-logs:
```

---

## H. Cron job en el host

```bash
# Agregar al crontab del servidor (crontab -e)
# Corre a las 3:00 AM hora Costa Rica (UTC-6 = 09:00 UTC)
0 9 * * * docker compose -f /opt/mwt/docker-compose.yml run --rm --profile tools nightly-auditor >> /var/log/mwt-nightly-auditor.log 2>&1
```

---

## I. Configuración msmtp (email)

```bash
# /opt/mwt-nightly/msmtprc — montar en el container
# Configuración depende de CEO-28 (email provider)

# Opción A: Gmail SMTP
account gmail
host smtp.gmail.com
port 587
auth on
user [PENDIENTE — CEO proveer]
password [PENDIENTE — App Password de Gmail]
from auditor@mwt.one
tls on
tls_starttls on

# Opción B: SendGrid
account sendgrid
host smtp.sendgrid.net
port 587
auth on
user apikey
password [PENDIENTE — SendGrid API key]
from auditor@mwt.one
tls on

# Opción C: Amazon SES (si se elige para CEO-28)
account ses
host email-smtp.us-east-1.amazonaws.com
port 587
auth on
user [PENDIENTE — SES SMTP user]
password [PENDIENTE — SES SMTP password]
from auditor@mwt.one
tls on

account default : gmail  # Cambiar al provider elegido
```

---

## J. Guía de setup para AG-02 (Alejandro)

### Prerequisitos
1. ANTHROPIC_API_KEY configurada en `.env` del servidor
2. CEO-28 resuelto (email provider elegido)
3. Git repo `mwt-knowledge-base` clonado en `/opt/mwt-knowledge/docs`
4. Docker Compose v2+ en el servidor (ya existe)

### Pasos de instalación

```bash
# 1. Crear directorio del auditor
mkdir -p /opt/mwt-nightly/nightly-auditor

# 2. Crear los 4 archivos del agente:
#    - Dockerfile (sección C de este documento)
#    - run_audit.sh (sección D)
#    - SKILL_NIGHTLY_AUDIT.md (sección E)
#    - send_report.sh (sección F)

# 3. Agregar al docker-compose.yml (sección G)

# 4. Configurar msmtp (sección I — según provider elegido)

# 5. Agregar variables al .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> /opt/mwt/.env
echo "CEO_EMAIL=ceo@mwt.one" >> /opt/mwt/.env

# 6. Build del container
docker compose build nightly-auditor

# 7. Test manual
docker compose run --rm --profile tools nightly-auditor

# 8. Verificar que el reporte se generó
ls /opt/mwt-nightly/reports/

# 9. Verificar que el email llegó

# 10. Agregar cron (sección H)
crontab -e
# Pegar la línea de cron

# 11. Verificar cron
crontab -l | grep nightly
```

### Tiempo estimado: 1-2 horas (incluye troubleshooting email)

---

## K. Ubicación en el Roadmap

| Opción | Sprint | Justificación |
|--------|--------|---------------|
| **Recomendada** | S21 (Monitor/Activity Feed) | Sprint de observabilidad. El auditor nocturno es monitoring de la KB, complementa el activity feed de expedientes. |
| Alternativa | Item paralelo a S18-S19 | Si el CEO quiere monitoring ASAP, puede correr en paralelo porque no tiene dependencias de código. Solo necesita ANTHROPIC_API_KEY + email. |

### Items de sprint (para agregar al LOTE correspondiente)

| ID | Tarea | Tipo | Agente | Dependencia |
|----|-------|------|--------|-------------|
| SXX-N1 | Crear directorio /opt/mwt-nightly/ con 4 archivos del agente | Setup | AG-02 | Git repo operativo |
| SXX-N2 | Agregar nightly-auditor al docker-compose.yml (profile: tools) | Docker | AG-02 | — |
| SXX-N3 | Configurar msmtp con provider elegido (CEO-28) | Config | AG-02 | CEO-28 resuelto |
| SXX-N4 | Build + test manual del container | Test | AG-02 | N1, N2, N3 |
| SXX-N5 | Configurar cron job en host | Cron | AG-02 | N4 pass |
| SXX-N6 | Verificar email recibido con reporte correcto | Validación | CEO | N5 |

### Gate
- Container ejecuta sin errores
- health_check.sh score coincide con reporte
- Email recibido con subject correcto y contenido legible
- Reporte persiste en /opt/mwt-nightly/reports/
- Limpieza automática mantiene solo últimos 30 reportes

---

## L. JOB-2: Amazon Competitive Intelligence

### L1. Origen

Proyecto existente: `Competitor-Agent/` — agente Claude Code ya operativo con CLAUDE.md v2.0, 3 custom commands, 17 ASINs tracked (5 CORE + 5 SECONDARY + 5 BENCHMARK + DISCOVERY + propio), 10 keywords (5 T1 + 5 T2), y data real del 2026-03-24.

El CEO lo corre manualmente hoy. Este job lo automatiza dentro del container nocturno.

### L2. Estado actual del proyecto

```
Competitor-Agent/
├── .claude/
│   ├── commands/
│   │   ├── daily-morning.md    # SERP scan + offer monitor
│   │   ├── discover.md         # Buscar nuevos competidores
│   │   └── weekly.md           # Reporte semanal correlacionado
│   └── settings.local.json     # Permisos: WebSearch, WebFetch(amazon.com)
├── CLAUDE.md                   # Prompt del agente v2.0
├── config/
│   ├── tracked_asins.json      # 17 ASINs (v2.2, actualizado 2026-03-25)
│   └── keywords.json           # 5 T1 + 5 T2 keywords
├── data/
│   ├── snapshots/{ASIN}/{fecha}/  # L1_serp.json, L3_offer.json, L4_listing.json
│   ├── alerts/pending.jsonl       # (vacío actualmente)
│   ├── reports/weekly/            # W13 report existe
│   └── logs/                      # morning-2026-03-24.log
└── docs/                          # Prompts auxiliares y hallazgos
```

### L3. ASINs tracked (snapshot actual)

| Tier | ASINs | Ejemplo |
|------|-------|---------|
| CORE (competencia directa) | 5 | VALSOLE B0BM64FRDB ($35.98, 56K ventas/mes), CRUVHEAL, PCSsole ($37.99 = mismo precio), Dr. Scholl's, VALSOLE 250+ |
| SECONDARY (overlap parcial) | 5 | PowerStep, Psveb (newcomer 4.8★), WalkHero (49K/mes), CRUVHEAL M, B098PZGD4F |
| BENCHMARK (referencia) | 5 | Superfeet Blue/Green/XL, currex RunPro/M |
| DISCOVERY | dinámico | Escaneo de keywords → auto-agregar si cumple criterio |
| PROPIO | 1 | Goliath (ASIN: PENDIENTE — no lanzado aún) |

### L4. Cadencia automatizada

| Cron (UTC) | Cron (CR, UTC-6) | Job | Comando Claude Code |
|------------|-------------------|-----|-------------------|
| `0 9 * * *` | 3:00 AM | JOB-1: KB Health | (script propio, no usa commands) |
| `30 9 * * *` | 3:30 AM | JOB-2 night: listing+reviews | `/daily-night` (comando custom, por crear) |
| `0 13 * * *` | 7:00 AM | JOB-2 morning: SERP+precios | `/daily-morning` (comando existente) |
| `0 10 * * 0` | 4:00 AM domingos | JOB-2 weekly: reporte | `/weekly` (comando existente) |

**Nota:** `/daily-night` no existe aún como comando custom. Actualmente el CLAUDE.md menciona la cadencia pero el comando `.claude/commands/daily-night.md` no fue creado. Se debe crear con scope: listing tracker + review miner.

### L5. Script wrapper: run_amazon_intel.sh

```bash
#!/bin/bash
# =============================================================
# JOB-2: Amazon Competitive Intelligence
# Wrapper para ejecutar comandos del agente Competitor-Agent
# =============================================================

INTEL_DIR="/opt/mwt-nightly/Competitor-Agent"
COMMAND="${1:-/daily-morning}"
LOG_FILE="/logs/amazon_intel_$(date +%Y%m%d_%H%M%S).log"

echo ">>> JOB-2: Amazon Intel — comando: $COMMAND" | tee -a "$LOG_FILE"

# ─── Gate: verificar que el proyecto existe ───
if [ ! -f "$INTEL_DIR/CLAUDE.md" ]; then
  echo "⏭️  JOB-2 SKIP: $INTEL_DIR/CLAUDE.md no encontrado." | tee -a "$LOG_FILE"
  echo "JOB2_STATUS=SKIPPED" >> /tmp/job_status.env
  exit 0
fi

if [ ! -f "$INTEL_DIR/config/tracked_asins.json" ]; then
  echo "⏭️  JOB-2 SKIP: tracked_asins.json no configurado." | tee -a "$LOG_FILE"
  echo "JOB2_STATUS=SKIPPED" >> /tmp/job_status.env
  exit 0
fi

cd "$INTEL_DIR"

# ─── Ejecutar Claude Code con el proyecto ───
claude -p "$COMMAND" \
  --output-format text \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

# ─── Contar alertas pendientes ───
ALERT_COUNT=0
if [ -f "data/alerts/pending.jsonl" ]; then
  ALERT_COUNT=$(wc -l < "data/alerts/pending.jsonl")
fi

# ─── Resumen para el reporte consolidado ───
echo "JOB2_STATUS=DONE" >> /tmp/job_status.env
echo "JOB2_EXIT=$EXIT_CODE" >> /tmp/job_status.env
echo "JOB2_ALERTS=$ALERT_COUNT" >> /tmp/job_status.env
echo "JOB2_COMMAND=$COMMAND" >> /tmp/job_status.env

echo "JOB-2 completado. Exit: $EXIT_CODE. Alertas: $ALERT_COUNT" | tee -a "$LOG_FILE"
```

### L6. Alertas que genera

| Alerta | Trigger | Severidad | Acción CEO |
|--------|---------|-----------|-----------|
| PRICE_DROP | Competidor baja precio >8% vs día anterior | ALTA | Evaluar respuesta pricing |
| PRICE_UNDERCUT | Competidor debajo de $37.99 (precio Goliath) | CRÍTICA | Evaluar margen vs volumen |
| NEW_COMPETITOR | ASIN nuevo en top 15 de keyword T1 (via /discover) | MEDIA | Revisar y decidir tracking |
| BSR_SPIKE | Competidor sube >50 posiciones BSR en 7 días | MEDIA | Investigar causa |
| REVIEW_SURGE | Competidor gana >20 reviews en 7 días | MEDIA | Posible Vine o manipulación |
| LISTING_CHANGE | Competidor cambia título o imagen principal | BAJA | Info para next A/B test |
| OWN_BSR_DROP | Nuestro BSR cae >30% en 7 días | ALTA | Investigar (stock? PPC? review?) |

### L7. Sección del email nocturno (JOB-2)

```
## 📊 Amazon Intel — {FECHA}

**Alertas nuevas:** {N} ({N} CRITICAL, {N} HIGH, {N} MEDIUM)

### Precios competidores CORE (si hay cambio)
| Brand | ASIN | Ayer | Hoy | Δ |
|-------|------|------|-----|---|
[Solo filas con cambio. Si 0 cambios: "Sin cambios de precio en CORE."]

### Snapshot propio
| Métrica | Valor |
|---------|-------|
| BSR subcategoría | {N} |
| Rating | {X.X} ★ |
| Reviews | {N} |

**Reporte semanal:** {si es domingo: adjunto. Si no: "Próximo domingo."}
```

### L8. Dependencias para activar JOB-2

| Dependencia | Estado | Acción |
|-------------|--------|--------|
| Container nocturno operativo | [PENDIENTE] | Sprint 21 |
| Copiar Competitor-Agent/ al servidor | [PENDIENTE] | CEO: `scp -r Competitor-Agent/ server:/opt/mwt-nightly/` |
| Crear comando `/daily-night` | [PENDIENTE] | CEO o AG-01: crear `.claude/commands/daily-night.md` |
| ASIN propio (Goliath) | PENDIENTE en tracked_asins.json | CEO: actualizar cuando se lance |

**No requiere SP-API.** Usa WebSearch + WebFetch(amazon.com) — scraping público. Independiente del Track T2.

### L9. Docker volumes adicionales

```yaml
# Agregar al servicio nightly-auditor en docker-compose.yml
volumes:
  - /opt/mwt-nightly/Competitor-Agent:/opt/mwt-nightly/Competitor-Agent
```

Los snapshots se acumulan (~2KB por ASIN por día × 17 ASINs = ~34KB/día = ~1MB/mes). Negligible.

---

## M. JOB-3: Key & Secret Rotation Monitor

### M1. Qué hace

Verifica la antigüedad de API keys, secrets, y certificados SSL. No rota nada — solo reporta qué necesita atención. Corre como script bash puro (sin Claude Code, sin tokens API).

Ref → ENT_PLAT_SEGURIDAD §B4 (inventario secrets) y §H (cadencia: cada 90 días).

### M2. Inventario de secrets

| Secret | Ubicación | Política rotación | Cómo verificar |
|--------|-----------|-------------------|----------------|
| ANTHROPIC_API_KEY | .env | 90 días | mtime de .env o timestamp en .env.metadata |
| Django SECRET_KEY | .env | 90 días | mtime de .env |
| PostgreSQL password | .env | 90 días | mtime de .env |
| Redis password | .env | 90 días | Si existe (hoy [PENDIENTE]) |
| MinIO access/secret | .env | 90 días | mtime de .env |
| SSL certs | /etc/letsencrypt/ | Auto (Certbot) | `openssl x509 -enddate` |
| SP-API refresh token | .env (futuro) | Per Amazon policy | mtime |
| LLM_ENCRYPTION_KEY | .env (futuro) | 180 días (MultiFernet) | mtime |

### M3. Script: run_key_check.sh

```bash
#!/bin/bash
# =============================================================
# JOB-3: Key & Secret Rotation Monitor
# No usa Claude Code — solo bash + openssl
# Costo: $0 (no consume tokens API)
# =============================================================

MAX_AGE_DAYS=90
TODAY_EPOCH=$(date +%s)
REPORT=""
WARNINGS=0

echo ">>> JOB-3: Key & Secret Rotation Check"

# ─── Check 1: .env file age ───
ENV_FILE="/opt/mwt/.env"
if [ -f "$ENV_FILE" ]; then
  ENV_MTIME=$(stat -c %Y "$ENV_FILE" 2>/dev/null || stat -f %m "$ENV_FILE" 2>/dev/null)
  ENV_AGE_DAYS=$(( (TODAY_EPOCH - ENV_MTIME) / 86400 ))
  if [ "$ENV_AGE_DAYS" -gt "$MAX_AGE_DAYS" ]; then
    REPORT="$REPORT\n🔴 .env tiene $ENV_AGE_DAYS días sin modificar (política: $MAX_AGE_DAYS). Rotar secrets."
    WARNINGS=$((WARNINGS + 1))
  elif [ "$ENV_AGE_DAYS" -gt 60 ]; then
    REPORT="$REPORT\n🟡 .env tiene $ENV_AGE_DAYS días. Rotación en $((MAX_AGE_DAYS - ENV_AGE_DAYS)) días."
  else
    REPORT="$REPORT\n🟢 .env: $ENV_AGE_DAYS días (OK)."
  fi
else
  REPORT="$REPORT\n🔴 .env no encontrado en $ENV_FILE"
  WARNINGS=$((WARNINGS + 1))
fi

# ─── Check 2: SSL certificate expiry ───
for DOMAIN in mwt.one ranawalk.com portal.mwt.one; do
  CERT_FILE="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
  if [ -f "$CERT_FILE" ]; then
    EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo 0)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - TODAY_EPOCH) / 86400 ))
    if [ "$DAYS_LEFT" -lt 7 ]; then
      REPORT="$REPORT\n🔴 SSL $DOMAIN: expira en $DAYS_LEFT días! Certbot renewal urgente."
      WARNINGS=$((WARNINGS + 1))
    elif [ "$DAYS_LEFT" -lt 30 ]; then
      REPORT="$REPORT\n🟡 SSL $DOMAIN: expira en $DAYS_LEFT días. Verificar auto-renewal."
    else
      REPORT="$REPORT\n🟢 SSL $DOMAIN: $DAYS_LEFT días restantes (OK)."
    fi
  else
    REPORT="$REPORT\n⚪ SSL $DOMAIN: cert no encontrado en path esperado."
  fi
done

# ─── Check 3: Redis auth ───
REDIS_HAS_PASS=$(grep -c "REDIS_PASSWORD\|requirepass" "$ENV_FILE" 2>/dev/null || echo 0)
if [ "$REDIS_HAS_PASS" -eq 0 ]; then
  REPORT="$REPORT\n🟡 Redis: sin password detectado en .env (ref ENT_PLAT_SEGURIDAD §Z5)."
fi

# ─── Check 4: Sensitive keys present in git ───
GIT_DIR="/opt/mwt-knowledge/docs"
if [ -d "$GIT_DIR/.git" ]; then
  LEAKED=$(git -C "$GIT_DIR" log --all -p 2>/dev/null | grep -ciE "sk-ant-|ANTHROPIC_API_KEY|SECRET_KEY=" || echo 0)
  if [ "$LEAKED" -gt 0 ]; then
    REPORT="$REPORT\n🔴 Posible API key en historial Git ($LEAKED matches). Verificar manualmente."
    WARNINGS=$((WARNINGS + 1))
  else
    REPORT="$REPORT\n🟢 Git history: sin API keys detectadas."
  fi
fi

# ─── Output ───
echo "JOB3_STATUS=DONE" >> /tmp/job_status.env
echo "JOB3_WARNINGS=$WARNINGS" >> /tmp/job_status.env

echo -e "$REPORT"
echo -e "$REPORT" > /tmp/job3_report.txt
```

### M4. Sección del email nocturno (JOB-3)

```
## 🔑 Secrets & Certs — {FECHA}

{output de run_key_check.sh — semáforos 🟢🟡🔴}

**Warnings:** {N}
```

### M5. Cron schedule

JOB-3 corre dentro del mismo cron de las 3AM (es instantáneo, no usa API). Se ejecuta ANTES de JOB-1 y JOB-2 porque si las keys están mal, los otros jobs podrían fallar.

---

## N. Cron Schedule Consolidado

```bash
# /etc/crontab del servidor — todos los jobs nocturnos

# 3:00 AM CR (09:00 UTC) — JOB-1 KB Health + JOB-3 Keys + JOB-2 night
0 9 * * * root docker compose -f /opt/mwt/docker-compose.yml run --rm --profile tools nightly-auditor >> /var/log/mwt-nightly.log 2>&1

# 7:00 AM CR (13:00 UTC) — JOB-2 morning (SERP scan + precios)
0 13 * * * root docker compose -f /opt/mwt/docker-compose.yml run --rm --profile tools nightly-auditor morning >> /var/log/mwt-morning.log 2>&1

# 4:00 AM CR domingos (10:00 UTC) — JOB-2 weekly report
0 10 * * 0 root docker compose -f /opt/mwt/docker-compose.yml run --rm --profile tools nightly-auditor weekly >> /var/log/mwt-weekly.log 2>&1
```

El entrypoint (`run_audit.sh`) recibe un argumento: vacío = nightly full (JOB-3 + JOB-1 + JOB-2 night), `morning` = solo JOB-2 morning, `weekly` = solo JOB-2 weekly.

---

## O. Evolución futura

| Fase | Qué | Cuándo |
|------|-----|--------|
| v1.0 (esta spec) | JOB-1 KB Health + email | Sprint 21 |
| v1.1 | +JOB-3 Key Monitor (bash puro, sin costo) | Mismo sprint (trivial) |
| v1.2 | +JOB-2 Amazon Intel (requiere copiar Competitor-Agent al servidor) | Sprint 21 o paralelo |
| v1.3 | Crear `/daily-night` command (listing tracker + review miner) | Post-v1.2 |
| v1.4 | Comparación con reporte de ayer (tendencia KB + Amazon) | Post-v1.2 |
| v2.0 | Integración con n8n: alerta urgente si score <8 o PRICE_UNDERCUT | Post-Sprint 20 (emails) |
| v2.1 | KB auditoría profunda: muestreo archivos, verificar SSOT, determinismo | Post-pgvector operativo |
| v3.0 | Dashboard de tendencias: health score, precios competidores, key expiry | Post-T3.C1 (Command Center) |

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | ANTHROPIC_API_KEY para el servidor | CEO proveer | JOB-1 y JOB-2 (container no corre sin key) |
| Z2 | CEO-28: email provider | Decisión CEO | Envío de reportes |
| Z3 | CEO_EMAIL: dirección de destino | CEO proveer | Envío de reportes |
| Z4 | Decidir sprint de ejecución (S21 o paralelo) | Decisión CEO | Planificación AG-02 |
| Z5 | Copiar Competitor-Agent/ al servidor | CEO acción | JOB-2 Amazon Intel |
| Z6 | Crear comando `/daily-night` en .claude/commands/ | CEO o AG-01 | Cadencia nocturna JOB-2 |
| Z7 | Actualizar ASIN propio en tracked_asins.json cuando Goliath lance | CEO acción | Monitoreo precio propio |

---

Changelog:
- v1.0 (2026-03-26): Creación. JOB-1 KB Health completo con Dockerfile, scripts, SKILL, cron, email, guía AG-02.
- v1.1 (2026-03-26): +JOB-2 Amazon Competitive Intelligence (integración de Competitor-Agent existente). +JOB-3 Key & Secret Rotation Monitor. Cron schedule consolidado con 3 cadencias. 7 pendientes.
