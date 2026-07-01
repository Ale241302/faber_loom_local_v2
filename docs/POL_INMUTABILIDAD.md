# POL_INMUTABILIDAD - No Se Recalcula el Pasado
id: POL_INMUTABILIDAD
version: 1.1
status: VIGENTE
stamp: VIGENTE - 2026-05-03
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

Precios, comisiones y atribuciones registradas son inmutables.

## Regla
- PriceTable: una vez effective, el precio historico no se modifica. Nueva version = nuevo registro con effective_from.
- Attribution Ledger: eventos append-only. No se editan ni eliminan.
- Payouts: una vez PAYOUT_APPROVED, el monto no cambia. Correcciones = nuevo evento.
- Expedientes: costos registrados en un expediente cerrado no se recalculan.

## Regla 4 (v1.1) - Lo firmado no se edita in-place

`status: FROZEN` (sealed) y `status: VIGENTE` con stamp activo no se modifican in-place. Si hay cambio necesario:

1. Bumpear version (v1.x -> v1.x+1 o v2.0 si es breaking)
2. Crear nuevo archivo o actualizar el existente con `version:` incrementado
3. Si reemplaza completamente al anterior: marcar el anterior `status: DEPRECATED` con `replaced_by: <nuevo>`
4. Documentar en MANIFIESTO_CAMBIOS_v2 + POL_CHANGELOG

**Comportamiento del agente ante peticiones de editar FROZEN:**
- **Cowork/Code:** escalar al CEO antes de ejecutar - NO ejecutar silenciosamente, NO rechazar tampoco. El CEO es el unico que aprueba bumpear FROZEN.
- Excepcion unica: typos o fixes de metadata (sin tocar contenido normativo) -> permitido con bumpeo de patch (v1.x -> v1.x+1) y nota explicativa. Si modifica semantica, escalar.

**Archivos FROZEN canonicos (no exhaustivo):**
- `ENT_OPS_STATE_MACHINE.md`
- `PLB_ORCHESTRATOR.md`
- `ARCH_AGENT_PRINCIPLES.md` (sealed v1.5 commit `9ecd190`)
- `POL_DATA_CLASSIFICATION.md` (sealed v1.4)

## Alcance
Aplica a: pricing/, affiliates/, payments/, expedientes/, FROZEN registry.

## Justificacion
Recalcular el pasado corrompe auditorias, reportes financieros y confianza del sistema. Si hay error, se corrige hacia adelante con nuevo registro documentado.

---

## Enforcement
- **Deteccion:** Archivo con stamp FROZEN editado o status VIGENTE con cambio semantico sin bump de version.
- **Accion:** Revertir cambio, escalar al CEO con propuesta de version nueva.
- **Severidad:** HARD - rompe cadena de confianza.

---
Stamp: VIGENTE - 2026-05-03
Vencimiento: 2026-08-01
Estado: VIGENTE
Aprobador final: CEO

---
Changelog:
- v1.0 (2026-03-01): creacion inicial.
- v1.1 (2026-05-03): +Regla 4 "Lo firmado no se edita in-place" con comportamiento canonico del agente (escalar, no rechazar) + lista de FROZEN canonicos. Origen: AUDIT_REINDEXA_KB 2026-05-03 + intercambio cruzado con ChatGPT.
