# PROMPT DE AUDITORÍA EXTERNA — User Admin + Directory Sync + Knowledge Flow en FaberLoom

**Fecha:** 2026-04-19
**Pegá este prompt a un LLM externo (ChatGPT o Claude con web) para opinión independiente.**
**NO es un prompt para implementar — es para escuchar opinión arquitectónica antes de decidir.**

---

## Rol del auditor

Actuás como Principal PM/Arquitecto SaaS con experiencia específica en:
- Multi-tenant B2B SaaS (RBAC, ABAC, SCIM, OIDC)
- Directory sync con Microsoft Entra ID (M365) y Google Workspace
- Plataformas de agentes IA (Glean, Sana, Moveworks, Copilot Studio) — sabés cómo resolvieron identity + knowledge scoping
- Multi-tenant RAG con row-level security (Supabase/pgvector patterns)

Respondés directo, sin rodeos. Si un tradeoff es feo, lo decís. Si algo está subespecificado, lo marcás como tal. No inventás datos; si te faltan, pedís.

---

## Contexto FaberLoom (mínimo, no re-explicar)

FaberLoom es un SaaS B2B "control-plane" para agentes de IA. ICP: PYMEs LATAM 5-50 empleados. Wedge inicial: cotización B2B calzado seguridad (distribuidores Marluvas/Tecmater). Principio no negociable: **draft-first** — ningún agente envía nada externo sin aprobación humana.

Arquitectura acordada (para contexto):
- 3 objetos: AgentSpec · AgentRuntime · AgentMemory
- 3 capas de skill: Base sealed (FaberLoom) · Overlay manual (admin org) · Overlay aprendido (candidate→active→archived con gate humano)
- Autonomy Ladder L0-L4 (Shadow → Propone → Auto-low → Auto+notif → Auto+excep)
- Clasificador de aprendizaje 3 destinos: Contexto / Skill refinement / Gold sample (P11)
- Propagación cross-skill con checkbox por skill impactado (P12)
- Multi-tenant con contención: org A no ve lo aprendido por org B (P13)
- Stack target: Supabase (PostgreSQL + pgvector + RLS) + FastAPI + Next.js + LiteLLM

Roles identificados hoy en docs (no validados): Tenant Owner · Admin · Operator. Sin jerarquía más fina.

---

## El gap a auditar

Tres preguntas específicas del CEO, sin spec hoy en el KB:

### Pregunta 1 — Directory sync y herencia de jerarquía

Si FaberLoom se conecta a **Microsoft 365 (Entra ID)** o **Google Workspace** del cliente:

- ¿Debe heredar la jerarquía de la organización automáticamente (OUs, grupos, managers, departamentos)?
- ¿Qué se sincroniza exactamente: usuarios, grupos, manager chain, departamentos, locations, custom attributes?
- ¿SCIM 2.0 es el protocolo correcto o es overkill para PYMEs 5-50 empleados?
- ¿Qué pasa si el cliente NO tiene M365 ni Workspace (usa Gmail personal o POP3 corporativo custom)?
- ¿Cómo se resuelve conflicto entre la jerarquía sincronizada y la que el admin de FaberLoom quiere definir localmente?

### Pregunta 2 — Creación manual + mapeo con directory

Si el admin crea usuarios manualmente en FaberLoom (sin sync):

- ¿Cómo se mapean después con un directory cuando se conecta?
- ¿Merge por email canónico? ¿Y cuando el email cambia?
- ¿Qué wins: la verdad del directory o la data local? ¿Se permite override local con flag `locally_managed: true`?
- ¿Qué permisos inicializa por default un usuario nuevo sin directory?

### Pregunta 3 — Knowledge flow (lo más importante)

FaberLoom maneja conocimiento que viene de distintas fuentes y alcances. El CEO quiere que sea explícito **dónde vive cada tipo de conocimiento y cómo fluye**:

| Tipo propuesto | Ejemplos | Alcance natural | Fuente |
|---|---|---|---|
| **Knowledge global** (plataforma) | Best practices FaberLoom, templates, skill base sealed | Todos los tenants | FaberLoom publica |
| **Knowledge org/tenant** | Catálogo Marluvas, políticas comerciales Muito Work, historias de clientes | Solo esa org | Admin org sube |
| **Knowledge departamental** | "Cómo cotiza el equipo MX", SLAs del equipo soporte LatAm, tono del equipo de ventas enterprise | Solo ese depto | Manager depto sube o hereda |
| **Knowledge usuario** | Voice profile personal de Álvaro, firma propia, estilo personal, preferencias de control | Solo ese usuario | Usuario autoría + sistema aprende (UserControlProfile) |

Preguntas específicas:

a) ¿Esta taxonomía de 4 niveles (global/org/depto/user) es correcta o debería colapsar a 3, o expandir?

b) ¿Cómo se resuelven **conflictos de overlay** cuando un skill compone conocimiento de los 4 niveles al mismo tiempo?
   Ejemplo real: cotización a cliente grande — el skill base dice "nunca prometer plazo <5 días", la org dice "para clientes CR aplicar descuento 8%", el depto MX dice "pesos mexicanos con IVA en body", el usuario Álvaro tiene voz "Estimado/Hola según recurrencia". ¿Quién gana si hay choque? ¿Precedencia fija o negociada por caso?

c) ¿El aprendizaje (P11: Contexto/Skill refinement/Gold sample) respeta esta jerarquía?
   - Un patrón aprendido por Álvaro ¿puede promoverse a nivel depto? ¿A nivel org?
   - ¿Qué aprueba el promote-up: el usuario, el manager, el admin, el CEO?
   - ¿Hay promote-down (algo org que se vuelve solo depto)?

d) **Multi-tenant vs multi-user leakage** — dado que la P13 dice "org A no ve lo de org B", ¿dentro de la misma org, un usuario ve lo que aprendió otro usuario?
   - ¿Depto A (ventas MX) ve gold samples de Depto B (ventas CO) por default?
   - ¿O todo es privado por default y el admin decide qué compartir?

e) ¿Cómo debería ser el **UI de gobierno del conocimiento** en Admin Panel?
   - Matriz rol × alcance × tipo-de-conocimiento
   - Visualización del flujo (sankey? árbol?)
   - Audit log de promociones/demociones de conocimiento entre niveles

f) ¿Qué **conocimiento NUNCA se comparte automáticamente aunque la jerarquía lo permita**?
   - PII del usuario
   - Credenciales de canal personal (Gmail OAuth personal vs corporativo)
   - Conversaciones privadas del usuario con agentes

g) ¿Cómo se reconcilia esto con la **P12 cross-skill propagation**? Un patrón de tono aprendido en `sk_cotizar` se propaga a `sk_followup` dentro del mismo skill cluster — pero ¿se propaga también desde el depto MX al depto CR? ¿Desde el usuario Álvaro a otros usuarios del mismo depto?

---

## Comparables que mencionar en tu análisis

Te invito a referenciar cómo resolvieron esto:
- **Glean** — directory sync + permissions inheritance para search enterprise
- **Sana / Moveworks** — agentes con conocimiento departamental
- **Microsoft Copilot Studio** — herencia de Entra ID + topic scoping
- **Salesforce Einstein Agents** — perfiles + roles + sharing rules
- **Zendesk / Intercom Fin** — knowledge org-wide vs team-specific

No asumás que son modelos perfectos. Señalá dónde fallan para una PYME LATAM 5-50 empleados.

---

## Restricciones del producto que debés respetar

- ICP es PYME LATAM 5-50 empleados, NO enterprise. Soluciones "SCIM + full SAML + ABAC granular" pueden ser overkill.
- El admin de la org probablemente es el CEO o un líder comercial, NO un IT admin dedicado. La UX no puede parecerse a Okta.
- Draft-first absoluto para comunicación externa: aunque la jerarquía autorice autonomía, el correo/WhatsApp/Slack externo siempre pasa por humano.
- Multi-tenant con contención estricta: org A nunca ve lo de org B. Esto es inquebrantable.
- Stack Supabase + pgvector con RLS (Row-Level Security) como capa primaria de aislamiento.

---

## Entregable esperado

Respondé en este formato estructurado:

### 1. Veredicto rápido (párrafo de 150 palabras)
¿La taxonomía 4 niveles está bien? ¿Qué cambiarías antes de diseñar la UI?

### 2. Modelo de identidad recomendado
- Qué sincronizar de M365/Workspace (lista concreta de campos)
- Qué protocolo (SCIM / OIDC / OAuth + custom / sin sync)
- Cómo resolver manual-vs-synced
- Precedencia de conflictos — tabla clara
- Qué hacer para PYMEs sin directory corporativo

### 3. Modelo de flujo de conocimiento
- Taxonomía final (4 niveles o cuántos)
- Algoritmo de composición de overlays — pseudocódigo o diagrama
- Tabla de precedencia (base < org < depto < user? ¿o al revés? ¿o depende del tipo?)
- Cómo respeta la propagación cross-skill P12
- Qué se promueve up y qué no, con criterios

### 4. Matriz de governance (rol × permiso × tipo-de-conocimiento)
Tabla concreta. No describas en prosa.

### 5. UI implicada
Qué pantallas nuevas faltan en el mockup (o cambios a las existentes) para gobernar esto. Lista corta.

### 6. Riesgos específicos LATAM PYME
- Riesgos de privacidad (LGPD Brasil, Ley 29733 Perú, etc.)
- Riesgos de adopción (admin sin IT)
- Riesgos de costo (Entra ID licensing, SCIM tooling)
- Qué workarounds son aceptables en beta y cuáles no

### 7. Decisiones que el CEO debe tomar antes de diseñar
Lista numerada, cada decisión con opciones + recomendación. Máximo 10.

### 8. Qué NO hacer en v1
Patrón de sobre-ingeniería a evitar. Identificá 3-5 tentaciones que habría que resistir.

---

## Tono y restricciones del auditor

- Español, directo, sin rodeos, sin formalidades.
- Tablas cuando sean comparaciones.
- Si no tenés datos, decilo explícitamente ("no sé, esto requiere entrevista con 3 PYMEs para validar").
- Recomendación concreta en cada decisión con trade-offs, no lista neutral de opciones.
- No repitas el contexto que ya te di.
- Si ves un gap en las preguntas del CEO (algo que debería preguntarse y no preguntó), marcalo con **[GAP DEL CEO — X]** y respondé igual.
