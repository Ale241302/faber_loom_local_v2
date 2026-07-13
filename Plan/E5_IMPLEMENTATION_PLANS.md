# E5 — Planes de implementación detallados (E5-1, E5-3, E5-4, E5-5, E5-6)

id: PLAN_E5_IMPLEMENTATION_PLANS
version: 1.0.0
status: BORRADOR-EJECUTABLE
fuente: docs/faberloom/PLAN_DESARROLLO_FABERLOOM_ETAPA5_v1.md
base_revisada: main @ 066527f (e5fix19); grafo graphify stale (a13f02f7) — correr `graphify update .` tras cambios
autor: Fugu
fecha: 2026-07-13

> Este documento NO contiene código. Es el plan de implementación por hito:
> objetivo, archivos a crear/modificar, cambios específicos de código (con nombres de
> función, firmas y SQL previstos), tests a escribir y criterios de DoD.
>
> Costuras no negociables aplicables a todo el documento:
> - `Context(workspace_id, tenant_id, user_id)` en toda query; `enforce_tenant_scoped(ctx)` en helpers críticos (fail-closed).
> - `AuditWriter` con `correlation_id` en toda mutación / evento.
> - Cookie HttpOnly `faberloom_at` + `GET /api/me`; nunca leer JWT de `localStorage`.
> - HITL (doble confirmación con token) para envío/borrado y para promociones.
> - Sin injection por contenido; sin fuga cross-workspace; sin dato inventado sin fuente en KB.
> - Campos latentes contract-first: `tenant_id`, `actor_id`, `actor_role_at_decision`,
>   `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`, `verified_by`.
> - Segundo gate gold: `verified_by != approved_by`.

---

## Índice

| Hito | Naturaleza | Código nuevo esperado |
|---|---|---|
| E5-1 | Operación instrumentada + código menor de tablero | Bajo (≤1 sesión, condicional a fricción) |
| E5-3 | Carga KB + gobierno de catálogo | Bajo-medio (test de invariantes + materialización pipeline existente) |
| E5-4 | Código de conector tributario live | Medio-alto (conector ATV real + PDF fiscal condicional) |
| E5-5 | Operación dogfood + promoción | Cero (todo existe; solo evidencia) |
| E5-6 | Comercial instrumentado + script soak | Medio (soak_report.py + acuerdo de datos) |

---

# E5-1 — Operación shadow→natural (routing natural gobernado por datos)

## Objetivo

Que el routing natural tome control real en los workspaces del tenant dogfood MWT,
gobernado por el ACE (Autonomy Control Engine) y por datos del shadow report, con
un rollback real ejercitado. La meta: ≥3 workspaces MWT en `natural` estables ≥2
semanas, 1 rollback ejercitado, ahorro real medido y documentado.

Es un hito **operacional** (≈4 semanas de reloj); el código está construido
(`living_agent/autonomy.py`). El presupuesto de código es ≤1 sesión y **condicional**
a que la operación revele fricción en el tablero.

## Estado del código base (ya existe, no reimplementar)

`app/src/living_agent/autonomy.py`:
- `generate_promotion_token(workspace_id, action) -> str` (acciones `promote-shadow`, `rollback-natural`).
- `evaluate_promotion_readiness(ctx, conn, workspace_id, *, days, min_decisions) -> dict`
  — gates: `shadow_decisions >= min_decisions`, `projected_savings_usd >= 0`,
  `absurd_decisions == 0`, no cooldown tras doble degradación.
- `promote_or_rollback_workspace(ctx, conn, workspace_id, *, requested_mode, confirmation_token)`
  — token constant-time + readiness (solo en promoción); audita
  `workspace.routing.promoted` / `workspace.routing.rollback`.
- `degrade_workspace_if_needed(ctx, conn, workspace_id, ...)` — auto-degrade a `shadow`
  si `actual_cost > estimated_cost * overrun_ratio`; audita `living_agent.routing.degraded`.

Frontend existente: `routing_shadow.jsx`, `promotion_readiness.jsx`, `health_dashboard.jsx`.

## Archivos a crear

- `docs/audits/OPERACION_E5_ROUTING_<fecha>.md` (evidencia quincenal): números del shadow
  report (decisiones, ahorro proyectado, absurdas), promociones (workspace, token usado,
  `audit_event_id`), degradaciones/rollback, y la curva de estabilidad por semana.

## Archivos a modificar (SOLO si la operación revela fricción; presupuesto ≤1 sesión)

- `app/static/js/routing_shadow.jsx` — filtros que falten (por workspace / rango de fechas),
  columna "costo estimado vs real", columna/acción "decisión absurda" con el feedback tipificado.
- `app/static/js/promotion_readiness.jsx` — exponer el desglose de `evaluate_promotion_readiness`
  (decisiones, ahorro, absurdas, cooldown) para que el curador decida con datos.
- `app/src/api.py` — solo si falta un endpoint read-only de listado/filtrado del shadow log.

## Cambios específicos de código (condicionales)

1. **Endpoint de shadow log filtrable (si falta):** en `api.py`, un `GET` read-only que
   acepte `workspace_id`, `from`, `to`, `mode`, y devuelva agregados de `planner_decision_log`.
   - Debe construir `Context` desde la request (`context_from_request`), llamar
     `enforce_tenant_scoped(ctx)` y filtrar por `tenant_id`/`workspace_id`. Nunca cruzar tenant.
   - Solo agregados/decisiones del propio tenant; sin contenido sensible del plan.
2. **Columna costo estimado vs real:** derivar de `plan_json.est_total_cost_usd` y
   `actual_outcome_json.cost_usd` (mismo origen que `evaluate_promotion_readiness`). No recalcular
   umbrales en el front; consumir el dict del backend.
3. **Marca de "decisión absurda":** reusar el feedback tipificado existente (no crear tabla nueva);
   el curador marca desde el tablero y el evento se audita con `correlation_id`.
4. **No** añadir auto-promote. La promoción SIEMPRE pasa por
   `generate_promotion_token` + `promote_or_rollback_workspace` (HITL con token).

## Procedimiento operativo (no-código, parte del DoD)

1. Encender `routing.mode="shadow"` en todos los workspaces activos de MWT vía la API de
   settings (`routing.mode` está en `_SETTING_REGISTRY`).
2. Rutina semanal (lunes): revisar "Routing en sombra"; marcar absurdas.
3. Al umbral (≥2 semanas o ≥50 decisiones, ahorro ≥0, 0 absurdas): promover el workspace de mayor
   volumen con `generate_promotion_token(ws, "promote-shadow")` → `promote_or_rollback_workspace(..., requested_mode="natural", confirmation_token=...)`.
4. Observar 1 semana; verificar que `degrade_workspace_if_needed` no dispara; promover 2 más.
5. **Rollback REAL:** degradar manualmente un workspace promovido con token `rollback-natural`
   → `promote_or_rollback_workspace(..., requested_mode="shadow", ...)`; confirmar en auditoría el
   evento `workspace.routing.rollback` y que no hubo pérdida.

## Tests

Solo si se toca código. En ese caso:
- Actualizar `app/tests/test_e2_4_routing_policy.py` y `app/tests/test_e4_2_shadow_planner.py`
  para no romper con cambios del tablero/endpoint.
- Test nuevo para el endpoint read-only del shadow log:
  - `test_shadow_log_endpoint_tenant_scoped` — un tenant no ve decisiones de otro (fail-closed).
  - `test_shadow_log_endpoint_read_only` — el `GET` no muta `planner_decision_log`.
  - `test_shadow_log_filters` — filtros por workspace/fecha devuelven el subconjunto correcto.
- Reutilizar el patrón de fixture `client(tmp_path, monkeypatch)` con `TestClient(create_app())`
  y helpers `_auth_headers` / `_demo_workspace_id` (ver `test_e3_4_tax_connectors.py`).

## DoD

- [ ] ≥3 workspaces MWT en `natural`, estables ≥2 semanas (sin auto-degrade en la ventana).
- [ ] 1 rollback real ejercitado y auditado (`workspace.routing.rollback`).
- [ ] Ahorro real medido y documentado en `docs/audits/OPERACION_E5_ROUTING_<fecha>.md`.
- [ ] Si hubo código: suite verde (incl. tests del tablero/endpoint) y `graphify update .` corrido.
- [ ] Ninguna promoción sin token (verificado en auditoría).

---

# E5-3 — KB H3 cargada y catálogo sin huecos de definición

## Objetivo

Cargar el conocimiento real Marluvas/Tecmater (H3) al sistema con citas verificadas, y
resolver la needs-list del catálogo v1.1 de modo que **ningún** skill quede en un hueco:
cada skill tiene estado terminal, o "pospuesto con razón + fecha" (que es un veredicto).
Salida: `ENT_FB_SKILL_CATALOG_v1.2.md`. Con H3 cargada, desbloquear ≥3 golden candidates
reales de PACK 2 (comex) vía el harvester.

## Estado del código base (ya existe, no reimplementar)

- `app/scripts/ingest_kb_h3.py` — CLI: `--tenant-id`, `--workspace-id`, `--source-dir`,
  `--execute`, `--approved-by`, `--db-path` (o `FABERLOOM_DB_PATH`). Dry-run por defecto.
- `app/src/golden_harvester.py` — `propose_golden_case_from_run`, `list_golden_cases`,
  `approve_golden_case`, `verify_golden_case` (segundo gate `verified_by != approved_by`).
- `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.1.md` — 13 legacy skills (11 MIGRADO-SHADOW, 2 DEPRECATED).
- Pipeline de materialización de skills (compiler v2, estado SHADOW): usado en olas 3-5 de E3-4
  (`app/scripts/generate_olas_3_5_skills.py`, `app/src/faberloom_catalog.py`, `skill_catalog.py`).

## Archivos a crear

- `docs/faberloom/ENT_FB_SKILL_CATALOG_v1.2.md` — reemplaza v1.1 con changelog; una fila por skill
  con veredicto explícito: `DEFINIDO-SHADOW` (manifest v2 completo), `POSPUESTO` (razón + fecha),
  o `DESCARTADO` (razón). Cero `DEFINITION_PENDING` sin veredicto.
- `docs/audits/EVIDENCIA_KB_H3_<fecha>.md` — reporte de carga (conteos por fuente) + verificación
  de 10 citas al azar (dev+AM): para cada cita, ¿el chunk citado dice lo que la respuesta afirma?
- `app/tests/test_e5_3_catalog_v12.py` — invariantes del catálogo (ver Tests).

## Archivos a modificar

- Manifests/assets de skills del catálogo, según pipeline existente, para los skills `DEFINIDO-SHADOW`
  (manifest v2 con `metadata.fbl`, `budget.kill_switch.enabled=true`, `learning_consolidation.auto_apply=false`,
  outputs externos con `requires_human_approval: true`, golden `[PENDIENTE — NO INVENTAR]` honestos).
- Posiblemente `app/src/faberloom_catalog.py` / `app/src/skill_catalog.py` si los manifests viven ahí.
- **NO** modificar `ingest_kb_h3.py` salvo bug (documentar el bug si aparece).

## Cambios específicos de código

1. **Carga H3 (operación con el CLI existente):**
   - Dry-run: `python app/scripts/ingest_kb_h3.py --tenant-id <mwt> --workspace-id <ws> --source-dir <dir>`.
   - Revisar reporte de conteos → ejecución real: añadir `--execute --approved-by <user_id>`.
   - Los chunks cargados deben portar `source_version` y `approved_by` (campos latentes); verificar
     que el script los sella (si no, es bug bloqueante — documentar, no inventar).
2. **Materialización de los `DEFINIDO-SHADOW`:** correr el pipeline E3-4 (compiler v2) por skill;
   todos entran en estado SHADOW, ninguno ACTIVE, ninguno con `auto_apply=true`.
3. **Golden candidates PACK 2 (comex):** con H3 cargada, correr los skills de PACK 2 sobre runs
   reales y usar `propose_golden_case_from_run` (harvester) para proponer ≥3 candidatos. **Prohibido**
   fabricar golden; solo desde runs reales.

## Tests — `app/tests/test_e5_3_catalog_v12.py`

Parsear/consumir `ENT_FB_SKILL_CATALOG_v1.2.md` (o el registro de catálogo en código) y afirmar:
- `test_todo_skill_tiene_veredicto` — cada skill tiene estado terminal o `POSPUESTO` con razón+fecha;
  cero huecos `DEFINITION_PENDING`.
- `test_nuevos_skills_compilan` — cada `DEFINIDO-SHADOW` compila con compiler v2 sin error.
- `test_ningun_nuevo_skill_active` — ningún nuevo skill queda en estado `active`.
- `test_ningun_nuevo_skill_auto_apply` — `learning_consolidation.auto_apply == false` en todos.
- `test_campos_fuente_sellados` — ningún campo fuente sin `source_version`/`approved_by`.
- Fixture: patrón `client`/DB temporal como en `test_e3_4_*`; o parseo estático del `.md` si el
  veredicto vive en el doc.

## Riesgos / mitigaciones

- CEO no entrega H3 → PACK 2 queda `POSPUESTO` con razón; E5 puede cerrar igual (H3 no bloquea el gate).
- Dato inventado → verificación obligatoria de 10 citas; falla el hito si una cita no respalda la afirmación.
- Golden fabricado → solo vía harvester desde runs reales.

## DoD

- [ ] KB H3 cargada con reporte de conteos y 10 citas verificadas (`EVIDENCIA_KB_H3_<fecha>.md`).
- [ ] `ENT_FB_SKILL_CATALOG_v1.2.md` sin huecos (todo skill con veredicto).
- [ ] Skills `DEFINIDO-SHADOW` materializados en SHADOW (ninguno ACTIVE, ninguno `auto_apply`).
- [ ] PACK 2 con ≥3 golden candidates reales propuestos por el harvester.
- [ ] `test_e5_3_catalog_v12.py` verde; suite completa verde; `graphify update .` corrido.

---

# E5-4 — Tributario live: ATV Costa Rica end-to-end

## Objetivo

Emitir la **primera factura electrónica real** del tenant MWT, firmada, enviada a ATV
(Hacienda Costa Rica) y con acuse de aceptación. Cerrar el conector ATV (de mock a
sandbox a live) y hacer que el PDF deje de decir "NO FISCAL" solo para tenants con
certificado configurado. SAT/DIAN: solo documentar hallazgos, no activar.

Este es el hito de **mayor código** de la etapa.

## Estado del código base (ya existe)

`app/src/connectors/tax_authority.py`:
- `TaxConnectorConfig` (dataclass frozen): `authority, mode, base_url, document_status_endpoint,
  taxpayer_info_endpoint, api_key, api_secret, certificate`; props `is_mock`, `is_live`.
- `TaxAuthorityConnector` con `check_document_status`, `fetch_taxpayer_info`, `_require_configured`,
  `_require_certificate` (mensaje `"certificado no configurado (HE2-9)"`).
- `_live_document_status` / `_live_taxpayer_info` — **hoy lanzan `TaxConnectorError` fail-closed**
  con marcador `[PENDIENTE — NO INVENTAR]` (esto es lo que E5-4 implementa de verdad para ATV).
- Config no-secreta en `tenant_settings` bajo `connectors.tax.<authority>.*`; secretos en
  `_ConnectorSecretStore` (encriptado por `TenantSecretStore`) bajo `connectors/tax/<authority>/<suffix>`.
- Helpers: `get_tax_connector`, `build_tax_fetcher`, `set_tax_connector_secret`, `get_tax_connector_secret`.

`app/src/billing.py`:
- `_render_invoice_pdf(invoice: dict) -> bytes` — hoy imprime SIEMPRE `"DOCUMENTO NO FISCAL - BETA"`
  (líneas de leyenda hardcodeadas con `set_font`/`pdf.cell`/`pdf.multi_cell`).
- `download_invoice_pdf(...)` — tiene `request`, `conn=Depends(get_db)`, construye `ctx` con
  `_tenant_context(request, tenant_id)`, y ya audita `manual_invoice.pdf_generated`.

Tests existentes (no duplicar): `app/tests/test_e3_4_tax_connectors.py` ya cubre mock, live sin
credenciales (fail-closed), live sin certificado (HE2-9), aislamiento de secretos por tenant, y
`sandbox` fail-closed hasta que el HTTP real exista.

## Archivos a modificar

### `app/src/connectors/tax_authority.py`

1. **Implementar `_live_document_status(self, document_key)` y `_live_taxpayer_info(self, taxpayer_id)`
   reales para ATV** (mantener SAT/DIAN fail-closed con `[PENDIENTE — NO INVENTAR]`):
   - Cliente HTTP real (usar `httpx`/`requests` según lo ya presente en el repo) contra
     `config.base_url` + `config.document_status_endpoint` / `taxpayer_info_endpoint`.
   - **No inventar URLs ni endpoints:** solo funcionan cuando la config trae URLs verificadas por el
     timebox del PLB (`PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1`). Si falta, seguir fail-closed.
   - Autenticación con `api_key`/`api_secret` y firma con `certificate` (para live).
   - Devolver el mismo shape que los métodos mock: `{status, authority, mode, evidence:[{source_type,
     source_locator, captured_at, content_text, content_hash}]}` con `source_type="sandbox"|"live"`.
   - Manejo de errores del portal → `TaxConnectorError` con mensaje claro (nunca fabricar acuse).
2. **Rama por autoridad:** un dispatch para que solo `atv` entre a la ruta HTTP real; `sat`/`dian`
   sigan lanzando el error `[PENDIENTE — NO INVENTAR]`.
3. **Validación de config ATV:** reforzar `_require_configured` para que `sandbox`/`live` exijan
   `document_status_endpoint`/`taxpayer_info_endpoint` además de `base_url` y credenciales.
4. **`_require_certificate` fail-closed** ya existe: reusar tal cual para `live`.
5. (Opcional) función de emisión/firma si la emisión de la e-factura pasa por este conector; si la
   emisión vive en el pipeline de skills FE (`SKILL_FE_*`), mantener aquí solo status/taxpayer y
   dejar la emisión a la skill, alimentada por `build_tax_fetcher`.

### `app/src/billing.py`

1. **Derivar `has_tax_certificate`** para el tenant: leer el secreto de certificado ATV vía
   `get_tax_connector_secret(ctx, "atv", "certificate")` (o consultar
   `connectors.tax.atv.mode == "live"` + certificado presente). Encapsular en un helper
   `_tenant_has_tax_certificate(ctx) -> bool`.
2. **PDF fiscal condicional:** cambiar `_render_invoice_pdf` para aceptar el flag
   (`_render_invoice_pdf(invoice, *, has_tax_certificate: bool)`):
   - `has_tax_certificate == False` → conservar exactamente `"DOCUMENTO NO FISCAL - BETA"` y la
     leyenda actual (comportamiento por defecto, no regresión).
   - `has_tax_certificate == True` → NO imprimir la leyenda "NO FISCAL"; imprimir en su lugar los
     datos fiscales (clave numérica, autoridad, estado de aceptación ATV).
3. En `download_invoice_pdf`, calcular el flag desde `ctx` y pasarlo a `_render_invoice_pdf`.
   Mantener el audit `manual_invoice.pdf_generated` con `correlation_id`.

### Config vía API (tenant_settings de MWT)

- Setear `connectors.tax.atv.mode`, `connectors.tax.atv.base_url`,
  `connectors.tax.atv.document_status_endpoint`, `connectors.tax.atv.taxpayer_info_endpoint`
  con las URLs verificadas (deja de haber `[PENDIENTE]` para ATV).
- Certificado y credenciales: `set_tax_connector_secret(ctx, "atv", "certificate"|"api_key"|"api_secret", ...)`
  → `TenantSecretStore` namespace `connectors/tax/atv/cert`. **Nunca** commitear secretos.

## Archivos a crear

- `app/tests/fixtures/atv_cassettes/*.json` — respuestas reales del sandbox de Hacienda,
  **anonimizadas** (grabadas durante el timebox de verificación).
- `app/tests/test_e5_4_atv_sandbox_contract.py` — contrato contra los cassettes.
- `app/tests/test_e5_4_pdf_fiscal_flag.py` — flag fiscal del PDF.
- `docs/audits/EVIDENCIA_EFACTURA_ATV_<fecha>.md` — clave numérica, estado de aceptación, capturas
  de auditoría; **sin datos sensibles del receptor**.

## Tests

### `test_e5_4_atv_sandbox_contract.py`
- `test_atv_document_status_parsea_cassette` — con `mode="sandbox"` + cliente HTTP monkeypatcheado
  que devuelve el cassette, `check_document_status` produce evidence con `source_type="sandbox"`,
  `content_hash` estable, y campos esperados.
- `test_atv_taxpayer_info_parsea_cassette` — análogo para `fetch_taxpayer_info`.
- `test_atv_sin_url_verificada_falla_cerrado` — sandbox/live sin `base_url`/endpoints → `TaxConnectorError`.
- `test_sat_dian_siguen_pendientes` — SAT/DIAN en sandbox/live siguen lanzando `[PENDIENTE — NO INVENTAR]`.
- `test_live_sin_certificado_he2_9` — reafirma el gate de certificado en modo live (no romper E3-4).
- Patrón: monkeypatch del cliente HTTP para no golpear la red real; cargar cassettes desde
  `app/tests/fixtures/atv_cassettes/`.

### `test_e5_4_pdf_fiscal_flag.py`
- `test_pdf_sin_certificado_contiene_no_fiscal` — tenant sin cert → los bytes/el texto del PDF
  contienen `"NO FISCAL"`.
- `test_pdf_con_certificado_no_contiene_no_fiscal` — tenant con cert ATV → el PDF NO contiene
  `"NO FISCAL"` y sí incluye la clave numérica/estado.
- Extraer texto del PDF (p.ej. leer el stream fpdf o un `pypdf` si ya está en deps) o inyectar el
  flag y verificar la rama tomada; mantener el test determinista.

## Riesgos P0 / mitigaciones

- **Envío sin HITL** → la emisión de e-factura real es acción externa: doble confirmación obligatoria
  (token), igual que envío de correo/borrado.
- **Secreto en git** → solo `TenantSecretStore`; los cassettes van anonimizados; evidencia sin secretos.
- **URLs inventadas** → mantener `[PENDIENTE — NO INVENTAR]` hasta verificación del timebox.
- **Certificado lead-time** → compra el DÍA 1 de E5 (no en la ola 3).

## DoD

- [ ] Factura electrónica MWT **aceptada por ATV en live** (evidencia con clave numérica, sin datos sensibles del receptor).
- [ ] SAT/DIAN documentados (hallazgos), no activados.
- [ ] Cassettes de contrato anonimizados en la suite; `test_e5_4_atv_sandbox_contract.py` y
      `test_e5_4_pdf_fiscal_flag.py` verdes.
- [ ] Tests E3-4 de conectores siguen verdes (sin regresión).
- [ ] `graphify update .` corrido tras los cambios.

---

# E5-5 — PACK 1 y PACK 3 a ACTIVE por uso real

## Objetivo

Que PACK 1 (fiscalidad, ya con ATV real de E5-4) y PACK 3 (cobranza, sobre facturas
reales de MWT) crucen el umbral de promoción **con datos, no con fe**. Meta por pack:
≥3 golden cases `approved+verified`, track record ≥100 runs y ≥90% acceptance.
PACK 1 primero, PACK 3 después.

**Código nuevo esperado: cero.** Toda la maquinaria existe; el hito es operación +
evidencia. Solo se crea código si un bug aparece.

## Estado del código base (ya existe, no reimplementar)

- `app/src/skill_primitives.py`:
  - `promote_pack(ctx, conn, *, pack_id, approved_by)` — `enforce_tenant_scoped(ctx)`,
    `require_scoped_workspace()`; valida: golden cases del pack existen, 0 sin aprobar,
    0 aprobados sin `verified_by` (segundo gate), track record ≥ `PROMOTION_THRESHOLDS`; setea
    `pack_status.status='active'` y `skill_manifest.status='active'`.
  - `PROMOTION_THRESHOLDS = {"runs_total": 100, "acceptance_rate": 0.90}`.
  - `compute_pack_readiness(ctx, conn, *, pack_id)` — snapshot read-only para el tablero (nunca inventa).
- `app/src/api.py`: `api_get_pack_readiness` (GET) y el endpoint que llama
  `promote_pack(ctx, conn, pack_id=..., approved_by=user_id)` (con token HITL).
- `app/src/golden_harvester.py`: `propose_golden_case_from_run`, `approve_golden_case`,
  `verify_golden_case` (con gate `verified_by != approved_by`).

## Archivos a crear

- `docs/audits/OPERACION_E5_PACKS_<fecha>.md` — evidencia: capturas del tablero de readiness por pack
  (runs, acceptance, golden approved+verified), fecha de cruce de umbral, token de promoción usado,
  y la curva de volumen semana a semana.

## Archivos a modificar

- Ninguno esperado. Si aparece bug en `promote_pack`/`compute_pack_readiness`/harvester, corregir
  con test de regresión dedicado.

## Procedimiento operativo

1. Rutina de dogfood semanal (`PLB_FB_PROMOTION_READINESS_DOGFOOD_v1`): correr skills de PACK 1
   (fiscalidad con ATV real) y PACK 3 (cobranza sobre facturas reales de MWT).
2. Proponer golden cases con el harvester desde runs reales; curador **aprueba** y **verifica**
   (verificador distinto del aprobador — segundo gate).
3. Cuando el tablero muestre verde (≥3 golden approved+verified, ≥100 runs, ≥90% acceptance):
   `promote_pack` manual con token. **PACK 1 primero, PACK 3 después.**
4. Si a 3 semanas no hay 100 runs: **no** bajar el umbral — ampliar uso real (más facturas reales
   de MWT) y documentar la curva. El umbral es el contrato de calidad.

## Tests

No nuevos salvo bug. La suite existente cubre las invariantes:
- `app/tests/test_e3_4_pack_readiness.py`
- `app/tests/test_e3_4_pack1_fe.py`
- `app/tests/test_e3_4_pack3_cobranza.py`

Verificar que siguen verdes tras E5-4 (ATV live puede cambiar fixtures de PACK 1).

## DoD

- [ ] PACK 1 en ACTIVE (con evidencia de tablero verde y token de promoción).
- [ ] PACK 3 en ACTIVE (o cierre autorizado 1 semana después si la conciliación de la primera
      factura de E5-6 es su caso golden #100).
- [ ] Tablero de readiness como evidencia (`OPERACION_E5_PACKS_<fecha>.md`).
- [ ] Cero golden fabricado (todos vía harvester + runs reales, approved+verified).

---

# E5-6 — Design partner: onboarding, soak de 30 días y primera factura pagada

## Objetivo

Cumplir el **gate comercial de salida de E5** con un tenant externo real: acuerdo de
datos firmado, onboarding asistido, soak instrumentado de 30 días (≥10 casos reales,
0 fugas, canarios verdes 4 semanas, sin P0), y primera factura **pagada y conciliada**
con PACK 3.

## Estado del código base (reutilizar)

- `app/src/health_dashboard.py`: `_compute_tenant_health(app_conn, tenant_id)` ya agrega runs
  (30d/7d, éxito/fallo, error_rate), costo (`summarize_tenant_usage_cost`), invoices (open/paid/overdue),
  `_count_pending_drafts` (HITL pendientes), workspaces, users. **Es la base del soak report.**
- `app/src/db.py`: `summarize_tenant_usage_cost`, `list_reconciliations`, `match_reconciliation`,
  `list_manual_invoices`, `create_reconciliation` (PACK 3 / conciliación).
- `app/scripts/check_canary_isolation.py` y `check_canary_isolation_postgres.py`: verifican
  aislamiento del tenant canario (exit 0 = OK, 1 = fuga). Reusar como fuente de "canarios verdes".
- `PLB_FB_TENANT_ONBOARDING_v1` (onboarding), `ENT_FB_VERTICAL_CANDIDATES_v2` (ranking), y el agente
  vivo hace el onboarding conversacional (E4-7.3 ya existe).

## Archivos a crear

- `app/scripts/soak_report.py` — script read-only del reporte semanal de soak.
- `app/tests/test_e5_6_soak_report.py` — tests de agregados/aislamiento/fail-closed.
- `docs/faberloom/SCH_FB_ACUERDO_DATOS_BETA_v1.md` — plantilla del acuerdo de datos beta.
- `docs/audits/SOAK_<tenant>_S1.md` … `SOAK_<tenant>_S4.md` — 4 reportes semanales.
- `docs/audits/ACTA_ETAPA5_<fecha>.md` — acta de cierre de E5 (formato estándar).

## Archivos a modificar

- Ninguno esperado si el soak se implementa como script read-only. Posible ajuste de
  `PLB_FB_TENANT_ONBOARDING_v1` si la operación revela gaps.

## Cambios específicos de código — `app/scripts/soak_report.py`

CLI (argparse, patrón de `ingest_kb_h3.py` / `check_canary_isolation.py`):
- `--tenant-id` (requerido), `--week` (entero S1..S4), `--out docs/audits` (dir),
  `--json` (imprime JSON), `--db-path`/`FABERLOOM_DB_PATH`.

Funciones:
- `build_soak_report(ctx: Context, conn, week: int) -> dict` — **read-only**; llama
  `enforce_tenant_scoped(ctx)` y `ctx.require_tenant()` (fail-closed sin tenant). Agrega:
  - health del tenant (reusar/derivar de `_compute_tenant_health` o consultas equivalentes).
  - casos procesados (runs de la semana), HITL aprobados/rechazados (drafts/hitl del tenant).
  - costo (`summarize_tenant_usage_cost`).
  - incidentes (P0/degradaciones desde auditoría).
  - canarios de contaminación: invocar la lógica de `check_canary_isolation` (verde/rojo).
  - **Solo agregados y conteos; NUNCA contenido de casos** (sin cuerpos de correo/PDF/KB).
- `render_markdown(report: dict) -> str` — renderiza el `.md` con formato estándar de auditoría.
- `main(argv) -> int` — arma `Context(workspace_id=..., tenant_id=..., user_id=...)`, escribe
  `docs/audits/SOAK_<tenant>_S<week>.md`, exit no-cero si un criterio crítico falla (p.ej. canario rojo).

Reglas: read-only estricto, `Context` tenant-scoped en toda query, `enforce_tenant_scoped` en las
críticas, fail-closed si falta tenant, cero contenido sensible.

## Contenido de `SCH_FB_ACUERDO_DATOS_BETA_v1.md` (plantilla)

- Alcance de datos; visibilidad y sellado (key broker explicado en lenguaje de negocio).
- **No-entrenamiento** con datos del cliente.
- SLA beta (referencia a `PLB_FB_SOPORTE_SLA_BETA`); beta 90 días con precio preferente.
- Terminación y exportación de datos.
- Términos económicos como campo explícito `[PENDIENTE — decisión CEO]`.
- Nota: **revisión legal humana obligatoria antes de firmar** (responsable CEO). Fugu genera la
  plantilla; el CEO firma, no redacta.

## Tests — `app/tests/test_e5_6_soak_report.py`

- `test_soak_report_agregados_correctos` — con datos sembrados (runs, HITL, invoices, costo),
  `build_soak_report` devuelve los conteos/sumas esperados.
- `test_soak_report_sin_contenido_sensible` — el dict/markdown no contiene cuerpos de casos
  (solo agregados); afirmar ausencia de campos de contenido.
- `test_soak_report_aislamiento_tenant` — datos de tenant B no aparecen en el reporte del tenant A.
- `test_soak_report_falla_cerrado_sin_tenant` — `Context` sin tenant → error fail-closed
  (`enforce_tenant_scoped`/`require_tenant`).
- `test_soak_report_canarios_verde_rojo` — canario limpio → verde; canario con fuga simulada → rojo
  reflejado y exit no-cero.
- Fixture: DB temporal (`tmp_path`) sembrada; patrón de `test_e3_6_billing.py` / `test_e3_4_*`.

## Riesgos P0 / mitigaciones

- **Fuga en tenant externo** → canarios de contaminación en cada reporte semanal; cualquier fuga = P0
  y el soak se **reinicia** tras remediación.
- **Reporte filtra contenido** → solo agregados + test `test_soak_report_sin_contenido_sensible`.
- **Factura no pagada** → el gate no cierra hasta pago conciliado con PACK 3.
- **Partner #1 no firma** → candidato #2 con trigger automático a los 21 días.

## DoD (= GATE DE SALIDA DE E5)

- [ ] Tenant externo activo ≥30 días; ≥10 casos reales; 0 fugas (canarios verdes las 4 semanas); sin P0.
- [ ] 4 reportes soak generados (`SOAK_<tenant>_S1..S4.md`) por `soak_report.py`.
- [ ] `test_e5_6_soak_report.py` verde; suite completa verde.
- [ ] Acuerdo de datos firmado y archivado (`SCH_FB_ACUERDO_DATOS_BETA_v1.md` + firma).
- [ ] Primera factura **pagada** y **conciliada** con PACK 3 (idealmente el caso golden #100 de PACK 3).
- [ ] `docs/audits/ACTA_ETAPA5_<fecha>.md` en formato estándar; `graphify update .` corrido.

---

## Apéndice — Orden de ejecución y dependencias

1. **E5-4** (código ATV + PDF fiscal) habilita facturas fiscales reales → alimenta **E5-5** (golden reales de PACK 1/3).
2. **E5-1** (MWT en `natural` estable ≥2 semanas) es prerequisito operativo de **E5-6** (no tocar al partner antes).
3. **E5-3** es independiente (KB/catálogo); si H3 no llega, PACK 2 queda `POSPUESTO` y E5 cierra igual.
4. **E5-6** es el gate de salida: requiere E5-1 estable, E5-4 (si el partner es CR y pide e-factura),
   E5-5 (PACK 1 ACTIVE), y las evidencias de E5-2 ya commiteadas.

### Recordatorios transversales (aplican a todos los hitos con código)

- Correr la suite completa (`cd app && python -m pytest -q`) antes de cualquier deploy; deploy siempre desde `main`.
- Tras modificar código: `graphify update .`.
- No commitear secretos; usar `TenantSecretStore` / variables de entorno.
- Toda mutación audita con `correlation_id`; toda query es tenant-scoped y fail-closed.
