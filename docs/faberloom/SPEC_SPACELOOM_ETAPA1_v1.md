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
