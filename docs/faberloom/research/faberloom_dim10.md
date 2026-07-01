# Dimension 10: Action Flow — Approval Flows y Human-in-the-Loop Patterns

## Investigacion para FaberLoom
**Fecha:** Junio 2026
**Enfoque:** Patrones de aprobacion human-in-the-loop en sistemas con agentes IA
**Objetivo:** Disenar el flujo optimo para los 3 botones de aprobacion de FaberLoom: APROBAR / DESCARTAR / ITERAR

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Approval Gates: Cuando Pausar para Aprobacion](#2-approval-gates-cuando-pausar-para-aprobacion)
3. [3-Action Pattern (Approve/Discard/Iterate)](#3-3-action-pattern-approvediscarditerate)
4. [Confidence Routing](#4-confidence-routing)
5. [Undo/Redo en Aprobaciones](#5-undoredo-en-aprobaciones)
6. [Batch Approvals](#6-batch-approvals)
7. [Approval History y Audit Trail](#7-approval-history-y-audit-trail)
8. [Escalation y Timeouts](#8-escalation-y-timeouts)
9. [Differential Previews](#9-differential-previews)
10. [Catalogo de Patterns: Evaluacion FaberLoom Fit](#10-catalogo-de-patterns-evaluacion-faberloom-fit)
11. [Gaps Identificados](#11-gaps-identificados)
12. [Recomendaciones Especificas](#12-recomendaciones-especificas)
13. [Bibliografia y Fuentes](#13-bibliografia-y-fuentes)

---

## 1. Resumen Ejecutivo

- **El patron 3-action (approve/discard/iterate) es estandar emergente** en herramientas de IA generativa de codigo/UI: VS Code Copilot (Keep/Undo), Cursor (Accept/Reject), Tiptap AI (accept/reject), Dagu workflows (Approve/Retry/Reject), e inference.sh (Approve/Reject/Modify). La triada APROBAR/DESCARTAR/ITERAR de FaberLoom se alinea directamente con esta convencion.
- **Los approval gates deben ubicarse antes de la ejecucion para acciones irreversibles** y despues para acciones reversibles. El framework de 3 checkpoints (Plan Gate → Findings Gate → Diff Gate) es el patron de consola para agentes de codigo [^662^].
- **Confidence routing con umbrales graduales** es un patron de produccion validado: auto-approve >90%, human review 70-90%, auto-reject <20%. Los umbrales deben calibrarse empiricamente, no asumirse [^614^][^610^].
- **Undo/Redo es no negociable** para sistemas de generacion de UI: VS Code, Cursor, Bolt.new, y Zed ofrecen mecanismos de rollback. Bolt.new tiene version history nativo; Cursor usa checkpoints automaticos [^622^][^736^].
- **Los audit trails inmutables** son requisito para cualquier sistema enterprise: hash chaining + Merkle trees + tiered storage es el estandar arquitectonico [^645^].
- **Escalation por timeout** con fallback configurable: el estandar emergente es ESCALATE.md, que define notificacion, timeout, y fallback (deny/killswitch) [^641^].

---

## 2. Approval Gates: Cuando Pausar para Aprobacion

### 2.1 Framework de 3 Checkpoints (Plan → Findings → Diff)

Claim: La investigacion identifica tres gates minimos efectivos para agentes de IA: (1) Plan review gate antes de tocar archivos, (2) Findings review gate despues de explorar pero antes de cambiar, (3) Diff-before-push gate despues de implementar pero antes de commitear. [^662^]
Source: Code on Grass — Where to Gate Your AI Coding Agent
URL: https://codeongrass.com/blog/where-to-gate-your-ai-coding-agent-3-checkpoint-framework/
Date: 2026-05-04
Excerpt: "Three gates cover the majority of meaningful risk without meaningful overhead: 1. Plan review gate — approve the agent's approach before it touches any files; 2. Findings review gate — confirm what the agent discovered before it acts on it; 3. Diff-before-push gate — inspect the full diff before any code leaves your machine."
Context: Este framework es tool-agnosotico y aplica a Claude Code, Codex, y cualquier agente. Los gates responden preguntas diferentes en momentos distintos.
Confidence: high

### 2.2 Decision Flowchart: Que Patron Usar

Claim: No toda accion necesita el mismo nivel de oversight. Si la accion es irreversible o alto blast-radius → pre-execution approval gate. Si es rutinaria con casos limite → exception-based escalation. Si es un agente nuevo o se necesita construir confianza → graduated autonomy. [^663^]
Source: Cordum — Human-in-the-Loop AI: 5 Production Patterns
URL: https://cordum.io/blog/human-in-the-loop-ai-patterns
Date: 2026-04-01
Excerpt: "Q1: Is the action irreversible or high-blast-radius? Yes → Pattern 1: Pre-execution approval gate. Q2: Is this routine with occasional edge cases? Yes → Pattern 2: Exception-based escalation. Q3: New agent or domain where you need to build trust? Yes → Pattern 3: Graduated autonomy."
Context: La mayoria de los sistemas de produccion combinan 2-3 patrones. Pre-execution gates + output review es el baseline mas comun.
Confidence: high

### 2.3 Plan-and-Execute como Patron UI

Claim: El patron plan-and-execute muestra al usuario un plan de accion propuesto antes de que el agente comience a trabajar. El usuario aprueba el plan completo, modifica pasos individuales, o elimina pasos antes de que comience la ejecucion. [^619^]
Source: FuseLab Creative — Agent UX: Designing UI for AI agents in 2026
URL: https://fuselabcreative.com/ui-design-for-ai-agents/
Date: 2025-08-28
Excerpt: "Plan-and-execute shows the user a proposed action plan before the agent begins working. During execution, completed steps show a checkmark while the active step pulses with a progress indicator. Any upcoming step can still be edited or removed even after execution has started."
Context: Validado en produccion enterprise. Sin este preview, cada accion autonoma se siente como una sorpresa no consentida.
Confidence: high

### 2.4 FaberLoom Implication

Para FaberLoom, que genera propuestas de UI, el **Plan review gate** seria: mostrar la propuesta generada en modo preview (no aplicada) con los 3 botones APROBAR/DESCARTAR/ITERAR visibles. La accion solo se ejecuta despues de la aprobacion explicita. Esto es consistente con el patron de pre-execution approval gate.

---

## 3. 3-Action Pattern (Approve/Discard/Iterate)

### 3.1 Evidencia del Patron Triada en Productos

**VS Code Copilot Chat (Keep/Undo):**
Claim: VS Code permite revisar ediciones generadas por IA individualmente o todas a la vez, con acciones Keep (aceptar), Undo (rechazar), y navegacion entre ediciones. [^678^]
Source: VS Code Docs — Review AI-generated code edits
URL: https://code.visualstudio.com/docs/copilot/chat/review-code-edits
Date: 2026-05-06
Excerpt: "For each edit, choose one of the following actions: Select Keep to accept the edit. Select Undo to reject the edit and revert the change. Hover over an inline change to accept or reject that specific change without affecting other edits in the file."
Context: Microsoft ha estandarizado este flujo para todas las ediciones de IA en VS Code. Tambien ofrecen auto-accept configurable.
Confidence: high

**Tiptap AI Suggestion (Preview/Review modes):**
Claim: Tiptap ofrece dos modos: Preview mode (cambio se preview antes de aplicar) y Review mode (cambio se revisa despues de aplicar). Los usuarios pueden accept/reject individual o todos a la vez. [^676^][^646^]
Source: Tiptap AI Toolkit — Review changes
URL: https://tiptap.dev/docs/content-ai/capabilities/ai-toolkit/agents/review-changes
Date: 2026-05-10
Excerpt: "Preview mode: The change is previewed before applying it. The document is not modified until the user accepts the suggestion. Review mode: The change is reviewed after applying it. The document has already been modified and the suggestion allows the user to undo the change."
Context: Este patron es exactamente aplicable a FaberLoom: preview mode para ver la propuesta antes de aplicar.
Confidence: high

**Dagu Workflow (Approve/Retry/Reject):**
Claim: Dagu workflows muestran botones Approve y Retry (push-back) por step, mas un boton Reject global en el action bar. Incluye contador de iteracion de aprobacion. [^710^]
Source: Dagu Docs — Approval
URL: https://docs.dagu.sh/writing-workflows/approval
Date: 2026-05-04
Excerpt: "When steps enter Waiting status, an Approval tab appears... showing each waiting step with Approve and Retry (push-back) buttons per step, plus the current approval iteration count (if pushed back). To reject all waiting steps at once, use the Reject button."
Context: El contador de iteraciones es un detalle interesante para FaberLoom: tracking de cuantas veces se ha iterado.
Confidence: high

**inference.sh (Approve/Reject/Modify):**
Claim: inference.sh implementa approval gates con tres opciones: Approve (ejecuta la accion), Reject (bloquea e informa al agente), y Modify (permite cambiar parametros antes de aprobar). [^717^]
Source: inference.sh — Tool Approval Gates
URL: https://inference.sh/blog/tools/approval-gates
Date: 2026-02-16
Excerpt: "The human has three options. Approve allows the action to proceed as proposed. Reject blocks the action and informs the agent. Modify allows changing parameters before approval."
Context: El tercer boton aqui es Modify en lugar de Iterate, pero el proposito es el mismo: dar feedback para ajustar antes de continuar.
Confidence: high

### 3.2 La Triada APROBAR / DESCARTAR / ITERAR

Claim: En sistemas de produccion SAP con agentes IA, el patron de aprobacion usa tres decisiones: approve (aprobacion total), reject (rechazo), y conditional (aprobacion con condiciones/modificaciones). [^609^]
Source: SAP Community — Human-in-the-Loop SAP Agents
URL: https://community.sap.com/t5/artificial-intelligence-blogs-posts/human-in-the-loop-sap-agents-approval-escalation-and-audit-series-2-part-5/ba-p/14372994
Date: 2026-04-13
Excerpt: "options: ['approve', 'conditional', 'reject']... if decision == 'approve': state['final_status'] = 'MIGRATION_APPROVED'; elif decision == 'conditional': state['final_status'] = 'MIGRATION_APPROVED_WITH_CONDITIONS'; else: state['final_status'] = 'MIGRATION_REJECTED'"
Context: SAP usa 3 opciones con conditional como variante de "iterar con condiciones". Para FaberLoom, ITERAR es mas propositivo que CONDITIONAL.
Confidence: high

### 3.3 Intent by Augment — Approve the Spec, Iterate the Spec

Claim: Intent usa un flujo de aprobacion del spec (documento de especificacion) antes de generar codigo. El usuario revisa, aprueba o redirige el spec; el Coordinador delega la implementacion despues. El spec es "living" — se actualiza a medida que los agentes completan trabajo. [^653^][^751^]
Source: Augment Code — Introducing Intent
URL: https://docs.augmentcode.com/intent/overview
Date: 2026-02-10
Excerpt: "The Coordinator: 1. Analyzes your codebase; 2. Drafts a Spec that serves as a living document; 3. Generates tasks for specialized agents to execute. You can stop the Coordinator at any time to manually edit the Spec."
Context: El spec como artifact central de aprobacion es un patron poderoso para FaberLoom: la propuesta de UI es el spec que se aprueba, descarta o itera.
Confidence: high

---

## 4. Confidence Routing

### 4.1 Confidence-Based Routing: El Patron de Produccion

Claim: El patron de confidence routing es: HIGH confidence (>90%) → auto-approve; MEDIUM confidence (70-90%) → human review; LOW confidence (<20%) → auto-reject. Los umbrales deben calibrarse empiricamente. [^614^]
Source: Grizzly Peak — Human-in-the-Loop Patterns for AI Agents
URL: https://www.grizzlypeaksoftware.com/library/human-in-the-loop-patterns-for-ai-agents-n64sb2cm
Date: 2026-02-13
Excerpt: "I typically set the auto-approve threshold conservatively at first — around 0.95 — and lower it gradually as the system proves reliable. The auto-reject threshold catches obvious garbage: malformed actions, hallucinated tool calls, or actions with no rational basis."
Context: Advertencia importante: los confidence scores de LLMs no son probabilidades bien calibradas. Un 90% de confidence no significa 90% de accuracy.
Confidence: high

### 4.2 Implementacion en SAP

Claim: SAP implementa confidence-based routing con reglas de negocio explicitas: auto-approve solo si LOW risk, HIGH confidence, no financial impact > 10k, no core customizing changes, standard transport route. [^609^]
Source: SAP Community — Human-in-the-Loop SAP Agents
URL: https://community.sap.com/t5/artificial-intelligence-blogs-posts/human-in-the-loop-sap-agents-approval-escalation-and-audit-series-2-part-5/ba-p/14372994
Date: 2026-04-13
Excerpt: "AUTO_APPROVE only if: LOW risk, HIGH confidence, no financial impact > 10k, no core customizing changes, standard transport route."
Context: Las reglas de auto-approval deben ser explicitas y combinadas con condiciones de negocio, no solo confidence scores.
Confidence: high

### 4.3 Confidence Signaling en la UI

Claim: Un indicador de confianza binario (alto/bajo) supera a los porcentajes numericos en testing de usuarios. Los usuarios deciden mas rapido con "estoy seguro" vs "no estoy seguro" que con "estoy 73% seguro". [^619^]
Source: FuseLab Creative — Agent UX
URL: https://fuselabcreative.com/ui-design-for-ai-agents/
Date: 2025-08-28
Excerpt: "We tested numeric percentages, color scales, and binary high-low indicators. The binary version outperformed the others because users decided faster with 'I am confident' versus 'I am not sure' than with 'I am 73% confident.'"
Context: Para FaberLoom, esto sugiere mostrar un indicador visual simple de confianza (ej: verde/amarillo/rojo) en lugar de un porcentaje.
Confidence: high

### 4.4 Calibration de Umbrales

Claim: El proceso de calibracion recomendado es: (1) empezar alto (80+), (2) trackear approval rate, (3) bajar gradualmente de 10 en 10 puntos, (4) monitorear rechazos. Un spike en rechazos significa que se fue demasiado lejos. [^746^]
Source: UserOrbit — How to configure agent confidence thresholds
URL: https://userorbit.com/help/en/how-to-configure-agent-confidence-thresholds
Date: 2026-05-06
Excerpt: "Start high (80+). Track your approval rate. If you are approving 90% or more of proposals without changes, the threshold is likely too high. Lower gradually. Drop the threshold by 10 points and observe."
Context: Proceso practico y aplicable para FaberLoom en su fase de calibracion inicial.
Confidence: high

---

## 5. Undo/Redo en Aprobaciones

### 5.1 Checkpoints en Cursor

Claim: Cursor crea checkpoints automaticos antes de cada edicion de codigo en Agent mode. Son snapshots locales, separados de Git, que solo trackean cambios del agente (no ediciones manuales). Se pueden restaurar desde el input box o desde el message history. [^622^]
Source: Steve Kinney — Understanding Cursor Checkpoints
URL: https://stevekinney.com/courses/ai-development/cursor-checkpoints
Date: 2026-03-17
Excerpt: "Checkpoints are automatically created by Cursor. Every time the Agent modifies your code, Cursor zips up the pre-change state into a checkpoint. In Agent mode, checkpoints are created before every code edit. Checkpoints are stored locally, in a hidden directory, and are separate from Git history."
Context: El mecanismo es "disposable safety net" — los checkpoints son efimeros y se limpian automaticamente.
Confidence: high

### 5.2 Version History en Bolt.new

Claim: Bolt.new ofrece version history nativo: cada cambio se guarda como una version, permitiendo comparar versiones y hacer rollback a cualquier punto anterior del proyecto. [^736^][^739^]
Source: Bolt.new Docs — Version history
URL: https://support.bolt.new/concepts/version-history-github
Date: 2026-04-07
Excerpt: "Bolt offers a built-in feature that allows you to easily switch between different saved copies (backups) of your project... Version history means being able to track changes to a file over time. Instead of saving multiple copies with different names, you can look back at previous versions, see what changed, and restore them if needed."
Context: Bolt.new recomienda usar Version History en lugar de prompts para hacer undo, ahorrando tokens.
Confidence: high

### 5.3 Undo en VS Code Copilot

Claim: VS Code permite undo individual por edicion o undo all changes across all files. Cuando se cierra VS Code, el estado de pending edits se conserva y restaura al reabrir. [^678^]
Source: VS Code Docs
URL: https://code.visualstudio.com/docs/copilot/chat/review-code-edits
Date: 2026-05-06
Excerpt: "When you close VS Code, the status of the pending edits is remembered and restored when you reopen VS Code... Alternatively, accept or reject all changes across all files at once from the Chat view."
Context: La persistencia del estado de aprobacion entre sesiones es critica para workflows enterprise.
Confidence: high

### 5.4 Rollback para FaberLoom

Claim: El patron de recovery mechanisms recomienda: Undo/Rollback button si la IA hace cambios, Audit Trail para enterprise scenarios, y activity log con opcion de revertir. [^655^]
Source: High Peaks — Designing AI UIs People Actually Trust
URL: https://highpeaksw.com/designing-ai-uis-people-actually-trust-microcopy-controls-and-recovery/
Date: 2026-04-30
Excerpt: "Undo / Rollback: If the AI makes changes (auto-formatting a document, categorizing an email), provide an 'Undo AI action' button. Users feel safer knowing they can revert with one click. Audit Trail: In enterprise scenarios, show a log: 'AI applied filter X at 3:45pm' with an option to revert."
Context: Para FaberLoom: DESCARTAR actua como undo de la propuesta (no se aplica), y si ya se aplico, debe haber un mecanismo de rollback.
Confidence: high

---

## 6. Batch Approvals

### 6.1 Patron de Batch Review

Claim: Un agente que genera 100 acciones durante la noche necesita una interfaz de revision batch, no 100 popups individuales. Se debe agrupar acciones similares y permitir aprobar/rechazar en bulk desde el dia uno. [^614^]
Source: Grizzly Peak — HITL Patterns
URL: https://www.grizzlypeaksoftware.com/library/human-in-the-loop-patterns-for-ai-agents-n64sb2cm
Date: 2026-02-13
Excerpt: "An agent that generates 100 actions overnight needs a batch review interface, not 100 individual approval popups. Group similar actions and let reviewers approve or reject in bulk."
Context: Para FaberLoom esto es menos critico en fase inicial (una propuesta a la vez), pero importante para escalar a multiples propuestas.
Confidence: medium

### 6.2 Sampled Audit at Scale

Claim: Cuando un agente maneja miles de acciones por dia, la revision completa es imposible. Sampled audit da confianza estadistica sin el cuello de botella: uniform (cada N acciones), stratified (riesgo mayor = muestreo mayor), mandatory (ciertas acciones siempre revisadas). [^663^]
Source: Cordum — HITL Patterns
URL: https://cordum.io/blog/human-in-the-loop-ai-patterns
Date: 2026-04-01
Excerpt: "Sampled audit gives statistical confidence without the bottleneck: a random subset is flagged for human review after execution. Uniform: every Nth action audited. Stratified: higher-risk sampled at higher rates. Mandatory: certain actions always reviewed."
Context: Relevante para FaberLoom en escenarios de generacion masiva de componentes UI.
Confidence: medium

---

## 7. Approval History y Audit Trail

### 7.1 Arquitectura de Audit Trail Inmutable

Claim: El patron core es hash chaining + Merkle trees + tiered storage: cada entrada de log incorpora el digest SHA-256 de la entrada anterior. Los Merkle trees permiten verificar integridad en O(log n). El root se ancla a una autoridad de timestamping. [^645^]
Source: The Bright Byte — AI Agent Audit Trail Architecture
URL: https://thebrightbyte.com/playbook/expertise/ai-audit-trail-architecture-compliance
Date: 2026-04-16
Excerpt: "Hash chaining means each new log entry incorporates the SHA-256 digest of the previous entry. Changing any record in history invalidates all successor hashes. Merkle trees let you batch records and verify integrity in O(log n) time."
Context: Arquitectura enterprise-grade para compliance (HIPAA, GDPR, DORA, FINRA).
Confidence: high

### 7.2 Minimum Viable Audit Schema

Claim: El schema minimo requiere: Timestamp_UTC, Audit_ID, User_ID, Model_Name & Version, Prompt_Version, Query_Classification, Source_Documents, Confidence_Score, Approval_Status (APPROVED_HUMAN/APPROVED_AUTO/PENDING_REVIEW). [^657^]
Source: Lawrence Emenike — Audit Trails and Explainability for Compliance
URL: https://lawrence-emenike.medium.com/audit-trails-and-explainability-for-compliance-building-the-transparency-layer-financial-services-d24961bad987
Date: 2025-12-17
Excerpt: "Approval_Status: Workflow state (APPROVED_HUMAN, APPROVED_AUTO, PENDING_REVIEW). Documents decision governance and control points."
Context: El campo Approval_Status con sus 3 valores es exactamente el patron de FaberLoom.
Confidence: high

### 7.3 Action Receipts Pattern

Claim: Cada accion debe producir un receipt: que cambio, donde, referencias, timestamps, agente responsable, y opcion de rollback. Esto reduce tickets de soporte y satisface requisitos de compliance. [^615^]
Source: HatchWorks — Chat-First UX Fails. Use These Patterns Instead
URL: https://hatchworks.com/blog/ai-agents/agent-ux-patterns/
Date: 2026-03-25
Excerpt: "Every action produces a receipt: what changed, where, references, timestamps, responsible agent, and a rollback option. This reduces 'what did it do?' support tickets and satisfies audit and compliance requirements."
Context: Pattern #6 de 12 agent UX patterns. Directamente aplicable a FaberLoom.
Confidence: high

---

## 8. Escalation y Timeouts

### 8.1 ESCALATE.md — El Protocolo Abierto

Claim: ESCALATE.md es una especificacion abierta (marzo 2026) que define: triggers (acciones que siempre requieren aprobacion), channels (email/Slack/PagerDuty con timeouts), approval methods (email reply, Slack reaction, API endpoint), context requirements (accion, razon, costo, reversibilidad), y audit logging. Si nadie responde en el timeout, el fallback es configurable: default es handoff a KILLSWITCH.md. [^641^][^750^]
Source: escalate.md — The AI Agent Human Approval Protocol
URL: https://escalate.md/
Date: 2026-03-13
Excerpt: "If no human responds within the configured timeout, ESCALATE.md automatically hands off to KILLSWITCH.md for a full shutdown. Default behaviour: escalate to KILLSWITCH.md for a full stop. Alternative: deny the action automatically and log the timeout."
Context: Especificacion MIT license. Parte de un stack de 12 especificaciones de seguridad para agentes IA.
Confidence: high

### 8.2 Async Approval con Reminders y Escalation

Claim: AXME implementa aprobacion asincrona con: reminder a los 5 minutos, escalation a backup reviewer a los 30 minutos, timeout a las 8 horas. El agente no bloquea ni hace poll; se suspende durablemente y reanuda cuando el humano responde. [^756^]
Source: AXME — Async Human Approval for AI Agents
URL: https://github.com/AxmeAI/async-human-approval-for-ai-agents
Date: 2026-03-26
Excerpt: "Agent -> send_intent('needs_approval', remind=5min, timeout=8h); 5 min later: AXME sends reminder; 30 min later: AXME escalates to backup reviewer; 2 hours later: Human approves from phone. Agent <- resumes with approval result."
Context: La suspension durable (durable suspend) es clave: el agente consume cero recursos mientras espera.
Confidence: high

### 8.3 Cloudflare waitForApproval

Claim: Cloudflare Workflows ofrece waitForApproval() con timeout configurable (horas, dias, semanas). Aprobar o rechazar via API. Reporta progreso durante la espera. [^651^][^684^]
Source: Cloudflare Agents — Human-in-the-loop patterns
URL: https://developers.cloudflare.com/agents/guides/human-in-the-loop/
Date: 2026-04-20
Excerpt: "Use Workflow approval when you need durable, multi-step processes with approval gates that can wait hours, days, or weeks... this.waitForApproval(step, { timeout: '7 days' })"
Context: API especifica: approveWorkflow(workflowId, { reason?, metadata? }) y rejectWorkflow(workflowId, { reason? }).
Confidence: high

### 8.4 Intercom Ask Teammate with Timeout

Claim: Intercom Fin permite configurar un timeout en steps de "Ask teammate". Si nadie responde antes del timeout, Fin envia un mensaje de escalacion, se remueve de la conversacion, y la asigna segun la configuracion. [^647^]
Source: Intercom Help — Human-in-the-loop approvals
URL: https://www.intercom.com/help/en/articles/14468561-human-in-the-loop-approvals-using-ask-teammate-in-procedures
Date: 2026-04-21
Excerpt: "If no teammate responds before the timeout, Fin sends the escalation message, removes itself from the conversation, and assigns it per your configuration."
Context: El patron de "remove and assign" es un tipo de fallback cuando nadie responde.
Confidence: medium

### 8.5 SLA-Driven Timeout Escalation

Claim: Cada request de aprobacion necesita un timeout y fallback. Los SLAs se definen por tipo de excepcion: financial variances → 2 horas, data quality issues → 8 horas. La urgencia debe coincidir con el impacto de negocio. [^609^]
Source: SAP Community
URL: https://community.sap.com/t5/artificial-intelligence-blogs-posts/human-in-the-loop-sap-agents-approval-escalation-and-audit-series-2-part-5/ba-p/14372994
Date: 2026-04-13
Excerpt: "SLA-driven timeout escalation: Every approval request needs a timeout and fallback. Define SLAs by exception type — financial variances get 2 hours, data quality issues get 8 hours. Match the urgency to the business impact."
Context: Para FaberLoom: un timeout de 24-48 horas para aprobacion de UI proposals parece razonable.
Confidence: medium

---

## 9. Differential Previews

### 9.1 Diff Review en Cursor

Claim: Cursor 2.0 implementa: (1) Command Approval — preview antes de ejecucion, auto-approve solo para operaciones seguras; (2) Undo Functionality — todas las acciones se pueden deshacer en un paso; (3) Diff Review — review completo del diff antes de aplicar cambios; (4) Tool Call Limits — max 25 tool calls antes de parar. [^620^]
Source: Digital Applied — Cursor 2.0 Agent-First Architecture Guide
URL: https://www.digitalapplied.com/blog/cursor-2-0-agent-first-architecture-guide
Date: 2025-12-15
Excerpt: "Diff Review: Before applying changes, you can review a complete diff of all modifications across all files, seeing exactly what the agent plans to change. Undo Functionality: All agent actions can be undone in a single step, reverting all file changes made during a workflow."
Context: Cursor trata el diff review como feature de seguridad core.
Confidence: high

### 9.2 Visual Diff Review

Claim: El diff review visual es el estandar emergente: antes/después renderizado lado a lado, no como texto crudo. Cuando un agente edita un mockup, se debe ver el before/after renderizado, no JSON blobs. [^745^]
Source: Nimbalyst — How to Review AI Code Changes Before Applying Them
URL: https://nimbalyst.com/blog/ai-diff-review-visual-agent-changes/
Date: 2026-03-26
Excerpt: "When an agent edits a mockup, you should see the before and after mockup side by side, or better, see the changes highlighted directly on the rendered mockup... This is what AI diff review should look like. Not a text dump. A visual representation of change, native to each file type."
Context: Critico para FaberLoom: el diff de una propuesta de UI debe ser visual (render before/after), no solo código.
Confidence: high

### 9.3 Zed AI Diff Review

Claim: Zed ofrece diff review editable en unified diff, con accept/reject all changes antes de commitear. [^738^]
Source: Zed — AI Code Editor
URL: https://zed.dev/ai
Date: 2026 (current)
Excerpt: "Review the agent's work in an editable unified diff. Accept or reject all changes before committing them."
Context: Zed hace el diff review explicito y bloqueante: no se puede commitear sin revisar.
Confidence: high

### 9.4 Diff en GitHub Copilot Workspace

Claim: Copilot Workspace genera cambios en diff view para inspeccion linea por linea. El usuario puede iterar pidiendo a Workspace que revise archivos especificos o regenere secciones antes del PR. [^613^]
Source: Vibecoder — GitHub Copilot Workspace Reviewed
URL: https://blog.vibecoder.me/github-copilot-workspace-hands-on-review
Date: 2026-04-05
Excerpt: "The changes appear in a diff view so you can inspect every line. You can also iterate, asking Workspace to revise specific files or regenerate sections before the PR goes out."
Context: Stage 3 (Code Generation) muestra diff; Stage 4 (Go/No-Go) es la aprobacion final con iteracion.
Confidence: high

---

## 10. Catalogo de Patterns: Evaluacion FaberLoom Fit

| # | Pattern | Fit para FaberLoom | Confidence | Implementacion |
|---|---------|-------------------|------------|----------------|
| 1 | **3-Checkpoint Framework** (Plan→Findings→Diff) | ALTO | high | El Plan Gate es exactamente la propuesta de UI que FaberLoom muestra. Aprobar el plan antes de generar código. |
| 2 | **3-Action Triad** (Approve/Discard/Iterate) | ALTO | high | Los botones APROBAR/DESCARTAR/ITERAR de FaberLoom coinciden con: Keep/Undo/Refine (VS Code), Approve/Reject/Modify (inference.sh), Approve/Conditional/Reject (SAP). |
| 3 | **Confidence-Based Routing** | MEDIO-ALTO | high | Auto-aprobar propuestas con confianza >90% (ej: cambios cosméticos). Revisión humana obligatoria para <90%. Calibrar empíricamente. |
| 4 | **Pre-execution Approval Gate** | ALTO | high | Mostrar preview antes de aplicar cambios. No modificar el código fuente hasta que el usuario apruebe. |
| 5 | **Visual Diff Preview** | ALTO | high | Before/after renderizado de la UI propuesta, no solo código. Crítico para que diseñadores evalúen. |
| 6 | **Undo/Rollback** | ALTO | high | DESCARTAR actúa como undo pre-aplicación. Post-aplicación: checkpoints automáticos (como Cursor). |
| 7 | **Audit Trail Inmutable** | MEDIO | high | Log de quién aprobó qué y cuándo. Inicialmente: simple tabla con timestamp, usuario, decisión. Escalar a hash-chaining para compliance. |
| 8 | **ESCALATE.md Protocol** | MEDIO | medium | Timeout configurable (ej: 24h). Si nadie aprueba: fallback a DESCARTAR con notificación. Escalar a manager después de 2 timeouts. |
| 9 | **Progressive Delegation** | MEDIO | medium | Empezar con aprobación manual obligatoria para todas las propuestas. Auto-aprobar después de N aprobaciones consecutivas sin correcciones. |
| 10 | **Action Receipts** | ALTO | high | Cada propuesta aprobada genera un receipt: qué cambió, quién aprobó, timestamp, opción de rollback. |
| 11 | **Batch Approval** | BAJO | medium | No prioritario para MVP. Importante cuando FaberLoom genere múltiples propuestas simultáneas. |
| 12 | **Plan-and-Execute UI** | ALTO | high | Mostrar pasos del plan con checkmarks (completados) y pulsing indicator (activo). Pasos futuros editables. |
| 13 | **Tool-level Smart Review** | MEDIO | medium | Solo interrumpir para cambios de alto riesgo (estructura, navegación). Auto-aprobar cambios cosméticos simples. |
| 14 | **Evidence Panel** | MEDIO | medium | Mostrar razonamiento del agente (sources, constraints). Separar hechos de asunciones. No es chain-of-thought dump. |
| 15 | **Sampled Audit at Scale** | BAJO | low | Relevante solo a escala enterprise con 1000+ propuestas/día. |

---

## 11. Gaps Identificados

1. **El patrón exacto "approve/discard/iterate" como trío de botones UI no se encontró documentado formalmente** en la literatura de UX/AI. Los productos usan variantes (Keep/Undo, Approve/Reject/Modify, Approve/Conditional/Reject) pero el framing exacto de "Iterate" como tercera opción propositiva (no solo reject+retry) es una innovación que FaberLoom puede liderar. Los productos de IA generativa de UI (v0, Bolt, Lovable) usan más un loop conversacional de refinamiento que botones formales de iteración.

2. **Lovable.dev y Bolt.new** no documentan sus flujos de aprobación formalmente. Usan un modelo de conversación continua sin gates formales — el usuario itera por chat, no por botones de aprobación. Esto sugiere que el modelo conversacional es más común que el modelo gate-based en herramientas de generación de UI, aunque el modelo gate-based es más seguro para enterprise.

3. **Batch approval** para UI proposals no se encontró implementado en ningún producto estudiado. Este es un gap real que FaberLoom podría innovar.

4. **No se encontró evidencia** de que ninguno de los productos estudiados (v0, Bolt, Lovable) implemente confidence routing visual explícito en su UI de generación de UI. La confianza es más común en sistemas de procesamiento de documentos que en generación de UI.

5. **Manufacturing software approval patterns**: Las búsquedas específicas no arrojaron resultados aplicables. Los patrones de MES/ERP parecen usar workflows de aprobación tradicionales (no específicos de IA).

6. **OpenAI Playground y Anthropic Console** no tienen flujos de aprobación formal con botones de approve/discard/iterate. Son más orientados a experimentación que a workflows de producción.

---

## 12. Recomendaciones Especificas

### Inmediatas (MVP)

1. **Implementar 3-Checkpoint Gate**: Propuesta generada → Preview visual con diff → APROBAR/DESCARTAR/ITERAR. No aplicar cambios hasta aprobación. [Confidence: high]
2. **Diff visual before/after**: Mostrar la UI propuesta renderizada lado a lado con la actual (o solo la propuesta si es nueva). [Confidence: high]
3. **Audit log simple**: Tabla con session_id, timestamp, usuario, decisión (approve/discard/iterate), comentario. [Confidence: high]
4. **Undo post-aprobación**: Checkpoints automáticos antes de aplicar cambios, restaurables en 1 click. [Confidence: high]

### Corto plazo (v2)

5. **Confidence routing**: Implementar auto-approve para cambios cosméticos simples (colores, spacing, texto) con confidence >90%. Revisión obligatoria para cambios estructurales. [Confidence: medium]
6. **Timeout con escalation**: 24h para aprobación. Si nadie responde: fallback a DESCARTAR + notificación email. Escalar a manager después de 2 timeouts. [Confidence: medium]
7. **Action receipts**: Cada propuesta aprobada genera un receipt inmutable: qué cambió, quién aprobó, timestamp, rollback disponible. [Confidence: high]
8. **Progressive delegation tracking**: Contador de aprobaciones consecutivas. Después de 20 aprobaciones sin correcciones, ofrecer auto-approve opcional. [Confidence: medium]

### Medio plazo (v3)

9. **Batch approval UI**: Para escenarios de generación múltiple, permitir seleccionar múltiples propuestas y aprobar/rechazar en bulk. [Confidence: medium]
10. **Audit trail inmutable**: Migrar a hash-chaining + tiered storage para compliance enterprise. [Confidence: medium]
11. **Smart review por tipo de cambio**: Clasificar propuestas por tipo (estructural, visual, contenido, interacción) y aplicar diferentes umbrales de aprobación por tipo. [Confidence: medium]
12. **Integration con ESCALATE.md**: Implementar el protocolo como archivo de configuración versionado para definir triggers, channels, y fallback. [Confidence: low — es un estandar emergente]

---

## 13. Bibliografia y Fuentes

### Fuentes Primarias (Documentacion Oficial, GitHub, Engineering Blogs)

1. **VS Code Docs** — Review AI-generated code edits. 2026-05-06. https://code.visualstudio.com/docs/copilot/chat/review-code-edits [^678^]
2. **Cursor Checkpoints** — Steve Kinney. 2026-03-17. https://stevekinney.com/courses/ai-development/cursor-checkpoints [^622^]
3. **Cursor 2.0 Guide** — Digital Applied. 2025-12-15. https://www.digitalapplied.com/blog/cursor-2-0-agent-first-architecture-guide [^620^]
4. **Cloudflare Agents HITL** — Cloudflare Docs. 2026-04-20. https://developers.cloudflare.com/agents/guides/human-in-the-loop/ [^651^]
5. **Tiptap AI Diff View** — Tiptap Docs. 2026-04-23. https://tiptap.dev/docs/content-ai/capabilities/suggestion/features/diff-view [^646^]
6. **Tiptap AI Toolkit Review** — Tiptap Docs. 2026-05-10. https://tiptap.dev/docs/content-ai/capabilities/ai-toolkit/agents/review-changes [^676^]
7. **LangGraph HITL Tutorial** — Turion AI. 2026-04-28. https://turion.ai/blog/langgraph-human-in-the-loop-interrupt-tutorial/ [^674^]
8. **LangGraph HITL Patterns** — Abstract Algorithms. 2026-03-28. https://www.abstractalgorithms.dev/langgraph-human-in-the-loop [^679^]
9. **Bolt.new Version History** — Bolt Docs. 2026-04-07. https://support.bolt.new/concepts/version-history-github [^736^]
10. **Dagu Approval** — Dagu Docs. 2026-05-04. https://docs.dagu.sh/writing-workflows/approval [^710^]
11. **Anthropic Claude Code Review** — Anthropic Docs. 2025-09-01. https://code.claude.com/docs/en/code-review [^656^]
12. **Intent by Augment** — Augment Docs. 2026-02-10. https://docs.augmentcode.com/intent/overview [^751^]
13. **inference.sh Approval Gates** — inference.sh. 2026-02-16. https://inference.sh/blog/tools/approval-gates [^717^]
14. **ESCALATE.md Spec** — escalate.md. 2026-03-13. https://escalate.md/ [^641^]
15. **Zed AI** — zed.dev. https://zed.dev/ai [^738^]

### Fuentes de Analisis y Engineering Blogs

16. **3-Checkpoint Framework** — Code on Grass. 2026-05-04. https://codeongrass.com/blog/where-to-gate-your-ai-coding-agent-3-checkpoint-framework/ [^662^]
17. **5 HITL Production Patterns** — Cordum. 2026-04-01. https://cordum.io/blog/human-in-the-loop-ai-patterns [^663^]
18. **Agent UX Patterns** — HatchWorks. 2026-03-25. https://hatchworks.com/blog/ai-agents/agent-ux-patterns/ [^615^]
19. **Agent UX 2026** — FuseLab Creative. 2025-08-28. https://fuselabcreative.com/ui-design-for-ai-agents/ [^619^]
20. **SAP HITL Agents** — SAP Community. 2026-04-13. https://community.sap.com/t5/artificial-intelligence-blogs-posts/human-in-the-loop-sap-agents-approval-escalation-and-audit-series-2-part-5/ba-p/14372994 [^609^]
21. **Confidence Routing** — Grizzly Peak. 2026-02-13. https://www.grizzlypeaksoftware.com/library/human-in-the-loop-patterns-for-ai-agents-n64sb2cm [^614^]
22. **AI Audit Trail Architecture** — The Bright Byte. 2026-04-16. https://thebrightbyte.com/playbook/expertise/ai-audit-trail-architecture-compliance [^645^]
23. **Claude Code HITL** — LowCode Agency. 2026-04-10. https://www.lowcode.agency/blog/claude-code-human-in-the-loop [^675^]
24. **Designing AI UIs People Trust** — High Peaks. 2026-04-30. https://highpeaksw.com/designing-ai-uis-people-actually-trust-microcopy-controls-and-recovery/ [^655^]
25. **Cline Architecture** — Cline. 2026-01-27. https://cline.bot/blog/the-architecture-that-gets-ai-coding-tools-approved [^649^]
26. **GitHub Copilot Workspace** — Vibecoder. 2026-04-05. https://blog.vibecoder.me/github-copilot-workspace-hands-on-review [^613^]
27. **Vercel v0 Rebuilt** — VentureBeat. 2026-02-03. https://venturebeat.com/infrastructure/vercel-rebuilt-v0-to-tackle-the-90-problem-connecting-ai-generated-code-to-existing-production-infrastructure-not-prototypes [^666^]
28. **V0 Review** — AI Viewer. 2026-03-08. https://aiviewer.ai/tools/v0-dev/ [^664^]
29. **Replit Agent 4** — MindStudio. 2026-04-07. https://www.mindstudio.ai/blog/what-is-replit-agent-4/ [^713^]
30. **Confidence Thresholds** — UserOrbit. 2026-05-06. https://userorbit.com/help/en/how-to-configure-agent-confidence-thresholds [^746^]
31. **Visual Diff Review** — Nimbalyst. 2026-03-26. https://nimbalyst.com/blog/ai-diff-review-visual-agent-changes/ [^745^]
32. **Copilot Workspace Stages** — Vibecoder. 2026-04-05. https://blog.vibecoder.me/github-copilot-workspace-hands-on-review [^613^]
33. **ASDLC Autonomy Levels** — ASDLC.io. 2026-03-18. https://asdlc.io/concepts/levels-of-autonomy/ [^714^]
34. **Cloudflare Agents HITL Concepts** — Cloudflare Docs. 2026-04-20. https://developers.cloudflare.com/agents/concepts/human-in-the-loop/ [^712^]
35. **AXME Async Approval** — GitHub. 2026-03-26. https://github.com/AxmeAI/async-human-approval-for-ai-agents [^756^]
36. **NIST AI RMF Agentic Profile** — Cloud Security Alliance. 2026-04-02. https://labs.cloudsecurityalliance.org/agentic/agentic-nist-ai-rmf-profile-v1/ [^677^]
37. **Intent vs Cline** — Augment Code. 2026-03-11. https://www.augmentcode.com/tools/intent-vs-cline [^653^]
38. **Lovable vs v0** — Lovable. 2026-03-05. https://lovable.dev/guides/lovable-vs-v0 [^755^]
39. **AI Delegation Matrix** — Syntax Stream. 2026-02-03. https://syntaxstream.substack.com/p/the-ai-delegation-matrix-what-parts-of-your-ui-shouldnt-exist [^721^]
40. **Approval Gates for Autonomous Agents** — Tian Pan. 2026-03-06. https://tianpan.co/blog/2026-03-06-designing-approval-gates-for-autonomous-ai-agents [^737^]
41. **SAP Agentic AI Practice** — SAP Community. 2026-04-03. https://community.sap.com/t5/artificial-intelligence-blogs-posts/sap-agentic-ai-in-practice-building-the-sap-migration-assessment-agent-part/ba-p/14365363 [^665^]
42. **Dify Human Input Node** — Dify. 2026-03-03. https://dify.ai/blog/the-human-input-node-bringing-human-judgment-into-automated-workflows [^642^]
43. **SAP HITL Patterns** — SAP Community. 2026-04-13. https://community.sap.com/t5/artificial-intelligence-blogs-posts/human-in-the-loop-sap-agents-approval-escalation-and-audit-series-2-part-5/ba-p/14372994 [^609^]
44. **Zapier HITL Patterns** — Zapier. 2025-11-12. https://zapier.com/blog/human-in-the-loop/ [^744^]
45. **Lovable Build Guide** — Lovable. 2026-05-08. https://lovable.dev/guides/how-to-build-an-ai-code-generator [^754^]
46. **Warp Code Review** — Warp Docs. 2026-04-14. https://docs.warp.dev/guides/agent-workflows/how-to-review-ai-generated-code [^747^]
47. **HITL Arxiv Paper** — Arxiv. 2026-03-04. https://arxiv.org/html/2603.04552v1 [^608^]
48. **Confidence Routing Dev.to** — Dev.to. 2026-04-20. https://dev.to/iterationlayer/building-ai-agents-that-process-documents-mcp-structured-io-and-confidence-routing-8ic [^610^]
49. **Audit Trail AI** — SparkCo. 2025-10-05. https://sparkco.ai/blog/mastering-audit-trails-for-ai-models-a-deep-dive [^652^]
50. **Cursor Regression Diff UI** — Cursor Forum. 2026-03-16. https://forum.cursor.com/t/regression-ai-edits-applying-automatically-without-diff-approval-ui/154887 [^680^]
51. **Zed Agent Diff Issue** — GitHub. 2026-02-25. https://github.com/zed-industries/zed/issues/50142 [^682^]
52. **Agent UX Design** — kweinmeister/agent-design-patterns (GitHub). https://github.com/kweinmeister/agent-design-patterns [^617^]
53. **Intercom HITL** — Intercom Help. 2026-04-21. https://www.intercom.com/help/en/articles/14468561-human-in-the-loop-approvals-using-ask-teammate-in-procedures [^647^]
54. **Lovable Build Internal Tools** — Lovable. 2026-05-07. https://lovable.dev/guides/build-internal-tool-without-code [^640^]
55. **Replit Plan/Build Modes** — Replit Community. 2025-08-30. https://replit.discourse.group/t/new-agent-build-plan-modes/6831 [^718^]
56. **V0 by Vercel Guide** — Vercel Academy. 2025-11-15. https://vercel.com/academy/ai-sdk/ui-with-v0 [^667^]
57. **Claude Code HITL Workflow** — LowCode Agency. 2026-04-10. https://www.lowcode.agency/blog/claude-code-human-in-the-loop [^675^]
58. **AI Agent Workflow Building UI** — Builder.io. https://www.builder.io/m/explainers/ai-agent-workflow-building-ui [^618^]
59. **ESCALATE.md LLMs** — escalate.md. https://escalate.md/llms.txt [^750^]
60. **FAILSAFE.md** — failsafe.md. 2026-03-13. https://failsafe.md/ [^749^]

---

## Estadisticas de la Investigacion

- **Busquedas realizadas:** 25+ queries independientes
- **Fuentes analizadas:** 60+ fuentes primarias y secundarias
- **Productos estudiados:** VS Code Copilot, Cursor, Bolt.new, Lovable, v0 (Vercel), Replit Agent, Claude Code, Cline, Intent by Augment, Zed, GitHub Copilot Workspace, Tiptap AI
- **Frameworks/patrones:** LangGraph HITL, Cloudflare Agents, SAP Agentic AI, ESCALATE.md, Dagu workflows, inference.sh
- **Confidence promedio de findings:** high (70%), medium (25%), low (5%)
