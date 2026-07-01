# ENT_PLAT_CANALES_CLIENTE — Canales de Interacción B2B con Clientes
id: ENT_PLAT_CANALES_CLIENTE
status: DRAFT
visibility: [INTERNAL]
version: 1.1
domain: Plataforma (IDX_PLATAFORMA)
classification: ENTITY — Data pura: canales por donde clientes B2B consultan el sistema
aplica_a: [SHARED]

refs:
  - ENT_PLAT_CANALES (canales de VENTA — complementario, no duplicado)
  - ENT_PLAT_KNOWLEDGE.E3 (routing de consultas B2B)
  - ENT_PLAT_LEGAL_ENTITY (mapeo client → legal entity)
  - ENT_PLAT_SEGURIDAD (auth por canal)
  - PLB_INTERACCION_CLIENTE (reglas de respuesta)
  - LOTE_SM_SPRINT8 (JWT, roles CLIENT_*, permisos)

---

## A. Canales definidos

| # | Canal | Entrada | Auth | Respuesta | Prioridad | Status |
|---|-------|---------|------|-----------|-----------|--------|
| 1 | Portal B2B (portal.mwt.one) | Chat widget en consola | JWT session (Sprint 8) | Texto + descarga directa de artifacts | **P1** | Auth lista (JWT, roles, API). Bloqueadores: fix 500 en /api/knowledge/ask/ + carga inicial docs en pgvector + ENT_PLAT_SEGURIDAD pendientes (signed URLs, CORS, rate limiting). |
| 2 | WhatsApp Business | Webhook → mensaje texto. Audio: [PENDIENTE — requiere transcripción + confidence threshold + fallback a texto] | Número verificado → mapeo a CLIENT_* (virtual request, no JWT) | Texto + links a docs | **P2** | Requiere: WhatsApp Cloud API (Meta, gratis tier), webhook, tabla mapeo números. Timeline estimado: 5-7 días post-decisión (hallazgo Gemini). |
| 3 | Email | n8n parsea inbox dedicado | Dirección remitente → mapeo a CLIENT_* | Email respuesta con signed URL | **P3** | Requiere: inbox dedicado, n8n flow, parseo edge cases (adjuntos, threads) |
| 4 | Llamada telefónica | Manual — CEO/operador | N/A — verbal | Verbal | Fallback | Siempre disponible. Sin automatización. |

**Nota de prioridad:** Portal es P1 porque la infra de auth ya existe (Sprint 8 JWT + roles), pero NO está listo hoy — tiene bloqueadores técnicos y de seguridad. WhatsApp Cloud API es gratis y se configura en 5-7 días (Gemini research), pero requiere tabla de mapeo y decisiones de audio. Email tiene más edge cases.

---

## B. Flujo unificado — todos los canales convergen

```
Cliente envía mensaje (cualquier canal)
    │
    ▼
1. IDENTIFICACIÓN
   Canal → mapeo a user_id → CLIENT_* role → legal_entity_id
   Si no identificado → respuesta genérica + alerta CEO
    │
    ▼
2. CLASIFICACIÓN DE INTENCIÓN (ref → ENT_PLAT_KNOWLEDGE.E3)
   a) Consulta de expediente → PostgreSQL directo (ORM, filtro client_id)
   b) Consulta de producto/operaciones → pgvector (knowledge chunks, visibility=PUBLIC)
   c) Solicitud de documento → artifact download (DOWNLOAD_DOCUMENTS)
   d) Acción fuera de scope → escalamiento al CEO
    │
    ▼
3. GENERACIÓN DE RESPUESTA
   IA genera respuesta en idioma del cliente
   Templates: ref → LOC_SVC_{LANG}
   Tono: ref → PLB_INTERACCION_CLIENTE.B
    │
    ▼
4. ENTREGA
   Responde por el mismo canal de entrada
    │
    ▼
5. LOG
   ConversationLog (Sprint 8): quién, qué preguntó, qué respondió, canal, timestamp
```

---

## C. Mapeo de identidad por canal

### C1. Portal B2B
- Auth: JWT directo. El usuario ya está autenticado con role=CLIENT_MARLUVAS o CLIENT_TECMATER.
- legal_entity_id viaja en el JWT (Sprint 8).
- No requiere mapeo adicional.

### C2. WhatsApp
- Tabla necesaria: `client_whatsapp_numbers`

```
client_whatsapp_numbers {
  id: serial PRIMARY KEY
  phone_number: varchar(20) UNIQUE    # formato E.164: +5511999999999
  user_id: FK → MWTUser
  legal_entity_id: FK → LegalEntity
  verified: boolean                    # CEO verifica el número
  verified_at: timestamp               # fecha última verificación
  created_at: timestamp
}
```

- Flujo: mensaje entrante → extraer número → lookup en tabla → si match y verified=True → crear virtual request (objeto request.user poblado internamente con datos del cliente, NO un JWT que viaja al exterior)
- Contexto conversacional: Redis key `wa:{phone_number}:context` con TTL 24h desde último mensaje
- Si número no mapeado → respuesta genérica: "Número no reconocido. Para registrar su número, contacte a soporte." (no revelar si el número existe o no — anti-enumeración)
- CEO registra números manualmente (MVP). Futuro: self-service en portal.

**Re-verificación periódica (hallazgo Gemini — riesgo rotación de personal):**
- Cada 60-90 días, el CEO debe re-verificar que los números en client_whatsapp_numbers siguen siendo válidos
- Riesgo: un técnico de Marluvas renuncia pero conserva su número de WhatsApp → sigue teniendo acceso a expedientes
- Implementación MVP: CEO revisa tabla manualmente cada 60 días
- Implementación futura: alerta automática cuando verified_at > 60 días → CEO re-confirma o desactiva

### C3. Email
- Mapeo por dirección de remitente. Campo `contact_email` en LegalEntity o tabla dedicada.
- Mismo flujo: email entrante → extraer from address → lookup → crear virtual request.
- Si no mapeado → NO responder automáticamente. Solo notificar CEO. (Email tiene mayor riesgo de spoofing que WhatsApp.)

### C4. Regla de seguridad transversal
- **Nunca responder datos de expediente si la identidad no está verificada.**
- Canal no identificado: respuesta genérica de cortesía + escalamiento al CEO. Excepción: email no verificado no recibe respuesta automática (C3).
- Un número/email puede mapear a UN solo client. No compartido.
- Ref → ENT_PLAT_SEGURIDAD.E para controles de seguridad por canal.

---

## D. Idioma por cliente

| Cliente | Legal Entity | Idioma | LOC de templates |
|---------|-------------|--------|-----------------|
| Sondel/Marluvas | SONDEL-BR | PT-BR | LOC_SVC_PT |
| Tecmater | TECMATER-CR | ES | LOC_SVC_ES |
| [Futuro cliente EN] | — | EN | LOC_SVC_EN [por crear] |

- Detección: por legal_entity_id → idioma configurado en LegalEntity.
- El IA responde SIEMPRE en el idioma del cliente.
- Ref → ENT_PLAT_I18N para reglas generales de idioma.

---

## E. Notificaciones proactivas

[PENDIENTE — requiere AI Middleware (ENT_PLAT_KNOWLEDGE.F) + event bus (Redis Streams) operativos]

**Concepto:** el sistema notifica al cliente cuando el estado de su expediente cambia, sin que el cliente pregunte.

**Transiciones candidatas a notificación:**

| Transición | Mensaje tipo | Canal sugerido |
|-----------|-------------|---------------|
| PRODUCCION → PREPARACION | "Su pedido salió de producción" | WhatsApp / Email |
| DESPACHO → TRANSITO | "Su carga fue embarcada. Tracking: [X]" | WhatsApp / Email |
| TRANSITO → EN_DESTINO | "Su carga llegó a [destino]" | WhatsApp / Email |

**Decisiones pendientes CEO:**
- ¿Cuáles transiciones notificar? ¿Todas las candidatas o solo algunas?
- ¿Por cuál canal? ¿El preferido del cliente o todos los configurados?
- ¿Con qué frecuencia máxima? (evitar spam)

Ref → ENT_OPS_STATE_MACHINE (FROZEN) para transiciones canónicas. No se proponen cambios a la state machine.
Ref → ENT_PLAT_KNOWLEDGE.F (AI Middleware) como dependencia técnica.

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Fix error 500 en /api/knowledge/ask/ | Técnico | Portal B2B (P1) operativo |
| Z2 | Carga inicial de .md en pgvector | Técnico | Respuestas de knowledge base |
| Z3 | Setup WhatsApp Business API (Meta) | Integración | Canal P2 |
| Z4 | Tabla client_whatsapp_numbers | Backend | Auth WhatsApp |
| Z5 | Inbox dedicado + n8n flow para email | Integración | Canal P3 |
| Z6 | Decisión CEO: notificaciones proactivas | Decisión | Sección E |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v1.0 (2026-03-15): creación. 4 canales definidos (Portal P1, WhatsApp P2, Email P3, Teléfono fallback). Flujo unificado. Mapeo identidad por canal. Idioma por cliente. Notificaciones proactivas PENDIENTE. Iteración Claude↔Perplexity aprobada.
