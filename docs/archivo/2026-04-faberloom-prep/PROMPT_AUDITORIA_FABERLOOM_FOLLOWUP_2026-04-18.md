# FOLLOW-UP AUDITORÍA FABERLOOM — 4 deltas para revalidar

**Contexto:** Ya me entregaste la auditoría completa (6 secciones A-F, con Sprint plan 1-3 y veredicto final). Acepté el 80% de tu análisis en bloque. Este follow-up solo introduce 4 deltas que NO tenías cuando escribiste esa auditoría. Revisá si cambian tu posición en Sección B (priorización), Sección E (sprint plan) o Sección F (score).

**Regla:** si un delta no cambia tu posición, decilo con una línea. Si cambia, decí exactamente qué y por qué.

---

## Delta 1 — Insight de Relevance AI (Copilot/Autopilot toggle)

Relevance AI muestra un **toggle explícito por workflow**: Copilot (humano en loop) ↔ Autopilot (autónomo). No es una propiedad emergente del agente; es una decisión UX que el cliente aprieta cuando quiere.

Mi propuesta revisada: **el toggle es UX, el framework L0-L5 es unlock condition**. Hasta que el agente no llegue a rubric L3 (N gold samples + precision ≥ X), el switch Autopilot está **disabled** con tooltip "requires 50 gold samples + 95% precision". Una vez que califica, el cliente decide cuándo flipear.

**Tu tarea:** ¿esto resuelve tu objeción de "L0-L5 público es branding prematuro" (vos dijiste mantenerlo interno)? ¿O seguís viendo que el toggle expone el framework antes de tiempo?

---

## Delta 2 — Modelo híbrido Chat + Workflows (DAG) en vez de Orchestrator-Worker puro

Tu crítica central fue: orchestrator-worker runtime para todo es overkill en v1, recomendaste single-agent + tools + approval loop. Acepto.

Pero tras ver Relevance AI, propongo **2 modos separados** en vez de uno:

| Modo | Patrón | Cuándo se usa |
|---|---|---|
| **Chat** (consulta ad-hoc vía cliente) | Single agent + tool router (como vos sugerís) | Queries irregulares, no estructuradas |
| **Workflows** (procesos recurrentes) | DAG definido por humano con triggers (cron, webhook, email, CRM event) + AI routing en nodos específicos | Cotización, follow-up, reconciliación — procesos repetibles |

Ninguno de los dos requiere orchestrator-worker runtime complejo en v1. El DAG es **definido por humano**, no decidido runtime. El routing AI solo aparece en nodos específicos donde hay decisión (ej: "¿es esta respuesta una objeción o una confirmación?").

Schema propuesto:
```yaml
workflow:
  id: cotizacion_argos
  trigger: {type: webhook, source: pipedrive}
  mode: copilot
  nodes:
    - id: extraer_specs
      agent: research_agent
      tools: [pipedrive, drive]
    - id: verificar_disponibilidad
      agent: inventory_agent
      depends_on: [extraer_specs]
    - id: generar_cotizacion
      agent: writer_agent
      depends_on: [verificar_disponibilidad]
      hitl: approval_required
```

**Tu tarea:** ¿esto resuelve tu preocupación "orchestrator es sobreingeniería para v1"? ¿O agrega superficie técnica que vuelve al mismo problema por otra ruta?

---

## Delta 3 — Vertical específico definido (antes era genérico)

En el prompt original dije "SMB no-tech en construcción/logística/agricultura/retail físico". Vos criticaste: "no vendas AI employees para SMB, vendé workflow concreto con aprobación humana".

Acepto. El wedge concreto ahora es:

**Cotización B2B calzado seguridad industrial (LatAm, distribuidores de Marluvas/Tecmater).**

Ventaja: yo (Álvaro) ya vendo ahí. Conozco el buyer (director de compras/HSE), el proceso (RFQ → specs ASTM → verificación stock → negociación precio/plazo → cierre), el dolor (cotización tarda 3-5 días, specs incorrectos en 30% de casos, throughput limitado por rep manual).

Design partners candidatos: 3 distribuidores de mi red actual (México, Colombia, Costa Rica), cero pago, intercambio por feedback tipificado.

Métricas concretas para las 12 semanas de sprint 3:
1. Tiempo promedio RFQ → cotización entregada (hoy vs FaberLoom)
2. Tasa de cotizaciones con spec técnico correcto a primer intento (hoy vs FaberLoom)
3. Throughput cotizaciones/semana por rep comercial (hoy vs FaberLoom)

**Tu tarea:** ¿este vertical es suficientemente estrecho como wedge? ¿O detectás algún problema de economía (TAM pequeño, ciclo venta largo, ACV bajo)? Alternativa que descarté: seguimiento pipeline B2B industrial genérico (replicable pero menos diferenciado) y compliance ergonomía (ciclo RRHH muy largo). ¿Estarías de acuerdo con el descarte?

---

## Delta 4 — 2 features nuevos que emergieron

Agregué a la priorización:

| # | Feature | Impacto | Esfuerzo | Clase | Razón |
|---|---|---|---|---|---|
| 27 | **Trigger framework** (cron, webhook, email, CRM event) | 9 | M | MUST v2 | Sin esto, workflows no existen, todo es chat |
| 28 | **Copilot/Autopilot toggle por workflow** | 9 | S | MUST v2 | UX que hace visible el unlock del framework interno |

Los dos son parte del modelo híbrido Delta 2, quedan en v2 (sprint 4-5), no v1.

**Tu tarea:** ¿agregarías alguno más que haya quedado fuera por mi lista original, ahora que el modelo es híbrido?

---

## Output esperado

**Formato corto.** 4 secciones (una por delta) + 1 conclusión. No más de 1,500 palabras.

Cada sección:
1. ¿Cambia tu posición anterior? (Sí/No)
2. Si sí: qué específicamente (score ajustado, ítem re-clasificado, nuevo riesgo visible)
3. Si no: por qué el delta no mueve la aguja

Conclusión:
- **Score de la estrategia ajustada** (tu Sección F original dio 7.8/10 — ¿sube, baja, se mantiene?)
- **Score de la priorización ajustada** (original 6.4/10)
- **Un cambio concreto** que harías en el Sprint plan 1-3 a la luz de los 4 deltas — o confirmación de que mantenés el plan original intacto.

Empezá ya. No preguntes nada; si algo no está claro, asumí lo razonable y marcá la asunción.
