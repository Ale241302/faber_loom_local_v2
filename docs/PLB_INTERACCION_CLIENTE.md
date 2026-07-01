# PLB_INTERACCION_CLIENTE — Playbook Interacción con Clientes B2B
id: PLB_INTERACCION_CLIENTE
status: DRAFT
visibility: [INTERNAL]
version: 1.1
domain: Plataforma (IDX_PLATAFORMA)
classification: PLAYBOOK — Instrucciones operativas: qué puede preguntar un cliente, qué responde el sistema, qué escala
aplica_a: [SHARED]

refs:
  - ENT_OPS_STATE_MACHINE (estados para respuestas — FROZEN)
  - ENT_OPS_EXPEDIENTE (campos del expediente)
  - ARTIFACT_REGISTRY (documentos descargables ART-01..12)
  - ENT_PLAT_CANALES_CLIENTE (canales de entrada)
  - ENT_PLAT_KNOWLEDGE.E3 (routing consultas B2B)
  - ENT_PLAT_I18N (idioma del cliente)
  - ENT_GOB_AGENTES.E.SVC-01 (agente de servicio B2B)
  - LOC_SVC_ES (templates ES)
  - LOC_SVC_PT (templates PT-BR)

---

## A. Intenciones clasificadas — qué puede preguntar un cliente

### A1. Intenciones que el sistema RESPONDE

| # | Intención | Ejemplo (ES) | Ejemplo (PT-BR) | Fuente de datos | Permiso |
|---|-----------|-------------|-----------------|-----------------|---------|
| 1 | Estado del expediente | "¿En qué va mi pedido?" | "Qual o status do meu pedido?" | expediente.status (PostgreSQL) | VIEW_EXPEDIENTES_OWN |
| 2 | Fecha estimada | "¿Cuándo sale de fábrica?" | "Quando sai da fábrica?" | expediente.fechas + estado actual | VIEW_EXPEDIENTES_OWN |
| 3 | Tracking de envío | "¿Dónde está mi carga?" | "Onde está minha carga?" | ART-05 (AWB/BL) tracking | VIEW_EXPEDIENTES_OWN |
| 4 | Solicitar documento | "Necesito la proforma" | "Preciso da proforma" | ART-02 (Proforma) file | DOWNLOAD_DOCUMENTS |
| 5 | Estado de pago | "¿Cuántos días de crédito llevo?" | "Quantos dias de crédito tenho?" | credit_clock | VIEW_EXPEDIENTES_OWN |
| 6 | Lista de expedientes | "¿Qué pedidos tengo abiertos?" | "Quais pedidos tenho abertos?" | expedientes WHERE client_id AND status NOT IN (CERRADO, CANCELADO) | VIEW_EXPEDIENTES_OWN |
| 7 | Info de producto | "¿Qué materiales usan las Goliath?" | "Que materiais usam nas Goliath?" | pgvector (knowledge chunks, visibility=PUBLIC) | ASK_KNOWLEDGE_PRODUCTS |
| 8 | Info operativa | "¿Cuál es el MOQ?" | "Qual é o MOQ?" | pgvector (knowledge chunks, visibility=PUBLIC) | ASK_KNOWLEDGE_OPS |

### A2. Intenciones que el sistema ESCALA al CEO

| # | Intención | Ejemplo | Por qué no responder | Acción |
|---|-----------|---------|---------------------|--------|
| 9 | Precio / cotización | "¿Cuánto me cuesta 500 pares?" | CEO-ONLY: pricing, márgenes | Notificar CEO con contexto completo |
| 10 | Negociación | "Necesito descuento" | Decisión comercial del CEO | Notificar CEO |
| 11 | Queja / reclamo | "El producto llegó dañado" | Requiere investigación + decisión | Notificar CEO + registrar incidente |
| 12 | Nuevo pedido | "Quiero hacer un pedido de 1000 pares" | Requiere proforma + aprobación CEO |

### A3. Intenciones adicionales identificadas en auditoría (v4.4.1)

| # | Intención | Ejemplo | Resolución | Permiso |
|---|-----------|---------|-----------|---------|
| 13 | Cambio de pedido | "Quiero cambiar las tallas del pedido 2026-001" | Escalar al CEO — modifica expediente | — |
| 14 | Faltantes / RMA | "Me llegaron 960, faltan 40 pares" | Escalar al CEO + registrar incidente | — |
| 15 | Docs técnicos / compliance | "Necesito la ficha técnica de Goliath" | pgvector (visibility=PARTNER_B2B) | ASK_KNOWLEDGE_PRODUCTS |
| 16 | Soporte de acceso | "Cambié de correo y no puedo entrar al portal" | Escalar al CEO (gestión de usuarios) | — |
| 17 | Disponibilidad / SKU / muestras | "¿Tienen talla 46 disponible?" | pgvector (PARTNER_B2B) o PostgreSQL (inventario si existe) | ASK_KNOWLEDGE_OPS | Notificar CEO |

### A3. Intención no clasificable

Si la pregunta no encaja en ninguna intención conocida:
1. Intentar pgvector (knowledge base PUBLIC)
2. Si no hay match con similarity >0.7 → responder: "No tengo esa información disponible. Estoy notificando a Santiago para que te contacte."
3. Notificar CEO con mensaje original + contexto del cliente

---

## B. Reglas de respuesta

### B1. Reglas absolutas (nunca violar)

1. **Nunca inventar datos.** Si el sistema no tiene la info → escalar. No aproximar, no asumir.
2. **Nunca revelar pricing, márgenes, costos internos, comisiones, proveedores, estructura interna.**
3. **Nunca revelar datos de OTRO cliente.** VIEW_EXPEDIENTES_OWN es estricto: solo expedientes donde client_id = el del JWT.
4. **Siempre en el idioma del cliente.** Ref → ENT_PLAT_CANALES_CLIENTE.D para mapeo.
5. **Documentos:** si el cliente pide un documento que existe como artifact, enviar link de descarga. No enviar contenido inline (riesgo de formatting, truncamiento).
6. **Escalamiento inmediato** cuando la intención es A2 (#9-#12). No intentar responder parcialmente.

### B2. Tono y estilo

- Profesional, directo, servicial.
- No usar jerga técnica interna (no "state machine", no "artifact", no "pgvector").
- Usar nombres de estado naturales (ref → LOC_SVC_{LANG} para traducciones).
- No tutear en español (usted). En portugués usar "você" (estándar BR business).
- Firmar como "Asistente MWT" o "Assistente MWT", no como nombre propio.

### B3. Formato de respuesta por canal

| Canal | Largo máximo | Formato | Archivos |
|-------|-------------|---------|----------|
| Portal B2B | Sin límite | Markdown renderizado | Download directo (signed URL) |
| WhatsApp | ~1000 caracteres | Texto plano, sin markdown | Link a portal para descarga (signed URL) |
| Email | ~500 palabras | HTML simple | Link a portal para descarga (signed URL) |

**Regla:** documentos siempre se entregan como signed URL con expiración (15 min). Nunca inline, nunca adjunto directo. Ref → ENT_PLAT_SEGURIDAD.E4.

---

## B4. Matriz de delegación (v4.4.1 — resuelve bottleneck CEO)

| Nivel | Tipo de caso | Owner (MVP) | Owner (escala) | SLA |
|-------|-------------|-------------|---------------|-----|
| L1 — Automatizado | Estado expediente, tracking, docs descargables, info producto | SVC-01 (IA) | SVC-01 (IA) | Inmediato |
| L2 — Operativo | Cambio de pedido, faltantes/RMA, docs no disponibles, soporte acceso | CEO | Operador logística / soporte | 12h business |
| L3 — Comercial | Pricing, cotización, negociación, nuevo pedido, descuentos | CEO | CEO (siempre) | 24h business |
| L3 — Calidad | Queja, reclamo, producto dañado | CEO | Responsable calidad (futuro) | 12h business |

**Principio:** L1 es 100% automático. L2 se delega cuando haya operador. L3 comercial siempre pasa por el CEO. L3 calidad se delega cuando haya responsable de calidad.

**Nota:** hoy L2 y L3 van todos al CEO. La matriz existe para que cuando haya equipo, la delegación esté definida.

---

## C. Respuestas por estado del expediente

Templates canónicos viven en LOC_SVC_{LANG}. El sistema consulta el estado del expediente y selecciona el template correspondiente, reemplazando placeholders con datos reales.

**Placeholders disponibles:**

| Placeholder | Fuente | Ejemplo |
|------------|--------|---------|
| {expediente_ref} | expediente.ref | "EXP-2026-001" |
| {fecha_estimada} | expediente.fechas[estado_actual] | "2026-04-15" |
| {tracking} | ART-05.tracking_number | "MSKU123456789" |
| {carrier} | ART-05.carrier | "MSC" |
| {destino} | expediente.destino | "Santos, BR" |
| {fecha_cierre} | expediente.fecha_cierre | "2026-03-10" |
| {dias_credito} | credit_clock.dias_transcurridos | "45" |
| {dias_limite} | credit_clock.dias_limite | "90" |

Ref → LOC_SVC_ES para templates en español.
Ref → LOC_SVC_PT para templates en portugués brasileño.

---

## D. Documentos descargables por el cliente

Artifacts que un cliente con DOWNLOAD_DOCUMENTS puede solicitar:

| Artifact | ID | Disponible para cliente | Nota |
|----------|----|------------------------|------|
| OC Cliente | ART-01 | ✅ | Su propia orden de compra |
| Proforma MWT | ART-02 | ✅ | Proforma de su expediente |
| AWB/BL | ART-05 | ✅ | Documento de embarque |
| Cotización flete | ART-06 | ⚠️ CEO decide | Puede contener costos internos |
| Factura MWT | ART-09 | ✅ | Factura de su expediente |
| Decisión B/C | ART-03 | ❌ | Interno — decisión banking/card |
| Confirmación SAP | ART-04 | ❌ | Interno — confirmación proveedor |
| Aprobación despacho | ART-07 | ❌ | Interno — workflow aprobación |
| Docs aduanales | ART-08 | ⚠️ CEO decide | Depende del tipo |
| Registro costos | ART-11 | ❌ | CEO-ONLY — costos reales |
| Nota compensación | ART-12 | ❌ | Interno |

**Regla:** ante la duda, no enviar. Escalar al CEO.

---

## E. Clasificador de intención — lógica de routing (v1.1 — corregido por auditoría triangulada)

**Interfaz del clasificador** (independiente de implementación):

```
INPUT:  message: string, lang: string, user: MWTUser
OUTPUT: { intent: IntentEnum, params: { ref?: string, artifact_id?: string, ... } }
```

**MVP:** reglas con prioridad jerárquica (DeepSeek). **Escala:** Function Calling LLM (Gemini). La interfaz no cambia.

### E1. Jerarquía de prioridad (menor número = mayor prioridad)

```
P1 — QUEJA/RECLAMO (siempre escalar)
     Keywords: "dañado", "roto", "problema", "queja", "reclamo", "faltante",
              "danificado", "quebrado", "problema", "reclamação", "faltando"
     → Escalar CEO + registrar incidente

P2 — COMERCIAL/NEGOCIACIÓN (siempre escalar)
     Keywords: "precio", "costo", "cotización", "descuento", "negociar",
              "nuevo pedido", "preço", "custo", "cotação", "desconto",
              "quiero pedir", "quero pedir", "cambiar pedido", "alterar pedido"
     → Escalar CEO

P3 — SOPORTE ACCESO (escalar)
     Keywords: "no puedo entrar", "cambié correo", "cambié número",
              "não consigo entrar", "mudei email", "mudei número", "contraseña", "senha"
     → Escalar CEO (gestión de usuarios)

P4 — DOCUMENTO ESPECÍFICO (responder — artifact download)
     Keywords: "proforma", "factura", "fatura", "AWB", "BL", "conocimiento de embarque",
              "documento", "descargar", "baixar", "enviar documento"
     → Buscar artifact por nombre + expediente del cliente
     → Permiso: DOWNLOAD_DOCUMENTS

P5 — OPERATIVO / EXPEDIENTE (responder — PostgreSQL directo)
     Keywords: "pedido", "orden", "estado", "status", "tracking",
              "envío", "embarque", "carga", "crédito", "pago",
              "ordem", "rastreio", "pagamento"
     → PostgreSQL con filtro client_id
     → Permiso: VIEW_EXPEDIENTES_OWN

P6 — PRODUCTO / OPERACIONES GENÉRICA (responder — pgvector)
     Keywords: "material", "talla", "tamanho", "MOQ", "proceso", "ficha técnica"
     → pgvector (visibility IN [PARTNER_B2B, PUBLIC])
     → Permiso: ASK_KNOWLEDGE_PRODUCTS o ASK_KNOWLEDGE_OPS

P7 — NO CLASIFICABLE (fallback)
     → Intentar pgvector (similarity >0.7)
     → Si no match → escalar al CEO
```

### E2. Resolución de ambigüedad

Si un mensaje activa múltiples prioridades (ej: "necesito el precio de la proforma"), gana la de **menor número** (mayor prioridad). Excepción: si P4 (documento) y P2 (comercial) coinciden, y el mensaje pide explícitamente un documento descargable, P4 gana — porque pedir una proforma que ya existe no es negociación.

Regla: `if P4_match AND P2_match AND artifact_exists_for_client → P4 wins`

### E3. Extracción de entidades (NER ligero)

Después de clasificar, extraer parámetros del mensaje:
- `expediente_ref`: regex `\b(EXP-)?20\d{2}-\d{3}\b` o similar al formato del sistema
- `artifact_name`: match contra nombres conocidos (proforma, factura, AWB)
- `product_name`: match contra catálogo de productos (Goliath, Velox, Orbis...)

Validar SIEMPRE que el parámetro extraído pertenece al cliente (ref → ENT_PLAT_KNOWLEDGE.E3 ClientScopedManager).

**Nota:** este clasificador es diseño, no código. Alejandro implementa en el AI Middleware.

---

## F. Escalamiento al CEO

### F1. Formato de notificación

Cuando el sistema escala, el CEO recibe:

```
🔔 Escalamiento de cliente B2B

Cliente: {nombre_cliente} ({legal_entity})
Canal: {canal}
Expediente: {expediente_ref} (si aplica)
Mensaje original: "{texto_del_cliente}"
Intención detectada: {intención}
Razón de escalamiento: {razón}
Timestamp: {fecha_hora}

→ Responder en: {canal_respuesta}
```

### F2. Canal de notificación al CEO

- MVP: notificación en consola MWT (dashboard CEO)
- Futuro: push notification, email, WhatsApp del CEO
- [PENDIENTE — CEO definir canal preferido de notificación]

### F3. SLA de respuesta del CEO

- Precio/cotización: 24h (business hours)
- Queja/reclamo: 12h
- Nuevo pedido: 48h
- [PENDIENTE — CEO confirmar SLAs]

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Implementar clasificador de intención en AI Middleware | Técnico (Ale) | Flujo automatizado |
| Z2 | Definir artifacts visibles para cliente (ART-06, ART-08 — CEO decide) | Decisión | Sección D completa |
| Z3 | Definir canal notificación al CEO (F2) | Decisión | Escalamiento operativo |
| Z4 | Confirmar SLAs de respuesta CEO (F3) | Decisión | Compromisos de servicio |
| Z5 | Implementar canal WhatsApp (P2) | Técnico | Sección A.2 operativo |
| Z6 | Implementar canal Email (P3) | Técnico | Sección A.3 operativo |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v1.0 (2026-03-15): creación. 12 intenciones clasificadas (8 responde, 4 escala). Reglas de respuesta (6 absolutas + tono + formato por canal). Templates ref → LOC_SVC_{LANG}. Artifacts descargables por cliente. Clasificador de intención (diseño). Escalamiento al CEO con formato. Iteración Claude↔Perplexity aprobada.
