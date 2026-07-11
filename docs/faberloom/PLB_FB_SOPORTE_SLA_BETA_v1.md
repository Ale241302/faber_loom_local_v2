# PLB — Soporte SLA Beta (FaberLoom / SpaceLoom)

**Versión:** 1.0 beta  
**Ámbito:** suscriptores activos de FaberLoom durante la etapa beta cerrada (E3).  
**Estado:** borrador operativo; las cifres comerciales finales quedan marcadas como `[PENDIENTE — NO INVENTAR]`.

---

## 1. Propósito

Este documento define el nivel de servicio mínimo de soporte técnico que FaberLoom ofrece a sus tenants beta. No constituye un acuerdo comercial vinculante hasta que el CEO/CSO fije los valores comerciales marcados como pendientes.

---

## 2. Canales de soporte

| Canal | Uso recomendado | Disponibilidad |
|-------|-----------------|----------------|
| Correo electrónico | Incidencias no urgentes, solicitudes de facturación, cambios de plan | `[PENDIENTE — NO INVENTAR]` |
| Formulario en app | Reporte de bugs con trazabilidad automática de tenant | `[PENDIENTE — NO INVENTAR]` |
| WhatsApp / SMS de guardia | Solo severidad 1 (outage total) | `[PENDIENTE — NO INVENTAR]` |
| Status page pública | Estado de la plataforma y mantenimientos programados | `[PENDIENTE — NO INVENTAR]` |

---

## 3. Severidades y tiempos de respuesta beta

| Severidad | Definición | Tiempo de respuesta inicial objetivo | Tiempo de resolución objetivo |
|-----------|-----------|--------------------------------------|-------------------------------|
| S1 — Crítica | Plataforma inaccesible o pérdida de datos activa | `[PENDIENTE — NO INVENTAR]` | `[PENDIENTE — NO INVENTAR]` |
| S2 — Alta | Función core degradada (login, facturación, aislamiento tenant) | `[PENDIENTE — NO INVENTAR]` | `[PENDIENTE — NO INVENTAR]` |
| S3 — Media | Bug funcional o consulta de configuración | `[PENDIENTE — NO INVENTAR]` | `[PENDIENTE — NO INVENTAR]` |
| S4 — Baja | Mejora, documentación o duda de uso | `[PENDIENTE — NO INVENTAR]` | `[PENDIENTE — NO INVENTAR]` |

> **Nota beta:** Los tiempos objetivo son aspiracionales durante la etapa de validación. Todo incidente S1/S2 se rastrea obligatoriamente en el audit log del tenant y en el canal de escalamiento interno.

---

## 4. Escalamiento

1. **Nivel 1:** Atención vía canal de soporte con contexto de tenant y `correlation_id` del evento.
2. **Nivel 2:** Ingeniería de plataforma se activa automáticamente en S1/S2.
3. **Nivel 3:** Liderazgo técnico y comunicación al cliente en incidentes con exposición de datos o downtime prolongado.

Contactos internos de escalamiento: `[PENDIENTE — NO INVENTAR]`.

---

## 5. Exclusiones

- Soporte sobre código fuente propietario del cliente fuera del alcance del SKILL.md aprobado.
- Configuración de credenciales tributarias reales (ATV/SAT/DIAN) queda bajo responsabilidad del cliente; FaberLoom solo provee adaptadores mock/sandbox en beta.
- Facturación manual beta genera documentos **no fiscales** explícitamente marcados como tal; no reemplazan facturas electrónicas ante autoridades tributarias.

---

## 6. Métricas de salud visibles

El dashboard de salud por tenant (`/api/admin/tenants/{id}/health` y su espejo para owner) muestra agregados operativos:

- runs exitosos/fallidos en 7 y 30 días,
- tasa de error,
- costo acumulado y presupuesto restante según plan,
- facturas abiertas/pagadas/vencidas,
- último login del owner,
- flags activos (drafts pendientes de aprobación, facturas vencidas).

Estos datos son **agregados**; ningún contenido de workspace se expone a través de este endpoint.

---

## 7. Cambios y aprobación

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0 beta | 2026-07-10 | Equipo FaberLoom | Versión inicial operativa con campos comerciales pendientes. |

Valores comerciales pendientes de aprobación: `[PENDIENTE — NO INVENTAR]`.
