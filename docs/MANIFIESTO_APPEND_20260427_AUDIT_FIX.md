# MANIFIESTO_APPEND_20260427_AUDIT_FIX
id: MANIFIESTO_APPEND_20260427_AUDIT_FIX
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: VIGENTE — 2026-04-27
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)
aplica_a: [MWT]

---

## Contexto

Auditoría 4-alcance integral solicitada por CEO sobre la KB MWT (404 .md totales). Cubre:
1. Estructural / taxonomía
2. Integridad de dependencias
3. Visibilidad / CEO-ONLY
4. Pendientes y estado

Detectó drift acumulado post-v4.8.6 (+82 archivos sin sync con SSOTs) y 4 focos rojos. Sesión incluyó remediación mecánica antes de git sync — todos los cambios de contenido riesgoso (CEO-32 remediación, KB_AUDIT B2-B11) quedaron explícitamente diferidos a decisión CEO.

## Cambios ejecutados

### 1. Higiene de raíz — 22 ephemerals movidos

Origen → destino: `./*.md` → `docs/archivo/2026-04-faberloom-prep/`

| Patrón | Cantidad | Ejemplos |
|---|---|---|
| `AUDIT_*-local.md` | 6 | A-token-system, B1-B3-screens, C-i18n-a11y, D-pendientes |
| `PROMPT_*.md` | 14 | AUDITORIA (×4), CODE (×4), DESIGN (×3), LOGO, PARCHE, REINICIO |
| `COWORK_DELIVERY_*.md` | 1 | FABERLOOM_v3.5 |
| `UX_VISION_*.md` | 1 | FABERLOOM_2026-04-18 |

**Raíz post-cleanup:** 3 archivos canónicos — `CLAUDE.md` (entrada raíz), `README.md`, `COWORK_INSTRUCTIONS.md`.

### 2. faberloom-mockup/ → docs/archivo/

Carpeta entera (26 .md + assets: research/A1-A7, B0, B1; verification/AC_v2/v3/v3_5, trazabilidad_v2/v3, axe_report; raíz AC_V4, CHANGES_F1, DELIVERY_NOTES_v2/v3/v3.5/V4, GEMINI_PROMPT_PACK, HANDOFF_TO_COWORK, HANDOFF_V4, README) → `docs/archivo/faberloom-mockup/`.

Justificación: per RW_ROOT v4.8.4 esta carpeta estaba fuera del scope KB activo. Se mantiene como referencia histórica pre-build.

### 3. Headers fix mecánicos

| Cambio | Archivos | Detalle |
|---|---|---|
| +stamp | 10 IDX | Preservando `last_review` como fecha del stamp. Cumple meta-regla "stamp obligatorio para VIGENTE/ACTIVO/FROZEN" (RW_ROOT) |
| +stamp | 1 ENT | ENT_PLAT_SKILLS_CATALOG (`stamp: VIGENTE — 2026-04-16`) |
| +visibility | 1 SPEC | SPEC_AGENT_ARCHITECTURE_ALE (`visibility: [INTERNAL]` + stamp `PARA_REVISION — 2026-04-16`) |

Listado IDX con stamps post-fix:
- IDX_COMERCIAL → 2026-04-16
- IDX_COMPLIANCE → 2026-04-03
- IDX_DISTRIBUCION → 2026-03-14
- IDX_GOBERNANZA → 2026-04-22
- IDX_MARCA → 2026-04-16
- IDX_MARKETPLACE → 2026-04-16
- IDX_MERCADOS → 2026-03-18
- IDX_OPS → 2026-04-01
- IDX_PLATAFORMA → 2026-04-21
- IDX_PRODUCTO → 2026-04-03

### 4. SSOT counts sync

Post-cleanup:
- Total .md: **322 → 404** (drift de +82 corregido)
- docs/ activos: **254 → 285**
- docs/archivo/ total: **55 → 105** (57 raíz + 22 prep + 26 mockup)
- raíz repo: **25 → 3**

Archivos actualizados:
- `RW_ROOT.md` v4.8.6 → **v4.8.7** (changelog + counts + 4 huérfanos indexados + retira ref MANIFIESTO_CAMBIOS.md)
- `DASHBOARD_SNAPSHOT.md` v9.0 → **v10.0** (counts + headers fix + AUDIT 2026-04-27)
- `CLAUDE.md` (entrada raíz canónica + counts + KB_AUDIT status)
- `COWORK_INSTRUCTIONS.md` (counts)

### 5. Indexación de huérfanos

4 archivos existentes no indexados ahora visibles desde RW_ROOT §Registros Especiales:
- `SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md`
- `SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md`
- `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md`
- `FABERLOOM_MOCKUP_CHANGES_F1_v3.6.md`

### 6. CEO-32 update (no remediación)

`ENT_GOB_PENDIENTES` v13.0 → **v14.0**. CEO-32 actualizado de **10 → 14 leaks**:

Tier A (originales — PUBLIC + ceo_only_sections, 10 archivos):
- 9 PRODUCTO + 1 DISTRIBUCION (sin cambios)

Tier B (nuevos — INTERNAL + ceo_only_sections, 4 archivos):
- ENT_PLAT_CONTRATO_NODO [B]
- ENT_PLAT_LEGAL_ENTITY [C]
- ENT_PLAT_LLM_ROUTING [D]
- ENT_PROD_SCANNER_MERCADO [C, D]
- PLB_SCANNER_DISTRIB [H, I]

Mismo deadline (2026-05-30, **33 días**), mismas opciones (a) bumpear visibility / (b) extraer a archivo `*_CEO.md`. Scope ampliado a B10 PLATAFORMA.

**Decisión CEO pendiente.** No se remedió en esta sesión por respetar R5 (visibilidad sensible, opciones binarias).

### 7. MANIFIESTO_CAMBIOS.md retirado de SSOTs

Archivo no existía en disco; CLAUDE.md y RW_ROOT lo listaban como "FROZEN histórico". Se retiró la referencia en ambos. Trazabilidad pre-2026 ya consolidada como changelog textual en `MANIFIESTO_CAMBIOS_v2.md`. `CLAUDE.md` queda como entrada raíz canónica para todas las instancias (Code, Cowork, Project).

## NO ejecutado (riesgo o decisión CEO)

| Hallazgo | Acción correcta | Razón de diferir |
|---|---|---|
| 14 leaks CEO-32 remediación | Opción (a) o (b) por archivo | Decisión CEO — pierde consumo externo o agrega 14 archivos nuevos |
| KB_AUDIT B2-B11 (estancado 9 días) | Reanudar batches | Scope grande — sesión dedicada |
| 22 archivos sueltos (faberloom-prep) | Promover algunos a ENT_/SPEC_ canónicos (UX_VISION, AUDIT_*-local) | Decisión CEO — esos contenidos podrían ser canon |
| 64 broken refs (post-filtrado de gaps conocidos) | Crear SCHs faltantes (B1-B6) + corregir refs versionadas | Bloqueado por 21 OQ A7 + Q1-Q18 LLM Orchestration |
| Git history corrupto (`19ce5fb8` unreadable) | `git fsck --full` + posible re-clone | Operación riesgosa — requiere espacio de trabajo aislado |
| 7 ENT_EXP_* refs en ENT_PLAT_MODULOS | Update ENT_PLAT_MODULOS o crear ENT_EXP_* | Sin contexto de qué se consolidó dónde — requiere lectura de migración Sprint 6+ |
| 5 SPECs FaberLoom faltantes | Promover desde AUDIT_FABERLOOM o crear desde 0 | Bloqueado por Q1-Q12 |

## Verificación post-cambio

```
Total .md: 404 ✅
Raíz: 3 (CLAUDE+README+COWORK_INSTRUCTIONS) ✅
FROZEN md5 estable (ENT_OPS_STATE_MACHINE 77099773... + PLB_ORCHESTRATOR 30e4aa2c...) ✅
10 IDX con stamp ✅
1 SPEC con visibility ✅
DRIFT corregido en 4 SSOTs ✅
```

## Health KB post-fix

**Mantenido AMARILLO** (no degraded). Tres focos rojos pre-existentes siguen abiertos:
1. Pendientes CEO con vencimiento 2026-05-30 (33 días) — ahora 4 confirmados (CEO-25/26/27/32)
2. KB_AUDIT B2-B11 estancado desde 2026-04-18 (9 días)
3. 5 SPECs FaberLoom faltantes (B1-B6 brechas KB)

Mejoras incrementales:
- ✅ Higiene raíz: 25 → 3 archivos
- ✅ Headers: 11 archivos sin stamp/visibility → 0
- ✅ Drift counts: 322 declarado vs 404 real → ambos sincronizados a 404
- ✅ Huérfanos: 4 → 0

## Próxima acción CEO recomendada

1. **Git sync inmediato** — esta sesión deja todo en estado committable. Sugerencia commit: `[GOBERNANZA] AUDIT 4-alcance + higiene raíz — 322→404 sync, IDX +stamp, CEO-32 10→14, faberloom→archivo`
2. **CEO-32 decisión binaria** — opción (a) bumpear o (b) extraer. Para los 5 archivos PLATAFORMA (tier B) la opción (a) `INTERNAL → CEO-ONLY` puede ser más rápida si no hay consumo externo.
3. **Reanudar KB_AUDIT B3 PRODUCTO + B8 DISTRIBUCION** — bloquea el grueso de remediación CEO-32 tier A (10 leaks PUBLIC).

---

Trigger: CEO "puedes auditar este proyecto" → "ajustes para después sincronizar el git" (sesión 2026-04-27, Cowork mode).
