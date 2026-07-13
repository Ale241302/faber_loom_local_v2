# PLAN_DESARROLLO_FABERLOOM_ETAPA8_v1 — Plataforma técnica moderna (frontend, realtime, desktop)

id: PLAN_FB_ETAPA8
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 8: pagar la deuda de plataforma técnica sin cambiar comportamiento funcional
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · SPEC_FB_FRONTEND_REALTIME_STATE_v1 · SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1 · SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1 · SPEC_FB_FUNC_M20_AUTO_UPDATE_v1 · SPEC_FABERLOOM_DESIGN_FOUNDATION_v1 · POL_CONTEXT_BUDGET

**Cláusula de re-validación:** v1.1 antes de arrancar, con los datos de fricción reales de E6-E7. Si el var-hack de Babel produce un bug P0 antes, E8-0 se adelanta como banda paralela a la etapa en curso (regla del roadmap §4).

---

## §0. Naturaleza y decisiones

E8 es una etapa de INGENIERÍA PURA: el criterio de éxito es "todo funciona exactamente igual, pero sobre cimientos sanos". Ningún hito de E8 cambia contratos de negocio, autonomía ni datos.

**Decisiones del Arquitecto:**
- **DA8-1. Build: Vite + React 18 + módulos ES**, eliminando Babel standalone y el var-hack de E4. Migración INCREMENTAL por vista (estrangulamiento): el shell nuevo carga vistas legacy dentro de un adaptador hasta migrarlas todas. Nada de big-bang.
- **DA8-2. Realtime: SSE (Server-Sent Events), no WebSockets.** Razón: el tráfico es servidor→cliente (progreso de tasks, mensajes del agente, propuestas ambientales); SSE atraviesa proxies sin fricción, reconecta solo, y FastAPI lo sirve con `StreamingResponse` sin dependencia nueva. WebSocket se reevalúa solo si aparece necesidad cliente→servidor de baja latencia (no la hay: el composer es HTTP normal).
- **DA8-3. Desktop: Electron con auth M18 y auto-update M20**, empaquetando el MISMO frontend Vite (una sola base de código). pywebview actual queda como modo dev.
- **DA8-4. Offline (M19): solo-lectura mínima viable** — cache local de briefs, WorkLoom y últimas conversaciones para consulta sin red; NADA de escritura offline con sync (conflictos multi-tenant no valen su costo hoy). Escritura offline se re-evalúa en E10+ con demanda real.
- **DA8-5.** Presupuesto de contexto y performance se auditan contra `POL_CONTEXT_BUDGET` con números medidos, no estimados. Rama `e8-plataforma`.

## §1. Mapa de olas

| Ola | Hitos |
|---|---|
| 1 | E8-0 (build system + migración shell) |
| 2 | E8-1 (migración de vistas), E8-2 (realtime SSE) |
| 3 | E8-3 (desktop Electron), E8-4 (offline lectura) |
| 4 | E8-5 (performance/presupuestos), E8-6 (acta) |

## §2. Detalle por hito

### E8-0 — Build system Vite y shell moderno

**Objetivo:** compilación real del frontend: módulos ES, imports, minificación, cache-busting por hash — se acaba el scope global compartido.

**Tareas:**
1. Crear `app/frontend/` (workspace npm): Vite + React 18 + estructura `src/{shell,views,components,lib,styles}`. `vite.config` con build a `app/static/dist/` (el backend FastAPI sigue sirviendo estático — sin servidor de front separado en prod).
2. Migrar el SHELL (rail, navegación, sesión, branding) a módulos ES. Crear el **adaptador legacy**: componente `LegacyView` que monta las vistas aún-Babel dentro del shell nuevo (iframe o mount point con los scripts legacy cargados bajo namespace) — el estrangulamiento permite migrar vista por vista con la app siempre funcional.
3. Tokens de diseño: portar las variables de `css/main.css` y `Diseños/tokens` (dtcg) a `src/styles/tokens.css` generado desde los .json de tokens (script `npm run tokens`) — una sola fuente de verdad con el sistema de marca.
4. CI: job de build del frontend + fallo si el bundle supera presupuesto (decisión: 500KB gz inicial del shell; ajustable con changelog).
5. `index.html` pasa a cargar `dist/` con hashes; eliminar unpkg/babel-standalone del camino de producción (dev puede conservar HMR de Vite).

**Archivos:** `app/frontend/**` (nuevo), `app/static/dist/` (build), `index.html`, `.github/workflows/frontend.yml`, `AGENTS.md` (sección de build front).
**Tests:** suite Python intacta; nuevo `app/frontend/src/**/*.test.tsx` mínimo (shell render, navegación, adaptador legacy monta) con Vitest; smoke E2E manual documentado (login→chat→brief→workloom).
**DoD:** producción sirve el shell desde Vite con TODAS las vistas funcionando (migradas o vía adaptador); var-hack eliminado del shell. **Esfuerzo:** 3 sesiones Fugu.

### E8-1 — Migración de vistas al build

**Objetivo:** cero vistas legacy; morir el adaptador.

**Tareas:**
1. Migrar por orden de riesgo ascendente: (1) vistas hoja simples (health_dashboard, promotion_readiness, routing_shadow, tenant_admin, tenant_settings, signup), (2) WorkLoom/KB/Gold, (3) SpaceView/chat del agente (la más rica: composer, stream, tab Agente, termómetro), (4) foundation views.
2. Cada vista migrada: misma API, mismos estados, mismo diseño (verificación visual lado a lado); componentes compartidos extraídos a `src/components` (RailItem, Accordion, tiles, tablas) SIN rediseñar — rediseñar es otra etapa.
3. Al final: borrar `app/static/js/*.jsx` legacy y el adaptador; `graphify update .`.

**Tests:** Vitest por vista (render + interacción principal); la suite Python de endpoints cubre el backend sin cambios; checklist E2E manual por vista firmada en la auditoría de ola.
**DoD:** 100% vistas en el build; adaptador y Babel eliminados; ninguna regresión funcional reportada en 1 semana de dogfood. **Esfuerzo:** 4-5 sesiones Fugu (repartidas).

### E8-2 — Realtime SSE

**Objetivo:** lo que hoy se ve con refresh/polling se ve en vivo: progreso de tasks del agente, mensajes nuevos, propuestas ambientales, aprobaciones HITL.

**Tareas:**
1. Backend: `app/src/events_stream.py` — endpoint `GET /api/stream` (SSE) autenticado por la cookie de sesión, scoped por tenant/usuario (Context obligatorio). Fuente de eventos: el outbox/audit existente (M15/AuditWriter) filtrado a tipos de interés (`task.step.*`, `chat.message.created`, `ambient_proposal.visible`, `workloom_item.*`, `draft.pending`). Backpressure: heartbeat cada 25s, reconexión con `Last-Event-ID`.
2. Aislamiento estricto: el stream JAMÁS emite eventos de otro tenant ni de workspaces sin membresía (mismo filtro de visibilidad de briefs) — test de contaminación dedicado.
3. Frontend: `src/lib/stream.ts` (EventSource con reconexión) + integración: badge de WorkLoom en vivo, progreso "paso 2/3" en el chat (reemplaza el patrón de polling de E4-3.6), toast de propuesta ambiental.
4. Degradación: sin SSE (proxy hostil), la app vuelve a polling suave (intervalo 30s) — feature detection, no configuración.

**Archivos:** `app/src/events_stream.py`, `main.py` (mount), `src/lib/stream.ts`, vistas afectadas.
**Tests:** `test_e8_2_sse_isolation.py` (cross-tenant/cross-workspace imposible en el stream — el test crítico), `test_e8_2_sse_stream.py` (eventos llegan, heartbeat, Last-Event-ID), Vitest del cliente con EventSource mock.
**DoD:** una task multi-paso se ve progresar en vivo; contamination del stream verde. **Esfuerzo:** 2-3 sesiones Fugu.

### E8-3 — Desktop Electron (M18 + M20)

**Objetivo:** el desktop de la spec E1 (SPEC_FB_WORKSPACE asumía Electron) existe de verdad: instalable, firmado, auto-actualizable.

**Tareas:**
1. `app/desktop/` (workspace Electron): carga el frontend Vite contra el backend configurable (VPS o local). Implementar `SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1`: auth de escritorio (cookie de sesión segura en el contenedor de Electron, sin tokens en localStorage — coherente con la convergencia HttpOnly de E2).
2. Auto-update según `SPEC_FB_FUNC_M20_AUTO_UPDATE_v1`: electron-updater con feed en el VPS (o GitHub Releases — decisión: GitHub Releases firmadas, menos infra propia), canal `stable`.
3. Firma de código: certificado de firma Windows (insumo de compra CEO — pedirlo al ARRANCAR E8, lead time). Sin firma no hay distribución (fail-closed del hito).
4. Menú nativo mínimo, notificaciones de sistema para HITL pendiente (opt-in), deep-link `faberloom://` para abrir items de WorkLoom.

**Archivos:** `app/desktop/**`, `.github/workflows/desktop.yml` (build+release), docs de instalación.
**Tests:** build reproducible en CI; smoke checklist del instalador (instala, autentica, chat, update desde versión N-1 — documentado con evidencia); los specs M18/M20 actualizados a as-built con changelog.
**DoD:** instalador Windows firmado que se auto-actualiza; CEO usándolo a diario 1 semana. **Esfuerzo:** 3 sesiones Fugu + compra certificado.

### E8-4 — Offline de lectura (M19 mínimo)

**Objetivo:** sin red, el usuario consulta lo último que vio: briefs, WorkLoom, conversaciones recientes.

**Tareas:**
1. Cache local (IndexedDB vía `src/lib/offline.ts`): al navegar, se cachean las últimas respuestas de briefs/workloom/chats (TTL 7 días, límite 50MB, cifrado NO necesario en E8 — es el mismo usuario en su máquina, pero SÍ scoping por usuario: el cache se purga al logout/cambio de usuario).
2. Modo offline explícito: banner "sin conexión — viendo datos de <fecha>", escritura deshabilitada con mensaje claro (DA8-4: cero escritura offline).
3. Actualizar `SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1` → as-built v1.1 (alcance lectura, decisión de no-escritura con razón y criterio de re-evaluación).

**Tests:** Vitest de cache (hit/miss/TTL/purga en logout), checklist manual de modo avión.
**DoD:** modo avión muestra los últimos datos con banner; logout purga. **Esfuerzo:** 1-2 sesiones Fugu.

### E8-5 — Performance y presupuestos medidos

**Objetivo:** números, no sensaciones.

**Tareas:**
1. Backend: medir p50/p95 de los endpoints calientes (completions, briefs, workloom, stream) con el middleware de timing + reporte `docs/audits/PERF_BASELINE_E8_<fecha>.md`; índices faltantes detectados con EXPLAIN sobre Postgres real (las 5 queries más caras).
2. Contexto LLM: auditar los prompts del agente contra `POL_CONTEXT_BUDGET` (¿cuántos tokens inyecta recall+brief+instrucciones?); recortar lo que no paga su costo (medido por A/B en la arena de E7-3 — la arena valida que recortar no degrada).
3. Frontend: presupuesto de bundle vigilado en CI (E8-0.4), lazy-load de vistas pesadas, lighthouse ≥90 en performance del shell.
4. Costos: revisar el ledger agregado — costo IA por tenant activo/mes contra el pricing de E6-0; si el margen es negativo en algún tier, reporte al CEO (dato para re-pricing, no decisión de código).

**DoD:** baseline documentado; las 3 mejoras más rentables aplicadas y re-medidas; margen por tier calculado. **Esfuerzo:** 2 sesiones Fugu.

### E8-6 — Acta

Suite completa + Vitest + arena verdes; 1 semana de dogfood sin regresiones; `docs/audits/ACTA_ETAPA8_<fecha>.md`; merge a main + tag `e8-cierre`; AGENTS.md actualizado (flujo de build front y desktop); bloques KB.

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| La migración de vistas rompe flujos silenciosamente | Estrangulamiento con adaptador (app siempre funcional) + checklist E2E por vista + 1 semana dogfood por ola |
| SSE filtra eventos cross-tenant | Filtro de visibilidad en el emisor (no en el cliente) + test de contaminación del stream como bloqueante |
| Electron amplía superficie de ataque | M18 spec (sin tokens en localStorage), contextIsolation on, CSP estricta, auto-update firmado |
| El certificado de firma demora | Compra al DÍA 1 de E8 (patrón HE2-9 aprendido) |
| "Ya que estamos" rediseños | Prohibido por plan: E8 migra, no rediseña — cualquier rediseño es propuesta para E9+ |

## §4. Gate de salida

Frontend 100% en build moderno sin Babel/var-hack; realtime operando con contaminación verde; desktop firmado auto-actualizable en uso diario; offline lectura funcionando; baseline de performance con mejoras aplicadas; acta commiteada.

## Changelog

- v1.0.0 (2026-07-12): Creación. Decisiones DA8-1..DA8-5 (Vite, SSE, Electron con Releases firmadas, offline solo-lectura).
