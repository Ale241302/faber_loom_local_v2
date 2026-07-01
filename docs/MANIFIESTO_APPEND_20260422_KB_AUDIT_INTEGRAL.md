# MANIFIESTO_APPEND_20260422_KB_AUDIT_INTEGRAL
fecha: 2026-04-22
autor: Claude (Cowork)
tipo: INDEXACION (auditoría integral + fix estructural de routers)
trigger: CEO — "puedes auditar el proyecto" + "haslo todo" + "indexa"
aplica_a: [SHARED]

---

## Resumen

Gate cierra auditoría integral 7-alcance sobre la KB MWT (402 archivos .md, 254 activos en docs/) y canoniza fix estructural de los 10 IDX routers que operaban sin header YAML frontmatter — brecha crítica porque los IDX gobiernan el ruteo pgvector por dominio y visibilidad.

Salud general de la KB: AMARILLA con 3 focos rojos. Disciplina FROZEN respetada. Namespace sin duplicados ni cruces tipo/contenido. Memoria cross-sesión (auto-memory) con 21 entradas sólidas pero 5 SPECs FaberLoom faltantes y 23 open questions del handoff v3.5 sin cerrar. 4 pendientes CEO CRÍTICOS vencen 2026-05-30 (28 días).

Este batch NO modifica FROZENs, NO toca pgvector (B1c-P2 sigue bloqueado esperando CEO-35). Solo cierra el gap taxonómico P0 de los IDX y persiste el reporte ejecutivo como registro CEO-ONLY en `reportes/`.

## Contexto

Auditoría solicitada por CEO post-iteración de productividad (intento de bootstrap plugin `/productivity:start` se descartó por colisión con CLAUDE.md MWT + duplicación con auto-memory + ENT_GOB_PENDIENTES). Se ofrecieron 7 alcances — CEO eligió "haslo todo". Ejecución delegada en 3 subagentes paralelos (Explore):

1. **Compliance taxonómico** — 23 archivos sin header, 10 IDX sin los 5 campos obligatorios, 11 CEO-ONLY sin declarar `ceo_only_sections:`
2. **KB_AUDIT B0-B11 + FROZENs** — B0/B1a/B1b/B1c-P1 DONE; B1c-P2 BLOQUEADO CEO-35; FROZENs íntegros
3. **Pendientes CEO + gap FaberLoom** — 17 activos (4 CRÍTICOS vencen 2026-05-30); 5 SPECs FaberLoom faltantes en KB pero presentes en auto-memory

Tras entrega del reporte, CEO autorizó ejecutar las 2 acciones de 48h que sí son ejecutables desde Cowork: fix headers IDX (acción P0) + persistir reporte. Las acciones #1 (ZIPs) y #3 (batch Q1-Q12 LLM) quedaron pendientes por requerir decisión humana. Los 10 CEO-ONLY leaks se dejaron pendientes en otra iteración (ya trackeados como CEO-32 con deadline 2026-05-30).

## Archivos creados

| Archivo | Bytes | Función |
|---------|-------|---------|
| `reportes/AUDIT_KB_INTEGRAL_20260422.md` | ~14000 | Reporte ejecutivo 7-alcance CEO-ONLY. 10 secciones: exec summary, higiene, compliance, KB_AUDIT status, FROZENs, pendientes CEO, gap FaberLoom, top 5 riesgos, plan 48h/7d/30d, observaciones finales |
| `MANIFIESTO_APPEND_20260422_KB_AUDIT_INTEGRAL.md` | (este) | Manifiesto del gate |

## Archivos modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `IDX_COMERCIAL.md` | ADD HEADER | `id/version/status/visibility/domain/tipo/last_review` · preserva revisión 2026-04-16 |
| `IDX_COMPLIANCE.md` | ADD HEADER | idem · preserva 2026-04-03 |
| `IDX_DISTRIBUCION.md` | ADD HEADER | idem · preserva 2026-03-14 |
| `IDX_GOBERNANZA.md` | ADD HEADER + EDIT | header + last_review 2026-04-21→2026-04-22 + nota audit integral |
| `IDX_MARCA.md` | ADD HEADER | idem · preserva 2026-04-16 |
| `IDX_MARKETPLACE.md` | ADD HEADER | idem · preserva 2026-04-16 |
| `IDX_MERCADOS.md` | ADD HEADER | idem · preserva 2026-03-18 |
| `IDX_OPS.md` | ADD HEADER | idem · preserva 2026-04-01 |
| `IDX_PLATAFORMA.md` | ADD HEADER | idem · preserva 2026-04-21 |
| `IDX_PRODUCTO.md` | ADD HEADER | idem · preserva 2026-04-03 |
| `RW_ROOT.md` | EDIT v4.8.5→v4.8.6 | Changelog v4.8.6 con resumen del INDEXA KB_AUDIT_INTEGRAL |

## Decisiones de indexación

1. **Visibilidad de los 10 IDX = INTERNAL, no PUBLIC.** Los routers de dominio listan nombres de entities y estado (ej. `ENT_COMERCIAL_PRICING`, `ENT_COMP_LGPD`). Si un atacante lee un IDX completo, obtiene mapa de la organización. INTERNAL protege sin bloquear acceso del equipo. PUBLIC se descarta. CEO-ONLY sería excesivo — la mayoría del equipo necesita navegar estos índices.

2. **`tipo: index` agregado aunque no esté en la taxonomía de 8 tipos.** El prefijo IDX_ ya implica el tipo, pero declararlo explícitamente en header simplifica parsing para pgvector y scripts de validación. Consistente con precedente: ENTs/PLBs/POLs declaran `tipo:` en muchos archivos pese a que el prefijo ya es self-describing.

3. **`last_review` preservado de cada IDX, no uniformado a 2026-04-22.** La última revisión del contenido siguió su fecha original — el header se agregó en 2026-04-22 pero el contenido de IDX_DISTRIBUCION (por ejemplo) sigue reflejando el estado del 2026-03-14. Uniformar a hoy mentiría sobre frescura del contenido.

4. **Reporte AUDIT va a `reportes/`, no a `docs/`.** Precedente: `reportes/AUDIT_FULL_20260328.md`, `reportes/AUDIT_POST_CLONE_20260416.md`. Los audits puntuales CEO-ONLY no compiten con el archivo canónico `KB_AUDIT` en curso (carpeta `audit/`) y quedan accesibles para referencias futuras sin inflar `docs/`.

5. **No se agregaron items a ENT_GOB_PENDIENTES.** Toda la deuda detectada ya estaba trackeada:
   - Leaks CEO-ONLY → CEO-32 (vence 2026-05-30)
   - B1c-P2 → CEO-35
   - 5 SPECs FaberLoom faltantes → Q1-Q18 track FaberLoom LLM Orchestration
   - Compliance BR → CEO-23, CEO-25, CEO-27
   - Sin duplicación.

6. **Los 10 CEO-ONLY leaks se dejaron para otra iteración.** Camino A (cambiar visibility PUBLIC→INTERNAL) era opción recomendada en 10 min, pero CEO eligió postponer. Justificación: 36 días de buffer antes del vencimiento CEO-32, menor riesgo que B1c-P2 o el batch Q1-Q12 LLM. Coherente con priorización de riesgos del reporte.

7. **Commit single, no split.** Los 10 IDX + reporte van en un solo commit `51737ef` por coherencia del gate. Alternativa (11 commits atómicos) habría roto el principio de "un cambio atómico = un gate" del flujo INDEXA.

8. **Branch feat/faberloom-mockup-v2-chat mantenida, NO merge a main.** El audit no cierra la rama activa. Merge a main se hará cuando Sprint FaberLoom avance a MVP. Mantener auditorías acumuladas en la rama permite revisión conjunta antes del merge.

## Ámbito del gate

```
GATE ✅ INDEXA KB_AUDIT_INTEGRAL_20260422 (señal CEO: "indexa")

SCOPE
├── Auditoría 7-alcance (higiene · taxonomía · KB_AUDIT · FROZENs · pendientes CEO · FaberLoom gap · git/sync)
├── Fix taxonómico 10 IDX routers (visibility pgvector-routable)
├── Persistencia reporte ejecutivo CEO-ONLY en reportes/
└── Bump RW_ROOT v4.8.5→v4.8.6

NO SCOPE (deferred)
├── CEO-32 leaks CEO-ONLY (10 archivos) — Camino A mov visibility PUBLIC→INTERNAL, 10 min
├── CEO-34 renovación 22 POLs pre-2026-05-30 (opcional)
├── CEO-35 B1c-P2 shadow reindex pgvector (requiere container access)
├── Q1-Q12 LLM Orchestration batch CEO decisions (7 P0 bloqueantes)
├── 5 SPECs FaberLoom faltantes (LLM_ORCHESTRATION, RESEARCH_SWARM, 2 ADRs, BRAND)
├── Higiene raíz (2 ZIPs + 14 PROMPTs + scripts/)
└── CRLF normalización global (93.75% archivos afectados)

COMMITS
├── 51737ef [GOBERNANZA] Fix headers YAML en los 10 IDX routers (already pushed)
└── <next>  [GOBERNANZA] MANIFIESTO + IDX_GOB + RW_ROOT update (pendiente push)

POSTMORTEM
├── Audit detectó deuda estructural real pero no crítica en taxonomía
├── 3 focos rojos son de contenido/decisión (pendientes CEO, FaberLoom specs, higiene raíz) — no arreglables desde Cowork sin input humano
├── FROZEN discipline holds (cero violaciones en 20 últimos commits)
├── auto-memory va por delante de KB formalizada — riesgo de divergencia si se pierde auto-memory
└── Salud KB estable pero con deuda acumulada que requiere sprint dedicado post-FaberLoom Sprint 1
```

## Resumen salud post-gate

- **Taxonomía**: AMARILLO → AMARILLO-claro (10 IDX ✅ · aún 13 archivos sin header: RW_ROOT, SCHEMA_REGISTRY, MANIFIESTOs, algunos SPECs · 11 CEO-ONLY sin ceo_only_sections)
- **FROZENs**: VERDE (sin cambios)
- **Pendientes CEO**: ROJO (4 CRÍTICOS vencen 28d, sin movimiento en este gate)
- **FaberLoom specs**: ROJO (5 SPECs faltantes, sin movimiento en este gate)
- **Higiene raíz**: ROJO (27 archivos sueltos, sin movimiento en este gate)
- **Git/Sync**: AMARILLO → AMARILLO (21 modified uncommitted previos siguen sin review, commit 51737ef + este agregan 12 archivos nuevos)
- **KB_AUDIT 2026-04-18**: AMARILLO (sin cambios — CEO-35 sigue bloqueando)

**Next gate recomendado**: atacar #6 (B1c-P2 shadow reindex, requiere CEO-35) o #7 (transcribir SPEC_FABERLOOM_LLM_ORCHESTRATION desde auto-memory) — son los bloqueantes reales de avance.
