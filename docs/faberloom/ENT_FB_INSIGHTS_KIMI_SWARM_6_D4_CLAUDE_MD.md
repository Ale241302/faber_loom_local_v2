# ENT_FB_INSIGHTS_KIMI_SWARM_6_D4_CLAUDE_MD -- CLAUDE.md patterns emergentes 2026

---
id: ENT_FB_INSIGHTS_KIMI_SWARM_6_D4_CLAUDE_MD
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Kimi K2.6 multi-agente D4 (research) + Cowork (sintesis indexada) + CEO (decisiones)
aplica_a: [FaberLoom, MWT]
relacionado_con:
  - CLAUDE.md (raiz repo, pendiente bumpear v2)
  - WIKI.md (PENDIENTE crear, contract humano dual-surface)
  - hooks/ (PENDIENTE crear: sessionstart.py, pretooluse_canonical_protect.py, userpromptsubmit_reminder.py)
  - SKILL_KB_GATEWAY_v1 (PENDIENTE crear)
  - ARCH_AGENT_PRINCIPLES.md (P0-P14, P16 ya canonicos)
  - ROADMAP_INTEGRAL_KB_4_CAPAS.md (capa 1 cross-cutting)
origen: |
  Kimi Swarm #6 D4 ejecutado 2026-05-07. 16+ casos production citados.
  Research bruto: docs/anexos/kimi_swarm_6/research/mwt_swarm6_d4.md (875 lineas).
  Disparado por incidente Cowork 29-abr (11 archivos FB metidos en docs/
  raiz pese a indicaciones explicitas). Hipotesis: CLAUDE.md actual tiene
  reglas pero no fuerza "think before coding / surgical changes" tipo
  Karpathy. Hipotesis confirmada y profundizada por swarm.
---

## 1. Decision principal

**Implementar dual-surface CLAUDE.md + WIKI.md + hooks layer + anti-rationalization tables.**

CLAUDE.md SOLO no es suficiente. Anthropic envuelve CLAUDE.md con clausula dismissiva ("ignorar si no es altamente relevante") segun research swarm. Las reglas criticas deben ir en **hooks (PreToolUse / SessionStart)**, no solo en CLAUDE.md.

Este es el cambio con mayor palanca para todo lo siguiente. Sin enforcement layer, todo lo que ejecute Cowork puede repetir incidentes como el del 29-abr.

## 2. Hallazgos clave

### 2.1 CLAUDE.md NO es archivo configuracion, es contexto

Anthropic le aplica clausula descargo de responsabilidad que permite al modelo ignorarlo si decide que no es "altamente relevante". Esto **rompe expectativas** sobre uso CLAUDE.md como enforcement.

**Las reglas criticas deben vivir en hooks**, no solo CLAUDE.md.

### 2.2 Limite duro CLAUDE.md: ~150-200 instrucciones totales

Incluye system prompt Claude Code que ya consume ~50.

**Mas alla de eso, cumplimiento decae uniformemente.**

Casos production:
- **HumanLayer:** mantiene CLAUDE.md productivo bajo **60 lineas**
- **Boris Cherny** (creador Claude Code): mantiene su CLAUDE.md en **~60-83 lineas**

### 2.3 Hooks son la capa de enforcement real

Hook output llega como `system-reminder` **sin el framing dismissivo** de CLAUDE.md.

Casos production:
- Plugin con hooks `SessionStart` + `UserPromptSubmit` que re-inyecta valores tras cada compactacion logro cumplimiento donde CLAUDE.md solo fallaba

**Hooks tipos disponibles Claude Code:**
- `SessionStart` (re-inyecta reglas tras compactacion)
- `UserPromptSubmit` (anade ~15 tokens reminder cada prompt)
- `PreToolUse` (bloquea acciones antes de ejecutar)
- `PostToolUse` (audit despues)
- `Stop` (driftcheck al finalizar)

### 2.4 Anti-rationalization tables (Addy Osmani / Anthropic)

Codifico **20 skills con "anti-rationalization tables"**. Cada skill incluye tabla de excusas comunes que agentes usan para saltarse pasos ("agregare tests despues") con contra-argumentos documentados.

Es el patron mas robusto documentado para evitar que agente se hable a si mismo de saltar reglas.

Ejemplo:

| Excusa comun | Contra-argumento |
|---|---|
| "Es solo un cambio rapido, no necesita tests" | Cambio rapido + sin tests = deuda silenciosa que regresa en 3 sprints |
| "Voy a refactorear esto mientras estoy aqui" | Surgical changes - no improving. Cada cambio debe trazar a request explicito |
| "El usuario probablemente quiso decir X" | Si hay ambiguedad, parar y preguntar. No silenciosamente elegir |
| "Esta funcion ya existe pero la voy a re-escribir" | NO improving adjacent code. Match existing style |
| "Los tests pasan, podemos commitear" | Tests pasan != funcionalidad correcta. Verify behavior, not test |

### 2.5 Patron dual-surface CLAUDE.md + WIKI.md

Caso badwally/TheKnowledge: setup mas cercano a MWT con sync canonico.

Estructura:
```
~/code/knowledge/
├── CLAUDE.md              # Agent control surface (<60 lineas)
├── WIKI.md                # Conventions reference (contract humano detallado)
├── raw/                   # Immutable ingested sources
├── wiki/                  # LLM-authored knowledge (6 page types)
├── .knowledge/
│   ├── policies/          # Editorial policies per domain
│   ├── locks/             # File locks for concurrency
│   └── lint/              # Lint reports
├── src/gateway/           # Gateway implementation
│   ├── core.py            # Gateway.execute(operation, args)
│   ├── validator.py       # WIKI.md rules as composable functions
│   ├── locking.py         # File locks
│   └── ops/               # One module per gateway operation
```

**Control surface dual:**
- `CLAUDE.md` = que puede hacer agente, como debe comportarse
- `WIKI.md` = contract tecnico que valida gateway. Cada componente (gateway, validator, converters) codifica contra WIKI.md
- Gateway implementa contract: validate input -> lock -> execute -> validate output -> write atomically -> update backlinks -> log -> release lock -> return

### 2.6 Patron Karpathy edit-time + Reneza runtime

**Karpathy 4 reglas (edit-time):**
1. Think Before Coding -- state assumptions, surface tradeoffs, ask when unclear
2. Simplicity First -- minimum code, no speculative abstractions
3. Surgical Changes -- touch only what task requires; every changed line traces to request
4. Goal-Driven Execution -- define success criteria, loop until verified

**Reneza extension 6 reglas runtime:**
5. State Inspection Before Action -- check current state before acting
6. Idempotency Always -- assume retry, design accordingly
7. Fail Loudly -- error messages should diagnose, not just report
8. Observable By Default -- log decisions, not just outcomes
9. Boundary Checks -- validate inputs at every boundary
10. Reversibility When Possible -- prefer reversible actions

## 3. Casos production citados

| Empresa | Caso | Metrica reportada |
|---|---|---|
| **HumanLayer** | CLAUDE.md productivo | Bajo 60 lineas |
| **Boris Cherny** (Claude Code creator) | CLAUDE.md propio | 60-83 lineas |
| **Addy Osmani** (Google/Anthropic) | 20 skills con anti-rationalization tables | Patron mas robusto documentado |
| **badwally/TheKnowledge** | Dual-surface CLAUDE.md + WIKI.md + gateway | Caso mas cercano a MWT con sync canonico |
| **Atlassian** | AI code review | -45% PR cycle time |
| **1mg** (300 ingenieros) | Claude Code adoption | -31.8% review time |
| **Altana** | Claude Code production | 2-10x velocidad desarrollo |
| **Behavox** | Claude Code "pair programmer" | Cientos de devs deployed |
| **CWAN Engineering** | CLAUDE.md research repo (4 tiers) | Source of Truth, Core Knowledge, Implementation, Historical |
| **LowCode Agency** | Multi-tenant SaaS CLAUDE.md | tenant_id propagation rules |
| **GoClaw** | Multi-tenant Go agents | Context.Context tenant flow |
| **Anthropic** (Karpathy) | forrestchang/andrej-karpathy-skills | 97.8K stars |
| **Mehul Gupta** (Medium) | CLAUDE.md for programmers | 4 reglas Karpathy adaptadas |
| **Reneza** | 6 reglas runtime extendidas | Article extending Karpathy |
| **Anthropic Claude Code Docs** | Best practices oficiales | -- |
| **Forrestchang** | Skills repo open source | Patron skills + plugins |

## 4. Recomendacion directa

### Lo que SI implementar (Sprint 0)

1. **Dual-surface CLAUDE.md + WIKI.md.** Patron badwally/TheKnowledge. CLAUDE.md <60 lineas (control surface). WIKI.md detallado (contract humano/tecnico).

2. **Hook PreToolUse `pretooluse_canonical_protect.py`:** verifica si path objetivo esta en `C:\dev\mwt-knowledge-hub` y bloquea Write/Edit si Cowork intenta escribir directo. Previene incidente 29-abr.

3. **Hook SessionStart `sessionstart.py`:** re-inyecta 6 reglas inquebrantables MWT tras cada compactacion.

4. **Hook UserPromptSubmit `userpromptsubmit_reminder.py`:** anade ~15 tokens reminder cada prompt sobre reglas criticas activas.

5. **Anti-rationalization table** en CLAUDE.md v2 (seccion al final, ~10 excusas comunes con contra-argumentos).

6. **Karpathy 4 reglas + 6 runtime** adaptadas al contexto KB MWT. Total <60 lineas.

### Lo que NO implementar (ahora)

1. NO **MCP gateway para KB ops.** Diferir hasta equipo crece >3 devs.

2. NO **migrar todas reglas existentes a hooks.** Solo las criticas (sync canonico, taxonomia, draft-first).

3. NO **CLAUDE.md monolitico >100 lineas.** Limite duro 60 lineas.

4. NO **multiples archivos hooks por regla.** Combinar en 3-4 archivos por trigger (sessionstart, pretooluse, userpromptsubmit).

### Lo que diferir (post-MVP)

1. **MCP gateway** cuando equipo crece
2. **Skill `SKILL_KB_GATEWAY_v1`** con gateway pattern (validate -> lock -> execute -> log) si lazy migration genera conflictos
3. **Driftcheck hook Stop** para auditoria automatica al final cada sesion
4. **Token cost tracking** detallado por skill/agent

## 5. Estructura propuesta CLAUDE.md v2 (esqueleto)

```markdown
# CLAUDE.md -- MWT Knowledge Hub

## Identity
You are the KB curator assistant for Muito Work Limitada.
Your job: organize, validate, synthesize knowledge.
NEVER write production code from this repo.

## Canonical Source of Truth
- Git repo at C:\dev\mwt-knowledge-hub is the ONLY canonical source
- OneDrive mirror is read/write for Cowork sessions
- ALL changes flow through sync_*_indexa.ps1 back to canonical
- NEVER write directly to canonical from Cowork

## Taxonomy (8 tipos canonicos + especiales)
- ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE + SPEC/ARCH/AUDIT
- Every file MUST have correct frontmatter type. Ask if unclear.

## Rules (think before coding)
1. DRAFT-FIRST invariante: All new content starts as draft: true
2. Curaduria 2 capas: USER review + COMMITTEE approval
3. NEVER create/move/delete files in canonical repo directly
4. NEVER modify files outside current working directory scope
5. If Cowork suggests changes to canonical files, STOP and ask
6. All claims must cite source with [[file:line]] format
7. Sealed/Open dual mode: Sealed = read-only; Open = working drafts

## Karpathy Edit-Time Rules
1. Think before acting -- state assumptions, ask if unclear
2. Simplicity first -- minimum to solve. No speculative.
3. Surgical changes -- every change traces to user request
4. Goal-driven -- define success criteria, loop until verified

## Anti-Rationalization Table
| Excusa | Contra-argumento |
|---|---|
| "Es cambio rapido sin tests" | Cambio sin tests = deuda silenciosa |
| "Refactoreo mientras estoy aqui" | Surgical changes only |
| "Usuario probablemente quiso X" | Si ambiguo, parar y preguntar |
| "Reescribir mejor" | NO improving adjacent code |
| "Tests pasan, commit" | Verify behavior not just tests |

## Multi-Tenant Rules (NEVER BREAK)
- Every query MUST include tenant_id filter
- Every isolatable table has tenant_id NOT NULL
- Tenant flows through context, NEVER from headers
- RLS policies are source of truth
- Per-tenant overrides: LLM configs, tools, skills enabled

## See WIKI.md for full conventions and gateway contract.
```

Total estimado: **~55 lineas** dentro del limite <60.

## 6. Estructura propuesta WIKI.md (esqueleto)

```markdown
# WIKI.md -- MWT Knowledge Hub Contract

## Conventions

### Naming
- Files: PREFIX_DOMAIN_TOPIC[_VERSION].md
- Folders: docs/, docs/faberloom/, docs/anexos/
- Hooks: hooks/<trigger>_<purpose>.py

### Frontmatter Schema (obligatorio)
- id, version, status, visibility, domain, type, stamp, aplica_a
- Si type == ENT: relacionado_con, origen
- Si type == POL: aprobador
- Si chunk_strategy != none: chunk_*, queries_answered

## Sync Protocol
1. Cowork escribe en OneDrive mirror
2. sync_<tema>_indexa.ps1 mueve a canonico
3. mirror_to_onedrive.ps1 restaura mirror
4. Validacion: hash content-based, idempotency

## Gateway Contract (writes al canonico)
1. validate input
2. acquire lock (.knowledge/locks/)
3. execute operation
4. validate output
5. write atomically
6. update backlinks
7. log a log.md (append-only)
8. release lock
9. return

## File Lifecycle
- Status: draft -> review -> active -> superseded -> archived
- Promotion requires curaduria 2 capas (USER + COMMITTEE)

## Anti-Patterns Documented
- AI cleanup behavior (touching unrelated code)
- Confident guessing (proceed with assumption sin verificar)
- Over-engineering (abstracciones speculativas)
- Cargo-cult patterns (copy from other repos sin entender)

## Reference Links
- ARCH_AGENT_PRINCIPLES.md (14 principios)
- POL_TAXONOMIA_v1 (cuando exista)
- POL_CHUNKING_KB_v1 (cuando exista)
```

Total estimado: **~150-200 lineas** (puede crecer, no tiene limite duro).

## 7. Hooks propuestos

### `hooks/sessionstart.py`

```python
"""
Re-inyecta 6 reglas inquebrantables tras cada compactacion.
Output llega como system-reminder sin framing dismissivo.
"""
RULES = [
    "1. NEVER write directly to canonical repo (C:\\dev\\mwt-knowledge-hub)",
    "2. ALL changes flow through sync_*_indexa.ps1",
    "3. Every file MUST have correct frontmatter type",
    "4. DRAFT-FIRST: new content starts as draft",
    "5. NEVER touch FROZEN files (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR)",
    "6. Anti-rationalization: surgical changes only",
]

def hook(context):
    return {"system_reminder": "\n".join(RULES)}
```

### `hooks/pretooluse_canonical_protect.py`

```python
"""
Bloquea Write/Edit a paths del repo canonico.
Previene incidente 29-abr (11 archivos FB en docs/ raiz).
"""
CANONICAL_PATH = r"C:\dev\mwt-knowledge-hub"

def hook(context):
    if context.tool_name in ["Write", "Edit"]:
        path = context.args.get("file_path", "")
        if CANONICAL_PATH in path:
            return {
                "blocked": True,
                "reason": f"Cannot write to canonical repo: {path}. "
                          f"Use OneDrive mirror + sync_*_indexa.ps1"
            }
    return {"blocked": False}
```

### `hooks/userpromptsubmit_reminder.py`

```python
"""
Anade ~15 tokens reminder cada prompt sobre reglas criticas activas.
"""
REMINDER = "[Active rules: draft-first | sync canonical | surgical changes]"

def hook(context):
    return {"prefix": REMINDER}
```

## 8. Plan implementacion (Sprint 0)

| Tarea | Esfuerzo | Dependencia |
|---|---|---|
| Bumpear CLAUDE.md a v2 | 1h | Ninguna |
| Crear WIKI.md desde scratch | 2h | CLAUDE.md v2 |
| Crear 3 hooks Python | 2h | Documentacion Claude Code hooks |
| Test integracion hooks | 1h | Hooks creados |
| MANIFIESTO_APPEND documentando cambios | 0.5h | Todo lo anterior |

**Total: 6.5h. Encaja en 1 sesion Cowork.**

## 9. Decisiones que cierran

- Dual-surface CLAUDE.md + WIKI.md (no monolitico)
- CLAUDE.md <60 lineas estricto
- Hooks como enforcement real, no solo CLAUDE.md
- Anti-rationalization table obligatoria
- Karpathy 4 + Reneza 6 reglas runtime
- PreToolUse hook bloquea writes al canonico
- SessionStart hook re-inyecta reglas tras compactacion

## 10. Sources

Research bruto completo en: `docs/anexos/kimi_swarm_6/research/mwt_swarm6_d4.md` (875 lineas).

16+ casos production citados, 80+ referencias web verificadas.

---

**Fin del documento.**
