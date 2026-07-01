# MWT_ARCHITECTURE_PACKAGE — Paquete Arquitectónico del Sistema
id: MWT_ARCHITECTURE_PACKAGE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-03-18

---

## Propósito

Paquete consolidado de referencia arquitectónica del sistema MWT. Referenciado por PLB_ORCHESTRATOR (FROZEN) como input obligatorio para sprints.

## Contenido (refs a docs vivos)

| Componente | Archivo canónico |
|-----------|-----------------|
| Infraestructura | ENT_PLAT_INFRA.md |
| Seguridad | ENT_PLAT_SEGURIDAD.md |
| Módulos | ENT_PLAT_MODULOS.md |
| State Machine | ENT_OPS_STATE_MACHINE.md (FROZEN) |
| Artefactos | ENT_PLAT_ARTEFACTOS.md |
| Design System | ENT_PLAT_DESIGN_TOKENS.md |
| Knowledge | ENT_PLAT_KNOWLEDGE.md |
| Eventos | ENT_PLAT_EVENTOS.md |
| Legal Entity | ENT_PLAT_LEGAL_ENTITY.md |
| LLM Routing | ENT_PLAT_LLM_ROUTING.md |

## Nota de gobernanza

Este archivo fue creado como materialización de la referencia `MWT_ARCHITECTURE_PACKAGE` usada en PLB_ORCHESTRATOR (FROZEN). El ORCHESTRATOR no puede editarse, así que el paquete se creó como documento consolidador que apunta a las fuentes canónicas actuales.

---

Changelog:
- v1.0 (2026-03-18): Creación. Trigger: auditoría ChatGPT — ref MWT_ARCHITECTURE_PACKAGE no existía.
