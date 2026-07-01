# SCH_PROFORMA_MWT — Schema Proforma MWT (ART-02)
id: SCH_PROFORMA_MWT
version: 2.2
status: ACTIVO
stamp: ACTIVO — 2026-05-06
visibility: [INTERNAL]
domain: Comercial (IDX_COMERCIAL)
refs: POL_ARTIFACT_CONTRACT, ARTIFACT_REGISTRY, ENT_PLAT_ARTEFACTOS.B, ENT_PLAT_EVENTOS.B, ENT_COMERCIAL_CLIENTES.E
aplica_a: [MWT]

---

## A. Identidad

| Campo | Valor |
|-------|-------|
| artifact_type_id | ART-02 |
| name | Proforma MWT |
| version | 1.0.0 |
| category | document |
| applies_to | [expediente] |
| description | Documento comercial dual-view con precios, líneas producto, tallas y condiciones. |

---

## B. Regla de dualidad

Toda proforma tiene exactamente 2 vistas del mismo dataset:

| Vista | Audience | Contenido |
|-------|----------|-----------|
| CEO | internal | Superset — precios Marluvas, comisión %, delta, arbitraje, cadena determinista |
| Marluvas | client | Solo precios cliente, líneas, tallas, condiciones, observaciones |

CEO es superset. No existen campos en Marluvas que no estén en CEO. La vista se controla por tab en webapp. Al imprimir, solo se imprime vista Marluvas.

---

## C. Estructura — Vista CEO

### C1. Header
brand, consecutivo, referencia, expediente_id, po_cliente, modelo (B/C), cliente, contacto, país, fecha.
Badges: BORRADOR (draft), CEO-ONLY · INTERNAL.

### C2. Condiciones de compra · Marluvas (card izquierda)
lista_precios, comision_pactada, condicion_pago, medio_pago, pares_calzado, pares_plantillas, total_unidades, total_compra.

### C3. Condiciones de venta · Cliente (card derecha)
po_cliente, fecha_po, credito, total_po, delta (total_po − total_compra).

### C4. Tabla de líneas — Precios paralelos + Comisión

| Col | Vista |
|-----|-------|
| #, código, producto, ncm, color, qty | ambas |
| precio_marluvas, subtotal_marluvas, comision_pct, delta_ud | CEO only |
| precio_cliente, subtotal_cliente | ambas |

Fila total con sumas. Fila nota opcional (`.ch`) bajo líneas promo. Líneas promo: clase `.promo-r`.

### C5. Tallas BRA (pills)
Por línea: label (código · referencia · N pares), pills[] con { talla_bra, qty }. Font monospace.

### C6. Comisiones — Proyección de ingreso (CEO only)
base_comision, tasa_comision, comision_bruta. Cadena determinista: aviso embarque → + crédito factura → cobro Marluvas → comisión MWT (10-15 mes siguiente).

### C7. Arbitraje CEO-ONLY
Por línea: producto, formula (qty × delta_ud), resultado. Total sobreprecio en barra navy.

### C8. Observaciones
Texto libre.

### C9. Actions (webapp only, no print)
Enviar a Marluvas, Duplicar, Editar, PDF Marluvas, Descartar.

---

## D. Estructura — Vista Marluvas

### D1. Header
brand + consecutivo. Emisor: Muito Work Limitada 3-102-751710 · Representante Regional Marluvas.

### D2. Cards tri-column
Card 1 (Cliente): cliente, contacto, país, teléfono, email.
Card 2 (Condiciones): forma de pago, plazo, moneda, valor neto en letras.
Card 3 (Datos proforma): consecutivo, PO, fecha, incoterm, pares, total.

### D3. Tabla de líneas (simplificada)
#, Código, Referencia + descripción, NCM, Color, Cantidad, Precio $, Total. Sin columnas internas.

### D4. Observaciones
Texto simplificado.

### D5. Tallas BRA (pills)
Mismo formato que C5.

### D6. Actions print
Imprimir Carta Vertical, Imprimir Carta Horizontal.

---

## E. Input schema

```
{
  expediente_id: ref → Expediente,
  po_cliente: string,
  cliente: ref → ENT_PLAT_LEGAL_ENTITY.C,
  modelo: enum [B, C],
  lineas: [{
    codigo: string,
    referencia: string,
    descripcion: string,
    ncm: string,
    color: string,
    qty: int,
    precio_marluvas: decimal,
    precio_cliente: decimal,
    comision_pct: decimal,
    tipo: enum [calzado, plantilla, accesorio],
    promo: boolean,
    promo_tag: string | null
  }],
  tallas: [{
    codigo: string,
    pills: [{ talla_bra: string, qty: int }]
  }],
  condiciones: {
    lista_precios: string,
    comision_pactada: decimal,
    condicion_pago: string,
    medio_pago: string,
    credito_dias: int,
    incoterm: string
  },
  observaciones: string
}
```

## F. Output schema

```
{
  consecutivo: string,
  referencia: string,
  brand: string,
  mode: enum [B, C],
  lineas: [{ codigo, referencia, qty, precio_cliente, subtotal_cliente }],
  montos: { total_compra, total_cliente, delta, comision_bruta },
  total_unidades: int,
  fecha: date
}
```

Evento: `proforma.created` con payload = output completo.
Evento condicional: `proforma.split` si divide AA/AB.

---

## G. Validation rules

| Regla | Condición | Acción |
|-------|-----------|--------|
| V1 | sum(lineas[].qty) ≠ total_unidades | Error: totales no cuadran |
| V2 | sum(tallas[].pills[].qty) ≠ linea.qty | Error: tallas no cuadran |
| V3 | precio_cliente < precio_marluvas en modo B | Warning: venta bajo costo |
| V4 | comision_pactada null y modelo = B | Bloqueo: comisión requerida |
| V5 | consecutivo = null o XXXX | Estado máximo = draft |

---

## H. State model

```
draft → submitted → approved → completed → void
```

requires_approval: true — CEO aprueba antes de enviar.

---

## I. Permisos

| Rol | create | view | edit | approve | complete |
|-----|--------|------|------|---------|----------|
| CEO | ✅ | ✅ full | ✅ | ✅ | ✅ |
| Sistema/IA | ✅ draft | ✅ full | ✅ draft | ❌ | ❌ |
| Cliente B2B | ❌ | ✅ vista Marluvas | ❌ | ❌ | ❌ |

---

## J. UI hints

### J1. Webapp
layout: dual-view tabs (CEO | Marluvas). Topbar fixed navy. CSS custom properties. Plus Jakarta Sans + JetBrains Mono. Responsive: tri → single at 900px.

### J2. Print
Solo vista Marluvas. Letter portrait/landscape. Margins 6mm 8mm. Oculta: topbar, badges, actions, arbitraje, CEO-ONLY. print-color-adjust exact. break-inside avoid en cards, tables, pills.

---

## K. Requires

requires:
  - ENT_PLAT_LEGAL_ENTITY.C (issuer + receiver)
  - ENT_COMERCIAL_PRICING (transfer price policy)
  - ENT_COMERCIAL_MODELOS (modelos comerciales)
  - ART-01 OC Cliente (trigger externo)
  - ART-03 Decisión B/C (modo pricing)
policies:
  - POL_VISIBILIDAD
  - POL_DETERMINISMO
  - POL_INMUTABILIDAD
  - POL_NUNCA_TRADUCIR
  - POL_DETERMINISMO
inherits: —

---

## M. Lifecycle

| Campo | Valor |
|-------|-------|
| definition_status | draft |
| created_by | IA + CEO |
| approved_by | [PENDIENTE — CEO] |
| superseded_by | — |

---

Stamp: ACTIVO — Aprobado. Golden Examples vivos en docs/archivo/.

---

## Golden Examples

| Golden | Cliente | Modelo | Caso | Archivo |
|--------|---------|--------|------|---------|
| PF_0000-2026 | (placeholder) | — | Esqueleto inicial | docs/archivo/PF_0000-2026_GOLDEN_EXAMPLE.html |
| PF_2463-2026 v3 | SONEPAR COLOMBIA | B | Comisión homogénea 10%, despacho inmediato (split logístico) | (en operación CEO) |
| PF_2467-2026 | DISTRIBUIDORA COMTEK | B | Comisión mixta 5%/10% por línea, despacho programado | docs/archivo/PF_2467-2026_COMTEK_GOLDEN.html |
| PF_2453-2026 | SONDEL S.A. | B-Tri | Triangular compra/reventa, 3 lineas multi-NCM (6403.99.90); vistas DDP MWT (costo real x par) + DDP SONDEL (contrafactual + liquidacion a facturar c/IVA) | docs/archivo/PF_2453-2026_SONDEL_TRIANGULAR_GOLDEN.html |

**Nota:** PF_2467-2026 documenta el patrón de comisión mixta (porcentajes distintos por SKU dentro de la misma proforma). Mantener como referencia para casos donde Marluvas pacta diferente comisión por familia.

**Nota PF_2453 (ventas triangulares):** golden del modo triangular compra/reventa: MWT compra a Marluvas (precio UF) y revende a SONDEL (precio SN), capturando el delta de precio MAS el ahorro fiscal de nacionalizar al precio bajo (arbitraje total $3,141.22 = $2,731.50 delta + $409.72 fiscal). Introduce dos caminos paralelos: vista DDP MWT (camino contable real, costo nacionalizado por par por linea, margen real) y vista DDP SONDEL (contrafactual reportado al cliente con liquidacion DUA y tabla a facturar con IVA). Documenta la secuencia FOB/par -> CIF/par -> nacionalizado/par.

**[PENDIENTE - taxonomia]** El artefacto rotula este modo "B Triangular", pero ENT_COMERCIAL_MODELOS define "B"=comision y el patron compra/reventa como "C". Reconciliacion de ENT_COMERCIAL_MODELOS pendiente de decision CEO. Hasta entonces se registra como B-Tri para diferenciarlo de los goldens B-comision (PF_2463 Sonepar, PF_2467 Comtek).

**[PENDIENTE - validacion datos]** En el artefacto: contacto comprador figura "Alvaro Solis" (verificar vs Alfaro); color linea 75BPR29 "Cafe" en proforma vs "Marron" en factura/packing; contacto SONDEL "Saymon Arguedas" vs "Javier Bonilla". Servicios aduanales ($300) y transporte ($119.57) referenciales.

---

## Changelog

- v1.0 → v2.0 (2026-03-16): Dual-view CEO/Marluvas, B/C modos, validation rules, state model.
- v2.0 → v2.1 (2026-05-06): +Golden Examples table con PF 2463 (Sonepar, comisión homogénea) y PF 2467 (Comtek, comisión mixta). Refs ENT_COMERCIAL_CLIENTES.E (perfil enriquecido).
- v2.1 -> v2.2 (2026-06-02): +Golden PF_2453 (SONDEL, ventas triangulares compra/reventa) con vistas DDP MWT/SONDEL, liquidacion por par y secuencia FOB/CIF/nacionalizado. Flags: reconciliacion modelo B/C pendiente; validacion de datos pendiente.
