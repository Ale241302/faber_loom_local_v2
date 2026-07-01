# POL_NUEVO_DOC - Regla de Creacion
id: POL_NUEVO_DOC
version: 1.1
status: VIGENTE
stamp: VIGENTE - 2026-05-03
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

| Necesito... | Creo un... | Ubicacion |
|-------------|------------|-----------|
| Estructura de output nueva | Schema (SCH_) | /schemas/ + SCHEMA_REGISTRY |
| Dato nuevo | Entity (ENT_) | Domain Index correspondiente |
| Traduccion/adaptacion idioma | Loc (LOC_) | Junto a su entity padre |
| Regla del sistema | Policy (POL_) | /policies/ |
| Instruccion operativa | Playbook (PLB_) | Domain Index correspondiente |
| Ruta nueva | Index (IDX_) | Root Index si dominio nuevo |

## Regla
- Nunca mezclar tipos: dato en entity, instruccion en playbook, estructura en schema
- Si no sabes que tipo es -> probablemente es entity (dato puro)

## Regla 1 (v1.1) - Si no esta indexado, no existe

Todo archivo nuevo debe entrar en su `IDX_{DOMINIO}` (o `SCHEMA_REGISTRY` si es SCH) **en el mismo PR que lo crea**. No diferir indexacion a "la proxima INDEXA". Crear archivo huerfano = HARD violation.

**Ejecutable como gate de PR:**
- Si el PR agrega un .md nuevo en `docs/` o `docs/faberloom/` y no toca el `IDX_{DOMINIO}` correspondiente (o `SCHEMA_REGISTRY` para SCH_) -> bloquear merge.
- Excepcion unica: archivos efimeros con `type: TRANSITORIO` declarado correctamente (ver POL_EPHEMERAL_OUTPUT v1.1+).

---

## Enforcement
- **Deteccion:** Archivo nuevo creado sin registrar en IDX correspondiente
- **Accion:** Registrar en IDX antes de continuar
- **Severidad:** HARD - archivo huerfano no es descubrible

---
Stamp: VIGENTE - 2026-05-03
Vencimiento: 2026-08-01 (90 dias desde ultimo review)
Estado: VIGENTE
Aprobador final: CEO

---

## Changelog
- v1.0 (2026-03-01): creacion inicial.
- v1.1 (2026-05-03): +Regla 1 "Si no esta indexado, no existe" canonizada como ejecutable de PR. Origen: AUDIT_REINDEXA_KB 2026-05-03 detecto 5 SCH_FB huerfanos del SCHEMA_REGISTRY violando esta regla implicita. Stamp renovado.
