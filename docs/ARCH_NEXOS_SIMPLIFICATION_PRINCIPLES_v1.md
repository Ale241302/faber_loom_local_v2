---
id: ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: ARQUITECTURA_FUNDACIONAL
type: ARCH
date: 2026-05-17
source: destilacion de nexos.ai (workspace.nexos.ai trial)
related: AUDIT_NEXOS_AI_DELTAS_v1
---

# ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1 - Principios de simplificacion destilados

## Proposito

nexos.ai se siente notablemente mas simple que las UIs tipicas de plataformas de IA enterprise. Este documento destila las 8 decisiones de diseno concretas que producen esa simplicidad - **principios transferibles a MWT/FaberLoom**, no features a copiar.

Distincion clave: hay dos clases de complejidad y MWT las tiene mezcladas:

- **Complejidad estructural** (taxonomia 8 tipos, visibility 4 niveles, headers obligatorios, hooks fail-closed, manifest selectivo). Es necesaria, legitima, no se simplifica.
- **Complejidad de configuracion expuesta al usuario** (frontmatter visible en cada edicion, sliders numericos, matrices de toggles, formularios bloqueantes, vocabulario parametrico). Es accidental, evitable, **es lo que nexos resuelve elegantemente**.

Este documento codifica los principios para reducir la segunda sin tocar la primera.

---

## Los 8 principios

### P1. Progressive disclosure

**Que hace nexos**: el Studio panel lateral no existe hasta que el usuario empieza a crear algo. Settings se abre cuando se pide. Conversation starters aparecen solo si se agregan. Integrations se listan solo si hay modelo seleccionado.

**Principio**: nada se ve hasta que el contexto operativo lo demanda. Default = invisible. Invocacion explicita = visible.

**Aplicacion MWT/FaberLoom**:
- El frontmatter de 5+ campos obligatorios no debe ser visible al autor en cada edicion.
- El sistema infiere lo inferible: `domain` por path, `version` auto-semver, `status: DRAFT` por default.
- Solo se pregunta al humano lo que requiere decision genuina (visibility CEO-ONLY vs otra, status DRAFT vs VIGENTE en promotion).
- En FaberLoom UI: tabs Configurar/Iterar/Sanidad aparecen contextualmente, no siempre.

---

### P2. Vocabulario semantico, no parametrico

**Que hace nexos**: "Grounded / Guided / Balanced / Analytical / Creative" en vez de slider de temperatura 0.0-1.0. "Schedule" en vez de cron expression. "Prompt | Schedule" como execution trigger en vez de tipo MIME de evento.

**Principio**: el usuario decide intencion, no parametro. El sistema traduce semantica a numeros internamente.

**Aplicacion MWT/FaberLoom**:
- Fabricante FaberLoom NO toca `temperature`, `top_p`, `context_window`, `max_tokens`. Toca "que tan estricto" (Grounded..Creative) y "que tan rapido" (Inmediato/Programado).
- En POL_GROUNDING_POLICY usar los 5 niveles nexos como vocabulary canonico (Grounded/Guided/Balanced/Analytical/Creative). Aplica a todo skill y agent.
- Cualquier control que aparezca con slider numerico es candidato a reformularse como preset semantico de 3-5 opciones.

---

### P3. Conceptos pocos y profundos

**Que hace nexos**: dos primitivas - **Agent** y **Project** - operan todo el modelo mental. Files, Integrations, Capabilities, Conversation starters son atributos colgados de esas dos. No hay tipos de objetos primitivos adicionales.

**Principio**: pocos conceptos, cada uno con muchos atributos. Mejor 2 entidades con 10 campos cada una que 10 entidades con 2 campos cada una.

**Aplicacion MWT/FaberLoom**:
- Backend MWT mantiene los 8 tipos de taxonomia (ENT/PLB/SCH/LOC/POL/IDX/LOTE_SM_SPRINT/SKILL + especiales). Es necesario para integridad de la KB y para gobernanza.
- Usuario FaberLoom NUNCA ve los 8 tipos. Para el existen 3 conceptos: **agentes** (lo que hace), **conocimiento** (lo que sabe), **politicas** (lo que no puede hacer). Punto.
- La taxonomia interna mapea a esos 3: SKILL+PLB -> agentes; ENT+SCH+LOC -> conocimiento; POL+IDX -> politicas. El usuario nunca cruza esa frontera.

---

### P4. Defaults responsables, override visible cuando importa

**Que hace nexos**: Auto model selector (deja al sistema escoger). Balanced creativity. Capabilities desactivadas por default (Web search OFF, Knowledge base OFF). El usuario configura solo si tiene motivo.

**Principio**: el sistema toma decisiones razonables por el usuario. El usuario sobreescribe explicitamente cuando le importa. El override es siempre visible (no oculto en un settings menu) pero no obligatorio.

**Aplicacion MWT/FaberLoom**:
- `visibility: INTERNAL` es default implicito. El control en UI solo aparece si el autor quiere subirla (CEO-ONLY) o bajarla (PUBLIC/PARTNER_B2B).
- `grounding_policy: Guided` es default para todo skill no-frozen. Override explicito solo para Grounded (FROZEN, POL_) o Creative (marketing copy).
- `model_primary: <tier>` infiere fallback chain por POL desde SPEC_LLM_GATEWAY_FALLBACK. El skill no la repite.
- `version` y `changelog` auto-incrementan en cada sync; el autor no los toca.

---

### P5. Asistencia inline, no documental

**Que hace nexos**: suggestion chips dentro del editor mientras escribis ("Add brand voice customization", "Tighten response instructions", "Switch to creative mode"). "Generate with AI" boton sobre el campo Instructions autocompleta system prompt. Help text de 1 linea inline bajo cada label.

**Principio**: el sistema susurra. No te manda a leer documentacion. La ayuda aparece donde estas trabajando, en el momento exacto en que la necesitas.

**Aplicacion MWT/FaberLoom**:
- Mientras se edita un PLB_ o SKILL_, el sistema susurra: "te falta declarar `grounding_policy`", "tu instructions cita un dato sin fuente", "no declaraste `conversation_starters`", "tu `domain` no coincide con el path del archivo".
- NO crear documentos WIKI separados de "como editar un PLB". El conocimiento vive como prompts del autoring agent, no como prosa estatica.
- POL/SPEC pueden seguir existiendo como referencia formal, pero el flujo de autoring no los lee - los aplica via susurro contextual.

---

### P6. Una decision = un control

**Que hace nexos**: capabilities = 2 toggles binarios (Web search, Knowledge base). Permisos = "Shared with you / Created by you" (binario). Trigger = Prompt | Schedule (radio de 2). No hay matrices de checkboxes ni grids de role x resource.

**Principio**: si una funcionalidad requiere matrix de N x M checkboxes, la abstraccion esta mal. Probablemente la decision real es UNA (que tier? que visibilidad? que aprobacion?) y la matrix es artefacto de implementacion, no de pensamiento.

**Aplicacion MWT/FaberLoom**:
- En lugar de "rol x recurso x tenant" como matrix, una lista plana de switches por tenant que el admin recorre linealmente.
- En lugar de "que tools puede usar el agente X en tenant Y bajo policy Z", una sola pregunta: "que tier?". El tier infiere todo lo demas.
- Reformular cada feature con matrices visibles antes de implementarla.

---

### P7. Estado fluido, no formulario bloqueante

**Que hace nexos**: creas un agent draft sin nombre, sin modelo, sin instructions. Esta en "Discard draft" state. El boton Save bloquea al final si faltan campos required (Name, Model). Discard limpia y volves.

**Principio**: el sistema permite trabajar incompleto. Los gates aparecen en momentos de promocion, no de edicion. La iteracion no esta bloqueada por validacion.

**Aplicacion MWT/FaberLoom**:
- Headers obligatorios MWT NO bloquean creacion en `generated_staging/`. Un archivo puede vivir ahi sin frontmatter completo.
- El gate de validacion aparece **al promover de generated_staging a docs/** (en sync_*_indexa.ps1, no en Cowork).
- Edicion en Cowork = libre. Promocion = estricta. Hoy MWT mezcla las dos.

---

### P8. Composicion por referencia, no por configuracion explicita

**Que hace nexos**: invocas otro agente con `@nombre` en chat. No hay grafo declarativo de orquestacion visible (excepto el Flow narrativo opcional dentro de un agente). Los agents componen runtime.

**Principio**: las relaciones entre componentes se declaran en el componente, no en un orchestrator central. El grafo emerge de las declaraciones, no se construye top-down.

**Aplicacion MWT/FaberLoom**:
- En lugar de PLB_ORCHESTRATOR centralizado (que es FROZEN y por buena razon), considerar que cada SKILL declare `composes_with: [SKILL_X, SKILL_Y]` en su frontmatter.
- El orchestrator se deriva de las declaraciones (vista computada, no archivo escrito a mano).
- Beneficio: agregar un SKILL nuevo no requiere editar el orchestrator. La extension es local.
- Constraint: este principio NO toca PLB_ORCHESTRATOR (FROZEN). Aplica solo a nuevos patrones de composicion entre skills no-FROZEN.

---

## Complejidad MWT que NO se debe simplificar

Tres areas donde "ser simple como nexos" es deuda disfrazada y MWT debe mantener su rigor:

| Area | Por que MWT mantiene complejidad |
|------|----------------------------------|
| **Visibility per-archivo (4 niveles)** | B2B distribuidor Marluvas != CEO. Modelo de negocio MWT exige granularidad que nexos no soporta. Sin esto se cae el partner channel. |
| **Versioning + changelog auditado** | Fabricantes B2B piden trazabilidad de "que version de prompt aprobamos vs que se ejecuto". nexos no la expone; MWT la necesita visible. |
| **Hooks fail-closed + manifest selectivo + sync con git** | Auditoria regulatoria exige integridad demostrable, no "trust the platform". nexos modelo = RBAC simple; MWT modelo = append-only audited. Son diferentes contratos. |

## Reglas de aplicacion

1. **Antes de agregar un nuevo control a UI MWT/FaberLoom**, validar contra los 8 principios. Si rompe alguno, replantear.
2. **Cuando un control parezca "necesariamente complejo"**, preguntar si es complejidad estructural (mantener) o de configuracion expuesta (simplificar via principios).
3. **Los 5 niveles de creativity** (Grounded/Guided/Balanced/Analytical/Creative) son vocabulario canonico MWT. Usar igual en todos los contextos. No inventar sinonimos.
4. **Generated_staging es el playground**. Headers se relajan ahi. Gate estricto solo en promotion.
5. **Backend MWT mantiene los 8 tipos**. Frontend FaberLoom expone 3 conceptos (agentes, conocimiento, politicas). El mapping es responsabilidad de la capa de presentacion.

## Trazabilidad

- **AUDIT_NEXOS_AI_DELTAS_v1.md** (mismo batch): investigacion completa de la plataforma con 5 deltas operativos D1-D5 y 6 casos de uso comparados.
- Este ARCH_ destila los principios de diseno; AUDIT_ propone los archivos especificos. Leer juntos.

## Changelog

- v1.0 (2026-05-17): destilacion inicial de 8 principios + 3 areas no-simplificables. Fuente: navegacion directa workspace.nexos.ai trial TitanPoint7515 + sesion de discusion con CEO sobre simplificacion. Pendiente: validacion CEO sobre que principios entran a POL_ formal y cuales quedan como ARCH_ guideline.
