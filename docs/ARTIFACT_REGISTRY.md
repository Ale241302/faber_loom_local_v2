# ARTIFACT_REGISTRY — Registro de Artefactos del Sistema
id: ARTIFACT_REGISTRY
version: 1.4
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
aplica_a: [SHARED]

---

Principio: artefacto registrado + ACTIVE = se puede instanciar. Artefacto no registrado = primero se crea, valida y aprueba.

Funciones: registry (catálogo versionado), catalog (referencia consultable), governance index (ciclo de vida y aprobación).

Ref → POL_ARTIFACT_CONTRACT para contrato normativo que todo artefacto debe cumplir.

---

## EXPEDIENTE (artefactos que se pegan a expedientes)

| ID | Artefacto | Version | Category | Status | Ref |
|----|-----------|---------|----------|--------|-----|
| ART-01 | OC Cliente | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-02 | Proforma MWT | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-03 | Decisión B/C | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-04 | Confirmación SAP | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-05 | AWB/BL | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-06 | Cotización flete | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-07 | Aprobación despacho | 1.0 | process | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-08 | Documentación aduanal | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-09 | Factura MWT | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-10 | Factura comisión | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-11 | Registro costos | 1.0 | pricing | ACTIVE | ENT_PLAT_ARTEFACTOS.B |
| ART-12 | Nota compensación | 1.0 | document | ACTIVE | ENT_PLAT_ARTEFACTOS.B |

## GOLDEN EXAMPLES (artefactos de referencia canónica)

| ID | Artefacto | Referencia | Datos base | Status |
|----|-----------|------------|------------|--------|
| ART-02-GE | Proforma MWT Golden Example | PF_0000-2026_GOLDEN_EXAMPLE.html | PF 2429-2026 (UMMIE, Guatemala, 604 pares, 5 líneas) | ACTIVE |
| ART-02-GE-TRI | Proforma MWT Golden Triangular | PF_2453-2026_SONDEL_TRIANGULAR_GOLDEN.html | PF 2453-2026 (SONDEL, Costa Rica, 500 pares, 3 lineas, triangular compra/reventa + vistas DDP) | ACTIVE |

Nota: Los golden examples son instancias canónicas que documentan la implementación de referencia del artefacto. Se usan para validar que nuevas instancias cumplen el design system.

## TRANSFER (artefactos que se pegan a transfers entre nodos)

| ID | Artefacto | Version | Category | Status | Ref |
|----|-----------|---------|----------|--------|-----|
| ART-13 | Recepción en nodo | 1.0 | process | DRAFT | [por crear] |
| ART-14 | Preparación / Acondicionamiento | 1.0 | process | DRAFT | [por crear] |
| ART-15 | Despacho inter-nodo | 1.0 | process | DRAFT | [por crear] |
| ART-16 | Transfer pricing approval | 1.0 | pricing | DRAFT | [por crear] |
| ART-17 | Documento de excepción | 1.0 | document | DRAFT | [por crear] |

## NODE (artefactos que se pegan a nodos)

| ID | Artefacto | Version | Category | Status | Ref |
|----|-----------|---------|----------|--------|-----|
| ART-18 | Reporte operativo | 1.0 | report | DRAFT | [por crear] |

## PRODUCTO (artefactos de producto)

| ID | Artefacto | Version | Category | Status | Ref |
|----|-----------|---------|----------|--------|-----|
| ART-19 | Sticker de Talla v7.8 | 7.8 | document | ACTIVE | rw_sticker_v7_8.html |
| ART-20 | Insole Color Spec v7 | 7.0 | document | ACTIVE | rw_insole_color_spec_v7.html |

Nota ART-19: HTML standalone con sticker de talla (barcodes SVG), ficha de producto (sensation profile, performance, comparison, color spec, dimensional specs), i18n 4 mercados, CSS harmonizado por producto. PROD_SPECS recalibrados 2026-04-03 (DEC-RATE-01). +Sección dimensional con datos planos Bonny. Supersede: rw_sticker_v7_3.html.
Nota ART-20: HTML standalone con visualización detallada de colores por plantilla (2 capas PU + textil), Pantone Delta-E CIE Lab, stripe rendering.
Nota: Versiones EN/ZH de ART-19 y ART-20 (rw_sticker_v7_8_en_zh.html, rw_insole_color_spec_v7_en_zh.html) en iteración en Claude — pendientes de subir al proyecto.

## CROSS (artefactos transversales)

(vacío — se agregan cuando aparezca necesidad real)

---

## Ciclo de vida de una definición de artefacto

```
1. DRAFT
   Quién: IA o humano propone spec siguiendo POL_ARTIFACT_CONTRACT
   Qué: definición completa (campos, reglas, eventos, permisos, UI hints)
   Regla: NO puede instanciarse en producción

2. SANDBOX
   Quién: sistema
   Qué: simular artefacto contra datos de prueba
   Validar: inputs/outputs coherentes, reglas funcionan, eventos emiten, UI renderiza
   Output: reporte de simulación

3. REVIEW
   Quién: CEO (único aprobador — ref → POL_STAMP)
   Qué: revisar spec + reporte sandbox
   Decisiones: aprobar / rechazar con feedback / pedir cambios

4. ACTIVE
   Qué: registrado en ARTIFACT_REGISTRY como disponible
   Regla: se puede instanciar en expedientes/transfers/nodos reales
   Versionamiento: nueva versión no rompe instancias existentes (ref → ENT_PLAT_ARTEFACTOS.F)

5. DEPRECATED
   Cuándo: reemplazado por versión nueva o ya no necesario
   Qué: instancias activas siguen con versión anterior
   Campo: superseded_by → ID del reemplazo
   Nuevos usos solo con versión nueva
```

---

## Reglas del registry

- Todo artefacto debe cumplir POL_ARTIFACT_CONTRACT antes de entrar al registry
- No se crean artefactos especulativos. Solo cuando hay uso real.
- Status ACTIVE = se puede usar. Status DRAFT = no se puede usar en producción.
- ID auto-incremental: ART-XX. Nunca reutilizar IDs deprecados.
- Categorías válidas: document | process | pricing | report
- applies_to válidos: expediente | transfer | node | cross | producto

---

## Métricas del registry

Total artefactos: 20
- ACTIVE: 14 (ART-01 a ART-12, ART-19, ART-20)
- DRAFT: 6 (ART-13 a ART-18)
- DEPRECATED: 0

---

Stamp: VIGENTE — actualizado 2026-04-03
Origen: Sesión de diseño conceptual bodegas/nodos/transfers — 2026-02-26

Changelog:
- v1.0: Creación inicial con 18 artefactos.
- v1.1: Golden examples section.
- v1.2: +sección PRODUCTO (ART-19 Sticker v7.8, ART-20 Color Spec v7). +applies_to "producto". Métricas 18→20. Stamp actualizado. 2026-04-03.
- v1.3: ART-19 actualizado: +dimensional specs, PROD_SPECS recalibrados. Nota sobre versiones EN/ZH pendientes. 2026-04-03.
- v1.4: +golden ART-02-GE-TRI (PF 2453, SONDEL ventas triangulares con vistas DDP MWT/SONDEL). Reconciliacion modelo B/C pendiente CEO. 2026-06-02.
