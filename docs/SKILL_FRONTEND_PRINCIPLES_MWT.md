# SKILL_FRONTEND_PRINCIPLES_MWT — Lente cognitiva frontend MWT (9 principios)

id: SKILL_FRONTEND_PRINCIPLES_MWT
version: 1.0
status: SHADOW
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SKILL
stamp: SHADOW — 2026-05-04
trigger_word: (sin trigger explícito — se activa por contexto)
trigger_context: cualquier conversación, propuesta, crítica o iteración donde se piense, diseñe o implemente funcionalidad de frontend en mwt.one, ranawalk.com o portal.mwt.one (UI, UX, mocks, layouts, flujos, componentes, navegación, copy de UI, formularios, dashboards, alertas)
autonomy_ceiling: ACTIVO_BG (background — colorea el razonamiento sin esperar invocación)
escalation_policy: emitir flag P0 (`MUSCLE_AMPUTATION`, `DRIFT_DETECTED`, `LAYOUT_MISMATCH`, `ROLE_LEAK`) detiene la propuesta y escala al CEO antes de avanzar
aplica_a: [MWT]
derivado_de: docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md (v2.1) — selección 9/14 + adaptación al stack MWT y a sus 3 frontends
refs:
- ARCH_AGENT_PRINCIPLES (P9 gobernanza embebida — análogo conceptual)
- ENT_PLAT_FRONTENDS v2.0 — 3 instancias Next.js
- ENT_PLAT_DESIGN_TOKENS v1.1 (APROBADO Sprint 3) — tokens canónicos
- ENT_OPS_STATE_MACHINE (FROZEN) — 8 estados expediente, fuente canónica de la spec
- POL_DETERMINISMO v1.2 — dato único + vacío explícito (extiende a UI)
- POL_NUNCA_TRADUCIR — SKUs, tech names, brand names no se traducen
- POL_VISIBILIDAD — 4 tiers (PUBLIC, PARTNER_B2B, INTERNAL, CEO-ONLY)
- POL_ANTI_CONFUSION — Navy MWT vs Navy E1 Goliath

---

## Propósito

**No es un agente con workflow.** Es una **lente cognitiva persistente** que se aplica siempre que el razonamiento toque frontend de MWT. Cada vez que se piense una pantalla, un componente, un flujo, una navegación, una alerta o una propuesta de UI — esta lente se activa en background y colorea el análisis con 9 principios no-negociables, pensados específicamente para los 3 frontends de la plataforma MWT.

**Diferencia con el skill FaberLoom:** el skill `SKILL_FRONTEND_TEN_PRINCIPLES_V2` (v2.1) define 14 principios anclados al Design System FaberLoom (Workspace chat-first, Iterar object-first, Cotización document-first, Skill Arena). Este skill **no es una copia**: es una selección honesta de los 9 principios que pegan en el contexto MWT (expediente como objeto canónico, dashboard CEO power-user, portal B2B novato-friendly, sitio público + agentes IA), reescritos con ejemplos del dominio (expedientes Marluvas, pricing por marca, cash flow 90d, listings Amazon, kanban de tiempos).

**Modo de uso:** la lente vive como contexto disponible (Project Instructions, Custom Instructions, KB ref). No se invoca con un trigger word. Se aplica cada vez que la conversación cruza el `trigger_context`. Se adapta al modo (brainstorming, crítica de mock, diseño desde cero, implementación, decisión binaria) sin forzar artefactos formales salvo que se pidan.

---

## Contexto MWT que la lente asume

Antes de cualquier principio, recordar:

**Tres frontends, tres públicos, una arquitectura compartida.**

| Frontend                | URL              | Tipo | Público                                          | Densidad esperada                                                |
| ----------------------- | ---------------- | ---- | ------------------------------------------------ | ---------------------------------------------------------------- |
| Centro de Operaciones   | `mwt.one`        | SPA  | CEO + equipo interno                             | Power-user — densidad alta, atajos visibles, métricas ambient    |
| Sitio público Rana Walk | `ranawalk.com`   | SSR  | Consumidor humano + agentes IA (UCP/ACP/MCP)     | Cero fricción — la UI se enseña sola, sin manual                 |
| Portal B2B              | `portal.mwt.one` | SPA  | Distribuidores, sub-distribuidores, clientes B2B | Novato-friendly — pocas decisiones por pantalla, jerarquía obvia |

**Stack canónico (heredado del SPEC FB y aplicable a MWT):**

- Next.js App Router + React Server Components
- TanStack Query v5 para server-state · Zustand para UI-state local
- WebSocket nativo para realtime (alertas de expediente, eventos de pago)
- React Hook Form + Zod (tipos TS desde Pydantic backend)
- Tailwind + design tokens de `ENT_PLAT_DESIGN_TOKENS`

**Objeto canónico del dominio:** el **Expediente** de importación. Toda navegación, alerta, métrica y workflow gira alrededor de su ciclo de vida (8 estados de `ENT_OPS_STATE_MACHINE` FROZEN).

---

## Cómo se activa la lente

Cualquiera de estas señales en la conversación dispara la lente:

- Mock visual adjunto (imagen, wireframe, descripción detallada de pantalla)
- Mención de pantalla, componente, layout, flujo, navegación, formulario, dashboard, alerta
- Propuesta de "agregar / quitar / mover / ocultar / mostrar" algo en UI
- Discusión de affordance, jerarquía visual, cognitive load, progressive disclosure
- Decisión de qué métrica/control mostrar/esconder (especialmente en el portal B2B)
- Cualquier conversación cuyo output natural sea código frontend, especificación de UI o crítica de UX

Si el contexto la activa, el razonamiento debe pasar implícitamente por los 9 principios y emitir flags cuando un antipatrón asome — sin obligar a producir artefactos formales salvo que se pidan.

---

## Output esperado por modo de conversación

| Modo                                 | Output de la lente                                                                                                       |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Brainstorming / pensar en voz alta   | Observaciones en línea con citación del principio (M2, M6, etc.) cuando una propuesta cruce                              |
| Crítica de mock                      | Flags emitidos contra el catálogo + recomendación + alternativa MWT-coherente                                            |
| Diseño nuevo desde cero              | Audit sustractiva + spec ligera, sin obligar formato 3-artefactos                                                        |
| Implementación de código             | Comentarios con citación de principio en bloques relevantes (`// M2: SSOT — usar 'expediente' canónico, no 'operación'`) |
| Decisión binaria ("¿dónde pongo X?") | Respuesta directa con principio que la justifica, no checklist completo                                                  |

---

# Los 9 principios MWT (canon)

---

## M1 — THESIS DISTILLATION POR PANTALLA Y POR SECCIÓN

_(derivado de FB-P1)_

### Enunciado

Toda pantalla, toda sección de mwt.one y toda vista de portal.mwt.one debe poder describirse en **una sola oración de máximo 140 caracteres** con la forma:

```
[Persona] puede [acción core] para [outcome] vía [diferenciador]
```

Si la oración no entra en 140 chars, o si requiere "y también…" más de una vez, la pantalla está conceptualmente gorda y debe descomponerse antes de implementar.

### Por qué importa en MWT

mwt.one tiene 9 secciones declaradas en `ENT_PLAT_FRONTENDS §B` (Operaciones, Contabilidad, Pricing, Catálogo, Amazon Ads, Marketplace, Distribución, Forecast, Configuración). Sin disciplina de tesis, cada una se convierte en "todo lo de X" y termina con pestañas internas que duplican lo que hace otra sección. Pricing termina simulando, comparando, alertando y reportando — y se solapa con Contabilidad y con Forecast. La tesis fuerza decidir qué es **el corazón** de la sección.

### Cómo se aplica (operativo)

1. Antes de mockear o codear una pantalla nueva, escribí la tesis y ponela en el header del mock o como comentario al tope del archivo.
2. Si una sección existente no tiene tesis explícita, derivala de los workflows que ya soporta y validá que ningún elemento UI esté fuera de esa tesis.
3. Reviewer: si encuentra elementos en pantalla que no se derivan de la tesis → flag `CONCEPTUAL_FAT`.

### Antipatrones específicos MWT

- "El módulo Pricing también tiene histórico de cambios, alertas de margen, y un comparador con Contabilidad." → 4 cosas, 4 secciones potenciales.
- Dashboard CEO con 12 cards heterogéneas sin tesis unificadora.
- Portal B2B mostrando catálogo + tracking + facturación + soporte en una sola pantalla "Mi cuenta".

### Flags

- `THESIS_TOO_FAT` — severidad **P1** — descomponer antes de implementar.
- `CONCEPTUAL_FAT` — severidad **P1** — auditar elementos fuera de la tesis declarada.

### Ejemplo MWT correcto

> _"El CEO puede ver el estado vivo de todos los expedientes activos para detectar desvíos de tiempo o margen vía un timeline con semáforo y alertas."_ (138 chars)

### Ejemplo MWT incorrecto

> _"Pricing es donde gestionamos precios, fórmulas, simulaciones, comparaciones B vs C, históricos, alertas de margen, política de descuentos y reportes."_ → 5+ thesis pegadas.

---

## M2 — SINGLE SOURCE OF TRUTH + CANONICALIZACIÓN DE TÉRMINOS

_(derivado de FB-P3 — el más crítico para MWT)_

### Enunciado

Las "reglas inquebrantables" del dominio (`expediente`, `cliente B2B`, `distribuidor`, `proforma`, `factura`, `BL/AWB`, `POD`, `reloj crédito 90d`, `margen vivo`, `marca`, `mercado`, `SKU`) tienen **una única forma canónica** y esa misma cadena exacta aparece en **todo el frontend** donde el concepto se mencione.

Prohibido: "Expediente" en una pantalla and "Operación" en otra. "Cliente" en un menú and "Cuenta" en otro. "Pago" en Contabilidad and "Cobro" en Distribución. "Reloj crédito" en B2B and "Plazo de pago" en CEO. "Costo origen" en Pricing and "FOB" en Forecast cuando se refieren a lo mismo.

`POL_NUNCA_TRADUCIR` extiende M2: SKUs (RW-GOL-MED-S5), nombres técnicos (LeapCore, NanoSpread, ThinBoom), nombres de marca (Marluvas, Rana Walk, Tecmater), tallas y refs nunca se traducen ni se localizan — son cadenas inmutables del sistema.

### Por qué importa en MWT

Hoy `POL_DETERMINISMO` v1.2 manda "dato único" pero el alcance original es backend (un dato vive en un solo archivo de la KB). En frontend, el problema no es de almacenamiento sino de **vocabulario**: el mismo concepto se nombra distinto en distintas pantallas porque cada una se desarrolló sin glosario centralizado. Esto es el primer punto donde un cliente B2B se confunde y abre un ticket, y el primer punto donde un agente IA que consume `ranawalk.com` produce respuestas inconsistentes ("¿es Pedido o Expediente? ¿Es factura o invoice?"). M2 cierra ese boquete.

### Cómo se aplica (operativo)

1. Mantener un **glosario UI canónico** en `ENT_PLAT_FRONTENDS §UI_GLOSSARY` (a crear si no existe). Cada término del dominio tiene una y solo una forma de UI por idioma.
2. En el code: extraer todos los strings de dominio a `i18n/dominio.es.json` (y `.en.json`, `.pt-BR.json`) — nunca hardcodear "Expediente" o "Operación" en el JSX.
3. Reviewer: si detecta drift (mismo concepto, dos strings) → flag `DRIFT_DETECTED` con `{term_variant, location, canonical_expected}`.
4. Términos `POL_NUNCA_TRADUCIR` (SKUs, tech names, brands, sizes) deben pasarse por una función helper `canonical(value)` que garantice que no entran al pipeline de i18n.

### Antipatrones específicos MWT

- "Crédito" / "Plazo de pago" / "Reloj 90d" / "Días por cobrar" usados intercambiablemente.
- "Distribuidor" en Distribución pero "Reseller" en Amazon Ads.
- Botón "Confirmar pago" en CEO y "Marcar como pagado" en B2B (mismo command).
- SKU mostrado como "rw-gol-med-s5" en una pantalla y "RW Gol Medio S5" en otra.
- Marca mostrada como "RanaWalk" en un menú y "Rana Walk" en otro.

### Flags

- `DRIFT_DETECTED` — severidad **P0** — bloquea, unificar al término canónico antes de mergear.
- `TRANSLATION_LEAK` — severidad **P0** — un término `POL_NUNCA_TRADUCIR` entró al pipeline i18n.

### Ejemplo MWT

- ❌ Sidebar CEO: "Operaciones" · Sidebar B2B: "Mis Pedidos" · Email transaccional: "Tu importación".
- ✅ Sidebar CEO: "Expedientes" · Sidebar B2B: "Mis Expedientes" · Email: "Estado de tu Expediente #EXP-2026-0047".

---

## M3 — PROGRESSIVE DISCLOSURE + COGNITIVE LOAD

_(derivado de FB-P5)_

### Enunciado

La acción primaria de cualquier pantalla debe ser obvia al primer vistazo. Un novato debe entender el 20% más usado sin entrenamiento; el power-user debe poder llegar al 100% sin cambiar de pantalla. Cada elemento interactivo debe **gritar su propósito** vía label, ícono o affordance.

### Por qué importa en MWT

Los tres frontends MWT tienen densidades muy distintas. mwt.one carga al CEO con métricas, alertas, simuladores y kanbans porque su trabajo es ese (densidad alta, justificada). Pero `portal.mwt.one` heredando "el mismo frontend con permisos" — como dice hoy `ENT_PLAT_FRONTENDS §D` — significa que un cliente B2B novato se enfrenta a la misma densidad que el CEO, lo cual rompe M3. La solución no es ocultar (eso lo cubre M4) sino **graduar la disclosure**: B2B ve los 4 estados macro de su expediente y un CTA claro; CEO ve los 8 estados, los costos por línea, las desviaciones históricas y las alertas.

### Cómo se aplica (operativo)

1. Definir niveles de disclosure por pantalla y por rol: `default` (lo más usado), `expanded` (todo el detalle), `expert` (configuración avanzada). Nunca genéricamente "Advanced mode".
2. Controles operativos de uso frecuente (>3 veces/día) → ambient en la UI principal, nunca enterrados en menús "Más" o "Avanzado".
3. Cada elemento debe tener label visible o tooltip — íconos solos sin texto solo se permiten cuando son convención universal (papelera, lápiz, cerrar X).
4. Una pantalla no debe requerir más de 3 decisiones simultáneas para el rol target.

### Antipatrones específicos MWT

- Esconder el "Generar Proforma" del CEO bajo un menú "..." cuando es la acción que dispara 80% de los expedientes.
- Mostrar al cliente B2B los 8 estados granulares del expediente cuando él solo necesita 4 macro-estados (Confirmado / En tránsito / En aduana / Listo).
- Listing Amazon con filtros expertos (ACoS, TACoS, click-share) en la vista default cuando la acción primaria es "publicar/despublicar".
- Pricing simulator que pide elegir marca + mercado + canal + currency + modelo B/C antes de mostrar nada.

### Flags

- `AMBIENT_VISIBILITY_LOSS` — severidad **P1** — sacar control de la zona oculta.
- `OVERLOADED_DEFAULT` — severidad **P1** — la vista default tiene >3 decisiones simultáneas.

### Ejemplo MWT

- ❌ Pantalla de Expediente CEO: 30 campos en grilla densa, sin jerarquía.
- ✅ Pantalla de Expediente CEO: hero con estado + margen vivo + alerta si la hay; secciones colapsables (Costos, Documentos, Comunicación, Histórico) con default colapsado salvo la sección que disparó el ingreso.

---

## M4 — PROGRESSIVE DISCLOSURE POR ROL (acciones bloqueadas se EXPLICAN, no se ocultan)

_(derivado de FB-P7)_

### Enunciado

El sistema de roles y visibilidad (`POL_VISIBILIDAD`: PUBLIC / PARTNER_B2B / INTERNAL / CEO-ONLY) determina qué ve cada usuario, **pero las acciones prohibidas se explican, no desaparecen silenciosamente**. Mal: el botón no está. Bien: el botón está deshabilitado con tooltip "Requiere ROLE_DISTRIBUIDOR" o ítem fantasma en navegación con etiqueta "Solo CEO". Nunca `display:none` sin explicación.

### Por qué importa en MWT

`ENT_PLAT_FRONTENDS §D` describe el portal B2B como "mismo frontend con permisos y vistas diferentes según rol". Sin M4 esto produce el bug clásico de soporte: "yo no veo ese botón que dice el manual" → ticket → CEO descubre que un permiso está mal seteado para el rol. Si el botón estuviera deshabilitado con explicación, el cliente sabría inmediatamente qué pedirle a su admin. M4 también previene que distribuidores intenten acceder a comisiones de otros distribuidores: el ítem aparece pero ghost con "No autorizado para este territorio".

### Cómo se aplica (operativo)

1. Estado canónico de un control: `enabled` / `disabled+reason` / `ghost+requirement` / `hidden_only_if_pol_visibilidad_blocks_completely`.
2. La opción `hidden` se reserva exclusivamente para datos `CEO-ONLY` (regla de `POL_VISIBILIDAD`) — y nunca se aplica a controles que el rol "podría" tener si cambiara su nivel.
3. Tooltips de bloqueo deben usar lenguaje accionable: "Requiere ROLE_X" / "Disponible al confirmar Y" / "No autorizado para mercado Z" — nunca "No tienes permiso".
4. Pre-filtering en retrieval (heredado de `ARCH_AGENT_PRINCIPLES P13`): los datos que el usuario no está autorizado a ver **nunca se cargan al contexto del frontend** — no es output filtering, es input filtering.

### Antipatrones específicos MWT

- Cliente B2B con rol "ver pedidos" abre el detalle de un expediente y el botón "Editar fecha de entrega" simplemente no aparece. El cliente cree que es un bug.
- Distribuidor de mercado USA ve la sección "Distribución BR" enteramente vacía sin explicación.
- Sub-distribuidor ve el panel de comisiones del distribuidor padre vacío en lugar de bloqueado-con-razón.

### Flags

- `ROLE_LEAK` — severidad **P0** — el frontend recibió data que el rol no debería ver (falla de pre-filtering).
- `SILENT_BLOCK` — severidad **P1** — control oculto sin explicación accionable.

### Ejemplo MWT

- ❌ "Aprobar Pago" desaparece para roles distintos a CFO.
- ✅ "Aprobar Pago" aparece deshabilitado con tooltip: "Requiere ROLE_CFO. Pedí aprobación a tu admin."

---

## M5 — SYSTEM COHESION END-TO-END (cross-frontend)

_(derivado de FB-P4)_

### Enunciado

Cada flujo del dominio debe poder mapearse desde el trigger hasta el estado terminal **incluyendo cruces entre los 3 frontends**. Si una acción en mwt.one debe propagarse a portal.mwt.one o disparar un email/webhook hacia el cliente, ese flujo entero está documentado. Si una pantalla no se alcanza desde un entry point por un flujo declarado: no existe.

### Por qué importa en MWT

El mismo Expediente vive en los 3 frontends a la vez: CEO lo ve completo en mwt.one, el cliente B2B lo ve filtrado en portal.mwt.one, los agentes IA pueden consultarlo en `ranawalk.com` (parcialmente, vía endpoints públicos UCP/ACP/MCP). Cuando el CEO mueve un expediente a "En Tránsito", esa transición debe propagarse en tiempo real al portal B2B (vía WebSocket), disparar email transaccional al cliente, y actualizar el estado público si el agente IA lo consulta. Sin M5 documentado, cada cambio de estado introduce drift entre los 3 frontends.

### Cómo se aplica (operativo)

1. Cada `command` de `ENT_OPS_STATE_MACHINE` debe tener un mapa de propagación documentado: qué frontends afecta, qué notificaciones dispara, qué webhooks emite.
2. WebSocket es el canal de invalidación realtime entre mwt.one y portal.mwt.one (stack canónico).
3. El estado terminal de un flujo no es "el CEO marcó la transición" — es "todos los actores afectados (cliente B2B, distribuidor, sistemas externos) están sincronizados".
4. Reviewer: si un mock muestra una pantalla pero no hay entry point declarado desde otra → flag `FLOW_GAP`.

### Antipatrones específicos MWT

- CEO marca pago recibido en mwt.one y el cliente B2B sigue viendo "Pendiente de pago" 2 horas después porque la propagación es por polling cada hora.
- Pantalla "Detalle de comisión" en portal.mwt.one a la que solo se llega vía URL directa, sin link desde el dashboard del distribuidor.
- Email transaccional al cliente con un estado que no coincide con el estado en su portal.

### Flags

- `FLOW_GAP` — severidad **P1** — pantalla sin entry point declarado.
- `STATE_DRIFT` — severidad **P0** — los 3 frontends muestran estados distintos del mismo objeto.

### Ejemplo MWT

- ❌ Comando `MarkPaymentReceived` documentado solo en CEO; el cliente B2B descubre el cambio porque revisa manualmente.
- ✅ `MarkPaymentReceived` documenta: actualiza Expediente.payment_status; emite WebSocket a portal.mwt.one; dispara email transaccional `payment_received_es.html`; emite webhook a sistema contable.

---

## M6 — OPERATIONAL MUSCLE PROTECTION

_(derivado de FB-P11)_

### Enunciado

Las superficies operativas core del Centro de Operaciones MWT son **músculo**, no grasa. No se "absorben" en layouts chat-first, no se esconden bajo "Modo avanzado", no se simplifican removiendo capacidad. Si un diseño propone removerlas o colapsarlas: flag `MUSCLE_AMPUTATION` y HALT — escalar al CEO.

### Superficies protegidas (catálogo MWT)

- **Timeline de expedientes con semáforo** (verde/amarillo/rojo basado en histórico de tiempos por ruta)
- **Bundle de artefactos del expediente** (proforma → invoice comercial → BL/AWB → certificado origen → factura DIAN/SII/SAT/AFIP/NF-e → POD)
- **Margen vivo por expediente** (costo acumulado vs proyectado en tiempo real)
- **Reloj de crédito 90d** (cuántos días lleva cada cuenta por cobrar)
- **Pricing simulator B vs C** (simulación side-by-side de los dos modelos)
- **Kanban de alertas operativas** (expediente desviado de tiempos, costo > proyección, cliente debería reordenar)
- **Comparativa retroactiva** ("¿qué hubiera pasado si hubiera elegido otro modelo?")
- **Vista Amazon Ads ambient** (ACoS por producto en la card del producto, no en pestaña separada)

### Por qué importa en MWT

MWT es una plataforma operativa, no un asistente conversacional. La amenaza emerge cuando alguien intenta meter Cowork o un asistente IA dentro de mwt.one con la idea de "mover todo al chat" — eso convertiría el dashboard en un thread con tarjetas y destruiría la capacidad de leer 30 expedientes de un vistazo. M6 codifica que el dashboard operativo es **mesa de control**, no es chat con superpoderes.

### Cómo se aplica (operativo)

1. Cada superficie del catálogo está en pantalla de primera clase (sidebar o sección dedicada), no detrás de un botón "Ver más".
2. Si una propuesta de rediseño quiere mover una superficie del catálogo a un drawer, modal o subpantalla: requiere aprobación CEO explícita.
3. Asistentes IA (Cowork integrado, agentes específicos) viven **junto a** las superficies operativas, no las reemplazan. El chat es un complemento, no el contenedor.
4. Reviewer: cualquier propuesta que reduzca densidad de información en el Centro de Operaciones requiere justificar que no se está amputando músculo.

### Antipatrones específicos MWT

- "Vamos a reemplazar el timeline por un chat con Cowork donde el CEO pregunte 'qué expedientes están en riesgo'." → amputa la capacidad de detectar visualmente patrones de desvío.
- "El pricing simulator se simplifica a una sola tabla, eliminamos la comparativa B vs C porque genera confusión." → amputa la decisión central de pricing MWT.
- "El kanban de alertas se mueve a una página de notificaciones." → exilia el sistema nervioso del CEO.

### Flags

- `MUSCLE_AMPUTATION` — severidad **P0** — HALT, escalar al CEO.
- `MUSCLE_REMOVAL_RISK` — severidad **P0** — propuesta sospechosa de amputar, pedir justificación.

---

## M7 — AMBIENT ECONOMICS (margen, costo, crédito en contexto)

_(derivado de FB-P13)_

### Enunciado

Las métricas económicas core de MWT (**margen vivo**, **costo acumulado vs proyectado**, **reloj crédito 90d**, **rentabilidad por cliente/marca/expediente**, **cash flow proyectado**) deben ser visibles **en contexto** — en la card del expediente, en la fila de la tabla, en el header del cliente B2B — **nunca exiliadas** a una pestaña "Contabilidad" o "Reportes" como única vía de consulta.

### Por qué importa en MWT

El negocio MWT entero **es** unit economics. La diferencia entre un expediente rentable y uno perdedor son 3-5 puntos de margen. Si para ver ese dato hay que cambiar de pestaña, el CEO no lo mira en el momento de decidir, y los agentes que comparan modelos B vs C pierden el dato más importante. `ENT_PLAT_FRONTENDS §B2` ya lista estas métricas como métricas clave — M7 las eleva de "métricas listadas" a "invariante de UI".

### Cómo se aplica (operativo)

1. Toda card de expediente (en kanban, lista, detalle) muestra: estado · margen vivo · días en crédito · alerta si la hay. Estos 4 son ambient.
2. Toda card de cliente B2B muestra: nombre · mercado · cuentas por cobrar · días promedio en crédito.
3. Toda card de producto en Amazon muestra: ACoS · TACoS · margen.
4. La pestaña "Contabilidad" existe para análisis profundo (P&L, drill-down, exportar) — pero los números deben estar accesibles desde el contexto donde se decide.
5. Reviewer: si una decisión se toma sin tener la métrica económica relevante visible → flag `ECONOMICS_EXILED`.

### Antipatrones específicos MWT

- Card de expediente que solo muestra estado y fecha; el margen vive en Contabilidad.
- Listing Amazon que muestra el título y el precio pero no el ACoS.
- Vista de cliente B2B que muestra sus pedidos pero no su saldo por cobrar.

### Flags

- `ECONOMICS_EXILED` — severidad **P1** — métrica económica relevante para la decisión no está en contexto.

### Ejemplo MWT

- ❌ Kanban CEO: cards con `[EXP-2026-0047] Marluvas · En tránsito`
- ✅ Kanban CEO: cards con `[EXP-2026-0047] Marluvas · En tránsito · margen 18% (proy. 22%) · 47d en crédito`

---

## M8 — CONTEXTUAL NAVIGATION (jerarquía y contexto reciente como navegación de primera clase)

_(derivado de FB-P14)_

### Enunciado

El **contexto activo del usuario** (último expediente abierto, marca activa, mercado activo, cliente B2B en foco, distribuidor seleccionado, rango de fechas, modelo B vs C en simulación) es navegación de primera clase — vive en sidebar, topbar o sticky panels. **No se entierra** en dropdowns "Recientes", menús "Más" o toggles "Modo avanzado".

### Por qué importa en MWT

mwt.one navega entre 9 secciones, 3 marcas (Marluvas / Rana Walk / Tecmater), 3 mercados activos (USA / CR / BR), 657+ SKUs, decenas de clientes B2B y distribuidores. Sin M8, el CEO pasa la mayor parte del tiempo re-seleccionando filtros. Con M8, el contexto se mantiene visible y modificable desde cualquier sección — cambiar de "Marluvas USA" a "Rana Walk BR" es un click en el topbar, no un re-tour por 4 menús.

### Cómo se aplica (operativo)

1. **Contexto global persistente** en topbar: marca activa · mercado activo · rango temporal. Cambia con un click, persiste cross-sección.
2. **Breadcrumbs canónicos** en cada vista de detalle: `Expedientes > Marluvas > USA > EXP-2026-0047 > Costos`.
3. **Recent items** en sidebar (últimos 5 expedientes / últimos 3 clientes B2B vistos), no en un menú colapsado.
4. **Trace IDs** en outputs de operación (último command ejecutado, último agente que actuó) visibles en el panel lateral, no en logs.
5. Reviewer: si un usuario debe re-tipear o re-seleccionar contexto que ya estableció → flag `NAVIGATION_BURIED`.

### Antipatrones específicos MWT

- Filtro de marca en cada sección por separado, sin estado global.
- "Últimos expedientes vistos" enterrado en un dropdown del avatar del usuario.
- Cliente B2B que abrió un expediente, navegó a "Documentos" y al volver a "Mis Expedientes" perdió el filtro que tenía aplicado.

### Flags

- `NAVIGATION_BURIED` — severidad **P1** — contexto activo escondido o no persistente.

---

## M9 — EXTERNAL AFFORDANCE (la UI se enseña sola, también a los agentes IA)

_(derivado de FB-P10)_

### Enunciado

El usuario externo (consumidor humano sin training **y agente IA sin manual**) entiende `ranawalk.com` y los flujos públicos del portal B2B sin explicación previa. Test del principio: si tenés que decirle al usuario qué hacer, la UI falló. El producto se enseña a sí mismo. Para agentes IA, el equivalente son los endpoints UCP/ACP/MCP, el `llms.txt` y el schema markup — la "UI" para máquinas debe ser igualmente auto-explicativa.

### Por qué importa en MWT

`ranawalk.com` es 100% external (público + agentes IA). Un consumidor humano busca "calzado de seguridad industrial Marluvas" en Google y aterriza en una product page sin contexto. Un agente IA consume el feed `ranawalk.com/llms.txt` y los endpoints UCP para responderle a un comprador "compráme estos zapatos en talla 42". En ambos casos no hay manual, no hay onboarding, no hay agente humano del lado MWT explicando. M9 es la version visible+semántica de "auto-suficiencia external".

### Cómo se aplica (operativo)

1. **Para humanos:** label visible siempre, ícono solo si universal, CTAs primarios en el viewport sin scroll, microcopy explicativo bajo cada decisión.
2. **Para agentes IA:** schema markup completo (`Product`, `Offer`, `Organization`, `Brand`), endpoints UCP/ACP con OpenAPI bien documentado, `llms.txt` con la jerarquía del catálogo + políticas de uso.
3. **Test ácido:** un usuario nuevo debe completar la acción primaria de la pantalla en menos de 30 segundos sin ayuda.
4. **Test ácido para agentes:** un agente con solo el `llms.txt` debe poder construir una request ACP válida para comprar un SKU.
5. Reviewer: si la documentación de uso público está separada del producto (un manual aparte) → flag `MANUAL_REQUIRED`.

### Antipatrones específicos MWT

- Product page Rana Walk que requiere haber leído un blog para entender qué significan "LeapCore" o "ThinBoom" (tech names `POL_NUNCA_TRADUCIR`) sin tooltip o microcopy explicativo.
- Endpoint UCP cuyo schema no expone el SKU canónico, solo un ID interno.
- Formulario de pedido B2B que pide "modelo de operación (B o C)" sin explicar qué significa cada uno para un cliente nuevo.
- `llms.txt` que solo lista URLs sin describir el modelo de datos.

### Flags

- `MANUAL_REQUIRED` — severidad **P1** — la UI requiere documentación externa para usarse.
- `OPAQUE_TO_AGENTS` — severidad **P1** — el schema/feed/endpoint no es auto-descriptivo para agentes IA.

### Ejemplo MWT

- ❌ Product page con título "Goliath Med S5" sin explicar qué es Goliath, qué significa Med, qué significa S5.
- ✅ Product page con: título canónico "Goliath Med S5" + tagline "Botín de seguridad industrial · suela MED · talla S5 (EU 38-39)" + tooltip sobre cada token técnico.

---

# Catálogo de flags consolidado

| Flag                      | Principio | Severidad | Acción                                 |
| ------------------------- | --------- | --------- | -------------------------------------- |
| `THESIS_TOO_FAT`          | M1        | P1        | descomponer antes de implementar       |
| `CONCEPTUAL_FAT`          | M1        | P1        | auditar elementos fuera de la tesis    |
| `DRIFT_DETECTED`          | M2        | **P0**    | unificar al término canónico           |
| `TRANSLATION_LEAK`        | M2        | **P0**    | sacar término de pipeline i18n         |
| `AMBIENT_VISIBILITY_LOSS` | M3        | P1        | sacar control de "Avanzado"            |
| `OVERLOADED_DEFAULT`      | M3        | P1        | reducir decisiones por pantalla        |
| `ROLE_LEAK`               | M4        | **P0**    | falla de pre-filtering en retrieval    |
| `SILENT_BLOCK`            | M4        | P1        | explicar el bloqueo, no ocultar        |
| `FLOW_GAP`                | M5        | P1        | agregar entry point declarado          |
| `STATE_DRIFT`             | M5        | **P0**    | sincronizar estado cross-frontend      |
| `MUSCLE_AMPUTATION`       | M6        | **P0**    | HALT — escalar al CEO                  |
| `MUSCLE_REMOVAL_RISK`     | M6        | **P0**    | reabrir decisión, pedir justificación  |
| `ECONOMICS_EXILED`        | M7        | P1        | hacer métrica ambient en contexto      |
| `NAVIGATION_BURIED`       | M8        | P1        | promover contexto a sidebar/topbar     |
| `MANUAL_REQUIRED`         | M9        | P1        | hacer la UI auto-explicativa           |
| `OPAQUE_TO_AGENTS`        | M9        | P1        | enriquecer schema / llms.txt / OpenAPI |

**Severidades:**

- **P0** = bloquea la propuesta. HALT, escalar al CEO.
- **P1** = warning fuerte. Recomendar fix antes de mergear.
- **P2** = nota. Registrar como deuda técnica de UX.

---

# Antipatrones de rechazo automático

La lente rechaza inmediatamente cualquiera de estos patrones, independientemente del contexto:

1. **Inventar datos** que no están en el mock, la spec o la KB.
2. **Sinónimos** para términos canónicos del dominio (M2).
3. **Features "nice to have"** que ningún workflow pidió.
4. **Esconder acciones sin explicación** (silent removal — M4).
5. **Mergear `display:none`** controles que distintos roles deberían ver bloqueados.
6. **Mover superficies del catálogo M6** a drawers, modals o subpantallas.
7. **Exiliar métricas económicas** a la pestaña Contabilidad como única vía (M7).
8. **Hardcodear strings de dominio** en JSX en lugar de extraer al glosario UI canónico (M2).
9. **Traducir términos `POL_NUNCA_TRADUCIR`** (SKUs, tech names, brands).
10. **Bypass del governance gate** del Expediente (intentar mover de `OPENED` a `CLOSED` sin pasar por estados intermedios).
11. **Diseñar para un solo frontend** sin considerar la propagación a los otros 2 (M5).

---

# Modos de despliegue

| Modo                               | Cómo se activa la lente                                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Claude Project (este proyecto)** | Archivo en KB; la lente se activa cuando se discute frontend MWT                                                      |
| **Claude Code / Cowork**           | Referenciar este SKILL en system prompt o leer al inicio de sesiones de UI MWT                                        |
| **Custom Instructions**            | Pegar sección "Los 9 principios MWT (canon)" + "Catálogo de flags" + "Antipatrones de rechazo automático"             |
| **Subagent dedicado**              | Si el trabajo es grande (rediseño completo de una sección), envolver en agente con workflow Audit→Spec→Implementation |

---

# KB refs (consultar bajo demanda, no en cada iteración)

- `ARCH_AGENT_PRINCIPLES` — 14 principios fundacionales del ecosistema MWT/FB (P9 gobernanza embebida es análogo conceptual)
- `ENT_PLAT_FRONTENDS` v2.0 — los 3 frontends MWT
- `ENT_PLAT_DESIGN_TOKENS` v1.1 (APROBADO Sprint 3) — tokens canónicos
- `ENT_OPS_STATE_MACHINE` (FROZEN) — 8 estados expediente, fuente canónica de la spec del dominio
- `POL_DETERMINISMO` v1.2 — dato único + vacío explícito
- `POL_NUNCA_TRADUCIR` — qué cadenas son inmutables
- `POL_VISIBILIDAD` — los 4 tiers de visibilidad
- `POL_ANTI_CONFUSION` — Navy MWT vs Navy E1 Goliath
- `docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` v2.1 — skill canónico FB del que este deriva (referencia de trazabilidad)

La lente NO obliga a leer estos archivos en cada iteración. Los lee bajo demanda cuando un principio (especialmente M2 canonicalización, M4 visibility, M5 cross-frontend cohesion) requiere ground truth canónico.

---

## Changelog

- **v1.0 — 2026-05-04 (CEO + Arquitecto Cowork):** creación inicial. Selección 9/14 principios FB con adaptación a contexto MWT (3 frontends, expediente como objeto canónico, dashboard CEO power-user, portal B2B novato-friendly, ranawalk.com público + agentes IA). Renumerados M1-M9 con trazabilidad explícita al principio FB de origen. Catálogo de flags MWT-específico (16 flags, 4 P0 bloqueantes). Antipatrones de rechazo automático adaptados al dominio MWT. Status SHADOW hasta validación en primer mock real (mwt.one o portal.mwt.one).

---

## Pendientes

- [ ] Agregar fila en `SKILL_RUNTIME.md` (SKILL_FRONTEND_PRINCIPLES_MWT, autonomy ACTIVO_BG, SHADOW)
- [ ] Append a `MANIFIESTO_APPEND_*.md` documentando creación
- [ ] Crear `ENT_PLAT_FRONTENDS §UI_GLOSSARY` (glosario canónico de términos UI MWT) — referenciado por M2
- [ ] Sync al repo canónico vía script estándar
- [ ] Validar primera aplicación en una iteración real (kanban CEO, portal B2B, o ranawalk.com product page) → pasar a VIGENTE si la lente colorea sin generar fricción
- [ ] Agregar fila en `IDX_PLATAFORMA.md` sección Skills
- [ ] Decisión CEO: si después de 3+ aplicaciones exitosas en MWT, el FB skill v2.1 se promueve a `[SHARED]` reemplazando este o ambos coexisten
