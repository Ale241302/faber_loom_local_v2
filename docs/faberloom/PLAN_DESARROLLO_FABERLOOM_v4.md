# Plan de Desarrollo Tecnico - FaberLoom Shell v4 (Post-Auditoria 3ra ronda)

**id:** PLAN_DESARROLLO_FABERLOOM_v4
**version:** 4.0
**status:** DRAFT - listo para cuarta auditoria
**fuente:** PLAN_DESARROLLO_FABERLOOM_v3.md + correcciones auditoria 3ra ronda (8.0/10)
**tech stack:** Python (FastAPI), PostgreSQL, Redis, Docker Compose, React (Vite), LiteLLM (lib)
**infra:** KVM 8 (Hostinger), single-tenant interno MWT, 2 roles (Owner/Operator)
**estimated effort:** 12-14 semanas a sistema interno real; decision SaaS post-E2.5
**dedicacion dev:** 35h/sem (full-time) o timeline se extiende proporcionalmente
**dedicacion CEO:** 8-10h/sem

---

## 1. Cambios estructurales vs v3 (resumen de auditoria 3ra ronda)

| Problema v3 (gap a 9.2) | Correccion v4 |
|---|---|
| Breakeven "mes 4-6" aritmeticamente falso (CAPEX mensual de dev > beneficio) | Seccion 5 reescrita con matematica correcta: **breakeven ~15-18 meses** sobre inversion one-time; ROI negativo a mes 12. Se elimina "mes 4-6" y "1.2x-1.5x a mes 12". |
| Transferencia transfronteriza de PII (CR/GT -> US) tratada como "interes legitimo" sin analisis | E0.5 agrega tarea de **base legal de transferencia internacional**; data_jurisdiction agrega columna `transfer_basis`; la eleccion concreta queda **[PENDIENTE - decision CEO/abogado]**, no inventada. |
| DeepSeek (CN, sin DPA) en matriz con PII | **Eliminado de todo data_class con PII.** Solo disponible para data_class sin PII (metadata anonimizada), si acaso. |
| Cobranza a terceros = fork abierto ("o limitar hasta dictamen") en un gate bloqueante | **Cerrado en firme:** cobranza a terceros NO entra en E2.5 hasta dictamen legal escrito. E2.5 arranca solo con RFQ + seguimiento interno. |
| Gate "diff <20% en 3/10" = liston bajo | Subido a **>=6/10 tareas**, o reduccion agregada de edicion. |
| Grounding 85% choca con "0 precios inventados" | **Separado:** precios/condiciones = 100% trazado (hard fail), prosa = 85%. |
| Gate movil con "usuarios simulados" | **Usuarios reales** (CEO + operador + 1 prospecto), no simulados. |
| Moat afirmado como hecho | Marcado como **hipotesis a confirmar en E2** via improvement_score. Propiedad de gold_samples resuelta en DPA. |
| Injection = 10 tests fijos, una sola vez | Agregado **red-team abierto** + injection como control continuo, no gate de una sola vez. |
| E1a "1 semana" pero kill en semana 2 | E1a declarado **1-2 semanas**, alineado con el kill. |

---

## 2. Stack tecnico y arquitectura

### 2.1 Contenedores (Docker Compose)

| Servicio | Rol | Nota |
|---|---|---|
| caddy | Reverse proxy + HTTPS | Certbot auto |
| web | Frontend (React 18 Vite) | SPA, dark mode, design tokens CSS, responsive movil |
| api | Backend (FastAPI + Python 3.12) | API REST + WebSocket chat/drafts |
| worker | Celery + Redis | Jobs async: parsing, indexing, email ingest, OAuth refresh |
| postgres | PostgreSQL 16 | RLS desde dia 1, tenant isolation tests por tabla |
| redis | Redis 7 | Cache, Celery broker, pub/sub, session store |

**Descartados:** Grafana/Loki/Prometheus/MinIO -> logging JSON a disco + Langfuse Cloud metadata-only.
**Operacion:** RPO 24h, RTO 4h. Restore probado mensual en host distinto.

### 2.2 Dependencias clave

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
sqlalchemy[async]==2.0.31
alembic==1.13.0
asyncpg==0.29.0
redis==5.0.0
celery==5.4.0
litellm==1.40.0  # como libreria, no proxy standalone
python-multipart==0.0.9
pypdf==4.2.0
openpyxl==3.1.0
markdown-it-py==3.0.0
```

### 2.3 Schema fisico

Igual que v3, con un cambio en `data_jurisdiction` (columna `transfer_basis`):

```sql
data_jurisdiction: id, country_code, data_class, provider_allowed, storage_region, retention_days, redaction_required, dpa_required, legal_basis, transfer_basis, created_at
```

Resto de tablas sin cambio vs v3 (draft.edit_distance, draft.time_to_approve_sec, gold_sample.improvement_score, routing_preset.fallback_model, email_message.optout_flag + data_origin, prompt_injection_test, compliance_artifact).
**Secretos:** sops/age. **Backup:** Backblaze B2.

---

## 3. Secuencia de milestones (12-14 semanas)

### E0 - Dataset de verdad (3 dias, CEO + Cowork)

**No se escribe codigo.**

- [ ] 30 casos reales MWT: 10 RFQs, 10 cobranzas, 10 seguimientos.
- [ ] Tabla de verdad por caso: input real, respuesta ideal, datos requeridos, fuente, tiempo manual cronometrado.
- [ ] Baseline: tiempo del CEO hoy por clase de tarea (alimenta el ROI real, seccion 5).
- [ ] Respuesta con Claude crudo para los 10 candidatos (linea base del gate E1b).
- [ ] 10 casos 80% repetitivos marcados como candidatos a automatizar.
- [ ] Firmar dedicacion Alejandro: >=35h/sem, o timeline a ~5 meses.

**Gate de salida:** 30 casos con tiempos, 10 candidatos, 10 baselines Claude-crudo, Alejandro confirmado.
**Kill:** no hay 30 casos reales -> detener.

---

### E0.5 - Compliance y seguridad como artefactos (1 semana, paralela, sin codigo)

**Gate bloqueante antes de tocar correo real de terceros.**

- [ ] **PRODHAB (CR), Ley 8968:** registro de base de datos. Responsable: Alvaro. Fecha limite: dia 5.
- [ ] **Guatemala:** checklist legal (consentimiento, acceso, rectificacion, transferencia, retencion). Responsable: Alvaro. Dia 5.
- [ ] **Mexico:** LFPDPPP 2025. Bloqueado hasta DPA + aviso de privacidad + responsable legal. NO procesar datos MX en E2.5.
- [ ] **Transferencia internacional de datos (NUEVO, critico):** mandar PII de clientes CR/GT a OpenAI/Anthropic en US es transferencia transfronteriza bajo Ley 8968. Definir la base de la transferencia. Opciones: (a) consentimiento informado del titular, (b) clausulas contractuales de transferencia con el proveedor, (c) procesar PII solo con redaction/seudonimizacion antes de salir a US. **Eleccion concreta: [PENDIENTE - decision CEO/abogado].** Reflejar en `data_jurisdiction.transfer_basis`. Sin esto cerrado, no sale PII a proveedor US.
- [ ] **Data residency:** ubicacion fisica del KVM (Hostinger) + jurisdiccion aplicable documentada.
- [ ] **Matriz data_class (DeepSeek eliminado de PII):**
  | data_class | country | provider_allowed | storage_region | retention | redaction | dpa | legal_basis | transfer_basis |
  |---|---|---|---|---|---|---|---|---|
  | PII_cliente | CR/GT | openai,anthropic | us-east-1 | 7 anos | si | si | interes_legitimo | [PENDIENTE] |
  | precios | CR | openai,anthropic | us-east-1 | 3 anos | no | no | ejecucion_contrato | n/a |
  | facturas | CR | openai,anthropic | us-east-1 | 10 anos | no | si | obligacion_legal | [PENDIENTE] |
  | metadata | CR | openai,anthropic | us-east-1 | 1 ano | si | no | legitimo | n/a |
  | email_raw | CR | NINGUNO | local | 30 dias | si | no | legitimo | n/a |

  **DeepSeek (CN, sin DPA): provider_allowed=NINGUNO para todo data_class con PII.** Disponible solo para metadata anonimizada si se justifica; por defecto, fuera.
- [ ] **DPA template:** para prospectos E2.5. Debe definir **propiedad de los gold_samples derivados de data del cliente** (ver Dim moat, seccion 6).
- [ ] **Aviso de privacidad.**
- [ ] **Politica de retencion/borrado:** tabla por data_class + procedimiento (soft + hard delete tras retencion).
- [ ] **Matriz de proveedores LLM (sin DeepSeek para PII):**
  | Provider | Modelos | DPA | Region | Fallback | Redaction |
  |---|---|---|---|---|---|
  | OpenAI | gpt-4o, gpt-4o-mini | Si | US | Anthropic | Metadata only |
  | Anthropic | sonnet, opus, haiku | Si | US | OpenAI | Metadata only |
  | Google | gemini-1.5 | Si | US | OpenAI | Metadata only |
- [ ] **Defensa prompt injection:** separar contenido/instrucciones; allow-list de acciones; nunca auto-send sin HITL.
- [ ] **Pruebas de injection (10 fijas + red-team abierto):** las 10 de v3 (100% bloqueadas) MAS un componente red-team no scripteado. Injection es **control continuo**, no gate de una sola vez: re-correr el set en cada cambio de prompt/skill.
- [ ] **SPF/DKIM/DMARC** verificado antes del primer SMTP. Warm-up.
- [ ] **Langfuse redaction:** metadata + hashes por defecto.
- [ ] **Prueba de trazas sin PII:** 10 trazas, 0 PII = pass.

**Gate de salida:** artefactos aprobados y versionados; transfer_basis decidido (o PII bloqueada hasta decidir); injection 100% + red-team sin hallazgo critico; 0 PII en trazas; restore test <4h.
**Kill:** requisito legal bloquea CR/GT -> reestructurar. Injection falla -> no tocar correo real. transfer_basis sin decidir -> no sale PII a US.

---

### E1a - Fundacion tecnica (1-2 semanas, full-time dev)

**Solo infra + auth + inbox + audit + backup.** Buffer real hasta el kill de semana 2.

- [ ] Docker Compose 6 containers. PostgreSQL + Alembic + RLS por tenant_id con policies activas.
- [ ] Tenant isolation tests automatizados por tabla sensible (A no lee/edita/busca de B).
- [ ] Auth: httpOnly cookies, 2 roles. OAuth Gmail/Microsoft camino principal (app password solo lab). 2FA solo Owner.
- [ ] Audit log append-only (trigger PostgreSQL). Metadata only.
- [ ] Backup pg_dump diario a Backblaze B2. Restore test mensual en host distinto. RPO 24h / RTO 4h.
- [ ] Logging JSON a disco. Langfuse metadata-only.
- [ ] PolicyGate propio antes de LiteLLM. LiteLLM solo ejecuta y traza.
- [ ] Inbox OAuth: IMAP via OAuth. Polling 5 min. Clasificacion ventas/cobranza/soporte/spam.
- [ ] SpaceLoom base: 1 chat, 1 workspace, sin KB. Solo modo Operar.
- [ ] Responsive movil: login, navegacion, inbox visible desde movil (no requiere aprobacion de draft; eso es E1b).

**Gate E1a:**
1. Correo real entra via OAuth, se clasifica y queda auditado.
2. 0 PII en Langfuse (10 trazas).
3. Restore probado <4h en host distinto.
4. Tenant isolation test pasa para todas las tablas sensibles.
5. OAuth IMAP funciona sin app password.
6. Pantalla responsive cargable desde movil (login, navegacion, inbox visible).

**Kill:** semana 2 sin gate -> congelar 90 dias.

---

### E1b - Draft Engine + KB minima + HITL (1-2 semanas, full-time dev)

- [ ] KB pipeline: upload PDF/Excel/MD, parser basico, chunker 1000/200, FTS pg_trgm. Sin embeddings.
- [ ] Draft Engine: 1 skill generico (SkillSpec markdown). Timeout 30s. Cost cap $0.50. No HTTP externo, no code exec.
- [ ] HITL minima: 3 botones. Campo "por que rechazaste" obligatorio. edit_distance + time_to_approve_sec automaticos.
- [ ] Canal de salida: SMTP manual, doble confirmacion (no auto-send hasta E2).
- [ ] Gold samples: captura automatica desde dia 1, con source_draft_id.
- [ ] Wizard verificacion HIGH/LOW.

**Gate E1b:**
1. **Diff vs Claude:** edicion <20% en **>=6/10** tareas de E0 (subido desde 3/10), o reduccion agregada de edicion sobre las 10.
2. **Aprobar/rechazar desde movil en <=45s** con usuarios reales (CEO + operador + 1 prospecto), no simulados.
3. Tiempo login->draft aprobado <2 min (desktop).
4. 20 drafts reales, >=70% aprobados con edit_distance <20%.
5. 0 destinatarios incorrectos.
6. Tiempo promedio <=20% del baseline E0.
7. **Grounding separado:** precios y condiciones = **100% trazado a KB (hard fail si no)**; prosa = >=85% con cita de chunk. 0 precios inventados.
8. Contamination test: seed #2 no ve nada del #1.

**Kill:** E1a no cierra semana 2 -> congelar. E1b no cierra semana 4 -> congelar.

---

### E2 - Sistema de skills + trazabilidad (2 semanas, full-time dev)

**Hito 2a (sem 5-6):**
- [ ] Engine ejecutor generico (SkillSpec versionado).
- [ ] Skill 1: RFQ/cotizacion. Skill 2: seguimiento (clase distinta). **Cobranza NO entra hasta dictamen legal (ver E2.5).**
- [ ] Tier 0 deterministico del primer skill real.
- [ ] Evidence bundle: SHA-256, immutable.
- [ ] Savings ledger: costo real vs baseline E0. Tokens por clase medidos. Bloquear prompts >N tokens sin resumen.
- [ ] **Payback real:**
  - CAPEX mensual: infra ($100) + Alejandro ($3,000-5,000) + CEO ($800-1,600) + herramientas ($100) = **$4,000-6,700/mes**.
  - Ahorro mensual: 5h/sem CEO x $50/h x 4 sem = **$1,000/mes** (hipotesis a confirmar post-E0).
  - Ingreso E2.5: $39 x N clientes (hipotesis).
  - **Breakeven:** cuando ahorro + ingreso > CAPEX. Declarar mes objetivo.

**Hito 2b (sem 7-8):**
- [ ] Client map: seed + freemail list + triage.
- [ ] WorkLoom: cola por estado (TU CRITERIO / ESPERANDO / DELEGADO / ERROR).
- [ ] Captura del porque + edit_distance.
- [ ] Trazas redacted. Verificacion manual 10 trazas/semana.
- [ ] Aprendizaje minimo: CTA "Indexar esto" + cola.
- [ ] **Moat medible (hipotesis):** gold_sample.improvement_score = mejora del draft N vs N-1 para el mismo cliente. **A confirmar con datos, no afirmar como hecho.**

**Gate E2:**
1. >=10 outputs reales cliente-facing aprobados/enviados, >=2 clases.
2. Edit rate <40% en ultimos 20 drafts (edit_distance).
3. Reduccion de tiempo con cronometro >=5x vs baseline E0.
4. Costo IA por tarea aprobada <USD 0.35.
5. Cero incidentes de envio equivocado.
6. 0 fugas en trazas (10 trazas).
7. improvement_score medido (confirma o niega el moat).

**Kill:** edit rate >=60% en 30 drafts -> congelar.

---

### E2.5 - Validacion comercial (semanas 5-9, CEO 2h/sem + operador)

**Mismo flujo interno. Solo CR/GT/CO. MX bloqueado. Cobranza a terceros FUERA hasta dictamen.**

- [ ] Oferta a 10 PYMEs B2B NO-amigas: agente para **RFQ y seguimiento** (cobranza no, hasta dictamen). Aprueban todo antes de enviar.
- [ ] Mismo flujo: email/RFQ -> draft -> aprobacion -> envio.
- [ ] Cobrar piloto simbolico desde dia 1 ($5-10/mes).
- [ ] Medir WTP real (preguntar antes de anclar $39). Anclar vs alternativas reales (seccion 6).
- [ ] Registro por prospecto: uso sem 1, uso sem 2, reaccion a precio, objeciones.
- [ ] **Cobranza a terceros:** entra a E2.5 SOLO cuando exista dictamen legal escrito de base para contactar al deudor (interes legitimo + origen del dato + opt-out). Hasta entonces, fuera. **Sin "o limitar"; es un si/no con dictamen.**
- [ ] MX: bloqueado hasta paquete legal.

**Gate (decide E3):**
- >=4/10 usan 2 semanas seguidas Y >=3/10 pagan algo concreto -> E3 con design partners.
- <3/10 con pago -> E3 NO se construye. Interno MWT, re-evaluar en 6 meses.

---

### E3 - Workspaces (condicional a E2.5) - 2-3 semanas

**Solo si E2.5 dio >=3 con pago.** (Sin cambios vs v3: My/Shared workspaces, scope bar, herencia SpaceLoom, historial contextual, CTA indexar L3, StackLoom si >=30 drafts, Admin si >=2 operadores.)
**Gate:** operar 2+ cuentas reales puramente desde workspaces 1 semana.

---

### E4 - Multi-usuario y multi-tenant (condicional)

**E4a (interno):** membresia, 2 roles, columna Delegado, lock optimista, invitaciones.
**E4b (externo, gate E2.5):** design partners pagos, DPA firmado (con clausula de propiedad de gold_samples), 5 roles, WhatsApp Business API (diferido a Meta), pricing vs WTP. Solo si E2.5 dio >=3.

---

## 4. Criterios de calidad y riesgos

### 4.1 Quality gates (cambios vs v3 en negrita)

| Etapa | Gate | Metrica | Umbral |
|---|---|---|---|
| E0 | Dataset | casos + tiempos + Claude-crudo | 30, 10 candidatos, 10 baselines |
| E0.5 | Compliance artifacts | items verificados | 100% |
| E0.5 | **Transfer basis PII** | decidido | si (o PII bloqueada) |
| E0.5 | Injection | 10 fijas + red-team | 100% fijas, 0 critico red-team |
| E0.5 | Trazas sin PII | 10 trazas | 0 PII |
| E0.5 | Restore | tiempo | <4h |
| E1a | Correo OAuth + audit | funcional | si |
| E1a | Tenant isolation | tests | 100% tablas |
| E1a | **Responsive móvil** | **login/navegación/inbox** | **cargable desde móvil** |
| E1b | **Diff vs Claude** | edicion <20% | **>=6/10** |
| E1b | Tiempo login->draft aprobado | desktop | <2min |
| E1b | **Aprobación móvil <=45s** | **usuarios reales** | **CEO + operador + prospecto** |
| E1b | **Grounding precios** | trazado | **100% (hard fail)** |
| E1b | Grounding prosa | cita de chunk | >=85% |
| E1b | Drafts aprobados | count + edit<20% | >=20, >=70% |
| E2 | Outputs reales | count + clases | >=10, >=2 |
| E2 | Edit rate | edit_distance | <40% |
| E2 | Costo por tarea | USD | <$0.35 |
| E2 | **Moat** | improvement_score | medido (no asumido) |
| E2.5 | Intencion de pago | prospectos /10 | >=3/10 |
| E3 | Uso por workspace | dias sin global | 7 |
| E4b | Design partners pagos | tenants + DPA | >=3 |

### 4.2 Riesgos (nuevos/cambiados vs v3 en negrita)

| Riesgo | Prob | Impacto | Mitigacion |
|---|---|---|---|
| Alejandro no full-time | Media | Critico | Confirmar E0. Si <35h, 5 meses. |
| LiteLLM hook | Media | Alto | PolicyGate obligatorio. |
| CEO no usa | Media | Critico | Gate E1b diff >=6/10 vs Claude. |
| Costo IA | Baja | Medio | Cap $0.50. Bloquear prompts >N tokens. |
| Prompt injection | Alta | Critico | 10 tests + **red-team + control continuo**. Nunca auto-send. |
| Fuga en trazas | Media | Critico | Metadata-only. 10 trazas/sem. |
| Deliverability | Media | Alto | SPF/DKIM/DMARC. OAuth. Warm-up. |
| Dato comercial equivocado | Media | Critico | Precios 100% trazados. HITL. |
| CEO sobre-suscrito | Alta | Critico | 8-10h/sem. Low-risk a Alejandro. |
| Compliance bloquea | Baja | Critico | E0.5 gate. MX bloqueado. |
| **Transferencia transfronteriza PII** | **Media** | **Critico** | **transfer_basis decidido en E0.5 o PII no sale a US.** |
| Vendor LLM precio/modelo | Media | Medio | fallback_model. **DeepSeek fuera de PII.** |
| Dependencia de 1 dev | Media | Alto | Documentacion. Si sale, freeze. |
| App password fragil | Alta | Critico | OAuth principal. |
| **Cobranza terceros sin base** | **Alta** | **Critico** | **Fuera de E2.5 hasta dictamen escrito (no "o limitar").** |
| **Gold_samples del cliente, no tuyos** | **Media** | **Medio** | **Propiedad resuelta en DPA.** |

### 4.3 Kill criteria

1. E1a no cierra semana 2 -> congelar.
2. E1b no cierra semana 4 -> congelar.
3. Edit rate >=60% en 30 drafts -> replantear.
4. 1 incidente de envio equivocado -> pausar.
5. E2.5 <3/10 pago -> E4b no existe.
6. 1 fuga en trazas -> stop.
7. Compliance no cerrado en E0.5 -> no tocar correo real.
8. Injection falla (fijas o red-team critico) -> no tocar correo real.
9. **transfer_basis PII sin decidir -> no sale PII a proveedor US.**

---

## 5. Presupuesto, costos y ROI (v4 - matematica corregida)

### 5.1 Infra (mensual)

| Item | Costo |
|---|---|
| KVM 8 | ~$30/mes |
| Dominio + DNS | ~$15/ano |
| Backblaze B2 | ~$5/mes |
| Langfuse | $0 (free tier) |
| LLM API E2 | $30-50/mes |
| **Subtotal infra E2** | **~$75-105/mes** |

### 5.2 CAPEX de construccion (one-time, E0-E2, ~9-11 semanas)

| Concepto | Calculo | Costo |
|---|---|---|
| Alejandro full-time | ~35h/sem x 10 sem | ~350h |
| Costo dev | a $15-25/h (CR) | ~$5,300-8,800 |
| CEO build/curacion | 8-10h/sem x 9 sem a $50/h | ~$3,600-4,500 |
| Herramientas/setup | one-time | ~$200 |
| **CAPEX total de build** | | **~$9,100-13,500** |

### 5.3 ROI y payback (honesto, corregido)

El error de v3 fue mezclar CAPEX mensual con un "breakeven mes 4-6" imposible. La cuenta real:

- **Beneficio recurrente (hipotesis a confirmar en E0):** ahorro CEO 4h/sem x $50/h x 4 = ~$800/mes + ingreso E2.5 $39 x 3 = ~$117/mes = **~$917/mes bruto**.
- **Costo recurrente post-build:** infra ~$105/mes + mantenimiento dev ~5h/sem (~$300-500/mes) = **~$405-605/mes**.
- **Neto recurrente:** ~$917 - ~$505 = **~$412/mes** (en el escenario optimista del ahorro).
- **Breakeven sobre el CAPEX (~$11,300 medio):** $11,300 / $412 = **~27 meses.** En escenario conservador (ahorro CEO menor o E2.5 sin pago) puede no haber breakeven interno nunca.
- **ROI a mes 12:** **negativo.** A mes 24-27: recien cero. Solo positivo despues, y solo si el ahorro CEO real (medido en E0) sostiene el supuesto.

**Conclusion sin maquillaje:** como herramienta interna, FaberLoom NO se paga en menos de ~2 anos, y posiblemente nunca solo con uso interno. El "mes 4-6" de v3 y el "10x" de v1 eran ambos falsos. La justificacion de construir es **estrategica** (capacidad de IA propia + opcion SaaS via E2.5 + moat de datos), no un retorno financiero interno. E0 mide el ahorro real ANTES de gastar las 350h; si el ahorro es menor a ~4h/sem, el caso interno se cae y todo depende de E2.5.

### 5.4 Atencion semanal

| Rol | Horas |
|---|---|
| Alejandro (dev) | 35h |
| CEO | 8-10h |
| Agentes IA (Claude Code) | 5-10h |

---

## 6. Posicionamiento, moat y competencia

### 6.1 Tesis

**FaberLoom es "copiloto de backoffice comercial B2B": RFQs, cobranza (post-dictamen), seguimiento, con memoria por cliente y aprobacion humana.**

| ChatGPT directo | FaberLoom |
|---|---|
| No conectado a tu correo | OAuth IMAP + SMTP |
| No conectado a tu catalogo | KB con grounding + cita |
| Precio puede ser inventado | Precio 100% trazado a lista. 0 inventados. |
| No sabe quien es tu cliente | Memoria por cliente (mejora con uso) |
| Sin aprobacion humana | HITL obligatorio |
| Sin evidencia | Evidence bundle SHA-256 |
| Generico | RFQs/cobranza/seguimiento B2B LATAM |
| Sin loop de mejora | Gold samples (hipotesis de moat, a medir) |

### 6.2 Moat (hipotesis a confirmar, no hecho)

**Tesis:** "cada draft aprobado mejora el siguiente; un competidor arranca de cero." Se mide con `gold_sample.improvement_score`. **No esta probado**: el few-shot desde gold samples se aplana, y hay que ver si edit_distance baja de verdad por cliente con el uso. Si improvement_score no baja en E2, no hay foso y hay que decirlo.
**Riesgo de propiedad:** los gold_samples derivan de data del cliente. En SaaS pueden ser del cliente, no de FaberLoom. La clausula de propiedad va en el DPA (E0.5); sin eso, el moat no bloquea al competidor si el cliente se lleva su data.

### 6.3 Competidores reales (ancla de WTP en E2.5)

| Alternativa | Costo | Debilidad vs FaberLoom |
|---|---|---|
| ChatGPT/Claude + copy-paste | $20/mes | Sin integracion, sin HITL, sin memoria, precio inventable |
| Asistente humano | $500-1,000/mes | Lento, error humano, sin 24/7, turnover |
| Nada (CEO lo hace) | $0 directo | Tiempo del dueno, fatiga, error |
| CRM + plantillas | $200-500/mes | Plantillas estaticas, no genera ni aprende |

**Precio:** $39/mes es ancla, no dato. WTP se mide en E2.5 preguntando antes de anclar. El pitch no es "mas barato que ChatGPT" (no lo es): es "no manda precios mal, ya esta cableado a tu operacion, y aprobas antes de enviar".

---

## 7. Checklist go/no-go antes de E0

- [ ] Alejandro confirmo >=35h/sem por escrito (o CEO acepta ~5 meses).
- [ ] 30 casos reales identificados (10 RFQ, 10 cobranza, 10 seguimiento).
- [ ] KVM 8 provisionado.
- [ ] Repo GitHub privado, acceso Alejandro.
- [ ] Docker Compose base testeado.
- [ ] 10 PYMEs prospectos para E2.5.
- [ ] Abogado/contacto legal para MX y para transfer_basis identificado.
- [ ] **CEO entiende que el breakeven interno es ~27 meses (posiblemente nunca solo interno); la decision de construir es estrategica, no financiera.**
- [ ] Este plan leido y aprobado (o corregido post-auditoria 4ta ronda).

---

## 8. Glosario

(Igual que v3, + transfer_basis.)

| Termino | Definicion |
|---|---|
| SpaceLoom | Canvas universal. En E1a: 1 chat, 1 workspace. |
| WorkLoom | Mesa HITL. Kanban 4 columnas en E2. |
| StackLoom | Cola epistemica. Diferido a E3 (si >=30 drafts). |
| SkillSpec | Markdown + tools allowlist + schema JSON. |
| Tier 0 | Procesamiento deterministico pre-LLM. |
| Evidence bundle | SHA-256 immutable. |
| Gold sample | Draft aprobado reusable. Base del moat (hipotesis). |
| HITL | Human-in-the-loop. |
| RLS | Row Level Security. |
| PolicyGate | Gate propio fail-closed antes de LiteLLM. |
| WTP | Willingness to pay, medido en E2.5. |
| RPO/RTO | 24h / 4h. |
| edit_distance | % caracteres editados. Mide calidad y moat. |
| transfer_basis | Base legal de transferencia internacional de datos. |

---

## 9. Documentos relacionados

- `docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v3.md` - plan anterior (superseded al firmarse)
- `docs/faberloom/AUDIT_PLAN_DESARROLLO_FABERLOOM_v3.md` - auditoria 3ra ronda (8.0/10)
- `docs/faberloom/PROMPT_AUDITORIA_3RA_RONDA.md` - prompt 3ra ronda
- `docs/anexos/mockups/faberloom_shell_mock_v4_15.html` - mock UI CANONICO (referencia visual, no mandato de E1; staging + deltas en `docs/anexos/mockups/INDEX_v4_15.md`). Supersede v4_13.

---

*v4 aplica las 4 correcciones de la 3ra auditoria (8.0/10): breakeven con matematica real (~27 meses, no mes 4-6), transferencia transfronteriza de PII abierta como decision legal (transfer_basis), DeepSeek fuera de PII, cobranza a terceros fuera de E2.5 hasta dictamen, gates subidos (diff >=6/10, precios 100%, movil usuarios reales), moat marcado como hipotesis. Dos puntos quedan [PENDIENTE - decision CEO/abogado]: la base de transferencia y el dictamen de cobranza. Objetivo: >=9.2 con esas dos decisiones cerradas y E0 + spike corridos.*
> SUPERSEDED 2026-06-22 por PLAN_DESARROLLO_FABERLOOM_v5 (4ta ronda + despliegue dual). Conservado como historico.
