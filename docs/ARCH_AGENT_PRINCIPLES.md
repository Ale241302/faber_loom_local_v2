# ARCH_AGENT_PRINCIPLES — Principios Fundacionales de Arquitectura de Agentes
id: ARCH_AGENT_PRINCIPLES
version: 1.6
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
stamp: VIGENTE — 2026-04-28
aprobador: CEO
aplica_a: [MWT, FaberLoom]

---

## Declaración

Este documento define los principios invariantes que gobiernan el diseño de cualquier agente IA en los productos de Muito Work Limitada — tanto en la plataforma interna **MWT** como en el producto SaaS **FaberLoom**.

Cualquier decisión de diseño que contradiga estos principios requiere justificación explícita y aprobación CEO. No son sugerencias — son la arquitectura.

---

## Principio 0 — Un agente no es un prompt

Un agente útil es: **identidad + estado + contexto mínimo exacto + eventos + memoria curada + feedback estructurado + guardrails operativos.**

Un prompt sin estos componentes es un asistente de sesión, no un agente. No aprende, no mejora, no se gobierna.

---

## Principio 1 — Separación obligatoria en 3 objetos

Todo agente se implementa con 3 objetos separados. No hay excepciones.

```
AgentSpec     → Lo que el agente ES        (estático, versionado, inmutable entre ejecuciones)
AgentRuntime  → Lo que el agente HACE      (dinámico, actualizado por ejecución)
AgentMemory   → Lo que el agente APRENDIÓ  (acumulado, solo se escribe con gate humano)
```

**Por qué importa:** mezclar los tres en un solo objeto produce agentes que no se pueden medir, auditar ni mejorar de forma controlada. Cada objeto tiene su ciclo de vida y su dueño.

### AgentSpec contiene
- `trigger_word` — cómo se activa
- `autonomy_ceiling` — techo de autonomía posible
- `escalation_policy` — qué hacer fuera de scope
- `kb_refs` — contexto mínimo necesario (no toda la KB)
- `state_machine` — estados operativos del agente
- `events` — qué emite en cada interacción
- `learning_consolidation` — qué tipos de outputs califican como memoria

### AgentRuntime contiene
- Estado actual (de la state machine)
- Autonomía real actual (≤ ceiling)
- Métricas: ejecuciones, approval rate, edit-light rate, rejection rate
- Cola de outputs pendientes de consolidar (termómetro)
- Última ejecución

### AgentMemory contiene
- Gold samples activos (aprobados con gate humano)
- Patrones aprobados y correcciones recurrentes
- Excepciones documentadas con justificación
- Perfiles de remitente / contexto acumulado

---

## Principio 2 — Contexto mínimo y exacto

El agente carga **solo** lo declarado en su `kb_refs`. No toda la KB, no toda la memoria — lo necesario para ese skill.

**Por qué importa:** contexto inflado degrada la calidad del output y consume tokens sin beneficio. La precisión del contexto es la primera palanca de calidad.

Regla operativa: si un dato no está en `kb_refs`, el agente no lo usa. Si lo necesita, se escala o se actualiza el AgentSpec.

---

## Principio 3 — Draft-first es absoluto

Ningún agente envía comunicación externa, ejecuta transacciones financieras, modifica datos de clientes ni dispara workflows externos sin aprobación explícita del humano responsable.

**Esto no cambia con ningún nivel de autonomía.** El autonomy ladder gobierna acciones internas — nunca acciones externas con impacto real. Ningún Nivel del ladder, incluido L4, admite envío externo autónomo.

**Carácter invariante (declaración CEO 2026-04-28):** P3 es invariante absoluto. No admite excepción runtime, override CEO ad-hoc, ni cláusula condicional por tipo de canal. La única forma de modificar P3 es nueva versión del principio con changelog documentado y revisión integral del CORE.

Aplica a: correo, WhatsApp, Slack, webhooks, CRM writes, compromisos de fecha/monto/términos, notificaciones a clientes externos, factura, cobro, confirmaciones automáticas a terceros.

**Metáfora de gobierno:** la autonomía externa solo se otorga tras un proceso comprobado de aprendizaje y alta certeza técnica. Como un vehículo en carretera — no se acelera hasta tener confianza absoluta de que el sistema responde. La seguridad del usuario final es prioritaria sobre la velocidad de automatización.

---

## Principio 4 — Autonomía por evidencia, nunca por configuración

Un agente no sube de nivel de autonomía porque alguien lo configure. Sube cuando demuestra:

| Condición | Threshold |
|-----------|-----------|
| Ejecuciones en nivel actual | ≥ 10 |
| Approval rate | ≥ 80% |
| Edit-light rate (≤20% edición) | ≥ 60% |
| Rejection rate | ≤ 10% |
| Días estables sin error grave | ≥ 14 |
| AgentMemory activa | Sí |
| Aprobación CEO | Siempre requerida |

Excepción: SHADOW → primer nivel activo requiere solo ≥ 3 ejecuciones con approval rate > 70%.

**Degradación automática** si rejection rate > 30% en últimas 5 ejecuciones, error grave en acción de alto impacto, o dependencia de KB rota.

### Autonomy Ladder — 5 niveles

```
Nivel 0 — SHADOW          → observa, no sale al usuario
Nivel 1 — PROPONE         → draft siempre, aprobación requerida para cualquier acción
Nivel 2 — EJECUTA_INTERNO → acciones internas sin aprobación (KB, resúmenes, etiquetas)
Nivel 3 — AUTO_NOTIFICA   → ejecuta acciones internas reversibles probadas y
                            notifica al humano responsable post-hecho.
                            NO ejecuta acciones externas bajo ningún concepto.
Nivel 4 — AUTO_EXCEPCIONES → auto en flujos muy estrechos INTERNOS, CEO solo
                            ve excepciones. Externos siguen P3 (draft-first).
```

**Definición de "acción interna" (vinculante):** KB writes, etiquetas en bandeja propia del tenant, resúmenes internos, actualizaciones de estado interno de un caso, generación de drafts para aprobación, escritura a AgentMemory tras gate humano (P5), cálculos sin side-effect externo. NO incluye: envío de email/WhatsApp/Slack/webhook, mutación de datos en sistemas del cliente, comunicación a usuarios finales del tenant, factura, cobro, confirmaciones automáticas a terceros.

**Definición de "acción reversible probada":** acción interna con (a) métricas de aprobación >85% en últimas 50 ejecuciones, (b) mecanismo de retracción documentado, (c) scope estrecho declarado en AgentSpec.

---

## Principio 5 — Aprendizaje con gate humano

El agente no escribe a su memoria por sí solo. El flujo obligatorio:

```
Output generado → feedback del humano → evento estructurado emitido
        ↓
Termómetro de aprendizaje sube
        ↓                              🔵 Frío  (0-2)
Humano presiona "Indexar Aprendizaje"  🟡 Tibio (3-5)
        ↓                              🔴 Caliente (6+, urgente)
Modal muestra: patrones · correcciones recurrentes · gold samples candidatos · excepciones
        ↓
Humano confirma / edita / descarta
        ↓
Solo al confirmar → escribe a AgentMemory
```

**Nunca auto-promover desde thumbs up.** Un output aprobado es un Candidate sample. Se convierte en Gold sample solo después de revisión humana explícita.

### Pipeline de gold samples

```
Corrección del humano → Candidate → revisión humana → eval/simulación → Gold sample activo
                                                                        ↓
                                                              Archived / Reverted
```

---

## Principio 6 — Feedback tipificado, no texto libre

Cuando el humano rechaza o corrige un output, debe categorizar el tipo de corrección:

| Código | Significado |
|--------|-------------|
| `tone` | Tono incorrecto |
| `data` | Dato incorrecto o inventado |
| `structure` | Estructura incorrecta |
| `policy` | Violación de regla del sistema |
| `scope` | Fuera del scope del agente |
| `context` | Faltó contexto relevante |

Esto alimenta: score de confianza · detección de patrones recurrentes · mejora del AgentSpec.

---

## Principio 7 — State machine explícita por agente

Todo agente tiene estados operativos definidos. Los estados permiten:
- Mostrar UI útil (el usuario sabe qué está pasando)
- Auditar por qué no actuó
- Gobernar transiciones de autonomía
- Detectar bloqueos

Estados mínimos obligatorios:
```
drafting → awaiting_approval → approved → executing → completed
                ↓                                        ↓
            rejected ← ← ← ← ← ← ← ← ← ← ← ← ←    escalated
```

**Tabla de transiciones (v1.5) — eventos disparadores y timeouts:**

| Estado origen | Evento disparador | Condición | Estado destino | Timeout | Acción si timeout |
|---|---|---|---|---|---|
| drafting | `output_generated` | output válido contra output_schema | awaiting_approval | 60s para generar | escalated (timeout LLM) |
| drafting | `output_generated` | output inválido contra schema | rejected | — | retry hasta max 3, después escalated |
| awaiting_approval | `human_approval` | humano_responsable confirma | approved | 24h default (configurable per skill, max 72h) | escalated (sin respuesta) |
| awaiting_approval | `human_rejection` | humano_responsable rechaza con feedback tipificado (P6) | rejected | — | inmediato |
| approved | `execution_started` | gates de P9 pasan + autonomy_level permite | executing | inmediato | bloqueo si gate falla |
| approved | `gate_failed` | algún gate de P9 retorna false | escalated | — | notif al CEO con detalle |
| executing | `execution_success` | side-effect completado sin error | completed | depende de action_class (default 30s, hasta 5 min para external) | escalated (timeout exec) |
| executing | `execution_error` | excepción durante side-effect | escalated | — | retry condicional según error_class |
| escalated | `human_resolution` | humano resuelve manualmente | completed | sin timeout | — |
| rejected | `feedback_consolidated` | feedback registrado + termómetro actualizado | (estado terminal) | — | — |
| completed | `audit_logged` | AuditEntry inmutable persistida | (estado terminal) | — | — |

**Timeout default de awaiting_approval:** 24h. Configurable per-skill en AgentSpec entre 1h y 72h. Si action_class = `external_communication` con destinatario externo, el timeout default es 4h (más corto para evitar mensajes desactualizados).

**Aclaración crítica del timeout external (v1.5):** este timeout aplica exclusivamente al draft del agente esperando aprobación humana. NO autoriza envío externo autónomo bajo ningún concepto — al expirar el timeout, el draft pasa a `escalated`, NUNCA a `executing`. P3 (draft-first absoluto) sigue siendo invariante: cero envíos externos sin aprobación humana, ni siquiera al expirar timeout.

---

## Principio 8 — Telemetría mínima no negociable

Sin estas métricas no se puede mejorar, vender ROI, ni decidir autonomía:

- Ejecuciones totales · en SHADOW · en nivel actual
- Approval rate · edit-light rate · rejection rate
- Tiempo promedio a resolución
- Outputs pendientes de consolidar (termómetro)
- Bloqueos por policy
- Escalaciones a humano

---

## Principio 9 — Gobernanza embebida, no agregada después

Los policy gates se verifican **antes** de ejecutar, no después. No son una capa de seguridad encima — son parte del flow del agente.

Gates obligatorios antes de cualquier acción externa:
- ¿Hay aprobación explícita del humano responsable?
- ¿La acción está dentro del scope declarado en AgentSpec?
- ¿La dependencia KB está vigente (no DEPRECATED, no rota)?
- ¿El nivel de autonomía actual permite esta acción?

---

## Principio 10 — Handoffs estructurados entre agentes

Cuando un agente delega a otro, el paquete de handoff es explícito:

```
task · goal · context · constraints · artifacts · deadline · confidence · requested_output_format
```

No se pasa contexto libre. No se asume que el agente receptor entiende el contexto del emisor.

---

## Principio 11 — Clasificador de aprendizaje de 3 destinos

Todo evento de aprendizaje (corrección, aprobación, rechazo) genera **una o más propuestas** de clasificación antes de escribir a memoria. Cada propuesta pertenece exactamente a uno de tres destinos: CONTEXTO, SKILL REFINEMENT o GOLD SAMPLE. Un mismo evento puede producir múltiples propuestas simultáneas, pero cada escritura individual confirmada por humano corresponde a un único destino. El sistema propone la(s) clasificación(es) — el humano confirma, cambia o descarta cada propuesta independientemente.

```
Evento de aprendizaje
        ↓
Clasificador evalúa el delta (qué cambió, cuánto, cómo)
        ↓
Propone destino:

  A) CONTEXTO          → hecho sobre la organización que el skill no sabía
  B) SKILL REFINEMENT  → regla de comportamiento que debe actualizarse en el AgentSpec
  C) GOLD SAMPLE       → output completo aprobado que sirve de referencia futura
        ↓
Modal presenta propuesta al usuario → [Confirmar] [Cambiar clasificación] [Descartar]
        ↓
Solo al confirmar → escribe al destino
```

**Lógica del clasificador:**

| Delta detectado | Destino |
|-----------------|---------|
| Hecho organizacional ausente | Contexto |
| Regla de comportamiento mal aplicada o ausente | Skill refinement |
| Output aprobado con ≤20% de edición | Gold sample |

Cada propuesta se evalúa independientemente. `auto_approve: false` siempre — sin excepción para ningún destino.

**Dónde vive cada destino:**

| Destino | Capa | Alcance |
|---------|------|---------|
| Contexto | pgvector namespace org | Cross-skill |
| Skill refinement | Org AgentSpec (capa sobre base) | Por skill |
| Gold sample | AgentMemory del skill | Por skill |

**Naturaleza técnica del Clasificador (v1.5):**

| Componente | Especificación |
|---|---|
| Implementación | Prompt estructurado ejecutado sobre Claude Haiku 4.5 (o equivalente Tier 1 con DPA reconocido) con output JSON forzado vía structured outputs / response_format |
| Output schema | `{ propuestas: [{ destino: enum[CONTEXTO, SKILL_REFINEMENT, GOLD_SAMPLE], confidence: float[0-1], alcance_sugerido: enum[skill_specific, cluster, org_wide], classification_detectada: enum[N0,N1,N2,N3,N4], razonamiento: string }] }` |
| Confidence threshold | Si `confidence < 0.80` para una propuesta, se marca para Human Gate sin proponer destino — el humano clasifica desde cero |
| Latencia objetivo | < 1500 ms p95 |
| Costo objetivo | < $0.005 por evento clasificado |
| Mantenimiento | Revisión trimestral por equipo de compliance del tenant. Prompt versionado en repo, cambios disparan probation P13 del clasificador |
| Fallback | Si el clasificador falla (timeout, error API, output mal formado): el evento queda en cola "sin clasificar" — visible en UI, esperando clasificación humana directa. NUNCA se descarta silenciosamente |
| Auditoría | Cada invocación genera trace en observability + AuditEntry si propone destino N2+ |

---

## Principio 12 — Propagación cross-skill del aprendizaje

Un evento de aprendizaje clasificado en un skill puede impactar múltiples skills simultáneamente. El clasificador determina el alcance junto con el tipo.

```
Aprendizaje detectado en SKILL_COPY
        ↓
Clasificador determina alcance:

  Org-wide     → todos los skills (hechos del org, tono global)
  Cluster      → skills del mismo dominio (ej: todos los de comunicación)
  Skill-specific → solo el skill que generó el output (gold samples)
        ↓
Modal muestra skills impactados con checkbox por skill:
  ✅ SKILL_COPY           (activo)
  ✅ SKILL_HUMANIZE_COMMS (mismo cluster)
  ✅ SKILL_CLIENT_SERVICE (mismo cluster)
  ☐  SKILL_AMAZON_OPS    (diferente dominio)
        ↓
[Confirmar todos] [Seleccionar cuáles] [Descartar]
```

**Alcance natural por tipo de aprendizaje:**

| Tipo de aprendizaje | Alcance natural |
|---------------------|----------------|
| Hecho del org (contexto) | Org-wide — todos los skills |
| Regla de tono / voz | Cluster de comunicación |
| Regla de canal específico | Skills que usan ese canal |
| Regla de producto / compliance | Skills que tocan ese producto |
| Gold sample | Skill-specific únicamente |
| **Hecho del org que contiene datos N2/N3/N4** | **Skill-specific únicamente. NUNCA Org-wide ni Cluster sin des-identificación previa documentada y aprobación CEO** |

**Filtro de classification obligatorio (v1.5):** el clasificador detecta classification del hecho ANTES de proponer alcance. Si la classification del hecho es N2 o superior, el alcance "Org-wide" y "Cluster" quedan automáticamente bloqueados en el modal — la única opción seleccionable es "Skill-specific". Para promover un hecho N2+ a Org-wide se requiere flujo separado: des-identificación irreversible documentada + aprobación CEO documentada per-evento + AuditEntry inmutable.

El modal P12 muestra obligatoriamente: skills impactados + classification del hecho + warning visual si classification >= N2 + bloqueo de opciones de alcance ampliado.

**Confirmante humano de la propagación (v1.5):** cuando el alcance propuesto incluye múltiples skills receptores, el humano que confirma la propagación a cada skill receptor es el `humano_responsable` (ver glosario) **del skill receptor**, no del skill originador. Si la position del humano_responsable de un skill receptor está vacante, escala al admin del tenant. Esto cumple P5 gate humano de forma consistente para cada destino de escritura.

**Por qué importa:** una corrección de tono en SKILL_COPY resuelve el mismo problema en SKILL_HUMANIZE_COMMS y SKILL_CLIENT_SERVICE sin que el usuario tenga que corregirlos por separado. El aprendizaje se propaga donde tiene sentido. El gold sample siempre es skill-específico — un output ideal de copy no es el mismo que uno de servicio al cliente aunque compartan reglas de tono.

---

## Aplicación por producto

### MWT (plataforma interna)
- Implementación actual: SKILL_*.md = AgentSpec · SKILL_RUNTIME.md = AgentRuntime · SKILL_MEM_*.md = AgentMemory
- Todos los skills arrancan en SHADOW
- KB refs declaradas en cada SKILL_*.md son el contexto autorizado
- Ref operativa: `SCH_SKILL.md`

### FaberLoom (producto SaaS)
- Los agentes del Agent Builder heredan esta arquitectura
- AgentSpec → configuración del agente por organización
- AgentRuntime → tabla `agent_runtime` en DB
- AgentMemory → gold samples por organización + gold samples globales de FaberLoom
- La UI del Agent Console implementa el estado del agente (colores, badges, termómetro)
- El modal "Indexar Aprendizaje" es el gate de escritura a memoria

---

## Principio 13 — Contención de memoria y autonomía

La autonomía y el aprendizaje acumulado de un agente están contenidos y no se
transfieren automáticamente a otro agente ni a otra organización.

**Tres garantías de contención:**

```
1. Memoria contenida
   AgentMemory de un agente no se propaga a otro agente
   sin clasificación explícita (P11) y confirmación humana (P5).

2. Autonomía no transferible entre orgs
   La autonomía ganada por un agente en org A no es heredada por org B.
   Cada organización construye evidencia propia desde nivel 0.

3. Autonomía vinculada a ModelFingerprint
   La autonomía no pertenece al agente solo — pertenece a:
   agente × modelo × toolchain × policy version.

   ModelFingerprint = {
     provider, model_family, model_version,
     system_prompt_hash, tools_manifest_hash,
     policy_version, retrieval_index_version
   }

   Cambio de cualquier componente del fingerprint →
   estado de probation inmediato → un nivel abajo →
   revalidación por bucket antes de restaurar nivel anterior.
```

**Por qué importa:** un agente promovido a Nivel 3 con Claude Sonnet 4.5 no hereda
ese nivel automáticamente al migrar a Sonnet 4.6. El modelo nuevo puede comportarse
diferente en los casos que justificaron la promoción. La revalidación protege contra
regresión silenciosa de calidad.

**Garantía multi-tenant (FaberLoom):** org A nunca ve ni hereda lo aprendido por
org B. El gold sample de Sonepar Colombia no es visible para otro cliente de FaberLoom.

**Aislamiento absoluto del aprendizaje (declaración CEO 2026-04-28):** ningún
output, corrección, gold sample, patrón emergente, o derivado del uso de un
tenant cliente puede convertirse en gold sample global de FaberLoom, en
gold sample de otro tenant, ni alimentar mejoras del producto que beneficien
a tenants distintos al originador. El conocimiento reside en la organización
del cliente, no en FaberLoom. El producto se distribuye con gold samples
internos escritos por FaberLoom sin uso de data cliente — no hay global
learning derivado del uso comercial.

**Posicionamiento que esto implica:** FaberLoom no es una consola IA de
propósito general. Es un repositorio operativo de la organización cliente
que se adapta a su forma específica de trabajar. El gold sample es un
constructo único entre el agente y el usuario de esa empresa — no
transferible.

**Jerarquía interna del tenant (declaración CEO 2026-04-28):** dentro de
una misma organización cliente, FaberLoom soporta jerarquía de permisos
configurable por el admin del tenant:

- **Agente personal (scope=user):** vive en el espacio del usuario que lo
  creó. Memoria privada al usuario. No visible para otros usuarios del
  mismo tenant.
- **Agente publicado a la organización (scope=org):** disponible para
  todos los usuarios autorizados del tenant. Memoria compartida intra-tenant
  pero respeta niveles de permiso del consultante.
- **Permisos por nivel (ej. agente RRHH):** un mismo agente publicado puede
  responder distinto según el rol del usuario que consulta. La información
  que un agente puede leer Y devolver está acotada por la intersección
  entre AgentSpec, scope del agente y permisos del consultante. **El
  sistema NO debe recuperar, cargar en contexto ni exponer al modelo
  datos que el consultante no esté autorizado a ver** (pre-filtering en
  retrieval, no output filtering). La AgentSpec declara qué scopes de
  información expone a qué roles del tenant; el retrieval, chunking de
  KB y composición de prompt aplican esos permisos antes de invocar al
  modelo.

**Por qué pre-filtering y no output filtering:** output filtering es
vulnerable a prompt injection (84% éxito en research), inferencia
indirecta, side-channel via formato, leak en logs/observabilidad
(chunks completos persisten), y regresión silenciosa al cambiar
modelo. Pre-filtering elimina la superficie de ataque en origen — si
el modelo nunca vio el dato, no lo puede filtrar mal.

Esta jerarquía intra-tenant se gestiona dentro del aislamiento P13 — nunca
cruza el límite entre tenants.

**Step-up authentication para scope=user_self con datos N2+
(declaración CEO 2026-04-28):**

Cuando un agente publicado a la organización (scope=org) responde a un
consultante sobre sus PROPIOS datos clasificados N3+, el sistema aplica
step-up authentication antes de cargar esos datos en contexto. 3 niveles:

| Nivel | Acceso a | Auth requerida | TTL | Audit |
|---|---|---|---|---|
| **A — Sesión normal** | N0 público + N1 propio operativo (vacaciones, asistencia, políticas, mis solicitudes pendientes) | session token + tenant context | duración de sesión | log básico |
| **B — Sesión sensible** | N2/N3 propio (salario, bonos, evaluaciones, procesos disciplinarios propios, datos médicos propios) | MFA OTP fresh + reconfirm contraseña + IP estable | 15 min, después vuelve a A | AuditEntry inmutable per-acceso (D10) |
| **C — Documento formal** | Documentos con valor legal del consultante (constancia salarial, certificación de ingresos, hoja de vida laboral oficial, informes regulatorios personales) | Nivel B + propósito declarado + aprobación humano_responsable de RRHH/Legal | documento generado con expiración explícita | AuditEntry + copia firmada en ledger |

**Reglas de step-up:**
- Sin step-up válido del nivel correspondiente, el chunk N2+ propio NO se recupera del retrieval. El agente responde "necesito verificación adicional" sin haber visto el dato.
- El step-up NO sustituye al pre-filtering — sigue aplicando: solo se cargan al modelo datos del consultante DESPUÉS de validar el step-up.
- El step-up SOLO desbloquea datos PROPIOS del consultante. Datos de terceros nunca son accesibles vía step-up — requieren ser tercero autorizado en AgentSpec.
- Datos N4 biométricos propios siguen requiriendo además consentimiento explícito (POL_CONSENTIMIENTO).

Aplica a: agentes RRHH, agentes médicos, agentes financieros personales, agentes legales, scanner Rana Walk consultando escaneo propio, cualquier agente que exponga datos N2+ del propio consultante.

---

## Principio 14 — Deterministic First → LLM Fallback → Human Gate

Toda capa del sistema que pueda resolverse de forma determinística debe intentarlo
antes de invocar un LLM. Toda decisión cuyo riesgo o impacto exceda umbrales
predefinidos debe esperar gate humano antes de ejecutarse.

**Tres niveles, en orden estricto:**

```
1. Deterministic First
   Regex, AST, parsers XML, validación de schema, lookup en tabla.
   Latencia: microsegundos. Costo: $0. Determinismo: total.

2. LLM Fallback
   Solo si Deterministic falla, retorna confidence < threshold,
   o el caso no está cubierto por reglas.
   Latencia: cientos de ms. Costo: tokens. Determinismo: probabilístico.

3. Human Gate
   Solo si LLM Fallback retorna confidence < approval_threshold,
   el impacto excede umbral, o la action_class lo requiere.
   Latencia: minutos a horas. Costo: tiempo humano. Determinismo: total.
```

**Por qué importa:** los sistemas que saltan directamente a la capa inteligente
(LLM puro, bandit puro, swarm puro) tienen tasas de fallo 2-5× mayores que los
que aplican defensa en profundidad. La disciplina "empezar simple, escalar inteligente"
no es simplificación de MVP — es estrategia de producción robusta validada por
research convergente (Ruflo, RouteLLM, Reflex Fabric, Anthropic multi-agent research).

**Aplicación obligatoria en MWT/FaberLoom:**

| Capa | Deterministic First | LLM Fallback | Human Gate |
|---|---|---|---|
| Parsing de inputs | Regex + Pydantic + XML parsers LATAM (DIAN, SII, SAT, AFIP, NFe) | Haiku para casos no-estructurados | Si confidence < threshold |
| Routing | L1 rule-based + L2 dispatcher | Bandit adaptive (Phase 2, >3,000 req/día) | Revisión CEO en transición |
| Composición de agentes | Single-agent + L1/L2 (default) | Nivel 2 multi-agente: orquestador delgado + sub-agentes con handoff estructurado (habilitado bajo P17). MAS peer-to-peer (Nivel 3) sigue cerrado | Approval por tool + Human Gate de P14 obligatorio en cada handoff que cumpla los disparadores Tier 2 v1.5 |
| Vector retrieval | pgvector + RLS + composite indexes | Re-ranking con LLM si recall insuficiente | Si action de alto impacto |

**Anti-patrón que P14 prohíbe:** llamar a un LLM como respuesta default sin haber
intentado primero un parser determinístico. Ej: usar Haiku para parsear un XML
de DIAN cuando `xml.etree.ElementTree` lo resuelve en <1ms con accuracy 100%.

**Relación con principios anteriores:**
- P3 (Draft-first absoluto): P14 refina cuándo el draft viene de regex vs LLM.
- P4 (Niveles de autonomía): el Human Gate de P14 es el mismo gate que P4 escalan.
- P9 (Gobernanza embebida): P14 es la implementación táctica del P9 estratégico.
- P13 (Contención): el Human Gate de P14 es disparado también por cambio de fingerprint.

**Origen:** investigación cruzada Kimi #3 (Ruflo / 4 gaps) — el patrón emerge
como invariante en 3 de 4 dominios analizados (Tier 0, routing, spawning).
Ver `docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md` §Patrón transversal.

---

## P17 - Composicion multi-agente por niveles con activacion condicionada

**Decision (2026-06-01):** se levanta la prohibicion por defecto de multi-agente y se habilita el Nivel 2 como opcion de primera clase (deja de estar diferido a Fase 6), bajo condiciones de activacion y guardrails. El Nivel 3 (MAS peer-to-peer) permanece cerrado con criterios explicitos de reevaluacion. Razon: el research 2026 (RESEARCH_AGENTES_CONSOLIDADO_2026_v1) confirma orquestador-subagente con handoff estructurado como patron de produccion viable, mientras la evidencia MAST (NeurIPS 2025, UC Berkeley: 41-86.7% fallo en MAS; degradacion compuesta de handoffs; costo 2-5x) sigue desaconsejando el peer-to-peer para el equipo y la etapa actuales.

**Tres niveles (taxonomia vinculante):**

| Nivel | Patron | Estado | Coordinacion |
|-------|--------|--------|--------------|
| 1 | Sub-agentes atomicos (P16): orquestador delgado stateful invoca sub-agentes stateless | PERMITIDO (preexistente) | El workspace orquesta; sub-agentes no se comunican entre si |
| 2 | Handoff orquestado: sub-agentes especializados con handoff estructurado, scope contract y verification checkpoint | HABILITADO por P17, bajo condiciones | El workspace/orquestador media cada handoff; NO hay canal directo agente-agente |
| 3 | MAS peer-to-peer: agentes autonomos que se comunican/debaten entre si (A2A directo, debate) | CERRADO | Agente-a-agente directo |

**Condiciones de activacion del Nivel 2 (todas obligatorias):**

1. Justificacion por aislamiento de contexto: un sub-agente solo se incorpora si el caso requiere ventana de contexto limpia y aislada (no por estetica). Si no, se resuelve single-agent + skills.
2. Handoff estructurado, no conversacional: paquete estructurado (objetivo, hallazgos, constraints, scope contract, recomendacion); prohibido el canal directo agente-agente.
3. Verification checkpoint pre-handoff: el receptor declara su plan antes de accion de alto impacto; el orquestador valida el scope.
4. Cap de 5 handoffs por trayectoria (fiabilidad compuesta degrada: 10 handoffs @99% = 90.4%). Superarlo dispara Human Gate o aborto.
5. Profundidad maxima 3 niveles operativos (workspace -> sub-agente -> skills). Sub-agentes no crean sub-sub-agentes.
6. Telemetria P8 obligatoria por handoff (origen, destino, scope, tokens, resultado, latencia).

**Guardrails que P17 NO puede relajar (heredados):** Human Gate de P14 / restriccion Tier 2 v1.5 (ningun handoff omite el Human Gate cuando action_class in {external_communication, external_mutation}, umbral_impacto >= high, o data_classification >= N3); aislamiento multi-tenant (todo handoff preserva tenant_id; RLS source of truth); P3 draft-first y P13 contencion intactos; P16 (orquestador delgado + sub-agentes atomicos) se mantiene.

**Criterios de reevaluacion del Nivel 3 (cerrado hasta cumplir TODOS):** (1) eval harness interno operativo; (2) fiabilidad de handoff medida en produccion >= 98% sostenida; (3) volumen que justifique costo 2-5x; (4) equipo capaz de depurar coordinacion inter-agente sin comprometer validacion de mercado; (5) decision CEO documentada + nueva version de P17.

**Origen:** decision CEO 2026-06-01 sobre research consolidado (swarm Kimi + swarm Claude) reconciliado con evidencia MAST preexistente. Ver RESEARCH_AGENTES_CONSOLIDADO_2026_v1 y ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.

---

## Jerarquía de invariantes (v1.4)

No todos los principios admiten el mismo tipo de modificación. Esta jerarquía
es vinculante:

### Tier 1 — Invariantes absolutos
P1 · P3 · P5 · P9 · P13 + hard blocks DPA de POL_DATA_CLASSIFICATION

Modificación posible solo por: nueva versión del principio + changelog completo
+ revisión integral del CORE + aprobación CEO documentada.

NO admiten: excepción runtime, override CEO ad-hoc, cláusula condicional por
caso, derogación temporal, override por urgencia operativa.

### Tier 2 — Principios con override CEO documentado caso-a-caso
P2 · P4 · P6 · P7 · P8 · P10 · P11 · P12 · P14 · P17

Admiten excepción runtime con: justificación CEO escrita + audit trail
inmutable + revisión post-hecho. La excepción no modifica el principio,
solo lo suspende para el caso específico.

**Restricción del override Tier 2 (v1.5):** ningún override Tier 2 puede
omitir el Human Gate de P14 cuando se cumple cualquiera de:

- `action_class` ∈ {`external_communication`, `external_mutation`}
- `umbral_impacto` >= `high`
- `data_classification` >= N3 en el contexto del prompt o del output

En esos casos, el override puede acelerar otros pasos (ej. saltar
Deterministic First de P14, ajustar approval_threshold dentro del rango
permitido) pero el Human Gate sigue siendo obligatorio. La razón: estos
3 disparadores definen acciones cuyo error genera daño irreversible
para el cliente del tenant — el override nunca debe poder eliminarlos.

### Tier 3 — Principios meta (sobre los principios mismos)
P0 (un agente no es un prompt) — declarativo, no operativo, no tiene
mecanismo de excepción aplicable.

---

## Glosario vinculante (v1.4)

Términos usados en los principios con definición operativa precisa.
Cualquier referencia a estos términos en el CORE o en políticas
derivadas debe interpretarse según esta sección.

### error_grave

Cualquiera de las siguientes ocurrencias en una ejecución del agente:
- Data leak detectado: dato N2+ enviado a destinatario no autorizado, dato
  cross-tenant filtrado, contenido CEO-ONLY expuesto en output de tier
  inferior
- Acción externa ejecutada sin aprobación humana cuando P3 la requería
- Compromiso financiero generado: monto, fecha de pago, términos comerciales
  enviados a tercero sin revisión
- Mutación de datos del cliente (CRM write, edit en sistema del tenant)
  no autorizada por scope del agente
- Violación documentada de policy del provider LLM (Anthropic, OpenAI,
  Google) que el provider notifique formalmente
- Hallucination con impacto operativo: dato inventado que llegó a producción
  y disparó acción posterior
- Cualquier acción que viole un Tier 1 de la Jerarquía de invariantes

### humano_responsable

El humano designado en la AgentSpec del agente como aprobador de sus
acciones. Reglas de identificación (en orden de precedencia):

- Si el agente tiene `position_assignments` declaradas en su AgentSpec
  (mecanismo de binding agente↔position definido en SPEC_FABERLOOM_AGENT_COMPOSITION
  — Anillo 2), el humano_responsable es el ocupante actual de esa position
  en el tenant. Si la position está vacante, escala al admin del tenant.
- Si el agente está asignado a un usuario específico (scope=user), el
  humano_responsable es ese usuario.
- Si el agente está publicado a la organización (scope=org) sin position
  específica, el humano_responsable es el admin del tenant.
- En propagación cross-skill (P12), el humano_responsable de cada skill
  receptor se evalúa independientemente para confirmar la propagación
  a ese skill.
- Si ninguna de las anteriores aplica, la acción se bloquea hasta que la
  AgentSpec se complete con asignación válida.

### approval_threshold

Umbral mínimo de confidence (0.0 a 1.0) que un output debe alcanzar para
ser elegible de aprobación automática en niveles que lo permitan, o para
NO requerir Human Gate de P14. Default: 0.85. Configurable per-skill en
AgentSpec, nunca por debajo de 0.70 sin aprobación CEO documentada.

### action_class

Clasificación de la acción que un agente está por ejecutar. 5 clases:

- `read_only` — consulta sin side-effect (KB read, vector retrieval)
- `internal_write_reversible` — escritura interna que se puede revertir
  (etiqueta, draft, status update)
- `internal_write_irreversible` — escritura interna persistente (gold
  sample promovido a memoria, audit entry)
- `external_communication` — comunicación a terceros (email, WhatsApp,
  Slack a cliente)
- `external_mutation` — mutación de datos en sistemas del cliente o
  compromiso financiero (CRM write, factura, cobro)

`external_communication` y `external_mutation` requieren Human Gate
obligatorio (P3) sin importar nivel de autonomía.

### umbral_impacto

Severidad cuantificada del impacto si la acción falla. 4 niveles:

- `low` — error corregible sin afectar relación comercial ni datos del
  tenant
- `medium` — error requiere comunicación correctiva al humano responsable
- `high` — error afecta relación con cliente del tenant, requiere disculpa
  formal o reposición
- `critical` — error genera incidente legal/regulatorio, fuga de datos
  protegidos, o trust collapse

Acciones con umbral_impacto >= `high` requieren Human Gate de P14 incluso
si confidence > approval_threshold.

### scope_user_self

Modalidad de acceso dentro de scope=org cuando el consultante consulta
sus PROPIOS datos. Distinto de scope=user (agente personal): acá el
agente está publicado a la organización pero el consultante pide
información sobre sí mismo.

- Datos propios N0/N1 → Nivel A (sesión normal, sin step-up)
- Datos propios N2/N3 → Nivel B (step-up obligatorio, MFA fresh + IP
  estable, TTL 15 min)
- Datos propios N4 (biométrico) o documentos formales con valor legal
  → Nivel C (step-up + propósito declarado + aprobación humano_responsable)

El step-up no sustituye al pre-filtering: el sistema solo recupera
chunks N2+ del consultante DESPUÉS de validar el step-up del nivel
correspondiente. Sin step-up válido, el chunk no se carga al modelo.

### step_up_authentication

Verificación de identidad adicional por encima de la sesión normal,
necesaria para autorizar acceso a datos sensibles propios del consultante.
3 niveles definidos:

| Nivel | Acceso | Auth | TTL |
|---|---|---|---|
| A | N0/N1 propio | session token | duración de sesión |
| B | N2/N3 propio | session + MFA OTP fresh + reconfirm contraseña + IP estable | 15 min |
| C | N4 propio o documento formal con valor legal | Nivel B + propósito declarado + aprobación humano_responsable | doc con expiración explícita |

Sin el step-up del nivel correspondiente válido, los chunks de la
classification afectada NO se recuperan en el retrieval (pre-filtering
hard). El agente responde con mensaje de "verificación adicional
requerida" sin haber visto el dato.

Step-up SOLO desbloquea datos PROPIOS. Datos de terceros nunca son
accesibles vía step-up — requieren ser tercero autorizado en
AgentSpec.

---

## Lo que estos principios NO son

- No son una restricción de velocidad — un agente simple puede cumplirlos con implementación mínima
- No son burocracia — cada principio resuelve un problema real de agentes en producción
- No son definitivos — pueden evolucionar con aprobación CEO y changelog documentado, respetando la Jerarquía de invariantes

---

Changelog:
- v1.6 (2026-06-01): +Principio P17 (Composicion multi-agente por niveles). Levanta la prohibicion por defecto de multi-agente: habilita Nivel 2 (orquestador delgado + handoff estructurado) como opcion de primera clase bajo 6 condiciones + guardrails heredados (Human Gate Tier 2 v1.5, aislamiento multi-tenant, P3/P13/P16 intactos). Cap 5 handoffs/trayectoria, profundidad max 3. Nivel 3 (MAS peer-to-peer) CERRADO con 5 criterios de reevaluacion. Revisa fila Composicion de agentes de tabla P14. P17 clasificado Tier 2. Origen: decision CEO sobre RESEARCH_AGENTES_CONSOLIDADO_2026_v1 (swarm Kimi + Claude) reconciliado con evidencia MAST NeurIPS 2025.
- v1.5 (2026-04-28): Iteración 3 de auditoría CORE post ChatGPT 5.5 + Kimi K2.6 iter 2. Cierra BLOCKER H9 (ChatGPT) + 9 hallazgos consolidados. Cambios: (a) P13 jerarquía intra-tenant reescrita como **pre-filtering en retrieval** (no output filtering) — corrige redacción ambigua de v1.4; (b) +Step-up authentication 3 niveles (A/B/C) en P13 para scope=user_self con datos N2+ propios; (c) P12 nueva fila en tabla "Alcance natural" — hechos N2/N3/N4 NUNCA propagables Org-wide ni Cluster sin des-identificación + aprobación CEO; (d) P12 confirmante humano cross-skill = humano_responsable del skill receptor (no del originador); (e) +Apéndice operativo Clasificador en P11 (Haiku 4.5 + JSON forzado, threshold 0.80, fallback Human Gate, mantenimiento trimestral); (f) +Tabla de transiciones P7 con eventos disparadores y timeouts; (g) Tier 2 override no puede omitir Human Gate cuando action_class external/umbral_impacto high/data N3+; (h) Glosario humano_responsable resuelve referencia D12 (apunta a SPEC_FABERLOOM_AGENT_COMPOSITION Anillo 2); (i) +scope_user_self y step_up_authentication en glosario. Origen: ChatGPT iter 2 H9-H13 + Kimi iter 2 B2.1, B2.2, R2.5, G3.6, G3.7, G3.9 + decisión CEO Gemini step-up auth.
- v1.4 (2026-04-28): Iteración 2 de auditoría CORE post ChatGPT 5.5 + Kimi K2.6. Decisiones CEO via Gemini: (a) P3 absoluto reforzado — Nivel 3 AUTO_NOTIFICA reescrito como solo internas reversibles, NO externas; (b) P13 reforzado con aislamiento absoluto del aprendizaje + cláusula de jerarquía interna intra-tenant (agente personal vs publicado, permisos por rol). +P11 reescrito (multi-propuestas, single-destino-por-escritura). +Sección "Jerarquía de invariantes" (Tier 1/2/3). +Glosario vinculante (error_grave, humano_responsable, approval_threshold, action_class, umbral_impacto). Origen: 4 BLOCKERs + hallazgos convergentes consolidados en chat MWT Knowledge.
- v1.3 (2026-04-27): +Principio 14 (Deterministic First → LLM Fallback → Human Gate). Origen: Kimi #3 Ruflo, patrón emerge en 3 de 4 dominios analizados. Ver docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md.
- v1.2 (2026-04-17): +Principio 13 (Contención de memoria y autonomía) + ModelFingerprint como gate de probation cross-modelo.
- v1.1 (2026-04-16): Versión base con P0-P12.

---

## NOTA DE APLICACION -- P4 Shadow threshold en FaberLoom E1

El principio P4 establece >= 3 ejecuciones con > 70% como piso global.

Para Foundation Beta E1 de FaberLoom aplica un override documentado:

  Threshold E1: 10 runs reales de produccion con approval_rate >= 70%
  Gate: aprobacion explicita Owner/Admin
  Revisable: a las 8 semanas de beta

Ver especificacion completa en:
  ENT_FB_DECISIONES_E1_v1.md seccion D5.1

Este override es especifico de E1 y no modifica el principio general
que aplica a otros contextos y versiones futuras.

Registrado: 2026-06-24 -- auditoria Fugu Ultra + Kimi 2.7 Round 5.
