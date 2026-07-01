---
id: ENT_GOB_SOCIEDAD
version: 1.0
status: DRAFT
visibility: [CEO-ONLY]
domain: GOBERNANZA
tipo: entity
aplica_a: [MWT]
data_classification: N2
no_pgvector: true
stamp: DRAFT — 2026-05-04
refs: ENT_MARCA_MW_IDENTIDAD, ENT_PLAT_LEGAL_ENTITY, ENT_GOB_PROVEEDORES, ENT_COMERCIAL_CLIENTES, SCH_PROFORMA_MWT
---

# ENT_GOB_SOCIEDAD — Identidad Societaria y Estados Financieros MWT

> **Aviso CEO-ONLY (N2):** este documento contiene cédulas de identidad, distribución accionaria, saldos con partes relacionadas e indicadores financieros sensibles. **Nunca indexar en pgvector.** No referenciar contenido textual desde archivos PUBLIC/INTERNAL/PARTNER_B2B; solo permitir referencia por `id` desde otros archivos CEO-ONLY.

## A. Propósito
Documento canónico de la información societaria y financiera de Muito Work Limitada. Fuente única para cualquier proceso que requiera datos legales, contables o financieros de la sociedad: contratos, proformas, trámites bancarios, compliance, auditorías, declaraciones tributarias.

**No confundir con:**
- `ENT_MARCA_MW_IDENTIDAD` → identidad corporativa, paleta, voz
- `ENT_PLAT_LEGAL_ENTITY` → arquitectura técnica de entidades legales en la plataforma

---

## B. Identificación Legal
| Campo | Valor |
|---|---|
| Razón social | MUITO WORK LIMITADA |
| Nombre comercial | MWT |
| Cédula jurídica | 3-102-751710 |
| Tipo societario | Sociedad de Responsabilidad Limitada (Ltda) |
| Estado registral | INSCRITA |
| Fecha de constitución | 2018-01-10 |
| Fecha de inscripción | 2018-01-12 |
| Tomo / Asiento | 2018 / 16463 |
| Plazo social | 99 años |
| Vencimiento | 2117-01-10 |
| Domicilio social | San José, Santa Ana, Pozos, Urb. Bosques de Santa Ana, casa 18-E |

---

## C. Actividad Económica
| Campo | Valor |
|---|---|
| Código Hacienda CR | 4641.1 |
| Actividad declarada | Venta mayorista de calzado de protección industrial y EPP |
| Mercado primario | Costa Rica (sede operativa) |
| Cobertura regional | México → Colombia (representación B2B) |
| Líneas de negocio activas | (1) Representación comercial Marluvas/Tecmater · (2) Marca propia Rana Walk |
| Cliente B2B principal CR | Sondel S.A. |
| Código Marluvas autoconsumo | 4000000145 |

---

## D. Estructura de Capital
| Cuotista | Cuotas | % | Cédula |
|---|---|---|---|
| Álvaro Vinicio Alfaro Montero | 8 | 80% | 1-0854-0809 |
| Lady Gutiérrez Bolaños | 2 | 20% | 1-1165-0532 |

| Campo | Valor |
|---|---|
| Capital social total | ₡10,000 |
| Cuotas nominativas | 10 cuotas de ₡1,000 c/u |
| Estado | Totalmente suscritas y pagadas |
| Aumentos posteriores | Ninguno desde constitución |

---

## E. Administración y Representación
| Cargo | Persona | Cédula | Vigencia |
|---|---|---|---|
| Gerente 01 | Álvaro Vinicio Alfaro Montero | 1-0854-0809 | 2018-01-10 → 2117-01-10 |
| Gerente 02 | Lady Gutiérrez Bolaños | 1-1165-0532 | 2018-01-10 → 2117-01-10 |

**Facultades:** Apoderados Generalísimos sin Límite de Suma.

**Modo de actuación:**
- Separadamente para actos ordinarios.
- Conjuntamente obligatorio para venta o enajenación de bienes sociales.

**Atribuciones adicionales:** Pueden sustituir mandato total/parcial, otorgar poderes a terceros, revocar sustituciones. No les alcanza la prohibición del art. 1263 del Código Civil (autocontratación permitida).

---

## F. Equipo Profesional
| Función | Persona | Identificación |
|---|---|---|
| Contador Público Independiente | Lic. Alexander Solano Gutiérrez | CPI N° 39405 |
| Notario público (constitución) | Lic. Mario Arias Agüero | — |
| Banco operativo principal | Banco Promerica Costa Rica | — |

---

## G. Estados Financieros — Resumen Histórico

### G1. Marco normativo
NIIF para PYMES (Sección 10 — Políticas Contables, Estimaciones y Errores · Sección 17 — PPE · Sección 23 — Ingresos · Sección 33 — Partes Relacionadas). Período fiscal: año natural (1 enero → 31 diciembre).

### G2. Estado de Situación Financiera
| Cuenta | dic-2025 | dic-2024 |
|---|---|---|
| Bancos | 4,250,232 | 10,638,401 |
| Inventarios | 25,341,749 | — |
| **Total Activos Corrientes** | **29,591,981** | **10,638,401** |
| PPE neto (vehículo + cómputo) | 4,187,833 | 5,029,015 |
| Prepagos de impuestos | 5,600,632 | 6,787,140 |
| **TOTAL ACTIVO** | **₡39,380,446** | **₡22,454,556** |
| Cuenta x pagar a socios | 20,000,000 | 7,407,900 |
| Impuesto Renta x pagar | 326,974 | 1,756,947 |
| **TOTAL PASIVO** | **20,326,974** | **9,164,847** |
| Capital social | 10,000 | 10,000 |
| Utilidades acumuladas | 13,279,709 | 9,180,166 |
| Utilidad del período | 5,763,763 | 4,099,543 |
| **Total Patrimonio** | **19,053,472** | **13,289,709** |

### G3. Estado de Resultados
| Concepto | dic-2025 | dic-2024 | Variación |
|---|---|---|---|
| Ingresos por venta de mercadería | 40,383,201 | 151,200,991 | -73.3% |
| Costo de mercadería vendida | (19,518,751) | (123,529,391) | — |
| **Utilidad Bruta** | **20,864,450** | **27,671,600** | -24.6% |
| **Margen Bruto %** | **51.7%** | **18.3%** | +33.4 pp |
| Gastos G&A | (13,932,531) | (20,973,928) | -33.6% |
| Depreciación | (841,182) | (841,182) | 0% |
| **Utilidad Operativa** | **6,090,737** | **5,856,490** | +4.0% |
| Impuesto sobre la Renta | (326,974) | (1,756,947) | — |
| **Utilidad Neta** | **₡5,763,763** | **₡4,099,543** | +40.6% |

### G4. Activos Fijos Identificados
| Activo | Detalle | Costo | Valor en libros dic-25 | Valor mercado |
|---|---|---|---|---|
| Vehículo | KIA Sorento 2012, placa BTQ-429, importación directa USA 2019 | 6,580,000 | 3,180,333 | ~7,400,000 |
| Equipo de cómputo | — | 1,831,818 | 1,007,500 | — |

**Vidas útiles aplicadas:** vehículos 10 años, cómputo 5 años. Modelo de costo (no revaluación).

### G5. Eventos relevantes 2025
1. **Reorientación estratégica del modelo de negocio**: discontinuación de líneas de menor margen, especialización en EPP y lanzamiento Rana Walk en e-commerce internacional. Resultado: ventas -73% pero margen bruto +33 pp y utilidad neta +40.6%.
2. **Constitución de inventario operativo** ₡25.3M (calzado de protección industrial Marluvas/Tecmater) para atender demanda B2B 2026.
3. **Reclasificación contable de capital social**: ₡90,000 movidos de "Capital Social" a "Utilidades Acumuladas" para alinear presentación contable con monto legalmente inscrito en RNP (₡10,000). Aplicación retroactiva a 2023, 2024 y 2025. Sin efecto sobre patrimonio total.

---

## H. Partes Relacionadas — Saldos
| Concepto | dic-2025 | dic-2024 |
|---|---|---|
| Cuenta x pagar a socios — capital de trabajo | 20,000,000 | 7,407,900 |

**Condiciones:** Sin intereses, sin plazo definido, sin garantías. Los socios mantienen disposición de no exigir devolución mientras la operación lo requiera. Funciona como financiamiento estable de capital de trabajo.

---

## I. Indicadores Financieros Clave 2025
| Indicador | Valor | Lectura |
|---|---|---|
| Razón corriente | 1.46 | Adecuado |
| Endeudamiento total / Patrimonio | 1.07 | Moderado (predominantemente con socios) |
| Margen neto sobre ventas | 14.3% | Alto para el sector |
| ROE | 30.2% | Excelente |
| ROA | 14.6% | Sólido |
| Crecimiento utilidad neta | +40.6% | Muy positivo |

---

## J. Documentos Fuente
- Certificación notarial — Lic. Mario Arias Agüero, 2018-01-13
- Certificación RNP Digital — RNPDIGITAL-562728-2026, 2026-04-08
- Estados Financieros 2024 y 2025 — Lic. Alexander Solano Gutiérrez, CPI N° 39405
- Memorando técnico de ajustes EEFF 2025-2024 — 2026-05-04
- Declaración de actividad económica Hacienda CR — código 4641.1

---

## K. Reglas de Uso
1. **Datos en sección B-F son canónicos**: cualquier proforma, contrato, factura, declaración fiscal, trámite bancario o compliance debe usar exactamente estos valores. No abreviar razón social, no truncar cédula jurídica.
2. **Datos financieros (G-I) son históricos**: actualizar al cierre de cada ejercicio fiscal. La versión vigente de EEFF la mantiene el CPI Solano.
3. **Documento CEO-ONLY (N2)**: contiene cédulas de identidad, distribución accionaria, saldos con partes relacionadas e indicadores financieros sensibles. **Nunca indexar en pgvector.** Acceso restringido a CEO y procesos de gobernanza explícitamente autorizados.
4. **Sincronización con KB**: Si Cowork detecta inconsistencias entre este documento y otras menciones de datos societarios en `ENT_MARCA_MW_IDENTIDAD`, `ENT_COMERCIAL_CLIENTES`, `ENT_PLAT_LEGAL_ENTITY` u otros, **este documento prevalece**.
5. **Actualización de EEFF**: Al cierre de cada ejercicio fiscal, actualizar secciones G, H e I con nuevos saldos. Mantener serie histórica mínima de 2 años comparativos.

---

## L. Pendientes
| ID | Pendiente | Desbloquea | Quién decide |
|---|---|---|---|
| L1 | Reconciliación costo histórico vehículo (USD 17K vs ₡6.58M registrado) | Posible reexpresión EEFF 2026 | CEO + CPI Solano |
| L2 | Desglose Gastos G&A por subcategoría | Nota 8 EEFF completa para próximas presentaciones | CPI Solano |
| L3 | Composición inventario por proveedor (Marluvas vs Tecmater) | Nota 3 EEFF detallada | Operaciones |
| L4 | Carta de subordinación de socios sobre cuenta por pagar ₡20M | Mejora rating crediticio si se solicita financiamiento | CEO + socios |

---

## Changelog
- v1.0 (2026-05-04) — Creación inicial. Consolida datos societarios oficiales (RNP), identidad corporativa, EEFF cierre 2025 con ajustes de presentación aplicados (reclasificación capital social, identificación PPE, política inventarios). Fuentes: certificación RNP 2026-04-08 + EEFF firmados CPI Solano + Memorando ajustes 2026-05-04.
