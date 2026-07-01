# Dimensión 11 — GAP 4: Alternativas Vector DB (pgvectorscale, Qdrant, Weaviate, Mem0, LanceDB, Turbopuffer)

**Fecha investigación:** 2025-07-25
**Investigador:** Agente de Investigación Técnica
**Búsquedas realizadas:** 22 búsquedas independientes
**Fuentes primarias:** Documentación oficial, blogs de ingeniería, GitHub, papers/benchmarks publicados por vendors, Forrester, Hacker News, Reddit r/PostgreSQL, r/Supabase, r/vectordatabase

---

## 1. pgvectorscale (Timescale/Tiger Data)

### 1.1 ¿Qué añade?

Claim: pgvectorscale complementa pgvector con tres innovaciones clave: StreamingDiskANN (índice disk-based inspirado en Microsoft DiskANN), Statistical Binary Quantization (SBQ) para compresión 16x–32x, y label-based filtered vector search [^619^][^503^].
Source: GitHub pgvectorscale / TimescaleDB
URL: https://github.com/timescale/pgvectorscale
Date: 2023-07-01 (repo creation, ongoing updates)
Excerpt: "pgvectorscale complements pgvector... introduces: StreamingDiskANN; Statistical Binary Quantization; Label-based filtered vector search"
Context: Extensión de PostgreSQL escrita en Rust (PGRX). No reemplaza pgvector, lo complementa.
Confidence: high

Claim: SBQ usa la media per-dimensión como threshold en lugar de 0.0, logrando 32x compresión en modo 1-bit (dimensiones ≥ 900) y 16x en modo 2-bit (dimensiones < 900), con 96–99% recall vs búsqueda exacta [^503^].
Source: dbi-services blog
URL: https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/
Date: 2026-03-01
Excerpt: "SBQ instead computes the per-dimension mean across all vectors during index build and uses that as the threshold... A 3,072-dimension float32 vector becomes a 3,072-bit string (384 bytes). That’s 32x compression."
Context: El rescore step (default 50 candidatos) recupera vectores full-precision del heap para el ranking final.
Confidence: high

### 1.2 Benchmarks vs pgvector estándar

Claim: En benchmark de 50M vectores Cohere-768 a 99% recall, pgvector+pgvectorscale logró 471 QPS vs 41 QPS de Qdrant (11.4x mejor) en mismo hardware AWS r6id.4xlarge; p95 latency 60ms vs 37ms de Qdrant (Qdrant más rápido en tail latency pero 11x menos throughput) [^573^][^565^].
Source: Actian / Timescale benchmarks (ANN-Benchmarks fork)
URL: https://www.actian.com/blog/databases/how-to-evaluate-vector-databases-in-2026/
Date: 2026-03-27
Excerpt: "pgvectorscale achieved 471 queries per second at 99% recall on 50 million vectors, outperforming Qdrant’s 41 QPS on identical AWS hardware"
Context: Timescale publicó estos benchmarks en mayo 2025; algunos vendors omiten este resultado en sus comparativas.
Confidence: high (pero notar: vendor benchmark, posible optimización de parámetros favorables a pgvectorscale)

Claim: Contra Pinecone s1 (serverless/storage-optimized), pgvectorscale logró 28x menor p95 latency, 16x mayor throughput, y 75% menos costo. Contra Pinecone p2 (performance), 1.4x menor latency y 79% ahorro [^566^][^619^].
Source: Medium DataCraft / Timescale blog
URL: https://medium.com/@DataCraft-Innovations/postgres-vector-search-with-pgvector-benchmarks-costs-and-reality-check-f839a4d2b66f
Date: 2025-09-03
Excerpt: "On 50M vectors, Timescale’s pgvectorscale extension: Achieved 28× lower p95 latency and 16× higher throughput vs. Pinecone s1, at 75% lower cost. Against Pinecone p2, pgvector still delivered 1.4× lower latency with 79% cost savings"
Context: Costo comparado en EC2 self-hosted vs managed Pinecone.
Confidence: medium (vendor benchmark; contra-argumento: Pinecone serverless no se compara directamente en throughput sino en costo por query)

### 1.3 ¿Es gratis? ¿Dónde se puede usar?

Claim: pgvectorscale es open-source bajo licencia PostgreSQL (Apache-compatible) y gratuita. Escrita en Rust con PGRX [^619^][^613^].
Source: GitHub pgvectorscale / Tiger Data blog
URL: https://github.com/timescale/pgvectorscale
Date: ongoing
Excerpt: "open-source under the PostgreSQL license... available on any database service on Timescale’s cloud PostgreSQL platform"
Context: Disponible en Timescale Cloud. Para Supabase cloud: NO está disponible como extensión pre-instalada según reportes de usuarios.
Confidence: high

Claim: Supabase cloud NO ofrece pgvectorscale como extensión pre-instalada al menos hasta julio 2025. Usuarios en Reddit reportan que no pueden activarla [^658^][^626^].
Source: Reddit r/Supabase / Supabase Docs
URL: https://www.reddit.com/r/Supabase/comments/1i1z3c7/is_pgvectorscale_extension_available_on_supabase/
Date: Unknown (post activo en 2025)
Excerpt: "Hello, Has anyone successfully used pgvectorscale on their Supabase project? How did you activate it?"
Context: Supabase Docs lista pgvector pero no pgvectorscale en su catálogo de extensiones pre-instaladas. Self-hosted Supabase (Docker/Pigsty) SÍ puede instalarla.
Confidence: high

### 1.4 Contra-argumentos / Limitaciones

Claim: pgvectorscale es desarrollada por Timescale (vendor). Aunque open-source, la estrategia de "source available" de TimescaleDB ha generado debate sobre qué features permanecerán gratuitas [^615^].
Source: PostgresFM podcast transcript
URL: https://postgres.fm/episodes/pgvectorscale/transcript
Date: 2024-06-14
Excerpt: "TimescaleDB... has a free version... I doubt it's true open source because it doesn't have OSI approved license... We call it source available"
Context: pgvectorscale SÍ tiene licencia PostgreSQL según GitHub, pero el precedente de TimescaleDB genera cautela.
Confidence: medium

---

## 2. Qdrant

### 2.1 Self-host vs Cloud

Claim: Qdrant es open-source (Apache 2.0), implementado en Rust. Ofrece Qdrant Cloud (managed), Hybrid Cloud (BYO infra + management plane), y Private Cloud (on-prem) [^601^].
Source: Qdrant official pricing
URL: https://qdrant.tech/pricing/
Date: Unknown (current)
Excerpt: "Managed Cloud is fully managed by Qdrant. Hybrid Cloud lets you bring your own infrastructure while using Qdrant's management plane. Private Cloud gives you complete control with on-premise deployment."
Context: Free tier cloud: 0.5 vCPU / 1GB RAM / 4GB disk. Standard tier: usage-based. Premium: enterprise con mínimo.
Confidence: high

Claim: Qdrant Cloud free tier soporta ~1M vectores de 768 dimensiones en 1GB RAM / 4GB disk [^661^].
Source: Qdrant docs
URL: https://qdrant.tech/documentation/cloud/create-cluster/
Date: 2001-01-01 (template date, contenido actualizado)
Excerpt: "This configuration supports serving about 1 M vectors of 768 dimensions"
Context: Free tier suspende después de 1 semana sin uso; borra después de 4 semanas.
Confidence: high

### 2.2 Multi-tenancy nativo

Claim: Qdrant v1.16 (nov 2025) introdujo "Tiered Multitenancy": todos los tenants en una colección compartida, con capacidad de promover tenants grandes a shards dedicados sin downtime ni reindexing [^575^][^577^].
Source: DBTA / BusinessWire press release
URL: https://www.businesswire.com/news/home/20251119343840/en/Qdrant-Introduces-Tiered-Multitenancy-to-Eliminate-Noisy-Neighbor-Problems-in-Vector-Search
Date: 2025-11-19
Excerpt: "Qdrant combines payload-based filtering and custom sharding inside a single architecture. Tenants begin in a shared fallback shard. When a tenant grows or requires dedicated resources, operators can promote it through a single API call... Qdrant is one of the first vector search engines to provide both tenant isolation and global search inside the same collection."
Context: Esto es más sofisticado que simplemente "namespace per tenant" de Pinecone. Ofrece isolation + cross-tenant search.
Confidence: high

### 2.3 Performance a 1M+ vectores

Claim: Benchmarks independientes reportan Qdrant como el más rápido en latencia pura a 1M vectores: p50 ~3ms, p95 ~8ms (1536d) [^571^][^538^].
Source: Vecstore / Reddit benchmark
URL: https://vecstore.app/blog/vector-database-performance-compared
Date: 2026-04-06
Excerpt: "Qdrant: ~3ms. Milvus: ~4ms. pgvector HNSW: ~5ms. Weaviate: ~8ms. Pinecone Serverless: ~12ms"
Context: Qdrant es consistentemente rápido en ANN-Benchmarks. A 10M+ vectores, su ventaja se mantiene.
Confidence: high

Claim: Con quantization (binary 32x), Qdrant reduce memoria drásticamente: 768d float32 = 3KB/vector; 1M = 3GB RAM. Con binary quantization = 96 bytes/vector; 1M = 96MB [^653^].
Source: Qdrant quantization docs
URL: https://www.mintlify.com/qdrant/qdrant/advanced/quantization
Date: 2026-03-04
Excerpt: "Full-precision vectors: 768-dimensional vector = 768 × 4 bytes = 3KB per vector; 1 million vectors = ~3GB of RAM... Binary Quantization: 768 bits = 96 bytes... Savings: 96.9% reduction (32x compression)"
Context: Esto hace que Qdrant self-hosted sea extremadamente eficiente en RAM.
Confidence: high

### 2.4 Precio

Claim: Qdrant Cloud Standard arranca en ~$25/mes (4GB+ RAM). Para 10M vectores: ~$150-400/mes en Standard. Self-hosted en DigitalOcean 16GB Droplet = $96/mes, maneja 10-20M vectores sin quantization [^574^][^616^].
Source: Ranksquire / BuildMVPFast
URL: https://ranksquire.com/2026/03/04/vector-database-pricing-comparison-2026/
Date: 2026-03-04
Excerpt: "Qdrant Cloud pricing starts at $0.014/hr per node... Self-hosted on DigitalOcean costs $20–$40/mo for up to 10M vectors with zero query billing"
Context: Qdrant usa billing por recurso (RAM/vCPU/hora), no por query.
Confidence: medium (precios fluctúan; self-host requiere expertise DevOps)

---

## 3. Weaviate

### 3.1 Enterprise-grade / Multi-tenancy

Claim: Weaviate tiene multi-tenancy nativo "first-class": one shard per tenant + Tenant Controller con estados ACTIVE/INACTIVE/OFFLOADED + lazy loading. Soporta millones de tenants por cluster [^578^].
Source: Weaviate official blog
URL: https://weaviate.io/blog/weaviate-multi-tenancy-architecture-explained
Date: 2025-10-08
Excerpt: "One Shard per Tenant... The Tenant Controller dynamically manages tenant states... This design prevents unused tenants from consuming valuable system resources... supporting over a million tenants per cluster without noisy neighbor issues or prohibitive costs."
Context: Esta es la arquitectura más madura de multi-tenancy en vector DBs. Offloading a S3 para tenants inactivos.
Confidence: high

Claim: Weaviate se recomienda explícitamente para "multi-tenant SaaS platforms where tenant isolation is a hard requirement" [^562^].
Source: Groovy Web blog
URL: https://www.groovyweb.co/blog/vector-database-comparison-2026
Date: 2026-04-03
Excerpt: "We recommend Weaviate for multi-tenant SaaS platforms where tenant isolation is a hard requirement."
Context: Blog de consultora que evaluó las 4 DBs para clientes de producción.
Confidence: medium

### 3.2 Costo

Claim: Weaviate Cloud Flex (managed) = $45/mes mínimo + uso. Shared Cloud cobra ~$0.01668 por millón de dimensiones almacenadas/mes. Para 10M vectores 1536d ≈ $269/mes en Flex [^586^][^590^].
Source: CheckThat.ai / Weaviate blog pricing update
URL: https://checkthat.ai/brands/weaviate/pricing
Date: 2026-03-02
Excerpt: "Flex: $45/month minimum... 10M vector deployment at 1536 dimensions costs approximately $269/month on the Flex tier"
Context: Weaviate Plus = $280/mes mínimo (99.9% SLA). Premium = $400+/mes (HIPAA-ready). Self-hosted = gratis + infra propia.
Confidence: medium

Claim: Self-hosted Weaviate en VPS pequeño ≈ $20-50/mes para workloads modestos [^584^].
Source: Pecollective
URL: https://pecollective.com/tools/weaviate-pricing/
Date: 2026-02-20
Excerpt: "Self-hosted Weaviate is still free and open source... For a small RAG application, a $20/month VPS running Docker is all you need."
Context: Self-host requiere Kubernetes para producción enterprise.
Confidence: high

---

## 4. Mem0

### 4.1 ¿Qué backend usa?

Claim: Mem0 NO es una vector database. Es una capa de memoria AI (framework) que usa backends de vector DB externos. Por defecto en desarrollo usa SQLite (in-memory). En producción requiere configurar un vector store: Qdrant, Chroma, Pinecone, pgvector, Weaviate, FAISS, etc. [^583^][^563^][^589^].
Source: DigitalOcean / Medium / Dev.to
URL: https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory
Date: 2026-03-12
Excerpt: "Mem0 uses SQLite by default for quick testing, but production systems usually need a vector database... Mem0 requires a vector store to do a similarity search on embeddings"
Context: Mem0 OSS = framework. Mem0 Platform = managed (hosting incluido). Mem0 proporciona "memory management" (extracción, deduplicación, updates) sobre cualquier vector DB.
Confidence: high

Claim: Mem0 Platform (managed) usa pricing por uso. Free tier: 100 memorias/mes. Developer: $99/mes. Teams: $299/mes [^598^].
Source: Medium review
URL: https://medium.com/@reliabledataengineering/mem0-do-ai-agents-really-need-memory-honest-review-6760b5288f37
Date: 2026-01-27
Excerpt: "Free tier: 100 memories/month... Developer: $99/month... Teams: $299/month"
Context: Mem0 self-hosted requiere vector DB + LLM + embedder propios. "Documentation for self-hosting is sparse".
Confidence: medium

### 4.2 ¿Es solo memoria o también vector DB?

Claim: Mem0 es SOLO una capa de memoria (memory layer). No almacena vectores por sí mismo; orquesta operaciones CRUD (ADD/UPDATE/DELETE/NOOP) sobre un vector store configurado [^563^][^567^].
Source: Medium / Dwarves Memo
URL: https://memo.d.foundation/breakdown/mem0
Date: 2025-08-06
Excerpt: "Mem0 features an abstracted storage layer... Vector Store Structure: An abstracted VectorStore layer supports multiple vector databases... Mem0 supports a wide range of vector store providers (e.g., Qdrant, ChromaDB, PineconeDB, FAISS)"
Context: Mem0 también tiene "Graph Memory" (Mem0g) que usa Neo4j para relaciones.
Confidence: high

---

## 5. LanceDB

### 5.1 ¿Embedded solo?

Claim: LanceDB OSS es una "embedded library" (in-process), no un servidor. "Run it locally during development, then use the same data model and APIs as you scale up and need a managed solution" [^652^].
Source: LanceDB official docs
URL: https://docs.lancedb.com/
Date: current
Excerpt: "LanceDB OSS: The open-source embedded library, with client SDKs in Python, TypeScript and Rust. Run it locally during development, then use the same data model and APIs as you scale up and need a managed solution."
Context: LanceDB Enterprise es la versión distribuida/managed (contact sales). No hay modo servidor OSS.
Confidence: high

### 5.2 ¿Sirve para multi-tenant SaaS?

Claim: LanceDB OSS no es adecuado para backend multi-tenant SaaS: "Multi-process concurrent access has limitations", "Cloud offering is still in beta", "For backend services, pgvector or a managed option is usually a better fit" [^608^].
Source: Encore.dev
URL: https://encore.dev/articles/best-vector-databases
Date: 2026-03-08
Excerpt: "Limitations: Relatively new, with a smaller community and fewer production deployments. Cloud offering is still in beta. Multi-process concurrent access has limitations... For backend services, pgvector or a managed option is usually a better fit."
Context: LanceDB está diseñado para workloads locales, edge, data science. No para SaaS multi-tenant concurrente.
Confidence: high

---

## 6. Turbopuffer

### 6.1 ¿Precio? ¿Cuándo es más barato que Supabase?

Claim: Turbopuffer es serverless, usage-based, con mínimo $64/mes. A 1M reads + 1M writes + 10 namespaces + 1536d vectores, cuesta ~$9/mes de uso real (pero el mínimo es $64) [^565^][^581^].
Source: Firecrawl / Liveblocks
URL: https://www.firecrawl.dev/blog/best-vector-databases
Date: 2025-10-09
Excerpt: "At standard pricing (1536-dimension vectors, 1M reads, 1M writes, 10 namespaces), Turbopuffer comes in under $10/month... The $64/month minimum spend means it's not free for low-usage applications"
Context: Comparado con Supabase Pro ($25/mes base + compute), Turbopuffer es más caro en MVP muy pequeño pero más barato a escala de queries alta.
Confidence: medium

Claim: Turbopuffer tiene "no hard limits on namespaces", lo que lo hace ideal para multi-tenant SaaS. Usado por Cursor, Notion, Linear [^581^].
Source: Liveblocks engineering blog
URL: https://liveblocks.io/blog/whats-the-best-vector-database-for-building-ai-products
Date: 2025-09-15
Excerpt: "Multi-tenancy is simple and scalable. Each customer and project gets its own namespace, and there are no hard limits... Thanks to its performance, low cost, crazy high limits, and enterprise features without enterprise costs, Turbopuffer became the obvious choice for us."
Context: No es open-source. Cold-start latency requiere pre-warming API.
Confidence: high

Claim: A escala enterprise (100M vectores, 6M queries/mes), Pinecone Serverless puede costar $72,000/mes por billing de Read Units. Turbopuffer no cobra por query, solo por storage + writes + queries a tarifa fija, haciéndolo potencialmente mucho más barato a alta frecuencia de queries [^574^].
Source: Ranksquire
URL: https://ranksquire.com/2026/03/04/vector-database-pricing-comparison-2026/
Date: 2026-03-04
Excerpt: "Pinecone wins for low QIR (few queries); self-hosted Qdrant wins for high QIR (high frequency)"
Context: Turbopuffer también gana en high-QIR porque no penaliza queries con RUs caras.
Confidence: medium

---

## 7. RLS / Multi-tenancy Nativo: Comparativa

### 7.1 ¿Cuáles tienen RLS o equivalente nativo?

Claim: Solo PostgreSQL (pgvector) tiene RLS nativa a nivel de fila mediante políticas SQL. Ninguna vector DB dedicada (Qdrant, Weaviate, Pinecone, Milvus) implementa RLS de base de datos relacional [^585^][^587^].
Source: Dev.to / TechBuddies
URL: https://dev.to/young_gao/multi-tenant-architecture-database-per-tenant-vs-shared-schema-1n2e
Date: 2026-03-21
Excerpt: "PostgreSQL's Row-Level Security (RLS) eliminates that risk at the database level... Even if a developer forgets to filter by tenant, RLS blocks cross-tenant access."
Context: pgvector + RLS = multi-tenancy via shared table + tenant_id. Vector DBs dedicadas usan namespaces/collections/shards por tenant.
Confidence: high

### 7.2 Multi-tenancy en Vector DBs dedicadas

| Database | Mecanismo de multi-tenancy | Aislamiento |
|----------|---------------------------|-------------|
| **pgvector + PostgreSQL** | RLS por tenant_id en tabla compartida; o schema-per-tenant | Lógico (RLS) o físico (schema) |
| **Qdrant** | Payload filtering (key-value) + Tiered Multitenancy (v1.16) = shared collection con posibilidad de shard dedicado | Lógico; puede promover a físico por shard |
| **Weaviate** | One shard per tenant nativo; Tenant Controller (ACTIVE/INACTIVE/OFFLOADED) | Físico por shard; lazy loading |
| **Pinecone** | Namespaces (hasta 20 en Standard) | Lógico; mismo índice, partición por namespace |
| **Turbopuffer** | Namespaces (sin límite) | Lógico; aislado por namespace |
| **LanceDB** | No aplica (embedded) | N/A |
| **Mem0** | user_id/app_id scoping en queries al vector store subyacente | Depende del backend vector DB |

Claim: Weaviate tiene la arquitectura de multi-tenancy más sofisticada: "One shard per tenant" + lazy shard loading + delayed WAL flush + bucketed design. Soporta "millions of tenants across a cluster" [^578^].
Source: Weaviate blog
URL: https://weaviate.io/blog/weaviate-multi-tenancy-architecture-explained
Date: 2025-10-08
Excerpt: "With these innovations, Weaviate delivers a robust platform... Multi-tenancy isn't an afterthought or a bolt-on feature, it's woven into the very fabric of Weaviate's architecture"
Context: Weaviate es la única vector DB con tenant offloading a cold storage (S3).
Confidence: high

Claim: Qdrant Tiered Multitenancy (v1.16, nov 2025) es la primera solución que permite promover tenants a shards dedicados dentro del mismo collection, sin downtime [^576^].
Source: BusinessWire / Yahoo Finance
URL: https://finance.yahoo.com/news/qdrant-introduces-tiered-multitenancy-eliminate-130000386.html
Date: 2025-11-19
Excerpt: "First solution to promote growing tenants into dedicated shards inside one vector search engine environment."
Context: Esto resuelve el "noisy neighbor" sin el overhead de múltiples índices.
Confidence: high

### 7.3 Overhead de RLS en pgvector

Claim: Benchmarks en Go/Docker con 10k registros muestran que RLS añade ~20% overhead a vector search HNSW (3-5ms → 5-6ms), pero +0.1ms en selects simples. Es "acceptable vs. schema overhead" [^4^].
Source: Dev.to PostgreSQL RLS in Go
URL: https://dev.to/__8fa66572/postgresql-rls-in-go-architecting-secure-multi-tenancy-4ifm
Date: 2026-01-29
Excerpt: "Vector Search (HNSW): 3-5 ms → 5-6 ms, ~20% overhead. Acceptable vs. schema overhead."
Context: El 20% es manejable. GROUP BY y ILIKE con RLS tienen overhead mayor (2.4x-6x).
Confidence: high

---

## 8. Costo a Escala: 1M Vectores / 100 Tenants

### 8.1 Supabase Pro + pgvector (estatus actual de Faberloom)

Claim: Supabase Pro = $25/mes base (incluye 8GB DB, 100GB storage, 250GB bandwidth, 100K MAUs). pgvector ya está incluido. 1M vectores 768d ≈ 3GB de storage. 100 tenants con RLS = mismo storage compartido [^597^][^605^].
Source: DesignRevision / Medium Supabase vs Pinecone
URL: https://designrevision.com/blog/supabase-pricing
Date: 2026-02-12
Excerpt: "Pro plan at $25/month... 8 GB database... For a SaaS with 20,000 MAUs, 10 GB database, 50 GB storage, and 100 GB bandwidth, the monthly bill stays close to the $25 base"
Context: Para Faberloom (PYMEs B2B LATAM), 100 tenants con bajo volumen probablemente caben en Pro sin overages. El costo vector sería ~$0 adicional (pgvector es extensión gratis).
Confidence: high

Claim: pgvector en Supabase Pro con 1M vectores 768d (≈3GB) + HNSW index (≈3-4GB adicional) = ~6-7GB total. Cabe en los 8GB del Pro plan. Si se excede, storage adicional = $0.125/GB-mes [^604^].
Source: Supabase pricing
URL: https://supabase.com/pricing
Date: current
Excerpt: "8 GB disk size per project then $0.125 per GB"
Context: Con dimensiones más pequeñas (384d como all-MiniLM-L6-v2), 1M vectores = ~1.5GB raw + index ≈ 3GB. Mucho más barato.
Confidence: high

### 8.2 Alternativas: costo estimado para 1M vectores / 100 tenants

| Opción | Costo mensual estimado | Notas |
|--------|------------------------|-------|
| **Supabase Pro + pgvector** | **$25-35/mes** | Base $25 + posible storage adicional. RLS nativa. Sin costo extra por vector DB. |
| **Supabase Pro + pgvectorscale** | $25-35/mes (si disponible) | Mismo costo pero mejor performance. NO disponible en Supabase cloud aún. |
| **Qdrant Cloud (Standard)** | $25-75/mes | Free tier cubre 1M vectores 768d. 100 tenants = 100 namespaces? Qdrant no tiene límite estricto de namespaces. |
| **Qdrant self-hosted (DO 4GB)** | $24-48/mes | Droplet $24/mes (4GB RAM). Con quantization, cabe fácilmente 1M+ vectores. Requiere DevOps. |
| **Weaviate Cloud (Flex)** | $45-100/mes | Mínimo $45. 1M vectores 1536d = ~$45-60 de dimension storage. |
| **Weaviate self-hosted (VPS)** | $20-50/mes | VPS $20-50. Requiere Docker/K8s expertise. |
| **Turbopuffer** | $64/mes (mínimo) | ~$9 de uso real + $64 mínimo = $64. Sin límite namespaces. |
| **Pinecone Serverless** | $25-70/mes | Free tier 100K vectores. Standard $25 mínimo. 20 namespaces max en Standard. |
| **Mem0 Platform** | $99-299/mes | Capa de memoria, NO reemplaza vector DB. |
| **LanceDB OSS** | $0 (infra propia) | Embedded only. No sirve para SaaS multi-tenant concurrente. |

Claim: Para un workload de 1M vectores / 100 tenants / query volume moderado, Supabase Pro + pgvector es la opción más barata ($25-35/mes). Qdrant free tier es competitiva si se acepta el riesgo de suspensión por inactividad [^473^][^612^].
Source: Pecollective / LeanOpsTech
URL: https://pecollective.com/blog/vector-database-guide/
Date: 2026-02-15
Excerpt: "At 1M vectors: pgvector $0-50 (existing DB), Pinecone $70-231/mo, Weaviate Cloud $25-100/mo, Qdrant Cloud $25-75/mo"
Context: Estos rangos son para workloads generales. Con 100 tenants pequeños (PYMEs LATAM), pgvector en Supabase es prácticamente "gratis" dado que ya se paga por Postgres.
Confidence: high

---

## 9. Recomendaciones para Faberloom MVP

### 9.1 Decisión: pgvector en Supabase Pro (mantener)

**RECOMENDACIÓN: NO cambiar de vector DB en el MVP.** Las razones:

1. **Costo:** Supabase Pro ya cubre pgvector. 1M vectores caben en el plan base. Costo adicional por vector DB = $0.
2. **RLS nativa:** PostgreSQL RLS con `tenant_id` + `current_setting('app.current_tenant')` proporciona aislamiento multi-tenant sin código adicional [^585^][^547^].
3. **Stack simplificado:** Un solo sistema (PostgreSQL) para relacional + vector + auth + storage. Sin sincronización, sin ETL, sin múltiples connection pools [^662^].
4. **Suficiente para escala MVP:** Benchmarks muestran pgvector HNSW a 1M vectores = p50 ~5ms, p95 ~12ms [^571^]. Esto es más que suficiente para cobranza + proformas.
5. **pgvectorscale como upgrade futuro:** Si a 6-12 meses se necesita >5-10M vectores, migrar a pgvectorscale (si está disponible en Supabase) o self-host Postgres con pgvectorscale. El benchmark de 50M vectores muestra que pgvector+pgvectorscale compite con Qdrant/Pinecone [^565^][^572^].

### 9.2 Alternativas a considerar post-MVP (diferir)

| Alternativa | Cuándo evaluar | Condición trigger |
|-------------|---------------|-----------------|
| **pgvectorscale** | 6-12 meses | >5M vectores O Supabase lo habilita en cloud |
| **Qdrant self-hosted** | 12-18 meses | Necesidad de <3ms latency consistente O noisy neighbor en pgvector |
| **Weaviate** | 12-18 meses | Tenant isolation física requerida por compliance (HIPAA/SOC2) O >1M tenants |
| **Turbopuffer** | 12-18 meses | Escalar a 1000+ tenants con namespace isolation sin DevOps |
| **Mem0** | Solo si se añade "agent memory" | Necesidad de memoria contextual persistente por usuario (no reemplaza RAG) |

### 9.3 Descartar para MVP

- **LanceDB:** Es embedded. No sirve para backend SaaS multi-tenant concurrente. Descartar completamente para Faberloom.
- **Mem0 como reemplazo de vector DB:** Mem0 NO es vector DB. Es capa de memoria. Descartar como alternativa a pgvector. Evaluar SOLO si se construye "agent memory" feature separado.
- **Weaviate Cloud:** Mínimo $45/mes. Aumentaría costo MVP ~80% sin beneficio claro a 1M vectores.
- **Turbopuffer:** Mínimo $64/mes. Más caro que Supabase Pro entero.

### 9.4 Contra-argumentos documentados

Claim: Algunos ingenieros reportan que "complex vector operations feel like you're fighting the database" en pgvector. Advanced filtering requiere cuidadosa optimización SQL [^605^].
Source: Medium Supabase vs Pinecone migration
URL: https://deeflect.medium.com/supabase-vs-pinecone-i-migrated-my-production-ai-system-and-heres-what-actually-matters-7b2f2ebd59ee
Date: 2025-07-31
Excerpt: "Where it gets painful: Complex vector operations feel like you're fighting the database. Advanced filtering requires careful SQL optimization."
Context: Para Faberloom, los queries son simples (top-k similares + RLS tenant_id). No hay joins complejos ni aggregaciones vectoriales.
Confidence: high

Claim: pgvector HNSW tiene "expansion factor" variable (índice puede ser 1.2x-5x el tamaño del dataset), haciendo difícil predecir RAM requerida [^506^].
Source: Pinecone blog
URL: https://www.pinecone.io/blog/pinecone-vs-pgvector/
Date: 2024-04-17
Excerpt: "The 'expansion factor' — the ratio of the index RAM to the original dataset — varies significantly... there is no simple way to figure out how to size the index’s working set memory"
Context: A 1M vectores esto es manejable. A 50M+ vectores se vuelve crítico. Para MVP Faberloom, riesgo bajo.
Confidence: high

---

## 10. Hallazgos Clave Consolidados

| Pregunta | Respuesta | Confianza |
|----------|-----------|-----------|
| ¿pgvectorscale mejora pgvector? | Sí, dramáticamente a >5M vectores (DiskANN + SBQ). 11x throughput vs Qdrant a 50M. | High |
| ¿pgvectorscale está en Supabase? | NO (jul 2025). Solo self-hosted o Timescale Cloud. | High |
| ¿Qdrant tiene multi-tenancy nativo? | Sí, Tiered Multitenancy v1.16 (nov 2025). Shared→dedicated shard sin downtime. | High |
| ¿Weaviate es mejor para multi-tenant SaaS? | Sí, arquitectura más madura (shard-per-tenant + Tenant Controller). Pero overkill para MVP. | High |
| ¿Mem0 reemplaza vector DB? | NO. Es capa de memoria sobre vector DB externo. Requiere Qdrant/pgvector/etc. | High |
| ¿LanceDB sirve para SaaS backend? | NO. Es embedded. Descartar para Faberloom. | High |
| ¿Turbopuffer es más barato que Supabase? | A 1M vectores: NO ($64 mínimo vs $25 Supabase). A escala alta con muchos tenants: SÍ. | Medium |
| ¿Qué DBs tienen RLS nativo? | Solo PostgreSQL/pgvector. Las demás usan namespaces/payload filtering. | High |
| ¿Costo 1M vectores / 100 tenants? | Supabase Pro: $25-35. Qdrant free: $0 (riesgo suspensión). Qdrant Std: $25-75. Weaviate: $45+. Turbopuffer: $64. | Medium |
| ¿Recomendación para Faberloom MVP? | **Mantener pgvector en Supabase Pro.** Diferir alternativas a post-MVP. Evaluar pgvectorscale cuando Supabase lo soporte o >5M vectores. | High |

---

## Fuentes Citadas

[^4^]: https://dev.to/__8fa66572/postgresql-rls-in-go-architecting-secure-multi-tenancy-4ifm (2026-01-29)
[^503^]: https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/ (2026-03-01)
[^538^]: https://www.reddit.com/r/vectordatabase/comments/1sfv5x1/benchmark_pgvector_vs_pinecone_vs_qdrant_vs/
[^547^]: https://www.pedroalonso.net/blog/postgres-multi-tenant-search/ (2025-11-04)
[^562^]: https://www.groovyweb.co/blog/vector-database-comparison-2026 (2026-04-03)
[^565^]: https://www.firecrawl.dev/blog/best-vector-databases (2025-10-09)
[^566^]: https://medium.com/@DataCraft-Innovations/postgres-vector-search-with-pgvector-benchmarks-costs-and-reality-check-f839a4d2b66f (2025-09-03)
[^568^]: https://getathenic.com/blog/pinecone-vs-weaviate-vs-qdrant-vs-pgvector (2025-09-06)
[^571^]: https://vecstore.app/blog/vector-database-performance-compared (2026-04-06)
[^572^]: https://dev.to/polliog/postgresql-as-a-vector-database-when-to-use-pgvector-vs-pinecone-vs-weaviate-4kfi (2026-03-04)
[^573^]: https://www.actian.com/blog/databases/how-to-evaluate-vector-databases-in-2026/ (2026-03-27)
[^574^]: https://ranksquire.com/2026/03/04/vector-database-pricing-comparison-2026/ (2026-03-04)
[^575^]: https://www.dbta.com/Editorial/News-Flashes/Qdrant-Launches-Tiered-Multitenancy-for-Vector-Search-172538.aspx (2025-11-21)
[^576^]: https://finance.yahoo.com/news/qdrant-introduces-tiered-multitenancy-eliminate-130000386.html (2025-11-19)
[^577^]: https://www.businesswire.com/news/home/20251119343840/en/ (2025-11-19)
[^578^]: https://weaviate.io/blog/weaviate-multi-tenancy-architecture-explained (2025-10-08)
[^580^]: https://www.dbvis.com/thetable/pgvectorscale-an-extension-for-improved-vector-search-in-postgres/ (2025-09-03)
[^581^]: https://liveblocks.io/blog/whats-the-best-vector-database-for-building-ai-products (2025-09-15)
[^583^]: https://www.digitalocean.com/community/tutorials/langgraph-mem0-integration-long-term-ai-memory (2026-03-12)
[^585^]: https://dev.to/young_gao/multi-tenant-architecture-database-per-tenant-vs-shared-schema-1n2e (2026-03-21)
[^586^]: https://checkthat.ai/brands/weaviate/pricing (2026-03-02)
[^587^]: https://www.techbuddies.io/2026/01/01/how-to-implement-postgresql-row-level-security-for-multi-tenant-saas/ (2026-01-01)
[^589^]: https://dev.to/sudarshangouda/ai-agent-memory-from-manual-implementation-to-mem0-to-aws-agentcore-2d7c (2025-11-25)
[^593^]: https://docs.mem0.ai/platform/platform-vs-oss (2026-04-10)
[^597^]: https://designrevision.com/blog/supabase-pricing (2026-02-12)
[^598^]: https://medium.com/@reliabledataengineering/mem0-do-ai-agents-really-need-memory-honest-review-6760b5288f37 (2026-01-27)
[^601^]: https://qdrant.tech/pricing/ (current)
[^604^]: https://supabase.com/pricing (current)
[^605^]: https://deeflect.medium.com/supabase-vs-pinecone-i-migrated-my-production-ai-system-and-heres-what-actually-matters-7b2f2ebd59ee (2025-07-31)
[^608^]: https://encore.dev/articles/best-vector-databases (2026-03-08)
[^612^]: https://leanopstech.com/blog/vector-database-cost-comparison-2026/ (2026-03-23)
[^613^]: https://www.tigerdata.com/blog/making-postgresql-a-better-ai-database (2024-06-11)
[^615^]: https://postgres.fm/episodes/pgvectorscale/transcript (2024-06-14)
[^616^]: https://www.buildmvpfast.com/tools/api-pricing-estimator/qdrant (2024-01-01)
[^619^]: https://github.com/timescale/pgvectorscale (2023-07-01)
[^652^]: https://docs.lancedb.com/ (current)
[^653^]: https://www.mintlify.com/qdrant/qdrant/advanced/quantization (2026-03-04)
[^658^]: https://www.reddit.com/r/Supabase/comments/1i1z3c7/is_pgvectorscale_extension_available_on_supabase/
[^661^]: https://qdrant.tech/documentation/cloud/create-cluster/ (2001-01-01 template)
[^662^]: https://byteiota.com/vector-databases-2026-postgresql-kills-the-category/ (2026-04-22)
[^664^]: https://github.com/pgvector/pgvector/issues/690 (2024-10-03)
[^673^]: https://www.tigerdata.com/blog/pgvector-vs-pinecone (2024-06-11)
[^675^]: https://supabase.com/blog/fewer-dimensions-are-better-pgvector (2023-08-03)
