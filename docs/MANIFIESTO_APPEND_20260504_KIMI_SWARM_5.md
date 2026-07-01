---
id: MANIFIESTO_APPEND_20260504_KIMI_SWARM_5
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-04
fecha: 2026-05-04
agente: Cowork (arquitecto · ingestion Kimi Swarm output)
swarm: Kimi K2.6 Swarm #5 (12 sub-agentes paralelos)
aplica_a: [MWT, FaberLoom, ScanFoot]
---

# MANIFIESTO_APPEND_20260504_KIMI_SWARM_5

## Que paso

CEO ejecuto Kimi Swarm #5 con prompt creado en sesion previa (2026-05-03 · `KIMI_SWARM_5_TEAM_SOTA_PROMPT.md`). 12 sub-agentes paralelos cubrieron Arquitectura · Platform Eng · AI/Agents · Frontend · Backend · Data · Observability · Security · Compliance LATAM · Hardware/IoT · Mobile · QA/Reliability.

CEO subio output como zip (`Kimi_Agent_KIMI SWARM Prompt Guide.zip`) con 11 archivos: 9 sub-agentes individuales + RAW_OUTPUT.md (sintesis 30 KB con A1-A12 + S1-S5) + plan.md.

Cowork ingirio research raw, sintetizo aprendizaje, y construyo:
1. **ENT_GOB_TEAM_INVENTORY_FULL v2.0** (bump de v1.0 con +26 FTE) — gaps de v1.0 cerrados con SOTA 2026.
2. **ENT_GOB_ENGINEERING_COMPETENCIES v1.0** (archivo nuevo) — 10 competencias transversales que TODO eng del dominio debe dominar, con matriz cruzada × disciplinas.

## Documentos creados

| Archivo | Que documenta | Lineas aprox |
|---|---|---|
| `docs/ENT_GOB_ENGINEERING_COMPETENCIES.md` | 10 competencias transversales SOTA 2026 (C1-C10): Contract-first · RLS Hardening · SLO Engineering · HITL+Draft-first · Threat Modeling · Observability-driven · Supply Chain · Performance Budgets · Property/Contract testing · DPA-as-code. Por cada una: definicion · evaluacion en hire · disciplinas · KPI · confianza. Plus matriz × × × disciplinas, top-5 anti-patterns 2026, integracion con hiring stages. | ~280 |
| `docs/MANIFIESTO_APPEND_20260504_KIMI_SWARM_5.md` | Este archivo · trazabilidad ingestion swarm | ~150 |
| `docs/anexos/kimi_team_swarm/README.md` | Index del research raw (11 archivos · NO indexable pgvector) | ~50 |
| `docs/anexos/kimi_team_swarm/RAW_OUTPUT.md` | Output integrado swarm completo | ~500 |
| `docs/anexos/kimi_team_swarm/A1_ARCH.md` | Sub-agente arquitectura | ~80 |
| `docs/anexos/kimi_team_swarm/A2_PLATFORM_ENG.md` | Sub-agente platform eng | ~50 |
| `docs/anexos/kimi_team_swarm/A3_AI_AGENTS_SOTA_2026.md` | Sub-agente AI/agents | ~60 |
| `docs/anexos/kimi_team_swarm/A5_BACKEND_SOTA_2026.md` | Sub-agente backend | ~80 |
| `docs/anexos/kimi_team_swarm/A6_DATA.md` | Sub-agente data | ~55 |
| `docs/anexos/kimi_team_swarm/a8_security.md` | Sub-agente security | ~100 |
| `docs/anexos/kimi_team_swarm/A9_COMPLIANCE_LATAM_2026.md` | Sub-agente compliance LATAM | ~50 |
| `docs/anexos/kimi_team_swarm/A10_HW_IOT_SOTA_2026.md` | Sub-agente hardware/IoT | ~70 |
| `docs/anexos/kimi_team_swarm/A11_MOBILE_2026.md` | Sub-agente mobile | ~55 |
| `docs/anexos/kimi_team_swarm/plan.md` | Plan ejecucion swarm | ~50 |

## Documentos modificados

| Archivo | Cambio |
|---|---|
| `ENT_GOB_TEAM_INVENTORY_FULL.md` | v1.0 -> v2.0. +26 FTE total (~109 -> ~135). Disciplina nueva 2 Architecture (Software Architect + Solutions Architect). Disciplina 6 Mobile expandida 3->5. Disciplina 7 AI/Agents split en 4 sub-roles (AI Agent Architect Staff+, AI Eval/Red Team, LLM Ops, Prompt Eng capability). Disciplina 9 Hardware **expandida 3->8 FTE** (Embedded Architect Staff + 2x Firmware + RF/BLE + HW Security + HW/PCB + Manufacturing). Disciplina 10 split en 3 (Platform Eng + DevOps/SRE + Observability). Disciplina 11 Security split AppSec Architect + Security Engineers + Product Security. Disciplina 12 Compliance + Privacy Engineer tecnico (separado de DPO). Disciplina 14 QA + Contract Testing + Property-Based + Chaos. Disciplina 16 + Implementation Engineer. Disciplina 17 + Product Marketing Manager. +Top-10 roles indispensables seccion nueva. +Anti-patterns 2026 en Riesgos. AI Safety marcado [v2 RESUELTO] dentro de AI Eval/Red Team. |
| `IDX_GOBERNANZA.md` | +1 fila Entities (Engineering Competencies). Bump TEAM_INVENTORY v1.0 -> v2.0 con descripcion expandida. Health line: 12 -> 13 ENTs gob. Ultima revision -> 2026-05-04. last_review header -> 2026-05-04. |
| `CLAUDE.md` (raiz) | Conteo total 434 -> 446 archivos markdown. docs/ activo 296 -> 297 (+1 ENGINEERING_COMPETENCIES, TEAM_INVENTORY ya estaba). docs/anexos/ +11 archivos (kimi_team_swarm: 9 sub-agentes + RAW_OUTPUT + README + plan). +1 manifiesto. +linea Estado actual seccion. |

## Decisiones del arquitecto

1. **Bump v1.0 -> v2.0 en mismo archivo, no archivo nuevo.** Razon: TEAM_INVENTORY es archivo canonico unico. Versionar via header + changelog mantiene KB simple. Tags `[v2-NEW]`, `[v2-EXPANDED]`, `[v2-SPLIT]`, `[v2-RECAT]` en cada rol modificado preservan trazabilidad granular.

2. **ENGINEERING_COMPETENCIES como archivo separado, no seccion del INVENTORY.** Razon: son dimensiones distintas (cualitativa vs cuantitativa). Roles cuantifican headcount; competencias cualifican el nivel del hire. Companion files independientes con cross-ref explicita.

3. **Hardware expandido 3 -> 8 FTE es el cambio mas grande.** Kimi A10 [HIGH] no negociable: equipo <5 FTE biometrico = imposible cubrir BLE+OTA+seguridad+PCB+test+manufactura. Embedded Architect Staff es prerequisito AC-02 gate. 6 roles separados (Embedded Architect, 2x Firmware, RF/BLE, HW Security, HW/PCB, Manufacturing) son SOTA 2026 hardware comercial.

4. **AI Safety resuelto via AI Eval/Red Team Engineer (no role separado).** v1.0 lo marco como pendiente "no se que quedara". v2.0 lo resuelve dentro de §7 AI/Agents. Coherente con Kimi A3 [HIGH]: AI Eval/Red Team es role separado dedicado (Senior).

5. **Platform Engineering decision IDP SaaS no self-hosted.** Kimi A2 [HIGH]: Backstage self-hosted <100 eng = 3-12 FTE + $1M+/year. Port o Roadie SaaS hasta umbral 100 eng. Esto cierra la decision arquitectonica antes de que se materialice como tech debt.

6. **Privacy Engineer separado de DPO.** Kimi A9 [HIGH]: PE codifica (RLS, KMS, DP); DPO gobierna (regulatorio, contratos). Ratio DPO:PE 1:1.5. v1.0 los confundia (Compliance Engineer tecnico era hibrido).

7. **Status v2.0 sigue DRAFT.** Documento con cambios materiales (+26 FTE, disciplina nueva, splits multiples) requiere validacion CEO antes VIGENTE. CEO valida headcount + roles + estructura + competencies en sesion dedicada.

8. **Top-10 roles indispensables como seccion nueva.** Kimi S1 da orden estrategico de hire. v2.0 lo expone explicito al inicio para que cuando se cree HIRING_ROADMAP_F1 los primeros 10 hires esten priorizados.

9. **Research raw a `docs/anexos/kimi_team_swarm/` (no `docs/`).** Patron Ruflo replicado: research raw NO va a pgvector ni IDX. README en la carpeta documenta contenido. Solo el aprendizaje destilado (TEAM_INVENTORY v2 + COMPETENCIES) entra a KB indexable.

## Por que dual output (inventory + competencies)

CEO en sesion 2026-05-03 eligio "ambos: roles + competencias transversales" en AskUserQuestion. La separacion en 2 archivos refleja la estructura real:
- **Roles** = headcount + responsabilidad core. Operacional, planificable, contable.
- **Competencias** = piso de calidad por hire. Filtro cualitativo, evaluable en entrevista.

Mezclar ambos en un solo archivo seria confuso (hiring manager lee diferente "necesito 8 FTE hardware" vs "todo eng debe dominar threat modeling"). Companion files con cross-ref explicito.

## Que NO se hizo

- **No se actualizo ARCH_AGENT_PRINCIPLES.** v2.0 referencia los 14 principios pero no los modifica. Si en el futuro un principio frontend o multi-agent amerita cambio fundacional, va en PR separado.
- **No se actualizo ENT_GOB_DECISIONES.** Decisiones del swarm (anti-patterns, IDP SaaS, ratio platform 1:8, etc.) NO se formalizaron como DEC-NNN. Si CEO quiere formalizarlas, va en sesion siguiente.
- **No se creo HIRING_ROADMAP_F1.** Roadmap concreto con candidatos/fechas/comp ranges requiere Head of People + CFO + plan financiero. Pendiente P0 documentado en TEAM_INVENTORY v2.0.
- **No se creo COMP_BANDS_LATAM.** Bandas salariales requieren benchmark LATAM real. Pendiente P1.
- **No se creo POL_HIRING_GATES.** Gates de revenue/runway per fase. Pendiente P1.
- **No se promovio v2.0 a VIGENTE.** Status sigue DRAFT por cambios materiales. CEO valida antes.
- **No se ingirio research raw a pgvector.** Sigue patron Ruflo: research crudo en `docs/anexos/`, NO indexable. Solo el destilado (ENT_v2 + COMPETENCIES_v1) va a pgvector.
- **No se creo PLB de "como ejecutar Kimi Swarm".** Patron empirico CEO+Cowork. Si se vuelve frecuente, formalizar como PLB_KIMI_SWARM_RESEARCH.

## Sync canonico requerido

Esta sesion es Cowork -> escribio en OneDrive. Para que cambios pasen al repo canonico (`C:\dev\mwt-knowledge-hub`):

1. Ejecutar `sync_kimi_swarm_5_indexa.ps1` (creado en raiz del workspace) — copia los archivos modificados/nuevos al repo canonico (incluyendo carpeta `docs/anexos/kimi_team_swarm/` completa).
2. CEO valida diff con `git diff`.
3. CEO commitea con mensaje sugerido: `[GOBERNANZA] Kimi Swarm #5 ingestion - TEAM_INVENTORY v2.0 + ENGINEERING_COMPETENCIES v1.0 (+26 FTE / 10 capabilities)`.
4. Restaurar mirror oficial al final con `mirror_to_onedrive.ps1`.

## Proximas acciones

| Prioridad | Item | Bloqueo | Dueño |
|---|---|---|---|
| **P0** | CEO valida TEAM_INVENTORY v2.0 + ENGINEERING_COMPETENCIES v1.0 | Lectura | CEO |
| **P0** | CEO decide orden hire F1 (28 FTE simultaneos imposible) | v2.0 aprobado | CEO + futuro CTO |
| **P0** | Crear ENT_GOB_HIRING_ROADMAP_F1 con candidatos/fechas/comp ranges | v2.0 + competencies aprobados | CEO + futuro Head of People |
| P1 | Crear ENT_GOB_COMP_BANDS_LATAM con bandas salariales | Roadmap firmado | Head of People |
| P1 | Crear POL_HIRING_GATES con gates revenue/runway per fase | F1 cerrado | CEO + CFO |
| P1 | Reconciliar TEAM_INVENTORY v2.0 con ENT_GOB_PENDIENTES | v2.0 VIGENTE | CEO |
| P2 | Validar 5 items que swarm marco "validacion humana requerida" | docs/anexos/kimi_team_swarm/README | CEO |
| P2 | Considerar formalizar PLB_KIMI_SWARM_RESEARCH si patron se repite >3 veces | Despues de Swarm #6 | Cowork |

## Items que el swarm marco para validacion humana

Estos 5 items requieren expertise externa o decision CEO que el swarm no pudo resolver:

1. **Vendor lock-in data residency LATAM por proveedor** (AWS/GCP/Oracle Q2 2026) — verificar contratos vigentes.
2. **Presupuesto hardware (8-10 FTE)** — validar contra roadmap ScanFoot y unit economics. Es el cambio mas grande de v2.0.
3. **LangGraph vs in-house HITL absoluto** — PoC 2 semanas con `interrupt_before` real para confirmar.
4. **Calculo epsilon DP pool colectivo** — revision estadistico; e<=8 es heuristica del swarm.
5. **LATAM cloud residency** — verificar contratos vigentes Q2 2026 con proveedores.

## Changelog

- 2026-05-04 · Creacion inicial. Ingestion Kimi Swarm #5 output (12 sub-agentes paralelos). Construccion ENT_GOB_TEAM_INVENTORY v1.0 -> v2.0 (+26 FTE) + ENT_GOB_ENGINEERING_COMPETENCIES v1.0 (10 capabilities transversales). Total: 13 archivos nuevos (1 ENT canonico + 1 manifiesto + 11 anexos research raw incluido README) + 2 modificados (TEAM_INVENTORY bump major + IDX_GOBERNANZA + CLAUDE.md).
