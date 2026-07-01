# POL_CHANGELOG — Registro Obligatorio de Cambios
id: POL_CHANGELOG
version: 1.0
status: VIGENTE
stamp: VIGENTE — 2026-03-01
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]


---

## Reglas

1. **Sesión sin registro = sesión que no existió.** Toda sesión que modifique la KB debe agregar una entrada al MANIFIESTO_CAMBIOS.md antes de cerrar.
2. **Formato de entrada**:
   - Fecha y nombre de sesión
   - Lista de archivos creados, modificados y deprecados
   - Resumen de cambios por ola/tema
   - Métricas antes/después (campos normalizados, stubs, violaciones)
3. **Orden**: el MANIFIESTO se escribe en orden cronológico. La entrada más reciente va al final.
4. **Pre-backup**: actualizar el MANIFIESTO es paso obligatorio ANTES de generar cualquier backup/export de la KB.

## Enforcement
- **Detección:** si la versión de RW_ROOT incrementó pero MANIFIESTO no tiene entrada para esa versión → violación
- **Acción:** escalar al CEO. No se genera backup hasta que se documente
- **Severidad:** HARD — bloquea backup

---
Stamp: VIGENTE 2026-03-14
Estado: VIGENTE
Aprobador final: CEO

---
Changelog:
- v1.0 (2026-03-14): creación inicial (Ola H).
