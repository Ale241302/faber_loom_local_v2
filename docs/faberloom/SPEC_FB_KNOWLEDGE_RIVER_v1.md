# SPEC_FB_KNOWLEDGE_RIVER_v1 — Templates como activos organizacionales con curaduría colectiva
id: SPEC_FB_KNOWLEDGE_RIVER_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-05-02 (v1.1 post correccion modelo 2 capas R5)
aprobador: CEO (sesión Cowork 2026-04-30 + correccion 2026-05-02)
aplica_a: [FaberLoom]
relacionado: ENT_FB_USER_LEARNING_MODEL_v1 · ENT_FB_COMMITTEE_OPERATING_MODEL_v1 · POL_FB_KR_PRIVACY_TIERS_v1.1 · ENT_FB_RFQ_REPLAY_SET_v1.1 · SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.1 · ARCH_AGENT_PRINCIPLES.md

---

## Aclaracion v1.1 · modelo 2 capas (correccion R5 + CEO 2026-05-02)

> **CRITICO · canonizado en v1.1.** El Knowledge River opera en **2 capas distintas** que NO se mezclan:
>
> **CAPA 1 USUARIO (L0 + L1 + L2)** · gobernada por `ENT_FB_USER_LEARNING_MODEL_v1`
> - Actor: AM individual con SUS agentes
> - Cadencia: AM-driven · cuando quiera
> - Privacidad: SIN k-anon (es SU data)
> - Decisiones: AM soberano sobre SU agente · puede aplicar/editar/ignorar patterns personales
> - Memoria: L2 episodica privada · solo el AM ve sus aprendizajes
>
> **CAPA 2 ORGANIZACION (L3 + L4)** · gobernada por `ENT_FB_COMMITTEE_OPERATING_MODEL_v1`
> - Actor: Comite (curador + reviewers · rol distinto del AM)
> - Cadencia: semanal/mensual estructurada
> - Privacidad: k-anon ≥5 OBLIGATORIO + 7 checks privacy
> - Decisiones: comite gobierna patterns cross-AM que cumplen k-anon
> - Memoria: L3 colectivo · L4 indexed firmado
>
> **Transicion L2 → L3** es responsabilidad EXCLUSIVA del comite (capa 2). No hay auto-promote desde capa 1.
>
> **MWT v1 con 1 AM (Alvaro multi-hat)** · capa 2 esta dormida hasta multi-AM · todos los patterns quedan en L2 personal.
>
> Ver detalles operacionales en `ENT_FB_USER_LEARNING_MODEL_v1` y `ENT_FB_COMMITTEE_OPERATING_MODEL_v1`. El previo `ENT_FB_CURATOR_OPERATING_MODEL_v1` queda DEPRECATED por mezclar las 2 capas.

---

## Declaracion

Este SPEC define la arquitectura del **Knowledge River** de FaberLoom: el modelo por el cual los agentes de la plataforma dejan de ser artefactos privados y se convierten en **activos organizacionales que capturan y destilan conocimiento institucional** a traves del uso colectivo.

El concepto central:
- los **templates de agentes** son la unidad organizacional (no el agente individual)
- cada template es un **activo con P&L propio**
- el conocimiento crece desde el **rio de contribuciones de los usuarios**
- un **comite de curaduria** filtra y firma que entra al template
- los patterns recurrentes se elevan a **mejores practicas destiladas**

Este modelo resuelve el problema #1 del B2B regulado: **retencion de conocimiento institucional**. La gente se va con la cabeza llena; aca el conocimiento queda en el agente.

**Diferencial defendible vs ChatGPT Workspace Agents:** ellos permiten compartir un agente con el equipo donde cada usuario tiene su instancia privada. FaberLoom canaliza el conocimiento de N usuarios hacia un solo activo organizacional con curaduria colegiada y audit trail granular.

---

## §1 · Modelo conceptual

### 1.1 La unidad central es el TEMPLATE

```
TEMPLATE (activo organizacional con P&L propio)
   ├ ID, identidad, archetype
   ├ skills · KB · learnings firmados · gold samples
   ├ comite de curaduria responsable
   ├ metricas de adopcion · calidad · crecimiento · ROI
   ├ biografia publica (cómo evoluciono)
   └ politica de privacidad per template (data retention, k-anonymity)

      ↓ usuario "toma prestado" (clona)

INSTANCIA (efimera per usuario)
   ├ hereda todo del template (read-only)
   ├ memoria episodica privada del usuario (no compartida)
   ├ contribuciones al pool del template (anonimas)
   └ se descarta cuando el usuario lo abandona
```

### 1.2 Metafora: agentes como libros de una biblioteca viva

```
BIBLIOTECA del TENANT (catalogo curado)
   ↓ usuario activa (toma prestado)
INSTANCIA personal (lee + interactua)
   ↓ contribuciones
COMMON POOL (rio anonimo agregado)
   ↓ comite filtra
KNOWLEDGE INDEXED (firmado, propaga)
   ↓ proxima version del template
BIBLIOTECA enriquecida (siguiente lector hereda valor)
```

El conocimiento de la organizacion **no se escribe**, se **destila** del uso real. El curador no es autor — es destilador.

---

## §2 · Las 5 capas de conocimiento

| Capa | Que es | Persistencia | Quien accede | Storage |
|---|---|---|---|---|
| **L0 · KB inicial** | docs subidos al crear el template | permanente · editable por curador | todos los clones | postgres + pgvector |
| **L1 · Working** | contexto del run actual | volatil · solo durante run | nadie despues del run | in-memory · LiteLLM |
| **L2 · Episodic privada** | log de interacciones del usuario individual | TTL 90d | solo el usuario propietario del clon | postgres con user_id como filtro estricto |
| **L3 · Pool colectivo** | agregado anonimo de contribuciones | persistente hasta promocion o descarte | comite (lectura agregada) · usuarios contribuyen anonimo | postgres tabla `template_pool` con k-anon ≥ N |
| **L4 · Indexed firmado** | learnings/gold/skills firmados por comite | immutable + versionada | todos los clones (read) · comite (firma) | postgres tabla `template_indexed` + gold_samples/ |

**Regla critica:** L2 es privada per usuario · LFPDPPP/GDPR cumple porque el usuario tiene confidencialidad de su uso. Solo lo agregado anonimo del pool sale.

**Regla critica:** L4 es immutable + versionada. Los cambios firmados son archivar+nueva version (estilo git commit), nunca edit in-place. Mantiene audit trail.

---

## §3 · Los 3 niveles de aprendizaje

Heredados de POL_FB_OUTCOME_ACCOUNTABILITY pero aplicados al modelo de templates:

| Nivel | Que cubre | Gate | Audit |
|---|---|---|---|
| **L1 · Auto** (sin firma) | ajustes safe del clon individual: re-rank gold_samples por uso, refresh KB chunks, threshold cosmetico, budget dinamico | sin firma · automatico | log a `auto_learnings` · admin ve dashboard 24h |
| **L2 · Firma rapida** | pattern del pool sale a L4 · propaga a clones · cambios en prompts de skill · gold_sample nuevo · ajuste pre-dispatch filter | 1 reviewer recomienda + curador firma con un click + diff | log a `iteration_log` con admin_id |
| **L3 · Critico** | cambia outcome metric · autonomy level · sub-agentes · archetype · ARCH/POL · ≥3 secciones de una iteracion | 2 reviewers recomiendan + curador firma con justificacion textual + auto-SHADOW del template 30d | log a `critical_changes_log` con justificacion immutable |

Configuracion del Nivel 1 esta definida per template en `POL_FB_AUTO_LEARNING_SCOPE` (admin del tenant declara que safe ops permite).

---

## §4 · Los 3 roles del modelo

Sin Owner / Editor / Approver / Consumer. Solo 3 roles claros:

| Rol | Que hace | Cuantos por template |
|---|---|---|
| **Curador** | evalua patterns del pool · firma indexaciones (L2/L3) · transfer ownership · responsable formal del template | 1 principal + 0-N reviewers segun modo de gobernanza |
| **Usuario** | activa templates del catalogo · usa · contribuye anonimamente al pool · marca util/no util · sugiere mejoras | sin limite |
| **Auditor** | read-only completo · audit trail · iteration_log · reportes de compliance | 0-N (opcional) |

Un mismo usuario del tenant puede tener distintos roles en distintos templates: usuario en uno, curador en otro, auditor en otro.

---

## §5 · 3 modos de gobernanza · admin del tenant elige al crear template

### A · Curador unico (default)

- 1 persona firma todo
- bajo impacto · datos no sensibles
- ejemplo: review_triage Amazon, listing_opt

### B · Comite de curaduria

- 1 Curador Principal (firma final, responsable formal)
- 2-3 Reviewers (proponen, revisan, recomiendan)
- 0-N Auditores read-only (compliance externo)
- templates criticos · datos regulados · alto volumen
- ejemplo: derecho laboral, HR, compliance

### C · Gobernanza federada

- Curador principal global
- Reviewers especialistas por sub-dominio
- ejemplo: template universal HR con sub-comites por pais (LFPDPPP MX, GDPR EU, Ley 19628 CL)

---

## §6 · Workflow del pool (detection → review → firma → indexed)

```
[1] sistema detecta pattern · N consultas · M/N satisfaccion
        ↓ (k-anonymity ≥ 5 users distintos · sino no procesa)

[2] entra a "Cola de revision" del comite del template
        ↓ (visible a curador + reviewers · NO usuarios)

[3] cualquier reviewer puede:
        · 👀 marcar como revisado (recomienda firmar)
        · ✎ editar texto antes de firma
        · 💬 comentar en hilo del pattern
        · ✗ marcar como falsa practica (descarta)
        · 🔝 escalar a curador principal
        ↓

[4] cuando ≥1 reviewer recomienda:
        pasa a "Pendiente firma del curador"
        ↓ (en Modo A se salta este paso · curador firma directo)

[5] Curador Principal:
        · firma simple (nivel 2 · cambios output)
        · firma con justificacion (nivel 3 · cambios identidad/autonomia)
        · rechaza con razon documentada
        · solicita revision adicional (vuelve a paso 3)
        ↓

[6] indexed a L4 · propaga a todos los clones del template
        nueva version del template publicada
        ↓

[7] iteration_log granular:
        cada miembro tiene su firma + timestamp + accion
        diff_hash + scope + admin_id immutable
```

---

## §7 · Configuracion de gobernanza per template

La gobernanza vive como **seccion dedicada en la configuracion del template**, accesible al admin del tenant + curador principal.

### Campos configurables

```yaml
governance:
  mode: B  # A · B · C
  profile: "alto_riesgo_legal"  # ← perfil preconfigurado del tenant

  members:
    curator_principal:
      user_id: maria_rodriguez
      email: maria@bufete.cr
      escalation_timeout_h: 168  # 7 dias

    reviewers:
      - user_id: juan_perez
        scope: "derecho_colectivo"
      - user_id: ana_lopez
        scope: "derecho_individual"

    auditors:
      - user_id: pwc_externo
        access: read_only

  rules:
    quorum:
      L1_auto: enabled  # ajustes safe sin firma
      L2_firma_rapida: "1 reviewer + curador"
      L3_critico: "2 reviewers + curador con justificacion"
      compliance_skill_change: "comite_completo"  # todos firman

    timeouts:
      notify_pending_days: 7
      escalate_to_admin_days: 14
      auto_archive_days: 30

    privacy:
      k_anonymity_threshold: 5
      data_retention_days: 90
```

### Perfiles preconfigurados del tenant (atajo)

El admin del tenant puede definir perfiles reusables. Cuando alguien crea un template, elige un perfil en lugar de configurar todo:

| Perfil | Caso de uso |
|---|---|
| `operacional_rutinario` | A · curador unico + auto-aprobacion L1 · timeouts amplios |
| `alto_riesgo_legal` | B · 3 personas + quorum estricto · k-anon ≥5 |
| `cumplimiento_regulado` | B · 3 personas + auditor obligatorio · retention 365d |
| `marca_publica` | C · curador + reviewers por canal · timeouts cortos |
| `compliance_iso27001` | B · auditor obligatorio + journal export trimestral |

### Reglas de quien puede tocar la gobernanza

| Accion | Quien | Audit |
|---|---|---|
| Cambiar modo A/B/C | Admin tenant + Curador principal · firma colegiada | nivel 3 critico · justificacion obligatoria |
| Agregar/remover miembro del comite | Admin tenant + Curador principal | nivel 2 · notificacion al comite entero |
| Editar reglas de quorum/timeouts | Curador principal solo si esta en perfil custom | nivel 2 · alerta a reviewers |
| Transferir ownership del curador principal | Curador actual con firma + admin tenant aprueba | nivel 3 · auto-SHADOW del template 7d |

### Cambio de modo durante la vida del template

- Patterns ya firmados quedan firmados con su firma original (no se invalidan)
- Patterns en cola re-rutean al nuevo flujo
- Audit log registra el momento exacto del cambio + justificacion
- Nuevos miembros reciben onboarding del template

Cambio de modo NUNCA invalida lo firmado · solo cambia el flujo hacia adelante.

---

## §8 · Best practices destiladas (feature explicito)

El sistema NO solo guarda conocimiento · **destila lo que funciona** y lo presenta al comite como candidatos a "best practice".

### Mecanica

```
Pool del colectivo (L3) tiene N interacciones
  ↓
Sistema detecta cluster:
  · "estos K usuarios resolvieron este tipo de caso"
  · "M/K quedaron satisfechos (M/K > threshold)"
  · "el patron comun fue X"
  · "agregaria valor si se eleva a gold"
  ↓
Score automatico · 0-100:
  · frecuencia (cuantos users)
  · satisfaccion (M/K)
  · diversidad (¿son K users distintos o el mismo de varios devices?)
  · impacto (¿que metrica afecta?)
  · novedad (¿no esta cubierto por gold existente?)
  ↓
Si score > threshold (ej: 70):
  · pasa a "Best Practice Candidates" en bandeja del comite
  · presenta evidencia: cuales conversaciones contribuyeron
    (anonimizadas) · que skills usaron · cuanto ahorraria
  ↓
Comite firma o rechaza:
  · si firma → entra a L4 como gold sample firmado
  · si rechaza → marca pattern como "falsa practica"
    para que el sistema no lo proponga otra vez
```

### Ejemplo concreto · template "Derecho Laboral"

```
🏆 Best Practice Candidate · score 87/100

"Renuncia voluntaria · prima de antiguedad"

  · 14 consultas en 30d
  · 12/14 marcados util (86% satisfaccion)
  · 4 abogados de 47 distintos (k-anon ✓)
  · respuesta comun: estructura X + cita STPS art. 162
  · impacto: si se firma como gold, próximas consultas
    ahorran ~8min/c/u

  evidencia: 14 conversaciones anonimizadas disponibles para review

  [✓ firmar como gold sample] [📝 editar antes de firmar]
  [✗ rechazar · marcar como falsa practica]
  [⏸ posponer · necesita mas data]
```

El curador NO escribe la mejor practica · valida que es practica real, no patron espurio.

---

## §9 · 6 mecanismos de defensa

| Riesgo | Mecanismo |
|---|---|
| **Envenenamiento del pool** (1 user malicioso) | weighting por user reputation + diversity threshold (≥5 users distintos) + outlier detection automatico antes de propuesta al comite |
| **Curador overloaded** | pre-filtrado IA del pool · dashboard prioriza por score · cap declarable (max 10 propuestas/semana) · resto queda en backlog |
| **Sesgo del corpus** (todos juniors) | weighting opcional por seniority declarado · auditor externo trimestral (rol Auditor) · reporte de diversidad de contribuyentes |
| **Privacidad colectiva** (org pequena) | k-anonymity threshold ≥ N usuarios distintos · si no se cumple, no se procesa pattern · transparente en metricas |
| **Drift sin gobierno** (curador renuncia) | timeouts escalation · si curador inactivo > 30d, alerta al admin del tenant para reasignar · template puede quedar en "freeze" hasta reasignacion |
| **Lock-in** | export del template entero en formato estandar (SKILL.md extendido + KB tar.gz + learnings.json) · interoperable con otras plataformas |

---

## §10 · Metricas del template (P&L del activo)

```
TEMPLATE: ⚖️ Derecho Laboral · v4.7 · 4 meses de vida

📊 Adopcion
   47 usuarios activos · 1240 consultas totales · 287 ultimos 7d
   89% retencion mensual · 23% nuevos usuarios este mes

⭐ Calidad
   92% satisfaccion · accept rate 88% · escalation rate 4%

📚 Crecimiento del activo (capital intelectual)
   docs indexados: 142 → 287 (+102%)
   learnings firmados: 23 (en 4 meses)
   gold samples: 12 → 47
   skill versions: 7 ediciones · 3 forks

💰 ROI
   tiempo ahorrado: ~890 horas-equivalente (47 abogados × ~19h)
   cost del template: $84/mes (LLM + storage + API calls)
   valor declarado por gerencia: $42k Q1 (estimacion)

🏆 Best Practices destiladas
   8 patterns elevados a gold · 3 propuestas pendientes

🏛 Salud del comite
   tiempo promedio de firma: 2.3 dias (sano)
   tasa de rechazo: 8% (sano)
   patterns reversados post-firma: 0 (excelente)
```

---

## §11 · UX en 3 universos de pantallas

Cada rol tiene su entry point distinto al loguearse. No hay pantalla universal.

### Universo 1 · Operacion (usuario comun)

- Catalogo de la biblioteca del tenant
- Mis agentes activos
- Drafts pendientes (HITL P3)
- Historial de mis consultas
- Marcar util/no util · sugerir mejoras

### Universo 2 · Gobernanza (curador / reviewer)

- **Bandeja del comite** · cross-template
  · pendientes en todos los templates donde participo
  · agrupado por urgencia (vence pronto · asignados a mi · libre)
  · best practice candidates priorizados
  · mis metricas como curador
- Vista de gobernanza per-template
  · cola del pool con propuestas pendientes
  · KB indexada actual editable
  · biografia narrativa del template
- Detalle del pattern
  · evidencia · hilo de discusion · firma o rechazo

### Universo 3 · Audit (auditor)

- Audit log cross-template read-only
- Filtros: template / miembro / accion / fecha / severidad
- Exports: CSV / PDF para LFPDPPP/ISO 27001
- Reportes mensuales de gobernanza

Un usuario con multiples roles (ej: curador en un template, usuario en otro) tiene switcher en topbar para cambiar de universo.

---

## §12 · Diferencial vs ChatGPT WA / Notion / Linear

| Feature | ChatGPT WA | Notion AI / Linear AI | FaberLoom Knowledge River |
|---|---|---|---|
| Compartir agente con equipo | ✓ | ✓ | ✓ |
| Memoria persistente | ✓ auto-mutante | ✗ | ✓ con gate humano P5 |
| Curaduria colegiada | ✗ | ✗ | ✓ comite con quorum configurable |
| Pool de contribuciones colectivas | ✗ | ✗ | ✓ k-anon · agregacion automatica |
| Best practices destiladas | ✗ | ✗ | ✓ con scoring + evidencia |
| Audit trail granular per firma | basico | basico | ✓ iteration_log immutable per accion |
| Template como activo organizacional con P&L | ✗ | ✗ | ✓ adopcion · crecimiento · ROI |
| Compliance B2B regulado (LFPDPPP/ISO 27001) | parcial | parcial | ✓ nativo desde dia 1 |
| Lock-in / portabilidad | alto | alto | ✓ export estandar (SKILL.md+KB+learnings) |

**El moat real:** retencion de conocimiento institucional. Imposible de copiar facilmente porque requiere arquitectura desde el dia 1 (multi-tenant + versioned KB + audit + curaduria como rol primario).

---

## §13 · Pendientes para v2/v3

### v2 · pendientes inmediatos cuando entre tenant 2

- pricing del template: tier subscription + usage overflow + posible outcome-based
- co-curaduria silenciosa (backup curador)
- forking de templates (estilo GitHub) · merge back con aprobacion del curador del original
- migracion de templates entre tenants (si un usuario va de tenant A a tenant B)

### v3 · roadmap diferido

- Marketplace cross-tenant: tenant publica template para que otros lo licencien · royalty al tenant origen · gobernanza de IP
- Auditor IA: pre-filtrado del pool con LLM antes de presentar al comite humano
- Federated learning entre tenants: patterns que aparecen en multiples tenants se pueden proponer como "standard de industria" (con consentimiento)
- Templates con SLA: el tenant ofrece tiempos de respuesta garantizados a sus usuarios

---

## §14 · Relacion con archivos FB existentes

Este SPEC extiende y reposiciona varios archivos previos:

| Archivo previo | Como se relaciona |
|---|---|
| `SPEC_FB_AGENT_BUILDER_v1` | sigue siendo el plan de construccion del builder · Knowledge River es el modelo operacional encima |
| `SCH_FB_SKILL_MANIFEST_v2` | el manifest del agente se aplica al template · cada clon hereda el manifest sin modificar |
| `POL_FB_OUTCOME_ACCOUNTABILITY` | regla P15 aplica al template (no al clon individual) · si el template no muestra trending agregado vuelve a SHADOW |
| `ENT_FB_TEMPLATE_LIBRARY_v1` | catalogo inicial · ahora se reposiciona como "biblioteca del tenant" con curaduria colegiada |
| `ENT_FB_AGENT_ARCHETYPES_v1` | los 7 arquetipos siguen siendo validos · cada template declara su archetype |
| `SCH_FB_FLOW_DAG` | aplica al proceso del template · se hereda a clones |
| `SCH_FB_TASK_ENTITY` | tasks per clon · tenant_id + template_id + user_id como filtros |
| `ENT_FB_TOOL_CATALOG_v1` | tools disponibles per template · tenant configura permisos a nivel template |
| `SCH_FB_CLI_INTERFACE` | CLI debe agregar comandos: `fbl template ls`, `fbl template publish`, `fbl committee assign` |

---

## §15 · Pendientes para Design

Cuando este SPEC se traspase a Design, los entregables esperados son:

1. **Biblioteca del tenant** (catalogo de templates con metricas)
2. **Vista del usuario** (mis agentes activos + activar nuevo + sugerir mejora)
3. **Bandeja del comite** (cross-template · pendientes priorizados)
4. **Vista de gobernanza per template** (pool + best practices + KB indexada + biografia)
5. **Detalle del pattern** (evidencia + hilo + firma colegiada)
6. **Configuracion de gobernanza** (modo A/B/C + perfiles + miembros + reglas)
7. **Audit dashboard** (cross-template · filtros · exports)

Todo respetando el design system sealed (paleta calida cobre + Georgia italic + Inter + dark/light paritarios).

---

## Stamp
VIGENTE — 2026-04-30 — SPEC inicial v1.0 del Knowledge River.

## Changelog
- v1.0 (2026-04-30): creacion. Modelo de templates como activos organizacionales con curaduria colegiada. 5 capas de conocimiento. 3 niveles de aprendizaje. 3 roles. 3 modos de gobernanza A/B/C con perfiles configurables. Pool del colectivo con k-anonymity. Best practices destiladas con scoring automatico. 6 mecanismos de defensa. Metricas del template como activo (adopcion · calidad · crecimiento · ROI). 3 universos de pantallas (operacion · gobernanza · audit). Diferencial vs ChatGPT WA / Notion / Linear documentado. Pendientes v2/v3 listados. Derivado de iteracion CEO sesion Cowork 2026-04-30 evaluando 3 propuestas de Claude Design (Bandeja · Cockpit · Cuaderno) + insight critico CEO sobre captura de conocimiento + identificacion de mejores practicas + comite de curaduria.
