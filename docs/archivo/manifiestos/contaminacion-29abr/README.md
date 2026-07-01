# Contaminacion FaberLoom 29-abr-2026 -- Manifiestos archivados

## Por que estan aca

Los 4 MANIFIESTO_APPEND_20260429*.md de esta carpeta describen cambios
ejecutados por sesion Cowork del 29-abr-2026 que metieron scope FaberLoom
dentro del repo MWT. Esa contaminacion fue revertida en branch
saneamiento-29abr-fb. Ver MANIFIESTO_APPEND_20260429_REMEDIACION_FB.md
en docs/ raiz para estado final del incidente.

## Estado actual de los archivos que estos manifiestos referencian

- 11 archivos FB puros movidos a docs/faberloom/
- 3 gold_samples movidos a docs/faberloom/gold_samples/
- 5 archivos preexistentes (ENT_PLAT_OBSERVABILIDAD, ENT_PLAT_INFRA,
  IDX_PLATAFORMA, DEPENDENCY_GRAPH, RW_ROOT) revertidos al estado canonico
  del commit bc3695b (cierre 2026-04-28b)
- ARCH_AGENT_PRINCIPLES NO fue revertido. Modificado por commit legitimo
  9ecd190 (CORE BLINDADO ARCH v1.5).
- CLAUDE.md sin cambios committed del 29. Solo line endings descartados.

## Por que no se borran

Regla R3 de la KB MWT: no eliminar contenido, mover. Estos manifiestos
son evidencia historica del incidente y de la remediacion.

## Leccion incorporada

Regla anadida a CLAUDE.md (operacion separada post-merge): "Todo FaberLoom
vive bajo docs/faberloom/. Nunca crear archivos FB en docs/ raiz."
