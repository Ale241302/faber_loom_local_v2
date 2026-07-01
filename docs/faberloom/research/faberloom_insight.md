# Insight Extraction: FaberLoom Design Foundation
## Phase 6 — Cross-Dimension Insights

**Fecha:** 2026-05-11
**Dimensiones cruzadas:** 12
**Insights extraídos:** 12 (mínimo requerido: 5)

---

## Insight 1: DTCG + CSS Variables como arquitectura dual es el único camino viable para multi-tenant agentic

**Insight:** Ningún formato de design tokens existente soporta multi-tenancy nativamente. Sin embargo, la combinación DTCG (source of truth formal) + CSS Custom Properties (runtime implementation) resuelve ambos problemas: los agentes IA consumen DTCG para generar UI consistente, y cada tenant recibe su CSS bundle resuelto en edge sin runtime overhead.

**Derived From:** Dim01 (format comparison), Dim02 (multi-tenant architecture), Dim03 (enterprise adoption)

**Rationale:** Las empresas enterprise (Shopify, Atlassian, Salesforce) ya operan con esta dualidad: mantienen tokens como source of truth y exportan a CSS variables. Para FaberLoom, donde agentes IA generan UI desde tokens, tener un formato formal parseable (DTCG JSON) es obligatorio. CSS variables solo no bastan para generación programática.

**Implications:** La arquitectura de FaberLoom debe tener: (1) DTCG JSON por tenant en PostgreSQL JSONB, (2) Style Dictionary v4+ como build pipeline, (3) CSS bundle resuelto servido por CDN con content-hash, (4) DESIGN.md como capa semántica opcional para LLMs (no como source of truth).

**Confidence:** high

---

## Insight 2: El "Trust Ladder" es el principio arquitectónico que une a todos los demás

**Insight:** Todos los principios UX de más alto score para FaberLoom (#1 Progressive Disclosure, #2 Trust Ladder, #3 HITL Estratégico) están subordinados a un único principio arquitectónico: el sistema debe construir confianza progresivamente con el usuario industrial. Esto no es un principio de UX más, es la estrategia de producto completa.

**Derived From:** Dim06 (Anthropic philosophy), Dim07 (Claude patterns), Dim09 (UX principles), Dim10 (approval flows)

**Rationale:** En industria textil, un error de UI puede detener una línea de producción. La "consent fatigue" del 93% (Dim07) significa que aprobaciones excesivas degradan la experiencia, pero aprobaciones insuficientes son peligrosas. La solución es un espectro de autonomía calibrado por evidencia acumulada: empieza conservador, recopila datos, ajusta.

**Implications:** FaberLoom necesita un "Autonomy Engine" que: (1) registre cada decisión del agente y su outcome, (2) calibre el umbral de auto-approval basado en historial de éxito por tipo de acción, (3) nunca auto-approve acciones destructivas (parar línea, eliminar datos), (4) permita override manual instantáneo.

**Confidence:** high

---

## Insight 3: Sanidad como tab primario es la diferenciación más grande y más riesgosa de FaberLoom

**Insight:** Ninguna plataforma agentic existente (LangGraph, AutoGen, CrewAI, Vercel v0, Bolt, Cursor) implementa "Validación/Sanidad" como un tab primario de igual jerarquía que Configuración e Iteración. Esto es simultáneamente la mayor oportunidad de diferenciación y el mayor riesgo de descubribilidad del producto.

**Derived From:** Dim11 (agent orchestration UI), Dim12 (observability patterns)

**Rationale:** En industria manufacturera, "sanidad" (QA/validación) es un paso obligatorio regulado (ISO, Six Sigma). Los usuarios industriales están condicionados a verificar antes de aprobar. Hacer Sanidad un tab primario, no una función oculta en un menú, alinea con el modelo mental del usuario industrial.

**Implications:** El tab Sanidad debe incluir: (1) visual diff de cambios propuestos, (2) scorecard de calidad automática (contrast, accessibility, consistency), (3) trazabilidad completa (quién, qué, cuándo, por qué), (4) aprobación con comentario obligatorio para cambios de alto impacto. Este tab es el que justifica el precio enterprise de FaberLoom.

**Confidence:** medium (alto en diferenciación, medio en adopción por usuarios)

---

## Insight 4: El AG-UI Protocol resuelve el problema de comunicación agente-UI que ningún otro estándar toca

**Insight:** Mientras DTCG estandariza design tokens, AG-UI Protocol estandariza los eventos entre agentes y UI. Los 17 eventos (RUN_STARTED, STEP_STARTED, TOOL_CALL_START, STATE_DELTA, etc.) permiten que cualquier agente backend se comunique con cualquier frontend sin acoplamiento.

**Derived From:** Dim11 (orchestration UI), Dim12 (observability)

**Rationale:** FaberLoom tiene 3 tabs (Configurar, Iterar, Sanidad) con múltiples agentes posibles. Sin un protocolo estándar, cada integración agente-UI sería custom. AG-UI permite: (1) agregar nuevos tipos de agentes sin cambiar la UI, (2) migrar entre backends (LangGraph, CrewAI, custom) sin reescribir el frontend, (3) observabilidad consistente sin importar el agente.

**Implications:** FaberLoom debe adoptar AG-UI Protocol como capa de comunicación entre agentes y frontend. Esto es arquitectura, no feature — un decision irreversible que debe tomarse en el diseño inicial.

**Confidence:** medium (el protocolo es nuevo, adopción en progreso)

---

## Insight 5: Los 3 botones (Aprobar/Descartar/Iterar) necesitan un 4to estado invisible: "Auto-approve silencioso"

**Insight:** El patrón 3-botones es correcto para el MVP, pero la evidencia de Anthropic (93% consent fatigue, Dim07) y Cursor (auto-approve configurable, Dim10) muestra que a largo plazo FaberLoom necesita un cuarto estado: auto-approval progresivo basado en confianza acumulada.

**Derived From:** Dim07 (Claude approval modes), Dim10 (approval patterns), Dim09 (Trust Ladder)

**Rationale:** En operación diaria, un supervisor de fábrica no puede aprobar cada ajuste de UI. Si el agente ha generado 50 ajustes cosméticos exitosos con 95%+ de aceptación, el sistema debería poder auto-aprobar el tipo 51 con notificación silenciosa. Pero esto requiere: (1) clasificador de riesgo por tipo de cambio, (2) historial de aprobaciones por usuario/tenant, (3) override instantáneo visible.

**Implications:** Arquitectura de 4 niveles: Level 0 (siempre human approval) → Level 1 (confidence >90%, notify only) → Level 2 (confidence >95%, silent log) → Level 3 (full auto, daily digest). Cada tenant configura su nivel; cada usuario puede bajar el nivel individualmente.

**Confidence:** medium

---

## Insight 6: DESIGN.md no es competidor de DTCG — es capa de presentación para LLMs

**Insight:** DESIGN.md (Google Labs) y DTCG no son formatos competidores sino complementarios en una arquitectura de agentes IA. DTCG es el formato de intercambio estructurado; DESIGN.md es la presentación semántica para consumo por LLMs. El primero es para máquinas (parseo); el segundo es para modelos de lenguaje (comprensión contextual).

**Derived From:** Dim01 (format comparison), Dim06 (Anthropic patterns)

**Rationale:** Los agentes IA de FaberLoom necesitan dos cosas: (1) tokens estructurados para generar UI consistente (DTCG), y (2) comprensión contextual de la identidad visual para interpretar correctamente solicitudes ambiguas (DESIGN.md). Anthropic usa un approach similar: CLAUDE.md para contexto del proyecto + herramientas formales para ejecución.

**Implications:** FaberLoom debería: (1) almacenar tokens en DTCG JSON como source of truth, (2) exportar/generar DESIGN.md por tenant como "brief de diseño" que el agente lee antes de generar UI, (3) mantener ambos en sync automáticamente via CI/CD.

**Confidence:** high

---

## Insight 7: El chat-first de FaberLoom es correcto si y solo si el chat no es el único modo de interacción

**Insight:** La evidencia de Anthropic ("Chat para apertura, GUI para pasos intermedios", Dim06) y de plataformas agentic (chat + preview side-by-side, Dim11) muestra que el chat es excelente para iniciar pero insuficiente para tareas complejas. FaberLoom debe ser "chat-initiated, GUI-mediated".

**Derived From:** Dim06 (Anthropic philosophy), Dim11 (orchestration UI), Dim09 (B2B industrial)

**Rationale:** En una fábrica, un operador puede iniciar con "cambia el dashboard para mostrar OEE" (chat), pero la configuración detallada (posición de widgets, colores, filtros) requiere GUI directa. El chat-first no significa chat-only.

**Implications:** Los 3 tabs (Configurar/Iterar/Sanidad) deben tener: chat siempre visible para iniciar acciones, pero panel GUI para manipulación directa cuando el usuario lo necesite. No forzar chat para todo.

**Confidence:** high

---

## Insight 8: Role-based interfaces + multi-tenant tokens = arquitectura de personalización completa

**Insight:** La combinación de principios UX #4 (Role-Based Interfaces, Dim09) con la arquitectura multi-tenant de tokens (Dim02) crea un sistema de personalización bidimensional: cada rol en cada tenant ve una interfaz diferente, con su identidad visual, sus features, y sus flujos de trabajo.

**Derived From:** Dim02 (multi-tenant architecture), Dim09 (UX principles), Dim03 (enterprise adoption)

**Rationale:** Shopify ya hace esto (cada merchant ve su admin con su marca), pero lo hace con templates predefinidos. FaberLoom puede ir más allá: agentes IA que generan vistas personalizadas por rol y por tenant en tiempo real, usando tokens como constraints y prosa semántica como brief.

**Implications:** La arquitectura de tokens necesita: (1) base tokens (universales), (2) brand tokens (por tenant), (3) role tokens (por rol), (4) component tokens (por componente). Style Dictionary puede generar builds separados por (tenant, role) combinación.

**Confidence:** medium

---

## Insight 9: El costo de agentes IA debe ser visible para construir trust, pero no dominante

**Insight:** La evidencia de LangSmith/Langfuse (Dim12) y Anthropic Console muestra que los usuarios enterprise quieren ver cuánto cuesta cada operación de agente, pero mostrar costo en cada interacción genera ansiedad. El patrón correcto es: resumen por sesión + alerta si supera umbral.

**Derived From:** Dim12 (observability/cost), Dim07 (Claude patterns), Dim09 (trust)

**Rationale:** En manufactura, los gerentes de planta necesitan control de costos. Pero un operador no debería ver "$0.023 por consulta" en cada chat — eso inhibe el uso. El modelo correcto: dashboard administrativo con costos acumulados + alerta cuando un tenant supera su quota.

**Implications:** Panel de administrador: costo por tenant, por sesión, por tipo de agente. Panel de operador: solo alerta de "límite cercano" si aplica. Nunca mostrar costo per-interaction en la interfaz de trabajo.

**Confidence:** medium

---

## Insight 10: La navegación Configurar→Iterar→Sanidad debe ser lineal forward pero editable backward

**Insight:** Aunque FaberLoom define 3 tabs, la evidencia de wizards industriales (Dim09, ISA-101) y plataformas agentic (Dim11) muestra que los usuarios necesitan: (1) flujo lineal para aprender (Configurar → Iterar → Sanidad), (2) capacidad de saltar para expertos, (3) volver atrás para corregir sin perder trabajo.

**Derived From:** Dim11 (orchestration UI), Dim09 (industrial UX), Dim10 (approval flows)

**Rationale:** Los usuarios nuevos necesitan guía paso a paso. Los usuarios expertos necesitan saltar directamente a Iterar. Todos necesitan poder volver a Configurar sin perder el trabajo en Iterar.

**Implications:** Implementar: (1) wizard lineal por defecto para primer uso, (2) tabs saltables para usuarios avanzados, (3) draft auto-save entre tabs, (4) warning si se modifica Configurar después de haber avanzado a Iterar.

**Confidence:** high

---

## Insight 11: Los anti-patterns más peligrosos para FaberLoom son los que funcionan en consumer

**Insight:** Todos los anti-patterns que deberían prohibirse explícitamente en FaberLoom son patrones que funcionan bien en B2C/consumer pero son destructivos en B2B industrial: (1) dark patterns de engagement (notificaciones constantes), (2) chat-only sin GUI, (3) auto-approval sin historial, (4) onboarding intrusivo con tours de 10 pasos, (5) gamificación con puntos/badges.

**Derived From:** Dim09 (B2B industrial), Dim06 (Anthropic), Dim10 (approval patterns)

**Rationale:** En una fábrica, el objetivo no es "engagement" ni "time spent" — es eficiencia operativa. Un operador no quiere badges por usar el sistema; quiere hacer su trabajo rápido y sin errores.

**Implications:** Documento de anti-patterns obligatorio en el design system de FaberLoom. Revisión de cada feature contra esta lista antes de implementar.

**Confidence:** high

---

## Insight 12: El tooling de linting y validación es más importante que el tooling de edición

**Insight:** La investigación de enterprise (Dim03: IBM Carbon stylelint plugin, Atlassian codemods) y de migración (Dim05: 17 codemods para SD v3→v4) muestra que el diferenciador a escala no es cómo se editan los tokens, sino cómo se validan. Un error de token puede propagarse a toda la UI de un tenant.

**Derived From:** Dim01 (governance), Dim03 (enterprise adoption), Dim05 (migration), Dim12 (observability)

**Rationale:** En multi-tenant, un token inválido (ej: color de contraste insuficiente) afecta a todos los usuarios de ese fabricante. La validación automática en CI/CD es obligatoria.

**Implications:** Stack de validación: (1) DTCG schema validator en cada save, (2) WCAG contrast checker automático, (3) stylelint con plugin custom para tokens, (4) visual regression testing por tenant, (5) accessibility audit automático en Sanidad.

**Confidence:** high
