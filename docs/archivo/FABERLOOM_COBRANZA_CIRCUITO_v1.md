# FABERLOOM — CIRCUITO CERRADO: COBRANZA B2B
## Aplicación operativa del Marco Rector · v1.0 · 2026-04-15

---

## 1. DEFINICIÓN EXACTA DEL CASO DE USO

**Usuario principal:** Responsable de cartera o vendedor que administra la relación con el cliente. No es un especialista de cobranza. Es la persona que conoce al cliente, lleva la cuenta y tiene que cobrar sin romper la relación.

**Destinatario externo:** Contacto de pagos del cliente deudor. Puede ser el mismo que compró, puede ser un área de cuentas por pagar, puede ser el dueño de la PYME. El contacto correcto no siempre es obvio ni estable.

**Trigger típico:** Factura vencida. Tres umbrales que generan comportamientos distintos del sistema:
- T1: 1–15 días vencida → recordatorio
- T2: 16–45 días → solicitud formal
- T3: 45+ días → escalación o acuerdo de pago

El trigger puede ser automático (el sistema detecta la mora) o manual (el usuario abre el caso directamente).

**Output principal:** Borrador de email de cobranza adaptado a la etapa de mora, al historial del cliente, al perfil del contacto y al estilo del usuario. Listo para revisar y aprobar — no para enviar automáticamente.

**Riesgo principal si el sistema falla:**
- Tono incorrecto con un cliente que va a pagar → daño relacional innecesario
- Datos desactualizados (cliente ya pagó) → email de cobranza a cliente al día → pérdida de credibilidad
- Contacto equivocado → el email llega a quien no corresponde → fuga de información financiera sensible
- Oferta de acuerdo de pago fuera del rango autorizado → compromiso financiero no aprobado

**Valor concreto para el usuario:** Preparar el email correcto para el caso correcto en menos de 3 minutos, sin tener que recordar qué se le dijo a este cliente la última vez, sin tener que buscar cuánto debe ni desde cuándo, y sin miedo de escribir algo que dañe la relación o comprometa algo que no debería.

---

## 2. QUÉ PARTES DEL MARCO RECTOR ENTRAN EN ESTE CIRCUITO

| Sección | Decisión | Justificación |
|---------|----------|---------------|
| 1. Knowledge Engine | **Indispensable** | Sin política de cobranza y condiciones de crédito estructuradas, el skill no tiene fuente de verdad. El primer chunk que falle aquí contamina todos los borradores. |
| 2. Ingestión y Taxonomía | **Simplificada** | Solo 4–5 documentos relevantes entran en v1. No se necesita el sistema de ingestión completo. El admin carga los documentos manualmente con tipo y visibilidad. Gate simplificado. |
| 3. Policy Engine | **Indispensable** | Datos de deuda de un cliente no pueden aparecer en outputs para otros usuarios. El monto, las condiciones especiales y el historial de pago son INTERNAL. Esto no se puede simplificar sin romper visibilidad. |
| 4. Skills / Playbooks | **Indispensable** | El skill de cobranza es el núcleo del caso. Sin él, el sistema genera texto genérico. Esta es la sección que más trabajo requiere en v1. |
| 5. Context Engine | **Indispensable** | El contexto del cliente (monto, días de mora, historial, último contacto) es lo que hace que el borrador sea útil y no genérico. Sin contexto, el skill no puede diferenciar entre un cliente que siempre paga tarde y uno que está en problemas. |
| 6. Perfil Operativo Personal | **Simplificada** | En v1: 3 parámetros fijos (formalidad, longitud, saludo preferido). Sin aprendizaje automático todavía — se configura manualmente en onboarding. El aprendizaje automático viene cuando hay suficientes pares aprobados. |
| 7. Output Engine | **Indispensable** | El ciclo borrador → aprobación → memoria es el mecanismo de valor. Sin él, los borradores aprobados se pierden y el sistema no mejora. |
| 8. Voice Layer | **Simplificada** | En v1: solo aplica el perfil de usuario (parámetros básicos). El perfil de contacto es manual (el usuario puede anotar "este cliente prefiere mensajes cortos"). Aprendizaje de perfil de contacto viene en v2. |
| 9. Nightly Engine | **Simplificada** | En v1: solo procesa señales de este caso de uso. No hace propuestas de cambio al Knowledge Engine. Solo reporta métricas, detecta posibles desactualizaciones y sugiere recalibración del skill si la tasa de edición supera el umbral. |
| 10. Channel Surfaces | **Simplificada** | En v1: solo email vía IMAP APPEND. Un canal, bien hecho. |

**Fuera de scope para este caso:** No hay combinación de skills. No hay WhatsApp. No hay portal externo. No hay licitaciones ni compliance cruzado. La complejidad del marco existe — simplemente no la activas para este caso.

---

## 3. FLUJO EXTREMO A EXTREMO

### Paso 0 — Trigger de la cobranza

**Qué pasa:** El sistema detecta una factura vencida (polling diario contra los datos cargados) o el usuario abre manualmente un caso de cobranza.

**Entradas:**
- ID de factura o cliente
- Días de mora actuales
- Canal desde donde llega el trigger (automático o manual)

**Salidas:**
- DebtCase abierto o actualizado
- Notificación al usuario responsable
- Etapa de cobranza asignada (T1/T2/T3)

**Validación:** Verificar que el caso no esté marcado como "en litigio" o "no contactar". Si lo está → bloquear y notificar.

---

### Paso 1 — Recuperación de contexto

**Qué pasa:** El Context Engine recupera todo lo relevante sobre este caso específico.

**Entradas:**
- DebtCase ID
- Contact ID (contacto de pagos)
- Organization ID (cliente deudor)

**Salidas:**
```
ContextPackage {
  deuda: {
    facturas: [{ id, monto, fecha_vencimiento, dias_mora, estado }],
    total_vencido: decimal,
    etapa: T1 | T2 | T3
  },
  historial_pago: {
    promedio_dias_demora_historico: int,
    veces_vencido_ultimo_año: int,
    ultimo_pago_fecha: date,
    comportamiento_clasificado: "puntual" | "tardio_habitual" | "irregular" | "sin_historial"
  },
  comunicaciones_previas: [{ fecha, tipo, resumen, resultado }],
  notas_manuales: string[],
  estado_relacion_comercial: "activa" | "en_pausa" | "en_riesgo"
}
```

**Validación:**
- ¿Los datos de factura tienen menos de 24h de antigüedad? Si no → warning de frescura
- ¿El contacto de pagos está verificado? Si no → advertencia al usuario antes de generar
- ¿Hay comunicaciones previas en los últimos 7 días? Si sí → incluir en contexto y ajustar tono

---

### Paso 2 — Consulta al Knowledge Engine (vía Policy Engine)

**Qué pasa:** El Policy Engine determina qué chunks del Knowledge Engine pueden inyectarse para este usuario generando un borrador para este destinatario.

**Entradas:**
- Usuario: rol de responsable de cartera
- Destinatario: externo (cliente)
- Tipo de output: email de cobranza

**Chunks autorizados para inyección:**
- Política de crédito y plazos (INTERNAL → autorizado para generar borrador interno)
- Scripts de cobranza por etapa (INTERNAL → autorizado)
- Condiciones de acuerdo de pago dentro del rango estándar (INTERNAL → autorizado con límite)

**Chunks excluidos:**
- Márgenes del cliente (CEO-ONLY → fuera de vectores, no disponible)
- Condiciones especiales negociadas individualmente (CEO-ONLY o PARTNER_B2B según caso)
- Historial de mora de otros clientes (INTERNAL de otro caso → no inyectable en este contexto)

**Registro:** El Policy Engine loguea qué fue excluido y por qué. Este log es inmutable.

---

### Paso 3 — Aplicación del Skill de Cobranza

**Qué pasa:** El skill recibe el ContextPackage + los chunks autorizados y razona sobre el caso.

**Entradas:**
- ContextPackage del paso 1
- Chunks autorizados del paso 2
- Etapa de mora (T1/T2/T3)
- Comportamiento histórico del cliente

**Razonamiento del skill:**

```
SI etapa = T1 Y comportamiento = "puntual":
  → tono: recordatorio amable, asumir que fue un olvido
  → oferta: solo confirmación de recepción de factura
  → no mencionar consecuencias todavía

SI etapa = T1 Y comportamiento = "tardio_habitual":
  → tono: directo pero no agresivo
  → incluir referencia a patrón sin decirlo explícitamente ("queremos asegurarnos de que llegó")
  → ofrecer confirmar fecha de pago

SI etapa = T2 (independiente del historial):
  → tono: formal, claro en la urgencia
  → mencionar monto exacto y días de mora
  → ofrecer plan de pago dentro del rango estándar si el monto supera umbral
  → requerir confirmación de fecha comprometida

SI etapa = T3:
  → tono: firme, sin amenazas legales (requieren autorización)
  → escalar internamente si el monto supera umbral de escalación
  → no generar borrador de promesa de acuerdo sin autorización

SI comportamiento = "sin_historial":
  → tono conservador, no asumir mala fe
  → priorizar verificar recepción de factura antes de reclamar pago
```

**Salidas del skill:**
- Intención del borrador (qué está intentando lograr este email)
- Contenido estructurado (apertura, cuerpo, cierre, call to action)
- Campos usados del contexto (trazabilidad)
- Gaps identificados (qué contexto faltó)
- Confianza estimada: ALTA / MEDIA / BAJA (basada en cobertura de contexto)
- Flags: acuerdo_de_pago_requerido, escalacion_requerida, contacto_no_verificado

---

### Paso 4 — Ajuste de Voz

**Qué pasa:** La Voice Layer aplica el perfil del usuario sobre el output del skill.

**Entradas:**
- Output del skill
- Parámetros del perfil del usuario: formalidad (1–10), longitud_preferida (corto/medio/largo), saludo, cierre
- Notas de contacto si existen ("este cliente prefiere mensajes sin rodeos")

**Salidas:**
- Borrador con voz aplicada
- Parámetros de voz usados (para auditoría)

**Restricción:** La Voice Layer no puede modificar el contenido sustantivo (monto, fecha, call to action). Solo puede modificar la forma expresiva.

---

### Paso 5 — Presentación al usuario para aprobación

**Qué pasa:** El Output Engine presenta el borrador al usuario con toda la información necesaria para que pueda aprobarlo con confianza.

**Lo que ve el usuario:**
```
BORRADOR DE COBRANZA — [Cliente] — Factura #[N]
Monto vencido: $[X]
Días de mora: [N] — Etapa: T2
Último contacto: [fecha] — [resumen]
Confianza del sistema: ALTA
Fuentes usadas: Política de crédito v2.1, Script T2 estándar
Gaps: ninguno

--- BORRADOR ---
[Texto del email]
---

[APROBAR] [EDITAR] [RECHAZAR] [ESCALAR]
```

**Validaciones antes de mostrar:**
- Si confianza = BAJA → mostrar advertencia clara antes del borrador
- Si flag escalacion_requerida → bloquear botón APROBAR, mostrar solo ESCALAR
- Si flag contacto_no_verificado → advertencia prominente sobre el destinatario

---

### Paso 6 — Aprobación humana

**Qué pasa:** El usuario toma una decisión.

**Opciones:**
- APROBAR → pasa al paso 7
- EDITAR y APROBAR → guarda el diff como señal de aprendizaje, pasa al paso 7
- RECHAZAR → pide razón (opcional), archiva el borrador, cierra el caso o abre nuevo intento
- ESCALAR → notifica al rol con autoridad, el caso queda en estado PENDIENTE_ESCALACIÓN

**Registro:** Quién aprobó, cuándo, qué versión del borrador, qué fue editado. Inmutable.

---

### Paso 7 — Entrega al canal

**Qué pasa:** El email aprobado se prepara y se entrega vía IMAP APPEND a la carpeta Drafts del servidor del usuario.

**Entradas:**
- Borrador aprobado
- Cuenta de email del usuario (credenciales del Credential Vault)
- Dirección del destinatario (verificada en el paso de contexto)

**Proceso:**
1. Conectar al servidor IMAP del usuario
2. Construir el email con headers correctos (Message-ID, In-Reply-To si es reply de un thread existente)
3. IMAP APPEND a la carpeta Drafts
4. Confirmar éxito o reportar error

**Resultado:** El email aparece en la bandeja de Drafts del usuario. El usuario lo envía. FaberLoom no envía.

---

### Paso 8 — Registro como memoria aprobada

**Qué pasa:** El Output Engine convierte el par (borrador generado → versión aprobada) en memoria.

**Entradas:**
- Borrador original del skill
- Versión aprobada por el usuario (con o sin ediciones)
- Metadatos: cliente, etapa de mora, comportamiento histórico, confianza del sistema

**Proceso:**
1. Calcular diff entre borrador original y versión aprobada
2. Clasificar el tipo de edición: estilo / contenido / corrección_de_hecho / ninguna
3. Guardar el par como ApprovedPair con metadata completa
4. Actualizar el perfil de voz del usuario con la señal (si la edición fue de estilo)
5. Generar señal para el Nightly Engine (si la edición fue de contenido o corrección)

---

### Paso 9 — Señales para mejora nocturna

**Qué pasa:** Se registran todas las señales del caso para que el Nightly Engine las procese.

**Señales generadas:**
- Tipo de edición y magnitud
- Chunks usados vs. chunks disponibles (retrieval effectiveness)
- Gaps reportados por el skill
- Flags activados (escalación, acuerdo, contacto no verificado)
- Resultado del caso si el usuario lo actualiza (¿pagó? ¿no respondió? ¿prometió fecha?)

---

## 4. KNOWLEDGE PACK MÍNIMO PARA ESTE CASO

### Conocimiento canónico (indispensable antes de activar el skill)

| Documento | Qué contiene | Visibilidad | Formato mínimo |
|-----------|-------------|-------------|---------------|
| Política de crédito y plazos | Días de crédito estándar, proceso de aprobación de excepciones, umbrales de escalación | INTERNAL | 1–2 páginas, claro y sin ambigüedad |
| Umbrales de autorización para acuerdos de pago | Qué rango puede ofrecer un vendedor sin autorización, qué requiere gerencia | INTERNAL (con sección CEO-ONLY para los montos exactos) | Tabla simple |
| Política de "no contactar" | Criterios para marcar un caso como intocable (litigio, acuerdo especial) | INTERNAL | Lista de criterios |

### Conocimiento por función (scripts de cobranza)

| Documento | Qué contiene | Visibilidad |
|-----------|-------------|-------------|
| Scripts T1 / T2 / T3 | Estructura de email por etapa, qué ofrecer, qué no decir, ejemplos aprobados | INTERNAL |
| Guía de situaciones especiales | Cómo tratar cliente nuevo vs. cliente histórico, cómo manejar "ya pagué" sin confirmación | INTERNAL |

### Skill experto (configurado, no un documento)
Ver Sección 6.

### Contexto del caso (dinámico, no pre-cargado)
- Datos de factura(s) vencida(s)
- Historial de pagos del cliente
- Comunicaciones previas con este contacto
- Notas manuales del usuario

### Perfil operativo personal (configurado en onboarding)
- 3 parámetros: formalidad (1–10), longitud (corto/medio/largo), saludo y cierre preferidos
- En v1 se configura manualmente. No aprende automáticamente todavía.

### Perfil de contacto (manual en v1)
Campo de texto libre por contacto: "Contacto de pagos. Prefiere mensajes directos y cortos. Responde bien cuando se incluye número de factura en el asunto."

### Plantillas base (opcionales pero recomendadas)
2–3 emails reales de cobranza que el usuario ha enviado antes y que considera buenos. El sistema los usa como few-shot, no como templates fijos.

---

## 5. MODELO DE DATOS MÍNIMO

### DebtCase
Qué representa: la cobranza abierta para un cliente específico. Puede agrupar múltiples facturas.

```
DebtCase {
  id: uuid
  organization_id: FK → Organization       // el cliente deudor
  assigned_user_id: FK → User              // el responsable de la cobranza
  status: open | in_escalation | resolved | blocked
  current_stage: T1 | T2 | T3
  total_overdue_amount: decimal
  oldest_invoice_days: int                  // días de mora de la factura más antigua
  last_contact_date: date | null
  notes: string                            // notas manuales del usuario
  created_at: timestamp
  updated_at: timestamp
}
```

Relaciones: tiene muchas Invoice, tiene muchos Draft, tiene muchos Communication, tiene un ContactProfile (el de pagos de este cliente).

---

### Invoice
Qué representa: una factura específica en mora.

```
Invoice {
  id: uuid
  debt_case_id: FK → DebtCase
  invoice_number: string
  amount: decimal
  due_date: date
  days_overdue: int                        // calculado diariamente
  status: overdue | paid | disputed | in_agreement
  payment_confirmed_at: timestamp | null
}
```

---

### Contact
Qué representa: el contacto de pagos del cliente deudor (puede cambiar).

```
Contact {
  id: uuid
  organization_id: FK → Organization
  name: string
  email: string
  role: string                            // "Cuentas por Pagar", "Gerente", etc.
  verified: boolean                        // ¿el usuario confirmó que es el correcto?
  is_primary_for_collections: boolean
  do_not_contact: boolean                  // flag de bloqueo
  do_not_contact_reason: string | null
}
```

---

### ContactProfile
Qué representa: lo que el sistema sabe sobre cómo comunicarse con este contacto específico.

```
ContactProfile {
  id: uuid
  contact_id: FK → Contact
  manual_notes: string                    // texto libre del usuario
  preferred_length: short | medium | long | null
  formality_observed: int | null          // 1-10, inferido de pares aprobados
  best_time_to_contact: string | null
  response_rate: float | null             // % de emails que generaron respuesta
  version: int
  updated_at: timestamp
}
```

---

### UserProfile
Qué representa: el perfil operativo del usuario cobrador.

```
UserProfile {
  id: uuid
  user_id: FK → User
  formality: int                          // 1-10
  preferred_length: short | medium | long
  preferred_greeting: string
  preferred_sign_off: string
  few_shot_examples: ApprovedPair[]       // los más representativos
  version: int
  updated_at: timestamp
}
```

---

### KBChunk
Qué representa: una pieza de conocimiento del Knowledge Engine.

```
KBChunk {
  id: uuid
  content: text
  type: canonical | skill | script | policy
  domain: collections                     // para este caso
  visibility: INTERNAL | CEO_ONLY | etc.
  status: active | draft | archived
  valid_from: date
  valid_until: date | null
  version: int
  in_vector_index: boolean               // false si CEO_ONLY
  created_by: FK → User
  last_validated_at: timestamp
}
```

---

### Draft
Qué representa: un borrador generado para un DebtCase.

```
Draft {
  id: uuid
  debt_case_id: FK → DebtCase
  invoice_ids: uuid[]                     // facturas incluidas en el borrador
  contact_id: FK → Contact
  generated_by_skill: string             // "collections_skill_v1"
  skill_confidence: HIGH | MEDIUM | LOW
  chunks_used: uuid[]                    // FK → KBChunk[]
  chunks_excluded: { chunk_id, reason }[]
  context_freshness_hours: int           // antigüedad del contexto en horas
  gaps_reported: string[]
  flags: {
    escalation_required: boolean,
    payment_plan_offered: boolean,
    contact_not_verified: boolean
  }
  content_original: text                 // lo que generó el skill
  content_final: text | null             // lo que aprobó el usuario (si editó)
  status: pending | approved | rejected | escalated | expired
  created_at: timestamp
}
```

---

### Approval
Qué representa: el registro inmutable de la decisión sobre un borrador.

```
Approval {
  id: uuid
  draft_id: FK → Draft
  user_id: FK → User
  decision: approved | rejected | escalated
  edit_type: none | style | content | fact_correction
  edit_distance_pct: float               // % del texto que cambió
  rejection_reason: string | null
  approved_at: timestamp
}
```

---

### ApprovedPair
Qué representa: el par de aprendizaje generado de cada aprobación.

```
ApprovedPair {
  id: uuid
  approval_id: FK → Approval
  debt_case_id: FK → DebtCase
  stage: T1 | T2 | T3
  client_behavior: puntual | tardio_habitual | irregular | sin_historial
  input_context_summary: text            // resumen del contexto usado
  output_original: text
  output_approved: text
  edit_type: none | style | content | fact_correction
  used_for_few_shot: boolean
  created_at: timestamp
}
```

---

### NightlySignal
Qué representa: una señal del día para que el Nightly Engine procese.

```
NightlySignal {
  id: uuid
  signal_type: edit_content | edit_style | gap_reported | low_confidence | escalation | context_stale
  source_draft_id: FK → Draft
  source_approval_id: FK → Approval | null
  payload: jsonb                         // detalles de la señal
  processed: boolean
  created_at: timestamp
}
```

---

## 6. SKILL PRINCIPAL DEL CASO

### Skill: Collections (Cobranza B2B)

**Qué sabe:**
- Los tres estadios de mora y su lógica de escalación (de la política de crédito)
- Qué ofrecer en cada estadio sin exceder el rango de autorización
- Cómo tratar distintos perfiles de comportamiento de pago
- Qué nunca debe prometer sin autorización (acuerdos fuera de rango, condonaciones, acciones legales)
- Que la relación comercial tiene valor más allá de la deuda y que debe preservarse si hay historial positivo

**Fuentes (en orden de prioridad):**
1. Política de crédito y plazos (INTERNAL, canónica) — fuente de verdad sobre umbrales
2. Scripts T1/T2/T3 (INTERNAL, por función) — estructura y lenguaje validado
3. Guía de situaciones especiales (INTERNAL) — manejo de edge cases
4. ContextPackage del caso — estado actual del cliente
5. ApprovedPairs anteriores del mismo usuario y etapa (si existen) — few-shot

**Qué puede sugerir:**
- Recordatorio de deuda con tono calibrado según etapa e historial
- Solicitud de confirmación de recepción de factura
- Oferta de fecha comprometida de pago
- Oferta de plan de pago dentro del rango estándar (si está en política)
- Solicitud de actualización de contacto de pagos si el actual no responde

**Qué nunca decide:**
- Ofrecer acuerdo fuera del rango estándar → siempre escala
- Condonar deuda (ni parcialmente) → bloquea y escala
- Mencionar acción legal → bloquea y escala
- Confirmar que la deuda fue perdonada o está en disputa sin que el sistema lo confirme
- Elegir un contacto sin verificación cuando hay ambigüedad

**Salidas:**
- IntentStatement: qué está intentando lograr este email (1 oración)
- DraftContent: apertura + cuerpo + call_to_action + cierre
- FieldsUsed: qué campos del contexto usó
- GapsReported: qué le faltó
- ConfidenceLevel: HIGH / MEDIUM / LOW con razón
- Flags: escalation_required, payment_plan_offered, contact_not_verified

**Cómo aprende:**
- Cada ApprovedPair del tipo fact_correction → señal fuerte: la fuente de verdad puede estar mal o el skill la está leyendo mal → NightlySignal para propuesta de revisión
- Cada ApprovedPair del tipo content → señal media: el skill no leyó bien el contexto o aplicó mal el script
- Cada ApprovedPair del tipo style → señal débil para el skill, fuerte para el perfil de usuario
- Patrón de 5+ señales del mismo tipo en la misma etapa → propuesta de recalibración del skill

**Señales de que está mal calibrado:**
- Tasa de edición de tipo "content" > 40% en T1 → el skill está siendo demasiado agresivo para recordatorios
- Tasa de escalación de tipo "fact_correction" > 15% → la fuente de verdad tiene datos incorrectos o desactualizados
- Confidence = LOW en > 30% de los drafts → el contexto que llega es sistemáticamente incompleto
- Usuario rechaza (sin editar) > 25% de drafts de T2 → el script de T2 no está funcionando

---

## 7. LÓGICA DE VISIBILIDAD ESPECÍFICA

### Qué puede consultar el usuario (responsable de la cuenta)
- Todas las facturas vencidas de sus propios clientes asignados
- Historial de comunicaciones de sus propios clientes
- Scripts de cobranza (INTERNAL)
- Política de crédito nivel estándar (INTERNAL)
- Su propio perfil de usuario

### Qué puede usar el skill para construir respuesta (inyección autorizada)
- Todo lo anterior
- Umbrales de autorización estándar (INTERNAL)
- ApprovedPairs del mismo usuario (por seguridad, no de otros usuarios)
- Scripts y guías de situaciones especiales (INTERNAL)

### Qué puede recibir el destinatario externo (cliente deudor)
- El monto de su propia deuda
- Las fechas de vencimiento de sus propias facturas
- La solicitud de pago con el nivel de urgencia apropiado a la etapa
- Una oferta de plan de pago si está dentro del rango estándar y fue explícitamente aprobada por el usuario

### Qué NUNCA recibe el destinatario externo
- Condiciones de crédito de otros clientes
- Márgenes o condiciones especiales negociadas
- Información sobre el estado interno del expediente de cobranza de la empresa
- Umbrales de autorización internos ("podemos ofrecerte hasta X% de descuento")
- Cualquier indicación de que hay un sistema de IA generando la comunicación (salvo que la empresa decida comunicarlo explícitamente)

### Qué puede aprobar el usuario
- Cualquier borrador de T1 o T2 dentro del rango estándar
- Borradores de T3 que no incluyan amenazas legales ni acuerdos fuera de rango

### Qué requiere aprobación de nivel superior (no puede aprobar el usuario base)
- Cualquier acuerdo de pago fuera del rango estándar
- Cualquier comunicación que mencione acción legal
- Cualquier borrador de cliente en estado "en_riesgo" con monto > umbral de escalación

### Qué debe quedar fuera de vectores
- Márgenes por cliente (CEO-ONLY)
- Condiciones especiales negociadas individualmente (CEO-ONLY o PARTNER_B2B)
- Umbrales exactos de autorización (CEO-ONLY)
- Perfiles de contacto con información sensible de la relación (en índice separado con filtro de acceso)

---

## 8. DECLINE / FALLBACK / ESCALATION LOGIC

| Situación | Respuesta del sistema |
|-----------|----------------------|
| Datos completos, etapa clara, contacto verificado, confianza HIGH | **Genera normal.** Borrador completo sin advertencias. |
| Datos completos, pero contexto > 48h de antigüedad | **Genera con warning.** "Los datos de factura tienen más de 48 horas. Verifica que el estado siga siendo correcto antes de enviar." |
| Etapa T1 o T2, contacto no verificado | **Genera con advertencia prominente.** "El contacto de pagos para este cliente no ha sido verificado. Confirma el destinatario antes de aprobar." Botón de aprobación disponible pero requiere click adicional de confirmación. |
| Sin historial de pago del cliente | **Genera con gap reportado.** "No tengo historial de pago de este cliente. El borrador asume primera incidencia. Ajusta si conoces el comportamiento del cliente." |
| Comunicaciones previas en los últimos 5 días sin respuesta | **Genera con warning.** "Ya se envió comunicación el [fecha]. Si no ha habido respuesta, considera si es momento de escalar antes de enviar otro email." |
| Skill detecta que el monto supera umbral de acuerdo de pago | **Genera borrador sin oferta de acuerdo + flag escalar.** "Este monto supera el límite de acuerdo estándar. El borrador no incluye oferta de plan de pago. Para ofrecerlo, escala el caso." |
| Skill confidence = LOW (contexto insuficiente para razonar bien) | **Genera borrador incompleto + solicita contexto.** "No tengo suficiente información para generar un borrador confiable. Necesito: [lista de gaps]. Puedes completar la información o aprobar el borrador parcial con tus ajustes." |
| Cliente marcado como "no contactar" | **Bloquea.** No genera borrador. "Este cliente tiene restricción de contacto: [razón]. El caso debe gestionarse manualmente." |
| Cliente en litigio | **Bloquea.** "Este cliente tiene un caso legal activo. No se pueden generar comunicaciones de cobranza estándar. Contacta al área legal." |
| Comunicación implicaría acción legal (detectado por el skill) | **Bloquea el contenido específico.** Genera el borrador sin esa parte y escala: "La acción legal no puede incluirse en este borrador sin autorización. El caso ha sido marcado para revisión." |
| Usuario intenta forzar un acuerdo fuera de rango mediante instrucción manual | **Escala, no obedece.** "La instrucción excede el límite de acuerdo autorizado. Para proceder, necesito aprobación de [rol con autoridad]." |

---

## 9. UI MENTAL MÍNIMA DEL USUARIO

### Lo que el usuario ve

**Vista 1 — Bandeja de cobranzas (entrada al sistema)**
```
COBRANZAS PENDIENTES

Empresa A     $4,500     T2 · 28 días     ⚠️ Contacto no verificado
Empresa B     $1,200     T1 · 8 días      ✓ Listo para borrador
Empresa C     $18,000    T3 · 62 días     🔴 Requiere escalación
Empresa D     $890       T1 · 3 días      ✓ Listo para borrador

[Prioridad automática por: días de mora + monto + comportamiento histórico]
```

**Vista 2 — Caso de cobranza (al seleccionar un cliente)**
```
EMPRESA B — Factura #2847 — $1,200
Vencida hace 8 días | T1 | Comportamiento: puntual habitual
Contacto: Juan Pérez — cuentaspagar@empresab.com ✓ verificado
Último contacto: hace 45 días (cotización enviada)
Comunicaciones de cobranza previas: ninguna

[GENERAR BORRADOR]
```

**Vista 3 — Borrador generado (el momento más crítico)**
```
BORRADOR GENERADO

Para: Juan Pérez <cuentaspagar@empresab.com>
Asunto: Factura #2847 — Recordatorio de pago

--- PREVIEW DEL EMAIL ---
[Texto del borrador]
---

INFORMACIÓN DEL SISTEMA
Confianza: ● ALTA
Fuentes usadas: Política de crédito v2.1 · Script T1 · Historial del cliente
Contexto: Factura actualizada hace 3 horas
Gaps: ninguno
Notas del caso: [notas manuales del usuario si existen]

[APROBAR Y MOVER A DRAFTS]   [EDITAR]   [RECHAZAR]   [ESCALAR]
```

### Qué acciones toma el usuario
1. Revisar la bandeja de cobranzas pendientes (ordenada por prioridad)
2. Seleccionar un caso
3. Opcionalmente agregar notas antes de generar
4. Revisar el borrador + la información del sistema
5. Aprobar, editar, rechazar o escalar

### Señales de confianza que necesita ver
- Confianza del sistema (HIGH/MEDIUM/LOW con razón)
- Qué fuentes usó el sistema (para poder verificar si algo se ve raro)
- Antigüedad del contexto (para saber si los datos son frescos)
- Flags activos (advertencias específicas)
- Notas previas del caso (para recordar el contexto que él mismo anotó)

### Lo que NO debe ver
- El texto de los chunks inyectados (solo las fuentes usadas)
- Información de otros clientes
- Los parámetros internos del skill

---

## 10. SEÑALES DE APRENDIZAJE

### Aprendizaje del skill (requiere validación humana para aplicar)

| Señal | Tipo | Acción automática | Acción propuesta |
|-------|------|-------------------|-----------------|
| Edición de tipo fact_correction en un draft | Fuerte | Generar NightlySignal | Proponer revisión del chunk de origen |
| 5+ ediciones de tipo content en T1 en misma dirección | Fuerte | Generar NightlySignal | Proponer ajuste de script T1 |
| Confidence LOW en 30%+ de drafts del día | Media | Registrar patrón | Proponer revisión de qué contexto falta sistemáticamente |
| Escalación por motivo no previsto | Media | Registrar tipo de escalación | Proponer añadir ese tipo al manejo del skill |

### Aprendizaje del perfil operativo personal (automático dentro de threshold)

| Señal | Acción |
|-------|--------|
| 5+ ediciones de tipo style en la misma dirección (longitud, saludo) | Actualizar parámetro automáticamente si el cambio es consistente (mismo parámetro, misma dirección) |
| Usuario sobreescribe el saludo en 80%+ de los drafts aprobados | Proponer actualizar el saludo por defecto del perfil |

El perfil no actualiza automáticamente si la señal viene de menos de 5 eventos. No aprende de un solo caso.

### Aprendizaje del perfil de contacto (manual en v1)

En v1 el usuario actualiza manualmente las notas del contacto. El sistema no infiere automáticamente del perfil de contacto todavía. V2: inferencia automática de patrones de respuesta (si el sistema sabe cuándo respondió el email).

### Aprendizaje del retrieval (automático)

| Señal | Acción |
|-------|--------|
| Chunk X fue incluido en 20 drafts y el skill reportó que no fue útil en 18 | Proponer revisar la relevancia del chunk en el índice |
| Chunk Y no aparece en retrieval pero el usuario lo menciona en notas | Registrar como gap de retrieval para el Nightly Engine |

### Propuestas para el Nightly Engine (no automáticas)
- Ajuste de script si hay patrón de edición de contenido consistente
- Revisión de chunk si hay fact_correction recurrente
- Revisión del ranking de retrieval si hay chunks inutilizados o gaps frecuentes

---

## 11. NIGHTLY PROCESSING ESPECÍFICO PARA ESTE CASO

### Qué señales recoge
- Todos los NightlySignal del día con tipo relevante a cobranza
- Métricas del día: drafts generados, tasa de aprobación por etapa, tipos de edición, escalaciones
- Lista de DebtCases que no tuvieron actividad pero tienen mora > 15 días (candidatos a recordatorio automático de acción al usuario)
- Chunks usados y su tasa de utilidad (feedback implícito del retrieval)

### Qué recalcula automáticamente
- Prioridad de la bandeja de cobranzas (días de mora + monto + historial + tiempo sin acción)
- Estado de frescura del contexto por DebtCase (¿cuándo fue la última actualización de datos?)
- Métricas acumuladas del skill por etapa

### Qué propone (no aplica — presenta al admin en el reporte)
- Si tasa de edición de content en T1 > 40%: "El script de T1 puede estar siendo demasiado agresivo. Revisar y ajustar."
- Si hay 3+ fact_corrections en la misma semana: "La fuente de verdad [chunk X] puede estar desactualizada. Revisar vigencia."
- Si DebtCase de Empresa X no tuvo actividad en 10 días con mora > 30 días: "El caso de Empresa X lleva 10 días sin acción. ¿El responsable necesita una recordatorio?"

### Qué nunca toca
- Contenido de ningún chunk del Knowledge Engine
- Visibilidad de ningún chunk
- La definición del skill de cobranza
- Los ApprovedPairs ya registrados (son histórico inmutable)
- Perfiles de contacto (solo propone, no modifica)

### Qué reporta por la mañana (reporte específico para cobranza)

```
REPORTE NOCTURNO — COBRANZA B2B — [fecha]

ACTIVIDAD DEL DÍA
- Drafts generados: N | Aprobados sin edición: N (X%) | Editados: N | Rechazados: N
- Escalaciones: N | Bloqueados: N

ALERTAS DE CARTERA
- DebtCases sin actividad > 10 días: [lista con montos]
- DebtCases en T3 sin escalación formal: [lista]
- Contactos no verificados con mora > 15 días: [lista]

SEÑALES DEL SKILL
- Tasa de edición content en T1: X% [OK / ATENCIÓN si > 40%]
- Fact corrections detectadas: N [con descripción de qué fue corregido]
- Escalaciones por motivo no previsto: N [con descripción]

RETRIEVAL
- Chunks con baja utilidad detectados: [lista]
- Gaps frecuentes reportados: [descripción]

PROPUESTAS PENDIENTES (requieren decisión)
1. [propuesta específica con evidencia]
...
```

---

## 12. MÉTRICAS DEL CIRCUITO CERRADO

### M1 — Activación real
**Qué mide:** % de usuarios que, en sus primeros 7 días, generaron al menos 1 draft Y lo aprobaron.
**Por qué importa:** Completar el onboarding no es activación. Aprobar el primer draft es.
**Resultado bueno:** > 60%
**Resultado que indica que el caso no está listo:** < 35%. Causa probable: fricción en carga de datos de factura o knowledge pack incompleto.

### M2 — Tiempo a primer valor
**Qué mide:** Minutos desde que el usuario abre el primer DebtCase hasta que aprueba el primer draft.
**Por qué importa:** Si tarda más de 10 minutos, hay fricción en la generación o en la presentación del borrador.
**Resultado bueno:** < 5 minutos para un caso con datos completos
**Resultado que indica problema:** > 15 minutos. Causa probable: contexto incompleto que requiere mucha intervención manual del usuario.

### M3 — Tasa de aprobación sin edición por etapa
**Qué mide:** % de drafts aprobados exactamente como fueron generados, separado por T1/T2/T3.
**Por qué importa:** Es el proxy de calidad del skill por etapa.
**Resultado bueno:** T1 > 65%, T2 > 55%, T3 > 40% (T3 es naturalmente más variable)
**Resultado que indica problema:** T1 < 40%. El skill está calibrado incorrectamente para el segmento más simple.

### M4 — Tasa de edición significativa (content + fact_correction)
**Qué mide:** % de drafts donde el usuario cambió sustancialmente el contenido (no solo el estilo).
**Por qué importa:** Edición de contenido indica que el skill no entendió el caso o la fuente de verdad tiene errores.
**Resultado bueno:** < 15% de ediciones son de tipo content o fact_correction
**Resultado que indica problema:** > 30%. El knowledge pack está incompleto o desactualizado.

### M5 — Tiempo de preparación del borrador (generación técnica)
**Qué mide:** Segundos desde que el usuario solicita el borrador hasta que aparece en pantalla.
**Por qué importa:** Si tarda más de 10 segundos, la UX del flujo de aprobación se rompe.
**Resultado bueno:** < 8 segundos
**Resultado que indica problema:** > 20 segundos. Causa probable: retrieval lento o contexto demasiado grande.

### M6 — Recuperación útil de contexto
**Qué mide:** % de drafts donde el usuario no tuvo que agregar información de contexto manualmente que el sistema debería haber tenido.
**Por qué importa:** Si el usuario tiene que completar datos en cada draft, el sistema no está ahorrando trabajo.
**Resultado bueno:** > 80% de drafts con contexto completo sin intervención manual del usuario
**Resultado que indica problema:** < 60%. Los datos de factura no están siendo cargados correctamente o el Context Engine no los está recuperando bien.

### M7 — Errores por información incorrecta
**Qué mide:** Número de fact_corrections registradas por semana, especialmente si el usuario corrige el monto, el contacto o el estado de la deuda.
**Por qué importa:** Un error en el monto o en el destinatario de un email de cobranza destruye la confianza en el sistema instantáneamente.
**Resultado bueno:** 0 fact_corrections en monto o destinatario en el primer mes
**Resultado que indica problema:** Cualquier fact_correction en monto o destinatario. Investigar inmediatamente.

### M8 — Confianza del usuario (self-reported)
**Qué mide:** En la semana 2, pregunta directa al usuario: "¿Confías en que el sistema tiene los datos correctos de tus clientes?" (1–5).
**Por qué importa:** La métrica de aprobación puede estar alta porque el usuario aprueba sin leer. La confianza self-reported revela si el sistema se ganó la confianza real.
**Resultado bueno:** > 4/5 en semana 2
**Resultado que indica problema:** < 3/5. El sistema está generando pero el usuario no confía en lo que genera.

### M9 — Valor operativo real
**Qué mide:** % reducción en tiempo de preparación de comunicaciones de cobranza vs. baseline (self-reported en onboarding).
**Por qué importa:** Es la promesa de valor. Si no hay reducción medible, el sistema no vale el precio.
**Resultado bueno:** > 50% reducción en semana 4
**Resultado que indica problema:** < 20% reducción. El proceso de aprobación es tan lento que elimina el ahorro de la generación.

---

## 13. RIESGOS DEL PILOTO

### R1 — Cliente ya pagó pero el sistema no lo sabe
**Cómo se detecta:** El usuario aprueba el draft y cuando va a enviarlo descubre que el cliente pagó ayer. O peor: lo envía.
**Cómo se mitiga:** (1) Warning de frescura si los datos tienen > 24h. (2) Instrucción explícita en el onboarding: "antes de aprobar, verifica el estado de pago si hubo actividad reciente". (3) En v2: integración con el sistema de facturación para actualización en tiempo real.
**Daño si se escapa:** Pérdida de credibilidad con el cliente. Potencialmente daño relacional con un cliente que ya estaba al día. Difícil de recuperar en cuentas delicadas.

### R2 — Contacto equivocado
**Cómo se detecta:** El draft se dirige a la persona equivocada (el comprador en lugar del área de pagos, o un contacto que ya salió de la empresa).
**Cómo se mitiga:** Flag visible cuando el contacto no está verificado. Verificación obligatoria en el primer uso. Advertencia cuando el contacto tiene > 6 meses sin actualización.
**Daño si se escapa:** Información financiera del cliente llega a alguien no autorizado. Daño de confianza y posible problema legal.

### R3 — Tono demasiado agresivo para el historial del cliente
**Cómo se detecta:** El skill aplica T2 tone a un cliente con historial "puntual" que se atrasó por primera vez. El usuario lo nota y rechaza el draft o lo edita significativamente.
**Cómo se mitiga:** El skill tiene lógica de historial explícita. El parámetro "comportamiento_clasificado" es el atenuador. La tasa de edición por tipo de cliente es la métrica de detección.
**Daño si se escapa:** El cliente recibe un email agresivo que no corresponde a la relación. Posible ruptura de una cuenta valiosa por una deuda menor.

### R4 — Knowledge pack desactualizado
**Cómo se detecta:** Fact_corrections frecuentes en monto o en umbrales de autorización. El usuario edita el borrador con condiciones diferentes a las que la política dice.
**Cómo se mitiga:** Timestamp de vigencia en cada chunk. Warning si el chunk de política tiene > 30 días sin revisión. Fact_correction como señal fuerte al Nightly Engine.
**Daño si se escapa:** El sistema ofrece condiciones de pago que la empresa ya no puede dar, o aplica umbrales de escalación incorrectos.

### R5 — Aprendizaje contaminado por ediciones atípicas
**Cómo se detecta:** El usuario edita un draft por una razón excepcional (cliente especial, situación inusual) y el sistema aprende ese caso como si fuera la norma.
**Cómo se mitiga:** En v1 el aprendizaje de perfil solo ocurre después de 5+ señales consistentes. Un solo evento no cambia el perfil. El usuario puede marcar una aprobación como "caso especial, no aprender de esto".
**Daño si se escapa:** El skill empieza a generar drafts con el tono o contenido de un caso excepcional en casos normales.

### R6 — Demasiada fricción para aprobar
**Cómo se detecta:** El tiempo promedio de aprobación supera los 5 minutos. Los usuarios empiezan a aprobar sin leer (aprobación ciega).
**Cómo se mitiga:** La pantalla de aprobación debe ser escaneable en 30 segundos. Información clave arriba: monto, días, confianza, warnings. El texto del borrador abajo. No al revés.
**Daño si se escapa:** O el usuario no usa el sistema (demasiado lento) o lo usa mal (aprueba sin revisar, convirtiendo a FaberLoom en una fuente de errores automáticos).

### R7 — Fuente de verdad ambigua para el estado de la deuda
**Cómo se detecta:** El sistema dice que la factura está vencida pero el cliente tiene un acuerdo verbal con el vendedor que el sistema no conoce.
**Cómo se mitiga:** Campo de "notas manuales" visible y fácil de actualizar en el DebtCase. El skill siempre pregunta por notas del caso antes de generar si el caso tiene > 30 días de mora. Instrucción explícita: "antes de generar el borrador de un caso T3, revisa las notas del caso".
**Daño si se escapa:** El sistema genera un email de escalación para un cliente que ya tiene un acuerdo activo. Daño relacional significativo.

---

## 14. ALCANCE DE MVP ESTRICTO

### Sí construyo ya

- Carga manual de facturas vencidas por el usuario (CSV simple o entrada manual)
- Knowledge pack de cobranza: política de crédito + 3 scripts (T1/T2/T3) cargados como texto plano
- Skill de cobranza con lógica de 3 etapas y 4 comportamientos de cliente
- Generación de borrador con confidence score y chunks usados visibles
- Pantalla de aprobación con información del sistema visible
- IMAP APPEND a la carpeta Drafts del usuario (1 cuenta de email)
- Registro inmutable de aprobaciones
- ApprovedPairs básicos (sin inferencia automática todavía)
- Perfil de usuario: 3 parámetros configurables manualmente
- Bandeja de cobranzas ordenada por prioridad simple (días × monto)
- Nightly Engine mínimo: solo reporta métricas del día, no propone cambios al skill todavía

### Simplifico

- Perfil de usuario: solo configuración manual, sin aprendizaje automático. El aprendizaje viene en v2 cuando hay suficientes pares.
- Perfil de contacto: solo campo de notas manuales. Sin inferencia de patrón.
- Context Engine: solo datos cargados manualmente (factura, historial, notas). Sin integración ERP/CRM.
- Nightly Engine: solo reporte de métricas. Las propuestas de ajuste se hacen manualmente en las primeras semanas.
- Policy Engine: implementado como checklist de validación simple, no como motor de reglas complejo.

### Simulo manualmente

- Actualización del estado de deuda (¿el cliente pagó?): el usuario actualiza manualmente el estado de la factura. No hay polling automático contra el sistema de facturación.
- Integración con servidor de email para detectar respuestas del cliente: en v1, el usuario reporta si hubo respuesta. No es automático.
- Ranking de retrieval sofisticado: en v1 los chunks se pasan al skill en orden fijo. El retrieval semántico con pgvector viene en v2.

### Difiero

- Aprendizaje automático del perfil de usuario (v2)
- Perfil de contacto inferido de pares aprobados (v2)
- Retrieval semántico con pgvector (v2)
- Detección de respuestas del cliente en el thread de email (v2)
- Integración con sistema de facturación para actualización en tiempo real (v2)
- Nightly Engine con propuestas de ajuste al skill (v2)

### Elimino por completo (de este caso)

- WhatsApp para cobranza
- Portal externo para que el cliente vea su estado de cuenta
- Combinación de múltiples skills (cobranza + legal + compliance)
- Cobranza automatizada sin aprobación humana (eliminado permanentemente, no diferido)
- Dashboard de cartera con visualizaciones complejas (las métricas están en el reporte del Nightly Engine)

---

## 15. BLUEPRINT OPERATIVO FINAL

| Elemento | Definición |
|----------|-----------|
| **Caso de uso** | Preparación de comunicaciones de cobranza B2B — deuda vencida de clientes con relación comercial activa |
| **Usuario** | Responsable de cartera o vendedor que lleva la cuenta del cliente |
| **Output principal** | Email de cobranza en Drafts del servidor del usuario, listo para envío manual |
| **Knowledge mínimo requerido** | Política de crédito · Scripts T1/T2/T3 · Umbrales de autorización (sin montos CEO-ONLY inyectables) |
| **Skill principal** | Collections Skill — razona por etapa de mora + comportamiento histórico, con límites explícitos de lo que puede sugerir |
| **Política de visibilidad** | Datos de deuda: INTERNAL · Márgenes y condiciones especiales: CEO-ONLY fuera de vectores · El destinatario externo solo recibe lo que el borrador aprobado contiene |
| **Lógica de aprobación** | Aprobación humana explícita para todo output externo. Sin excepciones en v1. Usuario base aprueba T1/T2 estándar. T3 con acuerdo fuera de rango o acción legal: escala. |
| **Señales de aprendizaje** | Tipo de edición (style/content/fact_correction) → perfil de usuario o NightlySignal según tipo |
| **Nightly maintenance mínimo** | Reporte de métricas del día · Alertas de cartera sin actividad · Señales de skill para revisión manual |
| **Métricas clave** | Aprobación sin edición > 60% en T1 · Fact_corrections en monto = 0 · Tiempo a primer valor < 5 min · Reducción de tiempo de preparación > 50% en semana 4 |
| **Criterio "esto funciona"** | 3 usuarios activos en semana 2, tasa de aprobación > 50%, 0 errores de monto o destinatario, al menos 1 usuario reporta ahorro real de tiempo |
| **Criterio "esto no está listo"** | Cualquier error de monto o destinatario · Tasa de aprobación < 30% · Tiempo a primer valor > 20 minutos · Ningún usuario activo en semana 2 |

---

## 16. CRÍTICA BRUTAL FINAL

### Qué parte del Marco Rector demuestra su valor en este caso

**La jerarquía de herencia con regla de conflicto explícita.** En este caso de uso aparece varias veces: cuando el usuario intenta ofrecer un acuerdo fuera de rango, cuando el perfil de contacto diría "sé directo" pero el skill de T3 requiere un tono específico, cuando el historial del cliente atenúa la agresividad del script de T2. Sin una regla clara de qué capa gana, cada uno de esos casos se resuelve con inconsistencia. Con la jerarquía, se resuelven de forma determinista.

**El modelo de visibilidad de 4 dimensiones.** La distinción entre "quién puede consultar el monto de la deuda" y "qué puede recibir el destinatario externo" es exactamente la que protege que los umbrales internos de autorización o los márgenes negociados nunca aparezcan en el email. Esa distinción no es obvia y el marco la hace explícita.

### Qué parte del Marco Rector todavía sobra para este piloto

**El Nightly Engine en su versión completa.** Para el piloto, el Nightly Engine es un reporte de métricas y una lista de alertas. El ciclo completo de propuestas → validación → promoción → rollback es correcto arquitectónicamente pero es sobre-ingeniería para las primeras 4 semanas con 3–5 clientes de FaberLoom. El admin de esas empresas no va a tener un proceso de revisión matutina todavía.

**La taxonomía de ingestión completa.** Para cargar 5 documentos de cobranza, no necesitas un sistema de ingestión con gate, estados y changelog. Eso importa cuando la KB tiene 50+ documentos en múltiples dominios. En el piloto: el admin carga los documentos, los marca como activos, y listo.

### Qué parte del caso puede romper confianza rápidamente

**El error de "cliente ya pagó".** Es el riesgo más probable y el de mayor daño relacional. Ocurre cuando los datos de factura no se actualizan en tiempo real (que en v1 es lo esperado) y el usuario no verifica antes de aprobar. La mitigación (warning de frescura + instrucción explícita) no garantiza que no ocurra — solo reduce la probabilidad.

Si ocurre en los primeros 30 días del piloto, el usuario puede abandonar el sistema aunque el error sea de datos, no de producto. La narrativa que se instala es "el sistema me hizo quedar mal con un cliente". No hay recuperación fácil de esa narrativa.

**Acción concreta:** Antes de lanzar el piloto, acordar con el usuario piloto que actualizar el estado de pago de las facturas es su responsabilidad explícita. No dejarlo implícito. Que el sistema tiene los datos que el usuario le dio, y si esos datos cambiaron, el usuario debe actualizarlos antes de generar el borrador.

### Qué decisión concreta tomarías antes de escribir una sola línea de producto

**Conseguir 3 usuarios piloto reales con carteras de cobranza activas y sentarte a hacer el proceso manualmente con ellos — sin ninguna tecnología — por una semana.**

No para validar si les gusta la idea. Para entender exactamente qué información tienen disponible sobre sus deudores, dónde está esa información (Excel, su cabeza, el email), cómo deciden qué tono usar, qué les frena antes de enviar un email de cobranza, y cuánto tiempo les toma preparar uno.

Esa semana de observación va a cambiar el knowledge pack mínimo, el flujo de contexto y probablemente la UI mental. Sin ella, el sistema va a estar bien diseñado para el caso de uso imaginado, no para el caso de uso real.

---

*FABERLOOM — Circuito Cerrado: Cobranza B2B · v1.0 · 2026-04-15*
