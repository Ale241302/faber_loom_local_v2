# PLB_AI_GOV_DUAL_REVIEW
aplica_a: [MWT, FaberLoom]
## Playbook: Revisión Cruzada Dual-LLM para Decisiones Técnicas

---

id: PLB_AI_GOV_DUAL_REVIEW
version: 1.0
domain: Gobernanza (IDX_GOBERNANZA)
subfamilia: AI_GOV
status: VIGENTE
visibility: [INTERNAL]
owner: CEO (delegable a tech leads / decision-makers)
stamp: VIGENTE — 2026-05-01
vencimiento: 2026-08-01 (revisión trimestral)
modo: prescriptivo MVP (ejecutable post Action Engine F1, ver §Modo de operación)
requires:
  - SPEC_AI_GOV_GOVERNANCE_AND_ROUTING
  - SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (Token Ledger campos role + parent_request_id)
  - SCH_AI_GOV_DUAL_REVIEW_OUTPUT
  - ENT_PLAT_ACTION_REGISTRY (catálogo proveedores)
policies:
  - POL_AI_GOV_DATA_CLASS_PROVIDER (proveedores permitidos según data tier de la decisión)
  - POL_AI_GOV_FINAL_OUTPUT_QUALITY (sintetizador es final pass premium)
  - POL_AI_GOV_SKILL_INSTALLATION (no instalar skills durante el flujo)
  - POL_DATA_CLASSIFICATION
  - POL_DETERMINISMO (anti-alucinación)
  - POL_INMUTABILIDAD (no tocar archivos canon en el flujo)

---

## PROPÓSITO

Reducir puntos ciegos en decisiones técnicas relevantes mediante revisión cruzada controlada por **dos modelos LLM de familias distintas** seguida de síntesis por un tercero. El output es un veredicto accionable estandarizado (ver SCH_AI_GOV_DUAL_REVIEW_OUTPUT), no un debate abierto.

**Lo que este playbook NO es:**
- No es multi-agente libre (prohibido por restricción operativa).
- No es debate eterno: tiene cap de 1 sola ronda de revisión.
- No es decisión automática: la decisión final sigue siendo humana.
- No es brainstorming: opera sobre propuestas técnicas concretas, no ideación.

---

## CUÁNDO INVOCAR ESTE PROTOCOLO

| Disparador | Severidad sugerida |
|---|---|
| SPEC nuevo o extensión mayor de SPEC existente | P0/P1 |
| Cambio de schema de KB (`SCH_*`) que rompe compatibilidad | P0 |
| Cambio de POL que afecta enforcement runtime | P0 |
| Migración de schema de DB con downtime o riesgo de rollback | P0 |
| PR con side effects en Action Engine, Token Ledger, AI Governance, Data Classification | P0 |
| Routing policy: alta/baja de proveedor LLM o cambio de matriz | P0 |
| Skill installation: skill externa con `can_execute_code: true` o tier ≥N2 | P1 |
| DMS integration changes con impacto en privacy o costo | P1 |
| Prompt crítico para skill que opera tier ≥N2 | P1 |
| Workflow nuevo que mueve dinero, modifica permisos, o altera contratos B2B | P0 |
| Decisión arquitectónica con costo runtime mensual proyectado >USD 500 | P1 |
| Cambio de permisos / RLS / tenant isolation FaberLoom | P0 |

---

## CUÁNDO **NO** INVOCAR

| Caso | Razón |
|---|---|
| Typos, fixes cosméticos, refactors triviales | Costo > beneficio, mata productividad |
| Tareas con gold sample estable y pin activo | Ya hay receta canónica, dual review redundante |
| Extracción rutinaria, clasificación básica, parsing estándar | Tier 0 deterministic o single LLM cubre |
| Decisiones con `data_classification: N0` y costo run <USD 0.10 | El cap del flujo (USD 2.50) es desproporcionado |
| Decisiones ya validadas por revisión humana CEO | No agrega valor |
| Cualquier consulta conversacional o exploratoria | El flujo requiere propuesta concreta como input |

**Si tenés duda:** no invocar. El default es modo single-LLM con final pass policy normal (POL_AI_GOV_FINAL_OUTPUT_QUALITY). Dual review es excepción, no regla.

---

## ROLES DEL FLUJO

| Rol | Función | Modelo recomendado | Token Ledger `role` |
|---|---|---|---|
| **Proponente** | Genera plan técnico inicial completo (entendimiento, supuestos, plan, archivos afectados, deps, riesgos, tests, rollback, dudas) | Modelo de razonamiento fuerte: Opus 4.7 o GPT-5.5 Pro o Gemini 3.1 Pro | `carpintero` (produce el draft) |
| **Auditor adversarial** | Ataca el plan del proponente. Busca contradicciones, dependencias colgantes, violaciones al canon, riesgos. Clasifica hallazgos por severidad. | **Familia distinta al proponente.** Opciones: Sonnet 4.6, GPT-5.5, Kimi K2.6, DeepSeek v4 Pro | `judge` |
| **Sintetizador** | Recibe propuesta + audit, decide qué objeciones aceptar/rechazar, produce veredicto final según SCH_AI_GOV_DUAL_REVIEW_OUTPUT | Modelo de máxima calidad disponible: Opus 4.7 default. Aplica POL_AI_GOV_FINAL_OUTPUT_QUALITY (final pass premium) | `final_pass` |

---

## REGLA INQUEBRANTABLE: MODELOS DE FAMILIAS DISTINTAS

Proponente y auditor **DEBEN ser de familias distintas**. Razón: modelos de la misma casa (Opus + Sonnet, GPT-5.5 + GPT-5.5 Pro) comparten datos de training, RLHF, sesgos arquitectónicos. Si auditor y proponente son misma familia, sufren *sycophancy de familia*: tienden a coincidir en supuestos errados. El adversarialismo real requiere sesgos distintos.

### Pares válidos (auditor × proponente)

| Proponente | Auditor permitido |
|---|---|
| Anthropic (Opus, Sonnet, Haiku) | OpenAI · Google · Moonshot · DeepSeek |
| OpenAI (GPT-5.5, GPT-5.5 Pro) | Anthropic · Google · Moonshot · DeepSeek |
| Google (Gemini 3.1 Pro, Gemini 2.5 Flash) | Anthropic · OpenAI · Moonshot · DeepSeek |
| Moonshot (Kimi K2.6 managed o self-host) | Anthropic · OpenAI · Google · DeepSeek |
| DeepSeek (v4 Pro, v4 Flash) | Anthropic · OpenAI · Google · Moonshot |

### Pares prohibidos

- Cualquier combinación dentro de la misma familia (ej. Opus + Sonnet, GPT-5.5 + GPT-5.5 Pro).
- Mismo modelo con prompts distintos jugando ambos roles.
- Sintetizador de la misma familia que **ambos** revisores (familia mayoritaria → sesgo de mayoría). El sintetizador puede ser de la familia del proponente O del auditor, pero no debe coincidir con ambos simultáneamente.

---

## RESTRICCIÓN DE DATA CLASSIFICATION

La decisión técnica que se somete a dual review tiene un `data_classification` (N0..N4 según POL_DATA_CLASSIFICATION). Los tres modelos del flujo deben cumplir POL_AI_GOV_DATA_CLASS_PROVIDER:

| `data_classification` decisión | Restricción de proveedores |
|---|---|
| N0 / N1 | Cualquier proveedor del catálogo (incluye NO-DPA-MANAGED como Kimi managed o DeepSeek) |
| N2 | DPA-FULL (Anthropic, OpenAI, Google) o SELF-HOST-OPEN. Excepción: cost-mode opt-in vigente (CEO firma) |
| N3 / N4 | DPA-FULL o SELF-HOST-OPEN exclusivamente. Sin excepciones |

**Asimetría de orquestador NO aplica acá.** En dual review los tres modelos ven el contenido completo del problema técnico (no solo metadata). No es un orquestador-carpintero pattern.

---

## FLUJO DE SESIÓN — 4 PASOS

### PASO 1 — Definir el problema técnico

Antes de invocar el flujo, el decisor (Alejandro u otro) prepara:

```yaml
problem_brief:
  problem_id:                <kebab-case, ej. extender-action-engine-d11>
  problem_statement:         <2-5 líneas: qué se quiere lograr>
  scope:                     <archivos, componentes, sistemas afectados>
  constraints_known:         <restricciones que el decisor ya identificó>
  data_classification:       N0..N4
  decision_severity:         P0 | P1 | P2
  expected_implementer:      <agente o persona que ejecutará>
  deadline:                  <fecha o "sin deadline">
  refs:                      <KB refs relevantes: SPECs, POLs, PLBs>
```

**Si el `problem_statement` requiere más de 5 líneas para ser claro, el problema no está suficientemente acotado para dual review.** Volver a refinar.

### PASO 2 — Invocar al Proponente

Input al proponente: `problem_brief` completo + KB refs.

System prompt obligatorio:

```
Sos el Proponente Técnico en un flujo de Dual Review (PLB_AI_GOV_DUAL_REVIEW).

Tu output DEBE incluir TODAS estas secciones:

1. Entendimiento del problema (2-3 párrafos)
2. Supuestos críticos (lista numerada, marcar cuáles son verificados vs asumidos)
3. Plan de implementación (pasos numerados, ejecutables)
4. Archivos / componentes afectados (lista con razón)
5. Dependencias (técnicas y operativas, marcar las colgantes)
6. Riesgos identificados (severidad P0/P1/P2)
7. Tests obligatorios (unit, contract, integration, regression)
8. Rollback (pasos exactos para revertir)
9. Dudas abiertas (lo que no podés resolver desde tu input)

REGLAS:
- Aplicar Protocolo Anti-Alucinación MWT (POL_DETERMINISMO):
  · Dato no verificado → "[SIN DATOS — NO INVENTAR]"
  · Confianza parcial → declarar
  · Etiquetar fuente: [ENTRENAMIENTO] [CONTEXTO] [INFERENCIA]
- No inventar refs a archivos KB que no estén en tu input
- No proponer cambios fuera del scope declarado
- Si el problema está mal acotado, decirlo en sección "Dudas abiertas" en lugar de inferir
```

Output del proponente: `proposal.md` (markdown estructurado en las 9 secciones).

### PASO 3 — Invocar al Auditor Adversarial

Input al auditor: `problem_brief` + `proposal.md` del paso 2 + KB refs.

System prompt obligatorio:

```
Sos el Auditor Adversarial en un flujo de Dual Review (PLB_AI_GOV_DUAL_REVIEW).

Tu trabajo es atacar el plan del Proponente. NO sos complaciente.
NO felicites el plan. Buscás huecos.

Audita en estas dimensiones:

1. Contradicciones internas
2. Dependencias colgantes (refs a archivos/sistemas que no existen o no están en el scope)
3. Violaciones al canon MWT/FaberLoom (CLAUDE.md, taxonomía, FROZEN files, headers obligatorios)
4. Riesgos de seguridad
5. Riesgos de privacy / data classification
6. Riesgos de costo runtime (LLM, infra, APIs)
7. Casos edge no cubiertos
8. Partes no implementables (vagas, ambiguas)
9. Falta de tests (qué deberían testear y no testean)
10. Falta de rollback (pasos faltantes o irrealistas)
11. Scope creep (cambios que exceden el problema declarado)
12. Inconsistencias con SPECs/POLs/PLBs existentes

Para CADA hallazgo:
- Severidad: P0 (bloqueante), P1 (alta), P2 (media)
- Descripción concreta (no abstracta)
- Evidencia (sección/línea del proposal o ref KB que viola)
- Recomendación específica de fix

REGLAS:
- Si no encontrás hallazgos P0/P1, decilo explícitamente. NO inventar problemas para parecer útil.
- Aplicar Protocolo Anti-Alucinación MWT.
- No proponer plan alternativo completo. Tu rol es auditar, no re-proponer.
- Si el proposal es sólido en una dimensión, decir "OK en X" en vez de inventar críticas.
```

Output del auditor: `audit.md` (lista de hallazgos clasificados + áreas OK).

### PASO 4 — Invocar al Sintetizador

Input al sintetizador: `problem_brief` + `proposal.md` + `audit.md`.

System prompt obligatorio:

```
Sos el Sintetizador en un flujo de Dual Review (PLB_AI_GOV_DUAL_REVIEW).
Aplicás POL_AI_GOV_FINAL_OUTPUT_QUALITY (sos el final pass premium).

Tu output DEBE seguir el schema SCH_AI_GOV_DUAL_REVIEW_OUTPUT exactamente.

Tu trabajo:
1. Para cada hallazgo del Auditor: aceptar o rechazar con justificación.
2. Decidir veredicto global: aprobar / aprobar con cambios / rechazar.
3. Listar cambios obligatorios antes de implementar (los hallazgos aceptados como bloqueantes).
4. Producir plan final consolidado (proposal + cambios obligatorios integrados).
5. Listar tests requeridos consolidados.
6. Documentar rollback consolidado.
7. Listar decisiones que quedan abiertas para el humano.

REGLAS:
- No re-proponer. Solo consolidar.
- Si auditor encontró P0 sin resolución obligatoria, veredicto NO PUEDE ser "aprobar". Mínimo "aprobar con cambios" o "rechazar".
- Si proposal y audit se contradicen sin que vos puedas decidir (faltan datos), declarar la decisión como "abierta" y no inferir.
- Aplicar Protocolo Anti-Alucinación MWT.
- Output en markdown siguiendo SCH_AI_GOV_DUAL_REVIEW_OUTPUT al pie de la letra.
```

Output del sintetizador: `verdict.md` (estructurado según SCH_AI_GOV_DUAL_REVIEW_OUTPUT).

---

## ANTI-LOOP

Regla dura: **el flujo tiene 1 sola ronda completa** (proposal → audit → verdict). NO hay re-runs automáticos.

Si el sintetizador detecta P0 sin resolución (proposal no cubre el hallazgo y auditor no propuso fix viable), el veredicto es **"rechazar"** o **"aprobar con cambios"** marcando el P0 como decisión abierta. NO se vuelve al proponente automáticamente.

Si el decisor (humano) decide re-correr el flujo después de modificar el problem_brief, eso cuenta como **invocación nueva** con su propio `problem_id` y su propio cap de costo. NO es continuación.

**Razón:** loops infinitos de proposal-audit-proposal-audit son la forma más rápida de vaciar el budget mensual de IA.

---

## CAPS DE ACTIVACIÓN (anti-teatro)

```yaml
activation_caps:
  per_decisor_per_week:
    P0:                  sin cap
    P1:                  3 invocaciones
    P2:                  2 invocaciones
    P3:                  bloqueado por defecto (justificación CEO requerida)

  cost_caps:
    per_run_max_usd:     2.50           # 3 modelos premium pueden subir
    per_run_soft_warn:   1.50
    per_decisor_monthly_cap_usd: 30.00   # ajustable post-review trimestral

  duration_caps:
    proponente_max_tokens_out:   8000
    auditor_max_tokens_out:      6000
    sintetizador_max_tokens_out: 4000
    full_run_max_minutes:        20    # si excede, abort y escalación humana

  fail_open: false                      # si excede cap, BLOQUEA. No degrada silenciosamente.
```

Caps registrados en Token Ledger v1.3 (`budget_caps_applied`, `budget_status`).

---

## OUTPUT MÍNIMO ENTREGADO AL DECISOR

El veredicto sigue **exactamente** SCH_AI_GOV_DUAL_REVIEW_OUTPUT. Resumen del schema:

```markdown
# Resultado de revisión cruzada · <problem_id>

## Veredicto
APROBAR | APROBAR CON CAMBIOS | RECHAZAR

## Hallazgos críticos
- P0: ...
- P1: ...
- P2: ...

## Cambios obligatorios antes de implementar
1. ...
2. ...

## Plan final recomendado
1. ...
2. ...

## Tests requeridos
- Unit: ...
- Contract: ...
- Integration: ...
- Regression: ...

## Rollback
1. ...

## Decisiones abiertas
- ...

## Metadata
- Modelos usados: proponente=X, auditor=Y, sintetizador=Z
- Familias distintas: ✅ verificado
- Costo total: USD X.XX
- Token Ledger entries: 3 (parent_request_id=<uuid>)
- data_classification: N<n>
```

---

## REGISTRO EN TOKEN LEDGER

Cada invocación produce **3 entries** en Token Ledger (SPEC_LLM_ROUTING_ARCHITECTURE v1.3) con el mismo `parent_request_id`:

```yaml
entry_proponente:
  role:               carpintero
  model:              <modelo proponente>
  data_classification: <N0..N4>
  parent_request_id:  <uuid raíz>

entry_auditor:
  role:               judge
  model:              <modelo auditor>
  parent_request_id:  <mismo uuid>

entry_sintetizador:
  role:               final_pass
  model:              <modelo sintetizador>
  parent_request_id:  <mismo uuid>
  final_pass_required: true
  final_pass_executed: true
```

Costo total real de la decisión = `SUM(cost_total_usd)` de las 3 entries.

---

## RESTRICCIONES OPERATIVAS

1. **No tocar Sprint 1 MWT.** Decisiones que afecten Sprint 1 quedan fuera del flujo y van a CEO directo.
2. **No instalar skills durante el flujo.** Si proposal o audit recomiendan instalar skill nueva, eso queda en "decisiones abiertas" — la instalación pasa por POL_AI_GOV_SKILL_INSTALLATION después.
3. **No modificar archivos canon durante el flujo.** Los modelos generan recomendaciones, no hacen Edit/Write a la KB. La canonización pasa por flow Cowork↔KB con sync script.
4. **No cambiar routing policy directamente.** El flujo puede recomendar cambios a POL_AI_GOV_DATA_CLASS_PROVIDER, no aplicarlos.
5. **No acceder a secretos.** Ningún modelo recibe API keys, tokens, credenciales en el `problem_brief`.
6. **No autorizar deploy.** El veredicto es recomendación. Implementación + deploy pasan por gates humanos normales.
7. **No autorizar merge automático.** Si el flujo se invoca sobre un PR, el veredicto se adjunta como comentario; el merge sigue requiriendo aprobación humana.

---

## MODO DE OPERACIÓN

### MVP — Prescriptivo (vigente desde 2026-05-01)

El decisor (Alejandro u otro) ejecuta los 4 pasos manualmente:
1. Prepara `problem_brief` en su entorno.
2. Abre 3 sesiones de modelos distintos (Cowork, Claude Code, ChatGPT, etc.) respetando regla de familias distintas.
3. Pasa system prompts + inputs según pasos 2/3/4.
4. Recibe outputs y los registra en archivo `<problem_id>_dual_review.md` en `docs/dual_reviews/` (carpeta nueva, gitignoreada hasta canonizar veredictos selectos).

**Telemetría manual:** decisor registra en bitácora propia los 3 modelos usados, costos estimados, veredicto. Aún no escribe a Token Ledger formal (Action Engine no tiene hookpoints todavía).

### Ejecutable — Post Action Engine F1 (sem 3+ del roadmap actual)

Cuando Action Engine tenga hookpoints para POL_AI_GOV_DATA_CLASS_PROVIDER + Token Ledger v1.3:

```python
action_engine.execute(
    intent="dual_review",
    problem_brief=brief,
    config={
        "proponente_model": "auto_select_strongest",  # respeta data_class
        "auditor_model": "auto_select_distinct_family",
        "sintetizador_model": "auto_select_premium",
    }
)
```

El Engine:
- Valida cap de invocación del decisor.
- Selecciona modelos respetando regla de familias distintas + POL_AI_GOV_DATA_CLASS_PROVIDER.
- Ejecuta los 3 pasos secuenciales.
- Escribe 3 entries al Token Ledger con parent_request_id compartido.
- Retorna veredicto en formato SCH_AI_GOV_DUAL_REVIEW_OUTPUT.

Migración prescriptivo → ejecutable: requiere bumping este PLB a v2.0.

---

## ARCHIVO DE VEREDICTOS

Veredictos importantes (decisiones P0 sobre arquitectura, schemas, policies) se preservan en `docs/dual_reviews/<problem_id>__<YYYY-MM-DD>.md` para auditoría retrospectiva.

Veredictos triviales o rechazados sin acción quedan en bitácora del decisor, no en KB.

CEO decide qué veredictos canonizar.

---

## TELEMETRÍA Y REVISIÓN TRIMESTRAL

Cada trimestre, CEO revisa:
1. Cuántas invocaciones por categoría de severidad.
2. Cuántos veredictos terminaron en "aprobar" sin cambios — si >70%, el flujo se está sub-utilizando o aplicando a casos triviales (señal de teatro).
3. Cuántos veredictos terminaron en "rechazar" — si >30%, el problem brief está mal acotado upstream.
4. Costo total trimestral vs valor de errores evitados (estimación).
5. Pares de familias usados — si Anthropic vs OpenAI domina >80%, considerar incluir Kimi/DeepSeek en rotación para diversificar sesgos.

Resultado del review: ajuste de caps + actualización de "cuándo invocar / cuándo no".

---

## CHANGELOG

- v1.0 (2026-05-01): Creación. Modo prescriptivo MVP. 4 pasos del flujo. Regla familias distintas inquebrantable. Caps de activación. Anti-loop 1-shot. Conexión con SPEC_AI_GOV + Token Ledger v1.3. Origen: idea CEO 2026-05-01 evaluada por Cowork como arquitecto.
