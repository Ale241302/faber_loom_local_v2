# POL_RECURSOS
aplica_a: [SHARED]

id: POL_RECURSOS
version: 1.2
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: 2026-03-21 — VIGENTE

---

## A. Propósito

Política de monitoreo y gestión de recursos del context window durante sesiones de trabajo con el Arquitecto Ejecutor (Claude). Garantiza calidad de output y previene degradación por saturación de contexto.

---

## B. Parámetros de cálculo

| Parámetro | Valor |
|-----------|-------|
| Modelo | Claude Sonnet 4.6 |
| Context window | 200,000 tokens |
| Costo input | $3.00 / M tokens |
| Costo output | $15.00 / M tokens |
| Caching | Activo desde turno 2 (~90% descuento system prompt) |

---

## C. Niveles de contexto

| Nivel | Rango | Acción |
|-------|-------|--------|
| Óptimo | 0 – 40% | Operación normal. Coherencia total. |
| Precaución | 40 – 50% | Sugerir priorizar tareas restantes. |
| **Checkpoint** | **50%** | **Aviso obligatorio al CEO + generar CHECKPOINT_SESSION_[fecha].md. CEO decide si continuar o cortar a chat nuevo.** |
| Riesgo | 50 – 65% | Solo si CEO decide continuar post-checkpoint. Calidad degradándose. |
| **Corte obligatorio** | **65%** | **Generar checkpoint automático sin preguntar. Recomendar chat nuevo.** |
| Crítico | 65%+ | No operar. Restaurar desde checkpoint en chat nuevo. |

---

## D. Protocolo de checkpoint

### D1. Trigger a 50% — aviso + checkpoint

1. Arquitecto Ejecutor detecta ~100K tokens consumidos
2. Avisa al CEO: "Contexto al 50%. Generando checkpoint."
3. Genera `CHECKPOINT_SESSION_[fecha].md` como archivo descargable
4. CEO decide: continuar en mismo chat o abrir chat nuevo

### D2. Trigger a 65% — corte obligatorio

1. Arquitecto Ejecutor detecta ~130K tokens consumidos
2. Genera checkpoint automático sin esperar confirmación
3. Recomienda abrir chat nuevo y subir el checkpoint

### D3. Contenido del checkpoint

Cada `CHECKPOINT_SESSION_[fecha].md` incluye:

- **Sesión:** fecha, versión KB al inicio, versión KB al cierre
- **Decisiones tomadas:** lista numerada con contexto
- **Archivos creados/modificados:** con estado (entregado / pendiente)
- **Pendientes abiertos:** nuevos + arrastrados
- **Punto de restauración:** instrucción exacta para retomar en chat nuevo
- **Tokens consumidos:** input, output, costo acumulado

### D4. Restauración

En el chat nuevo:
1. CEO sube el checkpoint + archivos relevantes
2. Arquitecto Ejecutor lee checkpoint y retoma desde el punto documentado
3. System prompt se cachea automáticamente (no consume ventana adicional)

---

## E. Monitor por turno

Al finalizar cada respuesta, incluir línea de recursos:

```
**Recursos:** 📥 [input] in · 📤 [output] out · 💸 $[costo] · 🧠 [%] · ⚠️ [nivel]
```

CEO puede suspender con "modo silencioso" y reactivar con "modo recursos".

---

## F. Justificación técnica

El mecanismo de atención del context window no es uniforme. Existe degradación documentada ("lost in the middle") donde:
- Inicio del contexto (system prompt): atención alta → protegido
- Final del contexto (turnos recientes): atención alta → protegido
- Medio del contexto (turnos intermedios): atención baja → zona de pérdida

Para una KB donde la precisión es crítica (6 reglas, gate de 9 checks, modelo de visibilidad de 4 tiers), operar por encima del 65% produce errores sutiles: pendientes olvidados, archivos no actualizados en batch, contradicciones con decisiones de turnos tempranos.

---

## Enforcement

- **Detección:** Respuesta del Arquitecto sin tabla de recursos al final
- **Acción:** Agregar tabla de recursos. CEO puede activar/desactivar con "modo silencioso" / "modo recursos"
- **Severidad:** SOFT — metadata operativa, no afecta integridad de datos

---

## Changelog

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-03-15 | Creación inicial — monitor de recursos por turno |
| 1.1 | 2026-03-19 | Protocolo de checkpoint: trigger 50% (aviso), 65% (corte obligatorio). Niveles de contexto expandidos. Sección D completa. Justificación técnica en sección F. |
| 1.2 | 2026-03-21 | +Enforcement section (H-VR4-1 remediación post-auditoría) |
