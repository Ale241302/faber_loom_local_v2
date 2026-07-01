# MANIFIESTO_APPEND_20260420_AUDIT_FABERLOOM_REFRESH
fecha: 2026-04-20
autor: Claude (Cowork)
tipo: REFRESH + INDEXACION
trigger: CEO — path al mockup v3.5 post-handoff de Claude Code (`MWT KB/faberloom-mockup/` con A7 actualizado C1-C17 + 21 OQ, verification/AC_v3_5.md, HANDOFF_TO_COWORK.md)
aplica_a: [FaberLoom]

---

## Resumen

Refresh de la serie `AUDIT_FABERLOOM_` para sincronizarla con el mockup v3.5 (461 KB · 7935 líneas · 27 fragments), posterior a la indexación inicial del 2026-04-20 AM que se había hecho contra v3. Tres acciones:

1. **Bump `AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1` a v1.1** — +C17 (agent lifecycle UX) + 4 OQ nuevas (18-21 C17-specific).
2. **Nuevo `AUDIT_FABERLOOM_AC_V3_5_v1`** — verification acceptance criteria mockup v3.5 (28/28 PASS · cumulative 94 PASS).
3. **Nuevo `PLB_FABERLOOM_KB_PROMOTION_v1`** — handoff Claude Code → Cowork como playbook operativo (roadmap D1-D10 + U1-U8 + O1-O3 + 6 brechas KB + 21 OQ P0-P3 con target file por decisión).

## Contexto

La indexación del AM 2026-04-20 se hizo sobre la versión de la serie research/ que existía en ese momento (mockup v3 · A7 con C1-C16 · 17 OQ). Durante el mismo día Claude Code produjo mockup v3.5 (gap B1 #5 cerrado · C17 agent lifecycle completo · 28 AC nuevos) + HANDOFF_TO_COWORK.md como documento de traspaso. El CEO dio la ruta al mockup como señal de procesar el refresh completo. Se valida verbatim del source actualizado, no se reinventa.

## Diff vs AM 2026-04-20

| Documento | v1.0 indexada AM | v3.5 source PM | Acción |
|-----------|------------------|----------------|--------|
| A1 SPEC canon | 172 líneas · 12630 B | idéntico | sin cambios |
| A2 code inventory | 176 líneas · 9629 B | idéntico | sin cambios |
| A3 dark palette | 208 líneas · 11541 B | idéntico | sin cambios |
| A4 ARCH principles | 156 líneas · 8389 B | idéntico | sin cambios |
| A5 knowledge flow | 239 líneas · 10113 B | idéntico | sin cambios |
| A6 reconciliation | 175 líneas · 8159 B | idéntico | sin cambios |
| **A7 contradictions** | **C1-C16 · 17 OQ · 20786 B** | **C1-C17 · 21 OQ · 24146 B** | **REFRESH v1.1** |
| B0 methodology | 258 líneas · 13360 B | idéntico | sin cambios |
| B1 service blueprint | 703 líneas · 27395 B | idéntico | sin cambios |
| AC_v3_5 | — | 65 líneas · 5352 B | **NUEVO** `AUDIT_FABERLOOM_AC_V3_5_v1.md` |
| HANDOFF_TO_COWORK | — | 290 líneas · 23498 B | **NUEVO** `PLB_FABERLOOM_KB_PROMOTION_v1.md` |

## Archivos creados

| Archivo | Bytes | Función |
|---------|-------|---------|
| `AUDIT_FABERLOOM_AC_V3_5_v1.md` | 6053 | Acceptance criteria mockup v3.5 (agent lifecycle). 28/28 PASS. Cumulative v2+v3+v3.5 = 94 PASS · 1 RB · 0 FAIL. Evidencia de cierre B1 gap #5 + C17 |
| `PLB_FABERLOOM_KB_PROMOTION_v1.md` | 23972 | Playbook operativo: roadmap D1-D10 (promoción directa a canon con target file), U1-U8 (edits a docs existentes), O1-O3 (referencias operacionales), 6 brechas KB (schemas/policies/entities faltantes), 21 OQ P0-P3. Mapea cada decisión/contradicción de la serie AUDIT_ hacia su target en la KB canónica |

## Archivos modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1.md` | BUMP v1.0→v1.1 | Contenido verbatim del A7 source actualizado post-v3.5. Header title `16 conflicts` → `17 conflicts C1-C17 + 21 OQ`. Nueva `C17 · Agent lifecycle UX` (46 líneas origen). OQs expandidas de 17 a 21 (+ 4 OQ C17-specific: autonomy ceiling gate, diff visual, sandbox test, auto-rollback). Changelog extendido v1.0+v1.1 |
| `RW_ROOT.md` | EDIT v4.8.2→v4.8.3 | Registros especiales: `9 archivos`→`10 archivos` + PLB_FABERLOOM_KB_PROMOTION entrada dedicada. Changelog v4.8.3 con resumen refresh |
| `IDX_GOBERNANZA.md` | EDIT health + tablas | Health: `10 PLBs`→`11 PLBs`, `9 AUDIT`→`10 AUDIT`. Última revisión: REFRESH. PLB_FABERLOOM_KB_PROMOTION añadido a tabla Playbooks. A7 entry actualizado a v1.1 (17 C + 21 OQ). +AUDIT_FABERLOOM_AC_V3_5 en tabla Serie A |
| `ENT_GOB_PENDIENTES.md` | EDIT +4 OQ + 6 brechas | Sub-sección FABERLOOM: OQ 17→21 (+ 4 C17-specific priorizadas P0 C17#18, P1 C17#20, P2 C17#19/21). Nueva sub-sección "Brechas KB detectadas en handoff" con B1-B6 (SCH_CONNECTOR_ACCOUNT, SCH_AGENT_EVENTS, SCH_DRAFT_STATE_MACHINE, SCH_OVERLAY_POLICY, POL_NOTIFICATION_ROUTING, ENT_PERSONAS_OPERATIVAS) |

## Open questions C17 nuevas escaladas a ENT_GOB_PENDIENTES

| # | OQ | Prioridad | Justificación |
|---|----|-----------|---------------|
| 18 | Approval gate diferenciado para `autonomyCeiling` raise vs otros AgentSpec edits | **P0** | Bloqueante: promover autonomía es cambio de riesgo operativo que requiere CEO gate explícito. v3.5 lo deja sin diferenciar |
| 19 | Diff visual entre 2 versiones del AgentSpec (changeNote textual no alcanza) | P2 | Polish — v3.5 muestra changeNote textual; diff campo-por-campo de los 7 AgentSpec fields sería v4 |
| 20 | Sandbox test del AgentSpec antes de publish | P1 | Skill Studio ya tiene sandbox skill-level; agent-level análogo pendiente. Necesario para L4 auto-exec |
| 21 | Auto-rollback on quality regression post-publish (P13 probation logic) | P2 | P13 implica probation pero el mockup no surfacea el loop — diferido a iteración post-partners |

## Brechas KB detectadas en handoff §7 (escaladas como B1-B6 en ENT_GOB_PENDIENTES)

1. `SCH_CONNECTOR_ACCOUNT.md` — SPEC menciona tabla S3 pero no enumera kinds
2. `SCH_AGENT_EVENTS.md` — wizard v3.5 tiene 11 events hardcoded sin catálogo canon
3. `SCH_DRAFT_STATE_MACHINE.md` — A4 P7 es ASCII, falta schema formal exportable
4. `SCH_OVERLAY_POLICY.md` — **P0** central para skill 3-layer (manual + learned + sealed)
5. `POL_NOTIFICATION_ROUTING.md` — qué eventos LIVE broadcast a bandeja vs solo log
6. `ENT_PERSONAS_OPERATIVAS.md` — Bruno/Ana/Álvaro con JTBD canon

## Decisiones de indexación tomadas

1. **Handoff como PLB, no AUDIT.** Los AUDIT son análisis forense del pasado (qué decidió el mockup, qué contradicciones surfacea). El handoff es prescriptivo (qué hacer con eso). Taxonomía correcta: Playbook.

2. **AC_v3_5 como AUDIT, no dentro del mockup.** Evidencia externa de que la serie AUDIT_A7 (C17) tiene implementación verificada. Consistente con serie AUDIT_ como registros especiales.

3. **Refresh del A7 con bump v1.1, no nuevo archivo.** Mismo ID canónico, mismo contenido verbatim del source; solo creció. Alternativa considerada: A7_v2. Descartada porque no hay reescritura — es extensión.

4. **Las 6 brechas KB como sub-sección nueva en ENT_GOB_PENDIENTES.** No son open questions (no requieren decisión CEO), son trabajo de creación de schemas. Tracking separado.

5. **U1-U8 (edits a docs existentes) NO escalados como pendientes independientes.** Ya están listados en el PLB indexado. Si se quieren seguir como tickets, se puede extraer en iteración futura. Evita duplicación.

6. **DEPENDENCY_GRAPH no actualizado.** AUDIT y PLB son referencia/meta, no se consumen en cadenas de ensamblaje de schemas.

## Ámbito del gate

```
GATE ✅ REFRESH (señal CEO: path al mockup post-handoff)
✔ Determinismo     — 2 archivos nuevos + 1 bump version + 4 docs editados. Ninguno duplica contenido
✔ Tipo             — AUDIT + PLB (ambos precedente documentado en RW_ROOT §Registros Especiales)
✔ Stamp            — DRAFT todos
✔ Version          — A7 1.0→1.1, AC_V3_5 v1.0 · PLB v1.0, RW_ROOT v4.8.2→v4.8.3
✔ Impacto cruzado  — ENT_GOB_PENDIENTES +4 OQ +6 brechas · IDX_GOBERNANZA health +1 PLB +1 AUDIT · NO toca FROZEN
✔ Pendientes       — 21 OQ + 6 brechas visibles en ENT_GOB_PENDIENTES
✔ Sin inventados   — A7 verbatim del source actualizado · AC_V3_5 verbatim · PLB verbatim del HANDOFF_TO_COWORK.md. Solo headers MWT + changelog añadidos
✔ IDX              — IDX_GOBERNANZA health + tablas Serie A (v1.1 + AC_V3_5) + Playbooks (+PLB_FABERLOOM_KB_PROMOTION)
✔ Seguridad        — [INTERNAL] todos. No CEO_ONLY leak. Sin datos sensibles
```

## Refs activos

- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` v1.0 DRAFT (target de promoción D1-D10 + U1-U8)
- `ARCH_AGENT_PRINCIPLES` v1.2 VIGENTE (target edits U1-U4)
- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA` v1.0 DRAFT (target edits U6-U7)
- `ENT_GOB_PENDIENTES` v12.0+ (track FABERLOOM: 21 OQ + 6 brechas)
- `faberloom-mockup/` v3.5 461 KB (fuente de verdad del estado actual)
- `MANIFIESTO_APPEND_20260420_AUDIT_FABERLOOM.md` (manifiesto padre — indexación inicial AM)

## Lo que el CEO tiene que decidir ahora

1. **4 P0 bloqueantes** siguen abiertos + **1 P0 nuevo** (OQ#18 — autonomy ceiling raise approval gate). Total 5 P0. Orden sugerido para resolver:
   - C1 feedback taxonomy (más corto — decisión de mapping 5↔6 codes)
   - OQ#18 autonomy ceiling gate (impacta P4 ARCH_AGENT_PRINCIPLES)
   - C15 chat primitiva (impacta D2 `SPEC_CHAT_PRIMITIVE.md`)
   - C14 bandeja polimórfica (impacta D1 `SPEC_BANDEJA_UNIFIED.md` con 12 kinds)
   - C16 LGPD (impacta D8 `POL_DATA_PORTABILITY_LATAM.md` — legal exposure no negociable)

2. **P1 de esta semana según handoff §9:**
   - D9 dark palette → crear `ENT_DESIGN_SYSTEM_TOKENS.md` (bajo riesgo)
   - D7 AgentSpec lifecycle → editar `ARCH_AGENT_PRINCIPLES.md` P1 + audit verbs en SPEC §12
   - Crear `SCH_OVERLAY_POLICY.md` (P0 en brechas — central para skill 3-layer)

3. **Crear serie B2-B5 pendiente** (sin cambio vs manifiesto padre). B2 persona journeys tiene mayor ROI pre-design-partners.

## Stamp

REFRESH — indexación propia VIGENTE desde 2026-04-20. Serie AUDIT_FABERLOOM continúa DRAFT hasta validación de 3 design partners + cierre de las 21 OQ + 6 brechas (proyectado post-2026-06-14).
