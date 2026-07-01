# AUDIT_FB_MODULAR_2026-06-11 - Revision modular post-simplificacion
id: AUDIT_FB_MODULAR_2026-06-11
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: AUDIT
stamp: VIGENTE -- 2026-06-11 -- 10 modulos revisados, 10 vacios rankeados; vacios 1-3 resueltos en PLB v1.3.2 (E-3, E-2 storage, pendiente V9.1 en Sprint 1)
aprobador: CEO (Alvaro) -- mandato sesion 2026-06-11
aplica_a: [FaberLoom]
relacionado: SPEC_FB_BUILD_SEQUENCE v2.1 - PLB_FB_FOUNDATION_BETA v1.3.2 - SPEC_FB_ROUTING_PRESETS v1


Alcance: el sistema COMO QUEDO esta semana (BUILD_SEQUENCE v2.1, ROUTING_PRESETS v1, ARCHETYPE v1.1, VOICE v2.1, shell v4 con 3 modos y lente de scope). No revisa el diseno pre-simplificacion.
Metodo: por modulo -> responsabilidad unica, contrato (consume/produce), encaje, estado en KB, vacios.
Nota de gobernanza: esto es analisis efimero pre-build, NO un SPEC nuevo (el freeze sigue). Lo que merezca canon entra como enmienda a docs existentes o como decision en el sketch del shell.

---

## Mapa de 10 modulos

```
[1 Canales/Ingesta] -> [2 Clasificador] -> [3 Router/Presets] -> [5 Engine skills] -> [6 Workflow cotizacion]
        |                    |                    |                     |                    |
        v                    v                    v                     v                    v
   [4 KB/Conocimiento] <--- consume ----------------------------- [7 HITL/Mesa] -> [8 Aprendizaje]
        ^                                                               |                    |
        |                                                               v                    v
   [9 Shell: 5 superficies x scope]                              [10 Audit/Seguridad] <-- todo escribe aqui
```

---

## M1 - Canales / Ingesta (Inbox agregador)

**Responsabilidad:** N cuentas de correo (+WhatsApp E3) entran a UNA cola normalizada.
**Consume:** IMAP/Gmail OAuth, adjuntos. **Produce:** `inbound_item {account_id, raw, adjuntos[], data_class_heredada}`.
**Encaje:** alimenta a M2; el Inbox del shell es su superficie; las 5 categorias (accionable/resumen/oculto/borrar/agente) son su output de triage.
**Estado KB:** filosofia y categorias canon (shell consolidated §13); SCH_FB_RESUMEN_RULE declarado "a redactar" y sigue sin existir.
**Vacios:**
- **V1.1 Resumenes activos sin schema** - la categoria "resumen diario" depende de SCH_FB_RESUMEN_RULE que nunca se escribio. Para E1-E2 alcanza una version minima (regla + ventana + destino), pero hoy es una promesa de UI sin contrato.
- **V1.2 Adjuntos sin pipeline declarado** - el RFQ real llega como PDF/Excel adjunto. Quien lo extrae, donde se guarda el archivo, como se versiona (MinIO quedo descartado con la observabilidad self-host... y era tambien el object storage del PLB S2). **Decision pendiente: storage de archivos en E1** (filesystem KVM + backup ya previsto, o S3 externo). Hueco real dejado por la simplificacion.

## M2 - Clasificador / Triage

**Responsabilidad:** decidir workspace destino + clase de tarea + data-class de cada item.
**Consume:** inbound_item + client_map + reglas. **Produce:** `{workspace_id|null, task_class, data_class, confidence}`. Sin match -> triage humano inline (canon flujo e2e).
**Encaje:** capas canon (canal -> reglas -> semantico -> fallback, ARCHETYPE E.1); data-class NUNCA se adivina (regla inquebrantable E.3); alimenta router y workspaces.
**Estado KB:** bien especificado en ARCHETYPE v1.1 + POL_DATA_CLASSIFICATION.
**Vacios:**
- **V2.1 Resolucion de identidad (el hueco mas serio de la mitad superior).** "compras@sondel.cr -> ws_sondel" requiere un mapa contacto->cliente->workspace vivo: dominios, alias personales, contactos nuevos del mismo cliente, el mismo contacto para dos clientes (distribuidor multi-marca). El `client_map.xlsx` del PLB era un compromiso CEO pre-S4, no un modulo. Sin entity resolution declarada (aunque sea: dominio gana, alias se curan via triage), el Inbox degenera en triage manual permanente. **Propuesta: las decisiones del triage humano ALIMENTAN el client_map automaticamente** - cada "decidir destino" es un training example gratis. Encaja en el patron M8.
- **V2.2 Umbral de confianza sin numero.** "matched alta conf -> directo; baja conf -> Mesa" - alta es cuanto? Definir en E1 con los 20 RFQs del golden set (investigacion #5 ya planificada cubre esto si se le agrega la medicion del clasificador).

## M3 - Router / Presets

**Responsabilidad:** dado (task_class, data_class, preset, curva) -> modelo. Mas: caps, ledger, boost.
**Consume:** output M2 + preset del tenant. **Produce:** `routing_decision {model, reason, cost_est}` + entrada en savings ledger.
**Encaje:** ECU/preset/curva resuelto por interseccion (<20ms, deterministico); la regla de promocion vive en M8, no aca - el router solo EJECUTA el preset vigente. Limpio.
**Estado KB:** SPEC_FB_ROUTING_PRESETS v1 completo. El mejor especificado de los 10.
**Vacios:**
- **V3.1 Schema fisico del ledger.** El savings ledger es pieza central (mide, alimenta backtest y promocion) pero no tiene schema de tabla declarado (campos minimos: task_id, task_class, model, tokens, cost, baseline_cost, outcome). Es 1 hora de trabajo - hacerla en Sprint 1, no despues, porque TODOS los modulos le escriben.
- **V3.2 Baseline premium: definicion operativa.** "Ahorro vs baseline" - el baseline es el precio del modelo top POR TAREA REAL o un estimado? Si nunca corres el premium, el ahorro es contrafactual estimado. Declararlo (estimado por tokens equivalentes) para que el numero del ledger no sea cuestionable en una demo.

## M4 - KB / Conocimiento (L0-L4)

**Responsabilidad:** verdad operativa con vigencia, visibilidad, capas y conflictos marcados.
**Consume:** uploads + candidatos curados de M8. **Produce:** contexto inyectable por scope + alertas de vigencia/conflicto.
**Encaje:** retrieval E1 = seleccion de docs completos via taxonomia + prompt caching (decision de esta semana); FTS para SKUs; el conflicto se VE en el workspace que lo consume y se CURA en Aprendizaje (lente, no duplicacion).
**Estado KB:** capas y curadores canon (§11); MARCO_RECTOR seccion 1 es la doctrina.
**Vacios:**
- **V4.1 Vigencia sin motor.** "Lista T2 vence en 18 dias" exige un job que evalue `valid_until` y dispare alertas. No existe modulo scheduler declarado (ver V9.2 - es transversal).
- **V4.2 El mapa doc->scope es manual.** Que conocimiento "consume" cada workspace (heredado L2 vs propio L3) hoy se declara a mano. Aceptable en E1 con 6 workspaces; declarar el campo (`consumed_by[]` o herencia por vertical) para no inventarlo en runtime.

## M5 - Engine de skills/agentes

**Responsabilidad:** ejecutar un skill (markdown + tools allowlist + schema salida) con contexto del scope, draft-first.
**Consume:** routing_decision + contexto M4 + SkillSpec. **Produce:** draft + trace + costo.
**Encaje:** post-simplificacion es capa fina sobre el SDK estandar (decision "productizar el patron, no runtime bespoke"). Tier 0 deterministico vive aca como pre-paso del skill.
**Estado KB:** la decision de simplificacion esta en chat/eval pero NO aterrizo en ningun doc canon - el PLB S3 sigue describiendo el engine bespoke (SkillSpec en DB, Pydantic dinamico).
**Vacios:**
- **V5.1 La decision arquitectonica mas importante de la semana no esta escrita en canon.** "Skill = markdown versionado + tools allowlist via SDK estandar" contradice S3 del PLB firmado y no hay enmienda. Es EXACTAMENTE el tipo de hueco que mata: Alejandro abre el PLB y construye el engine viejo. -> Va en la proxima sesion de enmienda del PLB junto con lo ya pendiente (supersede + #10/S1B). La deuda con el PLB ya son 3 items.
- **V5.2 Contrato de tools minimo sin lista.** "NO HTTP externo, NO code exec" (heredado) sigue valido, pero la allowlist E1-E2 concreta (kb_search, get_client, get_prices, create_draft, send_email_via_tenant) no esta enumerada en ningun lado. Una tabla de 8 filas; sin ella cada skill inventa la suya.

## M6 - Workflow cotizacion (vertical)

**Responsabilidad:** RFQ -> draft proforma -> HITL -> salida, con document state machine y evidence bundle.
**Consume:** RFQ clasificado + pricing M4 + skill M5. **Produce:** PF_xxxx + evidence bundle (SHA-256, 8+5 campos).
**Encaje:** es EL caso de negocio de E2; golden PF_2453 como referencia; exception codes del PLB S3 se reutilizan.
**Estado KB:** SPEC_FB_DOCUMENT_STATE_MACHINE + SCH_FB_QUOTE_EVIDENCE_BUNDLE + ENT_FB_QUOTING_SOURCE_OF_TRUTH: solido.
**Vacios:**
- **V6.1 Pricing computable** (= investigacion #2, sigue siendo el vacio funcional #1 del sistema). Si el calculo no sale de la KB sin tu juicio, M6 entrega "agente que redacta" y no "agente que cotiza". Nada nuevo que agregar salvo insistir: se resuelve en semana 2 de E1 o el gate de E2 esta en riesgo.
- **V6.2 Numeracion de proformas.** PF_2468 - quien asigna el consecutivo, que pasa con descartadas (huecos en la serie), colision con la numeracion manual actual de MWT (AA/AB del expediente). Detalle chico que toca contabilidad: definir antes del primer envio real.

## M7 - HITL / Mesa de Control

**Responsabilidad:** cola de outputs esperando criterio; 3 botones; captura del porque; severity por 5 fuentes.
**Consume:** drafts M5/M6 + severity signals. **Produce:** aprobaciones/edits/rechazos + HITL signals para M8 + outbound autorizado.
**Estado KB:** el mejor heredable del PLB/canon (kanban 4 columnas, anatomia card, captura porque con dropdown).
**Vacios:**
- **V7.1 El envio post-aprobacion es un mini-modulo sin dueno.** Aprobar = enviar email desde el buzon del tenant: OAuth send, retry si falla, registro del message_id para threading futuro. Hoy "sale" es una palabra en el flujo. Asignarlo a M1 (canales es bidireccional) y declarar el retry minimo (3 intentos + cola de error visible en Mesa columna ERROR).
- **V7.2 Concurrencia trivial pero no declarada:** dos operadores (vos + Alejandro como tester) sobre el mismo draft. Un lock optimista (updated_at check) alcanza; gratis si se decide ahora, doloroso si aparece en produccion.

## M8 - Aprendizaje (StackLoom + promociones)

**Responsabilidad:** cola epistemica - candidatos a indexar, conflictos, promociones L4->L2, regla de promocion del router, ajuste few-shot de voz. Sistema propone con evidencia, humano cura.
**Consume:** CTA de chats + HITL signals M7 + stats ledger M3. **Produce:** updates a M4 (knowledge), a M3 (preset deltas aprobados), a M5 (few-shot voz).
**Encaje:** el modo Aprendizaje del shell le da superficie; unifica tres loops que estaban dispersos (knowledge, routing, voz) bajo UN patron. Conceptualmente cerrado esta semana.
**Vacios:**
- **V8.1 Gold samples sin schema fisico.** Igual que el ledger: pieza central (few-shot de voz + golden corpus + replay) sin tabla declarada (par contexto/accion_aprobada + task_class + outcome + embedding opcional). El PLB la tenia como "vista materializada" - revalidar que sobrevive a la simplificacion. 1 hora, Sprint 1.
- **V8.2 Heuristica del CTA "vale la pena indexar".** Triggers canon (N terminos nuevos, M mensajes de proceso) son palabras, no umbrales. E1: empezar con UN trigger barato (deteccion de afirmacion operativa por el propio modelo al final del turno) y medir false-positive rate; no construir el detector sofisticado.

## M9 - Shell (5 superficies x scope)

**Responsabilidad:** Inbox, Mesa, Chat, KB, Aprendizaje como componentes que reciben `scope: tenant|workspace_id`. 3 modos. Cejas + focus.
**Estado:** sketch v4 + 7 decisiones de esta semana. Adelante del canon escrito (enmienda pendiente al consolidated).
**Vacios:**
- **V9.1 El lente exige scoping en datos, no solo en UI.** Tenemos RLS por tenant_id; el lente workspace necesita `workspace_id` NOT NULL en items operativos + permisos de membresia (administrados vs heredados = quien ve que workspace). Con 2 roles E1 alcanza una tabla workspace_members simple - pero si no se declara, el lente se implementa como filtro de frontend y eso ES una fuga en potencia. **Decision: el scope del lente se aplica en query (RLS o WHERE server-side), nunca solo en UI.**
- **V9.2 No existe modulo scheduler y tres modulos lo asumen:** digest 17:00 (M1), vigencia (M4), batch semanal de promocion (M8). Un cron + tabla jobs (ARQ ya esta en el stack) - declararlo como mini-modulo M0 para que nadie lo improvise tres veces.
- **V9.3 Persistencia de conversaciones** (hilos de SpaceLoom/workspaces, fijados, "promover a workspace"): el objeto conversacion (id, scope, mensajes, estado) no tiene schema. Es la entidad mas usada de toda la UI.

## M10 - Audit / Seguridad

**Responsabilidad:** append-only, actor+rol, evidence hashes, data-class enforcement fail-closed.
**Estado KB:** TIER 1 del PLB sobrevive integro a las simplificaciones; scanner deterministico especificado.
**Vacios:**
- **V10.1 Ninguno estructural nuevo.** Solo la herencia de V9.1: los eventos de audit deben registrar workspace_id ademas de tenant_id para que el lente tambien aplique al audit. Trivial si se hace en el schema inicial.

---

## Sintesis: los vacios que importan, rankeados

| # | Vacio | Modulo | Severidad | Cuando resolver |
|---|---|---|---|---|
| 1 | Decision engine-fino-sobre-SDK no esta en canon; PLB sigue mandando el engine bespoke (3ra contradiccion acumulada al PLB) | M5 | ALTA | Sesion de enmienda PLB - ya impostergable |
| 2 | Entity resolution contacto->workspace (client_map vivo, alimentado por el triage) | M2 | ALTA | Disenar 1 pagina en E0; poblar en E1 sem 2 |
| 3 | Scoping del lente en datos (workspace_id + membresia), no en UI | M9 | ALTA | Schema Sprint 1 - barato ahora, fuga despues |
| 4 | Pricing computable (inv. #2, sin cambio) | M6 | ALTA | E1 sem 2 |
| 5 | Schemas fisicos: ledger + gold samples + conversaciones | M3/M8/M9 | MEDIA | Sprint 1, son ~3 horas en total |
| 6 | Scheduler como mini-modulo unico (digest/vigencia/batch) | transversal | MEDIA | Sprint 1 (ARQ ya esta) |
| 7 | Storage de adjuntos post-descarte de MinIO | M1 | MEDIA | Decision E0 (filesystem+backup vs S3) |
| 8 | Envio outbound con retry + threading como parte de M1 | M7->M1 | MEDIA | E2 sem 7 |
| 9 | Umbral de confianza del clasificador con numero | M2 | BAJA | Cae de la medicion Tier 0 (inv. #5) |
| 10 | Numeracion PF + serie contable | M6 | BAJA | Antes del primer envio real |

**Lectura general:** la columna vertebral (router -> engine -> workflow -> HITL -> aprendizaje) quedo bien modularizada y con contratos claros despues de la semana de simplificacion - no hay vacios de concepto ahi. Los huecos reales estan en los BORDES del sistema: identidad (quien es este correo), tiempo (quien dispara lo programado), archivos (donde viven los adjuntos) y persistencia fisica (4 schemas chicos sin escribir). Todos son baratos si se resuelven en E0/Sprint 1 y caros si se descubren en produccion. Y el #1 no es tecnico: es que la decision de arquitectura mas grande de la semana solo existe en conversaciones de chat.
