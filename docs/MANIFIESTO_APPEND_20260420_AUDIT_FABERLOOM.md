# MANIFIESTO_APPEND_20260420_AUDIT_FABERLOOM
fecha: 2026-04-20
autor: Claude (Cowork)
tipo: INDEXACION
trigger: CEO — "indexa" sobre 9 archivos serie A1-A7 + B0 + B1 (auditoría pre-build FaberLoom mockup v1 beta, sesión Claude Code 2026-04-19)
aplica_a: [FaberLoom]

---

## Resumen

Indexación de 9 documentos de auditoría pre-build del mockup FaberLoom v1 beta como registros especiales tipo `AUDIT_` en dominio Gobernanza. Serie A (7 docs) = reconciliación forense entre SPECs MWT + prompt de build + código existente del mockup modular. Serie B (2 docs) = framework metodológico Service Design + service blueprint de 14 módulos × 4 capas. Todos quedan como **DRAFT · referencia, no canon** — su función es alimentar decisiones de producto antes de cerrar SPECs FaberLoom y design partners.

## Contexto

Los 9 archivos originales fueron generados en sesión Claude Code 2026-04-19 como due diligence pre-build del mockup. Álvaro los subió a Cowork 2026-04-20 con pregunta "qué piensas de ese trabajo" → análisis crítico → "indexa" como siguiente acción. La decisión de indexar fue deliberada: estos docs contienen 15 decisiones canon (A6) + 16 contradicciones (A7) + 17 open questions que necesitan visibilidad como pendientes, no pueden quedar como efímeros de sesión.

## Archivos creados

| Archivo | Bytes | Función |
|---------|-------|---------|
| `AUDIT_FABERLOOM_A1_SPEC_CANON_v1.md` | 13282 | Inventario forense SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT, 16 secciones, gaps `[NOT IN SPEC]` |
| `AUDIT_FABERLOOM_A2_CODE_INVENTORY_v1.md` | 10261 | Triage salvage mockup modular ~3600 LOC. Widgets 11/15, módulos 6/14, mock 3/17 collections |
| `AUDIT_FABERLOOM_A3_DARK_PALETTE_v1.md` | 11343 | Paleta dark WCAG AA. CRs calculados. 70+ tokens CSS listos para fragment |
| `AUDIT_FABERLOOM_A4_ARCH_PRINCIPLES_CANON_v1.md` | 8652 | Canon ARCH_AGENT_PRINCIPLES P0-P13, Autonomy Ladder L0-L4, 3 canonical objects |
| `AUDIT_FABERLOOM_A5_KNOWLEDGE_FLOW_CANON_v1.md` | 10691 | Canon SPEC_USER_ADMIN_KNOWLEDGE_FLOW. 4 scopes, roles matrix, break-glass, TTL 90d |
| `AUDIT_FABERLOOM_A6_RECONCILIATION_v1.md` | 8851 | 15 decisiones D1-D15 con precedencia (SPEC > prompt para data · prompt > SPEC para UI copy) |
| `AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1.md` | 20786 | 16 contradicciones C1-C16 + 17 open questions pendientes decisión CEO |
| `AUDIT_FABERLOOM_B0_METHODOLOGY_v1.md` | 13824 | Framework Service Design + UX Architecture + toolkit (Blueprint, JTBD, Nielsen 10 + 5 AI) |
| `AUDIT_FABERLOOM_B1_SERVICE_BLUEPRINT_v1.md` | 27620 | Blueprint 14 módulos × 4 capas (Frontstage/Backstage/Supporting/User actions) |

Total: 125,310 bytes · 2424 líneas contenido original + headers MWT canónicos añadidos.

## Archivos modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `RW_ROOT.md` | EDIT — registros especiales + changelog v4.8.2 | Agregada entrada `AUDIT_FABERLOOM_*` en tabla registros especiales. Changelog v4.8.2 con resumen indexación. |
| `IDX_GOBERNANZA.md` | EDIT — sección nueva + health counts | +sección "Auditorías FaberLoom pre-build" con tabla serie A (7) + serie B (2) + pendientes serie B no creados (B2-B5). Health header: +9 AUDIT. Última revisión → 2026-04-20. |
| `ENT_GOB_PENDIENTES.md` | EDIT — +17 open questions FaberLoom | Nueva sub-sección "Open questions AUDIT_FABERLOOM" bajo track FABERLOOM activo. 17 pendientes priorizados P0-P2 con ref a contradicción C-code. |

## Decisiones tomadas en esta indexación

1. **Nomenclatura `AUDIT_` como registro especial fuera de taxonomía 8 tipos.** Precedente: `SPEC_` y `ARCH_` ya existen como registros especiales en RW_ROOT §Registros Especiales. `AUDIT_` sigue misma lógica — no encaja limpio en ENT/PLB/SCH/LOC/POL/IDX/LOTE/SKILL. Alternativa considerada: clasificar como ENT_FABERLOOM_AUDIT_*. Descartada porque su contenido es meta-análisis sobre SPECs existentes, no data operativa.

2. **Dominio Gobernanza.** Consistente con SPEC_FABERLOOM_MVP, SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT, ENT_FABERLOOM_INSIGHTS_KIMI ya indexados ahí. FaberLoom no tiene dominio propio aún (pendiente decisión IDX_FABERLOOM vs registro especial en Gobernanza — ver MANIFIESTO_APPEND_20260419_FABERLOOM_BLUEPRINT).

3. **Status DRAFT uniforme.** Son reconciliación + blueprint pre-build. Promoción a VIGENTE requiere (a) validación de 3 design partners del wedge cotización B2B calzado seguridad, (b) cierre de las 17 open questions, (c) ratificación retroactiva de las invenciones prompt-authoritative (action-risk registry 6 fields, provenance chain field names, 12 inbound kinds) contra SPECs canónicos.

4. **Título original preservado.** Cada archivo abre con sección "## Titulo original" que captura el `# A1 — ...` original antes del contenido. Permite búsqueda por nombre original.

5. **17 open questions escalados a ENT_GOB_PENDIENTES.** No pueden quedar enterrados en A7. Priorización P0 (4 items — feedback taxonomy, bandeja polimórfica, chat primitiva, LGPD) · P1 (5 items) · P2 (8 items).

6. **DEPENDENCY_GRAPH no actualizado.** Estos docs son referencia meta, no se consumen en cadenas de ensamblaje de schemas. No aplica nodo en el grafo.

## Ámbito del gate

```
GATE ✅ (indexa explícito)
✔ Determinismo     — 9 archivos nuevos, ninguno duplica contenido de SPECs existentes
✔ Tipo             — AUDIT (registro especial, precedente SPEC_/ARCH_ documentado en RW_ROOT)
✔ Stamp            — DRAFT — referencia, no canon
✔ Version          — v1.0 (creación)
✔ Impacto cruzado  — referencia SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT, SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA, ARCH_AGENT_PRINCIPLES; NO modifica FROZENs
✔ Pendientes       — 17 open questions escalados a ENT_GOB_PENDIENTES sección FABERLOOM
✔ Sin inventados   — contenido verbatim del Claude Code original. Solo se añaden headers + changelog estándar
✔ IDX              — IDX_GOBERNANZA actualizado con sección dedicada + health count
✔ Seguridad        — visibility [INTERNAL]. No CEO_ONLY leak. Sin datos operativos sensibles.
```

## Refs activos

- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` v1.0 DRAFT (objeto auditado por A1)
- `ARCH_AGENT_PRINCIPLES` v1.2 VIGENTE (objeto auditado por A4)
- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA` v1.0 DRAFT (objeto auditado por A5)
- `faberloom-mockup/` (código salvage auditado por A2 — fuera de KB, en repo)
- `ENT_GOB_PENDIENTES` v12.0+ (recibe 17 open questions como track FaberLoom)

## Lo que el CEO tiene que decidir

1. **Las 17 open questions en ENT_GOB_PENDIENTES son bloqueantes para cerrar SPECs FaberLoom antes de design partners.** 4 son P0 (feedback taxonomy, bandeja polimórfica, chat primitiva, LGPD) — decisión esta semana o se empieza a construir sobre supuestos que van a cambiar.

2. **Ratificación retroactiva de "prompt-authoritative" en SPECs.** A6 documenta que el mockup fija canon (action-risk registry 6 fields, provenance chain, 12 inbound kinds) que no existe en ninguna SPEC. O se promueven a `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` en PR explícito, o quedan como legacy silencioso.

3. **Promoción DRAFT → VIGENTE de los AUDIT_.** Requiere cierre de las 17 open questions + validación de design partners. Proyectado post-2026-06-14 (corte S4 beta).

4. **Crear serie B2-B5.** B2 (persona journeys × 3 × 2 días = 6 journeys) · B3 (heurísticas Nielsen + 5 AI-specific) · B4 (edge case matrix) · B5 (cross-concern). B2 es el de mayor ROI — permite ver fricciones antes de construir. Pendiente asignación.

## Stamp

DRAFT — serie AUDIT_FABERLOOM queda en DRAFT. Indexación propia VIGENTE desde 2026-04-20.
