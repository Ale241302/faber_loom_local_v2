"""pgvector helpers for tenant-partitioned embeddings."""
from __future__ import annotations

from uuid import UUID

from django.db import connection


def ensure_tenant_partition(tenant_id: UUID, dimensions: int = 1536) -> None:
    """Create a partition for the given tenant if it does not exist."""
    partition_name = f"kb_embedding_t_{str(tenant_id).replace('-', '_')}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {partition_name}
            PARTITION OF kb_embedding
            FOR VALUES IN (%s);
            """,
            [str(tenant_id)],
        )
        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{partition_name}_hnsw
            ON {partition_name} USING hnsw (embedding vector_cosine_ops);
            """
        )


def tenant_vector_search_sql(tenant_id: UUID, top_k: int = 5) -> tuple[str, list]:
    """Return a SQL query string that always filters by tenant_id first."""
    sql = """
        SELECT id, chunk_id, embedding <=> %s::vector AS distance
        FROM kb_embedding
        WHERE tenant_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """
    # params: embedding vector, tenant_id, embedding vector, limit
    return sql, [tenant_id, top_k]
