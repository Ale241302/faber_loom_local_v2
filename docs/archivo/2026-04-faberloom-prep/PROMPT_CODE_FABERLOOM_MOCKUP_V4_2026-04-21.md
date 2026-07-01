# PROMPT_CODE_FABERLOOM_MOCKUP_V4 — Handoff Cowork → Claude Code
fecha: 2026-04-21
autor: Álvaro (CEO) vía Cowork
target: Claude Code sesión nueva
input: mockup v3.5 (`MWT KB/faberloom-mockup/index-standalone.html` 461 KB · 7935 líneas · 27 fragments)
output: mockup v4.0 con mejoras iteradas post Kimi Swarm #4 + canonización FaberLoom Architecture v1 Blueprint

---

## 1. Objetivo

Iterar mockup v3.5 → v4.0 absorbiendo 3 oleadas de cambios canonizados en la KB:

1. **SPEC_FABERLOOM_SKILL_COMPOSITION v1** (Sealed/Open, 5 Add-ons originales)
2. **SPEC_FABERLOOM_AGENT_COMPOSITION v1** (Agent = instancia operativa con skills + canales + position + autonomy)
3. **ENT_PLAT_LLM_ROUTING v2.0 post Kimi Swarm #4** → remover Arena Mode, sumar Voice Profile (6º Add-on), tiered hardcoded routing F1, data residency hard block, HA LiteLLM, circuit breakers, cold start 30d, F2 adaptive postpuesto gated

El mockup debe reflejar F1 como build-ready y F2 como roadmap visible pero sin implementación UI.

---

## 2. Scope segmentado — TRES ALCANCES

### 2.1 F1 CANONIZADO — build-ready (implementar completo en v4.0)

Todo lo listado aquí YA tiene SPEC/ENT canonizado. Implementar UI funcional (mock data OK, backend no necesario).

#### A. LLM Orchestration — 4 tiers hardcoded
- **Tabla visual de 4 tiers** en config global (no por agente):
  - `simple` → gemini_flash · max_cost $0.01 · fallback: [gpt_4o_mini, kimi_k2]
  - `medium` → kimi_k2 · max_cost $0.05 · fallback: [deepseek_v3, gpt_4o_mini]
  - `complex` → sonnet_4_6 · max_cost $0.50 · fallback: [opus_4_6]
  - `local_only` → ollama_llama_3_2_3b · max_cost $0.00 · fallback: []
- **Origen:** YAML en git (`faberloom/config/llm_tiers.yaml`). UI debe mostrar "editable solo vía commit + PR" (read-only en UI, botón "Ver en GitHub" que linkea a dummy URL).
- **NO mostrar** Arena Mode, evidence ledger, weekly tuning, shadow mode, MAB, ni nada adaptive. Todo eso es F2.

#### B. tenant_model_allowlist — Data Residency (Admin Console)
- Nueva tabla en Admin Console → sección "Compliance · Data Residency".
- Por tenant: lista de modelos permitidos con checkbox y motivo ("GDPR", "LGPD", "CEO-ONLY no CN", etc.).
- **Hard block visual:** si un workflow intenta rutear a un modelo fuera del allowlist, mostrar toast rojo "BLOCKED: model X not in tenant allowlist (reason: GDPR)" antes del tier-check.
- Defaults por plan:
  - Starter → ["gemini_flash", "gpt_4o_mini", "kimi_k2"]
  - Pro → +sonnet_4_6
  - Enterprise → +opus_4_6 + ollama_llama_3_2_3b
  - CEO-ONLY → SOLO US models (bloquea kimi, deepseek, ollama si es local CN)

#### C. Circuit Breaker Status — Observabilidad
- Nuevo widget en Admin Console → "Infra Health".
- 2 niveles: Provider-level (Anthropic/OpenAI/Google/Groq/Moonshot/DeepSeek/Ollama) · Model-level (cada modelo del registry).
- Estados: 🟢 Closed (healthy) · 🟡 Half-open (1 req probing) · 🔴 Open (blocked).
- Thresholds visibles: "Opens: 50% error rate over 20 requests · Half-open: 1 req probe · Closes: <10% error over 10 requests".
- Debe mostrar Redis como fuente de estado ("state: redis://cb:anthropic:claude_sonnet_4_6").

#### D. HA LiteLLM — Infra status
- Admin Console → Infra Health → bloque "LiteLLM HA".
- 2 instancias: `litellm-primary:4000` · `litellm-backup:4001`.
- HAProxy frontend con health check cada 10s (mostrar ping visual).
- Failover banner: si primary down > 30s, mostrar "Failover active → backup serving".

#### E. Cold Start Banner — 30 días
- Banner en dashboard principal para tenants nuevos: "Cold Start Mode · 30 days remaining · YAML defaults active · CEO review weekly".
- Contador regresivo visual.
- Tras día 30 → banner desaparece + se habilita edición de `tenant_model_allowlist` por el tenant admin (antes era solo CEO).

#### F. Voice Profile — 6º Add-on (NUEVO, reemplaza slot Arena)
- En Skill Studio → sección Add-ons, sumar "Voice Profile" como 6º toggle.
- Configuración a nivel **tenant** (no per-skill).
- Campos:
  - Tono: [formal / casual / neutral / técnico]
  - Terminología bloqueada: textarea (palabras prohibidas)
  - Terminología preferida: textarea (sinónimos a forzar)
  - Idioma primario: dropdown (ES-LATAM / PT-BR / EN-US / etc.)
  - Firma default: textarea
- Aplicación: se inyecta en system prompt de todos los agentes del tenant automáticamente.
- **Sealed agents**: Voice Profile se aplica como overlay, no modifica la skill base.
- **Open agents**: Voice Profile es parte del fork editable.

#### G. Cambios en agent detail view
- Sumar campo **Position** (org-role del agente: "Executive Assistant", "Sales Rep", "Customer Support Tier 1", etc.) — influye en tono y escalamiento.
- Sumar campo **Authority** (matriz L0-L4 × Authority):
  - L0 Suggestion · L1 Draft · L2 Execute-low-risk · L3 Execute-medium · L4 Autonomous
  - Authority level es independiente de autonomy level (autonomy = cuánto asume, authority = qué puede firmar).
- Mostrar ambos como sliders separados.

#### H. Sealed vs Open badge
- En cada skill card y agent card, badge visual:
  - 🔒 **Sealed** → no editable, solo Add-ons
  - 🔓 **Open** → forkeable, editable
- Botón "Fork to Open" en sealed skills (CTA principal cuando usuario intenta editar).

---

### 2.2 F2 DIFERIDO — mostrar como roadmap visible (NO implementar)

Todo lo que sigue va como **cards grises con badge "Coming in F2"** en una pestaña/sección "Roadmap" del Admin Console. NO implementar funcionalidad. NO mostrar como opciones activas.

#### F2.A — Adaptive Routing
- Card: "Adaptive Routing — Auto-tuning based on real usage"
- Gate visible: "Unlocks when: 3 tenants × 5,000 drafts/mes × 3 meses sostenido"
- Progress bar placeholder: "0 / 3 tenants qualified"
- Listar features que llegarán: per-tenant evidence ledger · weekly policy tuning · concept drift detection (Page-Hinkley/ADWIN) · MAB híbrido Thompson+ε-greedy · pesos aprendidos via logistic regression · N≥500 per comparison · 4-eyes workflow + firma digital SOC 2 · sintético shadow testing

#### F2.B — Arena Mode
- Card: "Arena Mode — Head-to-head model testing with human vote"
- Badge: "Deferred F2 · gated to Adaptive unlock"
- Rationale visible: "Discarded from F1: beta volume insufficient for N≥20 per model-pair comparison"

#### F2.C — Research Swarm con critic
- F1 implementa Research Swarm SIN critic (paralelo → merge directo).
- F2 card: "Adversarial Critic — Second-pass validation of swarm output"
- NO implementar tab de critic config en F1.

**Convención visual:** todas las cards F2 deben usar el token `--fl-muted-bg` (gris amortiguado) + `--fl-text-secondary`. El usuario no debe confundir F2 con F1 disponible.

---

### 2.3 BLOQUEADO POR Q1-Q18 — placeholders con flag

Hay 18 preguntas abiertas al CEO (ENT_GOB_PENDIENTES v13.0 track FaberLoom LLM Orchestration). 7 P0 bloquean spec final. Mientras no estén resueltas, implementar placeholders con valores default razonables + **badge "⚠ Pending CEO decision"** + tooltip con Q#.

Lista completa de Q1-Q18 está en `docs/ENT_GOB_PENDIENTES.md` sección "Open questions post-Kimi Swarm #4 — LLM Orchestration". Pegar las 18 en un panel escondible "Open Questions (18)" en Admin Console → Settings → Governance, para que sean visibles al CEO dentro del mockup.

**Ejemplos de placeholders bloqueados:**
- Fernet key rotation cadence → default "90 días" + ⚠ Q12
- Langfuse endpoint → default "langfuse.faberloom.internal" + ⚠ Q15
- Alerting destination → default "Slack #faberloom-ops" + ⚠ Q16
- Circuit breaker exact thresholds → defaults del blueprint + ⚠ Q7
- tenant_model_allowlist defaults por plan → usar defaults §2.1.B + ⚠ Q9

El CEO debe poder ver el placeholder, entender que es provisional, y saber cuál pregunta responder para destrabarlo.

---

## 3. Cambios UI concretos desde v3.5 — DIFF resumido

### REMOVE
- ❌ Arena Mode tab (reemplazar por Voice Profile en el slot del 6º Add-on)
- ❌ Evidence ledger UI (era para adaptive)
- ❌ Weekly tuning config panel
- ❌ Shadow mode toggle
- ❌ Policy proposal workflow UI

### ADD
- ➕ Voice Profile (6º Add-on) — Skill Studio
- ➕ tenant_model_allowlist — Admin Console · Compliance
- ➕ Circuit Breaker Status — Admin Console · Infra Health
- ➕ LiteLLM HA status — Admin Console · Infra Health
- ➕ Cold Start Banner — Dashboard principal (tenant-level)
- ➕ Position field — Agent detail
- ➕ Authority slider (L0-L4) — Agent detail
- ➕ Sealed/Open badges — cada skill + agent card
- ➕ "Fork to Open" CTA en sealed skills
- ➕ Roadmap tab — Admin Console (F2 cards)
- ➕ Open Questions panel — Admin Console · Governance (18 Qs)

### UPDATE
- 🔄 LLM Orchestration view → ahora tiered 4 levels read-only (con link a GitHub YAML)
- 🔄 Agent detail → autonomy + authority separados (antes solo autonomy)
- 🔄 Skill cards → badge Sealed/Open
- 🔄 System prompt preview → mostrar capas: base · Voice Profile · Add-ons · (si es Open) custom

### NO TOCAR
- Autonomy Ladder L0-L4 (canonizado en ARCH_AGENT_PRINCIPLES P0-P13)
- Draft-first policy (canonizada P13 Contención)
- RLS visual en Knowledge Scope (4 niveles: private/team/company/public)
- Bandeja bidireccional (D11 v3.5)
- Task launcher ⌘K
- Paleta dark/light actual (AUDIT_FABERLOOM_A3 canonizada)
- Estructura de 11 rutas principales

---

## 4. Referencias KB canonizadas

Leer en este orden antes de implementar:

1. `docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` — schema 30 tablas S1 (v1.0 DRAFT, bump a final post Q1-Q18)
2. `docs/SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md` — Sealed/Open + 5 Add-ons + fork path
3. `docs/SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md` — Agent=instancia, matriz L0-L4 × Authority
4. `docs/SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` — pg-boss F1 + 4 patrones handoff + sandwich contención
5. `docs/ENT_PLAT_LLM_ROUTING.md` v2.0 — §F FaberLoom F1 tiered hardcoded · §H separación MWT vs FaberLoom
6. `docs/ENT_GOB_DECISIONES.md` v2.0 — DEC-006/007/008
7. `docs/ENT_GOB_PENDIENTES.md` v13.0 — Q1-Q18 completas
8. `docs/archivo/kimi_swarm_4_adaptive_routing.md` — fundamento técnico del downgrade
9. `docs/ARCH_AGENT_PRINCIPLES.md` v1.2 — P0-P13 (P13 Contención clave para UI draft-first)
10. `docs/AUDIT_FABERLOOM_A3_DARK_PALETTE_v1.md` — tokens CSS canonizados
11. `docs/AUDIT_FABERLOOM_B1_SERVICE_BLUEPRINT_v1.md` — 14 módulos × 4 capas
12. `docs/FABERLOOM_MOCKUP_CHANGES_F1_v3.6.md` — changes parciales acumulados (si existe)
13. `docs/MANIFIESTO_APPEND_20260421_LLM_ORCHESTRATION.md` — gate report de esta iteración

---

## 5. Preguntas a hacer al CEO antes de asumir

Si se topa con ambigüedad, NO inventar. Preguntar en bloque al final de la sesión. Candidatos probables:

- ¿Voice Profile se configura 1 per tenant o permite N profiles seleccionables por agente?
- ¿El botón "Fork to Open" requiere confirmation modal con disclaimer "⚠ You lose future automatic updates to base skill" o es instantáneo?
- ¿Cold Start Banner debe mostrarse también al admin durante los 30 días o solo al CEO del tenant?
- ¿Circuit Breaker Status debe permitir manual override (botón "Force open" / "Force close") en UI o es read-only?
- ¿Authority level (L0-L4) se setea por agente globalmente, o puede variar por canal (Slack vs email)?
- ¿Los 18 placeholders Q1-Q18 se muestran al admin del tenant o solo al CEO MWT?

---

## 6. Entregables esperados

1. **Código modular en `faberloom-mockup/`** — NO reescribir monolito. Editar fragments existentes + crear nuevos fragments para bloques F1 nuevos (voice-profile.html, tenant-allowlist.html, circuit-breaker.html, ha-status.html, cold-start-banner.html, roadmap-f2.html, open-questions-panel.html).
2. **`index-standalone.html` rebuild** vía `python build.py` (mismo flujo v3.5).
3. **`AC_V4_v1.md`** — acceptance criteria con cumulative count esperado (94 prev + nuevos de v4).
4. **`DELIVERY_NOTES_V4.md`** — changelog, byte size, LOC, screenshots clave.
5. **`CHANGES_F1_v4.0.md`** — diff completo por archivo.
6. **Handoff back a Cowork** para indexación (archivo `HANDOFF_V4_TO_COWORK.md` con las 6 preguntas CEO pendientes + cualquier OQ nuevo surgido durante build).

### Criterios de "Done"
- `node --check` pasa en todos los JS inline.
- `axe-core` 0 violations críticas (WCAG 2.1 AA static).
- No hay referencias residuales a "Arena", "evidence ledger", "adaptive routing" en F1 (salvo en Roadmap F2 tab).
- Voice Profile visible como 6º Add-on con tooltip "New — canonizado 2026-04-21".
- Placeholders Q1-Q18 todos con flag ⚠ + tooltip explicativo.
- Sealed/Open badges consistentes en skills + agents.

---

## 7. Fuera de scope v4.0

- Fase 2 SPECs (RESEARCH_SWARM, KNOWLEDGE_BROKER, SWARM_PLANNER, INVOCATION_REGISTRY) → bloqueados hasta Q1-Q18 P0 resueltas por CEO.
- Backend real (todo mock data, JSON estático).
- Build adaptive routing (F2, gated).
- Schema DB real (mantener staging tables S1 del blueprint, no migrar a prod).

---

## 8. Stamp

HANDOFF VIGENTE desde 2026-04-21. Target delivery: v4.0 mockup con 3 alcances claramente separados (F1 build / F2 roadmap / Q1-Q18 placeholder). Next gate: cuando CEO responda Q1-Q18 P0 → iteración v4.1 con valores reales.
