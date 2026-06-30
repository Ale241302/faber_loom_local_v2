---
id: SPEC_SPACELOOM_SELFHOSTED_v1_2
version: 1.2
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-06-17 - extiende v1.1 con modelo de agente-entidad (single-user) + SKILL.md
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
extiende: SPEC_SPACELOOM_SELFHOSTED_v1.1 (todo lo no tocado aca sigue vigente)
fuente_adicional: ARCH_FB_AGENT_RUNTIME_EVAL_v1 (modelo de agente; aca en version single-user lightweight)
---

# SPEC_SPACELOOM_SELFHOSTED_v1.2 (addendum)
## Modelo de agente-entidad para single-user + skills en SKILL.md

> Este addendum NO reescribe v1.1; agrega dos cosas y precisa una linea. Todo lo demas de v1.1
> (stack, runtime guarantees, seguridad, licencia, etapas, distribucion) sigue igual.

## A. Por que este addendum

El `ARCH_FB_AGENT_RUNTIME_EVAL` traia el modelo de "agente por tenant". En v1.1 lo fileteé entero
como "multi-tenant deferido". Error: parte de ese modelo **agrega valor a la interaccion aunque seas
un solo usuario** y es lo que hace que SpaceLoom se sienta vivo (lo que Alvaro vio en Kimi Work).
La linea correcta:

- **Sello CRIPTOGRAFICO + aislamiento hostil cross-tenant** (Container/VM, RBAC+ABAC, SMTA 92%): sigue DEFERIDO. Solo si/cuando haya multi-tenant. En single-user, scoping local alcanza.
- **Modelo de agente-entidad** (identidad persistente, memoria sellada por workspace, indice-vs-contenido, llave graduada, proactividad, particion embebido/gobierno): **se adopta ahora**, en version liviana single-user. No necesita cripto.

## B. Cambio 1 - Skills en formato SKILL.md (correccion del swarm)

Las skills de SpaceLoom usan **SKILL.md (YAML frontmatter, estandar AgentSkills)**, no un markdown propio.
Razon (swarm AOSS): es el formato portable que ya usan OpenHands/Hermes/OpenClaw y Claude Code/Cowork;
deja las skills portables entre runtimes y alineadas con las `SKILL_` de la KB. Reemplaza la mencion
generica de "markdown" en v1.1 sec 5. El sandbox de v1.1 sec 7 sigue igual (skills nunca como codigo,
allowlist read_file/search_kb/format_output, marketplaces = veneno: no instalar sin auditar).

## C. Cambio 2 - Modelo de agente-entidad (single-user, lightweight)

1. **Identidad persistente e inmutable-en-sesion.** El agente tiene una personalidad estable (valores, estilo, forma de razonar) que viaja entre workspaces pero es read-only durante la sesion. No se reescribe con lo aprendido en un workspace -> no se vuelve canal de fuga al siguiente. Implementacion: `agent.identity_md` (markdown), cargado read-only.

2. **Memoria sellada por workspace + visibilidad.** El contexto/memoria de un workspace NO entra a otro. La herencia legitima es solo hacia abajo via `parent_id` (hijo hereda del padre), nunca lateral entre hermanos ni hacia arriba. Enforcement = scoping local en la query (no cripto; es single-user, vos sos dueno de todo, pero no querés que Rana Walk se cuele en un workspace de cliente). Namespacing por `workspace_id` + `visibility`.

3. **Indice global vs contenido sellado (saber-que vs saber-que).** El agente puede saber QUE existe algo y DONDE (metadata/punteros), pero el CONTENIDO de otro workspace queda sellado salvo que estes en el o abras la llave. Implementacion: tabla `existence_index(workspace_id, title, kind, visibility)` — solo metadata, sin contenido.

4. **Llave graduada por politica (la controlas vos).** Tres posiciones: cerrada / indice-abierto (default sano: el agente responde "tenes un doc sobre X en el workspace Y", no su contenido) / contenido-abierto (cross-workspace, alto, explicito). La cambia el owner (vos), queda en `audit.jsonl`. El agente nunca tiene la llave.

5. **Proactividad (el "se siente vivo").** Loop = persistencia + identidad continua + memoria episodica + reactividad + PROACTIVIDAD. La proactividad (que aborde primero: "vi que llego X, te preparo el draft?") es lo que cruza de herramienta a entidad. Es lo que querés. Se dosifica por visibilidad: max en lo repetitivo/comercial, minima/efimera en lo sensible. Se trata como software determinista para seguridad, no como criterio propio.

6. **Particion embebido vs gobierno.** Procesos deterministas que el agente invoca -> embebidos como skills/tools. Acciones irreversibles (NEVER: enviar, borrar, firmar) -> FUERA del agente, gate humano (ya cubierto por HITL en v1.1). El agente propone, no dispone. En single-user el "plano de gobierno" no necesita n8n: una funcion-gate local + el HITL alcanzan.

## D. Esquema - delta sobre v1.1

```sql
agent           : + identity_md TEXT            -- personalidad persistente read-only
workspace       : + visibility TEXT             -- my/confidential/etc, para sellar memoria
knowledge_item  : + visibility TEXT
existence_index(id, workspace_id, title, kind, visibility, created_at)  -- saber-que/saber-donde, sin contenido
key_state(id, scope, position, set_by, set_at)  -- cerrada/indice/contenido por scope, auditable
```

(Sigue sin `routing_rule`, sin `audit_log` tabla -> `audit.jsonl`, sin Shared workspace; igual que v1.1.)

## E. Donde entra en las etapas

- **SKILL.md:** desde SL3a (cuando aparecen skills). Sin costo extra.
- **Identidad persistente (`identity_md`) + proactividad basica:** SL3 (con agentes).
- **Memoria sellada por workspace + visibilidad:** SL2a (cuando entran workspaces; es scoping de la query, barato).
- **Indice global vs contenido + llave graduada:** SL3.5 (nueva sub-etapa corta, ~0.5-1 sem) despues de SL3c. Gate: el agente responde "donde" sin filtrar "que" de otro workspace; abrir la llave es explicito y queda en audit.jsonl.

Total revisado: ~10.5-11 semanas (v1.1 eran ~10; +0.5-1 por SL3.5).

## F. Lo que SIGUE deferido (no re-inflar)

Sello criptografico de memoria, aislamiento hostil cross-tenant, Container/VM, RBAC+ABAC, namespace isolation grado-SMTA, meta-agente curador que promueve a canonico, broker mediador multi-tenant. Todo eso es del FaberLoom multi-tenant (ARCH_FB_AGENT_RUNTIME_EVAL, PAUSADO). En single-user, el scoping local + la llave graduada + el HITL alcanzan. Se sube a cripto solo cuando otra persona comparta tu infra.

## G. Changelog

- v1.2 (2026-06-17): addendum a v1.1. Adopta el modelo de agente-entidad en version single-user lightweight (identidad persistente, memoria sellada por workspace+visibilidad, indice-vs-contenido, llave graduada, proactividad, particion embebido/gobierno) — sin cripto, que queda deferido a multi-tenant. Skills pasan a formato SKILL.md (estandar AgentSkills, correccion del swarm). Delta de esquema (identity_md, visibility, existence_index, key_state). Nueva sub-etapa SL3.5 (~0.5-1 sem). Corrige el sobre-filtrado de v1.1 que habia deferido todo el modelo de agente. No toca FROZEN.
