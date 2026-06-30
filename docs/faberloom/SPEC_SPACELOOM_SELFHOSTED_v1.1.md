---
id: SPEC_SPACELOOM_SELFHOSTED_v1_1
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-06-15 - post-auditoria dual (Kimi 7.1 + ChatGPT 6.7) - re-codeable
fecha: 2026-06-15
agente: Claude (Cowork) - Arquitecto Ejecutor
supersede: SPEC_SPACELOOM_SELFHOSTED_v1 (v1.0)
aplica_a: [FaberLoom, SpaceLoom]
---

# SPEC_SPACELOOM_SELFHOSTED_v1.1
## SpaceLoom self-embedded, distribuible, local-first (post-auditoria)

> Cambios vs v1.0: aplica las 2 auditorias. De ChatGPT (premisa): privacidad honesta + licencia que
> NO excluya uso profesional individual + matriz competitiva horizontal + quitar "Shared" + runtime
> guarantees + dogfood real desde SL0. De Kimi (ingenieria): esquema mas simple (sin routing_rule,
> audit a jsonl, agent diferido), sandbox de skills duro, PyInstaller + matriz OS, estimaciones,
> filesystem-native + offline-first como diferenciadores. Conflicto sqlite-vec: resuelto a favor de
> FTS5-primero (lean), vec como upgrade hibrido posterior, no obligatorio dia 1.

## 1. Decision y alcance

SpaceLoom es el telar general (workspaces heredables + grounding propio + HITL + memoria) entregado
**self-embedded y distribuible**, no como SaaS. Cada persona corre su copia, con su API key y su data local.
Alcance amplio (sirve a muchos), entrega liviana (1 proceso). No es recorte de alcance; es cambio de entrega.

## 2. Principios

1. Self-embedded: un proceso, una DB en archivo, cero servicios externos.
2. BYO-key: cada usuario pone su API key. El software no paga inferencia.
3. Local-first **con excepcion declarada**: la data vive local; el contexto enviado al LLM SI sale a la nube del proveedor que el usuario elija. No se vende "privacidad por arquitectura" a secas (correccion ChatGPT).
4. Config, no hardcode: configurable para cualquier dominio.
5. Skills como archivos markdown; **nunca ejecutados como codigo** (ver seguridad).
6. Defer agresivo: multi-tenant, inbox, code-exec, HTTP externo, multi-usuario concurrente, billing.
7. **Zero telemetry (NUEVO):** el proceso nunca abre conexiones a dominios del autor. Unica salida de red = el proveedor LLM que el usuario configura. Verificable: test de red en CI que falla si hay outbound a cualquier dominio que no sea el endpoint LLM.

## 3. Arquitectura

```
Python 3.12 + FastAPI (un proceso: API + UI local en 127.0.0.1)
SQLite + FTS5     -> workspaces, conversaciones, drafts, skills, KB, gold_samples
LiteLLM (lib)     -> routing multi-proveedor + fallback (Ollama first-class para offline)
UI web local (dark mode, acento naranja)
```

### 3.1 Runtime guarantees (NUEVO - correccion ChatGPT)

- SQLite: `PRAGMA journal_mode=WAL`, `busy_timeout=5000`, migraciones versionadas (numeradas).
- Ingestion: cola in-process (asyncio), un archivo a la vez, con limite de tamano (20MB/archivo) y manejo de archivo corrupto (skip + log, no crash).
- LLM: timeout por llamada (60s), retry con backoff (2 intentos), budget cap por sesion (config), cancelacion de streaming.
- Fallback policy: si el preset primario falla o devuelve salida que no valida contra el schema, cae al `fallback_model`.
- Contexto KB: maximo 4000 tokens inyectados por query (chunks 512 / overlap 50).
- Bind solo a `127.0.0.1`; CSRF token en la UI local.

## 4. Esquema (simplificado - correccion Kimi)

```sql
workspace(id, parent_id, name, type, color, settings_json, created_at)   -- type solo 'my' en v1 (Shared FUERA)
conversation(id, workspace_id, title, context_json, created_at, updated_at)
message(id, conversation_id, role, content, model_used, cost_usd, latency_ms, created_at)
draft(id, conversation_id, status, content_json, evidence_json, edit_pct, approved_at, created_at)
knowledge_item(id, workspace_id, title, content, level, source, source_hash, created_at)
knowledge_fts USING fts5(...)                                            -- SL2a
gold_sample(id, skill_id, input_json, output_json, source_draft_id, uses_count, created_at)
skill(id, name, spec_markdown, tools_allowlist, schema_output_json, is_active, created_at)  -- SL3a
agent(id, name, system_prompt, model_config_json, is_active, created_at)                    -- SL3+ (no SL1)
routing_preset(id, name, provider, model, temperature, max_tokens, fallback_model, is_default)
```

Eliminado vs v1.0:
- `routing_rule` (JSON dinamico): reemplazado por logica Python en `routing.py` (if-then). Tabla solo si se pasan 5 reglas.
- `audit_log` tabla: reemplazado por `audit.jsonl` append-only en disco, rotado mensual a `.jsonl.gz`.
- `agent` se crea recien en SL3 (en SL1 hay 1 agente "default" hardcodeado).
- `Shared` workspace: fuera de v1 (es promesa sin mecanismo: sin usuarios, sin permisos, sin sync).

## 5. Las piezas

- **Routing:** LiteLLM + presets (Eco/Balanceado/Sport+) + if-then en `routing.py` + PolicyGate (allow-list data_class, fail-closed). Fallback por preset. Ollama first-class.
- **SpaceLoom:** chat draft-first con streaming, contra la KB del workspace activo.
- **Workspaces + herencia:** `parent_id`; resolver contexto subiendo la cadena y mergeando KB + settings.
- **KB:** extractores por tipo (pandas Excel, pypdf/marker PDF, beautifulsoup HTML, MD/TXT nativo); chunk 512/overlap 50; `source_hash` para dedupe y reindex. FTS5 base; **sqlite-vec hibrido como upgrade posterior** (no dia 1).
- **Skills + gold:** SkillSpec markdown + schema (validado con pydantic/jsonschema) + tools allowlist; draft aprobado -> gold_sample -> few-shot.
- **HITL + evidence:** aprobar/editar/rechazar; evidence bundle = SHA-256(input) + skill_id + timestamp + model_used (no chain-of-custody forense - correccion Kimi).

## 6. Design tokens

- **Acento (accion/IA): NARANJA `--accent: #F97316`** (hover `#EA670C`, soft `#FB923C`). Reemplaza el coral del mock v4.15.
- Semanticos: sage exito/trazado · amber espera/asumido · vino error · slate neutro. Dark mode por capas. Serif titulos. 13.5px base.

## 7. Seguridad y privacidad (NUEVO - correccion ChatGPT + Kimi)

`SECURITY.md` requerido. Threat model minimo:

| Amenaza | Mitigacion |
|---|---|
| Contexto sale a LLM cloud | Banner "que sale al proveedor" antes de enviar; doc explicita; opcion Ollama offline |
| Prompt injection desde documentos/skills | Separar contenido de instrucciones; skills nunca ejecutados como codigo |
| Skill de tercero malicioso | Sandbox: markdown plano; allowlist SOLO `read_file`, `search_kb`, `format_output`; code-exec y HTTP externo **PROHIBIDOS** (no "deferred") |
| API key en texto plano | keyring/secret store del OS, no en el .db ni en config plano |
| Logs con prompts sensibles | logs redacted por default; LiteLLM con logging de mensajes apagado |
| Laptop robado / DB sin cifrar | Opcional SL2: SQLite cifrado (SQLCipher o passphrase) |
| Puerto local expuesto | bind `127.0.0.1` + CSRF token |
| Telemetria accidental | Zero-telemetry (principio 7) + test de red en CI |

## 8. Licencia y marca (NUEVO - correccion ChatGPT)

Problema detectado: PolyForm **Noncommercial** + "uso personal" **excluye al profesional que lo usa en su operacion real** (vos con MWT, un abogado con su bufete) — que es el caso de prueba mas valioso. Se descarta.

- **Licencia recomendada: FSL (Functional Source License).** Permite TODO uso incluido el comercial del usuario (un profesional lo usa en su trabajo: OK) y solo prohibe construir un producto **competidor**; convierte a Apache/MIT tras 2 anos. Resuelve el agujero de Noncommercial sin regalar el moat. **Eleccion final: [PENDIENTE - decision legal]** entre FSL y un dual-license custom.
- **Modelo dual:** gratis para individuos (incluido uso profesional individual); licencia comercial paga para empresas/equipos; oferta de comercial bajo demanda post-SL4.
- **Marca:** registrar FaberLoom/SpaceLoom (USPTO + EUIPO) **antes de SL3**. Trademark policy (que puede un fork, como se nombra una build no oficial). **CLA** obligatorio para contribuciones externas (copyright centralizado). Abogado ANTES de publicar, no despues.

## 9. Diferenciacion (reescrita - correccion ChatGPT)

Los competidores reales NO son verticales (Harvey/Pearl/ADP) sino horizontales local/AI-tooling: AnythingLLM, Open WebUI, Dify, LibreChat, LM Studio, ChatGPT/Claude Projects, Obsidian, Cursor/Continue. [PENDIENTE-VERIFICAR con matriz directa].

El moat no es SQLite ni BYO-key (eso es arquitectura, copiable). El moat es: **trabajo aprobado convertido en memoria reutilizable, versionada, portable y auditable (gold_samples + evidence)** + skills-como-archivos compartibles + starter packs por flujo. Diferenciadores tecnicos que un SaaS puro no replica sin canibalizarse:
- **Filesystem-native:** watch folders, drag-and-drop, abrir archivos con la app por defecto del OS.
- **Offline-first:** Ollama first-class con auto-deteccion; sin internet, funciona con modelo local.
- **Data gravity:** la memoria heredada por workspace no se exporta a un SaaS generico sin perder contexto.

Matriz comparativa a llenar (6 horizontales x criterios: data local, BYO-key, skills portables, HITL/gold loop, evidence bundle, offline). [PENDIENTE - construir en v1.2].

## 10. Etapas de desarrollo (re-partidas - correccion Kimi + ChatGPT)

Estimacion para 1 dev full-time. Cada etapa entrega valor usable (dogfood), no UI vacia.

| Etapa | Entrega | Gate | Sem |
|---|---|---|---|
| **SL0** | boot + DB + migraciones + config BYO-key + seed workspace "Alvaro Ops" + 10 knowledge_items MD seed + healthcheck + tokens naranja | corre en maquina limpia; existe workspace y datos seed; healthcheck verde | 1 |
| **SL1** | chat + LiteLLM + cost ledger + fallback + 1 agente default + **draft real desde KB seed** | draft util con evidencia minima desde la KB seed; se ve costo; fallback dispara | 1 |
| **SL2a** | workspaces + herencia + KB MD/TXT + FTS5 + citas | grounding citado por workspace; cambiar de workspace cambia contexto e historial | 1 |
| **SL2b** | extractor PDF + chunking + reindex | grounding citado desde PDF; archivo corrupto no rompe | 1 |
| **SL2c** | extractor Excel | grounding desde Excel (hojas/celdas) | 1 |
| **SL3a** | SkillSpec markdown + schema validation (pydantic) + tools allowlist | un skill corre end-to-end con salida validada | 1 |
| **SL3b** | HITL aprobar/editar/rechazar + evidence bundle (hash simple) | flujo de aprobacion completo; evidence guardado | 1 |
| **SL3c** | gold_sample + few-shot + metrica de mejora (edit_pct) | en N usos del mismo tipo, edit_pct baja | 1 |
| **SL4** | distribucion + polish | **un tercero no-tecnico instala y corre sin vos** | 2 |

**Total: ~10 semanas, 1 dev full-time.** SL4 no cuenta como dogfood interno (es distribucion).

### Distribucion (SL4) - 3 canales (correccion ChatGPT + Kimi)
- `uvx`/`pipx` = canal dev/interno.
- Docker = canal tecnico reproducible.
- **Desktop firmado (PyInstaller one-folder, Python embebido + SQLite + UI + modelos) = el gate del tercero no-tecnico.** No es "opcional"; es el canal que cumple "sin el autor".
- OS soportado: macOS 12+ (Intel/Apple Silicon), Windows 10+, Linux Ubuntu 20.04+. First-run: descarga modelos locales si se usa vec (descarga unica).

## 11. Fuera de alcance (deferred)

Multi-tenant/RLS, Shared workspaces, inbox IMAP/SMTP, envio externo, code-exec/HTTP en skills (PROHIBIDOS, no solo deferred), multi-usuario concurrente, billing, observabilidad self-hosted.

## 12. Pendientes [NO INVENTAR]

- Licencia final: [PENDIENTE - decision legal] (FSL recomendada vs dual custom).
- Matriz competitiva horizontal: [PENDIENTE - v1.2].
- sqlite-vec/embeddings: upgrade hibrido posterior, no dia 1.

## 13. Changelog

- v1.1 (2026-06-15): post-auditoria dual. Privacidad honesta (excepcion LLM declarada + threat model + zero-telemetry). Licencia: FSL recomendada (Noncommercial descartada por excluir uso profesional). Esquema simplificado (sin routing_rule, audit a jsonl, agent diferido, Shared fuera). Sandbox de skills duro (code-exec/HTTP prohibidos). Runtime guarantees. Etapas re-partidas SL0-SL4 (9 sub-etapas) con estimacion ~10 sem. Distribucion: desktop firmado como gate de tercero. Diferenciacion reescrita (rivales horizontales + filesystem-native + offline-first). Supersede v1.0. No toca FROZEN.
