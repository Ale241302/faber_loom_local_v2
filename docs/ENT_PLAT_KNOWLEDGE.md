# ENT_PLAT_KNOWLEDGE — Capa de Conocimiento
id: ENT_PLAT_KNOWLEDGE
status: VIGENTE
stamp: VIGENTE — aprobado 2026-03-15
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
version: 2.2
classification: ENTITY — Data pura inyectable.
refs: ENT_PLAT_INFRA, ENT_PLAT_SEGURIDAD, ENT_PLAT_AGENTIC, POL_ARCHIVO, POL_VISIBILIDAD
aplica_a: [SHARED]

---

## A. Propósito

Definir la arquitectura de la capa de conocimiento que permite al agente IA operar embebido en MWT.ONE con consciencia continua del negocio: reglas, procesos, clientes, historial y contexto en tiempo real. El agente no espera consultas — observa, piensa y actúa.

---

## B. Principios

1. **IA-nativa.** La IA no es un servicio que se consulta. Es una capa que envuelve toda la operación.
2. **Conocimiento agnóstico de proveedor.** Markdown + pgvector + PostgreSQL = estándares abiertos. Cualquier modelo de IA puede consumir el conocimiento.
3. **Seguridad por diseño.** Los datos CEO-ONLY nunca viajan a APIs externas como contexto de knowledge base. Viven solo en PostgreSQL con acceso controlado por rol.
4. **La fuente de verdad son los markdown.** El vector store es un índice de consulta derivado, no una copia independiente.
5. **DRAFT no entra.** Solo documentos con stamp VIGENTE se indexan en el vector store. El agente no actúa con reglas no aprobadas.

---

## C. Arquitectura

### C1. Tres capas de almacenamiento

| Capa | Tecnología | Contenido | Acceso |
|------|-----------|-----------|--------|
| Archivos raw | MinIO (ya existe) | Markdown files, PDFs, emails, adjuntos | Lectura por Windmill para indexación |
| Búsqueda semántica | pgvector en PostgreSQL 16 (ya existe) | Embeddings de chunks de conocimiento | Query por Django API |
| Datos estructurados | PostgreSQL 16 (ya existe) | Expedientes, clientes, pricing, estados | Query directo por Django ORM |

### C2. Modelo de datos — knowledge_chunks

```
knowledge_chunks {
  id: serial PRIMARY KEY
  source_file: varchar(100)        # PLB_REGISTRO_PROFORMA
  section: varchar(50)             # B6b.1
  chunk_index: integer             # orden dentro del archivo
  content: text                    # texto del chunk
  embedding: vector(1024)          # embedding generado por modelo
  
  # Metadata del documento fuente
  doc_type: enum                   # ENT | SCH | POL | PLB | LOC | IDX
  domain: varchar(50)              # Comercial | OPS | Plataforma | Gobernanza | Marca
  visibility: enum                 # INTERNAL | PUBLIC
  version: varchar(10)             # 2.3
  stamp: enum                      # VIGENTE | DRAFT | DEPRECATED
  
  # Control
  embedding_model: varchar(50)     # claude-3-sonnet | text-embedding-3-large
  indexed_at: timestamp
  source_hash: varchar(64)         # SHA-256 del archivo fuente
}
```

**Reglas de la tabla:**
- Solo `stamp = VIGENTE` es consultable por el agente.
- `visibility = CEO-ONLY` nunca se inserta en esta tabla.
- `source_hash` detecta si el archivo cambió. Si no cambió, no se re-indexa.
- Índice GiST/IVFFlat sobre `embedding` para búsqueda eficiente.

### C3. Qué se indexa y qué no

| Tipo | Se indexa en pgvector | Razón |
|------|----------------------|-------|
| PLB_ (playbooks) | ✅ | Reglas operativas, flujos, delegación |
| POL_ (policies) | ✅ | Constraints del sistema |
| SCH_ (schemas) | ✅ | Plantillas de ensamblaje |
| ENT_ visibility=INTERNAL | ✅ | Datos operativos |
| ENT_ visibility=CEO-ONLY | ❌ | Datos sensibles. Solo en PostgreSQL directo |
| LOC_ (localizations) | ✅ | Datos localizados por idioma |
| IDX_ (indexes) | ✅ | Rutas y estructura |
| Datos comerciales reales | ❌ | Precios, márgenes, comisiones → PostgreSQL tablas operativas |

### C4. Resource planning

| Recurso | Estimación | Disponible |
|---------|-----------|-----------|
| RAM pgvector | ~100-200 MB para 119+ archivos | 22 GB libres (ref ENT_PLAT_INFRA) |
| Disco | ~500 MB (embeddings + chunks) | 307 GB libres |
| Servicios nuevos | 0 (pgvector es extensión de PostgreSQL existente) | — |

---

## D. Pipeline de indexación

### D1. Trigger

```
Archivo nuevo/actualizado en MinIO (bucket: knowledge/)
    → webhook a Windmill
    → Windmill ejecuta pipeline
```

### D2. Pipeline (Windmill script Python)

```
1. DETECTAR CAMBIO
   - Calcular SHA-256 del archivo
   - Comparar contra source_hash en knowledge_chunks
   - Si no cambió → skip
   - Si cambió → continuar

2. VALIDAR
   - Verificar header: status, visibility, stamp, domain, version
   - Si stamp ≠ VIGENTE → no indexar (DELETE chunks existentes si había)
   - Si visibility = CEO-ONLY → no indexar
   - Si header incompleto → alerta, no indexar

3. CHUNKAR
   - Dividir por secciones (## headers)
   - Chunks de ~500-800 tokens
   - Preservar contexto: cada chunk incluye header del documento + sección padre
   - Asignar chunk_index secuencial

4. GENERAR EMBEDDINGS
   - Llamar API del modelo de embeddings (configurable)
   - Un embedding por chunk

5. PERSISTIR
   - DELETE FROM knowledge_chunks WHERE source_file = X
   - INSERT nuevos chunks con embeddings
   - Actualizar source_hash, indexed_at

6. LOG
   - Registrar en tabla indexation_log: archivo, chunks, timestamp, modelo, status
```

### D3. Modelos de embedding soportados

| Modelo | Proveedor | Dimensiones | Nota |
|--------|----------|-------------|------|
| claude-3-sonnet | Anthropic | 1024 | Default actual |
| text-embedding-3-large | OpenAI | 3072 | Alternativa |
| Local (futuro) | Self-hosted | Variable | Cuando sea viable |

El modelo es configurable. Si se cambia, se re-indexa todo.

---

## E. Consulta por el agente

### E1. Endpoint Django

```
POST /api/knowledge/search/
{
  "query": "qué hacer si Marluvas bloquea un SKU",
  "top_k": 5,
  "filters": {
    "doc_type": ["PLB", "POL"],     // opcional
    "domain": "Comercial",           // opcional
    "stamp": "VIGENTE"               // siempre forzado
  }
}

Response:
{
  "chunks": [
    {
      "source_file": "PLB_REGISTRO_PROFORMA",
      "section": "B6b.1",
      "content": "...",
      "similarity": 0.92
    }
  ]
}
```

### E2. Flujo de consulta del agente

```
Evento llega (email, cambio, timer)
    → AI Middleware recibe evento
    → Genera query semántica basada en el evento
    → POST /api/knowledge/search/
    → Recibe chunks relevantes (reglas, procesos, contexto)
    → Consulta PostgreSQL directo (datos del expediente, cliente, estado)
    → Construye prompt: evento + chunks + datos
    → Llama API del modelo IA (Claude, GPT, otro)
    → Recibe decisión: ACTUAR | RECOMENDAR | OBSERVAR
    → Ejecuta según delegación (ref PLB_REGISTRO_PROFORMA §C R14)
    → Logea razonamiento en el expediente
```

### E3. Consulta por cliente B2B — routing de consultas (SSOT)

**Esta sección es la fuente única de verdad (SSOT) para el routing de consultas B2B.** PLB_INTERACCION_CLIENTE.E y ENT_PLAT_CANALES_CLIENTE.B resumen y referencian aquí. Si hay contradicción, E3 gana.

Cuando el query viene de un cliente B2B (role=CLIENT_*), el routing es diferente al del agente interno:

**Principio:** las consultas B2B de expediente van directo a PostgreSQL (datos operativos), NO a pgvector. pgvector solo entra para preguntas genéricas de producto/operaciones.

```
Mensaje del cliente B2B (cualquier canal)
    │
    ├─ Intención operativa (expediente, tracking, documento, pago)
    │   → PostgreSQL directo (Django ORM via ClientScopedManager)
    │   → Filtro OBLIGATORIO: legal_entity_id = JWT.legal_entity_id
    │   → Permiso: VIEW_EXPEDIENTES_OWN
    │   → Nunca exponer: pricing, márgenes, datos de otros clientes
    │
    ├─ Intención de producto/operaciones genérica
    │   → pgvector (knowledge_chunks WHERE visibility IN ['PARTNER_B2B', 'PUBLIC'])
    │   → Filtro: stamp = VIGENTE
    │   → Permiso: ASK_KNOWLEDGE_PRODUCTS o ASK_KNOWLEDGE_OPS
    │
    ├─ Intención comercial (precio, cotización, negociación)
    │   → NO responder → escalar al CEO
    │
    └─ No clasificable
        → Intentar pgvector (similarity >0.7, visibility IN ['PARTNER_B2B', 'PUBLIC'])
        → Si no match → escalar al CEO
```

**ClientScopedManager (spec técnica — hallazgo DeepSeek):**

```python
class ClientScopedQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.role in ['CLIENT_MARLUVAS', 'CLIENT_TECMATER']:
            return self.filter(legal_entity_id=user.legal_entity_id)
        return self  # CEO/INTERNAL ven todo

class ExpedienteManager(models.Manager):
    def get_queryset(self):
        return ClientScopedQuerySet(self.model, using=self._db)
```

**Regla:** toda consulta B2B a expedientes DEBE usar `Expediente.objects.for_user(user)`. Nunca `Expediente.objects.all()` para un cliente. El scope es imposible de bypass si el manager está bien implementado.

**Mensajes de error genéricos (anti data-leakage):**
- Si el expediente no existe O no pertenece al cliente → mismo mensaje: "No encontré ese expediente."
- Nunca distinguir entre "no existe" y "no tienes acceso" — eso revela información.

**Visibilidad PARTNER_B2B (nuevo v4.4.1):**
Tier intermedio entre PUBLIC e INTERNAL. Para contenido que un distribuidor necesita pero no es público: fichas técnicas, certificados, catálogos privados, docs de onboarding, políticas operativas permitidas. Ref → ENT_PLAT_SEGURIDAD.C1.

**La IA nunca toca el ORM directamente (hallazgo Gemini):**
```
IA clasifica → extrae {intent, params} → Django ejecuta query con params validados
```
La IA es un router. Django es el ejecutor. Separación estricta.

Ref → PLB_INTERACCION_CLIENTE para reglas completas de respuesta y clasificador.
Ref → ENT_PLAT_CANALES_CLIENTE para canales de entrada y auth.
Ref → ENT_PLAT_SEGURIDAD.E para seguridad por canal.

---

## F. AI Middleware — El agente vivo

### F1. Concepto

Servicio Python que escucha el event bus, piensa con la IA, y actúa. Siempre encendido, siempre escuchando. No espera que le pregunten.

### F2. Modos de operación

| Modo | Trigger | Acción |
|------|---------|--------|
| ACTUAR | Evento + delegación lo permite | Ejecuta automáticamente (recordatorio, reply estructural, alerta) |
| RECOMENDAR | Evento requiere decisión CEO | Genera draft/resumen con contexto y opciones, lo pone en cola del CEO |
| OBSERVAR | Evento informativo | Registra en el diario del expediente, no actúa |

### F3. Diario del agente

Cada expediente tiene un log de lo que el agente pensó, observó, recomendó y ejecutó:

```
agent_diary {
  id: serial
  expediente_id: ref
  timestamp: datetime
  mode: enum                # ACTUAR | RECOMENDAR | OBSERVAR
  event_type: varchar       # email.received | sla.approaching | date.changed
  reasoning: text           # qué pensó el agente y por qué
  action_taken: text | null # qué hizo (si actuó)
  recommendation: text | null # qué sugirió (si recomendó)
  chunks_used: jsonb        # qué knowledge consultó
  model_used: varchar       # claude-sonnet-4 | gpt-4o
}
```

Cuando el CEO abre un expediente, no solo ve datos — ve el razonamiento del sistema.

### F4. Docker

| Servicio | RAM | CPU | Función |
|----------|-----|-----|---------|
| ai-middleware | 1 GB | 0.5 core | Event listener + knowledge query + IA API calls |

Cabe en el headroom actual (22 GB RAM, 3.8 cores libres post-MVP).

Depende de: Redis Streams (event bus), PostgreSQL (knowledge + datos), API externa (modelo IA).

---

## G. Puente: Taller → Producción

### G1. Flujo de publicación

```
Claude Project (taller de diseño)
    │ CEO descarga archivo .md aprobado
    ▼
Git repo privado (mwt-knowledge/)
    │ git push
    ▼
GitHub webhook → Windmill
    │ pipeline D2
    ▼
MinIO (archivo raw) + pgvector (embeddings)
    │
    ▼
Agente en producción consulta versión nueva
```

### G2. Reglas del puente

- Solo archivos con stamp VIGENTE se pushean al repo.
- El repo Git es la fuente de verdad para producción. No MinIO, no pgvector — el repo.
- Git da historial completo, diff entre versiones, rollback.
- Si se deja de usar Claude como taller, el repo sigue vivo con todo el knowledge base.
- Múltiples personas o agentes pueden contribuir al repo.

### G3. Independencia de proveedor

```
Hoy:  Claude Project (taller) → Git → Producción (pgvector + API Claude)
Mañana: Cualquier editor → Git → Producción (pgvector + cualquier modelo IA)
```

El conocimiento es portable. La IA es intercambiable.

---

## H. Seguridad

### H1. Qué viaja a la API externa (modelo IA)

- Chunks de knowledge (INTERNAL solamente, nunca CEO-ONLY)
- Contexto del evento (email parseado, datos del expediente)
- La pregunta/instrucción del agente

### H2. Qué NUNCA viaja a la API externa

- Datos CEO-ONLY (precios reales, márgenes, comisiones)
- Credenciales, API keys, tokens
- Datos personales de clientes sin necesidad operativa

### H3. Cómo se accede a datos CEO-ONLY

El agente los lee directamente de PostgreSQL (tablas operativas, no knowledge_chunks) dentro del servidor. El dato nunca sale. El cálculo se hace localmente. Solo el resultado (ej: "margen positivo" o "margen insuficiente") puede incluirse en el prompt al modelo IA si es necesario para la decisión.

### H4. Roles

| Rol | Accede knowledge_chunks | Accede datos CEO-ONLY | Llama API IA |
|-----|------------------------|----------------------|-------------|
| AI Middleware | ✅ (filtrado por visibility) | ✅ (lectura directa DB) | ✅ |
| CEO (webapp) | ✅ (todo INTERNAL) | ✅ (todo) | ✅ (chat interno) |
| Agente operativo (webapp) | ✅ (filtrado por rol) | ❌ | ❌ |
| API externa (modelo IA) | Recibe chunks seleccionados | ❌ Nunca | N/A (es el modelo) |

---

Stamp: DRAFT — Pendiente aprobación CEO


## Backup y sincronización KB (spec DeepSeek Prompt 6 — aprobación pendiente CEO)

### Arquitectura
- **Fuente de verdad:** GitHub repo privado `mwt-knowledge-base`
- **Servidor:** clon en `/opt/mwt-knowledge/docs`, cron `git pull` cada 5 min
- **Contenedor mwt-knowledge:** monta `/opt/mwt-knowledge/docs:/docs:ro` (read-only)
- **Acceso Perplexity:** Nginx en `knowledge.mwt.one` con auth básica (htpasswd)
- **Backup redundante:** script diario tar.gz → MinIO bucket `knowledge-backup`

### Flujo CEO
1. Trabaja en Claude Project → descarga ZIP
2. Descomprime en clon local de `mwt-knowledge-base`
3. `git add . && git commit -m "Actualización" && git push`
4. En <5 min: servidor hace pull → watcher detecta → reindexa en pgvector

### Esfuerzo: 3-4 horas Ale (crear repo, cron, Nginx, probar)
### Status: PENDIENTE aprobación CEO

---
Changelog:
- v2.0: Sprint 8 — arquitectura knowledge base completa.
- v2.1 (2026-03-15): +E3 "Consulta por cliente B2B — routing de consultas". Diseño del flujo B2B: PostgreSQL directo para expedientes, pgvector para producto genérico, escalamiento para comercial. Refs: PLB_INTERACCION_CLIENTE, ENT_PLAT_CANALES_CLIENTE. Iteración Claude↔Perplexity aprobada.
