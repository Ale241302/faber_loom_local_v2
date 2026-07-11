# SPEC_FB_WORKSPACE_v2 -- Workspace Conversacional FaberLoom
id: SPEC_FB_WORKSPACE_v2
version: 2.0
status: PROPUESTO -- pendiente aprobación CEO
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: 2026-07-11
aprobador: CEO (pendiente)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_WORKSPACE_v1.md · SPEC_QUERY_PROCESSING_PIPELINE.md · POL_VISIBILIDAD.md · E4_1_WORKSPACE_BRIEFS.md

---

## Declaracion

El Workspace es donde el usuario construye, itera y automatiza.
Distinto de WorkLoom (donde opera y aprueba).

WorkLoom = TRABAJO del dia (que tengo que hacer YO)
Workspace = SISTEMA vivo + CONSTRUCCION (como esta MI MAQUINA)

Existe solo en desktop Electron en E1.
La web app tiene Agent Factory y Skill Factory pero no Workspace.

## Cambios respecto a v1 (enmiendas E4-4)

1. **Tab "Agentes" del panel derecho se reemplaza por "Tab Agente".**
   - Muestra el estado del Agente Vivo: capacidades/skills activas, tareas en curso (link a Agent Tasks E4-3) y termómetro de aprendizaje (E4-5).
   - No permite crear ni mutar agentes; es solo lectura de estado.

2. **Se añade el "chat general del tenant"** como superficie conversacional nueva.
   - Implementado como workspace de sistema `ws-general` con `workspace.kind="tenant_general"`.
   - Responde desde índices (`workspace_brief` INDEX) de los workspaces visibles al usuario más memoria personal aprobada (E4-5).
   - Al profundizar, deriva al workspace concreto y usa la autoridad del usuario que pregunta (sin elevar privilegios).

3. **Los 3 modos se mantienen**, pero el Agente Vivo ES quien los detecta.
   - OPERACIONAL: invoca skills/capacidades.
   - AUTOMATIZACION: propone rutinas; HITL obligatorio.
   - CONSTRUCCION: detecta gaps y propone skills; HITL obligatorio.

4. **Las @menciones de agentes pasan a ser @menciones de CAPACIDADES/skills.**
   - El composer ofrece la lista de skills/rutinas activas del tenant.
   - No hay @menciones a agentes individuales.

---

## 1. Layout 3 columnas

COL IZQ: conversaciones recientes + [+ Nueva conv]
COL CENTRO: welcome compacto + stream + composer fijo + patrones
COL DER: Tab Agente / Tab Skills / Tab Aprendizaje / Contexto activo

Composer fijo: [+ Archivo] [+ Knowledge] [@mencion] [Modo] [Enviar]
Atajos: A=aprobar E=editar R=regenerar I=info S=escalar D=descartar

Breakpoints Electron:
  >= 1400px: 3 columnas full
  1100-1399px: col izq como drawer FAB
  < 1100px: ambas laterales como drawers

---

## 2. Chat general del tenant

### 2.1 Superficie
- Entrada fija arriba del rail: `"— {display_name_agente}"`.
- Al seleccionarla, el workspace activo pasa a ser `ws-general`.
- El composer y el stream usan los mismos endpoints `/api/workspaces/{ws}/chats/...`.

### 2.2 Comportamiento
- **Nivel general (INDEX):** responde qué hay en los workspaces usando `workspace_brief`.
  - Sin fuente → "No lo sé; ¿quieres que entre al workspace X?".
  - No inventa datos. No toca CONTENT.
- **Profundización (CONTENT):** cuando el usuario pide detalle de un workspace, la pregunta se deriva al workspace objetivo con el mismo usuario/rol.
  - Key broker media. Sin acceso → negativa según POL_VISIBILIDAD.
- **Tareas:** intención de automatización va al planner/orquestador E4-3 con HITL.
- **Memoria:** inyecta bloques personales aprobados (E4-5) dentro del presupuesto de tokens.

### 2.3 Identidad
- El system prompt usa `entity_identity` (nombre, tono) + instrucciones del workspace activo.
- Display name por defecto "Faber"; editable solo vía flujo de identidad E3-3 (owner distinto + token).

---

## 3. Los 3 modos (deteccion automatica por el Agente Vivo)

### Modo 1 -- OPERACIONAL

Trigger: usuario invoca skills existentes para tarea inmediata.
Senales: @skill + verbo, pregunta directa, solicitud inmediata.
Resultado: skills en secuencia lineal, output a WorkLoom si HITL requerido.
Working memory: se descarta al cerrar la conversacion.
NO crea skills ni rutinas.

### Modo 2 -- AUTOMATIZACION

Trigger: usuario describe algo que quiere automatico.
Senales: cuando llegue, cada dia, automaticamente, avisame si.
Resultado: propuesta de rutina --> SANDBOX --> Owner aprueba --> ACTIVE.
Ver SPEC_FB_ROUTINES_v1 para flujo completo.

### Modo 3 -- CONSTRUCCION

Trigger: sistema detecta gap (tarea sin skill, flujo sin automatizar).
Resultado: propuesta de skill nuevo con AgentSpec pre-completado.
Skill --> shadow --> Skill Factory --> Owner aprueba --> active.

Restricciones TIER 1 modos 2 y 3:
  HITL absoluto: nada va a PROD sin firma Owner/Admin
  Single-skill por task: skills nuevos son atomicos
  Sandbox obligatorio antes de promote
  Audit log con actor_role_at_decision

---

## 4. Panel derecho -- 4 tabs

### Tab Agente
Estado del Agente Vivo:
  - Capacidades/skills activas (lista, no editable).
  - Tareas en curso con link a Agent Tasks (E4-3).
  - Termómetro de aprendizaje (E4-5) con link al modal de indexación.

### Tab Skills
SEALED (FaberLoom, con candado): no editables
CUSTOM (tenant): editables en Skill Factory / Fábrica de skills
Por skill: nombre, archetype, estado, autonomy_ceiling, thermometer

### Tab Aprendizaje
Gold samples candidatos con [Aprobar y guardar] [Mantener] [Descartar]
Reglas candidatas con [Activar] [Mantener] [Descartar]
Estado: 78/100 -- Produccion sin cambios recientes

### Contexto activo (fijo abajo)
Knowledge: kb_marluvas v2.3 -- 18.4k -> 5.8k (68% cache)
Caso activo: RFQ Sondel #4521 (si hay uno abierto)
Freshness: precios vigentes hasta 2026-07-01
Tokens: 5.8k / 50k budget
[Ver contexto completo] --> drawer con 6 secciones

---

## 5. Navegación rail

- **— {display_name_agente}** → chat general del tenant (ws-general).
- **FaberLoom** → chat del workspace operativo seleccionado.
- **Inbox, WorkLoom, StackLoom, KB, Gold** (sin cambios).
- **Admin → Capacidades**
  - **Fábrica de skills** (antes "Agentes"): solo curador/owner/admin. CRUD de skills/rutinas.
  - Skills (si se mantiene separado).

---

## 6. Inbound activo usuario (tipos 12-13)

Tipo 12 -- Upload archivo:
  Formatos: PDF, DOCX, XLSX, CSV, TXT, PNG, JPG
  Max: 10MB por archivo, 50MB por sesion
  Path MinIO: /tenants/{tenant_id}/uploads/
  Flujo: archivo --> L1 clasifica data_class --> feed.item.received
  Si N3/N4: hard gate D9, no sale a providers sin DPA

Tipo 13 -- Inicio de tarea:
  Usuario escribe o arrastra --> task (invocation_mode=ad_hoc)
  WorkLoom si requires_human_gate=true
  Ejecucion directa si autonomy_ceiling lo permite

---

## 7. SpaceLoom en E1

No es espacio separado en E1.
Existe como boton [Pensar con IA] en cards de casos complejos WorkLoom.
Abre panel lateral en Workspace con contexto del caso pre-cargado.
Output: instruccion al agente --> WorkLoom como draft listo.

Post-beta: si >40% de casos usan este modo, SpaceLoom se convierte
en espacio propio con persistencia de sesiones.

---

## 8. Working memory

Se crea al abrir conversacion, contiene contexto + historial + skills.
Se descarta al cerrar (sin gate humano nunca va a Persistent memory).
Timeout: 24h sin actividad --> descarte automatico.

---

## 9. Conversaciones recientes

Ultimas 30 por usuario por tenant.
Nombre auto-generado del primer mensaje.
Indicador de modo + tipo de output producido.

---
Changelog:
- v2.0 (2026-07-11): Enmiendas E4-4. Tab Agentes → Tab Agente. Chat general del tenant (ws-general). @menciones de capacidades/skills. Agente Vivo detecta los 3 modos. Estado PROPUESTO.
- v1.0 (2026-06-24): Creacion. Layout 3 columnas. 3 modos. Panel derecho 4 tabs. Inbound 12-13. SpaceLoom E1.
  Cubre gap G2. Alineado con ENT_FB_DECISIONES_E1_v1 D4.
