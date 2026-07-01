# VISIÓN UX FABERLOOM — Propuesta para discusión y auditoría externa

**Autor:** Claude + Álvaro
**Fecha:** 2026-04-18
**Estado:** DRAFT — pendiente auditoría externa por ChatGPT
**Propósito:** Definir information architecture, user flows, wireframes textuales y objetivos por vista ANTES de pasar a Design.

---

## 0. Objetivos globales del producto (antes de UX)

| # | Objetivo | Métrica |
|---|---|---|
| 1 | El cliente entiende qué hace el sistema en ≤60 segundos de primera visita | Time-to-first-meaningful-action |
| 2 | Un Operator cierra una cotización 3× más rápido que sin FaberLoom | Tiempo RFQ→cotización |
| 3 | El Owner ve el ROI explícito en pantalla, sin armar Excel | Usage vs cap + ahorro estimado en hero billing |
| 4 | Un agente no actúa solo sin evidencia visible del unlock | 0 casos de autonomía sin rubric verde |
| 5 | Cualquier output es auditable hasta su fuente original en ≤2 clicks | Linked evidence navegable |
| 6 | Un Admin arma un workflow nuevo sin escribir código en ≤30 min | Template-to-first-run time |
| 7 | La factura del mes es comprensible sin llamada a soporte | 0 tickets "no entiendo mi factura" |

---

## 1. Roles y permisos (jerarquía)

```
Tenant Owner (CEO cliente)          [crea/paga/controla org entera]
  └── Admin (líder departamento)    [crea workflows, gestiona equipo]
       └── Operator (rep comercial) [ejecuta, aprueba drafts asignados]
            └── Viewer (auditor)    [solo lectura, logs y facturas]

[Fuera del tenant]
FaberLoom Staff                      [multi-tenant support, no mockup v1]
```

**Permisos por rol:**

| Acción | Owner | Admin | Operator | Viewer |
|---|---|---|---|---|
| Ver billing | ✅ | ❌ | ❌ | ✅ (read-only) |
| Invitar usuarios | ✅ | ✅ (solo su área) | ❌ | ❌ |
| Crear workflow | ✅ | ✅ | ❌ | ❌ |
| Modificar policy engine | ✅ | ❌ | ❌ | ❌ |
| Aprobar draft | ✅ | ✅ | ✅ (solo asignados) | ❌ |
| Flipear Copilot→Autopilot | ✅ | ✅ (si workflow califica) | ❌ | ❌ |
| Ver logs de ejecución | ✅ | ✅ (su área) | ✅ (sus runs) | ✅ |
| Conectar canales (Gmail, CRM) | ✅ | ❌ | ❌ | ❌ |

**Overrides granulares sobre el rol:** límite de aprobación monetaria (ej. Operator Juan aprueba hasta $10K, arriba requiere Admin). Esto vive en el Admin Panel.

---

## 2. Information Architecture global

### 2.1 Sidebar izquierda (navegación persistente)

```
┌────────────────────────┐
│ 🔷 FABERLOOM           │ ← logo + tenant selector (dropdown si multi-org)
├────────────────────────┤
│ 📥 Bandeja          12 │ ← tareas/drafts pendientes (número = badge)
│ ⚙️  Workflows           │ ← builder + runs
│ 🤖 Agentes              │ ← console por agente
│ 📚 Conocimiento         │ ← KB multi-tenant
│ 🔌 Conexiones           │ ← integraciones
├────────────────────────┤ ← separador visual
│ 👥 Equipo               │ ← Admin+ only
│ 💳 Facturación          │ ← Owner only
│ ⚙️  Configuración       │
└────────────────────────┘
         [avatar usuario]   ← menu user: perfil, log out
```

### 2.2 Sidebar derecha (contextual, cambia por vista)

| Vista | Panel derecho |
|---|---|
| Bandeja | Detalle del draft seleccionado + actions |
| Workflows | Config del nodo o run seleccionado |
| Agentes | "Qué usó / Por qué / Siguiente" + unlock progress |
| Chat (cliente) | Linked evidence del output actual |
| Equipo | Drawer de usuario seleccionado (tabs: rol, permisos, workflows, canales, historial) |
| Facturación | Ninguno (vista 1 columna) |

### 2.3 Header global (top bar)

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Distribuidora Seguridad SA ▾]    🔍 Buscar...       🔔  [Alvaro ▾] │
└──────────────────────────────────────────────────────────────────────┘
```

Solo visible si el usuario pertenece a múltiples orgs (FaberLoom staff o clientes multi-tenant).

---

## 3. Patrón mental elegido: "Workflows = procesos"

Hay 3 frames posibles para describir a los agentes al usuario B2B industrial:

| Frame | Ventaja | Desventaja |
|---|---|---|
| **Procesos** (elegido) | Intuitivo para industriales (piensan en SOPs) | Menos sexy |
| Empleados | Narrativa "AI employee" popular | Se confunde con "agente" individual, humaniza de más |
| Canales | Técnicamente preciso | Demasiado abstracto para non-tech |

**Consecuencia del frame:**
- **Workflow** = proceso (cotización B2B, follow-up, reconciliación)
- **Agente** = ejecutor que vive dentro del proceso (research_agent, writer_agent, inventory_agent)
- **Canal** = I/O (Gmail, Pipedrive, WhatsApp, webhook)

**Prohibido usar:** "AI employee", "autonomous colleague", "digital worker". Sí usar: "proceso automatizado", "agente", "tarea pendiente de aprobación".

---

## 4. Vistas a diseñar (4, no 3)

Con tu señalamiento del admin + billing, la lista queda:

| # | Vista | Rol principal | Objetivo |
|---|---|---|---|
| 1 | **Workflow Builder + Runs Ledger** | Admin | Configurar y monitorear procesos automatizables |
| 2 | **Agent Console con toggle Copilot/Autopilot** | Operator/Admin | Unlock de autonomía progresiva con evidencia visible |
| 3 | **Admin Panel — Orgs, Usuarios, Permisos** | Owner | Estructurar organización con jerarquía clara |
| 4 | **Billing & Usage** | Owner | Ver qué se paga y por qué en ≤60 segundos |

**NO diseñamos en este lote:** Chat cliente (es 1 input + response, no amerita mockup propio), Shadow Mode capture (se embebe en Agent Console tab "Aprendiendo"), Linked Evidence standalone (se embebe en cada output).

---

## 5. User Flows críticos

### Flujo A — Primer día del Tenant Owner (Onboarding)

```
1. Signup (email + password)
    ↓
2. "Bienvenido. ¿Cómo se llama tu empresa?"
   → "Distribuidora Seguridad SA"
    ↓
3. Empty state dashboard con 3 CTAs grandes:
   [Conectá un canal] [Invitá un usuario] [Importá un proceso]
    ↓
4. Wizard: conexión Pipedrive + Gmail (OAuth)
    ↓
5. "Detectamos que manejás RFQs de calzado seguridad.
    ¿Usamos el template 'Cotización B2B'?"
   [Sí, usarlo] [No, vacío]
    ↓
6. Shadow Mode onboarding:
   "Antes de que el agente actúe solo, que te observe 3-5 cotizaciones reales."
   → captura próximas 5 cotizaciones que hagas en Pipedrive
    ↓
7. Dashboard activo con contador "3/5 cotizaciones observadas · 1ra promoción en 2 días"
```

**Fricción intencional:** no dejás que el sistema actúe solo el día 1. El Shadow Mode es el onboarding, no feature opcional.

### Flujo B — Día típico del Operator

```
1. Login → Bandeja con N tareas pendientes
    ↓
2. Click en tarea "Cotización Cementos Argos — draft pendiente"
    ↓
3. Side panel derecho se abre con:
   - Draft del email al cliente
   - Linked Evidence chips: [Catálogo Goliath 2025 p.12] [RFQ original] [Política descuentos]
   - Botones fijos: [Aprobar] [Editar] [Rechazar]
    ↓
4. Si edita inline → modal al guardar:
   "¿Esta corrección es recurrente o puntual?"
   [Puntual] [Recurrente · crear gold sample candidate]
    ↓
5. Vuelve a Bandeja con 1 menos
```

### Flujo C — Admin monitoreando Workflow

```
1. Sidebar → Workflows → click "Cotización B2B"
    ↓
2. Vista split:
   - Izquierda 60%: DAG canvas con nodos y estados
   - Derecha 40%: lista últimos 20 runs (tabla)
    ↓
3. Click en run #142 → panel inferior expande con timeline:
   ⏱ 14:23 Email RFQ recibido (trigger)
   ✅ 14:23 extraer_specs (4.2s · $0.003)
   ✅ 14:24 verificar_stock (2.1s · $0.001)
   ⏸ 14:24 generar_cotizacion → awaiting_approval
   ✅ 14:26 approved por María
   ✅ 14:26 send_quote (enviado a argos@cemex.com)
    ↓
4. Click en cualquier nodo → muestra inputs, outputs, tool traces, cost
```

### Flujo D — Owner ajustando permisos

```
1. Sidebar → Equipo
    ↓
2. Tab "Usuarios": tabla con todos los users + rol badge + última actividad
    ↓
3. Click usuario "María González (Operator)"
    ↓
4. Drawer derecho abre con tabs: Overview · Permisos · Workflows · Canales · Historial
    ↓
5. Tab Permisos:
   - Rol: Operator (base permissions de su rol)
   - Overrides:
     ☑ Puede aprobar cotizaciones hasta $ [10,000] USD
     ☐ Puede ver facturación
     ☑ Puede enviar directamente sin Admin approval (si workflow en Autopilot)
    ↓
6. Tab Workflows: checklist de workflows asignados
    ↓
7. Save → notificación + audit log entry
```

### Flujo E — Owner revisando factura

```
1. Sidebar → Facturación
    ↓
2. Hero: "Abril 2026 · 312/500 runs · 62% del plan ($199/mes)"
   Progress bar con proyección fin de mes
    ↓
3. Alerta si proyección >100%: "A este ritmo llegás a 540 runs. ¿Upgrade?"
    ↓
4. Breakdown por workflow (cards):
   - cotización_argos · 142 runs · $67 · ⚠ 92% de cap interno
   - follow_up_pipeline · 98 runs · $34
   - ...
    ↓
5. Breakdown por agente (usage relativo):
   - research_agent · 60% compute
   - writer_agent · 25%
   - inventory_agent · 15%
    ↓
6. Historial 6 meses (tabla: mes · runs · monto · factura PDF)
    ↓
7. Settings: cambiar plan · método pago · dirección fiscal · email facturación
```

---

## 6. Wireframes textuales detallados (las 4 vistas)

### 6.1 Workflow Builder + Runs Ledger

```
┌─────────┬──────────────────────────────────────────────┬─────────────┐
│SIDEBAR  │ Header: Cotización B2B · v0.7.3 · L2 🟢      │ PANEL DER.  │
│         │ [Copilot|Autopilot] ← toggle, Autopilot gray │             │
│ Bandeja │ Unlock: L3 req 50 samples (34/50) + 95% prec │ [Node sel:  │
│Workflows│                                              │  generar_   │
│ Agentes │ ┌──────────────────────────────────────────┐ │  cotización]│
│   KB    │ │         🕐 Trigger: email RFQ          │ │             │
│Conexion │ │              ↓                         │ │ Tabs:       │
│         │ │  ┌─────────────────┐                   │ │ [Config]    │
│ Equipo  │ │  │ extraer_specs   │ 🟢                │ │ [Prompt]    │
│Facturac │ │  │ research_agent  │                   │ │ [Tools]     │
│ Config  │ │  │ 🔧 pipedrive,   │                   │ │ [HITL]      │
│         │ │  │    drive        │                   │ │ [Policy]    │
│         │ │  └────────┬────────┘                   │ │             │
│         │ │           ↓                            │ │ HITL:       │
│         │ │  ┌─────────────────┐                   │ │ ◉ Approval  │
│         │ │  │ verificar_stock │ 🟢                │ │   required  │
│         │ │  │ inventory_agent │                   │ │ ○ Auto run  │
│         │ │  │ 🔧 sheets       │                   │ │ ○ Agent     │
│         │ │  └────────┬────────┘                   │ │   decides   │
│         │ │           ↓                            │ │             │
│         │ │  ┌─────────────────┐                   │ │ Tools:      │
│         │ │  │ generar_cotizac │ 🟡 ← seleccionado │ │ ✓ drive_read│
│         │ │  │ writer_agent    │                   │ │   🟢 safe   │
│         │ │  │ 🔧 drive,mail   │ ⚠ financial_impact│ │ ✓ send_mail │
│         │ │  └────────┬────────┘                   │ │   🟠 $impact│
│         │ │           ↓                            │ │             │
│         │ │  ┌─────────────────┐                   │ │             │
│         │ │  │ send_quote      │                   │ │             │
│         │ │  └─────────────────┘                   │ │             │
│         │ │                                         │ │             │
│         │ │ [+ Add node]  [Test run]  [History]    │ │             │
│         │ └──────────────────────────────────────────┘ │             │
│         │                                              │             │
│         │ ─── Runs (últimos 20) ──────── [▼ expand]   │             │
│         │                                              │             │
│         │ Timestamp  │Status│Duration│Cost│Approver  │             │
│         │ 14:26 Apr18│  🟢  │ 2m 38s │$0.07│ María   │             │
│         │ 11:02 Apr18│  🟢  │ 3m 12s │$0.09│ Carlos  │             │
│         │ 09:47 Apr18│  🔴  │ 45s    │$0.02│ —       │             │
│         │ ...                                          │             │
└─────────┴──────────────────────────────────────────────┴─────────────┘
```

**Detalles críticos:**
- Toggle Copilot/Autopilot con Autopilot disabled y tooltip progresivo
- Unlock bar debajo del header, siempre visible
- Nodos con risk badge visible (🟢 safe · 🟠 financial · 🔴 legal)
- Expand panel inferior para ver runs históricos (no popup)
- Al click en nodo del canvas → panel derecho cambia al config de ese nodo

### 6.2 Agent Console

```
┌─────────┬──────────────────────────────────────────────┬─────────────┐
│SIDEBAR  │ ← Volver a Agentes                            │ PANEL DER.  │
│         │                                              │             │
│         │ 🤖 writer_agent · L2 🟢                       │ Qué usó:    │
│         │ "Listo y operando · última acción 14:26"    │ 📎 Catálogo │
│         │                                              │    Goliath  │
│         │ [Copilot|Autopilot] ← disabled, tooltip:    │ 📎 Gold     │
│         │  "Requires L3: 50 gold samples (34/50) ·    │    #123     │
│         │   95% precision (91%)"                       │ 📎 Voice    │
│         │                                              │    Profile  │
│         │ Unlock progress (siempre visible):           │             │
│         │ ▓▓▓▓▓▓▓▓░░░░ 68% hacia L3                   │ Por qué:    │
│         │ ├─ gold samples: 34/50  ─ 68%               │ "El cliente │
│         │ └─ precision:   91%/95% ─ 95.8%             │  pidió Goli-│
│         │                                              │  ath 35 y   │
│         │ ─── Actividad reciente ──────────────────── │  la política│
│         │                                              │  Argos per- │
│         │ ┌──────────────────────────────────────────┐│  mite 8% off│
│         │ │ Input: RFQ Cementos Argos              ││                 │
│         │ │ ──────────────────────────────────     ││ Siguiente:  │
│         │ │ Draft (14:26):                         ││ Espera       │
│         │ │                                         ││ aprobación   │
│         │ │ "Estimado Sr. Ruiz, le confirmamos...  ││ de María     │
│         │ │  Goliath 35 · 120 pares · $68/par ..." ││              │
│         │ │                                         ││              │
│         │ │ 📎 evidence: [Catálogo] [RFQ] [Política]││             │
│         │ │                                         ││              │
│         │ │ [✅ Aprobar] [✏ Editar] [❌ Rechazar]  ││             │
│         │ └──────────────────────────────────────────┘│             │
│         │                                              │             │
│         │ ─── Tabs ────────────────────────────────── │             │
│         │ [Consola] [Tareas] [Aprendizaje] [Skills]   │             │
│         │                                              │             │
└─────────┴──────────────────────────────────────────────┴─────────────┘
```

**Detalles críticos:**
- Toggle prominente pero honesto (disabled con razón concreta, no genérica)
- Unlock progress con los 2-3 requisitos desglosados numéricamente
- Cards de output con evidence chips clickables
- Tab "Aprendizaje" embebe Shadow Mode capture y gold samples pending
- Rechazar abre modal con razones tipificadas (no free text)

### 6.3 Admin Panel — Orgs/Usuarios/Permisos

```
┌─────────┬──────────────────────────────────────────────┬─────────────┐
│SIDEBAR  │ Distribuidora Seguridad SA · 12 users · 3 roles            │
│         │                                                             │
│         │ ┌──── Org chart (compacto, top) ──────────┐                │
│         │ │   Owner (Alvaro)                        │                │
│         │ │    ├── Admin (2: Carlos, Diana)        │                │
│         │ │    │    ├── Operator (5)               │                │
│         │ │    │    └── Operator (3)               │                │
│         │ │    └── Viewer (1: contador externo)    │                │
│         │ └─────────────────────────────────────────┘                │
│         │                                                             │
│         │ [Usuarios] [Roles] [Workflows asignados] [Canales]         │
│         │  ─────────                                                  │
│         │                                                             │
│         │ 🔍 Buscar...        Filter: [Todos ▾]    [+ Invitar]       │
│         │                                                             │
│         │ ┌──┬─────────────┬───────────┬──────┬────────┬─────────┐   │
│         │ │  │ Nombre      │ Rol       │ Últ. │ Flujos │ Estado  │   │
│         │ ├──┼─────────────┼───────────┼──────┼────────┼─────────┤   │
│         │ │👤│ María Gonz. │ Operator  │ hoy  │   3    │ activo  │   │
│         │ │👤│ Carlos R.   │ Admin     │ hoy  │  12    │ activo  │   │
│         │ │👤│ Diana M.    │ Admin     │ ayer │   8    │ activo  │   │
│         │ │👤│ Juan P.     │ Operator  │ 3d   │   2    │ ⚠ idle  │   │
│         │ │👤│ contador@   │ Viewer    │ 2sem │   —    │ activo  │   │
│         │ │👤│ nuevo@ema.. │ —         │ —    │   —    │ 📧 inv. │   │
│         │ └──┴─────────────┴───────────┴──────┴────────┴─────────┘   │
│         │                                                             │
└─────────┴─────────────────────────────────────────────────────────────┘

[Al click en María González → drawer derecho 480px]
┌─────────────────────────────────────┐
│ ← María González                    │
│ 👤 maria@distribseg.co              │
│ Operator · Activo · Últ. hoy 14:26  │
│ ─────────────────────────────────── │
│ [Overview] [Permisos] [Workflows]   │
│ [Canales] [Historial]               │
│ ─────────────────────────────────── │
│                                     │
│ PERMISOS                            │
│                                     │
│ Rol base: Operator                  │
│                                     │
│ Overrides:                          │
│  Puede aprobar cotizaciones hasta   │
│  $ [10,000] USD                     │
│  (arriba requiere Carlos o Diana)   │
│                                     │
│  ☐ Puede ver facturación            │
│  ☑ Puede flipear Autopilot en       │
│    workflows que califiquen          │
│  ☐ Puede crear workflows nuevos     │
│                                     │
│ ─────────────────────────────────── │
│ [💾 Guardar cambios]                │
└─────────────────────────────────────┘
```

**Detalles críticos:**
- Org chart visual arriba, no escondido
- Jerarquía visible de un vistazo
- Invitación con estado "pending" (no desaparecida)
- Drawer con tabs, no modal (modal corta el contexto)
- Overrides numéricos + checkboxes, no slider (exactitud)
- Cambios generan audit log entry automático

### 6.4 Billing & Usage

```
┌─────────┬─────────────────────────────────────────────────────────────┐
│SIDEBAR  │  Facturación                                                │
│         │                                                             │
│         │ ┌─────────────────────────────────────────────────────────┐│
│         │ │ ABRIL 2026 · Plan Growth · $199/mes                    ││
│         │ │                                                         ││
│         │ │ 312 / 500 runs  ████████████░░░░░░  62%               ││
│         │ │                                                         ││
│         │ │ Proyección fin de mes: ~498 runs  ⚠ cerca del cap      ││
│         │ │ [Upgrade a Scale · $399 + 2000 runs]                   ││
│         │ └─────────────────────────────────────────────────────────┘│
│         │                                                             │
│         │ ─── Por workflow ─────────────────────────────────────     │
│         │                                                             │
│         │ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│         │ │cotización_argos │  │follow_up_pipe   │  │inventory_sync│ │
│         │ │ 142 runs        │  │ 98 runs         │  │ 72 runs      │ │
│         │ │ $67 este mes    │  │ $34             │  │ $28          │ │
│         │ │ ⚠ 92% cap local │  │ 40% cap local   │  │ 30% cap local│ │
│         │ └─────────────────┘  └─────────────────┘  └─────────────┘ │
│         │                                                             │
│         │ ─── Por agente (distribución compute) ────────────────     │
│         │                                                             │
│         │ research_agent  ██████████████░░░░░░  60%  $78             │
│         │ writer_agent    █████░░░░░░░░░░░░░░░  25%  $32             │
│         │ inventory_agent ███░░░░░░░░░░░░░░░░░  15%  $19             │
│         │                                                             │
│         │ ─── ROI estimado (vs sin FaberLoom) ──────────────────     │
│         │                                                             │
│         │ 312 cotizaciones × ahorro estimado 2.5h/ea = 780h          │
│         │ × $15/h rep comercial = $11,700 equivalente                │
│         │ FaberLoom: $129 (plan + usage)  →  ROI 90×                 │
│         │                                                             │
│         │ ─── Historial ────────────────────────────────────────     │
│         │                                                             │
│         │ Mes    │ Runs │ Monto │ Factura                            │
│         │ Mar 26 │ 278  │ $112  │ [📄 Descargar]                     │
│         │ Feb 26 │ 241  │ $99   │ [📄 Descargar]                     │
│         │ ...                                                         │
│         │                                                             │
│         │ ─── Configuración de facturación ────────────────────      │
│         │                                                             │
│         │ Plan actual: Growth $199/mes  [Cambiar plan]               │
│         │ Método pago: Visa **** 4242   [Actualizar]                 │
│         │ Dirección fiscal: [editar]                                 │
│         │ Email facturación: admin@distribseg.co                     │
│         │ RUT/NIT/RFC: [editar]                                      │
└─────────┴─────────────────────────────────────────────────────────────┘
```

**Detalles críticos:**
- Hero con proyección, no solo mes actual (info accionable)
- Breakdown triple: workflow (qué proceso consume) · agente (qué LLM consume) · ROI (cuánto vale)
- ROI calculado con supuestos visibles, no caja negra
- Historial de 6 meses con PDF descargables
- Settings al final, no al inicio (el cliente consulta más que configura)

---

## 7. Microinteracciones críticas

| Interacción | Comportamiento |
|---|---|
| Hover en nodo DAG | Tooltip con último run: status, duration, cost |
| Click en evidence chip | Side panel con source renderizado (PDF page, email thread, CRM field) |
| Hover en unlock bar | Tooltip expandido con 3 requisitos desglosados y delta |
| Drag node to reorder | Snap grid + líneas guía + shadow |
| Rechazar output | Modal con razones tipificadas (no free-text obligatorio) |
| Aprobar con edición | Modal "¿corrección recurrente o puntual?" → gold sample candidate |
| Toggle Autopilot sin calificar | Shake animation + tooltip + link "Ver qué falta" |
| Invitar usuario | Inline form (no modal), envía email automáticamente |
| Click en run en tabla | Panel inferior expande con timeline (no nueva vista) |

---

## 8. Empty/error/loading states

| Contexto | Estado |
|---|---|
| Workflow Builder sin workflows | 3 templates sugeridos + CTA "Import de Zapier/Make" |
| Admin sin usuarios | "Invitá tu primer Admin" CTA grande centrado |
| Billing primer mes | Hero "$0 acumulado · 0 runs · empezá a usar algún workflow" |
| Error conexión canal | Banner ámbar persistente en top "Pipedrive desconectado · [Reconectar]" |
| Run en progreso | Skeleton en fila de tabla + progress bar animada en nodo activo |
| Agente en Shadow Mode inicial | Tab "Actividad" con placeholder "Observando tus próximas 5 ejecuciones" |
| Workflow sin runs aún | "Aún no hay ejecuciones. [Probar ahora] o esperá al primer trigger" |

---

## 9. Qué NO diseñar (decisiones deliberadas)

- Visual Canvas decorativo tipo Relevance (canvas del DAG lo cumple, no necesitamos el "workforce visualization" con avatares)
- Onboarding video/tour interactivo (overkill para v1; guided CTAs son suficientes)
- Dashboard "todo en uno" home (cada rol tiene su home natural: Operator → Bandeja, Admin → Workflows, Owner → Billing)
- Notificaciones in-app complejas (badge en sidebar basta; email para críticas)
- Dark mode (v2)
- Mobile responsive completo (priorizar desktop; mobile solo para approvals via email link)
- AI recommendations side bar ("te sugerimos..." — generan ruido, no valor en v1)

---

## 10. Paleta y dirección visual (heredada del Design ONE)

- Fondo cálido editorial: #F6F1E8
- Acento profundo: #6E1F2B (vino) para estados críticos y CTAs primarios
- Texto principal: #2A2824
- Texto secundario: #6B6258
- Tipografía títulos: Georgia serif
- Tipografía UI: -apple-system / Inter
- Risk colors: 🟢 #3D8B54 · 🟠 #C47F1E · 🔴 #A83232

Razón de elegir ONE sobre THREE: el ICP (compradores industriales, HSE) compra seriedad. Bold Block es para categorías que venden personalidad (DTC, productividad personal). FaberLoom vende control operativo.

---

## 11. Preguntas abiertas para el auditor UX (ChatGPT)

1. El frame "procesos" vs "empleados" — ¿es correcto para el ICP? ¿Debería testearse con copy alternativo?
2. Toggle Copilot/Autopilot disabled con tooltip — ¿frustra al usuario o educa? ¿Alternativa mejor?
3. Unlock rubric siempre visible en Agent Console — ¿informativa o ruido? ¿Esconder detrás de expand?
4. ROI calculation en Billing — ¿transparente o manipulativo? Supuestos visibles ayudan pero también debilitan la métrica.
5. Org chart en Admin Panel — ¿útil o decorativo? ¿En qué escala (>20 usuarios) deja de funcionar?
6. 4 vistas es mucho para un primer mockup de Design. ¿Prioridad si hay que elegir 2? Mi apuesta: Workflow Builder + Agent Console (son el producto). Admin + Billing pueden esperar 1 iteración.
7. ¿Falta alguna vista crítica que ni Álvaro ni yo nombramos? Candidatos que evalué y descarté: Knowledge Base, Conexiones, Bandeja general, Conversación Chat cliente.

---

## 12. Output esperado del auditor UX

Pedirle a ChatGPT:

- **Sección A — Validación de IA global:** ¿la sidebar/header/patrón mental son correctos? ¿Faltan nodos de navegación?
- **Sección B — Revisión de cada user flow (A-E):** fricciones, pasos de más/menos, alternativas.
- **Sección C — Revisión de cada wireframe (6.1-6.4):** densidad, jerarquía, elementos faltantes/redundantes.
- **Sección D — Microinteracciones:** cuáles agregar, cuáles quitar.
- **Sección E — Empty/error/loading states:** qué falta cubrir.
- **Sección F — Respuesta a las 7 preguntas abiertas de sección 11.**
- **Sección G — Priorización final:** si diseñamos solo 2 vistas para Design, ¿cuáles y por qué?
- **Sección H — Propuesta del prompt a Design:** basado en todo lo anterior, estructura del brief para Claude Design.
