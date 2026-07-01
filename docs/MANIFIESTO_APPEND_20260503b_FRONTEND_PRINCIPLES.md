---
id: MANIFIESTO_APPEND_20260503b_FRONTEND_PRINCIPLES
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-03
fecha: 2026-05-03
agente: Cowork (arquitecto · indexa skill nuevo a peticion CEO)
aplica_a: [FaberLoom]
---

# MANIFIESTO_APPEND_20260503b_FRONTEND_PRINCIPLES

## Que paso

CEO entrego un system prompt completo (14 principios) para crear el skill `frontend-ten-principles-v2` en el proyecto. Solicitud explicita: indexarlo en KB.

Primera version (v2.0) se creo replicando el system prompt original como agente con workflow rigido (3 fases obligatorias: Audit -> Spec -> Implementation, 3 artefactos: THESIS.md / SCREEN_INVENTORY.md / IMPLEMENTATION_SPEC.md, COMPLIANCE CHECKLIST bloqueante).

CEO clarifico el intent real: "lo que quiero es que sea una habilidad que tenga presente cuando piensa en funcionalidad enficado en el frontend". O sea, NO un agente con workflow — una **lente cognitiva persistente** que se active por contexto y coloree el razonamiento sin forzar artefactos.

Refactor v2.0 -> v2.1 mismo dia: se quito OUTPUT PROTOCOL rigido, EXECUTION WORKFLOW de 3 fases, COMPLIANCE CHECKLIST bloqueante. Se mantuvo canon (14 principios + catalogo de flags + antipatrones). Cambio autonomy de PROPONE a ACTIVO_BG.

## Documentos creados

| Archivo | Que documenta | Lineas aprox |
|---|---|---|
| `docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` | Skill type SKILL · status SHADOW · v2.1. Lente cognitiva frontend FaberLoom Design System. 14 principios (P1 thesis distillation - P14 contextual navigation), 13 flags catalogados (P0/P1/P2 severity), 4 modos de despliegue. Sin trigger word — activacion por contexto frontend (mock/UI/UX/layout/flujo/navegacion). Autonomy ACTIVO_BG (background — colorea razonamiento sin esperar invocacion). | ~250 |

## Documentos modificados

| Archivo | Cambio |
|---|---|
| `SKILL_RUNTIME.md` | v1.0 -> v1.1. +1 fila tabla principal (SKILL_FRONTEND_TEN_PRINCIPLES_V2 · trigger contexto · SHADOW · ACTIVO_BG). +1 bloque detalle. +1 entrada Historial de Cambios de Estado. Stamp VIGENTE 2026-04-16 -> 2026-05-03. Total skills: 10 -> 11. |
| `IDX_PLATAFORMA.md` | +1 fila seccion Skills (Frontend Ten Principles V2 -> faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md SHADOW v2.1). Health line actualizada (+1 SKILL en docs/faberloom/). Ultima revision -> 2026-05-03b. last_review header -> 2026-05-03. |
| `CLAUDE.md` (raiz) | Conteo total 430 -> 432 archivos markdown. docs/ activo 294 -> 296. Razon: +1 SKILL nuevo en docs/faberloom/ + 1 manifiesto en docs/. |

## Decisiones del arquitecto

1. **Path docs/faberloom/, no docs/ raiz.** Regla de scope FB (memoria 2026-04-29 sobre remediacion FB) — todo archivo nuevo de FaberLoom vive bajo `docs/faberloom/`. El skill aplica_a [FaberLoom] (FaberLoom Design System), entonces va alli sin discusion.

2. **Domain Plataforma, no Marca ni Producto.** Frontend governance / design system es infra de plataforma. IDX_PLATAFORMA tiene seccion Skills donde encaja. Coherente con SKILL_CLIENT_SERVICE que tambien aparece alli como cross-reference desde IDX_COMERCIAL.

3. **Refactor mismo dia v2.0 -> v2.1.** Aunque la regla 3 (no eliminar contenido aprobado) protege la KB, v2.0 nunca fue aprobado — fue creacion intermedia que CEO clarifico inmediatamente. Refactor permitido. Changelog explicito en archivo + en este manifiesto preserva trazabilidad.

4. **autonomy_ceiling ACTIVO_BG (concepto nuevo).** El catalogo previo era PROPONE / EJECUTA_INTERNO / AUTO_NOTIFICA. ACTIVO_BG (background) introduce un nivel **antes de PROPONE**: no genera outputs formales, solo emite flags + recomendaciones cuando un principio se cruza. No requiere aprobacion porque no propone acciones — solo razonamiento.

5. **Sin trigger word.** Otros skills tienen trigger explicito (`amazon-ops`, `kb-audit`, etc.). Este se activa por `trigger_context` (cualquier conversacion frontend). Decision tomada para que sea verdaderamente persistente — no requiere que CEO o agente lo invoque manualmente.

6. **No se actualizo ARCH_AGENT_PRINCIPLES.** El skill referencia los 14 principios fundacionales de ARCH_AGENT_PRINCIPLES pero NO los redefine ni extiende — los aplica al dominio frontend. Si en el futuro un principio frontend amerita promocion a fundacional, se hara via PR a ARCH separado.

## Por que en MWT/FaberLoom y como aplica

El skill aplica_a [FaberLoom] estrictamente. Razon: el system prompt original menciona "FaberLoom Design System" como ground truth canonico. Los 14 principios son aplicables a cualquier UI, pero el catalogo de flags (especialmente P11 OPERATIONAL_MUSCLE, P12 MODE_DISAMBIGUATION) hace referencia a surfaces especificas de FB (Workspace chat-first, Iterar object-first, Cotizacion document-first, Kanban triage, Evidence bundle, Skill Arena).

Si en el futuro Rana Walk monta un dashboard B2C, podria reusarse parcialmente — pero por ahora scope FB es mas honesto que [SHARED].

## Que NO se hizo

- **No se actualizo ARCH_AGENT_PRINCIPLES.md.** El skill consume canon, no lo extiende.
- **No se creo SKILL_MEM_FRONTEND_TEN_PRINCIPLES_V2.md (memoria).** Lentes ACTIVO_BG no tienen memoria propia — el aprendizaje vive en feedback CEO + iteraciones del archivo skill.
- **No se actualizo RW_ROOT.md.** El skill esta visible via IDX_PLATAFORMA. RW_ROOT puede actualizarse cuando promueva a VIGENTE post-validacion en mock real.
- **No se actualizo DEPENDENCY_GRAPH.md.** Skill nuevo, sin dependencias hacia archivos no-stub. Cuando se valide en mock real y consuma SPECs FB concretos, agregar dependencia ahi.
- **No se ejecuto la lente en un mock real.** Esta sesion es 100% documental — la validacion SHADOW requiere primera aplicacion a un mock FB (Workspace o Iterar) antes de promover a VIGENTE.

## Sync canonico requerido

Esta sesion es Cowork -> escribio en OneDrive. Para que cambios pasen al repo canonico (`C:\dev\mwt-knowledge-hub`):

1. Ejecutar `sync_frontend_skill_indexa.ps1` (creado en raiz del workspace) — copia los 4 archivos modificados/nuevos al repo canonico:
   - `docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` (nuevo)
   - `docs/SKILL_RUNTIME.md` (modificado)
   - `docs/IDX_PLATAFORMA.md` (modificado)
   - `docs/MANIFIESTO_APPEND_20260503b_FRONTEND_PRINCIPLES.md` (nuevo, este archivo)
   - `CLAUDE.md` (modificado)
2. CEO valida diff con `git diff`
3. CEO commitea con mensaje sugerido: `[PLATAFORMA] SKILL_FRONTEND_TEN_PRINCIPLES_V2 v2.1 SHADOW — lente cognitiva frontend FB`
4. Restaurar mirror oficial al final con `mirror_to_onedrive.ps1` (Push-Location al repo canonico antes)

## Proximas acciones

| Prioridad | Item | Bloqueo | Dueño |
|---|---|---|---|
| P1 | Validar lente en primer mock FB real (Workspace o Iterar) | — | CEO + Cowork |
| P2 (post-validacion) | Promover SHADOW -> VIGENTE si lente colorea sin friccion | Min 3 aplicaciones exitosas | CEO |
| P3 | Decidir si lente entra como Custom Instructions del Project | Validacion exitosa | CEO |
| P4 (futuro) | Evaluar si algun principio frontend amerita promocion a ARCH_AGENT_PRINCIPLES fundacional | Min 6 meses uso | CEO + arquitecto |

## Changelog

- 2026-05-03b · Creacion inicial. Indexado SKILL_FRONTEND_TEN_PRINCIPLES_V2 v2.1 SHADOW (lente cognitiva persistente, no agente con workflow). v2.0 (agente con 3 fases) creado y refactorizado el mismo dia tras clarificacion CEO. Total: 1 archivo nuevo (skill) + 3 modificados (SKILL_RUNTIME, IDX_PLATAFORMA, CLAUDE) + 1 manifiesto (este).
