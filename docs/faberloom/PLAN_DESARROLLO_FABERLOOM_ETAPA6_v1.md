# PLAN_DESARROLLO_FABERLOOM_ETAPA6_v1 — Apertura comercial self-serve

id: PLAN_FB_ETAPA6
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 6: abrir el registro público con planes reales, billing recurrente y soporte operativo
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · PLB_FB_E4_APERTURA_SIGNUP_v1 · ENT_FB_PRICING_TIERS_v1 · SPEC_FABERLOOM_MULTITENANT_BRANDING_v1 · SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1 · PLB_FB_SOPORTE_SLA_BETA_v1

---

## §0. Precondición y decisiones

**Precondición dura:** gate de salida de E5 verde (tenant externo con soak y factura pagada). E6 convierte ese caso de éxito en una puerta abierta.

**Decisiones del Arquitecto:**
- **DA6-1. Captcha: Cloudflare Turnstile.** Gratuito, sin fricción de usuario, widget simple. El stub de E4-7 ya dejó el seam (`signup.captcha.*`); solo se implementa el proveedor. Alternativa descartada: reCAPTCHA (privacidad y fricción).
- **DA6-2. Planes de lanzamiento: FREE (evaluación), PRO, BUSINESS** — 3 tiers, mapeados desde `ENT_FB_PRICING_TIERS_v1`. Los PRECIOS son dato de negocio: el hito E6-0 los exige como insumo CEO con campo explícito; el código se escribe contra constantes de configuración de plataforma, no contra números en duro.
- **DA6-3. Email transaccional: SMTP propio del dominio con SPF/DKIM/DMARC** (verificación, reset, avisos de billing). Sin proveedor externo nuevo en E6; si el volumen lo exige, se evalúa en E10. El conector SMTP hardened de E3 se reutiliza.
- **DA6-4. Billing recurrente = generación automática de borradores + cobro MANUAL.** Nada de pasarela de pago en E6 (transferencia + conciliación PACK 3, que ya está ACTIVE por E5). Pasarela de pago se decide en E9 con datos de fricción reales.
- **DA6-5. Branding por tenant: logo + paleta acotada** según `SPEC_FABERLOOM_MULTITENANT_BRANDING_v1`, sin CSS libre (superficie de ataque y de fealdad). Rama `e6-apertura`.

## §1. Mapa de olas

| Ola | Hitos |
|---|---|
| 1 | E6-0 (planes/pricing), E6-1 (defensas reales) |
| 2 | E6-2 (onboarding wizard), E6-4 (billing recurrente) |
| 3 | E6-3 (apertura ON), E6-5 (soporte operativo) |
| 4 | E6-6 (branding por tenant), E6-7 (acta y estabilización) |

## §2. Detalle por hito

### E6-0 — Planes y pricing reales

**Objetivo:** los tiers dejan de ser scaffold: límites, features y precios definidos y aplicados fail-closed.

**Tareas:**
1. **Insumo CEO (DoD lo exige):** tabla de 3 tiers con precio mensual, límites (usuarios, workspaces, storage GB, budget IA USD/mes, packs incluidos) y features (WhatsApp sí/no, e-factura sí/no, BYO keys) — partiendo de `ENT_FB_PRICING_TIERS_v1` actualizado a v2 con los números firmados.
2. Código: extender `PlanLimits` (`app/src/plans.py`) con los campos nuevos (packs_included, features_json); tabla de planes en config de plataforma (Foundation) editable por platform_admin — NO números en duro. `enforce_*` existentes cubren usuarios/workspaces/budget; añadir `enforce_storage` (suma de objetos por tenant vs límite, chequeado en upload) y `enforce_feature(feature_key)` (gate simple usado por WhatsApp/e-factura/BYO).
3. UI: página de planes en el signup (`signup.jsx`/`signup.html`) y vista "Mi plan" para el owner (límites, uso actual desde el ledger, botón "solicitar upgrade" → item para platform_admin; el upgrade lo ejecuta platform_admin con el endpoint de change-plan existente).
4. Migración de tenants existentes: script `app/scripts/assign_plans_to_existing_tenants.py` (default BUSINESS para MWT, plan pactado para el design partner).

**Archivos:** `plans.py`, `platform_admin.py` (CRUD de planes), `models.py` (migración vN: tabla `platform_plan` con campos latentes+RLS n/a —tabla de plataforma, documentar excepción—), `signup.jsx`, `app.jsx` (Mi plan), `docs/faberloom/ENT_FB_PRICING_TIERS_v2.md`.
**Tests:** `test_e6_0_plans.py` (límites fail-closed por tier: storage, feature gates, budget; upgrade cambia límites en vivo; tenant sin plan = FREE por default, jamás ilimitado).
**DoD:** 3 tiers operativos aplicados a los tenants existentes; pricing firmado en la KB. **Esfuerzo:** 2 sesiones Fugu + decisión CEO.

### E6-1 — Defensas de abuso reales

**Objetivo:** el signup aguanta internet abierto.

**Tareas:**
1. **Turnstile:** widget en `signup.html/jsx`; verificación server-side en `auth.public_signup` (`https://challenges.cloudflare.com/turnstile/v0/siteverify`); secrets (site key/secret key) en config de plataforma. Fail-closed: sin verificación válida no hay signup. El stub de E4-7 se reemplaza, manteniendo la interfaz para tests (modo test con token de bypass SOLO bajo `FABERLOOM_ENV=test`).
2. Endurecer lo existente: `signup.daily_limit` con valor real (decisión: 50/día al abrir, ajustable por platform_admin), lista de dominios desechables poblada desde una lista mantenida en config (semilla: lista pública curada, actualizable sin deploy), rate limit por IP verificado bajo proxy (respetar `X-Forwarded-For` SOLO desde el proxy propio — configurar `trusted_proxies`).
3. **Email transaccional serio:** SPF/DKIM/DMARC del dominio de envío (Ops, con evidencia); plantillas de verificación/bienvenida con la marca; reintentos con backoff en el envío de verificación.
4. Monitoreo de abuso: métricas en platform_admin (signups/día, tasa de verificación, tenants suspendidos) + detector ambiental `signup_abuse_spike` (propone item WorkLoom al platform admin si signups/hora > umbral).

**Archivos:** `auth.py`, `signup.jsx/html`, `platform_admin.py` (métricas), `ambient_detectors.py`, `connectors/smtp.py` (retries), evidencia DNS en `docs/audits/`.
**Tests:** `test_e6_1_turnstile.py` (fail-closed, bypass solo en test env), `test_e6_1_abuse_defenses.py` (daily limit, desechables, XFF solo de proxy confiable).
**DoD:** signup rechaza bots y spam por defecto; correo transaccional entregable (no spam folder — verificado con mail-tester o equivalente, evidencia). **Esfuerzo:** 2 sesiones Fugu + ½ día Ops DNS.

### E6-2 — Onboarding self-serve completo (wizard M07 + agente)

**Objetivo:** un desconocido pasa de registro a primer valor sin ayuda humana.

**Tareas:**
1. Implementar el wizard de bootstrap sobre la spec `SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1`: pasos post-verificación — (a) bautiza a tu agente (display name → entity_identity), (b) elige tu vertical (work type packs de `ENT_FB_WORK_TYPE_PACK_v1` → activa skills SHADOW del pack como sugerencias), (c) conecta tu correo (opcional, connector IMAP/SMTP existente), (d) sube tus primeros documentos (upload → KB), (e) primer chat con el agente (el onboarding conversacional de E4-7.3).
2. El wizard es reanudable (estado en tenant_settings `onboarding.step`), saltable, y NUNCA bloquea el acceso a la app.
3. Métricas de funnel: evento auditado por paso (`onboarding.step.completed`) + panel en platform_admin (conversión por paso, agregados).
4. Plantillas por vertical: para el vertical lead (distribución B2B), workspaces sugeridos pre-nombrados y 2-3 rutinas de ejemplo en estado borrador (nada auto-activo).

**Archivos:** `app/src/onboarding.py` (router del wizard), `app/static/js/onboarding.jsx`, `foundation/m07_bootstrap.py` (reusar), `app.jsx` (entrada), migración vN+1 si hace falta estado (preferir tenant_settings).
**Tests:** `test_e6_2_wizard.py` (flujo completo, reanudable, saltable, aislamiento), `test_e6_2_funnel_metrics.py` (solo agregados a platform_admin).
**DoD:** un tenant de prueba creado por signup auto llega a "primer chat con documentos propios" sin intervención humana; funnel medible. **Esfuerzo:** 3 sesiones Fugu.

### E6-3 — Apertura: signup.approval=auto ON

**Objetivo:** encender, con checklist y con la mano en el rollback.

**Tareas:**
1. Ejecutar el checklist de `PLB_FB_E4_APERTURA_SIGNUP_v1` (ampliarlo primero a v2 con lo construido en E6-0..E6-2: planes activos, Turnstile verificado, wizard funcional, monitoreo de abuso, DNS de correo, rollback = flag a manual).
2. Encender `signup.approval=auto` en producción. Primera semana: revisión diaria del panel de crecimiento por el CEO/platform_admin; los primeros 10 tenants auto reciben una revisión manual post-hoc (¿reales?, ¿uso legítimo?).
3. Anuncio controlado (canal del CEO; el alcance del anuncio es decisión de negocio, insumo del hito).

**DoD:** signup auto activo 2 semanas sin incidente P0 y sin flood; ≥N tenants reales registrados (N objetivo lo fija el CEO en el anuncio; el sistema debe aguantar 50/día). **Esfuerzo:** operación; código 0 (o fixes menores).

### E6-4 — Billing recurrente semi-automático

**Objetivo:** cada tenant activo recibe su factura mensual sin que un humano la componga.

**Tareas:**
1. Generador mensual: tarea del ciclo ambiental del tenant de plataforma (o cron del VPS — decisión: cron, es contabilidad, no agente) `app/scripts/generate_monthly_invoices.py`: por cada tenant activo con plan de pago, compone `manual_invoice` en `draft` con: cargo del plan + excedentes de uso (ledger: budget IA consumido sobre lo incluido, con el recargo BYO ya existente) + detalle por línea. NADA se envía automático: el draft queda para revisión de platform_admin (HITL de facturación).
2. Envío: platform_admin revisa y marca `sent` (email al owner con el PDF — e-factura si el tenant es CR y tiene certificado; no-fiscal si no).
3. Dunning: los skills de PACK 3 (ACTIVE desde E5) operan la cobranza de FaberLoom mismo — secuencia de recordatorios draft-first sobre facturas `sent` vencidas. Dogfood perpetuo del pack.
4. Conciliación: flujo existente (`payment_reconciliation` + match). Panel de cartera para platform_admin (agregados: facturado/cobrado/vencido por mes).

**Archivos:** `app/scripts/generate_monthly_invoices.py`, `billing.py` (líneas de detalle + envío), `platform_admin.py` (panel cartera), `app/static/js/health_dashboard.jsx` o vista propia.
**Tests:** `test_e6_4_monthly_invoices.py` (composición correcta plan+excedentes; idempotente por mes/tenant; draft-first; aislamiento), `test_e6_4_dunning_dogfood.py` (recordatorio como draft HITL).
**DoD:** primer ciclo mensual completo: generación → revisión → envío → ≥1 pago conciliado. **Esfuerzo:** 2 sesiones Fugu + operación mensual.

### E6-5 — Soporte operativo

**Objetivo:** los tenants tienen adónde acudir y el equipo tiene proceso.

**Tareas:**
1. `PLB_FB_SOPORTE_SLA_BETA` → v2 con los datos reales que E5/E6 definieron (canal real, horario, severidades S1-S4 con tiempos, escalamiento al CEO para S1). Los datos de contacto son insumo CEO exigido por el DoD.
2. In-app: enlace "Soporte" en el shell (mailto/canal + el agente vivo como primera línea: el agente responde FAQs desde una KB de soporte propia del tenant de plataforma, visible a todos los tenants como knowledge global read-only — nueva visibilidad `platform_public` en el key broker: decisión DA6-6, INDEX+CONTENT para todos, escritura solo platform_admin).
3. Runbook de incidentes: `PLB_INCIDENT_RESPONSE` (ya existe en KB MWT) adaptado a FaberLoom: quién apaga qué (kill switches por tenant/global, flag de signup, rollback de deploy) — `docs/faberloom/PLB_FB_INCIDENT_RESPONSE_v1.md`.
4. Status: endpoint público `GET /api/status` (up, versión, sin datos internos) para que los tenants verifiquen disponibilidad.

**Archivos:** `key_broker.py` (visibilidad platform_public — con tests de que NO abre nada tenant-privado), `api.py` (/api/status público), `app.jsx` (enlace soporte), PLBs.
**Tests:** `test_e6_5_platform_public_kb.py` (lectura global solo de lo marcado; jamás contenido de tenant), `test_e6_5_status_endpoint.py`.
**DoD:** SLA v2 publicado; agente responde FAQs; runbook de incidentes ensayado 1 vez (simulacro documentado). **Esfuerzo:** 2 sesiones Fugu + simulacro ½ día.

### E6-6 — Branding por tenant

**Objetivo:** cada tenant ve SU marca sin romper el sistema de diseño.

**Tareas:**
1. Según `SPEC_FABERLOOM_MULTITENANT_BRANDING_v1`: logo del tenant (upload → objeto cifrado → servido con cache), color primario y acento (2 variables CSS acotadas con validación de contraste WCAG AA automática — rechazar paletas ilegibles), nombre comercial en el shell. NADA de CSS libre (DA6-5).
2. Backend: `tenant_settings` claves `branding.*`; endpoint de upload de logo con validación (formato, tamaño, dimensiones); el shell resuelve branding al cargar sesión.
3. El agente conserva su identidad (nombre del agente ≠ marca del tenant; ambos visibles).
4. Leer `SKILL_FRONTEND_TEN_PRINCIPLES_V2` y los tokens de `Diseños/` antes de tocar el shell.

**Archivos:** `app.jsx` + `css/main.css` (variables), `api.py` (branding endpoints), `tenant_settings.jsx` (sección branding).
**Tests:** `test_e6_6_branding.py` (upload validado, contraste rechaza ilegible, aislamiento del logo por tenant, default FaberLoom sin config).
**DoD:** el design partner ve su logo y colores; tenants sin config ven FaberLoom estándar. **Esfuerzo:** 2 sesiones Fugu.

### E6-7 — Estabilización y acta

**Tareas:** 2 semanas de operación abierta observada; corrección de fricciones (presupuesto 2 sesiones); contamination suite completa re-ejecutada con los tenants reales nuevos; `docs/audits/ACTA_ETAPA6_<fecha>.md` formato estándar; merge a main + tag `e6-cierre` + deploy desde main; bloques KB (IDX, ENT_GOB_PENDIENTES) actualizados.
**DoD (= GATE DE SALIDA):** ≥10 tenants activos self-serve; funnel de onboarding con conversión medida; primer ciclo de billing mensual completado con ≥1 pago; 0 incidentes P0 en las 2 semanas de estabilización; acta commiteada.

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| Flood de signups maliciosos | Turnstile + daily_limit + revisión post-hoc de los primeros 10 + rollback a manual en 1 flag |
| Costo IA de tenants FREE se dispara | Budget por plan fail-closed (existe) + suspensión automática por exceso + FREE con budget mínimo |
| `platform_public` abre un agujero de visibilidad | Diseño explícito en key broker con tests dedicados; solo platform_admin escribe; nada tenant-privado jamás |
| Facturas mal compuestas | Draft-first SIEMPRE: platform_admin revisa antes de enviar; idempotencia por mes/tenant |
| Branding rompe accesibilidad | Validación de contraste automática que RECHAZA, no advierte |

## Changelog

- v1.0.0 (2026-07-12): Creación. Decisiones DA6-1..DA6-6; billing recurrente sin pasarela (se re-evalúa en E9).
