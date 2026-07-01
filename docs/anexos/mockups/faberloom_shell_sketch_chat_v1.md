# FaberLoom Shell · Sketch textual snapshot · Chat workspace v1

**Fecha:** 2026-05-07
**Status:** sketch en iteración (NO canon · pendiente SPEC_FB_CONSOLE_LAYOUT_v1)
**Siguiente:** sketches Skills adentro · Mesa de trabajo · Knowledge Curetaje
**Uso:** referencia para Claude Design / Stitch / iteración con CEO

---

## 1. Filosofía del shell (heredada del PROMPT MAESTRO Mesa de Control v4)

```
"El shell no trabaja; el workspace trabaja."

Shell = sistema operativo visual.
Workspace = lugar.
Herramienta = verbo.

Inteligente en comportamiento, silencioso en superficie.
```

El shell debe sentirse como mezcla de Apple Mail / Things 3 / Linear / Stripe — calma editorial con disciplina operativa. NO debe sentirse Salesforce / HubSpot / Notion / Material Design / dashboard SaaS saturado.

---

## 2. Paleta visual (Brand v2)

```
cream background    #F4F1ED      (fondo principal)
ink text            #1F1E1C      (texto)
coral primary       #C96442      (alarma · acción decisiva · solo en autoridad)
coral hover         #A84F33
coral tint          rgba(201,100,66,0.10)
vino forensic       #6E1F2B      (evidence / forensic)
salvia              #7A8E6D      (estado positivo sutil)
ámbar               #B88A4A      (warning · reloj atento)
pizarra             #5A6B7C      (texto secundario)
```

**Reglas:**
- Coral SOLO para alarma o acción decisiva
- Vino SOLO para evidencia / forensic
- Salvia SOLO para estados positivos sutiles
- Ámbar SOLO para warning / reloj atento
- Grises, cream y blanco cálido cargan la mayoría de la interfaz

---

## 3. Tipografía

```
Georgia italic         títulos editoriales · wordmark · momentos de autoridad
Inter                  UI · cuerpo · navegación · formularios
JetBrains Mono         IDs · trazas · estados técnicos · uppercase labels · forensic
```

Jerarquía por tamaño + peso + espacio + contraste tipográfico. NO por cajas + bordes + badges + iconografía ruidosa.

---

## 4. Layout general (tres zonas)

```
┌──── TOPBAR ──────────────────────────────────────────────────────────────────────────────────┐
│ [breadcrumb workspace]      ⌕ Buscar o ejecutar...    [● Aprendizaje · estado · N◷]          │
│ [tipo · controlled_by]                       ⌘K              [Role ▾]   [◐ tema]             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
┌─ SIDEBAR LEFT ─────────┬─── CANVAS ─────────────────────────────┬── SIDEPANEL RIGHT ──┐
│                        │                                         │                     │
│  Navegación principal  │   Workspace activo                      │  Contextual al      │
│  + workspace expandido │   (contenido del workspace)             │  workspace activo   │
│  + avatar foot         │                                         │                     │
│                        │                                         │  Colapsable         │
│                        │                                         │                     │
└────────────────────────┴────────────────────────────────────────┴─────────────────────┘
```

---

## 5. Sidebar izquierdo (con Chat expandido)

```
┌─────────────────────────────────────┐
│ [F*] Faber*loom                     │
│      tenant · MWT                   │
│ ─────────────────────────────────── │
│ [⇤] Colapsar                        │
│                                     │
│  ○ Mesa de trabajo            [7]   │
│  ○ Inbox sin asignar         [24]   │
│ ─────────────────────────────────── │
│ ▼ (●) Chat                   [27]   │   ← workspace padre (home)
│    [+ Nueva conversación]           │
│    ──                               │
│    Pinned (3)                       │
│     ◉ Voice MWT banned phrases      │
│     ◉ Política descuentos por tier  │
│     ◉ Plantilla follow-up B2B v2    │
│    Hoy                              │
│     ○ Industrias Norte 09:14        │
│     ○ Glossary safety MX 11:30      │
│     ○ Sondel renovación 14:02       │
│    Ayer                             │
│     ○ Deep research dieléctrico     │
│    Esta semana (5)                  │
│     ↪ ver todas                     │
│ ─────────────────────────────────── │
│                                     │
│  Espacios de Trabajo            +   │
│                                     │
│  Administrados                      │
│   ○ Mwt.one                         │
│   ○ FaberLoom                 [2]   │
│   ○ Rana Walk                 [1]   │
│                                     │
│  Heredados                          │
│   ○ Industrias del Norte [Crítico]  │
│   ○ Sondel SA                 [3]   │
│   ○ Distribuidora Ramírez     [2]   │
│   ○ Constructoras Alfa        [1]   │
│   ○ Minera Central                  │
│                                     │
│  Administrar                        │
│                                     │
│   Capacidades                       │
│    ○ Skills              [16] +     │
│    ○ Agents               [7] +     │
│    ○ Knowledge Atlas      [7] +     │
│    ○ Knowledge Curetaje [◷ 5]       │
│                                     │
│   Tenant                            │
│    ○ Usuarios y permisos     [12]   │
│    ○ IA: modelos y ruteo            │
│    ○ Audit                          │
│    ○ Configuración tenant           │
│                                     │
│ ─────────────────────────────────── │
│ [AF] Alejandro Faro · OPERATOR  ▾   │
│      ↓ Mi cuenta                    │
│        Mi voz                       │
│        Preferencias                 │
│        Cerrar sesión                │
└─────────────────────────────────────┘
```

### Marcas visuales

| Símbolo | Significado |
|---|---|
| `(●)` | Workspace padre activo (relleno coral) |
| `▼` | Item expandido con sub-items inline |
| `◉` | Item propio del user (relleno) |
| `○` | Item heredado / system / no-propio (vacío) |
| `[N]` | Count numérico (pendientes operativos) |
| `[◷ N]` | Count de elementos a indexar (knowledge) |
| `[Crítico]` | Pill coral para urgencia |
| `+` | Acción crear (al lado del label, fin de línea) |

---

## 6. Topbar

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ Chat                                  ⌕ Buscar o ejecutar...                              │
│ home cognitivo · KB tenant                              ⌘K                                │
│                                                          [● Aprendizaje · atento · 5◷]  │
│                                                                  [Operator ▾] [◐]        │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

**Elementos:**
- Izquierda: breadcrumb del workspace (línea 1: nombre del ws · línea 2: tipo · controlled_by)
- Centro: command bar `⌘K` (sistema nervioso · Raycast/Linear style)
- Derecha: reloj de aprendizaje universal · role switcher · theme toggle

**NO hay:** logo, avatar, métricas operativas, notificaciones, breadcrumb pesado, accesos rápidos.

### Estados del reloj de aprendizaje

```
[● Aprendizaje · al día · 12d]              salvia (sin pendientes)
[● Aprendizaje · atento · 5◷]               ámbar (1-9 pendientes)
[● Aprendizaje · bloqueado · 14◷ revisar]   coral (10+ pendientes)
```

**Click en el reloj → panel desplegable:**

```
┌─────────────────────────────────┐
│ Reloj de aprendizaje            │
│ Estado · atento                 │
│                                 │
│ Knowledge a indexar:            │
│  ─ 3 candidatos en Curetaje     │
│  ─ 1 conflicto de fuente        │
│  ─ 1 promoción L4→L2 esperando  │
│                                 │
│ Templates sin congelar: 3       │
│ Próximo freeze: 18 días         │
│                                 │
│ [Abrir Curetaje →]              │
└─────────────────────────────────┘
```

---

## 7. Canvas (workspace Chat)

```
Chat
home cognitivo · KB tenant · contexto auto-detect

┌──────────────────────────────────────────────────┐
│ Pregunta o pedí algo. @ws_xx para fijar scope.   │
│                                                  │
│                          [↑ Adj.]   [Enviar]     │
└──────────────────────────────────────────────────┘

Sugerencias del día:
 → Curar 3 candidatos pending
 → Iterar voice MWT (4 términos sectoriales nuevos)
 → Continuar deep research D2

─────────────────────────────────

09:14  "¿Cómo cerramos el follow-up de Industrias del Norte?"
       → contexto: ws_industrias_norte
       → KB: histórico · voice MWT · políticas
       → modelo: Sonnet 4.6 (vía Routing Inheritance)

[Respuesta IA con contenido]

  ┌──────────────────────────────────────────────┐
  │ ◷ Esto puede valer la pena indexar           │
  │   "4 términos sectoriales nuevos detectados" │
  │   contexto sugerido: L1 vertical             │
  │   [Indexar a L1] [Más tarde] [No]            │
  └──────────────────────────────────────────────┘

Acciones sobre la respuesta:
 → Promover a workspace
 → Guardar como contexto pinned
 → Crear borrador en ws_industrias_norte
 → Iterar (refinar pregunta)

─────────────────────────────────

11:30  "Términos sectoriales nuevos en safety footwear MX"
       → 7 mensajes · candidato L1 vertical
       [Continuar] [Curar] [Descartar]
```

### CTA inline de indexación

Aparece cuando el sistema agente detecta candidato heurísticamente:

- ≥N términos sectoriales nuevos
- ≥M mensajes sobre proceso/política
- mención explícita de regla/template

Acciones:
- `Indexar a L1/L2/L3` → abre creator inline con conversación pre-poblada
- `Más tarde` → cola Knowledge Curetaje (no se pierde)
- `No` → signal para mejorar heurística

---

## 8. Sidepanel derecho (4 tabs · contextual)

### Selector

```
[ Agentes ] [ Skills ] [Conocimiento◷] [ Workspace ]
```

Solo Conocimiento puede tener `◷` (knowledge a indexar). Los otros usan `[●]` para alertas operativas genéricas.

### Tab Agentes

```
─────────────────────────
Agentes · 12

Propios (5)
 ◉ industrias_account_manager
 ◉ sondel_followup_writer       [●]
 ◉ ramirez_dunning_specialist
 ◉ alfa_negotiator              [●]
 ◉ minera_proposals

Heredados (7)
 ○ account_manager
 ○ dunning_gentle
 ○ classify_router
 ○ proforma_builder
 ○ escalation_handler
 ○ deep_research                [BETA]
 ○ explorer_lab

[+ Crear]  [⎘ Adoptar]
```

### Tab Skills

```
─────────────────────────
Skills · 24

Propios (4)
 ◉ proforma_builder_safety
 ◉ dunning_gentle_mwt           [●]
 ◉ industrias_pricing_calc
 ◉ sondel_voice_tweak

Heredados (20)
 ○ classify_intent
 ○ retrieve_kb
 ○ generate_quote
 ○ format_output
 ○ voice_humanizer              [●]
 ○ extract_metadata
 ○ classify_destination
 ○ detect_exception
 ○ dunning_message
 ↪ ver todos (11 más)

[+ Crear]  [⎘ Adoptar]
```

### Tab Conocimiento

```
─────────────────────────
Contextos · 19

Propios (7)
 ◉ Voice MWT                    L4
 ◉ Histórico Sondel             L3
 ◉ Política descuentos          L2   [◷]
 ◉ Plantilla follow-up B2B      L2
 ◉ Replay set Q1                L4
 ◉ Notas Industrias             L4
 ◉ Glosario minería             L1

Heredados (12)
 ○ Catálogo BC-7240             L1
 ○ Normas EPP LATAM             L0
 ○ Banned phrases tenant        L2
 ○ Voice tenant MWT             L2   [◷]
 ○ Replay safety_footwear       L1
 ○ Política LFPDPPP             L0
 ○ Glosario comercial           L2
 ↪ ver todos (5 más)

[+ Crear]  [⎘ Adoptar]

─────────────────────────
◷ 5 niveles a indexar
 ─ 3 candidatos en Curetaje
 ─ 1 conflicto de fuente (BC-7240)
 ─ 1 promoción L4→L2 esperando Owner
```

### Tab Workspace

```
─────────────────────────
Workspaces · 13

Administrados (3)
 ◉ Mwt.one
 ◉ FaberLoom                    [●]
 ◉ Rana Walk

Heredados (10)
 ○ Industrias del Norte         [●]
 ○ Sondel SA
 ○ Distribuidora Ramírez
 ○ Constructoras Alfa
 ○ Minera Central
 ○ Lab MWT                      [●]
 ○ Inbox sin asignar            [●]
 ↪ ver todos (3 más)

[+ Crear]  [⎘ Adoptar]
```

### Principios del sidepanel derecho

- **Minimalista**: solo nombre del item + alerta sutil. Sin metadata operativa (versión, uso, tipo, operator, etc.).
- **Detalle vive en el workspace**: click en item → te lleva al workspace correspondiente, donde sí ves changelog, rutinas, procesos, prompt, sandbox, métricas, audit trail.
- **Counts numéricos NO se duplican**: viven solo en sidebar izquierdo. El sidepanel derecho usa solo `[●]` o `[◷]` como alertas binarias.
- **Solo Conocimiento usa `◷`**: el reloj de aprendizaje es exclusivo de knowledge a indexar.
- **Siempre colapsable**.

---

## 9. Reglas duras del sistema (heredadas del PROMPT MAESTRO)

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

---

## 10. Decisiones tomadas en sesiones de iteración

| # | Decisión | Status |
|---|---|---|
| 1 | Workspace padre se llama "Chat" (chat libre con KB tenant) | Confirmada CEO |
| 2 | Inbox sin asignar y Mesa de trabajo son workspaces hermanos arriba del Chat | Confirmada CEO |
| 3 | Sidebar izquierdo · item Chat expandible con conversaciones inline | Confirmada CEO |
| 4 | Conversaciones agrupadas por Pinned · Hoy · Ayer · Esta semana | Default |
| 5 | Sidepanel derecho con 4 tabs minimalistas: Agentes · Skills · Conocimiento · Workspace | Confirmada CEO |
| 6 | Sidepanel sin metadata operativa (solo nombre + alerta) | Confirmada CEO |
| 7 | Reloj de aprendizaje exclusivo para knowledge a indexar | Confirmada CEO |
| 8 | CTA inline cuando sistema detecta candidato heurísticamente (opción B) | Default |
| 9 | Distinción Administrados / Heredados en workspaces | Confirmada CEO |
| 10 | Distinción Propios / Heredados en Skills · Agents · Knowledge | Confirmada CEO |
| 11 | Avatar foot dropdown con Mi cuenta · Mi voz · Preferencias · Cerrar sesión | Default |
| 12 | "AI Control Plane" renombrado a "IA: modelos y ruteo" | Confirmada CEO |
| 13 | Sub-secciones de Administrar: Capacidades · Tenant | Default |
| 14 | Knowledge Curetaje como entrada propia bajo Capacidades | Confirmada CEO |
| 15 | + en items significa crear / importar / adoptar inline | Confirmada CEO |
| 16 | Counts numéricos `[N]` solo en sidebar izquierdo, no en sidepanel derecho | Confirmada CEO |
| 17 | Conversaciones del Chat van a la izquierda (no son herramienta) | Confirmada CEO |
| 18 | Solo "lo que crea" va a la derecha como herramienta | Confirmada CEO |

---

## 11. Lo que NO está en este sketch (pendiente)

- **Workspace Skills adentro**: cómo se ve cuando hacés click en un skill (changelog · rutinas · procesos · sandbox · métricas)
- **Workspace Agents adentro**: similar
- **Workspace Knowledge Atlas adentro**: vista de las 5 capas L0-L4
- **Workspace Knowledge Curetaje**: el flujo de indexación que activa el `◷`
- **Workspace Mesa de trabajo**: feed cross-workspace HITL ordenado por prioridad
- **Workspace Inbox sin asignar**: routing manual de no-clasificados
- **Workspace cuenta cliente**: tabs Bandeja · Histórico · KB · Iteración · Configurar · Sanidad
- **Workspace cuenta cliente con urgencia**: critical card domina, resto atenuado
- **Workspace Lab MWT**: candidatos a promover · deep research · iterar skills
- **Modal Crear workspace** (Workspace maker wizard 6 pasos)
- **Modal Crear skill** (5 pasos)
- **Modal Crear agente** (4 pasos)
- **Modal Crear contexto knowledge** (con conversación pre-poblada del Chat)
- **Estado expandido del rail** (240px con labels)
- **Estado `⌘K` abierto** (command palette Raycast-style)
- **Reloj bloqueado**: estado crítico y CTAs
- **Mobile / responsive**

---

## 12. Próximos pasos

1. **Iterar este sketch del Chat** hasta cierre con CEO
2. **Sketch siguiente**: Skills adentro · Mesa de trabajo · o Knowledge Curetaje (CEO elige)
3. **Cuando todos los sketches estén iterados**: pasar a Claude Design / Stitch para producir mock final
4. **Cuando el mock final esté validado**: redactar `SPEC_FB_CONSOLE_LAYOUT_v1` con las decisiones congeladas
5. **Sync indexa al canónico** vía `sync_console_layout_indexa.ps1`

---

## 13. Para Claude Design / Stitch · brief consolidado

Si vas a usar este snapshot como brief para una herramienta de diseño:

**El producto:** plataforma SaaS multi-tenant para PYMEs B2B (FaberLoom). Primer tenant: MWT (distribución calzado seguridad LATAM).

**El shell debe sentirse como:** Apple Mail × Things 3 × Linear × Stripe.

**El shell NO debe sentirse como:** Salesforce × HubSpot × Notion × Material Design × dashboard SaaS saturado.

**La regla madre:** "El shell no trabaja; el workspace trabaja."

**Tres zonas:**
1. Sidebar izquierdo (260px) — navegación principal · workspace expandido si aplica · avatar foot
2. Topbar (58px) — breadcrumb · command bar `⌘K` · reloj de aprendizaje · role switcher · theme toggle
3. Canvas — contenido del workspace activo
4. Sidepanel derecho (240px · colapsable) — contextual al workspace activo

**Paleta:** cream `#F4F1ED`, ink `#1F1E1C`, coral `#C96442`, vino `#6E1F2B`, salvia `#7A8E6D`, ámbar `#B88A4A`, pizarra `#5A6B7C`.

**Tipografía:** Georgia italic (títulos), Inter (UI), JetBrains Mono (IDs · estados técnicos).

**Reglas duras:** ver sección 9.
