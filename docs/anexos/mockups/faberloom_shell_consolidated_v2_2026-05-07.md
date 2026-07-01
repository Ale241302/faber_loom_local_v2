# FaberLoom · Shell consolidated snapshot v2 · 2026-05-07

**Status:** sketch en iteración (NO canon · pendiente SPEC_FB_CONSOLE_LAYOUT_v1)
**HTML actual:** `docs/anexos/mockups/faberloom_shell_v6.html`
**Sesión:** Cowork 2026-05-07 (continuación de sketch v1)
**Próximo paso:** sketch HTML del WorkLoom (Mesa de Control kanban)

---

## 0. Cómo usar este documento

Este snapshot consolida TODAS las decisiones de iteración del shell de FaberLoom hasta 2026-05-07. Si retomás el trabajo en otro chat:

1. **Leé este documento entero**
2. **Abrí el HTML v6** en navegador para ver el estado visual
3. **Continuá desde sección 19** (Próximos pasos)

Este documento reemplaza al anterior `faberloom_shell_sketch_chat_v1.md` que quedó desactualizado tras la iteración masiva.

---

## 1. Filosofía y reglas duras

### Filosofía madre

```
"La IA prepara. Vos aportás tu criterio."
"Tejé tu trabajo."
```

El shell no trabaja, el workspace trabaja. La herramienta es verbo, el workspace es lugar, el shell es sistema.

Inteligente en comportamiento, silencioso en superficie.

### Reglas duras (heredadas del PROMPT MAESTRO Mesa de Control v4)

1. Header global = búsqueda universal + reloj de aprendizaje. Nada más.
2. El título del workspace vive dentro del workspace.
3. Métricas operativas viven dentro del workspace, no en el shell.
4. Herramientas aparecen por contexto, no como showcase permanente.
5. Evidencia existe, pero no se grita.
6. Coral solo para alarma / acción decisiva.
7. Vino solo para evidence.
8. NO Material Design / Salesforce / HubSpot estética.
9. NO dashboard saturado.
10. NO llenar la pantalla para demostrar profundidad.
11. NO copiar literal mockups previos. SÍ heredar carácter visual.

### Sensación deseada

Apple Mail × Things 3 × Linear × Stripe.

NO debe sentirse: Salesforce × HubSpot × Notion × Material Design × dashboard SaaS saturado.

---

## 2. Familia *Loom · 4 pilares de la marca

```
FaberLoom    marca · brand foot · siempre visible
WorkLoom     Mesa de Control · operar (cross-workspace HITL kanban)
SpaceLoom    home cognitivo · iterar con IA libre (chat con KB tenant)
StackLoom    construir knowledge · apilar capas L0-L4 (curaduría)
```

### Por qué cada *Loom

| *Loom | Origen del nombre | Función | Posición visual |
|---|---|---|---|
| **FaberLoom** | Faber (latín · hacedor) + Loom (telar) = "telar del hacedor" | Marca producto entero | Brand foot del Rail 1 (siempre) |
| **WorkLoom** | Work + Loom = "telar de trabajo" | Donde accionás · feed cross-workspace HITL | Sidebar item bajo "Operar" |
| **SpaceLoom** | Space + Loom = "telar de espacio cognitivo" | Donde iterás con la IA libremente · home | Sidebar item bajo "Operar" |
| **StackLoom** | Stack + Loom = "telar que apila capas" | Donde construís el knowledge como lego · capas L0-L4 son un stack literal | Sidebar item bajo "Administrar/Capacidades" |

### Por qué la metáfora del telar

El telar (loom) evoca:
- Trabajo artesanal cuidadoso
- Tejido construido paciente, hilo a hilo
- Patrón que emerge de la repetición
- Humano + herramienta colaborando
- Producto vs proceso industrial automático

Encaja con el espíritu del producto: "La IA prepara. Vos tejés."

### Decisiones rechazadas en iteración

- **SpaceLoom como reemplazo de Workspace**: rechazado · Workspace ya es estándar SaaS funcional
- **ChatLoom como reemplazo de Chat**: rechazado · Chat es estándar universal. SpaceLoom ocupa ese rol pero con nombre distintivo
- **TypeLoom como reemplazo de Chat**: rechazado · "type" es mecánico, no comunica iteración cognitiva
- **FaberChat como reemplazo de Chat**: rechazado · choca con consistencia *Loom + nombre confuso vs marca
- **BuildLoom como reemplazo de Curaduría**: rechazado a favor de StackLoom (build genérico, stack más preciso)
- **FaberLoom como reemplazo de StackLoom/Curaduría**: rechazado · 3 entidades con mismo nombre = caos

---

## 3. Cross-language · matriz completa

### Términos de la familia *Loom (universales sin traducir)

| Concepto | EN | ES | PT | FR | IT |
|---|---|---|---|---|---|
| FaberLoom | FaberLoom | FaberLoom | FaberLoom | FaberLoom | FaberLoom |
| WorkLoom | WorkLoom | WorkLoom | WorkLoom | WorkLoom | WorkLoom |
| SpaceLoom | SpaceLoom | SpaceLoom | SpaceLoom | SpaceLoom | SpaceLoom |
| StackLoom | StackLoom | StackLoom | StackLoom | StackLoom | StackLoom |

### Términos canon en inglés (se mantienen igual)

| Concepto | EN | Razón |
|---|---|---|
| Workspace | Workspace | Estándar SaaS internacional |
| Inbox | Inbox | Universal |
| Skills | Skills | Término técnico estándar IA |
| Atlas | (no se usa, decidido "Conocimiento") | Reemplazado |

### Términos localizables por idioma del tenant

| Concepto | EN | ES | PT |
|---|---|---|---|
| Mesa de Control (UI WorkLoom) | Control Desk | Mesa de Control | Mesa de Controle |
| Conocimiento (workspace knowledge) | Knowledge | Conocimiento | Conhecimento |
| Agentes | Agents | Agentes | Agentes |
| Fijados | Pinned | Fijados | Fixados |
| Espacios de Trabajo (header) | Workspaces | Workspaces | Espaços de Trabalho |
| Tagline brand | Weave your work | Tejé tu trabajo | Teça seu trabalho |

### HITL / Criterio · terminología completa

**Filosofía**: el user aporta criterio profesional, no aprobación robótica.

| Lugar | EN | ES | PT | FR | IT |
|---|---|---|---|---|---|
| Filter chip / estado | "Awaiting your criteria" | "Esperando tu criterio" | "Aguardando seu critério" | "En attente de votre critère" | "In attesa del tuo criterio" |
| Badge corto card | "YOUR CRITERIA" | "TU CRITERIO" | "SEU CRITÉRIO" | "VOTRE CRITÈRE" | "IL TUO CRITERIO" |
| Configuración (governance) | "Approval criteria" | "Criterio para aprobación" | "Critério para aprovação" | "Critère d'approbation" | "Criterio di approvazione" |
| Subheader WorkLoom | "nerve center · what needs your criteria today" | "centro nervioso · qué necesita tu criterio hoy" | "centro nervoso · o que precisa do seu critério hoje" | (FR) | (IT) |
| Tooltip | "Apply your criteria · AI prepared, you decide how" | "Aplicá tu criterio · la IA preparó, vos decidís cómo" | "Aplique seu critério · a IA preparou, você decide como" | (FR) | (IT) |
| Botón aprobar tal cual | "Approve & send" | "Aprobar y enviar" | "Aprovar e enviar" | (FR) | (IT) |
| Botón aprobar editado | "Edit & send" | "Editar y enviar" | "Editar e enviar" | (FR) | (IT) |
| Botón rechazar | "Reject" | "Rechazar" | "Rejeitar" | (FR) | (IT) |
| Canon SPECs | HITL | HITL | HITL | HITL | HITL |

**Por qué "criterio"**: es más orientado al objetivo HITL. No transaccional como "aprobación". Comunica que el user aporta JUICIO PROFESIONAL.

---

## 4. Tipología de workspaces

Tres tipos según función:

| Tipo | Rol | Ejemplos |
|---|---|---|
| **Operativos** | Donde se TRABAJA | Mwt.one · ws_sondel · ws_industrias_norte · Lab MWT |
| **Visibilidad** | Donde se VE y se NAVEGA al trabajo | WorkLoom (Mesa) · Inbox |
| **Iteración** | Donde se PIENSA con la IA | SpaceLoom (Chat) |

Inbox y WorkLoom **nunca son lugar de resolución**. Son entry points que redirigen al workspace destino donde se opera.

### Workspace polimórfico via vertical_spec_object

Para MWT (vertical safety_footwear): workspace = cuenta cliente B2B.
Para abogado: workspace = caso.
Para estudiante: workspace = curso.
Para freelancer: workspace = cliente/proyecto.

Schema unificado vertical-agnostic. Mismo tab structure (Bandeja · Histórico · KB · Iteración · Configurar · Sanidad).

---

## 5. Layout del shell · 4 paneles + topbar

```
┌──── TOPBAR ──────────────────────────────────────────────────────────────────┐
│ [breadcrumb workspace]    ⌕ Buscar o ejecutar...   [● Aprendizaje · estado] │
│ [tipo · controlled_by]                ⌘K                  [Role ▾]   [◐]    │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ RAIL 1 ────────┬─ RAIL 2 ──────┬─── CANVAS ───────────────┬── RAIL 3 ──────┐
│                 │               │                           │                │
│ Navegación      │ Contextual al │   Contenido del workspace │ Tools          │
│ principal       │ workspace     │   activo                  │ contextuales   │
│ siempre visible │ activo        │                           │ del workspace  │
│ (collapsable    │ (sólo cuando  │                           │ activo         │
│ a 64px)         │ aplica · ej.  │                           │ (4 tabs)       │
│                 │ Conversaciones│                           │                │
│                 │ del SpaceLoom)│                           │ (collapsable   │
│                 │ (collapsable  │                           │ a 44px mini)   │
│                 │ a 44px mini)  │                           │                │
└─────────────────┴───────────────┴───────────────────────────┴────────────────┘
```

### Resize handles entre paneles

- Width handle 6px hairline visible
- Hover: coral 35%
- Drag: coral 100%
- Doble click: reset al ancho default
- Drag con rail colapsado: descolapsa automáticamente
- Cursor: col-resize

### Anchos default y rangos

| Panel | Default | Min | Max |
|---|---|---|---|
| Rail 1 (principal) | 248px | 64px (colapsado) | 360px |
| Rail 2 (contextual) | 240px | 44px (mini con icono) | 360px |
| Canvas | flex | 0 | flex |
| Rail 3 (tools) | 280px | 44px (mini con icono) | 400px |

### Toggle visual

- Iconos SVG sidebar toggle (rectángulo + línea vertical)
- Rail 2 (izquierdo): línea vertical a la izquierda del rectángulo
- Rail 3 (derecho): línea vertical a la derecha del rectángulo (espejo)

---

## 6. Sidebar principal (Rail 1) · estructura final

```
┌─────────────────────────────────────┐
│ [F*] Faber*loom                     │
│      tenant · MWT                   │
│      Tejé tu trabajo                │   ← brand foot tagline
│ ─────────────────────────────────── │
│ [⇤] Colapsar                        │
│                                     │
│ OPERAR                              │   ← header sección
│  ○ Mesa de Control            [3]   │   ← UI: "Mesa de Control" · canon: workloom
│  ○ Inbox                     [12]   │
│  ○ SpaceLoom                        │   ← sin badge (no es cola operativa)
│                                     │
│ WORKSPACES                      +   │   ← concepto múltiple
│                                     │
│  Administrados                      │
│   ○ Mwt.one                         │
│   ○ FaberLoom proyecto        [2]   │
│   ○ Rana Walk                 [1]   │
│                                     │
│  Heredados                          │
│   ○ Industrias del Norte [Crítico]  │
│   ○ Sondel SA                 [3]   │
│   ○ Distribuidora Ramírez     [2]   │
│   ○ Constructoras Alfa        [1]   │
│   ○ Minera Central                  │
│   ○ Lab MWT                   [3]   │
│   ○ Inbox sin asignar        [24]   │
│                                     │
│ ADMINISTRAR                         │
│                                     │
│  Capacidades                        │
│   ○ Skills              [16] +      │
│   ○ Agentes              [7] +      │
│   ○ Conocimiento         [7] +      │
│   ○ StackLoom         [◷ 5]         │
│                                     │
│  Tenant                             │
│   ○ Usuarios y permisos     [12]    │
│   ○ IA: modelos y ruteo             │
│   ○ Audit                           │
│   ○ Configuración tenant            │
│                                     │
│ ─────────────────────────────────── │
│ [AF] Alejandro Faro · OPERATOR  ▾   │
│      ↓ Mi cuenta                    │
│        Mi voz                       │
│        Preferencias                 │
│        Cerrar sesión                │
└─────────────────────────────────────┘
```

### Sistema de badges

| Badge tipo | Significa | Ejemplo |
|---|---|---|
| **Numérico operativo** `[N]` | Items pendientes operativos | Mesa `[3]` · Inbox `[12]` · ws_sondel `[3]` |
| **Coral pill** `[Crítico]` | Urgencia · alta prioridad | Industrias del Norte `[Crítico]` |
| **Numérico inventario** `[N]` | Total disponible (no urgente) | Skills `[16]` · Agentes `[7]` |
| **Reloj** `[◷ N]` | Knowledge a indexar | StackLoom `[◷ 5]` |
| **Sin badge** | No requiere atención | SpaceLoom (cuando no hay sugerencias) |
| **Bajo verde** `[1-3]` | Sugerencias del día | SpaceLoom `[3]` (cuando hay candidatos a curar) |

### Headers de sección · razones

| Header | Por qué |
|---|---|
| **OPERAR** | Agrupa los 3 puntos de operación cotidiana |
| **WORKSPACES** | Concepto múltiple (N instancias) · plural en español funciona |
| **ADMINISTRAR** | Gobernanza del tenant + capacidades |
| Subgroup **Administrados** | Workspaces donde el user es Owner/Admin |
| Subgroup **Heredados** | Workspaces que el user adoptó (es Operator/Viewer) |
| Subgroup **Capacidades** | Skills · Agentes · Conocimiento · StackLoom (lo que se construye) |
| Subgroup **Tenant** | Usuarios · IA · Audit · Configuración (lo que se gobierna) |

---

## 7. Topbar

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ [breadcrumb workspace]                ⌕ Buscar o ejecutar...                      │
│ [tipo · controlled_by]                                ⌘K                          │
│                                                       [● Aprendizaje · atento · 5◷]│
│                                                                  [Operator ▾] [◐] │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Solo 5 elementos:**
1. Breadcrumb (línea 1: nombre · línea 2: tipo + controlled_by)
2. Command bar `⌘K` (sistema nervioso · Raycast/Linear style)
3. Reloj de aprendizaje universal
4. Role switcher (dev · cambio rápido de rol)
5. Theme toggle

**NO hay**: logo, avatar, métricas, notificaciones, breadcrumb pesado, accesos rápidos.

### Estados del reloj de aprendizaje

```
[● Aprendizaje · al día · 12d]              salvia (sin pendientes)
[● Aprendizaje · atento · 5◷]               ámbar (1-9 niveles a indexar)
[● Aprendizaje · bloqueado · 14◷ revisar]   coral (10+ pendientes o conflicto)
```

**El reloj es exclusivamente de KNOWLEDGE A INDEXAR**. NO es indicador operativo general.

Click en el reloj → panel desplegable con desglose:

```
Reloj de aprendizaje
Estado · atento

Knowledge a indexar:
 - 3 candidatos en StackLoom
 - 1 conflicto de fuente
 - 1 promoción L4→L2 esperando Owner

Templates sin congelar: 3
Próximo freeze: 18 días

[Abrir StackLoom →]
```

---

## 8. Rail 2 contextual · Conversaciones del SpaceLoom

Aparece SOLO cuando el workspace activo es SpaceLoom. En otros workspaces el Rail 2 puede no aparecer o mostrar contenido contextual distinto.

```
┌──────────────────────────────┐
│ Conversaciones      [⊟ tog]  │   ← header con título + toggle SVG
│                              │
│ [+ Nueva conversación]       │
│                              │
│ Fijados (3)                  │
│  ◉ Voice MWT banned phrases  │
│  ◉ Política descuentos       │
│  ◉ Plantilla follow-up B2B   │
│                              │
│ Hoy                          │
│  ○ Industrias Norte 09:14    │
│  ○ Glossary safety MX 11:30  │
│  ○ Sondel renovación 14:02   │
│                              │
│ Ayer                         │
│  ○ Deep research diel.       │
│                              │
│ Esta semana (5)              │
│  ↪ ver todas                 │
└──────────────────────────────┘
```

Colapsable a 44px (mini con solo el icono toggle visible para reabrir).

---

## 9. Sidepanel derecho (Rail 3) · 4 tabs minimalistas

```
┌──────────────────────────────────┐
│ [⊟ toggle]                       │   ← header con toggle SVG espejo
├──────────────────────────────────┤
│ [Agentes][Skills][Conocim●][Wks] │   ← 4 tabs
├──────────────────────────────────┤
│                                  │
│ Conocimiento                     │
│ 19 contextos disponibles         │
│                                  │
│ Propios (7)                      │
│  ◉ Voice MWT              L4     │
│  ◉ Histórico Sondel       L3     │
│  ◉ Política descuentos    L2 ◷   │
│  ◉ Plantilla follow-up    L2     │
│  ◉ Replay set Q1          L4     │
│  ◉ Notas Industrias       L4     │
│  ◉ Glosario minería       L1     │
│                                  │
│ Heredados (12)                   │
│  ○ Catálogo BC-7240       L1     │
│  ○ Normas EPP LATAM       L0     │
│  ○ Banned phrases tenant  L2     │
│  ○ Voice tenant MWT       L2 ◷   │
│  ○ Replay safety_footwear L1     │
│  ○ Política LFPDPPP       L0     │
│  ○ Glosario comercial     L2     │
│  ↪ ver todos (5 más)             │
│                                  │
│ [+ Crear]  [⎘ Adoptar]            │
│                                  │
│ ────────────────────────────     │
│ ◷ 5 niveles a indexar            │
│  ─ 3 candidatos en StackLoom     │
│  ─ 1 conflicto de fuente         │
│  ─ 1 promoción L4→L2 pending     │
└──────────────────────────────────┘
```

### Principios del sidepanel derecho

- **Minimalista**: solo nombre del item + alerta sutil
- **Sin metadata operativa** (no versión, no uso, no tipo, no operator)
- **Detalle vive en el workspace** correspondiente cuando hacés click
- **Solo Conocimiento usa `◷`** (knowledge a indexar)
- **Otros tabs usan `[●]`** para alertas operativas genéricas
- **Counts numéricos NO se duplican** del sidebar izquierdo
- **Siempre colapsable** a 44px mini

### Comportamiento de cada tab

| Tab | Default sort | Acciones | Alertas |
|---|---|---|---|
| Agentes | Propios → Heredados | + Crear · ⎘ Adoptar | `[●]` agente con métrica baja · iterar |
| Skills | Propios → Heredados | + Crear · ⎘ Adoptar | `[●]` skill con SHADOW pending · uso anómalo |
| Conocimiento | Propios → Heredados (agrupados por L0-L4) | + Crear · ⎘ Adoptar | `[◷]` candidato a curar · conflicto fuente |
| Workspace | Administrados → Heredados | + Crear · ⎘ Adoptar | `[●]` workspace nuevo sin config |

---

## 10. Avatar foot dropdown · personal

```
[AF] Alejandro Faro · OPERATOR  ▾

  ┌──────────────────┐
  │ Mi cuenta        │
  │ Mi voz           │
  │ Preferencias     │
  │ ─────────────    │
  │ Cerrar sesión    │
  └──────────────────┘
```

Personal del user. Separado claramente del scope organizacional.

---

## 11. Knowledge en 5 capas · L0-L4

```
L0 · Mundo (cima · más institucional)         leyes, normas externas
L1 · Vertical                                  terminología sector, jurisprudencia
L2 · Tenant                                    voice MWT, políticas, catálogos
L3 · Workspace                                 histórico cliente, estilo cliente
L4 · Usuario (base · más íntimo)               sabor user, learning HITL personal
        ↑
   nuevas piezas entran acá
   suben capa por capa con curación (StackLoom)
```

### Quién cura cada capa

| Capa | Curador | Visibilidad |
|---|---|---|
| L0 Mundo | FaberLoom system | Cross-tenant lectura |
| L1 Vertical | FaberLoom + tenants con DPA | Cross-tenant del vertical |
| L2 Tenant | Owner/Admin del tenant | Tenant entero |
| L3 Workspace | Operator asignado | Workspace + imports declarados |
| L4 Usuario | El propio user | Solo el user, escalable |

---

## 12. SpaceLoom · home cognitivo

### Vista del SpaceLoom

```
SpaceLoom
home cognitivo · KB tenant · contexto auto-detect

[Input chat con placeholder "Pregunta o pedí algo. @workspace para fijar scope."]
[mention: contexto @ws_industrias_norte | 4 fuentes KB | Sonnet 4.6]
[tokens: ↑ 12,450 ↓ 8,320 | ≈ USD 0.087]

Sugerencias del día:
 → Curar 3 candidatos pending en StackLoom
 → Iterar voice MWT con 4 términos sectoriales nuevos
 → Continuar deep research mercado dieléctrico LATAM (en curso, día 2)

[divider]

09:14 · @ws_industrias_norte
"¿Cómo cerramos el follow-up de Industrias del Norte?"
   → contexto: ws_industrias_norte (cuenta gold)
   → KB consultada: histórico cliente · voice MWT · políticas comerciales
   → modelo: Sonnet 4.6 (vía Routing Inheritance)

[Respuesta IA con contenido relevante]

┌──────────────────────────────────────────────┐
│ ◷ Esto puede valer la pena indexar           │
│   "4 términos sectoriales nuevos detectados" │
│   contexto sugerido: L1 vertical             │
│   [Indexar a L1] [Más tarde] [No]            │
└──────────────────────────────────────────────┘

Acciones sobre la respuesta:
 → Promover a workspace
 → Guardar como contexto fijado
 → Crear borrador en ws_industrias_norte
 → Iterar (refinar pregunta)
```

### CTA inline indexar · cuándo aparece

Trigger heurístico del sistema agente cuando detecta candidato:
- ≥N términos sectoriales nuevos
- ≥M mensajes sobre proceso/política
- mención explícita de regla/template

Acciones:
- `Indexar a L1/L2/L3` → abre creator inline con conversación pre-poblada
- `Más tarde` → cola StackLoom (no se pierde)
- `No` → signal para mejorar heurística

### SpaceLoom global vs Tab Iteración dentro de workspace

**Misma anatomía visual, distinto scope.**

| | SpaceLoom global | Tab Iteración en ws_sondel |
|---|---|---|
| Breadcrumb | "SpaceLoom" | "Sondel SA › Iteración" |
| Mention default | vacío (user opcional) | `@ws_sondel` pre-fijado |
| Conversaciones del rail | TODAS del user | Solo scoped a ws_sondel |
| Sidepanel derecho | Catálogo completo tenant | Filtrado a items del workspace |
| CTA indexar | Modal con opciones L1/L2/L3/L4 | Default L3 ws_sondel directo |

---

## 13. Inbox · agregador de N cuentas conectadas

### Filosofía

> "El Inbox no es otra bandeja de correo. Aprende qué ignorar, qué resumir, qué convertir en tarea y qué abrir en Workspace."

### 5 categorías auto-detectadas

| Categoría | Significa | Acción default |
|---|---|---|
| **Accionables** | Requiere decisión humana o resolución HITL | Click → resolver (jump al workspace destino) |
| **Resumen diario** | Info útil sin acción inmediata · agrupable | Resumen agrupado al final del día |
| **Leído oculto** | Ya visto, archivar silenciosamente | Auto-archive en histórico |
| **Auto-borrar** | Spam evidente · sin valor | Papelera con audit |
| **Agente** | El agente puede manejar autónomamente | Auto-respuesta si está dentro del scope |

### Cuentas conectadas (sidepanel derecho del Inbox)

```
POR BANDEJA · 4 cuentas conectadas

VENTAS    Ventas MWT          ventas@muito.work       3 correos · todos accionables
CEO       Buzón CEO           alvaro@muito.work       3 correos · 1 recurrente útil
PER       Personal            sjoalfaro@gmail.com     3 correos · 2 NL + 1 spam
LIC       Licitaciones        licitaciones@muito.work 1 correo  · cliente nuevo platinum
```

Cada cuenta tiene su propio agente `@mail_X` conectado.

### Tipos de cuenta

| Tipo | Quién recibe digest | Quién puede crear/editar |
|---|---|---|
| Personal del user | Solo el owner | Solo el owner |
| Organizacional | Todos los users con acceso | Cualquier user con acceso (audit) |

### Resúmenes activos · capacidad declarativa del agente

**No es categoría pasiva**. Es flujo activo del agente de comunicación que el user instruye.

```
USER instruye al agente de comunicación
       ↓
AGENTE intercepta correos que matchean la regla
       ↓
EXTRAE información relevante de cada uno
       ↓
ACUMULA durante la ventana (día, semana, etc.)
       ↓
SINTETIZA en UN solo output al final
       ↓
ENTREGA el digest al user
       ↓
AUTO-BORRA los originales (audit · recuperables 7d)
       ↓
APRENDE de qué leyó el user, qué editó, qué ignoró
```

Schema en `SCH_FB_RESUMEN_RULE_v1` (a redactar). Vinculado a `account_id` (cuenta), no a `user_id`.

### Prioridad aprendida del Inbox

Score 0-100 por correo. Aprende de:
- Qué correos el user resuelve primero
- Qué clientes/dominios prioriza implícitamente
- SLA × valor económico
- Qué subjects/keywords resuelve rápido
- Cuándo marca "auto-borrar" o "leído oculto"

Vive en L4 user (preferencias personales). NO en reloj de aprendizaje.

---

## 14. WorkLoom · Mesa de Control kanban

### Filosofía

> "Qué necesita tu criterio hoy."

### 4 columnas del kanban

| Columna | Significa | Color |
|---|---|---|
| **TU CRITERIO** (críticos) | Alarmas, override, decisiones bloqueadas | Coral |
| **ESPERANDO CRITERIO** (a revisar) | Drafts terminados esperando aprobación HITL | Ámbar |
| **DELEGADO** | Tareas asignadas a otros members del tenant | Pizarra |
| **ERROR ACCIONABLE** | Outputs con error que necesitan acción | Vino |

### Cómo se establece la criticidad · 5 fuentes

| Fuente | Cuándo aplica |
|---|---|
| **Severity weight del exception taxonomy** | Skill detecta excepción tipificada (canon: ENT_FB_RFQ_EXCEPTION_TAXONOMY) |
| **Priority rules del workspace** | Reglas declarativas del dueño (extender SCH_FB_WS_INSTRUCTIONS) |
| **Severity signal del output del skill** | Skill emite signal con `{severity, reason, sla_hint}` |
| **Reglas globales del tenant** | Compliance breach · cost cap · banned phrase |
| **Override manual del operator** | Drag entre columnas o cambio status (audit log) |

### Anatomía de una card · heredada del mockup que el CEO mostró

```
┌─────────────────────────────────────────────────────────────┐
│ [ TU CRITERIO ]                                      0.96   │
│ Industrias del Norte SA                                     │
│ @mailbox:ventas → @router → @cotizador                      │
│ ◐ 14m SLA  ·  [A] Álvaro  ·  USD 12,400                     │
│                                                              │
│ 240 pares BC-7240 dieléctrica · contrato Iberdrola           │
│                                                              │
│  → Aprobar y enviar    → Editar y enviar    → Rechazar      │
└─────────────────────────────────────────────────────────────┘
```

| Elemento | Función |
|---|---|
| Severity tag | Estado del item |
| Score numérico (0.41-0.91) | Priority score para sort intra-columna |
| Trace path | Cadena de skills que produjo el output |
| Edad + asignado + costo | Metadata operativa |
| `Próx:` | Lo que falta hacer |
| Botón coral | Jump al workspace o acción específica |

### Item detalle de Mesa · 3 tabs

```
← Volver al kanban
Industrias del Norte SA · 240×BC-7240 dieléctrica
Tipo: RFQ B2B   Origen: @mailbox:ventas   Ruta: @router → @cotizador   trace: trc_a8f2

[ Ver solución ●]  [ Editar ]  [ Workspace ]
```

| Tab | Función |
|---|---|
| **Ver solución** (default) | Renderiza draft cliente-facing read-only · Acciones HITL |
| **Editar** | Editor inline · captura "porqué" del edit al guardar |
| **Workspace** | Jump al workspace destino con item activo |

### Captura del "porqué" del edit · learning HITL

```
┌──────────────────────────────────────────────────┐
│ Cambios guardados. ¿Por qué editaste?            │
│                                                  │
│ Tipo de cambio: [▼ Tono / formalidad           ] │
│                                                  │
│ Comentario (opcional):                           │
│ [Cliente prefiere mensajes más cortos          ] │
│                                                  │
│  [ Saltar ]                  [ Guardar signal ]  │
└──────────────────────────────────────────────────┘
```

Tipos del dropdown:
- Tono / formalidad
- Saludo / cierre
- Longitud
- Terminología / glosario
- Banned phrase no respetada
- Contenido factual
- Otro (libre obligatorio)

Edits >20% activan modal obligatorio. Edits <20% son opcionales.

### Sidepanel derecho del item detalle (canon `SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1`)

```
EVIDENCE BUNDLE
 · 4 fuentes citadas · todas HIGH
 · SHA-256 sellado: a3f2e9...7c41
 · KB consultada: Catálogo Marluvas v4.2 · Pricing 2026-04 ·
        Política descuentos v1.7 · Caso Iberdrola 2024

✓ VALIDACIONES
 ✓ Margen ≥ floor 22% (real 27.5%)
 ✓ Cliente al día de pago
 ⚠ Validez 15d < default 30d (override Owner)
 ⚠ Descuento platinum override Owner

AUDIT RESUMIDO
 · trc_a8f2 creada · @router · 12m
 · @cotizador draft v1 · conf 0.41
 · Álvaro adjuntó política · 5m
 · @cotizador draft v2 · conf 0.78
 ver audit completo →
```

### Flujo end-to-end consolidado

```
[Llegada externa: email/WhatsApp/etc.]
       ↓
[Inbox global] ← agregador de N cuentas conectadas con su agente @mail_X
       ↓
       ├─ Tier 0 deterministic + classifier Haiku
       │
       ├─ matched alta conf → Workspace destino directo (visible en Inbox como ✓)
       ├─ matched baja conf → expand inline en Mesa para decidir
       └─ sin match → expand inline en Inbox para decidir destino
                              ↓
                   [Workspace destino] · agente procesa · genera draft
                              ↓
                   [WorkLoom] ← visibilidad del HITL kanban
                              ↓
                              ├─ pending (a resolver) → JUMP al workspace
                              └─ resuelto → expand inline read-only
```

---

## 15. Tipología de agentes

| Tipo | Scope | Dónde se crea | Ejemplo |
|---|---|---|---|
| **Agente de comunicación** (canal-bound) | Tenant-level · vinculado a cuenta conectada | Chat padre (SpaceLoom) o Configuración tenant | `@mail_ventas`, `@mail_ceo`, `@whatsapp_mwt` |
| **Agente operativo** (workspace-bound) | Workspace-level · cadena lineal de skills | Workspace destino o desde SpaceLoom | `account_manager_industrias`, `dunning_specialist_ramirez` |
| **Agente de iteración** (cognitivo) | Tenant-level · siempre en SpaceLoom | SpaceLoom (predefinido) | `explorer_lab`, `deep_research` |
| **Agente de gobernanza** (meta) | Tenant-level · cross-workspace | Configuración tenant | `audit_collector`, `cost_monitor` |

### Cuando se conecta nueva cuenta de comunicación

```
Conectar nueva cuenta
 ▸ Gmail OAuth
 ▸ IMAP/SMTP custom
 ▸ Microsoft 365 (E2)
 ▸ WhatsApp Cloud API
 ▸ Otro canal (futuro)

Al conectar, se crea automáticamente un agente @mail_X
para esta bandeja con configuración default editable.
```

---

## 16. Voice Humanizer · skill SYSTEM mandatory (canon)

Ya canonizado en sesión 2026-05-07 anterior. Resumen:

### Modelo de capas

```
Voz = Sabor del user (base, una sola, evoluciona con HITL)
        modulada por
      Instrucciones del dueño del workspace (persistentes, mandan en conflicto)
        modulada por
      Ajuste transitorio del output (one-off, comando libre, con feedback)
```

### Resolución property-by-property

```
Para cada propiedad (saludo, tono, longitud, formalidad, etc.):

  Si ajuste transitorio del output declara la propiedad → gana
  Sino, si instrucciones del workspace declaran la propiedad → gana
  Sino, hereda del sabor user controlador del workspace
```

### Voice del workspace · regla

> "Workspaces bajo control de un user heredan la voz de ese user. Solo se modifica si hay instrucciones para modificarla."

### Filtros tenant post-resolución

| Filtro | Comportamiento |
|---|---|
| Banned phrases tenant | Severity HIGH: regenerar (1 retry) · si persiste BLOCKED_COMPLIANCE |
| Banned phrases workspace | Severity por declaración |
| Glosario tenant (preferred terms) | Sustitución automática |

Canon: `SPEC_FB_VOICE_HUMANIZER_v2`, `SCH_FB_VOICE_PROFILE_v1`, `SCH_FB_WS_INSTRUCTIONS_v1`, `POL_FB_VOICE_RESOLUTION_v1`.

---

## 17. Iteraciones del HTML · histórico

### v3 (`faberloom_shell_universal_v3.html`)

Primer mock con la nueva arquitectura post-redesign. Sidebar con grupos Sistema/Cuentas/Internal/Governance. Sidepanel derecho con drawers fijos.

### v4 (`faberloom_shell_chat_v4.html`)

Refactor con sidebar Operar + Workspaces + Administrar. Sidepanel derecho con 4 tabs minimalistas. Avatar foot dropdown.

### v5 (`faberloom_shell_chat_v5.html`)

Layout 4 paneles + resize handles. Rail 2 contextual del Chat con conversaciones (Pinned + Hoy + Ayer). Mini-rail con icono toggle. Footer del input con tokens IO + costo.

### v6 (`faberloom_shell_v6.html`) · ACTUAL

Familia *Loom completa: FaberLoom + WorkLoom + SpaceLoom + StackLoom. Brand foot tagline "Tejé tu trabajo". Sin badge en SpaceLoom. Header "Operar" agrupando los 3. Conocimiento (no Atlas).

---

## 18. Decisiones tomadas · cronológico

### Modelo conceptual (sesión iteración shell)

| # | Decisión | Status |
|---|---|---|
| 1 | 3 tipos de workspace según función: Operativos · Visibilidad · Iteración | ✓ |
| 2 | Workspace polimórfico via vertical_spec_object | ✓ |
| 3 | Workspace = unidad de trabajo coherente del vertical (en MWT: cuenta cliente B2B) | ✓ |
| 4 | Misma estructura schema para todos los workspaces, distintos valores | ✓ |
| 5 | Workspace bajo control de user (`controlled_by` obligatorio) | ✓ |
| 6 | Knowledge en 5 capas L0-L4 con taxonomía 8+especiales | ✓ |
| 7 | Voice Humanizer con resolución property-by-property | ✓ |
| 8 | Reloj de aprendizaje exclusivo de knowledge a indexar | ✓ |
| 9 | Inbox con cuentas conectadas multi-bandeja | ✓ |
| 10 | 5 categorías auto-detectadas en Inbox | ✓ |
| 11 | Resúmenes activos como flujo declarativo | ✓ |
| 12 | Resumen scope = cuenta (personal o organizacional) | ✓ |
| 13 | Mesa = kanban por criticidad (no por workspace) | ✓ |
| 14 | 4 columnas: Tu Criterio · Esperando Criterio · Delegado · Error Accionable | ✓ |
| 15 | Item detalle Mesa con 3 tabs (Ver solución / Editar / Workspace) | ✓ |
| 16 | Captura del "porqué" del edit con dropdown tipificado | ✓ |
| 17 | Inbox y Mesa nunca son lugar de resolución (jump al workspace) | ✓ |
| 18 | Inbox/Mesa items resueltos: expand inline read-only | ✓ |
| 19 | Patrón propio/heredado en Workspaces, Skills, Agentes, Conocimiento | ✓ |
| 20 | Tipos de agentes: comunicación · operativo · iteración · gobernanza | ✓ |
| 21 | Agentes de comunicación se crean desde SpaceLoom | ✓ |
| 22 | Iteración con IA = misma surface en Chat global y Tab Iteración de workspace | ✓ |

### Naming · familia *Loom

| # | Decisión | Razón |
|---|---|---|
| 1 | FaberLoom = marca/producto (intacto) | Identidad consistente cross-language |
| 2 | WorkLoom = Mesa de Control (canon) · UI muestra "Mesa de Control" | Llena vacío "Mesa de control" sin ser industrial |
| 3 | SpaceLoom = home cognitivo (antes "Chat") | Telar de espacio cognitivo · iteración |
| 4 | StackLoom = construir knowledge (antes "Curaduría") | Stack literal · capas L0-L4 son apilables como lego |
| 5 | Workspace estándar (no SpaceLoom para esto) | Estándar SaaS internacional · "Espacios de Trabajo" en sidebar |
| 6 | Chat estándar (NO ChatLoom · SpaceLoom ocupa ese rol) | Chat universal | rol cognitivo va a SpaceLoom |
| 7 | Conocimiento (no Atlas) | "Atlas" abstracto · "Conocimiento" comunica el valor del producto |
| 8 | Curaduría (no Curetaje) | "Curetaje" es médico en todos los idiomas |
| 9 | Agentes (no Agents) | Localización ES |
| 10 | Fijados (no Pinned) | Localización ES |

### Copy · HITL / Criterio

| # | Decisión |
|---|---|
| 1 | HITL = "criterio" (no "aprobación") · más orientado al objetivo HITL |
| 2 | Cross-language: Esperando tu criterio · Awaiting your criteria · Aguardando seu critério |
| 3 | Configuración (governance) = "Criterio para aprobación" · "Approval criteria" |
| 4 | Tagline brand: "Tejé tu trabajo" · "Weave your work" |
| 5 | Subheader WorkLoom: "centro nervioso · qué necesita tu criterio hoy" |
| 6 | Tooltip: "Aplicá tu criterio · la IA preparó, vos decidís cómo" |
| 7 | Botones HITL: "Aprobar y enviar" · "Editar y enviar" · "Rechazar" |
| 8 | Canon SPECs/código: mantener `HITL` por compatibilidad |

### Layout y comportamiento

| # | Decisión |
|---|---|
| 1 | 4 paneles (Rail 1 · Rail 2 · Canvas · Rail 3) |
| 2 | Resize handles entre paneles · drag · doble click reset · drag descolapsa |
| 3 | Rails colapsables a mini (44px con icono toggle SVG) |
| 4 | Toggle iconos: rectángulo + línea vertical · espejo izq/der |
| 5 | Header "Operar" agrupa Mesa de Control + Inbox + SpaceLoom |
| 6 | SpaceLoom sin badge habitualmente · `[3]` solo si sugerencias del día |
| 7 | Conversaciones del SpaceLoom van en Rail 2 contextual (no inline en sidebar) |
| 8 | Sidepanel derecho con 4 tabs minimalistas (Agentes · Skills · Conocimiento · Workspace) |
| 9 | Footer del input · ctx + fuentes KB + modelo + tokens IO + costo |
| 10 | CTA inline indexar cuando sistema detecta candidato |
| 11 | Avatar foot dropdown personal: Mi cuenta · Mi voz · Preferencias · Cerrar sesión |

---

## 19. Próximos pasos · pendiente sketch

### Ya cerrado

- [x] Shell completo del SpaceLoom (v6 HTML)
- [x] Familia *Loom + naming completo
- [x] Cross-language matrix
- [x] Copy HITL / Criterio
- [x] Modelo conceptual de Inbox · Mesa · SpaceLoom · StackLoom
- [x] Tipología de workspaces y agentes
- [x] Patrón propio/heredado
- [x] Resúmenes activos como flujo declarativo

### Pendiente próximo sketch

- [ ] **HTML del WorkLoom (Mesa de Control)** · kanban 4 columnas + cards anatomía completa + badge "TU CRITERIO" coral + métricas top
- [ ] **HTML del Inbox** · 5 categorías + cuentas conectadas en sidepanel · prioridad aprendida · resúmenes activos como cards especiales
- [ ] **HTML item detalle de Mesa** · 3 tabs (Ver solución / Editar / Workspace) · sidepanel evidence + validaciones + audit
- [ ] **Modal "porqué del edit"** con dropdown tipificado
- [ ] **Modal Workspace Factory** wizard 6 pasos
- [ ] **HTML StackLoom** · vista de capas L0-L4 con candidatos a curar
- [ ] **HTML cuenta cliente** (ws_sondel) con tabs Bandeja · Histórico · KB · Iteración · Configurar · Sanidad
- [ ] **HTML cuenta cliente con urgencia** · critical card domina, resto atenuado
- [ ] **Estado expandido del rail** (240→280px con labels)
- [ ] **CmdK palette** abierto (Raycast-style)
- [ ] **Reloj bloqueado** (estado crítico coral pulse)
- [ ] **Mobile / responsive**

### Pendiente canon (SPECs a redactar)

- [ ] `SPEC_FB_CONSOLE_LAYOUT_v1` (canoniza el shell entero)
- [ ] `SPEC_FB_INBOX_ROUTING_v1` (5 categorías + cuentas multi-bandeja)
- [ ] `SPEC_FB_MESA_KANBAN_v1` (4 columnas + anatomía cards + scoring)
- [ ] `SPEC_FB_WORKSPACE_FACTORY_v1` (wizard 6 pasos)
- [ ] `SPEC_FB_STACKLOOM_v1` (flujo de promoción L4→L1)
- [ ] `SPEC_FB_VOICE_BOOTSTRAP_v1` (UI configuración voice user E1)
- [ ] `POL_FB_VOICE_LEARNING_v1` (captura "porqué" del edit)
- [ ] `POL_FB_INBOX_PRIORITY_LEARNING_v1` (score aprendido)
- [ ] `POL_FB_TENANT_PRIORITY_OVERRIDES_v1` (reglas globales tenant)
- [ ] `POL_FB_AUTO_DELETE_v1` (auto-borrar puro vs tras síntesis)
- [ ] `SCH_FB_MAIL_ACCOUNT_v1` (cuenta conectada con team_users si organizacional)
- [ ] `SCH_FB_RESUMEN_RULE_v1` (reglas de resúmenes activos)
- [ ] `SCH_FB_MESA_ITEM_v1` (schema completo del item de Mesa)
- [ ] `ENT_FB_AGENT_TYPES_v1` (4 tipos de agente)

---

## 20. Para Claude Design / Stitch · brief consolidado

Si vas a usar este snapshot como brief para herramienta de diseño:

**El producto:** plataforma SaaS multi-tenant para PYMEs B2B (FaberLoom). Primer tenant: MWT (distribución calzado seguridad LATAM).

**El shell debe sentirse como:** Apple Mail × Things 3 × Linear × Stripe.

**Familia *Loom (no traducir cross-language):**
- FaberLoom = marca/producto
- WorkLoom = mesa de control (UI: Mesa de Control)
- SpaceLoom = home cognitivo
- StackLoom = construir knowledge

**Cuatro paneles principales:**
1. Rail 1 (248px) — navegación principal · Operar / Workspaces / Administrar
2. Rail 2 (240px contextual) — solo cuando aplica (ej: conversaciones del SpaceLoom)
3. Canvas — contenido del workspace
4. Rail 3 (280px colapsable) — sidepanel derecho con 4 tabs (Agentes · Skills · Conocimiento · Workspace)

**Topbar (58px):** breadcrumb · command bar `⌘K` · reloj de aprendizaje · role switcher · theme toggle.

**Paleta:** cream `#F4F1ED`, ink `#1F1E1C`, coral `#C96442`, vino `#6E1F2B`, salvia `#7A8E6D`, ámbar `#B88A4A`, pizarra `#5A6B7C`.

**Tipografía:** Georgia italic (títulos), Inter (UI), JetBrains Mono (IDs · estados técnicos).

**HITL → "criterio":** "Esperando tu criterio" / "Awaiting your criteria" / "Tu criterio". Configuración: "Criterio para aprobación" / "Approval criteria".

**Reglas duras:** ver sección 1.

**Modelo de iteración del user:**
> "La IA prepara. Vos aportás tu criterio."

El user no es aprobador robótico. Es profesional que aporta JUICIO. Cada interacción HITL es signal capturado que mejora al sistema. Aprendizaje progresivo, no configuración upfront.

---

## 21. Reglas inquebrantables canon FaberLoom (TIER1 plan firmado)

Recordatorio para que cualquier sketch nuevo respete:

1. **HITL absoluto** · cero auto-send a cliente sin aprobación humana
2. **Single-agent por task** · NO sub-agentes ni orquestación entre agentes
3. **N0–N2 only** en uploads · N3-N4 hard-block
4. **RLS Postgres por tenant** en toda tabla con tenant_id
5. **Audit log append-only** con actor_user_id + actor_role_at_decision
6. **Evidence bundle** mínimo 8+5 campos + SHA-256
7. **Anthropic-only** para LLM en E1
8. **Voice Profile completo** persona+tono+glosario+saludo+firma por user
9. **5 roles tenant**: Owner / Admin / Supervisor / Operator / Viewer
10. **Skill Factory con 14 límites duros**: classifier/generator/formatter only · sin tools externas · sin HTTP · sin code exec · sandbox obligatorio · etc.

Cualquier diseño UI/UX que viole estas reglas requiere MANIFIESTO_APPEND y reabrir canon.

---

## Stamp

VIGENTE 2026-05-07 · sketch consolidado de iteración del shell de FaberLoom.
HTML actual: `docs/anexos/mockups/faberloom_shell_v6.html`
Próximo paso: HTML del WorkLoom (Mesa de Control kanban).

Documento autocontenido. Si retomás trabajo en otro chat, este documento + el HTML v6 dan contexto completo para continuar sin perder iteraciones.
