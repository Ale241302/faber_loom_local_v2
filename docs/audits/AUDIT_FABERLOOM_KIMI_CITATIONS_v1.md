---
id: AUDIT_FABERLOOM_KIMI_CITATIONS_v1
version: 1.0.0
status: STABLE
visibility: [INTERNAL]
domain: faberloom
type: audit
date: 2026-05-10
---

# Auditoría de citas críticas — SPEC FaberLoom Kimi multiagente

## Contexto

Sesión Cowork del 2026-05-10 detectó 3 citas con confianza baja en
`SPEC_FABERLOOM_DESIGN_FOUNDATION_v1.md` y `SPEC_FABERLOOM_BRAND_FOUNDATION_v1.md`.
Antes de promover el SPEC de DRAFT a STABLE, validar contra fuente primaria.

## Resultado

| # | Cita en SPEC | Estado | Fuente verificada |
|---|---|---|---|
| 1 | "93% consent fatigue Anthropic" | **VERIFICADA** | Anthropic Engineering blog · Claude Code Auto Mode |
| 2 | "0.4% FPR clasificador Anthropic" | **VERIFICADA** | Anthropic Engineering blog · Claude Code Auto Mode + arXiv stress-test |
| 3 | "ACM DIS 2026 paper visible thinking aumenta trust" | **NO ENCONTRADA** | DIS 2026 no tiene paper que coincida; sí hay papers CHI 2026 relacionados |

## Detalle por cita

### 1. "93% consent fatigue" — VERIFICADA

**Cita textual original (SPEC):** "El 93% de usuarios experimenta consent
fatigue con aprobaciones excesivas."

**Fuente primaria:** Anthropic. *Claude Code Auto Mode: a safer way to skip
permissions.* Engineering blog, 2026.
URL: https://www.anthropic.com/engineering/claude-code-auto-mode

**Cita exacta de la fuente:** "Claude Code users approve 93% of permission
prompts. Over time this leads to approval fatigue, where people stop
paying close attention to what they're approving."

**Diferencia con el SPEC:** El 93% NO es "usuarios que sufren consent
fatigue" — es "porcentaje de prompts aprobados". El paper concluye que
ese ratio alto causa la fatiga. La cita del SPEC está parcialmente
correcta pero invierte causa y efecto. **Acción:** corregir wording en
v1.1 del SPEC a:

> "El 93% de los permission prompts en Claude Code son aprobados, lo
> que conduce a consent fatigue medible donde los usuarios dejan de
> prestar atención a lo que están aprobando." [^anthropic-auto-mode]

### 2. "0.4% FPR clasificador" — VERIFICADA

**Cita textual original (SPEC):** "0.4% FPR del clasificador" (referido al
sistema Auto Mode de Claude Code).

**Fuente primaria:** Anthropic. *Claude Code Auto Mode.* (mismo URL).
Confirmada también por:
- arXiv 2604.04978v2 — *Measuring the Permission Gate: A Stress-Test
  Evaluation of Claude Code's Auto Mode.*
  URL: https://arxiv.org/abs/2604.04978

**Cita exacta:** "On 10,000 real internal tool calls, the full pipeline
has a 0.4% false positive rate — meaning very few legitimate actions get
blocked."

**Detalle adicional valioso:** El sistema es de 2 etapas. Stage 1 es un
filtro yes/no rápido. Stage 2 corre chain-of-thought solo en acciones
flageadas. La combinación reduce FPR de 8.5% (stage 1 solo) a 0.4%
(pipeline completo). El stress-test independiente de arXiv encontró FNR
de 81% en escenarios deliberadamente ambiguos vs 17% en tráfico real —
no es contradicción, es workload diferente.

**Acción:** mantener la cita en el SPEC v1.1 con cita arXiv añadida como
respaldo independiente:

> "El clasificador Auto Mode de Anthropic alcanza 0.4% FPR en pipeline
> completo de dos etapas (cae de 8.5% en stage 1 a 0.4% al añadir
> stage 2 con CoT)." [^anthropic-auto-mode] [^arxiv-permission-gate]

### 3. "ACM DIS 2026 paper visible thinking" — NO ENCONTRADA

**Cita textual original (SPEC):** "Un paper de ACM DIS 2026 confirma que
visible thinking aumenta el trust del usuario en sistemas con LLMs."

**Búsqueda realizada:** WebSearch query "ACM DIS 2026 paper visible
thinking LLM trust transparency" mayo 2026.

**Hallazgos:** No se encontró paper específico de DIS 2026 (Designing
Interactive Systems) que coincida. SÍ hay papers cercanos en
**CHI 2026** (Conference on Human Factors in Computing Systems —
distinta conferencia ACM SIGCHI):

| Paper CHI 2026 | URL | Relevancia para la cita |
|---|---|---|
| "Can Transparency Help Clinicians Trust AI? Reframing Trust as an Information Foraging and Sensemaking Loop" | dl.acm.org/doi/10.1145/3772363.3798817 | Cercana — conecta transparency con trust calibration |
| "Be Friendly, Not Friends: How LLM Sycophancy Shapes User Trust" | dl.acm.org/doi/10.1145/3772318.3791079 | Tangencial — trata trust en LLM, no thinking visibility |
| "Do I Trust the AI? Towards Trustworthy AI-Assisted Diagnosis" | dl.acm.org/doi/10.1145/3772318.3790835 | Tangencial — trust en AI clínico |

**Hipótesis del error:** Kimi probablemente confundió **DIS** con **CHI**
(ambas son conferencias ACM SIGCHI), o citó un paper que no existe con
ese título exacto.

**Acción:** corregir cita en el SPEC v1.1 a una de estas dos opciones:

a) **Si el principio "visible thinking aumenta trust" es válido para
   FaberLoom**, reemplazar la cita inventada por la verificable más
   cercana:

   > "Investigación HCI sobre transparency en sistemas con LLMs sugiere
   > que mostrar el razonamiento del agente ayuda al usuario a calibrar
   > confianza apropiada — ni overtrust ni undertrust." [^chi-2026-transparency]

b) **Si el principio depende del paper específico**, marcar como
   **PENDING** y buscar fuente real antes de promover SPEC a STABLE.

## Citas formales (para incorporar al SPEC)

```markdown
[^anthropic-auto-mode]: Anthropic. (2026). Claude Code Auto Mode: a safer
way to skip permissions. Engineering blog. Recuperado de
https://www.anthropic.com/engineering/claude-code-auto-mode

[^arxiv-permission-gate]: Anonymous. (2026). Measuring the Permission
Gate: A Stress-Test Evaluation of Claude Code's Auto Mode. arXiv preprint
arXiv:2604.04978v2. Recuperado de https://arxiv.org/abs/2604.04978

[^chi-2026-transparency]: Autores. (2026). Can Transparency Help Clinicians
Trust AI? Reframing Trust as an Information Foraging and Sensemaking Loop.
En Proceedings of the 2026 CHI Conference on Human Factors in Computing
Systems. ACM. https://doi.org/10.1145/3772363.3798817
```

## Recomendación

**No promover SPEC FaberLoom de DRAFT a STABLE hasta:**

1. Aplicar correcciones de wording de las 3 citas (cita 1 y 2 en v1.1
   con cita formal añadida; cita 3 reemplazada o marcada PENDING).
2. Revisar otras citas similares en `SPEC_FABERLOOM_*` que no hayan sido
   verificadas. Recomendado: muestreo aleatorio de 5 citas adicionales
   antes de declarar SPEC estable.
3. Append a `MANIFIESTO_CAMBIOS_v2` el batch v1.1 con cambios.

**Riesgo si se promueve sin corregir:** Cita 3 (DIS 2026 inventado)
contamina la credibilidad del SPEC entero. Vale la pena el ciclo de
corrección.
