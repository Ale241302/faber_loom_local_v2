---
id: ENT_FABERLOOM_AGENT_BUILDER_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
aplica_a: [FaberLoom, MWT]
stamp: DRAFT — 2026-04-14
classification: ENTITY — Especificación funcional Agent Builder FaberLoom. 168 agentes, taxonomía de autoridad, esquema YAML de configuración, top ROI, orden MVP, mapa de dependencias, KB mínima por agente, modelo de planes.
---

# ENT_FABERLOOM_AGENT_BUILDER_v1 — Agent Builder: Especificación Funcional
## Basado en Kimi Swarm Research · 168 agentes catalogados · 2026-04-13

---

## RESUMEN EJECUTIVO

El swarm de Kimi catalogó **168 agentes virtuales** distribuidos en 9 áreas funcionales de PYME. Este documento extrae lo que importa para construir el Agent Builder de FaberLoom: arquitectura del configurador, parámetros requeridos por agente, y el orden de construcción del MVP.

**Validación clave del mercado (del segundo swarm):**
- Ningún competidor une Email + KB de forma nativa (gap confirmado)
- 54% de PYMEs LATAM ya usa IA — mercado receptivo
- Modelo flat mensual preferido sobre usage-based — valida $99/$199/$299
- Riesgo principal: costo de configuración percibido > beneficio percibido en primeras semanas

---

## 1. TAXONOMÍA DE AUTORIDAD (verificada contra 168 agentes)

Todo agente en FaberLoom opera en exactamente uno de cuatro modos:

| Modo | Qué hace | Requiere aprobación | Ejemplos |
|------|----------|---------------------|----------|
| **SEÑALA** | Informa, alerta, resalta | No | KPIMonitor, ChurnPredictor, CompetitorAlert |
| **PROPONE** | Genera draft o recomendación | Sí, antes de ejecutar | CompraBot-Comparador, ProposalBot, ContentBot |
| **EJECUTA CON APROBACIÓN** | Ejecuta tras confirmación explícita del usuario | Sí, en el momento | CompraBot-Ordenador, RefundBot, PaymentBot |
| **EJECUTA SOLO** | Acción automática dentro de reglas preconfiguradas | No (ya autorizado en config) | TrackBot, CollectionBot, DailyBriefBot |

**Regla de diseño:** El Admin configura el modo máximo del agente. El agente nunca puede auto-escalarse a más autonomía de la configurada.

---

## 2. PARÁMETROS REQUERIDOS POR AGENTE (esquema del configurador)

Cada agente en el Agent Builder necesita estos parámetros:

```yaml
agente:
  nombre: "string"
  area: "OPERACIONES | VENTAS | CX | COMPLIANCE | RRHH | FINANZAS | MARKETING | GERENCIA | INDUSTRIA"
  
  kb_scope:
    - PERSONAL      # Solo el usuario asignado
    - ROL           # Todos con el mismo rol
    - ORGANIZACION  # Toda la empresa
    - PUBLICO       # Información pública / VIP externo
  
  canales:
    primario: "EMAIL | WHATSAPP | CHAT_INTERNO | PORTAL_VIP"
    secundario: "EMAIL | WHATSAPP | CHAT_INTERNO | PORTAL_VIP | null"
  
  autoridad: "SEÑALA | PROPONE | EJECUTA_CON_APROBACION | EJECUTA_SOLO"
  
  tono: "EJECUTIVO | TECNICO | COMERCIAL | EMPÁTICO | FORMAL"
  
  escalamiento:
    trigger_keywords: ["string"]       # palabras que activan escalamiento
    escalamiento_a: "ROL o USUARIO"    # quién recibe el escalamiento
    threshold_monto: number | null     # USD, si aplica
    confianza_minima: 0.70             # % mínimo antes de escalar vs inventar
  
  limites:
    monto_maximo: number | null        # para agentes de compras/finanzas
    categorias_autorizadas: ["string"] # para agentes de compras
    draft_first_externo: boolean       # true = nunca envía a externos sin revisión
    
  triggers:
    tipo: "INBOUND | SCHEDULED | EVENT"
    horario: "cron | null"             # para agentes programados
    evento: "string | null"            # ej. "factura_vencida"
```

---

## 3. LOS 5 LÍMITES ABSOLUTOS

Ninguna configuración puede desactivar esto — son hardcoded en el motor de FaberLoom:

1. **Cero envíos externos sin aprobación** — todo draft externo (email, WhatsApp a cliente) pasa por aprobación del usuario asignado antes de salir. Sin excepción.

2. **Cero transacciones financieras autónomas** — pagos, transferencias, aprobaciones de factura siempre requieren firma humana. El agente prepara, el humano ejecuta.

3. **Cero acceso fuera del KB scope configurado** — un agente con scope ROL no puede leer capas de ORGANIZACIÓN aunque la pregunta lo requiera. Responde "no tengo acceso a esa información" y escala.

4. **Cero aprobaciones legales autónomas** — contratos, cláusulas, documentos con implicación legal solo son señalados o propuestos, nunca aprobados por el agente.

5. **Audit trail inmutable** — toda acción del agente queda registrada con timestamp, usuario que aprobó, y contenido. No hay modo de borrar el log.

---

## 4. TOP 5 AGENTES POR ROI (para pitch de ventas)

| Rank | Agente | Área | ROI estimado | Por qué gana primero |
|------|--------|------|-------------|----------------------|
| 1 | **CollectionBot** | Finanzas | 400-600% | Recupera dinero directamente. KPI inmediato y medible. |
| 2 | **InfoBot** | CX | 300-500% | Elimina 70-85% de tickets repetitivos. Libera equipo. |
| 3 | **QualifyBot** | Ventas | 250-400% | Más leads calificados con mismo equipo comercial. |
| 4 | **CompraBot-Solicitudes** | Operaciones | 200-350% | Elimina el cuello de botella del dueño en compras día a día. |
| 5 | **TrackBot** | CX | 150-250% | Alta visibilidad, fácil de medir, cero riesgo de error crítico. |

---

## 5. TOP 3 MVP — ORDEN DE CONSTRUCCIÓN

### MVP-1: **TrackBot** (Semana 1-2)
- **Función:** Responde "¿dónde está mi pedido?" via WhatsApp/Email
- **Por qué primero:** Cero riesgo, alta frecuencia, resultado visible en minutos
- **KB requerida:** Tabla de pedidos con número de tracking y estado
- **Autoridad:** EJECUTA SOLO
- **Canales:** WhatsApp Business + Email
- **Parámetros config:** fuente de datos de tracking, formato de respuesta, horario de operación

### MVP-2: **FAQ-HRBot / InfoBot** (Semana 2-3)
- **Función:** Responde preguntas internas frecuentes (políticas, beneficios, procesos) o externas (producto, precios, horarios)
- **Por qué segundo:** Demuestra el valor de la KB de 4 capas — el mismo motor responde distinto según quién pregunta
- **KB requerida:** FAQ estructurado por capa (PERSONAL, ROL, ORG, PÚBLICO)
- **Autoridad:** EJECUTA SOLO
- **Canales:** Chat Interno (versión HR) / WhatsApp o Email (versión CX)
- **Parámetros config:** scope de KB, threshold de confianza (0.70 default), a quién escalar si no sabe

### MVP-3: **DailyBriefBot** (Semana 3-4)
- **Función:** Email ejecutivo a las 7 AM con: alertas del día, KPIs críticos, tareas vencidas, reuniones importantes
- **Por qué tercero:** Demuestra el valor de tener todos los agentes conectados — es el "dashboard" del CEO sin dashboard
- **KB requerida:** KPIs configurados, fuentes de datos de otros agentes
- **Autoridad:** EJECUTA SOLO
- **Canal:** Email
- **Parámetros config:** hora de envío, KPIs a monitorear, thresholds de alerta, destinatarios

---

## 6. MAPA DE DEPENDENCIAS (agentes que se potencian mutuamente)

```
EmailIntelBot ──────────────────────► DailyBriefBot
     │                                      ▲
     ├──► PipelineGuard (identifica deals)  │
     ├──► CompraBot (detecta solicitudes)   │
     └──► CollectionBot (detecta disputas)  │
                                            │
KPIMonitor ─────────────────────────────────┘
     │
     ├──► AlertBot (umbrales críticos)
     └──► BrandManager (anomalías de marca)

ProductMatch ──► QualifyBot ──► ProposalBot ──► ContractBot-Ventas
                    │
                    └──► FollowUpMaster

CompraBot-Solicitudes ──► CompraBot-Cotizador ──► CompraBot-Comparador ──► CompraBot-Aprobador
                                                                                    │
                                                                                    └──► ProvBot-Pagos
```

**Dependencia crítica para FaberLoom:** El EmailIntelBot (Email Intelligence) es el hub central que alimenta prácticamente todos los demás agentes. Si no funciona bien, nada funciona bien. Confirma que el Email MVP CORE es la decisión correcta.

---

## 7. KB MÍNIMA REQUERIDA POR AGENTE (qué debe estar bien estructurado)

| Agente | KB imprescindible | Capa |
|--------|-------------------|------|
| TrackBot | Tabla pedidos + estados + tracking numbers | ORG |
| InfoBot | FAQ curado por categoría | ORG + PÚBLICO |
| CollectionBot | Lista clientes + facturas + días vencidos + tonos por segmento | ORG |
| CompraBot | Proveedores aprobados + presupuestos por rol + categorías autorizadas | ROL + ORG |
| QualifyBot | Criterios BANT de la empresa + ICP definido | ROL |
| ProductMatch | Catálogo técnico estructurado + certificaciones | ORG + PÚBLICO |
| DailyBriefBot | KPIs definidos + calendario + salidas de todos los agentes | ORG |
| VacationHandoff | Proyectos activos + threads email + contactos clave | PERSONAL + ROL |

**Insight crítico:** La calidad de la KB determina el 80% de la calidad del agente. El Agent Builder debe incluir un wizard de carga de KB antes de activar el agente — si la KB está vacía o mal estructurada, el agente no se activa.

---

## 8. CATÁLOGO COMPLETO: DISTRIBUCIÓN POR ÁREA

| Área | # Agentes | Agentes 100% virtualizables | ROI típico |
|------|-----------|----------------------------|------------|
| Operaciones y Compras | 24 | 8 | Medio-Alto |
| Ventas y Comercial | 24 | 10 | Alto |
| Servicio al Cliente | 14 | 9 | Alto |
| Compliance y Legal | 17 | 3 | Medio (riesgo reducido) |
| RRHH Administrativo | 15 | 6 | Medio |
| Finanzas | 16 | 5 | Muy Alto |
| Marketing y Marca | 16 | 4 | Medio |
| Gerencia / Ejecutivo | 20 | 7 | Alto |
| Industrias LATAM | 22 | 4 | Sectorial |
| **TOTAL** | **168** | **56** | — |

---

## 9. AGENTES LATAM-ESPECÍFICOS (diferenciadores competitivos)

Los competidores globales no tienen estos:

| Agente | Sector | Función | Valor único LATAM |
|--------|--------|---------|-------------------|
| **ExpedienteBot** | Importación | Estado aduanal, docs pendientes, fechas de liberación | Integra con VUCE/DUA/agentes aduanales |
| **TiposDeCambioBot** | Importación | Alerta cuando TC afecta márgenes de importaciones | Configurable por moneda y umbral |
| **ProductMatch-EPI** | Distribución | Spec matching tipo Marluvas — recibe necesidad, devuelve producto + gaps | Catálogo técnico con certificaciones locales |
| **LicitaciónBot** | Servicios prof. | Analiza pliegos, calcula probabilidad de ganar, genera checklist | Reglas por país (Chile, Colombia, CR) |
| **DistribuidorBot** | Distribución | Seguimiento de metas por zona, pedidos por distribuidor | Jerarquía: representante → distribuidor → zona |
| **HonorariosBot** | Servicios prof. | Facturación + seguimiento de honorarios por caso/cliente | Integra con sistemas de facturación electrónica LATAM |

---

## 10. MODELO DE CONFIGURACIÓN POR PLAN FABERLOOM

| Plan | Agentes activos | KB scope disponible | Canales | Precio |
|------|----------------|---------------------|---------|--------|
| Starter | 3 agentes | ORG + PÚBLICO | Email + Chat | $99/mes |
| Professional | 10 agentes | ROL + ORG + PÚBLICO | + WhatsApp Business | $199/mes |
| Enterprise | Ilimitado | Todos (4 capas) | Todos + Portal VIP | $299/mes |

**Nota:** Los 3 límites absolutos aplican en todos los planes sin excepción.

---

## FUENTES

- `kimi_results/FABERLOOM_AGENT_BUILDER_RESEARCH_COMPLETO.md` — catálogo 168 agentes
- `kimi_results/faberloom_mapa_agentes_completo.md` — síntesis y top ROI/MVP
- `kimi_results/matriz_agentes_resumen.md` — matriz compliance
- `kimi_results/agentes_virtuales_industrias_LATAM_PYMEs.md` — casos LATAM
- `kimi_results2/REPORTE_FINAL_KB_AS_A_SERVICE.md` — validación de mercado
- `kimi_results2/investigacion_dolores_administrativos_pyme_latam.md` — dolores verificados

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Promovido desde docs/archivo/faberloom_agent_builder_spec.md a docs/ENT_FABERLOOM_AGENT_BUILDER_v1.md. Frontmatter actualizado: id ENT_FABERLOOM_AGENT_BUILDER_v1, domain Gobernanza (IDX_GOBERNANZA), type ENT, aplica_a [FaberLoom, MWT]. v1.0 se mantiene.
- v1.0 (2026-04-14): Creación inicial. Catálogo 168 agentes, taxonomía de autoridad, esquema YAML, top ROI, MVP.

*FaberLoom Agent Builder Spec v1.0 — Muito Work Limitada · 2026-04-13*
