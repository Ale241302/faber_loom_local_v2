# ENT_DIST_SAP_SCHEMAS — Esquemas de Export SAP para Demand Forecasting
id: ENT_DIST_SAP_SCHEMAS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Distribucion (IDX_DISTRIBUCION)
aplica_a: [MWT]

---

## A. Propósito

Catálogo de formatos de export Excel/CSV producidos por transacciones SAP relevantes para demand forecasting B2B. Usado por Agent_0A del SKILL_DEMAND_FORECASTER para normalizar datos antes del análisis.

---

## B. Detección automática de transacción

Agent_0A detecta la fuente por presencia de columnas clave:

| Si el export contiene... | Fuente probable |
|--------------------------|----------------|
| "Tipo mov." o "Mvt Type" + "Cantidad" | MB51 |
| "Consumo total" + "Período" | MCBA |
| "Documento compras" + "Fecha entrega" | ME2M |
| "Documento ventas" + "Solicitante" | VA05 |
| "No restringido" + "En control calidad" | MMBE |
| fecha + sku + cantidad sin columnas SAP | CSV genérico |

Si no se detecta la fuente → solicitar al usuario que confirme la transacción.

---

## C. Transacciones — Detalle por fuente

### MB51 — Material Document List (consumo real)

**Cuándo usar:** fuente principal de demanda real histórica.

| Columna SAP | Columna estándar | Transformación |
|-------------|-----------------|----------------|
| Fecha contab. | fecha | YYYYMMDD → YYYY-MM-DD |
| Material | sku_sap | limpiar ceros a la izquierda |
| Texto breve material | descripcion | as-is |
| Cantidad | unidades | quitar signo negativo en salidas |
| UM | uom | mantener para validación |
| Tipo mov. | mov_type | usar para filtro (ver abajo) |
| Centro | planta | as-is |

**Tipos de movimiento válidos para demanda:**

| Tipo | Descripción | Incluir |
|------|-------------|---------|
| 261 | GI para orden de producción | ✅ consumo real |
| 601 | GD Goods Issue (venta) | ✅ consumo real |
| 251 | GI a centro de costo | ✅ consumo real |
| 201 | GI a centro de costo (otro) | ✅ consumo real |
| 101 | Entrada de mercancía (GR) | ❌ no es demanda |
| 311/312 | Traslado entre almacenes | ❌ no es demanda |
| 501 | Entrada sin orden | ❌ no es demanda |
| 161/162 | Devolución | ❌ excluir o manejar por separado |

**Regla de signo:** salidas = negativo en SAP → multiplicar por -1 para obtener unidades positivas de demanda.

---

### MCBA — Plant Analysis: Consumption (consumo agregado)

**Cuándo usar:** cuando el cliente entrega resumen mensual ya calculado.

| Columna SAP | Columna estándar | Transformación |
|-------------|-----------------|----------------|
| Período | fecha | YYYYMM → YYYY-MM-01 (primer día del mes) |
| Material | sku_sap | limpiar ceros |
| Descripción | descripcion | as-is |
| Consumo total | unidades | as-is (ya positivo) |
| Centro | planta | as-is |

**Nota:** MCBA ya está agregado por mes — no requiere reagrupación. Preferido sobre MB51 cuando está disponible porque incluye correcciones del período.

---

### ME2M — Purchase Orders by Material (órdenes de compra)

**Cuándo usar:** cuando no hay consumo disponible y se usa historial de pedidos como proxy de demanda.

| Columna SAP | Columna estándar | Transformación |
|-------------|-----------------|----------------|
| Fecha entrega | fecha | DD.MM.YYYY → YYYY-MM-DD |
| Material | sku_sap | limpiar ceros |
| Descripción material | descripcion | as-is |
| Cantidad pedido | unidades | as-is |
| Centro suminist. | planta | as-is |

**Advertencia:** órdenes de compra ≠ consumo real. Incluye stock de seguridad y lotes mínimos. Agent_A debe alertar si la fuente es ME2M.

---

### VA05 — Sales Orders (órdenes de venta)

**Cuándo usar:** distribuidores con módulo SD activo. Demanda desde perspectiva de ventas.

| Columna SAP | Columna estándar | Transformación |
|-------------|-----------------|----------------|
| Fecha entrega deseada | fecha | DD.MM.YYYY → YYYY-MM-DD |
| Material | sku_sap | limpiar ceros |
| Descripción material | descripcion | as-is |
| Cantidad pedido | unidades | as-is |
| Solicitante | cliente_id | as-is |

---

### MMBE — Stock Overview (inventario actual)

**Cuándo usar:** NO para series históricas. Solo para calcular stock actual disponible en reorder point.

| Columna SAP | Campo destino |
|-------------|--------------|
| No restringido | stock_disponible |
| En control calidad | stock_bloqueado |
| Bloqueado | stock_bloqueado_adicional |
| Material | sku_sap |
| Centro | planta |

---

### CSV Genérico

**Cuándo usar:** cliente exportó datos manualmente o usa sistema no-SAP.

Esquema esperado mínimo:
```
fecha | sku_id | unidades
2024-01-01 | MLV-BOT-001 | 520
```

Columnas aceptables por nombre: fecha/date/periodo/period, sku/material/producto/item, unidades/qty/quantity/cantidad.

Si las columnas no coinciden → Agent_0A solicita mapeo manual antes de continuar.

---

## D. Esquema estándar de salida de Agent_0A

Independiente de la fuente, Agent_0A entrega:

```
fecha        : YYYY-MM-DD (primer día del mes para datos mensuales)
sku_id       : string legible (si hay tabla de mapeo SAP→ID) o sku_sap como fallback
sku_sap      : número de material SAP original
descripcion  : texto del material
unidades     : número positivo (demanda real en unidades base)
uom          : unidad de medida (PAR, UN, KG, etc.)
planta       : código de planta SAP
fuente       : MB51 | MCBA | ME2M | VA05 | CSV_GENERICO
advertencias : lista de flags detectados
```

---

## E. Casos especiales

**Multi-planta:** si el export incluye múltiples plantas → modelar como series separadas por (sku_id, planta). Nunca sumar plantas distintas sin confirmación CEO.

**Multi-UoM:** si el mismo SKU aparece en PAR y UN → convertir todo a UoM base. Solicitar factor de conversión si no está en el export.

**Fechas inválidas o vacías:** excluir fila, registrar en advertencias de Agent_0A.

**Material sin descripción:** usar sku_sap como descripcion. No inventar nombres.

---

Changelog:
- v1.0 (2026-04-14): Creación. Cubre MB51, MCBA, ME2M, VA05, MMBE y CSV genérico. Reglas de movimiento, transformación y esquema estándar de salida.
