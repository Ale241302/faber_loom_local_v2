# POL_STUB_LIFECYCLE — Ciclo de Vida de Stubs
id: POL_STUB_LIFECYCLE
version: 1.0
status: VIGENTE
stamp: VIGENTE — 2026-03-01
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]


---

## Reglas

1. **Creación justificada**: un stub se crea solo si hay un plan concreto de llenado. Debe declarar `planned_sprint:` o `planned_date:` en su header.
2. **Caducidad 90 días**: stub sin contenido real después de 90 días desde su creación → se depreca automáticamente en la próxima revisión.
3. **Revisión trimestral**: el CEO revisa la lista de stubs cada 90 días. Stubs vencidos se deprecan o eliminan.
4. **Conteo en IDX**: cada IDX reporta cuántos stubs tiene en su bloque Health. Más de 30% stubs en un dominio = señal de que se están creando archivos especulativos.

## Enforcement
- **Detección:** IDX Health muestra ratio stubs/total > 30%, o stub con created_at > 90 días sin contenido
- **Acción:** stub vencido se marca `status: DEPRECATED — stub caducado sin contenido`
- **Severidad:** SOFT — no bloquea operaciones, pero se reporta en auditoría

---
Stamp: VIGENTE 2026-03-14
Estado: VIGENTE
Aprobador final: CEO

---
Changelog:
- v1.0 (2026-03-14): creación inicial (Ola G).
