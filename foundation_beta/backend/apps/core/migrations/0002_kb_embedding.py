# Generated manually for Foundation Beta M16
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE EXTENSION IF NOT EXISTS vector;
                CREATE TABLE IF NOT EXISTS kb_embedding (
                    id UUID NOT NULL,
                    tenant_id UUID NOT NULL,
                    chunk_id UUID NOT NULL,
                    embedding vector(1536),
                    PRIMARY KEY (id, tenant_id)
                ) PARTITION BY LIST (tenant_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS kb_embedding;",
        ),
    ]
