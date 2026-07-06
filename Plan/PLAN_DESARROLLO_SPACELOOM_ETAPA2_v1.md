# PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1 -- Plan de Build SpaceLoom Etapa 2 (multi-usuario interno)
id: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1
version: 1.6
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-07-06 -- plan de build Etapa 2; v1.7: especificacion del ciclo ambiental (Sec.1.7.1-1.7.5) con limites, dark-launch, deduplicacion, backoff, metricas y auditoria por ciclo
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_ETAPA1_v1.md - ENT_FB_RFQ_REPLAY_SET_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - EVAL_PLAN_SPACELOOM_FUGU_ULTRA.md - EVAL_PLAN_SPACELOOM_KIMI.md

---

## 0. Que es la Etapa 2 (y que NO)

**Etapa 2 = multi-usuario interno** (definicion canonica: SPEC_SPACELOOM_ETAPA1_v1 §1).
El telar completo de Etapa 1 (SpaceLoom + router + workspaces + KB + HITL + Routine Hub
+ correo) deja de ser una app de un solo usuario y pasa a ser usada por el equipo MWT
(AMs, curador, CEO) contra una instancia compartida self-hosted (LAN/VPN).

NO es Etapa 3: sin multi-tenant SaaS, sin clientes externos dentro del sistema, sin
nube publica. Un solo tenant (MWT); `tenant_id` se activa como constante real, no como
espacio de clientes.

La regla de Etapa 1 se invierte: alli las costuras se dejaron limpias sin construir el
futuro; aqui **se activan esas costuras** (tenant_id/user_id/actor_role latentes, capa
Context, AuditWriter, sellado por espacio, router abstraido) sin reescribir el nucleo.

## 1. Los 7 pilares de Etapa 2 (delta sobre Etapa 1)

### 1.1 Routing (modelo OpenRouter/Ollama: catalogo + manual + auto)
- **Catalogo multi-proveedor multi-key**: N api keys de N proveedores cloud + N modelos
  locales (Ollama) registrados en un catalogo unico. Cada modelo lleva tags de
  capacidad (`text`, `vision`, `audio`, `image_gen`, ...), costo por token y latencia.
  El router abstraido de Etapa 1 es la costura; el catalogo es la capa que se suma.
- **Modo MANUAL**: en el chat el usuario escoge explicitamente que modelo responde
  (selector por mensaje o por workspace). Ya sembrado en E1 (router minimo); aqui se
  expone sobre el catalogo completo.
- **Modo AUTO (dispatcher)**: un modelo barato clasifica el mensaje, lo descompone en
  tareas y asigna cada tarea al modelo adecuado por capacidad/costo, encadenando
  outputs. Ejemplo canonico: "lee este PDF, resume y genera una imagen" ->
  dispatcher barato -> modelo economico lee/resume el PDF -> modelo capaz de
  `image_gen` recibe el resumen y genera la imagen.
- **Atribucion**: la UI muestra solo el modelo que produjo el entregable final (la
  imagen, no el resumen intermedio). La cadena completa (dispatcher + intermedios +
  costos por paso) queda inmutable en `evidence_json` y en el cost ledger — visible al
  expandir, nunca oculta al audit.
- **Guardrails del modo auto**: max pasos por cadena, budget cap por request, y
  provider allowlist por workspace (un workspace confidencial puede forzar solo-local).
  El dispatcher propone; no puede invocar acciones irreversibles (HITL intacto).
- De BYO-key personal a **keys gestionadas por admin**: budget cap y cost ledger por
  usuario y por equipo, no solo global.
- Se desbloquea lo diferido en la enmienda 7.3 de Etapa 1: presets completos de
  SPEC_FB_ROUTING_PRESETS_v1 (builder, templates), ahora que existe ledger real de uso
  para justificarlos. Auto-optimizador sigue fuera hasta tener datos multi-usuario.

### 1.2 Inbox (WorkLoom multi-usuario)
- WorkLoom pasa de cola personal a **cola compartida**: asignacion de items por usuario,
  estados visibles al equipo, urgencia, reasignacion.
- Correo: connector multi-cuenta donde cada AM conecta SUS cuentas; read-first y envio
  HITL se mantienen identicos (P0 de Etapa 1 no se relaja).
- Todo item de inbox registra `actor_id` y `actor_role_at_decision` (campo latente E1
  que se activa).

### 1.3 Conocimiento (KB compartida)
- Herencia org -> equipo -> workspace: la KB de MWT es una, con vistas selladas por
  workspace/cliente. El sellado local de SL3.5 se sube detras de la MISMA costura a
  control de acceso por rol.
- Citas con fuente, source_to_field_check y stale_data_block se mantienen sin cambios.
- **Gold loop capa 2**: se activa la etapa "candidate -> active -> L3 cross-AM" de
  ENT_FB_RFQ_REPLAY_SET_v1 §8.2: el AM valida su capa personal (L2) y un comite valida
  el paso a conocimiento cruzado (L3, k-anon >=5). En Etapa 1 solo existia auto-add.

### 1.4 Aprobar (HITL con roles)
- HITL deja de ser "el unico usuario aprueba todo": aparecen **roles reales**
  (AM / curador / CEO). `approved_by` y `actor_role_at_decision` dejan de ser constantes.
- Segundo gate anti-contaminacion para gold de campos duros (DoD 7.5 de E1): quien
  aprueba el draft no puede ser el mismo que promueve el dato a gold.
- Irreversibles (enviar/borrar = NEVER sin doble confirmacion) siguen en la capa de
  gobierno fina, fuera de la entidad. Sin cambios de principio.

### 1.5 Skills (Routine Hub compartido)
- Biblioteca de rutinas **compartida y versionada**: quien crea, quien aprueba, quien
  puede invocar (`@nombre`) se gobierna por rol.
- SKILL.md portable (costura E1) se cobra aqui: la misma skill corre para cualquier
  usuario sin tocar su contenido. `skill_version` y `routine_version` activos en cada run.
- El compilador de rutinas sigue emitiendo subconjunto de SCH_FB_SKILL_MANIFEST_v2.

### 1.6 Agentes
- Se mantiene el principio "**una entidad, no fabrica de agentes**": los agentes siguen
  siendo perfiles de config (persona + preset + tools) dentro de rutinas.
- Delta: perfiles por usuario/equipo (el "agente cotizador" de un AM puede tener persona
  distinta al de otro), heredables del workspace padre.
- El patron "una entidad -> una entidad por tenant" (costura E1) NO se ejerce aun: en
  Etapa 2 hay UNA entidad para el tenant MWT. Multiplicarla es Etapa 3.

### 1.7 La entidad viva (agente ambiental del sitio)
Es el delta cualitativo de Etapa 2: la entidad pasa de reactiva (responde en el canvas)
a **proactiva acotada** — un ciclo de revision continuo sobre todo el sitio:
- Recorre workspaces, inbox y KB en ciclos programados (scheduler de la capa de
  gobierno, no cron propio de la entidad).
- Detecta y PROPONE: correos sin draft, fuentes vencidas (stale_data_block), pendientes
  HITL estancados, rutinas fallidas, presupuesto de routing por agotarse, gold
  candidates sin revisar.
- Deposita todo como items en WorkLoom con evidencia; **nunca ejecuta irreversibles**.
  Propone y ejecuta solo lo reversible, igual que en Etapa 1.
- Limites duros (mitiga blind spot Fugu #11 — "rutinas con triggers/proactividad pueden
  volverse orquestador pesado"): frecuencia maxima de ciclo, budget cap propio del ciclo
  ambiental, tools allowlist de solo-lectura + creacion de items, kill switch por
  workspace.

#### 1.7.1 Ciclo ambiental: activacion, ventana y presupuesto
El scheduler de gobierno dispara el ciclo; la entidad **no** tiene su propio cron ni puede
auto-activarse. Defaults operativos (configurables por admin, nunca por debajo de los
limites duros):

| Parametro | Default | Minimo permitido | Razon |
|---|---|---|---|
| Frecuencia global | 30 min | 15 min | Evita costo ruido en tenants pequenos |
| Frecuencia por workspace | 1 h | 30 min | Un workspace no puede ser revisado constantemente |
| Ventana activa | 06:00-22:00 America/Bogota | 08:00-18:00 | Fuera de ventana solo eventos criticos |
| Budget ciclo ambiental | 5% del budget diario del router | 1% | Tope duro de costo autonomo |
| Max propuestas por ciclo | 10 por workspace | 3 | Evita inundar WorkLoom |

Fuera de la ventana activa el ciclo se ejecuta solo ante eventos criticos: rutina fallida,
budget del workspace agotado al >90%, o stale_data_block con fuentes marcadas como bloqueantes.

#### 1.7.2 Dark-launch y deduplicacion
**Dark-launch**: durante las primeras 2 semanas de E2-5 (o hasta decision del curador), el
ciclo corre en modo observacion: ejecuta detectores, genera propuestas internas y audita
ruido/utilidad, pero **no crea items visibles en WorkLoom**. Esto permite calibrar
sensibilidad sin contaminar la cola real.

**Deduplicacion**: cada detector genera una clave estable `hash(detector|target_id|bucket_temporal)`.
Antes de crear un item WorkLoom se consulta si ya existe una propuesta abierta o reciente
(< 24 h) para esa clave. Si existe, se anexa evidencia al existente en lugar de crear un duplicado.

#### 1.7.3 Backoff y circuit breakers
- **Backoff por error**: si un detector falla (API, DB, parser), el siguiente intento espera
  `2^n * 60 s` hasta un maximo de 4 h. Tres fallos consecutivos del mismo detector lo marcan
  `disabled` hasta revision manual.
- **Circuit breaker de utilidad**: si la razon `aceptadas / creadas` es < 20% durante 3 ciclos
  consecutivos, el ciclo ambiental se auto-pausa y alerta al admin. Solo se reanuda tras
  ajuste de detectores o reset explicito.
- **Circuit breaker de costo**: si un ciclo consume mas del 150% de su budget asignado,
  los detectores restantes se saltan y se registra `cost_overrun`.

#### 1.7.4 Metricas de ruido y utilidad
Cada ciclo escribe un registro `ambient_cycle` con:

| Metrica | Definicion | Umbral de alarma |
|---|---|---|
| propuestas_creadas | Items creados en WorkLoom | > max por ciclo |
| propuestas_aceptadas | Items movidos a "en progreso" o "hecho" | utilidad objetivo >= 25% |
| propuestas_ignoradas | Vistos sin accion | ruido si > 60% |
| costo_usd | Costo LLM/API del ciclo | > budget asignado |
| latencia_ms | Tiempo total del ciclo | > 5 min |
| detector_fallos | Fallos por detector | >= 3 consecutivos |

Dashboard minimo: serie temporal de utilidad/ruido por semana, costo acumulado vs budget,
y kill-switch activos.

#### 1.7.5 Auditoria por ciclo y kill switch
Cada ciclo genera un `audit_log` inmutable con:
- `cycle_id`, `started_at`, `ended_at`, `tenant_id`, `workspace_ids` revisados.
- Detectores ejecutados y resultados (solo metadatos; evidencia completa en `evidence_json`).
- Propuestas creadas con IDs de WorkLoom.
- Costo del ciclo y estado del budget.
- Estado del kill switch (`enabled`/`disabled` por workspace).

**Kill switch**: por workspace y global. Un admin puede desactivar el ciclo ambiental para
un workspace sin afectar a otros. El kill switch se verifica antes de cada detector y se
registra en audit. Al activarlo, las propuestas pendientes se marcan `cancelled_by_kill_switch`.

### 1.8 Archivos y almacenamiento (ingesta universal + MinIO)
- **Subida universal en el chat**: imagenes, audio, video, PDF, Excel, Word, Access,
  JSON, SQL — cualquier archivo. Cada tipo pasa por un pipeline de ingestion (extraer
  texto/tablas/transcripcion segun tipo) antes de llegar al modelo; los tipos ya
  robustos de E1 (CSV/XLSX/PDF/MD/TXT) se reusan tal cual.
- **MinIO dedicada a FaberLoom**: instancia propia de MinIO en el compose de
  `faber_loom` (patron identico a como `consola-mwt-one` agrupa sus servicios en su
  propio compose; NO se comparte la infraestructura entre ambos proyectos). Todo objeto
  subido por el usuario Y todo objeto generado por la IA (imagenes, exports, drafts
  renderizados) se persiste alli — la DB guarda solo metadata + referencia al objeto.
- **Sellado hereda al objeto**: bucket/prefijo por workspace; un objeto de un cliente
  jamas es legible desde otro workspace (mismo test de fuga de E2-3 extendido a
  objetos). Acceso via URLs presignadas con expiracion; nunca bucket publico.
- **Seguridad de ingesta**: los canaries de injection de E1 (PDF/HTML/Excel) se
  extienden a todos los tipos nuevos (audio transcrito, video, JSON, SQL). Archivo que
  dispara accion = falla P0. Limites de tamano y tipos ejecutables bloqueados.
- **Exfiltracion**: si el workspace tiene allowlist solo-local, el contenido de sus
  archivos NUNCA sale a un modelo cloud — el pipeline de ingestion respeta la misma
  allowlist del router (Sec.1.1).

## 2. Secuencia de build E2-0 -> E2-6

| Hito | Objetivo | Entregable | Can-start-when | Gate / DoD | Talla |
|---|---|---|---|---|---|
| E2-0 | Activar costuras + higiene E1 | Context(workspace, tenant, user) real en toda query; migracion datos E1; AuditWriter a tabla; login local; lote higiene herencia E1 (Sec.8: H6 runtime unico, H7 DEC promocion spike, H8 lessons learned, H9 LICENSE, sl1b json) | Etapa 1 DONE + gate adopcion pasado | app E1 corre identica con usuario autenticado; audit por actor; lote higiene commiteado | M |
| E2-1 | Servidor compartido | instancia self-hosted LAN/VPN; N usuarios concurrentes; decision motor DB ejecutada (Sec.4) | E2-0 | 2+ usuarios trabajan a la vez sin pisarse | L |
| E2-2 | Roles + HITL multi-user | roles AM/curador/CEO; WorkLoom cola compartida con asignacion; segundo gate gold | E2-1 | un draft creado por A es aprobado por B con rol registrado | M |
| E2-3 | KB compartida + sellado por rol | herencia org->equipo->workspace; sellado por rol sobre la costura de SL3.5; gold loop capa 2 (comite, k-anon) | E2-2 | test de fuga cross-rol y cross-workspace = 0, **incluido tenant canario** (Sec.7.3): M16 con 2do tenant sembrado = 0 filas cruzadas en ambas direcciones | L |
| E2-4 | Routing gestionado + catalogo + modo auto | keys admin; budget por usuario/equipo; catalogo multi-proveedor/local con tags de capacidad; selector manual en chat; dispatcher modo auto con guardrails; presets con ledger real | E2-1 | caso canonico end-to-end: PDF -> resumen (modelo barato) -> imagen (modelo image_gen), UI muestra solo el modelo final y el ledger muestra la cadena completa | L |
| E2-5 | Entidad viva | ciclo ambiental con limites duros (Sec.1.7); items proactivos en WorkLoom | E2-2 + E2-3 | la entidad detecta y propone (0 acciones irreversibles); el equipo acepta >=1 propuesta util/semana | L |
| E2-6 | Ingesta universal + MinIO | MinIO en compose faber_loom; subida de cualquier tipo en chat; pipelines por tipo; objetos generados por IA persistidos; sellado por workspace a nivel objeto | E2-1 (MinIO) / E2-4 (pipelines con modo auto) | subir archivo de cualquier tipo soportado -> objeto en MinIO sellado -> modelo lo procesa respetando allowlist; test de fuga de objetos = 0; canaries de ingesta pasan | L |

Estimacion (arquitecto, 1 dev full-time, con la leccion de E1 de que las tallas fueron
optimistas — Kimi §3):
- **Dogfood interno multi-usuario** (E2-0 -> E2-2, con E2-4 minimo): ~7-9 semanas.
  El equipo ya trabaja compartido desde aqui.
- **Etapa 2 completa** (E2-0 -> E2-6, con QA de sellado y canaries): ~14-18 semanas.
Tallas por hito: E2-0 M(~1.5s), E2-1 L(~2.5s), E2-2 M(~2s), E2-3 L(~2.5s),
E2-4 L(~2.5s), E2-5 L(~2.5s), E2-6 L(~2.5s). E2-4/E2-6 parcialmente solapables con
E2-3/E2-5. Compromiso: el calendario corto; el largo es el techo honesto.

## 3. Riesgos P0 + kill criteria

- **Fuga cross-workspace o cross-rol** -> test en E2-3; falla = no avanzar a E2-5.
- **Accion irreversible del ciclo ambiental** -> kill inmediato del hito E2-5; el ciclo
  vuelve a solo-lectura hasta auditoria.
- **Injection via contenido compartido** (un usuario planta contenido que dispara accion
  en la sesion de otro): canaries de E1 (email/PDF/Excel/KB/SKILL.md) se re-corren en
  modo multi-usuario. Falla = no liberar E2-2.
- **Gold contaminado entre AMs**: dato erroneo de un AM promovido a L3 -> k-anon + comite
  obligatorios; sin segundo gate no hay promocion.
- **Exfiltracion via archivos**: contenido de archivo de workspace confidencial enviado
  a modelo cloud pese a allowlist solo-local -> falla P0 de E2-6; no liberar.
- **Cadena auto sin techo**: modo auto que encadena pasos/costo sin limite -> budget cap
  y max-pasos son gate de E2-4, no opcionales.
- **Kill de Etapa**: si en Etapa 1 el gate de adopcion no paso (Alvaro dejo de usarlo),
  Etapa 2 NO arranca — multiplicar usuarios de algo que uno solo no adopta es multiplicar
  el fracaso (blind spot 7.10 de E1 sigue vigente).

## 4. Decisiones tecnicas que bloquean E2-1 — RESUELTAS (arquitecto, 2026-07-05)

1. **Motor DB: Postgres + RLS.** Es la costura que E1 dejo prevista ("SQLite hoy ->
   Postgres+RLS despues"), y el host ya opera Postgres en produccion (consola-mwt-one),
   asi que hay experiencia operativa real. Instancia PROPIA en el compose de
   faber_loom (`faberloom-postgres`, puerto host 5435 — el 5434 lo usa consola-mwt-one);
   nunca compartir la DB entre proyectos. Migracion: script SQLite -> Postgres en E2-0
   con verificacion de conteos por tabla.
2. **Auth interna: local.** Usuario + passphrase con hash Argon2id, sesion por token;
   sin directorio externo (equipo <10 personas, LAN/VPN; un IdP seria sobre-ingenieria
   hoy). La costura queda: si MWT adopta un directorio, se suma como capa OIDC sin
   tocar el modelo `user_id`.
3. **Despliegue: host actual 187.77.218.102.** Compose `faber_loom` ampliado
   (api + postgres + minio), detras de mwt-nginx, mismo patron que consola-mwt-one.
   Opera: Alejandro (dev/admin). Acceso del equipo via los dominios faberloom.ai
   ya proxied en Cloudflare.
4. **MinIO: prefijo-por-workspace** (`ws-{id}/...`), no bucket-por-workspace (limites
   de buckets y policies mas simples; el sellado lo hace la API + policy de la
   credencial de servicio). Retencion: sin borrado automatico en Etapa 2; alerta de
   disco al 80% y revision manual (borrar datos de clientes automaticamente es riesgo,
   no ahorro). Backup: `mc mirror` nocturno de ambos buckets al mismo destino de
   backup que ya usa el host para postgres; smoke test de restore antes de datos
   reales (regla heredada de DoD 7.5 E1). Config de despliegue/DNS: Anexo A.
5. **Capacidades multimodales: politica de catalogo, no lista fija.** El catalogo
   arranca con los proveedores de los que YA existen keys + los modelos locales que
   Ollama tenga instalados; cada modelo se registra con sus tags de capacidad al
   darlo de alta (el admin los declara, el sistema no los adivina). Si una capacidad
   no tiene modelo registrado (ej. `image_gen`), el modo auto responde "no hay modelo
   para esta tarea" — nunca finge la capacidad. Asi el plan no depende de que modelos
   existan al momento del build.

## 5. Prerequisitos (higiene de cierre Etapa 1)

1. ~~Gate de adopcion~~ RESUELTO — ver Sec.6 #1.
2. Recuperar y commitear `harness/prompts/sl1b_dogfood_prompts.json` (unico test rojo
   de la suite E1: 278/279; el archivo quedo fuera de git al cerrar SL1b). Unica
   tarea mecanica abierta; se hace en E2-0.
3. ~~SL5 dentro o diferido~~ RESUELTO — SL5 quedo DENTRO de Etapa 1: implementado y
   testeado detras del flag `FABERLOOM_ENABLE_EMAIL_CONNECTOR` (verificacion de cierre
   2026-07-05, suite desde git HEAD). E2-2 activa el flag en la instancia compartida.
4. Ratificacion de este plan = mandato CEO 2026-07-05 (esta sesion). El freeze scope
   de DEC_FB_SPACELOOM_FREEZE_SCOPE_v1 no se altera: Etapa 2 sigue siendo interna,
   sin SaaS.

## 6. Decisiones tomadas (por mandato CEO 2026-07-05: "resuelvelo todo")

1. **Gate de adopcion Etapa 1: PASADO, por decision CEO.** La instruccion de avanzar a
   Etapa 2 (esta sesion) lo declara; el cierre auditado existe
   (cierre_etapa1_faberloom.md, fugu, 2026-06-30) y la suite corre verde desde git
   HEAD (278/279, unico rojo por archivo faltante, no por codigo). Clausula honesta:
   si el uso real se detiene durante E2-0/E2-1, el gate se reabre y aplica el kill de
   etapa de Sec.3 — declarar el gate no fabrica adopcion.
2. **Motor DB y despliegue: resueltos en Sec.4** (#1 Postgres+RLS propio del compose,
   #3 host actual + mwt-nginx).
3. **Alcance del ciclo ambiental (Sec.1.7): TODOS los workspaces con `is_active`,
   inbox y KB del tenant.** Frecuencia: 1 ciclo global cada 30 min como techo, y por
   workspace maximo 1 revision/hora; ventana 06:00-22:00 America/Bogota (fuera de
   ventana solo eventos criticos: budget agotado, rutina fallida). Budget del ciclo
   ambiental: tope 5% del budget diario global del router. Todos estos valores son
   config de admin (defaults, no constantes); cambiarlos no requiere nueva version
   del plan. Sus limites duros (solo-lectura, 0 irreversibles, kill switch) SI son
   contrato y no son configurables hacia abajo.
4. **Dedicacion y calendario: 1 dev full-time (Alejandro), calendario dos vias de
   Sec.2** — compromiso sobre el corto (7-9 semanas a dogfood multi-usuario),
   techo honesto 14-18 para Etapa 2 completa. Arranque: al commitear E2-0.

---

## 7. Tenant: evidencia de linea base y test canario

### 7.1 Bootstrap del tenant (hecho, 2026-07-05)

El tenant MWT existe por **seed de instalacion**, no por UI: slug `mwt`, ACTIVE,
plan BETA, 3 usuarios, creado/activado 7/5/2026 ~10:28 (owner:
alejandro@muitowork.com). Es deliberado que NO exista pantalla de "crear empresa":
en Etapa 2 hay UN tenant y crear mas es la frontera con Etapa 3 (el flujo
signup -> tenant -> owner es el primer hito de esa etapa, no un faltante de esta).
Settings JSON del tenant aplicados conforme a Sec.6: timezone America/Bogota,
budget 5 USD/dia (2 por usuario, 5% ciclo ambiental), router manual con max 4
pasos, `ambient.enabled: false`, HITL irreversibles NEVER + segundo gate gold,
storage minio.faberloom.ai con buckets fl-uploads/fl-generated. Ambient y modo
auto se encienden solo al pasar los gates de E2-5 y E2-4 respectivamente.

### 7.2 M16 linea base (verde, 2026-07-05)

Reporte "Aislamiento multi-tenant (M16)": 21 tablas `fnd_*`, scoping OK en todas,
0 filas de otros tenants (pobladas: audit_log 52, events 29, sessions 22, roles 4,
users 3, user_roles 3; el resto en 0 por modulos aun sin uso).
**Lectura honesta:** con un solo tenant en la base, "0 filas de otros tenants" es
verdad por definicion. Este verde prueba que el scoping esta CABLEADO en las 21
tablas (linea base valiosa), pero NO prueba el filtro bajo presion. Por si solo
NO cierra el gate de fuga de E2-3.

### 7.3 Tenant canario (obligatorio en gate E2-3)

Prueba real del aislamiento: un segundo tenant `canary` sembrado con filas basura
reconocibles (prefijo `CANARY_`) en TODAS las tablas `fnd_*`. El gate exige:
- M16 desde sesion MWT: 0 filas del canario visibles.
- M16 desde sesion canary: 0 filas de MWT visibles (ambas direcciones).
- Cualquier query que olvide el filtro `tenant_id` la delata el canario al instante.
El canario es **permanente**: no se borra al pasar el gate; M16-contra-canario se
corre en cada despliegue como test de regresion. Sus filas se excluyen de
dashboards y del gold loop (flag `is_canary`). Al migrar a Postgres+RLS (E2-0/E2-1),
el mismo canario valida que las policies RLS filtran, no solo la capa de app.

---

## 8. Herencia de Etapa 1: gaps, parciales y pendientes — CERRADOS POR DECISION

Fuente: estado de avance 2026-07-06 (spike E1 SL0-SL4 cerrados, SL5 parcial, SPINE
Camino B verde en Django/Postgres + 14/14 modulos M07-M20 portados a app/ FastAPI,
294 tests, v0.2.0). Nada de esta lista queda como gap: cada item tiene decision y
hito donde aterriza.

| # | Item heredado de E1 | Estado E1 | DECISION (arquitecto, 2026-07-06) | Aterriza en |
|---|---|---|---|---|
| H1 | SL5 correo sin cierre formal (PRC-09 diferido) | Parcial | SL5 se declara **cerrado tecnico** (connector + flag + canaries + outbox ya testeados: test_sl5_*). El cierre FORMAL es parte del gate de E2-2: activar flag en instancia compartida + 1 correo real end-to-end (recibir -> draft -> aprobar -> enviar) | E2-2 |
| H2 | PRC-09 credenciales de correo + rotacion IMAP Kimi Work | Bloqueo | Rotar credenciales IMAP Kimi Work como PRIMERA tarea de E2-2 (30 min, la hace el dev); cada AM conecta sus cuentas propias via app-password — no hay credencial compartida, asi que PRC-09 deja de ser procurement y pasa a ser onboarding por usuario | E2-2 |
| H3 | PRC-01/02 datos reales MWT en KB | Gap | La carga de KB real (catalogo, listas de precios Marluvas/Tecmater, fichas) es entregable de E2-1: la instancia compartida arranca CON datos reales, no seed. Responsable: Alejandro carga, un AM verifica citas | E2-1 |
| H4 | PRC-03 criterio de adopcion: N sin fijar | Pendiente CEO | **N = 10 casos reales voluntarios en 14 dias corridos por usuario activo** (calibrado con el dogfood SL1b: 10 drafts, edit_pct 3.66%). "Friccion que mata" = tener que salir de la app para terminar el caso (copiar/pegar manual, recalcular afuera); 3 casos consecutivos con friccion = alto y diagnostico | gate E2-2 |
| H5 | PRC-05/06/07 certificados firma Win/Mac + llave update publicable | Bloqueo | **No bloquean Etapa 2.** Para equipo interno (LAN/VPN, <10 maquinas conocidas) el self-signed + Ed25519 actual es suficiente y el riesgo es aceptable. Certificados comerciales (cert OV Windows + Apple Developer USD 99) se compran al ARRANCAR E2-6, para que la salida distribuible no espere; presupuesto aprobado por esta decision | compra en E2-6; uso post-E2 |
| H6 | Doble stack: SPINE Django/Postgres (canonico) vs port FastAPI/SQLite (app/) | Ambiguedad | **UN solo runtime: app/ FastAPI** (294 tests, 14/14 modulos, ya es lo que el equipo usa). El SPINE Django/Postgres NO se mantiene como codigo vivo: pasa a ser CONTRATO DE REFERENCIA — sus gates (RLS FORCE, hash chain, fail-closed) son la definicion de verde que el port debe igualar sobre Postgres en E2-0/E2-1. Coherente con el principio E1 "una entidad, sin runtimes paralelos". El repo Django se archiva con tag, no se borra | E2-0 |
| H7 | Deploy del spike en VPS (/opt/faber_loom, app.faberloom.ai) — manifiesto pedia renombrar a spike | Pendiente | **Se PROMUEVE, no se renombra**: ese deploy (Docker+nginx+JWT multi-user, ya corriendo) es la base fisica de la instancia compartida de E2-1. Renombrarlo para luego levantar otro identico seria trabajo doble. La promocion se documenta en DEC_FB_SPIKE_PROMOTION (E2-0) que supersede la instruccion de renombre del manifiesto 2026-06-30 | E2-0/E2-1 |
| H8 | SPEC_FB_SPIKE_E1_LESSONS_LEARNED + portar 7 aprendizajes a specs canonicos | Pendiente | Se escribe en E2-0 como parte de la higiene de arranque (mismo lote que sl1b_dogfood_prompts.json y DEC_FB_SPIKE_PROMOTION). Es 1 documento, no un proyecto | E2-0 |
| H9 | Licencia FSL sin confirmar | Pendiente legal | **FSL 1.1 adoptada** (era la recomendada del plan E1 y nadie presento alternativa en 2 revisiones). Registro de marca FaberLoom arranca en paralelo; ninguno de los dos bloquea build interno | E2-0 (aplicar LICENSE al repo) |
| H10 | Calendario Foundation Beta 8-10 vs 14-18 + sunset del spike | Pendiente CEO | Ya resuelto en v1.4 (Sec.6 #4): dos vias, compromiso 7-9 semanas dogfood / techo 14-18. El "sunset del spike" queda SIN OBJETO por H7: el spike no muere, se promueve — lo que hace sunset es el stack Django (H6) | Sec.6 |

Regla de esta seccion: si durante el build un H# resulta mal decidido, se cambia con
changelog — pero nunca vuelve a estado "pendiente/gap". Toda re-decision reemplaza,
no reabre.

---

## Anexo A. Configuracion MinIO para faberloom.ai

Objetivo: instancia MinIO propia de FaberLoom, separada de la MinIO existente de
muito.work (`minio.muito.work` / `console.minio.muito.work`), replicando el mismo
patron de despliegue en el host 187.77.218.102.

### A.1 DNS (Cloudflare, zona faberloom.ai)

Crear 2 registros A (hoy la zona solo tiene app/n8n/wc/root/www):

| Nombre | Tipo | Contenido | Proxy | Uso |
|---|---|---|---|---|
| `minio.faberloom.ai` | A | 187.77.218.102 | DNS only | endpoint S3 (API, presigned URLs) |
| `console.minio.faberloom.ai` | A | 187.77.218.102 | DNS only | consola web admin |

Notas:
- **DNS only en el endpoint S3 es deliberado** (mismo patron que minio.muito.work): el
  proxy de Cloudflare free limita uploads a ~100 MB por request y rompe archivos
  grandes (video). Presigned URLs van directo al origen.
- Tradeoff IP expuesta: **ACEPTADO** (decision arquitecto). La IP 187.77.218.102 ya
  esta expuesta por minio.muito.work y console.minio.muito.work (DNS only) — dos
  registros mas no agregan superficie nueva. Mitigacion vigente: firewall del host
  solo con 80/443 + puertos publicados necesarios, TLS en origen. Mejora programada
  (no bloqueante): migrar los endpoints DNS-only a Cloudflare Tunnel al cierre de
  E2-6.
- TLS del origen: **Let's Encrypt via certbot gestionado en mwt-nginx**, igual que el
  resto de dominios del host. Si al abrir los conf existentes se encuentra otro
  mecanismo ya operando, se replica ese — la regla es un solo mecanismo TLS por host,
  no dos.

### A.2 Servicio en el compose de faber_loom (propuesta)

Agregar al compose existente (hoy solo `faberloom-api` en 8200:8000). Puertos host
propuestos evitando colision con lo ya publicado (8100, 3101, 5434, 6380, 8200 y los
que use la MinIO de muito.work — verificar en el host antes de fijar):

```yaml
  faberloom-minio:
    image: minio/minio:latest        # fijar tag exacto al desplegar
    container_name: faberloom-minio
    command: server /data --console-address ":9001"
    ports:
      - "9100:9000"   # S3 API   (propuesta; verificar libre en host)
      - "9101:9001"   # Console  (propuesta; verificar libre en host)
    environment:
      MINIO_ROOT_USER: "${FL_MINIO_ROOT_USER}"       # .env NO versionado
      MINIO_ROOT_PASSWORD: "${FL_MINIO_ROOT_PASSWORD}" # generar: openssl rand -hex 32
      MINIO_SERVER_URL: "https://minio.faberloom.ai"
      MINIO_BROWSER_REDIRECT_URL: "https://console.minio.faberloom.ai"
    volumes:
      - faberloom_minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 30s
    restart: unless-stopped

volumes:
  faberloom_minio_data:
```

### A.2.1 Reverse proxy: mwt-nginx (aqui viven los .conf)

El ruteo de dominios -> puertos del host lo hace **mwt-nginx**; toda la configuracion
de puertos y server blocks vive en sus archivos `.conf`. Para esta MinIO se agregan
2 conf nuevos alli (no en el compose de faber_loom), siguiendo el patron de los conf
existentes (ej. el de minio.muito.work):

- `minio.faberloom.ai` -> proxy_pass al :9100 (S3 API)
- `console.minio.faberloom.ai` -> proxy_pass al :9101 (consola)

Propuesta de server block (ajustar al estilo de los conf existentes en mwt-nginx):

```nginx
# minio.faberloom.ai.conf — S3 API
server {
    server_name minio.faberloom.ai;
    # TLS: certbot/Let's Encrypt, mismo mecanismo del resto de conf de mwt-nginx (A.1)

    ignore_invalid_headers off;
    client_max_body_size 0;        # sin tope: videos/archivos grandes
    proxy_buffering off;
    proxy_request_buffering off;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_pass http://127.0.0.1:9100;
    }
}

# console.minio.faberloom.ai.conf — consola web
server {
    server_name console.minio.faberloom.ai;
    # TLS: idem (certbot, A.1)

    client_max_body_size 0;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # websockets (la consola los usa)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://127.0.0.1:9101;
    }
}
```

Notas (decisiones):
- **Puertos: 9100/9101 quedan fijados.** No colisionan con nada publicado conocido
  (8100, 3101, 5434, 6380, 8200) ni con los defaults 9000/9001 que usaria la MinIO de
  muito.work. El unico paso al desplegar es `ss -tlnp | grep -E '9100|9101'`; si
  contra todo pronostico estan tomados, correr al siguiente par libre (9102/9103) y
  actualizar los 2 conf — decision de 5 minutos del dev, no del CEO.
- **proxy_pass: via puerto publicado (`127.0.0.1:9100/9101`).** Es la opcion que
  funciona igual si mwt-nginx corre como contenedor con network_mode host, como
  proceso del host o en otra red compose — no acopla los dos proyectos a una red
  Docker compartida (misma filosofia de aislamiento que el resto del plan). Si los
  conf existentes de mwt-nginx ya proxean por nombre de servicio en una red comun,
  el dev replica ese patron; ambas rutas son validas, la publicada es el default.

### A.3 Buckets y acceso (propuesta inicial)

- `fl-uploads` — archivos subidos por usuarios (prefijo por workspace: `ws-{id}/...`).
- `fl-generated` — objetos producidos por la IA (misma estructura de prefijos).
- Credencial de servicio para `faberloom-api` (access key propia, NO el root user),
  con policy limitada a esos 2 buckets.
- Acceso de lectura solo via presigned URLs con expiracion emitidas por la API;
  ningun bucket publico. Decision bucket-vs-prefijo por workspace: Sec.4 #4.
- La MinIO de muito.work NO se toca ni se comparte: cada proyecto su instancia,
  como consola-mwt-one y faber_loom hoy.

---

Changelog:
- v1.0 (2026-07-05): Creacion. Plan de build Etapa 2 (multi-usuario interno) sobre las
  costuras contract-first de Etapa 1 cerrada (cierre auditado 2026-06-30). Define los 7
  pilares (routing, inbox, KB, HITL, skills, agentes, entidad viva), secuencia E2-0->E2-5,
  riesgos P0, decisiones tecnicas bloqueantes y prerequisitos. DRAFT — sin calendario
  comprometido hasta decision de motor DB y gate de adopcion E1.
- v1.1 (2026-07-05): Por directriz CEO: router estilo OpenRouter/Ollama (catalogo
  multi-proveedor/multi-key + modelos locales, modo manual en chat, modo auto con
  dispatcher barato que descompone y encadena tareas, atribucion = solo modelo final
  visible con cadena completa en evidence/ledger); nueva Sec.1.8 ingesta universal de
  archivos (cualquier tipo, incl. audio/video) + MinIO dedicada FaberLoom en el compose
  faber_loom con sellado por workspace a nivel objeto; hito E2-6; riesgos exfiltracion
  via archivos y cadena auto sin techo; decisiones tecnicas 4-5.
- v1.2 (2026-07-05): Anexo A — configuracion MinIO faberloom.ai: 2 registros A en
  Cloudflare (minio./console.minio.faberloom.ai -> 187.77.218.102, DNS only, mismo
  patron que minio.muito.work), servicio propuesto en el compose faber_loom (puertos
  9100/9101 propuestos, secrets pendientes), buckets fl-uploads/fl-generated con
  prefijo por workspace y credencial de servicio no-root. Instancia separada de la
  MinIO de muito.work.
- v1.3 (2026-07-05): A.2.1 — el ruteo dominios->puertos lo hace mwt-nginx (los .conf
  viven alli): 2 server blocks nuevos propuestos (minio./console.minio.faberloom.ai),
  client_max_body_size 0, websockets en consola, TLS y proxy_pass (127.0.0.1 vs red
  Docker) a verificar contra los conf existentes.
- v1.4 (2026-07-05): Por mandato CEO ("resuelvelo todo"), el arquitecto cierra TODOS
  los pendientes: gate adopcion E1 declarado PASADO (con clausula de reapertura si el
  uso se detiene); motor DB = Postgres+RLS propio del compose (puerto 5435); auth
  local Argon2id; despliegue en host actual tras mwt-nginx; MinIO prefijo-por-workspace,
  sin borrado automatico, mc mirror nocturno; catalogo multimodal por politica (tags
  al alta, sin fingir capacidades); ciclo ambiental = todos los workspaces activos,
  techo 30 min global / 1h por workspace, ventana 06-22 Bogota, tope 5% budget;
  calendario dos vias 7-9 / 14-18 semanas, 1 dev (Alejandro); tradeoff IP aceptado
  (Tunnel post-E2-6); TLS certbot; puertos 9100/9101 fijados; proxy_pass via puerto
  publicado; secrets via .env no versionado. Sec.6 pasa de "Pendientes CEO" a
  "Decisiones tomadas". SL5 confirmado DENTRO de E1 (flag).
- v1.5 (2026-07-05): Nueva Sec.7 (tenant): 7.1 evidencia de bootstrap del tenant MWT
  por seed + settings aplicados (sin UI de crear empresas: eso es Etapa 3); 7.2 M16
  linea base verde en 21 tablas fnd_* con lectura honesta (single-tenant = verde
  trivial, no cierra gate); 7.3 tenant canario permanente con filas CANARY_ en todas
  las tablas, bidireccional, como requisito del gate E2-3 y regresion en cada
  despliegue. Gate E2-3 actualizado en la tabla de Sec.2.
- v1.6 (2026-07-06): Nueva Sec.8 — herencia de Etapa 1 cerrada por decision (mandato
  CEO: nada queda como gap/parcial/bloqueo): H1 SL5 cierre formal en gate E2-2;
  H2 rotacion IMAP Kimi Work primera tarea E2-2 + cuentas por usuario; H3 KB real
  MWT entregable de E2-1; H4 adopcion N=10 casos/14 dias + definicion de friccion;
  H5 certs de firma no bloquean (self-signed interno; compra al arrancar E2-6);
  H6 runtime unico app/ FastAPI, SPINE Django pasa a contrato de referencia
  (archivado con tag); H7 deploy del spike se PROMUEVE a instancia E2-1
  (DEC_FB_SPIKE_PROMOTION supersede renombre del manifiesto); H8 lessons learned
  en E2-0; H9 licencia FSL 1.1 adoptada; H10 sunset del spike sin objeto (muere el
  stack Django, no el spike). E2-0 ampliado con lote de higiene. Regla: re-decidir
  reemplaza, nunca reabre.
- v1.7 (2026-07-06): Sec.1.7 expandida con subsecciones 1.7.1-1.7.5: ciclo ambiental
  (activacion, ventana, presupuesto), dark-launch, deduplicacion, backoff/circuit
  breakers, metricas de ruido/utilidad y auditoria por ciclo + kill switch. Mantiene
  los limites duros (solo-lectura + creacion de items, 0 irreversibles) y deja los
  defaults como configuracion de admin.
