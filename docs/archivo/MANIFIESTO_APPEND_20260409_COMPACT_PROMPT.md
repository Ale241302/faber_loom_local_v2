---
id: MANIFIESTO_APPEND_20260409_COMPACT_PROMPT
type: TRANSITORIO
stamp: 2026-04-09
expires: post-consolidación (próxima sesión de mantenimiento)
---

# MANIFIESTO_APPEND — 2026-04-09 — Compact System Prompt

## Contexto

El CLAUDE.md acumuló datos de estado inlinados (conteo de archivos, sprints activos, deuda técnica, GTINs, score de auditoría, etc.) que se cargaban en cada turno aunque no fueran relevantes. Esto violaba el principio de retrieval de la taxonomía: la KB es el estado, el CLAUDE.md es el comportamiento.

Solución: reescribir CLAUDE.md como Compact System Prompt — solo instrucciones permanentes. Todo dato de estado vive en la KB y se consulta on-demand.

## Archivos modificados (2)

| Archivo | Cambio | Versión |
|---------|--------|---------|
| CLAUDE.md | 466L → 207L (-56%). Datos de estado removidos. Navegación por tabla lookup. Tiers de carga. Comandos rápidos consolidados. CÓDIGO/SPRINT comprimido. | v4.6.5 → v4.6.7 |
| RW_ROOT.md | Version bump. +entrada changelog v4.6.7. | v4.6.6 → v4.6.7 |

## Qué se removió de CLAUDE.md (y dónde vive ahora)

| Dato removido | Ahora vive en |
|--------------|---------------|
| Conteo de archivos (~272) | DASHBOARD_SNAPSHOT.md |
| Sprints activos / status | DASHBOARD_SNAPSHOT.md |
| Deuda técnica detallada | DASHBOARD_SNAPSHOT.md |
| GTINs (66 EAN-13, prefijo GS1) | ENT_OPS_TALLAS.md |
| Mercados (USA/CR/BR status) | DASHBOARD_SNAPSHOT.md / ENT_MERCADO_* |
| Score auditoría (9.1/10) | DASHBOARD_SNAPSHOT.md |
| LLM pricing detallado por modelo | ENT_PLAT_LLM_ROUTING.md |
| Lista de SSOTs activos | ENT_PLAT_SSOT.md |
| Pendientes CEO activos | ENT_GOB_PENDIENTES.md |
| Nomenclaturas AG-*/SVC-*/CLIENT_* | ENT_GOB_AGENTES.md |
| Estado infraestructura / container | DASHBOARD_SNAPSHOT.md |
| Changelog detallado (Capas 1-9) | MANIFIESTO_CAMBIOS_v2.md |

## Impacto en tokens

| Métrica | Antes | Después |
|---------|-------|---------|
| CLAUDE.md líneas | 466 | 207 |
| CLAUDE.md tokens (est.) | ~6,000 | ~2,700 |
| Ahorro por turno | — | ~3,300 tokens |
| Ahorro en sesión 30 turnos | — | ~99,000 tokens (~$0.30 Sonnet) |

## RW_ROOT

v4.6.6 → v4.6.7
