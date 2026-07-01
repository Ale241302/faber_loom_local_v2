# FABERLOOM — PLAN DE CONSTRUCCIÓN: COBRANZA B2B
## Build Plan v1.0 · 2026-04-15

---

## 1. RESUMEN EJECUTIVO DE IMPLEMENTACIÓN

**Qué vamos a construir:**
Un sistema que toma datos de facturas vencidas de clientes B2B, recupera el contexto del caso (historial de pagos, comunicaciones previas, notas manuales), aplica el Collections Skill para generar un borrador de email calibrado por etapa y comportamiento, y lo deposita en la carpeta Drafts del servidor IMAP del usuario. El usuario revisa y aprueba. Nada sale sin su acción explícita.

**Qué NO vamos a construir todavía:**
- Integración con ERP o sistema de facturación externo
- Actualización automática del estado de pago
- Retrieval semántico con pgvector (chunks se pasan en orden fijo)
- Aprendizaje automático del perfil de usuario
- Perfil de contacto inferido (solo campo de notas manuales)
- Nightly Engine con propuestas de ajuste al skill
- WhatsApp, portal externo, chat interno
- Dashboard de cartera con visualizaciones

**Hipótesis principal del piloto:**
Si el sistema presenta un borrador de cobranza con el contexto correcto del caso, el confidence score visible y los chunks usados, el usuario lo aprobará sin editar en más del 60% de los casos y la preparación tomará menos de 5 minutos, frente a los 15–30 minutos actuales.

**Qué debe demostrarse para declarar el circuito exitoso:**
1. 3 usuarios activos en semana 2 (aprobaron al menos 1 draft)
2. 0 errores de monto o destinatario en el primer mes
3. Tasa de aprobación sin edición ≥ 50% en T1
4. Al menos 1 usuario reporta ahorro real de tiempo medible
5. El flujo completo (entrada → draft en Drafts) funciona sin intervención técnica manual

---

## 2. PRODUCT SLICE EXACTO

| Elemento | Definición |
|----------|-----------|
| **Usuario principal** | Responsable de cartera o vendedor con cuentas asignadas. No es especialista de cobranza. Conoce al cliente y lleva la relación. |
| **Caso exacto** | Factura B2B vencida con cliente activo y relación comercial existente. No clientes nuevos sin historial. No clientes en litigio. |
| **Trigger principal** | Manual: el usuario abre un caso de cobranza desde la bandeja. El sistema no inicia comunicaciones por sí solo. |
| **Output principal** | Email de cobranza en la carpeta Drafts del servidor IMAP del usuario, listo para envío manual. |
| **Fuente de verdad mínima** | Datos de factura cargados manualmente + política de crédito + scripts T1/T2/T3 como texto plano. Nada más. |
| **Canal único** | Email vía IMAP APPEND. Un solo canal. Una sola cuenta por usuario en v1. |
| **Interacción mínima del usuario** | (1) Abrir el caso. (2) Confirmar que el contacto es correcto. (3) Revisar el borrador. (4) Aprobar o editar y aprobar. Eso es todo. |

**Qué queda explícitamente fuera del slice:**
- Generación de borradores automática sin que el usuario abra el caso
- Envío de email desde FaberLoom (el usuario envía desde su cliente de email)
- Cobranza a clientes nuevos sin historial en el sistema
- Casos con litigio activo o restricción de contacto (bloqueados, no procesados)
- Múltiples cuentas de email por usuario
- Cobranza a personas naturales (solo B2B en v1)
- Seguimiento del resultado (¿pagó el cliente?) — el usuario actualiza manualmente

---

## 3. UX FLOW REAL DEL MVP

---

### Pantalla 1 — Bandeja de Cobranzas

**Propósito:** Vista principal. Mostrar todos los DebtCases activos del usuario ordenados por prioridad.

**Datos visibles:**
- Nombre del cliente
- Monto total vencido
- Días de mora de la factura más antigua
- Etapa actual (T1 / T2 / T3)
- Último contacto (fecha)
- Badge de estado: `Listo` / `⚠️ Contacto no verificado` / `🔴 Escalar` / `🔒 Bloqueado`

**Acciones posibles:**
- Abrir un caso (click en la fila)
- Filtrar por etapa (T1/T2/T3)
- Marcar caso como resuelto (desde la bandeja, sin abrir)

**Validaciones:**
- Si el caso está BLOQUEADO: fila visible pero no abre el flujo de generación. Muestra el motivo del bloqueo.

**Errores posibles:**
- Sin casos en cartera: estado vacío con instrucción para cargar facturas.
- Error de conexión al cargar la bandeja: mensaje de error con opción de reintentar.

**Siguiente estado:** Apertura del caso (Pantalla 2)

---

### Pantalla 2 — Apertura del Caso

**Propósito:** Mostrar el estado completo del DebtCase antes de generar el borrador. El usuario verifica datos y decide si procede.

**Datos visibles:**

*Sección deuda:*
- Lista de facturas vencidas: número, monto, fecha de vencimiento, días vencidos
- Total vencido
- Etapa asignada (T1/T2/T3) con criterio visible ("T2: 28 días vencido")

*Sección contacto:*
- Nombre, email, rol del contacto de pagos
- Badge: `✓ Verificado` o `⚠️ No verificado`
- Botón: `[Editar contacto]`

*Sección historial:*
- Comportamiento clasificado: `Puntual habitual` / `Tardío habitual` / `Irregular` / `Sin historial`
- Último pago: fecha
- Comunicaciones de cobranza previas: lista resumida (fecha + tipo)

*Sección notas:*
- Notas manuales del usuario sobre este caso (campo editable)

*Sección frescura:*
- Última actualización de datos de factura: timestamp
- Warning si > 24h: "Los datos de factura tienen más de 24 horas. Verifica el estado antes de continuar."

**Acciones posibles:**
- `[Generar borrador]` — acción principal
- `[Editar contacto]` — abre modal de edición de contacto
- `[Agregar nota]` — agrega nota al caso
- `[Marcar como resuelto]` — cierra el caso sin generar borrador
- `[Bloquear caso]` — marca como no contactar con campo de razón obligatorio

**Validaciones:**
- Si contacto no verificado: warning amarillo persistente. El botón `[Generar borrador]` está disponible pero con texto "Generar igualmente (contacto no verificado)"
- Si caso BLOQUEADO: no muestra botón de generar. Solo muestra el motivo y opciones de gestión.
- Si factura marcada como "en disputa": warning rojo. Requiere confirmación explícita para continuar.

**Errores posibles:**
- Sin facturas activas en el caso: estado de error con instrucción de verificar datos cargados.

**Siguiente estado:** Generación del borrador (estado intermedio) → Pantalla 3

---

### Estado intermedio — Generando borrador

**Propósito:** Feedback visual mientras el sistema genera. Dura típicamente 3–8 segundos.

**Datos visibles:**
- Spinner o barra de progreso
- Texto: "Recuperando contexto del caso…" → "Aplicando política de cobranza…" → "Generando borrador…"
- No mostrar los chunks ni el razonamiento del skill en este momento

**Acciones posibles:** Ninguna (no cancelable en v1 — si hay error, se muestra en la pantalla siguiente)

**Errores posibles:**
- Timeout de generación (> 15s): error con opción de reintentar
- Knowledge pack incompleto detectado: navegar a pantalla de error con descripción del gap

---

### Pantalla 3 — Revisión y Aprobación del Borrador

**Propósito:** El momento más crítico del flujo. El usuario revisa el borrador con toda la información necesaria para decidir con confianza.

**Datos visibles:**

*Panel superior — contexto del sistema:*
- Confianza: `● ALTA` / `● MEDIA` / `● BAJA` (con color verde/amarillo/rojo)
- Si BAJA: expansible con razón: "Falta: [descripción del gap]"
- Fuentes usadas: "Política de crédito v2.1 · Script T2 estándar · 3 comunicaciones previas"
- Frescura del contexto: "Datos actualizados hace 3 horas"
- Flags activos: solo se muestran si hay alguno activo
  - `⚠️ Contacto no verificado`
  - `⚠️ Acuerdo de pago incluido — requiere verificación`
  - `🔴 Escalación recomendada`

*Panel principal — el borrador:*
- Asunto del email
- Texto completo del borrador (editable inline)

*Panel inferior — acciones:*
- `[APROBAR Y MOVER A DRAFTS]` — acción principal
- `[RECHAZAR]` — con campo de razón opcional
- `[ESCALAR]` — con campo de nota obligatorio

**Reglas de habilitación de botones:**
- Si flag `escalacion_requerida = true`: botón `[APROBAR]` está deshabilitado. Solo `[ESCALAR]` disponible. Texto explicativo visible.
- Si confianza = BAJA: `[APROBAR]` disponible pero requiere confirmación adicional: modal "El sistema tiene baja confianza en este borrador. ¿Confirmas que revisaste los datos?" con `[Sí, aprobar]` / `[Cancelar]`
- Si contacto no verificado: `[APROBAR]` requiere confirmación: modal "El contacto no ha sido verificado. ¿Confirmas que el destinatario es correcto?" con `[Sí, es correcto]` / `[Ir a verificar contacto]`

**Acciones posibles en el texto:**
- Edición inline del cuerpo del email
- Si el usuario edita: el sistema detecta automáticamente si el cambio es de estilo o de contenido (basado en diff)
- Edición del asunto

**Errores posibles:**
- Error al intentar aprobar: reintento automático 1 vez, luego error con opción manual

**Siguiente estado:** APPROVED → Entrega al canal (Pantalla 4) o REJECTED → vuelta a Pantalla 2 o ESCALATED → Pantalla de Escalación

---

### Pantalla 4 — Confirmación de Draft Entregado

**Propósito:** Confirmar que el borrador fue depositado en la carpeta Drafts del email del usuario.

**Datos visibles:**
- "✓ Borrador movido a tu carpeta Drafts"
- Destinatario confirmado
- Asunto del email
- Instrucción: "Ve a tu cliente de email y envíalo desde ahí cuando estés listo"
- Botón: `[Ver siguiente caso]` o `[Volver a la bandeja]`

**Si el IMAP APPEND falla:**
- Error claro: "No pudimos mover el borrador a tu carpeta Drafts. Aquí está el texto para que lo copies manualmente:"
- Texto copiable del borrador completo
- Instrucción para verificar la conexión IMAP

---

### Pantalla de Escalación

**Propósito:** Registrar la escalación y notificar al nivel correspondiente.

**Datos visibles:**
- Resumen del caso (cliente, monto, etapa)
- Motivo de escalación (sistema o usuario)
- Campo de nota para el escalador: "¿Qué necesitas que el nivel superior decida?"

**Acciones posibles:**
- `[Confirmar escalación]` — registra y notifica
- `[Cancelar]` — vuelve al borrador

**Siguiente estado:** DebtCase → ESCALATED. El caso sale de la bandeja del usuario y aparece en la bandeja del rol con autoridad (en v1: notificación por email al admin).

---

### Estado vacío — Sin casos en cartera

**Propósito:** Guiar al usuario cuando no hay DebtCases activos.

**Datos visibles:**
- "No tienes cobranzas pendientes"
- Botón: `[Cargar facturas]` (abre el flujo de carga manual)

---

### Estado de error — Knowledge Pack incompleto

**Propósito:** Informar al usuario que el sistema no puede generar porque falta conocimiento base.

**Datos visibles:**
- "El sistema no tiene la información necesaria para generar este borrador"
- Descripción del gap: qué documento específico falta
- Instrucción: "El administrador debe cargar [X] antes de poder generar borradores"

---

## 4. STATE MACHINE DEL DEBTCASE

### Estados

| Estado | Descripción |
|--------|-------------|
| `OPEN` | Caso activo, sin borrador generado o último borrador rechazado. Listo para acción. |
| `DRAFT_GENERATING` | El sistema está generando un borrador. Estado transitorio (máx. 30s). |
| `DRAFT_READY` | Borrador generado, esperando decisión del usuario. |
| `APPROVED` | Borrador aprobado. El sistema está intentando hacer IMAP APPEND. Estado transitorio. |
| `DRAFT_DELIVERED` | Borrador depositado en Drafts del email del usuario. Caso activo pero con acción pendiente del usuario (enviar). |
| `ESCALATED` | Caso escalado. No puede generar nuevos borradores hasta que el nivel superior lo devuelva o resuelva. |
| `BLOCKED` | No se puede contactar al cliente. No genera borradores. Solo gestión manual. |
| `RESOLVED` | Deuda saldada o caso cerrado manualmente. Sin acciones posibles. |
| `EXPIRED` | El borrador estuvo en DRAFT_READY o DRAFT_DELIVERED más de N días sin acción. El caso vuelve a OPEN. |

### Transiciones válidas

```
OPEN
  → DRAFT_GENERATING    [evento: usuario solicita borrador]
  → BLOCKED             [evento: usuario marca "no contactar"]
  → RESOLVED            [evento: usuario marca como resuelto]

DRAFT_GENERATING
  → DRAFT_READY         [evento: borrador generado exitosamente]
  → OPEN                [evento: error en generación — sistema revierte]

DRAFT_READY
  → APPROVED            [evento: usuario aprueba]
  → OPEN                [evento: usuario rechaza]
  → ESCALATED           [evento: usuario escala]
  → EXPIRED             [evento: N días sin acción — vuelve a OPEN con nota en historial]

APPROVED
  → DRAFT_DELIVERED     [evento: IMAP APPEND exitoso]
  → DRAFT_READY         [evento: IMAP APPEND falla — vuelve a mostrar borrador con error]

DRAFT_DELIVERED
  → RESOLVED            [evento: usuario marca como resuelto después del envío]
  → OPEN                [evento: usuario reabre el caso — cliente no respondió]
  → ESCALATED           [evento: usuario escala desde este estado]
  → EXPIRED             [evento: N días sin resolución — vuelve a OPEN con prioridad incrementada]

ESCALATED
  → OPEN                [evento: nivel superior devuelve el caso para que el usuario actúe]
  → RESOLVED            [evento: nivel superior resuelve directamente]
  → BLOCKED             [evento: nivel superior bloquea el caso]

BLOCKED
  → OPEN                [evento: admin remueve el bloqueo con razón documentada]
  → RESOLVED            [evento: admin resuelve el caso directamente]

RESOLVED → [terminal, no transita. Puede reabrirse solo por acción explícita del admin]
```

### Transiciones inválidas (explícitas)

- `BLOCKED → DRAFT_GENERATING` — nunca. El sistema no genera si el caso está bloqueado.
- `ESCALATED → DRAFT_GENERATING` — nunca sin que el nivel superior devuelva primero el caso.
- `RESOLVED → cualquier estado` — no automáticamente. Solo por acción explícita con razón documentada.
- `DRAFT_GENERATING → DRAFT_GENERATING` — no puede haber dos generaciones simultáneas del mismo caso.

### Side effects permitidos por transición

| Transición | Side effects |
|-----------|-------------|
| `OPEN → DRAFT_GENERATING` | Crea Draft record con status `generating` |
| `DRAFT_GENERATING → DRAFT_READY` | Actualiza Draft con contenido, confidence, chunks_used, flags |
| `DRAFT_READY → APPROVED` | Crea Approval record; calcula diff; registra NightlySignal |
| `APPROVED → DRAFT_DELIVERED` | IMAP APPEND; actualiza Draft con `delivered_at` |
| `DRAFT_READY → OPEN` (rechazo) | Registra Approval con `decision: rejected`; NightlySignal si el usuario dio razón |
| `cualquier → ESCALATED` | Notifica al rol con autoridad; registra razón |
| `cualquier → RESOLVED` | Actualiza todas las Invoice del caso a `status: resolved_by_user` |
| `DRAFT_READY/DELIVERED → EXPIRED` | Crea evento en historial; incrementa prioridad para el siguiente ciclo |

---

## 5. MODELO DE DATOS MVP ESTRICTAMENTE MÍNIMO

| Entidad | ¿Entra en MVP? | Por qué | Simplificación permitida | Riesgo si simplifico demasiado |
|---------|---------------|---------|--------------------------|-------------------------------|
| `Organization` | Sí — core | El cliente deudor es la entidad raíz. Sin ella no hay caso ni contacto. | Solo: id, name, status (active/blocked). Sin CRM fields. | Bajo — es solo un contenedor en v1 |
| `Contact` | Sí — core | El destinatario del email. Sin él no hay output. | Sin campos de enriquecimiento. Solo: id, org_id, name, email, role, verified, do_not_contact. | Alto si omites `do_not_contact` — puede enviarse email a cliente bloqueado |
| `Invoice` | Sí — core | La factura es el trigger del caso. Sin datos de factura el skill no puede razonar. | Sin integración externa. Solo: id, debt_case_id, number, amount, due_date, days_overdue (calculado), status. | Alto si omites `status` — no detectas facturas ya pagadas |
| `DebtCase` | Sí — core | El objeto central del flujo. | Simplificar `notes` a string. Sin historial de estado interno (solo estado actual + timestamp). | Medio — sin historial de estados puede haber ambigüedad en auditoría |
| `KBChunk` | Sí — core | Sin policy + scripts el skill no tiene fuente. | Sin vectorización en v1. Solo texto plano con tipo y visibilidad. Sin chunks_used como foreign key — como array de IDs en Draft. | Medio — sin chunks no hay trazabilidad de qué usó el sistema |
| `Draft` | Sí — core | El output del sistema. Sin él no hay ciclo de aprobación. | Simplificar flags a JSONB. Sin versioning de drafts — solo el último. | Alto si omites `content_original` — pierdes el diff para aprendizaje |
| `Approval` | Sí — core | El registro inmutable de la decisión. Sin él no hay trazabilidad ni aprendizaje. | Sin edit_distance exacto en v1 — solo `edit_type` (none/style/content/fact). | Medio — edit_distance exacto es v2; el tipo de edición es suficiente para v1 |
| `ApprovedPair` | Sí — core | Es el mecanismo de aprendizaje. Sin él las aprobaciones no producen valor acumulativo. | Sin indexación semántica todavía. Solo almacenamiento para few-shot futuro. | Bajo en v1 — se almacena pero no se usa todavía para retrieval automático |
| `UserProfile` | Sí — simplificado | Sin perfil no hay ajuste de voz. | Solo 3 campos: formality (int), preferred_length (enum), preferred_greeting + sign_off (string). Sin aprendizaje automático. | Bajo — en v1 el usuario lo configura manualmente; si falla, el borrador suena genérico pero es correcto |
| `ContactProfile` | Sí — simplificado | Sin notas del contacto el skill no puede adaptar el tono. | Solo campo `manual_notes: text`. Sin parámetros inferidos. Sin versioning. | Bajo — el riesgo es un borrador con tono incorrecto para el contacto, no un error de datos |
| `NightlySignal` | Sí — simplificado | Sin señales el Nightly Engine no puede reportar nada útil. | Solo: id, signal_type, source_draft_id, payload (JSONB), created_at, processed. Sin ciclo de estados complejo en v1. | Bajo — en v1 el Nightly Engine solo lee y reporta; no actúa |
| `PaymentAgreement` | No | No entra en MVP | — | — |
| `EscalationRecord` | Simplificado | Suficiente con campo `escalation_note` en DebtCase + estado ESCALATED | — | Bajo |
| `AuditLog` | Sí — pero mínimo | Toda acción externa necesita registro inmutable | Solo: entity_type, entity_id, action, user_id, timestamp, diff_summary. Una tabla genérica sirve. | Alto si se omite — sin audit trail no puedes depurar errores de contacto equivocado |

---

## 6. CONTRATOS FUNCIONALES ENTRE MÓDULOS

---

### Módulo 1 — Context Engine

**Input:**
```
{
  debt_case_id: uuid,
  user_id: uuid
}
```

**Output:**
```
ContextPackage {
  invoices: Invoice[],
  total_overdue: decimal,
  days_overdue_max: int,
  stage: T1 | T2 | T3,
  payment_behavior: "puntual" | "tardio_habitual" | "irregular" | "sin_historial",
  previous_communications: Communication[],  // últimas 5
  manual_notes: string,
  contact: Contact,
  contact_verified: boolean,
  data_freshness_hours: int,
  gaps: string[]                             // qué falta para contexto completo
}
```

**Errores esperables:**
- `DEBT_CASE_NOT_FOUND` — el caso no existe o no pertenece al usuario
- `NO_ACTIVE_INVOICES` — el caso no tiene facturas activas (puede que ya se pagaron)
- `CONTACT_MISSING` — no hay contacto de pagos registrado

**Qué asume del módulo anterior:** Los datos de Invoice y Contact fueron cargados correctamente en la DB.

**Qué le garantiza al siguiente (Policy Engine):** Que el ContextPackage es completo con los datos disponibles, que los gaps están explícitos, y que `data_freshness_hours` es honesto.

---

### Módulo 2 — Policy Engine

**Input:**
```
{
  context_package: ContextPackage,
  user_id: uuid,
  user_role: string,
  output_type: "external_email",
  recipient: Contact
}
```

**Output:**
```
AuthorizedContext {
  authorized_chunks: KBChunk[],
  excluded_chunks: { chunk_id, reason }[],
  autonomy_level: 0,                         // siempre 0 en v1 — aprobación humana obligatoria
  escalation_required: boolean,              // true si monto supera umbral de autorización
  blocked: boolean,                          // true si do_not_contact o litigio
  block_reason: string | null,
  policy_log_id: uuid                        // referencia al log de auditoría
}
```

**Errores esperables:**
- `CASE_BLOCKED` — do_not_contact o litigio activo. El skill no debe invocarse.
- `KNOWLEDGE_PACK_INCOMPLETE` — no hay chunks del tipo requerido para este caso

**Qué asume del módulo anterior:** ContextPackage válido con contact verificable.

**Qué le garantiza al siguiente (Collections Skill):** Que los chunks autorizados son los únicos que puede usar. Que si `blocked = true` el skill no debe generar nada. Que el log de auditoría ya fue creado.

---

### Módulo 3 — Collections Skill

**Input:**
```
{
  authorized_context: AuthorizedContext,
  context_package: ContextPackage,
  user_profile: UserProfile
}
```

**Output:**
```
SkillOutput {
  intent: string,                  // "Recordatorio T1 para cliente puntual — primera mora"
  draft_content: {
    subject: string,
    opening: string,
    body: string,
    call_to_action: string,
    closing: string
  },
  fields_used: string[],           // qué campos del contexto usó
  gaps_reported: string[],
  confidence: HIGH | MEDIUM | LOW,
  confidence_reason: string,
  flags: {
    escalation_required: boolean,
    payment_plan_offered: boolean,
    contact_not_verified: boolean,
    low_confidence: boolean
  }
}
```

**Errores esperables:**
- `INSUFFICIENT_CONTEXT` — gaps críticos que impiden razonar (sin monto, sin contacto, sin etapa)
- `POLICY_VIOLATION_DETECTED` — la instrucción del usuario implicaría violar una política

**Qué asume del módulo anterior:** Que los chunks autorizados son la única fuente de verdad. Que `blocked = false`.

**Qué le garantiza al siguiente (Output Engine):** Que el borrador está fundamentado en fuentes declaradas. Que los flags son honestos. Que si hay `escalation_required`, el Output Engine debe bloquear el botón de aprobación directa.

---

### Módulo 4 — Output Engine

**Input:**
```
{
  skill_output: SkillOutput,
  user_profile: UserProfile,
  contact_profile: ContactProfile,
  debt_case_id: uuid,
  draft_id: uuid
}
```

**Proceso:**
1. Aplica Voice Layer (perfil de usuario + notas del contacto) sobre `skill_output.draft_content`
2. Persiste el Draft con `content_original` (pre-voz) y `content_final` inicial (post-voz)
3. Actualiza DebtCase a `DRAFT_READY`
4. Retorna el Draft completo al frontend

**Output:**
```
Draft {
  id: uuid,
  content_original: text,
  content_final: text,           // versión con voz aplicada — editable por el usuario
  confidence: HIGH | MEDIUM | LOW,
  confidence_reason: string,
  chunks_used: uuid[],
  gaps_reported: string[],
  flags: Flags,
  status: draft_ready
}
```

**Errores esperables:**
- `VOICE_LAYER_FAILED` — falla en aplicar el perfil. Fallback: retorna el output del skill sin ajuste de voz, con nota visible al usuario.

**Qué asume del módulo anterior:** SkillOutput válido con intent y draft_content completos.

**Qué le garantiza al siguiente (Channel Surface):** Que el Draft aprobado tiene `content_final` como el texto exacto que debe ir al email, con todos los flags correctos.

---

### Módulo 5 — Channel Surface (Email / IMAP APPEND)

**Input:**
```
{
  draft_id: uuid,
  approved_content: {
    subject: string,
    body: text
  },
  recipient_email: string,
  user_imap_credentials: EncryptedCredentials,    // del Credential Vault
  in_reply_to: string | null                       // Message-ID si es reply de un thread
}
```

**Proceso:**
1. Conectar al servidor IMAP del usuario
2. Detectar carpeta Drafts (con fallback por nombre en español)
3. Construir mensaje MIME con headers correctos
4. IMAP APPEND con flags `\Draft \Seen`
5. Confirmar UID del mensaje depositado

**Output:**
```
DeliveryResult {
  success: boolean,
  imap_uid: int | null,
  folder: string,                 // nombre de la carpeta donde fue depositado
  error: string | null
}
```

**Errores esperables:**
- `IMAP_AUTH_FAILED` — credenciales inválidas o expiradas
- `IMAP_CONNECTION_TIMEOUT` — servidor no responde
- `DRAFTS_FOLDER_NOT_FOUND` — no se encontró carpeta Drafts y no se pudo crear
- `APPEND_FAILED` — error al depositar el mensaje

**Qué asume del módulo anterior:** Que el contenido del Draft fue aprobado por un humano. Que el recipient_email fue validado.

**Qué le garantiza al siguiente:** El borrador está disponible en la bandeja de Drafts del usuario para envío manual.

---

### Módulo 6 — Nightly Engine (v1 mínimo)

**Input:**
```
NightlySignal[] del día +
DebtCase[] con datos de actividad +
KBChunk[] con timestamps de vigencia
```

**Proceso (solo lectura + cálculo en v1):**
1. Agrupa NightlySignals por tipo
2. Calcula métricas del día (aprobaciones, ediciones, escalaciones, rechazos)
3. Identifica DebtCases sin actividad > 10 días con mora > T1
4. Identifica KBChunks con `valid_until` < 7 días
5. Genera el reporte

**Output:** Reporte estructurado (ver Sección 11 del circuito cerrado) enviado por email al admin.

**Qué no hace en v1:** No propone cambios al Knowledge Engine. No actualiza perfiles. No recalibra el skill. Solo observa y reporta.

---

## 7. SOURCE OF TRUTH DOCTRINE PARA ESTE PILOTO

### Jerarquía cuando hay conflicto (mayor a menor autoridad)

```
1. Flag de bloqueo (do_not_contact / litigio activo)
2. Política de crédito y umbrales (KBChunk canónico activo)
3. Estado explícito de la Invoice (paid / disputed / in_agreement)
4. Script del skill para la etapa (KBChunk de función activo)
5. Historial de comunicaciones previas
6. Nota manual del usuario en el DebtCase
7. Comportamiento histórico de pago (calculado)
```

### Ejemplos de conflicto resuelto

**Conflicto 1:** La nota del usuario dice "le di plazo hasta el 20" pero la Invoice sigue marcada como vencida y el sistema asignó etapa T2.

**Resolución:** El sistema usa la etapa T2 (capa 1, estado de Invoice). La nota del usuario (capa 6) informa el contexto pero no cambia la etapa. El skill recibe la nota como contexto y puede ajustar el tono ("según nuestra conversación del...") pero no puede cambiar la urgencia del mensaje. **El usuario debe actualizar el estado de la Invoice si hay un acuerdo activo.**

---

**Conflicto 2:** El script T2 dice "mencionar consecuencias del incumplimiento", pero la política de crédito dice "no amenazar con acción legal sin autorización".

**Resolución:** La política de crédito (capa 2) gana sobre el script (capa 4). El skill elimina la mención a consecuencias legales y genera el borrador sin esa parte. Registra un flag de contenido omitido visible al usuario.

---

**Conflicto 3:** El historial de pago clasifica al cliente como "tardío habitual", pero la nota manual del usuario dice "cliente VIP, tratar con cuidado".

**Resolución:** El comportamiento histórico (capa 7) informa el razonamiento del skill. La nota manual (capa 6) tiene mayor autoridad. El skill combina: usa el script calibrado para tardío habitual pero aplica el tono cuidadoso indicado en la nota. La nota no cancela la etapa asignada — sí puede afectar el tono.

---

**Conflicto 4:** El usuario edita el borrador para incluir una oferta de descuento del 20% sobre el monto vencido. La política de crédito no permite descuentos sobre deuda sin autorización.

**Resolución:** El Output Engine no puede detectar esta edición en tiempo real (el usuario edita el texto libremente). Lo que sí ocurre: la edición se registra como tipo `content` en el Approval. Si el flag `payment_plan_offered` se activa por la edición, se genera un NightlySignal de contenido fuera de política para revisión del admin. **Este es un gap deliberado del MVP: el sistema confía en que el usuario aprueba dentro de los límites. La trazabilidad es el control, no el bloqueo.**

---

**Conflicto 5:** La factura tiene `status: paid` (actualizado manualmente por el usuario) pero el DebtCase sigue en estado `DRAFT_READY` con un borrador pendiente.

**Resolución:** El estado de Invoice (capa 3) gana. El sistema detecta que no hay facturas activas vencidas al intentar aprobar el borrador. Muestra error: "Las facturas de este caso ya fueron marcadas como pagadas. ¿Quieres cerrar el caso?" El borrador se descarta automáticamente.

---

## 8. ACCEPTANCE CRITERIA POR COMPONENTE

---

### C1 — Carga manual de datos de factura

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| El usuario puede cargar una factura con número, monto, fecha de vencimiento y cliente | Test funcional: cargar 5 facturas de diferentes clientes | 100% de las facturas aparecen en la bandeja con datos correctos | Sí — si falla, no hay datos para el flujo |
| El sistema calcula `days_overdue` correctamente | Test unitario con fechas conocidas | Cálculo correcto al día UTC-6 (Costa Rica) | Sí |
| El sistema asigna la etapa correcta (T1/T2/T3) | Test con facturas de 5, 20 y 50 días de mora | T1: ≤15 / T2: 16–45 / T3: >45 | Sí |
| El sistema detecta facturas duplicadas (mismo número de factura para el mismo cliente) | Test de carga de factura duplicada | Warning visible, no permite duplicar | No bloquea release pero sí debe existir en v1 |

---

### C2 — Creación y actualización de DebtCase

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| Crear un DebtCase para un cliente con facturas activas | Test funcional | DebtCase en estado OPEN con facturas asociadas | Sí |
| La state machine solo permite transiciones válidas | Test de todas las transiciones inválidas | Todas las transiciones inválidas retornan error 422 | Sí |
| Marcar una factura como pagada actualiza el estado del DebtCase | Test: pagar la única factura activa | Si no quedan facturas activas, DebtCase → RESOLVED automáticamente | Sí |

---

### C3 — Generación de borrador

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| El borrador generado contiene: asunto, apertura, cuerpo, call-to-action, cierre | Inspección del output | Los 5 elementos presentes y no vacíos | Sí |
| El confidence score es honesto (no siempre HIGH) | Test con caso de contexto incompleto (sin historial) | El sistema reporta MEDIUM o LOW cuando faltan datos | Sí |
| Los chunks usados están registrados en el Draft | Test de inspección del Draft record | `chunks_used` es un array no vacío con IDs válidos | Sí |
| El sistema no genera borrador para caso BLOQUEADO | Test: intentar generar borrador en caso do_not_contact | Error claro, sin borrador generado | Sí — fallo aquí es crítico |
| La generación completa en < 10 segundos | Test de rendimiento | P95 < 10s | No bloquea release pero debe monitorearse |

---

### C4 — Aplicación de política de visibilidad

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| Chunks CEO-ONLY nunca aparecen en el borrador | Test: cargar un chunk CEO-ONLY, verificar que no aparece en ningún draft | 0 instancias de contenido CEO-ONLY en output externo | Sí — fallo aquí es crítico |
| El log de chunks excluidos se registra en cada generación | Test de inspección del Draft record | `chunks_excluded` contiene los excluidos con razón | Sí |
| El Policy Engine bloquea la generación para casos con `do_not_contact = true` | Test funcional | `blocked: true` retornado, sin borrador | Sí |

---

### C5 — Aprobación humana

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| El botón de aprobación está deshabilitado cuando `escalation_required = true` | Test: generar borrador con monto sobre umbral | Botón APROBAR no disponible | Sí |
| La aprobación registra inmutablemente: usuario, timestamp, edit_type | Test de inspección del Approval record | Los 3 campos presentes y correctos | Sí |
| Si el usuario edita el borrador, el diff se registra como NightlySignal | Test: editar el cuerpo del email y aprobar | NightlySignal creado con edit_type correcto | No bloquea release v1 pero debe estar en v1 |
| La aprobación con confidence=LOW requiere confirmación adicional | Test: generar borrador con contexto mínimo, intentar aprobar | Modal de confirmación visible | Sí |

---

### C6 — Draft en email (IMAP APPEND)

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| El borrador aparece en la carpeta Drafts del cliente de email del usuario | Test end-to-end con servidor IMAP real | Email visible en Drafts con asunto y destinatario correctos | Sí |
| El borrador tiene los headers correctos (From, To, Subject, Message-ID) | Inspección del mensaje en Drafts | Todos los headers presentes | Sí |
| Si IMAP APPEND falla, el sistema muestra el texto para copia manual | Test: simular fallo de APPEND | Texto copiable visible sin perder el borrador | Sí |
| El sistema soporta al menos los servidores: Gmail (app password), Outlook (IMAP), cPanel/hosting estándar | Test en cada tipo | Entrega exitosa en los 3 | Sí para los 3 — si uno falla, bloquea solo ese tipo |

---

### C7 — Registro de ApprovedPair

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| Cada aprobación genera un ApprovedPair con: approval_id, output_original, output_approved, edit_type | Test de inspección | Todos los campos presentes | No bloquea release — pero debe existir en v1 |
| El ApprovedPair se crea aunque no haya edición | Test: aprobar sin editar | `edit_type: none`, `output_original == output_approved` | No bloquea release |

---

### C8 — Reporte nocturno mínimo

| Criterio | Validación | Resultado aceptable | Bloquea release |
|----------|-----------|---------------------|-----------------|
| El reporte se genera automáticamente cada noche (configurable: 02:00 UTC-6) | Test de cron job | Reporte recibido en el email del admin a la hora configurada | No bloquea release v1 — puede enviarse manualmente la primera semana |
| El reporte incluye: drafts generados, tasa de aprobación, escalaciones, alertas de cartera sin actividad | Inspección del reporte | Todos los campos presentes con datos del día | No bloquea release |
| El reporte NO incluye recomendaciones de cambio al Knowledge Engine ni al skill | Inspección | Ausencia de secciones de propuestas automáticas | Sí — si aparece, el Nightly Engine está excediendo su scope de v1 |

---

## 9. BACKLOG TÉCNICO POR FASES

---

### Fase 0 — Precondiciones (antes de escribir el flujo core)

| Tarea | Objetivo | Dependencia | Prioridad | Por qué existe | Riesgo que cubre |
|-------|----------|------------|-----------|----------------|-----------------|
| Definir y cargar el Knowledge Pack de cobranza | Política de crédito + scripts T1/T2/T3 en la DB como KBChunks activos | Ninguna | P0 | Sin esto el skill no tiene fuente de verdad | Evita que el skill invente políticas |
| Configurar las credenciales IMAP del usuario piloto | Credencial en el Credential Vault | Ninguna | P0 | Sin esto no hay entrega al canal | IMAP puede tener configuraciones no estándar que hay que resolver antes |
| Cargar datos de cartera del usuario piloto | Clientes + facturas + estados de pago + contactos de pagos | Knowledge Pack | P0 | Sin datos reales no hay flujo real | Valida que el modelo de datos es suficiente para los casos reales |
| Configurar el perfil de usuario (3 parámetros) | UserProfile con formalidad, longitud, saludo/cierre | Ninguna | P0 | El borrador necesita mínimo de voz para no sonar genérico | —  |
| Definir los umbrales de escalación exactos con el cliente piloto | ¿Desde qué monto o situación se escala? | Knowledge Pack | P0 | Sin umbrales definidos, el skill no puede activar `escalation_required` correctamente | Evita escalaciones incorrectas |

---

### Fase 1 — Flujo Core

| Tarea | Objetivo | Dependencia | Prioridad | Por qué existe | Riesgo que cubre |
|-------|----------|------------|-----------|----------------|-----------------|
| Implementar el Context Engine para cobranza | Recuperar ContextPackage desde DebtCase + Invoices + Contact + historial | Fase 0 completa | P0 | Es el primer módulo del flujo | Si falla, el skill recibe contexto vacío y genera basura |
| Implementar el Policy Engine (versión checklist) | Filtrar chunks por visibilidad + detectar bloqueos + loguear exclusiones | Knowledge Pack cargado | P0 | Sin esto, chunks CEO-ONLY pueden inyectarse en outputs | Riesgo de seguridad crítico |
| Implementar el Collections Skill (lógica T1/T2/T3 × 4 comportamientos) | Generar borrador estructurado con confidence y flags | Context Engine + Policy Engine | P0 | Es el núcleo de valor del piloto | Si genera mal, todo el flujo produce outputs inútiles |
| Implementar el Output Engine (Voice Layer básica + persistencia del Draft) | Aplicar perfil de usuario + crear Draft record | Collections Skill | P0 | Sin persistencia no hay aprobación | — |
| Implementar la State Machine del DebtCase | Transiciones válidas + side effects + transiciones inválidas bloqueadas | Output Engine | P0 | Sin state machine el DebtCase puede llegar a estados inconsistentes | Evita que se apruebe un borrador de un caso bloqueado |
| Implementar la UI de bandeja de cobranzas | Lista de DebtCases con prioridad simple | Estado del DebtCase | P0 | Es la entrada al sistema | — |
| Implementar la UI de apertura del caso | Mostrar datos completos del caso antes de generar | Context Engine | P0 | Es donde el usuario verifica los datos | Si no muestra datos completos, el usuario no puede detectar errores antes de generar |
| Implementar la UI de revisión y aprobación del borrador | Mostrar borrador + contexto del sistema + acciones | Draft persistido | P0 | Es el momento más crítico del flujo | Si la UI no muestra confianza y fuentes, el usuario aprueba a ciegas |
| Implementar IMAP APPEND | Depositar el borrador aprobado en Drafts del usuario | Credenciales IMAP | P0 | Sin esto no hay entrega al canal | — |
| Implementar el registro de Approval + ApprovedPair | Persistir la decisión del usuario y el par de aprendizaje | UI de aprobación | P0 | Sin esto el sistema no aprende y no hay trazabilidad | — |

---

### Fase 2 — Confianza y Control

| Tarea | Objetivo | Dependencia | Prioridad | Por qué existe | Riesgo que cubre |
|-------|----------|------------|-----------|----------------|-----------------|
| Implementar el warning de frescura de datos | Mostrar advertencia si los datos tienen > 24h | Context Engine | P1 | Evita el escenario "cliente ya pagó" | Riesgo R1 del circuito cerrado |
| Implementar la lógica de bloqueo completa (do_not_contact + litigio) | Bloquear generación + mostrar razón | Policy Engine + State Machine | P0 | Sin esto se puede generar borrador para casos que no deben contactarse | Riesgo legal y relacional |
| Implementar el mecanismo de escalación | Notificar al admin + cambiar estado del caso | State Machine | P1 | Sin escalación, los casos T3 con monto alto quedan sin manejo correcto | — |
| Implementar el Decline / Fallback logic completo | Todos los casos de la tabla de la sección 8 del circuito | Skill + Output Engine | P1 | Sin esto, el sistema genera siempre aunque no debería | Cubre 6 de los 7 riesgos del piloto |
| Implementar el AuditLog básico | Registrar todas las acciones externas con user_id + timestamp + acción | Approval | P1 | Sin trazabilidad no se puede depurar el error de contacto equivocado | Riesgo R2 |
| Tests de integración de visibilidad | Verificar que chunks CEO-ONLY nunca aparecen en outputs externos | Policy Engine | P0 | Es el acceptance criteria más crítico de seguridad | — |

---

### Fase 3 — Mejora y Reporting

| Tarea | Objetivo | Dependencia | Prioridad | Por qué existe | Riesgo que cubre |
|-------|----------|------------|-----------|----------------|-----------------|
| Implementar el cron job del Nightly Engine mínimo | Calcular métricas del día + generar reporte por email | NightlySignal table + ApprovedPair | P1 | Sin el reporte el piloto no produce aprendizaje visible para el admin | — |
| Implementar la clasificación básica de NightlySignals | Distinguir edit_type (none / style / content / fact) en los Approval | Approval + ApprovedPair | P1 | Es la señal de calidad del skill | — |
| Implementar las alertas de cartera sin actividad en el reporte | Listar DebtCases > 10 días sin acción con mora > T1 | Nightly Engine | P2 | Es la alerta operativa más útil para el usuario piloto | — |
| Implementar la expiración automática de borradores sin acción | Transición DRAFT_READY → OPEN después de N días | State Machine | P2 | Evita que la bandeja se llene de borradores viejos que ya no aplican | — |

---

## 10. QUÉ SIMULAR MANUALMENTE AL INICIO

### Sim 1 — Actualización del estado de pago

**Por qué simular:** No hay integración con el sistema de facturación del cliente. El riesgo más alto del piloto es generar un email de cobranza a un cliente que ya pagó.

**Cómo:** El usuario actualiza manualmente el estado de cada Invoice cuando recibe el pago. El sistema no detecta pagos automáticamente.

**Por cuánto tiempo:** Hasta que se tenga evidencia de que (a) hay un sistema de facturación con API accesible, y (b) el volumen de casos justifica la integración.

**Evidencia para automatizar:** El usuario piloto reporta que actualizar el estado manualmente toma más de X minutos por día, o que en 2+ ocasiones no actualizó a tiempo y se generó un borrador incorrecto.

---

### Sim 2 — Verificación del contacto de pagos

**Por qué simular:** Los contactos de pagos cambian. En v1, no hay integración con CRM ni directorio externo que valide que el email del contacto es correcto.

**Cómo:** El usuario verifica manualmente el contacto antes de generar el primer borrador para un cliente. El sistema solo muestra el flag de "no verificado" — la verificación es acción del usuario.

**Por cuánto tiempo:** En v1 completo. En v2 se puede agregar confirmación de email o integración con LinkedIn/CRM.

**Evidencia para automatizar:** 2+ casos donde el contacto incorrecto causó un problema, o el usuario piloto reporta que la verificación manual es una fricción constante.

---

### Sim 3 — Feedback del resultado de la comunicación

**Por qué simular:** ¿Pagó el cliente después de recibir el email? ¿Respondió? En v1 el sistema no detecta respuestas ni pagos.

**Cómo:** El usuario cierra el caso manualmente cuando el cliente paga o actualiza la nota del caso cuando hay respuesta del cliente.

**Por cuánto tiempo:** Hasta que se tenga integración con el servidor de email para detectar replies, o integración con el sistema de facturación.

**Evidencia para automatizar:** El volumen de casos hace que el cierre manual sea un cuello de botella operativo (> 20 casos activos simultáneos por usuario).

---

### Sim 4 — Clasificación de señales nocturnas

**Por qué simular:** En las primeras semanas, el admin debe revisar manualmente los NightlySignals para entender qué tipos de ediciones son frecuentes antes de automatizar la clasificación.

**Cómo:** El Nightly Engine genera una lista raw de ediciones del día. El admin las revisa y clasifica manualmente la primera semana.

**Por cuánto tiempo:** 2 semanas. Suficiente para calibrar si la clasificación automática (style / content / fact) es correcta.

**Evidencia para automatizar:** Cuando el admin confirma que la clasificación automática es correcta en > 85% de los casos en la semana 2.

---

### Sim 5 — Ajuste del skill después de feedback

**Por qué simular:** En v1, el Nightly Engine no propone ajustes al skill automáticamente. El ajuste es manual: el admin revisa el reporte, decide si hay un patrón y edita los scripts o la lógica del skill directamente.

**Cómo:** Reunión semanal del admin con el reporte nocturno. Si hay patrón claro, se edita el chunk del script correspondiente y se marca como nueva versión activa.

**Por cuánto tiempo:** Durante todo el piloto (4–6 semanas). El ajuste automático del skill es v2.

**Evidencia para automatizar:** Cuando hay suficientes pares aprobados (> 50 por etapa) para que la propuesta automática tenga evidencia estadística suficiente.

---

## 11. RIESGOS DE IMPLEMENTACIÓN

### R1 — Sobreconstrucción del modelo de datos

**Cómo se detecta temprano:** Si en Fase 1 el backend tarda más de 3 días en implementar las entidades core, el modelo es demasiado complejo para lo que hace.

**Cómo se mitiga:** El modelo MVP definido en la Sección 5 es el techo, no el piso. Empezar con las 5 entidades más simples (DebtCase, Invoice, Contact, Draft, Approval) y agregar solo lo que el flujo exija.

**Decisión de diseño que lo reduce:** UserProfile y ContactProfile como JSONBs en el User y Contact record respectivamente, no como tablas separadas en v1.

---

### R2 — Policy Engine sobre-diseñado para 5 documentos

**Cómo se detecta temprano:** Si la implementación del Policy Engine tarda más de 2 días para el caso de cobranza, está sobre-diseñado.

**Cómo se mitiga:** En v1 el Policy Engine es un checklist de 3 reglas: (1) ¿está el chunk marcado como CEO-ONLY? → excluir. (2) ¿está el caso bloqueado? → bloquear todo. (3) ¿el usuario tiene acceso al dominio de cobranza? → sí por defecto para el rol base. No más lógica en v1.

**Decisión de diseño que lo reduce:** Policy Engine como función pura, no como servicio independiente. Entra en el módulo de generación como validación previa.

---

### R3 — IMAP APPEND frágil en servidores de hosting estándar

**Cómo se detecta temprano:** Testing con el servidor real del cliente piloto antes de Fase 1. No suponer que funciona — probar primero.

**Cómo se mitiga:** (1) Implementar la detección de carpeta Drafts con múltiples nombres posibles (Drafts, Borradores, INBOX.Drafts, [Gmail]/Drafts). (2) Tener el fallback de "copia manual" listo desde el primer día. (3) Documentar los servidores que fallan y sus workarounds.

**Decisión de diseño que lo reduce:** El fallback de copia manual no es un error secundario — es una feature de primera clase. El usuario nunca pierde el borrador aunque IMAP falle.

---

### R4 — Clasificación incorrecta del edit_type

**Cómo se detecta temprano:** En Fase 0, hacer un test manual con 10 ediciones conocidas y verificar que el diff produce la clasificación correcta.

**Cómo se mitiga:** La clasificación en v1 es por threshold simple: < 15% del texto cambiado = style, ≥ 15% = content. No semántica. Si el usuario cambió el monto = fact (detectado por regex sobre números en el cuerpo del email).

**Decisión de diseño que lo reduce:** Clasificación rule-based en v1. No LLM para clasificar el tipo de edición. Determinista y auditable.

---

### R5 — Demasiados warnings que paralizan al usuario

**Cómo se detecta temprano:** En el primer test de usuario, si el piloto pregunta "¿tengo que hacer algo aquí o puedo aprobar?" más de 2 veces, hay demasiados warnings.

**Cómo se mitiga:** Máximo 2 warnings visibles al mismo tiempo. Los warnings de confianza LOW y contacto no verificado son los únicos que requieren confirmación adicional. El resto son informativos, no bloqueantes.

**Decisión de diseño que lo reduce:** Warnings con jerarquía: rojo = bloquea o requiere confirmación. Amarillo = informativo, no requiere acción. Verde = OK visible solo si hay algo relevante que destacar (ej: "cliente con historial impecable").

---

### R6 — UI de revisión demasiado cargada

**Cómo se detecta temprano:** Si el piloto tarda más de 30 segundos en decidir si aprobar en el primer test, la pantalla tiene demasiada información.

**Cómo se mitiga:** El diseño de la Pantalla 3 tiene una jerarquía clara: (1) confidence + warnings arriba, en una línea cada uno. (2) El texto del borrador en el centro, grande. (3) Los botones de acción abajo, el principal prominente. Las fuentes usadas son colapsables por defecto.

**Decisión de diseño que lo reduce:** El panel de "información del sistema" está colapsado por defecto para usuarios que ya llevan > 2 semanas en el sistema (ya saben qué buscar). Solo se expande automáticamente si hay warnings activos.

---

### R7 — Aprendizaje contaminado por falta de contexto al clasificar la edición

**Cómo se detecta temprano:** Si en el reporte nocturno de la semana 1 hay más de 30% de ediciones clasificadas como `content` cuando visualmente parecen ajustes de estilo, el clasificador está mal calibrado.

**Cómo se mitiga:** Threshold de 15% es conservador — preferir clasificar como content sobre style en casos de duda. Content genera una señal débil (revisión propuesta), no un cambio automático. En v1 el aprendizaje es humano-en-el-loop de todos modos.

---

## 12. RELEASE CHECKLIST

### DEBE ESTAR FUNCIONANDO SÍ O SÍ

- [ ] El flujo completo funciona end-to-end: cargar factura → generar borrador → aprobar → borrador en Drafts del email
- [ ] Los casos con `do_not_contact = true` NO generan borradores bajo ninguna circunstancia
- [ ] Los chunks CEO-ONLY NO aparecen en ningún borrador generado
- [ ] El registro de Approval es inmutable (no puede editarse o borrarse después de creado)
- [ ] IMAP APPEND funciona en el servidor real del cliente piloto
- [ ] El fallback de "copia manual" funciona cuando IMAP APPEND falla
- [ ] La state machine bloquea las transiciones inválidas (especialmente: no generar si BLOCKED, no aprobar si escalación requerida)

### PUEDE ESTAR FEO PERO FUNCIONAL

- [ ] El diseño visual de la UI (no es criterio de release)
- [ ] El reporte nocturno puede enviarse manualmente la primera semana
- [ ] El cálculo de `days_overdue` puede tener un margen de ±1 día (zona horaria)
- [ ] La clasificación del edit_type puede ser manual la primera semana
- [ ] El perfil de usuario puede configurarse directamente en la DB si el UI de configuración no está listo

### NO PUEDE ROMPERSE BAJO NINGUNA CIRCUNSTANCIA

- [ ] El monto en el borrador debe ser exactamente el mismo que en la Invoice cargada
- [ ] El destinatario del email debe ser exactamente el email del Contact registrado
- [ ] El AuditLog debe registrar cada aprobación con user_id y timestamp
- [ ] Un borrador NO puede ser enviado desde FaberLoom (solo IMAP APPEND a Drafts — el usuario envía)

### ERRORES QUE MATAN LA CONFIANZA INMEDIATAMENTE

- Borrador con monto incorrecto → investigación inmediata, no puede lanzarse si ocurrió en testing
- Borrador enviado a cliente equivocado → ídem
- Borrador generado para un caso marcado como `do_not_contact` → ídem
- Cualquier chunk CEO-ONLY visible en el output → ídem

---

## 13. DECISIONES ABIERTAS

### D1 — Integración de datos de factura: ¿CSV upload o entrada manual por formulario?

**Opciones:**
- A: Formulario de entrada manual por factura (simple, bajo riesgo técnico)
- B: Upload de CSV con mapeo de columnas (más rápido para carteras grandes)
- C: Ambos (más complejo, no necesario en v1)

**Recomendación:** B — CSV con template fijo de 5 columnas (cliente, número factura, monto, fecha vencimiento, contacto de pagos). El template se entrega al cliente piloto en el onboarding. Más rápido que el formulario para carteras > 10 facturas. El formulario puede agregarse en v2.

**Impacto:** Decide la UI de carga de datos y el proceso de onboarding del piloto.

---

### D2 — ¿Cuánto tiempo antes de que un borrador expire (DRAFT_READY → OPEN)?

**Opciones:**
- A: 3 días (agresivo — fuerza al usuario a actuar rápido)
- B: 7 días (razonable para ciclos de trabajo semanales)
- C: Sin expiración en v1 (más simple, pero la bandeja se llena)

**Recomendación:** B — 7 días. Comunica claramente al usuario que el borrador tiene una ventana. Incentiva uso regular sin ser punitivo.

**Impacto:** Afecta la lógica del cron job y la pantalla de bandeja (mostrar "expira en N días").

---

### D3 — ¿Qué hace el sistema cuando el Knowledge Pack está incompleto al momento de generar?

**Opciones:**
- A: Genera igual con confidence=LOW y gaps reportados visibles (el usuario decide)
- B: Bloquea la generación y pide al admin que complete el Knowledge Pack antes
- C: Genera un borrador parcial solo con los elementos que tiene

**Recomendación:** A — genera con confidence=LOW y gaps explícitos. El bloqueo en B es correcto arquitectónicamente pero produce una experiencia pésima si el Knowledge Pack tiene pequeños gaps. El usuario piloto necesita valor inmediato; puede mejorar el Knowledge Pack mientras el sistema ya está en uso.

**Impacto:** Decide la lógica del Collections Skill cuando tiene fuentes parciales.

---

### D4 — ¿Cómo se notifica al admin de una escalación?

**Opciones:**
- A: Email simple al admin con resumen del caso
- B: Notificación en la UI (si el admin también usa la plataforma)
- C: Ambos

**Recomendación:** A en v1 — email simple. El admin no necesita un UI propio para las escalaciones del piloto. Si hay > 5 escalaciones por semana, entonces vale la pena un UI.

**Impacto:** Decide si hay que construir una vista de admin para el piloto o no (recomendado: no en v1).

---

### D5 — ¿Cómo maneja el sistema los clientes con múltiples contactos de pagos?

**Opciones:**
- A: Un único contacto primario por cliente. El usuario actualiza manualmente si cambia.
- B: Múltiples contactos posibles, el usuario elige al generar
- C: Múltiples contactos con una lógica de selección automática

**Recomendación:** A en v1. La realidad de PYMEs B2B en LATAM es que hay 1–2 contactos de pagos por cliente. La complejidad de múltiples contactos con selección dinámica no se justifica en el piloto.

**Impacto:** Decide la estructura del modelo Contact y la UI de apertura del caso.

---

### D6 — ¿El sistema muestra el texto de los chunks usados o solo los nombres?

**Opciones:**
- A: Solo los nombres (ej: "Política de crédito v2.1") — más limpio
- B: Nombres + extracto relevante del chunk — más transparente
- C: Los chunks son un detalle técnico que el usuario no necesita ver

**Recomendación:** A en v1. El usuario piloto no necesita leer la política de crédito para aprobar el borrador. Los nombres son suficientes para la trazabilidad. Si el usuario quiere más contexto, puede leer los documentos directamente.

**Impacto:** Decide qué expone la pantalla de aprobación.

---

### D7 — ¿Cómo se maneja el primer draft para un cliente sin ningún historial?

**Opciones:**
- A: Genera con confidence=MEDIUM, comportamiento "sin_historial", tono conservador por defecto
- B: Pide al usuario que clasifique el comportamiento antes de generar (formulario previo)
- C: No genera hasta que haya al menos 1 comunicación previa registrada

**Recomendación:** A — genera con tono conservador y lo dice claramente en el confidence. El primer draft para un cliente nuevo es una comunicación de bajo riesgo (normalmente T1 o T2 temprano). No bloquear la generación por falta de historial.

**Impacto:** Decide el comportamiento del skill cuando `payment_behavior = "sin_historial"`.

---

### D8 — ¿Se permite que el usuario envíe el email directamente desde el sistema (no solo Drafts)?

**Opciones:**
- A: No. Solo IMAP APPEND a Drafts. El usuario envía desde su cliente de email.
- B: Sí, con botón de "Enviar" que ejecuta SMTP desde FaberLoom

**Recomendación:** A — permanente, no solo en v1. La doctrina de aprobación humana significa que el usuario envía. Si FaberLoom hace el SMTP, FaberLoom está "enviando en nombre del usuario" con todas las implicaciones que eso tiene (reputación del dominio, responsabilidad del envío, errores de entrega). No abrir esa puerta.

**Impacto:** Esta es una decisión de producto permanente, no solo de piloto.

---

### D9 — ¿Qué pasa si el usuario edita el borrador para incluir contenido fuera de política?

**Opciones:**
- A: El sistema no puede detectarlo en tiempo real — se registra como `content` edit y se genera NightlySignal para revisión del admin
- B: El sistema analiza el borrador editado antes de aprobar y bloquea si detecta violaciones (ej: monto diferente al de la factura, promesa legal)
- C: Solo bloquea para casos muy específicos (monto diferente al de la factura)

**Recomendación:** C en v1. Detectar la edición del monto es simple (regex numérico comparado contra Invoice.amount). Detectar promesas legales o condiciones fuera de política requiere LLM sobre el texto editado, lo cual añade latencia y complejidad. El AuditLog y el NightlySignal son el control de calidad — no el bloqueo en tiempo real para todo.

**Impacto:** Decide si hay una capa de validación post-edición antes de IMAP APPEND.

---

### D10 — ¿Cuándo se activa el aprendizaje automático del UserProfile?

**Opciones:**
- A: Nunca en v1 — siempre manual
- B: Cuando el usuario tiene ≥ 20 pares aprobados, el sistema actualiza automáticamente el parámetro de longitud
- C: El sistema propone el cambio después de 10 ediciones consistentes; el usuario lo aprueba

**Recomendación:** C — propone, no aplica. Después de 10 ediciones en la misma dirección (ej: siempre acorta los drafts), el sistema muestra: "Hemos notado que generalmente acortas los borradores. ¿Quieres que los generemos más cortos por defecto?" El usuario decide. Esto puede estar en v1 final o v2 temprano — no es bloqueante.

**Impacto:** Decide cuándo y cómo el UserProfile comienza a adaptarse.

---

## 14. CRÍTICA BRUTAL FINAL

### Qué parte del diseño está lista para construir

El flujo E2E está suficientemente definido para empezar Fase 1. Los contratos funcionales entre módulos son claros y verificables. El modelo de datos MVP tiene todas las entidades necesarias sin sobrar. La state machine es implementable directamente. La UI mental tiene suficiente detalle para diseño funcional sin ser un wireframe que ya tomó decisiones de componentes.

La lógica de decline / fallback / escalation es la parte más lista: está definida como tabla de condición → respuesta, que se traduce directamente a código.

### Qué parte todavía está demasiado abstracta

El Collections Skill está bien descrito en lógica de negocio pero no en implementación. La sección dice "razona por etapa × comportamiento" pero no especifica: ¿es esto un prompt template? ¿un árbol de condiciones en código? ¿una combinación? En Fase 1, alguien tiene que tomar esa decisión antes de implementar.

**Recomendación:** En v1, el skill es un prompt template con variables inyectadas (etapa, comportamiento, monto, contacto, historial resumido, scripts del Knowledge Pack). No es razonamiento libre del LLM — es un template estructurado con slots definidos. Eso es predecible, auditable y corregible.

### Qué parte está sobrediseñada para el piloto

El modelo de herencia completo (7 capas) es correcto como arquitectura a largo plazo pero innecesario de implementar completamente para el piloto. En la práctica, el piloto solo activa 4 capas: KB canónica, skill de cobranza, contexto del caso y perfil de usuario básico. Las otras 3 (conocimiento por función separado, perfil de contacto inferido, voz adaptativa completa) pueden simularse manualmente o ignorarse en v1.

El Nightly Engine también está sobrediseñado si se implementa con el ciclo de estados completo (OBSERVADO → PROPUESTO → VALIDADO). En v1 es: cron job → calcula métricas → envía email al admin. Tres funciones. No un sistema de estados.

### Qué NO tocarías porque ya está correctamente definida

La doctrina de visibilidad de 4 dimensiones (consultar / inyectar / recibir / aprobar) y la regla de que los chunks CEO-ONLY nunca van a vectores ni a outputs externos. Está bien definida, es implementable directamente y cubre el riesgo más serio del sistema. No agregar complejidad aquí.

La doctrina de aprobación humana obligatoria para toda salida externa. No hay argumentos de "sería útil en algunos casos automatizar". No se toca.

### La próxima decisión concreta después de este documento

**Armar el Knowledge Pack real con el primer cliente piloto antes de escribir una línea de código.**

La Fase 0 empieza con el Knowledge Pack — y ese Knowledge Pack no puede ser inventado. Necesita ser la política de crédito real del cliente piloto, los scripts de cobranza que ese cliente ya usa (aunque sea informalmente), y los umbrales de escalación que el dueño del negocio ha decidido. Sin eso, el Collections Skill es un motor sin combustible.

Eso requiere una reunión de 2 horas con el cliente piloto, no trabajo técnico.

---

*FABERLOOM — Plan de Construcción: Cobranza B2B · Build Plan v1.0 · 2026-04-15*
