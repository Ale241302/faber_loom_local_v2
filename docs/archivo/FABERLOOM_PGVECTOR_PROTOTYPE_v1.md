# FABERLOOM — PROTOTIPO INTERNO: pgvector, Retrieval y Economía de Contexto
## Retrieval Architecture v1.0 · 2026-04-15

---

## 1. TESIS DEL PROTOTIPO INTERNO

### El problema real que resuelve este prototipo

El MVP comercial de cobranza probará si el flujo funciona. Este prototipo prueba si la economía funciona. Son preguntas distintas.

**El MVP comercial responde:** ¿El usuario aprueba el draft? ¿El IMAP APPEND funciona? ¿El sistema produce valor en el circuito básico?

**Este prototipo responde:** ¿Cuántos tokens realmente necesito? ¿Qué fracción del contexto inyectado termina siendo útil? ¿Cuánto cuesta producir un draft aprobado? ¿Puedo bajar ese costo un 40% sin degradar la aprobación?

Sin este prototipo, escalar FaberLoom a 100 organizaciones activas puede ser insostenible por costos de inferencia antes de que el problema sea visible. Con este prototipo, sabes exactamente cuándo el margen se rompe y qué palancas tienes.

### Por qué usar pgvector aquí aunque no se use en el MVP comercial

El MVP comercial no usa pgvector porque con 5 documentos el retrieval semántico no justifica la complejidad. Pero ese mismo MVP no puede decirte nada sobre:
- Cómo degrada la calidad cuando el knowledge pack crece a 50 documentos
- Cuánto cuesta inyectar el documento completo vs. los chunks relevantes
- Qué fracción del contexto el LLM realmente usa
- Cómo se comporta retrieval con knowledge de distintos dominios mezclado

El prototipo interno usa pgvector como instrumento de medición, no como feature de producto. Necesitas entender el comportamiento del sistema bajo condiciones reales de retrieval antes de que el MVP comercial llegue a esas condiciones.

### Distinción operativa

| Dimensión | MVP Comercial Cobranza | Prototipo Interno |
|-----------|----------------------|-------------------|
| Objetivo | Validar flujo y adopción | Modelar economía y retrieval |
| Usuarios | Clientes reales piloto | Tú y tu equipo técnico |
| Knowledge Pack | 5 documentos fijos | 20–50 documentos de múltiples dominios |
| Retrieval | Chunks fijos en orden | pgvector + retrieval híbrido |
| Métricas clave | Aprobación, errores, tiempo | Tokens, costo, useful context ratio, retrieval precision |
| Éxito | 3 usuarios activos, 0 errores | Costo/draft < umbral, quality ≥ baseline |

---

## 2. QUÉ VIVE DÓNDE

### Canonical Store (PostgreSQL — fuente de verdad)

**Qué contiene:**
- El contenido textual completo de cada chunk canónico
- Metadatos: tipo, dominio, visibilidad, vigencia, versión, estado
- La historia de versiones de cada chunk
- El árbol de dependencias entre documentos
- Los conflictos abiertos y su estado de resolución
- El registro de quién aprobó cada chunk y cuándo

**Qué NO contiene:**
- Embeddings (esos van a pgvector)
- Scores de utilidad (esos son metadata derivada)
- Outputs generados (esos van a la tabla de Drafts)

**¿Entra a pgvector?** No directamente. pgvector recibe una representación del contenido del chunk. Si el contenido cambia, se re-embeddea. El canonical store es la autoridad sobre si ese re-embedding ocurrió correctamente.

**Por qué:** Separar la verdad de su representación matemática es la garantía de que un fallo en el índice vectorial no corrompe el conocimiento. Se puede destruir y reconstruir el índice completo de pgvector sin tocar el canonical store.

---

### Vector Store (pgvector — representación recuperable)

**Qué contiene:**
- Embeddings de los chunks activos del canonical store que tienen `in_vector_index = true`
- Metadata de filtrado: chunk_id, visibility, domain, type, skill_applicable, valid_until, status
- NO el contenido completo del chunk (se recupera del canonical store por chunk_id)

**Qué NO contiene:**
- Chunks con visibility = CEO_ONLY: nunca, bajo ninguna circunstancia
- Chunks en estado archived, deprecated o draft
- Perfiles de usuario o de contacto
- Logs de aprobación o audit trail
- Pares aprobados completos (solo referencias si aplica un índice separado)
- Datos financieros sensibles de clientes (margins, condiciones especiales negociadas)

**¿Entra a pgvector?** Es el pgvector. Pero solo los chunks que cumplen los criterios de visibilidad e indexabilidad.

**Por qué:** El índice vectorial debe poder responder la pregunta "¿qué chunks son relevantes para esta consulta?" de forma segura, sin que la similitud semántica bypass los controles de visibilidad.

---

### Memoria Aprobada (ApprovedPairs — índice separado)

**Qué contiene:**
- Pares (contexto de entrada → output aprobado) por usuario
- Metadata: etapa T1/T2/T3, comportamiento del cliente, edit_type, user_id, created_at
- Resumen del contexto usado (no el contexto completo — eso sería redundante)

**Qué NO contiene:**
- Información del cliente específico que no sea relevante para el patrón (el monto exacto no es el patrón; el comportamiento histórico sí lo es)
- Pares rechazados (archivados pero no indexados)

**¿Entra a pgvector?** Índice separado, filtrando por user_id. Los pares de un usuario no son recuperables en el contexto de otro usuario. La memoria aprobada es personal, no organizacional.

**Por qué:** Los pares aprobados son few-shot examples, no conocimiento canónico. Mezclarlos en el mismo índice que la KB produce competencia semántica incorrecta: un par aprobado de cobranza podría recuperarse cuando el sistema busca la política de crédito.

---

### Índice por Caso/Proyecto (namespace separado en pgvector)

**Qué contiene:**
- Resúmenes de comunicaciones anteriores con el cliente
- Notas del caso convertidas en chunks recuperables
- Estado del caso en forma de texto estructurado

**Qué NO contiene:**
- Contenido de facturas completas (datos estructurados, no texto semántico)
- Datos de otros casos del mismo cliente (no hay mezcla entre casos)

**¿Entra a pgvector?** Sí, en un namespace separado por org_id + case_id. La recuperación de contexto de caso nunca mezcla información entre clientes.

**Por qué:** El contexto de caso es dinámico y específico. Si entra al índice general, puede contaminar retrieval de conocimiento canónico (similitud semántica entre "el cliente debe $4,500" y "el límite de crédito estándar es $5,000" puede producir recuperación incorrecta).

---

### Perfiles de Usuario y Contacto (PostgreSQL relacional — no en pgvector)

**Qué contiene:** Parámetros de estilo, notas manuales, historial resumido de ajustes.

**¿Entra a pgvector?** No. Los perfiles son datos parametrizados, no texto semántico. Se inyectan directamente en el prompt como variables estructuradas, no como chunks recuperados por similitud.

**Por qué:** Buscar "el usuario prefiere mensajes cortos" por similitud semántica no aporta nada. El perfil se accede directamente por user_id. La recuperación semántica no agrega valor aquí y añade latencia.

---

### Logs y Audit Trail (PostgreSQL append-only — nunca en pgvector)

**Por qué nunca en pgvector:** Los logs son registros de hechos, no conocimiento recuperable. Su valor es para auditoría y debugging, no para informar razonamiento. Ponerlos en pgvector sería un error de categoría.

---

## 3. MODELO DE INDEXACIÓN

### Unidad de chunk

**Decisión:** El chunk no es un párrafo ni una oración. El chunk es la unidad mínima que tiene sentido por sí sola como criterio de decisión.

Para el dominio de cobranza:
- Una sección de la política de crédito = 1 chunk (ej: "Plazos estándar de pago y condiciones de escalación")
- Un script completo de etapa = 1 chunk (ej: "Script T1 — cliente puntual")
- Un script por variante = 1 chunk (no mezclar T1 puntual con T1 irregular)
- Un caso especial de la guía = 1 chunk

**Tamaño objetivo:** 150–400 tokens por chunk. Por debajo de 150: el chunk pierde contexto necesario para ser útil por sí solo. Por encima de 400: el embedding empieza a promediar conceptos distintos y pierde especificidad.

### Chunking strategy

**Para documentos de política (densos, precisos):**
- Chunking por sección semántica (no por párrafo fijo)
- Cada chunk debe responder a una pregunta específica: "¿Cuál es el plazo estándar?" / "¿Cuándo se escala?"
- Si una sección tiene subtemas, dividir en chunks hijos con referencia al chunk padre

**Para scripts:**
- Un chunk por variante (etapa × comportamiento del cliente). No agrupar.
- Razón: si busco "qué decirle a un cliente tardío en T2", quiero ese chunk específico, no uno que mezcle T1 puntual y T2 irregular.

**Para guías de situaciones especiales:**
- Un chunk por situación. Máximo 300 tokens.
- Si la situación requiere más de 300 tokens para describirse, el script está mal escrito — eso es un problema de conocimiento, no de chunking.

**Para approved pairs (few-shot):**
- No se chunkean. Se almacenan completos (input_summary + output_approved).
- Se recuperan por metadata (etapa, comportamiento, user_id), no por similitud semántica.
- Razón: buscar un par aprobado por similitud semántica puede traer el par incorrecto. El par correcto es el que tiene la misma etapa y el mismo comportamiento del cliente — eso es filtrado por metadata, no por embedding.

### Metadata obligatoria por chunk

```sql
chunk_id           UUID        PK
canonical_id       UUID        FK → canonical_store
version            INTEGER     versión del chunk (bumpa cuando cambia el contenido)
content_hash       VARCHAR     SHA256 del contenido (detectar cambios sin leer el contenido)

-- Clasificación
type               ENUM        canonical | skill | script | special_case | approved_pair_ref
domain             ENUM        collections | hr | compliance | procurement | general
subdomain          VARCHAR     NULL para dominios sin subdivisión

-- Visibilidad
visibility         ENUM        PUBLIC | PARTNER_B2B | INTERNAL | CEO_ONLY
in_vector_index    BOOLEAN     false si CEO_ONLY o archived

-- Aplicabilidad
skill_applicable   TEXT[]      ['collections_skill'] — qué skills pueden usar este chunk
country_market     TEXT[]      ['cr', 'mx', 'co', 'global']
stage_applicable   TEXT[]      ['T1', 'T2', 'T3'] — NULL si aplica a todos
behavior_tag       TEXT[]      ['puntual', 'tardio_habitual', 'irregular'] — NULL si aplica a todos

-- Vigencia
valid_from         DATE        cuándo empieza a ser vigente
valid_until        DATE        NULL = sin expiración conocida
status             ENUM        active | archived | deprecated | draft
freshness_warning_at DATE      cuándo el Nightly Engine debe sugerir revisión

-- Posición en documento
parent_doc_id      UUID        FK → canonical_documents
chunk_sequence     INTEGER     posición en el documento origen
has_children       BOOLEAN     si tiene chunks hijos derivados

-- Calidad (calculado, no manual)
retrieval_count    INTEGER     cuántas veces fue recuperado
used_in_output_count INTEGER   cuántas veces terminó siendo útil en el output
last_retrieved_at  TIMESTAMP
usefulness_score   FLOAT       used_in_output_count / retrieval_count (NULL si retrieval_count = 0)

-- Embedding
embedding          VECTOR(1536)  (o 3072 según el modelo)
embedding_model    VARCHAR     'text-embedding-3-small' | 'text-embedding-3-large'
embedding_version  INTEGER     bumpa cuando se reembeddea
embedded_at        TIMESTAMP
```

**Qué NO entra a metadata:** el contenido del chunk (vive en canonical_store). Los scores de retrieval de una query específica (son efímeros, viven en el log de retrieval). Las aprobaciones o rechazos del chunk (viven en el audit trail).

**CEO-ONLY:** `in_vector_index = false`. Nunca se embeddea. El Policy Engine lo excluye antes de llegar al retrieval.

**Sensibles no CEO-ONLY:** entran al índice con `visibility = INTERNAL` y el retrieval filtra por `user.max_visibility_level >= INTERNAL`. Un usuario con acceso PARTNER_B2B no recupera chunks INTERNAL.

---

## 4. RETRIEVAL PIPELINE COMPLETO

### Etapa 0 — Pre-retrieval: Construcción de la query

**Input:** ContextPackage (etapa, comportamiento, monto, notas del caso, stage, instrucción del usuario si aplica)

**Lógica:**
Construir la query de retrieval como texto estructurado, no como el texto libre de la instrucción del usuario. El objetivo es maximizar la especificidad del embedding, no la naturalidad.

```
query_text = f"""
Cobranza B2B. Etapa {stage}. Cliente {behavior_classification}.
Monto vencido: {amount_range}.
Objetivo: {intent_description}.
Restricción: {any_known_constraints}
"""
```

No usar el nombre del cliente ni el monto exacto — son datos identificadores que no mejoran el embedding de concepto.

**Costo:** ~50 tokens de input para construir la query (mínimo)

**Riesgo:** Si la query es demasiado genérica ("escribir email de cobranza"), el retrieval trae chunks genéricos. Si es demasiado específica, puede no matchear con los chunks correctos.

---

### Etapa 1 — Filtros Duros (pre-embedding, deterministas)

**Input:** Query construida + user context (user_id, role, visibility_level, domain)

**Lógica (SQL WHERE antes de calcular similitud):**
```sql
WHERE in_vector_index = true
  AND status = 'active'
  AND visibility <= user.max_visibility_level   -- nunca bypass esta regla
  AND valid_from <= CURRENT_DATE
  AND (valid_until IS NULL OR valid_until >= CURRENT_DATE)
  AND domain = 'collections'                     -- filtro de dominio del caso
  AND (skill_applicable @> ARRAY['collections_skill'] OR skill_applicable IS NULL)
  AND (country_market @> ARRAY[user.country] OR 'global' = ANY(country_market))
```

**Output:** Set filtrado de chunks candidatos (puede ser 20–200 según el knowledge pack)

**Costo:** Query de PostgreSQL con índices. < 5ms.

**Riesgo:** Si los filtros son demasiado estrictos, el set candidato queda vacío y el retrieval semántico no tiene material. Debe haber un fallback que relaje los filtros secundarios (country, skill_applicable) si el set inicial < 5 chunks.

**Qué mejora:** Garantiza que no hay CEO-ONLY ni datos expirados en ningún retrieval. Esto es el control de seguridad, no el retrieval de calidad.

---

### Etapa 2 — Candidate Retrieval (semántico + keyword)

**Input:** Set filtrado de chunks + embedding de la query

**Lógica — retrieval híbrido:**

**Rama A — Semantic similarity (pgvector):**
```sql
SELECT chunk_id, content_hash,
       1 - (embedding <=> query_embedding) AS cosine_similarity
FROM chunks
WHERE [filtros de etapa 1]
ORDER BY embedding <=> query_embedding
LIMIT 30
```

**Rama B — Keyword / BM25 (PostgreSQL full-text search):**
```sql
SELECT chunk_id,
       ts_rank(to_tsvector('spanish', content_preview), query) AS keyword_score
FROM chunks
WHERE [filtros de etapa 1]
  AND to_tsvector('spanish', content_preview) @@ plainto_tsquery('spanish', keyword_query)
```

`keyword_query` = términos técnicos exactos extraídos del ContextPackage: nombres de campos de la política ("plan de pago", "días de crédito"), identificadores del caso ("T2", "cliente tardío").

**Fusión de scores (Reciprocal Rank Fusion):**
```
final_score = (1 / (rank_semantic + 60)) + (1 / (rank_keyword + 60))
```
RRF es simple, efectivo y no requiere normalización de scores heterogéneos.

**Output:** Top-30 chunks con score fusionado

**Costo:** 1 embedding call para la query (~$0.000002 con text-embedding-3-small) + 2 queries PostgreSQL (~5–10ms)

**Riesgo:** Si el knowledge pack tiene chunks semánticamente similares pero con visibilidades diferentes, la similitud puede traer candidatos que luego los filtros eliminan. Solución: aplicar los filtros de Etapa 1 DENTRO de la query de pgvector, no después.

---

### Etapa 3 — Reranking (heurístico, no LLM)

**Input:** Top-30 chunks con score fusionado

**Lógica — ajustes multiplicativos al score:**

```python
def rerank_score(chunk, base_score, context):
    score = base_score
    
    # Authority of source (canonical > skill > script > special_case)
    authority_multiplier = {
        'canonical': 1.3,
        'skill': 1.1,
        'script': 1.0,
        'special_case': 0.9
    }
    score *= authority_multiplier[chunk.type]
    
    # Stage applicability (si el chunk aplica a la etapa específica)
    if context.stage in chunk.stage_applicable:
        score *= 1.4
    elif chunk.stage_applicable is None:  # aplica a todos
        score *= 1.0
    else:
        score *= 0.3  # penalizar chunks de otras etapas
    
    # Behavior applicability
    if context.behavior in chunk.behavior_tag:
        score *= 1.3
    elif chunk.behavior_tag is None:
        score *= 1.0
    else:
        score *= 0.4
    
    # Recency (preferir chunks actualizados recientemente)
    days_since_update = (today - chunk.valid_from).days
    recency_multiplier = max(0.8, 1.0 - (days_since_update / 365) * 0.2)
    score *= recency_multiplier
    
    # Usefulness history (si el chunk fue útil antes, darle ventaja)
    if chunk.usefulness_score is not None:
        score *= (0.8 + chunk.usefulness_score * 0.4)  # rango 0.8 a 1.2
    
    return score
```

**No uso LLM para reranking en el prototipo.** Un cross-encoder LLM para reranking añade 200–500ms y $0.001–0.005 por query. Para el prototipo, las heurísticas son más transparentes y medibles. El LLM reranker puede considerarse en v2 si las heurísticas resultan insuficientes.

**Output:** Top-30 chunks re-ordenados

**Costo:** Computación local, < 2ms

---

### Etapa 4 — Context Selection (selección final)

**Input:** Top-30 chunks re-ordenados

**Lógica:**
1. Seleccionar el top-1 chunk de tipo `canonical` (la política de crédito que aplica)
2. Seleccionar el top-1 chunk de tipo `script` para la etapa actual
3. Seleccionar hasta 2 chunks adicionales del top-10 (cualquier tipo), priorizando diversidad de subdocumento
4. Si hay approved pairs del mismo usuario para esta etapa + comportamiento: añadir los top-2
5. Verificar que ningún chunk seleccionado tiene `visibility > user.max_visibility_level` (doble check)

**Regla de diversidad:** No seleccionar más de 2 chunks del mismo `parent_doc_id`. Si los top-5 son todos del mismo documento, es señal de que ese documento es muy largo o está mal chunkeado.

**Output:** 4–6 chunks seleccionados

**Costo:** Cálculo local, < 1ms

**Riesgo:** La regla de diversidad puede eliminar el tercer chunk relevante de un documento importante. Mitigación: si el documento tiene 3 chunks en el top-10, revisar si el documento debe tener una sección canónica de resumen que capture los puntos esenciales en 1 solo chunk.

---

### Etapa 5 — Token Budgeting

**Input:** 4–6 chunks seleccionados + contenido completo de cada uno

**Lógica:**

```python
TOKEN_BUDGET_TOTAL = 6000      # para Claude 3.5 Haiku en generación de drafts
TOKEN_BUDGET_SYSTEM = 400      # system prompt fijo + skill definition
TOKEN_BUDGET_CONSTRAINTS = 150 # active instructions + policy constraints
TOKEN_BUDGET_CASE = 150        # context del caso (monto, días, etapa, contacto)
TOKEN_BUDGET_OUTPUT = 400      # reserva para el output (draft)
TOKEN_BUDGET_CONTEXT = TOKEN_BUDGET_TOTAL - TOKEN_BUDGET_SYSTEM \
                       - TOKEN_BUDGET_CONSTRAINTS - TOKEN_BUDGET_CASE \
                       - TOKEN_BUDGET_OUTPUT
                     = 6000 - 400 - 150 - 150 - 400 = 4900 tokens para contexto

# En la práctica, 4–6 chunks de 200–400 tokens = 800–2400 tokens
# Hay margen amplio → no truncar en el prototipo
# Instrumentar el uso real para ajustar el budget en producción
```

**Política de truncación (cuando se excede el budget):**
1. Primero truncar: approved pairs (los últimos caracteres del ejemplo de output)
2. Segundo truncar: chunks de special_case (menos críticos)
3. Nunca truncar: chunk de política canónica, chunk de script de la etapa
4. Nunca truncar: context del caso (monto, etapa, contacto)

**Output:** Lista final de chunks con sus tokens contados, ready para packing

**Costo:** Tokenización local, < 5ms

---

### Etapa 6 — Context Packing Final

**Input:** Lista final de chunks + datos del caso + perfil del usuario

**Output:** El prompt completo para el LLM (ver Sección 7)

**Qué se registra en este punto:**
- Total tokens de input
- Número de chunks inyectados
- IDs de chunks inyectados (para medir usefulness después)
- Timestamp (para calcular latencia de retrieval)

---

## 5. HYBRID RETRIEVAL DOCTRINE

### La postura: retrieval híbrido con jerarquía de activación

**No es semantic-only porque:** La política de crédito puede decir "plazo de 30 días" y la query puede hablar de "días de mora". La similitud semántica puede no capturar esa conexión de forma confiable. El keyword match sí lo hace.

**No es keyword-only porque:** "¿Cómo tratar a un cliente que siempre paga tarde pero ahora lleva 45 días?" no tiene keywords exactos que coincidan con el script correcto. La similitud semántica sí lo puede capturar.

**La jerarquía de decisión:**

```
NIVEL 1 — Filtros duros (siempre primero, no negociable)
  ├── Visibilidad: excluir si visibility > user.max_visibility_level
  ├── Vigencia: excluir si expired o draft
  ├── Bloqueo: excluir si case.blocked = true
  └── Dominio: incluir solo chunks del dominio relevante

NIVEL 2 — Recuperación por tipo de señal
  ├── Si la query contiene términos técnicos exactos (etapa, monto range, tipo de cliente)
  │   → activar keyword search primero, semantic como complemento
  ├── Si la query es conceptual (¿cómo tratar a X cliente en Y situación?)
  │   → activar semantic primero, keyword como complemento
  └── En todos los casos: RRF para fusionar los dos rankings

NIVEL 3 — Ajuste por autoridad y relevancia contextual
  ├── Tipo de documento (canonical > skill > script)
  ├── Aplicabilidad a la etapa específica (T1/T2/T3)
  ├── Aplicabilidad al comportamiento del cliente
  └── Historial de utilidad del chunk (usefulness_score)

NIVEL 4 — Selección final con diversidad
  ├── Top-1 canonical obligatorio
  ├── Top-1 script para la etapa obligatorio
  ├── Complementos con regla de diversidad de documento
  └── Approved pairs (solo si existen para esta combinación user × etapa × behavior)

NIVEL 5 — Aprobados anteriores (never compiten con canonical)
  ├── Se recuperan por metadata pura (user_id, stage, behavior) — no por embedding
  ├── Se añaden DESPUÉS de la selección de chunks de conocimiento
  └── Se truncan primero si hay presión de tokens
```

**Qué nunca debe competir semánticamente con qué:**
- Los approved pairs (ejemplos de outputs) no deben competir con los chunks de conocimiento (fuentes de verdad). Si ambos entran al mismo índice con el mismo namespace, la similitud semántica de un par aprobado puede "ganarle" a la política canónica. Esto es un fallo de arquitectura.
- Los resúmenes de comunicaciones del caso no deben competir con los scripts. El contexto del caso informa el razonamiento; el script lo guía. Son inputs de naturaleza distinta.

---

## 6. TOKEN ECONOMICS

### Framework de medición — qué instrumentar desde el prototipo

Cada generación debe registrar en un log de economics:

```sql
generation_log {
  generation_id         UUID
  draft_id              UUID
  user_id               UUID
  org_id                UUID
  case_stage            T1 | T2 | T3
  client_behavior       VARCHAR
  
  -- Tokens
  tokens_system         INTEGER     system prompt + skill definition
  tokens_constraints    INTEGER     active instructions + policies
  tokens_case_context   INTEGER     monto, días, etapa, contacto
  tokens_chunks         INTEGER     total de chunks inyectados
  tokens_pairs          INTEGER     approved pairs inyectados
  tokens_total_input    INTEGER     suma de todos los anteriores
  tokens_output         INTEGER     draft generado
  
  -- Chunks
  chunks_injected       INTEGER     cuántos chunks entraron al prompt
  chunks_ids            UUID[]      qué chunk_ids específicos
  chunks_useful         UUID[]      poblado por el LLM o inferido post-aprobación
  useful_context_ratio  FLOAT       NULL hasta calcular post-aprobación
  
  -- Modelo
  model_id              VARCHAR     'claude-haiku-3-5' | 'claude-sonnet-4-5'
  input_cost_usd        NUMERIC(10,8)
  output_cost_usd       NUMERIC(10,8)
  total_cost_usd        NUMERIC(10,8)
  
  -- Retrieval
  retrieval_latency_ms  INTEGER
  
  -- Resultado
  confidence_level      HIGH | MEDIUM | LOW
  gaps_reported         TEXT[]
  
  created_at            TIMESTAMP
}
```

### Cálculo de métricas económicas

**Costo por draft (generación directa):**
```
cost_per_draft = tokens_total_input × input_price + tokens_output × output_price
```

Para Claude 3.5 Haiku (modelo recomendado para generación de drafts):
- Input: $0.80/M tokens (con cache hit) / $1.00/M tokens (sin cache)
- Output: $4.00/M tokens

Draft típico estimado:
- system + skill: ~400 tokens
- constraints: ~150 tokens
- case context: ~120 tokens
- chunks (4–6 × 250 avg): ~1,200 tokens
- pairs (2 × 300): ~600 tokens
- **Total input: ~2,470 tokens**
- Output (draft): ~300 tokens

**Costo por draft ≈ $0.00197 + $0.00120 = ~$0.0032**

**Costo por draft aprobado:**
```
cost_per_approved_draft = cost_per_draft / approval_rate
```
Si approval_rate = 60% → $0.0032 / 0.60 = **~$0.0053 por draft aprobado**
Si approval_rate = 80% → $0.0032 / 0.80 = **~$0.0040 por draft aprobado**

**Costo por caso resuelto:**
```
cost_per_resolved_case = avg_drafts_per_case × cost_per_draft
```
Asumiendo 2.5 drafts por caso resuelto (algunos casos requieren segundo intento):
**~$0.008 por caso resuelto** — marginal dentro del modelo de pricing

**Costo por usuario activo por mes:**
Asumiendo 50 casos de cobranza por mes por usuario:
50 × 2.5 × $0.0032 = **~$0.40/usuario/mes en costos de inferencia de Haiku**

**Costo por org activa por mes (equipo de 3 cobradores):**
3 × $0.40 = **~$1.20/org/mes en costos de inferencia**

Sobre un precio de $99–$299/mes, la economía es sólida incluso con margen de 10×.

**Escenario de riesgo (si se usa Sonnet en lugar de Haiku para todos los drafts):**
Claude Sonnet: $3/M input, $15/M output
Costo por draft ≈ $0.0074 + $0.0045 = ~$0.012
Costo por org/mes ≈ 3 × 50 × 2.5 × $0.012 = **~$4.50/org/mes**
Todavía soportable, pero el margen se comprime 3.75×.

**Conclusión de la economía:** El modelo es sano con Haiku. El riesgo está en dos escenarios: (1) usar Sonnet para todo cuando Haiku es suficiente, (2) context windows muy grandes porque el retrieval no funciona bien.

### Métricas de fuga de tokens (donde el token no sirve)

**Token waste ratio:**
```
token_waste_ratio = 1 - (tokens_de_chunks_que_terminaron_en_el_output / tokens_chunks_inyectados)
```
Si inyecto 1,200 tokens de chunks y el LLM solo usa conceptos de 400 tokens worth, estoy desperdiciando 67% del contexto inyectado.

**Cómo medir tokens_que_terminaron_en_el_output:** En el prototipo, aproximado por los chunk_ids marcados como "útiles" en el generation_log (se pueblan por el proceso de logging post-aprobación). En v2: pedir al LLM que cite qué fuentes usó con `<source>chunk_id</source>` tags en el output.

**Dónde se fuga token inútil en cobranza:**
1. Chunks de políticas que aplican a otros dominios recuperados por similitud semántica difusa
2. Approved pairs de un comportamiento de cliente que no es el del caso actual
3. Instrucciones del sistema que son demasiado verbosas y podrían comprimirse
4. Context de caso con más información de la que el skill necesita (ej: historial de todos los pagos de los últimos 2 años cuando el skill solo necesita el comportamiento clasificado y la última fecha)

---

## 7. CONTEXT PACKING STRATEGY

### Estructura de slots del prompt

El prompt tiene slots con prioridad fija. Los slots de mayor prioridad nunca se truncan. Los de menor prioridad se truncan primero.

```
┌─────────────────────────────────────────────────────────────┐
│ SLOT 1 — System + Skill Definition [NUNCA SE TRUNCA]        │
│ ~350–450 tokens                                             │
│ Quién es el sistema, qué es el Collections Skill,           │
│ qué puede sugerir, qué nunca decide                         │
├─────────────────────────────────────────────────────────────┤
│ SLOT 2 — Constraints Activos [NUNCA SE TRUNCA]              │
│ ~100–200 tokens                                             │
│ Políticas de visibilidad del usuario,                       │
│ umbrales de escalación para este usuario,                   │
│ instrucciones activas del admin para este período           │
├─────────────────────────────────────────────────────────────┤
│ SLOT 3 — Case Context [NUNCA SE TRUNCA]                     │
│ ~100–150 tokens                                             │
│ Monto vencido, días de mora, etapa asignada,                │
│ comportamiento histórico clasificado,                        │
│ nombre y email del contacto de pagos,                       │
│ resumen de última comunicación (si existe)                  │
├─────────────────────────────────────────────────────────────┤
│ SLOT 4 — Canonical Policy Chunk [PRIORITARIO, NO TRUNCAR]   │
│ ~200–350 tokens                                             │
│ El chunk de política que define los umbrales y reglas       │
│ para este tipo de caso. SIEMPRE uno. Nunca dos.             │
├─────────────────────────────────────────────────────────────┤
│ SLOT 5 — Stage Script Chunk [PRIORITARIO, NO TRUNCAR]       │
│ ~150–250 tokens                                             │
│ El script exacto para la etapa × comportamiento del caso.   │
│ SIEMPRE uno. Es la guía directa del skill.                  │
├─────────────────────────────────────────────────────────────┤
│ SLOT 6 — Complementary Chunks [TRUNCAR SEGUNDO]             │
│ ~0–600 tokens (0–2 chunks)                                  │
│ Chunks adicionales relevantes: guías de situación especial, │
│ contexto de comunicaciones previas del caso.                │
│ Solo si aportan algo que Slots 4 y 5 no cubren.             │
├─────────────────────────────────────────────────────────────┤
│ SLOT 7 — Approved Pairs / Few-Shot [TRUNCAR PRIMERO]        │
│ ~0–500 tokens (0–2 pares)                                   │
│ Ejemplos de borradores anteriores aprobados del mismo       │
│ usuario para la misma etapa × comportamiento.               │
│ Ninguno si no existen todavía (early stage).                │
├─────────────────────────────────────────────────────────────┤
│ SLOT 8 — User/Contact Profile [TRUNCAR PRIMERO]             │
│ ~50–100 tokens                                              │
│ Parámetros: formalidad, longitud preferida, saludo, cierre, │
│ notas del contacto ("mensajes cortos, incluir #factura")    │
│ No más de 3–4 bullets. No párrafos.                         │
└─────────────────────────────────────────────────────────────┘
```

**Total típico: ~950–2,050 tokens de input para el contexto**
(con reserva amplia dentro del budget de 4,900 definido en Etapa 5)

### Variación por tipo de caso

| Caso | Slots activos | Tokens estimados |
|------|--------------|-----------------|
| T1, cliente puntual, sin historial de cobranza | 1+2+3+4+5+8 | ~950 |
| T2, cliente irregular, 2 comunicaciones previas | 1+2+3+4+5+6+8 | ~1,350 |
| T3, cliente sin historial, acuerdo de pago posible | 1+2+3+4+5+6+7+8 | ~1,800 |
| T1, usuario con 30 pares aprobados (sistema maduro) | 1+2+3+4+5+6+7+8 | ~2,050 |

### Qué nunca debe competir con qué

- **El script del skill (Slot 5) nunca compite con los approved pairs (Slot 7).** El script guía qué decir. Los pares muestran cómo lo dijo este usuario antes. Si hay conflicto entre el script y un par aprobado, el script gana (capa de conocimiento superior al perfil personal).

- **El policy chunk (Slot 4) nunca se omite aunque el sistema tenga muchos pares aprobados.** Los pares aprobados pueden haber sido generados antes de un cambio de política. La política canónica siempre debe estar presente para que el LLM pueda detectar si un par aprobado ya no es correcto.

- **El case context (Slot 3) nunca se mezcla con el canonical policy (Slot 4).** Son categorías de información distintas. Si se mezclan en un mismo slot, el LLM puede confundir el monto vencido de este caso con el umbral de crédito estándar de la política.

---

## 8. NIGHTLY VECTOR MAINTENANCE

### Qué hace el Nightly Engine respecto a pgvector (solo representación, nunca verdad)

**Operación 1 — Detectar chunks que necesitan re-embedding**
```sql
SELECT chunk_id FROM chunks
WHERE status = 'active'
  AND in_vector_index = true
  AND (
    content_hash != last_embedded_hash  -- el contenido cambió
    OR embedding_model != CURRENT_EMBEDDING_MODEL  -- el modelo cambió
    OR embedded_at < valid_from  -- chunk actualizado después del último embedding
  )
```
Re-embeddea estos chunks. Actualiza el vector en pgvector. No toca el canonical_store.

**Operación 2 — Detectar posibles duplicados semánticos**
```sql
SELECT a.chunk_id, b.chunk_id,
       1 - (a.embedding <=> b.embedding) AS similarity
FROM chunks a, chunks b
WHERE a.chunk_id != b.chunk_id
  AND a.status = 'active' AND b.status = 'active'
  AND a.domain = b.domain
  AND 1 - (a.embedding <=> b.embedding) > 0.92
```
**Acción:** Proponer al admin (no resolver). "El chunk X y el chunk Y tienen similitud 0.95. ¿Son el mismo concepto? Considera consolidar."

**Operación 3 — Calcular usefulness_score actualizado**
```sql
UPDATE chunks
SET usefulness_score = (
  SELECT CASE 
    WHEN retrieval_count = 0 THEN NULL
    ELSE used_in_output_count::FLOAT / retrieval_count
  END
  FROM generation_log
  WHERE chunk_id = ANY(chunks_ids)
  GROUP BY chunk_id
)
WHERE chunk_id IN (SELECT DISTINCT unnest(chunks_ids) FROM generation_log WHERE created_at > NOW() - INTERVAL '24h')
```

**Operación 4 — Identificar chunks con usefulness_score bajo**
```python
LOW_USEFULNESS_THRESHOLD = 0.15  # recuperado pero útil < 15% de las veces
MIN_RETRIEVALS = 20  # esperar suficiente muestra

# Chunks candidatos a revisión
candidates = chunks WHERE usefulness_score < LOW_USEFULNESS_THRESHOLD
                      AND retrieval_count > MIN_RETRIEVALS
```
**Acción:** Incluir en el reporte de la mañana como "candidatos a revisar". No archivar automáticamente.

**Operación 5 — Identificar chunks huérfanos (nunca recuperados)**
```python
ORPHAN_THRESHOLD_DAYS = 30  # 30 días sin ser recuperado

orphans = chunks WHERE last_retrieved_at < NOW() - INTERVAL '30 days'
                   AND status = 'active'
                   AND retrieval_count > 0  # fue indexado y recuperado alguna vez
```
También: chunks con `retrieval_count = 0` después de 14 días de estar activos.
**Acción:** Proponer en el reporte. El admin decide si archivar o ajustar la metadata de aplicabilidad.

**Operación 6 — Mover chunks a "archivo del hot path"**
Chunks que llevan > 90 días sin ser recuperados pueden moverse a un índice "frío" (todavía en pgvector pero con un flag `hot_path = false`). El retrieval solo consulta `hot_path = true` por defecto, con fallback al índice frío si el set de candidatos es < 5.

**Operación 7 — Rollback si un re-embedding empeora retrieval**

Antes de aplicar el re-embedding de un chunk actualizado:
1. Guardar el embedding anterior con `embedding_version - 1`
2. Aplicar el nuevo embedding
3. En el retrieval del día siguiente, comparar el recall de chunks re-embeddeados con su baseline histórico

```python
# Señal de alarma: si el recall de chunks re-embeddeados cae > 20%
if new_retrieval_count < old_avg_retrieval_count * 0.80:
    # Rollback: restaurar embedding anterior
    # Generar alerta en el reporte de la mañana
    trigger_rollback(chunk_id)
```

**Lo que el Nightly Engine nunca toca:**
- El contenido de ningún chunk en el canonical_store
- La metadata de visibilidad de ningún chunk
- Los estados de vigencia (valid_from, valid_until) — eso es del admin
- Los logs de aprobación (audit trail inmutable)
- Las definiciones de skills

---

## 9. CALIDAD DE RETRIEVAL

### Métricas a instrumentar desde el prototipo

---

**M1 — Useful Context Ratio (UCR)**

**Qué mide:** Fracción del contexto inyectado que realmente fue usado en el output.

**Cómo se calcula:**
```
UCR = chunks_that_contributed / chunks_injected
```
En el prototipo: aproximado pidiendo al LLM que indique con `<used>chunk_id</used>` cuáles chunks referenció. O inferido por intersección semántica entre el output y el contenido de cada chunk (más impreciso).

**Cómo se instrumenta:** En el generation_log, campo `chunks_useful` (array de chunk_ids). Populado en el momento de logging post-generación.

**Valor bueno:** UCR > 0.70 (al menos 70% del contexto inyectado fue usado)

**Señal de alarma:** UCR < 0.40 — el retrieval está trayendo chunks irrelevantes o el context packing es demasiado amplio.

---

**M2 — Retrieval Precision@K**

**Qué mide:** De los K chunks seleccionados, cuántos terminaron siendo útiles.

**Cómo se calcula:**
```
Precision@K = |useful_chunks ∩ selected_chunks| / K
```

**Cómo se instrumenta:** Comparar `chunks_useful` vs. `chunks_ids` en el generation_log.

**Valor bueno:** Precision@5 > 0.60 (3 de 5 chunks útiles)

**Señal de alarma:** Precision@5 < 0.30 — el retrieval está fallando sistemáticamente.

---

**M3 — Context Gap Rate (CGR)**

**Qué mide:** Frecuencia con que el usuario tuvo que agregar información de contexto que el sistema debería haber tenido.

**Cómo se calcula:** Inferido de las ediciones de tipo `fact_addition` en los Approval records (cuando el usuario agrega información nueva que no estaba en el borrador, como "el cliente mencionó que pagó la semana pasada").

**Cómo se instrumenta:** En el Approval, además de `edit_type`, agregar `edit_subtype`: `style | fact_correction | fact_addition | content_restructure`.

**Valor bueno:** CGR < 10% (en menos del 10% de los drafts el usuario tuvo que agregar datos que el sistema no tenía)

**Señal de alarma:** CGR > 25% — el Context Engine no está recuperando información relevante del caso, o el knowledge pack tiene gaps importantes.

---

**M4 — Freshness Correctness (FC)**

**Qué mide:** % de chunks recuperados donde `valid_until IS NULL OR valid_until >= CURRENT_DATE`.

**Cómo se calcula:** Verificación determinista en cada retrieval.

**Cómo se instrumenta:** El retrieval pipeline ya aplica el filtro. Este es un check de integridad para confirmar que el filtro está funcionando.

**Valor bueno:** FC = 100%. Cualquier valor < 100% es un bug.

**Señal de alarma:** FC < 100% — hay un error en los filtros del retrieval pipeline. Prioridad crítica.

---

**M5 — Policy Compliance in Retrieval (PCR)**

**Qué mide:** 0 chunks CEO_ONLY en cualquier resultado de retrieval para cualquier usuario.

**Cómo se instrumenta:** Log de todos los chunks recuperados (pre-filtro y post-filtro). Si `CEO_ONLY in pre_filter AND NOT in post_filter`: correcto. Si `CEO_ONLY in post_filter`: incidente de seguridad.

**Valor bueno:** PCR = 100% (0 leakage). Cualquier fallo es crítico.

---

**M6 — Orphan Chunk Rate (OCR)**

**Qué mide:** % de chunks activos en el índice que nunca son recuperados en 30 días.

**Cómo se calcula:**
```
OCR = chunks_with_zero_retrievals_in_30d / total_active_chunks
```

**Valor bueno:** OCR < 15% (máximo 1 de cada 7 chunks activos es huérfano)

**Señal de alarma:** OCR > 30% — el knowledge pack tiene documentos que nunca son relevantes para los casos que se procesan. Probablemente el dominio de esos chunks no está bien configurado, o los documentos no son tan útiles como se pensaba.

---

**M7 — Retrieval Latency**

**Qué mide:** Tiempo total del pipeline de retrieval (de Etapa 0 a Etapa 5).

**Valor bueno:** P95 < 200ms. El retrieval no debe ser el cuello de botella de la generación.

**Señal de alarma:** P95 > 500ms. Revisar: embedding call, índice de pgvector (¿falta HNSW index?), queries de PostgreSQL sin índices.

---

## 10. RIESGOS DE USAR pgvector DEMASIADO TEMPRANO

---

**Riesgo 1 — Falsa inteligencia**

El sistema recupera chunks que suenan relevantes pero no lo son. El LLM los usa porque están en el contexto y produce un output que suena fundamentado pero no lo está.

**Cómo se detecta:** UCR > 0.70 pero Approval sin edición < 40%. El sistema parece estar usando el contexto, pero los usuarios editan mucho. El contexto no era el correcto aunque sonara bien.

**Cómo se mitiga:** Instrumentar cuáles chunks específicos llevan a mayor tasa de edición. Un chunk con retrieval_count alto pero usefulness_score bajo es candidato principal.

**Decisión si persiste:** Reemplazar ese chunk con uno más específico o eliminar del índice.

---

**Riesgo 2 — Retrieval elegante pero inútil**

El pipeline de retrieval es sofisticado, produce buenos scores, pero el output del LLM no mejora respecto al baseline sin retrieval.

**Cómo se detecta:** Experimento 1 (ver Sección 13): baseline sin retrieval vs. retrieval híbrido. Si la diferencia en approval_rate es < 5%, el retrieval no está aportando.

**Cómo se mitiga:** Revisar la calidad del knowledge pack antes de culpar al retrieval. Si los documentos son pobres, el mejor retrieval del mundo no ayuda.

---

**Riesgo 3 — Overchunking**

Chunks demasiado pequeños (< 100 tokens) que pierden el contexto necesario para ser útiles por sí solos. El embedding captura el texto pero no el concepto.

**Cómo se detecta:** Usefulness_score sistemáticamente bajo en chunks cortos. Retrieval precision baja aunque el similarity score sea alto.

**Cómo se mitiga:** En el prototipo, empezar con chunks grandes (300–400 tokens) y reducir si se detecta que el LLM no puede usar el chunk completo. Overchunking es más difícil de corregir que underchunking.

---

**Riesgo 4 — Embeddings de mala calidad para terminología específica**

Los modelos de embedding generales no están optimizados para terminología de negocios en español de LATAM. "Plazo de 30 días" y "término de 30 días" pueden tener baja similitud si el modelo no conoce el contexto.

**Cómo se detecta:** Test manual: queries conocidas donde el chunk correcto debería aparecer en top-3. Si no aparece, hay problema de embedding para ese vocabulario.

**Cómo se mitiga:** En el prototipo: usar text-embedding-3-large en lugar de text-embedding-3-small para mayor capacidad de captura semántica. El costo extra es mínimo en el prototipo ($0.13/M vs $0.02/M tokens). Agregar keyword search (BM25) como complemento para términos exactos.

---

**Riesgo 5 — Mezclar tipos de conocimiento incompatibles en el mismo namespace**

Chunks de política canónica y chunks de approved pairs en el mismo índice producen competencia semántica incorrecta: un par aprobado puede ganarle en similitud a la política canónica cuando el LLM debería usar la política.

**Cómo se detecta:** Post-mortem de drafts con errores: ¿el chunk más similar era un par aprobado que desplazó a la política canónica?

**Cómo se mitiga:** Namespaces separados en pgvector para knowledge vs. approved pairs. La selección de approved pairs es por metadata (user_id, stage, behavior), no por similitud semántica.

---

**Riesgo 6 — Fuga de visibilidad por filtros mal aplicados**

Si los filtros de visibilidad se aplican DESPUÉS del ranking de similitud en lugar de ANTES, un chunk CEO-ONLY puede aparecer en el ranking (aunque luego sea filtrado), y en algunos implementaciones bugueadas puede "influenciar" el ranking de otros chunks.

**Cómo se detecta:** Audit de la query SQL: ¿el WHERE de visibilidad está en la query de pgvector o se aplica en Python post-retrieval? Si está en Python post-retrieval, hay una ventana de riesgo.

**Cómo se mitiga:** Siempre aplicar visibilidad como filtro SQL dentro de la query de pgvector. No como post-proceso en el código de aplicación.

---

**Riesgo 7 — Degradación silenciosa del retrieval**

Cuando el embedding model cambia de versión o se actualiza el knowledge pack, el retrieval puede degradarse sin que nadie lo detecte porque no hay tests de retrieval automatizados.

**Cómo se detecta:** El Nightly Engine calcula `avg_retrieval_count_per_chunk` antes y después de un re-embedding masivo. Si cae > 20%, hay degradación.

**Cómo se mitiga:** Golden test set: 20 queries conocidas con sus chunks correctos esperados. Correr contra el índice antes y después de cualquier cambio de modelo. No desplegar si el recall cae.

---

**Riesgo 8 — Ahorrar tokens a costa de perder calidad**

Se reduce el context window para bajar costos, pero los chunks truncados pierden información crítica. La aprobación cae y el costo efectivo (por draft aprobado) sube aunque el costo por generación baje.

**Cómo se detecta:** Medir el trade-off: costo_por_draft vs. costo_por_draft_aprobado. Si al reducir tokens sube el costo por draft aprobado, estás optimizando la métrica equivocada.

**Cómo se mitiga:** La métrica de optimización correcta es siempre `costo_por_draft_aprobado`, nunca `costo_por_generación`. El segundo sin el primero es engañoso.

---

## 11. DISEÑO DEL PROTOTIPO MÍNIMO

### Sí implemento ya

- **pgvector en el mismo PostgreSQL del proyecto.** No una base de datos vectorial separada. Una extensión. La complejidad operacional de mantener dos bases de datos no se justifica en el prototipo.
- **Embedding pipeline para el knowledge pack inicial (5–15 documentos).** Script Python que lee el canonical_store, chunkea según la estrategia definida, llama a text-embedding-3-small y guarda en pgvector.
- **Retrieval con filtros duros + semantic similarity.** Sin BM25 todavía. La semantic alone es suficiente para el prototipo.
- **Token counter en cada generación.** Instrumentado desde el día 1. No se puede optimizar lo que no se mide.
- **Chunk usefulness tracking básico.** Pedir al LLM que incluya `<sources>chunk_id1, chunk_id2</sources>` al final de cada output. Simple, parseable, no requiere infraestructura adicional.
- **Generation log completo.** La tabla de generation_log definida en Sección 6 se implementa completa. Es la fuente de datos para todos los experimentos.

### Dejo fijo/manual

- **La política de visibilidad.** En el prototipo no hay usuarios con distintos niveles de acceso. Todos los chunks son INTERNAL y hay 1 usuario. El filtro de visibilidad se hardcodea como "incluir todos los INTERNAL y PUBLIC". Se generaliza cuando haya múltiples usuarios con distintos roles.
- **El reranking.** En el prototipo, retrieval semántico puro con las 2 reglas de prioridad más importantes: (1) canonical > script > special_case, (2) stage_applicable match. Sin el score multiplicativo completo todavía.
- **La detección de útilidad automática.** En el prototipo, el `chunks_useful` se puebla manualmente revisando los outputs, o con el tag `<sources>` pedido al LLM. La inferencia automática viene cuando haya volumen suficiente.

### Simulo manualmente

- **BM25 keyword search.** En el prototipo, el keyword search se simula añadiendo los términos técnicos exactos (etapa, comportamiento) a la query de embedding. No es BM25 real, pero captura la idea.
- **Nightly re-embedding.** En el prototipo, el re-embedding se corre manualmente cuando hay cambios en el knowledge pack. No hay cron job todavía.
- **Rollback de embeddings.** En el prototipo, el rollback es manual (restaurar el dump anterior de la tabla de pgvector si algo sale mal).

### Difiero

- **BM25 real (PostgreSQL full-text)** — difiero hasta tener evidencia de que semantic solo es insuficiente
- **Cross-encoder reranker LLM** — difiero hasta que el volumen justifique la latencia y el costo
- **Índices separados por caso/proyecto** — difiero hasta tener múltiples casos activos simultáneos
- **HNSW index tuning en pgvector** — difiero hasta tener > 1,000 chunks (innecesario antes)
- **Nightly maintenance automatizado completo** — difiero hasta tener suficientes señales que procesar

### Elimino por completo en esta fase

- **Modelo de embedding fine-tuneado** — innecesario para el prototipo y complejo de mantener
- **Vector cache de queries recientes** — overhead sin beneficio en volumen de prototipo
- **Múltiples modelos de embedding en paralelo** — complejidad sin utilidad todavía
- **Dashboard de analytics de retrieval** — el generation_log en PostgreSQL más queries SQL ad-hoc es suficiente

---

## 12. ARQUITECTURA TÉCNICA MÍNIMA

```
┌─────────────────────────────────────────────────────────────────┐
│                     CANONICAL STORE                             │
│  PostgreSQL — chunks table                                      │
│  Fuente de verdad. Contenido, metadatos, vigencia, versión.     │
│  Nunca se escribe desde el retrieval pipeline.                  │
│  Solo el admin y el Nightly Engine (propuestas) pueden cambiarla│
└─────────────────────┬───────────────────────────────────────────┘
                      │ embedding_pipeline lee de aquí
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EMBEDDING PIPELINE                            │
│  Script Python (corre en Fase 0 del setup, luego en Nightly)   │
│  Lee chunks con in_vector_index=true y status=active            │
│  Llama a OpenAI text-embedding-3-small (o -large)              │
│  Escribe embeddings a pgvector                                  │
│  Actualiza embedded_at y embedding_version en canonical_store   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ escribe embeddings aquí
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     pgvector                                    │
│  Extensión de PostgreSQL (misma instancia que canonical)        │
│  Almacena: chunk_id + embedding + metadata de filtrado          │
│  NO almacena el contenido completo (está en canonical store)    │
│  Índice HNSW cuando haya > 1,000 chunks                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ retrieval_orchestrator consulta aquí
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                RETRIEVAL ORCHESTRATOR                           │
│  Módulo Python en el backend (Django service layer)             │
│  Responsabilidades:                                             │
│  1. Construir la query de retrieval desde el ContextPackage     │
│  2. Llamar al embedding de la query                             │
│  3. Ejecutar filtros duros + semantic search en pgvector        │
│  4. Aplicar reranking heurístico                                │
│  5. Seleccionar los chunks finales                              │
│  6. Loguear retrieval decisions en generation_log              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ chunks seleccionados + contenidos
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROMPT BUILDER                                │
│  Módulo Python                                                  │
│  Responsabilidades:                                             │
│  1. Ensamblar el prompt con los slots definidos en Sección 7    │
│  2. Aplicar token budgeting y truncación si necesario           │
│  3. Incluir el case context estructurado                        │
│  4. Incluir el user profile como variables                      │
│  5. Retornar el prompt completo con token count                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │ prompt completo
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              LLM (Claude 3.5 Haiku para drafts)                 │
│              Claude 3.5 Sonnet para síntesis compleja           │
│  Output: draft + <sources>chunk_ids</sources>                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ output + sources
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                LOGGING / OBSERVABILITY                          │
│  generation_log table (PostgreSQL)                             │
│  Registra: tokens_in, tokens_out, cost, chunks_injected,       │
│  chunks_useful (de <sources>), retrieval_latency, confidence   │
│  Fuente de datos para todos los experimentos y métricas         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ señales acumuladas
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│           NIGHTLY MAINTENANCE JOB                               │
│  Cron Python (02:00 UTC-6)                                     │
│  - Detecta chunks que necesitan re-embedding                    │
│  - Actualiza usefulness_scores                                  │
│  - Identifica duplicados semánticos y chunks huérfanos          │
│  - Genera reporte de economics del día                          │
│  - NO modifica el canonical_store                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │ reporte
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│           ECONOMICS REPORT (email diario al admin)              │
│  - Costo total del día (USD)                                    │
│  - Costo por draft / por draft aprobado                         │
│  - UCR promedio del día                                         │
│  - Chunks con usefulness_score bajo                             │
│  - Anomalías en retrieval                                       │
└─────────────────────────────────────────────────────────────────┘
```

**Stack mínimo:**
- PostgreSQL 15+ con pgvector extension
- Python 3.11+ con: openai, psycopg2, numpy, tiktoken
- Django (si el backend ya es Django) o FastAPI como wrapper del retrieval orchestrator
- Cron job: celery beat o crontab simple
- No hay nueva infraestructura: todo corre en el mismo servidor que el MVP comercial

---

## 13. EXPERIMENTOS PRIORITARIOS

### Exp 1 — Baseline sin retrieval vs. retrieval semántico

**Hipótesis:** El retrieval semántico mejora la tasa de aprobación sin edición y reduce el token waste respecto a inyectar todos los documentos completos.

**Método:**
- Grupo A: Los 5 documentos del knowledge pack inyectados completos (baseline sin retrieval)
- Grupo B: Retrieval semántico, top-5 chunks
- Mismos 20 casos de cobranza procesados con ambos grupos
- Comparar: approval_rate, tokens_total_input, UCR, cost_per_approved_draft

**Métrica principal:** Cost per approved draft

**Resultado que validaría seguir:** Grupo B tiene cost_per_approved_draft ≤ 70% del Grupo A Y approval_rate ≥ Grupo A - 5%

**Resultado que sugeriría cambiar enfoque:** Grupo B tiene approval_rate < Grupo A - 10%. El retrieval está degradando la calidad. Revisar chunking strategy antes de continuar.

---

### Exp 2 — Tamaño de chunk: 150 vs. 300 vs. 500 tokens

**Hipótesis:** Chunks de 300 tokens optimizan el balance entre especificidad del embedding y suficiencia del contenido para el LLM.

**Método:**
- Mismo knowledge pack chunkeado a 3 tamaños distintos (3 índices de pgvector separados)
- Mismos 20 casos procesados contra cada índice
- Comparar: Precision@5, UCR, approval_rate, tokens_injected

**Métrica principal:** Precision@5 (de los 5 chunks seleccionados, cuántos fueron útiles)

**Resultado que validaría:** Chunks de 300 tokens tienen Precision@5 más alta que 150 y comparable o mejor que 500

**Resultado que sugeriría cambiar:** Si Precision@5 es similar para los 3, significa que el tamaño no es el driver principal de calidad. Enfocarse en mejorar el reranking en su lugar.

---

### Exp 3 — Con approved pairs vs. sin approved pairs en el prompt

**Hipótesis:** Los approved pairs (few-shot examples) mejoran la tasa de aprobación sin edición, especialmente para el perfil de voz del usuario.

**Método:**
- Condición A: prompt con Slots 1–6 + 8 (sin approved pairs)
- Condición B: prompt con Slots 1–8 (con 2 approved pairs)
- Condición B solo puede evaluarse con usuarios que ya tienen ≥ 10 pares aprobados
- Comparar: approval_rate sin edición, edit_type distribution

**Métrica principal:** % de ediciones de tipo "style" vs. "content" (si los pares funcionan, las ediciones de style deben bajar porque el LLM ya capturó el estilo del usuario)

**Resultado que validaría:** Condición B tiene ≥ 10% menos ediciones de tipo style que condición A

**Resultado que sugeriría cambiar:** Si la diferencia es < 5%, los approved pairs no están ayudando al ajuste de voz. Revisar si el método de selección de pares (por metadata) es correcto, o si los pares seleccionados son demasiado genéricos.

---

### Exp 4 — Retrieval semántico solo vs. retrieval híbrido (semantic + keyword)

**Hipótesis:** El keyword search mejora el recall para términos técnicos específicos (nombres de etapas, montos en rangos, tipos de comportamiento) que la similitud semántica puede no capturar bien.

**Método:**
- Condición A: semantic only (pgvector)
- Condición B: hybrid (semantic + PostgreSQL full-text, RRF fusion)
- Test con 10 queries conocidas donde el chunk correcto tiene términos técnicos exactos
- Medir: está el chunk correcto en top-3?

**Métrica principal:** Recall@3 para queries con términos técnicos específicos

**Resultado que validaría:** Recall@3 en Condición B ≥ Condición A + 15% para el subset de queries técnicas

**Resultado que sugeriría no implementar:** Si Recall@3 es similar en ambas condiciones. Significa que semantic es suficiente para el vocabulario de este dominio y el overhead de implementar BM25 no se justifica.

---

### Exp 5 — Context budget corto (1,500 tokens) vs. largo (3,000 tokens)

**Hipótesis:** Existe un punto de saturación donde agregar más contexto no mejora el output y solo sube el costo.

**Método:**
- Condición A: budget de contexto = 1,500 tokens (3–4 chunks pequeños)
- Condición B: budget de contexto = 3,000 tokens (6–8 chunks)
- Mismo retrieval, mismos casos
- Comparar: approval_rate, UCR, cost_per_draft, cost_per_approved_draft

**Métrica principal:** Cost per approved draft y UCR

**Resultado que validaría presupuesto corto:** Approval_rate de A ≥ B - 3% Y UCR de A > UCR de B (el contexto pequeño es más preciso)

**Resultado que sugeriría presupuesto largo:** Approval_rate de B > A + 10%. El contexto adicional sí importa para la calidad y vale el costo.

---

## 14. CRITERIO DE ÉXITO DEL PROTOTIPO

### "pgvector aporta valor real a FaberLoom" si se cumplen todas:

**Calidad:**
- Approval rate sin edición con retrieval ≥ approval rate sin retrieval - 5% (no degrada)
- Context Gap Rate < 15% (el sistema tiene lo que necesita)
- Retrieval Precision@5 > 0.55

**Costo:**
- Cost per approved draft con retrieval ≤ 75% del baseline sin retrieval (ahorro de al menos 25%)
- Useful Context Ratio > 65% (el contexto inyectado es mayormente útil)
- Retrieval latency P95 < 200ms (no introduce fricción)

**Confianza:**
- 0 instancias de CEO_ONLY en retrieval output (no negociable)
- Freshness Correctness = 100% (no negociable)
- El administrador puede re-indexar completamente sin afectar el canonical_store (verificado al menos una vez)

**Mantenibilidad:**
- Re-indexar el knowledge pack completo (< 50 documentos) toma < 10 minutos
- El rollback de un embedding defectuoso está implementado y probado
- Los experimentos son reproducibles (mismo knowledge pack, mismas queries, mismos resultados)

**Gobernanza:**
- El canonical_store tiene 0 cambios no aprobados después de cualquier operación del Nightly Engine
- El audit trail registra cada embedding operation con modelo, versión y timestamp

### "Esto todavía no justifica la complejidad" si:

- El Exp 1 muestra que inyectar los documentos completos produce la misma quality que el retrieval, Y el knowledge pack sigue siendo < 10 documentos
- El retrieval latency P95 > 500ms (el sistema es más lento con retrieval que sin él)
- El UCR es sistemáticamente < 40% (el retrieval trae ruido, no señal)
- El tiempo de mantenimiento del índice supera el beneficio en costo

---

## 15. CRÍTICA BRUTAL FINAL

### Dónde pgvector sí crea ventaja real en FaberLoom

**Cuando el knowledge pack supera los 20–30 documentos.** Con 5 documentos y chunks fijos en orden, pgvector es infraestructura innecesaria. Con 30 documentos de 10 dominios distintos, el retrieval determinista por orden fijo es imposible sin pgvector. El punto de inflexión está entre 15 y 25 documentos activos.

**En la medición de la economía.** pgvector por sí solo no baja costos — pero el prototipo con pgvector te fuerza a instrumentar tokens, chunks útiles y costo por draft. Esa instrumentación es el verdadero activo, independientemente de si pgvector resulta ser la mejor solución de retrieval.

**En la separación visible entre conocimiento real y representación matemática.** Tener pgvector como capa separada del canonical_store hace que la distinción sea estructural, no solo conceptual. Es mucho más difícil que alguien confunda los vectores con la verdad cuando están en capas distintas del sistema.

### Dónde sería una distracción cara

**En el MVP comercial de 5 documentos.** No hay argumento técnico para pgvector en ese contexto. La complejidad de embedding pipeline, index management, y retrieval orchestration es puro overhead cuando el knowledge pack cabe en 3,000 tokens.

**Como sustituto de un buen knowledge pack.** Si los documentos están mal escritos, si los chunks son incoherentes, o si el knowledge pack tiene gaps, pgvector con el mejor retrieval del mundo no lo compensa. El retrieval amplifica la calidad del conocimiento — no la crea.

### El error conceptual más peligroso al usarlo

**Tratar la similitud coseno como comprensión semántica.** Un chunk puede tener similitud 0.87 con la query y ser completamente irrelevante para el caso específico. La similitud semántica mide proximidad de representación matemática, no relevancia de criterio de decisión.

La consecuencia práctica: nunca usar pgvector sin los filtros de metadata (etapa, comportamiento, dominio). Un chunk sobre política de crédito de México puede tener alta similitud con una query sobre cobranza en Costa Rica — y ser incorrecta para el caso. La metadata filtra lo que el embedding no puede.

### La decisión concreta antes de implementar

**Correr el Exp 1 con el knowledge pack real antes de construir el pipeline de embeddings.**

El Exp 1 es: tomar 20 casos reales, generar borradores con el conocimiento completo inyectado (baseline) y medir: tokens usados, tasa de aprobación, costo. Esto toma 2 horas, no 2 semanas. Y te dice el número más importante: cuánto costo se puede teóricamente ahorrar con retrieval en este caso de uso específico.

Si el baseline completo cuesta $0.008 por draft y el presupuesto de costo que tienes es $0.010, pgvector no es prioritario. Si el baseline cuesta $0.025 y tienes mucho margen por recuperar, pgvector es urgente.

No construyas el sistema de retrieval sin saber primero cuánto vale el problema que va a resolver.

### Tu versión mínima más inteligente para empezar

1 tabla chunks en PostgreSQL con la columna embedding (pgvector). 1 función de retrieval de 30 líneas de Python. 1 script de indexación que corre manualmente. 1 campo en el generation_log para tokens y chunk_ids. Eso es todo el prototipo en su versión día 1.

Todo lo demás — reranking, BM25, nightly jobs, rollback automático — se añade cuando los datos del generation_log demuestran que se necesita.

El conocimiento gobernado no necesita infraestructura sofisticada para demostrar su valor. Necesita medición honesta desde el primer día.

---

*FABERLOOM — Prototipo Interno: pgvector, Retrieval y Economía · v1.0 · 2026-04-15*
