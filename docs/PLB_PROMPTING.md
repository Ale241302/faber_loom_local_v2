# PLB_PROMPTING — Prompting por Modelo y Anti-Alucinación
id: PLB_PROMPTING
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
refs: ENT_PLAT_LLM_ROUTING, ENT_PLAT_SEGURIDAD, ENT_PLAT_KNOWLEDGE, ENT_GOB_AGENTES
aplica_a: [SHARED]

---

## A. Propósito

Instrucciones operativas para promptear cada modelo LLM de forma óptima, minimizar alucinaciones, y decidir cuándo activar contraparte. Rankings, pricing, context windows y specs técnicos viven en ENT_PLAT_LLM_ROUTING (ref → determinismo). Este playbook solo contiene INSTRUCCIONES.

---

## B. Fichas de precisión por modelo

> **Para specs de cada modelo** (pricing, context window, max output, arena score): ref → ENT_PLAT_LLM_ROUTING.B y .C

### B1. Claude (Opus 4.6 / Sonnet 4.6)

**Cómo hablarle:**
1. Usar XML tags para estructura (`<instructions>`, `<context>`, `<examples>`, `<o>`)
2. Ser explícito sobre formato de output esperado
3. Para constraints: decir qué SÍ hacer, no solo qué NO hacer
4. Para outputs largos: dar skeleton/outline primero, pedir que expanda

**Anti-alucinación:**
- Incluir datos de referencia en el prompt (no pedirle que invente)
- "Si no tienes esta información, escribe [NO DISPONIBLE]"
- Para claims técnicos: "Cita la fuente de cada afirmación"

**Thinking mode — reglas críticas:**
- Opus 4.6: usar `thinking.type = "adaptive"` (recomendado por Anthropic)
- Sonnet 4.6: usar `thinking.type = "enabled"` + `budget_tokens` (mín 1024)
- ⛔ `"enabled"` con `budget_tokens` está DEPRECATED en Opus 4.6
- ⛔ Thinking NO es compatible con `temperature` ni `top_k`. Si thinking está activo, solo ajustar `top_p` (0.95-1.0) y `effort` (low/medium/high/max)

**Parámetros SIN thinking:**
- Código/análisis: temperature 0.0-0.3
- General: temperature 0.5-0.7
- Creativo: temperature 0.7-1.0

### B2. GPT-5.4 (OpenAI)

**Cómo hablarle:**
1. Funciona bien con Markdown y con XML
2. Usar `reasoning.effort` para controlar profundidad (none/low/medium/high/xhigh)
3. Long-context tiene surcharge diferenciado — ref → ENT_PLAT_LLM_ROUTING.C

**Anti-alucinación:**
- "Distingue entre hechos verificados y suposiciones"
- Para datos: dar contexto + pedir que extraiga, no que genere

**Parámetros:**
- Código: temperature 0.0-0.3, reasoning.effort = medium/high
- Análisis: temperature 0.3-0.5, reasoning.effort = high
- Creativo: temperature 0.7-1.0, reasoning.effort = low/medium

### B3. Gemini (3.1 Pro / 3 Pro / 3 Flash)

**Cómo hablarle:**
1. Prompts directos y concisos (menos verboso que Claude)
2. Para vision: describir qué buscar en la imagen, dar contexto
3. Usar `thinkingLevel`: "low" o "high" (NO `thinkingBudget`, es legado de 2.5)
4. Long-context en Pro tiene surcharge — ref → ENT_PLAT_LLM_ROUTING.C

**Anti-alucinación:**
- Usar grounding con Google Search para datos actuales
- Para documentos: subir el archivo, no describir su contenido
- "Basándote SOLO en el documento adjunto, responde..."

### B4. DeepSeek V3.2

**Cómo hablarle:**
1. API compatible con formato OpenAI
2. `deepseek-chat` para tareas generales, `deepseek-reasoner` para razonamiento profundo
3. Formato de output estricto (JSON schema) — menos tolerante a ambigüedad
4. Diseñar prompts con prefijos repetidos para aprovechar cache — ref → ENT_PLAT_LLM_ROUTING.C

**Regla crítica:** En modo `deepseek-reasoner`, temperature, top_p, presence_penalty y frequency_penalty NO tienen efecto. Son ignorados silenciosamente.

### B5. Kimi K2.5 (Moonshot AI)

**Cómo hablarle (Agent Swarm):**
1. Dar roles de sub-agentes explícitos con outputs definidos
2. No pedir "investigá todo" — descomponer en sub-tareas paralelas
3. Especificar formato de entregable final
4. Instrucciones de coordinación para el orquestador

**Modos:** Instant, Thinking, Agent, Agent Swarm (hasta 100 sub-agentes).

### B6. Grok 4.20 (xAI)

**Cuándo usarlo:** Search (top 2 Arena), tendencias X/Twitter (acceso nativo), creative writing (top 4).

### B7. Modelos de imagen (por tipo de tarea)

| Tarea | Modelo | Por qué |
|-------|--------|---------|
| Producto fondo blanco | GPT Image 1.5 / Flux 2 Pro | Fotorealismo |
| Texto en imagen | Ideogram 3.0 | Mejor tipografía |
| Lifestyle/editorial | Midjourney v7 | Mood artístico |
| Precisión al prompt | Reve v1.5 | Adherencia estricta |
| Edición/inpainting | ChatGPT Image / Gemini 3 Pro Image | Modificar existente |

---

## C. Checklists anti-alucinación

### C1. Texto (antes de enviar)
1. ¿Incluí datos de referencia? (no pedir que invente)
2. ¿Especifiqué formato de output?
3. ¿Agregué "si no sabés, decí que no sabés"?
4. ¿El prompt es específico?
5. ¿Verifiqué compatibilidad de parámetros? (thinking+temp=ERROR, reasoner+temp=ignorado)

### C2. Imagen (antes de enviar)
1. ¿Especifiqué qué SÍ y qué NO debe aparecer?
2. ¿Usé lenguaje técnico de fotografía?
3. ¿Di colores exactos? (hex, no "azul oscuro")
4. ¿Especifiqué estilo? ("product photography, commercial")
5. ¿Elegí herramienta correcta? (ver B7)

---

## D. Decision tree

> **Tabla completa de cascade:** ref → ENT_PLAT_LLM_ROUTING.D

```
TAREA ENTRANTE
├─ ¿Código? → Claude Opus 4.6
├─ ¿Creativa? → Gemini 3.1 Pro
├─ ¿Razonamiento? → Claude Opus 4.6-thinking
├─ ¿Documentos? → Claude Opus 4.6
├─ ¿Búsqueda? → Claude Opus 4.6-search
├─ ¿Imagen? → ver B7
├─ ¿Masiva paralela? → Kimi K2.5 Swarm
├─ ¿Budget limitado? → DeepSeek V3.2 / Gemini Flash
└─ ¿Contraparte? → ver E
```

---

## E. Protocolo de contraparte

### E1. Cuándo activar
1. Consecuencias si está mal → SÍ
2. Datos que podrían ser inventados → VERIFICAR
3. Modelos empatados (<15 pts Arena) → PROBAR AMBOS
4. "Algo suena raro" → SÍ
5. Exploratoria → NO

### E2. Selección
- Primario Claude → contraparte GPT o Gemini
- Primario GPT → contraparte Claude o Gemini
- Primario Gemini → contraparte Claude o GPT
- NUNCA mismo proveedor

### E3. Prompt template
```
Otro modelo generó este output para esta tarea:
TAREA: {tarea}
OUTPUT: {output}
Evalúa: ¿Datos inventados? ¿Omisiones? ¿Errores lógicos?
Score: [1-10]. Correcciones si aplica.
```

---

## F. Mantenimiento

| Frecuencia | Acción | Quién |
|------------|--------|-------|
| Semanal | Verificar top 3 arena.ai | Windmill cron lunes 3am |
| Modelo nuevo top 10 | Registrar OBSERVACIÓN | Windmill automático |
| 21+ días post-lanzamiento | Evaluar si promover a GREEN | CEO decisión |
| Mensual | Verificar pricing | Windmill primer lunes |
| Trimestral | Auditoría completa | ChatGPT o Gemini |

---

Stamp: DRAFT — pendiente aprobación CEO

Changelog:
- v1.0 (2026-03-18): Creación inicial.
- v1.1 (2026-03-18): Fix determinismo — datos de pricing/context/output removidos de fichas B2-B4, reemplazados con refs a ENT_PLAT_LLM_ROUTING. Hallazgo: auditoría estructural ChatGPT+Gemini.
