# POL_DETERMINISMO - 4 Principios + Vacio Explicito
id: POL_DETERMINISMO
version: 1.2
status: VIGENTE
stamp: VIGENTE - 2026-05-03
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

1. **Dato Unico**: cada dato vive en un solo lugar. Si se necesita en otro, se referencia.
   - **Regla 3 ejecutable (v1.2):** los **conteos vivos** (totales de archivos, ratios de stubs, conteos por dominio, versiones de archivos referenciados) viven exclusivamente en `DASHBOARD_SNAPSHOT.md`. CLAUDE.md, RW_ROOT.md, DEPENDENCY_GRAPH.md, IDX_*.md NO deben hard-codear cifras totales - solo referenciar `-> ver DASHBOARD_SNAPSHOT seccion Conteos`. Origen: AUDIT_REINDEXA 2026-05-03 detecto drift de 4 fuentes desincronizadas (CLAUDE 446, RW_ROOT 308, DEPENDENCY_GRAPH 289, DASHBOARD 404 - real 535).
2. **Vacio Explicito**: dato ausente se marca `[PENDIENTE - NO INVENTAR]`. Nunca estimar, aproximar ni suponer. El PENDIENTE es informacion util: dice exactamente que falta para completar.
3. **Regla de Decision**: toda decision tiene criterio documentado, no se decide ad-hoc.
4. **Escalamiento por Defecto**: discrepancia, ambiguedad o PENDIENTE detectado = escalar al CEO con contexto de que falta y que desbloquea.

## Vacio Explicito - Reglas operativas
- Si un campo no tiene dato confirmado -> marcar `[PENDIENTE - NO INVENTAR]`
- Si un schema requiere entity con campos PENDIENTE -> no ensamblar. Escalar.
- Nunca rellenar con estimaciones, aproximaciones o suposiciones.

---

## Enforcement
- **Deteccion:** Dato duplicado en 2+ archivos, decision sin criterio documentado, discrepancia no escalada, o campo rellenado con estimacion en vez de `[PENDIENTE - NO INVENTAR]`. Conteos hardcoded fuera de DASHBOARD_SNAPSHOT (Regla 3 v1.2).
- **Accion:** Eliminar duplicado (mantener fuente maestra), documentar criterio, revertir a PENDIENTE, escalar al CEO. Para conteos hardcoded: reemplazar por referencia a DASHBOARD.
- **Severidad:** HARD - dato inventado o duplicado puede llegar a produccion.

---
Stamp: VIGENTE - 2026-05-03
Vencimiento: 2026-08-01
Estado: VIGENTE
Aprobador final: CEO

---
Changelog:
- v1.0 (2026-03-01): creacion inicial.
- v1.1 (2026-04-13): absorbe POL_VACIO. Principio 2 expandido. Seccion operativa de vacio explicito integrada. KB Hygiene v4.7.0.
- v1.2 (2026-05-03): +Regla 3 ejecutable bajo Principio 1 (Dato Unico). Conteos vivos solo viven en DASHBOARD_SNAPSHOT. Stamp renovado. Origen: AUDIT_REINDEXA_KB 2026-05-03.
