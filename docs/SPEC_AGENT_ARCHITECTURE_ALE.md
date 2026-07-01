# Especificación Técnica — Arquitectura de Agentes MWT
id: SPEC_AGENT_ARCHITECTURE_ALE
version: 1.0
fecha: 2026-04-16
para: Alejandro (AG-02)
de: CEO / Álvaro
status: PARA REVISIÓN
visibility: [INTERNAL]
stamp: PARA_REVISION — 2026-04-16
aplica_a: [MWT]

---

## Contexto

Esta semana se diseñó e implementó en la KB la arquitectura de agentes IA de MWT. Este documento explica qué se construyó, por qué, y qué implica para la plataforma **mwt.one** en futuros sprints.

**Nada de esto requiere cambios de código hoy.** Es información de diseño para que cuando llegue el sprint de integración, el modelo ya esté acordado.

---

## 1. Qué se construyó (capa KB — lado CEO)

Se definió una arquitectura de 3 capas para los agentes IA del sistema:

```
AgentSpec     → SKILL_*.md          → Qué ES el agente (estático, versionado)
AgentRuntime  → SKILL_RUNTIME.md    → Qué HACE en tiempo real (métricas, estado)
AgentMemory   → SKILL_MEM_*.md      → Qué APRENDIÓ (gold samples, patrones)
```

Hay **10 skills definidos**, todos en estado SHADOW (observan, no ejecutan autónomamente):

| Skill | Trigger word | Autonomía ceiling |
|-------|-------------|------------------|
| SKILL_AMAZON_OPS | `amazon-ops` | EJECUTA_INTERNO |
| SKILL_CLIENT_SERVICE | `client-service` | PROPONE |
| SKILL_COMPLIANCE_CHECKER | `compliance-check` | EJECUTA_INTERNO |
| SKILL_COPY | `copy` | PROPONE |
| SKILL_DEMAND_FORECASTER | `demand-forecast` | PROPONE |
| SKILL_EXPERIMENT_RUNNER | `experiment` | EJECUTA_INTERNO |
| SKILL_HUMANIZE_BRAND | `humanize-brand` | PROPONE |
| SKILL_HUMANIZE_COMMS | `humanize-comms` | PROPONE |
| SKILL_KB_AUDITOR | `kb-audit` | AUTO_NOTIFICA |
| SKILL_PROFORMA_BUILDER | `proforma` | PROPONE |

---

## 2. Cómo funciona el flujo (lado CEO hoy)

```
CEO escribe trigger word en sesión Cowork
        ↓
Sistema carga AgentSpec (SKILL_*.md) + AgentMemory (si existe)
        ↓
Agente ejecuta con ese contexto completo desde el primer token
        ↓
Genera output (draft / análisis / reporte)
        ↓
CEO aprueba / edita con correcciones / rechaza
        ↓
Evento estructurado registrado → termómetro de aprendizaje sube
        ↓
Cuando el termómetro está 🔴 (6+ outputs): CEO presiona "Indexar Aprendizaje"
        ↓
Modal muestra patrones detectados + gold samples candidatos
CEO confirma → se escribe a SKILL_MEM_{ID}.md (AgentMemory)
```

**Draft-first es un principio absoluto:** ningún skill envía emails, mensajes, ni ejecuta transacciones sin aprobación explícita del CEO. Esto no cambia con ningún nivel de autonomía.

---

## 3. Modelo de datos que necesitará la plataforma (futuro sprint)

Cuando se integre esta arquitectura en mwt.one, se necesitan las siguientes tablas Django:

### 3.1 `AgentSpec` (lectura desde KB, no editable en plataforma)

```python
class AgentSpec(models.Model):
    skill_id          = models.CharField(max_length=50, unique=True)  # "SKILL_AMAZON_OPS"
    trigger_word      = models.CharField(max_length=50, unique=True)  # "amazon-ops"
    autonomy_ceiling  = models.CharField(max_length=20)               # "PROPONE" | "EJECUTA_INTERNO" | "AUTO_NOTIFICA"
    status            = models.CharField(max_length=20)               # "SHADOW" | "ACTIVE" | "PAUSED" | "DEPRECATED"
    version           = models.CharField(max_length=10)               # "1.1"
    kb_refs           = models.JSONField()                            # lista de archivos KB que carga
    escalation_policy = models.TextField()
    updated_at        = models.DateTimeField(auto_now=True)
```

### 3.2 `AgentRuntime` (escritura en cada ejecución)

```python
class AgentRuntime(models.Model):
    skill             = models.OneToOneField(AgentSpec, on_delete=models.CASCADE)
    current_autonomy  = models.CharField(max_length=20)   # nivel real actual (≤ ceiling)
    total_executions  = models.IntegerField(default=0)
    shadow_executions = models.IntegerField(default=0)
    approval_rate     = models.FloatField(null=True)       # % aprobados sin edición
    edit_light_rate   = models.FloatField(null=True)       # % aprobados con ≤20% edición
    rejection_rate    = models.FloatField(null=True)
    pending_approvals = models.IntegerField(default=0)
    outputs_pending_consolidation = models.IntegerField(default=0)  # termómetro
    last_execution    = models.DateTimeField(null=True)
    memory_file       = models.CharField(max_length=100, null=True)  # "SKILL_MEM_COPY" o null
    updated_at        = models.DateTimeField(auto_now=True)
```

### 3.3 `AgentExecution` (log inmutable por ejecución)

```python
class AgentExecution(models.Model):
    skill             = models.ForeignKey(AgentSpec, on_delete=models.PROTECT)
    executed_at       = models.DateTimeField(auto_now_add=True)
    trigger_input     = models.TextField()                  # texto que activó el skill
    output_type       = models.CharField(max_length=20)     # "draft" | "report" | "analysis"
    autonomy_at_exec  = models.CharField(max_length=20)
    feedback          = models.CharField(max_length=30, null=True)  # "approved" | "approved_with_edits" | "rejected" | "escalated"
    edit_percentage   = models.IntegerField(null=True)      # 0-100
    correction_type   = models.CharField(max_length=20, null=True)  # "tone" | "data" | "structure" | "policy" | "scope"
    consolidated      = models.BooleanField(default=False)
    notes             = models.TextField(blank=True)

    class Meta:
        ordering = ['-executed_at']
```

### 3.4 `GoldSample` (memoria consolidada)

```python
class GoldSample(models.Model):
    skill             = models.ForeignKey(AgentSpec, on_delete=models.PROTECT)
    sample_type       = models.CharField(max_length=20)     # "style" | "decision" | "action"
    job_to_be_done    = models.TextField()
    canal             = models.CharField(max_length=50)
    context           = models.JSONField()                  # remitente, tipo, idioma, país
    input_original    = models.TextField()
    output_ideal      = models.TextField()
    mandatory_rules   = models.JSONField()
    prohibited_rules  = models.JSONField()
    allowed_sources   = models.JSONField()
    tone_voice        = models.TextField()
    approver          = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    version           = models.CharField(max_length=10)
    valid_from        = models.DateField()
    eval_result       = models.CharField(max_length=20)     # "passed" | "failed" | "drift"
    is_active         = models.BooleanField(default=True)
    created_at        = models.DateTimeField(auto_now_add=True)
```

---

## 4. Lógica de promoción de autonomía

Un skill solo puede subir de nivel cuando cumple **todos** estos criterios:

| Condición | Threshold |
|-----------|-----------|
| Ejecuciones en nivel actual | ≥ 10 |
| Approval rate | ≥ 80% |
| Edit-light rate (≤20% edición) | ≥ 60% |
| Rejection rate | ≤ 10% |
| Días estables sin error grave | ≥ 14 |
| AgentMemory activa | Sí |
| Aprobación CEO | Sí — siempre requerida |

Excepción: SHADOW → ACTIVE requiere solo ≥ 3 ejecuciones con approval rate > 70%.

**Degradación automática** (sin aprobación CEO) si:
- Rejection rate > 30% en últimas 5 ejecuciones
- Error grave en acción de alto impacto
- Referencia a archivo KB roto o DEPRECATED

---

## 5. Autonomy Ladder — 5 niveles

```
Nivel 0 — SHADOW        → observa, no sale al usuario
Nivel 1 — PROPONE       → genera draft, CEO aprueba antes de cualquier acción
Nivel 2 — EJECUTA_INTERNO → ejecuta acciones internas (KB, resúmenes) sin aprobación
Nivel 3 — AUTO_NOTIFICA → ejecuta y notifica post-hecho (para skills muy maduros)
Nivel 4 — AUTO_EXCEPCIONES → auto en flujos probados, CEO solo ve excepciones [futuro]
```

**Regla sagrada (no negociable):**
> Correo externo, WhatsApp, Slack a clientes, cualquier transacción financiera →
> **siempre draft-first**. El ladder NUNCA cambia esto.

---

## 6. Termómetro de Aprendizaje — componente UI

Widget fijo bottom-right en la consola del agente:

```
🔵 Frío   → 0-2 outputs pendientes de consolidar
🟡 Tibio  → 3-5 outputs
🔴 Caliente → 6+ outputs (urgente consolidar)
```

Al presionar **"Indexar Aprendizaje"**, se abre un modal con:
- Patrones nuevos detectados (lista con descripción)
- Correcciones recurrentes identificadas
- Gold samples candidatos (con preview)
- Excepciones identificadas

Acciones del modal: `[Confirmar]` `[Editar]` `[Descartar]`
Solo al confirmar → escribe a AgentMemory. Nunca auto-promueve desde thumbs up.

---

## 7. Feedback tipificado (no texto libre)

Cuando el CEO rechaza o edita un output, debe seleccionar categoría:

| Código | Significado |
|--------|-------------|
| `tone` | Tono incorrecto |
| `data` | Dato incorrecto |
| `structure` | Estructura incorrecta |
| `policy` | Violación de policy |
| `scope` | Fuera del scope del skill |

Esto alimenta el análisis de patrones y el aprendizaje estructurado.

---

## 8. Relación con la app `knowledge` de mwt.one

El endpoint `knowledge/ask` (existente) es el punto de entrada natural para la integración. El flujo propuesto cuando se implemente:

```
POST /api/knowledge/ask
{
  "trigger": "proforma",
  "input": "necesito proforma para cliente X"
}
        ↓
Backend identifica AgentSpec por trigger_word
        ↓
Carga AgentSpec + AgentMemory desde KB (o tabla DB)
        ↓
Envía al LLM con contexto completo
        ↓
Retorna draft + metadata de ejecución
        ↓
CEO aprueba/rechaza → POST /api/knowledge/feedback
        ↓
AgentRuntime actualizado, evento registrado
```

---

## 9. Lo que NO hay que implementar ahora

- Las tablas de DB descritas arriba son para un sprint futuro
- Los SKILL_*.md actuales son el source of truth mientras no haya DB
- SKILL_RUNTIME.md se actualiza manualmente por el CEO después de cada ejecución relevante
- El termómetro UI es futuro — hoy es solo el archivo markdown

---

## 10. Estado actual (referencia rápida)

| Item | Estado |
|------|--------|
| Skills definidos | 10 (todos SHADOW) |
| AgentSpec files | ✅ Completos |
| AgentRuntime | ✅ SKILL_RUNTIME.md activo |
| AgentMemory files | ❌ No existen aún (se crean con primer batch real) |
| DB tables | ❌ Pendiente sprint de integración |
| UI termómetro | ❌ Pendiente sprint de integración |
| Trigger word detection | ❌ Pendiente (hoy es manual en sesión Cowork) |

---

Refs KB: `SCH_SKILL.md` · `SKILL_RUNTIME.md` · `ENT_PLAT_SKILLS_CATALOG.md`
Changelog: