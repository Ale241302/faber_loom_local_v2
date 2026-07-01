---
id: POL_FABERLOOM_SURFACE_CONTRACT
version: 0.2
status: DRAFT
visibility: [INTERNAL]
domain: faberloom
owner: product/design
canonical_after_review: true
created: 2026-05-04
updated: 2026-05-17
references:
  - SHELL_FABERLOOM_CHROME_V2 (faberloom_shell_chrome_v2.html)
  - faberloom_shell_consolidated_v2_2026-05-07 (mockup posterior con naming actualizado)
  - ARCH_AGENT_PRINCIPLES.md
  - ARCH P5, P7, P11, P12, P14
---

# POL_FABERLOOM_SURFACE_CONTRACT v0.2 DRAFT

## NOTA DE ALINEACION NAMING (v0.2 - 2026-05-17)

Este POL fue redactado 2026-05-04 con naming "Workspace" para la mecanica universal de chat
contra KB. El mockup `faberloom_shell_consolidated_v2_2026-05-07` (3 dias posterior) renombro
esa mecanica a **SpaceLoom** dentro de la familia *Loom (FaberLoom / WorkLoom / SpaceLoom / StackLoom).

**Equivalencia para efectos de este POL:**

| Nombre en este POL (v0.1/v0.2) | Nombre en shell consolidated v2 | Funcion |
|---|---|---|
| Workspace (cuando se refiere a chat universal) | **SpaceLoom** | Mecanica universal de hablar con la IA, scopeable |
| Workspace (cuando se refiere a contenedor de cliente/tema) | **Workspace** (igual) | Contenedor por tema/cliente/proyecto con tabs |
| GlobalChatTrigger "Ask F*" | mismo (sin renombrar) | Trigger global que abre SpaceLoom con context pack |

El v0.3 futuro alineara el cuerpo del POL al naming SpaceLoom donde aplica. Hasta entonces,
toda referencia a "Workspace" en secciones 3.1, 4.3 y 4.4 debe leerse como **SpaceLoom** si
el contexto operativo es "chat contra KB", o como **Workspace** si el contexto es "contenedor
de cliente/proyecto".

Drift documentado en AUDIT_NEXOS_AI_DELTAS_v1_1 seccion 4 drift #2.

---

## 1. Proposito

Definir el contrato obligatorio que toda pantalla (surface) de Faber*loom debe
cumplir para garantizar consistencia operativa entre superficies sin que el
shell/chrome imponga el layout interno de cada pantalla (P12).

El shell provee primitivas universales. Este POL define:
- Que primitivas existen y como invocarlas.
- Que debe declarar cada surface al registrarse.
- Que excepciones se permiten y bajo que condiciones.

Regla raiz:
  Shell provee primitivas universales.
  Surface Contract obliga consistencia.
  Cada pantalla implementa significado especifico.

## 2. Scope

### Aplica a
Toda pantalla listada en SHELL v2/v2.1, incluyendo (no exhaustivo):
Mesa, Inbox, Workspace, Cotizacion, Knowledge, Agent Factory, Skill Arena,
Routing, Voice Profile, Canales, Dashboard, Audit, Bandeja, Unit Economics,
Usuarios, Settings, IA & Keys, Pricing.

### No aplica a
- Modales transaccionales (login, error fatal, onboarding stepper).
- Embeds externos sin chrome de shell.
- Documentos exportados (PDF, evidence bundle final).

## 3. Primitivas universales del shell

El shell expone las siguientes primitivas. Cada surface las consume; ninguna
las re-implementa.

### 3.1 GlobalChatTrigger
- Acceso global a Workspace [= SpaceLoom en naming shell consolidated v2] desde topbar y CmdK.
- Label desktop: "Ask F*"
- Label mobile: icono sparkle/chat
- Accion: workspace.open_with_context({ surface, object_id, scope })
- Comportamiento si el usuario YA esta en Workspace [= SpaceLoom]:
  crea nueva conversacion con context pack del objeto activo.
  NO reemplaza la conversacion actual.
  NO hace branch (diferido a v3).

### 3.2 UploadSlot
- Slot universal visible en chrome.
- Desktop: topbar o Context Dock cuando hay conversacion activa.
- Mobile: bottom sheet composer/tools.
- Cada surface declara su comportamiento (ver seccion 4.2).
- Evento: shell.upload.open

### 3.3 Context Controls
- KB Global ON/OFF, scope, participantes y fuentes activas.
- Estado vive en shell: conversation_context.
- KB Global ON/OFF se renderiza junto al reloj contextual en topbar
  (misma altura, hermano visual del reloj).
- Scope/participantes accesibles desde Context Dock + boton Contexto del right rail.
- Prohibido enterrar KB Global solo dentro de canvas.

### 3.4 ContextualClock
- Reloj del contexto activo, no global.
- Mapeo de colores canonico:
  - salvia  -> verde    (0-34%)
  - amber   -> amarillo (35-59%)
  - coral   -> naranja  (60-81%)
  - vino    -> rojo     (82-100%)
- Click abre Aprendizaje drawer con desglose global.

### 3.5 RightTools (mano derecha)
- Right rail desktop con tools contextuales.
- Mobile: NO desaparece. Se transforma en bottom dock/bottom sheet.
- Tabs canonicas: Tools, Context, Skills, Agents, Knowledge, Routing,
  Processes, Learning.

### 3.6 ActionFooter
- Primitiva reusable de acciones mutativas.
- Firma:
    <ActionFooter variant="footer|inline|toolbar" actions=[...] />
- Variantes:
  - footer:  drawer y modal (pie del panel)
  - inline:  por fila (Bandeja, listas de candidates)
  - toolbar: compacto en topbar contextual
- Action sets canonicos:
  - default:    [Cerrar, Usar]
  - governance: [Aprobar, Descartar, Iterar en Workspace]
- Prohibido inventar botones equivalentes fuera de esta primitiva.

### 3.7 RoleDisclosure
- Items inaccesibles por rol: visibles disabled con tooltip "Requiere ROL_X".
- Excepcion mobile bottom dock: filtrar por rol (ver 4.5).
- Prohibido display:none por rol salvo excepcion mobile declarada.

### 3.8 MobileToolsSheet
- Bottom dock fijo con max 5 slots filtrados por rol.
- Slot Tools abre bottom sheet con las tabs de RightTools.
- Slot Context abre Context Dock como sheet.

### 3.9 Telemetria
Eventos minimos que toda surface emite via shell:
- shell.surface.enter        { surface_id, entity_id?, role }
- shell.surface.exit         { surface_id, duration_ms }
- shell.upload.open          { surface_id, types_offered }
- shell.action_footer.click  { surface_id, action_id, variant }
- shell.global_chat.open     { surface_id, object_id?, scope }

## 4. Surface Contract: declaraciones obligatorias por pantalla

Toda surface DEBE declarar al registrarse en el shell:

### 4.1 surface_mode_tabs
Slot canonico para surfaces que ofrecen Configurar / Iterar / Sanidad.
Surfaces obligadas a usarlo: Agent Factory, Skill Arena, Voice Profile, Canales.
- Tabs por defecto: ["Configurar", "Iterar", "Sanidad"]
- Copy y permisos por tab los define la surface.
- Posicion canonica: bajo topbar contextual, sobre el canvas.

### 4.2 upload_slot
Cada surface declara:
- accepted_upload_types: array de mime/extension
- upload_destination: enum
    workspace_attachment | kb_candidate | mesa_evidence | agent_input | none
- upload_action: enum
    parse | classify | store | link_to_case | attach_to_sandbox | composite

Ejemplos canonicos:

| Surface        | accepted_upload_types       | upload_destination    | upload_action             |
|----------------|-----------------------------|-----------------------|---------------------------|
| Workspace      | *                           | workspace_attachment  | classify                  |
| Knowledge      | pdf, docx, md, csv, xlsx    | kb_candidate          | parse + classify          |
| Mesa           | pdf, png, jpg, eml          | mesa_evidence         | store + link_to_case      |
| Agent Factory  | json, yaml, csv             | agent_input           | parse + attach_to_sandbox |
| Skill Arena    | json, py, md                | agent_input           | parse + attach_to_sandbox |
| Cotizacion     | pdf, xlsx, csv              | workspace_attachment  | parse + classify          |
| Inbox          | derivado (no upload propio) | none                  | n/a                       |
| Dashboard      | none                        | none                  | n/a                       |
| Pricing        | none                        | none                  | n/a                       |

### 4.3 context_pack
Cada surface declara que entrega cuando el usuario invoca GlobalChatTrigger.
Estructura minima:
- object_id
- object_type
- snapshot (resumen ejecutivo serializable)
- relevant_kb_refs: array opcional
- relevant_agents:  array opcional

### 4.4 context_dock
Cada surface declara que chips muestra en Context Dock cuando esta activa:
- scope (heredado del shell)
- participantes (agentes, KB sources)
- chips de accion rapida (max 3)
- chips de toggle (KB global, etc - heredados del shell)

### 4.5 mobile_tools_sheet
Cada surface declara:
- mobile_dock_visible: boolean (si aparece en bottom dock)
- mobile_dock_min_role: rol minimo (filtra por rol; excepcion P7 declarada)
- mobile_tools_tabs:   subset de RightTools relevantes para mobile

### 4.6 action_footer
Cada surface declara para cada interaccion mutativa:
- variant:    footer | inline | toolbar
- action_set: default | governance | custom (requiere justificacion en docstring)
- placement:  drawer | modal | row | topbar

### 4.7 role_matrix
Cada surface declara matriz de permisos compatible con la matriz global del shell.
No puede otorgar permisos por encima del rol; puede restringir mas.

### 4.8 telemetry_extras
Eventos custom de la surface, prefijados con surface_id.
Ejemplo: workspace.classify.click, kb.candidate.promote.click

## 5. Reglas inquebrantables

R1. Ninguna surface implementa upload propio fuera del UploadSlot del shell.
R2. Ninguna surface implementa botones de aprobacion fuera de ActionFooter.
R3. Ninguna surface esconde items por rol via display:none (salvo MobileToolsSheet).
R4. Ninguna surface duplica el GlobalChatTrigger ni inventa "asistente local".
R5. Ninguna surface mueve KB Global ON/OFF fuera del topbar.
R6. Toda surface registra context_pack aunque no soporte iteracion (pack vacio valido).
R7. Toda surface declara mobile_dock_visible aunque sea false.

## 6. Excepciones permitidas

E1. Modales transaccionales (login, fatal error) pueden omitir ActionFooter
    si solo tienen una accion no reversible.
E2. Pantallas de onboarding pueden omitir context_pack en pasos pre-tenant.
E3. Mobile puede filtrar por rol (no disabled) por restriccion de espacio,
    declarando explicitamente la excepcion en mobile_dock_min_role.

## 7. Referencias

- SHELL_FABERLOOM_CHROME_V2 (faberloom_shell_chrome_v2.html)
- SHELL_FABERLOOM_CHROME v2.1 (a crearse, debe referenciar este POL en su header)
- faberloom_shell_consolidated_v2_2026-05-07 (mockup posterior con naming SpaceLoom)
- ARCH_AGENT_PRINCIPLES.md
  - P5  Affordance
  - P7  Role disclosure
  - P11 Muscle protection
  - P12 Mode collision
  - P14 Navigation buried
- POL_DATA_CLASSIFICATION (para upload_action de KB)
- SPEC_ACTION_ENGINE (para ActionFooter governance variant)

## 8. Open questions (para review CEO)

OQ1. context_pack: tamano maximo serializable y politica de truncamiento.
     Propuesta: 8KB JSON, truncar relevant_kb_refs primero.

OQ2. mobile_tools_sheet: orden canonico de tabs en bottom sheet.
     Propuesta: Tools, Context, Knowledge, Agents (4 max).

OQ3. ActionFooter "Iterar en Workspace" en variant inline (Bandeja por fila).
     Propuesta: solo footer/toolbar lo soportan; inline omite "Iterar".

OQ4. UploadSlot en pantallas sin upload util (Dashboard, Pricing).
     Propuesta: declarar upload_destination=none y ocultar el boton (no slot vacio).

OQ5. canonical_after_review: que rol firma para promover a VIGENTE.
     Propuesta: CEO + Product/Design lead.

OQ6 (v0.2). Alineacion completa naming Workspace -> SpaceLoom: hacer en v0.3 o
     mantener alias permanente? Propuesta: v0.3 reescribe cuerpo con SpaceLoom
     y mantiene Workspace solo para contenedor cliente/tema.

## 9. Changelog

| Version | Fecha       | Autor           | Cambio                              |
|---------|-------------|-----------------|-------------------------------------|
| 0.1     | 2026-05-04  | product/design  | DRAFT inicial post sesion shell v2  |
| 0.2     | 2026-05-17  | Cowork (Claude) | Nota alineacion naming Workspace = SpaceLoom (shell consolidated v2 posterior). Tabla equivalencia explicita. Cuerpo sin cambios; alias documentado en bloque inicial + 3.1 y 4.x referencias. OQ6 agregada. Drift documentado en AUDIT_NEXOS_AI_DELTAS_v1_1 seccion 4 drift #2 |
