# Plan de Desarrollo Tecnico - FaberLoom / SpaceLoom v5 (Post-4ta auditoria, swarm multi-modelo)

**id:** PLAN_DESARROLLO_FABERLOOM_v5
**version:** 5.0
**status:** DRAFT - listo para ratificacion CEO
**fuente:** PLAN_DESARROLLO_FABERLOOM_v4.md + correcciones 4ta ronda (swarm: ChatGPT 8.3, Qwen 7.8, zcode/GLM 7.4, Kimi 7.3) + reconciliacion con SPEC_FB_BUILD_SEQUENCE_v3 + decision de despliegue dual
**supersede:** PLAN_DESARROLLO_FABERLOOM_v3 y v4 (orden de build, timeline, costos); y el ORDEN/timeline de SPEC_FB_BUILD_SEQUENCE_v3 (ver seccion 0)
**tech stack:** Python (FastAPI) + LiteLLM (lib) + UI web (HTML/CSS/JS). Persistencia abstraida: SQLite/FTS5 (desktop) | PostgreSQL+RLS (web/server)
**despliegue:** dual - desktop instalable Win/Mac (Etapa 1, prioridad) + web/server (etapas posteriores). Mismo motor, mismo UI, distinto envoltorio y storage.
**estimated effort:** ~13-16 semanas a sistema interno real (recalculado con 1 dev); decision SaaS post-E2.5
**dedicacion dev:** Alejandro, objetivo 35h/sem full-time. [PENDIENTE - confirmar % real en E0]. Si <35h, timeline se extiende proporcionalmente.
**dedicacion CEO:** 8-10h/sem (fuente unica; reemplaza el "max 6h" de SPEC_FB_BUILD_SEQUENCE)

---

## 0. Reconciliacion de fuente de verdad (corrige falla de fondo #1 del swarm)

Kimi, Qwen y GLM coincidieron: habia DOS documentos canonicos en conflicto (PLAN_DESARROLLO y SPEC_FB_BUILD_SEQUENCE) en timeline, horas de CEO, decision OAuth vs app password, inicio de E2.5 y duracion de E2. Eso invalida la ejecucion. Este v5 cierra el conflicto:

| Punto en conflicto | SPEC_FB_BUILD_SEQUENCE_v3 | PLAN v4 | DECISION v5 (unica) |
|---|---|---|---|
| Timeline total | ~9 semanas | 12-14 semanas | **13-16 semanas** (recalculado con 1 dev real, ver seccion 5.4) |
| Horas CEO | max 6h/sem | 8-10h/sem | **8-10h/sem** |
| Inbox auth | app password (E2b) | OAuth principal (E1a) | **OAuth principal**; app password solo lab/dev |
| Inicio E2.5 | semanas 2-6 | semanas 5-9 | **arranca despues del gate E1b** (ver E2.5) |
| Duracion E2 | 4-5 semanas | 2 semanas | **4-5 semanas** (la de 2 era irreal con 1 dev) |
| Modalidad E2.5 | "concierge manual, cero plataforma" | "mismo flujo interno" | **mismo flujo interno** una vez exista E1b; concierge manual solo como fallback si E1b se atrasa |

Accion de gobernanza: al indexarse, `SPEC_FB_BUILD_SEQUENCE_v3` queda **superseded en orden/timeline/decisiones tecnicas** por este v5 (su contenido tecnico reutilizable se conserva como referencia, no como mandato). Nota de supersede en su changelog, sin borrar (Regla 3 KB).

---

## 1. Que cambia vs v4 (correcciones de la 4ta ronda)

| Hallazgo del swarm (quien) | Correccion v5 |
|---|---|
| Despliegue: empezo web, se orienta a desktop, debe correr en ambos (CEO) | **Arquitectura dual** desde dia 1: motor unico FastAPI+LiteLLM+UI web; capa de persistencia abstraida (repositorio) SQLite\|Postgres. Etapa 1 = empaque desktop (pywebview/PyInstaller) sobre SQLite. Web/server = mismo motor sobre Postgres+RLS, despues. Ver seccion 2. |
| E1a en 1 semana imposible con 1 dev (ChatGPT, Kimi, Qwen, GLM) | **E1a partido en E1a-Base (infra+DB+auth+audit+backup) y E1a-Mail (OAuth+inbox+clasificacion+movil).** Ver E1a. |
| E0.5 mezcla legal con tecnico, 1 semana irreal (todos) | **E0.5 partido en E0.5a-Legal (con abogado, ~2 sem, bloqueante) y E0.5b-Seguridad (~1 sem, dev+CEO).** Ver E0.5. |
| Grounding "85%" maquillable sin rubrica (ChatGPT, Qwen) | **Evaluador de grounding por assertion**: campos criticos enumerados, cada uno fuente exacta o falla. Ver E1b y 4.4. |
| E2.5 "pagan algo" es debil; $5-10 mide curiosidad (ChatGPT, Qwen, GLM) | Gate E2.5 endurecido: **pago recurrente >=2 ciclos o LOI/compromiso escrito con precio**, + uso activo semana 1 y 2. Amigos/testers no cuentan. |
| E0 puede sesgarse con casos "bonitos" (ChatGPT) | **Muestreo mecanico** (ultimos N por clase, no a mano) + **10 casos holdout congelados** que el dev no ve. |
| Kill criteria incoherentes con duraciones (Kimi) | Kill criteria reescritos **relativos al inicio real de cada etapa**, alineados a las nuevas duraciones. Ver 4.3. |
| CAPEX inconsistente: $3-5K vs $2.1-3.5K calculado (Kimi) | **Costo de Alejandro unificado** en una sola cifra derivada (35h x tarifa) en toda la seccion 5. |
| Gate E1b depende de un prospecto E2.5 que aun no existe (Kimi, GLM) | **Prospecto removido del gate E1b**; E1b valida con CEO + operador + 1 tester interno. La metrica con prospecto se mide en E2.5. |
| E4a nombrada, no disenada (todos) | **E4a con duracion, tareas y gate propio.** Ver E4a. |
| Salto 2->5 roles sin diseno intermedio (GLM) | **Progresion de roles 2->3->4->5 mapeada** a E1/E3/E4a/E4b. Ver E4. |
| WhatsApp "diferido a Meta" sin fecha (GLM) | **Fecha limite o kill explicito**: no entra en 2026 salvo tramite cerrado; corre en paralelo no bloqueante. |
| Moat afirmado/medido pero sin umbral que lo niegue (GLM) | **Umbral de falsacion del moat declarado**: si edit_distance no baja >=X% tras N>=10 drafts del mismo cliente, no hay foso y se dice. Ver 6.2. |
| E2 mezcla skill tecnico con payback (ChatGPT, Kimi) | E2 separado: **2a tecnico, 2b operativo; el payback es semaforo go/replan**, no entregable que maquilla progreso tecnico. |
| Dependencia E0->E1b: el baseline Claude no lo producia ninguna etapa (GLM) | Ya en v4: E0 produce los 10 baselines Claude-crudo. Se mantiene y se marca como gate de E0. |

Lo que NO cambia (decisiones de fondo ya correctas en v4): breakeven honesto (~27 meses, ver 5.3), transferencia PII como decision legal abierta (`transfer_basis`), DeepSeek fuera de PII, cobranza a terceros fuera de E2.5 hasta dictamen, injection como control continuo, HITL obligatorio.

---

## 2. Stack tecnico y arquitectura (despliegue dual)

### 2.1 Principio: un motor, dos envoltorios

```
                  +-------------------------------------------+
                  |  MOTOR (identico en ambos despliegues)    |
                  |  FastAPI + LiteLLM(lib) + PolicyGate       |
                  |  UI web (HTML/CSS/JS) servida por el motor |
                  |  Capa de repositorio (interfaz de datos)  |
                  +----------------+--------------------------+
                                   |
              +--------------------+----------------------+
              |                                           |
   +----------v-----------+                   +-----------v------------+
   | DESKTOP (Etapa 1)    |                   | WEB / SERVER (post)    |
   | pywebview/PyInstaller|                   | Docker + Caddy         |
   | SQLite + FTS5        |                   | PostgreSQL 16 + RLS    |
   | single-user local    |                   | multi-usuario/tenant   |
   | WebView2 / WKWebView |                   | Redis + Celery         |
   +----------------------+                   +------------------------+
```

Clave: la **capa de repositorio** (patron repository/port) aisla el resto del codigo del motor de almacenamiento. El dominio habla con interfaces (`DraftRepo`, `KBRepo`, `AuditRepo`...), no con SQL directo. Implementaciones: `SqliteRepo` (desktop) y `PostgresRepo` (server). Esto evita quemar el camino a web sin pagar el costo de Postgres en desktop.

### 2.2 Desktop (Etapa 1, prioridad)

- Empaque: **pywebview + PyInstaller** (recomendado, 100% Python, sin Rust/Node; ver SPEC_SPACELOOM_SELFHOSTED_v1.3). Tauri solo si despues se quiere bajar peso. Electron descartado.
- Datos: **SQLite + FTS5** (full-text local). Sin embeddings en Etapa 1.
- Single-user, local-first. Sin multi-tenant, sin nube.
- Aislamiento = por workspace dentro del archivo local (no RLS; el sellado por scope se aplica en la capa de repositorio).
- Backup: export local cifrado + copia a destino del usuario (Backblaze B2 opcional). RPO/RTO definidos por el usuario; default diario.

### 2.3 Web / server (etapas posteriores, condicional a E2.5)

- Docker Compose: caddy, web, api, worker(Celery+Redis), postgres, redis.
- **PostgreSQL 16 con RLS** por tenant_id desde el dia 1 del despliegue server (no antes; en desktop no aplica).
- KVM 8 (Hostinger) o equivalente.
- Tenant isolation tests por tabla sensible.

### 2.4 Implicacion de la dualidad en compliance (importante)

El pivote a **desktop local-first ATENUA pero no elimina** el problema de transferencia transfronteriza de PII:
- En desktop, la PII del cliente **vive en la maquina del usuario** (SQLite local), no en un server en US. Eso reduce la superficie de transferencia.
- PERO los **prompts** que se mandan al LLM (OpenAI/Anthropic, US) siguen pudiendo contener PII. La base legal de esa transferencia (`transfer_basis`) sigue siendo necesaria para lo que sale al LLM. La redaction/seudonimizacion antes de salir a US se vuelve la mitigacion principal en desktop.
- Conclusion: el `[PENDIENTE - transfer_basis]` de E0.5a sigue vigente, pero su alcance en desktop se limita a "que se manda al LLM", no "donde vive la base de datos".

### 2.5 Dependencias clave (motor)

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
litellm==1.40.0          # como libreria, no proxy
pydantic==2.7.0
python-multipart==0.0.9
pypdf==4.2.0
openpyxl==3.1.0
markdown-it-py==3.0.0
# desktop:
pywebview==5.x
pyinstaller==6.x
# server (post): sqlalchemy[async], alembic, asyncpg, redis, celery
```

---

## 3. Secuencia de milestones

> Duraciones recalculadas con 1 dev a 35h/sem y buffer del ~25% (correccion Kimi/Qwen). Cada duracion supone dedicacion confirmada; si Alejandro es <35h/sem, todo se extiende proporcionalmente.

### E0 - Dataset de verdad (1 semana, CEO + Cowork, cero codigo)

(Antes "3 dias"; subido a 1 semana por realismo y para incluir holdout.)

- [ ] **Muestreo mecanico:** ultimos N correos/RFQs/cobranzas/seguimientos reales por clase, NO elegidos a mano (anti-sesgo, correccion ChatGPT). Definir "caso valido".
- [ ] 30 casos: 10 RFQ, 10 cobranza, 10 seguimiento. Si una sola clase tiene volumen real, **aceptar reducir scope explicitamente** (correccion Qwen), no inflar.
- [ ] Tabla de verdad por caso: input real, respuesta ideal, datos requeridos, fuente de verdad, tiempo manual cronometrado, hash del input, fecha de origen, categoria.
- [ ] **Split train/holdout:** 20 train / **10 holdout congelados** que el dev no ve (correccion ChatGPT). El holdout solo se usa para evaluar en E1b/E2.
- [ ] **Baseline Claude-crudo** para los 10 candidatos: output de Claude sin KB, archivado (insumo del gate E1b; corrige dependencia rota detectada por GLM).
- [ ] Baseline de tiempo del CEO por clase (alimenta ROI real, seccion 5).
- [ ] **[PENDIENTE - confirmar dedicacion Alejandro >=35h/sem por escrito]** como gate externo previo, no como deliverable del CEO (correccion Kimi).

**Gate de salida:** 30 casos (o scope reducido firmado) con tiempos + hash + split versionado; 10 baselines Claude-crudo archivados; dedicacion Alejandro confirmada.
**Kill:** no hay casos reales suficientes -> no hay problema que resolver -> detener.

---

### E0.5a - Legal (paralela, ~2 semanas, CEO + abogado, bloqueante)

(Antes mezclada con seguridad en "1 semana". Separada por irrealismo y riesgo legal real - todos los modelos.)

- [ ] **PRODHAB (CR), Ley 8968:** registro de base de datos. Cada item con estado explicito: aprobado / pendiente / bloqueado / no aplica (no "aprobado por CEO" como sello vacio - correccion ChatGPT/Kimi).
- [ ] **Guatemala:** criterio legal local. Nota: GT puede no tener marco integral equivalente; un checklist no sustituye dictamen local. Estado explicito.
- [ ] **Colombia:** checklist equivalente (CO aparece en E2.5 y v4 no lo cubria - correccion Qwen).
- [ ] **Mexico:** LFPDPPP (vigente desde 2025). **Bloqueo real**, no nota decorativa: no procesar PII MX hasta DPA + aviso + responsable legal.
- [ ] **Transferencia internacional de PII (`transfer_basis`):** definir la base para lo que sale al LLM en US. Opciones: (a) consentimiento informado, (b) clausulas contractuales, (c) solo redaction/seudonimizacion antes de salir. **Eleccion concreta: [PENDIENTE - decision CEO/abogado].** Sin esto, no sale PII a proveedor US.
- [ ] **DPA template** (prospectos E2.5) con **clausula de propiedad de gold_samples** derivados de data del cliente.
- [ ] **Aviso de privacidad.** **Politica de retencion/borrado** por data_class (soft + hard delete).
- [ ] **Dictamen de cobranza a terceros: [PENDIENTE - dictamen legal escrito]** (interes legitimo documentado + origen del dato + opt-out). Sin dictamen, cobranza fuera de E2.5.

**Evidencia (no "firmado por CEO"):** carpeta `/compliance/evidence/` con comprobante PRODHAB/estado, dictamen breve por pais, screenshots DNS, DPA versionado, aviso, matriz proveedor/pais/data_class, y decision por jurisdiccion: allowed / restricted / blocked.

**Gate E0.5a:** transfer_basis decidido (o PII bloqueada hasta decidir); estado legal explicito por pais con evidencia; dictamen cobranza presente o cobranza excluida en firme.

### E0.5b - Seguridad (paralela, ~1 semana, dev + CEO; puede solapar E1a-Base)

- [ ] **Matriz data_class** (DeepSeek = NINGUNO para todo data_class con PII; disponible solo para metadata anonimizada):
  | data_class | country | provider_allowed | storage | retention | redaction | dpa | legal_basis | transfer_basis |
  |---|---|---|---|---|---|---|---|---|
  | PII_cliente | CR/GT/CO | openai,anthropic | local(desktop)/us-east-1(server) | 7 anos | si | si | [PENDIENTE] | [PENDIENTE] |
  | precios | CR | openai,anthropic | local/us | 3 anos | no | no | ejecucion_contrato | n/a |
  | facturas | CR | openai,anthropic | local/us | 10 anos | no | si | obligacion_legal | [PENDIENTE] |
  | metadata | CR | openai,anthropic | local/us | 1 ano | si | no | legitimo | n/a |
  | email_raw | CR | NINGUNO | local | 30 dias | si | no | legitimo | n/a |
- [ ] **Defensa injection:** separar contenido de instrucciones; allow-list de acciones; nunca auto-send sin HITL.
- [ ] **Injection como control continuo (no gate de una vez):** 10 tests fijos (100% bloqueados) + red-team abierto. **Re-correr en cada cambio de prompt/skill** (idealmente en CI). Log de "ultima corrida limpia" con fecha.
- [ ] **SPF/DKIM/DMARC** verificado antes del primer SMTP (aplica al despliegue que envie correo). Warm-up.
- [ ] **Langfuse redaction:** metadata + hashes por defecto. **Prueba de trazas sin PII:** 10 trazas, 0 PII = pass.
- [ ] **Restore test:** backup de ayer restaurado en <4h (server) / export-import verificado (desktop).

**Gate E0.5b:** injection 100% fijas + 0 critico red-team con harness minimo; 0 PII en 10 trazas; restore/export probado; SPF/DKIM/DMARC verificado.
**Kill:** injection falla -> no tocar correo real. transfer_basis sin decidir -> no sale PII a US.

---

### E1a-Base - Fundacion tecnica (1 semana, dev)

**Solo motor + datos + auth + audit + backup. Sin correo, sin OAuth de terceros.**

- [ ] Esqueleto FastAPI + UI web servida por el motor. Capa de repositorio con interfaces de dominio.
- [ ] **SqliteRepo** (desktop) operativo. Migrations/seed. (PostgresRepo se difiere al despliegue server.)
- [ ] Empaque desktop minimo: pywebview abre la app en ventana nativa (hola-mundo de la UI real).
- [ ] Auth local: sesion httpOnly, 2 roles (Owner/Operator). 2FA solo Owner.
- [ ] Audit log append-only (metadata only).
- [ ] Backup/export local + restore probado.
- [ ] PolicyGate propio antes de LiteLLM (fail-closed). LiteLLM solo ejecuta y traza.

**Gate E1a-Base:** app desktop abre nativa; CRUD basico persiste en SQLite; audit registra; restore/export probado; PolicyGate bloquea data_class no permitida (test).

### E1a-Mail - Conectores reales (1 semana, dev)

**Correo y movil separados de la base, para no mezclar seguridad de cimientos con conectores.**

- [ ] **Inbox OAuth:** IMAP via OAuth (un solo proveedor primero: Gmail O Microsoft, no ambos a la vez). Polling. App password solo lab.
- [ ] Clasificacion minima primero: spam / no-spam. Ventas/cobranza/soporte se afinan en E1b/E2 (correccion GLM, recortar alcance).
- [ ] SpaceLoom base: 1 chat, 1 workspace, sin KB. Solo modo Operar.
- [ ] **Responsive movil:** login, navegacion, inbox visible desde movil (sin aprobacion de draft todavia).

**Gate E1a-Mail:** correo real entra via OAuth, se clasifica spam/no-spam, queda auditado; OAuth sin app password; pantalla movil cargable (login/navegacion/inbox).
**Kill:** si al cierre de la semana 3 (desde inicio de E1a-Base) los dos sub-gates de E1a no estan -> congelar 90 dias, horas a Rana Walk/B2B.

---

### E1b - Draft Engine + KB minima + HITL (2-3 semanas, dev)

(Antes "1-2 sem"; subido por realismo: incluye parsers, HITL, salida, evaluador de grounding.)

- [ ] KB pipeline: upload PDF/Excel/MD, parser, chunker 1000/200, **FTS5** (desktop). Sin embeddings.
- [ ] Draft Engine: 1 skill generico (SkillSpec markdown). Timeout 30s. Cost cap $0.50. Sin HTTP externo, sin code exec.
- [ ] HITL minima: 3 botones (Aprobar/Editar/Rechazar). Campo "por que rechazaste" obligatorio. `edit_distance` + `time_to_approve_sec` automaticos.
- [ ] Canal de salida: SMTP manual, doble confirmacion (no auto-send hasta E2).
- [ ] Gold samples: captura automatica con `source_draft_id`.
- [ ] **Evaluador de grounding por assertion** (corrige metrica maquillable - ChatGPT/Qwen): cada assertion de campo critico (precio, SKU, descuento, lead time, condicion de pago, cliente, destinatario, pais, moneda, vencimiento) se mapea a fuente exacta o **falla** (hard fail). Reporte por draft: assertion -> fuente -> pass/fail.

**Gate E1b:**
1. **Diff vs Claude:** edicion <20% en **>=6/10** tareas del holdout E0 (o reduccion agregada sobre las 10), corrido contra el baseline archivado.
2. **Grounding campos criticos = 100% pass (hard fail si no); prosa >=85% con cita.** 0 precios/condiciones inventados.
3. Tiempo login->draft aprobado <2 min (desktop).
4. **Aprobacion movil <=45s con CEO + operador + 1 tester INTERNO** (prospecto removido del gate - correccion Kimi/GLM).
5. 20 drafts reales, >=70% aprobados con edit_distance <20%.
6. 0 destinatarios incorrectos. Tiempo promedio <=20% del baseline E0.

**Kill:** E1b no cierra a 3 semanas de su inicio -> congelar.

---

### E2 - Sistema de skills + trazabilidad (4-5 semanas, dev)

(Subido de 2 a 4-5 sem; coincide con SPEC_FB_BUILD_SEQUENCE. Payback separado del entregable tecnico.)

**Hito 2a - tecnico (sem 1-2 de E2):**
- [ ] Engine ejecutor generico (SkillSpec versionado).
- [ ] Skill 1: RFQ/cotizacion. Skill 2: seguimiento (clase distinta). **Cobranza NO entra hasta dictamen (E0.5a).**
- [ ] Tier 0 deterministico del primer skill real.
- [ ] Evidence bundle SHA-256 immutable.

**Hito 2b - operativo (sem 3-4 de E2):**
- [ ] Client map: seed + freemail list + triage.
- [ ] WorkLoom: cola por estado (TU CRITERIO / ESPERANDO / DELEGADO / ERROR).
- [ ] Trazas redacted. Verificacion manual 10 trazas/semana.
- [ ] Aprendizaje minimo: CTA "Indexar esto" + cola.
- [ ] Savings ledger: costo real vs baseline E0; tokens por clase; bloquear prompts >N tokens sin resumen.

**Payback (semaforo, no entregable que maquilla):** actualizado semanalmente con cifras reales. Verde si neto recurrente sostiene el supuesto de E0; rojo/replan si el ahorro real < ~4h/sem CEO. Ver 5.3.

**Gate E2:**
1. >=10 outputs reales cliente-facing aprobados/enviados, **denominador coherente** (medir edit rate sobre los mismos >=10, no "ultimos 20" sobre 10 - correccion Qwen), >=2 clases.
2. Edit rate <40% (edit_distance).
3. Reduccion de tiempo con cronometro >=5x vs baseline E0.
4. Costo IA por tarea aprobada <USD 0.35.
5. Cero incidentes de envio equivocado. 0 fugas en trazas (10 trazas).
6. **Moat:** `improvement_score` medido. Umbral de falsacion (ver 6.2): si no baja, se declara que no hay foso.

**Kill:** edit rate >=60% en 30 drafts -> congelar.

---

### E2.5 - Validacion comercial (arranca tras gate E1b; CEO 2h/sem + operador)

**Mismo flujo interno (no concierge), una vez exista E1b. Solo CR/GT/CO. MX bloqueado. Cobranza a terceros FUERA hasta dictamen.**

- [ ] Oferta a 10 PYMEs B2B NO-amigas (lista nominal en el go/no-go; correccion GLM): agente para RFQ y seguimiento. Aprueban todo antes de enviar.
- [ ] **Pago real, no intencion verbal** (correccion ChatGPT/Qwen/GLM): cobro recurrente >=2 ciclos O LOI/compromiso escrito con precio objetivo y uso minimo. $5-10 simbolico solo como filtro inicial, NO como evidencia de WTP.
- [ ] Medir WTP preguntando antes de anclar $39. Anclar vs alternativas reales (seccion 6).
- [ ] Registro por prospecto: uso sem 1, uso sem 2, **abandono tras semana 2**, reaccion a precio, objeciones textuales, precio aceptado.
- [ ] **Regla de muestra incompleta:** definir que pasa si solo se consiguen 5-6 prospectos (correccion GLM), no asumir 10.

**Gate (decide E3):**
- >=4/10 usan 2 semanas seguidas Y >=3/10 con **pago recurrente o LOI firmado** -> E3 con esos como design partners.
- Si no -> E3 NO se construye. Queda herramienta interna (desktop single-user), re-evaluar en 6 meses.

---

### E3 - Workspaces / el lente (2-3 semanas, condicional a E2.5 + E2 cerrado)

**Gate doble (correccion Qwen): E2 cerrado tecnicamente Y E2.5 con >=3 pago.**

- [ ] My/Shared workspaces; scope bar visible, salida a global en 1 click; herencia de anatomia SpaceLoom; historial contextual; CTA indexar default L3.
- [ ] Roles: progresion 2->3 (agregar rol de invitado/lectura si E2.5 lo pide).
- [ ] **Plan B declarado (correccion GLM):** si <30 drafts -> sin StackLoom; si <2 operadores -> sin Admin. Entregar workspaces + scope bar igual sigue siendo E3 valido.

**Gate E3:** operar 2+ cuentas reales puramente desde workspaces 1 semana + **leakage test por workspace** + recuperacion de contexto correcta + reduccion de busqueda vs global (no solo "navegar sin volver al global" - correccion ChatGPT).

---

### E4 - Multi-usuario y multi-tenant (progresion de roles explicita)

**Progresion de roles (corrige salto 2->5 sin diseno - GLM):**
- E1: 2 roles (Owner, Operator).
- E3: +1 (Invitado/lectura) si E2.5 lo pide.
- E4a: confirmar 3 roles internos con delegacion.
- E4b: +2 (Admin tenant, SuperAdmin) = 5, solo en multi-tenant.

**E4a - Multi-usuario interno (1-2 semanas, sin gate comercial):**
- [ ] Membresia; invitaciones; columna Delegado en WorkLoom; lock optimista con timeout; reasignacion de draft; ownership de draft; auditoria de edicion; matriz Owner/Operator/Invitado.
- [ ] **Gate E4a:** 2 operadores activos usando la columna Delegado 1 semana real, sin fuga de datos entre ellos (pruebas RBAC + concurrencia).

**E4b - Multi-tenant externo (CON gate E2.5; despliegue server/Postgres):**
- [ ] **Gate previo de viabilidad (correccion Qwen/GLM)** antes de disenar: security review, aislamiento tenant probado, export/delete de tenant, incident response, soporte.
- [ ] Design partners pagos, onboarding, DPA firmado (clausula gold_samples), 5 roles, pricing vs WTP.
- [ ] **WhatsApp Business API:** fecha limite o kill (correccion GLM). No entra en 2026 salvo tramite Meta cerrado; corre en paralelo, no bloquea.
- [ ] Solo si E2.5 dio >=3 con pago. Si no, E4b no existe.

---

### E5 - Amplitud post-validacion (parking lot, no se disena)

APIs abiertas, MCP, segundo vertical, Agent/Skill Factory, Voice Profile completo, arena/eval, Knowledge River L3+, tiers Enterprise. **Bloqueado explicitamente:** nada de E5 entra a E0-E2.5 sin gate nuevo (correccion ChatGPT). Se disena recien al cerrar E4b.

---

## 4. Criterios de calidad y riesgos

### 4.1 Quality gates

| Etapa | Gate | Metrica | Umbral |
|---|---|---|---|
| E0 | Dataset + holdout + baseline | casos + split + Claude-crudo | 30 (o scope reducido), 10 holdout, 10 baselines |
| E0.5a | Legal con evidencia | estado por pais + transfer_basis | decidido o PII bloqueada |
| E0.5b | Seguridad | injection + trazas + restore | 100% fijas, 0 PII, restore ok |
| E1a-Base | Motor+datos+auth | app desktop + persistencia + audit | funcional |
| E1a-Mail | OAuth + movil | correo entra + movil cargable | sin app password |
| E1b | Diff vs Claude | edicion <20% sobre holdout | >=6/10 |
| E1b | Grounding criticos | assertion->fuente | 100% pass (hard fail) |
| E1b | Aprobacion movil | usuarios internos | <=45s, CEO+operador+tester |
| E2 | Outputs reales | count + clases | >=10, >=2 |
| E2 | Edit rate | edit_distance (denominador coherente) | <40% |
| E2 | Moat | improvement_score | medido + umbral de falsacion |
| E2.5 | Pago real | recurrente o LOI | >=3/10 |
| E3 | Workspace util | leakage + reduccion busqueda | gate doble E2+E2.5 |
| E4a | Multiusuario | RBAC + concurrencia | 2 operadores 1 sem, 0 fuga |
| E4b | Viabilidad multi-tenant | aislamiento + export/delete | probado antes de disenar |

### 4.2 Riesgos (nuevos/cambiados vs v4 en negrita)

| Riesgo | Prob | Impacto | Mitigacion |
|---|---|---|---|
| Alejandro no full-time | Media | Critico | Confirmar en E0 (gate externo). Si <35h, extender. |
| **Sub-estimacion de tiempos (1 dev)** | **Alta** | **Critico** | **Duraciones recalculadas + buffer 25% + kill relativos a inicio de etapa.** |
| Prompt injection | Alta | Critico | 10 tests + red-team + control continuo. Nunca auto-send. |
| **Transferencia PII a US** | **Media** | **Critico** | **transfer_basis (lo que va al LLM) decidido en E0.5a; redaction; desktop local reduce superficie.** |
| Cobranza terceros sin base | Alta | Critico | Fuera de E2.5 hasta dictamen escrito. |
| Dato comercial equivocado | Media | Critico | Grounding por assertion 100% campos criticos. HITL. |
| **Adopcion E2.5 (10 PYMEs reales)** | **Alta** | **Alto** | **Lista nominal en go/no-go + regla de muestra incompleta + pago real.** |
| **Dualidad desktop/web duplica esfuerzo** | **Media** | **Alto** | **Capa de repositorio unica; server se difiere a post-E2.5; no se construyen dos productos a la vez.** |
| Moat no existe | Media | Medio | Umbral de falsacion en E2; si no baja edit_distance, se dice. |
| Fuga en trazas | Media | Critico | Metadata-only. 10 trazas/sem. |
| CEO sobre-suscrito | Alta | Critico | 8-10h/sem. Low-risk a Alejandro. |
| Dependencia de 1 dev | Media | Alto | Documentacion. Si sale, freeze. |

### 4.3 Kill criteria (relativos al inicio real de cada etapa - correccion Kimi)

1. **E1a (Base+Mail) no cierra a 3 semanas de su inicio -> congelar 90 dias.**
2. **E1b no cierra a 3 semanas de su inicio -> congelar.**
3. Edit rate >=60% en 30 drafts -> replantear.
4. 1 incidente de envio equivocado -> pausar, revisar clasificador.
5. E2.5 <3/10 con pago real -> E4b no existe; queda interno.
6. 1 fuga en trazas -> stop, revisar pipeline de logging.
7. E0.5a sin transfer_basis decidido -> no sale PII a US; no se toca correo real con PII.
8. Injection falla (fijas o red-team critico) -> no tocar correo real.
9. Ahorro real CEO medido en E0 < ~4h/sem y E2.5 sin pago -> el caso interno se cae; decision estrategica explicita de seguir o no.

### 4.4 Definicion de "assertion" para grounding (anti-maquillaje)

Una assertion es cualquier afirmacion verificable en un draft. Se separan:
- **Campos criticos** (hard fail si no trazan a fuente exacta): precio, SKU, descuento, lead time, condicion de pago, cliente, destinatario, pais, moneda, vencimiento.
- **Prosa explicativa** (>=85% con cita de chunk): redaccion, cortesia, contexto.

El gate no acepta "cito un chunk cualquiera y parezco grounded". Cada campo critico -> fila exacta de la KB o falla.

---

## 5. Presupuesto, costos y ROI

### 5.1 Infra

- **Desktop (Etapa 1):** ~$0 server. LLM API uso interno ~$10-20/mes. Backup destino del usuario.
- **Server (post-E2.5):** KVM ~$30/mes + Backblaze ~$5 + LLM $30-50 = ~$75-105/mes.

### 5.2 CAPEX de construccion (one-time, E0-E2, ~11-13 semanas)

| Concepto | Calculo | Costo |
|---|---|---|
| Alejandro | 35h/sem x ~12 sem = ~420h a $15-25/h (CR) | **~$6,300-10,500** |
| CEO build/curacion | 8-10h/sem x ~12 sem a $50/h | ~$4,800-6,000 |
| Herramientas/setup | one-time | ~$200 |
| **CAPEX total** | | **~$11,300-16,700** |

(Cifra de Alejandro **unificada y derivada** en toda la seccion; se elimina el "$3,000-5,000/mes" suelto de v4 que no cuadraba - correccion Kimi.)

### 5.3 ROI y payback (honesto)

- **Beneficio recurrente (hipotesis, confirmar en E0):** ahorro CEO ~4h/sem x $50 x 4 = ~$800/mes + ingreso E2.5 $39 x 3 = ~$117/mes = **~$917/mes bruto**.
- **Costo recurrente post-build:** infra (desktop ~$15 / server ~$105) + mantenimiento dev ~5h/sem (~$300-500) = **~$315-605/mes**.
- **Neto recurrente:** ~$917 - ~$460 = **~$457/mes** (escenario optimista).
- **Breakeven sobre CAPEX (~$14,000 medio):** ~30 meses. Conservador: puede no haber breakeven solo interno.
- **ROI a mes 12:** negativo. Recien cero a ~mes 30, y solo si el ahorro CEO real sostiene el supuesto.

**Conclusion sin maquillaje:** como herramienta interna, FaberLoom NO se paga en <~2.5 anos, y posiblemente nunca solo interno. La justificacion de construir es **estrategica** (capacidad IA propia + opcion SaaS via E2.5 + moat a confirmar), no retorno financiero interno. **E0 mide el ahorro real ANTES de gastar las ~420h.**

### 5.4 Timeline consolidado (1 dev)

| Semana | Track tecnico | Track legal/comercial |
|---|---|---|
| 1 | E0 dataset + baseline + holdout | confirmar 10 prospectos nominales |
| 2-3 | E0.5b seguridad / inicio E1a-Base | E0.5a legal (con abogado), bloqueante |
| 3 | E1a-Base | E0.5a cierre |
| 4 | E1a-Mail -> gate E1a | - |
| 5-7 | E1b -> gate E1b | - |
| 7-8 | (E2.5 arranca con E1b vivo) | E2.5 ofertas + medicion |
| 8-12 | E2 (hitos 2a/2b) -> gate E2 | E2.5 cierre -> gate E2.5 |
| 13-15 | E3 (si gate doble) | decision design partners |
| 16+ | E4a / E4b condicional | - |

Total a sistema interno: ~12-13 semanas. A decision SaaS si/no: ~semana 8-9.

---

## 6. Posicionamiento, moat y competencia

### 6.1 Tesis

**FaberLoom/SpaceLoom es copiloto de backoffice comercial B2B: RFQs, seguimiento, cobranza (post-dictamen), con memoria por cliente, grounding trazado y aprobacion humana. Corre como app de escritorio (single-user) y, si E2.5 valida, como servicio web multi-tenant.**

### 6.2 Moat (hipotesis con umbral de falsacion)

Tesis: "cada draft aprobado mejora el siguiente". Se mide con `gold_sample.improvement_score`.
**Umbral de falsacion (correccion GLM):** si tras **N>=10 drafts aprobados del mismo cliente** el `edit_distance` promedio **no baja al menos 30%** vs los primeros 3, **no hay foso** y se declara explicitamente. El moat deja de afirmarse como hecho hasta que el dato lo confirme en E2.
**Propiedad:** gold_samples derivan de data del cliente; en SaaS pueden ser del cliente. Clausula en DPA (E0.5a).

### 6.3 Competidores (ancla de WTP en E2.5)

| Alternativa | Costo | Debilidad vs FaberLoom |
|---|---|---|
| ChatGPT/Claude + copy-paste | $20/mes | Sin integracion, sin HITL, sin memoria, precio inventable |
| Asistente humano | $500-1,000/mes | Lento, error humano, sin 24/7 |
| Nada (CEO lo hace) | $0 directo | Tiempo del dueno, fatiga, error |
| CRM + plantillas | $200-500/mes | Plantillas estaticas, no genera ni aprende |

**Precio:** $39/mes es ancla, no dato. WTP se mide en E2.5. Pitch: "no manda precios mal, ya esta cableado a tu operacion, y aprobas antes de enviar."

---

## 7. Checklist go/no-go antes de E0

- [ ] [PENDIENTE] Alejandro confirmo >=35h/sem por escrito (o CEO acepta ~5 meses).
- [ ] 30 casos reales por muestreo mecanico (o scope reducido firmado), con holdout.
- [ ] Abogado/contacto legal identificado para transfer_basis, cobranza y MX.
- [ ] 10 PYMEs prospectos **nominales** para E2.5 + regla si solo hay 5-6.
- [ ] Repo privado, acceso Alejandro. Spike desktop (pywebview hola-mundo) testeado.
- [ ] CEO entiende: breakeven interno ~30 meses (posiblemente nunca solo interno); la decision de construir es estrategica.
- [ ] Decision de gobernanza: carve-out del SPEC freeze para CONSTRUIR (DEC_FB_SPACELOOM_FREEZE_SCOPE) ratificada.
- [ ] Este plan leido y aprobado.

---

## 8. Glosario

(Igual que v4, + dual deployment.)

| Termino | Definicion |
|---|---|
| Capa de repositorio | Interfaz de datos que aisla el dominio del storage (SQLite\|Postgres). |
| SpaceLoom | Canvas universal single-user. En desktop = el producto Etapa 1. |
| WorkLoom | Mesa HITL. Kanban por estado en E2. |
| StackLoom | Cola epistemica. Diferida a E3 (si >=30 drafts). |
| SkillSpec | Markdown + tools allowlist + schema JSON. |
| Tier 0 | Procesamiento deterministico pre-LLM. |
| Evidence bundle | SHA-256 immutable. |
| Gold sample | Draft aprobado reusable. Base del moat (hipotesis con umbral). |
| HITL | Human-in-the-loop. |
| transfer_basis | Base legal de transferencia internacional de datos al LLM. |
| Assertion | Afirmacion verificable en un draft; campos criticos = hard fail. |

---

## 9. Documentos relacionados

- `docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v4.md` - plan anterior (superseded por este v5 al firmarse).
- `docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md` - orden/timeline superseded por seccion 0 de este v5; contenido tecnico reutilizable se conserva.
- `docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.3.md` + `SPEC_SPACELOOM_ETAPA1_v1.md` - base del despliegue desktop (Etapa 1).
- `docs/faberloom/DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md` - decision de carve-out del freeze (pendiente ratificacion CEO).
- `docs/faberloom/AUDIT_SPACELOOM_ETAPA1_STRESS_v1.md` - stress test del diseno single-user contra casos reales.
- 4ta ronda de auditoria (swarm): ChatGPT 8.3, Qwen 7.8, zcode/GLM 7.4, Kimi 7.3. ID corrida AUD-FB-PLAN-V3-R4-20260622.

---

## Changelog

- v5.0 (2026-06-22): 4ta ronda (swarm 4 modelos) + decision de despliegue dual desktop/web. Reconciliada la contradiccion PLAN vs SPEC_FB_BUILD_SEQUENCE (seccion 0, fuente unica). E0.5 partido en legal/seguridad; E1a partido en Base/Mail; E0 con holdout y muestreo mecanico; grounding por assertion; E2.5 con pago real; kill criteria relativos a inicio de etapa; CAPEX unificado; prospecto removido del gate E1b; E4a detallado; progresion de roles 2-5; moat con umbral de falsacion; E2 4-5 sem con payback como semaforo. Dos puntos quedan [PENDIENTE - decision CEO/abogado]: transfer_basis y dictamen de cobranza. No se toco FROZEN ni control_surface.

---

**Stamp:** DRAFT - 2026-06-22 - PENDIENTE ratificacion CEO
**Aprobador final:** CEO (Alvaro) - firma pendiente
