# LOC_SVC_ES — Localización: Templates de Servicio al Cliente (Español)
id: LOC_SVC_ES
status: DRAFT
visibility: [INTERNAL]
version: 1.0
domain: Plataforma (IDX_PLATAFORMA)
classification: LOC — Data localizada por idioma (español)
aplica_a: [MWT]

refs:
  - PLB_INTERACCION_CLIENTE (playbook que consume estos templates)
  - ENT_OPS_STATE_MACHINE (estados canónicos — FROZEN)
  - ENT_PLAT_I18N (reglas generales de idioma)

---

## A. Templates por estado del expediente

| Estado | Código | Template |
|--------|--------|----------|
| Registro | REGISTRO | Su pedido {expediente_ref} está en fase de registro. Estamos procesando la orden de compra. |
| Producción | PRODUCCION | Su pedido {expediente_ref} está en producción en fábrica. La fecha estimada de finalización es {fecha_estimada}. |
| Preparación | PREPARACION | La producción de su pedido {expediente_ref} está completa. Estamos coordinando la logística de envío. |
| Despacho | DESPACHO | Su pedido {expediente_ref} está aprobado para despacho. Próximamente recibirá información de embarque. |
| Tránsito | TRANSITO | Su carga {expediente_ref} está en tránsito. Tracking: {tracking}. Transportista: {carrier}. |
| En destino | EN_DESTINO | Su carga {expediente_ref} ha llegado a {destino}. Estamos coordinando la entrega final. |
| Cerrado | CERRADO | El expediente {expediente_ref} está cerrado. La entrega fue confirmada el {fecha_cierre}. |
| Cancelado | CANCELADO | El expediente {expediente_ref} fue cancelado. Para más detalles, contacte a su ejecutivo MWT. |

---

## B. Templates de interacción general

| Situación | Template |
|-----------|----------|
| Saludo | Hola, soy el Asistente MWT. ¿En qué puedo ayudarle? |
| No identificado | Este número no está registrado en nuestro sistema. Por favor contacte a su ejecutivo MWT para configurar su acceso. |
| Sin información | No tengo esa información disponible en este momento. Su ejecutivo MWT ha sido notificado y le contactará en las próximas {sla_horas} horas hábiles. |
| Documento enviado | Aquí tiene el documento solicitado: {nombre_documento}. {link_descarga} (este enlace es válido por 15 minutos). |
| Documento no disponible | El documento {nombre_documento} no está disponible para su expediente en este momento. Su ejecutivo MWT le contactará con más información. |
| Lista de expedientes | Tiene {cantidad} expedientes abiertos: {lista_expedientes}. ¿Sobre cuál desea consultar? |
| Crédito / pago | Su expediente {expediente_ref} lleva {dias_credito} de {dias_limite} días de crédito. |
| Escalamiento | Esa solicitud requiere atención personalizada. Su ejecutivo MWT ha sido notificado y le contactará en las próximas {sla_horas} horas hábiles. |

---

## C. Reglas de estilo ES

- Tratar de "usted" (formal). No tutear.
- Firmar como "Asistente MWT".
- No usar jerga técnica: "expediente" (no "state machine"), "pedido" (no "artifact"), "documento" (no "ART-XX").
- Fechas: formato DD/MM/AAAA.
- Moneda: USD salvo que el contexto requiera otra.

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v1.0 (2026-03-15): creación. 8 templates por estado + 8 templates interacción general + reglas estilo ES.
