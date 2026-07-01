# FABERLOOM — CORRIDA 2: HERO FLOW
**Para pegar directo en Stitch · Requiere haber ejecutado Corrida 1 primero**

---

Toma el shell de FaberLoom de la corrida anterior y diseña el hero flow completo dentro de la consola principal.

**Lo que debes diseñar: 3 momentos del mismo flujo. No pantallas distintas — el mismo espacio evolucionando.**

---

## Contexto del producto

FaberLoom es Operational Memory para PYMEs. Su doctrina es draft-first: siempre propone, nunca actúa solo. El humano siempre aprueba.

El hero flow muestra esto: el sistema detecta una señal operativa de email, genera un draft de respuesta, y el usuario lo aprueba con un click.

---

## Momento A — Consola con señal activa

La consola está abierta. El área de mensajes está vacía o tiene conversaciones previas.

**Input bar:**
```
[ Skill: Respuesta comercial × ]   Escribe tu consulta...  ▶
```

**Panel derecho — tab "Contexto" activo:**
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

La señal de Ramírez tiene urgencia visual: borde izquierdo en `#D97706`, badge "ALTA URGENCIA" en texto `#D97706`.

El estado del sistema es legible pero no protagonista. La señal es el foco.

---

## Momento B — Draft propuesto (Estado 2)

Después de que el usuario interactúa con la señal, aparece en el área de mensajes de la consola:

**Mensaje del usuario** (arriba del draft):
Texto alineado a la derecha. Fondo rectangular `#263348`. Sin burbuja con cola. Sin borde redondeado exagerado. Texto: "Responde esto"

**Card de draft — especificaciones obligatorias:**

```
┌─ ● Draft · no enviado ─────────────────────────── [Editar] ─┐
│  ← borde izquierdo 2px en #6366F1                            │
│  fondo: #1E293B                                               │
│                                                               │
│  Estimado equipo de Distribuidora Ramírez,                   │
│                                                               │
│  Confirmamos que el pedido #4421 ha sido procesado           │
│  exitosamente y se encuentra en etapa de validación          │
│  logística. El envío está programado para salir de           │
│  nuestro almacén central mañana a primera hora.              │
│                                                               │
│  Quedamos a su disposición para cualquier consulta.          │
│                                                               │
│  Atentamente,                                                 │
│  Gestión Operativa                                            │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│  Basado en: 2 outputs similares aprobados ·                  │
│  Voz: perfil personal activo · KB: pedidos activos           │
│  [JetBrains Mono, 10px, color #475569]                       │
├───────────────────────────────────────────────────────────────┤
│  [ Rechazar ]      [ Editar ]               [ Aprobar ]      │
└───────────────────────────────────────────────────────────────┘
```

**Elementos obligatorios del card:**
- Borde izquierdo 2px `#6366F1` — siempre visible
- Badge "● Draft · no enviado" en `#6366F1`, fuente JetBrains Mono
- Trust layer siempre visible entre el cuerpo y los botones
- Botón "Aprobar" en `#4338CA`, alineado a la derecha
- Botones "Rechazar" y "Editar" secundarios, sin color de acento

**Panel derecho — cambia automáticamente a tab "Skill activo":**
```
RESPUESTA COMERCIAL               v1.4
Configurado por: Álvaro · 10 abr

── Instrucción activa ──────────
Al redactar respuestas a clientes
comerciales, mantener tono profesional
pero cercano. Confirmar datos del pedido
antes de comprometerse a fechas...

── Patrones aprendidos ─────────
✓ Saludo sin "Estimado" — 8 veces
✓ Cierre con nombre del ejecutivo — 12×
⚠ Longitud >3 párrafos — rechazado 3×
```

---

## Momento C — Estado post-aprobación

Después de que el usuario hace click en "Aprobar":

**El card evoluciona — no desaparece, no anima exageradamente:**
- Borde izquierdo cambia de `#6366F1` a `#16A34A`
- Badge cambia a "✓ Aprobado" en `#16A34A`
- Los 3 botones de acción desaparecen
- Al pie del card aparece una línea discreta:
  `Patrón registrado silenciosamente.` en JetBrains Mono `#475569`

**Lo que NO sucede:**
- Sin modal de confirmación
- Sin animación de celebración
- Sin notificación de "Approval Memory actualizado"
- Sin toast, sin popup, sin confetti

El sistema aprendió en silencio. El usuario lo sabe porque es la promesa del producto, no porque el sistema lo anuncie.

**Panel derecho — sin cambio notable.** El skill sigue visible. El contexto sigue disponible.

---

## Reglas visuales para los 3 momentos

**Los mensajes del usuario** son siempre texto alineado a la derecha con fondo `#263348`. No burbujas con cola. No estilo mensajería personal.

**El trust layer** siempre en JetBrains Mono, siempre debajo del cuerpo del draft, siempre antes de los botones. Es la capa de transparencia del sistema.

**El badge "Draft · no enviado"** es permanente hasta que el humano actúa. Es el recordatorio visual de la doctrina del producto.

**El color `#6366F1` (draft)** es el protagonista de este flujo. Aparece en el borde del card, en el badge, en el tag del skill del input. Es el color del trabajo en proceso.

---

## Anti-patrones de este flow

- Sin "FaberLoom está procesando..." como pantalla intermedia prominente
- Sin spinner o loader como experiencia central
- Sin modal de confirmación al aprobar
- El trust layer nunca puede estar ausente en un Estado 2
- El badge "Draft · no enviado" nunca puede estar ausente en un Estado 2
- La aprobación no ejecuta nada externo — solo cambia el estado visual

---

**Resultado esperado de esta corrida:**
3 frames del mismo flujo en la consola mostrando cómo una señal operativa se convierte en un draft y el draft pasa a aprobado. Debe quedar visualmente claro que el sistema propone y el humano decide.
