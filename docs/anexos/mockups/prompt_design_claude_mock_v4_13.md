# Prompt para Claude (Design) — Mejorar mock FaberLoom v4.13

**Objetivo:** Rediseñar el mock HTML de FaberLoom v4.13 para que sea visualmente más pulido, más funcional y 100% alineado con el plan técnico `PLAN_DESARROLLO_FABERLOOM_v4.md`.

---

## Contexto del proyecto

FaberLoom es un "copiloto de backoffice comercial B2B" para MWT (calzado de seguridad, Costa Rica/Guatemala). El MVP debe cubrir:

- RFQ / cotizaciones
- Seguimiento a clientes
- Cobranza (solo interna/post-dictamen; bloqueada para terceros en E2.5)

El sistema usa IA generativa (OpenAI, Anthropic, Google) pero con **human-in-the-loop (HITL) obligatorio**: nunca envía correos automáticamente. Todo draft requiere aprobación humana.

---

## Archivo base

Partir de: `docs/anexos/mockups/faberloom_shell_mock_v4_13.html`

Ese mock ya incluye:
- Tres modos: Operar / Aprender / Admin
- Rail izquierdo (navegación/contexto), canvas central, rail derecho (toolset)
- SpaceLoom (chat universal), Inbox, WorkLoom (Kanban 4 columnas), Routing
- Toolset: Agentes, Skills, KB, Gold, Routing
- HITL básico con botones Aprobar/Editar/Rechazar

---

## Áreas a mejorar

### 1. Diseño visual
- **Jerarquía clara**: que el usuario sepa inmediatamente dónde está, qué modo usa y qué acción espera el sistema.
- **Color funcional**: usar colores con significado (coral = acción/IA, sage = éxito/aprobado, amber = advertencia/espera, vino = error).
- **Tipografía**: mejorar legibilidad en estado default (13.5px es correcto), pero usar tamaños y pesos para jerarquía.
- **Espaciado**: reducir densidad en el rail derecho; aumentar aire en el canvas central.
- **Dark mode refinado**: evitar grises planos, usar sutilezas de elevación.

### 2. Funcionalidad / UX
- **HITL explícito y seguro**:
  - Separar "Aprobar" de "Enviar". Nunca un solo botón "Aprobar y enviar".
  - Mostrar contador de doble confirmación o diálogo modal antes de enviar.
  - Indicar claramente si un draft tiene datos asumidos o no verificados 100%.
- **Grounding y evidence bundle**:
  - Mostrar fuentes del KB de forma escaneable (no solo links).
  - Indicar qué datos son 100% trazados vs. asumidos/prosa.
- **Responsive móvil**:
  - Adaptar a < 768px: rail izquierdo colapsable, composer en bottom sheet, HITL en pantalla completa.
  - Gate E1a requiere login, navegación e inbox cargables desde móvil.
- **WorkLoom**:
  - Hacer más evidente el score/confianza de cada card.
  - Diferenciar urgencia por color de borde y tag.
  - Agregar acción rápida "Abrir en SpaceLoom" sin entrar al card.
- **Inbox**:
  - Vista de lista compacta con badges de clase (RFQ, seguimiento, cobranza, soporte, spam).
  - Acciones rápidas: asignar workspace, marcar spam, crear draft.
- **SpaceLoom**:
  - Distinguir visualmente mensajes del usuario, mensajes de IA y drafts en revisión.
  - Mostrar contexto activo (workspace/cliente) de forma prominente.
  - Indicador de costo/confianza/modelo usado por mensaje/draft.

### 3. Alineación con plan v4 (reglas duras)
- **NO mostrar DeepSeek** como proveedor disponible para PII. Si aparece, debe estar deshabilitado o con advertencia "solo metadata anonimizada".
- **Cobranza a terceros**: si se muestra, debe tener badge "Bloqueado hasta dictamen legal" o limitarse a cobranza interna/recordatorios suaves.
- **Transferencia de datos**: mostrar indicador visual cuando un draft va a usar proveedor US con PII pendiente de `transfer_basis`.
- **No auto-send**: todo envío debe requerir aprobación humana visible.
- **Cost cap**: mostrar cuando un draft/routing se acerca al límite ($0.50 por defecto).

### 4. Navegación y estados
- Modo focus (ocultar paneles) mejor integrado.
- Palette cmd+K con iconos y acciones agrupadas.
- Estados de carga/typing más suaves.
- Empty states para inbox vacío, WorkLoom vacío, KB vacío.

---

## Entregables esperados

Generar un archivo `faberloom_shell_mock_v4_14.html` con:

1. HTML/CSS/JS autocontenido (single file).
2. Todos los cambios de diseño aplicados.
3. Al menos 3 breakpoints responsive (desktop, tablet, móvil).
4. Comentarios en el HTML indicando qué sección corresponde a cada milestone (E1a, E1b, E2, E3, E4).
5. Notas de decisiones de diseño al final del archivo o en un `INDEX_v4_14.md` asociado.

---

## Preguntas para resolver en el diseño

1. ¿Cómo hacemos que el HITL sea imposible de saltar accidentalmente en móvil?
2. ¿Cuál es la forma más rápida de aprobar un draft desde el celular en ≤45s (gate E1b)?
3. ¿Cómo mostramos grounding de precios (100% trazado) vs. prosa (≥85% con cita) sin saturar?
4. ¿Qué elemento visual indica que México o DeepSeek están bloqueados por compliance?
5. ¿Cómo adaptamos el WorkLoom Kanban a pantallas verticales?

---

## Restricciones

- No usar frameworks externos (React, Vue, etc.). Single file HTML+CSS+JS vanilla.
- No usar imágenes externas; usar SVG inline o emojis si es necesario.
- Mantener tokens CSS con nombres semánticos.
- Priorizar funcionalidad sobre estética: primero que fluya, luego que brille.

---

## Métricas de éxito

Al revisar el nuevo mock, deberíamos poder verificar:
- [ ] El CEO sabe en <2s qué cliente/contexto está activo.
- [ ] Un draft se puede aprobar en desktop en <2 min login→draft aprobado.
- [ ] La aprobación móvil es clara y requiere doble confirmación.
- [ ] Los precios/condiciones se muestran como 100% trazados a fuente.
- [ ] DeepSeek y México están bloqueados o advertidos visualmente.
- [ ] El inbox es usable desde un viewport de 375px.
