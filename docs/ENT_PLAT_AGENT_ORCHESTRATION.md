# ENT_PLAT_AGENT_ORCHESTRATION — Patrones de Orquestación de Agentes
id: ENT_PLAT_AGENT_ORCHESTRATION
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
aplica_a: [SHARED]

---

## A. Propósito

Documenta los patrones de orquestación de agentes IA en MWT.ONE. Dos modelos coexisten: Paperclip (agentes en Claude.ai project) y Claude Code (agentes de desarrollo en terminal).

## B. Modelo Paperclip (KB + Skills)

Agentes que operan dentro del proyecto Claude.ai consumiendo la KB como contexto.

| Componente | Función |
|-----------|---------|
| Project instructions | Identidad + reglas base del arquitecto ejecutor |
| KB (project files) | Contexto: entities, policies, playbooks, schemas |
| SKILL_*.md | System prompt especializado por dominio |
| userMemories | Estado persistente entre sesiones |

**Flujo:** CEO → instrucción → Claude carga SKILL + KB refs → ejecuta → CEO valida

**Limitación:** ~200K tokens de context window. KB de ~85K tokens post-depuración deja ~115K para trabajo.

## C. Modelo Claude Code (Desarrollo)

Agentes de desarrollo (AG-02, AG-03) que operan en terminal con acceso al repo.

| Componente | Función |
|-----------|---------|
| PROMPT_ANTIGRAVITY | System prompt completo del sprint |
| GUIA_ALE | Instrucciones paso a paso para AG-02 |
| LOTE_SM_SPRINT* | Spec del sprint con items, gates, criterios |
| Repo Git | Código fuente MWT.ONE |

**Flujo:** Arquitecto genera LOTE + GUIA + PROMPT → AG-02 ejecuta en Claude Code → CEO revisa PR → merge

## D. Coordinación entre modelos

| Escenario | Orquestador | Ejecutor |
|-----------|-------------|----------|
| Sprint de plataforma | Arquitecto (Paperclip) | AG-02/AG-03 (Claude Code) |
| Auditoría KB | SKILL_KB_AUDITOR (Paperclip) | Mismo agente genera reporte |
| Consulta cliente B2B | SKILL_CLIENT_SERVICE (Paperclip) | Django procesa via {intent, params} |
| Proforma nueva | SKILL_PROFORMA_BUILDER (Paperclip) | CEO valida antes de registrar |
| Experiment Amazon | SKILL_EXPERIMENT_RUNNER (Paperclip) | CEO aprueba antes de launch |

## E. Regla de seguridad

La IA nunca toca el ORM directamente. El flujo es:

1. IA clasifica intención del usuario
2. IA extrae `{intent, params}` estructurado
3. Django ejecuta la query/comando con ClientScopedManager
4. Django retorna resultado filtrado
5. IA formatea respuesta para el usuario

Ref → ENT_PLAT_SEGURIDAD para framework completo.

---

Changelog:
- v1.0 (2026-04-01): Creación inicial. Dos modelos documentados: Paperclip + Claude Code.
