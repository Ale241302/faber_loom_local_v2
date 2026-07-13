# PLAN_DESARROLLO_FABERLOOM_ETAPA10_v1 — Escala, resiliencia y certificación (GA 1.0)

id: PLAN_FB_ETAPA10
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 10: operar a escala con resiliencia probada y seguridad certificable; cierre GA 1.0
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · ENT_PLAT_OBSERVABILIDAD · ENT_PLAT_MEMORY_STACK · ENT_COMP_ISO_ROADMAP · ENT_PLAT_SEGURIDAD · PLB_FB_INCIDENT_RESPONSE_v1 (E6) · POL_HEALTH_CHECK

**Cláusula de re-validación:** v1.1 al arrancar, con los números reales de E6-E9 (tenants, volumen, incidentes). Los umbrales de disparo del §2 se recalibran con esos datos.

---

## §0. Naturaleza y decisiones

E10 no agrega features: agrega CERTEZA. El sistema ya hace lo que debe; esta etapa garantiza que lo siga haciendo con 10x tenants, con un disco quemado, con un atacante competente y con un auditor mirando. Cierra con el acta de GA 1.0.

**Decisiones del Arquitecto:**
- **DA10-1. Observabilidad: Prometheus + Grafana self-hosted en el VPS** (compose junto a la app; coherente con la doctrina self-hosted del proyecto). Métricas vía `prometheus-fastapi-instrumentator` + métricas de negocio propias. Logs: estructurados JSON a archivo con rotación + Loki si el volumen lo pide (criterio de disparo abajo). Nada de SaaS de observabilidad en E10.
- **DA10-2. HA pragmática, no multi-región:** Postgres con backups PITR (WAL archiving + base backups) y réplica en standby caliente en un segundo VPS; MinIO con replicación al mismo secundario; DNS failover manual documentado. Multi-región/k8s NO — el tamaño no lo justifica; se re-evalúa con >100 tenants activos.
- **DA10-3. Memoria a escala por criterios de disparo, no por moda:** pgvector se extiende con **pgvectorscale** cuando p95 de búsqueda KB >500ms o >5M chunks (Plan A de `ENT_PLAT_MEMORY_STACK`); **Letta self-hosted** para memoria operativa cuando M17 muestre límites concretos (recall irrelevante medido por feedback, o >100k bloques/tenant). Si los umbrales no se cruzan, el hito documenta la medición y NO migra — eso también es cerrar el hito.
- **DA10-4. Pentest externo humano** (no solo herramientas), alcance: API pública, MCP, signup, multi-tenancy. Proveedor = decisión de compra CEO con 2 cotizaciones (insumo del hito). Remediación P0/P1 obligatoria antes del acta GA.
- **DA10-5. ISO 27001: en E10 se construye la BASE certificable** (inventario de controles, políticas, evidencia continua) según `ENT_COMP_ISO_ROADMAP`; la certificación formal con auditor es decisión de negocio posterior (depende de si los clientes enterprise la exigen). Rama `e10-escala`.

## §1. Mapa de olas

| Ola | Hitos |
|---|---|
| 1 | E10-0 (observabilidad + SLOs) |
| 2 | E10-1 (HA/DR con simulacro), E10-2 (memoria a escala por criterios) |
| 3 | E10-3 (pentest + remediación), E10-4 (base ISO + hardening supply chain) |
| 4 | E10-5 (performance multi-tenant), E10-6 (acta GA 1.0) |

## §2. Detalle por hito

### E10-0 — Observabilidad y SLOs

**Objetivo:** el sistema se mide solo y avisa antes de doler.

**Tareas:**
1. Stack: Prometheus + Grafana + Alertmanager en `docker-compose` del VPS (red interna; Grafana tras auth). Instrumentar FastAPI (latencias, errores, RPS por endpoint) + métricas de negocio: tasks por estado, decisiones del planner por modo, propuestas ambientales, costo IA por hora, HITL pendientes, edad del backup smoke, profundidad del outbox.
2. Logs estructurados: `structlog` (JSON, correlation_id en todo — ya existe en audit; unificar el logger de app) con rotación; criterio de disparo para Loki: >2GB/día o necesidad de búsqueda cross-servicio.
3. **SLOs (contrato interno, medible en Grafana):** disponibilidad API 99.5% mensual; p95 completions <8s; p95 endpoints de lectura <500ms; entrega de webhooks <60s p95; edad máxima del backup verificado 26h. Alertas de burn-rate sobre cada SLO.
4. Dashboards: (a) salud técnica, (b) negocio (tenants activos, tasks, costo vs facturación), (c) agente (autonomía por nivel, alignment score, oscilaciones). El health dashboard in-app NO se reemplaza (es para tenants); Grafana es para operar la plataforma.
5. Runbook de alertas: cada alerta enlaza a su procedimiento en `PLB_FB_INCIDENT_RESPONSE` (ampliar a v2 con las alertas nuevas).

**Archivos:** `docker-compose.yml` (servicios), `app/src/metrics.py`, `main.py` (instrumentator), `app/src/log_config.py`, dashboards como JSON en `ops/grafana/`, `PLB_FB_INCIDENT_RESPONSE_v2.md`.
**Tests:** `test_e10_0_metrics_endpoint.py` (métricas expuestas solo en red interna; sin datos de contenido en labels — cardinalidad y privacidad), smoke de alertas (disparo sintético documentado).
**DoD:** SLOs midiéndose 2 semanas; 1 alerta real o sintética recorrida end-to-end con su runbook. **Esfuerzo:** 2-3 sesiones Fugu.

### E10-1 — HA y DR con simulacro real

**Objetivo:** perder el VPS primario es un mal día, no una extinción.

**Tareas:**
1. **Postgres PITR:** WAL archiving continuo + base backup diario al VPS secundario (y copia cifrada fuera de ambos — decisión: bucket S3-compatible externo cifrado client-side con la master key de ops, `[PENDIENTE — proveedor: decisión de compra CEO, 2 opciones al hito]`). Standby caliente con streaming replication; promoción documentada paso a paso.
2. **MinIO:** replicación de site a la instancia del secundario (mc mirror programado o replicación nativa — elegir según versión instalada, documentar).
3. **DR runbook** `docs/OPERACION_DR_E10.md`: RTO objetivo 4h, RPO 15min; procedimiento de failover (promover standby, redirigir DNS, verificar canarios) y de failback.
4. **SIMULACRO OBLIGATORIO:** apagar el primario en ventana controlada y levantar el servicio desde el secundario siguiendo el runbook, con cronómetro. Evidencia con tiempos reales en `docs/audits/SIMULACRO_DR_<fecha>.md`. Un DR no simulado es una hipótesis, no un plan.
5. El backup smoke de E5-2 se extiende: restore de prueba semanal DESDE el secundario.

**Tests:** `test_e10_1_replication_lag_metric.py` (métrica de lag expuesta y alertada); el simulacro ES el test del hito.
**DoD:** simulacro completado dentro de RTO/RPO; runbook corregido con lo aprendido; réplica y PITR monitoreados. **Esfuerzo:** 2 sesiones Fugu + 1 día Ops + simulacro.

### E10-2 — Memoria y búsqueda a escala (por criterios de disparo)

**Objetivo:** medir contra los umbrales de DA10-3 y actuar SOLO si se cruzan.

**Tareas:**
1. Medición formal: benchmark de búsqueda KB (p50/p95 por tamaño de tenant), conteo de chunks/bloques, calidad de recall de M17 (muestreo con feedback tipificado).
2. Si pgvector cruza umbral: instalar **pgvectorscale**, migrar índices (StreamingDiskANN), re-benchmark A/B. Si no: reporte de headroom.
3. Si M17 cruza umbral: piloto Letta self-hosted según el plan E de `ENT_PLAT_MEMORY_STACK` (4 semanas, perfil aislado, criterios de éxito de la spec) antes de cualquier migración. Si no: reporte.
4. Independiente del disparo: compactación de memoria CAPA 1 (bloques viejos no usados → archivo con TTL de la spec E4-5) y particionado de tablas de log calientes (`planner_decision_log`, `action_execution_log`, `usage_record`) por mes si superan 5M filas.

**Archivos:** `app/scripts/benchmark_kb_search.py`, reportes en `docs/audits/`, migraciones condicionales.
**Tests:** benchmark reproducible commiteado; si hay migración de índices: paridad de resultados FTS/vector pre/post (patrón E3-1).
**DoD:** medición documentada; acciones disparadas ejecutadas o headroom certificado. **Esfuerzo:** 1-3 sesiones Fugu según disparos.

### E10-3 — Pentest externo y remediación

**Objetivo:** un adversario pago no encuentra lo que un adversario gratis sí encontraría.

**Tareas:**
1. Contratación (CEO, 2 cotizaciones — iniciar al DÍA 1 de E10, lead time): alcance = API pública v1, MCP, signup/auth, aislamiento multi-tenant, webhooks, desktop auth. Reglas de engagement documentadas; entorno: staging con datos sintéticos + producción solo lectura pasiva.
2. Pre-pentest interno: correr la contamination suite completa + `security/injection.py` extendido + dependencia scanning (pip-audit + npm audit en CI — añadirlo YA como job permanente) + revisión de headers/CSP/cookies.
3. Remediación: P0/P1 del informe = bloqueantes del acta GA (sin excepciones); P2+ priorizados a backlog con fecha. Re-test de los P0/P1 remediados por el mismo proveedor.
4. Evidencia: informe (redactado si hace falta) + remediaciones en `docs/audits/PENTEST_E10_<fecha>/`.

**Archivos:** `.github/workflows/security_audit.yml` (pip-audit/npm audit permanentes), fixes según hallazgos.
**DoD:** informe recibido; P0/P1 remediados y re-testeados; scanning de dependencias en CI. **Esfuerzo:** compra + 2-4 sesiones Fugu de remediación (estimación se ajusta al informe).

### E10-4 — Base certificable ISO 27001 y supply chain

**Objetivo:** cuando un cliente enterprise pida evidencia de seguridad, la respuesta es un paquete, no una promesa.

**Tareas:**
1. Mapear lo EXISTENTE contra el Anexo A de ISO 27001 usando `ENT_COMP_ISO_ROADMAP` como guía: mucho ya está (RLS, cifrado por tenant, HITL, audit trail, rotaciones E5-2, DR E10-1, incidentes E6-5). Salida: `docs/faberloom/ENT_FB_ISO_CONTROL_MAP_v1.md` — control por control: implementado (evidencia) / parcial (gap con dueño y fecha) / no aplica (razón).
2. Políticas formales faltantes como docs KB versionados: control de acceso (ya hay matriz E2 — formalizar), gestión de vulnerabilidades (el scanning de E10-3 + SLA de parcheo), retención y borrado de datos de tenant (incluye el derecho de exportación/borrado del acuerdo E5-6 — implementar `export_tenant_data.py` y `delete_tenant.py` con doble confirmación y evidencia, si no existen ya del bootstrap: verificar primero).
3. Supply chain: lockfiles estrictos (pip-tools/uv lock + package-lock), imágenes Docker pinneadas por digest, SBOM generado en CI (syft), firmas de imagen (cosign) para el deploy.
4. Evidencia continua: los reportes recurrentes (backup smoke, rotaciones, simulacros, canarios) se indexan en el control map — la evidencia se genera sola desde E5; aquí solo se cataloga.

**Archivos:** `ENT_FB_ISO_CONTROL_MAP_v1.md`, políticas POL_FB_* nuevas, `app/scripts/export_tenant_data.py` + `delete_tenant.py` (con tests de completitud y de que el borrado no toca a otros tenants), CI de SBOM/firmas.
**Tests:** `test_e10_4_tenant_export.py` (export completo y solo del tenant), `test_e10_4_tenant_delete.py` (borrado total verificado + cero efecto colateral — correr contra la contamination suite después).
**DoD:** control map sin huecos sin dueño; export/delete operativos; SBOM y firmas en el pipeline. **Esfuerzo:** 3 sesiones Fugu + redacción de políticas.

### E10-5 — Performance multi-tenant a escala

**Objetivo:** 10x tenants sin 10x dolor.

**Tareas:**
1. Carga sintética: script de carga (locust/k6) simulando N tenants concurrentes (chat, briefs, tasks, API v1) contra staging; encontrar el primer cuello (conexiones Postgres → PgBouncer si hace falta; workers uvicorn; colas del orquestador).
2. Fairness entre tenants: límite de tasks concurrentes por tenant (constante por plan) para que un tenant ruidoso no acapare el orquestador; cola FIFO por tenant con presupuesto de workers.
3. Los presupuestos de E8-5 se re-verifican bajo carga; los SLOs de E10-0 son el criterio de aprobación.

**Archivos:** `ops/load/` (escenarios), `orchestrator.py`/`plans.py` (límites de concurrencia), posible PgBouncer en compose.
**Tests:** `test_e10_5_tenant_fairness.py` (tenant saturado no bloquea a otro); reporte de carga en `docs/audits/`.
**DoD:** carga de 10x tenants actuales cumpliendo SLOs; fairness probada. **Esfuerzo:** 2 sesiones Fugu.

### E10-6 — Acta GA 1.0

**Tareas:** suite + Vitest + arena + contamination + canarios TODOS verdes; SLOs cumplidos 90 días corridos (puede solaparse con las olas — el reloj corre desde E10-0); checklist GA: DR simulado ✓, pentest remediado ✓, control map ✓, export/delete ✓, fairness ✓; `docs/audits/ACTA_GA_1_0_<fecha>.md` firmada por CEO; tag `v1.0.0` en main; actualización final de la KB (RW_ROOT, DASHBOARD_SNAPSHOT, IDX_PLATAFORMA, ENT_GOB_PENDIENTES a cero-o-con-dueño).
**DoD:** el acta GA existe porque todo lo anterior existe. FaberLoom 1.0.

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| El simulacro DR falla | Por eso se hace: en ventana controlada, con rollback al primario; se repite hasta cumplir RTO |
| El pentest encuentra un P0 de aislamiento | Es el mejor dinero gastado del roadmap; remediación bloqueante + re-test + post-mortem a la contamination suite |
| Observabilidad filtra contenido en métricas/logs | Regla: labels y logs con ids y agregados, jamás contenido; test de cardinalidad/privacidad |
| Migrar memoria "porque toca" | Criterios de disparo numéricos (DA10-3); no cruzar umbral = no migrar, documentado |
| Fatiga de etapa (todo es fontanería) | Los dashboards de negocio (E10-0.4) hacen visible el valor; el acta GA es la meta narrativa |

## §4. Gate de salida

ACTA_GA_1_0 firmada con su checklist completo. A partir de aquí el roadmap se replanifica con el negocio (E11+: lo que los clientes de GA enseñen).

## Changelog

- v1.0.0 (2026-07-12): Creación. Decisiones DA10-1..DA10-5; DR con simulacro obligatorio; GA condicionada a evidencia, no a fecha.
