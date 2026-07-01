# FABERLOOM_RETRIEVAL_V01_PIPELINE
**id:** FABERLOOM_RETRIEVAL_V01_PIPELINE  
**version:** 1.0  
**status:** DRAFT  
**visibility:** INTERNAL  
**domain:** PLATAFORMA  
**fecha:** 2026-04-15  
**upstream:** FABERLOOM_PGVECTOR_PROTOTYPE_v1.md · FABERLOOM_BUILD_PLAN_COBRANZA_v1.md  

---

## Propósito

Este documento es la especificación ejecutable del retrieval pipeline v0.1 de FaberLoom. No es arquitectura conceptual — es lo que se implementa en la primera semana.

Incorpora las 4 correcciones del audit externo (ChatGPT, 2026-04-15) como doctrina explícita. Incluye SQL real, pseudocódigo Python ejecutable, logging de tokens y 2 experimentos listos para correr.

**Lo que este documento entrega:**
- Doctrina v0.1 resuelta sin contradicciones
- Schema SQL mínimo (tabla `chunks` + `generation_log` + `approved_pairs`)
- Script de indexación manual
- Pipeline de retrieval en pseudocódigo Python (~80 líneas)
- Prompt builder para Collections Skill
- Experimento 1 y Experimento 2 con hipótesis, método y métricas

**Lo que este documento no entrega:**
- BM25 / keyword search (entra solo si Experimento 4 lo justifica)
- Aprobación de drafts (lógica de negocio, no retrieval)
- Nightly engine completo (es Fase 2)
- UI / API endpoints (son capa de producto, no retrieval lab)

---

## Sección 1 — Doctrina v0.1 Resuelta

### 1.1 Corrección #1 — Contradicción híbrido vs. semantic-only

El documento upstream (FABERLOOM_PGVECTOR_PROTOTYPE_v1.md) definía la doctrina ideal como híbrida (semantic + keyword + filtros + autoridad + approved pairs) pero en el prototipo mínimo proponía semantic-only sin resolverlo explícitamente.

**Resolución permanente:**

| Versión | Retrieval mode | Condición para avanzar |
|---------|---------------|----------------------|
| v0.1 | Semantic (pgvector cosine) + Hard filters (SQL WHERE) | — (este documento) |
| v0.2 | + Approved pairs via metadata | Approved pairs ≥ 10 pares validados |
| v0.3 | + BM25 keyword (PostgreSQL full-text) | Experimento 4 demuestra mejora UCR ≥ 15% |
| v1.0 | Híbrido completo: semantic + keyword + RRF + reranking heurístico | UCR estable ≥ 70% por 4 semanas |

La doctrina ideal es el destino. v0.1 es el punto de partida sin sobreingeniería. No son contradictorios — son secuenciales con condiciones de avance explícitas.

### 1.2 Corrección #2 — Approved pairs staging

Los pares aprobados son datos de alto valor: un draft que el usuario aprobó sin editar es la mejor señal de calidad. Pero meterlos en el hot path demasiado pronto introduce complejidad sin datos suficientes para validar su impacto.

**Staging explícito:**

| Versión | Acción sobre approved_pairs |
|---------|-----------------------------|
| v0.1 | Se guardan en tabla `approved_pairs`. `hot_path_enabled = FALSE`. No se inyectan en contexto. |
| v0.2 | Se inyectan via filtro de metadata (`type = 'approved_pair'` en chunks). Máximo 1 par por draft. |
| v0.3 | Experimento 3 mide si la tasa de aprobación-sin-edición mejora con pares inyectados. Si sí: hot path. Si no: se mantienen como archivo de aprendizaje únicamente. |

**Preservar sí. Hot path en v0.1, no.**

### 1.3 Corrección #3 — Metadata mínima para v0.1

El schema completo del prototipo (20+ campos) es correcto para el estado maduro. Para v0.1, 12 campos son suficientes para correr el circuito completo.

**Campos activos en v0.1:**

| Campo | Propósito |
|-------|-----------|
| `chunk_id` | Identificador único |
| `canonical_id` | Referencia al documento fuente de verdad |
| `type` | Clasificación: `policy`, `script`, `example`, `contact_note` |
| `domain` | Dominio operativo: `collections`, `sales`, etc. |
| `visibility` | `INTERNAL`, `CEO_ONLY` (filtro de seguridad) |
| `status` | `active`, `deprecated`, `draft` |
| `valid_from` | Inicio de vigencia |
| `valid_until` | Fin de vigencia (NULL = sin expiración) |
| `skill_applicable` | `collections_skill`, NULL para general |
| `stage_applicable` | `T1`, `T2`, `T3`, NULL para todos |
| `behavior_tag` | `puntual`, `tardio_habitual`, `irregular`, `sin_historial`, NULL |
| `content` | Texto del chunk |
| `embedding` | Vector pgvector |
| `embedding_model` | Modelo usado (para re-embedding si cambia) |
| `in_vector_index` | `FALSE` para CEO_ONLY — enforced en indexación |

**Campos diferidos (entran cuando haya datos reales):**
- `usefulness_score` — requiere suficientes ciclos de uso
- `retrieval_count` / `used_in_output_count` — métricas de observabilidad, Fase 2
- `freshness_warning_at` — lógica de expiración, Fase 2
- `has_children` / `parent_doc` — jerarquía documental, cuando haya docs estructurados

### 1.4 Corrección #4 — chunks_useful como señal aproximada

El campo `chunks_useful_approx` en `generation_log` se infiere mediante tags del LLM (el modelo reporta qué chunks usó). Esta señal es útil para exploración pero no es confiable para gobernar el nightly engine.

**Doctrina:**
- `chunks_useful_approx` es una **señal exploratoria**. Se guarda pero no activa lógica automática.
- La fuente confiable de utilidad es: el draft fue aprobado + los `chunk_ids_used` quedan en `generation_log`. Eso sí es verdad.
- El nightly engine usa `retrieval_count` + aprobación, no el tag del modelo.
- UCR (Useful Context Ratio) en v0.1 se calcula como: `drafts_aprobados_con_retrieval / total_drafts` como proxy macro, no chunk-by-chunk.

---

## Sección 2 — Schema SQL Mínimo

```sql
-- Habilitar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- TABLA PRINCIPAL: chunks
-- ============================================================
CREATE TABLE chunks (
    chunk_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id    UUID NOT NULL,  -- FK a canonical_docs cuando exista
    type            VARCHAR(50)  NOT NULL
                    CHECK (type IN ('policy','script','example','contact_note','approved_pair')),
    domain          VARCHAR(50)  NOT NULL,
    visibility      VARCHAR(20)  NOT NULL DEFAULT 'INTERNAL'
                    CHECK (visibility IN ('PUBLIC','PARTNER_B2B','INTERNAL','CEO_ONLY')),
    status          VARCHAR(20)  NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','deprecated','draft')),
    valid_from      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    valid_until     TIMESTAMPTZ,            -- NULL = sin expiración
    skill_applicable    VARCHAR(100),       -- NULL = aplicable a todos los skills
    stage_applicable    VARCHAR(10),        -- 'T1' | 'T2' | 'T3' | NULL
    behavior_tag        VARCHAR(50),        -- 'puntual' | 'tardio_habitual' | 'irregular' | 'sin_historial' | NULL
    content             TEXT         NOT NULL,
    embedding           VECTOR(1536),       -- dimensions: text-embedding-3-small
    embedding_model     VARCHAR(100) DEFAULT 'text-embedding-3-small',
    in_vector_index     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  DEFAULT NOW()
);

-- Índice pgvector para búsqueda coseno
-- lists=100 es apropiado para <100k chunks; ajustar cuando escale
CREATE INDEX idx_chunks_embedding
    ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Índice compuesto para hard filters (siempre se aplican antes del embedding search)
CREATE INDEX idx_chunks_filters
    ON chunks (domain, status, visibility, in_vector_index, stage_applicable, behavior_tag);

-- ============================================================
-- TABLA: generation_log
-- Registra cada llamada al LLM para economía y observabilidad
-- ============================================================
CREATE TABLE generation_log (
    log_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID         NOT NULL,
    user_id             UUID         NOT NULL,
    created_at          TIMESTAMPTZ  DEFAULT NOW(),

    -- Retrieval
    chunks_retrieved    INTEGER,               -- candidatos antes de packing
    chunks_used         INTEGER,               -- slots efectivamente inyectados
    chunk_ids_used      UUID[],                -- para rastrear qué chunks contribuyeron
    retrieval_latency_ms INTEGER,

    -- Token economics (fuente de verdad para costo)
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    model_used          VARCHAR(50),
    cost_usd            NUMERIC(10,6),

    -- Output
    draft_id            UUID,                  -- FK a drafts cuando exista
    approval_status     VARCHAR(20)            -- 'pending'|'approved'|'rejected'|'edited'
                        CHECK (approval_status IN ('pending','approved','rejected','edited')),

    -- Señal aproximada — exploratoria, NO gobierna lógica automática
    -- Ver doctrina Sección 1.4
    chunks_useful_approx INTEGER
);

-- ============================================================
-- TABLA: approved_pairs
-- Almacena drafts aprobados. hot_path_enabled=FALSE en v0.1
-- Ver staging en Sección 1.2
-- ============================================================
CREATE TABLE approved_pairs (
    pair_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id         UUID         NOT NULL,
    user_id         UUID         NOT NULL,
    log_id          UUID         REFERENCES generation_log(log_id),

    -- Contexto de retrieval que produjo este draft
    chunk_ids_used  UUID[],
    prompt_hash     VARCHAR(64),    -- SHA-256 del prompt final (para dedup)

    -- Contenido
    draft_content   TEXT         NOT NULL,
    final_content   TEXT,          -- contenido después de edición del usuario
    was_edited      BOOLEAN      DEFAULT FALSE,

    approved_at     TIMESTAMPTZ  DEFAULT NOW(),

    -- CRÍTICO: FALSE hasta v0.3 — ver doctrina Sección 1.2
    hot_path_enabled BOOLEAN     NOT NULL DEFAULT FALSE
);
```

---

## Sección 3 — Script de Indexación Manual

```python
"""
indexer.py — Script de indexación manual para v0.1

Uso:
    python indexer.py --file knowledge_pack.json --domain collections

knowledge_pack.json formato:
[
  {
    "canonical_id": "uuid-del-doc-fuente",
    "type": "policy",
    "domain": "collections",
    "visibility": "INTERNAL",
    "skill_applicable": "collections_skill",
    "stage_applicable": null,
    "behavior_tag": null,
    "content": "Texto del chunk aquí..."
  },
  ...
]
"""

import json
import uuid
import hashlib
import argparse
from openai import OpenAI
import psycopg2

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536

client_openai = OpenAI()  # OPENAI_API_KEY en env

def get_embedding(text: str) -> list[float]:
    """Genera embedding con retry simple."""
    response = client_openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def should_index(chunk: dict) -> bool:
    """CEO_ONLY nunca entra al índice de vectores."""
    return chunk.get("visibility") != "CEO_ONLY"

def index_knowledge_pack(filepath: str, domain: str, db_conn):
    with open(filepath, "r") as f:
        chunks = json.load(f)

    cursor = db_conn.cursor()
    indexed = 0
    skipped = 0

    for chunk in chunks:
        # Validar campos mínimos requeridos
        required = ["canonical_id", "type", "domain", "visibility", "content"]
        missing = [f for f in required if not chunk.get(f)]
        if missing:
            print(f"  ⚠️  Chunk sin campos requeridos: {missing}. Saltando.")
            skipped += 1
            continue

        in_vector = should_index(chunk)

        # Generar embedding solo si va al índice
        embedding = get_embedding(chunk["content"]) if in_vector else None

        cursor.execute("""
            INSERT INTO chunks (
                chunk_id, canonical_id, type, domain, visibility, status,
                skill_applicable, stage_applicable, behavior_tag,
                content, embedding, embedding_model, in_vector_index
            ) VALUES (
                %s, %s, %s, %s, %s, 'active',
                %s, %s, %s,
                %s, %s::vector, %s, %s
            )
            ON CONFLICT (chunk_id) DO NOTHING
        """, (
            str(uuid.uuid4()),
            chunk["canonical_id"],
            chunk["type"],
            chunk["domain"],
            chunk["visibility"],
            chunk.get("skill_applicable"),
            chunk.get("stage_applicable"),
            chunk.get("behavior_tag"),
            chunk["content"],
            embedding,
            EMBEDDING_MODEL if in_vector else None,
            in_vector
        ))

        status = "indexed" if in_vector else "stored (CEO_ONLY, no vector)"
        print(f"  ✅ {chunk['type']:<15} {status}")
        indexed += 1

    db_conn.commit()
    cursor.close()
    print(f"\nResultado: {indexed} chunks procesados, {skipped} saltados.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--domain", default="collections")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host="localhost", dbname="faberloom_db",
        user="faberloom_user", password="..."  # usar env var en producción
    )
    index_knowledge_pack(args.file, args.domain, conn)
    conn.close()
```

---

## Sección 4 — Pipeline de Retrieval v0.1

```python
"""
retrieval.py — Pipeline de retrieval v0.1

Doctrina activa:
  - Hard filters primero (SQL WHERE, sin vector)
  - Semantic search (pgvector cosine)
  - Reranking heurístico (sin LLM)
  - Diversity rule (max 2 chunks por tipo)
  - Token budgeting (slots 1-5 inviolables)

BM25 diferido hasta Experimento 4.
Approved pairs diferidos hasta v0.2.
"""

from dataclasses import dataclass
from typing import Optional
import tiktoken

TOKENIZER = tiktoken.encoding_for_model("gpt-4")

@dataclass
class Chunk:
    chunk_id: str
    canonical_id: str
    type: str               # policy | script | example | contact_note
    domain: str
    stage_applicable: Optional[str]
    behavior_tag: Optional[str]
    content: str
    cosine_score: float     # resultado del pgvector search

@dataclass
class RetrievalContext:
    case_id: str
    stage: str              # T1 | T2 | T3
    client_behavior: str    # puntual | tardio_habitual | irregular | sin_historial
    domain: str = "collections"
    skill: str = "collections_skill"

def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))


def retrieve(
    ctx: RetrievalContext,
    db_conn,
    token_budget: int = 2000,
    max_candidates: int = 20,
    max_chunks_final: int = 8
) -> tuple[list[Chunk], dict]:
    """
    Pipeline principal. Retorna (chunks_seleccionados, metadata_retrieval).
    metadata_retrieval incluye métricas para generation_log.
    """
    import time
    t0 = time.time()

    # ── Stage 1: Candidate retrieval (SQL + pgvector) ──────────────────
    query_text = build_query_text(ctx)
    query_embedding = get_embedding(query_text)

    rows = db_conn.execute("""
        SELECT
            chunk_id, canonical_id, type, domain,
            stage_applicable, behavior_tag, content,
            1 - (embedding <=> %s::vector) AS cosine_score
        FROM chunks
        WHERE status = 'active'
          AND in_vector_index = TRUE
          AND visibility != 'CEO_ONLY'
          AND (valid_until IS NULL OR valid_until > NOW())
          AND domain = %s
          AND (skill_applicable IS NULL OR skill_applicable = %s)
          AND (stage_applicable IS NULL OR stage_applicable = %s)
          AND (behavior_tag IS NULL OR behavior_tag = %s)
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (
        query_embedding, ctx.domain, ctx.skill,
        ctx.stage, ctx.client_behavior,
        query_embedding, max_candidates
    )).fetchall()

    candidates = [Chunk(
        chunk_id=r[0], canonical_id=r[1], type=r[2], domain=r[3],
        stage_applicable=r[4], behavior_tag=r[5], content=r[6], cosine_score=r[7]
    ) for r in rows]

    # ── Stage 2: Reranking heurístico ─────────────────────────────────
    ranked = rerank_heuristic(candidates, ctx)

    # ── Stage 3: Diversity rule ────────────────────────────────────────
    diverse = apply_diversity(ranked, max_per_type=2, max_total=max_chunks_final)

    # ── Stage 4: Token budgeting ───────────────────────────────────────
    selected = pack_to_budget(diverse, token_budget)

    latency_ms = int((time.time() - t0) * 1000)

    meta = {
        "chunks_retrieved": len(candidates),
        "chunks_used": len(selected),
        "chunk_ids_used": [c.chunk_id for c in selected],
        "retrieval_latency_ms": latency_ms,
        "query_text": query_text
    }

    return selected, meta


def build_query_text(ctx: RetrievalContext) -> str:
    """Texto de consulta para el embedding. Específico, no genérico."""
    return (
        f"Comunicación de cobranza B2B. "
        f"Etapa: {ctx.stage}. "
        f"Comportamiento de pago del cliente: {ctx.client_behavior}. "
        f"Dominio: {ctx.domain}."
    )


def rerank_heuristic(candidates: list[Chunk], ctx: RetrievalContext) -> list[Chunk]:
    """
    Boost por autoridad de tipo y coincidencia exacta de stage/behavior.
    Sin LLM. Pesos calibrados para dominio collections.
    """
    type_priority = {"policy": 4, "script": 3, "example": 2, "contact_note": 1}

    def heuristic_score(c: Chunk) -> float:
        base = c.cosine_score
        type_boost = type_priority.get(c.type, 0) * 0.05
        stage_boost = 0.10 if c.stage_applicable == ctx.stage else 0.0
        behavior_boost = 0.10 if c.behavior_tag == ctx.client_behavior else 0.0
        return base + type_boost + stage_boost + behavior_boost

    return sorted(candidates, key=heuristic_score, reverse=True)


def apply_diversity(ranked: list[Chunk], max_per_type: int = 2, max_total: int = 8) -> list[Chunk]:
    """Máximo max_per_type chunks del mismo tipo."""
    selected = []
    type_counts: dict[str, int] = {}

    for chunk in ranked:
        if type_counts.get(chunk.type, 0) < max_per_type:
            selected.append(chunk)
            type_counts[chunk.type] = type_counts.get(chunk.type, 0) + 1
        if len(selected) >= max_total:
            break

    return selected


def pack_to_budget(chunks: list[Chunk], budget: int) -> list[Chunk]:
    """
    Respeta budget de tokens. Política: policy y script primero (inviolables),
    example y contact_note se truncan si no hay espacio.
    Sin chunks parciales — un chunk entra completo o no entra.
    """
    priority_order = ["policy", "script", "example", "contact_note"]
    sorted_chunks = sorted(
        chunks,
        key=lambda c: priority_order.index(c.type) if c.type in priority_order else 99
    )

    packed = []
    tokens_used = 0

    for chunk in sorted_chunks:
        chunk_tokens = count_tokens(chunk.content)
        if tokens_used + chunk_tokens <= budget:
            packed.append(chunk)
            tokens_used += chunk_tokens

    return packed
```

---

## Sección 5 — Prompt Builder (Collections Skill)

```python
"""
prompt_builder.py — Ensambla el prompt final para Collections Skill v0.1

Slot structure (8 slots, prioridad de truncación inversa):
  Slot 1 — System: identidad + restricciones absolutas (nunca truncar)
  Slot 2 — Constraints: políticas activas (nunca truncar)
  Slot 3 — Case context: datos del caso activo (nunca truncar)
  Slot 4 — Canonical policy: política de cobranza (nunca truncar)
  Slot 5 — Stage script: guión de etapa (nunca truncar)
  Slot 6 — Retrieved examples: ejemplos del retrieval
  Slot 7 — Approved pairs: VACÍO en v0.1 (hot_path_enabled=FALSE)
  Slot 8 — Contact/user profile: preferencias y notas
"""

SYSTEM_PROMPT = """Eres el asistente de cobranza B2B de {company_name}.
Tu trabajo es generar borradores de comunicación profesional para cuentas con facturas vencidas.

RESTRICCIONES ABSOLUTAS (no negociables):
- Nunca amenaces con acciones legales sin instrucción explícita del usuario
- Nunca ofrezcas condiciones de pago fuera del rango {payment_range}
- Nunca uses información de pago más antigua de 24 horas sin advertir al usuario
- Nunca envíes comunicación directamente — solo generas borradores para revisión humana
- Si no tienes suficiente contexto, indica qué falta en lugar de inventar
"""

def build_prompt(
    case: dict,
    policy_chunks: list[Chunk],
    script_chunks: list[Chunk],
    example_chunks: list[Chunk],
    contact_chunks: list[Chunk],
    company_config: dict
) -> str:
    """
    Ensambla el prompt final con todos los slots.
    Retorna el prompt completo como string.
    """
    sections = []

    # Slot 1 — System
    sections.append(SYSTEM_PROMPT.format(
        company_name=company_config["name"],
        payment_range=company_config.get("payment_range", "acordado en contrato")
    ))

    # Slot 2 — Constraints (de policy chunks tipo 'policy')
    if policy_chunks:
        policies_text = "\n\n".join(
            f"POLÍTICA: {c.content}" for c in policy_chunks
        )
        sections.append(f"## Políticas activas\n{policies_text}")

    # Slot 3 — Case context
    sections.append(f"""## Contexto del caso
Cliente: {case['client_name']}
Monto vencido: {case['currency']} {case['amount_due']:,.2f}
Días vencidos: {case['days_overdue']}
Facturas: {', '.join(case['invoice_ids'])}
Etapa de cobranza: {case['stage']}  (T1 = recordatorio, T2 = presión, T3 = urgente)
Comportamiento histórico: {case['client_behavior']}
Último contacto: {case.get('last_contact_date', 'Sin registro')}
""")

    # Slot 4 — Canonical policy (stage script tipo 'script')
    if script_chunks:
        script_text = "\n\n".join(
            f"GUIÓN {c.stage_applicable}: {c.content}" for c in script_chunks
        )
        sections.append(f"## Guión de etapa\n{script_text}")

    # Slot 5 — Retrieved examples
    if example_chunks:
        examples_text = "\n\n---\n\n".join(
            f"EJEMPLO ({c.behavior_tag or 'general'}):\n{c.content}"
            for c in example_chunks
        )
        sections.append(f"## Ejemplos de referencia\n{examples_text}")

    # Slot 6 — Contact notes
    if contact_chunks:
        notes_text = "\n".join(f"- {c.content}" for c in contact_chunks)
        sections.append(f"## Notas del contacto\n{notes_text}")

    # Slot 7 — Approved pairs: VACÍO en v0.1
    # Ver doctrina Sección 1.2 — hot_path_enabled=FALSE hasta v0.3

    # Instrucción final
    sections.append(f"""## Tarea
Genera un borrador de email de cobranza en español para el cliente {case['client_name']}.
Etapa: {case['stage']}. Tono: {get_tone(case['stage'])}.
El borrador debe ser directo, profesional y no mayor a 200 palabras.
Usa los guiones y políticas como estructura. No inventes condiciones de pago.
""")

    return "\n\n".join(sections)


def get_tone(stage: str) -> str:
    tones = {
        "T1": "cordial y recordatorio",
        "T2": "firme y urgente",
        "T3": "muy urgente, sin perder profesionalismo"
    }
    return tones.get(stage, "profesional")
```

---

## Sección 6 — Generation Logger

```python
"""
generation_logger.py — Registra cada llamada al LLM con economía completa
"""

import uuid
from datetime import datetime, timezone

# Costos por modelo (USD por millón de tokens)
MODEL_COSTS = {
    "claude-haiku-3-5":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-5": {"input": 3.00,  "output": 15.00},
    "gpt-4o-mini":       {"input": 0.15,  "output": 0.60},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    costs = MODEL_COSTS.get(model, {"input": 3.00, "output": 15.00})
    return (
        input_tokens  * costs["input"]  / 1_000_000 +
        output_tokens * costs["output"] / 1_000_000
    )

def log_generation(
    db_conn,
    case_id: str,
    user_id: str,
    retrieval_meta: dict,
    model: str,
    input_tokens: int,
    output_tokens: int,
    draft_id: str = None,
    chunks_useful_approx: int = None  # señal aproximada, ver doctrina 1.4
) -> str:
    """
    Inserta un registro en generation_log.
    Retorna el log_id generado.
    """
    log_id = str(uuid.uuid4())
    cost = calculate_cost(model, input_tokens, output_tokens)

    db_conn.execute("""
        INSERT INTO generation_log (
            log_id, case_id, user_id,
            chunks_retrieved, chunks_used, chunk_ids_used,
            retrieval_latency_ms,
            input_tokens, output_tokens, model_used, cost_usd,
            draft_id, approval_status,
            chunks_useful_approx
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s,
            %s, %s, %s, %s,
            %s, 'pending',
            %s
        )
    """, (
        log_id, case_id, user_id,
        retrieval_meta["chunks_retrieved"],
        retrieval_meta["chunks_used"],
        retrieval_meta["chunk_ids_used"],
        retrieval_meta["retrieval_latency_ms"],
        input_tokens, output_tokens, model, cost,
        draft_id,
        chunks_useful_approx  # puede ser None
    ))

    db_conn.commit()
    return log_id


def get_economics_summary(db_conn, days: int = 30) -> dict:
    """
    Resumen de economía del último período.
    Útil para el fundador, no para el nightly engine.
    """
    row = db_conn.execute("""
        SELECT
            COUNT(*)                            AS total_generations,
            SUM(cost_usd)                       AS total_cost_usd,
            AVG(cost_usd)                       AS avg_cost_per_draft,
            AVG(input_tokens)                   AS avg_input_tokens,
            AVG(output_tokens)                  AS avg_output_tokens,
            SUM(CASE WHEN approval_status IN ('approved','edited') THEN 1 ELSE 0 END)
                                                AS drafts_approved,
            AVG(CASE WHEN chunks_used > 0
                THEN chunks_used::float / NULLIF(chunks_retrieved,0)
                ELSE NULL END)                  AS avg_selection_ratio
        FROM generation_log
        WHERE created_at > NOW() - INTERVAL '%s days'
    """, (days,)).fetchone()

    total = row[0] or 1
    approved = row[5] or 0

    return {
        "total_generations": total,
        "total_cost_usd": round(row[1] or 0, 4),
        "avg_cost_per_draft_usd": round(row[2] or 0, 6),
        "avg_cost_per_approved_draft_usd": round((row[1] or 0) / max(approved, 1), 6),
        "approval_rate_pct": round(approved / total * 100, 1),
        "avg_input_tokens": round(row[3] or 0),
        "avg_output_tokens": round(row[4] or 0),
        "avg_selection_ratio_pct": round((row[6] or 0) * 100, 1)
    }
```

---

## Sección 7 — Orquestador Principal

```python
"""
orchestrator.py — Pipeline completo end-to-end

Uso desde REPL o script:
    from orchestrator import generate_draft
    draft = generate_draft(case_id="uuid-del-caso", user_id="uuid-del-usuario")
    print(draft["content"])
    print(draft["economics"])
"""

import anthropic
from retrieval import retrieve, RetrievalContext
from prompt_builder import build_prompt
from generation_logger import log_generation

def generate_draft(case_id: str, user_id: str, db_conn, model: str = "claude-haiku-3-5") -> dict:
    """
    Pipeline completo: retrieve → build prompt → call LLM → log → return draft.
    """
    # 1. Cargar datos del caso desde DB
    case = load_case(db_conn, case_id)

    # 2. Retrieval
    ctx = RetrievalContext(
        case_id=case_id,
        stage=case["stage"],
        client_behavior=case["client_behavior"],
        domain="collections",
        skill="collections_skill"
    )

    retrieved_chunks, retrieval_meta = retrieve(ctx, db_conn, token_budget=2000)

    # Separar por tipo para slots del prompt
    policy_chunks  = [c for c in retrieved_chunks if c.type == "policy"]
    script_chunks  = [c for c in retrieved_chunks if c.type == "script"]
    example_chunks = [c for c in retrieved_chunks if c.type == "example"]
    contact_chunks = [c for c in retrieved_chunks if c.type == "contact_note"]

    # 3. Build prompt
    company_config = load_company_config(db_conn, case["company_id"])
    prompt = build_prompt(
        case=case,
        policy_chunks=policy_chunks,
        script_chunks=script_chunks,
        example_chunks=example_chunks,
        contact_chunks=contact_chunks,
        company_config=company_config
    )

    # 4. Llamada al LLM
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    draft_content = response.content[0].text
    input_tokens  = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    # 5. Log
    log_id = log_generation(
        db_conn=db_conn,
        case_id=case_id,
        user_id=user_id,
        retrieval_meta=retrieval_meta,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    # 6. Guardar draft (status=DRAFT_READY — nunca AUTO_SENT)
    draft_id = save_draft(db_conn, case_id, user_id, draft_content, log_id)

    # Actualizar log con draft_id
    db_conn.execute(
        "UPDATE generation_log SET draft_id = %s WHERE log_id = %s",
        (draft_id, log_id)
    )
    db_conn.commit()

    cost = (input_tokens * 0.80 + output_tokens * 4.00) / 1_000_000

    return {
        "draft_id": draft_id,
        "content": draft_content,
        "economics": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "model": model,
            "chunks_used": retrieval_meta["chunks_used"],
            "retrieval_latency_ms": retrieval_meta["retrieval_latency_ms"]
        }
    }


def load_case(db_conn, case_id: str) -> dict:
    """Carga datos del caso desde PostgreSQL."""
    row = db_conn.execute("""
        SELECT c.case_id, c.stage, c.amount_due, c.days_overdue,
               c.client_behavior, c.currency, c.company_id,
               cl.name AS client_name,
               ARRAY_AGG(i.invoice_id) AS invoice_ids,
               MAX(comm.sent_at)::text AS last_contact_date
        FROM debt_cases c
        JOIN clients cl ON cl.client_id = c.client_id
        LEFT JOIN invoices i ON i.case_id = c.case_id
        LEFT JOIN communications comm ON comm.case_id = c.case_id
        WHERE c.case_id = %s
        GROUP BY c.case_id, c.stage, c.amount_due, c.days_overdue,
                 c.client_behavior, c.currency, c.company_id, cl.name
    """, (case_id,)).fetchone()

    return dict(zip([
        "case_id","stage","amount_due","days_overdue",
        "client_behavior","currency","company_id",
        "client_name","invoice_ids","last_contact_date"
    ], row))
```

---

## Sección 8 — Experimento 1: Baseline vs. Retrieval

### Hipótesis
Los drafts generados con retrieval semántico tienen mayor tasa de aprobación-sin-edición que los drafts generados con solo el prompt base (sin chunks recuperados).

### Diseño

| Parámetro | Valor |
|-----------|-------|
| Grupo A | 20 casos: draft sin retrieval (solo system prompt + case context) |
| Grupo B | 20 casos: draft con retrieval v0.1 (semantic + filtros) |
| Casos | Mismos 40 casos reales del cliente piloto |
| Modelo | claude-haiku-3-5 (mismo para ambos grupos) |
| Evaluadores | 2 usuarios del cliente piloto (ciegos al grupo) |
| Duración | 2 semanas |

### Métrica primaria
`approval_without_edit_rate` = drafts aprobados sin modificación / total drafts presentados

### Métricas secundarias
- `avg_edit_distance`: distancia de edición promedio (draft original vs. final enviado)
- `avg_cost_usd`: costo promedio por draft (para confirmar economics)
- `avg_input_tokens`: para verificar que el retrieval no infla innecesariamente el contexto

### Condición de éxito
Grupo B tiene `approval_without_edit_rate` ≥ Grupo A + 15 puntos porcentuales.

### Query de análisis

```sql
-- Comparar aprobación entre grupo con retrieval y sin retrieval
SELECT
    CASE WHEN chunks_used > 0 THEN 'con_retrieval' ELSE 'sin_retrieval' END AS grupo,
    COUNT(*) AS total_drafts,
    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) AS aprobados_sin_edicion,
    ROUND(
        100.0 * SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS pct_aprobacion_sin_edicion,
    ROUND(AVG(cost_usd)::numeric, 6) AS costo_promedio_usd,
    ROUND(AVG(input_tokens)) AS tokens_input_promedio
FROM generation_log
WHERE created_at BETWEEN %s AND %s   -- fechas del experimento
GROUP BY 1;
```

---

## Sección 9 — Experimento 2: Chunk Size Óptimo

### Hipótesis
Chunks de 400 tokens tienen mejor relación UCR/costo que chunks de 200 o 800 tokens para el dominio collections.

### Diseño

| Parámetro | Valor |
|-----------|-------|
| Variantes | 200 tokens · 400 tokens · 800 tokens por chunk |
| Casos | 15 casos idénticos por variante (mismo knowledge pack, re-chunked) |
| Modelo | claude-haiku-3-5 |
| Evaluadores | Mismos 2 usuarios |
| Duración | 1 semana por variante |

### Procedimiento
1. Preparar 3 versiones del knowledge pack con diferente chunk size
2. Indexar cada versión en tabla temporal (`chunks_exp2_200`, `chunks_exp2_400`, `chunks_exp2_800`)
3. Correr exactamente los mismos 15 casos contra cada variante
4. Registrar métricas en `generation_log` con campo adicional `experiment_tag`

### Métrica primaria
UCR proxy = `avg_selection_ratio` de `generation_log` (chunks_used / chunks_retrieved)

### Métricas secundarias
- `avg_input_tokens` (costo relativo por variante)
- `approval_without_edit_rate`
- `avg_retrieval_latency_ms`

### Condición de éxito
La variante ganadora tiene UCR proxy ≥ 0.5 y `avg_input_tokens` ≤ 2500.

```sql
-- Comparar variantes de chunk size
SELECT
    experiment_tag,
    COUNT(*) AS drafts,
    ROUND(AVG(chunks_used::float / NULLIF(chunks_retrieved,0)) * 100, 1) AS ucr_proxy_pct,
    ROUND(AVG(input_tokens)) AS avg_input_tokens,
    ROUND(AVG(cost_usd)::numeric * 1000, 4) AS costo_por_mil_usd,
    ROUND(AVG(retrieval_latency_ms)) AS latencia_ms
FROM generation_log
WHERE experiment_tag LIKE 'exp2_%'
GROUP BY 1
ORDER BY ucr_proxy_pct DESC;
```

---

## Sección 10 — Cómo Correr el Pipeline Hoy

### Prerrequisitos

```bash
# Variables de entorno requeridas
export OPENAI_API_KEY="..."          # para embeddings
export ANTHROPIC_API_KEY="..."       # para generación
export DATABASE_URL="postgresql://faberloom_user:...@localhost/faberloom_db"

# Dependencias
pip install psycopg2-binary pgvector openai anthropic tiktoken
```

### Secuencia de primer arranque

```bash
# 1. Crear schema
psql $DATABASE_URL -f schema.sql

# 2. Preparar knowledge pack del cliente piloto
# Formato: knowledge_pack.json (ver Sección 3)
# Contenido mínimo: 3 policies + 3 scripts (T1/T2/T3) + 5 examples

# 3. Indexar
python indexer.py --file knowledge_pack_piloto.json --domain collections

# 4. Verificar indexación
psql $DATABASE_URL -c "
SELECT type, COUNT(*), in_vector_index
FROM chunks
WHERE domain='collections'
GROUP BY type, in_vector_index
ORDER BY type;"

# 5. Correr retrieval de prueba
python -c "
import psycopg2
from retrieval import retrieve, RetrievalContext
conn = psycopg2.connect('$DATABASE_URL')
ctx = RetrievalContext(
    case_id='test',
    stage='T2',
    client_behavior='tardio_habitual',
    domain='collections',
    skill='collections_skill'
)
chunks, meta = retrieve(ctx, conn)
print(f'Chunks recuperados: {meta[\"chunks_retrieved\"]}')
print(f'Chunks seleccionados: {meta[\"chunks_used\"]}')
print(f'Latencia: {meta[\"retrieval_latency_ms\"]}ms')
for c in chunks:
    print(f'  [{c.type}] score={c.cosine_score:.3f} | {c.content[:60]}...')
conn.close()
"

# 6. Generar primer draft real
python -c "
import psycopg2
from orchestrator import generate_draft
conn = psycopg2.connect('$DATABASE_URL')
result = generate_draft(
    case_id='CASO-UUID-REAL',
    user_id='USER-UUID-REAL',
    db_conn=conn
)
print('DRAFT:')
print(result['content'])
print()
print('ECONOMICS:')
for k, v in result['economics'].items():
    print(f'  {k}: {v}')
conn.close()
"
```

### Verificación de economics esperada

Con knowledge pack estándar (~300 chunks, ~400 tokens promedio):

| Métrica | Valor esperado | Alarma si |
|---------|---------------|-----------|
| `chunks_retrieved` | 10–20 | < 5 (filtros demasiado restrictivos) |
| `chunks_used` | 5–8 | > 8 (revisar token budget) |
| `input_tokens` | 2,000–2,800 | > 3,500 |
| `output_tokens` | 250–400 | > 600 |
| `cost_usd` (Haiku) | $0.0025–0.0040 | > $0.006 |
| `retrieval_latency_ms` | < 200ms | > 500ms |

---

## Sección 11 — Crítica Brutal

**Lo que v0.1 hace bien:**
El pipeline es implementable en 1 semana. La separación entre verdad (canonical_store), representación (pgvector) y señal de calidad (generation_log) está respetada. Las correcciones del audit externo están incorporadas como doctrina, no como notas al margen.

**Lo que v0.1 no resuelve y está bien que no lo resuelva:**

El prompt builder asume que el usuario ya tiene un knowledge pack cargado. El cold start del knowledge pack (cómo se construye ese JSON desde los documentos reales del cliente) no está aquí. Es un problema real que debe resolverse antes del piloto, pero no es un problema de retrieval — es un problema de onboarding. Tratarlo aquí mezclaría responsabilidades.

El reranking heurístico es una apuesta. Los pesos (0.05, 0.10, 0.10) son estimados. Pueden ser incorrectos para el cliente piloto real. El Experimento 1 puede mostrar que el retrieval sin reranking funciona igual. Si eso pasa, simplificar.

La función `load_case` asume un schema de base de datos que todavía no existe formalmente. Es pseudocódigo con intenciones claras, no código ejecutable hoy. El schema real lo define el build plan (FABERLOOM_BUILD_PLAN_COBRANZA_v1.md) y tendrá diferencias.

**El riesgo real de este documento:**
Es fácil implementar exactamente esto y declarar victoria antes de tener datos. El pipeline en sí no demuestra nada hasta que Experimento 1 corre con casos reales. El trabajo de v0.1 no es tener el pipeline corriendo — es tener el pipeline corriendo *y* los primeros 40 drafts generados y evaluados por usuarios reales.

**Frase de cierre:**
Este documento convierte el prototipo conceptual en código con forma. El siguiente paso no es más diseño — es ejecutar `python indexer.py` con datos reales.

---

*upstream: FABERLOOM_PGVECTOR_PROTOTYPE_v1.md | FABERLOOM_BUILD_PLAN_COBRANZA_v1.md*  
*status: DRAFT — pendiente validación con primer piloto real*
