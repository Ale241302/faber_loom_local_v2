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
relacionado: SPEC_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_SELFHOSTED_v1.1.md - SPEC_SPACELOOM_SELFHOSTED_v1.2.md - SPEC_SPACELOOM_SELFHOSTED_v1.3.md - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md - SPEC_FB_E0_5_VALIDATION_SLICE_v1.md - IDX_SPACELOOM_ETAPA1_v1.md - PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT_v1.md

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
