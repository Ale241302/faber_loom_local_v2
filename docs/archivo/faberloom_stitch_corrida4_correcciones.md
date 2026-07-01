# FABERLOOM — CORRIDA 4: CORRECCIONES CRÍTICAS
**Para pegar directo en Stitch · Toma los frames de las corridas anteriores como base**

---

Toma los frames existentes de FaberLoom y aplica estas correcciones. No rediseñes desde cero — corrige los problemas específicos que se listan aquí.

**Lo que debes corregir: 4 problemas. Nada más.**

---

## Corrección 1 — Unificar el shell en todos los frames

El shell de Corrida 1 (`faberloom_app_shell`) es el único correcto. Aplicarlo sin cambios a todos los demás frames.

**Shell correcto:**

```
[ TOPBAR ]
[ SIDEBAR IZQUIERDO | ÁREA CENTRAL | PANEL DERECHO ]
[ STATUSBAR ]
```

**Topbar:** Fondo `#1E293B`. Borde inferior `#334155`.
- Izquierda: punto pequeño `#4338CA` + texto "FABERLOOM" SemiBold 14px
- Centro: tabs de la vista actual
- Derecha: ícono notificaciones · ícono configuración · avatar circular

**Sidebar izquierdo:** Fondo `#1E293B`. Borde derecho `#334155`. Labels visibles.
```
─ NAVEGACIÓN ─────────────────────
▶ Consola
  Outputs aprobados
  Señales
  Conocimiento
  ──────────────────────────
  Organización
  Configuración

─ SESIÓN ACTUAL ───────────────────
● Respuesta Ramírez #4421
  Reactivación B2B Arkano

─ AYER ────────────────────────────
  Propuesta Constructoras

──────────────────────────────────
[avatar]  Javier M.
          javier@faberloom.io
```

**Statusbar:** Fondo `#263348`. Borde superior `#334155`. JetBrains Mono 10.5px. Color `#475569`.
```
● Listener activo  |  KB: Pedidos activos  |  Voz: Perfil personal  |  Draft · no enviado · FaberLoom nunca actúa sin permiso
```

**Lo que debe desaparecer de todos los frames:**
- El texto "FaberLoom Hero Flow" en el topbar — no existe como nombre de vista
- El botón "DEPLOY STATE" — eliminarlo completamente
- El topbar con tabs "Signals / Drafts / Approved" — reemplazar por el topbar correcto
- El sidebar con "Dashboard / Archive / Operations" — reemplazar por el sidebar correcto
- Cualquier dato técnico en el panel derecho: `LATENCY`, `TOKENS_REMAINING`, `SECURITY_LEVEL`, `LVL_04` — eliminar

---

## Corrección 2 — Eliminar botones de acción autónoma

FaberLoom nunca actúa sin permiso del usuario. Estos dos elementos violan el principio central del producto y deben eliminarse:

**Eliminar completamente:**
- El botón "EXECUTE AUTO-RESPONSE" (aparece en Momento A, esquina inferior derecha del panel)
- El botón "DEPLOY STATE" (aparece en el topbar de los frames del Hero Flow)

**Nada reemplaza estos botones.** No hay sustituto. El área queda sin ese elemento. El único punto de acción del usuario es el input bar en la consola o los botones dentro de los cards de draft.

---

## Corrección 3 — Reconstruir Momento C (post-aprobación)

El frame actual de Momento C está completamente equivocado — muestra un dashboard con grafos de red. Reemplazarlo por esto:

**Momento C es el mismo frame que Momento B, con 4 cambios únicamente:**

1. **Borde izquierdo del card:** cambia de `#6366F1` a `#16A34A`
2. **Badge del card:** cambia de `● Draft · no enviado` a `✓ Aprobado` en `#16A34A`
3. **Los 3 botones de acción desaparecen:** quitar "Rechazar", "Editar" y "Aprobar"
4. **Al pie del card aparece una línea:** `Patrón registrado silenciosamente.` en JetBrains Mono `#475569`

**Lo que NO cambia:**
- El área de mensajes de la consola — igual que Momento B
- El panel derecho — igual que Momento B, sin cambios
- La consola, el sidebar, el statusbar — sin cambios

**Lo que NO sucede en Momento C:**
- Sin página nueva o vista diferente
- Sin dashboard de "Approved Signals"
- Sin grafos, métricas, visualizaciones de red
- Sin modal de confirmación
- Sin notificación de éxito
- Sin confetti, toast, ni animación de celebración
- Sin "Pattern Validator", "NODE_SYNC", "14ms"

El sistema aprendió. No lo anuncia. El card cambió de color. Eso es todo.

---

## Corrección 4 — Panel derecho en Momento A

El panel derecho de Momento A muestra tags técnicos de NLP: `[ORG: DIST_RAMIREZ]`, `[PROD: NODE_V500]`, `[INTENT: QUOTE_REQUEST]`. Reemplazar por el panel de Contexto correcto:

```
── Contexto activo ─────────────────
● KB: Pedidos activos
● Voz: Perfil personal activo

── Señales ─────────────────────────
● Distribuidora Ramírez · pedido #4421
  hace 3h · sin respuesta · ALTA URGENCIA
  [ Atender → ]

○ Inversiones Delta · consulta renovación
  hace 5h · MEDIA URGENCIA

── Patrones aprobados: 8 ───────────
── Señales activas: 2 ──────────────
```

Borde izquierdo de la señal de Ramírez en `#D97706`. Badge "ALTA URGENCIA" en texto `#D97706`. El tab activo del panel derecho es "Contexto", no "Skill activo".

**Eliminar también:** la firma "FaberLoom Operational System" del cuerpo del draft en Momento B. El draft lo firma el usuario, nunca el sistema.

---

## Lo que NO tocar

Estos frames están bien — no modificar:

- **Vista A (Señales):** estructura correcta, mantener tal cual
- **Vista B (Conocimiento):** estructura correcta, mantener tal cual
- **Vista C (Outputs Aprobados):** estructura correcta, mantener tal cual
- **El card de draft de Momento B:** los botones Rechazar / Editar / Aprobar están bien posicionados

---

## Regla de identidad visual para todos los frames

| Token | Hex | Uso |
|-------|-----|-----|
| Fondo principal | `#0F172A` | Toda la app |
| Superficie | `#1E293B` | Sidebar, panel, topbar |
| Elevado | `#263348` | Statusbar, hover, mensaje usuario |
| Borde | `#334155` | Divisores |
| Texto principal | `#F1F5F9` | Todo el texto principal |
| Texto secundario | `#94A3B8` | Labels, metadata |
| Texto muted | `#475569` | Placeholders, statusbar |
| Primary | `#4338CA` | Acciones primarias, nav activo |
| Draft | `#6366F1` | Estado de propuesta |
| Aprobado | `#16A34A` | Post-aprobación |
| Señal | `#0284C7` | Email signals, media urgencia |
| Warning | `#D97706` | Alta urgencia |

Tipografía: **Inter** para UI general. **JetBrains Mono** para metadata, trust layers, statusbar.

---

**Resultado esperado de esta corrida:**
Los mismos frames de las corridas anteriores con shell unificado, sin botones de acción autónoma, con Momento C mostrando el estado post-aprobación silencioso (card con borde verde, sin dashboard), y con el panel derecho de Momento A mostrando contexto operativo legible en lugar de tags técnicos.
