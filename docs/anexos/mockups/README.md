# Anexos · Mockups Mesa de Control

Mockups HTML standalone del producto FaberLoom · Mesa de Control de Cotizaciones Tecnicas (UI consola operativa AM).

Estos archivos NO son canonicos · son **referencias visuales** que documentan la evolucion del diseño UI hasta el v5 final aprobado.

## Versiones

| Archivo | Autor | Lineas | Glosses | Notas |
|---|---|---|---|---|
| `mesa_de_control_v3.html` | Claude Design | 1343 | 120 | Primera entrega · estetico pulido pero saturado |
| `mesa_de_control_v4.html` | ChatGPT (rol Apple designer) | 588 | 2 | Reduccion radical · filosofia simplicidad Apple/Things |
| **`mesa_de_control_v5.html`** | **Claude Design** | **919** | **9** | **FINAL · consolida pulido v3 + filosofia v4** |

## Status

`mesa_de_control_v5.html` es la version **APROBADA** que guia Sprint 1 implementacion. v3 y v4 quedan como referencia historica del proceso de diseño.

## Filosofia canonizada (mock v5)

- Brand v2 paleta exacta (cream/coral/ink/vino)
- Tipografia Georgia italic + Inter + JetBrains Mono
- Gloss as signature device (max 2 visibles default · scarce)
- HERO unificado · 1 cola priorizada con 3 etiquetas (RECIBIDO/LISTO/ALARMA)
- Solo ALARMA usa coral · resto grises distinguibles
- Sidebar 3 contadores click-to-filter (Mi pipeline · En curso/Espera firma/Alarma)
- Cintilla 3 metricas (RFQ semana · Ciclo medio · Pendientes firma)
- Cards LISTO con 3 botones fijos (Aprobar y enviar · Editar · ✕ Rechazar) NUNCA kebab
- AgentConsole panel slide-in 80% derecho · 20% snapshot cuenta activa
- Modales Editar/Rechazar con razones tipificadas (dato/tono/fuente/accion/contexto)
- Light/dark toggle funcional
- ⌘K command bar pill compacta keyboard-first
- Estados A/B/C funcionales (Urgente · Firma · Calma) con toggle demo
- Wordmark "Mesa de Control" lockup vertical · "powered by Faberloom" footer pequeño
- Headlines editorial Apple-style: "Una cosa requiere criterio humano." · "Revisar, decidir, cerrar." · "No hay nada urgente."

## Implementacion

Sprint 1 toma `mesa_de_control_v5.html` como **contract visual**. El equipo de implementacion debe materializar:

1. Stack frontend (React/Vue/Svelte segun stack tenant) replicando layout + interacciones del v5
2. Brand tokens CSS variables exactas
3. Estados A/B/C dinamicos (no toggle demo · estado real driven por datos)
4. AgentConsole con backend P16 sub-agentes
5. Modales con razones tipificadas conectados a Knowledge River

## Pendientes post-v5

- UI Curador alineada con v5 (otro pase v6 · cuando aplique)
- UI Auditor alineada (otro pase v7 · cuando aplique)
- Logo definitivo (woven lattice direccion A refinada · pendiente design pass externo)

## Stamp
VIGENTE 2026-05-02 — v5 mock final aprobado · referencia visual canonica para Sprint 1.
