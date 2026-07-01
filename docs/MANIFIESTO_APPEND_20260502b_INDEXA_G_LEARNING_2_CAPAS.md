---
id: MANIFIESTO_APPEND_20260502b_INDEXA_G_LEARNING_2_CAPAS
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (planificacion + redaccion) + CEO (correccion conceptual) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
relacionado_con:
  - 6 indexas previas (a-f)
  - Modelo aprendizaje 2 capas
---

# MANIFIESTO_APPEND_20260502b_INDEXA_G_LEARNING_2_CAPAS

## Que paso

Septima indexa post auditoria R5 ChatGPT. CEO + ChatGPT detectaron error conceptual en el modelo de aprendizaje canonizado en indexa-e (`ENT_FB_CURATOR_OPERATING_MODEL_v1`): mezclaba curaduria personal del AM con gobernanza colegiada del comite organizacional. Son 2 capas distintas que necesitan separarse.

## El error conceptual

```
ANTES (mal):
  Un solo rol "curador" que cubria
    - cadencia diaria del AM
    - cadencia semanal/mensual del comite
    - aplicacion de k-anon en cada decision
    - L3 visible en cada accion

  Resultado: UI mezcla niveles · roles contaminados · controles falsos.
```

```
DESPUES (bien · canonizado en esta indexa):
  CAPA 1 USUARIO (ENT_FB_USER_LEARNING_MODEL_v1)
    - Actor: AM individual
    - Cadencia: AM-driven · cuando quiera
    - Privacidad: SIN k-anon
    - Memoria: L2 episodica privada
    - Soberano sobre SU agente

  CAPA 2 ORGANIZACION (ENT_FB_COMMITTEE_OPERATING_MODEL_v1)
    - Actor: Comite (curador + reviewers · rol distinto)
    - Cadencia: semanal/mensual estructurada
    - Privacidad: k-anon ≥5 + 7 checks privacy
    - Memoria: L3 colectivo · L4 firmado
    - Gobierna patterns cross-AM

  Transicion L2 → L3 es responsabilidad EXCLUSIVA del comite (no auto-promote).
  MWT v1 con 1 AM (Alvaro multi-hat): capa 2 dormida hasta multi-AM.
```

## Cambios canonizados en esta indexa

### Nuevos (2)

| Archivo | Lineas | Proposito |
|---|---|---|
| `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v1.md` | ~270 | Capa 1 USUARIO · curaduria personal AM |
| `docs/faberloom/ENT_FB_COMMITTEE_OPERATING_MODEL_v1.md` | ~280 | Capa 2 ORGANIZACION · gobernanza comite |

### DEPRECATED (1)

| Archivo | Accion |
|---|---|
| `docs/faberloom/ENT_FB_CURATOR_OPERATING_MODEL_v1.md` | Marcado DEPRECATED 2026-05-02 con redirect a los 2 nuevos · contenido preservado para referencia historica · NO eliminar (regla R3 inquebrantable) |

### Modificados in-place (3)

| Archivo | Cambio v1.0 → v1.1 |
|---|---|
| `SPEC_FB_KNOWLEDGE_RIVER_v1.md` | Aclaracion 2 capas: L0+L1+L2 USUARIO · L3+L4 ORGANIZACION · transicion EXCLUSIVA comite |
| `ENT_FB_RFQ_REPLAY_SET_v1.md` | Auto-add vs auto-promote en 3 etapas: produccion→candidate · AM valida active capa 1 · comite valida cross-AM L3 capa 2 |
| `POL_FB_KR_PRIVACY_TIERS_v1.md` | k-anon ≥5 SOLO en transiciones L2→L3 capa 2 · NUNCA capa 1 personal |

### Bumps + Manifiesto (3)

| Archivo | Cambio |
|---|---|
| `docs/RW_ROOT.md` | v4.8.14 → v4.8.15 + entry changelog |
| `docs/DASHBOARD_SNAPSHOT.md` | v12.5 → v12.6 + conteos |
| `docs/MANIFIESTO_APPEND_20260502b_INDEXA_G_LEARNING_2_CAPAS.md` | NUEVO · este archivo |

### Brief Design v6 (paralelo · NO bloquea indexa-g)

`design_brief_v6_fix_2_capas.md` en OneDrive instruye:
- Eliminar de Mesa de Control AM-view: `@CURADOR · ACPT N · L3 · k-anon ≥5 · POOL L3 vino` · badges promocion
- Reemplazar con lenguaje personal: "Aprendiste N cosas" · "Detectado en tus ultimas cotizaciones" · "Aplicar a mi agente" · etc
- Mantener todo lo demas del v5 que aprobamos
- Vista comite separada (`curator-workspace.html`) NO se mezcla con Mesa de Control

## Reconciliacion modelo · UI · ChatGPT R5

| Item | R5 ChatGPT votó | Estado canonizado esta indexa |
|---|---|---|
| Modelo 2 capas correcto | ✓ canonizar | ✓ HECHO |
| Renombrar curator → committee | ✓ OK | ✓ HECHO (via DEPRECATED + nuevo file) |
| Crear ENT_FB_USER_LEARNING_MODEL_v1 | ✓ OK | ✓ HECHO |
| Update KR v1.1 (L0-L2 usuario · L3-L4 organizacion) | ✓ OK | ✓ HECHO |
| Update Replay Set v1.1 (2 etapas → 3 etapas detalladas) | ✓ OK | ✓ HECHO |
| Update Privacy Tiers v1.1 (k-anon SOLO L2→L3) | ✓ OK | ✓ HECHO |
| Mock v5 fix UI AM-view | ✓ obligatorio | ⏳ Brief v6 enviado a Design (paralelo) |

## Indexa-g es la primera de 3 escalonadas post R5

Plan canonizacion ChatGPT R5 ordenado:

```
1. INDEXA-G (ESTA) · modelo aprendizaje 2 capas
   - ENT_FB_USER_LEARNING_MODEL_v1 (NUEVO)
   - ENT_FB_COMMITTEE_OPERATING_MODEL_v1 (NUEVO · sustituye curator)
   - SPEC_FB_KNOWLEDGE_RIVER v1.1 (UPDATE)
   - ENT_FB_RFQ_REPLAY_SET v1.1 (UPDATE)
   - POL_FB_KR_PRIVACY_TIERS v1.1 (UPDATE)
   - Brief Design v6 (paralelo · pendiente entrega)

2. INDEXA-H (PROXIMA) · contratos ejecutables
   - SPEC_FB_AUTH_TENANT_RBAC_v1 (NUEVO crítico)
   - SPEC_FB_INTEGRATION_LAYER_v1 (NUEVO con scope reducido)
   - SPEC_FB_FRONTEND_REALTIME_STATE_v1 (NUEVO)
   - SPEC_FB_CONTRACT_TEST_HARNESS_v1 (NUEVO)

3. INDEXA-I (DESPUES) · sistema nervioso + plataforma
   - SPEC_FB_EVENTING_AND_OUTBOX_v1 (NUEVO renombrado de event_bus)
   - SPEC_FB_SYSTEM_TOPOLOGY_v1 (NUEVO con prohibiciones K8s/Kafka Sprint 1)
   - SPEC_FB_TENANT_BOOTSTRAP_SEED_v1 (NUEVO)
```

## Stack tecnico canonizable (post R5 · pre-indexa-i)

| Pieza | Decision | Justificacion R5 |
|---|---|---|
| Backend | FastAPI + Pydantic + SQLAlchemy/Alembic | OpenAPI auto · WS directo · type-safe |
| Frontend | Next.js App Router + TypeScript | RSC + Suspense · server-driven |
| LLM router | LiteLLM Proxy | OpenAI-compatible gateway · canonizado |
| DB | Postgres + pgvector | Operacional + memoria + embeddings |
| Cache/bus | Redis + Redis Streams | Append-only log · NO Kafka Sprint 1 |
| Workers | Celery + Redis broker | Robusto para drafts/replay |
| Auth | App-native FastAPI | NO Auth0/Keycloak Sprint 1 (control + bajo costo) |
| Observability | OpenTelemetry + Prometheus + Loki/Grafana minimo | Audit reconstruction E2E |
| Orchestration | Docker Compose + Caddy/Traefik | NO K8s Sprint 1 (12 containers KVM 8) |
| Object storage | MinIO | Evidence bundles · adjuntos |

## Bonus 5%/50% headers obligatorios desde dia 1

```
x-trace-id        request completa
x-tenant-id       multi-tenant routing
x-actor-id        quien (AM/Curator/Committee/CEO)
x-agent-id        que agente actuó
x-command-id      que accion
x-idempotency-key evita duplicados retry
```

En TODA request · evento · log. R5 explicit: "sin esto observability llega tarde y con cara de consultor caro."

## Estado del proyecto post-indexa-g

```
✓ R1+R2+R3+R4 auditorias (cero rechazos)
✓ R5 auditoria (Sprint 1 readiness 6.7→9.1 proyectado)
✓ Indexa-a Knowledge River
✓ Indexa-b P16 Decomposition
✓ Indexa-c AM Vertical
✓ Indexa-d Audit Reconciliation R2+R3
✓ Indexa-e Backend post R4
✓ Indexa-f Cierre arquitectonico (mock v5 + fixtures)
✓ Indexa-g (ESTA) Modelo aprendizaje 2 capas
○ Indexa-h Contratos ejecutables (Auth + Integration + Frontend State + Contract Test)
○ Indexa-i Sistema nervioso + Plataforma (Eventing + Topology + Seed)
○ Mock v6 Design (paralelo · brief enviado)
```

## Pendientes post-indexa-g

### Inmediato

1. **Indexa-h** · 4 SPECs contratos ejecutables (Auth · Integration · Frontend State · Contract Test)
2. **Mock v6 Design** · entrega Claude Design tras procesar brief paralelo

### Mediano plazo

3. Indexa-i · 3 SPECs sistema nervioso + plataforma (Eventing · Topology · Seed)
4. Sprint 1 implementacion arranca cuando indexa-h + indexa-i merged

## Origen del insight CEO

CEO Alvaro · sesion 2026-05-02:
> "el usuario siempre esta agergando conocimiento y se le informa de patrones y nuevas cosas que se han aprendido y el tiene un proceso de curado que el itera y se integra y de lo que el integra es lo que va al comite para revisar que de lo que aprendio la organizacion puede ser considerado para toda la comunidad. uno es el usuario y otro la organizacion"

Y posteriormente:
> "Si A"

Confirmacion ejecutiva del plan A · 3 indexas escalonadas. Indexa-g cierre primer paso · capa 2 (h+i) por seguir.

## Stamp
VIGENTE 2026-05-02 — Indexa-g modelo aprendizaje 2 capas. Correccion error conceptual canonizado · USER_LEARNING + COMMITTEE separados · CURATOR DEPRECATED preservado. KR + Replay + Privacy v1.1 alineados con modelo 2 capas. Brief Design v6 paralelo. Primera de 3 indexas escalonadas post R5. ARCH sealed v1.5 NO tocado. POL_DATA_CLASSIFICATION sealed v1.4 NO tocado. FROZENs intactos.
