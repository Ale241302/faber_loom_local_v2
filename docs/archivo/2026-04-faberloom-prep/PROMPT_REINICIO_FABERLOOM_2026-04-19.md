# PROMPT DE REINICIO — FaberLoom Mockup v2

Pega esto en una conversación nueva para retomar sin cargar contexto viejo.

---

## Contexto mínimo

Soy Álvaro (Muito Work Limitada, Costa Rica). Estoy construyendo **FaberLoom**, un SaaS B2B tipo control-plane para agentes de IA, ICP PYMEs LATAM 5-50 empleados, wedge inicial cotización B2B calzado seguridad industrial (distribuidores Marluvas/Tecmater en LatAm).

Principio no negociable: **draft-first absoluto** — ningún agente envía nada externo sin aprobación humana.

## Estado del mockup

Archivo activo: `/sessions/eloquent-happy-galileo/mnt/MWT KB/faberloom-mockup/index-standalone.html`

Single-file HTML, doble-click y corre. También existe versión modular ESM (`index.html` + `core/` + `modules/`) pero requiere servidor HTTP.

Tokens light+dark, i18n ES/EN/PT-BR, theme toggle, state toggle (loaded/empty/loading/error) via event bus.

Brand: editorial-warm coral (#C96442) + cream (#F4F1ED) + warm-dark (#1F1E1C). Georgia italic display + Inter UI + JetBrains Mono IDs. Claude-adjacent.

## Rutas implementadas (4)

- `#/bandeja/dr_001` — draft detail con claims `<sup>` clickeables + 4 tabs (evidence/provenance/risk/trace)
- `#/skills/sk_cotizar` — 3 capas (base/manual/aprendido) + modal consolidación
- `#/agentes/ag_cotizador` — 4 tabs + autonomy ladder L1 67%/43 runs
- `#/workflows` — canvas SVG 7 nodos + inspector

## Bugs documentados (pendientes de fix)

1. **Tablero (`#/dashboard`) tira 404** — sidebar apunta pero la ruta no existe en el router
2. **Conexiones no funciona** — mismo problema, ruta no registrada
3. **Bandeja va directo a un mensaje** — falta la vista lista; debe mostrar mixto correos entrantes + entregables de agentes (inbound bidireccional)
4. **Faltan rutas lista**: `/bandeja`, `/agentes`, `/skills`, `/conexiones` (solo existen los detalles)

## Feedback conceptual del usuario (el que NO debés olvidar)

### Skills — modelo mental del usuario
Skills = **paquetes de conocimiento especializados** (ej. Forecast, Flujo de caja, Cotizador). Son habilidades específicas por dominio.

Dentro de cada skill hay dos secciones:
1. **Habilidades/conocimiento base** — el paquete en sí (instrucciones sealed + contexto embebido de fábrica)
2. **Habilidades aprendidas** — instrucciones + contexto que producen gold samples (overlay aprendido con ciclo Candidate→Active→Archived)

Los **agentes componen skills** — un agente puede tener 1+ skills, y el aprendizaje se granula por skill, no por agente.

### Voz de usuario — perdida
El usuario flagged que se perdió la edición/configuración de la voz del usuario (voice profile personal). Había estado en Skill Studio o Settings, ya no se ve.

### Otras funcionalidades que el usuario siente perdidas vs versión previa
- Agent Factory (creación de templates)
- Skills Library (marketplace)
- Learning Thermometer persistente
- Modal de consolidación accesible globalmente
- Shadow memory panel
- Acciones ciclo de vida por item (Edit/Version/Revert/Suspend/Archive)

## Decisiones arquitectónicas previas (no re-debatir)

- **Modular real**: shell + bus + store + lazy modules con contrato `{mount, unmount, onError}`. Si un módulo cae, el resto sigue vivo (DegradedCard). Ya implementado en versión ESM, consolidado en standalone.
- **3 capas de instrucciones por skill**: Base (sealed, FaberLoom), Overlay manual (Admin org), Overlay aprendido (sistema propone, humano aprueba)
- **Aprendizaje con 3 ejes**: Tipo (knowledge/instrucción/output pattern), Alcance (usuario/skill/agente/org), Propagación cross (P12)
- **Shadow memory + termómetro**: todo candidate va a shadow, usuario decide cuándo indexar vía modal de consolidación
- **Bandeja bidireccional**: outbound drafts + inbound deliverables + alertas + todo

## Auditorías previas disponibles

- 6 archivos `AUDIT_*-local.md` en `/mnt/MWT KB/` — audit local exhaustivo (tokens, screens, i18n, pending, roadmap 60 filas)
- `Auditoria_FaberLoom_v2.html` — audit externo de Claude estratégico contra las 10 memorias. 5 P1 blockers identificados.
- Merge acordado: Sprint 1 arquitectónico (10 items) + Sprint 1 visual (10 items) + Sprint 2 (i18n + a11y)

## Memorias activas relevantes

- `project_faberloom.md` — decisiones producto, arquitectura, precios
- `project_faberloom_brand.md` — tokens, paleta, tipografía
- `project_faberloom_agents_design.md` — Autonomy Ladder, gold samples, thermometer
- `project_faberloom_architecture.md` — AgentSpec/Runtime/Memory, state machine
- `project_faberloom_positioning.md` — wedge + sprint plan
- `project_faberloom_security.md` — policy engine, draft-first

## Modo de trabajo pedido

**DOCUMENTAR, NO EJECUTAR.** El usuario está iterando con observaciones en varios chats. Solo aplica cambios cuando diga explícitamente "ajusta" o "aplica".

## Primera tarea al retomar

Antes de cualquier fix:
1. Listar funcionalidades en la capa de interacción de usuario (lo que el user ve/hace)
2. Listar funcionalidades en la capa por detrás (bus events, store schema, módulos, contratos)
3. Mapear contra lo que el usuario siente perdido (voz de usuario, Factory, Skills Library, Thermometer, etc.)
4. Proponer arquitectura de Skills que separe "paquete de conocimiento base" de "habilidades aprendidas productoras de gold samples"

## Preferencias de respuesta

Español, tono directo, sin rodeos, sin formalidades, sin saludos. Tablas para comparaciones. Código al bloque. Recomendación directa cuando haya alternativas, no lista neutral. Si no hay datos suficientes, decirlo.
