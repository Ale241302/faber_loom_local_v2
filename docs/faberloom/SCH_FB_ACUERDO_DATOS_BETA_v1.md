# Acuerdo de Datos Beta — FaberLoom

**ID:** SCH_FB_ACUERDO_DATOS_BETA_v1  
**Versión:** 1.0.0  
**Estado:** PLANTILLA — requiere revisión legal humana y campos económicos antes de firma  
**Responsable de firma:** CEO / representante legal designado

---

## 1. Partes

- **FaberLoom / MWT.one** (en adelante, "el Proveedor"), plataforma de agentes de inteligencia operativa para empresas B2B.
- **Cliente Beta** (en adelante, "el Cliente"), identificado en el anexo de designación.

## 2. Alcance de datos

Durante la beta el Cliente podrá cargar en FaberLoom los siguientes tipos de datos, únicamente para los fines operativos autorizados:

- Datos de contacto comercial (nombres, correos, teléfonos) de sus clientes/proveedores.
- Documentos comerciales históricos (cotizaciones, facturas, órdenes de compra) en formatos PDF/Excel/Word.
- Conocimiento de dominio específico (listas de precios, catálogos, políticas de crédito, FAQs).
- Datos de uso interno generados por el agente dentro del workspace del Cliente (borradores, decisiones, runs).

**Queda explícitamente fuera del alcance:**
- Datos de tarjetas de crédito o información financiera sensible no relacionada con facturación B2B.
- Datos de salud, biometría, o categorías especiales bajo regulaciones adicionales.
- Cualquier dato que el Cliente no tenga derecho a compartir con el Proveedor.

## 3. Visibilidad y sellado

- Cada workspace del Cliente está aislado por `tenant_id` y `workspace_id`.
- El Proveedor utiliza un **key broker** para controlar qué datos pueden ser leídos por cada skill y bajo qué condiciones; los skills del catálogo global nunca acceden al contenido del Cliente salvo que el Cliente los active en su workspace.
- Todo acceso a datos del Cliente queda registrado en `audit.jsonl` y en la cadena de auditoría de Foundation (`fnd_audit_log`) con `correlation_id`, `actor_id` y `actor_role_at_decision`.
- El Cliente puede solicitar un extracto de sus registros de auditoría en cualquier momento.

## 4. No-entrenamiento con datos del Cliente

- **Los datos del Cliente no se utilizarán para entrenar modelos de lenguaje ni para mejorar modelos de terceros.**
- Los proveedores de modelos subyacentes (OpenAI, Anthropic, etc.) reciben prompts transitorios únicamente para producir la respuesta solicitada; no retienen esos datos para entrenamiento.
- Cualquier golden case propuesto por el harvester requiere aprobación y verificación humana (`verified_by != approved_by`) antes de convertirse en material de referencia del Cliente.

## 5. SLA beta

Ver referencia: `PLB_FB_SOPORTE_SLA_BETA_v1.md`.

Resumen no vinculante:
- Disponibilidad objetivo: 95% horario laboral CR (L-V 07:00-19:00 CST).
- Tiempo de respuesta a incidentes P0: 4 horas.
- Tiempo de respuesta a consultas de soporte: 1 día hábil.

## 6. Duración y precio beta

- **Duración:** 90 días calendario desde la fecha de firma.
- **Precio preferente:** `[PENDIENTE — decisión CEO]`.
- **Facturación:** mensual por adelantado; primera factura manual, conciliada vía PACK 3 (cobranza).
- **Uso incluido:** `[PENDIENTE — decisión CEO]` runs/mes, workspaces `[PENDIENTE]`, usuarios `[PENDIENTE]`.

## 7. Terminación y exportación de datos

- Cualquiera de las partes puede terminar la beta con 15 días de aviso previo por escrito.
- A solicitud del Cliente dentro de los 30 días posteriores a la terminación, el Proveedor entregará:
  - Exportación de datos cargados por el Cliente en formatos originales o CSV/JSON.
  - Extracto de registros de auditoría del período beta.
- Transcurrido el plazo de exportación, los datos del Cliente serán eliminados de los entornos activos, salvo obligación legal de conservación.

## 8. Responsabilidades del Cliente

- Designar un "owner" técnico/comercial como punto de contacto.
- No cargar datos de terceros sin la autorización correspondiente.
- Revisar y aprobar/rechazar las acciones que requieran HITL (doble confirmación con token).
- Participar en la revisión semanal de métricas de soak y canarios.

## 9. Responsabilidades del Proveedor

- Mantener el aislamiento del tenant y los canarios de contaminación.
- No promover skills a ACTIVE en el workspace del Cliente sin el umbral de calidad (≥3 golden cases verified, ≥100 runs, ≥90% acceptance).
- Documentar cualquier incidente P0 y reiniciar el soak si se detecta una fuga cross-tenant.

## 10. Aprobaciones

| Rol | Nombre | Fecha | Firma |
|---|---|---|---|
| Representante legal Proveedor | | | |
| Representante legal Cliente | | | |
| Revisión legal Proveedor | | | |
| Revisión legal Cliente | | | |

---

**Nota:** Esta plantilla fue generada por Fugu como punto de partida. No constituye asesoría legal. El CEO/AM debe revisarla con abogado antes de la firma. Los campos `[PENDIENTE]` deben completarse antes de la ejecución.
