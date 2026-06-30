---
id: SPEC_SPACELOOM_SELFHOSTED_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-06-15 - blueprint self-embedded distribuible - listo para auditoria
fecha: 2026-06-15
agente: Claude (Cowork) - Arquitecto Ejecutor
aplica_a: [FaberLoom, SpaceLoom]
relacionado_con:
  - ENT_FB_USE_CASE_CATALOG_v1 (los usos que el telar sirve)
  - PLAN_DESARROLLO_FABERLOOM_v4 (superseded para esta version self-host; el v4 era el SaaS)
  - faberloom_shell_mock_v4_15 (referencia visual)
---

# SPEC_SPACELOOM_SELFHOSTED_v1
## SpaceLoom self-embedded, distribuible, local-first

## 1. Decision y alcance

SpaceLoom es el **telar general** (no una app por industria, no una version recortada de MWT): workspaces heredables que se autoenriquecen, donde un profesional hace su trabajo con grounding propio + aprobacion humana (HITL) + memoria. Sirve a muchos.

Lo que cambia vs el plan v4 NO es el alcance, es la **entrega**: en vez de un SaaS hosteado, es un producto **self-embedded y distribuible** donde cada persona corre su copia, con su propia API key y su data en su maquina. Licencia de uso personal.

Esto resuelve, por arquitectura, lo que el SaaS no podia: multi-tenant (no existe), peaje AI Act (cada usuario es su deployer; se shippea software), costo de inferencia (BYO-key), y GTM de hostear (es descarga e instala). Ademas es una posicion que un incumbente financiado (Harvey, Pearl, ADP) no puede copiar sin canibalizar su renta de SaaS.

## 2. Principios

1. **Self-embedded:** un proceso, una base de datos en archivo, cero servicios externos.
2. **BYO-key:** cada usuario pone su API key de LLM. El software no paga inferencia.
3. **Local-first:** la data del usuario vive en su maquina. Su privacidad es por arquitectura.
4. **Config, no hardcode:** nada de MWT clavado adentro; configurable para cualquier dominio.
5. **Skills como archivos:** un skill es un markdown que el usuario escribe y comparte.
6. **Defer agresivo:** multi-tenant, inbox IMAP/SMTP, code-exec, HTTP externo, multi-usuario concurrente quedan FUERA hasta que duelan.

## 3. Arquitectura

```
Python 3.12 + FastAPI (un proceso: API + UI local)
SQLite con FTS5   -> workspaces, conversaciones, drafts, skills, agentes, KB, gold_samples
LiteLLM (lib)     -> routing multi-proveedor + fallback, sin proxy
UI web servida por el mismo proceso (dark mode, acento naranja)
```

Flujo de una iteracion (todo en RAM de un proceso):

```
pedido -> PolicyGate (allow-list data_class) -> router elige preset
       -> arma contexto: workspace activo + herencia de padres + KB (FTS5) + gold_samples similares (few-shot)
       -> LiteLLM llama al modelo -> draft con schema de salida
       -> HITL: aprobar / editar / rechazar (+ evidence bundle SHA-256)
       -> draft aprobado se guarda como gold_sample -> mejora el siguiente
```

Sin Postgres, Redis, Celery, Caddy, auth/OAuth. Backup = copiar el archivo `.db`.

## 4. Esquema SQLite (minimo)

```sql
workspace(id, parent_id, name, type, color, settings_json, created_at)         -- parent_id = herencia
conversation(id, workspace_id, title, context_json, created_at, updated_at)
message(id, conversation_id, role, content, model_used, cost_usd, latency_ms, created_at)
draft(id, conversation_id, status, content_json, evidence_json, edit_pct, approved_at, created_at)
knowledge_item(id, workspace_id, title, content, level, source, created_at)
knowledge_fts USING fts5(title, content, content=knowledge_item)               -- grounding
gold_sample(id, skill_id, input_json, output_json, source_draft_id, uses_count, created_at)
skill(id, name, spec_markdown, tools_allowlist, schema_output_json, is_active, created_at)
agent(id, name, system_prompt, model_config_json, is_active, created_at)
routing_preset(id, name, provider, model, temperature, max_tokens, fallback_model, is_default)
routing_rule(id, condition_json, action_json, priority, is_active)
audit_log(id, action, entity_type, entity_id, diff_json, created_at)           -- append-only, local
```

## 5. Las 5 piezas

- **Routing:** LiteLLM lib + `routing_preset` (Eco/Balanceado/Sport+) + `routing_rule` (if-then) + PolicyGate (funcion fail-closed antes de la llamada). Fallback por preset.
- **SpaceLoom:** chat draft-first con SSE/streaming, una conversacion por contexto, contra la KB del workspace activo.
- **Workspaces + herencia:** `workspace.parent_id`; al resolver contexto se sube por la cadena y se mergea KB + settings. My / Shared como tipo.
- **Agentes:** `agent(system_prompt, model_config)`, configurables.
- **Skills + gold:** SkillSpec = markdown + tools allowlist + schema JSON; salida validada contra el schema; cada aprobacion -> gold_sample reusable como few-shot (memoria que mejora).

## 6. Design tokens

- **Acento (accion / IA): NARANJA** `--accent: #F97316`. Estados derivados: `--accent-hover: #EA670C`, `--accent-soft: #FB923C`. (Reemplaza el coral `#ffb59d` del mock Stitch v4.15.)
- Semanticos: `--sage` exito/aprobado/trazado · `--amber` espera/asumido · `--vino` error/bloqueo · `--slate` neutro.
- Dark mode por capas (sunken -> canvas -> surface -> raised) + luz cenital sutil. Serif (Georgia/Source Serif) para titulos. 13.5px base.

## 7. Tensiones self-embedded (honestas) + regla de skills

1. Busqueda semantica a gran escala: FTS5 (keyword) alcanza para KB personal; `sqlite-vec`/embeddings local es opcional, no dia 1.
2. LLM 100% offline: posible via Ollama (LiteLLM le habla) pero calidad depende del hardware. Default = BYO-key nube.
3. Skills que ejecutan codigo o HTTP externo: piden sandbox y rompen lo embebido. **Regla: skills = LLM + KB + herramientas locales (leer/buscar/formatear). Code-exec y HTTP externo = opt-in, despues.**
4. Multi-usuario concurrente: SQLite (WAL) aguanta pocos; el modelo es 1 copia por persona. No es un bug, es el diseno.

## 8. Licencia y marca

- **Codigo:** PolyForm Noncommercial (gratis para uso personal/no-comercial; todo lo comercial reservado al autor). Mantiene viva la opcion de girar a comercial despues.
- **Marca:** registrar FaberLoom/SpaceLoom aparte del codigo. La marca es moat barato aunque el codigo sea visible.

## 9. Etapas de desarrollo (lean, dogfood cada una)

Cada etapa produce algo que Alvaro USA en su operacion esa misma semana.

**SL0 - Esqueleto (gate: corre en maquina limpia)**
Repo + un proceso FastAPI + esquema SQLite (se crea solo) + config BYO-key + licencia PolyForm + tokens (naranja). UI vacia navegable. Distribuible via `uvx`/`pipx`.
Gate: `uvx spaceloom` levanta, sin login, crea su `.db`, muestra UI.

**SL1 - Routing + Chat (gate: chateas con costo y fallback)**
LiteLLM + presets + reglas + PolicyGate; chat draft-first; cost ledger en SQLite.
Gate: respondes con un modelo, ves costo por mensaje, el fallback dispara si el primario cae.

**SL2 - Workspaces + herencia + KB (gate: grounding por workspace)**
Crear workspaces con parent_id; subir PDF/MD/Excel; chunk + FTS5; contexto del workspace inyectado, hereda del padre.
Gate: respuesta citada de la KB del workspace; cambiar de workspace cambia el contexto y el historial.

**SL3 - Skills + Agentes + HITL + gold (gate: el telar cierra el loop)**
SkillSpec markdown + schema + allowlist; agentes configurables; HITL aprobar/editar/rechazar + evidence bundle; draft aprobado -> gold_sample -> few-shot.
Gate: un skill end-to-end; aprobas; en N usos el edit_pct del mismo tipo de tarea baja (la memoria mejora).

**SL4 - Distribucion (gate: un tercero lo corre sin vos)**
Empaque pulido (docker/uvx + opcional desktop one-click Tauri/PyInstaller) + starter pack de skills + README + licencia.
Gate: alguien que no sos vos instala y corre una tarea real sin ayuda.

## 10. Fuera de alcance (deferred, no construir ahora)

Multi-tenant/RLS, inbox IMAP/SMTP, envio externo automatico, code-exec en skills, HTTP externo en skills, multi-usuario concurrente, embeddings semanticos, observabilidad self-hosted, billing. Se agregan cuando duelan, no por las dudas.

## 11. Changelog

- v1.0 (2026-06-15): blueprint inicial self-embedded distribuible. Alcance = telar general; entrega = local-first personal-use. Stack 1 proceso + SQLite/FTS5 + LiteLLM. Acento naranja #F97316. Etapas SL0-SL4. Licencia PolyForm Noncommercial. Supersede el plan v4 para esta version (el v4 era el SaaS hosteado). No toca FROZEN.
