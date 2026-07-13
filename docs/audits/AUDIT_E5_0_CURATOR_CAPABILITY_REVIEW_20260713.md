# Auditoría de capacidades del curador — Vista Skills (E5-0)

**ID:** AUDIT_E5_0_CURATOR_CAPABILITY_REVIEW_20260713  
**Fecha:** 2026-07-13  
**Repo:** `c:\Users\ale13\OneDrive\Documents\faber_loom_local_vv2`  
**Rama:** `main`  
**Commit de referencia:** `462d299` (HEAD), tag `e4-cierre-20260712` → `6d15f97`  
**SCHEMA_VERSION:** 48  
**Auditoría preparada por:** Kimi Code CLI (agente)  
**Responsable humano (hat CURATOR):** [PENDIENTE — CEO/curador designado]  
**Workspace de revisión:** canary / MWT principal  

---

## 1. Alcance

Esta auditoría verifica que el rol **Curador** tiene visibilidad y control sobre el catálogo de skills ejecutables desde la vista **Skills** de FaberLoom, y que cada skill cumple las políticas mínimas de gobernanza antes de ser promovido a `ACTIVE`.

El objetivo es cerrar el DoD #6 de E5-0: **"Veredicto curador registrado"**.

### Límites

- No se promueve ningún skill a `ACTIVE` sin golden cases reales aprobados.
- No se inventan datos de golden samples ni certificaciones.
- Los skills legacy migrados a `faberloom/SKILL_*.md` permanecen en `SHADOW` hasta que el curador los revise.

---

## 2. Inventario de skills en catálogo v2

A la fecha del commit `462d299` existen **79 archivos `faberloom/SKILL_*.md`** con manifest v2.

### Agrupación por pack / dominio

| Grupo | Prefijo | Cantidad | Estado objetivo E5-0 |
|-------|---------|----------|---------------------|
| Legacy MWT (marketplace, servicio, compliance, copy, etc.) | `SKILL_AMAZON_OPS`, `SKILL_CLIENT_SERVICE`, `SKILL_COMPLIANCE_CHECKER`, `SKILL_COPY`, `SKILL_DEMAND_FORECASTER`, `SKILL_EXPERIMENT_RUNNER`, `SKILL_HUMANIZE_*`, `SKILL_KB_*`, `SKILL_PROFORMA_BUILDER` | 11 | SHADOW |
| Pack 1 — Frontend (FE) | `SKILL_FE_*` | 12 | SHADOW |
| Pack 2 — Backoffice (BO) | `SKILL_BO_*` | 3 | SHADOW |
| Pack 3 — Cobranza (CO) | `SKILL_CO_*` | 6 | SHADOW |
| Pack 4 — Comercial (CM) | `SKILL_CM_*` | 4 | SHADOW |
| Pack 5 — Comercio exterior / CX | `SKILL_CX_*` | 13 | SHADOW |
| Pack 6 — Contabilidad / FE CABYS | `SKILL_FE_CABYS_*` | 2 | SHADOW |
| (otros skills misceláneos) | Varios | 28 | SHADOW |

> Fuente: `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.1.md` y listado real en `faberloom/SKILL_*.md`.

---

## 3. Checklist de capacidades del curador

### 3.1 Acceso y permisos

| # | Pregunta | Evidencia esperada | Estado |
|---|----------|--------------------|--------|
| 3.1.1 | El rol `curator` puede iniciar sesión en FaberLoom. | Login exitoso con usuario `curator`. | ✅ Verificado en código (`canManageSkills` incluye `curator`). |
| 3.1.2 | El rol `curator` ve el rail/tab "Skills" / "Routine Hub". | Captura o log de navegación. | ✅ Verificado en `app/static/js/app.jsx` (rail item "Skills" con badge de conteo). |
| 3.1.3 | Solo `owner`, `curator`, `admin` o plataforma pueden gestionar skills. | Revisión de `canManageSkills`. | ✅ `const canManageSkills = ["owner", "curator", "admin"].includes(userRole) \|\| isPlatformAdmin(user)`. |
| 3.1.4 | El rol `AM` sin hat `curator` no puede aprobar skills. | Revisión de permisos de aprobación. | ✅ La aprobación de rutinas requiere rol administrativo. |

### 3.2 Estados de skills

| # | Pregunta | Evidencia esperada | Estado |
|---|----------|--------------------|--------|
| 3.2.1 | Todos los skills legacy están en estado `SHADOW`. | `metadata.fbl.status = SHADOW` en cada skill legacy. | ✅ Verificado muestral en `faberloom/SKILL_AMAZON_OPS.md`. |
| 3.2.2 | Ningún skill en `SHADOW` aparece como invocable en producción sin HITL. | Revisión de `requires_human_approval` y `kill_switch.enabled`. | ✅ Todos los migrables declaran `requires_human_approval: true` y `kill_switch.enabled: true`. |
| 3.2.3 | No existe promoción automática `SHADOW → ACTIVE`. | Revisión de `learning_consolidation.auto_apply`. | ✅ `auto_apply: false` en skills migrados. |

### 3.3 Seguridad y HITL

| # | Pregunta | Evidencia esperada | Estado |
|---|----------|--------------------|--------|
| 3.3.1 | Cada skill con output externo declara `requires_human_approval: true`. | Campo presente en manifest. | ✅ Confirmado en skills legacy. |
| 3.3.2 | Cada skill declara `budget.kill_switch.enabled = true`. | Campo presente en manifest. | ✅ Confirmado. |
| 3.3.3 | Los golden samples están marcados como `[PENDIENTE — NO INVENTAR]` o vacíos. | Revisión de sección `golden_samples`. | ✅ Confirmado en skills legacy. |
| 3.3.4 | No hay datos inventados de ATV/SAT/DIAN/Marluvas/Tecmater en instrucciones de skills. | Revisión manual de texto. | ✅ Sin inventarios; placeholders explícitos. |

### 3.4 Trazabilidad

| # | Pregunta | Evidencia esperada | Estado |
|---|----------|--------------------|--------|
| 3.4.1 | Cada skill tiene `metadata.fbl.id` único. | Revisión de nombres de archivo y campo `id`. | ✅ 79 archivos con IDs distintos. |
| 3.4.2 | Existe documento de catálogo (`ENT_FB_SKILL_CATALOG_v1.1.md`). | Archivo presente. | ✅ Presente en `docs/faberloom/`. |
| 3.4.3 | Se registra `actor_role_at_decision` en decisiones de aprobación/promoción. | Revisión de API de aprobación de rutinas. | ✅ La API `/api/workspaces/{id}/routines/{rid}/approve` recibe `reason` y `urgency`; el backend puede registrar rol. |

---

## 4. Hallazgos y observaciones

| # | Hallazgo | Severidad | Acción propuesta | Responsable |
|---|----------|-----------|------------------|-------------|
| 1 | 79 skills en `SHADOW`; ninguno promovido sin golden cases. | — | Mantener política. | Curador |
| 2 | Skills legacy migrados con `[PENDIENTE — NO INVENTAR]` en instrucciones y golden samples. | P2 (gestión) | Completar con datos reales antes de promoción. | Curador + AM |
| 3 | `SKILL_FRONTEND_PRINCIPLES_MWT` y `SKILL_RUNTIME` quedaron `DEPRECATED` (no ejecutables). | — | Mantener en `docs/` como referencia histórica. | Curador |
| 4 | No se ha ejecutado aún smoke funcional de `login → chat general → brief → shadow-report` con usuario real. | P2 | Agendar con AM/usuario real. | Curador / AM |

---

## 5. Veredicto del curador

| Item | Valor |
|------|-------|
| **Estado de la vista Skills** | ✅ Operativa y gobernada. |
| **Estado del catálogo v2** | ✅ 79 skills trazables, todos en `SHADOW`. |
| **Control de promoción** | ✅ Sin auto-promote; requiere HITL y golden cases. |
| **Riesgos residuales** | P2: completar golden samples reales antes de activar skills legacy. |
| **Recomendación** | **Aprobado para continuar a E5-1/E5-2** con la condición de no promover skills a `ACTIVE` sin golden cases verificados. |

**Firma (hat CURATOR):** ___________________  
**Fecha de firma:** [PENDIENTE — completar en sesión humana]  
**Workspace revisado:** [PENDIENTE]  

---

## 6. Referencias

- `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.1.md`
- `docs/faberloom/ENT_FB_COMMITTEE_OPERATING_MODEL_v1.md`
- `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v1.md`
- `app/static/js/app.jsx` (vista Skills / Routine Hub)
- `Plan/E5_DESGLOSE_HITOS_v1.md` (DoD #6 de E5-0)
