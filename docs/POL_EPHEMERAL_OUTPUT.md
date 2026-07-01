# POL_EPHEMERAL_OUTPUT - Gestion de Outputs Efimeros
id: POL_EPHEMERAL_OUTPUT
version: 1.2
status: VIGENTE
stamp: VIGENTE - 2026-05-04
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

---

## Objetivo

Prevenir la acumulacion de archivos transitorios en la KB que inflan el conteo, consumen tokens del context window, y confunden al Arquitecto con contenido obsoleto.

## Definicion de efimero

Un archivo es efimero si cumple alguna de estas condiciones:
1. Su contenido queda completamente absorbido por otro archivo al consolidarse
2. Tiene fecha de expiracion implicita (sprint cerrado, sesion terminada)
3. Es un artefacto de proceso, no un dato o instruccion permanente

## Clasificacion y destino

| Tipo | Destino correcto | Persiste en KB? | Accion |
|------|-----------------|-----------------|--------|
| MANIFIESTO_APPEND_* | Consolidar en MANIFIESTO_CAMBIOS_v2, luego eliminar | NO | Consolidar al cierre de sesion |
| CHANGELOG_SESION_* | Google Drive MWT-KB-Archive/ | NO | Mover post-sesion |
| CHECKPOINT_SESSION_* | Google Drive MWT-KB-Archive/ | NO | Mover post-sesion |
| REPORTE_AUDITORIA_* | DASHBOARD_SNAPSHOT (actualizar seccion health) | NO | Absorber en DASHBOARD |
| apply_batch_*.sh | Ejecutar via Bash tool, luego descartar | NO | Eliminar post-ejecucion |
| GUIA_ALE_SPRINT* | Mantener solo sprint activo. Sprints DONE -> eliminar | Parcial | Purgar al marcar DONE |
| PROMPT_ANTIGRAVITY_SPRINT* | Igual que GUIA_ALE_* | Parcial | Purgar al marcar DONE |
| RESUMEN_SPRINT* | Google Drive MWT-KB-Archive/ | NO | Mover post-sesion |
| AUDIT_*_SPRINT* | DASHBOARD_SNAPSHOT o Drive | NO | Absorber o mover |
| SESION_* | Google Drive MWT-KB-Archive/ | NO | Mover post-sesion |
| DEC_* | Si es decision permanente -> ENT_GOB_DECISIONES. Si no -> eliminar | No como DEC_ | Absorber o eliminar |
| *.zip | Google Drive o repositorio git. Nunca en KB | NO | Mover o eliminar |
| LOTE_SM_SPRINT* DONE | Comprimir a <=50 lineas (ref -> POL_CONTEXT_BUDGET) | Si, comprimido | Comprimir post-DONE |

## Regla de header para transitorios (v1.1 - Regla 2 ejecutable)

Todo efimero que persista temporalmente DEBE declarar en su header los **3 campos canonicos**:

```yaml
type: TRANSITORIO                         # o EPHEMERAL - sinonimos
expires_at: 2026-MM-DD                    # FECHA CONCRETA, no "post-sprint" ni "fin-sesion"
consolidation_target: <archivo destino>   # ej: MANIFIESTO_CAMBIOS_v2.md
action_after_consolidation: DELETE | ARCHIVE
```

Sin los 3 campos, **no se acepta crear el archivo**. Esto es lo que fallo en los 42 `MANIFIESTO_APPEND_*` huerfanos detectados por AUDIT_REINDEXA 2026-05-03 (ninguno declaraba `expires_at` ni `consolidation_target`).

**Migracion:** archivos efimeros pre-existentes sin estos campos se completan en el siguiente touch (lazy migration). Archivos nuevos: gate de PR rechaza el merge si faltan.

## Ciclo de vida obligatorio (v1.2 - Regla del 0-dias ejecutable)

1. **Creacion:** Declarar como TRANSITORIO en header con `expires_at`, `consolidation_target`, `action_after_consolidation`.
2. **Uso:** El archivo cumple su funcion (guia ejecucion, contexto de sesion, etc.)
3. **Consolidacion o mover (Regla 5 - 0-dias):** **Al cierre de la sesion que lo creo** - no diferir a la siguiente sesion. El umbral historico de "7 dias sin consolidar" se reduce a **0 dias para sesiones nuevas** (sesion sin consolidacion = trabajo a medias).
4. **Eliminacion:** Confirmar que el contenido esta absorbido antes de borrar. Si ejecuta `git rm`, hacer reindex pgvector shadow primero.
5. **Anti-acumulacion (umbral >3):** Si hay >3 archivos del mismo tipo efimero en la KB, es senal de violacion.

**Excepcion transitoria:** los 42 MANIFIESTO_APPEND_* legacy detectados en AUDIT 2026-05-03 se purgan via PR-1+PR-2 del plan de remediacion. Despues de ese cleanup, el umbral 0-dias aplica sin excepcion.

## Umbral de alerta

Si la KB tiene >10 archivos efimeros acumulados, el Arquitecto debe escalar al CEO antes de continuar con trabajo nuevo.

## Enforcement

- **Deteccion:** DASHBOARD_SNAPSHOT health check lista archivos por tipo. Cualquier MANIFIESTO_APPEND_ >7 dias sin consolidar es violacion (umbral 0-dias para sesiones nuevas a partir de v1.1).
- **Accion:** Consolidar y eliminar en la sesion siguiente. No crear nuevos efimeros hasta resolver los pendientes.
- **Severidad:** MEDIUM - la acumulacion es gradual pero el impacto en context budget es acumulativo.

---

Changelog:
- v1.0 (2026-04-09): Creada. Formaliza reglas implicitas en CLAUDE.md (H8 auditoria ECC). Consolida lecciones aprendidas de depuracion 2026-04-01 (85 efimeros purgados) y 2026-04-09 (27 archivos adicionales).
- v1.1 (2026-05-03): +Regla 2 (header efimero ejecutable: 3 campos `type`+`expires_at`+`consolidation_target`+`action_after_consolidation`). +Regla 5 (sesion sin consolidacion = trabajo a medias, umbral 7 dias -> 0 dias para sesiones nuevas). Origen: AUDIT_REINDEXA_KB 2026-05-03 detecto 42 MANIFIESTO_APPEND_* huerfanos sin `expires_at`. Stamp renovado.
- v1.2 (2026-05-04): Resuelve colision semantica "Regla 5" detectada en audit retrieval golden-set 10q. Step 3 del ciclo ahora es el ancla canonica de "Regla 5 = 0-dias". Step 5 renombrado a "Anti-acumulacion (umbral >3)" para evitar dos definiciones con el mismo nombre. Sin cambio de enforcement, solo claridad nominal. ASCII puro.
