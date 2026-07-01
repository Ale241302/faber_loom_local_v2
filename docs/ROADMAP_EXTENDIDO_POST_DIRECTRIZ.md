# ROADMAP EXTENDIDO — Post-Directriz Artefactos Modulares
aplica_a: [MWT]
## MWT.ONE — Sprints 20-23 detallados
## Fecha: 2026-03-29 · Arquitecto: Claude Opus
## Inputs: ROADMAP_CONVERGENCIA_MWTONE + DIRECTRIZ_ARTEFACTOS_MODULARES + ROADMAP_SPRINTS_17_27

---

## CONTEXTO

Sprint 19 está en ejecución (frontend expedientes). La DIRECTRIZ_ARTEFACTOS_MODULARES introduce un cambio de paradigma: la **proforma (ART-02) pasa a ser la unidad operativa**, no el expediente. Esto requiere cambios en modelo de datos, artifact policy, gates, y rendering frontend que no estaban en el roadmap.

Este documento extiende los Sprints 20-23 para absorber esos cambios sin perder el scope que ya estaba planificado (emails, monitor, pricelists, autogestión).

**Estado de sprints anteriores (no tocar):**
- Sprint 17: DONE — modelos base (EPL, FactoryOrder, ExpedientePago, campos operativos)
- Sprint 18: DONE — endpoints backend, BrandSizeSystem, fixes Agent-A
- Sprint 19: EN EJECUCIÓN — frontend expedientes + tallas en Brand Console

**SPEC_GAPs resueltos por el arquitecto (pendientes confirmación CEO):**
- SG-01: ArtifactPolicy arranca como constante Python, migra a DB en S23+
- SG-02: Proforma Flujo C → descarga manual primero, email post-S21
- SG-03: ART-01 auto-generada → registro digital + PDF bajo demanda
- SG-04: ART-05 multi-proforma → M2M (HR-12)
- SG-05: Cambio modo B→C → void automático de artefactos incompatibles + confirmación CEO
- SG-06: operated_by → CharField con default "Muito Work Limitada"

---

## SPRINT 20 — Modelo Proformas + ArtifactPolicy Backend
**Prioridad:** P0 (bloqueante para S20B, S21B, S24)
**Duración estimada:** 1.5 semanas
**Agente:** AG-02 Backend
**Dependencia:** Sprint 19 DONE (necesita EPL y bundle existentes para extender)
**Refs:** DIRECTRIZ_ARTEFACTOS_MODULARES (HR-7 a HR-15), POL_ARTIFACT_CONTRACT, ENT_OPS_STATE_MACHINE (FROZEN)

### Objetivos
1. Transformar la proforma (ART-02) de artefacto simple a unidad operativa con mode propio
2. Implementar ArtifactPolicy calculada por backend (eliminar decisión del frontend)
3. Flexibilizar C1 para los 3 flujos de inicio
4. Vincular líneas a proformas, no directamente al expediente

### Fase 0 — Modelo de datos (migración aditiva)

| ID | Tarea | HR | Detalle |
|----|-------|----|---------|
| S20-01 | FK `proforma` nullable en `ExpedienteProductLine` | HR-10 | `proforma = ForeignKey(ArtifactInstance, null=True, blank=True, limit_choices_to={'artifact_type': 'ART-02'}, on_delete=SET_NULL, related_name='lines')`. Se mantiene `expediente` FK directo para queries rápidas. |
| S20-02 | `parent_proforma` FK nullable en `ArtifactInstance` | HR-11 | Para vincular ART-04/05/09/10 a su proforma. `parent_proforma = ForeignKey('self', null=True, blank=True, limit_choices_to={'artifact_type': 'ART-02'}, on_delete=SET_NULL, related_name='child_artifacts')` |
| S20-03 | M2M `proformas` en ART-05 (embarque multi-proforma) | HR-12 | `ArtifactInstance` con artifact_type='ART-05' puede vincular a N proformas. Implementar como campo M2M en payload JSON (array de proforma IDs) + validación en serializer. |
| S20-04 | Validar que payload de ART-02 incluye `mode` | HR-8/9 | Enum: `mode_b`, `mode_c`, `default`. El mode vive en `payload.mode`, NO como campo flat en Expediente. Proformas del mismo expediente pueden tener modos distintos. |

### Fase 1 — ArtifactPolicy engine

| ID | Tarea | HR | Detalle |
|----|-------|----|---------|
| S20-05 | Crear `backend/apps/expedientes/services/artifact_policy.py` | HR-1/2 | Constante `ARTIFACT_POLICY` con dict completo por brand × mode (Parte VII de la directriz). 4 configs: marluvas/mode_b, marluvas/mode_c, rana_walk/default, tecmater/default. |
| S20-06 | Función `resolve_artifact_policy(expediente)` | HR-1 | Sin proformas → policy genérica REGISTRO. Con proformas → unión de policies por mode de cada una. Sets → listas para serialización JSON. |
| S20-07 | Endpoint GET `/api/ui/expedientes/{id}/` retorna `artifact_policy` | HR-1 | Agregar al bundle existente el campo `artifact_policy` calculado por `resolve_artifact_policy()`. |

### Fase 2 — C1 flexible + C5 actualizado

| ID | Tarea | HR | Detalle |
|----|-------|----|---------|
| S20-08 | Actualizar `handle_c1`: mínimo `client_id` + `brand_id` | HR-13 | OC, líneas y proformas son opcionales en creación. Backward compatible: POST con campos viejos sigue funcionando. |
| S20-09 | Actualizar `validate_c5_gate` | HR-13 | Gate real para avanzar a PRODUCCION: (1) ART-01 existe, (2) ≥1 ART-02 completada, (3) todas las líneas asignadas a una proforma, (4) cada proforma tiene mode asignado. |
| S20-10 | Endpoint POST `reassign-line/` | HR-10 | Mover línea de una proforma a otra (antes de PRODUCCION). Valida que ambas proformas pertenecen al mismo expediente. |

### Fase 3 — Void por cambio de modo

| ID | Tarea | HR | Detalle |
|----|-------|----|---------|
| S20-11 | Void automático de artefactos incompatibles al cambiar mode | SG-05 | Si proforma cambia de mode_b → mode_c: void ART-10 (factura comisión) si existe. Si mode_c → mode_b: void ART-09 (factura MWT). Requiere confirmación CEO (flag `confirm_void=true` en payload). EventLog registra el void. |
| S20-12 | Tests completos | — | (1) Crear expediente sin OC → OK. (2) 2 proformas modo mixto → policy correcta. (3) C5 con línea sin proforma → bloquea. (4) Policy Rana Walk no incluye ART-03/04/08. (5) Mover línea entre proformas → OK. (6) Cambiar mode → void automático. (7) ART-05 multi-proforma. (8) C1 backward compat. |

### Migración
- Una sola migración aditiva: AddField(proforma FK en EPL), AddField(parent_proforma FK en ArtifactInstance)
- 0 AlterField, 0 RemoveField, 0 data migration destructiva
- Seed: `ARTIFACT_POLICY` es constante Python, no necesita migración

### Gate Sprint 20
- [ ] Los 8 checks de verificación de la Parte X de la directriz pasan
- [ ] C1 funciona con solo client_id + brand_id
- [ ] 2 proformas con modos distintos en mismo expediente
- [ ] Policy del bundle refleja unión de modes
- [ ] Líneas se mueven entre proformas
- [ ] Tests existentes siguen verdes

### Excluido explícitamente
- Frontend de proformas (→ S20B)
- Vista portal cliente (→ S20B)
- Emails/notificaciones (→ S21)
- BrandWorkflowPolicy en DB (→ S23+)
- Tecmater policy seed (cuando haya datos — SG-01)

---

## SPRINT 20B — Frontend Policy-Driven + Vista Proformas
**Prioridad:** P0 (bloqueante para portal B2B funcional)
**Duración estimada:** 1-1.5 semanas
**Agente:** AG-03 Frontend
**Dependencia:** Sprint 20 DONE (backend artifact_policy en bundle)
**Refs:** DIRECTRIZ_ARTEFACTOS_MODULARES (HR-1 a HR-6, Parte VI)

### Objetivos
1. Eliminar toda lógica de artefactos hardcodeada del frontend
2. Renderizar artefactos basándose exclusivamente en artifact_policy del bundle
3. Vista CEO con proformas como unidad organizativa
4. Vista portal cliente: OC → líneas individuales con estado

### Items

| ID | Tarea | HR | Detalle |
|----|-------|----|---------|
| S20B-01 | Eliminar de `ExpedienteAccordion.tsx`: `STATE_ARTIFACTS`, `ARTIFACT_COMMAND_MAP`, `ARTIFACT_LABELS` | HR-1 | Reemplazar por consumo de `data.artifact_policy` del bundle. El frontend solo renderiza lo que el backend dice. |
| S20B-02 | Componente `ArtifactSection` genérico | HR-1/2 | Recibe `{ required, optional, gate_for_advance }` y renderiza: required siempre visible, optional como botón "+ Agregar", gate como indicador de bloqueo para avanzar. |
| S20B-03 | Solo mostrar estado actual + anteriores | HR-4 | Estados anteriores: collapsed con indicador completado. Estados futuros: NO se renderizan. Nunca mostrar artefactos grayed-out de estados futuros. |
| S20B-04 | Opcionales = "+ Agregar [nombre]" | HR-5 | No mostrar como "Pendiente". Si no se crea, no existe. Botón desaparece si el artefacto ya fue creado. |
| S20B-05 | Artefacto completado = read-only | HR-6 | Ref POL_ARTIFACT_CONTRACT sección C. Corrección vía C19 (Supersede) o C20 (Void, CEO-ONLY). |
| S20B-06 | Vista CEO: expediente → N proformas | HR-7/8 | Layout §6.1 de la directriz: cada proforma como sección con su mode badge, sus líneas, y su cadena de artefactos. Botón "+ Crear nueva proforma". |
| S20B-07 | Asignar líneas a proformas + mover | HR-10 | Drag o select para mover líneas entre proformas. Endpoint `reassign-line/` de S20. Solo antes de PRODUCCION. |
| S20B-08 | Labels de artefactos desde constante | — | Usar tabla Parte VIII de la directriz: ART-01→"Orden de Compra del Cliente", etc. Constante en frontend (no hardcoded por estado). |
| S20B-09 | Vista portal: OC → líneas con estado | §6.2 | El cliente ve su OC como ancla, líneas individuales con estado. NO ve proformas, modos, costos. Señal sutil "Operado por Muito Work" en líneas Mode C. |
| S20B-10 | Botón "Avanzar" con validación de gate | HR-2 | Antes de avanzar de estado: verificar que todos los artefactos en `gate_for_advance` del estado actual están completados. Deshabilitar botón si faltan, con tooltip indicando cuáles. |

### Gate Sprint 20B
- [ ] 0 constantes de artefactos hardcodeadas en frontend
- [ ] Expediente Rana Walk NO muestra ART-03, ART-04, ART-08
- [ ] Opcional muestra botón "+ Agregar" no "Pendiente"
- [ ] 2 proformas visibles con modos distintos
- [ ] Líneas se pueden mover entre proformas
- [ ] Portal muestra líneas sin proformas/modos
- [ ] Gate de avance bloquea correctamente

### Dependencias internas
```
S20B-01 (limpiar hardcoded) → S20B-02 (componente genérico) → S20B-03..05 (comportamiento)
S20B-06 (vista proformas) → S20B-07 (asignar líneas)
S20B-08 (labels) → paralelo con todo
S20B-09 (portal) → independiente
S20B-10 (gate UI) → después de S20B-02
```

---

## SPRINT 21 — Notificaciones Email + Cobranza
**Prioridad:** P1
**Duración estimada:** 1 semana
**Agente:** AG-02 Backend
**Dependencia:** Sprint 18 DONE (hook post_command_hooks). Puede correr en paralelo con S20B.
**Pendiente CEO:** CEO-28 (email provider: SMTP/SendGrid/SES + contact_email en ClientSubsidiary)

### Objetivos
1. Sistema de notificaciones email por cambio de estado del expediente
2. Cron de cobranza para pagos vencidos
3. Templates editables por CEO
4. Soporte de envío a nivel proforma (post-S20: notificar por proforma, no solo por expediente)

### Items

| ID | Tarea | Detalle |
|----|-------|---------|
| S21-01 | Modelos `NotificationTemplate` + `NotificationLog` | Template: name, event_type, subject_template, body_template (Jinja2), is_active, brand FK nullable. Log: template FK, expediente FK, proforma FK nullable (NUEVO — para notificaciones a nivel proforma), recipient_email, sent_at, status, error. |
| S21-02 | Data migration: 8 templates seed | Los 8 del sistema viejo que Agent-A identificó: registro, avance estado, pago recibido, pago vencido, despacho, entrega, factura disponible, proforma enviada (NUEVO — Flujo C de la directriz). |
| S21-03 | Celery task `send_expediente_notification` | Recibe (template_name, expediente_id, proforma_id=None, extra_context={}). Resuelve destinatario: para MWT → CEO email. Para cliente → contact_email de ClientSubsidiary. Renderiza Jinja2, envía, loguea. |
| S21-04 | Hook en dispatcher: post-éxito → `.delay()` | Cada command exitoso dispara notificación. Mapeo: C1→registro, C5→produccion, C11→despacho, etc. S20 agrega: C5 valida por proforma → notificación incluye proforma_number. |
| S21-05 | Celery Beat: `check_overdue_payments` | Diario 8am. Usa `payment_grace_days` de ClientSubsidiary (S17). Detecta pagos vencidos → envía email cobro → registra en `CollectionEmailLog`. |
| S21-06 | Modelo `CollectionEmailLog` | expediente FK, proforma FK nullable, sent_at, grace_days_used, amount_overdue, recipient. Auditoría de cobros enviados (Agent-D). |
| S21-07 | Lógica operado_por para cobranza | MWT opera (Mode C) → cobro va a entidad MWT (no al cliente). CLIENTE opera (Mode B) → cobro va al cliente. Ahora es por proforma: una proforma Mode B cobra al cliente, una Mode C cobra a MWT. |
| S21-08 | Campo `deferred_total_price` en Expediente | Equivalente `order_full_price_diferido` del sistema viejo. Nullable, editable por CEO. (Agent-D) |
| S21-09 | Endpoints CEO: templates CRUD + historial + test send | GET/POST/PATCH templates. GET historial de envíos. POST test-send (CEO envía email de prueba a sí mismo). |
| S21-10 | Endpoint: POST enviar proforma por email (Flujo C) | Envía proforma completada al cliente vía email. Template específico. Solo CEO. Registra en NotificationLog con proforma FK. |
| S21-11 | Tests | Cambio estado → NotificationLog creado. Pago vencido → cobro enviado. Operado_por determina destinatario. Template test-send funciona. Envío proforma email OK. |

### Gate Sprint 21
- [ ] Email se envía al cambiar estado vía hook (no hardcoded en command)
- [ ] Cron detecta pagos vencidos usando payment_grace_days por cliente
- [ ] operado_por por proforma determina destinatario de cobro
- [ ] Templates editables por CEO
- [ ] Proforma enviable por email (Flujo C)
- [ ] Tests verdes

### Excluido
- Frontend de templates (→ S21B o S22)
- WebSocket/realtime (→ nunca, polling es suficiente para MVP)
- Adjuntos en email (→ futuro)

---

## SPRINT 21B — Monitor de Actividad + Role-Based Sidebar
**Prioridad:** P1
**Duración estimada:** 1 semana
**Agente:** AG-02 Backend + AG-03 Frontend
**Dependencia:** Sprint 20 DONE (proformas en EventLog). Puede correr en paralelo con S21.

### Objetivos
1. Feed de actividad con read-state por usuario
2. Badge de notificaciones en header + panel dropdown
3. Activar sidebar filtrado por roles (ya existe el código, solo activar)

### Items

| ID | Tarea | Detalle |
|----|-------|---------|
| S21B-01 | Extender EventLog: +user FK, +proforma FK nullable, +command_id, +previous_status, +new_status | Agent-D hallazgo. Ahora registra a nivel proforma si aplica. |
| S21B-02 | Modelo `UserNotificationState` | user FK, last_seen_event_id. Para calcular "no leídos" sin marcar cada evento individualmente. |
| S21B-03 | GET `/activity-feed/` con filtrado | Retorna eventos no vistos + recientes. Filtra por expediente, proforma, tipo. Polling 60s, no WebSocket. |
| S21B-04 | GET `/activity-feed/count/` | Solo count de no vistos. Barato para polling frecuente. |
| S21B-05 | Frontend: badge en header + panel dropdown | Badge numerico. Panel: lista de actividades recientes con link a expediente/proforma. Al abrir, marca como visto. |
| S21B-06 | Activar role-based sidebar | `layout/Sidebar.tsx` ya tiene soporte de roles (Agent-C hallazgo). Solo activar: CEO ve todo, CLIENT_* ve solo portal, AGENT_* ve operaciones. |
| S21B-07 | Tests | Operación → log con proforma FK. Feed retorna no-vistas. Sidebar filtra por rol. Count endpoint correcto. |

### Gate Sprint 21B
- [ ] Badge muestra count correcto
- [ ] Al abrir panel, marca como visto
- [ ] Sidebar filtra items según rol del usuario
- [ ] EventLog registra proforma cuando aplica

---

## SPRINT 22 — Capa Comercial: Pricing Engine + Asignaciones
**Prioridad:** P0 (camino crítico → bloquea S23, S24)
**Duración estimada:** 2 semanas
**Agente:** AG-02 Backend + AG-03 Frontend
**Dependencia:** Sprint 18 DONE + CEO-25 resuelto (sesión diseño capa comercial)
**Pendiente CEO:** CEO-25 (pricelists reales, reglas rebates, descuentos plazo, herencia)

### Objetivos
1. Upload y versionamiento de pricelists en Brand Console
2. Descuentos por plazo de pago
3. ClientProductAssignment con cached pricing
4. Conexión con proformas: al agregar línea, resolve_client_price() sugiere precio por proforma mode

### Fase 0 — Modelos y pricing engine

| ID | Tarea | Detalle |
|----|-------|---------|
| S22-01 | `ClientProductAssignment` | Modelo: client_subsidiary FK, brand_sku FK, client_price, cached_base_price, is_active, created_at. **Decisión pendiente CEO #1:** permanente vs con vigencia temporal (valid_from/valid_to). Recomendación: permanente para MVP, vigencia en v2. |
| S22-02 | Paso 0 en resolve_client_price() | Waterfall: (0) CPA cached_client_price → (1) BCPA → (2) PriceList MIN → (3) manual. Ahora resolución es **por proforma mode**: Mode B puede tener pricing distinto de Mode C para el mismo SKU. |
| S22-03 | Upload pricelist CSV/Excel en Brand Console | Parsing con Pandas. Validación: SKU existe en BrandSKU, precio numérico positivo, talla válida en BrandSizeSystem. Error report por línea. |
| S22-04 | Versionamiento pricelists | Modelo PriceListVersion: brand FK, file_url, uploaded_by, is_active, activated_at, deactivated_at. Solo 1 activa por brand a la vez. Log de cambios. |
| S22-05 | `PaymentTermDiscount`: brand × plazo → % descuento | Modelo: brand FK, payment_days, discount_percentage. Ejemplo: Marluvas × 8 días → 5%, Marluvas × 30 días → 2%. |
| S22-06 | Integrar descuento por plazo en resolve_client_price() | Después de resolver base_price, aplicar descuento según payment_days del expediente/proforma. Precio final = base × (1 - discount_pct). |

### Fase 1 — Validaciones y bulk

| ID | Tarea | Detalle |
|----|-------|---------|
| S22-07 | Validación MOQ por talla (WARNING) y por pedido (ERROR en C5) | MOQ por talla: min_order_qty en BrandSKU. Si línea tiene menos → warning visual. MOQ por pedido: sum todas las líneas de la proforma ≥ min_order_total. Si no → C5 bloquea. |
| S22-08 | Bulk assignment endpoint | POST `/api/client-assignments/bulk/` — asignar por product_key (no por SKU individual, porque 565 SKUs uno por uno es inviable). Recibe: client_id, brand_id, product_key, price → crea N assignments (1 por talla). |
| S22-09 | Recálculo cached_client_price como Celery task | Evento: nueva pricelist activada → recalcular todos los CPA de esa brand. Idempotente. |
| S22-10 | Alerta automática de margen | Al activar nueva pricelist: calcular si algún CPA rompe margen mínimo → alerta CEO (via NotificationTemplate de S21). |

### Fase 2 — Frontend

| ID | Tarea | Detalle |
|----|-------|---------|
| S22-11 | Frontend expediente: pre-llenar precio al agregar línea | Al seleccionar BrandSKU en una proforma, resolve_client_price() retorna precio sugerido. Tooltip: "Base: $43.00 (2026v6) × 1.05 (30d) = $45.15 — fuente: pricelist". (Agent-C de S19, ahora conectado a proformas) |
| S22-12 | Frontend Brand Console: tab upload pricelists | Upload, historial de versiones, activar/desactivar. Preview del CSV antes de confirmar. |
| S22-13 | Frontend Brand Console: tab payment terms | CRUD de PaymentTermDiscount por brand. |
| S22-14 | Tests | Upload, versionamiento, descuento aplicado, CPA funcional, bulk assignment, recálculo, alerta, pre-fill precio en expediente, MOQ warning/error. |

### Gate Sprint 22
- [ ] Pricelist uploadable y versionada
- [ ] ClientProductAssignment funcional con cached_client_price
- [ ] resolve_client_price() usa waterfall de 4 pasos
- [ ] Descuento por plazo aplicado correctamente
- [ ] Línea en expediente pre-llena precio con tooltip de fuente
- [ ] MOQ por talla (warning) y por pedido (error C5)
- [ ] Alerta de margen funciona
- [ ] Tests verdes

---

## SPRINT 23 — Capa Comercial: Rebates + Herencia + Comisiones
**Prioridad:** P0
**Duración estimada:** 2 semanas
**Agente:** AG-02 Backend + AG-03 Frontend
**Dependencia:** Sprint 22 DONE + CEO-25 resuelto

### Objetivos
1. Rebates trimestrales con metas por cliente
2. Herencia de reglas brand → cliente → subsidiaria con override
3. Comisiones por producto/cliente
4. Migrar ArtifactPolicy de constante Python a DB (BrandWorkflowPolicy)

### Items

| ID | Tarea | Detalle |
|----|-------|---------|
| S23-01 | Modelo `RebateProgram` | brand FK × client FK × trimestre → meta_amount → rebate_percentage. Con is_active, period (Q1/Q2/Q3/Q4 + year). |
| S23-02 | Modelo `ClientProductCommission` | client_subsidiary FK × brand_sku FK → commission_type (fixed/percentage), commission_value. Para Mode B: comisión individual por producto/cliente. |
| S23-03 | Herencia de reglas | brand → aplica a todos los clientes. Override por client → aplica a todas las subsidiarias de ese client. Override por subsidiary → aplica solo a esa subsidiaria. Cascade: subsidiary > client > brand. |
| S23-04 | Liquidación de rebates | Celery task trimestral. Calcula total facturado vs meta → aplica rebate si cumple. Genera ART-12 (Nota de Compensación) automáticamente. |
| S23-05 | **Migrar ArtifactPolicy a DB** | Modelo `BrandWorkflowPolicy`: brand FK, mode, state, required_artifacts (JSONField), optional_artifacts, gate_artifacts. Seed con datos de la constante Python de S20. Admin en Brand Console. |
| S23-06 | **BrandWorkflowPolicy seeding condicional** | Marluvas y Rana Walk: seed desde constante. Tecmater: seed cuando haya datos confirmados (CEO pendiente). El resolve_artifact_policy() primero busca en DB, fallback a constante Python. |
| S23-07 | Frontend Client Console: vista rebates/metas/comisiones | Tab con progreso vs meta, historial de rebates, comisiones por producto. |
| S23-08 | Frontend Brand Console: gestión reglas comerciales | Tab con: upload pricelists (S22), rebate programs CRUD, commission rules CRUD, workflow policy editor. |
| S23-09 | Tests | Herencia brand>client>subsidiary. Override funciona. Liquidación calcula correctamente. BrandWorkflowPolicy sustituye constante Python. |

### Gate Sprint 23
- [ ] Rebate se calcula al cierre de trimestre
- [ ] Override por subsidiaria no afecta otras subsidiarias
- [ ] Comisión por producto se refleja en pricing
- [ ] ArtifactPolicy viene de DB (con fallback a constante)
- [ ] Tests verdes

---

## RESUMEN VISUAL — Nuevo orden de ejecución

```
Sprint 19 (EN EJECUCIÓN — frontend expedientes)
    │
    ├──→ Sprint 20 (backend proformas + policy)
    │        │
    │        ├──→ Sprint 20B (frontend policy-driven)
    │        │        │
    │        │        ├──→ Sprint 24 (autogestión B2B portal)
    │        │        │
    │        │        └──→ Sprint 21B (monitor + sidebar)
    │        │
    │        └──→ Sprint 21 (emails + cobranza) ←── puede correr en paralelo con 20B
    │                 │
    │                 └──→ Sprint 26 (permisos + admin templates)
    │
    ├──→ Sprint 22 (pricelists + pricing engine) ←── CEO-25 bloquea
    │        │
    │        └──→ Sprint 23 (rebates + herencia + policy a DB)
    │                 │
    │                 └──→ Sprint 24 (autogestión B2B portal)
    │
    ├──→ Sprint 25 (negocio avanzado — paralelo)
    │
    └──→ Sprint 27 (migración datos — después de 19+20)
```

**Camino crítico:** 19 → 20 → 20B → 24 (portal funcional con proformas)
**Segundo track:** 22 → 23 → 24 (pricing completo)
**Paralelizables:** S21 con S20B. S21B con S21. S25 en cualquier momento post-S18.

---

## DECISIONES CEO REQUERIDAS

| # | Decisión | Bloquea | Urgencia |
|---|----------|---------|----------|
| SG-01 | Confirmar ArtifactPolicy como constante Python (S20) → DB (S23) | S20 | ANTES de S20 |
| SG-02 | Proforma email vs descarga manual | S21 | Antes de S21 |
| SG-03 | ART-01 auto-generada: registro + PDF bajo demanda | S24 | Antes de S24 |
| SG-04 | Confirmar ART-05 M2M (embarque multi-proforma) | S20 | ANTES de S20 |
| SG-05 | Void automático al cambiar modo + confirmación CEO | S20 | ANTES de S20 |
| SG-06 | operated_by = siempre MWT por ahora | S20 | ANTES de S20 |
| CEO-25 | Sesión diseño capa comercial (pricelists, rebates, herencia) | S22-23 | Antes de S22 |
| CEO-28 | Email provider (SMTP/SendGrid/SES) + contact_email | S21 | Antes de S21 |
| CEO #1 (convergencia) | ClientProductAssignment: permanente o con vigencia? | S22 | Antes de S22 |

---

## ESTIMACIÓN DE TIMELINE

| Sprint | Duración | Puede paralelo con |
|--------|----------|---------------------|
| S20 | 1.5 semanas | — |
| S20B | 1-1.5 semanas | S21 |
| S21 | 1 semana | S20B |
| S21B | 1 semana | S21, S22 |
| S22 | 2 semanas | S21B |
| S23 | 2 semanas | — |

**Total secuencial:** ~9 semanas (S20→S20B→S21→S21B→S22→S23)
**Total con paralelización:** ~6-7 semanas
