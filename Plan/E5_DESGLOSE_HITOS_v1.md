# E5 — Desglose de hitos FaberLoom

id: PLAN_E5_DESGLOSE_HITOS
version: 1.0.0
status: BORRADOR-EJECUTABLE
fuente: docs/faberloom/PLAN_DESARROLLO_FABERLOOM_ETAPA5_v1.md
base_revisada: main @ 066527f — e5fix19
autor: Fugu
fecha: 2026-07-13

> Etapa 5: Madurez operativa y primer cliente.  
> Este documento traduce el plan vigente E5 a tareas ejecutables por ola/hito.  
> Reglas no negociables: contract-first, Context tenant-scoped, AuditWriter con correlation_id,
> cookie HttpOnly `faberloom_at`, tenant canario permanente, HITL para envío/borrado,
> no injection por contenido, no fugas cross-workspace, no datos inventados sin fuente.

---

## 0. Estado base observado

### Git

- Rama: `main`
- HEAD: `066527f feat(chat): renderizar imagenes generadas + URL estable sin expiracion (e5fix19)`
- Commits recientes relevantes:
  - `497198a` e5fix18 — consultas JSON Postgres en autonomy
  - `71154dc` e5fix17 — timeout 180s imágenes sin reintentos
  - `1959073` e5fix16 — precios reales Moonshot/Kimi
  - `26bc639` e5fix15 — extracción PDF adjunto solo-texto
- Estado:
  - `AGENTS.md` modificado sin stage.
  - Untracked: planes E5–E10, backups smoke, `_to_delete/`, `pytest_full.log`.

### Módulos presentes

Backend `app/src/`:

- `foundation/`, `living_agent/`, `routing/`, `router/`, `connectors/`, `billing.py`, `key_broker.py`, `context.py`, `ambient_detectors.py`, `api.py`, `skills_router.py`, `golden_harvester.py`, `faberloom_catalog.py`.
- `living_agent/autonomy.py` contiene:
  - `evaluate_promotion_readiness`
  - `generate_promotion_token`
  - `promote_or_rollback_workspace`
  - `degrade_workspace_if_needed`
- `connectors/tax_authority.py` contiene:
  - `TaxConnectorConfig`
  - `TaxAuthorityConnector`
  - `get_tax_connector`
  - `build_tax_fetcher`
  - `set_tax_connector_secret`
  - `get_tax_connector_secret`
  - stubs sandbox/live todavía no implementados.
- `billing.py` contiene PDF manual con leyenda hardcodeada `DOCUMENTO NO FISCAL - BETA`.

Frontend `app/static/js/`:

- `app.jsx`
- `routing_shadow.jsx`
- `promotion_readiness.jsx`
- `health_dashboard.jsx`
- `tenant_settings.jsx`
- `tenant_admin.jsx`
- `agent_tasks.jsx`
- `foundation*.jsx`, `fnd_*.jsx`

Scripts `app/scripts/`:

- `backup_restore_smoke.py`
- `ingest_kb_h3.py`
- `migrate_minio_objects_to_tenant_prefix.py`
- `check_canary_isolation.py`
- `check_canary_isolation_postgres.py`
- `generate_olas_3_5_skills.py`

Docs clave existentes:

- `docs/audits/AUDIT_E4_CIERRE_20260711.md`
- `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md`
- `docs/ENT_PLAT_LLM_ROUTING.md`
- `docs/OPERACION_VPS_E3.md`
- `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.1.md`
- `docs/faberloom/PLB_FB_PROMOTION_READINESS_DOGFOOD_v1.md`
- `docs/faberloom/PLB_FB_TENANT_ONBOARDING_v1.md`
- `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`
- `docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v2.md`

Nota graphify:

- `graphify-out/GRAPH_REPORT.md` existe.
- El grafo fue construido desde commit `a13f02f7`, por lo que está stale contra HEAD `066527f`.
- Después de modificar código debe ejecutarse `graphify update .`.

---

# 1. Orden recomendado de ejecución

## Orden macro

1. **Ola 1 / E5-0** — consolidar E4 en `main`, docs, deploy, suite.
2. **Ola 1 / E5-2** — seguridad operativa ejecutada: detector backup freshness + rotación VPS + MinIO + cron.
3. **Día 1 paralelo humano**:
   - CEO inicia compra del certificado ATV CR.
   - CEO selecciona design partner #1 y agenda.
4. **Ola 2 / E5-1** — operación shadow→natural en MWT.
5. **Ola 2 / E5-3** — carga KB H3 + catálogo v1.2 sin huecos.
6. **Ola 3 / E5-4** — ATV Costa Rica sandbox/live end-to-end.
7. **Ola 3 / E5-5** — PACK 1 y PACK 3 a ACTIVE por uso real.
8. **Ola 4 / E5-6** — design partner, onboarding, soak 30 días y primera factura pagada.

## Justificación

- E5-0 bloquea todo: deploy siempre desde `main`.
- Certificado ATV y design partner tienen lead time humano: iniciar día 1 aunque su implementación ocurra en olas posteriores.
- E5-1 requiere reloj operativo: shadow por semanas, no solo código.
- E5-4 alimenta E5-5: factura real → golden cases reales.
- E5-6 es gate de salida: mínimo 30 días de soak.

---

# 2. Mapa por ola

| Ola | Hitos | Naturaleza | Resultado esperado |
|---|---|---|---|
| 1 | E5-0, E5-2 | Código + Ops | Main estable, docs E4 cerradas, seguridad operativa evidenciada |
| 2 | E5-1, E5-3 | Operación instrumentada | Routing natural progresivo y KB/catálogo sin huecos |
| 3 | E5-4, E5-5 | Código + compra + dogfood | ATV live y packs core ACTIVE |
| 4 | E5-6 | Comercial instrumentado | Primer cliente externo con soak + factura pagada |

---

# 3. Hitos detallados

---

## E5-0 — Consolidación de E4

### Objetivo

Producción corre desde `main`; documentación E4 queda al estándar E3; el curador no perdió capacidades.

### Dependencias

- Ninguna.
- Bloquea E5-1, E5-2, E5-3, E5-4, E5-5, E5-6.

### Tareas secuenciales

- [ ] Revisar `git status`.
- [ ] Decidir qué hacer con:
  - `AGENTS.md` modificado.
  - `_to_delete/`.
  - `pytest_full.log`.
  - `docs/audits/BACKUP_SMOKE_*.md`.
  - planes E5–E10 untracked.
- [ ] Confirmar integración E4→main o hacer merge de `e4-agente-vivo` si aún aplica.
- [ ] Crear tag `e4-cierre-20260712`.
- [ ] Correr suite completa:
  - `cd app && python -m pytest -q`
  - Esperado del plan: 724 passed / 0 failed.
- [ ] Redeploy VPS desde `main`.
- [ ] Smoke:
  - `/api/health` con schema 48.
  - login.
  - chat general.
  - brief.
  - shadow-report.
- [ ] Reescribir auditoría E4 al formato E3.
- [ ] Completar arquitectura as-built del living agent.
- [ ] Actualizar routing doc con `routing.mode`.
- [ ] Hacer auditoría de capacidades del curador con CEO en vista Skills.
- [ ] Si falta alguna acción de fábrica, restaurarla dentro de Skills, no como rail item nuevo.

### Archivos a modificar

- `docs/audits/AUDIT_E4_CIERRE_20260711.md`
  - Formato E3: semáforo por hito, evidencia archivo/función, tabla de tests, desviaciones, fixes producción.
- `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md`
  - Módulos reales `living_agent/`.
  - Flujo pregunta-general, profundización, task multi-paso.
  - Mapeo Autonomy Ladder.
  - Tablas v42–48.
- `docs/ENT_PLAT_LLM_ROUTING.md`
  - `routing.mode = manual | shadow | natural`.
  - Deprecación `FABERLOOM_AUTO_MODE_ENABLED`.
  - Changelog.
- `app/static/js/app.jsx`
  - Solo si falta acceso a importar catálogo, compilar, golden cases, `promote_pack`, kill switch.
- Posible `.gitignore`
  - Para `pytest_full.log`, `_to_delete/`, etc.

### Archivos a crear

- `docs/audits/SMOKE_DEPLOY_E5_0_<fecha>.md`

### Tests

- Suite completa.
- Si se toca frontend Skills, añadir/actualizar test de presencia de acciones del curador.

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Suite rota antes de deploy | No deployar si pytest no está verde |
| Acción del curador inaccesible | Checklist CEO + fix dentro de Skills |
| Grafo stale | `graphify update .` tras cambios |

### DoD

- [x] Producción corre desde `main` (commit `462d299`, VPS healthy).
- [x] Tag `e4-cierre-20260712` apunta a `6d15f97`.
- [x] Suite 0 failed (728 passed / 12 skipped / 0 failed / 33 warnings).
- [x] `/api/health` schema 48 verde.
- [x] Docs E4 al estándar E3 (`docs/audits/AUDIT_E4_CIERRE_20260711.md`).
- [x] Veredicto curador registrado (`docs/audits/AUDIT_E5_0_CURATOR_CAPABILITY_REVIEW_20260713.md` — firma humana pendiente).

---

## E5-2 — Seguridad operativa ejecutada

### Objetivo

Cerrar deudas operativas E3 con evidencia: rotación VPS, MinIO tenant-prefix, cron real de backup smoke + detector.

### Dependencias

- E5-0.

### Tareas secuenciales

#### Código

- [x] Crear `app/scripts/check_backup_smoke_freshness.py`.
- [x] Añadir detector `stale_backup_smoke` en `app/src/ambient_detectors.py`.
- [x] Registrar detector en `DETECTOR_REGISTRY`.
- [x] Crear tests `test_e5_2_backup_freshness_detector.py`.
- [x] Ignorar reportes `BACKUP_SMOKE_*.md` generados en `.gitignore`.

#### Operación

- [ ] Ejecutar `docs/OPERACION_VPS_E3.md`.
- [ ] Rotar password root.
- [ ] Configurar SSH solo llaves: `PasswordAuthentication no`.
- [ ] Rotar claves correo compartidas.
- [ ] Verificar `.env` fuera de git.
- [ ] Ejecutar migración MinIO:
  - backup verificado.
  - dry-run.
  - revisar conteos.
  - ejecución real.
  - verificar origen=destino.
  - smoke lectura 10 objetos.
- [ ] Formalizar cron nocturno de backup smoke.
- [ ] Alerta si smoke falla o último reporte >48h.
- [ ] Añadir protocolo trimestral en `docs/ENT_GOB_PROTOCOLOS.md`.

### Archivos a crear

- `app/scripts/check_backup_smoke_freshness.py`
  - `check_freshness(...) -> dict`
  - CLI `--max-age-hours 48`
  - CLI `--json`
  - exit code no-cero si stale.
- `app/tests/test_e5_2_backup_freshness_detector.py`
  - stale → finding.
  - fresh → no finding.
  - read-only → DB no cambia.
- `docs/audits/EVIDENCIA_ROTACION_<fecha>.md`
- `docs/audits/EVIDENCIA_MINIO_MIGRACION_<fecha>.md`

### Archivos a modificar

- `app/src/ambient_detectors.py`
  - `detect_stale_backup_smoke(ctx, conn)`.
  - `DETECTOR_REGISTRY["stale_backup_smoke"]`.
- `docs/ENT_GOB_PROTOCOLOS.md`
  - Cadencia trimestral + responsable.

### Código esperado

En `ambient_detectors.py`:

- Usar `Context`.
- Usar patrón `AmbientFinding`.
- Detector read-only.
- Fail-closed si no hay tenant/workspace scoping.
- No escribir WorkLoom directamente; solo devolver findings.

En `check_backup_smoke_freshness.py`:

- Leer último `BACKUP_SMOKE_*.md` o fuente formal equivalente.
- Calcular edad.
- Devolver JSON:
  - `fresh`
  - `last_smoke_at`
  - `age_hours`
  - `threshold_hours`

### Tests

- `test_detector_propone_item_si_stale`
- `test_detector_no_propone_si_fresco`
- `test_detector_es_read_only`
- `test_cli_exit_code_stale`

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| MinIO cross-tenant leak | dry-run + conteos + smoke 10 objetos |
| Detector escribe estado | test read-only obligatorio |
| Secretos en evidencia | huellas, fechas y comandos, nunca secretos |

### DoD

- [ ] Evidencia rotación commiteada.
- [ ] Evidencia MinIO commiteada.
- [ ] Cron backup smoke corriendo.
- [x] Detector verde.
- [x] Test E5-2 verde.
- [x] Script `check_backup_smoke_freshness.py` verde.

---

## E5-1 — Operación shadow→natural

### Objetivo

El routing natural toma control real en dogfood MWT, gobernado por ACE y datos.

### Dependencias

- E5-0.
- No tocar design partner hasta que MWT acumule 2 semanas estables.

### Tareas secuenciales

- [ ] Encender `routing.mode="shadow"` en todos los workspaces activos MWT.
- [ ] Rutina semanal lunes: revisar "Routing en sombra".
- [ ] Curador marca decisiones absurdas con feedback tipificado.
- [ ] Cuando haya:
  - ≥2 semanas o ≥50 decisiones.
  - ahorro proyectado ≥0.
  - 0 absurdas.
  promover workspace de mayor volumen a `natural`.
- [ ] Usar `generate_promotion_token(workspace_id, "promote-shadow")`.
- [ ] Usar `promote_or_rollback_workspace(...)`.
- [ ] Observar 1 semana.
- [ ] Confirmar que `degrade_workspace_if_needed(...)` no dispara.
- [ ] Promover 2 workspaces adicionales.
- [ ] Ejecutar rollback REAL:
  - token `rollback-natural`.
  - workspace vuelve a shadow.
  - audit event registrado.
- [ ] Registrar evidencia quincenal.

### Archivos a crear

- `docs/audits/OPERACION_E5_ROUTING_<fecha>.md`

### Archivos a modificar

Solo si la operación revela fricción:

- `app/static/js/routing_shadow.jsx`
- `app/static/js/promotion_readiness.jsx`
- `app/src/api.py`

### Código esperado si hay fricción

- Filtros por workspace/fecha.
- Columna de costo estimado vs real.
- Columna decisión absurda / feedback.
- Endpoints read-only con `Context(workspace_id, tenant_id, user_id)`.

### Tests

Solo si hay cambios:

- Actualizar `test_e2_4_routing_policy.py`.
- Actualizar `test_e4_2_shadow_planner.py`.
- Añadir test tenant-scoped para endpoint nuevo.

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Natural degrada producción | ACE degrada solo + rollback ejercitado |
| Promoción sin humano | Token obligatorio, nunca auto-promote |
| Se toca design partner muy pronto | DA5-4: MWT 2 semanas estable primero |

### DoD

- [ ] ≥3 workspaces MWT en `natural`.
- [ ] Estables ≥2 semanas.
- [ ] 1 rollback real ejercitado.
- [ ] Ahorro real documentado.

---

## E5-3 — KB H3 cargada y catálogo sin huecos

### Objetivo

Cargar conocimiento Marluvas/Tecmater y resolver todos los `DEFINITION_PENDING`.

### Dependencias

- E5-0.
- CEO entrega archivos H3.

### Tareas secuenciales

- [ ] CEO entrega archivos Marluvas/Tecmater.
- [ ] Ejecutar dry-run:
  - `python app/scripts/ingest_kb_h3.py --tenant-id <mwt> --workspace-id <ws> --source-dir <dir>`
- [ ] Revisar reporte.
- [ ] Ejecutar real:
  - `--execute --approved-by <user_id>`
- [ ] Verificar 10 citas al azar dev+AM.
- [ ] Documentar evidencia KB H3.
- [ ] Hacer 2–3 sesiones CEO+Arquitecto para needs-list.
- [ ] Crear `ENT_FB_SKILL_CATALOG_v1.2.md`.
- [ ] Para cada skill:
  - definido ahora → manifest v2 completo, SHADOW.
  - pospuesto → razón + fecha.
  - descartado → razón.
- [ ] Materializar definidos con pipeline E3-4:
  - compiler v2.
  - SHADOW.
  - golden placeholders honestos.
- [ ] Proponer ≥3 golden candidates PACK 2 desde runs reales.

### Archivos a crear

- `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.2.md`
- `docs/audits/EVIDENCIA_KB_H3_<fecha>.md`
- `app/tests/test_e5_3_catalog_v12.py`

### Archivos a modificar

- Catálogo/manifests de skills según pipeline existente.
- Posiblemente `app/src/faberloom_catalog.py` o assets de catálogo, si allí viven los manifests.
- No modificar `ingest_kb_h3.py` salvo bug.

### Código esperado

Test `test_e5_3_catalog_v12.py`:

- Todo skill tiene estado terminal o pospuesto con razón+fecha.
- Nuevos skills compilan.
- Ningún nuevo skill queda ACTIVE.
- Ningún nuevo skill tiene `auto_apply`.
- Ningún campo fuente queda sin `source_version`/`approved_by`.

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| CEO no entrega H3 | PACK 2 queda pospuesto-con-razón; E5 puede cerrar |
| Dato inventado | Verificación de 10 citas |
| Golden fabricado | Solo desde runs reales con harvester |

### DoD

- [ ] KB H3 cargada.
- [ ] 10 citas verificadas.
- [ ] Catálogo v1.2 sin huecos.
- [ ] PACK 2 con ≥3 golden candidates reales.
- [ ] Test E5-3 verde.

---

## E5-4 — Tributario live: ATV Costa Rica

### Objetivo

Emitir primera factura electrónica real aceptada por ATV Costa Rica.

### Dependencias

- E5-0.
- Certificado HE2-9 comprado e instalado.
- Timebox de verificación ATV 3 días.

### Tareas secuenciales

- [ ] Dev+AM ejecutan `PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1` para ATV.
- [ ] Registrar URLs oficiales, credenciales sandbox, hallazgos.
- [ ] SAT/DIAN: documentar solo hallazgo, no activar.
- [ ] CEO compra certificado de firma MWT.
- [ ] Guardar certificado en `TenantSecretStore`:
  - namespace `connectors/tax/atv/cert`.
- [ ] Configurar `connectors.tax.atv.*` en tenant settings MWT.
- [ ] Implementar conector sandbox/live ATV.
- [ ] Probar con `SKILL_FE_STATUS_CHECK` y `SKILL_FE_*` PACK 1.
- [ ] Cambiar `mode=sandbox` → `mode=live`.
- [ ] Derivar `has_tax_certificate`.
- [ ] Ajustar PDF para no mostrar "NO FISCAL" si tenant tiene certificado.
- [ ] Emitir factura real MWT.
- [ ] Verificar aceptación ATV.
- [ ] Documentar evidencia.

### Archivos a modificar

- `app/src/connectors/tax_authority.py`
  - `_live_document_status`
  - `_live_taxpayer_info`
  - validación config ATV.
  - `_require_certificate` fail-closed.
- `app/src/billing.py`
  - `_render_invoice_pdf(...)`
  - derivación `has_tax_certificate`
  - sello no-fiscal condicional.
- Tenant settings vía API.

### Archivos a crear

- `app/tests/test_e5_4_atv_sandbox_contract.py`
- `app/tests/test_e5_4_pdf_fiscal_flag.py`
- `app/tests/fixtures/atv_cassettes/*.json`
- `docs/audits/EVIDENCIA_EFACTURA_ATV_<fecha>.md`

### Código esperado

En `tax_authority.py`:

- Soportar `mode=mock|sandbox|live`.
- Si `sandbox/live` sin URL o certificado requerido → error fail-closed.
- No inventar URLs: solo pasar de `[PENDIENTE — NO INVENTAR]` a datos verificados.
- Cassettes anonimizados.

En `billing.py`:

- Sin certificado → conserva `DOCUMENTO NO FISCAL - BETA`.
- Con certificado ATV configurado → PDF fiscal sin esa leyenda.

### Tests

- Sandbox contract con fixtures reales anonimizadas.
- PDF fiscal flag:
  - tenant sin cert → contiene `NO FISCAL`.
  - tenant con cert → no contiene `NO FISCAL`.

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Certificado tarda semanas | Comprar día 1 |
| Secreto en git | Solo TenantSecretStore |
| URLs inventadas | Mantener PENDIENTE hasta verificación |
| Envío sin HITL | Doble confirmación obligatoria |

### DoD

- [ ] Factura MWT aceptada por ATV live.
- [ ] Evidencia sin datos sensibles.
- [ ] SAT/DIAN documentados, no activados.
- [ ] Tests E5-4 verdes.

---

## E5-5 — PACK 1 y PACK 3 a ACTIVE

### Objetivo

PACK 1 y PACK 3 cruzan umbral de promoción por uso real.

### Dependencias

- E5-4 para facturas reales y fiscalidad real.

### Tareas secuenciales

- [ ] Rutina dogfood semanal.
- [ ] Correr PACK 1 con ATV real.
- [ ] Correr PACK 3 sobre facturas reales MWT.
- [ ] Harvester propone golden cases desde runs reales.
- [ ] Curador aprueba.
- [ ] Segundo gate: `verified_by != approved_by`.
- [ ] Meta por pack:
  - ≥3 golden approved+verified.
  - ≥100 runs.
  - ≥90% acceptance.
- [ ] Promover PACK 1 primero con `promote_pack`.
- [ ] Promover PACK 3 después.
- [ ] Si no hay 100 runs en 3 semanas: ampliar uso real, no bajar umbral.

### Archivos a crear

- `docs/audits/OPERACION_E5_PACKS_<fecha>.md`

### Archivos a modificar

- Ninguno esperado.

### Tests

No nuevos salvo bug. Suite existente:

- `test_e3_4_pack_readiness.py`
- `test_e3_4_pack1_fe.py`
- `test_e3_4_pack3_cobranza.py`

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Dogfood no alcanza 100 runs | Ampliar uso real |
| Golden fabricado | Solo harvester + runs reales |
| Promoción sin calidad | No bajar umbrales |

### DoD

- [ ] PACK 1 ACTIVE.
- [ ] PACK 3 ACTIVE.
- [ ] Evidencia readiness verde.
- [ ] Cero golden fabricado.

---

## E5-6 — Design partner, soak 30 días y factura pagada

### Objetivo

Tenant externo real activo ≥30 días, sin fugas, con primera factura pagada y conciliada.

### Dependencias

- E5-1: MWT natural estable antes de partner.
- E5-4: si partner es CR y se requiere e-factura.
- Soak 30 días.

### Tareas secuenciales

- [ ] CEO elige candidato #1 de `ENT_FB_VERTICAL_CANDIDATES_v2`.
- [ ] Backup candidato #2 si #1 no firma en 21 días.
- [ ] Crear plantilla acuerdo de datos beta.
- [ ] Revisión legal humana.
- [ ] Firmar acuerdo.
- [ ] Ejecutar `PLB_FB_TENANT_ONBOARDING_v1`:
  - aprobación manual.
  - bootstrap tenant.
  - identidad del agente.
  - KB inicial.
  - workspaces.
  - usuarios.
- [ ] Crear `soak_report.py`.
- [ ] Generar reportes semanales S1–S4.
- [ ] Criterios:
  - ≥10 casos reales.
  - 0 fugas.
  - canarios verdes 4 semanas.
  - disponibilidad sin P0.
- [ ] Día 30+: emitir factura.
- [ ] Registrar pago por transferencia.
- [ ] Conciliar con PACK 3.
- [ ] Usar conciliación como golden definitivo si aplica.

### Archivos a crear

- `docs/faberloom/SCH_FB_ACUERDO_DATOS_BETA_v1.md`
- `app/scripts/soak_report.py`
- `app/tests/test_e5_6_soak_report.py`
- `docs/audits/SOAK_<tenant>_S1.md`
- `docs/audits/SOAK_<tenant>_S2.md`
- `docs/audits/SOAK_<tenant>_S3.md`
- `docs/audits/SOAK_<tenant>_S4.md`
- `docs/audits/ACTA_ETAPA5_<fecha>.md`

### Archivos a modificar

- Ninguno esperado para soak si se implementa como script read-only.
- Posible doc onboarding si operación revela gaps.

### Código esperado

`soak_report.py`:

- CLI:
  - `--tenant-id`
  - `--week`
  - `--out docs/audits`
  - `--json`
- Funciones:
  - `build_soak_report(ctx, conn, week) -> dict`
  - `render_markdown(report) -> str`
- Agregados:
  - health tenant.
  - casos procesados.
  - HITL aprobados/rechazados.
  - costo.
  - incidentes.
  - canarios contaminación.
- Reglas:
  - read-only.
  - solo agregados, no contenido.
  - `Context(workspace_id, tenant_id, user_id)`.
  - `enforce_tenant_scoped(ctx)` en queries críticas.
  - fail-closed si falta tenant.

`SCH_FB_ACUERDO_DATOS_BETA_v1.md`:

- Alcance de datos.
- Visibilidad y sellado.
- Explicación key broker en lenguaje de negocio.
- No entrenamiento con datos del cliente.
- SLA beta con referencia a `PLB_FB_SOPORTE_SLA_BETA_v1`.
- Beta 90 días.
- Terminación.
- Exportación de datos.
- Campo explícito `[PENDIENTE — decisión CEO]` para términos económicos.
- Revisión legal humana obligatoria.

### Tests

`test_e5_6_soak_report.py`:

- Agregados correctos.
- No incluye contenido sensible.
- Aislamiento tenant.
- Falla cerrado sin tenant.
- Canarios verdes/rojos reflejados correctamente.

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Partner #1 no firma | Backup #2 a los 21 días |
| Fuga tenant externo | Canarios semanales; fuga = P0; soak reinicia |
| Reporte filtra contenido | Solo agregados + test |
| Factura no pagada | Gate no cierra hasta pago conciliado |

### DoD

- [ ] Tenant externo activo ≥30 días.
- [ ] ≥10 casos reales.
- [ ] 0 fugas.
- [ ] 4 reportes soak.
- [ ] Acuerdo firmado archivado.
- [ ] Primera factura pagada.
- [ ] Pago conciliado con PACK 3.

---

# 4. Gate de salida E5

E5 cierra solo si:

- [ ] E5-6 DoD completo.
- [ ] ≥3 workspaces MWT en `natural` estables.
- [ ] PACK 1 ACTIVE.
- [ ] PACK 3 ACTIVE o cierre autorizado una semana después si la conciliación de la primera factura es su caso 100.
- [ ] Evidencias E5-2 commiteadas:
  - rotación.
  - MinIO.
  - cron backup smoke.
- [ ] `docs/audits/ACTA_ETAPA5_<fecha>.md` en formato estándar.

---

# 5. Bloqueantes potenciales

| Bloqueante | Hito | Dueño | Mitigación |
|---|---|---|---|
| Certificado ATV demora | E5-4 | CEO | Compra día 1 |
| Design partner no firma | E5-6 | CEO | Candidato #2 a 21 días |
| KB H3 no llega | E5-3 | CEO | Pospuesto-con-razón; no bloquea gate |
| MinIO cross-tenant | E5-2 | Ops/Kimi | dry-run + conteos + smoke 10 objetos |
| Natural degrada | E5-1 | ACE/Kimi | rollback real + ACE auto-degrade |
| Dogfood no alcanza 100 runs | E5-5 | Curador/AM | ampliar uso, no bajar umbral |
| Fuga en tenant externo | E5-6 | Kimi/Ops | canarios; P0; reiniciar soak |
| Entorno sin escritura/red | Todos | Kimi | usar entorno writable para código/deploy |

---

# 6. Primer bloque de trabajo recomendado para Kimi

## Paso 1 — guardar este plan

Crear:

`Plan/E5_DESGLOSE_HITOS_v1.md`

## Paso 2 — preparar E5-0

- Resolver `git status`.
- Confirmar qué untracked se versiona.
- Correr suite completa.
- Actualizar docs E4:
  - `docs/audits/AUDIT_E4_CIERRE_20260711.md`
  - `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md`
  - `docs/ENT_PLAT_LLM_ROUTING.md`

## Paso 3 — iniciar acciones humanas día 1

Pedir al CEO:

- iniciar compra certificado ATV.
- elegir design partner #1.
- agendar auditoría de capacidades del curador.
```

---

## Resumen final para Kimi

- **Dónde quedó el plan:** no pude escribirlo físicamente por sandbox read-only. Debes guardar el bloque anterior en `Plan/E5_DESGLOSE_HITOS_v1.md`.
- **Primer hito/ola a desarrollar:** **Ola 1 / E5-0**. Primero consolidar `main`, suite, docs E4 y smoke VPS. En paralelo, pedir al CEO iniciar certificado ATV y selección de design partner.
- **3 riesgos principales:**
  1. **Certificado ATV** demora semanas → comprar día 1.
  2. **Fuga cross-tenant en MinIO/tenant externo** → dry-run, canarios y tests fail-closed.
  3. **Design partner o dogfood no generan volumen** → candidato #2 a 21 días y ampliar uso real, nunca bajar umbrales.
