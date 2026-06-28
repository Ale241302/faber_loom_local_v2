# Consulta a Fugu: gaps de Etapa 1 / SL1a router

Contexto: estoy construyendo SpaceLoom Etapa 1 single-user local-first. Ya cerré SL0, SL1b parcial, SL2a/b/c KB, SL3a skills/agents/toolset, SL3.5 workspace isolation y SL4 empaque desktop (build .exe funciona; tests 154 passed). Pero siento que el SL1a router mínimo no es visible para el usuario: en el chat no se ve qué modelo/proveedor se usó, ni hay una UI clara de fallback, costo por mensaje ni presupuesto restante.

Preguntas:
1. Según PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md y SPEC_SPACELOOM_ETAPA1_v1.md, ¿qué de SL1a (router mínimo) aún falta o está mal implementado en el código actual?
2. ¿Hay alguna regla de SPEC_FB_ROUTING_PRESETS_v1.md o SCH_FB_SKILL_MANIFEST_v2.md que deba respetarse ya en Foundation Beta E1 aunque sea versión reducida?
3. ¿Qué mejora concreta debería aplicar AHORA para que SL1a se sienta "real" (visible modelo usado, costo, fallback, budget cap, Ollama opcional) sin over-engineering?
4. ¿Detectas algún riesgo P0 o must-fix antes de seguir a Fase 4?

Por favor responde en modo auditor: qué falta, qué está mal, qué mejora aplicar, y ordena por prioridad. No escribas código; solo diagnóstico y recomendación.

---

## Documentos de referencia

### PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md

# PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1 -- Plan de Build SpaceLoom Etapa 1 (single-user)
id: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-06-25 -- plan de build SL0-SL4 sobre SPEC_SPACELOOM_ETAPA1
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: SPEC_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_SELFHOSTED_v1.1.md - SPEC_SPACELOOM_SELFHOSTED_v1.2.md - SPEC_SPACELOOM_SELFHOSTED_v1.3.md - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md - SPEC_FB_E0_5_VALIDATION_SLICE_v1.md

---

## 0. Que es este plan (y que NO)

Plan de BUILD que secuencia SPEC_SPACELOOM_ETAPA1_v1 (que define QUE; este plan
define COMO/CUANDO). Etapa 1 = app de escritorio single-user, local-first, "telar
completo": SpaceLoom (canvas) + Routine Hub (skills) + router multi-proveedor +
workspaces + KB + HITL, instalable sin terminal. NO incluye multi-tenant, nube ni
RLS (eso es Etapa 2-3, hoy pausado). Lo que el CEO pidio -- "SpaceLoom + skills +
router" -- es el nucleo SL0 -> SL1 -> SL3a de esta secuencia.

## 1. Principios de construccion

1. **Dogfooded desde SL1.** Alvaro usa el producto desde el primer sub-hito con draft
   real; no se valida con metricas cronometradas sino por ADOPCION (ver
   SPEC_FB_E0_5_VALIDATION_SLICE_v1 v1.2): si lo sigue usando, sirve.
2. **Expansion-ready, no expansion-built.** Costuras limpias para que Etapa 2-3 se
   AGREGUE encima, sin reescribir. No construir el futuro; solo no bloquearlo.
3. **Una entidad, no fabrica de agentes.** Un orquestador persistente; los "agentes"
   son perfiles de config (persona) dentro de una Rutina. Sin runtimes paralelos, sin
   n8n como orquestador.
4. **HITL absoluto + irreversibles fuera de la entidad.** La entidad propone y ejecuta
   lo reversible; enviar/borrar (NEVER) y disparadores que deben correr aunque la
   entidad falle viven en una capa de gobierno fina (scheduler local + HITL).
5. **Cero dato inventado.** Todo precio/dato del draft trazado a fuente de la KB del
   espacio activo.

## 2. Secuencia de build SL0 -> SL4

| Hito | Objetivo | Entregable | Can-start-when | Gate / DoD | Talla |
|---|---|---|---|---|---|
| SL0 | Esqueleto + seed | app vacia corre; 1 workspace de prueba; datos semilla; modelo de datos base | carve-out ratificado (Sec.5) | la app abre y persiste estado local | S |
| SL1 | Router + SpaceLoom + draft real | routing multi-proveedor + presets + fallback + cost ledger (BYO-key); canvas chat draft-first contra contexto del espacio; primer draft real | SL0 | Alvaro genera un draft real y EMPIEZA a usarlo (dogfooding) | L |
| SL2a/b/c | Workspaces + KB | workspaces por cliente con herencia; subir KB (MD/TXT/PDF/Excel, FTS5); el agente cita con fuente | SL1 | un draft cita dato real de la KB, 0 inventado | L |
| SL3a | Skills / Routine Hub | SKILL.md + schema + sandbox; autoria liviana (entidad redacta skill -> HITL aprueba -> guarda); invocable @nombre; biblioteca/invocacion/historial | SL2 | crear y correr una skill por @nombre end-to-end | L |
| SL3b/c | HITL + gold loop | WorkLoom (cola por estado/urgencia: aprobar/editar/rechazar + captura del porque); evidence; gold loop | SL3a | el edit_pct de un mismo tipo de tarea baja con el uso | M |
| SL3.5 | Sellado + llave graduada | indice-vs-contenido; sellado por workspace; lo de un cliente no se cuela en otro | SL3 | test de fuga cross-workspace = 0 | M |
| SL5 | Correo | connector multi-cuenta, read-first, envio HITL | SL3.5 (recortable) | recibe correo -> draft -> envio solo tras aprobacion | M |
| SL4 | Empaque desktop | app firmada Win/Mac (pywebview + PyInstaller + auto-update); doble-clic, sin terminal | SL5 (o SL3.5 si SL5 se difiere) | instala un no-tecnico sin ayuda; Etapa 1 DONE | M |

Nota: SL5 (correo) es lo unico recortable sin romper el nucleo (se pega/lee a mano).
Estimacion KB: ~11.5-12 semanas, 1 dev full-time; usable desde SL1.

## 3. Costuras contract-first (lo que debe quedar limpio para Etapa 2-3)

Construir con estas costuras para que lo grande se SUME, no que obligue a reescribir:
- **SKILL.md portable**: la skill no depende de single-user; sirve igual en multi-tenant.
- **Sellado por espacio**: hoy local; manana se sube a cripto/RLS detras de la MISMA
  costura. Aditivo (no clavar supuestos single-user en el modelo de acceso).
- **Modelo de datos limpio**: SQLite hoy -> Postgres+RLS despues; no clavar supuestos
  que fuercen rewrite. Tenant_id "latente" donde corresponda sin activarlo aun.
- **Una entidad -> una entidad por tenant**: mismo patron, escalado.
- **BYO-key -> keys gestionadas**: el router abstrae el proveedor; cambiar el origen
  de la key es una capa que se suma.
- **Esquema Routine (supersede split agent/skill)**:
  `routine(id, workspace_id, name, skill_md, tools_allowlist, schema_output_json, preset_id, trigger_json, persona_md, is_active, created_at)`
  `routine_run(id, routine_id, workspace_id, input_json, output_json, evidence_json, status, edit_pct, created_at)`

## 4. Riesgos P0 + kill criteria

P0 (de la Definition of Done del spec):
- **Envio sin HITL** -> kill del hito. Cero accion irreversible sin doble confirmacion.
- **Injection por contenido de email** (un correo que dispara una accion) -> test
  obligatorio en SL5; falla = no liberar correo.
- **Fuga cross-workspace** (lo de un cliente en otro) -> test en SL3.5; falla = no
  avanzar a SL5/SL4.
- **Dato inventado en draft** (precio/stock sin fuente) -> el draft debe trazar a KB;
  sin fuente, no se aprueba.
Kill de Etapa: si SL1-SL3 no alcanzan adopcion real (Alvaro deja de usarlo), se
diagnostica (concepto vs artefacto) antes de empacar SL4.

## 5. Dependencias que bloquean SL0 (arranque)

1. **Ratificar DEC_FB_SPACELOOM_FREEZE_SCOPE** (carve-out para construir SL0
   single-user). Sin esto, sigue en planeacion -- es la tarea 1 real.
2. **Licencia final** (FSL recomendada) -- [PENDIENTE legal].
3. **Rotar credenciales IMAP de Kimi Work** (urgente, independiente; bloquea SL5).
4. **Presupuestar firma de codigo** (Apple Developer USD 99/ano + cert Windows) --
   necesaria para SL4.

## 6. Pendientes CEO

1. [PENDIENTE] Ratificar el carve-out del freeze (Sec.5 #1) para destrabar SL0.
2. [PENDIENTE] Confirmar licencia FSL y arranque de marca registrada.
3. [PENDIENTE] Confirmar dedicacion: 1 dev full-time ~12 semanas (quien: Alejandro?).
4. [PENDIENTE] Confirmar si SL5 (correo) entra en Etapa 1 o se difiere (pegar a mano).

---

Changelog:
- v1.0 (2026-06-25): Creacion. Plan de build SL0-SL4 sobre SPEC_SPACELOOM_ETAPA1_v1.
  Secuencia con entregable/can-start-when/gate por hito; costuras contract-first para
  Etapa 2-3; riesgos P0 + kill; dependencias que bloquean SL0. Dogfooding desde SL1,
  validacion por adopcion (no metricas). DRAFT condicionado a ratificacion del carve-out.

---

# 7. ENMIENDA v1.1 (2026-06-25) -- Ajustes del review cruzado Fugu + Kimi

Ambos motores: MATIZADO (Fugu ROLE-B: desacuerdo en liberar sin endurecer DoD de
seguridad). Convergen. Fuente: EVAL_PLAN_SPACELOOM_KIMI.md + EVAL_PLAN_SPACELOOM_FUGU_ULTRA.md.

## 7.1 SL1 no genera adopcion como estaba -> split
SL1 generaba draft pero sin envio (Kimi) y con seed artificial, no KB real (Fugu) = demo,
no habito. Split:
- **SL1a**: router minimo + chat.
- **SL1b**: primer draft contra mini-KB REAL de MWT + HITL minimo (aprobar/editar +
  export o envio). La adopcion arranca en SL1b.

## 7.2 Sellado adelantado a SL2a
Test minimo "workspace A no lee contenido B" ANTES de cargar datos de clientes distintos.
La llave graduada completa queda en SL3.5.

## 7.3 Router minimo (cortar over-build)
SL1a = 1 proveedor cloud + Ollama opcional + fallback + costo visible + budget cap +
provider allowlist. SIN preset builder / auto-optimizador / backtest / fabrica de niveles
hasta tener ledger real. (SPEC_FB_ROUTING_PRESETS completo = etapa posterior.)

## 7.4 SL2 es el core dificil (hito mas fragil)
Priorizar CSV/XLSX (precios) sobre PDF. La KB debe extraer, citar y verificar dato duro
confiable. Si SL2 falla: SL1 no se vuelve habito, gold aprende basura, SL3.5 no protege
nada y SL5 acelera errores.

## 7.5 DoD de seguridad/datos endurecida (P0 no cubiertos)
- source_to_field_check: cada precio/SKU/stock/margen/lead time/equivalencia -> fuente
  vigente y autorizada.
- stale_data_block: fuente vencida o sin fecha/version -> el draft PIDE confirmacion, no afirma.
- Injection canaries: email + PDF/HTML + Excel/CSV + KB text + SKILL.md (no solo email).
- Cifrado local (SQLCipher/passphrase) obligatorio para workspaces confidenciales.
- Auto-update firmado y verificado + rollback; sin firma valida no se instala.
- Backup/export/restore smoke test antes de usar datos reales.
- Gold de campos duros solo con verificacion independiente / segundo gate (anti-contaminacion).

## 7.6 Costuras contract-first: de intencion a contrato
- Campos latentes desde SL0: tenant_id, user_id/actor_id, actor_role_at_decision,
  routine_version, skill_version, schema_version, source_version, approved_by.
- Capa Context(workspace_id, tenant_id?, user_id?) usada por TODA query (constantes en v1).
- Interfaz AuditWriter (hoy audit.jsonl; manana outbox/tabla).
- Routine compiler que emita un SUBCONJUNTO de SCH_FB_SKILL_MANIFEST_v2, no formato paralelo.

## 7.7 Estimacion en dos calendarios
- **Dogfood interno usable**: ~8-10 semanas (SL5 diferido, SL4 instalador simple, 1 OS,
  router minimo).
- **Etapa 1 distribuible real**: ~14-18 semanas (ingestion robusta, seguridad, firma/
  notarizacion, update, QA Win/Mac). Las 12 semanas solo valen como dogfood recortado.

## 7.8 SL3c reframe
SL3c = capturar edit_pct + gold candidates. Demostrar que edit_pct baja = criterio de
salida extendido, no una semana fija.

## 7.9 Adopcion: definicion operativa minima (no cronometro)
Coherente con SPEC_FB_E0_5 v1.2 (adopcion, no metricas): uso VOLUNTARIO en >=N casos
reales durante ~2 semanas; si lo dejas de agarrar, no paso. [PENDIENTE -- fijar N y "que
friccion mata".]

## 7.10 Blind spot a investigar (ambos)
No esta probado que este flujo le gane a la solucion tonta: Claude Projects + Obsidian/
Excel + templates de Gmail. Eso es parte del gate de adopcion, no un supuesto.

---

# 8. Decisiones CEO pendientes (del review)
1. [PENDIENTE] Confirmar descope: construir "dogfood interno recortado" primero
   (recomendado por ambos motores), no Etapa 1 completa de una.
2. [PENDIENTE] Cual calendario se compromete: 8-10 dogfood vs 14-18 distribuible.
3. [PENDIENTE] N de casos y criterio de adopcion (Sec.7.9).
4. [PENDIENTE] Cifrado local: obligatorio siempre o solo workspaces confidenciales.

Changelog (cont.):
- v1.1 (2026-06-25): Enmienda por review cruzado Fugu+Kimi (ambos MATIZADO). Split SL1a/b,
  sellado en SL2a, router minimo, SL2 como core, DoD de seguridad/datos endurecida,
  costuras contract-first concretas, dos calendarios, SL3c reframe, definicion de adopcion.
  Recomendacion: dogfood interno recortado primero. Sigue DRAFT + carve-out pendiente.

---

### SPEC_SPACELOOM_ETAPA1_v1.md

---
id: SPEC_SPACELOOM_ETAPA1_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-06-17 - definicion de Etapa 1 = app standalone con toda la funcionalidad
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
extiende: SPEC_SPACELOOM_SELFHOSTED_v1.1/v1.2/v1.3 + IMAP_CONNECTOR_v1
relacionado_con: DEC_FB_SPACELOOM_FREEZE_SCOPE_v1
---

# SPEC_SPACELOOM_ETAPA1_v1
## Definicion de Etapa 1: app standalone con toda la funcionalidad

## 1. Que es Etapa 1

Una **app de escritorio (Win/Mac) que un profesional instala y usa para su flujo de trabajo completo.**
No es un MVP delgado: es el **telar completo, single-user, local-first**. Es la primera etapa de un
roadmap mayor (Etapa 2 = multi-usuario interno; Etapa 3 = multi-tenant/SaaS, hoy pausado).

"Toda la funcionalidad" = todo el telar single-user. NO incluye multi-tenant ni nube (eso es Etapa 2-3).
La entrega es el app completo, pero se construye y se dogfoodea por sub-etapas (no big-bang).

## 1.1 Principio rector

**La entidad es UNA, pero resuelve cada tarea con el contexto del espacio de trabajo activo, y solo ese.**
Dentro de un workspace, el agente usa todo lo de ese espacio: su conocimiento/KB, sus skills, sus golden
samples (lo aprobado ahi = como lo quiere el usuario), sus rutinas y sus crons. El espacio es a la vez su
memoria y su caja de herramientas para ese cliente/tema. Lo extra que puede usar es lo que HEREDA del
espacio padre (hacia abajo), nunca de un espacio hermano. **Sabe-donde (global) vs resuelve (local):** el agente tiene vision GLOBAL de QUE existe y DONDE (indice de
existencia) para navegar, rutear y gestionar -- puede llevar un pedido al espacio correcto o decir "esto es
de Sondel". Pero RESOLVER (construir la respuesta/accion) ocurre solo con el contexto del espacio activo,
sellado. Tener el indice de toda la casa no es poder leer el contenido de cada cuarto.

De aqui salen las dos propiedades centrales:
- **Eficacia:** opera con el contexto exacto, no generico.
- **Seguridad:** sellado por espacio; lo de un cliente no se mezcla con otro (ver llave graduada, v1.2).

## 2. Resultado (que puede hacer el usuario al cerrar Etapa 1)

1. Instalar con doble clic (Win o Mac), sin terminal; poner su API key (guardada en keyring).
2. Conectar 1 o varias cuentas de correo (read-first, OAuth/IMAP).
3. Crear workspaces por cliente/area, con herencia (un workspace hereda del padre).
4. Subir su conocimiento (catalogo, lista de precios, PDF, Excel, MD) y que el agente lo cite.
5. Recibir/pegar un pedido (RFQ, cobranza, consulta) y generar un **draft aprobable** con precios y datos **trazados a la fuente** (0 inventados).
6. Aprobar / editar / rechazar (HITL); **enviar solo tras aprobacion** (doble confirmacion).
7. Cada aprobacion mejora la siguiente (gold loop: el edit baja con el uso).
8. Agentes con identidad propia y persistente; skills en formato SKILL.md.
9. Memoria sellada por workspace + llave graduada (el correo de un cliente no se cuela en otro).

## 3. Alcance funcional (el telar completo)

**Nomenclatura:** el producto/app = **FaberLoom**. Sus superficies = **Inbox** (entrada), **WorkLoom** (mesa de trabajo / cola de aprobacion), **SpaceLoom** (canvas de iteracion), sobre **workspaces** + **Routine Hub** + **KB**. SpaceLoom es un elemento, no el producto.

| Pieza | Detalle en | Sub-etapa |
|---|---|---|
| Routing multi-proveedor + presets + fallback + cost ledger (BYO-key) | v1.1 | SL1 |
| **Inbox** (entrada: correo/pedidos -> clasificar -> rutear a workspace; acciones rapidas) | IMAP_CONNECTOR_v1 | SL2/SL5 |
| **SpaceLoom** (canvas de iteracion, chat draft-first contra el contexto del espacio) | v1.1 | SL1 |
| **WorkLoom (mesa de trabajo)** (cola de drafts por estado/urgencia: aprobar/editar/rechazar + captura del porque; aqui vive la revision por muestra/excepciones = autonomia ganada) | v1.1 (HITL) | SL3b |
| Workspaces + herencia | v1.1/v1.2 | SL2a |
| KB grounding (MD/TXT, PDF, Excel; FTS5) | v1.1 | SL2a/b/c |
| 1 entidad persistente (orquestador unico) + perfiles de agente como CONFIG (no runtimes paralelos) | v1.2 | SL3 |
| Skills (SKILL.md + schema + sandbox) + autoria liviana (la entidad redacta el skill -> HITL aprueba -> se guarda) | v1.2 | SL3a |
| HITL + evidence + gold loop | v1.1/v1.2 | SL3b/c |
| Indice-vs-contenido + llave graduada (sellado por workspace) | v1.2 | SL3.5 |
| Connector de correo (multi-cuenta, read-first, envio HITL) | IMAP_CONNECTOR_v1 | SL5 |
| App desktop firmada Win/Mac (pywebview + PyInstaller + auto-update) | v1.3 | SL4 (empaque) |

## 4. Fuera de Etapa 1 (para que "toda" no se desborde)

Multi-usuario, multi-tenant/RLS, cloud sync, marketplace de skills, code-exec/HTTP en skills, embeddings semanticos a gran escala, observabilidad self-hosted, billing, **"agent factory" como subsistema, multiples agentes-runtime paralelos, n8n como orquestador**. -> Etapa 2-3 o innecesario.

### 4.1 Decision: una entidad, no una fabrica de agentes

Con el modelo tipo OpenClaw, Etapa 1 corre con **UNA entidad persistente** (orquestador), no varios agentes-runtime. Implicaciones:
- **Agentes = perfiles de config** (system_prompt + identidad + modelo) que la entidad adopta segun tarea/workspace. No son procesos; guardarlos es trivial, no un subsistema. -> "agent factory" eliminada.
- **Skill authoring se queda, pero liviano:** la entidad redacta un SKILL.md, vos aprobas (HITL/curador), se guarda. Es como crece el telar; no es una "fabrica" pesada.
- **Crons/procesos:** la entidad orquesta lo seguro (poll de correo, drafts proactivos, invocar procesos deterministas). Pero las **acciones irreversibles (enviar/borrar = NEVER) y los disparadores que deben correr aunque la entidad falle viven en una capa de gobierno FINA, fuera de la entidad** (en single-user: scheduler local minimo + HITL, no n8n). La entidad propone y ejecuta lo reversible; no dispone de lo irreversible.

### 4.2 El Routine Hub (reemplaza a la "agent factory")

Lo que se define en vez de una fabrica es **donde viven, se ven, se editan y se llaman las ejecuciones**: el **Routine Hub** del workspace.

**Unidad = Rutina** (el kit completo de como se ejecuta una tarea):
- nombre (interno, invocable con `@nombre`)
- SKILL.md (instruccion + tools allowlist + schema de salida)
- binding (preset/modelo a usar)
- trigger (manual / cron / al-llegar-correo)
- persona opcional (identity_md, tono/voz)

Una rutina con nombre y persona ES lo que el usuario llama "agente". No hay `agent` aparte: la persona
es un campo de la rutina (el `agent` de v1.2 se pliega aca -> un subsistema menos).

**Tres caras, dentro del workspace (heredables del padre):**
1. **Biblioteca:** lista de rutinas; ver/editar/versionar su SKILL.md.
2. **Invocacion:** llamarlas por `@nombre` en el chat, o que la entidad las dispare por trigger.
3. **Historial:** log de ejecuciones (`routine_run`) para ver/auditar que corrio y como salio.

**Delta de esquema (supersede el split agent/skill de v1.2):**
```sql
routine(id, workspace_id, name, skill_md, tools_allowlist, schema_output_json, preset_id, trigger_json, persona_md, is_active, created_at)
routine_run(id, routine_id, workspace_id, input_json, output_json, evidence_json, status, edit_pct, created_at)
```
(la `agent` table de v1.2 se elimina; persona vive en `routine.persona_md`.)

## 5. Definition of Done (Etapa 1 cerrada cuando)

- App **firmada** Win + Mac, instalable por un no-tecnico sin terminal ni ayuda.
- Las 9 capacidades de la seccion 2 funcionan end-to-end con **datos reales de Alvaro** (RFQ/cobranza/seguimiento de MWT).
- Gold loop demostrado: el edit_pct de un mismo tipo de tarea baja con el uso.
- Cero envio sin HITL; cero accion disparada por contenido de email (test de injection); cero fuga cross-workspace.
- Licencia aplicada (FSL recomendada) + marca registrada iniciada.

## 6. Secuencia interna (no big-bang; se usa desde SL1)

SL0 (esqueleto+seed) -> SL1 (routing+chat+draft real) -> SL2a/b/c (workspaces+KB) -> SL3a/b/c (skills+HITL+gold) -> SL3.5 (sellado+llave) -> SL5 (correo) -> SL4 (empaque desktop firmado).

Estimacion: ~11.5-12 semanas, 1 dev full-time. Alvaro lo usa desde SL1; queda DONE (distribuible) en SL4.
Si el timeline aprieta, **SL5 (correo) es lo unico recortable** sin romper el nucleo (se pega/lee a mano mientras tanto).

## 7. Dependencias para arrancar (bloquean SL0)

1. **Ratificar DEC_FB_SPACELOOM_FREEZE_SCOPE** (carve-out para construir SL0 single-user). Sin esto, sigue en planeacion.
2. **Licencia final** (FSL recomendada) - [PENDIENTE legal].
3. **Rotar credenciales IMAP de Kimi Work** (urgente, independiente).
4. **Presupuestar firma de codigo** (Apple Developer USD 99/ano + cert Windows) - necesaria para SL4.

## 8. Roadmap mayor (donde encaja Etapa 1)

**Etapa 1 = prueba, no techo.** El objetivo sigue siendo todo el alcance; Etapa 1 valida el modelo en
chico antes de gastar en lo grande. Regla de construccion: **expansion-ready, no expansion-built** -- armar
con costuras limpias para que lo grande se AGREGUE encima, no que obligue a reescribir:
- Sellado de espacios: idea ya presente (local) -> mañana se sube a cripto/multi-tenant detras de la misma costura. Aditivo.
- Rutinas/skills en SKILL.md: ya portables; sirven igual en grande.
- Una entidad -> una entidad por tenant. Mismo patron, escalado.
- Lo que cambia (SQLite->Postgres+RLS, app desktop->web, BYO-key->keys gestionadas) son capas que se SUMAN, si el modelo de datos queda limpio desde ahora (no clavar supuestos single-user que fuercen rewrite).
Cuidado: NO construir el futuro ahora; solo no bloquearlo.


- **Etapa 1 (esta):** app standalone single-user, telar completo, local-first, distribuible.
- **Etapa 2:** multi-usuario interno (equipo MWT comparte; roles, delegacion). Sin gate comercial.
- **Etapa 3:** multi-tenant / SaaS (el FaberLoom pausado; sello criptografico, ARCH_FB_AGENT_RUNTIME_EVAL). Solo si la validacion de mercado lo justifica.

## 9. Changelog
- v1.0 (2026-06-17): define Etapa 1 = app standalone con todo el telar single-user. Outcome (9 capacidades), alcance funcional, fuera-de-alcance, DoD, secuencia interna SL0-SL5, dependencias, roadmap mayor. DRAFT, condicionada a ratificacion del carve-out (DEC freeze). No toca FROZEN.
- v1.0a (2026-06-17, post-sesion): agregado principio rector (sec 1.1: entidad resuelve con contexto del espacio; sabe-donde global / resuelve local), Routine Hub (sec 4.2, reemplaza agent factory; rutina = SKILL.md + persona, invocable @nombre), superficies del producto (Inbox/WorkLoom/SpaceLoom; FaberLoom = producto, SpaceLoom = superficie), y regla "expansion-ready, no expansion-built" en el roadmap (sec 8).

---

### SPEC_FB_ROUTING_PRESETS_v1.md

# SPEC_FB_ROUTING_PRESETS -- Presets de ruteo y fabrica de presets (modelo Pedal Commander)

id: SPEC_FB_ROUTING_PRESETS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: SPEC
stamp: DRAFT -- 2026-06-10 -- indexado a canonico via sync_fb_routing_indexa.ps1
aprobador: CEO (Alvaro) -- aprueba indexacion 2026-06-10
fuente: research web 2026-06-10 (OpenRouter presets/provider-routing/sovereign-AI, Microsoft Foundry model router, Portkey configs, LiteLLM tags) + sesion Cowork 2026-06-10
aplica_a: [FaberLoom, MWT]
relacionado: SPEC_FB_BUILD_SEQUENCE v2 - POL_DATA_CLASSIFICATION - ENT_FABERLOOM_PRICING_TIERS - ENT_GOB_PENDIENTES (Q7 tenant_model_allowlist) - SPEC_FB_ARCHETYPE (optimiza-vs-sugiere)
reemplaza: SPEC_FB_EVAL_ARENA_v1 como mecanismo de optimizacion (la arena queda archivada como referencia)

---

## 1. Concepto

Tres capas que componen, en jerarquia estricta:

```
ECU (envelope de seguridad)      = POL_DATA_CLASSIFICATION, fail-closed. NO configurable.
  > Preset del tenant (el pedal) = jurisdiccion + providers + curva + caps. Lo elige el Owner.
    > Curva del usuario          = modo eco/balanceado/sport dentro del preset. Lo elige cada usuario.
      > Auto-optimizador         = regla de promocion HITL elige default POR CLASE DE TAREA
                                   dentro del conjunto factible. Sugiere, no aplica.
```

Resolucion en runtime: `feasible = allowed_by_data_class(N) INTERSECT preset.providers INTERSECT curve.tiers` -> pick por task_class. Interseccion de listas, deterministico, <20ms, cada decision auditada con su razon.

## 2. Anatomia de un preset (schema)

Patron de la industria adoptado: preset como configuracion NOMBRADA y VERSIONADA, referenciable como si fuera un modelo (`@preset/ahorro-maximo`), separada del codigo, con rollback (OpenRouter). Vocabulario de provider preferences tomado del estandar de facto: allowlist/blocklist, sort, max_price, data_collection deny, ZDR.

```yaml
preset:
  slug: ahorro-maximo            # referenciable como @preset/ahorro-maximo
  version: 3                     # historial completo, rollback, cambio = evento auditado
  owner_locked: [envelope]       # secciones que solo Owner edita

  envelope:                      # decision de compliance -- SOLO Owner
    jurisdictions: [US, EU]      # o [US, EU, CN_selfhost] con cost-mode opt-in
    providers_allow: [anthropic, openai]      # allowlist explicita
    providers_deny: []                        # blocklist gana sobre allow
    data_collection: deny        # ZDR donde el provider lo ofrezca
    byo_keys: false              # E3+

  curve:                         # el "pedal" -- editable por usuario dentro del envelope
    mode: eco | balanceado | sport | sport_plus
    borderline_policy: cheap | premium
    # ESTE es el parametro que de verdad distingue modos (hallazgo industria):
    # las tareas claramente simples van baratas y las complejas van caras en TODOS los modos;
    # la diferencia es a donde va lo AMBIGUO. eco -> cheap. sport -> premium.

  task_overrides:                # por clase de tarea (patron tags LiteLLM)
    cotizacion: { default: sonnet, escalation: opus }
    cobranza:   { default: haiku,  escalation: sonnet }
    chat_kb:    { default: sonnet, escalation: opus }
    # los defaults aqui son los que la regla de promocion HITL propone actualizar

  caps:
    monthly_budget_usd: 150      # hard stop + alerta 80%
    max_cost_per_task_usd: 0.50
    max_latency_s: 12            # umbral suave: deprioriza, no excluye (patron OpenRouter)

  escalation:
    user_boost_button: true      # "rehacer con el mejor" -- el click es senal gratis
    boost_cap_per_day: 10
```

Merge en runtime: parametros del request hacen shallow-merge sobre el preset (patron OpenRouter). Validacion AL GUARDAR, no en runtime: un preset que viole el envelope de data-class no se puede salvar (ej: providers CN + ceiling N2 = error de lint, no excepcion en produccion).

## 3. Los 4 presets de casa (nivel 0 de la fabrica)

| Preset | Envelope | Curva | Para quien |
|---|---|---|---|
| Conservador | US/EU only, ZDR on | sport (borderline->premium) | regulado, primera impresion, default de onboarding |
| Balanceado | US/EU only | balanceado | default post-confianza; recomendado interactivo |
| Ahorro Maximo | US/EU + cost-mode CN_selfhost para N0-N1 | eco (borderline->cheap) | batch, back-office, sensible al precio |
| Sport+ | US/EU only | sport_plus (siempre el mejor, costo ignorado) | demos, tareas criticas, boost |

Curados y versionados por FaberLoom. El tenant arranca en Conservador (default seguro = decision ya firmada en PRICING_TIERS limitaciones v1.0).

## 4. La fabrica de presets (niveles 1-3)

**Nivel 1 -- Wizard de onboarding (3 preguntas, 0 knobs):**
1. "Tus datos pueden procesarse solo en US/EU, o tambien proveedores chinos/self-host para data no sensible?" -> envelope
2. "Que preferis: maxima calidad, balance, o maximo ahorro?" -> curve
3. "Presupuesto mensual de IA?" -> caps
El wizard COMPONE un preset desde la matriz envelope x curve x caps. El usuario nunca ve nombres de modelos. Anti-pattern prohibido: exponer model picker crudo o mas de ~7 campos.

**Nivel 2 -- Template por vertical:**
El vertical (safety_footwear, legal_practice...) aporta las task_classes y sus defaults razonables. El preset del tenant hereda del template del vertical via copy-on-create (plano, sin cascada -- coherente con la simplificacion de herencia ya acordada).

**Nivel 3 -- Presets derivados por datos (la fabrica continua):**
La regla de promocion HITL (N>=30 tareas de una clase, aprobacion-sin-edicion del modelo barato dentro de X pts del premium) NO toca el preset: genera una PROPUESTA de delta con evidencia adjunta:
> "En cobranza, haiku rindio 94% vs 96% de sonnet en 42 tareas. Cambiar el default ahorra ~$31/mes. [Aplicar] [Ignorar] [Shadow run 2 semanas]"
Owner aprueba -> nueva version del preset (auditada, reversible). Esto implementa optimiza-vs-sugiere de SPEC_FB_ARCHETYPE con HITL como fuente, sin arena.

**Nivel 4 -- Preset builder con IA (chat-first):**
El builder es un SKILL mas de FaberLoom (dogfooding del propio runtime). Patron: IA como compilador de lenguaje natural -> preset.

- **Modo creacion:** entrevista conversacional en vez de formulario. El agente pregunta por la operacion, detecta restricciones implicitas ("manejas datos financieros de clientes -> limita proveedores"; "tu volumen es batch -> eco sirve") y COMPONE el preset. El wizard nivel 1 queda como fallback no-conversacional.
- **Modo tuning:** "estoy gastando mucho en cobranza" -> el agente consulta savings ledger + stats HITL -> propone delta con evidencia. Es el nivel 3 invocable por el usuario, no solo batch semanal.
- **Backtest obligatorio antes de aprobar:** el agente simula el preset propuesto contra los ultimos 30 dias del ledger real del tenant (replay del calculo de costos, sin re-correr LLMs): "habrias gastado $X vs $Y; estas N tareas cambiarian de modelo; tu edit-rate historico en esa clase sube/baja Z pts". Convierte la aprobacion en decision con numeros. Costo de build: bajo (query + aritmetica sobre ledger).
- **Contrato de seguridad del builder:**
  1. Output estructurado contra el JSON schema del preset; pasa por el MISMO lint que una edicion manual; si viola envelope -> rechazo y retry del agente. La IA nunca aplica nada.
  2. Draft llega al Owner con el patron universal de 3 botones (aprobar/descartar/iterar).
  3. Relajar jurisdiccion o providers = paso de confirmacion explicito separado, nunca implicito en un "ok" general.
  4. Audit: `generated_by: ai_preset_builder`, `approved_by: owner`, prompt de origen y backtest adjuntos al evento.
- **Etapa:** el skill builder entra en E2 (necesita ledger con datos y el engine de skills ya vivo); el backtest en E2; la entrevista de onboarding para terceros en E3.

**Guardrails de la fabrica:**
- Lint de presets al guardar (envelope vs data-class, caps coherentes, providers existentes)
- Jurisdiccion y providers: SOLO Owner (firma el DPA). Curva y boost: por usuario. Nunca al reves.
- Cambio de preset = evento de audit con diff
- Maximo 1 preset custom activo por tenant en E3 inicial (evitar zoo de configs)

## 5. Que se construye cuando

| Etapa | Alcance |
|---|---|
| E1 | Schema completo + los 4 presets de casa. Anthropic-only: la curva degenera a haiku/sonnet/opus y el envelope es trivial -- pero el codigo del hook ya resuelve por interseccion, asi que E3 no rediseña nada. Savings ledger registra desde el dia 1. |
| E2 | task_overrides reales (cotizacion, cobranza) + boost button + primeras propuestas nivel 3 con datos HITL propios |
| E3 (condicional gate E2.5) | Wizard nivel 1 + template por vertical nivel 2 + multi-proveedor/multi-jurisdiccion real + cost-mode CN opt-in con consentimiento explicito |

## 6. Por que esto es vendible (y la arena no lo era)

El preset ES la interfaz comercial del diferenciador "tiers de confidencialidad + cost-mode" de PRICING_TIERS: se demuestra en 30 segundos en una llamada ("elegi donde pueden procesar tus datos y cuanto queres gastar; el sistema optimiza adentro de eso y te muestra el ahorro"). Mapea ademas a la practica estandar de la industria (OpenRouter presets/sovereign-AI, Portkey workspaces+residency, Foundry router cost-aware), o sea: comprable sin fe.

---

Changelog:
- v1.0 (2026-06-10): Creacion. 3 capas (ECU/preset/curva) + auto-optimizador HITL. Schema YAML, 4 presets de casa, fabrica niveles 1-4 (nivel 4 = preset builder con IA chat-first + backtest contra ledger), guardrails, fases E1-E3. Reemplaza SPEC_FB_EVAL_ARENA como mecanismo de optimizacion. ASCII puro.

---

### SCH_FB_SKILL_MANIFEST_v2.md

# SCH_FB_SKILL_MANIFEST_v2 — Schema Canónico Manifest Skill v2 FaberLoom
id: SCH_FB_SKILL_MANIFEST_v2
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE — 2026-04-29 (re-scopeado de MWT a FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_AGENT_BUILDER_v1.md · ARCH_AGENT_PRINCIPLES.md · POL_FB_OUTCOME_ACCOUNTABILITY.md · ENT_FB_AGENT_ARCHETYPES_v1.md · SCH_FB_FLOW_DAG.md · SCH_FB_TASK_ENTITY.md · ENT_FB_TEMPLATE_LIBRARY_v1.md · ENT_FB_TOOL_CATALOG_v1.md

---

## Declaración

Este schema define el **manifest canónico v2 para todo SKILL en la plataforma FaberLoom**. Extiende el frontmatter SKILL.md (estándar abierto Anthropic, soportado por 26+ plataformas y agentskills.io) con extensión namespaceada `metadata.mwt.*` que captura los campos específicos requeridos por ARCH_AGENT_PRINCIPLES.

**Estrategia: extender, no inventar.** El frontmatter base mantiene compatibilidad con el ecosistema (Claude Skills, Hermes, Cursor, Cline, OpenCode). La extensión captura los principios fundacionales (P0-P15) como campos auditables.

**Deuda técnica conocida:** el namespace `metadata.mwt.*` quedó así porque la sesión original conceptualizó el schema como MWT-internal antes de re-scopearlo a FB. El namespace correcto a futuro es `metadata.fbl.*` (FaberLoom). Migración del namespace queda como deuda — backward compat se mantiene con alias `mwt -> fbl` en el compiler hasta que todos los manifests del primer tenant (MWT) migren.

**Migración obligatoria:** todos los SKILLs en SHADOW del primer tenant beta (MWT/Rana Walk) se migran a v2 progresivamente, empezando por SKILL_RW_REVIEW_TRIAGE (primer agente autónomo objetivo de FB v1). Hasta migración, los SKILLs legacy del tenant MWT siguen siendo válidos. Tenants futuros entran directamente con manifest v2.

---

## Por qué este schema existe

Los frontmatters actuales de los 10 SKILLs en SHADOW del primer tenant (MWT) son heterogéneos. Ninguno declara archetype formal, ningún tools_mcp explícito, ningún sub_agents formalizado (DEMAND_FORECASTER es swarm de facto sin declarar), ningún outcome metric, ningún kill switch, ningún learning_consolidation target. El estado del primer tenant es representativo del problema que la plataforma FB resuelve para tenants en general.

Sin schema canónico:
- Validación automática imposible
- Audit cross-SKILL no formalizable
- Patch broadcast (cambio en POL/ENT aguas arriba) no detecta dependencias
- Autonomy graduation sin criterios uniformes
- ARCH_AGENT_PRINCIPLES P0-P14 quedan declarativos no ejecutables

---

## Schema base SKILL.md (estándar Anthropic, no se toca)

```yaml
name: SKILL_RW_REVIEW_TRIAGE
description: |
  Skill que clasifica reviews entrantes de Amazon FBA Rana Walk y genera
  draft de respuesta según POL_BRAND_VOICE + POL_AMAZON_TOS.
version: 2.0.0
metadata:
  # extensiones libres, namespaceadas
  mwt:
    # ver sección "Extensión metadata.mwt.*" abajo
    ...
```

Campos `name`, `description`, `version` son obligatorios y siguen estándar agentskills.io.

---

## Extensión metadata.mwt.* (canónica MWT)

```yaml
metadata:
  mwt:
    # === Identidad y dominio ===
    id: SKILL_RW_REVIEW_TRIAGE              # canonical ID, formato SKILL_* o TPL_*
    type: agent                              # skill_package | agent (NUEVO v1.2)
    architectural_archetype: triage          # generator | triage | validator | orchestrator | swarm | reactive | skill_package (NUEVO v1.2 — ver ENT_AGENT_ARCHETYPES_V1)
    domain: PRODUCTO                         # IDX_DOMINIO al que pertenece
    archetype: routine                       # skill | workflow | reactive | autonomous | supervisor | routine (cómo ejecuta)
    visibility: INTERNAL                     # PUBLIC | PARTNER_B2B | INTERNAL | CEO_ONLY
    status: SHADOW                           # SHADOW | ACTIVE | DEPRECATED | ARCHIVED

    # === Inputs y dependencias KB ===
    inputs:
      kb_refs:                               # archivos de la KB requeridos
        - PLB_REVIEW_TRIAGE
        - ENT_RW_BRAND_VOICE
        - LOC_ES_MX
        - POL_BRAND_VOICE
        - POL_AMAZON_TOS
        - POL_CLAIMS_SCANNER
      data_sources:
        - SP-API/reviews
      depends_on_skills: []                  # otros SKILL_ invocados (sub-agents)

    # === Skills imports (NUEVO v1.2 — separado de tools_mcp) ===
    # Skills son paquetes de comportamiento reutilizables (type: skill_package).
    # Distintos de tools_mcp (que son capacidades externas tipo APIs).
    skills_imports:
      - skill_id: SKILL_HUMANIZE_COMMS
        version: ">=0.2"
        invocation_alias: humanize_comms     # cómo el agent lo referencia internamente
      - skill_id: SKILL_BRAND_VOICE_RW
        version: ">=0.3"
        invocation_alias: brand_voice

    # === Multi-cliente lógico (NUEVO v1.2 — D17) ===
    multi_client_mode: true                  # default false; true exige client_resolver
    client_resolver:
      kind: config_lookup                    # config_lookup | explicit_id | email_pattern
      source: ENT_COMERCIAL_CLIENTES         # KB ref o tabla
      key_field: client_id
      resolve_strategy: by_domain            # by_domain | by_explicit_id | by_email_pattern
      payload_extraction: payload.email.sender_domain
      fallback: prospect_unknown             # client_id por defecto si no matchea
      cache_ttl_min: 60

    # === Contract: outputs plural y policies ===
    contract:
      outputs:                               # lista tipada — un agente puede emitir varios artefactos
        - id: response_draft
          schema: SCH_REVIEW_RESPONSE
          kind: asset                        # asset | decision | learning | side_effect
          destination: drafts/queue
          required: true
          requires_human_approval: true      # P3 draft-first explícito por output
        - id: severity_tag
          schema: SCH_SEVERITY_DECISION
          kind: decision
          destination: episodic_memory
          required: true
        - id: escalation_ticket
          schema: SCH_ESCALATION_TICKET
          kind: side_effect
          destination: case_log/
          required: false
          condition: severity == "critical"  # solo si rama crítica
      policies:                              # POL_ obligatorios pre-ejecución
        - POL_BRAND_VOICE
        - POL_AMAZON_TOS
        - POL_CLAIMS_SCANNER
        - POL_DATA_CLASSIFICATION
      schema_lock: strict                    # strict | flexible (no se acepta flexible en archetype routine/autonomous)

    # === State machine (P7 obligatorio) ===
    state_machine:
      ref: SCH_STATE_MACHINE_REVIEW_TRIAGE   # estado y transiciones declaradas
      states_minimum: [drafting, awaiting_approval, approved, executing, completed, rejected, escalated]
      timeout_default_h: 24

    # === Golden samples (norte de calidad + few-shot + regression eval) ===
    golden_samples:
      - id: GS_REVIEW_RESPONSE_2026_03
        path: docs/faberloom/gold_samples/review_response_2026_03.md
        validates_outputs: [response_draft]  # qué outputs valida este sample
        evaluation_use: reference            # reference | regression_test | few_shot
        added_by: ceo
        added_at: 2026-03-15
        notes: "Caso 4-star queja tamaño, recovery rating post respuesta"
      - id: GS_REVIEW_ESCALATION_2026_02
        path: docs/faberloom/gold_samples/review_escalation_2026_02.md
        validates_outputs: [escalation_ticket]
        evaluation_use: regression_test
        added_by: ceo
        added_at: 2026-02-10

    # === Skill package metadata (cuando type: skill_package) — NUEVO v1.2 ===
    # Solo para type: skill_package. Skills son ejecutables standalone via CLI.
    skill_package_metadata:
      default_prompt: "Use $humanize_comms para redactar mensajes con voz CEO en tono directo, sin saludos, al punto."
      invocation_alias: humanize_comms       # CLI: mwt skill run humanize_comms
      stateless: true                        # skill packages típicamente stateless
      reusable_by_agents: true               # importable por agents

    # === Template metadata (cuando is_template: true) ===
    is_template: false                       # default false
    template_metadata:                        # solo si is_template: true
      template_id: TPL_REVIEW_TRIAGE         # ID del template
      template_version: 1.0
      icon: triage                           # NUEVO v1.2: icon ID del catálogo (triage | generator | validator | orchestrator | swarm | reactive | custom_path)
      maintained_by: ceo
      template_status: approved              # approved | draft | deprecated
      forks_count: 0                         # auto-incrementa en cada Fork
      placeholders:                          # campos que el Fork pide al CEO
        - path: outcome.baseline_value
          type: number
          help: "TTR review actual sin agente, en horas"
          required: true
        - path: outcome.target_at_60d
          type: expression
          help: "Objetivo a 60 días (ej: '< 8')"
          required: true
        - path: budget.usd_monthly
          type: number
          default: 25
          help: "Budget mensual aprox"
          required: false

    # === Triggers (NUEVO v1.2 — D16 conector dumb / agent smart) ===
    # El conector solo detecta evento + extrae payload + POST al endpoint.
    # CERO clasificación, branching o transformación de negocio en n8n.
    # Toda la lógica vive embebida en el agent vía flow.
    triggers:
      - kind: webhook                         # webhook | cron | api | manual
        source: gmail                         # gmail | slack | sp-api | sap | ...
        endpoint: /api/triggers/gmail
        connector: n8n                        # n8n | native | mcp_server
        connector_workflow_id: gmail_b2b_watcher_v1   # ref versionada al workflow n8n
        idempotency_key_field: payload.email.message_id
        rate_limit_per_min: 30
        deduplication_window_h: 24
        pre_dispatch_filters:                 # opcional, lógica trivial pre-agent
          - kind: spam_domains_blocklist
            max_logic_complexity: trivial    # solo regex/lookup, NO LLM
        auth_method: hmac

    # === Tools MCP (capacidades externas tipo APIs) ===
    tools_mcp:
      - id: amazon_sp_api_reviews
        kind: read_only
        scope: list_reviews | get_review | mark_actioned
        permission_model: per-tool            # cada tool con su permission
      - id: gmail_send                        # tool de SALIDA, distinto de trigger Gmail de ENTRADA
        kind: write
        scope: draft_only                     # nunca send sin approval

    # === Memory binding (three-layer) ===
    memory:
      pgvector_filter:
        domain: PRODUCTO
        visibility: [PUBLIC, INTERNAL]
        exclude: [FROZEN, CEO_ONLY]
      episodic_logger:
        enabled: true
        retention_days: 365
        pii_scrubbing: true
      learning_consolidation:                  # P5: target de aprendizaje
        target: GOLD_SAMPLES                   # CONTEXTO | SKILL_REFINEMENT | GOLD_SAMPLES | none
        requires_human_gate: true              # SIEMPRE true
        auto_apply: false                      # SIEMPRE false (regla inquebrantable)

    # === Deliverable type (Mitjana) — derivado de contract.outputs[] ===
    # NOTA: con outputs plural (v1.1) el deliverable.type se computa automáticamente del kind
    # de cada output. Si todos los outputs son kind:asset → deliverable.type=asset.
    # Si mezcla → deliverable.type=hybrid. No declarar manualmente.
    deliverable:
      computed_from_outputs: true              # builder calcula tipo desde contract.outputs[]
      decision_branches:                       # solo si algún output kind:decision
        - approve_response
        - escalate_to_human
        - ignore
      must_close_decisions: true               # no se acepta "tal vez" como output decision

    # === Outcome metric (P15 — POL_OUTCOME_ACCOUNTABILITY) ===
    outcome:
      primary: time_to_response_p50_hours      # métrica de negocio
      baseline_value: 28                       # valor pre-agente (PENDIENTE — CEO declara)
      target_at_60d: < 8                       # objetivo a 60 días
      secondary:
        - cited_complaints_resolved_rate
        - account_health_rating_delta
      measurement_cadence: weekly

    # === Budget y kill switch ===
    budget:
      usd_monthly: 25
      hard_cap_usd: 50
      tokens_monthly: 500000
      time_per_run_s: 60
      kill_switch:
        enabled: true
        trigger_on:
          - acceptance_rate_drop_pp: 10        # baja 10pp en 7 días
          - cost_overrun_count: 3              # 3 overruns en 7 días
          - human_intervention_count: 1        # 1 intervención manual
          - outcome_no_progress_days: 90       # sin moverse en 90 días → SHADOW

    # === Autonomy graduation (P4 — autonomía por evidencia) ===
    autonomy:
      current_level: 1                          # 0-6, ver SPEC_AUTONOMY_CONTROL_ENGINE
      target_level: 3                           # objetivo
      promotion_policy: standard                # standard | conservative | aggressive
      promotion_criteria:
        runs_minimum: 100
        acceptance_rate_min: 0.90
        schema_compliance_min: 0.99
        decision_closure_rate_min: 0.70
        diversity_coverage_min: 0.80
        cost_within_budget_rate_min: 0.95
      shadow_mode_runs: 50                      # paralelo SHADOW antes de promoción
      demotion_triggers:                        # democión automática
        acceptance_rate_drop_pp: 10
        consecutive_failures: 3                 # MAX_CONSECUTIVE_FAILURES (Claude Code leak)
        rejection_rate_max: 0.30

    # === Tenant scoping (MWT-only — single tenant siempre) ===
    # Para MWT v1 este campo es fijo y solo declarativo.
    # Si en el futuro se requiere multi-tenant, NO modificar este schema —
    # crear SCH_SKILL_MANIFEST_FB_V1 que extiende este con multi_tenant.
    tenant_scope:
      mode: single
      tenants: [mwt_internal]

    # === Consumers y observabilidad ===
    consumed_by:                                # quién invoca este skill
      - n8n://review-triage-flow
      - django://api/skills/review-triage
    observability:
      langfuse_session: review_triage
      audit_level: standard                     # standard | high | maximum
      trace_sample_rate: 1.0                    # 1.0 = todos los runs (SHADOW)
```

---

## Validaciones diferenciadas por type (NUEVO v1.2)

| Validación | Aplica a `type: skill_package` | Aplica a `type: agent` |
|------------|--------------------------------|------------------------|
| `tools_mcp[]` | NO permitido (skills no tienen tools propias) | sí |
| `channels` | NO permitido | sí |
| `triggers[]` | NO permitido | sí (si archetype: routine) |
| `skill_package_metadata` | obligatorio | NO permitido |
| `default_prompt` | obligatorio | NO aplica |
| `outcome.primary` | opcional | obligatorio |
| `budget.kill_switch` | opcional | obligatorio |
| `state_machine.ref` | opcional (skills suelen ser atómicos) | obligatorio |
| `multi_client_mode` | NO aplica | opcional |
| `architectural_archetype` | obligatorio = `skill_package` | obligatorio (Generator/Triage/Validator/Orchestrator/Swarm/Reactive) |

## Validaciones diferenciadas por architectural_archetype (NUEVO v1.2)

Cada arquetipo arquitectónico (ver ENT_AGENT_ARCHETYPES_V1) suma 2-3 validaciones específicas:

| Arquetipo | Validación adicional |
|-----------|----------------------|
| **Generator** | `golden_samples[]` ≥ 1 por output `kind: asset` |
| **Triage** | `flow.branches[]` con clausula `default:` exhaustiva en cada branch node |
| **Validator** | `policies[]` ≥ 1 + sección `deterministic_first` declarada en flow |
| **Orchestrator** | `state_machine.states ≥ 7` + side_effects con `requires_human_approval` por defecto |
| **Swarm** | `inputs.depends_on_skills[]` ≥ 2 + budget rollup declarado |
| **Reactive** | `triggers[]` ≥ 1 (cron o webhook) + `idempotency_key_field` declarado |
| **Skill_package** | `skill_package_metadata.default_prompt` no vacío |

## Validaciones build-time obligatorias

El compiler del builder valida estas reglas. Falla la compilación si alguna se rompe:

| # | Regla | Falla si |
|---|-------|----------|
| 1 | Visibility coherente | `mwt.visibility < max(inputs.kb_refs.visibility)` |
| 2 | Tipos no mezclados | `kb_refs` declara `ENT_X` pero apunta a archivo `PLB_X` |
| 3 | FROZEN seguro | input FROZEN no marcado `reference_only` |
| 4 | Dependency graph íntegro | manifest rompe cadena en DEPENDENCY_GRAPH.md |
| 5 | Schema lock activo | hay `tools_mcp.kind: write` sin `outputs[].schema` declarado |
| 6 | Outcome declarado | `outcome.primary` ausente y `archetype != skill_informational` |
| 7 | Kill switch activo | `archetype` en `[autonomous, routine, supervisor, workflow]` sin `budget.kill_switch.enabled: true` |
| 8 | Learning gate humano | `learning_consolidation.target != none` y `requires_human_gate != true` → reject |
| 9 | Auto-apply prohibido | `learning_consolidation.auto_apply: true` → reject (regla inquebrantable) |
| 10 | Tenant single | `tenant_scope.mode != single` → reject (este schema es MWT-only) |
| 11 | Sub-agents declarados | `archetype: supervisor` o `swarm` y `depends_on_skills: []` → reject |
| 12 | Promotion criteria coherentes | `autonomy.promotion_criteria` valores fuera de [0, 1] o thresholds inconsistentes → reject |
| 13 | Outputs plural | `contract.outputs[]` vacío → reject (al menos un output requerido) |
| 14 | Output kind válido | `contract.outputs[].kind` no en {asset, decision, learning, side_effect} → reject |
| 15 | Output IDs únicos | duplicados en `contract.outputs[].id` → reject |
| 16 | Approval requerida en assets externos | `kind: asset` con `destination` externa (publica) sin `requires_human_approval: true` → reject (P3 absoluto) |
| 17 | Golden sample requerido | `archetype` en `[workflow, autonomous, routine]` y `golden_samples: []` vacío → reject (al menos uno por output kind:asset) |
| 18 | Golden sample válido | `golden_samples[].path` no existe en filesystem → reject |
| 19 | Template placeholders válidos | `is_template: true` y `template_metadata.placeholders[]` vacío → warning (template sin placeholders es manifest plano) |
| 20 | Flow DAG válido | `archetype: workflow` y falta `flow.nodes[]` → reject (ver SCH_FLOW_DAG) |
| 21 | Type vs archetype coherente | `type: skill_package` con `archetype: workflow/supervisor/autonomous` → reject |
| 22 | Skills imports válidos | `skills_imports[]` referencia skill_id no presente en KB → reject |
| 23 | Triggers solo en agent | `type: skill_package` con `triggers[]` declarado → reject |
| 24 | Tools solo en agent | `type: skill_package` con `tools_mcp[]` declarado → reject |
| 25 | Multi-cliente coherente | `multi_client_mode: true` sin `client_resolver` declarado → reject |
| 26 | Trigger pre_dispatch_filters disciplinado | `pre_dispatch_filters[].max_logic_complexity != trivial` → warning (riesgo violar D16) |
| 27 | Connector workflow versionado | `triggers[].connector: n8n` sin `connector_workflow_id` → reject |
| 28 | Architectural archetype declarado | falta `architectural_archetype` → reject |

---

## Migración de SKILLs legacy

Los 10 SKILLs actuales (SKILL_AMAZON_OPS, SKILL_CLIENT_SERVICE, SKILL_COMPLIANCE_CHECKER, SKILL_COPY, SKILL_DEMAND_FORECASTER, SKILL_HUMANIZE_BRAND, SKILL_HUMANIZE_COMMS, SKILL_KB_AUDITOR, SKILL_PROFORMA_BUILDER, SKILL_RW_REVIEW_TRIAGE) se migran progresivamente en orden de prioridad operacional.

Orden recomendado:
1. **SKILL_RW_REVIEW_TRIAGE** (Fase 1 SPEC_AGENT_BUILDER_MWT_V1) — primer agente autónomo
2. **SKILL_RW_LISTING_OPT** o equivalente — segundo agente
3. **SKILL_DEMAND_FORECASTER** — único swarm, requiere sub_agents declarados
4. **SKILL_COMPLIANCE_CHECKER** — validator, two-stage review
5. Resto en orden CEO-priorizado

**Hasta migración**: SKILLs legacy mantienen su frontmatter actual y son válidos. Coexisten con v2 sin conflicto. La validación schema v2 solo aplica a SKILLs que declaran `metadata.mwt.id` con esta version.

---

## Compatibilidad cross-vendor

El frontmatter base SKILL.md es legible por:
- Claude Code (subagents y skills, Anthropic)
- Hermes Agent (NousResearch)
- Cursor (.cursorrules)
- OpenCode
- Cline
- Gemini CLI extensions
- agentskills.io hub

La extensión `metadata.mwt.*` es invisible para estos vendors (campo libre del estándar). Esto preserva portabilidad: un SKILL puede ejecutarse en runtime MWT con todas las reglas, o ejecutarse en Claude Code stand-alone para testing rápido.

---

## Ejemplo mínimo (para testing rápido)

```yaml
name: SKILL_TEST_HELLO
description: Skill mínimo para testing del compiler
version: 0.1.0
metadata:
  mwt:
    id: SKILL_TEST_HELLO
    domain: PLATAFORMA
    archetype: skill
    visibility: INTERNAL
    status: SHADOW
    inputs:
      kb_refs: []
    contract:
      outputs:
        - id: hello_text
          schema: SCH_HELLO_OUTPUT
          kind: asset
          destination: logs/hello/
          required: true
      schema_lock: strict
    state_machine:
      ref: SCH_STATE_MACHINE_BASIC
    golden_samples:
      - id: GS_HELLO_BASIC
        path: docs/gold_samples/hello_basic.md
        validates_outputs: [hello_text]
        evaluation_use: reference
    deliverable:
      computed_from_outputs: true
    outcome:
      primary: hello_count
      baseline_value: 0
      target_at_60d: > 0
    budget:
      usd_monthly: 1
      hard_cap_usd: 5
      kill_switch:
        enabled: true
        trigger_on:
          consecutive_failures: 3
    autonomy:
      current_level: 0
      target_level: 1
    tenant_scope:
      mode: single
      tenants: [mwt_internal]
```

Este manifest pasa todas las validaciones build-time. Sirve como smoke test del compiler.

---

## Nota de scope

Este schema aplica a **FaberLoom v1 (single-tenant beta con MWT como primer tenant)**. La sección `tenant_scope` y los campos relacionados con `multi_client_mode` están desde día 1 aunque el tenant inicial sea uno solo, evitando migración traumática cuando entre tenant 2. La infra cripto multi-tenant (isolation key per tenant, A2A bridge, profile system multi-org) se diseña para FB v2 cuando exista segundo prospect/LOI — heredando este schema como base.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29): creación con scope MWT-only erróneo. Schema base SKILL.md + extensión `metadata.mwt.*` con 12 secciones (identidad, inputs, contract, state_machine, tools_mcp, memory, deliverable, outcome, budget, autonomy, tenant_scope, consumed_by/observability). 12 validaciones build-time. Plan de migración de 10 SKILLs legacy. Compatibilidad cross-vendor preservada.
- v1.1 (2026-04-29b): outputs plural en `contract.outputs[]` (reemplaza `output_schema` singular) — cada output con id, schema, kind (asset/decision/learning/side_effect), destination, required, condition opcional. Nueva sección `golden_samples` (norte de calidad + few-shot + regression eval). Nueva sección `is_template + template_metadata + placeholders` para Template Library (mismo módulo en MWT v1, separable en FaberLoom). 8 validaciones nuevas (13-20): outputs vacío, output kind, IDs únicos, approval externa, golden requerido, golden válido, template placeholders, flow DAG. Deliverable type ahora computed_from_outputs. Derivado de observación CEO sobre Workspace Agents OpenAI 2026-04-22 (templates pre-hechas + step-by-step plan + golden sample + outputs múltiples).
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SCH_SKILL_MANIFEST_V2 → SCH_FB_SKILL_MANIFEST_v2. El schema fue conceptualizado durante sesión Cowork 2026-04-29 como MWT-only por error de scoping. El scope correcto siempre fue FB platform — MWT pasa de "el sistema" a "primer tenant beta". Sección `tenant_scope` desde día 1 con valor único `[mwt_internal]` en v1, extensible a multi-tenant en v2. Multi-client mode (D17) renombrado conceptualmente a multi-tenant base (sin cambio de nombre del campo por backward compat). Namespace `metadata.mwt.*` se conserva como deuda técnica con alias futuro a `metadata.fbl.*`. Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v1.2 (2026-04-29c): distinción formal **type: skill_package | agent** con validaciones diferenciadas por type. Nueva sección **architectural_archetype** (Generator/Triage/Validator/Orchestrator/Swarm/Reactive/Skill_package) con validaciones específicas por arquetipo. Nueva sección **skills_imports[]** separada de tools_mcp[] (skills son paquetes reutilizables, tools son capacidades externas). Nueva sección **triggers[]** formal con D16 (conector dumb / agent smart): connector_workflow_id, idempotency_key_field, pre_dispatch_filters trivial-only, rate_limit. Nueva sección **multi_client_mode + client_resolver** para D17 (procesos embebidos, config en data — NO N flujos por cliente). Nueva sección **skill_package_metadata** con default_prompt + invocation_alias para skills ejecutables standalone vía CLI. Field **icon** opcional en template_metadata. 8 validaciones nuevas (21-28). Derivado de sesión Cowork 2026-04-29c (4 demos OpenAI Workspace Agents + observación CEO sobre voz como skill + sub-agentes + procesos embebidos multi-cliente).
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de refs legacy FB-prefijo y paths `docs/gold_samples/*` → `docs/faberloom/gold_samples/*`.


---

## SECCION E1 -- Whitelist arquetipos ejecutables Foundation Beta E1

Esta seccion complementa el schema general del manifest.
En Foundation Beta E1, el executor TIER 1 aplica whitelist estricta.

Arquetipos ejecutables E1:
  classifier:   etiqueta/routing, output decision
  validator:    verifica reglas/policy, output decision + reporte
  generator:    crea contenido nuevo, output asset
  formatter:    transforma formato de asset existente
  triage:       clasifica + ramifica + draft condicional (1 output max)
  skill_package: meta-arquetipo reutilizable, NO agente ejecutable

Arquetipos reservados E2+:
  orchestrator: state machine multi-step (E2+)
  swarm:        composicion jerarquica (E2+)
  reactive:     event-driven (E2+)

Mapeo Pack 1:
  SKILL_PROFORMA_BUILDER:   generator
  SKILL_COMPLIANCE_CHECKER: validator
  SKILL_CLIENT_SERVICE:     triage
  SKILL_HUMANIZE_COMMS:     skill_package
  SKILL_KB_AUDITOR:         validator

Regla compiler E1:
  type == agent y archetype not in whitelist --> E1_ARCHETYPE_BLOCKED
  type == skill_package y archetype != skill_package --> E1_SKILL_PACKAGE_BAD_ARCHETYPE

Ver especificacion ejecutable completa:
  ENT_FB_DECISIONES_E1_v1.md seccion D6.1

Registrado: 2026-06-24 -- auditoria Fugu Ultra + Kimi 2.7 Round 5.

---

## Estado actual del router en el código

Backend (`app/src/router/`):
- Providers soportados: openai, anthropic, google, kimi, ollama.
- `MODEL_ALLOWLIST` global con modelos permitidos por proveedor.
- `ProviderConfigStore` guarda API keys por workspace en SQLite.
- `Router` hace fallback por prioridad cuando un provider falla.
- `CompletionRequest` lleva `spent_usd` para budget cap acumulado; `BudgetExceeded` si se pasa `SPACELOOM_BUDGET_CAP_USD`.
- Cada completion guarda `usage_record` con costo, tokens, modelo, proveedor.
- Endpoint `GET /workspaces/{id}/router/status` devuelve presupuesto usado/disponible y estado de providers.

Frontend (`app/static/js/app.jsx`):
- Topbar muestra un budget chip con barra de progreso (llena a `GET /router/status`).
- SettingsView permite configurar API keys, modelo default, prioridad, habilitar/deshabilitar providers.
- Composer y ToolsetPanel permiten elegir provider:model override.
- SpaceLoom chat envía mensajes y muestra respuestas, pero NO muestra qué modelo/proveedor se usó ni el costo del mensaje.

Falta percibida:
- En el chat no se ve el modelo/proveedor elegido ni el costo.
- No hay indicador de fallback activo ni razón de rechazo de provider.
- No hay opción visible para "usar Ollama local" fácilmente.
- No hay presupuesto por workspace (solo global).
- No hay presets de ruteo con nombre (solo provider/model overrides crudos).

Solicito tu veredicto.
