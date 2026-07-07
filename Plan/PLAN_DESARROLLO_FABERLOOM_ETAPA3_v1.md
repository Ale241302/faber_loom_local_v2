# PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1 -- Plan de Build FaberLoom Etapa 3 (multi-tenant + fabrica de skills)
id: PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-07-07 -- plan de build Etapa 3; disenado sobre cierre_etapa2_faberloom.md v1.0
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md - cierre_etapa2_faberloom.md - SPEC_SPACELOOM_ETAPA1_v1.md (SS8: definicion Etapa 3) - SPEC_FB_EVOLUTION_ROADMAP_v1.md (Fases 4-5) - ARCH_FB_AGENT_RUNTIME_EVAL_v1.md - ENT_FB_SKILL_CATALOG_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md - ENT_FB_PRICING_TIERS_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - DEC_FB_SPIKE_PROMOTION (E2)

Nota de nombre: las etapas 1-2 se llamaron PLAN_DESARROLLO_SPACELOOM_*. Etapa 3 se nombra
FABERLOOM deliberadamente: SpaceLoom es una superficie; lo que se construye aqui es el
producto multi-tenant (SPEC_SPACELOOM_ETAPA1 SS8: "Etapa 3 = el FaberLoom pausado").

---

## 0. Que es la Etapa 3 (y que NO)

**Etapa 3 = multi-tenant + fabrica de skills.** Definicion canonica (SPEC_SPACELOOM_ETAPA1
SS8): "multi-tenant / SaaS (el FaberLoom pausado; sello criptografico,
ARCH_FB_AGENT_RUNTIME_EVAL)". El sistema que en Etapa 2 usa el equipo MWT (un tenant, seed,
sin UI de crear empresa) pasa a soportar N tenants aislados, con el flujo
signup -> tenant -> owner que el plan E2 SS7.1 declaro explicitamente como "el primer hito
de esa etapa". Y la entidad deja de tener 14 skills heredadas: se dota con el catalogo
maestro ENT_FB_SKILL_CATALOG_v1 (62 skills en 13 packs), en olas, con dogfood MWT primero.

Corresponde a las Fases 4-5 del SPEC_FB_EVOLUTION_ROADMAP (aprendizaje ya parcialmente
cubierto por el gold loop de E2-3; multi-tenant real + BYO keys aqui).

**NO es Etapa 3** (diferido a Etapa 4, coherente con roadmap Fase 6 y "profundidad antes
que amplitud"):
- MCP server (exponer FaberLoom a Cowork/n8n) y el resto de superficies UI.
- Agent builder de 168 agentes; segundo vertical masivo.
- Pasarela de pagos automatizada (el cobro de Etapa 3 es manual, ver Sec.6 #6).
- Learning cross-tenant (L3/L4 entre tenants distintos): PROHIBIDO en Etapa 3; el gold
  loop k-anon opera solo DENTRO de cada tenant.
- App movil, marketplace de skills publico, self-service de billing.

**Gate comercial invertido (decision Sec.6 #1):** la clausula "solo si la validacion de
mercado lo justifica" (SPEC_SPACELOOM_ETAPA1 SS8) no bloquea el arranque: el mandato CEO
2026-07-07 (cierre E2 + orden de disenar E3) levanta la pausa. La validacion de mercado
pasa de gate de ENTRADA a gate de SALIDA: cerrar Etapa 3 exige 1 tenant externo real
(E3-6). Si no aparece, aplica el kill honesto de Sec.5.

## 1. Los 5 pilares de Etapa 3 (delta sobre Etapa 2)

### 1.1 Runtime en Postgres+RLS (la deuda que ya no puede esperar)
E2 dejo el staging validado (migracion completa 616 filas, policies aplicadas, canario RLS
verde bidireccional) pero el runtime sigue en SQLite. Multi-tenant SaaS sobre SQLite es
inaceptable: RLS es la capa de aislamiento que no depende de que la app recuerde el filtro.
El switch es el cimiento fisico de todo lo demas y por eso es E3-1, antes de crear tenants.

### 1.2 Tenant lifecycle (signup -> tenant -> owner)
La pantalla de "crear empresa" que E2 deliberadamente NO construyo. Bootstrap seed
programatico (SPEC_FB_TENANT_BOOTSTRAP_SEED_v1), herencia de config en cascada
tenant -> workspace -> user, limites por plan (ENT_FB_PRICING_TIERS_v1), rol
platform_admin que administra tenants sin poder leer su contenido.

### 1.3 Entidad por tenant + sello criptografico
El patron "una entidad -> una entidad por tenant" (costura declarada en E2 SS1.6) se
ejerce aqui, con el modelo de ARCH_FB_AGENT_RUNTIME_EVAL: identidad inmutable por tenant,
indice global (sabe-donde) vs contenido sellado (resuelve-local), memoria namespaced por
tenant y visibilidad, llave graduada controlada por el owner (el agente nunca tiene la
llave), cifrado por tenant para credenciales y objetos.

### 1.4 Fabrica de skills (el catalogo se materializa)
ENT_FB_SKILL_CATALOG_v1: 62 skills / 13 packs (33 GAP, 29 TEMPLATE). No se escriben una a
una a mano alzada: se construye la GRAMATICA (primitivos P01-P18 + manifest v2 + compiler)
y se instancia por pack, en olas, con golden cases de la operacion MWT real. Los skills
son el VALOR que un tenant externo compra; por eso la fabrica corre en paralelo desde
E3-0 (es contenido + manifest sobre la instancia viva, no requiere el switch de DB).

### 1.5 Routing por tenant (BYO keys)
Cada tenant puede registrar sus propias API keys y modelos (roadmap F5: "disponibilidad
heredada, estricto + hibrido opt-in"); ledger y budgets por tenant ademas de por usuario;
presets builder UI (el menor diferido de E2-4) se cobra aqui.

## 2. Secuencia de build E3-0 -> E3-6

| Hito | Objetivo | Can-start-when | Gate / DoD | Talla |
|---|---|---|---|---|
| E3-0 | Cierre operativo de E2 + seguridad | cierre E2 commiteado (hecho 2026-07-07) | los 4 gates operativos E2 ejecutados o corriendo (correo H1, auto ON, ambient dark-launch, seguridad rotada); acta "Etapa 2 TERMINADA" | M |
| E3-1 | Switch runtime Postgres+RLS | E3-0 tareas 1-2 (seguridad + correo; no espera el dark-launch de 14 dias) | prod corre en Postgres; suite verde; canario RLS bidireccional en cada deploy; 7 dias sin regresion | L |
| E3-2 | Tenant lifecycle | E3-1 | tenant demo creado por signup UI end-to-end; aislamiento N-tenant verde; limites de plan enforced | L |
| E3-3 | Entidad por tenant + sello | E3-2 | contamination suite 0 fugas (datos, memoria, identidad, objetos); llave graduada auditada; identidad no reescribible | L |
| E3-4 | Fabrica de skills (olas 0-5) | fundacion: E3-0 tarea 1. Olas: ver Sec.4 | PACK 1 y PACK 3 ACTIVE en dogfood MWT con golden cases verdes; resto de olas segun Sec.4 | XL (por olas) |
| E3-5 | Routing por tenant + BYO keys + presets builder | E3-2 | tenant demo opera con su propia key sin tocar keys MWT; ledger separa costo por tenant; preset creado desde builder UI | M |
| E3-6 | Primer tenant externo + billing manual | E3-3 + E3-5 + E3-4 ola 1 | 1 tenant externo activo >=30 dias, >=10 casos reales, aislamiento verde, primera factura emitida (con PACK 1) y pagada | L |

E3-4 es una banda paralela, no un eslabon de la cadena: regla de dedicacion en Sec.7.

## 3. Detalle por hito (que toca hacer, en orden)

### E3-0 -- Cierre operativo de E2 + seguridad (talla M)

Todo esto es herencia del cierre E2 (Sec.8-9 de cierre_etapa2_faberloom.md). Nada queda
como gap: cada item tiene tarea, responsable y criterio.

1. **Seguridad primero (dia 1, dev):** rotar password root del VPS; migrar SSH a llaves
   (`PasswordAuthentication no`); rotar TODAS las claves de correo compartidas por chat
   en la sesion 2026-07-07 (incl. info@mwt.one); verificar que `.env` del VPS no este en
   git y que las credenciales en BD sigan cifradas (Fernet). Criterio: login por password
   imposible; claves viejas revocadas.
2. **Gate H1 correo end-to-end (humano, dev + 1 AM):** rotar/verificar credenciales de
   trade@ y mw_doc@ (fallaron 535 en E2); ejecutar 1 correo real completo desde la UI:
   recibir -> draft -> aprobar (rol registrado) -> enviar, con info@mwt.one ya conectado.
   Criterio: el ciclo consta en audit con actor_id y actor_role_at_decision.
3. **Encendido modo auto (gate E2-4):** activar para el equipo con la politica vigente
   (budget 2 USD/usuario, max 4 pasos); 7 dias de observacion del ledger. Criterio: >=1
   cadena auto real por usuario activo sin sobrecosto (>100% budget) ni fail de guardrail.
4. **Arranque dark-launch ciclo ambiental (gate E2-5):** `ambient_config.global_enabled=1`;
   14 dias en modo observacion (ya implementado); al salir de dark, medir aceptacion de
   propuestas. Criterio de encendido visible: utilidad >=25% (el CB de utilidad ya lo
   enforcea); si no llega, el ciclo queda en dark y se recalibran detectores (no es
   bloqueante del resto de E3).
5. **KB real (H3, tarea condicionada -- respeta la decision CEO 2026-07-07 de diferirla):**
   la carga se ejecuta cuando existan los archivos Marluvas/Tecmater (el cargador ya esta
   listo). Deadline duro NO negociable: antes de arrancar la ola 3 de skills (PACK 2 comex
   usa importaciones Marluvas como golden cases -- Sec.4). Responsable de conseguir los
   archivos: CEO; de cargar y verificar citas: dev + 1 AM.
6. **Whisper en imagen runtime (decision arquitecto: SI, talla S):** instalar
   faster-whisper en la imagen para cerrar el fail-closed de audio/video de E2-6. Modelo
   `small` multilenguaje local (respeta require_local_only por diseno). Criterio: subir un
   audio -> transcripcion en el pipeline de ingesta -> canary de injection sobre
   transcripcion pasa.
7. **Acta de cierre:** cuando 1-4 esten ejecutados (5 puede quedar condicionada, 6 es S),
   escribir `ACTA_ETAPA2_TERMINADA` (1 pagina) declarando Etapa 2 TERMINADA con los gates
   y fechas. Sin acta no se declara terminada: el cierre actual es "construida", no
   "terminada".

DoD del hito: tareas 1-3 ejecutadas; 4 corriendo (los 14 dias no bloquean E3-1); acta
escrita al completarse.

### E3-1 -- Switch runtime Postgres+RLS (talla L)

Base heredada: `sqlite_to_postgres.py` corregido y validado (616 filas verificadas),
`postgres_rls_policies.sql` aplicado, rol `faberloom_app` con NOBYPASSRLS, canario RLS
verde bidireccional. Falta la capa de runtime (documentado en DEC_FB_SPIKE_PROMOTION).
Contrato de referencia (H6 de E2): los gates del SPINE Django -- RLS FORCE, fail-closed,
hash chain de audit -- definen el verde que este port debe igualar.

1. **Adapter de conexion dual** en `db.py` y foundation: psycopg3 con pool, placeholders
   `%s`, transacciones explicitas; flag `FABERLOOM_DB_ENGINE=sqlite|postgres` (default
   sqlite hasta el corte). Regla: cero query con placeholder hardcodeado de un solo motor;
   el adapter traduce. `SET LOCAL app.tenant_id` (o equivalente de sesion) en cada
   transaccion para que RLS filtre por el Context -- el tenant fluye via context, NUNCA
   via headers (regla multi-tenant inquebrantable).
2. **FTS5 -> tsvector/GIN:** portar las queries de busqueda de KB; indices GIN; paridad
   funcional verificada con un set fijo de queries de busqueda (mismos resultados top-k o
   mejor).
3. **Suite completa contra Postgres:** las 398 pasan con `FABERLOOM_DB_ENGINE=postgres`
   en el contenedor de test (levanta postgres efimero). Los 2 fallos de entorno conocidos
   se resuelven o se documentan como exentos con razon.
4. **Ensayo de corte en staging:** migracion fresca + smoke manual + 
   `check_canary_isolation.py` contra RLS real. Dos ensayos verdes consecutivos antes del
   corte real.
5. **Corte real (ventana 22:00-06:00 Bogota):** freeze de escrituras (modo read-only de la
   API), migracion, verificacion de conteos por tabla, switch del flag, canario, smoke,
   unfreeze. Plan de rollback escrito ANTES del corte: volver el flag a sqlite (la BD
   SQLite no se toca durante el corte).
6. **Post-corte:** SQLite queda como respaldo read-only 30 dias, luego se archiva con tag.
   `check_canary_isolation.py` (ahora contra RLS) sigue bloqueando cada deploy. Backup
   nocturno de Postgres verificado con smoke de restore (regla heredada DoD 7.5 E1).

Gate/DoD: prod en Postgres; suite verde; canario RLS en deploy; 7 dias sin regresion
funcional. Kill: 2 cortes fallidos -> se re-disena el adapter antes de un tercer intento
(no se insiste a golpes contra una ventana de mantenimiento).

### E3-2 -- Tenant lifecycle: signup -> tenant -> owner (talla L)

1. **Flujo signup:** pantalla publica de registro (nombre empresa -> slug unico, email
   owner, passphrase Argon2id); verificacion de email (SMTP ya operativo); el primer
   usuario del tenant nace `owner`. Anti-abuso minimo: rate limit por IP + registro
   requiere aprobacion de platform_admin en Etapa 3 (signup abierto de verdad es Etapa 4)
   -- esto elimina captchas y spam-handling del alcance sin dejar la puerta abierta.
2. **Bootstrap seed programatico** (implementa SPEC_FB_TENANT_BOOTSTRAP_SEED_v1): al
   aprobar el tenant se siembran roles de sistema (owner/am/curador/ceo), settings default
   identicos al patron MWT (timezone del tenant, budget por plan, `ambient.enabled:false`,
   HITL irreversibles NEVER + segundo gate gold, storage prefijado), workspace inicial
   vacio. El seed es el MISMO codigo que sembro MWT (se parametriza, no se duplica).
3. **Herencia de config en cascada** tenant -> workspace -> user para LLM configs, tools
   y skills habilitadas; overrides viven en su scope y no se filtran a otros tenants
   (regla multi-tenant #3). Resolucion determinista: user > workspace > tenant > default.
4. **Limites por plan** (ENT_FB_PRICING_TIERS_v1): usuarios max, storage max (MinIO),
   budget LLM/dia por tier; enforcement fail-closed (mismo patron del budget cap E2-4:
   verificar ANTES de gastar, 422 con detalle). El plan de un tenant lo cambia solo
   platform_admin.
5. **Rol platform_admin** (solo Alejandro en Etapa 3): crear/aprobar/suspender tenants,
   ver metricas agregadas (conteos, costo, salud) -- NUNCA contenido (mensajes, KB,
   objetos). La llave graduada de E3-3 lo hace criptografico; aqui nace como RBAC +
   audit de cada accion de plataforma.
6. **Aislamiento N-tenant:** `check_canary_isolation.py` se generaliza: para CADA tenant
   y cada tabla `fnd_*`, scope propio devuelve solo lo propio; el canario permanente
   sigue vivo; al crear un tenant nuevo corre el check automaticamente. Prefijos MinIO
   pasan a `t-{tenant}/ws-{workspace}/...` (los objetos MWT existentes se migran con
   script + verificacion de conteo).

Gate/DoD: tenant demo `acme` creado via UI end-to-end; M16 N-tenant 0 fugas; limites de
plan enforced (test que excede y recibe 422); acciones de platform_admin auditadas.

### E3-3 -- Entidad por tenant + sello criptografico (talla L)

Implementa el modelo de ARCH_FB_AGENT_RUNTIME_EVAL SS1 (los 7 puntos), que es la
definicion canonica de esta capa:

1. **Identidad inmutable por tenant:** la persona/identidad del agente-entidad de cada
   tenant es read-only en sesion, versionada; cambiarla es operacion de owner con audit.
   Test: intento de auto-reescritura desde una sesion = rechazado y auditado.
2. **Indice global vs contenido sellado:** el agente sabe QUE existe y DONDE entre los
   espacios de SU tenant (punteros/metadata), pero el contenido queda sellado al
   workspace activo. Cross-TENANT no hay ni indice: un tenant no sabe que otros existen.
3. **Memoria namespaced** (extiende M17): claves de memoria prefijadas por
   tenant+dominio+visibilidad; un agente vivo persistente jamas mezcla memoria entre
   tenants ni entre visibilidades. Migracion de la memoria MWT existente al namespace.
4. **Llave graduada por politica:** tres posiciones (cerrada / indice abierto -- default /
   contenido abierto) por espacio, controlada por el owner del tenant, versionada y
   auditada; apertura = consulta mediada por broker, el agente nunca tiene la llave.
   PISO: CEO-ONLY y FROZEN no cruzan a menor visibilidad aunque se abra la llave.
5. **Cifrado por tenant:** envelope encryption -- master key de plataforma + data key por
   tenant (derivada/almacenada cifrada); credenciales, correo y objetos sensibles de un
   tenant se cifran con SU key. Rotacion de data key por tenant documentada. (Las
   credenciales ya usan Fernet global: se re-cifran por tenant en la migracion.)
6. **Contamination test suite a fondo** (roadmap F5): ademas del canario de filas, canaries
   de injection cross-tenant (contenido plantado en tenant A no dispara accion en B),
   memoria (recuerdo de A invisible en B), gold loop (k-anon >=5 SOLO dentro del tenant;
   promocion cross-tenant inexistente por codigo, no por config), objetos MinIO
   (presigned URL de A invalida con sesion de B).
7. **Ciclo ambiental multi-tenant:** budget, ventana horaria y kill switch POR tenant
   (hereda defaults de plataforma); el ciclo de un tenant jamas lee otro.

Gate/DoD: contamination suite completa 0 fugas en las 4 dimensiones (filas, memoria,
objetos, injection); identidad no reescribible; llave graduada operando con audit;
corre en cada deploy junto al canario.

### E3-5 -- Routing por tenant + BYO keys + presets builder (talla M)

1. **BYO keys por tenant:** el owner registra keys propias (cifradas con SU data key de
   E3-3); modos "estricto" (solo keys propias) e "hibrido opt-in" (fallback a keys de
   plataforma con recargo del plan) -- roadmap F5. El catalogo de modelos por capacidad
   (E2-4) se vuelve scoped por tenant: cada tenant ve/administra su catalogo.
2. **Ledger por tenant:** costo agregado por tenant ademas de por usuario; visible al
   owner del tenant y a platform_admin (agregado, sin contenido).
3. **Presets builder UI** (menor heredado de E2-4, SPEC_FB_ROUTING_PRESETS_v1): builder +
   templates sobre el ledger real que ya existe; la validacion de preset_id ya esta.
4. **Defaults por plan:** cada tier trae presets y budgets default; el seed de E3-2 los
   aplica.

Gate/DoD: tenant demo opera 100% con su propia key (0 requests con keys MWT, verificado
en ledger); preset creado desde el builder y usado en una cadena auto real.

### E3-6 -- Primer tenant externo + billing manual (talla L)

1. **Seleccion del design partner (criterios decididos, no pendientes):** candidato
   default = un distribuidor/cliente B2B con relacion comercial viva con MWT (universo:
   ENT_FB_VERTICAL_CANDIDATES_v2 y cartera MWT). Criterios de elegibilidad: opera correo +
   cotizacion + facturacion electronica; <10 usuarios; acepta plan BETA gratis 90 dias con
   feedback quincenal; firma acuerdo de datos (piso: sus datos jamas entrenan ni cruzan a
   otro tenant -- ya es verdad por E3-3, se pone por escrito). El CEO elige A o B entre
   los que pasen el filtro -- eso es gestion comercial, no una decision de diseno abierta.
2. **Playbook de onboarding** (se escribe como PLB_FB_TENANT_ONBOARDING_v1): aprobar
   tenant, bootstrap, conectar cuentas de correo del tenant (app-passwords propias, mismo
   patron H2 de E2), carga inicial de SU KB con el cargador existente, habilitar packs de
   skills segun su operacion, capacitacion de 1 sesion.
3. **Billing manual con dogfooding (decision Sec.6 #6):** plan BETA gratis 90 dias ->
   primera factura emitida usando los PROPIOS skills del PACK 1 (fiscalidad electronica)
   sobre el tenant MWT. Sin pasarela de pago: transferencia + conciliacion con
   SKILL_CO_PAYMENT_MATCH_FE (PACK 3). El sistema factura su primera venta con sus
   propias manos: ese es el gate de que los skills sirven.
4. **Telemetria y soporte:** dashboard de salud por tenant para platform_admin (uptime,
   errores, costo, casos/semana -- agregados); canal de soporte (correo) y ventana de
   mantenimiento documentada; SLA honesto de beta: mejor esfuerzo, backup diario,
   RPO 24h.

Gate de cierre de ETAPA 3: tenant externo activo >=30 dias con >=10 casos reales
completados, 0 fugas (suite E3-3 verde todo el periodo), primera factura emitida y
pagada. Con eso la validacion de mercado (gate de salida, Sec.0) queda cumplida.

## 4. E3-4 -- Fabrica de skills (banda paralela, por olas)

Fuente unica: ENT_FB_SKILL_CATALOG_v1 (62 skills / 13 packs). Principios no negociables
del catalogo aplican a cada skill: dato exacto = lookup con cita y fecha (nunca memoria
del modelo); toda accion con efecto externo = HITL; autonomia se gana por track record
(ceilings). Cada skill se emite como manifest SCH_FB_SKILL_MANIFEST_v2 y entra
SHADOW -> ACTIVE con gate del curador + >=3 golden cases verdes.

### Ola 0 -- Fundacion (sin esto los skills son wrappers)

1. **Taxonomia v2 (decision arquitecto: P15-P18 SE ADOPTAN):** escribir
   ENT_FB_UNIT_OF_WORK_TAXONOMY_v2 incorporando P15 verificar_vigencia_normativa,
   P16 rastrear_externo, P17 corregir_en_cascada_temporal, P18 capturar_interaccion_informal;
   los descartados y los resueltos-via-P14+HITL quedan registrados como en el catalogo.
   (El catalogo lo marcaba "Decision CEO pendiente"; el agregador ya demostro que la v1
   no es exhaustiva -- se resuelve aqui, con changelog.)
2. **Skill compiler v2:** el compilador de rutinas existente (Routine Hub) se extiende
   para validar manifest v2 completo (archetype, tools_mcp, outcome metric, kill switch,
   learning target), registrar `skill_version` por run (ya activo desde E2) y rechazar
   manifests invalidos fail-closed. Alias de namespace `mwt -> fbl` segun la deuda
   documentada en SCH_FB_SKILL_MANIFEST_v2.
3. **C0-1 captura informal (P18):** pipeline WhatsApp/texto pegado/nota de llamada ->
   compromiso trazable (quien, que, cuando, evidencia = transcripcion + timestamp) ->
   item HITL para confirmar -> conocimiento citable. Es el prerequisito que desbloquea
   PACK 6 y SKILL_CO_PROMESA_PAGO (convergencia B del swarm).
4. **C0-2 recopilacion viva (P16):** consulta a fuente externa web SIN API (portal
   tributario, tracking, TICA) con evidence bundle obligatorio: URL + fecha/hora +
   captura + valor extraido. Fail-closed si la fuente no responde: el skill reporta
   "fuente no disponible", jamas rellena de memoria.
5. **C0-5 ceilings mecanica:** contador de track record por skill/usuario (aciertos
   confirmados en HITL) que gradua el techo de autonomia (mas track record = drafts mas
   completos, nunca = saltarse HITL en efectos externos).
6. **C0-7 evidence bundle generalizado:** el patron del quote bundle se extrae a un
   componente que cualquier skill adjunta a su output.

DoD ola 0: taxonomia v2 indexada; compiler validando; C0-1 y C0-2 con test + canary de
injection (contenido externo capturado no dispara acciones).

### Olas 1-5 (orden = prioridad swarm del catalogo, Sec.5 del mismo)

| Ola | Pack(s) | Skills | Golden cases (operacion MWT real) | Depende de |
|---|---|---|---|---|
| 1 | PACK 1 fiscalidad electronica | 8 | facturas propias MWT | ola 0 (C0-2) |
| 2 | PACK 3 cobranza | 6 | cartera MWT | ola 1 (estados FE) + C0-1 para PROMESA_PAGO |
| 3 | PACK 2 comex corredor BR->CR | 10 | importaciones Marluvas | KB real H3 cargada (E3-0 t.5) |
| 4 | PACKs 4 planilla, 5 tributario, 6 whatsapp, 7 bodega | 17 | planilla MWT; tramites reales | ola 0 (C0-1 para PACK 6) |
| 5 | PACKs 8-13 (TEMPLATE, volumen mecanico) | 21+ | EEFF Del Risco (PACK 10); resto por pack | ninguna dura; localizar NIIF / derecho civil LATAM / Codigo de Trabajo |

**Primera tarea de la ola 1 (timebox 3 dias, dev):** verificar existencia y acceso de las
APIs oficiales de validacion FE -- Hacienda ATV (CR), SAT (MX), DIAN (CO) -- el
[PENDIENTE-VERIFICAR] del catalogo. Ambos resultados estan disenados: con API -> conector
directo; sin API -> C0-2 (web + evidence bundle). El resultado se registra en
ENT_FB_SKILL_CATALOG v1.1. No es bloqueante ni decision abierta: es una verificacion con
dos caminos ya resueltos. Corredor v1 de comex: BR->CR (como fija el catalogo); los otros
corredores (BR->MX, BR->CO, CR->CA) entran al terminar BR->CR, USMCA segunda ola.

**Los 15 items regulatorios [PENDIENTE-VERIFICAR]** de faberloom_B_convergencia Sec.4 se
verifican por lote DENTRO de la ola que los usa (cada skill que cite una norma ejecuta
P15 sobre ella como parte de su golden case). Nada se da por vigente sin verificacion.

Reglas de la fabrica:
- Un skill TEMPLATE se "roba" estructura del catalogo Claude y se LOCALIZA (NIIF no
  US-GAAP, derecho civil no common law, es-LATAM); jamas se traduce a ciegas.
- Los 14 skills existentes + 10 sub-agentes NO se re-escriben; migran a manifest v2
  lazy (al tocarse), empezando por los que las olas reutilizan.
- Cada ola cierra con: skills en ACTIVE en el workspace MWT correspondiente, golden
  cases verdes con evidencia, catalogo actualizado (estado GAP/TEMPLATE -> EXISTE),
  1 parrafo de lessons por pack.
- Un skill cuyo golden case detecte un dato inventado (output sin cita verificable) NO
  pasa a ACTIVE. Sin excepciones.

Gate E3-4 (para efectos del cierre de etapa): olas 0-2 completas (PACK 1 + PACK 3
ACTIVE en dogfood MWT). Las olas 3-5 continuan en paralelo y no bloquean E3-6; su fin
natural es el cierre de etapa o su traspaso al backlog de Etapa 4 con estado explicito.

## 5. Riesgos P0 + kill criteria

- **Fuga cross-tenant (datos, memoria, objetos o injection)** -> parar onboarding externo
  y todo E3-6; auditoria completa antes de reanudar. Con tenant externo dentro: notificar
  al tenant afectado (honestidad contractual del acuerdo de datos).
- **Corte Postgres fallido** -> rollback al flag sqlite (BD intacta). 2 cortes fallidos ->
  re-diseno del adapter antes del tercer intento.
- **Identidad del agente reescrita en sesion** -> kill del hito E3-3; canal de fuga
  numero 1 segun ARCH_FB_AGENT_RUNTIME_EVAL; no se avanza con mitigacion parcial.
- **Skill que ejecuta efecto externo sin HITL** -> skill a SHADOW inmediato + revision del
  compiler (el gate es del plano de gobierno, no del skill; si un skill lo salto, el
  agujero es del gate).
- **Dato inventado en output de skill** -> no-ACTIVE (regla de fabrica); si se detecta en
  ACTIVE, rollback de version y golden case nuevo que lo cace.
- **platform_admin viendo contenido de tenant** -> P0 de diseno; el rol se construye sin
  esa capacidad, y el audit lo probaria: cualquier acceso de contenido con credencial de
  plataforma = incidente.
- **Cadena auto multi-tenant sin techo** -> los budgets por tenant (E3-2 t.4) son gate,
  no opcionales (misma leccion E2-4).
- **Kill de etapa (honesto):** si tras cerrar E3-5 no hay tenant externo dispuesto
  despues de 8 semanas de gestion comercial activa, Etapa 3 se cierra en estado
  "multi-tenant listo, sin SaaS abierto": los skills y el multi-tenant siguen dando valor
  a MWT (dogfood), y abrir SaaS queda como decision comercial futura sin deuda tecnica.
  No es fracaso: es el techo honesto que el gate de salida hace explicito.

## 6. Decisiones tomadas (arquitecto, 2026-07-07 -- mandato "sin faltantes ni decisiones abiertas")

1. **Pausa de Etapa 3 levantada; gate comercial pasa de entrada a salida.** El mandato
   CEO de disenar y ejecutar E3 (esta sesion, sobre el cierre E2) la levanta; la
   validacion de mercado se exige para CERRAR la etapa (E3-6), no para arrancarla.
   Clausula honesta: kill de etapa en Sec.5 si el mercado no responde.
2. **Postgres switch es E3-1, antes de tenants.** Sin RLS en runtime no se crea el
   segundo tenant real. Orden inegociable.
3. **P15-P18 adoptados** en ENT_FB_UNIT_OF_WORK_TAXONOMY_v2 (ola 0). El "pendiente
   decision CEO" del catalogo se resuelve: la evidencia del agregador (taxonomia v1 no
   exhaustiva) es suficiente y el costo de adoptar es un documento, no un build.
4. **Whisper: SI** (faster-whisper local, modelo small) en E3-0. Cierra el unico tipo de
   ingesta fail-closed y respeta require_local_only por naturaleza.
5. **Signup con aprobacion de platform_admin** (no signup abierto) en Etapa 3. Elimina
   anti-abuso complejo del alcance; signup abierto = Etapa 4.
6. **Billing manual, sin pasarela:** BETA 90 dias gratis -> factura electronica emitida
   con los propios skills PACK 1 + conciliacion PACK 3. Pasarela de pagos = Etapa 4.
7. **Cross-tenant learning PROHIBIDO en Etapa 3** por codigo (no por config). El k-anon
   L3 opera solo dentro de cada tenant. Repensar cross-tenant es una decision de
   producto de Etapa 4+ con su propio analisis legal.
8. **Design partner por criterios** (Sec.3 E3-6 t.1): el CEO escoge entre candidatos que
   pasen el filtro; el filtro esta decidido aqui. Nada del diseno depende de cual sea.
9. **KB real H3 sigue diferida** (decision CEO 2026-07-07 se respeta) pero con deadline
   estructural: antes de la ola 3 de skills. La tarea de conseguir los archivos es del
   CEO y esta agendada, no abierta.
10. **Naming:** plan de Etapa 3 = FABERLOOM (producto), no SPACELOOM (superficie).
    Cadena documental intacta via `relacionado`.
11. **MCP server, agent builder 168, segundo vertical, pasarela, mobile: Etapa 4.**
    Profundidad antes que amplitud (regla G del roadmap).
12. **Dedicacion:** 1 dev full-time (Alejandro) + horas de AM/curador para golden cases
    y gates humanos. Regla de banda paralela: ~2 dias/semana a la fabrica de skills
    (E3-4) desde el arranque, el resto a la cadena E3-0 -> E3-6. Los skills son contenido
    sobre la instancia viva: no compiten con los cortes de infra.

## 7. Calendario (dos vias, leccion E1/E2: el corto es compromiso, el largo es techo honesto)

Tallas: E3-0 M (~1.5s, con esperas operativas en paralelo), E3-1 L (~3s), E3-2 L (~2.5s),
E3-3 L (~2.5s), E3-5 M (~1.5s), E3-6 L (~2s + 30 dias de convivencia). Fabrica E3-4:
ola 0 ~2s, ola 1 ~2s, ola 2 ~1.5s, ola 3 ~2s, olas 4-5 ~4s -- en banda paralela (regla
Sec.6 #12), por lo que alargan el calendario ~35% en vez de sumarse linealmente.

- **Via corta (compromiso): multi-tenant interno listo** (E3-0 -> E3-3 + olas 0-1):
  ~10-12 semanas.
- **Via larga (techo honesto): Etapa 3 completa** (todo lo anterior + E3-5 + E3-6 con sus
  30 dias de tenant externo + olas 2-3): ~20-24 semanas. Olas 4-5 continuan hasta el
  cierre y lo que no alcance pasa a backlog E4 con estado explicito (nunca gap silencioso).

Arranque: al commitear E3-0 tarea 1 (seguridad).

## 8. Herencia de Etapa 2 -- CERRADA POR DECISION (nada queda como gap)

Fuente: cierre_etapa2_faberloom.md Sec.8-9. Misma regla que la Sec.8 del plan E2: si un
item resulta mal decidido se re-decide con changelog, pero nunca vuelve a "pendiente".

| # | Item heredado de E2 | DECISION | Aterriza en |
|---|---|---|---|
| HE2-1 | Switch runtime Postgres+RLS (staging validado, runtime SQLite) | Hito dedicado, primero de la cadena tecnica | E3-1 |
| HE2-2 | Gate H1 correo end-to-end + credenciales trade@/mw_doc@ | Tarea 2 de E3-0, humana, con criterio de audit | E3-0 |
| HE2-3 | KB real (H3, diferida por CEO) | Condicionada con deadline duro pre-ola 3 | E3-0 t.5 |
| HE2-4 | Encendido modo auto (gate E2-4) | Tarea 3 de E3-0, 7 dias observacion | E3-0 |
| HE2-5 | Dark-launch ciclo ambiental (gate E2-5) | Tarea 4 de E3-0, 14 dias, no bloquea E3-1 | E3-0 |
| HE2-6 | Presets builder UI (menor E2-4) | Se cobra con el routing por tenant | E3-5 t.3 |
| HE2-7 | Whisper para audio/video (menor E2-6) | SI, faster-whisper local | E3-0 t.6 |
| HE2-8 | Seguridad: rotar root VPS, SSH a llaves, claves de correo | PRIMERA tarea de la etapa | E3-0 t.1 |
| HE2-9 | Certificados de firma comerciales (H5 E1; el cierre E2 no evidencia la compra prevista "al arrancar E2-6") | Verificar si se compraron; si no, compra al arrancar E3-6 (primer uso externo real). Build interno no los necesita | E3-6 |
| HE2-10 | Declarar Etapa 2 TERMINADA | Acta al completar E3-0 t.1-4 | E3-0 t.7 |

---

Changelog:
- v1.0 (2026-07-07): Creacion. Plan de build Etapa 3 (multi-tenant + fabrica de skills)
  sobre cierre_etapa2_faberloom.md v1.0. Define 5 pilares (Postgres+RLS runtime, tenant
  lifecycle, sello criptografico por tenant, fabrica de skills del catalogo
  ENT_FB_SKILL_CATALOG_v1 en 6 olas, routing por tenant/BYO keys), secuencia E3-0 -> E3-6
  con tareas por hito, riesgos P0 + kill criteria (incl. kill honesto de etapa),
  12 decisiones de arquitecto (pausa levantada con gate comercial a la salida, P15-P18
  adoptados, whisper si, signup con aprobacion, billing manual dogfooding PACK 1/3,
  cross-tenant learning prohibido por codigo, MCP/builder/pasarela a Etapa 4), calendario
  dos vias (10-12s / 20-24s), herencia E2 cerrada por decision (HE2-1..10). DRAFT en
  generated_staging, pendiente promocion + indexacion en IDX_FB_FOUNDATION_BETA +
  MANIFIESTO. ASCII puro. No toca FROZEN ni control_surface.
