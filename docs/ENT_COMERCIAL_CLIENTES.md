# ENT_COMERCIAL_CLIENTES - Registro de Clientes
id: ENT_COMERCIAL_CLIENTES
status: DRAFT
visibility: [CEO-ONLY]
domain: Comercial (IDX_COMERCIAL)
version: 1.1
classification: ENTITY - Data pura inyectable.
refs: ENT_PLAT_LEGAL_ENTITY, ENT_MERCADO_{X}, COM-01 (ENT_GOB_PENDIENTES), SCH_PROFORMA_MWT
aplica_a: [MWT]

---

## A. Proposito

Registro canonico de clientes B2B. Actualmente solo canal Marluvas. Se expande con Rana Walk y Tecmater cuando aplique.

El campo `codigo_marluvas` es un identificador interno del sistema SAP de Marluvas. No es un codigo MWT. Clientes de otros canales tendran sus propios identificadores externos.

---

## B. Registro - Canal Marluvas

| codigo_marluvas | cliente | pais |
|-----------------|---------|------|
| 4000000100 | SONDEL S.A. | Costa Rica |
| 4000000145 | MUITO WORK LIMITADA | Costa Rica |
| 4000000102 | DISTRIBUIDORA COMTEK S.A.S. | Colombia |
| 4000000116 | MELEXA S.A.S. | Colombia |
| 4000000402 | SONEPAR COLOMBIA S.A.S. | Colombia |
| 4000000115 | IMPORCOMP S.A. | Guatemala |
| 4000000400 | COMERCIALIZADORA UMMIE, S.A. | Guatemala |
| 4000000484 | GRUPO SOLUCIONES DE INGENIERIA Y AUTOMATIZACION S.A. | Guatemala |
| 4000000501 | EQUIPOS Y GUANTES INDUSTRIALES S.A. | Guatemala |
| 4000000126 | PRO CUSTOMER CORP. | Panama |
| 4000000128 | IMPORTACIONES Y COMPRAS S. DE R.L. | Honduras |

---

## C. Reglas

1. El nombre del cliente en proformas DEBE ser exactamente como aparece en seccion B. No abreviar, no reformatear.
2. El codigo Marluvas DEBE aparecer visible junto al nombre en toda proforma (ref SCH_PROFORMA_MWT D2).
3. Nuevos clientes se agregan solo cuando Marluvas confirma el codigo SAP asignado.
4. Campo `pais` determina que ENT_MERCADO_{X} aplica.
5. MUITO WORK LIMITADA (4000000145) es autoconsumo - proformas para stock propio o Rana Walk.

---

## D. Campos pendientes (ref COM-01)

Cuando se materialice COM-01 completo, cada cliente necesitara:
- cedula_juridica: string
- contacto: { nombre, telefono, email }
- condiciones_default: { credito_dias, medio_pago, incoterm }
- direccion_entrega: string
- canal: enum [directo, distribuidor]
- estado: enum [activo, inactivo]

Estos campos son [PENDIENTE - NO INVENTAR] hasta que se recopilen. Conforme se vayan recopilando, se agregan al perfil enriquecido en seccion E.

---

## E. Perfiles enriquecidos (lazy populate)

Aqui viven los datos completos por cliente conforme se obtienen de OCs reales o intercambios. No es obligatorio tener todos los campos llenos; se llenan a medida que aparecen en operacion.

### E1. DISTRIBUIDORA COMTEK S.A.S. (Colombia)

| Campo | Valor |
|-------|-------|
| codigo_marluvas | 4000000102 |
| razon_social | DISTRIBUIDORA COMTEK S.A.S. |
| pais | Colombia |
| nit | 900895760-4 |
| direccion | CR 43 A # 1-50, T3 OFC 805, San Fernando Plaza, Medellin |
| telefono_oficina | (4) 356 9330 |
| canal | distribuidor |
| estado | activo |

**Contactos:**

| Nombre | Rol | Email | Telefono |
|--------|-----|-------|----------|
| Jose Angel Avila | Comercial | jose.avila@comtek.la | +1 305 831 5815 |

**Condiciones default observadas (PF 2467-2026):**

| Campo | Valor |
|-------|-------|
| condicion_pago | Credito 90 dias |
| medio_pago | Transferencia bancaria |
| incoterm | FOB Brasil |
| moneda | USD |
| lista_precios | Tabela COMEX 2026 v6 |

**Comisiones MWT observadas por linea (PF 2467-2026):**

| Familia | Comision |
|---------|----------|
| 100AWORKF (PVC con forro) | 5% |
| 70B22-BP-HIDRO (microfibra hidrocarburos) | 10% |

**Modelo comercial habitual:** B (comision pura, P.Marluvas = P.Cliente, delta 0). Ref ENT_COMERCIAL_MODELOS B3.

**Direccion de entrega:** [PENDIENTE - confirmar si difiere de direccion notificacion]

---

## Changelog

- v1.0 (2026-03-DD): Creacion. Tabla canal Marluvas + reglas + campos pendientes COM-01.
- v1.1 (2026-05-06): +Seccion E perfiles enriquecidos (lazy populate). Primera entrada: E1 DISTRIBUIDORA COMTEK S.A.S. con NIT, direccion, contacto, condiciones default observadas en PF 2467-2026.

---

Stamp: DRAFT - Pendiente aprobacion CEO
