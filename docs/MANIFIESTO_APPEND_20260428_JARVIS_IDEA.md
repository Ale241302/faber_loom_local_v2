# MANIFIESTO_APPEND_20260428_JARVIS_IDEA
id: MANIFIESTO_APPEND_20260428_JARVIS_IDEA
type: TRANSITORIO
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-28
expires: post-cumplimiento gates G1-G4 (DEC-010) y reapertura CEO-36
aplica_a: [SHARED]

---

## Contexto

Sesión Cowork 2026-04-28 (tercera parte). CEO consultó factibilidad técnica de un "open Claude worker" per-user que actúe como orquestador conversacional persistente sobre los sub-agentes existentes — patrón "Jarvis" — ejecutando **rutinas re-evaluables** en lugar de flujos predefinidos.

Discusión iteró desde worker efímero (recomendación inicial) hacia orquestador persistente con memoria multi-capa. CEO solicitó dejar la idea registrada y evaluar impacto real antes de decidir.

**No hay decisión todavía.** Este append registra la idea + análisis para futura resolución.

## Cambios ejecutados

### 1. ENT_GOB_PENDIENTES.md v14.0 → v15.0

Agregado **CEO-36** — Jarvis Orchestrator (idea/evaluación arquitectura).

Resumen entrada:
- Patrón: agente conversacional persistente per-user, no efímero
- Cruza sub-agentes existentes (AG-01..AG-07 + SKILL_*) como tools
- Ejecuta rutinas re-evaluables sobre Action Engine, no flujos n8n estáticos
- Plan en 3 fases: F1 reactivo (4-6 sem) → F2 rutinas+memoria episódica (6-8 sem) → F3 proactivo+multi-tenant (3+ meses)
- Pre-req duro: Action Engine maduro (≥30 actions registradas)
- Decisión pendiente CEO: build F1 / defer / descartar

## Análisis de impacto (resumen ejecutivo)

### Mejora UX donde

| Vector | Magnitud | Probabilidad |
|---|---|---|
| Reducción carga mental orquestación CEO (3 unidades de negocio) | -50% a -60% (5-9h/sem) | alta |
| Capacidad de operar más unidades sin headcount | alto | alta |
| Tiempo "encontrar contexto" antes de decidir | <1 min vs 5-15 min | alta |
| Decisiones B2B más rápidas (Marluvas/Tecmater pipeline) | medio | media |
| Revenue directo Rana Walk/Marluvas/Tecmater | bajo o nulo | — |
| Jarvis como producto SaaS (vertical propio) | alto | especulativo |

### Costos

- **Construcción F1+F2:** 2-3 meses dedicados (o equivalente Ale)
- **Tokens Anthropic ongoing:** USD 200-800/mes (vos + 1-3 users internos)
- **Infra (Postgres + Redis + workers):** USD 50-150/mes
- **Mantenimiento:** 20-30% tiempo de un dev
- **Costo oculto:** refactor del Action Registry — inevitable

### Riesgos ranqueados

1. Memoria episódica mal calibrada (~30% prob primera versión peor que chat fresco)
2. Construcción 4 meses → solo uso personal (no escala a equipo/clientes)
3. Distracción del CEO en proyecto técnico vs operación
4. Vendor lock-in con Anthropic (manageable hoy, riesgo a 12+ meses)
5. Action Engine no madura suficiente (Jarvis con 50 actions vs 200 = 25% utilidad)

### ROI personal estimado

Hora valor CEO: USD 100-300 (rango razonable). Ahorro mensual: USD 2,400-9,000. Costo Jarvis funcionando: USD 200-600/mes. **ROI: 4x-15x.** Bueno si las hipótesis se cumplen.

### Veredicto

No es la mejor inversión de los próximos 4 meses **a menos que**:
- (a) Action Engine ya tenga ≥30 actions registradas, o
- (b) CEO sienta dolor real de orquestación que frene crecimiento

Si NO se cumple ninguna → mejor inversión: madurar Action Engine + automatizar flujos n8n concretos. Captura 60% del valor a 20% del costo.

Si SÍ se cumple alguna → Fase 1 reactiva en 4-6 semanas tiene buen ROI esperado.

## Datos pendientes para decisión final

1. Cantidad actual de actions en `ENT_PLAT_ACTION_REGISTRY` (verificar antes de decidir)
2. Cuán dolida siente CEO la orquestación mental hoy (señal subjetiva, vale)
3. Roadmap Letta (CEO-34) — Jarvis necesita memoria persistente; si Letta avanza, encaja como capa de memoria

## Encaja con

- `SPEC_ACTION_ENGINE` v1.2 — Jarvis solo invoca actions registradas, no inventa
- `SPEC_AUDIT_MODULE` — toda decisión de Jarvis va al audit log inmutable
- `ARCH_AGENT_PRINCIPLES` — orquestador respeta scope de cada sub-agente
- `ENT_PLAT_MEMORY_STACK` (CEO-34 Letta) — capa de memoria episódica + procedural
- `POL_DATA_CLASSIFICATION` v1.2 — enforcement runtime per-user

## Si decisión = BUILD

Crear:
- `SPEC_JARVIS_ORCHESTRATOR.md` (contract-first, status: VIGENTE post-aprobación)
- `SCH_ROUTINE_SPEC.yaml` (define rutina re-evaluable)
- `ENT_PLAT_JARVIS_RUNTIME.md` (specs runtime per-user)

Asignar a: AG-01 Architect (models), AG-02 API Builder (endpoints conversación), AG-06 QA (tests rutinas).

## Si decisión = DEFER

Mantener entrada CEO-36 abierta. Reevaluar cuando Action Registry cruce 30 actions y/o Letta esté operativo.

## Si decisión = DESCARTAR

Cerrar CEO-36 con razón documentada en `ENT_GOB_DECISIONES`. Mantener este MANIFIESTO como registro histórico.

---

**Origen conversacional:** sesión Cowork CEO 2026-04-28. Pregunta inicial: "qué tan difícil es hacer un open claw worker en servicio de un usuario dentro de la instancia de cada usuario que interactúe con los agentes". Iteración llevó a patrón Jarvis. CEO autorizó registro: `procede`.

---

## ANEXO v1.1 — Decisión arquitectónica (2026-04-28, mismo día)

CEO delegó autoridad arquitectónica con `eres el arquitecto`. Tras verificación de pre-reqs reales (no asumidos):

### Hallazgos en frío

| Pre-req | Estado real verificado |
|---|---|
| Action Registry ≥30 actions catalogadas | ✅ 53 actions (ENT_PLAT_ACTION_REGISTRY v1.1) |
| Action Engine **runtime ejecutable** | ❌ solo contrato v1.2 VIGENTE; runtime passthrough programado sem 3+ |
| Memoria persistente per-user | ❌ Letta DRAFT, CEO-34 piloto sin decisión |
| FaberLoom MVP fuera de path crítico | ❌ MVP en sem 3-9 consume mismo Engine |

### Decisión: DEFER con gates cuantitativos (DEC-010)

**No descarta. No construye. Difiere con criterio objetivo.** Gates de reapertura:

- **G1** Action Engine runtime passthrough en producción + ≥3 skills MWT migradas
- **G2** Memoria persistente operativa (Letta o equivalente VIGENTE)
- **G3** FaberLoom MVP en sem 6+ (fuera de path crítico Engine)
- **G4** OutcomeLedger ≥1000 decisiones loggeadas

Calendario realista para reabrir CEO-36: **8-12 semanas desde 2026-04-28**.

### Por qué no construir ahora (el argumento técnico de fondo)

Construir Jarvis sobre el contrato v1.2 sin runtime activo significa que cada sub-agente seguiría llamando APIs hardcoded — exactamente lo que el Action Engine vino a eliminar. Jarvis F1 pasaría a coordinar integraciones custom en lugar de actions registradas, y todo el trabajo se descartaría cuando el Engine pase a passthrough en sem 3+.

**Es construir sobre arena.** Viola P14 (Deterministic First — preferir lo determinístico maduro antes que sumar capa nueva) y P3 (Draft First — la base debe estabilizarse antes que la capa de orquestación).

### Acción intermedia obligatoria — CEO-37

Antes de cualquier build de Jarvis (incluso post-gates), ejecutar **captura formal de rutinas mentales CEO** en sesión Cowork de 90-120 min. Output: `ENT_GOB_RUTINAS_CEO.md` (CEO-ONLY).

Justificación:
- **(a)** valida hipótesis "5-9h/sem orquestación mental" con datos reales — sin esto, todo el ROI estimado es especulativo
- **(b)** genera el corpus que Jarvis F1 necesitará para razonar — sin rutinas estructuradas, F1 arranca sin entrenamiento
- **(c)** detecta cuáles rutinas pueden automatizarse YA con n8n + Engine passthrough sem 3 — captura **30-40% del valor de Jarvis por 2% del costo**
- **(d)** clasifica las rutinas en re-evaluables (Jarvis-fit) vs deterministas (n8n-fit) — clarifica qué construir y qué no

Costo: 2-3h CEO + 1h arquitecto.

VENCE: 2026-05-15 (3 semanas).

### Si en 12 semanas los gates no se cumplen

No es señal de descartar Jarvis — es señal de revisar prioridades del roadmap. Acción correctiva: revisar SPEC_ACTION_ENGINE roadmap + estado Letta CEO-34 + carga FaberLoom. Posibles caminos: (a) acelerar Engine contratando dev dedicado, (b) descartar Letta y elegir alternativa más rápida, (c) reescalonar Jarvis a 2027.

### Reversibilidad

DEC-010 es **two-way door**. Si surgen datos nuevos (ej. CEO-37 muestra dolor mucho mayor al estimado, o Engine runtime acelera, o aparece un cliente B2B dispuesto a pagar por Jarvis as-a-service), los gates se ajustan. La decisión NO mata Jarvis — protege la secuencia arquitectónica.

### Trazabilidad

- Decisión formal: `ENT_GOB_DECISIONES` DEC-010 v2.1
- Pendiente operativo: `ENT_GOB_PENDIENTES` CEO-36 status DEFERRED + CEO-37 nueva (v16.0)
- Este MANIFIESTO bumpea a v1.1 con anexo

CEO autorizó indexación con `indexa`.
