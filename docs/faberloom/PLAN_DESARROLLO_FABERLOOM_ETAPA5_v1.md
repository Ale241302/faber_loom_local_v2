# PLAN_DESARROLLO_FABERLOOM_ETAPA5_v1 — Madurez operativa y primer cliente

id: PLAN_FB_ETAPA5
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 5: operar el agente, madurar la fábrica y cerrar el primer cliente pagando
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · PLAN_DESARROLLO_FABERLOOM_ETAPA4_v2 · PLB_FB_E4_ROUTING_NATURAL_v1 · PLB_FB_PROMOTION_READINESS_DOGFOOD_v1 · PLB_FB_TENANT_ONBOARDING_v1 · PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1 · ENT_FB_VERTICAL_CANDIDATES_v2

---

## §0. Naturaleza de la etapa y decisiones

E5 es la etapa donde los "pendientes humanos" heredados (H1-H9 de E3) **dejan de ser una lista y se convierten en hitos con DoD**. Es 60% operación instrumentada y 40% código de refinamiento. Duración estimada: 5-7 semanas (el soak de 30 días marca el piso).

**Decisiones del Arquitecto (no re-abrir):**
- **DA5-1.** Autoridad tributaria live PRIMERO: **ATV Costa Rica** (MWT/Marluvas operan CR; el dogfood propio es el primer usuario de e-factura). SAT/DIAN quedan en sandbox hasta que un tenant real los pida.
- **DA5-2.** El design partner se elige del ranking de `ENT_FB_VERTICAL_CANDIDATES_v2` (lead: distribución B2B técnica). El acuerdo de datos usa la plantilla del hito E5-6 — el CEO firma, no redacta.
- **DA5-3.** El soak se mide con lo que ya existe (health dashboard + shadow report + contamination canaries); no se construye telemetría nueva salvo el reporte semanal automatizado (E5-6.4).
- **DA5-4.** La promoción `shadow→natural` sigue el PLB de E4 con el ACE; primer candidato: el workspace de dogfood MWT con más volumen. Nada de natural en el design partner hasta que MWT acumule 2 semanas estables.
- **DA5-5.** Rama `e5-madurez`. Antes de TODO: hito E5-0 (merge E4 a main + cierre documental). Deploy siempre desde main.

Reglas R1-R13 del roadmap vigentes. Suite base: 724 passed / 0 failed.

## §1. Mapa de olas

| Ola | Hitos | Banda |
|---|---|---|
| 1 | E5-0 (consolidación), E5-2 (seguridad operativa) | Código+Ops |
| 2 | E5-1 (shadow→natural), E5-3 (KB H3 + catálogo) | Operación instrumentada |
| 3 | E5-4 (tributario live), E5-5 (PACK 1/3 ACTIVE) | Código+Compra+Dogfood |
| 4 | E5-6 (design partner + soak + factura) | Comercial instrumentado |

## §2. Detalle por hito

### E5-0 — Consolidación de E4 (deuda inmediata)

**Objetivo:** producción corre desde `main`, la documentación de E4 queda al estándar E3, y el curador no perdió capacidades.

**Tareas:**
1. Git: merge `e4-agente-vivo` → `main`, tag `e4-cierre-20260712`, rebuild y redeploy del VPS desde main; verificar `/api/health` (schema 48) y humo de endpoints críticos (login, chat general, brief, shadow-report).
2. Reescribir `docs/audits/AUDIT_E4_CIERRE_20260711.md` al formato E3 (semáforo por hito, evidencia archivo/función, tabla de tests, desviaciones: const→var, fábrica fuera del rail, 6 fixes de producción como lecciones).
3. Completar `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md` como as-built real: módulos de `living_agent/` (briefs/planner/autonomy/orchestrator/tasks/artifacts/memory/feedback/presence), flujo pregunta-general vs profundización vs task multi-paso, mapeo al Autonomy Ladder, tablas v42-48 con propósito.
4. Verificar/añadir en `docs/ENT_PLAT_LLM_ROUTING.md` la sección de `routing.mode` (manual|shadow|natural) y la deprecación de `FABERLOOM_AUTO_MODE_ENABLED`, con changelog.
5. **Auditoría de capacidades del curador:** recorrer con el CEO la vista Skills y verificar que TODAS las acciones de fábrica (importar catálogo, compilar, ver golden cases, promote_pack, kill switch) son accesibles sin la entrada "Fábrica de skills" eliminada en E4. Si falta alguna: restaurarla dentro de la vista Skills (no como rail item nuevo). Registrar el veredicto en la auditoría.

**Archivos:** `docs/audits/AUDIT_E4_CIERRE_20260711.md` (reescritura), `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md`, `docs/ENT_PLAT_LLM_ROUTING.md`, posible `app/static/js/app.jsx` (acciones curador).
**Tests:** suite completa post-merge en main (0 failed); smoke manual de deploy documentado.
**DoD:** producción = main con tag; docs al estándar; veredicto del curador registrado. **Esfuerzo:** 1 sesión Fugu + 1h CEO.

### E5-1 — Operación shadow→natural

**Objetivo:** el routing natural toma el control real en el dogfood, gobernado por datos.

**Tareas:**
1. Encender `routing.mode="shadow"` en TODOS los workspaces activos del tenant MWT (hoy solo dogfood). Rutina semanal (calendario del equipo): revisar "Routing en sombra" cada lunes; el curador marca decisiones absurdas con el feedback tipificado.
2. Al cumplir el umbral del PLB (≥2 semanas o ≥50 decisiones, ahorro proyectado ≥0, 0 absurdas): promover el workspace de mayor volumen a `natural` vía `promote_or_rollback_workspace` (token). Observación 1 semana; si `degrade_workspace_if_needed` no dispara, promover 2 workspaces más.
3. Ejercicio de rollback REAL (no simulado): degradar manualmente un workspace promovido y verificar que vuelve a shadow sin pérdida (auditado). Es el simulacro de incendio del routing.
4. Código menor: si la operación revela fricciones del tablero (falta un filtro, una columna), corregirlas — presupuesto máximo 1 sesión.
5. Registrar la evidencia quincenal en `docs/audits/OPERACION_E5_ROUTING_<fecha>.md` (números del shadow report, promociones, degradaciones).

**DoD:** ≥3 workspaces MWT en `natural` estables ≥2 semanas; 1 rollback ejercitado; ahorro real medido y documentado. **Esfuerzo:** 4 semanas de operación + ≤1 sesión Fugu.

### E5-2 — Seguridad operativa ejecutada (no más runbooks sin correr)

**Objetivo:** las tres deudas operativas de E3 quedan EJECUTADAS con evidencia.

**Tareas:**
1. **Rotación VPS:** ejecutar `docs/OPERACION_VPS_E3.md` completo (password root, SSH solo-llaves con `PasswordAuthentication no`, rotación de claves de correo compartidas, verificación `.env` fuera de git). Evidencia en `docs/audits/EVIDENCIA_ROTACION_20260712.md` (comandos, fechas, huellas de llaves — sin secretos).
2. **Migración MinIO prod:** backup verificado → `migrate_minio_objects_to_tenant_prefix.py --dry-run` → revisión de conteos → ejecución real → verificación origen=destino → smoke de lectura de 10 objetos al azar vía app. Evidencia en `docs/audits/EVIDENCIA_MINIO_MIGRACION_<fecha>.md`.
3. **Backup smoke en cron real del VPS** (ya corre ad-hoc; formalizarlo): cron nocturno documentado + alerta si el reporte falla o no se genera (script `check_backup_smoke_freshness.py` que el ciclo ambiental del tenant default ejecuta y propone item WorkLoom si el último smoke >48h — usa la arquitectura E2-5, detector nuevo read-only).
4. Rotación programada: entrada en `ENT_GOB_PROTOCOLOS` (KB) con cadencia trimestral de rotación y responsable.

**Archivos:** `app/scripts/check_backup_smoke_freshness.py`, `app/src/ambient_detectors.py` (detector `stale_backup_smoke`), evidencias en `docs/audits/`.
**Tests:** `test_e5_2_backup_freshness_detector.py` (detector propone item si stale; no propone si fresco; read-only).
**DoD:** tres evidencias commiteadas; detector verde; cron corriendo. **Esfuerzo:** 1 sesión Fugu + ½ día Ops.

### E5-3 — KB H3 cargada y catálogo sin huecos de definición

**Objetivo:** el conocimiento real entra al sistema y la needs-list del catálogo se resuelve con el CEO — se acaba el `DEFINITION_PENDING` masivo.

**Tareas:**
1. **Carga H3:** el CEO entrega los archivos Marluvas/Tecmater (insumo de negocio — DoD de este hito lo exige, responsable CEO, fecha pactada en la ola 2). Ejecutar `python app/scripts/ingest_kb_h3.py` → reporte de carga → verificación de 10 citas al azar por dev+AM (¿el chunk citado dice lo que la respuesta afirma?). Evidencia en `docs/audits/EVIDENCIA_KB_H3_<fecha>.md`.
2. **Sesiones de definición de dominio:** 2-3 sesiones CEO+Arquitecto sobre la needs-list del catálogo v1.1: para cada skill en `DRAFT`/`DEFINITION_PENDING`, decidir: definir ahora (→ manifest v2 completo, SHADOW), posponer con razón, o descartar. Salida: `ENT_FB_SKILL_CATALOG_v1.2.md` (reemplaza, con changelog) con CERO skills sin veredicto — un "pospuesto con razón y fecha" es un veredicto; un hueco no.
3. Fugu materializa los definidos (mismo pipeline de olas 3-5 de E3-4: compiler v2, SHADOW, golden placeholders honestos).
4. Con KB H3 cargada: desbloquear golden cases de PACK 2 (comex) — proponer los 3 primeros desde runs reales con el harvester.

**Tests:** `test_e5_3_catalog_v12.py` (todo skill del catálogo tiene estado terminal o pospuesto-con-razón; los nuevos compilan; ninguno ACTIVE ni auto_apply).
**DoD:** KB H3 con citas verificadas; catálogo v1.2 sin huecos; PACK 2 con ≥3 golden candidates reales. **Esfuerzo:** 1-2 sesiones Fugu + 3 sesiones CEO.

### E5-4 — Tributario live: ATV Costa Rica end-to-end

**Objetivo:** la primera factura electrónica REAL sale del sistema, con certificado, contra la autoridad de verdad.

**Tareas:**
1. **Timebox de verificación (3 días, dev+AM):** ejecutar `PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1` para ATV: registro en Hacienda CR, credenciales del ambiente de pruebas, documentación de URLs oficiales. Resultado a la tabla del playbook y al catálogo. (SAT/DIAN: solo registrar el hallazgo, sin activar.)
2. **Certificados HE2-9:** compra e instalación del certificado de firma para el tenant MWT (responsable CEO — es el ítem de mayor lead time del roadmap: INICIARLO EL DÍA 1 de E5, no en esta ola). Almacenamiento: `TenantSecretStore` namespace `connectors/tax/atv/cert` (mecanismo E3-4 ya gateado).
3. **Código de cierre del conector:** configurar `connectors.tax.atv.*` en tenant_settings del tenant MWT con las URLs verificadas (deja de haber `[PENDIENTE]` para ATV); pasar `mode=sandbox` → pruebas contra el ambiente de Hacienda con `SKILL_FE_STATUS_CHECK` y los SKILL_FE_* de PACK 1 → corregir lo que el mundo real rompa (presupuesto: 2 sesiones) → `mode=live`.
4. **Primera e-factura real:** emitir sobre el tenant MWT (dogfood, factura propia real de MWT) con firma, envío a ATV y verificación de aceptación. El PDF deja de decir "no fiscal" SOLO para tenants con certificado configurado (flag derivado: `has_tax_certificate`).
5. Evidencia: `docs/audits/EVIDENCIA_EFACTURA_ATV_<fecha>.md` (clave numérica, estado de aceptación, capturas de auditoría — sin datos sensibles del receptor).

**Archivos:** `app/src/connectors/tax_authority.py` (ajustes del mundo real), `app/src/billing.py` (flag no-fiscal condicional), tenant_settings vía API, evidencias.
**Tests:** `test_e5_4_atv_sandbox_contract.py` (contra fixtures grabadas del sandbox real — grabar respuestas reales anonimizadas como cassettes), `test_e5_4_pdf_fiscal_flag.py`.
**DoD:** factura electrónica MWT aceptada por ATV en live; SAT/DIAN documentados; cassettes de contrato en la suite. **Esfuerzo:** 2-3 sesiones Fugu + timebox 3d dev/AM + compra CEO.

### E5-5 — PACK 1 y PACK 3 a ACTIVE por uso real

**Objetivo:** los dos packs core cruzan el umbral de promoción con datos, no con fe.

**Tareas:**
1. Rutina de dogfood semanal (`PLB_FB_PROMOTION_READINESS_DOGFOOD_v1`): correr los skills de PACK 1 (fiscalidad, ahora con ATV real) y PACK 3 (cobranza, sobre las facturas reales de MWT) con casos reales; proponer golden cases con el harvester; curador aprueba/verifica.
2. Meta por pack: ≥3 golden cases `approved+verified` y track record ≥100 runs / ≥90% acceptance (los umbrales existentes de `promote_pack`).
3. Promoción: `promote_pack` manual con token cuando el tablero de readiness lo muestre verde. PACK 1 primero.
4. Si a las 3 semanas el volumen de dogfood no alcanza 100 runs: NO bajar el umbral — ampliar el uso (más facturas reales de MWT por el sistema) y documentar la curva en el reporte quincenal. El umbral es el contrato de calidad.

**DoD:** PACK 1 y PACK 3 en ACTIVE; tablero de readiness como evidencia; cero golden fabricado. **Esfuerzo:** operación 3-4 semanas; código 0 (todo existe).

### E5-6 — Design partner: onboarding, soak de 30 días y primera factura pagada

**Objetivo:** el gate comercial completo se cumple con un tenant externo real.

**Tareas:**
1. **Selección (semana 1 de E5):** CEO elige del ranking de `ENT_FB_VERTICAL_CANDIDATES_v2` (lead: distribución B2B técnica) y agenda. Backup: candidato #2 del ranking con trigger automático si el #1 no firma en 3 semanas.
2. **Acuerdo de datos:** Fugu genera `docs/faberloom/SCH_FB_ACUERDO_DATOS_BETA_v1.md` — plantilla con: alcance de datos, visibilidad y sellado (key broker explicado en lenguaje de negocio), NO-entrenamiento con sus datos, SLA beta (referencia PLB_FB_SOPORTE_SLA_BETA), beta 90 días con precio preferente, terminación y exportación de datos. Los términos económicos son `[PENDIENTE — decisión CEO]` con campo explícito. Revisión legal humana antes de firmar (responsable CEO).
3. **Onboarding asistido:** ejecutar `PLB_FB_TENANT_ONBOARDING_v1` (aprobación manual, bootstrap, identidad del agente bautizada por el tenant, carga de su KB inicial, workspaces por proceso, usuarios). El agente vivo hace el onboarding conversacional (E4-7.3 ya existe).
4. **Soak instrumentado (30 días):** reporte semanal automatizado — script `app/scripts/soak_report.py` que compone: health del tenant, casos procesados, HITL aprobados/rechazados, costo, incidentes, canarios de contaminación (corrida programada). Salida a `docs/audits/SOAK_<tenant>_S<N>.md`. Criterios: ≥10 casos reales, 0 fugas (canarios verdes las 4 semanas), disponibilidad sin P0.
5. **Primera factura:** al día 30+, factura manual (billing existente; e-factura si el partner es CR y E5-4 cerró) → pago por transferencia → conciliación con PACK 3 (¡el pack cobra su propia factura — ese es el caso golden definitivo!).

**Archivos:** `docs/faberloom/SCH_FB_ACUERDO_DATOS_BETA_v1.md`, `app/scripts/soak_report.py`, `app/tests/test_e5_6_soak_report.py` (agregados correctos, sin contenido, aislamiento).
**DoD (= GATE DE SALIDA DE E5):** tenant externo activo ≥30 días; ≥10 casos reales; 0 fugas; primera factura PAGADA y conciliada; acuerdo firmado archivado. **Esfuerzo:** 1 sesión Fugu + 5 semanas de operación comercial.

## §3. Riesgos P0 de la etapa

| Riesgo | Mitigación |
|---|---|
| Certificado HE2-9 demora semanas | Compra inicia el DÍA 1 de E5 (no en la ola 3); ATV sandbox no lo requiere para avanzar |
| Design partner #1 no firma | Candidato #2 con trigger a los 21 días (DA5-2) |
| Natural degrada en producción | ACE degrada solo + rollback ejercitado en E5-1.3 antes de tocar al partner |
| KB H3 nunca llega | El DoD de E5-3 lo exige con responsable y fecha; sin H3, PACK 2 queda pospuesto-con-razón en el catálogo v1.2 (veredicto, no hueco) y E5 CIERRA igual — H3 no bloquea el gate |
| Fuga en el tenant externo | Canarios de contaminación en el soak semanal; cualquier fuga = P0, soak se reinicia tras remediación |
| Dogfood no alcanza 100 runs | Ampliar uso real, no bajar umbral (E5-5.4) |

## §4. Gate de salida

E5 cierra cuando: (1) E5-6 DoD completo (el gate comercial histórico), (2) ≥3 workspaces en `natural` estables, (3) PACK 1 ACTIVE (PACK 3 puede cerrar 1 semana después si la conciliación de la primera factura ES su caso 100), (4) las 3 evidencias de seguridad operativa commiteadas, (5) acta `docs/audits/ACTA_ETAPA5_<fecha>.md` con formato estándar. Con este gate verde, E6 (apertura) arranca de inmediato.

## Changelog

- v1.0.0 (2026-07-12): Creación. Los pendientes H1-H9 de E3/E4 formalizados como hitos con DoD; decisiones DA5-1..DA5-5.
