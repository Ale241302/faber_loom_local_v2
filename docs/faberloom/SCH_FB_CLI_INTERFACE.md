# SCH_FB_CLI_INTERFACE — Interfaz CLI del Agent Builder FaberLoom
id: SCH_FB_CLI_INTERFACE
version: 2.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29c + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_AGENT_BUILDER_v1.md · SCH_FB_SKILL_MANIFEST_v2.md · SCH_FB_TASK_ENTITY.md

---

## Declaración

Este schema define la **interfaz de línea de comandos `fbl`** (FaberLoom CLI) para invocar agents, skills, templates y tareas desde la consola. Operacionaliza el principio "para cada cosa que se hace, puede haber un agente que se invoque desde la consola" (sesión Cowork 2026-04-29c).

El CLI es **multi-tenant aware** desde día 1: el tenant se especifica vía `--tenant` o variable de entorno `FBL_TENANT`. En FB v1 beta con un solo tenant, default `--tenant=mwt` está implícito.

**Deuda de naming:** la sesión original de diseño usó comando `mwt` por error de scoping. El comando correcto siempre fue `fbl` (FaberLoom platform CLI). Los ejemplos del documento conservan el comando `mwt` como referencia histórica en algunos lugares — leer como `fbl` con default tenant. Migración del comando es trivial (alias bash `mwt = fbl --tenant=mwt`).

**Stack:** Python CLI usando `click` o `typer`, wrapper sobre los endpoints REST de Django de la plataforma FB. Cero overhead — la misma consola que ya manejás para `git`, `docker`, `npm`.

---

## Por qué este documento existe

Sin CLI estandarizada:
- Cada SKILL se invoca de forma distinta (algunos via curl, otros via Django shell, otros via dashboard)
- Difícil incluir invocaciones en scripts automatizados (cron de tu máquina, GitHub Actions, etc.)
- No hay surface unificada para CEO o equipos futuros

Con CLI:
- Comando único `mwt agent run X` o `mwt skill run Y`
- Output JSON-friendly para scripting (`--output=json`)
- Auth automática (token en `~/.mwt/credentials`)
- Extensible: cada nuevo agent se vuelve invocable sin cambios al CLI

---

## Estructura de comandos

```
mwt
├── agent
│   ├── list                                # lista todos los agents
│   ├── show <agent_id>                     # detalle de un agent
│   ├── run <agent_id> [--payload=...]      # invoca un agent (crea task)
│   ├── shadow <agent_id>                   # ver runs SHADOW últimos 30d
│   ├── graduate <agent_id>                 # propone promoción a nivel siguiente (CEO firma)
│   └── kill <agent_id>                     # vuelve a SHADOW
├── skill
│   ├── list                                # lista todos los skills
│   ├── show <skill_id>                     # detalle del skill
│   ├── run <skill_id> [--input=...]        # ejecuta skill standalone
│   └── refine <skill_id>                   # abre prompt para refinar instructions (CEO firma)
├── template
│   ├── list                                # lista templates disponibles
│   ├── show <tpl_id>                       # detalle del template
│   ├── fork <tpl_id> [--name=...]          # instancia template como agent nuevo
│   └── catalog                             # ver templates agrupados por architectural_archetype
├── task
│   ├── queue                               # ver cola de tasks
│   ├── show <task_id>                      # detalle de una task
│   ├── approve <task_id>                   # aprobar task en awaiting_approval
│   ├── reject <task_id> [--reason=...]     # rechazar task
│   └── cancel <task_id>                    # cancelar task
├── trigger
│   ├── list                                # ver triggers activos (cron, webhooks)
│   ├── test <trigger_id>                   # ejecutar trigger manualmente para probar
│   └── pause <trigger_id> / resume <trigger_id>
├── stats
│   ├── agent <agent_id> [--days=30]        # métricas L0-L5 del agent
│   ├── cost [--month=2026-04]              # cost total por agent
│   └── outcome <agent_id>                  # outcome trending vs target_at_60d
└── builder
    ├── new                                 # bootstrap mode interactivo (Plan preview + Edit/Start)
    ├── compile <manifest.yaml>             # valida y compila manifest local
    └── audit [--type=...]                  # audit visibility / outcomes / gaps
```

---

## Comandos clave en detalle

### `mwt agent run`

Invoca un agent ad-hoc desde consola. Crea Task con `invocation_mode: ad_hoc`, `invoked_by: ceo` (lee de `~/.mwt/credentials`).

```bash
# Sintaxis básica
mwt agent run review_triage --payload='{"review_id": "R12345"}'

# Desde archivo JSON
mwt agent run lead_qualifier --payload-file=lead_email.json

# Pipe desde stdin
cat email.json | mwt agent run lead_qualifier --payload=-

# Wait sync (bloquea hasta completion)
mwt agent run review_triage --payload='{...}' --wait

# Con prioridad
mwt agent run review_triage --payload='{...}' --priority=high

# Output formato
mwt agent run review_triage --payload='{...}' --output=json   # default
mwt agent run review_triage --payload='{...}' --output=table
mwt agent run review_triage --payload='{...}' --output=summary
```

Response (json):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "SKILL_RW_REVIEW_TRIAGE",
  "status": "queued",
  "expected_completion_by": "2026-04-29T18:30:00Z",
  "url": "https://portal.mwt.one/agents/tasks/550e8400-..."
}
```

### `mwt skill run`

Invoca un skill_package standalone. NO requiere agent envolviendo. Útil para casos puntuales (CEO necesita redactar un correo en su voz, sin pasar por un agent dedicado).

```bash
mwt skill run humanize_comms \
  --input="tengo que avisar a Pedro de Marluvas que llega tarde el container, fecha estimada 15 mayo"

# Con output target
mwt skill run humanize_comms \
  --input="..." \
  --voice-profile=marluvas_formal_es

# El default_prompt del skill_package se usa si no se especifica template
mwt skill run humanize_comms --input="..."
# → equivale a: ChatGPT-style invoke con default_prompt + input dado
```

### `mwt template fork`

Instancia un template (Fork mode). Pregunta placeholders interactivamente o los toma de `--vars`.

```bash
# Modo interactivo (preguntas guiadas)
mwt template fork TPL_REVIEW_TRIAGE --name=review_triage_v2

# Con vars no interactivo
mwt template fork TPL_REVIEW_TRIAGE \
  --name=review_triage_v2 \
  --var outcome.baseline_value=28 \
  --var outcome.target_at_60d="< 8"

# Dry run (no crea, solo valida)
mwt template fork TPL_REVIEW_TRIAGE --dry-run
```

### `mwt task approve` / `reject`

Aprobar o rechazar tasks que están en `awaiting_approval`. HITL granular por output cuando aplica.

```bash
# Aprobar task entera (todos los outputs)
mwt task approve <task_id>

# Aprobar output específico (cuando hay múltiples)
mwt task approve <task_id> --output=response_draft

# Aprobar con edit_light (modificación menor)
mwt task approve <task_id> \
  --output=response_draft \
  --edit-diff="cambio palabra X por Y"

# Rechazar con razón
mwt task reject <task_id> --reason="tono muy formal para este caso"
```

### `mwt builder new` (bootstrap interactivo)

Modo Bootstrap discusivo: CEO describe intención, builder genera plan, CEO edita, builder compila.

```bash
mwt builder new

# Preguntas guiadas:
# 1. ¿Qué querés que el agente haga? (descripción libre)
# 2. ¿De qué tipo? (Generator/Triage/Validator/...) — sugerido por intención
# 3. ¿Importa skills existentes? (humanize_comms, brand_voice, ...)
# 4. ¿Tools que necesita? (Gmail, SP-API, Drive, ...)
# 5. ¿Triggers? (manual, cron, webhook)
# 6. ¿Outcome metric primaria?
# 7. ¿Baseline pre-agente?
# 8. ¿Budget mensual?

# Builder muestra:
# Agent plan generated:
#   name: ...
#   architectural_archetype: triage
#   skills_imports: [humanize_comms]
#   tools_mcp: [gmail_send]
#   ...
#
# [Edit plan] [Start building] [Cancel]

# Tras Start building:
#   manifest YAML guardado en ~/.mwt/agents/<agent_id>.yaml
#   compilado con SCH_SKILL_MANIFEST_V2 v1.2
#   estado inicial: SHADOW
```

---

## Auth y permissions

```bash
# Setup inicial
mwt auth login                              # OAuth flow desde browser
mwt auth status                             # ver credenciales actuales
mwt auth logout

# Token en ~/.mwt/credentials (encrypted via OS keyring)
# Permissions definidas por role: ceo / curator / consumer
```

| Role | Puede |
|------|-------|
| **ceo** | todo: agent run/kill, skill refine, template fork, task approve, builder new, audit |
| **curator** | agent run, skill run, template fork (no kill ni refine sin firma CEO) |
| **consumer** | agent run + task approve (solo de tasks asignadas a ellos) |

En MWT v1: solo CEO existe. Roles emergen con FaberLoom multi-tenant.

---

## Output formats

### json (default)
Estructurado para scripting, JSON parseable.

### table
Render ASCII tabla legible para humanos.

### summary
Resumen narrativo de 3-5 líneas (útil para terminal scrollback).

### tail (en `mwt task show --tail`)
Sigue la ejecución en tiempo real (similar a `docker logs --follow` o `kubectl logs --follow`).

---

## Integración con scripts y CI

CLI diseñada para ser ejecutable desde:

- **Cron de tu máquina**: `0 8 * * 1 mwt agent run weekly_kpi_report --output=summary | mail`
- **GitHub Actions / GitLab CI**: cuando hay un push, invocar audit del KB
- **Otros agents**: un agent puede invocar a otro agent vía CLI subprocess (alternativa a sub_agents declarados, útil para cross-process)
- **Cowork sessions**: dentro de Cowork, `mwt` está disponible como bash command

---

## Diferencia con dashboard portal.mwt.one/agents/*

| Capability | CLI | Dashboard |
|------------|-----|-----------|
| Invocación rápida ad-hoc | ✓ ideal | ✓ pero más clicks |
| Scripting / automatización | ✓ ideal | no |
| Multi-step interactivo | limitado | ✓ ideal |
| Visualización flow DAG | no | ✓ ideal |
| Review tasks pendientes | listing OK | ✓ ideal con preview |
| Edit drafts antes de approve | menos cómodo | ✓ ideal |
| Audit cross-agente | OK | ✓ ideal con visualizaciones |

CLI y dashboard son **complementarios**, no excluyentes.

---

## Roadmap de implementación

| Fase | Comandos a entregar |
|------|---------------------|
| **Fase 0** (Foundation) | `mwt auth login/status` + `mwt agent list/show/run` + `mwt task show/approve/reject` |
| **Fase 1** (Manifest v2) | `mwt builder compile` + `mwt template list/show/fork` |
| **Fase 2** (Runtime) | `mwt skill run` + `mwt trigger list/test` |
| **Fase 2.6** (Tasks) | `mwt task queue/cancel` + tail mode |
| **Fase 3** (SHADOW) | `mwt agent shadow` + `mwt stats agent/cost/outcome` |
| **Fase 4** (Graduation) | `mwt agent graduate` + `mwt audit` |
| **Futuro** | `mwt builder new` interactivo + `mwt skill refine` (capa de aprendizaje) |

---

## Pre-requisitos

Esta CLI **no se construye en Fase 0** — los comandos básicos sí, pero la CLI completa emerge en Fases 1-4. Lo crítico Fase 0:

1. Endpoints REST funcionando (Django módulo `agents/tasks_api.py`)
2. Auth implementada
3. 3 comandos mínimos: `mwt agent run`, `mwt task show`, `mwt task approve`

Resto se agrega progresivo. La CLI es herramienta del CEO, no bloqueante de funcionalidad.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29c): creación con scope MWT-only erróneo y comando `mwt`. CLI surface completa con 6 grupos. Comandos clave detallados. Auth + roles definidos. Roadmap por fase.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SCH_CLI_INTERFACE → SCH_FB_CLI_INTERFACE. Comando canónico cambia de `mwt` → `fbl` (FaberLoom CLI). Multi-tenant aware desde día 1 vía `--tenant` o `FBL_TENANT`. En FB v1 beta default `--tenant=mwt`. Migración trivial vía alias bash `mwt = fbl --tenant=mwt`. Aprobador: CEO sesión re-scoping 2026-04-29f.**
