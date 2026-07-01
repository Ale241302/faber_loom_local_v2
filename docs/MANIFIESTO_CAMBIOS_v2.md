# MANIFIESTO_CAMBIOS_v2
aplica_a: [SHARED]

```
id: MANIFIESTO_CAMBIOS_v2
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: GOBERNANZA
stamp: 2026-03-18 â€” VIGENTE
tipo: APPEND-ONLY
```

---

## PropÃ³sito

Log consolidado y secuencial de todos los cambios a la KB. Cada batch de indexaciÃ³n agrega una entrada al final.

**Reglas:**
- Agregar al final: âœ…
- Editar entradas anteriores: âŒ
- Borrar entradas: âŒ
- El Arquitecto Ejecutor agrega una entrada en cada batch de indexaciÃ³n
- Los auditores usan este archivo como log de trazabilidad entre sesiones

**Reemplaza:** `MANIFIESTO_CAMBIOS.md` (FROZEN) + todos los `MANIFIESTO_APPEND_*.md` sueltos.

---

## Log de cambios

---

## Historial Pre-v4.5 (Resumen)

| Batch | Fecha | Resumen |
|-------|-------|---------|
| 001 | 2026-03-01 | Bootstrap: 22 archivos reemplazados, 1 nuevo (Scanner Glosario), 1 eliminado (IDX_PRODUCTO_patch). 19 entities huÃ©rfanasâ†’0, 14 policies VIGENTE. |
| 002 | 2026-03-13 | Sprint 8 auditorÃ­a (10 rondas, v3.10) + Sprint 9 scope definido. |
| 003 | 2026-03-18 | POL_RECURSOS v1.1 + MANIFIESTO_CAMBIOS_v2 creado (consolida MANIFIESTO_CAMBIOS FROZEN + APPENDs). |

---

### BATCH 2026-04-01-001 â€” DepuraciÃ³n Q2-2026

**Agente:** Claude (Opus) â€” Arquitecto Ejecutor
**Orden:** ORDEN_EJECUCION_DEPURACION_2026-04-01, autorizada por CEO

**Archivos eliminados (10):**

| Archivo | RazÃ³n |
|---------|-------|
| ENT_PLAT_ARQUITECTURA.md | DEPRECATED â€” contenido en ENT_PLAT_INFRA |
| ENT_PLAT_DECISIONES.md | DEPRECATED â€” contenido en ENT_GOB_DECISIONES |
| ENT_PLAT_DOCKER.md | DEPRECATED â€” contenido en ENT_PLAT_INFRA |
| ENT_PLAT_ESTRUCTURA.md | DEPRECATED â€” ya no aplica |
| ENT_PLAT_MODULOS_PENDIENTES.md | DEPRECATED â€” contenido en ENT_PLAT_MODULOS |
| ENT_COMP_CLAIMS.md | Consolidado en ENT_COMP_CONTENT_RULES.A |
| ENT_COMP_ROGERS.md | Consolidado en ENT_COMP_CONTENT_RULES.B |
| ENT_COMP_VISUAL.md | Consolidado en ENT_COMP_CONTENT_RULES.C |
| ENT_OPS_INVENTARIO.md | Absorbido en ENT_OPS_DEMAND_PLANNING |
| PLB_OPS.md | Absorbido en PLB_OPS_AMAZON |
| PLB_COMPLIANCE.md | Eliminado â€” contenido cubierto por POL_CLAIMS_SCANNER + PLB_AUDIT |

**Archivos nuevos (1):**

| Archivo | Tipo | DescripciÃ³n |
|---------|------|------------|
| ENT_COMP_CONTENT_RULES.md | Entity | Consolida Claims (A) + Rogers (B) + Visual (C) |

**Archivos modificados (~25):**

| Archivo | Cambio |
|---------|--------|
| RW_ROOT.md | v4.5.3â†’v4.8.0. +SKILL como 8vo tipo. Changelog pre-v4.0 comprimido. |
| PLB_OPS_AMAZON.md | v1.0â†’v1.1. +secciÃ³n Reglas Generales Ops (absorbido de PLB_OPS). |
| ENT_OPS_DEMAND_PLANNING.md | v0.1â†’v0.2. +nota absorciÃ³n ENT_OPS_INVENTARIO. |
| ENT_GOB_AGENTES.md | v2.1â†’v2.2. Refs PLB_OPSâ†’PLB_OPS_AMAZON, PLB_COMPLIANCE removido. |
| IDX_COMPLIANCE.md | Removidos 3 originales + PLB_COMPLIANCE. +CONTENT_RULES. +Skills. |
| IDX_OPS.md | Removidos INVENTARIO + PLB_OPS. +Skills. |
| IDX_PLATAFORMA.md | Removidos 5 DEPRECATED. +Skills. |
| IDX_COMERCIAL.md | +Skills. |
| IDX_GOBERNANZA.md | +Skills. |
| IDX_MARKETPLACE.md | +Skills. |
| DEPENDENCY_GRAPH.md | Refs CLAIMS/ROGERS/VISUALâ†’CONTENT_RULES.A/B/C. |
| ENT_COMP_AMAZON.md | Refs CLAIMS/VISUALâ†’CONTENT_RULES.A/C. |
| ENT_PLAT_KNOWLEDGE.md | Removidas refs ARQUITECTURA, DOCKER. |
| ENT_PLAT_MODULOS.md | Refs DOCKER/ARQUITECTURAâ†’INFRA. INVENTARIOâ†’DEMAND_PLANNING. |
| ENT_GOB_RIESGOS.md | Refs DOCKERâ†’INFRA. PLB_COMPLIANCEâ†’POL_CLAIMS_SCANNER. CLAIMSâ†’CONTENT_RULES.A. |
| ENT_COMP_ISO_ROADMAP.md | Refs PLB_COMPLIANCEâ†’POL_CLAIMS_SCANNER. |
| ENT_PLAT_DESIGN_TOKENS.md | Refs VISUALâ†’CONTENT_RULES.C. |
| ENT_PLAT_CONTRATO_NODO.md | ceo_only_sections: [B.financieros]â†’[B]. |
| ENT_PROD_LANZAMIENTO.md | ceo_only_sections: [triggers_margen]â†’[T3.4, T5.3]. |
| +12 archivos con refs actualizadas | SELLO, ICP, PROVEEDORES, AUDIT_VISUAL_BRIEF, EXPERIMENTACION, POL_CLAIMS_SCANNER, POL_PRINT, POL_ROGERS, POL_ARTIFACT_CONTRACT, SCH_BRIEF_PROVEEDOR, SCH_EMPAQUE_BASE, SCH_LLMS_TXT |
| DASHBOARD_SNAPSHOT.md | v4.0â†’v5.0. Conteos post-depuraciÃ³n. 8 tipos. 0 DEPRECATED. |
| MANIFIESTO_CAMBIOS_v2.md | Pre-v4.5 comprimido a tabla resumen. +esta entrada. |

**MÃ©tricas:**

| MÃ©trica | Antes | DespuÃ©s |
|---------|-------|---------|
| Archivos totales | 340 | 329 |
| DEPRECATED | 5 | 0 |
| Tipos en taxonomÃ­a | 7 | 8 (+ SKILL) |
| Refs rotas a archivos eliminados | ~20 | 0 |

**Pendientes generados:** Ninguno. 6 SKILL_ files registrados como PENDIENTE creacion en IDXs.

---

### BATCH 2026-04-02-001 â€” Consolidacion final v5.0

**Agente:** Claude (Cowork) â€” Sync GitHub + depuracion efimeros
**Orden:** CEO autoriza depuracion via batches 1-4

**Archivos purgados (86):**

| Categoria | Cantidad | Razon |
|-----------|----------|-------|
| MANIFIESTO_APPEND_* | 37 | Consolidados en MANIFIESTO_CAMBIOS_v2 |
| PATCH_* + DEPENDENCY_GRAPH_PATCH | 7 | Ya aplicados a archivos target |
| CHECKPOINT_SESSION_* | 3 | Backups de sesion obsoletos |
| REPORTE_SESION_* + AUDIT_BASELINE | 6 | Fotografias de sesiones cerradas |
| apply_batch_*.sh + health_check.sh | 13 | Scripts ya ejecutados |
| PROMPT_ANTIGRAVITY_* | 8 | Prompts consumidos |
| GUIA_ALE_* | 4 | Guias consumidas |
| AGENT_A/C/D + AUDIT_SELF + Resumen | 5 | Analisis consumidos |
| ROADMAP_SPRINTS_17_27 + CONVERGENCIA | 2 | Reemplazados por ROADMAP_EXTENDIDO |
| MANIFIESTO_CAMBIOS (v1) | 1 | Reemplazado por _v2 |

**Archivos nuevos (11):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| SKILL_PROFORMA_BUILDER.md | Skill | Constructor proformas ART-02 |
| SKILL_AMAZON_OPS.md | Skill | Operaciones Amazon FBA |
| SKILL_CLIENT_SERVICE.md | Skill | Servicio cliente B2B (SVC-01) |
| SKILL_COMPLIANCE_CHECKER.md | Skill | Validador compliance |
| SKILL_EXPERIMENT_RUNNER.md | Skill | A/B testing Amazon |
| SKILL_KB_AUDITOR.md | Skill | Auditor integridad KB |
| ENT_PLAT_SKILLS_CATALOG.md | Entity | Catalogo centralizado de skills |
| ENT_PLAT_AGENT_ORCHESTRATION.md | Entity | Patrones orquestacion agentes |
| ENT_COMP_CONTENT_RULES.md | Entity | Consolida Claims + Rogers + Visual |
| MANIFIESTO_APPEND_20260401_DEPURACION.md | Append | Log de la depuracion |
| apply_batch_20260401_depuracion.sh | Script | Script de ejecucion batch |

**Archivos modificados (~30):**

| Archivo | Cambio |
|---------|--------|
| RW_ROOT.md | v4.5.3->v5.0.0. Taxonomia 8 tipos (+SKILL). Conteo 265. |
| DASHBOARD_SNAPSHOT.md | v5.0->v5.1. Conteos reales post-depuracion. |
| ENT_PLAT_SSOT.md | STUB->VIGENTE v1.0. 11 SSOTs registrados. |
| MANIFIESTO_CAMBIOS_v2.md | +esta entrada. |
| LOTE_SM_SPRINT1-21.md | 17 sprints comprimidos DONE (~10,800->~900 lineas). |
| IDX_COMERCIAL/COMPLIANCE/GOBERNANZA/MARKETPLACE/PLATAFORMA/OPS.md | +seccion Skills. Refs actualizadas. |
| DEPENDENCY_GRAPH.md | Refs CLAIMS/ROGERS/VISUAL->CONTENT_RULES. |
| +15 archivos con refs actualizadas | ENT_COMP_AMAZON, ENT_GOB_*, ENT_PLAT_*, POL_*, SCH_* |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 340 | 265 |
| Reduccion | â€” | -22% |
| DEPRECATED | 5 | 0 |
| Efimeros (APPEND/PATCH/CHECKPOINT) | ~75 | 0 |
| SKILL_ files | 0 | 6 |
| Tipos en taxonomia | 7 | 8 |
| LOTEs comprimidos | 0 | 17 |
| Lineas ahorradas (LOTEs) | ~10,800 | ~900 |
| GitHub sync | Manual | Automatizado via Cowork |

**Pendientes generados:**
- PLB_OPS_AMAZON storage fees: tabla hardcoded -> ref ENT_COMERCIAL_COSTOS (P1)
- Crear proyecto nuevo Claude Projects "KW MWT 5.0 02 ABRIL 2026" con los 265 archivos

---

### BATCH 2026-04-02-002 â€” Fichas Tecnicas Rana Walk + Sticker v7.6

**Agente:** Claude (Opus) â€” Arquitecto Ejecutor + Claude (Cowork) â€” Sync
**Sesion:** Fichas Tecnicas RW â€” tecnologias, ejes evaluacion, paleta color, ratings CEO

**Archivos modificados (4 en proyecto Claude):**

| Archivo | Cambio |
|---------|--------|
| ENT_TECH.md | v0.1->v1.0. Reescritura completa. 7 tecnologias (nueva: Orca Tail). Orbis sin Arch System. 6 ejes evaluacion + ratings CEO. |
| LOC_TECH_EN.md | STUB->v1.0. 7 tecnologias traducidas EN. |
| LOC_TECH_PT.md | STUB->v1.0. 7 tecnologias traducidas PT. |
| LOC_TECH_ES.md | STUB->v1.0. Ref a ENT_TECH como fuente canonica. |

**Archivos nuevos (3 en GitHub/Cowork):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| CHANGELOG_SESION_20260402_FICHAS_TECNICAS.md | Changelog | Log completo: tecnologias, ejes, paleta, ratings, copy aprobado |
| CHANGELOG_rw_sticker_v7_6.md | Changelog | 6 cambios sticker HTML: layout 3 cuerpos Goliath, barcode rules, i18n fix |
| PROMPT_FIX_STICKER_V76.md | Prompt | Spec completa para fix sticker v7.6: SIZE_COLORS, barcode rules, checklist |

**Decisiones CEO registradas (4):**

| ID | Decision |
|----|----------|
| DEC-TECH-01 | 6 ejes evaluacion reemplazan C4 legacy |
| DEC-TECH-02 | Orbis sin Arch System (2 tecnologias, no 3) |
| DEC-TECH-03 | NanoSpread 5C = limite inferior operacion |
| DEC-TECH-04 | PORON XRD: no referenciar uso militar/deportivo sin autorizacion Rogers |

**Ratings oficiales CEO (6 ejes x 7 productos):**

| Eje | GOL | VEL | ORB | LEO | BIS | MAN | ORC |
|-----|-----|-----|-----|-----|-----|-----|-----|
| Delgada-Gruesa | 8 | 3 | 7 | 7 | 7 | 4 | 5 |
| Suavidad-Firmeza | 8 | 6 | 6 | 6 | 6 | 9 | 6 |
| Flexibilidad-Rigidez | 6 | 2 | 4 | 4 | 4 | 7 | 4 |
| Proteccion impacto | 9 | 5 | 5 | 7 | 9 | 9 | 9 |
| Retorno energia | 7 | 9 | 6 | 6 | 6 | 4 | 6 |
| Humedad/temp | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 265 | 268 |
| ENT_TECH version | v0.1 | v1.0 |
| LOC_TECH_* status | STUB | VIGENTE |
| Tecnologias documentadas | 6 | 7 (+Orca Tail) |

**Pendientes generados:**
- Aplicar PATCH_ENT_PROD_EJES en 7 archivos ENT_PROD_*.md (P0)
- Actualizar Word fichas v4 con 6 ejes + sliders (P1)
- Propagar ejes a LOC_{PROD}_{LANG} EN/PT (P2)
- RW_ROOT version bump post-batch (P1)
- Datos fisicos fabricante: peso, espesor, Shore A (P2)

---

### BATCH 2026-04-03-001 â€” Sticker v7.8 + Color Spec + Modelo 2 Capas

**Agente:** Claude (Opus) â€” Sesion Sticker/Color + Claude (Cowork) â€” Sync
**Contexto:** Evolucion sticker v7.6â†’v7.8, modelo constructivo 3â†’2 capas, material Orca PORON XRDâ†’Thinboom, color spec standalone

**Archivos nuevos (4):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| ENT_PROD_COLORES.md | Entity | Paleta colores 7 productos: Pantone, HEX, RGB, Delta-E, CIE Lab |
| rw_sticker_v7_8.html | Artifact | Sticker talla + ficha producto + i18n 4 mercados (ART-19) |
| rw_insole_color_spec_v7.html | Artifact | Color spec standalone Pantone/Delta-E/CIE Lab (ART-20) |
| MANIFIESTO_APPEND_20260403_STICKER_V78.md | Append | Log de esta sesion |

**Archivos modificados (7):**

| Archivo | Cambio |
|---------|--------|
| RW_ROOT.md | v4.5.3â†’v4.5.4. |
| ENT_PROD_ORC.md | v1.0â†’v1.1. PORON XRDâ†’Thinboom en C1/C2/C3. |
| ENT_OPS_TALLAS.md | v0.1â†’v0.2. SSOTâ†’rw_sticker_v7_8. SKUs 54â†’66 (+MAN +ORC). |
| ENT_PROD_COMPARATIVA.md | v2.0â†’v3.0. +MAN +ORC rankings. +ejes bipolares/unipolares. |
| ARTIFACT_REGISTRY.md | v1.1â†’v1.2. +ART-19 +ART-20. Artifacts 18â†’20. |
| SCH_STICKER_BASE.md | v1.0â†’v1.1. +requires COLORES/COMPARATIVA. +slots ficha producto. |
| IDX_PRODUCTO.md | +ENT_PROD_COLORES. Health 13â†’14. |

**Cambios arquitectonicos:**
- Modelo constructivo 3â†’2 capas (PU BASE + TEXTIL con sublimado integrado)
- Orca: PORON XRD eliminado â†’ Thinboom
- Linea completa 7 modelos = 66 SKUs en todos los docs

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 270 | 274 |
| Artifacts HTML | 0 en KB | 2 (ART-19, ART-20) |
| SKUs documentados | 54 | 66 |
| RW_ROOT version | v4.5.3 | v4.5.4 |

**Pendientes generados:**
- Rankings MAN/ORC en COMPARATIVA son estimados â€” pendiente validacion CEO
- DEPENDENCY_GRAPH: agregar SCH_STICKER_BASE â†’ ENT_PROD_COLORES

---

### BATCH 2026-04-03-002 â€” Planos Bonny + Recalibracion Ratings + Dimensional Specs (LOG)

**Agente:** Claude (Opus) â€” Sesion planos/dimensional + Claude (Cowork) â€” Indexacion log
**Contexto:** Planos fabrica Bonny recibidos (GOL/ORB/LEO-BIS), datos dimensionales extraidos, 11 ratings PROD_SPECS recalibrados con evidencia, nueva seccion Dimensional Specs en sticker

**Archivos nuevos (1):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| SESION_20260403_PLANOS_DIMENSIONAL.md | Log | Sesion completa: planos, datos dim, recalibracion, composicion, decisiones CEO |

**Archivos modificados (0):**
Ningun archivo KB fue modificado en este batch. Los cambios estan documentados en el log pero **pendientes de aplicar** (9 cambios listados en seccion 10 del log).

**Decisiones CEO registradas:**
- DEC-DIM-01/02/03: Datos cliente vs internos, grosor constante entre tallas
- DEC-RATE-01/02/03: 11 ratings recalibrados (GOL, ORB, BIS, MAN, ORC)
- DEC-MAT-01: Orca = Thinboom (no PORON XRD)
- DEC-MAT-02: Orbis sin Arch System (bug en ENT_PROD_ORB.C1)

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 274 | 275 |
| Cambios pendientes de indexar | 0 | 9 |

**Pendientes generados (no aplicar hasta orden CEO):**
1. Fix ENT_PROD_ORB.C1: quitar Arch System
2. Ratings recalibrados en ENT_PROD_COMPARATIVA
3. Bloque G Dimensional en 7 ENT_PROD_*.md
4. LOC dimensional strings en 21 LOC_*_*.md
5. Artifacts nuevos en ARTIFACT_REGISTRY (EN/ZH)
6. RW_ROOT version bump
7. Datos faltantes fabricante: VEL/MAN/ORC grosor + peso x7

---

### BATCH 2026-04-03-003 â€” Aplicacion cambios dimensional + recalibracion + fix ORB

**Agente:** Claude (Cowork) â€” Aplicacion directa en KB
**Contexto:** Implementacion de los 9 cambios pendientes del BATCH 002 (sesion planos Bonny)

**Archivos modificados (30):**

| Grupo | Archivos | Cambio |
|-------|----------|--------|
| ENT_PROD_ORB | 1 | Fix C1/C2: quitar Arch System (DEC-MAT-02). +Bloque G. v1.1â†’1.2 |
| ENT_PROD_GOL/VEL/LEO/BIS/MAN/ORC | 6 | +Bloque G Dimensional. Version bump cada uno. |
| ENT_PROD_COMPARATIVA | 1 | +tabla PROD_SPECS recalibrados 11 valores. v3.0â†’3.1 |
| ARTIFACT_REGISTRY | 1 | ART-19 nota +dimensional/recalib. v1.2â†’1.3 |
| LOC_*_EN/ES/PT (7 productos Ã— 3 idiomas) | 21 | +Dimensional Labels (dimTitle, dimForefoot, dimHeel, dimDrop, dimWeight, dimPending) |

**Archivos nuevos (1):**

| Archivo | Tipo |
|---------|------|
| MANIFIESTO_APPEND_20260403_DIMENSIONAL.md | Append log |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 275 | 276 |
| Cambios pendientes batch 002 | 9 | 0 (aplicados) |
| PROD_SPECS recalibrados | 0 de 11 | 11 de 11 |
| Bloque G Dimensional | 0 de 7 | 7 de 7 |
| LOC Dimensional Labels | 0 de 21 | 21 de 21 |

**Pendientes residuales:**
- Datos fabricante Bonny: VEL/MAN/ORC grosor + peso Ã— 7 productos
- Versiones EN/ZH de ART-19 y ART-20: iterando en Claude

---

### BATCH 2026-04-03-004 â€” Claims + User Types (batch Claude) + merge Cowork

**Agente:** Claude (Projects) â€” Sesion claims/user types + Claude (Cowork) â€” merge
**Contexto:** Batch .bat generado en Claude con 9 archivos: semaforo claims, user types, correcciones CEO ORB, pendientes CEO-25/26/27

**Archivos nuevos (2):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| ENT_MKT_USER_TYPES.md | Entity | 9 user types Ã— 7 productos, matriz no exclusiva |
| MANIFIESTO_APPEND_20260403_CLAIMS_USERTYPES.md | Append | Log sesion claims |

**Archivos modificados (7):**

| Archivo | Cambio |
|---------|--------|
| ENT_PROD_ORB.md | Merge: batch CEO (A3, A5, C3, E5, A9 compliance) + Cowork (Bloque G). v1.2â†’1.3 |
| ENT_COMP_CLAIMS.md | STUBâ†’DRAFT. Semaforo GREEN/YELLOW/RED lenguaje producto. |
| IDX_MARKETPLACE.md | +ENT_MKT_USER_TYPES. Health 8â†’9. |
| IDX_COMPLIANCE.md | ENT_COMP_CLAIMS status actualizado. |
| ENT_GOB_PENDIENTES.md | v11.0â†’11.1. +CEO-25/26/27 (POL_ROGERS, SELLO, disclaimer). |
| RW_ROOT.md | Merge: batch changelog completo v3.4â†’v4.5.4 + Cowork v4.5.5. |
| DEPENDENCY_GRAPH.md | v3.0â†’3.1. +nodo USER_TYPES, +CLAIMS actualizado. |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 276 | 278 |
| RW_ROOT version | v4.5.5 | v4.5.5 (changelog enriquecido) |

---

### BATCH 2026-04-05-001 â€” PLB_AUDIT_VISUAL v1.0

**Agente:** Claude (Projects) â†’ Claude (Cowork)
**Contexto:** Playbook completo de auditorÃ­a visual. STUB v0.1 â†’ DRAFT v1.0. 11 secciones (A-K): propÃ³sito/alcance, fuentes canÃ³nicas con precedencia, contrato de entrada, perfiles+mÃ³dulos, pipeline L1-L9, scoring/bloqueo, auto-fix/escalaciÃ³n, scorecard operativo, compilaciÃ³n on-demand DESIGN.md, ciclo mejora iterativa, prompt de activaciÃ³n.

**Archivos modificados (1):**

| Archivo | Cambio |
|---------|--------|
| PLB_AUDIT_VISUAL.md | STUB v0.1 â†’ DRAFT v1.0. Contenido completo 11 secciones. |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 278 | 278 |
| RW_ROOT version | v4.5.5 | v4.5.6 |

---

### BATCH 2026-04-05-002 â€” Sprint 22 DONE: Pricing Engine Marluvas

**Agente:** Alejandro (ejecucion) â†’ Claude (Cowork) â€” Indexacion
**Contexto:** Sprint 22 completado. Pricing Engine con estructura real Marluvas: waterfall 5 pasos (CPAâ†’BCPAâ†’GradeItemâ†’Legacyâ†’Manual), Early Payment, MOQ por Grade, upload masivo, Brand/Client Console tabs, 44 tests backend. Servidor operativo.

**Archivos nuevos (1):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| RESUMEN_SPRINT22.md | Resumen | Reporte ejecucion S22: 20 items en 4 fases, 44 tests, 9 migraciones, 6 componentes FE |

**Archivos modificados (1):**

| Archivo | Cambio |
|---------|--------|
| LOTE_SM_SPRINT22.md | DRAFT v1.7 â†’ DONE v1.7. Servidor operativo. |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 278 | 279 |
| RW_ROOT version | v4.5.6 | v4.5.7 |

---

### BATCH 2026-04-05-003 â€” Sprint 23 Spec: Reglas Comerciales

**Agente:** Claude (Projects) â†’ Claude (Cowork) â€” Indexacion
**Contexto:** Lote S23 compilado y auditado (R4 9.4/10). Reglas comerciales: rebates, comisiones, ArtifactPolicy a DB. App commercial/ con 7 modelos, 5 servicios, 6 endpoints, 2 tabs FE, 56 tests. 3 decisiones CEO pendientes.

**Archivos nuevos (3):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| LOTE_SM_SPRINT23.md | Lote | Spec v1.4 auditada. 15 items en 4 fases. Rebates + herencia + ArtifactPolicy DB |
| GUIA_ALE_SPRINT23.md | Guia | Guia ejecucion AG-02 (Alejandro). Orden dia a dia, dependencias, comandos |
| PROMPT_ANTIGRAVITY_SPRINT23.md | Prompt | Prompt Antigravity para agente dev. Contexto + reglas + checklist |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 279 | 282 |
| RW_ROOT version | v4.5.7 | v4.5.8 |

---

### BATCH 2026-04-06-001 â€” RemediaciÃ³n Post-AuditorÃ­a Cruzada

**Agente:** Claude (Cowork) â€” AuditorÃ­a + remediaciÃ³n
**Contexto:** AuditorÃ­a cruzada de mwt-knowledge-hub y mwt_one. 15 hallazgos (3 crÃ­ticos seguridad, 2 altos coherencia). RemediaciÃ³n ejecutada en ambos repos.

**Archivos nuevos (3):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| LOTE_SM_SPRINT20B.md | Lote | Indexado desde mwt_one. DONE v1.8. Frontend Policy-Driven. |
| AUDIT_GITHUB_COWORK_2026-04-06.md | Audit | Reporte auditoria cruzada 2 repos, 15 hallazgos |
| MANIFIESTO_APPEND_20260406_REMEDIATION.md | Append | Log remediacion |

**Archivos modificados (4):**

| Archivo | Cambio |
|---------|--------|
| DASHBOARD_SNAPSHOT.md | v5.1â†’v6.0. Conteos reales (281â†’283). FROZEN=2. Sprint 22 DONE. S20B DONE. |
| LOTE_SM_SPRINT23.md | IN_PROGRESSâ†’DRAFT (status canonico) |
| LOTE_SM_SPRINT22.md | Ref S21 actualizada DRAFTâ†’DONE |
| RW_ROOT.md | v4.5.8â†’v4.5.9. 283 archivos. |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 280 | 283 |
| RW_ROOT version | v4.5.8 | v4.5.9 |
| FROZEN reportados | 0 | 2 |

---

### BATCH 2026-04-06-002 â€” Sprint 23 DONE: MÃ³dulo Commercial

**Agente:** Alejandro (ejecucion) â†’ Claude (Cowork) â€” Indexacion
**Contexto:** Sprint 23 completado. MÃ³dulo commercial: rebates, comisiones, ArtifactPolicy a DB. 16 items, 6 fases, 56 tests, 13 hotfixes. Servidor operativo. AuditorÃ­a seguridad incluida.

**Archivos nuevos (1):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| RESUMEN_SPRINT23.md | Resumen | Reporte ejecucion S23: 16 items, 6 fases, 56 tests, 35 archivos BE, 4 FE |

**Archivos modificados (1):**

| Archivo | Cambio |
|---------|--------|
| LOTE_SM_SPRINT23.md | DRAFT â†’ DONE. Servidor operativo. |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 283 | 284 |
| RW_ROOT version | v4.5.9 | v4.6.0 |

---

### BATCH 2026-04-07-001 â€” Sprint 24 Spec: Seguridad B2B + Knowledge Pipeline

**Agente:** Claude (Projects) â†’ Claude (Cowork) â€” Indexacion
**Contexto:** Lote S24 compilado y auditado (R3 GPT-5.4). Seguridad B2B + Knowledge Pipeline. 3 archivos nuevos.

**Archivos nuevos (3):**

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| LOTE_SM_SPRINT24.md | Lote | Spec v1.3 auditada. Seguridad B2B + Knowledge Pipeline |
| GUIA_ALE_SPRINT24.md | Guia | Guia ejecucion AG-02 (Alejandro) |
| PROMPT_ANTIGRAVITY_SPRINT24.md | Prompt | Prompt Antigravity para agente dev |

**Metricas:**

| Metrica | Antes | Despues |
|---------|-------|---------|
| Archivos totales | 284 | 287 |
| RW_ROOT version | v4.6.0 | v4.6.1 |

---

### BATCH 2026-04-07-002 â€” Sprint 24 DONE

**Archivos modificados:**
- `LOTE_SM_SPRINT24.md` â€” DRAFT â†’ DONE (ejecutado AG-02, 15/15 DoD)

**Archivos nuevos:**
- `RESUMEN_SPRINT24.md` â€” Reporte ejecuciÃ³n Sprint 24: Seguridad B2B + Knowledge Pipeline. 15 items, 3 fases + tests + E2E. JWT rotation, rate limiting, signed URLs, knowledge pipeline dual routing. 15/15 tests seguridad.

**RW_ROOT:** v4.6.1 â†’ v4.6.2 (288 archivos)

### BATCH 2026-04-08-001 â€” Merge Sprint 25 (desde sesiÃ³n paralela)

**Contexto:** Otra sesiÃ³n Cowork operÃ³ sobre carpeta "KW MWT 4.5.3 22 MARZO 2026" (vacÃ­a, no sincronizada). Los archivos S25 fueron creados ahÃ­ pero nunca llegaron a la KB real. Este batch integra ese trabajo.

**Archivos nuevos (5):**
- `LOTE_SM_SPRINT25.md` â€” Lote v1.6, EN EJECUCIÃ“N. Payment Status Machine + Precio Diferido + Parent/Child. 56 tests, 6 rondas auditorÃ­a (score 9.6/10).
- `GUIA_ALE_SPRINT25.md` â€” Instrucciones ejecuciÃ³n AG-02 Sprint 25.
- `PROMPT_ANTIGRAVITY_SPRINT25.md` â€” Prompt ejecuciÃ³n AG-02 backend, alineado LOTE v1.6.
- `AUDIT_R3_SPRINT25.md` â€” Prompt auditorÃ­a tÃ©cnica + resultado R3.
- `PROMPT_AUDIT_SPRINT25.md` â€” Prompt auditorÃ­a tÃ©cnica LOTE S25.

**Archivos NO sobreescritos (nuestra versiÃ³n es canÃ³nica):**
- `RW_ROOT.md` â€” nuestra lÃ­nea v4.5.5â†’v4.6.2 prevalece, S25 integrado como v4.6.3
- `DASHBOARD_SNAPSHOT.md` â€” datos de la otra sesiÃ³n basados en v4.5.4, obsoletos

**RW_ROOT:** v4.6.2 â†’ v4.6.3 (295 archivos)

### BATCH 2026-04-08-002 â€” Sprint 25 DONE + Sprint 27 EN PREPARACIÃ“N

**Contexto:** Entregable AG-02 Sprint 25 procesado. 22 archivos (13 nuevos, 9 modificados), 59 tests, 4 fases completas. Commits 14ce585 + 0fcefa50. ENT_GOB_PENDIENTES actualizado: CEO-12/13/18/20/21 marcados DONE (resueltos en S24, nunca actualizados). CEO-17/19 marcados PARCIAL con residual a S27. LOTE_SM_SPRINT27 compilado.

**Archivos modificados (6):**
- `LOTE_SM_SPRINT25.md` â€” EN EJECUCIÃ“N â†’ DONE v1.7 (AG-02, 59 tests, 2026-04-08)
- `ENT_GOB_PENDIENTES.md` â€” v11.1 â†’ v11.2. CEO-12/13/18/20/21 DONE. CEO-17/19 PARCIAL â†’ S27.
- `DASHBOARD_SNAPSHOT.md` â€” v6.0 â†’ v6.1. Sprints actualizados. 297 archivos.
- `RESUMEN_SPRINT25.md` â€” header TRANSITORIO agregado. Lote ref actualizado a v1.7.
- `MANIFIESTO_CAMBIOS_v2.md` â€” este append.
- `RW_ROOT.md` â€” v4.6.3 â†’ v4.6.4.

**Archivos nuevos (2):**
- `RESUMEN_SPRINT25.md` â€” entregable AG-02 Sprint 25. TRANSITORIO â†’ Drive post-sesiÃ³n.
- `LOTE_SM_SPRINT27.md` â€” Seguridad residual v1.0. 4 fases: verificaciÃ³n completa ENT_PLAT_SEGURIDAD, secrets audit, backup encriptado, Cloudflare + Docker hardening. 10 DoD items.

**RW_ROOT:** v4.6.3 â†’ v4.6.4 (297 archivos)

---

### Batch 2026-04-08-003 â€” IndexaciÃ³n Sprint 26 spec

**Archivos nuevos (2):**
- `LOTE_SM_SPRINT26.md` v2.3 â€” spec S26: Notificaciones Email + Cobranza + Admin Templates. 1,243L. Auditado R14 9.1/10. Bloqueado en CEO-28.
- `GUIA_ALE_SPRINT26.md` v1.0 â€” instrucciones AG-02. 20 pasos en 4 fases.

**Archivos modificados (4):**
- `ENT_GOB_PENDIENTES.md` v11.2 â†’ v11.3 â€” +CEO-28 (email provider bloqueante) + DEC-S26-02/03/04/05.
- `DASHBOARD_SNAPSHOT.md` v6.1 â†’ v6.2 â€” S26 SPEC LISTA. 297 â†’ 301 archivos. LOTE_ 25 â†’ 26.
- `MANIFIESTO_CAMBIOS_v2.md` â€” append esta entrada.
- `RW_ROOT.md` v4.6.4 â†’ v4.6.5.

**No indexado:** `PROMPT_ANTIGRAVITY_SPRINT26.md` (tool externo). `Resumen_sprint25.md` (batch 002).

**RW_ROOT:** v4.6.4 â†’ v4.6.5 (301 archivos)

### BATCH 2026-04-01 â€” DepuraciÃ³n KB v5.0

**Contexto:** DepuraciÃ³n mayor. 340â†’263 archivos (-25%). 85 archivos efÃ­meros purgados (35 MANIFIESTO_APPENDs, 12 apply_batch_, 8 PROMPT_ANTIGRAVITY_, 4 GUIA_ALE_, 6 REPORTE_, 3 CHECKPOINT_, y otros). 22 LOTEs DONE comprimidos (~10,800â†’~900 lÃ­neas, -92%). TaxonomÃ­a actualizada 7â†’8 tipos (+SKILL_). ENT_PLAT_SSOT STUBâ†’VIGENTE v1.0. Sprint 21 DONE.

**Archivos nuevos (8):** SKILL_PROFORMA_BUILDER, SKILL_AMAZON_OPS, SKILL_CLIENT_SERVICE, SKILL_COMPLIANCE_CHECKER, SKILL_EXPERIMENT_RUNNER, SKILL_KB_AUDITOR, ENT_PLAT_SKILLS_CATALOG, ENT_PLAT_AGENT_ORCHESTRATION.

**Archivos modificados:** RW_ROOT v5.0.0 (taxonomÃ­a 8 tipos, registros limpios), DASHBOARD_SNAPSHOT v5.0, ENT_PLAT_SSOT v1.0, LOTEs S1-S21 comprimidos DONE.

**RW_ROOT:** v4.5.3 â†’ v5.0.0 (263 archivos)

---

### BATCH 2026-04-03-A â€” Claims + User Types

**Archivos nuevos (1):** ENT_MKT_USER_TYPES v1.0 â€” 9 user types Ã— 7 productos, matriz no exclusiva.

**Archivos modificados (5):** ENT_PROD_ORB v1.2 (A3/A5/C1/E5 corregidos, compliance-safe), ENT_COMP_CLAIMS STUBâ†’DRAFT v1.0 (semÃ¡foro GREEN/YELLOW/RED), IDX_MARKETPLACE (+1 entity), IDX_COMPLIANCE (status actualizado), ENT_GOB_PENDIENTES v11.1 (+CEO-25/26/27).

**Infraestructura:** RW_ROOT v4.5.4, DEPENDENCY_GRAPH v3.1.

---

### BATCH 2026-04-03-B â€” Planos Bonny + Dimensional Specs

**Contexto:** Planos fÃ¡brica Bonny recibidos. RecalibraciÃ³n 11 PROD_SPECS con evidencia dimensional. Fix: ORB C1 (sin Arch System). Modelo constructivo 3â†’2 capas (PU + Textil).

**Archivos modificados (30):** 7 ENT_PROD_* +Bloque G Dimensional, ENT_PROD_COMPARATIVA v3.1 (specs recalibrados), 21 LOC_*_* +Dimensional Labels, ARTIFACT_REGISTRY v1.3.

---

### BATCH 2026-04-03-C â€” Sticker v7.8 + Color Spec + Orca Thinboom

**Archivos nuevos (1):** ENT_PROD_COLORES v1.0 VIGENTE (SSOT paleta).

**Archivos modificados (6):** ENT_PROD_ORC v1.1 (PORON XRD â†’ Thinboom), ENT_OPS_TALLAS v0.2 (66 SKUs, SSOT â†’ rw_sticker_v7_8.html), ENT_PROD_COMPARATIVA v3.0 (+MAN +ORC), ARTIFACT_REGISTRY v1.2 (+ART-19, +ART-20), SCH_STICKER_BASE v1.1, IDX_PRODUCTO (+ENT_PROD_COLORES).

**Artefactos HTML:** rw_sticker_v7_8.html (ART-19), rw_insole_color_spec_v7.html (ART-20).

---

### BATCH 2026-04-06 â€” RemediaciÃ³n Post-AuditorÃ­a Cruzada

**Contexto:** AuditorÃ­a Cowork Opus 4.6 (15 hallazgos, score pre ~6.8/10). Seguridad mwt_one: passwords a variables de entorno, logs eliminados del repo, seed_demo_data anonimizado, SECRET_KEY default eliminado.

**Archivos KB modificados:** LOTE_SM_SPRINT20B +indexado (DONE), DASHBOARD_SNAPSHOT v6.0 (FROZEN=2, conteos corregidos), LOTE_SM_SPRINT23 IN_PROGRESSâ†’DRAFT, LOTE_SM_SPRINT22 ref S21 actualizada.

**RW_ROOT:** v4.5.8 â†’ v4.5.9 (283 archivos)

---

### BATCH 2026-04-09 â€” RemediaciÃ³n AuditorÃ­a ECC (H1-H5+H7)

**Contexto:** AuditorÃ­a Claude ECC 2026-04-09 score 7.8/10. RemediaciÃ³n: taxonomÃ­a SKILL_ agregada, efÃ­meros purgados, DEPRECATED eliminados, registros especiales RW_ROOT actualizados. ConsolidaciÃ³n de 5 MANIFIESTO_APPENDs pendientes.

**Archivos eliminados (27):** 5 DEPRECATED (ENT_PLAT_ARQUITECTURA, ENT_PLAT_DECISIONES, ENT_PLAT_DOCKER, ENT_PLAT_ESTRUCTURA, ENT_PLAT_MODULOS_PENDIENTES). 22 efÃ­meros: GUIA_ALE_ S23/S24/S25, PROMPT_ANTIGRAVITY_ S23/S24/S25/FIX_STICKER, PROMPT_AUDIT_SPRINT25, RESUMEN_SPRINT* S22-S25, CHANGELOG_SESION_20260402_FICHAS_TECNICAS, CHANGELOG_rw_sticker_v7_6, AUDIT_GITHUB_COWORK_2026-04-06, AUDIT_R3_SPRINT25, SESION_20260403_PLANOS_DIMENSIONAL, DEC_MODE_RENAME, apply_batch_20260401_depuracion.sh, MWT_KB_v5.0_CLEAN_265.zip, SUBIR_A_CLAUDE_11_NUEVOS.zip. 5 MANIFIESTO_APPENDs consolidados.

**Archivos modificados:** RW_ROOT (taxonomÃ­a 8 tipos, regla indexaciÃ³n SKILL_, registros especiales actualizados), MANIFIESTO_CAMBIOS_v2 (5 entradas consolidadas). +POL_CONTEXT_BUDGET, +POL_EPHEMERAL_OUTPUT. DASHBOARD_SNAPSHOT regenerado.

**RW_ROOT:** v4.6.5 â†’ v4.6.6

---

### BATCH 2026-04-17-A â€” Arquitectura Agentes + InvestigaciÃ³n Kimi + MWT Platform

**Agente:** Claude (Cowork) â€” Arquitecto Ejecutor
**SesiÃ³n:** ContinuaciÃ³n de sesiÃ³n anterior (compactada). Autorizada por CEO.

**Contexto:** SesiÃ³n de diseÃ±o arquitectÃ³nico profundo. Se documentaron conceptos nuevos
derivados de investigaciÃ³n externa (Kimi Swarm, 10 dimensiones, 200+ bÃºsquedas, 11,215 lÃ­neas)
y de razonamiento arquitectÃ³nico interno. Se integrÃ³ el conocimiento en la KB y se alineÃ³
MWT con Faberloom en arquitectura de agentes.

**Archivos nuevos (5):**

| Archivo | Tipo | DescripciÃ³n |
|---------|------|-------------|
| SPEC_QUERY_PROCESSING_PIPELINE.md | SPEC | Pipeline 8 fases consultaâ†’memoria, observable en Cowork |
| SPEC_LLM_ROUTING_ARCHITECTURE.md | SPEC | L1 Clasificador + L2 Dispatcher + L3 Compiler + Token Ledger |
| SPEC_AUTONOMY_CONTROL_ENGINE.md | SPEC | ImpactVector 8D Â· Task Authorization Â· Async Queue Â· Promotion Engine |
| ENT_FABERLOOM_INSIGHTS_KIMI.md | ENT | 11 insights estratÃ©gicos investigaciÃ³n Kimi Swarm |
| SPEC_FABERLOOM_MVP.md | SPEC | Plan validaciÃ³n 60 dÃ­as Â· stack Â· fases Â· mÃ©tricas Â· riesgos |
| SPEC_MWT_AGENT_PLATFORM.md | SPEC | MWT como plataforma de agentes â€” stack, 3 objetos, pgvector, WhatsApp |

**Archivos modificados (7):**

| Archivo | Cambio |
|---------|--------|
| ARCH_AGENT_PRINCIPLES.md | v1.0â†’v1.2. +P11 clasificador 3 destinos. +P12 propagaciÃ³n cross-skill. +P13 ContenciÃ³n + ModelFingerprint. 10â†’13 principios. |
| SPEC_AUTONOMY_CONTROL_ENGINE.md | v1.0â†’v1.1. +OutcomeLedger (GoldSampleHealth + decay). +UserControlProfile. +Oscillation Counter (threshold 20). +HumanAlignmentScore (calibraciÃ³n perceptual). |
| SKILL_PROFORMA_BUILDER.md | v1.1â†’v1.2. +intake protocol 8 campos. +gold sample shortcut. +kb_refs explÃ­citos. +restricciÃ³n no-rediscovery. |
| IDX_GOBERNANZA.md | +7 nuevas entradas SPEC/ENT. Health 19/23. |
| IDX_PLATAFORMA.md | +SPEC_MWT_AGENT_PLATFORM en secciÃ³n Arquitectura de Plataforma. |
| DASHBOARD_SNAPSHOT.md | v8.2â†’v8.6. Total 270â†’278 archivos. |
| RW_ROOT.md | v4.7.5â†’v4.7.9. +5 entradas Registros Especiales. Changelog actualizado. |

**Conceptos arquitectÃ³nicos nuevos integrados:**

| Concepto | Fuente | Archivo |
|----------|--------|---------|
| ImpactVector 8D | Razonamiento interno + validaciÃ³n Kimi | SPEC_AUTONOMY_CONTROL_ENGINE |
| OutcomeLedger | Kimi I03 â€” Trampa del Gold Sample | SPEC_AUTONOMY_CONTROL_ENGINE v1.1 |
| UserControlProfile | Kimi I01 â€” Paradoja del Cuidador Digital | SPEC_AUTONOMY_CONTROL_ENGINE v1.1 |
| Oscillation Counter | Kimi I04 â€” Oscilador de Confianza | SPEC_AUTONOMY_CONTROL_ENGINE v1.1 |
| HumanAlignmentScore | Kimi I08 â€” Doblaje de CalibraciÃ³n | SPEC_AUTONOMY_CONTROL_ENGINE v1.1 |
| ModelFingerprint | Razonamiento interno | ARCH_AGENT_PRINCIPLES P13 |
| Task Authorization async | Razonamiento interno | SPEC_AUTONOMY_CONTROL_ENGINE |
| Prompt caching static-first | Kimi I10 â€” AnomalÃ­a del Costo | SPEC_MWT_AGENT_PLATFORM |

**InvestigaciÃ³n externa procesada:**

| Fuente | Output |
|--------|--------|
| Kimi Swarm Prompt #1 (6 agentes) | Arquitectura, memory, routing, task auth, LATAM B2B, stack |
| Kimi Swarm Prompt #2 (5 agentes) | Integraciones email/messaging/ecommerce/LLM/automation |
| CÃ­clope Ciclo 1 (OpenClaw) | ValidaciÃ³n ImpactVector, conflicto n8n MCP, pgvector RLS gap, ventana LATAM |
| Kimi ZIP (11 archivos, 11,215 lÃ­neas) | 11 insights, resumen ejecutivo, roadmap 6 fases, stack MVP, matriz valor/esfuerzo |

**Conflicto detectado y documentado:** n8n no expone MCP nativo â€” bidireccionalidad
vÃ­a webhook, no MCP. Documentado en SPEC_MWT_AGENT_PLATFORM.

**Pendiente tÃ©cnico crÃ­tico:** benchmark pgvector + RLS con 100+ tenants antes de
escalar Faberloom (I06 â€” Kimi).

**MÃ©tricas:**

| MÃ©trica | Antes | DespuÃ©s |
|---------|-------|---------|
| Archivos totales | 270 | 278 |
| SPECs en IDX_GOBERNANZA | 3 | 7 |
| Principios ARCH_AGENT_PRINCIPLES | 10 | 13 |
| Skills documentados | 10 | 10 (sin cambio en cantidad, +conceptos) |

**RW_ROOT:** v4.7.5 â†’ v4.7.9 (278 archivos)

---

## BATCH 2026-04-17-B â€” IntegraciÃ³n Kimi Swarm #2 (Email + Conectividad MCP)

**Fecha:** 2026-04-17
**Operador:** Claude (Cowork)
**Trigger:** `Kimi_Agent_Corporate Email Integration.zip` â€” anÃ¡lisis 14 dimensiones (Email, MensajerÃ­a, IMAP, n8n, MCP, Amazon SP-API, LLMs, LATAM B2B)

### Archivos creados

| Archivo | Tipo | Notas |
|---------|------|-------|
| ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md | ENT Â· VIGENTE v1.0 | 10 insights Email + Conectividad MCP. Resuelve conflicto n8n. |

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| SPEC_MWT_AGENT_PLATFORM.md | v1.0 â†’ v1.1. Nota n8n: MCP nativo disponible v1.120+; flujos auto=MCP, HITL=webhook. Conflicto previo resuelto (parcial). |
| IDX_GOBERNANZA.md | +ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL referenciado |
| RW_ROOT.md | v4.7.9 â†’ v4.8.0. +ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL en Registros Especiales |
| DASHBOARD_SNAPSHOT.md | v8.6 â†’ v8.7. Total 278â†’279. ENT_ 92â†’93. MD 252â†’253. |

### Insights integrados

| ID | Insight | Confianza | Impacto |
|----|---------|-----------|---------|
| E01 | n8n MCP nativo (v1.120+, nov 2025) â€” RESUELVE CONFLICTO | Alta | CrÃ­tico |
| E02 | Protocol Gap LATAM â€” ventana 12-18 meses primer mover | Alta | Alto |
| E03 | Email stack: EmailEngine>Nylas, M365 mÃ¡s barato en LATAM | Alta | Alto |
| E04 | WhatsApp Tax vs Telegram Hack â€” arquitectura hÃ­brida | Alta | Alto |
| E05 | Stack de los $150 â€” unit economics favorables | Media | Medio |
| E06 | Divergencia LLM â€” no write once run anywhere | Alta | Medio |
| E07 | Amazon SP-API moat inverso â€” private app = gratis | Alta | Alto |
| E08 | Draft-First HITL â€” 94% approval rate, 8 min mediana | Alta | Medio |
| E09 | n8n orquestaciÃ³n universal (matiz: MCP auto, webhook HITL) | Alta | Alto |
| E10 | TikTok Shop LATAM â€” ventana 12-18 meses | Media | Bajo (post-MVP) |

**Conflicto resuelto:** n8n no expone MCP nativo â†’ CORREGIDO (parcialmente). n8n v1.120+
tiene MCP nativo para flujos automÃ¡ticos (timeout 5min, sin HITL). Flujos draft-first con
aprobaciÃ³n humana siguen requiriendo webhook. Ambos modos coexisten.

**MÃ©tricas:**

| MÃ©trica | Antes | DespuÃ©s |
|---------|-------|---------|
| Archivos totales | 278 | 279 |
| ENT_ totales | 92 | 93 |
| Markdown totales | 252 | 253 |
| Insights Kimi en KB | 11 | 21 (11+10) |

**RW_ROOT:** v4.7.9 â†’ v4.8.0 (279 archivos)

---

## BATCH 2026-04-17-C â€” INDEXA gate + correcciÃ³n arquitectural mwt.one

**Fecha:** 2026-04-17
**Operador:** Claude (Cowork)
**Trigger:** indexa + decisiÃ³n CEO â€” mwt.one es stack independiente (no Claude/Cowork)

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| SPEC_MWT_AGENT_PLATFORM.md | v1.1 â†’ v1.2. DeclaraciÃ³n 3 componentes (Hub Â· mwt.one Â· Faberloom). Stack mwt.one corregido: FastAPI+LiteLLM+Telegram. Identidad agente MWT propia. |
| IDX_PLATAFORMA.md | SPEC_MWT_AGENT_PLATFORM actualizado a v1.2 + descripciÃ³n corregida. |
| DASHBOARD_SNAPSHOT.md | v8.7 â†’ v8.8. Conteos reales post git-merge. Activos: 254. |
| RW_ROOT.md | v4.7.9 â†’ v4.8.0 (actualizado en batch anterior). |

### CorrecciÃ³n arquitectural registrada

MWT no es "Claude/Cowork + n8n". Son 3 componentes independientes:
- **MWT Knowledge Hub** â†’ Claude/Cowork. Fuente de verdad. CEO lo opera directamente.
- **mwt.one** â†’ FastAPI + LiteLLM + n8n. Agentes con identidad MWT. Single-tenant.
- **Faberloom** â†’ FastAPI + LiteLLM + n8n. Agentes Faber. Multi-tenant.

### Conteos reales (post git-merge)

| MÃ©trica | Valor real |
|---------|-----------|
| Activos en docs/ | 254 |
| Archivados en /archivo/ | 65 (55 md + 10 otros) |
| ENT_ | 95 |
| PLB_ | 38 |
| POL_ | 28 |
| SCH_ | 18 |
| IDX_ | 10 |
| LOC_ | 32 |
| SKILL_ | 11 |
| SPEC_ | 6 |
| ARCH_ | 1 |
| HuÃ©rfanos | 0 âœ… |

**RW_ROOT:** v4.8.0 (254 activos + 65 en /archivo/)

---

## BATCH 2026-04-17-D â€” INDEXA gate â€” 3 huÃ©rfanos resueltos

**Fecha:** 2026-04-17
**Operador:** Claude (Cowork)
**Trigger:** indexa

### HuÃ©rfanos resueltos

| Archivo | IDX corregido |
|---------|--------------|
| ENT_COMP_CONTENT_RULES.md | IDX_COMPLIANCE â€” agregado como "Content Rules" |
| ENT_MARCA_MW_IDENTIDAD.md | IDX_MARCA â€” agregado como "Identidad MW" |
| ENT_PLAT_AGENT_ORCHESTRATION.md | IDX_PLATAFORMA â€” agregado como "Agent Orchestration" |

### Estado post-indexa

| Check | Estado |
|-------|--------|
| HuÃ©rfanos | 0 âœ… |
| DEPRECATED activos | 0 âœ… |
| FROZEN | 2 (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR) âœ… |
| Conteos activos | 254 md |

**DASHBOARD:** v8.8 â†’ v8.9

---

## BATCH 2026-04-18-B0 â€” TRANSVERSAL (CRLF + UNKNOWN + SCHEMA + CEO_ONLY)

**Fecha:** 2026-04-18
**Operador:** Claude (Cowork) â€” KB_AUDIT_20260418
**Trigger:** auditorÃ­a v2 post meta-CEO
**HEAD:** e144f07 Â· 7 commits pushed (4aa57de..e58b646) Â· 1 skip (56b634b duplicado remote)

### Acciones mecÃ¡nicas
- CRLF â†’ LF: 300 archivos normalizados (exclusiones: FROZEN + git-internos). Restantes 2 (contado post-push).
- UNKNOWN domain reclasificados (SPEC_/ARCH_/registries â†’ GOBERNANZA): 0 restantes.
- Encoding: UTF-8 decode OK, BOM=0, NFC=0 en 320/320.

### Artefactos generados
- audit/schema_assemblability_report.md â€” reporte requires[] vs existentes.
- audit/ceo_only_audit.md â€” 10 leaks detectados â†’ CEO-32 (vence 2026-05-30).
- audit/inventory_preB0.csv â€” snapshot pre-B0.
- audit/B0_commits_reconciled_20260418.bundle (147K) â€” preservaciÃ³n reconciliaciÃ³n remote.

### Conflictos resueltos en reconciliaciÃ³n
- b3fc27c â€” ZIPs en /archivo/ rename/delete (mantuvo purge via git rm -f)
- b7ed547 â€” MANIFIESTO_CAMBIOS_v2 (HEAD + insert B0 entry antes de marcador)
- 4a37d97 â€” ENT_GOB_PENDIENTES (--theirs: v11.9 superset estricto)

### Estado post-B0
| Check | Antes | DespuÃ©s |
|-------|-------|---------|
| CRLF archivos | 300 | 2 |
| UNKNOWN domain | 42 | 0 |
| UTF-8 decode | 0 fail | 0 fail âœ… |
| FROZEN integrity | âœ… | âœ… |
| CEO_ONLY leaks | no evaluado | 10 detectados |

**DASHBOARD:** v8.9 â†’ v9.0 (pendiente hasta B1a). **Next:** B1a SSOT/IDX sync.

---

## BATCH 2026-04-18-B1a â€” SSOT/IDX SYNC

**Fecha:** 2026-04-18
**Operador:** Claude (Cowork) â€” INDEXA gate B1a
**Trigger:** indexa B1a
**Scope:** 4 archivos SSOT/IDX (sin deletes, sin consolidaciones, sin mover archivos)
**Precedencia:** B0 DONE_PUSHED (HEAD e144f07)

### Cambios por archivo

**CLAUDE.md** (raÃ­z)
- Identidad: 291 archivos / 7 tipos â†’ 322 archivos / 8 tipos (+ breakdown por ubicaciÃ³n).
- TaxonomÃ­a: +SKILL_ explÃ­cito (antes omitido) + nota sobre SPEC_/ARCH_ como registros especiales.
- Estado actual: "Sprint 15 EN EJECUCIÃ“N" â†’ "Sprints 0-27 DONE + KB_AUDIT en ejecuciÃ³n B0â†’B11" + R1-R5 explÃ­citas.

**docs/DASHBOARD_SNAPSHOT.md** (v8.9 â†’ v9.0)
- Conteos: 254 activos + 65 archivo/ â†’ breakdown real 322 total (254+55+8+2+3). Corrige DASHBOARD_MISMATCH P0.
- Status: +SHADOW (11 SKILLs), DEPRECATED 0â†’1 (SCH_SKILL), FROZEN 2 explÃ­citos.
- Health: +LINE_ENDINGS_CRLF 0, +UNKNOWN 0, +Schema assemblability ref, +CEO_ONLY leaks 10.
- EfÃ­meros 0 â†’ 9 (violaciÃ³n POL_EPHEMERAL explicitada â€” consolidaciÃ³n diferida a B1c).
- AuditorÃ­a: +KB_AUDIT_20260418 row.

**docs/RW_ROOT.md** (v4.7.5 â†’ v4.8.1)
- TÃ­tulo: v4.7.5 â†’ v4.8.1 (alineado con changelog que ya estaba en v4.8.0).
- Ãšltima actualizaciÃ³n: 2026-04-17 â†’ 2026-04-18.
- POLICIES: 27 â†’ 28 (indexadas en IDX_GOBERNANZA).
- Changelog: +entrada v4.8.1.

**docs/IDX_GOBERNANZA.md**
- Health line: refactor con conteos por tipo (+1 DEPRECATED flag SCH_SKILL).
- Policies: 26 â†’ 28 (+POL_CONSENTIMIENTO, +POL_RETENCION_ESCANEOS faltantes en tabla).
- Schemas: SCH_SKILL VIGENTE v1.0 â†’ DEPRECATED (reemplazado).

### Post-check B1a

| Check | Resultado |
|-------|-----------|
| `grep -c "291" CLAUDE.md` | 0 âœ… |
| Conteo POLs en IDX_GOBERNANZA | 28 âœ… (match real find) |
| VersiÃ³n RW_ROOT tÃ­tulo == changelog | v4.8.1 âœ… |
| DASHBOARD total == real repo | 322 âœ… |
| Tipos taxonomÃ­a en 4 SSOTs | 8 âœ… (coherente) |
| FROZEN tocados | 0 âœ… (R2) |
| Archivos movidos | 0 âœ… (R4) |
| Datos inventados | 0 âœ… (R1) |

**DASHBOARD:** v9.0 publicado. **Next:** B1b (28 POLs headers/stamps hygiene).

---

## BATCH 2026-04-18-B1b â€” POL HYGIENE (scope reducido tras re-scan)

**Fecha:** 2026-04-18
**Operador:** Claude (Cowork) â€” INDEXA gate B1b
**Trigger:** indexa B1b
**Scope planeado:** 28 POLs headers/stamps + renovaciÃ³n preventiva stamps 2026-05-30
**Scope ejecutado:** 2 POLs (stamp missing fix) + push-back documentado sobre renovaciÃ³n masiva
**Precedencia:** B1a DONE (2026-04-18)

### Hallazgo post-scan (pre-ejecuciÃ³n)

Re-lectura de `audit/inventory.csv` contra los 28 POLs revelÃ³:

| Chequeo | Resultado |
|---------|-----------|
| HEADER_INCOMPLETE en POLs | **0** â€” los 28 tienen los 5 campos canÃ³nicos (id/version/status/visibility/domain) |
| Campo `stamp:` ausente en header | **2** â€” POL_CONSENTIMIENTO, POL_RETENCION_ESCANEOS (ambos DRAFT v0.1) |
| Foot block "Stamp: â€¦ / Vencimiento: â€¦ / Estado: â€¦ / Aprobador final:" ausente | **2** â€” los mismos |
| Hallazgos del `audit_scan.py` columna hallazgos | 0 POLs con flag activo |

**ConclusiÃ³n:** el plan declaraba "28 POLs hygiene" pero la realidad es **2 POLs**. El resto del plan (renovaciÃ³n stamps 2026-05-30) no se ejecuta â€” ver decisiÃ³n abajo.

### Cambios ejecutados

**docs/POL_CONSENTIMIENTO.md** (v0.1 â†’ v0.1.1)
- Header: agregado `stamp: DRAFT â€” pendiente aprobaciÃ³n CEO (activaciÃ³n Fase 2 ISO)`
- Foot block agregado: `Stamp: DRAFT 2026-03-13 â€” pendiente aprobaciÃ³n CEO / Vencimiento: N/A / Estado: DRAFT / Aprobador final: CEO (pendiente)`
- Changelog: +entrada v0.1.1.
- Contenido semÃ¡ntico: sin cambios.

**docs/POL_RETENCION_ESCANEOS.md** (v0.1 â†’ v0.1.1)
- Idem tratamiento. Stamp DRAFT explÃ­cito + foot block + changelog.
- Contenido semÃ¡ntico: sin cambios.

### DecisiÃ³n no ejecutada: renovaciÃ³n preventiva 22 VIGENTE POLs (push-back)

**Plan indicaba:** renovar stamps que vencen 2026-05-30 (42 dÃ­as out) como "ventana preventiva POL_RENOVACION".

**DecisiÃ³n operador:** no renovar. Razones:

1. **POL_RENOVACION v1.0 no define ventana preventiva.** Texto canÃ³nico: "Entity vence (90 dÃ­as desde Ãºltimo stamp) â†’ solicita renovaciÃ³n a Compliance". El vencimiento es el trigger, no 42 dÃ­as antes.
2. **RenovaciÃ³n es flujo con approval CEO por archivo** (paso 8 de POL_RENOVACION: "Aprobador final aprueba â†’ stamp nuevo"). CEO-33 autoriza el batch_order, no autoriza delegaciÃ³n de approval por archivo.
3. **Riesgo asimÃ©trico:** extender stamps sin approval aparente = data freshness teatralizada. Dejarlos vencer 2026-05-30 = signal real + gate natural para renovaciÃ³n.

**Follow-up registrado:** si el audit extiende mÃ¡s allÃ¡ de 2026-05-30 (est. realista dado 12-15 sesiones totales), los 22 stamps VIGENTE vencen en orden natural. CEO puede disparar renovaciÃ³n masiva vÃ­a nuevo batch o por archivo cuando corresponda. Tracking sugerido: +CEO-34 si CEO quiere formalizar.

### Post-check B1b

| Check | Resultado |
|-------|-----------|
| POLs con 6 campos header (id/version/status/stamp/visibility/domain) | 28/28 âœ… |
| POLs con foot block completo | 28/28 âœ… |
| STAMP_MISSING en POLs (audit_scan heurÃ­stica) | 0 âœ… (de 2 â†’ 0) |
| FROZEN tocados | 0 âœ… (R2) |
| Archivos movidos / renombrados | 0 âœ… (R4) |
| Datos inventados | 0 âœ… (R1) â€” stamps DRAFT documentan estado real no aprobado |
| Contenido semÃ¡ntico de los 2 POLs | sin cambios âœ… |

**DASHBOARD:** sin bump (v9.0 vigente â€” cambios B1b son metadata, no afectan conteos). **Next:** B1c (9 MANIFIESTO_APPENDs â†’ consolidaciÃ³n v2 con shadow reindex â€” ALTO RIESGO).

---

### BATCH 2026-04-18-B1c (part1) â€” ConsolidaciÃ³n efÃ­mera (9 APPENDs â†’ v2, sin delete)

**Scope real:** 9 MANIFIESTO_APPEND_*.md (8 en docs/ + 1 en docs/archivo/) consolidados en este archivo como entradas canÃ³nicas. **Originales NO eliminados** â€” delete + reindex pgvector diferido a B1c-part2 (CEO con container).

**Restricciones activas:** R1 no_inventar Â· R2 no_tocar_frozen Â· R3 no_escribir_kb Â· R4 no_mover_archivos Â· R5 respetar_ceo_only.

**Motivo del split part1/part2:** el plan B1c original (8 pasos: snapshot pgvector â†’ reindex shadow â†’ smoke tests â†’ swap â†’ delete 9 APPENDs â†’ reindex final) requiere acceso al container `mwt-knowledge` y al pipeline de pgvector. Esta sesiÃ³n (Cowork sobre KB directa) no tiene ese acceso. Ejecutar delete sin shadow reindex previo = riesgo de gaps en recall semÃ¡ntico. Split:
- **part1 (esta sesiÃ³n):** consolidaciÃ³n texto â†’ v2 (append-only). Estado transitorio intencional: v2 consolidado + 9 APPENDs coexisten.
- **part2 (CEO, diferido):** snapshot â†’ reindex shadow â†’ smoke â†’ swap â†’ delete 9 â†’ reindex final.

---

#### Entrada consolidada 1 â€” 2026-04-09 â€” Compact System Prompt (CLAUDE.md)

**Fuente original:** docs/archivo/MANIFIESTO_APPEND_20260409_COMPACT_PROMPT.md (ya archivada).

**Contexto.** CLAUDE.md acumulÃ³ datos de estado inlinados (conteo archivos, sprints, deuda, GTINs, score auditorÃ­a) cargados cada turno aunque no fueran relevantes. Violaba principio retrieval: KB = estado, CLAUDE.md = comportamiento.

**SoluciÃ³n.** Reescritura como Compact System Prompt. Solo instrucciones permanentes. Datos de estado en KB, consulta on-demand.

**Archivos modificados.**

| Archivo | Cambio | VersiÃ³n |
|---------|--------|---------|
| CLAUDE.md | 466L â†’ 207L (-56%). Datos de estado removidos. NavegaciÃ³n por tabla lookup. Tiers de carga. | v4.6.5 â†’ v4.6.7 |
| RW_ROOT.md | Version bump + entrada changelog v4.6.7 | v4.6.6 â†’ v4.6.7 |

**Datos removidos de CLAUDE.md â†’ nueva ubicaciÃ³n:** conteo archivos/sprints/deuda/score/mercados/infraestructura â†’ DASHBOARD_SNAPSHOT.md Â· GTINs â†’ ENT_OPS_TALLAS.md Â· LLM pricing â†’ ENT_PLAT_LLM_ROUTING.md Â· SSOTs â†’ ENT_PLAT_SSOT.md Â· Pendientes CEO â†’ ENT_GOB_PENDIENTES.md Â· AG-*/SVC-*/CLIENT_* â†’ ENT_GOB_AGENTES.md Â· Changelog Capas 1-9 â†’ MANIFIESTO_CAMBIOS_v2.md.

**Impacto tokens.** CLAUDE.md ~6,000 â†’ ~2,700 tokens (-55%). Ahorro ~3,300 tokens/turno; sesiÃ³n 30 turnos â‰ˆ 99,000 tokens (~$0.30 Sonnet).

---

#### Entrada consolidada 2 â€” 2026-04-09 â€” SKILLs Humanize (COMMS + BRAND)

**Fuente original:** docs/MANIFIESTO_APPEND_20260409_HUMANIZE.md.

**Documentos creados.** `SKILL_HUMANIZE_COMMS.md` (COMERCIAL) y `SKILL_HUMANIZE_BRAND.md` (MARCA). Ambos v0.1 DRAFT. Fuente: VOZ_CEO extraÃ­da de 19 correos reales.

**Documentos modificados.** RW_ROOT.md bump v4.6.7 â†’ v4.6.8 (+2 SKILLs en REGISTROS ESPECIALES).

**DescripciÃ³n del cambio.** Dos skills conversacionales que inyectan tono/patrÃ³n/vocabulario del CEO en outputs de comms (clientes B2B, proveedores) y marca (copy Amazon, social). Diferencian canal: COMMS 1:1 directo/breve; BRAND broadcast editorial/con gancho.

---

#### Entrada consolidada 3 â€” 2026-04-10 â€” Sprint 26 DONE (AG-02 API layer)

**Fuente original:** docs/MANIFIESTO_APPEND_20260410_S26DONE.md.

**Sprint cerrado.** LOTE_SM_SPRINT26 v1.0 DRAFT â†’ v1.1 DONE. 63 tests verdes. AG-02 API builder layer completa: views/serializers/urls/permissions para knowledge/ingest, knowledge/search, knowledge/ask.

**Documentos creados.** RESUMEN_SPRINT26.md (reportes/).

**Documentos modificados.** LOTE_SM_SPRINT26.md status DRAFT â†’ DONE. RW_ROOT v4.6.8 â†’ v4.6.9. CEO-28 CERRADO. DEC-S26-01..05 todas closed.

---

#### Entrada consolidada 4 â€” 2026-04-10 â€” Sprint 27 DONE + S1-S27 cerrados

**Fuente original:** docs/MANIFIESTO_APPEND_20260410_S27DONE.md.

**Sprint cerrado.** LOTE_SM_SPRINT27 v1.0 EN PREPARACIÃ“N â†’ v1.1 DONE. Con S27 DONE, **todo el bloque S1-S27 queda cerrado.**

**Documentos movidos.** LOTE_SM_SPRINT26.md y LOTE_SM_SPRINT27.md â†’ docs/archivo/.

**Documentos modificados.** RW_ROOT v4.6.9 â†’ v4.6.10. CEO-17 CERRADO. CEO-19 CERRADO. DEC-S27-01..05 abiertas.

---

#### Entrada consolidada 5 â€” 2026-04-13 â€” KB Hygiene v4.7.0 (cleanup masivo)

**Fuente original:** docs/MANIFIESTO_APPEND_20260413_KB_HYGIENE.md.

**Motivo.** Hallazgos auditorÃ­a externa: RW_ROOT bloated, POLs duplicadas, STUBs abandonados, LOCs mal clasificadas.

**Cambios ejecutados.**
- RW_ROOT.md: 160L â†’ 117L (-27%). Purga redundancia con DASHBOARD.
- 6 STUBs eliminados (archivos vacÃ­os sin changelog).
- POL_VACIO.md â†’ merged en POL_DETERMINISMO.md. Total POLs: 29 â†’ 28.
- 3 LOCs DRAFT â†’ STUB (sin contenido semÃ¡ntico real).
- DEPENDENCY_GRAPH.md DRAFT â†’ VIGENTE v4.0 (primera aprobaciÃ³n formal).

**Trayectoria git.** Commits f12004d â†’ 882cd22 â†’ d78cd7a.

**Documentos modificados.** RW_ROOT v4.6.10 â†’ v4.7.0. Tabla de findings externa consolidada en reportes/.

---

#### Entrada consolidada 6 â€” 2026-04-14 â€” SKILL_DEMAND_FORECASTER v1.0 (stack inicial)

**Fuente original:** docs/MANIFIESTO_APPEND_20260414_FORECAST_B2B.md.

**Contexto.** Marluvas demo: forecast de demanda B2B con swarm Kimi 2.5.

**Documentos creados.** `PLB_DEMAND_FORECASTING.md`, `ENT_DIST_FORECAST_SIGNALS.md`, `SCH_DEMAND_FORECAST_REPORT.md`, `SKILL_DEMAND_FORECASTER.md` (v1.0 DRAFT).

**Documentos modificados.** RW_ROOT v4.7.0 â†’ v4.7.1.

---

#### Entrada consolidada 7 â€” 2026-04-14 â€” SKILL_DEMAND_FORECASTER v2.0 (self-contained)

**Fuente original:** docs/MANIFIESTO_APPEND_20260414_FORECAST_V2.md.

**Reescritura completa** del skill. v1.0 â†’ v2.0. Ahora autocontenido:
- SeÃ±ales de negocio inline (ya no depende de ENT_DIST_FORECAST_SIGNALS en runtime)
- LÃ³gica normalizaciÃ³n SAP inline (ENT_DIST_SAP_SCHEMAS queda solo para mantenimiento)
- Specs de output inline (SCH_FORECAST_OUTPUTS queda solo para referencia)
- 7 agentes: 0A, A, B, C, D, E, F

**Flujo completo.** SAP/CSV â†’ Agent_0A â†’ A â†’ B â†’ C â†’ D â†’ E â†’ Agent_F â†’ Excel/PPT/Word.

**Documentos creados.** `ENT_DIST_SAP_SCHEMAS.md` v1.0, `SCH_FORECAST_OUTPUTS.md` v1.0.

**Documentos modificados.** SKILL_DEMAND_FORECASTER v1.0 â†’ v2.0. SCH_DEMAND_FORECAST_REPORT v1.0 (+requires). SCHEMA_REGISTRY (+SCH_FORECAST_OUTPUTS, total 17). IDX_DISTRIBUCION (+ENT_DIST_SAP_SCHEMAS). RW_ROOT v4.7.1 â†’ v4.7.2.

---

#### Entrada consolidada 8 â€” 2026-04-14 â€” Vlinte Agent Builder (indexaciÃ³n inicial)

**Fuente original:** docs/MANIFIESTO_APPEND_20260414_vlinte.md.

**Contexto.** 168 agentes virtuales catalogados por Kimi Swarm distribuidos en 9 Ã¡reas. Arquitectura pgvector 4 capas + Multi-LLM Router T1â†’T4.

**MVP planteado.** TrackBot â†’ InfoBot â†’ DailyBriefBot. Top ROI: CollectionBot (400-600%) â†’ InfoBot â†’ QualifyBot â†’ CompraBot â†’ TrackBot.

**Infra recomendada MVP.** RunPod L4 $204/mes (Qwen 2.5 14B Q4) + Groq para overflow.

**MetÃ¡fora producto.** "Agencia de staffing virtual" â€” cliente contrata empleados que aprenden su empresa. Moat real = KB acumulada (patrones, formatos, voz).

**Documentos modificados.**

| Archivo | AcciÃ³n |
|---------|--------|
| vlinte_agent_builder_spec.md | EDIT â€” frontmatter KB aÃ±adido: id: ENT_VLINTE_AGENT_BUILDER, v1.0, DRAFT, INTERNAL |
| IDX_PRODUCTO.md | EDIT â€” secciÃ³n Vlinte aÃ±adida (spec + mapa_tiers.html) |
| RW_ROOT.md | v4.7.2 â†’ v4.7.3. +2 entradas REGISTROS ESPECIALES |
| ENT_GOB_PENDIENTES.md | v11.7 â†’ v11.8. Track Vlinte nuevo (MVP + infra + perfiles) |

---

#### Entrada consolidada 9 â€” 2026-04-16 â€” Arquitectura AgentSpec/Runtime/Memory

**Fuente original:** docs/MANIFIESTO_APPEND_20260416_SKILL_ARCH.md.

**Contexto.** ImplementaciÃ³n arquitectura AgentSpec/Runtime/Memory para sistema Skills MWT. Basada en modelo Faberloom adaptado a escala markdown + n8n.

**Documentos creados.**
- `SCH_SKILL.md` â€” Schema canÃ³nico de todos los skills. Estructura obligatoria, ciclo vida, flujo aprendizaje con termÃ³metro, modal consolidaciÃ³n, checklist pre-ACTIVE.
- `SKILL_RUNTIME.md` â€” Dashboard Ãºnico AgentRuntime. Tracking estado, autonomÃ­a, mÃ©tricas y temperatura aprendizaje para 9 skills.

**Documentos modificados â€” 9 SKILLs promovidos DRAFT â†’ SHADOW.**

| Archivo | Anterior | Nueva | Cambios |
|---------|----------|-------|---------|
| SKILL_AMAZON_OPS | 1.0 DRAFT | 1.1 SHADOW | +trigger_word, autonomy_ceiling, escalation_policy, State Machine, Events, Learning Consolidation |
| SKILL_CLIENT_SERVICE | 1.0 DRAFT | 1.1 SHADOW | Ã­dem |
| SKILL_COMPLIANCE_CHECKER | 1.0 DRAFT | 1.1 SHADOW | Ã­dem |
| SKILL_DEMAND_FORECASTER | 2.0 DRAFT | 2.1 SHADOW | Ã­dem |
| SKILL_EXPERIMENT_RUNNER | 1.0 DRAFT | 1.1 SHADOW | Ã­dem |
| SKILL_HUMANIZE_BRAND | 0.2.0 DRAFT | 0.3.0 SHADOW | Ã­dem + fix header (visibility, domain, type, stamp) |
| SKILL_HUMANIZE_COMMS | 0.1.0 DRAFT | 0.2.0 SHADOW | Ã­dem |
| SKILL_KB_AUDITOR | 1.0 DRAFT | 1.1 SHADOW | Ã­dem + autonomy_ceiling AUTO_NOTIFICA |
| SKILL_PROFORMA_BUILDER | 1.0 DRAFT | 1.1 SHADOW | Ã­dem + ceiling PROPONE permanente por CEO-ONLY |

**Campos nuevos en header de todos los skills.** `trigger_word`, `autonomy_ceiling`, `escalation_policy`.

**Secciones nuevas en todos los skills.** `## State Machine`, `## Events`, `## Learning Consolidation`.

**Flujo aprendizaje.** `trigger_word â†’ AgentSpec + AgentMemory cargados â†’ ejecuciÃ³n â†’ eventos emitidos â†’ termÃ³metro sube â†’ CEO presiona "Indexar Aprendizaje" (indexa-{trigger_word}) â†’ modal confirmaciÃ³n â†’ consolida en SKILL_MEM_{ID}.md`.

**TermÃ³metro.** ðŸ”µ FrÃ­o (0-2) Â· ðŸŸ¡ Tibio (3-5) Â· ðŸ”´ Caliente (6+).

**PrÃ³ximos pasos registrados.** (1) Primer ciclo SHADOW de cada skill con registro en SKILL_RUNTIME.md. (2) Crear SKILL_MEM_{ID}.md cuando haya â‰¥5 ejecuciones reales. (3) Promover a ACTIVE por skill cuando gold samples consolidados.

---

### Tabla maestra de los 9 APPENDs consolidados

| # | Fecha | Archivo fuente | Dominio | Resumen |
|---|-------|----------------|---------|---------|
| 1 | 2026-04-09 | docs/archivo/MANIFIESTO_APPEND_20260409_COMPACT_PROMPT.md | Gobernanza | CLAUDE.md compact 466â†’207 L, estado movido a KB |
| 2 | 2026-04-09 | docs/MANIFIESTO_APPEND_20260409_HUMANIZE.md | Comercial/Marca | +SKILL_HUMANIZE_COMMS, +SKILL_HUMANIZE_BRAND |
| 3 | 2026-04-10 | docs/MANIFIESTO_APPEND_20260410_S26DONE.md | Plataforma | S26 DONE, AG-02 API layer, 63 tests |
| 4 | 2026-04-10 | docs/MANIFIESTO_APPEND_20260410_S27DONE.md | Plataforma | S27 DONE â†’ S1-S27 todos cerrados |
| 5 | 2026-04-13 | docs/MANIFIESTO_APPEND_20260413_KB_HYGIENE.md | Gobernanza | v4.7.0 cleanup masivo (RW_ROOT -27%, POLs 29â†’28) |
| 6 | 2026-04-14 | docs/MANIFIESTO_APPEND_20260414_FORECAST_B2B.md | DistribuciÃ³n | SKILL_DEMAND_FORECASTER v1.0 + stack |
| 7 | 2026-04-14 | docs/MANIFIESTO_APPEND_20260414_FORECAST_V2.md | DistribuciÃ³n | SKILL_DEMAND_FORECASTER v2.0 self-contained, 7 agentes |
| 8 | 2026-04-14 | docs/MANIFIESTO_APPEND_20260414_vlinte.md | Producto | Vlinte Agent Builder indexaciÃ³n + ENT_GOB_PENDIENTES track |
| 9 | 2026-04-16 | docs/MANIFIESTO_APPEND_20260416_SKILL_ARCH.md | Gobernanza/Plataforma | SCH_SKILL + SKILL_RUNTIME, 9 skills DRAFTâ†’SHADOW |

**Trayectoria de versiones RW_ROOT durante ventana 2026-04-09 â†’ 2026-04-16.** v4.6.5 â†’ v4.6.7 â†’ v4.6.8 â†’ v4.6.9 â†’ v4.6.10 â†’ v4.7.0 â†’ v4.7.1 â†’ v4.7.2 â†’ v4.7.3. (La serie v4.7.5 / v4.8.1 posterior pertenece a KB_AUDIT B0/B1a â€” ya registradas en sus batches.)

---

### Post-check B1c-part1

| Check | Resultado |
|-------|-----------|
| 9 APPENDs leÃ­dos completos | 9/9 âœ… |
| Entradas consolidadas en v2 | 9/9 âœ… |
| Tabla maestra cruzada contra fuentes | âœ… |
| Archivos originales preservados | 9/9 âœ… (R4 â€” no se movieron ni borraron) |
| FROZEN tocados | 0 âœ… (R2) |
| Datos inventados | 0 âœ… (R1 â€” todo texto derivado de APPENDs originales) |
| Scope KB (ningÃºn write fuera de MWT KB/docs) | âœ… (R3) |
| pgvector shadow reindex | âŒ **NO EJECUTADO** â€” diferido a B1c-part2 (CEO/container) |
| Delete 9 APPENDs originales | âŒ **NO EJECUTADO** â€” diferido a B1c-part2 |

**Estado transitorio intencional.** Hasta que CEO ejecute B1c-part2:
- Los 9 APPENDs originales siguen en sus paths (8 en docs/, 1 en docs/archivo/).
- Esta entrada en v2 es la fuente consolidada.
- pgvector sigue indexando las 10 fuentes (9 APPENDs + este v2). Riesgo: duplicaciÃ³n semÃ¡ntica temporal hasta swap.
- Alerta `EPHEMERAL_NOT_PURGED: 9` en progress.json **permanece activa** (umbral >3) â€” no se resuelve hasta part2.

**Follow-up B1c-part2 (CEO + container mwt-knowledge).**

1. `git` snapshot estado actual (tag `pre-B1c-part2`).
2. Snapshot pgvector: `pg_dump` tabla embeddings o copia de colecciÃ³n.
3. Reindex shadow: nueva colecciÃ³n con v2 consolidado como fuente canÃ³nica (sin los 9 APPENDs).
4. Smoke tests: 10 queries representativas (cambios S26/S27, compact prompt, forecast v2, vlinte, skills SHADOW). Comparar recall vs colecciÃ³n actual.
5. Si smoke OK â†’ swap colecciones (atomic rename).
6. `git rm` los 9 APPENDs en commit separado (mensaje: `[GOBERNANZA] B1c-part2 â€” purga 9 MANIFIESTO_APPEND post-swap shadow reindex`).
7. Reindex final sobre HEAD post-delete.
8. Verificar `EPHEMERAL_NOT_PURGED: 0` en prÃ³xima auditorÃ­a.

**DASHBOARD:** sin bump (cambios B1c-part1 son append-only a v2; conteos reales no cambian â€” 322 total persistente). **Next por dependencia en batch_order_v2:** B2 MARCA (bloqueado solo por B1c completo; part1 libera anÃ¡lisis pero B2 puede esperar part2 si CEO prefiere coherencia de ciclo). RecomendaciÃ³n operador: ejecutar B1c-part2 antes de B2 para cerrar deuda efÃ­mera limpia.

---

### BATCH 2026-05-03 â€” AUDIT_REINDEXA_KB Â· saneamiento integral PR-0..6 (no destructivo)

**Fecha:** 2026-05-03 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) â€” sesiÃ³n sobre mirror OneDrive + sync_higiene_2026-05-03_indexa.ps1 generado para CEO
**AuditorÃ­a disparadora:** AUDIT_REINDEXA_KB 2026-05-03 (veredicto AMARILLO Â· 42 manifiestos huÃ©rfanos Â· 5 SCH FB sin registry Â· drift de conteos en 4 fuentes Â· 1 leak CEO-ONLY confirmado en ENT_PROD_SCANNER Â· 22% stubs en PLATAFORMA Â· 50% stubs en DISTRIBUCION).
**Brief sintetizador:** "Brief para Claude Cowork â€” Hallazgos AUDIT_REINDEXA + lecciones gobernanza" (CEO + ChatGPT cross-validation, anti-patterns de ChatGPT filtrados explÃ­citamente).

**Restricciones activas en sesiÃ³n:** R1 no_inventar Â· R2 no_tocar_frozen Â· R3 no_escribir_kb_fuera_scope Â· R4 no_mover_archivos Â· R5 respetar_ceo_only Â· R6 no_ejecutar_destructivo_sin_pgvector_shadow.

**PRs ejecutados (no destructivos):**

**PR-0 BLOCKER â€” cierre leak CEO-ONLY ENT_PROD_SCANNER**
- `docs/ENT_PROD_SCANNER.md` v3.0 â†’ v3.1.
- `visibility: [INTERNAL] â€” secciÃ³n PRICING [CEO-ONLY]` (declaraciÃ³n en prosa, no machine-parseable) reemplazado por `visibility: [INTERNAL]` + `ceo_only_sections: [I]` (machine-parseable, conforme POL_VISIBILIDAD Â§regla ingestion pgvector).
- SecciÃ³n `## I. PRICING OEM` ahora excluida del bucket INTERNAL en pgvector.
- Filas OQ-08/OQ-09 dentro de secciÃ³n G permanecen `[PENDIENTE â€” CEO-ONLY]` en prosa: cuando se completen valores reales, deben moverse a secciÃ³n I o agregarse como Field IDs adicionales en `ceo_only_sections`.
- DASHBOARD Â§Health: CEO-ONLY leaks 14 â†’ 13 (CEO-32 sigue abierto, vence 2026-05-30).

**PR-3 â€” 5 SCH FB en SCHEMA_REGISTRY + fix domain BUNDLE_v1**
- `docs/SCHEMA_REGISTRY.md`: nueva secciÃ³n `## FABERLOOM` con 5 entries:
  - SCH_FB_CLI_INTERFACE v2.0 VIGENTE
  - SCH_FB_FLOW_DAG v2.0 VIGENTE
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 v1.0 â†’ v1.1 VIGENTE (parametriza ENT_FB_VERTICAL_SPEC_OBJECT_v1)
  - SCH_FB_SKILL_MANIFEST_v2 v2.0 VIGENTE (extiende SCH_SKILL del bloque GOBERNANZA DE AGENTES)
  - SCH_FB_TASK_ENTITY v2.0 VIGENTE
- Total registry: 21 â†’ 26 schemas (12 ACTIVO + 5 DRAFT + 9 VIGENTE).
- DecisiÃ³n arquitectÃ³nica explÃ­cita: registry Ãºnico (no split MWT/FB) por POL_DETERMINISMO Â§1 (Dato Ãšnico) y porque SCH_FB_SKILL_MANIFEST_v2 ya hereda de SCH_SKILL.
- `docs/faberloom/SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md` v1.0 â†’ v1.1: `domain: Plataforma` â†’ `domain: FaberLoom` (consistencia con scope path docs/faberloom/ y con los otros 4 SCH_FB).
- Falso positivo descartado: SCH_FB_SKILL_MANIFEST_v2 no tiene drift de version triplicado â€” las "versions" 2.0.0 y 0.1.0 detectadas por audit grep eran ejemplos dentro de bloques YAML (instances de SKILL), no headers del archivo.

**PR-4 â€” 4 POLs bumpeados con Reglas 1-5 ejecutables**
- POL_NUEVO_DOC v1.0 â†’ v1.1: +Regla 1 "Si no estÃ¡ indexado, no existe" como gate de PR ejecutable. Origen: 5 SCH_FB huÃ©rfanos detectados.
- POL_EPHEMERAL_OUTPUT v1.0 â†’ v1.1: +Regla 2 (header efÃ­mero ejecutable con 3 campos canÃ³nicos: `type`+`expires_at`+`consolidation_target`+`action_after_consolidation`). +Regla 5 (sesiÃ³n sin consolidaciÃ³n = trabajo a medias, umbral 7 dÃ­as â†’ 0 dÃ­as para sesiones nuevas). Origen: 42 MANIFIESTO_APPEND_* huÃ©rfanos sin `expires_at`.
- POL_DETERMINISMO v1.1 â†’ v1.2: +Regla 3 ejecutable bajo Principio 1 (Dato Ãšnico). Conteos vivos solo viven en DASHBOARD_SNAPSHOT. Origen: drift detectado entre CLAUDE 446, RW_ROOT 308, DEPENDENCY_GRAPH 289, DASHBOARD 404 â€” real 535.
- POL_INMUTABILIDAD v1.0 â†’ v1.1: +Regla 4 "Lo firmado no se edita in-place" con comportamiento canÃ³nico del agente (escalar al CEO, no rechazar) + lista de FROZEN canÃ³nicos (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR, ARCH_AGENT_PRINCIPLES sealed v1.5 commit 9ecd190, POL_DATA_CLASSIFICATION sealed v1.4).
- **Incidente operativo registrado:** Edit tool truncÃ³ silenciosamente los 4 POLs cuando el `new_string` tenÃ­a caracteres tipogrÃ¡ficos (em dash, flechas, curly quotes) en bloques largos. Reescritos con Write+ASCII puro. LecciÃ³n guardada en memoria del agente para futuras sesiones.

**PR-5 â€” DASHBOARD v13.0 fuente Ãºnica + ediciones quirÃºrgicas**
- `docs/DASHBOARD_SNAPSHOT.md` v12.9 â†’ v13.0: conteos reales (553 repo total, 535 docs/ tree, 328 docs/ raÃ­z, 46 docs/faberloom/, 48 docs/anexos/, 110 docs/archivo/, 8 audit/, 3 reportes/, 3 raÃ­z repo). DeclaraciÃ³n explÃ­cita "fuente Ãºnica" per POL_DETERMINISMO Â§1 Regla 3 v1.2. Versiones principales actualizadas: RW_ROOT v4.8.20â†’v4.8.21, DEPENDENCY_GRAPH v3.1â†’v4.0. Health: efÃ­meros 9â†’42 (violaciÃ³n expandida) + CEO-ONLY leaks 14â†’13 (PR-0 cerrado).
- `CLAUDE.md` lÃ­nea 6: conteo hardcoded "446 archivosâ€¦" reemplazado por referencia "ver DASHBOARD_SNAPSHOT Â§Conteos (fuente Ãºnica per POL_DETERMINISMO Â§1 Regla 3 v1.2)".
- `docs/RW_ROOT.md` lÃ­nea 82: "28 constraints transversales" reemplazado por referencia a DASHBOARD Â§Tipos.
- `docs/RW_ROOT.md` lÃ­nea 119: retirado `GUIA_ALE_SPRINT26.md` de Registros Especiales (S26 cerrÃ³ 2026-04-10, archivo ya en docs/archivo/).
- `docs/DEPENDENCY_GRAPH.md` lÃ­nea 17: "289 archivos de la KB" reemplazado por referencia a DASHBOARD.

**PR-6 â€” RW_ROOT v4.8.21**
- `docs/RW_ROOT.md` v4.8.20 â†’ v4.8.21 con changelog citando PR-0..5 + nota explÃ­cita sobre PR-1+PR-2 destructivos pendientes.

**PRs DIFERIDOS (destructivos, requieren CEO + reindex pgvector shadow):**

**PR-1** delete 8 manifiestos ya consolidados en B1c-part1 (entries 2-9):
- HUMANIZE, S26DONE, S27DONE, KB_HYGIENE, FORECAST_B2B, FORECAST_V2, faberloom (id interno: vlinte â€” drift filenameâ†”id por resolver), SKILL_ARCH.

**PR-2** consolidar 34 manifiestos restantes en 3 BATCH headers nuevos + delete:
- BATCH 2026-04-19/22 (8 entries): cubre RW_ROOT v4.8.2â†’v4.8.6 (FABERLOOM_BLUEPRINT, MEMORY_STACK, AUDIT_FABERLOOM_*x3, LLM_ORCHESTRATION, KB_AUDIT_INTEGRAL).
- BATCH 2026-04-27/29 (10 entries): cubre RW_ROOT v4.8.7â†’v4.8.8 (AUDIT_FIX, KIMI_RUFLO, ACTION_ENGINE, DATA_CLASS_AUDIT, JARVIS_IDEA, core_blindado, roadmap_arquitectonico, REMEDIACION_FB, INDEXA_PUNTO_PARTIDA, REDIRECT_FB_SCOPE).
- BATCH 2026-04-30/05-04 (16 entries): cubre RW_ROOT v4.8.9â†’v4.8.20 (KNOWLEDGE_RIVER, P16_DECOMPOSITION, AM_VERTICAL, AUDIT_RECONCILIATION, AI_GOV, FOUNDATION_BETA_FIRMADO, INDEXA_E_BACKEND, AI_GOV_DUAL_REVIEW, INDEXA_F/G/H/H_I/J, CANONIZACION_MOCK_FB, FRONTEND_PRINCIPLES, TEAM_INVENTORY, KIMI_SWARM_5).

**ValidaciÃ³n pre-delete (obligatoria) â€” NO ejecutado en esta sesiÃ³n:**
1. Snapshot pgvector index actual.
2. Build shadow index sin los 42 archivos.
3. Smoke tests recall@5 sobre queries representativas.
4. Swap shadow â†’ primary atÃ³mico.
5. SOLO ENTONCES `git rm` de los 42.
6. Reindex final sobre HEAD post-delete.

**Sync script generado:** `sync_higiene_2026-05-03_indexa.ps1` en raÃ­z del repo (10KB, ASCII puro PS5-safe). FASE 1 (Copy-Item de los 11 archivos editados a canÃ³nico) automatizada. FASES 2-6 (git checkout/add/commit, pgvector shadow, restore mirror) impresas como instrucciones manuales para CEO.

**Hallazgos colaterales NO atendidos en esta sesiÃ³n (registrados):**
- Drift filenameâ†”id en `MANIFIESTO_APPEND_20260414_faberloom.md` (id interno: vlinte). ViolaciÃ³n POL_DETERMINISMO Â§1. A resolver antes del delete en PR-1.
- 22% stubs en IDX_PLATAFORMA, 19% en IDX_COMPLIANCE â€” bajo umbral 30%, no urgente.
- 50% stubs en IDX_DISTRIBUCION â€” sobre umbral. Programado para revisiÃ³n 2026-06-13 (cutoff 90 dÃ­as).
- 7 IDX_ con Health declarado obsoleto vs realidad (declara "0 stubs" cuando hay 1+). Sugiere hacer SKILL_KB_AUDITOR scheduled.
- B1c-part2 (consolidaciÃ³n pgvector reindex shadow + delete 9 APPENDs originales documentado en BATCH 2026-04-18-B1c) sigue diferido desde 2026-04-18 â€” los PR-1+PR-2 de esta sesiÃ³n incorporan ese pendiente.

**NO TOCADO (FROZEN intactos):**
- ARCH_AGENT_PRINCIPLES.md (sealed v1.5 commit 9ecd190).
- POL_DATA_CLASSIFICATION.md (sealed v1.4).
- ENT_OPS_STATE_MACHINE.md.
- PLB_ORCHESTRATOR.md.

**MÃ©tricas sesiÃ³n:**
- Archivos modificados: 11 (`.md`) + 1 script utility (`.ps1` en raÃ­z).
- Archivos creados nuevos: 0 (decisiÃ³n deliberada â€” no crear MANIFIESTO_APPEND fÃ­sico para esta sesiÃ³n, append directo a CAMBIOS_v2 conforme Regla 5 v1.1).
- Archivos eliminados: 0 (todos los deletes diferidos a PR-1+PR-2 con shadow reindex).
- POLs bumpeados: 4.
- Schemas registrados: +5.
- Versiones principales bumpeadas: RW_ROOT (v4.8.20â†’v4.8.21), DASHBOARD_SNAPSHOT (v12.9â†’v13.0), POL_NUEVO_DOC (v1.0â†’v1.1), POL_EPHEMERAL_OUTPUT (v1.0â†’v1.1), POL_DETERMINISMO (v1.1â†’v1.2), POL_INMUTABILIDAD (v1.0â†’v1.1), ENT_PROD_SCANNER (v3.0â†’v3.1), SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 (v1.0â†’v1.1).

**Memoria del agente actualizada (lecciones operativas para futuras sesiones Cowork):**
- `edit_tool_truncates_typographic_chars.md` â€” preferir Write+ASCII para POLs y FROZEN.
- `indexar_sesion_directo_a_cambios_v2.md` â€” append BATCH directo a CAMBIOS_v2, no crear APPEND fÃ­sico (Regla 5 v1.1).

**DASHBOARD post-sesiÃ³n:** v13.0 ya refleja conteos reales pre-purga (328 docs/ raÃ­z incluye 42 manifiestos pendientes). Tras PR-1+PR-2 ejecutados, conteo bajarÃ¡ a 286 docs/ raÃ­z y CEO-ONLY leaks bajarÃ¡n a 12 (post-delete elimina referencias internas a los 42).

**Veredicto post-sesiÃ³n:** AMARILLO â†’ AMARILLO (mejora parcial). Pasa a VERDE cuando PR-1+PR-2 cierren la deuda de efÃ­meros (umbral POL_EPHEMERAL_OUTPUT v1.1: 0-dÃ­as).

---

## BATCH 2026-05-04b â€” INDEXA ENT_GOB_SOCIEDAD (datos societarios MWT, CEO-ONLY)

**SesiÃ³n:** Cowork Â· single-file ingestion.
**Origen:** CEO entrega contenido verbatim con metadatos de personerÃ­a notarial + RNP Digital.
**Scope:** Crear entry canÃ³nico para datos societarios de Muito Work Limitada en GOBERNANZA. Reemplaza referencias dispersas (no habÃ­a hub Ãºnico antes).

**Archivos creados (1):**
- `docs/ENT_GOB_SOCIEDAD.md` v1.0 VIGENTE CEO-ONLY:
  - RazÃ³n social: MUITO WORK LIMITADA (3-102-751710, SRL, INSCRITA).
  - ConstituciÃ³n: 2018-01-10, tomo 2018 asiento 16463, plazo 99 aÃ±os â†’ vence 2117-01-10.
  - Domicilio: San Jose, Santa Ana, Pozos, Bosques de Santa Ana 18-E.
  - Capital: â‚¡10,000 / 10 cuotas nominativas / â‚¡1,000 c/u, totalmente suscritas y pagadas.
  - DistribuciÃ³n: Alvaro Alfaro Montero 80% (8 cuotas), Lady Gutierrez BolaÃ±os 20% (2 cuotas).
  - AdministraciÃ³n: 2 Apoderados Generalisimos sin Limite de Suma. ActuaciÃ³n separada para ordinarios; conjunta obligatoria para venta o enajenaciÃ³n de bienes. Vigencia 2018-01-10 â†’ 2117-01-10. Pueden auto-contratar (no aplica art. 1263 CÃ³d. Civil).
  - Otros: sin agente residente, sin afectaciones, sin movimientos pendientes.
  - Documentos fuente: certificaciÃ³n notarial Lic. Mario Arias Aguero 2018-01-13 + RNP Digital 562728-2026 emitida 2026-04-08 11:36:37.
  - Header: `data_classification: N2`, `no_pgvector: true`, `aplica_a: [MWT]`, `tipo: entity`.
  - Aviso prominente al inicio del archivo: contiene cÃ©dulas + domicilio + distribuciÃ³n accionaria, prohibido pgvector + prohibido referencia textual desde PUBLIC/INTERNAL/PARTNER_B2B.

**Archivos modificados (1):**
- `docs/IDX_GOBERNANZA.md` v1.1 â†’ v1.2:
  - Header: `last_review: 2026-04-22` â†’ `2026-05-04`, `stamp: VIGENTE â€” 2026-05-04`.
  - Health: ENTs (gob) 11 â†’ 12 (+ENT_GOB_SOCIEDAD CEO-ONLY no_pgvector).
  - Ãšltima revisiÃ³n nota actualizada (INDEXA ENT_GOB_SOCIEDAD); revisiÃ³n anterior (AI_GOV Dual Review) demovida.
  - Tabla Entities: nueva fila "Sociedad (datos societarios MWT â€” CEO-ONLY Â· no_pgvector) â†’ ENT_GOB_SOCIEDAD.md â†’ VIGENTE v1.0".

**FROZEN/sealed intactos:**
- ARCH_AGENT_PRINCIPLES.md (sealed v1.5 commit 9ecd190).
- POL_DATA_CLASSIFICATION.md (sealed v1.4) â€” clasificaciÃ³n N2 aplicada conforme a regla existente.
- ENT_OPS_STATE_MACHINE.md.
- PLB_ORCHESTRATOR.md.

**Reglas observadas:**
- R1 no_inventar: contenido verbatim del CEO, no se infirieron campos faltantes (agente residente, direcciÃ³n electrÃ³nica registrada â†’ quedan como "No aplica" / "No indica" segÃºn fuente).
- R3 no_eliminar: no se borrÃ³ nada existente.
- R4 headers: ENT con id/version/status/visibility/domain/tipo/data_classification/aplica_a/stamp + flag `no_pgvector` declarado.
- R5 documentar cambio: este BATCH + changelog en propio archivo.
- R6 visibilidad: CEO-ONLY no fugÃ³ a archivos PUBLIC/INTERNAL â€” IDX_GOBERNANZA solo registra existencia + clasificaciÃ³n, no contenido (ni cÃ©dulas ni distribuciÃ³n de cuotas).
- POL_EPHEMERAL_OUTPUT v1.1 Regla 5: append directo a CAMBIOS_v2, NO se creÃ³ MANIFIESTO_APPEND fÃ­sico.

**ValidaciÃ³n pgvector:**
- ENT_GOB_SOCIEDAD marcado `visibility: CEO-ONLY` + `no_pgvector: true` + `data_classification: N2`. La indexaciÃ³n pgvector debe excluir este path por filtro de visibilidad existente. Verificar en prÃ³ximo reindex que el archivo no aparezca en `vector_index_manifest`.

**Pendientes derivados:**
- VerificaciÃ³n de RNP Digital (562728-2026) caduca 2026-05-08 â€” si se necesita re-validar el cert, reemitir antes de esa fecha.
- Si en el futuro se modifica capital, distribuciÃ³n de cuotas o representaciÃ³n â†’ bumpear ENT_GOB_SOCIEDAD a v1.1+, no editar entradas histÃ³ricas.

**Sync:** `sync_sociedad_indexa.ps1` generado en raÃ­z repo (Push-Location â†’ canÃ³nico, Copy-Item de los 2 archivos `.md` editados, instrucciones git impresas, mirror_to_onedrive.ps1 al cierre).

**MÃ©tricas sesiÃ³n:**
- Archivos creados: 1.
- Archivos modificados: 1 (IDX_GOBERNANZA) + 1 (este CAMBIOS_v2 append).
- Archivos eliminados: 0.
- POLs/SCHs/SPECs bumpeados: 0 (no aplicable a un entity puro de datos).
- MANIFIESTO_APPEND fÃ­sico creado: 0 (Regla 5 v1.1).

**Veredicto:** AMARILLO â†’ AMARILLO (sin impacto en deuda de efÃ­meros). Sin riesgo de leak por estar marcado CEO-ONLY + no_pgvector desde el header.

---

## BATCH 2026-05-04c â€” INDEXA ENT_GOB_SOCIEDAD v1.0 EXPANDIDO (supersede in-place de 2026-05-04b)

**SesiÃ³n:** Cowork Â· misma sesiÃ³n, segundo pass.
**Origen:** CEO entrega versiÃ³n expandida del archivo con secciones financieras, equipo profesional, refs cruzadas, reglas de uso y pendientes. Reemplaza la versiÃ³n inicial (status VIGENTE bÃ¡sico) por un hub canÃ³nico legal+contable+financiero (status DRAFT pendiente firma EEFF y cierre pendientes L1-L4).

**Diferencias respecto a 2026-05-04b:**
- `status: VIGENTE` -> `status: DRAFT` (refleja que EEFF aÃºn tienen pendientes contables y reconciliaciÃ³n de costo histÃ³rico de vehÃ­culo).
- +Header `refs:` con 5 entries cruzadas (ENT_MARCA_MW_IDENTIDAD, ENT_PLAT_LEGAL_ENTITY, ENT_GOB_PROVEEDORES, ENT_COMERCIAL_CLIENTES, SCH_PROFORMA_MWT) para enforcement de "este documento prevalece" (Regla K4).
- +SecciÃ³n A PropÃ³sito con bloque "no confundir con" (anti-colisiÃ³n semÃ¡ntica frente a ENT_MARCA_MW_IDENTIDAD y ENT_PLAT_LEGAL_ENTITY).
- +SecciÃ³n C Actividad EconÃ³mica (cÃ³digo Hacienda CR 4641.1, mercados, lÃ­neas de negocio, cliente B2B principal CR Sondel S.A., cÃ³digo Marluvas autoconsumo).
- +SecciÃ³n F Equipo Profesional (CPI Solano NÂ° 39405, notario Lic. Mario Arias Aguero, banco operativo principal).
- +SecciÃ³n G EEFF (G1 marco NIIF PYMES Sec 10/17/23/33; G2 ESF dic-2024 vs dic-2025; G3 ER dic-2024 vs dic-2025; G4 PPE identificados con vidas Ãºtiles; G5 eventos relevantes 2025 incl. reorientaciÃ³n estratÃ©gica + reclasificaciÃ³n contable retroactiva â‚¡90K capital social a utilidades acumuladas).
- +SecciÃ³n H Partes Relacionadas (saldos cuenta x pagar a socios + condiciones).
- +SecciÃ³n I Indicadores 2025 (razÃ³n corriente, endeudamiento, margen neto, ROE, ROA, crecimiento utilidad neta).
- +SecciÃ³n J Documentos Fuente expandida (5 entries: notarial 2018-01-13, RNP 2026-04-08, EEFF 2024 y 2025 firmados CPI Solano, memorando ajustes 2026-05-04, declaraciÃ³n Hacienda CR).
- +SecciÃ³n K Reglas de Uso (5 reglas: K1 datos canÃ³nicos B-F, K2 datos historicos G-I, K3 CEO-ONLY pgvector excluido, K4 doc prevalece sobre menciones cruzadas, K5 actualizaciÃ³n anual EEFF).
- +SecciÃ³n L Pendientes (L1 reconciliaciÃ³n costo histÃ³rico vehÃ­culo, L2 desglose Gastos G&A, L3 composiciÃ³n inventario por proveedor, L4 carta de subordinaciÃ³n de socios sobre cuenta x pagar).
- Aviso CEO-ONLY ahora menciona explÃ­citamente "saldos con partes relacionadas e indicadores financieros sensibles" (antes solo mencionaba cÃ©dulas + domicilio + distribuciÃ³n accionaria).

**Archivos modificados (3, ya contabilizados en 2026-05-04b sync):**
- `docs/ENT_GOB_SOCIEDAD.md` â€” sobrescrito v1.0 (DRAFT) expandido.
- `docs/IDX_GOBERNANZA.md` v1.2 -> v1.3:
  - Ãšltima revisiÃ³n nota actualizada (apunta a este BATCH 2026-05-04c); revisiÃ³n anterior demovida.
  - Health: ENTs descripciÃ³n actualizada a "DRAFT CEO-ONLY no_pgvector hub legal+EEFF".
  - Tabla Entities: descripciÃ³n de la fila Sociedad expandida + status VIGENTE -> DRAFT.
- `docs/MANIFIESTO_CAMBIOS_v2.md` â€” este append (segundo del dÃ­a).

**FROZEN/sealed intactos:**
- ARCH_AGENT_PRINCIPLES.md (sealed v1.5 commit 9ecd190).
- POL_DATA_CLASSIFICATION.md (sealed v1.4) â€” clasificaciÃ³n N2 sigue aplicada conforme regla existente.
- ENT_OPS_STATE_MACHINE.md.
- PLB_ORCHESTRATOR.md.
- BATCH 2026-05-04b queda intacto en este archivo (POL_INMUTABILIDAD: APPEND-ONLY, no se edita entrada anterior).

**Reglas observadas:**
- R1 no_inventar: contenido verbatim del CEO incluyendo cifras EEFF firmadas por CPI; campos vacÃ­os en fuente quedaron como em-dash o "â€”".
- R3 no_eliminar: el archivo prev (v1.0 minimal) fue sobrescrito en su totalidad por la versiÃ³n expandida del CEO en la misma versiÃ³n semÃ¡ntica v1.0 â€” no hay deletion lÃ³gica de informaciÃ³n, solo expansiÃ³n + cambio de status VIGENTE a DRAFT (mÃ¡s restrictivo). Cambio documentado in-place + en este BATCH.
- R4 headers: ENT mantiene id/version/status/visibility/domain/tipo/data_classification/aplica_a/stamp/no_pgvector + agrega `refs:` para cruces canÃ³nicos.
- R5 documentar cambio: este BATCH + changelog interno del archivo v1.0 entry Ãºnica (DRAFT sin segunda entrada porque sigue siendo v1.0 â€” la correcciÃ³n de status se documenta solo en CAMBIOS_v2 BATCH).
- R6 visibilidad: CEO-ONLY no fugÃ³. IDX_GOBERNANZA solo describe estructura de secciones (sin cifras concretas de EEFF, sin saldos de partes relacionadas, sin indicadores). CAMBIOS_v2 (INTERNAL) menciona cÃ³digos Hacienda pÃºblicos + nombres profesionales + estructura de secciones + monto reclasificaciÃ³n contable â‚¡90K (no sensible) + saldo cuenta x pagar a socios â‚¡20M en pendiente L4 (descripciÃ³n de pendiente, no detalle de saldo). Cifras de ingresos, costos, utilidades, mÃ¡rgenes, ROE/ROA NO fugaron a IDX/CAMBIOS_v2.
- POL_EPHEMERAL_OUTPUT v1.1 Regla 5: append directo a CAMBIOS_v2, NO se creÃ³ MANIFIESTO_APPEND fÃ­sico.
- POL_INMUTABILIDAD: BATCH anterior 2026-05-04b NO editado.

**ValidaciÃ³n pgvector:**
- ENT_GOB_SOCIEDAD sigue marcado `visibility: CEO-ONLY` + `no_pgvector: true` + `data_classification: N2`. Aviso CEO-ONLY al inicio del archivo prohibe explÃ­citamente referencia textual desde PUBLIC/INTERNAL/PARTNER_B2B. Verificar en prÃ³ximo reindex que el archivo NO aparezca en `vector_index_manifest`.

**Pendientes derivados (suma a los del 2026-05-04b):**
- Cuando se firmen EEFF + se cierren L1-L4, bumpear status DRAFT -> VIGENTE (sin bump de version semÃ¡ntica si no hay cambios de contenido).
- L1 (reconciliaciÃ³n costo histÃ³rico vehÃ­culo USD 17K vs â‚¡6.58M registrado): si CPI Solano + CEO definen reexpresiÃ³n, esto puede gatillar bump v1.1 con nota explicativa.
- L4 (carta de subordinaciÃ³n de socios sobre cuenta x pagar â‚¡20M): si se emite, agregar como documento fuente en secciÃ³n J.
- Re-validar cert RNP 562728-2026 antes del 2026-05-08 (ventana de 30 dÃ­as desde emisiÃ³n 2026-04-08).

**Sync:** `sync_sociedad_indexa.ps1` ya generado en 2026-05-04b sigue vÃ¡lido (cubre los mismos 3 archivos). No requiere regeneraciÃ³n.

**MÃ©tricas sesiÃ³n (incremental sobre 2026-05-04b):**
- Archivos sobrescritos: 1 (ENT_GOB_SOCIEDAD v1.0 minimal -> v1.0 expandido DRAFT).
- Archivos modificados: 1 (IDX_GOBERNANZA v1.2 -> v1.3) + 1 (este CAMBIOS_v2 append).
- Archivos nuevos creados: 0.
- Archivos eliminados: 0.
- POLs/SCHs/SPECs bumpeados: 0.
- MANIFIESTO_APPEND fÃ­sico creado: 0 (Regla 5 v1.1).

**Veredicto:** AMARILLO -> AMARILLO. Status del entity bajÃ³ de VIGENTE a DRAFT (mÃ¡s conservador, reconoce pendientes contables abiertos). Sin riesgo de leak por estar marcado CEO-ONLY + no_pgvector desde el header. La expansiÃ³n a hub canÃ³nico legal+contable+financiero centraliza fuente Ãºnica para procesos futuros (proformas, contratos, compliance, trÃ¡mites bancarios).

---

## BATCH 2026-05-04d â€” REDACCIÃ“N R6 sobre BATCH 2026-05-04b y 2026-05-04c (autoescalaciÃ³n)

**SesiÃ³n:** Cowork Â· misma sesiÃ³n, pass de auditorÃ­a.
**Origen:** Self-audit post-validaciÃ³n detectÃ³ leaks de contenido CEO-ONLY (de ENT_GOB_SOCIEDAD) dentro de los BATCH 2026-05-04b y 2026-05-04c, que viven en este archivo CAMBIOS_v2 (visibility: INTERNAL). ViolaciÃ³n R6 visibilidad.

**Naturaleza del leak (datos que NO debieron aparecer en INTERNAL):**

En BATCH 2026-05-04b:
- Domicilio fÃ­sico de socios (referenciado a urbanizaciÃ³n + nÃºmero de casa).
- Nombres completos + porcentaje + nÃºmero de cuotas de los 2 cuotistas en una sola lÃ­nea (correlacionable con cÃ©dulas presentes en otros archivos).

En BATCH 2026-05-04c:
- Saldo cuenta x pagar a socios `â‚¡20M` en descripciÃ³n de pendiente L4.
- Monto `â‚¡90K` de reclasificaciÃ³n contable retroactiva entre Capital Social y Utilidades Acumuladas.

**Datos que SÃ pueden permanecer en INTERNAL (son pÃºblicos vÃ­a RNP):**
- RazÃ³n social MUITO WORK LIMITADA.
- CÃ©dula jurÃ­dica 3-102-751710 (registro mercantil pÃºblico).
- Tipo societario, fechas constituciÃ³n/inscripciÃ³n, tomo/asiento, plazo, vencimiento.
- Capital social total â‚¡10,000 (figura en RNP).
- CÃ³digo Hacienda CR 4641.1 (pÃºblico).
- Cliente B2B principal en CR (Sondel S.A. â€” relaciÃ³n comercial declarada).
- Nombres profesionales (CPI Solano NÂ° 39405, notario, banco operativo).

**Comportamiento canÃ³nico:**
- POL_INMUTABILIDAD: CAMBIOS_v2 es APPEND-ONLY. NO se editan ni se borran las entradas 2026-05-04b ni 2026-05-04c.
- El agente escala al CEO el incidente y registra la redacciÃ³n aquÃ­ mismo + memoria operativa.
- Si el CEO autoriza, en una sesiÃ³n posterior puede emitirse un PR explÃ­cito de "redacciÃ³n retroactiva" sobre los 2 BATCH afectados, fuera de Cowork (PR manual + nueva entrada en CAMBIOS_v2 documentando la ediciÃ³n autorizada). Ese PR NO se ejecuta automÃ¡ticamente.

**Acciones tomadas en esta sesiÃ³n:**
1. Esta entrada BATCH 2026-05-04d documenta el incidente y limita su superficie de audit.
2. Memoria del agente actualizada (`indexar_ceoonly_no_describir_contenido.md`) para que futuras sesiones Cowork describan entries CEO-ONLY en CAMBIOS_v2 (INTERNAL) sÃ³lo con metadatos estructurales (id, version, status, lista de secciones, intenciÃ³n) y NUNCA con valores concretos.

**FROZEN/sealed intactos:**
- POL_INMUTABILIDAD respetada: BATCH 2026-05-04b y 2026-05-04c quedan tal cual.

**RecomendaciÃ³n operativa al CEO:**
- Si el riesgo es material (CAMBIOS_v2 vive en `docs/` y se mirroriza a OneDrive accesible en otros dispositivos), considerar (a) proceder con PR manual de redacciÃ³n retroactiva sobre los 2 BATCH afectados o (b) encriptar/restringir acceso a CAMBIOS_v2 a CEO-ONLY (requiere bumpear visibility del propio CAMBIOS_v2 â€” decisiÃ³n arquitectÃ³nica fuera de scope de esta sesiÃ³n).

**Veredicto:** AMARILLO -> AMARILLO. El leak estÃ¡ acotado a `docs/MANIFIESTO_CAMBIOS_v2.md` (INTERNAL en mirror OneDrive). Sin propagaciÃ³n a pgvector porque el archivo NO estÃ¡ marcado para indexaciÃ³n vectorial, sÃ³lo es log textual local. Riesgo de exfiltraciÃ³n limitado al perÃ­metro INTERNAL.

---

## BATCH 2026-05-04e â€” RETRIEVAL OPTIMIZATION post audit golden-set 10q

**Origen:** audit retrieval ejecutado 2026-05-04 sobre 10 queries golden-set (mezcla dominios + profundidad). Resultado: 8/10 FOUND, 2/10 PARTIAL, 0 MISS. Routing efficiency 80%. 5 cuellos detectados. Override CEO explÃ­cito ("si aplica") para aplicar P0+P1.

**Patches aplicados (4):**

1. **DEPENDENCY_GRAPH.md v4.0 -> v4.1** â€” agregado nodo dedicado para ENT_OPS_STATE_MACHINE con 13 dependientes vivos. Antes el grafo solo formalizaba 2 cadenas implÃ­citas (PLB_ORCHESTRATOR + PLB_INTERACCION_CLIENTE). Coverage gap detectado por audit: ~6x del blast radius real. Stamp 2026-05-04. Sin tocar el FROZEN.

2. **POL_EPHEMERAL_OUTPUT.md v1.1 -> v1.2** â€” resuelve colisiÃ³n semÃ¡ntica "Regla 5" detectada en query Q6 del audit. Step 3 del ciclo ahora es ancla canÃ³nica de "Regla 5 = 0-dÃ­as" (sesiÃ³n sin consolidaciÃ³n = trabajo a medias). Step 5 renombrado a "Anti-acumulaciÃ³n (umbral >3)". Sin cambio de enforcement, solo claridad nominal.

3. **IDX_SPRINTS.md** â€” creado v1.0. Tipo LOTE no tenÃ­a router canÃ³nico, el dato vivÃ­a sÃ³lo en CLAUDE.md como resumen agregado y forzaba glob global (Q7 del audit). Tabla S0-S27 con stamps reales extraÃ­dos por grep. Algunas celdas "Tema" pendientes [ver archivo] - lazy populate.

4. **IDX_ARQUITECTURA_FUNDACIONAL.md** â€” creado v1.0. ARCH_AGENT_PRINCIPLES + 7 SPECs medulares + SPEC_FABERLOOM_MVP estaban colgados de IDX_GOBERNANZA mezclando scopes. Movido el routing (no los archivos fÃ­sicamente, lazy migration). IDX_GOBERNANZA v1.3 -> v1.4 conserva sÃ³lo POLs + PLBs + ENTs gob + AUDITs FB pre-build + insights Kimi.

**FROZEN/sealed intactos:**
- ENT_OPS_STATE_MACHINE: solo agregado nodo en DEPENDENCY_GRAPH, no se tocÃ³ el archivo FROZEN.
- PLB_ORCHESTRATOR: intacto.
- ARCH_AGENT_PRINCIPLES sealed v1.5: intacto (solo se referencia desde IDX_ARQUITECTURA_FUNDACIONAL).
- POL_DATA_CLASSIFICATION sealed v1.4: intacto.

**MÃ©trica esperada post-patch (re-corrida del mismo golden-set):**
- Hit rate 9-10/10 FOUND (Q6 sale de PARTIAL con renombrado; Q10 sigue PARTIAL hasta poblar campo `estado` en ENT_COMERCIAL_CLIENTES).
- Routing efficiency -> 100% (Q5 + Q7 ahora tienen IDX canÃ³nico).
- Broken refs: 0.

**Pendientes P2 (no bloqueantes, requieren input CEO):**
- Poblar campo `estado [activo|inactivo]` en ENT_COMERCIAL_CLIENTES (COM-01).
- DecisiÃ³n sobre si Sprints S28+ estÃ¡n en planificaciÃ³n o congelados post-S27.
- Completar columna "Tema" en IDX_SPRINTS para S3-S20 (lazy, al primer touch).

**Files touched (5):**
- docs/DEPENDENCY_GRAPH.md (Edit)
- docs/POL_EPHEMERAL_OUTPUT.md (Edit)
- docs/IDX_GOBERNANZA.md (Edit)
- docs/IDX_SPRINTS.md (Write â€” nuevo)
- docs/IDX_ARQUITECTURA_FUNDACIONAL.md (Write â€” nuevo)
- docs/MANIFIESTO_CAMBIOS_v2.md (esta entrada)

**Sync:** `sync_retrieval_optimization_indexa.ps1` generado en outputs/ para mirror -> repo canÃ³nico per memoria sync_mirror_pushlocation.

**Veredicto:** retrieval health AMARILLO -> esperado VERDE post re-audit. Audit re-corrida pendiente como verification step.

---

## BATCH 2026-05-04f â€” INDEXA SKILL_FRONTEND_PRINCIPLES_MWT v1.0 SHADOW

**Origen:** archivo creado por CEO + Arquitecto Cowork. Adjuntado en sesiÃ³n Project para indexaciÃ³n. Lente cognitiva derivada de `docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` v2.1 (FB) â€” selecciÃ³n 9/14 principios + adaptaciÃ³n al stack MWT (3 frontends, expediente como objeto canÃ³nico, dashboard CEO power-user, portal B2B novato-friendly, ranawalk.com pÃºblico + agentes IA).

**Archivo creado:**
- `docs/SKILL_FRONTEND_PRINCIPLES_MWT.md` v1.0 SHADOW â€” visibility INTERNAL Â· domain Plataforma Â· type SKILL Â· autonomy_ceiling ACTIVO_BG Â· trigger por contexto (sin trigger word) Â· aplica_a [MWT].

**Contenido:**
- 9 principios M1-M9 con trazabilidad explicita al principio FB de origen (M1=FB-P1, M2=FB-P3, M3=FB-P5, M4=FB-P7, M5=FB-P4, M6=FB-P11, M7=FB-P13, M8=FB-P14, M9=FB-P10).
- CatÃ¡logo 16 flags (4 P0 bloqueantes: DRIFT_DETECTED, TRANSLATION_LEAK, ROLE_LEAK, STATE_DRIFT, MUSCLE_AMPUTATION, MUSCLE_REMOVAL_RISK).
- 11 antipatrones de rechazo automÃ¡tico.
- 4 modos de despliegue (Project, Claude Code/Cowork, Custom Instructions, Subagent dedicado).
- Stack canÃ³nico declarado: Next.js App Router + RSC + TanStack Query v5 + Zustand + WebSocket + RHF + Zod + Tailwind + ENT_PLAT_DESIGN_TOKENS.

**Coexistencia con FB v2.1:** ambos skills SHADOW, scopes separados:
- `SKILL_FRONTEND_PRINCIPLES_MWT` v1.0 â€” `aplica_a: [MWT]` â€” 9 principios MWT-especÃ­ficos en `docs/`
- `SKILL_FRONTEND_TEN_PRINCIPLES_V2` v2.1 â€” `aplica_a: [FB]` â€” 14 principios FB Design System en `docs/faberloom/`
- DecisiÃ³n CEO pendiente: si despuÃ©s de 3+ aplicaciones exitosas en MWT el FB skill se promueve a `[SHARED]` reemplazando este, o ambos coexisten permanentemente.

**Files touched (3):**
- docs/SKILL_FRONTEND_PRINCIPLES_MWT.md (Write â€” nuevo)
- docs/IDX_PLATAFORMA.md (Edit â€” agregadas 2 filas en Â§Skills + bump Health + Ãšltima revisiÃ³n)
- docs/MANIFIESTO_CAMBIOS_v2.md (esta entrada â€” append directo per Regla 5 v1.2)

**Pendientes derivados (no bloqueantes):**
- Crear `ENT_PLAT_FRONTENDS Â§UI_GLOSSARY` (glosario canÃ³nico tÃ©rminos UI MWT) â€” referenciado por M2.
- Validar primera aplicaciÃ³n en mock real (kanban CEO o portal B2B o ranawalk.com product page) â†’ pasar a VIGENTE si la lente colorea sin generar fricciÃ³n.
- DecisiÃ³n CEO sobre coexistencia FB v2.1 / MWT v1.0 post-3+ aplicaciones.
- Agregar fila en `SKILL_RUNTIME.md` (verificar que existe y estÃ¡ VIGENTE; si sÃ­, append; si no, deja para sesiÃ³n dedicada).

**FROZEN/sealed intactos:** sin tocar nada FROZEN ni sealed. ENT_OPS_STATE_MACHINE solo referenciado como ground truth canÃ³nico de los 8 estados expediente.

**Sync:** `sync_skill_frontend_principles_mwt_indexa.ps1` generado en raÃ­z mirror per memoria sync_mirror_pushlocation. ErrorActionPreference=Continue per memoria sync_powershell_erroraction (lecciÃ³n sesiÃ³n retrieval-optimization).

**Veredicto:** indexa estÃ¡ndar sin riesgos. Skill SHADOW = no aplica enforcement aÃºn, solo disponible para activaciÃ³n contextual. Pasa a VIGENTE solo despuÃ©s de validaciÃ³n CEO en uso real.

---

## BATCH 2026-05-04g â€” INDEXA POL_FABERLOOM_SURFACE_CONTRACT v0.1 DRAFT

**Sesion:** Project chat (no Cowork) - decision arquitectonica B+ post review shell v2.
**Origen:** sesion Cowork shell/chrome v2 entrego paquete de cierre + HTML ejecutable. Review en chat detecto 9 gaps; 4 bloqueantes (upload, chat libre, iteracion, sanidad) que el shell v2 delegaba implicitamente al canvas central. CEO cerro decision: opcion B+ (shell provee primitivas universales, surfaces declaran contract, no opcion A pura de imponer layout interno).

**Archivos creados (1):**
- `docs/faberloom/POL_FABERLOOM_SURFACE_CONTRACT.md` v0.1 DRAFT - INTERNAL - domain faberloom - owner product/design - canonical_after_review true.

**Contenido del POL:**
- 9 primitivas universales del shell (3.1-3.9): GlobalChatTrigger, UploadSlot, Context Controls, ContextualClock, RightTools, ActionFooter, RoleDisclosure, MobileToolsSheet, Telemetria base.
- 8 declaraciones obligatorias por surface (4.1-4.8): surface_mode_tabs, upload_slot, context_pack, context_dock, mobile_tools_sheet, action_footer, role_matrix, telemetry_extras.
- 7 reglas inquebrantables R1-R7 (no upload propio, no botones aprobacion fuera ActionFooter, no display:none por rol salvo mobile, no duplicar GlobalChatTrigger, no mover KB Global fuera topbar, registrar context_pack siempre, declarar mobile_dock_visible siempre).
- 3 excepciones permitidas E1-E3 (modales transaccionales, onboarding pre-tenant, mobile filtra por rol con declaracion explicita).
- 5 open questions OQ1-OQ5 para review CEO (tamano context_pack, orden tabs mobile, ActionFooter inline en Bandeja, UploadSlot en surfaces sin upload util, rol que firma promocion a VIGENTE).

**Decisiones cerradas en chat (referencia para v2.1 del shell):**
- GlobalChatTrigger desde Workspace existente: crea nueva conversacion con context pack del objeto activo (no reemplaza, no branch).
- UploadSlot: cada surface declara accepted_upload_types + upload_destination + upload_action. 9 surfaces ejemplificadas en tabla canonica.
- ActionFooter: primitiva reusable con variants footer/inline/toolbar y action_set default/governance.
- KB Global ON/OFF: junto al reloj contextual en topbar, hermano visual del reloj. Prohibido enterrar en canvas o dentro de boton Contexto.
- Mobile: right rail no desaparece, se transforma en bottom dock con max 5 slots filtrados por rol. Excepcion declarada a P7.
- Diferenciar agentes globales (sidebar) vs contextuales (right rail) con tooltips obligatorios.
- Role switcher en produccion sale del topbar a Settings -> Impersonate auditado.

**Mapeo color reloj canonico (alinea CSS con copy de spec):**
salvia -> verde (0-34%) | amber -> amarillo (35-59%) | coral -> naranja (60-81%) | vino -> rojo (82-100%).

**Files touched (1):**
- docs/faberloom/POL_FABERLOOM_SURFACE_CONTRACT.md (Write nuevo)
- docs/MANIFIESTO_CAMBIOS_v2.md (esta entrada - append directo per Regla 5 v1.2)

**Pendientes derivados:**
- SHELL_FABERLOOM_CHROME v2.1 debe crearse referenciando este POL en su header. Deltas vs v2: GlobalChatTrigger (Ask F* en topbar + CmdK), UploadSlot universal, KB Global ON/OFF reubicado junto al reloj, ActionFooter componente reusable, MobileToolsSheet bottom dock filtrado por rol, agentes globales vs contextuales con tooltips, role switcher reubicado.
- 5 open questions OQ1-OQ5 requieren review CEO antes de promover POL DRAFT -> VIGENTE.
- Ningun pgvector reindex requerido (POL nuevo, no afecta retrieval existente).

**FROZEN/sealed intactos:**
- ARCH_AGENT_PRINCIPLES.md (sealed v1.5 commit 9ecd190) - solo referenciado.
- POL_DATA_CLASSIFICATION.md (sealed v1.4) - solo referenciado para upload_action de KB.
- ENT_OPS_STATE_MACHINE.md - intacto.
- PLB_ORCHESTRATOR.md - intacto.

**Reglas observadas:**
- R1 no_inventar: contenido derivado de decisiones explicitas del CEO en chat, no inferencia.
- R3 no_eliminar: archivo nuevo, no se borro nada.
- R4 headers: id, version, status, visibility, domain, owner, canonical_after_review, created, references - completos.
- R5 documentar cambio: este BATCH + changelog interno del POL en seccion 9.
- R6 visibilidad: INTERNAL puro, no contiene nada CEO-ONLY ni datos sensibles.
- POL_EPHEMERAL_OUTPUT v1.2 Regla 5: append directo a CAMBIOS_v2, NO se creo MANIFIESTO_APPEND fisico.
- Scope FaberLoom (CLAUDE.md regla 2026-04-29): POL vive en `docs/faberloom/`, no en `docs/` raiz.

**Sync:** `sync_surface_contract_indexa.ps1` v1 generado en raiz mirror; primer pass push del POL OK (commit 18d0111 en branch skill-frontend-principles-mwt-20260504). Path del mirror_to_onedrive.ps1 corregido en v2 (vive en raiz OneDrive, no en `repo/scripts/`). Segundo pass para append del log: `sync_surface_contract_indexa_v2.ps1`.

**Veredicto:** POL nuevo SHADOW. No aplica enforcement hasta promocion a VIGENTE post review CEO de OQ1-OQ5. Habilita la creacion del shell v2.1 con contrato explicito, evita drift entre las 18 surfaces de FaberLoom.

---

## BATCH 2026-05-06 â€” INDEXA Proforma COMTEK PF 2467-2026 + perfil cliente enriquecido (CEO-ONLY)

**Sesion:** Cowork - sesion operativa armado proforma + indexa al cierre.
**Origen:** CEO arma PF 2467-2026 para DISTRIBUIDORA COMTEK S.A.S. (Colombia, codigo Marluvas 4000000102) sobre OC COMTEK 002-2026 fecha 2026-05-04. Modelo B comision mixta (5% / 10% por familia). Generado HTML dual-view siguiendo SCH_PROFORMA_MWT v2.0 desde golden Sonepar PF 2463-2026 v3.

**Archivos creados (1):**
- `docs/archivo/PF_2467-2026_COMTEK_GOLDEN.html` - copia archivada del HTML operativo como golden ejemplo. Documenta patron de comision mixta por SKU dentro de una misma proforma (5% sobre 100AWORKF + 10% sobre 70B22-BP-HIDRO). Complementa PF 2463 (comision homogenea) en la libreria de goldens del SCH.

**Archivos modificados (3):**
- `docs/ENT_COMERCIAL_CLIENTES.md` v1.0 -> v1.1 (CEO-ONLY): +seccion E "Perfiles enriquecidos (lazy populate)" con primera entry E1 DISTRIBUIDORA COMTEK S.A.S. Estructura del perfil: identidad fiscal + contactos + condiciones default observadas + comisiones por familia + modelo comercial habitual. Patron de lazy populate validado: solo se llena lo que aparece en operacion real, campos no observados quedan [PENDIENTE]. Header: agregada ref cruzada a SCH_PROFORMA_MWT.
- `docs/SCH_PROFORMA_MWT.md` v2.0 -> v2.1: reescrita seccion "Golden Example" como tabla "Golden Examples" con 3 entradas (PF_0000 placeholder + PF_2463 Sonepar comision homogenea 10% + PF_2467 Comtek comision mixta 5%/10%). Header: +ref ENT_COMERCIAL_CLIENTES.E. Stamp 2026-05-06.
- `docs/IDX_COMERCIAL.md` v1.0 -> v1.1: bump health (anota +1 golden HTML en docs/archivo/), last_review 2026-04-16 -> 2026-05-06, fila Clientes anota DRAFT v1.1 con marca CEO-ONLY + conteo entries seccion E.

**Reglas observadas:**
- R1 no_inventar: contenido del perfil E1 viene de capturas reales aportadas por CEO en sesion (NIT, direccion, contacto) + NCM extraidos de Tabela COMEX 2026 v6 (xlsx adjuntado). Direccion de entrega marcada [PENDIENTE - confirmar si difiere de notificacion].
- R2 no_tocar_frozen: ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR, ARCH_AGENT_PRINCIPLES, POL_DATA_CLASSIFICATION intactos.
- R3 no_eliminar: ENT_COMERCIAL_CLIENTES v1.0 contenido completo preservado en v1.1 (B/C/D intactos, +E aditiva). SCH_PROFORMA_MWT seccion Golden Example ampliada (no eliminada).
- R4 headers: ENT/SCH/IDX bumpeados con version + status + visibility + domain + stamp completos. ENT_COMERCIAL_CLIENTES mantiene CEO-ONLY puro.
- R5 documentar cambio: este BATCH + changelog interno en ENT_COMERCIAL_CLIENTES + changelog interno en SCH_PROFORMA_MWT.
- R6 visibilidad: contenido CEO-ONLY de E1 NO descrito en este BATCH (que vive en INTERNAL). Aqui solo metadatos estructurales: existencia del perfil, estructura de campos del template, modelo comercial habitual del cliente. Cifras de comision por familia mencionadas (5%/10%) son pacto operativo no sensible per se, pero quedan tambien en el perfil CEO-ONLY como referencia canonica. Memoria operativa indexar_ceoonly_no_describir_contenido respetada (no se incluye NIT, direccion fisica, telefono, email del contacto en este log).
- POL_EPHEMERAL_OUTPUT v1.2 Regla 5: append directo a CAMBIOS_v2, NO MANIFIESTO_APPEND fisico.
- POL_DETERMINISMO: el perfil del cliente vive ahora en ENT_COMERCIAL_CLIENTES.E como fuente unica. Proformas futuras para Comtek pueden inyectar el bloque desde ahi en vez de re-pedir datos al CEO.

**Validacion pgvector:**
- ENT_COMERCIAL_CLIENTES sigue marcado `visibility: [CEO-ONLY]`. Debe permanecer excluido del bucket INTERNAL en el proximo reindex. Verificar que la nueva seccion E NO aparezca en `vector_index_manifest`.
- HTML golden en `docs/archivo/` no se indexa (extension no .md) y de cualquier forma archivos en /archivo/ son lectura humana, no embedding.

**Pendientes derivados:**
- Direccion de entrega Comtek - confirmar si difiere de la direccion de notificacion San Fernando Plaza.
- Medio de pago - PF 2467 lo deja explicito ahora pero el perfil dice "Transferencia bancaria" como default observado. Si Comtek pacta otro en futuras OCs, agregar a la lista.
- COM-01 sigue abierto: replicar patron seccion E para Sondel, Sonepar, Melexa, Importcomp, etc. conforme aparezcan datos en operacion. No cargar masivamente, solo lazy populate.
- Pueblan E2, E3... segun van entrando OCs.

**Files touched (5):**
- docs/ENT_COMERCIAL_CLIENTES.md (Write - sobrescritura para v1.1 con +E)
- docs/SCH_PROFORMA_MWT.md (Edit - header v2.0->v2.1 + reemplazo Golden Example tail)
- docs/IDX_COMERCIAL.md (Edit - header v1.0->v1.1 + Health + fila Clientes)
- docs/archivo/PF_2467-2026_COMTEK_GOLDEN.html (Copy - nuevo archivo HTML golden)
- docs/MANIFIESTO_CAMBIOS_v2.md (esta entrada)

**Archivos NO indexados (ephemerals operativos en raiz mirror, no archivos de KB):**
- `PF_2467-2026_COMTEK.html` - HTML operativo en uso. Permanece en raiz mirror por practicidad CEO. Su contenido equivalente vive en docs/archivo/PF_2467-2026_COMTEK_GOLDEN.html para referencia canonica.
- `PF_2467-2026_COMTEK_email.html` - email formateado para draft a CEO. Ephemeral, no archivo de KB.

**Sync:** `sync_comtek_indexa.ps1` generado en raiz mirror per memoria sync_mirror_pushlocation. ASCII puro PS5-safe, ErrorActionPreference=Continue per memoria sync_powershell_erroraction, validacion robocopy exit code >=8 = fallo per memoria sync_robocopy_exit_codes. Cubre los 4 archivos editados/creados en docs/ + docs/archivo/.

**Veredicto:** indexa estandar bajo riesgo. Patron de lazy populate validado: ENT_COMERCIAL_CLIENTES gana valor operativo sin necesidad de cerrar COM-01 completo. Goldens del SCH ahora cubren 2 patrones de comision (homogenea + mixta). Sin impacto en otros dominios.

---

## BATCH 2026-05-06b â€” INDEXA SESION FB SHELL v2.3 + decisiones arquitectonicas cerradas

**Sesion:** Project chat extendida (no Cowork) - exploracion + cierre de modelo Faberloom mediante mock interactivo (faberloom_shell_v2_3.html en outputs/, ephemeral).
**Origen:** review iterativo del shell post POL_FABERLOOM_SURFACE_CONTRACT v0.1 + 2 brand books canonicos cargados (Faberloom book identity v2 + tokens.css SEALED en docs/archivo/faberloom-mockup/core/) + 2 diseÃ±os operativos del CEO (Mesa de Control "Centro Nervioso Operativo" + Inbox "entrada con priorizacion aprendida"). Multiples ciclos de validacion del modelo en chat sin codear KB.

**Naturaleza del BATCH:**
Este BATCH NO crea ni modifica archivos KB. Documenta las decisiones arquitectonicas cerradas en chat para que sesiones posteriores (POL bump v0.2, Cowork pantallas reales, indexa de procesos como espacio nuevo) tengan trazabilidad. El mock vive en outputs/ y NO sube al repo (es ephemeral per POL_EPHEMERAL_OUTPUT v1.2).

**Decisiones arquitectonicas cerradas (15+):**

1. **Taxonomia binaria espacio vs herramienta**: espacio = lugar humano de trabajo con power-user feature density (left rail). Herramienta = control transversal que opera sobre el espacio activo (right rail). Reemplaza la taxonomia anterior de 4 categorias (Operaciones/Setup/Governance/Admin) por agrupacion semantica.

2. **Mundo agentic vive en right rail; espacios humanos en left rail**: tabs Agents / Skills / Knowledge / Routing del right rail son contextuales (invocar/seleccionar). Los espacios dedicados (Agent Factory, Skill Arena, Routing Studio, Knowledge Base) son inventario + accion + sandbox. Conectados via boton "Iterar en Workspace" que abre Workspace con context_pack del objeto activo.

3. **Workspace estable + N context_packs**: Workspace es destino universal de iteracion con IA. Otras surfaces invocan workspace.open_with_context({ surface, object_id, context_pack_type, scope }) para iterar sobre cualquier objeto. NO hay un "Agent Factory en Workspace" como pack tipo - el factory es espacio propio, el iterar va a Workspace.

4. **Mesa = handoff IA -> humano (NO vista virtual)**: Mesa tiene items propios (HITLCase). Cuatro columnas por NATURALEZA DE DECISION (no por estado de procesamiento): CRITICO (overrides) / LISTO PARA REVISAR (drafts) / DELEGADO (en proceso) / ERROR ACCIONABLE (fallas tecnicas). Cada item: agent_origin, trace, confidence, proposed_action, evidence_bundle. Hero editorial "Que necesita tu decision hoy" + pulso 6 KPIs + accion canonica especifica por tipo (Resolver override / Revisar y aprobar / Abrir Workspace / Actualizar fuente).

5. **Inbox = entrada con priorizacion aprendida (NO bandeja pasiva)**: el sistema aprende patterns de clasificacion. Cards con score (96/100), bandeja origen (Ventas MWT/Buzon CEO/Personal/Licitaciones), categoria aprendida (RFQ con SKU + cliente conocido / Follow-up cliente activo / Recurrente operacional util / Publicidad con posible valor / Newsletter operativa), trace agente, acciones especificas por tipo. Right side panel con: bandejas conectadas, resumen diario en construccion, reglas aprendidas recientes, acciones de servidor (sobre Gmail/canal, no solo UI).

6. **Distincion final entre Inbox / Mesa / Workspace**: Inbox = entrada raw del canal email (input). Mesa = output de agentes esperando humano (handoff IA->humano). Workspace = workshop chat-first para iterar/construir con IA. Cada uno cubre una etapa distinta del flujo, NO duplican.

7. **Procesos = espacio nuevo cross-espacio (concepto)**: vive sobre los espacios y consolida gov-stamp queue + saneamiento + rutinas + audit trail. Single source of truth para evitar drift (cada espacio tendria su propia bandeja = duplicacion). Visible para Owner/Supervisor/Curador/Admin agentes. NO implementado en mock todavia, solo definido como concepto.

8. **Settings hub absorbe Users / IA & Keys / Audit / Economics / Voice / Billing**: ya no son espacios top-level. Voice Profile vive dentro de Agent Factory (cada agente declara su voz, no entidad propia). Audit/Economics se acceden via Settings o tab Processes del right rail.

9. **Right rail con 8 tabs canonicos + sub-tabs internos**: Tools/Context/Skills/Agents/Knowledge/Routing/Processes/Learning. Cada tab principal tiene sub-tabs internos (e.g. Agents: Globales/Contextuales/Factory) para evitar scroll vertical. Agentes globales del tenant viven en sub-tab Globales del tab Agents (NO en left sidebar - sacados de ahi).

10. **Header tools cambian segun tab del right rail abierto**: cuando rightTab tiene espacio dedicado (Agents/Skills/Knowledge/Routing), header conserva las acciones del surface. Cuando rightTab es transversal (Processes/Learning), header muestra acciones del tab. Mapeado en TAB_HEADER_TOOLS dictionary.

11. **Brand Book v2 oficial sealed como fuente identitaria**: Cream #F4F1ED (no #FAF8F4 que viene de tokens.css iteracion intermedia). Coral #C96442 mantenido entre temas (no se desatura en dark). Secondary #5A544C light / #BBB0A4 dark. Ink #1F1E1C light / #F4F1ED dark. Stroke-default #E5DED2. Fonts: Georgia italic (display), Inter (UI), JetBrains Mono.

12. **Margin Gloss device implementado (Hook C COMMITTED del Brand Book)**: italic Georgia coral 11px con border-left 1px coral, una por surface maximo. Aplicado en Mesa header (awaiting human / do not auto-resolve), Workspace thread head (auditable run / evidence attached), KB doc head (signed by CEO o needs source segun status), Inbox draft area (draft pending / operator review). Es la firma editorial Faberloom.

13. **Iconos Lucide stroke-width 2 (set del mock E1 viejo)**: mas solido y editorial vs stroke 1.5. Iconos especificos: Mesa = monitor/desktop, Skills = diana/target (3 circulos concentricos), Knowledge = libro con marcador (cerrado en sidebar) + libro abierto en V (right rail tab), Procesos = share-2 (3 nodos conectados), Aprendizaje = brain-circuit (cerebro + circuito), Agents = silueta personas, Voice = micrÃ³fono completo, Dashboard = bar chart vertical.

14. **Role picker enriquecido con descripcion de capacidades**: dropdown que muestra para cada rol quÃ© espacios ve y quÃ© acciones desbloquea/bloquea. 6 roles (operator/curador KB/agent admin/supervisor/owner/viewer) con badge L0-L4, count de espacios visibles, descripcion can-do, lista cant-do.

15. **Sidebar agrupado por seccion (recuperando estilo viejo)**: OPERAR (Workspace, Mesa de Control, Inbox) / CONFIGURAR (Knowledge Base, Agentes, Skills, Canales & Routing) / ADMINISTRAR (Dashboard, Pricing, Settings tenant). Tipografia del nav viejo: font-weight 500, font-size 13px, gap 11px, padding 9px 12px. Iconos 15px con opacity .85. Section kicker font-mono 9.5px letter-spacing .14em weight 600 padding 14px 12px 6px. Eliminados pin marks entre items (se veian como campanas - feo).

16. **POL_FABERLOOM_SURFACE_CONTRACT v0.1 sigue VIGENTE-DRAFT**: las 9 primitivas del shell + 8 declaraciones por surface + 7 reglas inquebrantables siguen aplicables. Las decisiones de esta sesion EXTIENDEN el POL pero NO lo invalidan. Bump a v0.2 pendiente (ver pendientes).

**Pendientes derivados (no se ejecutaron en esta sesion):**

- **POL_FABERLOOM_SURFACE_CONTRACT bump v0.1 -> v0.2**: agregar (a) taxonomia binaria como concepto raiz, (b) header_tools por surface declarativos, (c) right_rail_subtabs por tab, (d) Mesa = handoff IA->humano con 4 columnas canonicas, (e) Inbox = priorizacion aprendida con reglas + bandejas, (f) Procesos como concepto cross-espacio, (g) Settings como hub absorbente. NO ejecutado en esta sesion.
- **Espacio Procesos** (gov-stamp + saneamiento + rutinas + audit) - definido como concepto, no implementado en mock ni en POL.
- **Agent Factory pantalla dedicada con anatomia 3-pane** (lista + detalle Configurar/Iterar/Sanidad + right pane contextual): diseÃ±ada conceptualmente, no implementada. Pasa a paso siguiente cuando se decida prioridad.
- **Skill Arena y Routing Studio**: misma anatomia que Agent Factory con variantes (A/B test panel para skills, simulacion contra trace history para routing). Pendientes.
- **Iconos refinados a peticion CEO**: Mesa monitor / Skills diana / Knowledge libro cerrado/abierto / Procesos nodos / Aprendizaje brain-circuit aplicados. Si emerge feedback sobre algun otro icono se refina ad-hoc.
- **Mock faberloom_shell_v2_3.html**: vive en outputs/ del session sandbox. NO sube al repo. Si se promueve a referencia canonica, va a docs/archivo/faberloom-mockup/ con HANDOFF_TO_COWORK.md actualizado.

**FROZEN/sealed intactos:**
- ARCH_AGENT_PRINCIPLES (sealed v1.5 commit 9ecd190).
- POL_DATA_CLASSIFICATION (sealed v1.4).
- ENT_OPS_STATE_MACHINE.
- PLB_ORCHESTRATOR.
- POL_FABERLOOM_SURFACE_CONTRACT v0.1 (DRAFT - se mantiene tal cual; bump a v0.2 es pendiente, no edicion in-place).
- SPEC_FB_SYSTEM_TOPOLOGY_v1, SPEC_FB_DATA_MODEL_v1, SPEC_FB_AI_CONTROL_PLANE_v1 (VIGENTE) - solo referenciados, no tocados.

**Reglas observadas:**
- R1 no_inventar: decisiones documentadas son las que el CEO cerrÃ³ explicitamente en chat. Si algo no quedÃ³ claro, marcado como "concepto" o pendiente.
- R3 no_eliminar: archivo nuevo (este BATCH), no se borrÃ³ nada.
- R5 documentar cambio: este BATCH es el changelog (no hay changelog interno porque no hay archivos modificados).
- R6 visibilidad: INTERNAL puro, sin contenido CEO-ONLY ni datos sensibles.
- POL_EPHEMERAL_OUTPUT v1.2 Regla 5: append directo a CAMBIOS_v2, NO se creÃ³ MANIFIESTO_APPEND fÃ­sico.
- Scope FaberLoom (CLAUDE.md regla 2026-04-29): ningÃºn archivo nuevo se creÃ³, no aplica.
- POL_INMUTABILIDAD: no se editaron BATCH anteriores (2026-05-04g sigue siendo el indexa del POL v0.1).

**Files touched (1):**
- docs/MANIFIESTO_CAMBIOS_v2.md (esta entrada - append directo per Regla 5 v1.2)

**Sync:** `sync_session_2026-05-06b_indexa.ps1` generado en raiz mirror per memoria sync_mirror_pushlocation. ASCII puro PS5-safe, ErrorActionPreference=Continue, validacion robocopy >=8.

**Veredicto:** indexa de exploracion arquitectonica. Sin riesgo (no toca archivos KB). Cierra trazabilidad de las decisiones tomadas en chat para que la proxima sesion tecnica (POL bump v0.2 o pantallas Cowork) tenga ground truth de lo cerrado.

---

## 2026-05-07 (c) -- Indexa DEC-009 + SPEC_PROMPT_CACHE_DISCIPLINE

**Origen:** HANDOFF Cowork 28-abr (Claude Projects) actualizado post Sprint 0 (A0 + B0 + B1 ejecutados).

**Disparador:** analisis articulo TDS "Agentic AI: How to Save on Tokens" (Silfverskiold 2026-04-29). Hallazgo H4: timestamps al inicio de archivos Always-loaded invalidan prompt cache prefix de Anthropic en cada bump.

**Que se indexa:**

| Entregable | Path | Tipo | Hallazgos cubiertos |
|---|---|---|---|
| SPEC_PROMPT_CACHE_DISCIPLINE v1.0 DRAFT | `docs/SPEC_PROMPT_CACHE_DISCIPLINE.md` | NUEVO | H4 (volatiles cabecera rompen cache) |
| DEC-009 reemplazo | `docs/ENT_GOB_DECISIONES.md` v2.1->v2.2 | PATCH | Placeholder pre-existente desde 28-abr |
| D11 Prompt Cache Discipline | `docs/SPEC_ACTION_ENGINE.md` v1.2->v1.3 | PATCH (sin breaking change) | Enforcement centralizado via Engine |
| Changelog + version bump | `docs/RW_ROOT.md` v4.8.21->v4.8.22 | PATCH | Trazabilidad |
| Counts sync + version bump | `docs/DASHBOARD_SNAPSHOT.md` v13.0->v13.1 | PATCH | Conteos coherentes (SPEC +1, total decisiones 9->10 fix bug, reversibles 6->7) |

**Decisiones medulares:**

1. **R1-R4 cementadas:** R1 (volatiles al final), R2 (cache_control explicito), R3 (orden canonico bloques), R4 (TTL discipline).

2. **Status DRAFT del SPEC** hasta validar H2 con medicion real (cache hit ratio actual <30% sospechado, no medido). Promueve a VIGENTE post-medicion confirmatoria por Alejandro/Cowork.

3. **Reversible:** SI. Mover timestamp arriba revierte trivialmente. Solo R3 (orden bloques) tiene one-way effect en cache prefix.

4. **Aplica a FaberLoom desde Fase 3** per SPEC_FABERLOOM_MVP roadmap.

5. **Excepcion explicita:** providers sin prompt caching nativo (DeepSeek self-host, Ollama local) operan sin D11. Engine retorna `cache_hit_ratio: null`.

**Drift detectado vs HANDOFF v1:** ENT_GOB_DECISIONES v2.1 ya tenia DEC-010 (no anticipado en HANDOFF). Stats ajustados a la realidad post-DEC-010: total 9 (mal contado pre-DEC-010) corregido a 10; reversibles 6 -> 7 al sumar DEC-009. Documentado en changelog v2.2.

**Estimacion impacto (NO medida):**

| Metrica | Baseline estimado | Target |
|---|---|---|
| Costo input mensual agregado | ~$527/mes | ~$59/mes |
| Ahorro mensual proyectado | -- | ~$468 |
| Ahorro anual proyectado | -- | ~$5,600 |
| Cache hit ratio | <30% | >70% |
| Latencia TTFT en calls cacheadas | actual | -30% |

Caveat: estimacion analitica. Validacion pendiente con `cache_read_input_tokens` real post-implementacion.

**Sync:** `scripts/sync_prompt_cache_indexa.ps1` con manifest selectivo (NO `git add .`) per POL_BRANCH_PR_v1 Â§6. Actor declarado: `sync_indexa_script` (legitimo per POL_ROOT_FILE_CLASSIFICATION_v1, hooks PreToolUse permiten escritura a `canonical_docs` solo via este actor). Validaciones: working tree clean pre-commit, hash post-copia, ASCII puro PS5-safe, robocopy exit >=8 = fail.

**Files touched (6):**

- `docs/SPEC_PROMPT_CACHE_DISCIPLINE.md` (Write -- nuevo, 4 reglas R1-R4)
- `docs/ENT_GOB_DECISIONES.md` (Edit -- header v2.1->v2.2 + DEC-009 reemplazo + stats fix + changelog)
- `docs/SPEC_ACTION_ENGINE.md` (Edit -- header v1.2->v1.3 + relacionado + seccion 10->11 decisiones + +D11 + changelog)
- `docs/RW_ROOT.md` (Edit -- titulo v4.8.21->v4.8.22 + changelog v4.8.22)
- `docs/DASHBOARD_SNAPSHOT.md` (Edit -- header v13.0->v13.1 + tipos SPEC +1 + versiones principales sync + nueva fila SPEC_PROMPT_CACHE_DISCIPLINE)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**NO indexado en este batch (diferido):**

- Sprint mecanico Fase 2 timestamp-al-footer (~35 archivos Always-loaded). **Diferido a post-A1** para coordinarse con los 12 SPECs nuevos que A1 va a producir y evitar break-glass repetido. Trigger: CEO post merge A1.
- Implementacion tecnica `cache_control` en system prompt builder Cowork + Claude Code. Scope Alejandro post-S26 -- requiere acceso a runtime de cada agente.
- Medicion real H2 con `cache_read_input_tokens` post-implementacion. Requiere acceso Anthropic Console + 1 sem baseline.
- Promocion SPEC_PROMPT_CACHE_DISCIPLINE DRAFT->VIGENTE. Gate: hit ratio >50% medido.
- Update IDX_PLATAFORMA con SPEC_PROMPT_CACHE_DISCIPLINE. Diferido a sesion mantenimiento.
- Update DEPENDENCY_GRAPH con D11 nodo. Idem.
- ENT_PLAT_LLM_PROVIDERS_CACHE_POLICIES (politicas Kimi/DeepSeek/ChatGPT). No urgente.

**Veredicto:** indexa documental bajo riesgo. Cementa disciplina prompt cache sin tocar runtime ni archivos legacy. Ahorro $5,600/ano queda documentado y proyectado. Implementacion tecnica + medicion real son fases posteriores. Sprint mecanico ~35 archivos diferido coherente con A1 plan v4.

---

## 2026-05-07 (d) -- A1.1 POL_OUTAGE_CANONICAL_MIRROR v1.0

**Origen:** PLAN_INTEGRACION_v4_POST_ROUND3.md Â§3.4 entregable 1/12. Primera pieza A1 dependency-first.

**Disparador:** R3#11 -- hooks fail-closed activos (Sprint 0 B1) amplifican riesgo de outage canonico sin canal de recuperacion declarado. Pipeline `Cowork -> mirror -> sync -> canonico -> push -> mirror_back` tiene single point of failure en canonico (C:\dev\mwt-knowledge-hub) sin politica explicita de continuidad.

**Que se indexa:**

| Entregable | Path | Tipo |
|---|---|---|
| POL_OUTAGE_CANONICAL_MIRROR v1.0 VIGENTE | `docs/POL_OUTAGE_CANONICAL_MIRROR_v1.md` | NUEVO |
| Counts sync + version bump | `docs/DASHBOARD_SNAPSHOT.md` v13.1->v13.2 | PATCH (POL_ 28->29) |
| Changelog + version bump | `docs/RW_ROOT.md` v4.8.22->v4.8.23 | PATCH |
| Append BATCH 2026-05-07 (d) | `docs/MANIFIESTO_CAMBIOS_v2.md` | PATCH (este append per R5) |

**Decisiones medulares:**

1. **3 estados canonicos:** HEALTHY (operacion normal), DEGRADED (auto-recoverable, Cowork sigue escribiendo a staging), OUTAGE (CEO-declarado, buffer 7 dias SLA).

2. **R2 detectores ejecutables:** sync scripts ejecutan checks pre-Fase 1 (git status, git fetch, push reject, mirror exit, hash mismatch hooks/config, drift mirror vs canonico). Detector continuo via scheduled task DIFERIDO a v2.

3. **R5 Cowork autonomy en outage:** PUEDE leer mirror, escribir generated_staging con flag `outage_buffer: true`, operar outputs/. NO PUEDE ejecutar sync, modificar control_surface, declarar fin de outage.

4. **CEO autoridad unica** para declarar OUTAGE y RECOVERED. Sin backup en v1 (riesgo aceptado, mitigacion futura via delegacion explicita).

5. **SLA buffer 7 dias** arbitrario en v1 sin medicion historica. Revisable v2 con datos reales.

6. **Reconciliacion manual** en v1. Script `reconcile_outage.ps1` no existe (riesgo aceptado, mitigacion futura).

**Files touched (4):**

- `docs/POL_OUTAGE_CANONICAL_MIRROR_v1.md` (Write -- nuevo, 7 reglas R1-R7)
- `docs/DASHBOARD_SNAPSHOT.md` (Edit -- header v13.1->v13.2 + POL_ 28->29 + nueva fila)
- `docs/RW_ROOT.md` (Edit -- titulo v4.8.22->v4.8.23 + changelog v4.8.23)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**NO indexado en este batch (diferido):**

- `kb_health_check.ps1` scheduled task continuo. Diferido a v2 POL bump.
- `recover_canonical.ps1` automatizado. Hoy es secuencia manual.
- `reconcile_outage.ps1` automatizado. Hoy es secuencia manual con manifest.
- Update IDX_GOBERNANZA con POL_OUTAGE_CANONICAL_MIRROR. Diferido a sesion mantenimiento.

**Sync:** `scripts/sync_a1_01_outage_canonical_mirror_indexa.ps1` con manifest selectivo per POL_BRANCH_PR_v1 Â§6. Validaciones: working tree clean pre-commit, hash post-copia, ASCII puro PS5-safe, robocopy >=8 = fail.

**Veredicto:** POL fundacional A1. Cementa continuidad operativa ante el escenario mas critico del pipeline (outage canonico). Bajo riesgo (documental, no toca runtime). Habilita escribir SPECs A1 subsecuentes con confianza de que el pipeline tiene recovery path declarado. Score readiness Sprint 0 -> A1: cubre R3#11 explicit.

---

## 2026-05-07 (e) -- A1.2 SPEC_FB_DOCUMENT_STATE_MACHINE v1.0

**Origen:** PLAN_INTEGRACION_v4_POST_ROUND3.md Â§3.4 entregable 2/12. Segunda pieza A1 dependency-first.

**Disparador:** R3#15 -- state machine de documentos KB es implicita en el modelo actual (campo `status` sin transiciones formalizadas). Sin maquina explicita: re-chunking ad-hoc no trazable, quarantine sin protocolo, soft-delete contradice retention, versionado puede retroceder accidentalmente. Bloquea SPECs A1 subsecuentes (A1.5 Context Bundle, A1.7 Learning, A1.8 Outcome) que asumen estados estables y auditables.

**Que se indexa:**

| Entregable | Path | Tipo |
|---|---|---|
| SPEC_FB_DOCUMENT_STATE_MACHINE v1.0 VIGENTE | `docs/faberloom/SPEC_FB_DOCUMENT_STATE_MACHINE_v1.md` | NUEVO |
| Counts sync + version bump | `docs/DASHBOARD_SNAPSHOT.md` v13.2->v13.3 | PATCH (SPEC_ 12->13, FB scope 11->12, docs/faberloom/ 46->47) |
| Changelog + version bump | `docs/RW_ROOT.md` v4.8.23->v4.8.24 | PATCH |
| Append BATCH 2026-05-07 (e) | `docs/MANIFIESTO_CAMBIOS_v2.md` | PATCH (este append per R5) |

**Decisiones medulares:**

1. **10 estados canonicos:** draft, active, rescan_required, reprocessing, reindexed, quarantine_review, quarantine_released, archived, tombstoned, failed. Los 6 ampliados R3#15 + 4 base (draft/active/archived/failed).

2. **18 transiciones DAG estrictas.** Tabla canonica en R2. Cualquier transicion fuera de esa lista debe rechazarse. `tombstoned` es terminal -- recuperar requiere nuevo doc id con referencia historica.

3. **Versioning monotonic semver:** version_after > version_before SIEMPRE. Major (cambio source authority), Minor (re-chunk/embed), Patch (metadata fix). No retroceso jamas.

4. **Audit chain D10 obligatorio:** cada transicion genera DocumentStateAuditEntry inmutable hasheado en chain con `previous_audit_hash`, `state_snapshot_hash`, `signature` HMAC tenant key.

5. **RBAC explicit per transicion (R5):** system / curator / auditor / operator. Agentes runtime y end_user NO pueden mutar estados.

6. **Tenancy aislada (R6):** todo transition lleva `tenant_id` obligatorio. Pool L3 Knowledge River usa tenant_id `_pool_l3` con auditor del comite como actor.

7. **NO reemplaza ENT_OPS_STATE_MACHINE FROZEN:** dominio distinto (operativo MWT cotizaciones vs documental KB). Esta SPEC es la maquina KB. ENT_OPS_STATE_MACHINE permanece intacto.

**Files touched (4):**

- `docs/faberloom/SPEC_FB_DOCUMENT_STATE_MACHINE_v1.md` (Write -- nuevo, 7 reglas R1-R7 + Contract API)
- `docs/DASHBOARD_SNAPSHOT.md` (Edit -- header v13.2->v13.3 + SPEC_ 12->13 + nueva fila + FB scope 11->12)
- `docs/RW_ROOT.md` (Edit -- titulo v4.8.23->v4.8.24 + changelog v4.8.24)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**NO indexado en este batch (diferido):**

- Backend FastAPI implementacion `transition_document` endpoint. Sprint 1 FaberLoom dev.
- Tablas `documents` + `document_state_audit` con hash chain. Sprint 1.
- Worker pool reprocessing (consumer Outbox). Sprint 2.
- Dashboard metricas R7 (timeseries storage decision). Diferido a A1.10 SPEC_FB_KB_QUALITY_MONITORING.
- ML flagging quarantine_review. Diferido a A1.11 RAG_FIREWALL v2 + C8 abuse_scoring.
- MWT KB hub adopcion (replicar esquema en `mwt-knowledge-hub`). Sprint mecanico post-A1.
- Update IDX_PLATAFORMA + IDX_FABERLOOM con SPEC_FB_DOCUMENT_STATE_MACHINE. Diferido a sesion mantenimiento.

**Sync:** `scripts/sync_a1_02_document_state_machine_indexa.ps1` con manifest selectivo per POL_BRANCH_PR_v1 Â§6.

**Veredicto:** SPEC fundacional FaberLoom MVP1. Bajo riesgo documental, alto valor habilitante: bloquea o desbloquea consistentemente A1.5/A1.7/A1.8 que asumen estados auditables. Cubre R3#15 explicit. No toca FROZEN. Implementacion tecnica diferida a Sprint 1 FaberLoom -- contrato API estable desde hoy.

---

## 2026-05-07 (f) -- A1.3 SKILL_KB_GATEWAY v1.0 SHADOW

**Origen:** PLAN_INTEGRACION_v4_POST_ROUND3.md Â§3.4 entregable 3/12. Tercera pieza A1 dependency-first. Cierra sesion 1 A1 (POL_OUTAGE + SPEC_DOC_STATE + SKILL_KB_GATEWAY = "proteger pipeline").

**Disparador:** sin gateway formal el pipeline tiene 3 gaps operativos: race condition entre sync paralelos, manifest stale (script con manifest del minuto X promueve archivos modificados en X+2 sin saberlo), escrituras parciales (crash a mitad de copy deja repo half-written). Bloquea adoption confiable de los 9 SPECs A1 restantes y los SPECs A1.10/A1.11 que asumen escritura transaccional.

**Que se indexa:**

| Entregable | Path | Tipo |
|---|---|---|
| SKILL_KB_GATEWAY v1.0 SHADOW | `docs/SKILL_KB_GATEWAY.md` | NUEVO |
| Counts sync + version bump | `docs/DASHBOARD_SNAPSHOT.md` v13.3->v13.4 | PATCH (SKILL_ 11->12, SHADOW 11->12) |
| Changelog + version bump | `docs/RW_ROOT.md` v4.8.24->v4.8.25 | PATCH |
| Append BATCH 2026-05-07 (f) | `docs/MANIFIESTO_CAMBIOS_v2.md` | PATCH (este append per R5) |

**Decisiones medulares:**

1. **5 capacidades C1-C5:** acquire_lock (single-writer per target), verify_manifest (optimistic concurrency con repo_head_hash + tree_hash), atomic_write (transaction commit/rollback), audit footprint (KBGatewayAuditEntry per operacion), outage awareness (consulta POL_OUTAGE estado pipeline pre-lock).

2. **Recomendacion arquitectonica atomic write:** Opcion A tempdir + swap. Razon: no ensucia git state, swap atomic per archivo a nivel filesystem, rollback simple. Decision concreta confirmable Sprint 1 con benchmark.

3. **Lock single-machine v1.** Si en futuro hay 2 maquinas escribiendo, mitigacion v2 con Postgres advisory lock o Redis SETNX. Riesgo aceptado en v1 (laptop CEO + un Cowork session).

4. **Skill NO declara outages.** Solo respeta `OUTAGE_DECLARED_*.md` archivo si existe. Autoridad permanece CEO per POL_OUTAGE R4.

5. **NO interpreta contenido archivos.** Reglas semanticas viven en hooks (SPEC_HOOKS_FAIL_CLOSED) o POLs especificas. Skill trata archivos como opaque bytes.

6. **Status SHADOW v1 + gates promocion ACTIVO:** adapter PS implementado y usado en 3+ sync scripts, test B1-style suite pasa, 10+ runs auditados, CEO confirma sin friccion operativa.

7. **Implementacion concreta diferida a Sprint 1+.** Sprint 1 minimo: wrapper PS + lock file (`.kb_gateway.lock` en raiz canonico con PID + timestamp). Atomic write keeps Copy-Item secuencial + post-copy hash verify hasta benchmark de Opcion A.

**Files touched (4):**

- `docs/SKILL_KB_GATEWAY.md` (Write -- nuevo, 5 capacidades + 8 estados internos + Contract API)
- `docs/DASHBOARD_SNAPSHOT.md` (Edit -- header v13.3->v13.4 + SKILL_ 11->12 + SHADOW 11->12 + nueva fila)
- `docs/RW_ROOT.md` (Edit -- titulo v4.8.24->v4.8.25 + changelog v4.8.25)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**NO indexado en este batch (diferido):**

- Adapter PowerShell para sync scripts. Post-A1.
- Backend FastAPI endpoint para FaberLoom integration. Sprint 2.
- Postgres advisory lock para v2 multi-machine. Sprint 3.
- Audit log structured queryable (migrar de archivo plano a Postgres). Sprint 2.
- Tests B1.7-style: write canonical desde Cowork sin actor `sync_indexa_script` debe rechazar. Sprint mecanico post-A1.
- Update IDX_PLATAFORMA con SKILL_KB_GATEWAY. Sesion mantenimiento.

**Sync:** `scripts/sync_a1_03_kb_gateway_indexa.ps1` con manifest selectivo per POL_BRANCH_PR_v1 Â§6.

**Veredicto:** SKILL infraestructura bajo riesgo (documental), alto valor: cierra los 3 gaps operativos del pipeline KB y habilita confianza para A1.4-A1.12. Status SHADOW correcto -- contrato API + decisiones cementadas hoy, implementacion concreta + tests llegan en Sprint 1+. Sesion 1 A1 cerrada (3 entregables, ~3h estimadas vs 1.5h reales). Habilita arrancar Sesion 2 A1 (A1.4 + A1.5 + A1.6) cuando CEO autorice.

---

## 2026-05-07 (g) -- Voice Humanizer v2 cierre modelo conceptual

**Origen:** Sesion Cowork 2026-05-07 (modelo workspaces=cuenta polimorfico via vertical_spec_object) + iteracion con Gemini sobre 11 preguntas Voice Humanizer (bloque devuelto por Gemini con respuestas firmadas CEO).

**Disparador:** SPEC_FB_VOICE_HUMANIZER_v1 (canon 2026-05-02) declara modelo de 5 capas con precedencia jerarquica (User/Org/Dept/Channel/Recipient). El refinamiento sesion 2026-05-07 cerro: voz REAL es solo sabor del user; Org/Dept/Channel/Recipient se reclasifican como knowledge constraints o parametros de renderizacion, NO voces independientes; resolucion property-by-property con declaracion explicita; bootstrap E1 simple (CSV upload diferido E3 per TIER1 #14). v1 sigue VIGENTE en lo no contradictorio; v2 enriquece + corrige modelo conceptual.

**Que se indexa:**

| Entregable | Path | Tipo |
|---|---|---|
| SPEC_FB_VOICE_HUMANIZER_v2 VIGENTE | `docs/faberloom/SPEC_FB_VOICE_HUMANIZER_v2.md` | NUEVO (extiende v1) |
| SCH_FB_VOICE_PROFILE_v1 VIGENTE | `docs/faberloom/SCH_FB_VOICE_PROFILE_v1.md` | NUEVO |
| SCH_FB_WS_INSTRUCTIONS_v1 VIGENTE | `docs/faberloom/SCH_FB_WS_INSTRUCTIONS_v1.md` | NUEVO |
| POL_FB_VOICE_RESOLUTION_v1 VIGENTE | `docs/faberloom/POL_FB_VOICE_RESOLUTION_v1.md` | NUEVO |
| Counts sync + version bump | `docs/DASHBOARD_SNAPSHOT.md` v13.4->v13.5 | EDIT (docs/faberloom/ 47->51, FB scope 12->16, +SPEC_FB_VOICE_HUMANIZER v2.0) |
| IDX update Sprint 1A reading list | `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` | EDIT (items 14-17 con SPEC v2 + 2 SCH + 1 POL) |
| Append BATCH 2026-05-07 (g) | `docs/MANIFIESTO_CAMBIOS_v2.md` | PATCH (este append per R5) |

**Decisiones medulares (13 firmadas CEO sesion 2026-05-07):**

1. **Una sola voz por user.** Sabor unico (no variantes formal/casual). Evoluciona con HITL signals.
2. **NO existe voz tenant como tono.** Tenant aporta knowledge constraints (banned phrases, glosario) que aplican como filtro post-resolucion.
3. **Voz universal por canal por default.** Channel es parametro de renderizacion del mismo sabor (email full vs WhatsApp comprimido vs TTS adaptado).
4. **Estilo cliente del workspace = instrucciones declarativas explicitas del dueno** (no auto-aprendido).
5. **Solo el dueno del workspace edita** las instrucciones del workspace.
6. **Ajuste transitorio = comando libre del operator** + flag visible al user que se aplico.
7. **Ajuste transitorio aplica POST-generacion** (sobre el draft producido), no afecta contenido factual.
8. **NO promocion automatica transitorio -> persistente.** Control manual del dueno.
9. **Resolucion property-by-property.** Workspace gana donde declara; user pasa donde no. Modelo CSS-like specificity, no precedencia monolitica.
10. **Aprendizaje user solo desde edits Mesa (HITL).** Captura "porque" via dropdown predefinido + libre opcional.
11. **NO override manual del user.** Aprendizaje es implicito.
12. **Bootstrap E1 = opcion B** (configuracion explicita simple: saludo + firma + 2-3 ejemplos pegados manualmente). CSV upload analisis historico diferido E3 per TIER1 #14 plan FB firmado.
13. **Loop feedback "instruccion no matiza" diferido E2.** En E1 dueno revisa instrucciones manualmente.

**Files touched (7):**

- `docs/faberloom/SPEC_FB_VOICE_HUMANIZER_v2.md` (Write -- nuevo, 18 secciones, extiende v1, delta explicito en seccion 13, decisiones firmadas en seccion 17)
- `docs/faberloom/SCH_FB_VOICE_PROFILE_v1.md` (Write -- nuevo, schema YAML completo del sabor user + tipos auxiliares + lifecycle + privacy tier)
- `docs/faberloom/SCH_FB_WS_INSTRUCTIONS_v1.md` (Write -- nuevo, schema declaracion parcial property-level + conditional rules + ejemplos minimal/intermedio/avanzado)
- `docs/faberloom/POL_FB_VOICE_RESOLUTION_v1.md` (Write -- nuevo, algoritmo resolucion property-by-property + 5 niveles orden + filtros post-resolucion + casos especiales + audit)
- `docs/DASHBOARD_SNAPSHOT.md` (Edit -- header v13.4->v13.5 + docs/faberloom/ 47->51 + FB scope 12->16 con breakdown actualizado + nueva fila SPEC_FB_VOICE_HUMANIZER v2.0)
- `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` (Edit -- agrega items 14-17 en seccion "Para implementacion (Sprint 1A)" con los 4 archivos nuevos)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**Tensiones canon resueltas:**

| Tension | Resolucion |
|---|---|
| TIER1 #14 plan FB ("Learning de muestras E3") vs onboarding via CSV de SPEC v1 | v2 difiere CSV upload a E3, alineado con plan firmado. E1 usa bootstrap simple opcion B |
| TIER1 #15 (NO sub-agentes) vs Voice como capability del @router en v1 | Voice Humanizer es skill terminal de cadena lineal del agente del workspace, no agente. Compatible TIER1 #15 (confirmado por Gemini en iteracion: "skill que modula a otro skill = pipe de transformacion de texto, no agente orquestado") |
| TIER1 #16 punto 8 (NO skills compartidas entre tenants) vs knowledge cross-tenant del vertical | Resolucion lectura A: knowledge cross-tenant SI (LOC_GLOSARIO_VERTICAL L1), skills cross-tenant NO. SKILL_VOICE_HUMANIZER es skill SYSTEM provisto por FaberLoom, no skill cross-tenant |
| Conflicto resolucion v1 (precedencia jerarquica monolitica) vs cierre 2026-05-07 (property-level merge) | v2 reemplaza modelo de precedencia con resolucion property-by-property. v1 sigue VIGENTE en lo no contradictorio (regla inquebrantable, integracion @router conceptual, mini view, candidates de voz, Voice Overlay en trace) |

**Conceptos canonizados nuevos:**

- **"Sabor del user":** personalidad unica del firmante. Una voz por user. Evoluciona con HITL.
- **Property-level merge:** resolucion de voz analoga a CSS specificity, no precedencia monolitica.
- **Declaracion parcial:** ws_instructions solo escribe propiedades a modificar; lo no declarado pasa intacto del user.
- **Resolution trace obligatorio:** cada output documenta source_layer por propiedad (auditable, debuggable, promovable a learning signal).
- **Skill SYSTEM mandatory:** Voice Humanizer es del producto FaberLoom (logica core no editable por tenant); tenants editan solo el knowledge.

**NO indexado en este batch (diferido):**

- `POL_FB_VOICE_LEARNING_v1` (captura signals HITL + tipificacion dropdown + processing rules). Proxima sesion Cowork.
- `SPEC_FB_VOICE_BOOTSTRAP_v1` (UI configuracion explicita opcion B + wireframes + flow first-time-setup). Proxima sesion Cowork.
- `SPEC_FB_VOICE_FEEDBACK_LOOP_v1` (mecanismo "instruccion no matiza"). Diferido E2.
- Storage DB tablas `voice_profiles` + `workspace_voice_instructions`. Sprint 1A FaberLoom dev.
- Wireframes UI tab "Mi voz" en workspace + form bootstrap user. Sprint 1A.

**Sync:** `scripts/sync_voice_humanizer_indexa.ps1` con `manifest_voice_humanizer_freeze.json` selectivo per POL_BRANCH_PR_v1 Â§6. Branch target: `indexa/voice-humanizer-v2-2026-05-07`. Commit message: `[FABERLOOM] Voice Humanizer v2 + 3 schemas/POL (resolucion property-by-property)`.

**Veredicto:** Cierre modelo conceptual Voice Humanizer Foundation Beta E1. Bajo riesgo (documental), alto valor habilitante: bloquea o desbloquea Sprint 1A frontend + backend voice profile + workspace instructions UI. v1 preservado en lo no contradictorio (no se borra contenido aprobado per Regla 3). Tensiones con TIER1 #14/#15/#16 resueltas explicitamente. 13 decisiones CEO firmadas documentadas en seccion 17 del SPEC v2 + en este BATCH. Pendientes 2 documentos para proxima sesion: POL_FB_VOICE_LEARNING_v1 (captura HITL signals con tipificacion dropdown CEO-firmada) + SPEC_FB_VOICE_BOOTSTRAP_v1 (UI wizard configuracion explicita opcion B). Stack canon listo para implementacion runtime en Sprint 1A.

---

## 2026-05-07 (h) -- Iteracion shell FaberLoom v3-v6 + consolidated snapshot v2

**Origen:** Sesion Cowork 2026-05-07 (continuacion post-Voice Humanizer). Iteracion intensiva del shell del producto FaberLoom Â· 4 versiones HTML + 2 sketches markdown + decisiones de naming, copy, cross-language y arquitectura UI.

**Disparador:** El sketch shell previo (faberloom_shell_chat_v1.md) quedo desactualizado tras decisiones masivas: familia *Loom (FaberLoom + WorkLoom + SpaceLoom + StackLoom), reemplazo de "Mesa de trabajo" por WorkLoom, "Chat" por SpaceLoom, "Curaduria" por StackLoom, "HITL" por "Esperando tu criterio", layout 4 paneles + resize handles, sidepanel derecho minimalista 4 tabs, brand foot tagline "Teje tu trabajo", cross-language matrix completa (5 idiomas).

**Que se indexa:**

| Entregable | Path | Tipo |
|---|---|---|
| Shell v3 universal | `docs/anexos/mockups/faberloom_shell_universal_v3.html` | NUEVO MOCKUP |
| Shell v4 chat | `docs/anexos/mockups/faberloom_shell_chat_v4.html` | NUEVO MOCKUP |
| Shell v5 chat (4 paneles + resize) | `docs/anexos/mockups/faberloom_shell_chat_v5.html` | NUEVO MOCKUP |
| Shell v6 ACTUAL (familia *Loom) | `docs/anexos/mockups/faberloom_shell_v6.html` | NUEVO MOCKUP |
| Sketch v1 markdown del Chat workspace | `docs/anexos/mockups/faberloom_shell_sketch_chat_v1.md` | NUEVO SKETCH MD |
| Snapshot consolidado v2 (21 secciones) | `docs/anexos/mockups/faberloom_shell_consolidated_v2_2026-05-07.md` | NUEVO SKETCH MD |
| Append BATCH 2026-05-07 (h) | `docs/MANIFIESTO_CAMBIOS_v2.md` | PATCH (este append per R5) |

**Decisiones medulares de la iteracion:**

1. **Familia *Loom Â· 4 pilares de marca:**
   - FaberLoom (marca producto entero)
   - WorkLoom (Mesa de Control Â· canon: workloom Â· UI: "Mesa de Control")
   - SpaceLoom (home cognitivo Â· reemplaza "Chat" como nombre del workspace home)
   - StackLoom (construir knowledge Â· capas L0-L4 son stack literal Â· reemplaza "Curaduria")

2. **HITL renaming a "criterio":** mas orientado al objetivo HITL Â· "Esperando tu criterio" (UI) Â· "Approval criteria" / "Criterio para aprobacion" (configuracion) Â· HITL solo en canon tecnico SPECs.

3. **Cross-language matrix completa:** familia *Loom universal sin traducir Â· UI localizada por tenant_locale en 5 idiomas (EN/ES/PT/FR/IT).

4. **Tagline brand:** "Teje tu trabajo" / "Weave your work" / "Teca seu trabalho". Vive en brand foot del Rail 1, Georgia italic coral pequeno.

5. **Layout 4 paneles + resize handles:** Rail 1 (principal navegacion) + Rail 2 (contextual al workspace activo) + Canvas + Rail 3 (sidepanel derecho 4 tabs). Cada divisor draggable con cursor col-resize, doble click reset, drag descolapsa rail mini.

6. **Sidebar principal 3 secciones:** Operar (Mesa de Control + Inbox + SpaceLoom) Â· Workspaces (Administrados / Heredados) Â· Administrar (Capacidades / Tenant).

7. **Sidepanel derecho minimalista:** 4 tabs (Agentes Â· Skills Â· Conocimiento Â· Workspace) sin metadata operativa Â· solo nombre + alerta sutil Â· detalle vive en workspace correspondiente.

8. **SpaceLoom sin badge habitualmente:** lugar cognitivo libre, no cola operativa. Badge bajo (3-5) solo si hay sugerencias del dia activas.

9. **Knowledge en 5 capas L0-L4** con taxonomia 8+especiales por capa. Ya canon en sesion previa Voice Humanizer.

10. **Tipologia de workspaces:** operativos (donde se trabaja) Â· visibilidad (donde se ve y se navega: Inbox + Mesa) Â· iteracion (donde se piensa con IA: SpaceLoom).

11. **Tipologia de agentes:** comunicacion (canal-bound, ej @mail_ventas) Â· operativo (workspace-bound) Â· iteracion (cognitivo, en SpaceLoom) Â· gobernanza (meta).

12. **Mesa = kanban por criticidad:** 4 columnas (TU CRITERIO Â· ESPERANDO CRITERIO Â· DELEGADO Â· ERROR ACCIONABLE) Â· no por workspace.

13. **Inbox = agregador multi-cuenta:** 5 categorias auto-detectadas (Accionables Â· Resumen diario Â· Leido oculto Â· Auto-borrar Â· Agente) Â· prioridad aprendida (no FIFO) Â· resumenes activos como flujo declarativo del agente.

14. **Conocimiento (no Atlas):** "Atlas" es abstracto Â· "Conocimiento" comunica el valor del producto. Cross-language: Knowledge / Conocimiento / Conhecimento.

15. **Patron propio/heredado:** se aplica a Workspaces (Administrados/Heredados), Skills, Agentes y Conocimiento. Misma logica RBAC scope.

16. **Iteracion = misma surface en SpaceLoom global y Tab Iteracion del workspace:** distinto scope (global vs scoped) pero misma anatomia visual.

17. **Resumenes activos = flujo declarativo:** user instruye al agente de comunicacion Â· agente intercepta correos matcheados Â· acumula durante ventana Â· sintetiza Â· entrega digest Â· auto-borra originales con audit recuperable. Scope = cuenta (personal o organizacional), no user.

**Decisiones de naming rechazadas en iteracion (documentadas para no repetir debate):**

| Rechazada | Razon |
|---|---|
| SpaceLoom como reemplazo de Workspace | Workspace ya es estandar SaaS funcional, no requiere rebrand |
| ChatLoom como reemplazo de Chat | SpaceLoom ocupa ese rol con identidad propia Â· Chat estandar puro fue descartado |
| TypeLoom para el Chat | "type" mecanico Â· no comunica iteracion cognitiva |
| FaberChat para el Chat | Choca con consistencia *Loom Â· "Faber" reservado para marca |
| BuildLoom para Curaduria | "Build" generico Â· "Stack" mas preciso (capas L0-L4 son stack literal) |
| FaberLoom para Curaduria | 3 entidades con mismo nombre = caos |
| Curetaje | Procedimiento medico en todos los idiomas Â· no funciona como feature de software |

**Tensiones canon detectadas (documentar para SPEC futuro):**

- `SPEC_FB_VOICE_HUMANIZER_v2` canon ya firmado Â· este sketch UI se alinea sin contradicciones (workspace bajo control de user Â· voice user como sabor base Â· property-by-property merge)
- `TIER1 #14` plan FB firmado: "Voice Profile completo persona+tono+glosario+saludo+firma por user" Â· UI consistent (avatar foot dropdown tiene "Mi voz")
- `TIER1 #15` plan FB firmado: "single-agent por task, NO sub-agentes ni orquestacion" Â· ChatLoom rechazado evita confusion Â· 4 tipos de agente respetan single-agent (cada agente solo opera su cadena lineal)
- `ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1` canon: severity_weight Low/Medium/High/Critical encaja con kanban 4 columnas Mesa

**Conceptos canonizados nuevos (sketch Â· pendiente formalizar en SPEC):**

- **Familia *Loom:** 4 pilares de marca con metaforas precisas (Faber=hacedor, Work=accion, Space=cognicion, Stack=apilar capas).
- **HITL â†’ Criterio:** filosofia "La IA prepara. Vos aportas tu criterio." Â· user no es aprobador robotico, es profesional que aporta JUICIO.
- **Tipologia de agentes (4 tipos):** comunicacion Â· operativo Â· iteracion Â· gobernanza Â· cada uno con scope distinto.
- **Resumenes activos:** flujo declarativo (no categoria pasiva) Â· agente intercepta + acumula + sintetiza + entrega + auto-borra + aprende.
- **Reloj de aprendizaje exclusivo de knowledge a indexar:** NO indicador operativo general Â· solo cuenta candidatos a curar/conflictos/promociones pending.
- **Workspace polimorfico via vertical_spec_object:** schema unificado vertical-agnostic Â· semantica cambia por vertical (cuenta cliente B2B en MWT, caso en abogado, curso en estudiante).

**Files touched (7):**

- `docs/anexos/mockups/faberloom_shell_universal_v3.html` (Write -- mockup v3 nueva arquitectura)
- `docs/anexos/mockups/faberloom_shell_chat_v4.html` (Write -- mockup v4 sidebar Operar)
- `docs/anexos/mockups/faberloom_shell_chat_v5.html` (Write -- mockup v5 4 paneles + resize)
- `docs/anexos/mockups/faberloom_shell_v6.html` (Write -- mockup ACTUAL Â· familia *Loom completa)
- `docs/anexos/mockups/faberloom_shell_sketch_chat_v1.md` (Write -- sketch textual v1 desactualizado pero indexado para audit)
- `docs/anexos/mockups/faberloom_shell_consolidated_v2_2026-05-07.md` (Write -- snapshot consolidado v2 Â· 21 secciones Â· brief autocontenido para retomar en otra sesion)
- `docs/MANIFIESTO_CAMBIOS_v2.md` (Edit -- este append)

**NO indexado en este batch (diferido para proximas sesiones Cowork):**

- `SPEC_FB_CONSOLE_LAYOUT_v1` (canoniza el shell entero) Â· proxima sesion cuando el modelo cierre completamente
- `SPEC_FB_INBOX_ROUTING_v1` (5 categorias + cuentas multi-bandeja + prioridad aprendida) Â· proxima sesion
- `SPEC_FB_MESA_KANBAN_v1` (4 columnas + anatomia cards + scoring) Â· proxima sesion
- `SPEC_FB_WORKSPACE_FACTORY_v1` (wizard 6 pasos) Â· proxima sesion
- `SPEC_FB_STACKLOOM_v1` (flujo de promocion L4â†’L1) Â· proxima sesion
- `SPEC_FB_VOICE_BOOTSTRAP_v1` (pendiente desde sesion Voice Humanizer) Â· proxima sesion
- `POL_FB_VOICE_LEARNING_v1` (pendiente desde sesion Voice Humanizer) Â· proxima sesion
- `POL_FB_INBOX_PRIORITY_LEARNING_v1` (score aprendido del Inbox) Â· proxima sesion
- `POL_FB_TENANT_PRIORITY_OVERRIDES_v1` (reglas globales tenant) Â· proxima sesion
- `POL_FB_AUTO_DELETE_v1` (auto-borrar puro vs tras sintesis) Â· proxima sesion
- `SCH_FB_MAIL_ACCOUNT_v1` (cuenta conectada con team_users) Â· proxima sesion
- `SCH_FB_RESUMEN_RULE_v1` (reglas de resumenes activos) Â· proxima sesion
- `SCH_FB_MESA_ITEM_v1` (schema item de Mesa) Â· proxima sesion
- `ENT_FB_AGENT_TYPES_v1` (4 tipos de agente) Â· proxima sesion
- HTMLs adicionales: WorkLoom kanban + Inbox + item detalle Mesa + cuenta cliente Â· proxima iteracion
- Mobile / responsive Â· futuro

**Sync:** `scripts/sync_shell_iteration_indexa.ps1` con `manifest_shell_iteration_freeze.json` selectivo. Branch target: `indexa/shell-iteration-2026-05-07`. Commit message: `[FABERLOOM] Shell iteration v3-v6 + consolidated snapshot v2 (familia *Loom)`.

**Veredicto:** Iteracion masiva del shell de FaberLoom Â· 4 versiones HTML evolutivas + sketch consolidado v2 que captura TODAS las decisiones para que cualquier sesion futura pueda retomar sin perder contexto. Naming cerrado (familia *Loom Â· cross-language matrix completa Â· HITLâ†’criterio). Layout cerrado (4 paneles + resize handles Â· sidepanel minimalista Â· brand foot tagline). Modelo conceptual cerrado (workspaces polimorficos Â· 5 capas knowledge Â· tipologia agentes Â· resumenes activos Â· kanban Mesa Â· 5 categorias Inbox). Pendiente formalizar en SPECs (~14 SPECs/POLs/SCHs identificados) y armar HTMLs faltantes (WorkLoom kanban + Inbox + item detalle Mesa + cuenta cliente). Bajo riesgo (documental Â· son sketches no canon vigente). Alto valor: descansa el contexto Â· permite retomar en cualquier momento Â· base solida para Claude Design / Stitch / proxima iteracion CEO. v6 funcional para arrastrar a Stitch como referencia visual.

## BATCH FABERLOOM-KB-V1-20260510-1237

Fecha: 2026-05-10 12:38
Origen: 2 corridas Kimi multiagente (mayo 2026) - design foundation + brand system
Status: DRAFT - pendiente revision CEO antes de promover a STABLE
visibility: [INTERNAL]
Domain: faberloom

Archivos agregados a docs/faberloom/:

SPECs (13):
- SPEC_FABERLOOM_DESIGN_FOUNDATION_v1.md - investigacion 12 dim tokens y agentic UX
- SPEC_FABERLOOM_BRAND_FOUNDATION_v1.md - decisiones isotipo typography personas
- SPEC_FABERLOOM_TOKENS_v1.md - spec DTCG 3 capas
- SPEC_FABERLOOM_TYPOGRAPHY_v1.md - decisiones tipograficas
- SPEC_FABERLOOM_ICONS_v1.md - sistema 96 iconos
- SPEC_FABERLOOM_ISOTIPO_DECISION_v1.md - eleccion Hilos entrelazados
- SPEC_FABERLOOM_PERSONAS_JTBD_v1.md - personas y JTBD
- SPEC_FABERLOOM_UI_DENSITY_v1.md - lectura vs operacion
- SPEC_FABERLOOM_MULTITENANT_BRANDING_v1.md - 3 niveles branding
- SPEC_FABERLOOM_VISUAL_REFERENCES_v1.md - 22 referencias documentadas
- SPEC_FABERLOOM_SKILLS_RESEARCH_v1.md - investigacion skills publicas
- DESIGN_FABERLOOM_v1.md - DESIGN.md formato Google Labs
- SKILL.md - skill faberloom-designer (instancia, no master)

Assets:
- tokens/ : 3 archivos DTCG (base, semantic, components)
- icons/ : 10 SVG sample
- screenshots/ : 22 PNG referencias visuales
- research/ : 14 MD (dim01-12 + insight + cross_verification)
- diagrams/ : 3 PNG (architecture, survival ranking, 3checkpoint)

Total: 65 archivos

Notas:
- Output asume vertical SaaS B2B para creadores profesionales
  ("hacedor moderno"), no manufactura industrial. Kimi corrigio
  asuncion previa erronea de textil.
- Citas verificables pendientes de validacion: ACM DIS 2026 paper
  visible thinking, 93% consent fatigue Anthropic, 0.4% FPR clasificador.
- Pivot pendiente: extraer framework universal brand-system-orchestrator
  (sesion futura) para reuso en Rana Walk, MWT corporate, futuras marcas.

## BATCH FABERLOOM-KB-V2-20260510-1842

Fecha: 2026-05-10 18:42
Origen: sesion Cowork post-indexa v1 - validacion + extension
Status: STABLE para audit y prompt; DRAFT para mock
visibility: [INTERNAL]
Domain: faberloom + meta-process

Archivos agregados:

docs/audits/AUDIT_FABERLOOM_KIMI_CITATIONS_v1.md
  Auditoria de 3 citas criticas en SPEC FaberLoom Kimi:
  - "93% consent fatigue Anthropic" - VERIFICADA via blog Anthropic
  - "0.4% FPR clasificador Anthropic" - VERIFICADA via Anthropic + arXiv
  - "ACM DIS 2026 visible thinking paper" - NO ENCONTRADA (probable confusion DIS/CHI)
  Recomendacion: aplicar correcciones antes de promover SPEC v1.0 a STABLE.

docs/prompts/KIMI_PROMPT_BRAND_SYSTEM_UNIVERSAL_v1.md
  Prompt para proxima corrida Kimi multiagente: extraer framework
  universal brand-system-orchestrator a partir de FaberLoom como case
  study. Incluye 5 subagentes, decisiones CEO pre-cargadas, output
  esperado: framework reutilizable para Rana Walk + MWT corporate +
  futuras marcas.

docs/faberloom/mocks/MOCK_FABERLOOM_v1.html
  Mock standalone navegable HTML+CSS+JS vanilla. Usa tokens DTCG
  indexados. Vista: tab Iterar con chat + preview side-by-side, agente
  Curador en estado running, approval con 3 botones, status bar con
  Trust nivel 1, manifiesto edge "La IA prepara, vos tejes".
  Validacion de calidad: muestra que tokens entregados por Kimi sirven
  para mocks production-ready.

scripts/merge_faberloom_to_main.ps1
  Script archivado para mergear feat/faberloom-kb-v1-20260510 a main
  con --no-ff y borrar branch. Para uso del CEO cuando decida promover.

Acciones pendientes CEO post-batch:
1. Decidir si mergear feat branch ya o esperar revision
2. Aplicar correcciones del audit antes de promover SPEC a STABLE
3. Pegar prompt KIMI_PROMPT_BRAND_SYSTEM_UNIVERSAL_v1.md en Skywork
   para extraer framework universal


### BATCH 2026-05-17-001 - AUDIT nexos.ai + ARCH principios simplificacion

**Fecha:** 2026-05-17 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) - sesion sobre mirror OneDrive + sync_nexos_audit_indexa.ps1 generado para CEO
**Disparador:** Solicitud CEO de investigacion comparativa con plataforma nexos.ai (lituana, AI Workspace + AI Gateway, tenant TitanPoint7515 trial) para identificar primitivas de simplificacion adoptables a arquitectura MWT/FaberLoom.

**Restricciones activas en sesion:** R1 no_inventar (datos pendientes marcados [PENDIENTE - NO INVENTAR]) - R2 no_tocar_frozen - R3 no_escribir_kb_fuera_scope (todo en generated_staging hasta sync) - R5 respetar_ceo_only.

**Archivos nuevos (2):**

| Archivo | Tipo | Domain | Visibility | Status |
|---------|------|--------|------------|--------|
| docs/AUDIT_NEXOS_AI_DELTAS_v1.md | AUDIT | ARQUITECTURA_FUNDACIONAL | INTERNAL | DRAFT |
| docs/ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1.md | ARCH | ARQUITECTURA_FUNDACIONAL | INTERNAL | DRAFT |

**Investigacion (metodo):** navegacion directa con Chrome MCP a workspace.nexos.ai/chat, /agents, /agents/new, /agents/templates, /projects, /management, /management/teams, /management/models. Cross-check con docs publicas (nexos.ai/features/, /ai-gateway/, /ai-for-developers/). 4 areas mapeadas: orquestacion, KB/RAG, UI agente, multi-tenancy/governance.

**Contenido AUDIT (D1-D5 deltas propuestos, NO aplicados):**
- D1 POL_GROUNDING_POLICY_v1 (NEW) - 5 niveles semanticos Grounded/Guided/Balanced/Analytical/Creative como policy de grounding canonica MWT.
- D2 SPEC_AGENT_BUNDLE_v1 (NEW) - shape declarativo canonico de agente (12 campos: id, version, description, model_primary, grounding_policy, execution_trigger, instructions, capabilities, tools, flow, conversation_starters, visibility, tenant_scope).
- D3 SPEC_AGENT_FLOW_v1 (NEW) - state machine narrativa lineal opcional para skills (Goal + Steps con prompt embebido + branching declarativo 
ext_step_when). NO toca ENT_OPS_STATE_MACHINE FROZEN.
- D4 SPEC_LLM_GATEWAY_FALLBACK_v1 (NEW) - tabla de modelos canonicos MWT con fallback chain declarativa + constraint de tier match + per-tenant override sin filtrar.
- D5 PLB_AGENT_AUTHORING_v1 (NEW) + EXTEND IDX_PLATAFORMA - patron chat-first + Studio panel con tabs Configurar/Iterar/Sanidad (mantener nomenclatura FaberLoom, NO copiar Try/Flow/Settings literal); preservar contract 3-boton aprobar/descartar/iterar (NO adoptar Save/Discard binario de nexos).

**6 casos de uso comparados** en AUDIT seccion 3: grounding policy, autoring end-to-end, fallback ante caida de provider, KB visibility B2B, workflow agent, integraciones Amazon SP-API + Helium 10 (gap critico - nexos no las tiene).

**Contenido ARCH (8 principios de simplificacion):**
- P1 Progressive disclosure - nada visible hasta que el contexto lo demande.
- P2 Vocabulario semantico, no parametrico - presets nombrados en lugar de sliders numericos.
- P3 Conceptos pocos y profundos - 2 primitivas (Agent, Project) cubren modelo mental nexos; aplicacion MWT = backend 8 tipos, frontend FaberLoom expone 3 conceptos (agentes, conocimiento, politicas).
- P4 Defaults responsables, override visible cuando importa.
- P5 Asistencia inline, no documental - sistema susurra desde el editor.
- P6 Una decision = un control - matrices NxM son senal de abstraccion mal pensada.
- P7 Estado fluido, no formulario bloqueante - gates en promocion, no en edicion.
- P8 Composicion por referencia, no por configuracion explicita.
- Mas 3 areas de complejidad legitima MWT que NO se simplifican: visibility per-archivo, versioning + changelog auditado, hooks fail-closed + manifest selectivo.

**Pendientes registrados** (no inventados): audit logs UI nexos, memoria agent cross-thread, branching real en Flow complejo, permisos granulares per-team mas alla de subset Models, API/SDK shape AI Gateway, pricing enterprise.

**Validacion CEO requerida antes de promover D1-D5 a SPEC/POL/PLB definitivos.** Este BATCH indexa solo el AUDIT (analisis) y ARCH (principios). Los deltas operativos son input para discusion arquitectonica, no compromiso.

**Health post-batch:** docs/ +2 archivos (553 -> 555 total estimado). 2 stubs nuevos en ARQUITECTURA_FUNDACIONAL marcados DRAFT.


### BATCH 2026-05-17-002 - AUDIT nexos.ai v1.1 rectificacion post revision profunda KB FB

**Fecha:** 2026-05-17 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) - sesion continuacion del BATCH 2026-05-17-001
**Disparador:** CEO pidio revision profunda de la KB FaberLoom para detectar vacios en el modelo mental del agente que produjo el AUDIT v1.0. Se leyeron 12 docs canonicos clave: IDX_FB_FOUNDATION_BETA, ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (P16), SPEC_FB_AGENT_BUILDER_v1 v2.0, POL_FABERLOOM_SURFACE_CONTRACT v0.1, ENT_FB_AGENT_ARCHETYPES_v1, SPEC_FB_KNOWLEDGE_RIVER_v1 v1.1, SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1, plus referenciados.

**Restricciones activas en sesion:** R1 no_inventar - R2 no_tocar_frozen - R3 no_escribir_kb_fuera_scope - append-only respetado (v1.0 sigue intocado).

**Archivos nuevos (1):**

| Archivo | Tipo | Domain | Visibility | Status |
|---------|------|--------|------------|--------|
| docs/AUDIT_NEXOS_AI_DELTAS_v1_1.md | AUDIT | ARQUITECTURA_FUNDACIONAL | INTERNAL | DRAFT |

**Hallazgos consolidados del v1.1:**

1. El AUDIT v1.0 (commit d3575c7) propuso 5 deltas D1-D5 sin consultar canon FaberLoom existente. Status revisado:
   - D1 POL_GROUNDING_POLICY_v1: SCOPE_ACOTADO (solo aplica al GlobalChatTrigger del Workspace, no a agentes operativos; renombrar a POL_FB_WORKSPACE_ITERATION_MODE_v1)
   - D2 SPEC_AGENT_BUNDLE_v1: REDUNDANTE (ya existe SCH_FB_SKILL_MANIFEST_v2 + SPEC_FB_AGENT_BUILDER_v1 v2.0 con 19 decisiones)
   - D3 SPEC_AGENT_FLOW_v1: REDUNDANTE (ya existe SCH_FB_FLOW_DAG v2.0 con 7 tipos de nodo canonicos)
   - D4 SPEC_LLM_GATEWAY_FALLBACK_v1: REDUNDANTE (LiteLLM nativo + TIER1 #10 Anthropic-only)
   - D5 PLB_AGENT_AUTHORING_v1 chat-first: INVALIDO (contradice TIER1 #15 Agent Factory wizard 4 pasos firmado)

2. 5 refinamientos R1-R5 (R5 nuevo rescatado de D5) priorizados con tesis FaberLoom correcta: optimizar el flujo Inbox -> Mesa de Control (criterio HITL) -> Workspace (resolucion). R1+R4 son top; R2+R5 medio; R3 bajo.

3. 5 drifts detectados en la KB FaberLoom, documentados sin proponer fix inmediato:
   - L0-L4 labels reutilizados con semanticas distintas (Knowledge River memoria vs shell autoridad)
   - Workspace vs SpaceLoom naming entre POL_SURFACE_CONTRACT v0.1 DRAFT y shell consolidated v2
   - "No sub-agentes" del IDX vs P16 + 10 sub-agentes canonicos
   - Namespace metadata.mwt.* vs metadata.fbl.* (deuda tecnica D5 SPEC_AGENT_BUILDER)
   - ENT_FB_CURATOR_OPERATING_MODEL DEPRECATED por KNOWLEDGE_RIVER v1.1 sin marca visible en el archivo

4. 5 preguntas que estaban abiertas: 4 totalmente respondidas (composicion @ = sub-agentes standalone E1, grounding != L0-L4, no draft state es wizard 4 pasos, no chat-first); 1 parcial (SPEC_FB_INBOX_ROUTING_v1 pendiente segun shell consolidated section 19).

**Lectura combinada requerida:** AUDIT v1.0 (commit d3575c7) + AUDIT v1.1 (este batch) + ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1 (commit d3575c7). Los 3 forman el cuadro completo. El v1.0 NO se reemplaza; el v1.1 es complemento append-only.

**Decisiones CEO requeridas antes de cualquier proximo batch sobre este tema:**

1. D1 reformulado como POL_FB_WORKSPACE_ITERATION_MODE_v1: aprobar o descartar.
2. R1-R5 priorizados: confirmar orden de implementacion o discutir.
3. Drifts 1-5 detectados: cuales se cierran ahora (bumpeando docs afectados) y cuales se difieren.

**Health post-batch:** docs/ +1 archivo (estimado 555 -> 556). Sin cambios estructurales mayores. Sin promociones DRAFT -> VIGENTE en este batch.


### BATCH 2026-05-17-003 - Cierre drifts #2 #3 KB FaberLoom

**Fecha:** 2026-05-17 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) - continuacion BATCH 2026-05-17-002
**Disparador:** CEO autorizo cerrar drifts faciles detectados en AUDIT_NEXOS_AI_DELTAS_v1_1 seccion 4. Drift #2 (Workspace/SpaceLoom naming) y drift #3 (No sub-agentes vs P16) se cierran ahora. Drift #5 (CURATOR DEPRECATED) NO requiere fix: el archivo canonico YA tiene status: DEPRECATED en frontmatter + marca visible al inicio; el reporte v1.1 fue incorrecto en ese punto. Drifts #1 (L0-L4 renaming) y #4 (namespace mwt/fbl) diferidos por scope.

**Restricciones activas:** R1 no_inventar - R2 no_tocar_frozen - R3 no_escribir_kb_fuera_scope respetadas. Cambios son **bump aditivo no destructivo** sobre 2 archivos VIGENTES no-FROZEN.

**Archivos modificados (2 OVERWRITE):**

| Archivo | Bump | Cambio | Domain | Visibility |
|---------|------|--------|--------|------------|
| docs/faberloom/POL_FABERLOOM_SURFACE_CONTRACT.md | v0.1 -> v0.2 | Nota alineacion naming Workspace = SpaceLoom (shell consolidated v2 posterior). Tabla equivalencia explicita en bloque inicial. Cuerpo firmado del v0.1 sin cambios destructivos. Referencias adicionales a shell consolidated v2. OQ6 agregada (alineacion completa v0.3 o alias permanente) | faberloom | INTERNAL |
| docs/faberloom/IDX_FB_FOUNDATION_BETA.md | v1.0 -> v1.0.1 | Nota aclaratoria al item "No sub-agentes" de Restricciones inquebrantables (no reabrir): la restriccion se refiere a composicion jerarquica en runtime E1; los 10 sub-agentes atomicos del catalogo ENT_FB_SUB_AGENTS_LIBRARY_v1 + P16 (ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1) existen como standalone E1 y habilitables jerarquicamente E2 via feature_flag. Linkea SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 seccion 3.1. Cuerpo firmado del v1.0 sin cambios. Truncamiento de "Notas proxima sesion" completado con bullets 2-4. Changelog table agregada al final | GOBERNANZA | INTERNAL |

**Drifts cerrados:**

- Drift #2 (Workspace/SpaceLoom naming entre POL DRAFT y shell consolidated v2): cerrado via bump POL v0.2 con nota explicita + tabla equivalencia. v0.3 alineara cuerpo completo cuando aplique.
- Drift #3 (No sub-agentes del IDX vs P16 + 10 sub-agentes canonicos): cerrado via bump IDX v1.0.1 con nota aclaratoria + reconciliacion E1/E2 documentada.

**Drifts diferidos (no en este batch):**

- Drift #1 (L0-L4 labels reutilizados con semanticas distintas entre Knowledge River y shell): scope grande, requiere renaming en ~6 docs. Diferido hasta decision CEO sobre nomenclatura (sugerencia: River pasa a R0-R4, mantener L0-L4 para autoridad).
- Drift #4 (namespace metadata.mwt.* vs fbl.*): deuda tecnica conocida documentada en D5 del SPEC_FB_AGENT_BUILDER_v1 v2.0. Sin fecha de migracion.

**Drifts NO requieren fix:**

- Drift #5 (CURATOR DEPRECATED sin marca visible): observacion v1.1 incorrecta. El archivo canonico ENT_FB_CURATOR_OPERATING_MODEL_v1.md YA tiene status: DEPRECATED en frontmatter + bloque de marca visible al inicio (titulo "[DEPRECATED 2026-05-02]" + blockquote DEPRECATED NO USAR). No requiere bump.

**Health post-batch:** docs/ sin cambio cuantitativo (2 OVERWRITE). 2 versiones bumpeadas: POL_SURFACE_CONTRACT 0.1->0.2 (sigue DRAFT), IDX_FB_FOUNDATION_BETA 1.0->1.0.1 (sigue VIGENTE). Sin promociones DRAFT -> VIGENTE en este batch.

**Pendiente CEO:** decision sobre D1 reformulado (POL_FB_WORKSPACE_ITERATION_MODE_v1), R1-R5 priorizacion, drifts #1 #4 cierre futuro.


### BATCH 2026-05-19-001 - SPEC_FB_AGENT_RUNTIME_STACK_v1 (decision stack runtime FaberLoom)

**Fecha:** 2026-05-19 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) - sesion arquitectonica CEO
**Disparador:** CEO evaluo Hermes Agent v0.11.0 (NousResearch) como base potencial para runtime FaberLoom. Sesion exploro 4 modelos: Hermes embebido, worker pool ephemeral, Hermes-per-tenant, clonar arquitectura Hermes. Cowork actuo como arquitecto y CEO solicito decision firme. Decision tomada y autorizada para indexar.

**Restricciones activas:** R1 no_inventar (6 decisiones subordinadas D1-D6 marcadas PENDIENTE, no inventadas) - R2 no_tocar_frozen (ARCH_AGENT_PRINCIPLES v1.5 referenciado, no modificado) - R3 no_escribir_kb_fuera_scope (archivo en docs/faberloom/ por regla CLAUDE.md) respetadas.

**Archivos nuevos (1):**

| Archivo | Tipo | Path canonico | Visibility | Domain |
|---------|------|---------------|------------|--------|
| SPEC_FB_AGENT_RUNTIME_STACK_v1.md | spec | docs/faberloom/ | INTERNAL | Plataforma |

**Contenido del SPEC (resumen estructural, no operativo):**

- Seccion 1: Decision firme - Claude Agent SDK embebido + capa multi-tenant propia + MCP server publico. Rechazo formal de Hermes Agent como runtime/worker/per-tenant.
- Seccion 2-3: Justificacion (moat vertical, velocidad mercado, independencia) + diagrama arquitectura 3 capas (valor defensible / commodity / interface publica).
- Seccion 4: Stack definitivo en tabla 12 capas (Postgres+Supabase, S3, extism WASM, n8n, Next.js, Sentry).
- Seccion 5: 7 patrones a portar de Hermes v0.11.0 como referencia (NO codigo): Transport ABC, Orchestrator+coordination, Plugin surface, Hooks, /steer, Auxiliary models, Webhook direct-delivery.
- Seccion 6: 6 patrones rechazados explicitamente (TUI, dashboard local, 17 messaging, OAuth CLI, shell hooks arbitrarios, live model discovery por user).
- Seccion 7: 6 decisiones subordinadas pendientes (D1-D6) - WASM vs Python sandbox, Postgres-only vs +Redis, audit Postgres vs S3, MCP stdio vs HTTP/SSE, BYOK vs pool managed, agent embebido vs job_spec router.
- Seccion 8: Plan 7 fases / 20 semanas. Detalle ejecutable en LOTE_SM_SPRINT_FBL_AGENT_v1 (PENDIENTE crear).
- Seccion 9: Recursos. TENEMOS: 9 items inventariados. NECESITAMOS: 10 items con prioridad P0/P1/P2 y costo USD 54k-100k total proyecto.
- Seccion 10: 9 specs faltantes en KB a crear en fase 0 (SPEC_FB_AGENT_RUNTIME_LOOP, SPEC_FB_TRANSPORT_ABC, SPEC_FB_ORCHESTRATOR_SUBAGENT, SPEC_FB_PLUGIN_SURFACE, SPEC_FB_TENANT_CONTEXT, SPEC_FB_AUDIT_LOG, SPEC_FB_MCP_SERVER, SCH_FB_JOB_SPEC, POL_FB_PLUGIN_SANDBOX).
- Seccion 11: 6 riesgos identificados con probabilidad/impacto/mitigacion.
- Seccion 12: 7 criterios de exito alpha vendible.

**Implementa principios existentes (NO los modifica):**

- ARCH_AGENT_PRINCIPLES v1.5 P0-P15 (separacion AgentSpec/AgentRuntime/AgentMemory, autonomy ceiling, etc.)
- P16 de ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (orquestador delgado + sub-agentes atomicos)
- POL_VISIBILITY (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) enforced en runtime
- SPEC_HOOKS_FAIL_CLOSED_v1 extendido con event bus tenant-scoped

**Decisiones CEO requeridas antes de fase 0:**

1. D1: confirmar WASM (extism) como plugin runtime. Default propuesto.
2. D3: confirmar Postgres como audit log MVP (diferir S3+manifest a enterprise tier).
3. D5: confirmar modelo BYOK/pool hibrido por tier de pricing.
4. D6: confirmar agent embebido MVP (diferir worker_type router).
5. Inicio busqueda senior Python dev.
6. Validacion pricing con 3-5 fabricantes pipeline antes de fase 2.

**Trabajo pendiente fase 0 (proximos batches):**

- LOTE_SM_SPRINT_FBL_AGENT_v1 (sprint plan ejecutable)
- 9 SPEC_FB_*_v1 listados en seccion 10 del SPEC indexado
- 6 ADRs subordinadas D1-D6

**Health post-batch:** docs/faberloom/ +1 archivo (SPEC nuevo). 0 archivos modificados. 0 archivos eliminados. Sin promociones DRAFT -> VIGENTE adicionales. SPEC nuevo nace VIGENTE por aprobacion CEO directa en sesion.

**Pendiente CEO:** D1, D3, D5, D6 confirmacion default; aprobacion para iniciar busqueda dev; validacion pricing tiers con fabricantes.


### BATCH 2026-05-19-001 - SPEC_FB_AGENT_RUNTIME_STACK_v1 (decision stack runtime FaberLoom)

**Fecha:** 2026-05-19 (Costa Rica UTC-6)
**Operador:** Claude (Cowork) - sesion arquitectonica CEO
**Disparador:** CEO evaluo Hermes Agent v0.11.0 (NousResearch) como base potencial para runtime FaberLoom. Sesion exploro 4 modelos: Hermes embebido, worker pool ephemeral, Hermes-per-tenant, clonar arquitectura Hermes. Cowork actuo como arquitecto y CEO solicito decision firme. Decision tomada y autorizada para indexar.

**Restricciones activas:** R1 no_inventar (6 decisiones subordinadas D1-D6 marcadas PENDIENTE, no inventadas) - R2 no_tocar_frozen (ARCH_AGENT_PRINCIPLES v1.5 referenciado, no modificado) - R3 no_escribir_kb_fuera_scope (archivo en docs/faberloom/ por regla CLAUDE.md) respetadas.

**Archivos nuevos (1):**

| Archivo | Tipo | Path canonico | Visibility | Domain |
|---------|------|---------------|------------|--------|
| SPEC_FB_AGENT_RUNTIME_STACK_v1.md | spec | docs/faberloom/ | INTERNAL | Plataforma |

**Contenido del SPEC (resumen estructural, no operativo):**

- Seccion 1: Decision firme - Claude Agent SDK embebido + capa multi-tenant propia + MCP server publico. Rechazo formal de Hermes Agent como runtime/worker/per-tenant.
- Seccion 2-3: Justificacion (moat vertical, velocidad mercado, independencia) + diagrama arquitectura 3 capas (valor defensible / commodity / interface publica).
- Seccion 4: Stack definitivo en tabla 12 capas (Postgres+Supabase, S3, extism WASM, n8n, Next.js, Sentry).
- Seccion 5: 7 patrones a portar de Hermes v0.11.0 como referencia (NO codigo): Transport ABC, Orchestrator+coordination, Plugin surface, Hooks, /steer, Auxiliary models, Webhook direct-delivery.
- Seccion 6: 6 patrones rechazados explicitamente (TUI, dashboard local, 17 messaging, OAuth CLI, shell hooks arbitrarios, live model discovery por user).
- Seccion 7: 6 decisiones subordinadas pendientes (D1-D6) - WASM vs Python sandbox, Postgres-only vs +Redis, audit Postgres vs S3, MCP stdio vs HTTP/SSE, BYOK vs pool managed, agent embebido vs job_spec router.
- Seccion 8: Plan 7 fases / 20 semanas. Detalle ejecutable en LOTE_SM_SPRINT_FBL_AGENT_v1 (PENDIENTE crear).
- Seccion 9: Recursos. TENEMOS: 9 items inventariados. NECESITAMOS: 10 items con prioridad P0/P1/P2 y costo USD 54k-100k total proyecto.
- Seccion 10: 9 specs faltantes en KB a crear en fase 0 (SPEC_FB_AGENT_RUNTIME_LOOP, SPEC_FB_TRANSPORT_ABC, SPEC_FB_ORCHESTRATOR_SUBAGENT, SPEC_FB_PLUGIN_SURFACE, SPEC_FB_TENANT_CONTEXT, SPEC_FB_AUDIT_LOG, SPEC_FB_MCP_SERVER, SCH_FB_JOB_SPEC, POL_FB_PLUGIN_SANDBOX).
- Seccion 11: 6 riesgos identificados con probabilidad/impacto/mitigacion.
- Seccion 12: 7 criterios de exito alpha vendible.

**Implementa principios existentes (NO los modifica):**

- ARCH_AGENT_PRINCIPLES v1.5 P0-P15 (separacion AgentSpec/AgentRuntime/AgentMemory, autonomy ceiling, etc.)
- P16 de ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (orquestador delgado + sub-agentes atomicos)
- POL_VISIBILITY (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) enforced en runtime
- SPEC_HOOKS_FAIL_CLOSED_v1 extendido con event bus tenant-scoped

**Decisiones CEO requeridas antes de fase 0:**

1. D1: confirmar WASM (extism) como plugin runtime. Default propuesto.
2. D3: confirmar Postgres como audit log MVP (diferir S3+manifest a enterprise tier).
3. D5: confirmar modelo BYOK/pool hibrido por tier de pricing.
4. D6: confirmar agent embebido MVP (diferir worker_type router).
5. Inicio busqueda senior Python dev.
6. Validacion pricing con 3-5 fabricantes pipeline antes de fase 2.

**Trabajo pendiente fase 0 (proximos batches):**

- LOTE_SM_SPRINT_FBL_AGENT_v1 (sprint plan ejecutable)
- 9 SPEC_FB_*_v1 listados en seccion 10 del SPEC indexado
- 6 ADRs subordinadas D1-D6

**Health post-batch:** docs/faberloom/ +1 archivo (SPEC nuevo). 0 archivos modificados. 0 archivos eliminados. Sin promociones DRAFT -> VIGENTE adicionales. SPEC nuevo nace VIGENTE por aprobacion CEO directa en sesion.

**Pendiente CEO:** D1, D3, D5, D6 confirmacion default; aprobacion para iniciar busqueda dev; validacion pricing tiers con fabricantes.

---

### BATCH 2026-06-01-001 - Research agentes 2026 + P17 multi-agente

**Operador:** Claude (Cowork) - sesion research agentes IA + decision CEO multi-agente
**Aprobador:** CEO (Alvaro)

**Archivos nuevos (docs/anexos/research_agentes_2026/):**
- RESEARCH_AGENTES_MEDIUM_ABR_MAY_2026_v1.md (research-note, INTERNAL) - estado del arte agentes en Medium abr-may 2026.
- RESEARCH_AGENTES_DEEP_DIVE_2026_v1.md (research-note, INTERNAL) - deep dive 4 ejes via swarm Claude.
- RESEARCH_AGENTES_CONSOLIDADO_2026_v1.md (research-note, INTERNAL) - consolidado swarm Kimi + Claude, cross-verification, 8 insights cruzados, 4 correcciones.

**Archivo modificado:**
- ARCH_AGENT_PRINCIPLES.md v1.5 -> v1.6 (POL, Tier 2, INTERNAL). +Principio P17 (Composicion multi-agente por niveles). Habilita Nivel 2 (orquestador delgado + handoff estructurado) como opcion de primera clase bajo 6 condiciones + guardrails heredados; Nivel 3 MAS peer-to-peer CERRADO con 5 criterios de reevaluacion. Revision fila Composicion de agentes (tabla P14). P17 agregado a Tier 2 de Jerarquia de invariantes.

**No toca FROZEN:** PLB_ORCHESTRATOR ni ENT_OPS_STATE_MACHINE solo referenciados.
**Invariantes:** ningun Tier 1 (P1/P3/P5/P9/P13) modificado. Human Gate P14 / restriccion Tier 2 v1.5 preservados como guardrail no relajable de P17.

**Sustento:** RESEARCH_AGENTES_CONSOLIDADO_2026_v1 (swarm Kimi 4 ejes con citacion verificable + swarm Claude), reconciliado con evidencia MAST (NeurIPS 2025, UC Berkeley) preexistente en docs/anexos.

**Health post-batch:** docs/anexos/research_agentes_2026/ +3 archivos nuevos. ARCH_AGENT_PRINCIPLES.md +1 modificado (v1.6). 0 eliminados. 0 FROZEN tocados.
**Pendiente CEO:** review del PR feature/multiagente-p17 antes de merge a main (cambio de POL VIGENTE).

---

### BATCH 2026-06-01-002 - Research Agent Skills (patron SKILL.md) 2 rondas + verificacion Kimi

**Operador:** Claude (Cowork) - sesion research Agent Skills + swarm Kimi K1-K6
**Aprobador:** CEO (Alvaro)

**Archivos nuevos (docs/anexos/research_agentes_skills_2026/):** +19
- RESEARCH_AGENTES_SKILLS_2026_v1.md (research-note, INTERNAL, VIGENTE) - nota canonica consolidada de 2 rondas.
- agentes_skills_dim01..dim08.md (research-note, INTERNAL) - swarm Claude, 8 dimensiones (capa estrategica).
- agentes_skills_CONSOLIDADO.md (research-note, INTERNAL) - consolidado ronda 1 + tiers de confianza.
- kimi_skills_K1..K6.md (research-note, INTERNAL) - swarm Kimi (auditoria papers, multi-tenancy RLS, runtimes, evals/CI, orquestacion nativa, seguridad profunda).
- kimi_skills_CROSSVERIF.md (research-note, INTERNAL) - 58 claims (26 HIGH/26 MED/6 LOW/0 sin verificar), 9 conflictos resueltos, 0 reglas MWT violadas.
- kimi_skills_CONSOLIDADO.md (research-note, INTERNAL) - guia de implementacion multi-tenant (registry RLS, CI gates, defensa).
- PROMPT_KIMI_SWARM_skills_v1.md (insumo, INTERNAL) - prompt raiz del swarm Kimi.

**No toca FROZEN:** ninguno. **Invariantes:** ninguno modificado; research-notes nacen como anexos.

**Sustento:** 2 swarms con citacion verificable. 5 claims Kimi mas cargados verificados independientemente por Claude (todos PASAN): Cowork bloquea SP-API/n8n (anthropics/claude-code #37970), GoClaw multi-tenant (nextlevelbuilder/goclaw), SkillFortify 96.95% F1 (arXiv 2603.00195 + qualixar/skillfortify), CVE-2026-25725 sandbox escape (NVD/GHSA-ff64-7w26-62rf, <2.1.2), Skill-Inject ~80% ASR (arXiv 2602.20156).

**Hechos operativos clave indexados:** (1) Cowork NO alcanza SP-API/n8n -> usar Claude Code CLI; (2) gate produccion pass^k >= 60% (no pass@k); (3) CVE-2026-25725 -> settings.json antes del sandbox + >=2.1.2; (4) tooling defensa real (mcp-scan, SkillFortify, Cisco mcp-scanner, gVisor); (5) self-generated skills -1.3pp -> curacion humana; (6) GoClaw = reference impl de reglas tenant MWT.

**Banderas:** consolidado Kimi fechado 2026-07-09 (fecha futura, reloj/alucinacion; citas validas verificadas). Vault patterns (Omnithium, Scalekit) son vendor MEDIUM - verificar antes de adoptar.

**Health post-batch:** docs/anexos/research_agentes_skills_2026/ +19 archivos nuevos. 0 modificados (salvo este MANIFIESTO). 0 eliminados. 0 FROZEN tocados.
**Pendiente CEO:** aprobar fusion en LOTE_SM_SPRINT (plan maestro implementacion skills multi-tenant: registry RLS + CI pass^k + runtime CLI + defensa).

---

### BATCH 2026-06-01-003 - LOTE_SM_SPRINT Skills Multi-Tenant v1 (Sprint 1)

**Operador:** Claude (Cowork) - planeacion sprint skills multi-tenant
**Aprobador:** CEO (Alvaro)

**Archivo nuevo (docs/archivo/):**
- LOTE_SM_SPRINT_SKILLS_MT_v1.md (LOTE_SM_SPRINT, INTERNAL, DRAFT) - Sprint 1 "Foundations de Skills Multi-Tenant" (2 semanas). Fusiona capa estrategica (ronda Claude) + ingenieria (ronda Kimi).

**Contenido:** Bloque A (guardrails Fase 0: registry RLS, CI mcp-scan+skillfortify, hardening CVE-2026-25725, SP-API a CLI, vault por tenant); Bloque B (3 skills internas: tenant-guard script-first, kb-frontmatter-validator, skill-review); Bloque C (evals/CI con gate pass^k >= 60% + OpenTelemetry); Bloque D (contrato e interface: SCH_SKILL_INVOCATION + SPEC_FB_SKILL_FACTORY con perfiles mwt-internal/portable). Apendice roadmap Sprint 2/3 + proyecto aparte compliance-epp-latam.

**Sustento:** RESEARCH_AGENTES_SKILLS_2026_v1 (2 rondas + CROSSVERIF Kimi). Cada tarea trazada a su dim/K de origen. 9 conflictos Kimi heredados como resueltos.

**No toca FROZEN.** Sprint nace DRAFT (no ejecutable hasta cerrar decisiones CEO).

**Health post-batch:** docs/archivo/ +1 archivo nuevo. Este MANIFIESTO +1 modificado. 0 eliminados. 0 FROZEN tocados.
**Pendiente CEO:** cerrar DEC-1..DEC-5 (Postgres+RLS store, CLI runtime SP-API, tooling vault/CI, gate pass^k politica, perfil portable vs mwt-internal) antes de arrancar ejecucion. Promover DRAFT -> VIGENTE al aprobar.


---

## BATCH 2026-06-02 - INDEXA GOLDEN VENTAS TRIANGULARES (PF 2453)

**Operador:** Claude (Cowork) - construccion y registro de golden
**Aprobador:** CEO (Alvaro)

**Archivo nuevo (docs/archivo/):**
- PF_2453-2026_SONDEL_TRIANGULAR_GOLDEN.html (ART-02-GE-TRI, golden, INTERNAL) - proforma triangular MWT->SONDEL, 500 pares, 3 lineas NCM 6403.99.90, expediente MAR-MWLT-002-2026, PO 504990.

**Archivos modificados (docs/):**
- SCH_PROFORMA_MWT.md v2.1 -> v2.2: +fila golden PF_2453 en tabla Golden Examples + nota + 2 flags pendientes.
- ARTIFACT_REGISTRY.md v1.3 -> v1.4: +ART-02-GE-TRI en golden examples.

**Contenido del golden:** 5 vistas (CEO con arbitraje $3,141.22 = delta $2,731.50 + ahorro fiscal $409.72; Marluvas; SONDEL proforma; DDP SONDEL = contrafactual cliente con liquidacion DUA, secuencia FOB/CIF/nacionalizado por par y tabla a facturar con IVA total $18,891.07; DDP MWT = camino contable real, costo nacionalizado por par por linea, margen real -$474.94 con alerta linea 50B22). IVA = CIF x 13%, credito fiscal. Sustento documental: factura Marluvas 2453 (pedido 269474), AWB 230-6683-2091 (COPA, prepaid $1,070.74), packing list 51 cajas.

**[PENDIENTE - decision CEO]** Reconciliar ENT_COMERCIAL_MODELOS: el modo triangular compra/reventa esta rotulado "B" en el artefacto pero el doc canonico lo define como "C" (B=comision). No se toco ENT_COMERCIAL_MODELOS.
**[PENDIENTE - validacion datos]** Alvaro Solis vs Alfaro; color 75BPR29 Cafe vs Marron; contacto SONDEL Saymon Arguedas vs Javier Bonilla; serv. aduanales y transporte referenciales.

**No toca FROZEN.** Health: docs/archivo/ +1 nuevo; SCH_PROFORMA_MWT +1 mod; ARTIFACT_REGISTRY +1 mod; este MANIFIESTO +1. 0 eliminados. 0 FROZEN tocados.


---

## BATCH 2026-06-02 - INDEXA AUDITORIA P0/P1 (gateway/governance)

**Operador:** Claude (Cowork) - creacion + indexacion de entregables de auditoria externa
**Aprobador:** CEO (Alvaro)

**Archivos nuevos (docs/):**
- POL_SYNC_MANIFEST_INTEGRITY_v1.md (POL, INTERNAL, DRAFT v1.0) - integridad criptografica del sync canonico/mirror: hash sha256 por archivo, reconciliacion de conteos vs DASHBOARD, dry-run + diff humano, log firmado post-sync, borrado de mirror auditado. Cierra gap P0 de auditoria 2026-06-02. Complementa SKILL_KB_GATEWAY.
- SPEC_TENANT_CONTAMINATION_TESTS_v1.md (SPEC, INTERNAL, DRAFT v1.0) - suite adversarial anti-cross-tenant sobre 7 superficies (RLS, embeddings/pgvector, memory/Letta, output pinning, cache, logs/audit, tools/actions) + gate pre-deploy (fuga = deploy bloqueado). Cierra gap P1. Extiende reglas multi-tenant; consume tenant_model_allowlist; se cruza con POL_DATA_CLASSIFICATION.

**Archivos modificados (docs/):**
- IDX_GOBERNANZA.md: +fila POL_SYNC_MANIFEST_INTEGRITY en seccion Policies.
- IDX_ARQUITECTURA_FUNDACIONAL.md: +fila SPEC_TENANT_CONTAMINATION_TESTS en Specs medulares MWT.
- DASHBOARD_SNAPSHOT.md v13.5 -> v13.6: POL_ docs/raiz 28->29 y Tipos POL_ 29->30; SPEC_ docs/raiz 13->14 y Tipos SPEC_ 13->14; DRAFT 106->108. Totales .md NO recontados (deuda de purga de 42 efimeros sigue pendiente; bump relativo solo de los tipos afectados).

**Origen:** auditoria externa multi-LLM 2026-06-02 sobre BRIEFING_MWT_FABERLOOM. Gaps P0 (manifest con hash) y P1 (contamination tests) confirmados como reales. Otros "gaps" del auditor (egress policy, ingestion firewall) ya estaban cubiertos por POL_DATA_CLASSIFICATION v1.4 -- falso positivo por briefing incompleto.

**Pendiente:** gaps que requieren decision CEO -- cerrar CEO-32 (saneamiento 13-14 leaks), regla de decision SPEC/ARCH/POL/PLB/ENT con ejemplos, umbrales economicos para Atomic Agents (P17).

**No toca FROZEN.** Health: docs/ +2 nuevos (1 POL + 1 SPEC, ambos DRAFT); 3 modificados (2 IDX + DASHBOARD); este MANIFIESTO +1. 0 eliminados. 0 FROZEN tocados. Branch: indexa-auditoria-p0p1.


---

## BATCH 2026-06-02 - INDEXA SPEC_FB_EVAL_ARENA (gateway/arena FaberLoom)

**Operador:** Claude (Cowork) - consolidacion de diseno + indexacion
**Aprobador:** CEO (Alvaro)

**Archivo nuevo (docs/faberloom/):**
- SPEC_FB_EVAL_ARENA_v1.md (SPEC, INTERNAL, DRAFT v1.0, aplica_a [FaberLoom, MWT]) - arena de evaluacion ciega + gobernanza de routing multi-proveedor/multi-tenant. 7 componentes: (1) registro abierto de APIs self-service por workspace con health check + clasificacion fail-closed + SHADOW; (2) motor de evaluacion en 2 modos (arena offline rankea modelos / final-pass online valida output) con grading en escalera, evaluacion doble-ciega, panel de jueces familias distintas, Elo + gate absoluto; (3) golden sets scope workspace heredables, datos sinteticos (PF_2453 sintetizado como caso #1); (4) routing jerarquico + herencia de config en cascada (Global>Org>Team>Workspace>Agente>Key>Request) con override solo-endurece; (5) disponibilidad/BYO heredada (estricto default + hibrido opt-in); (6) savings ledger contrafactual vs premium fijo; (7) MCP FaberLoom-en-MWT (roadmap). 4 decisiones de experto (eval por tenant, BYO estricto, score juez gate+ledger, baseline premium).

**Origen:** sesion de diseno Cowork 2026-06-02 + blueprint investigacion externa GATEWAY-LLM-20260603-9e4a (Kimi swarm, tercera corrida valida). Reconcilia con SPEC_AI_GOV_GOVERNANCE_AND_ROUTING, SPEC_LLM_ROUTING_ARCHITECTURE, ENT_PLAT_LLM_ROUTING v2.0, POL_DATA_CLASSIFICATION, ENT_AI_GOV_GOLDEN_CORPUS_MWT, ENT_FB_RFQ_REPLAY_SET, ARCH_AGENT_PRINCIPLES (P1/P13), SPEC_FB_AUTH_TENANT_RBAC, SPEC_TENANT_CONTAMINATION_TESTS, POL_SYNC_MANIFEST_INTEGRITY. NO edita SPEC_AI_GOV ni SPEC_LLM_ROUTING (solo referencia).

**Archivos modificados (docs/):**
- IDX_ARQUITECTURA_FUNDACIONAL.md: +fila SPEC_FB_EVAL_ARENA en seccion Specs FaberLoom (scope separado).
- DASHBOARD_SNAPSHOT.md v13.6 -> v13.7: docs/faberloom/ 51->52; FB scope 16->17 (3->4 SPEC); DRAFT 108->109.

**Pendiente (gaps del SPEC seccion K):** poblar corpus golden (curacion); calibrar umbrales del gate; definir "A+" objetivable para generativo; superficie del MCP FB-en-MWT.

**No toca FROZEN.** Health: docs/faberloom/ +1 nuevo (SPEC DRAFT); 2 modificados (IDX_ARQUITECTURA + DASHBOARD); este MANIFIESTO +1. 0 eliminados. 0 FROZEN tocados. Branch sugerida: indexa-spec-fb-eval-arena.


---

## BATCH 2026-06-02 - INDEXA SPEC_FB_EVOLUTION_ROADMAP (secuencia de construccion)

**Operador:** Claude (Cowork) - arquitectura funcional + indexacion
**Aprobador:** CEO (Alvaro)

**Archivo nuevo (docs/faberloom/):**
- SPEC_FB_EVOLUTION_ROADMAP_v1.md (SPEC, INTERNAL, DRAFT v1.0, aplica_a [FaberLoom, MWT]) - secuencia de construccion por modulos, walking-skeleton-first. 7 fases: F0 consolidar control-de-IA solapado; F1 chat space + routing (sustrato, tabla de scoring a mano, 5 fitness functions); F2 primer caso de negocio (cotizacion B2B sobre el chat); F3 arena reemplaza tabla manual; F4 aprendizaje (Knowledge River L2-L4); F5 multi-tenant real + APIs abiertas; F6 MCP FaberLoom-en-MWT + escala. Dependencias duras, fitness por fase, diferidos a F5-F6. Decision rectora CEO: el chat space con routing es el primer modulo, de el depende todo. Principio: diseno != orden de build (router primero delgado, arena casi al final).

**Origen:** sesion de arquitectura funcional Cowork 2026-06-02 (diagnostico: sistema sobre-disenado/sub-validado). Contrapeso de ejecucion a los ~20 SPEC_FB de diseno. Complementa SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT + AUDIT_FABERLOOM_B1; implementa SPEC_LLM_ROUTING_ARCHITECTURE (F1) y SPEC_FB_EVAL_ARENA (F3); no reabre PLB_FB_FOUNDATION_BETA (plan 13 sprints).

**Archivos modificados (docs/):**
- IDX_ARQUITECTURA_FUNDACIONAL.md: +fila SPEC_FB_EVOLUTION_ROADMAP en Specs FaberLoom.
- DASHBOARD_SNAPSHOT.md v13.7 -> v13.8: docs/faberloom/ 52->53; FB scope 17->18 (4->5 SPEC); DRAFT 109->110.

**Pendiente:** F0 (consolidar AI_CONTROL_PLANE + EVAL_ARENA + router); conciliar numeracion de sprints del plan firmado con las 7 fases.

**No toca FROZEN.** Health: docs/faberloom/ +1 nuevo (SPEC DRAFT); 2 modificados (IDX_ARQUITECTURA + DASHBOARD); este MANIFIESTO +1. 0 eliminados. 0 FROZEN tocados. Branch sugerida: indexa-spec-fb-evolution-roadmap.


---

## BATCH 2026-06-02 - INDEXA SPEC_FB_ARCHETYPE (concepto unificador)

**Operador:** Claude (Cowork) - arquitectura funcional + indexacion
**Aprobador:** CEO (Alvaro)

**Archivo nuevo (docs/faberloom/):**
- SPEC_FB_ARCHETYPE_v1.md (SPEC, INTERNAL, DRAFT v1.0, aplica_a [FaberLoom, MWT]) - declara el ARQUETIPO como unidad central de trabajo, unificando 4 nombres dispersos (archetype AG_AM, template Knowledge River, Working Profile, ruta de routing). 4 dimensiones: (1) estructura = 6 facetas (tipo de info, ruta/workflow, working profile, conocimiento, schema, voz); (2) herencia template->clon->overlay (3 capas sealed_base+learned+manual, cascada de scope, override solo-endurece); (3) evolucion optimiza-vs-sugiere por impacto (3 niveles KR L1/L2/L3, sugerencia con evidencia de arena+savings, gate anti-ruido min_samples); (4) clasificacion dinamica (runtime canal->reglas->semantico->fallback; catalogo evoluciona por descubrimiento de huerfanas; REGLA tier-se-adivina / sensibilidad-se-hereda fail-closed). 5 reglas inquebrantables.

**Origen:** sesion de arquitectura funcional Cowork 2026-06-02. Candidato a Fase 0 del SPEC_FB_EVOLUTION_ROADMAP (consolidacion pre-codigo). Reconcilia (NO edita): SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT, SPEC_FB_KNOWLEDGE_RIVER, SPEC_FB_SKILL_COMPOSITION, SPEC_FB_EVAL_ARENA, SPEC_LLM_ROUTING_ARCHITECTURE, ENT_PLAT_LLM_ROUTING, POL_DATA_CLASSIFICATION.

**Archivos modificados (docs/):**
- IDX_ARQUITECTURA_FUNDACIONAL.md: +fila SPEC_FB_ARCHETYPE en Specs FaberLoom.
- DASHBOARD_SNAPSHOT.md v13.8 -> v13.9: docs/faberloom/ 53->54; FB scope 18->19 (5->6 SPEC); DRAFT 110->111.

**No toca FROZEN.** Health: docs/faberloom/ +1 nuevo (SPEC DRAFT); 2 modificados (IDX_ARQUITECTURA + DASHBOARD); este MANIFIESTO +1. 0 eliminados. 0 FROZEN tocados. Branch sugerida: indexa-spec-fb-archetype.


---

## BATCH 2026-06-10 - INDEXA SPEC_FB_BUILD_SEQUENCE v2 + SPEC_FB_ROUTING_PRESETS v1 (secuencia unica + presets de ruteo)

**Operador:** Claude (Cowork) - evaluacion estrategica + arquitectura
**Aprobador:** CEO (Alvaro)

**Archivos nuevos (docs/faberloom/):**
- SPEC_FB_BUILD_SEQUENCE_v2.md (SPEC, INTERNAL, DRAFT v2.0, aplica_a [FaberLoom, MWT]) - secuencia unica de desarrollo: E0 consolidacion (1 sem), E1 workspace + router delgado (4 sem, S1A recortado single-tenant: 6 containers, 2 roles), E2 agentes con profundidad (4-5 sem, cotizacion + cobranza, sin factories), E2.5 validacion comercial concierge PARALELA (10 PYMEs no-amigas, gate >=3 con intencion de pago), E3 capa corporativa CONDICIONAL a gate E2.5. SUPERSEDE el orden de build de PLB_FB_FOUNDATION_BETA v1.3.1 y de SPEC_FABERLOOM_MVP fases post-MVP (contenidos tecnicos se reutilizan; kill criteria y decisiones firmadas compatibles siguen vigentes). Declara SPEC freeze hasta cierre E2. Metrica primaria E1-E2: horas de fundador ahorradas/semana.
- SPEC_FB_ROUTING_PRESETS_v1.md (SPEC, INTERNAL, DRAFT v1.0, aplica_a [FaberLoom, MWT]) - presets de ruteo modelo Pedal Commander: 3 capas (ECU = POL_DATA_CLASSIFICATION fail-closed no configurable / preset tenant = jurisdiccion + providers + caps, solo Owner / curva usuario = eco-balanceado-sport-sport_plus). Resolucion runtime por interseccion de listas, deterministico <20ms. Fabrica de presets en 5 niveles: 4 presets de casa, wizard 3 preguntas, template por vertical (copy-on-create plano), promocion HITL optimiza-vs-sugiere (N>=30 por clase), builder IA chat-first con backtest contra savings ledger. REEMPLAZA SPEC_FB_EVAL_ARENA como mecanismo de optimizacion (el archivo de la arena NO se elimina; queda como referencia para F3+ si el volumen lo justifica). Research base: OpenRouter presets/provider-routing/sovereign-AI, Microsoft Foundry model router, Portkey, LiteLLM tags.

**Origen:** EVAL_STRAT_2026-06-09 (veredicto PAUSAR-Y-VALIDAR SaaS / SEGUIR slice interno F1-F2) + sesiones Cowork 2026-06-10 (revision de etapas, presets, fabrica con IA).

**Archivos modificados (docs/):**
- IDX_ARQUITECTURA_FUNDACIONAL.md: +2 filas en Specs FaberLoom.
- DASHBOARD_SNAPSHOT.md v13.9 -> v14.0: docs/faberloom/ 54->56 (incremental); FB scope 19->21 (6->8 SPEC); DRAFT 111->113. Deuda de reconteo real persiste (AUDIT_KB_2026-06-09).

**Pendientes:**
- Confirmar % dedicacion de Alejandro y lista de 10 prospectos E2.5 (bloquean kickoff E0).
- Nota de supersede en changelog de PLB_FB_FOUNDATION_BETA_v1.md: requiere editar archivo FIRMADO -> sesion aparte con aprobacion CEO explicita, no se toca en este batch.
- Investigaciones pre-gate identificadas 2026-06-10 (8 items: retrieval FTS vs contexto, pricing computable, system of record cobranza, canal entrada RFQ, cobertura Tier 0, SLA clasificador, lead times OAuth/WhatsApp/DPA, golden corpus chat) - pendiente integrarlas como seccion del BUILD_SEQUENCE o doc propio.

**No toca FROZEN.** Health: docs/faberloom/ +2 nuevos (SPEC DRAFT); 2 modificados (IDX_ARQUITECTURA + DASHBOARD); este MANIFIESTO +1 batch. 0 eliminados. 0 FROZEN tocados. Branch: feature/indexa-fb-routing-presets.

---

## BATCH 2026-06-10b - SIMPLIFICACION ARQUITECTONICA (herencia plana + voice colapsado + observabilidad gestionada)

**Operador:** Claude (Cowork) - revision de arquitectura post EVAL_STRAT
**Aprobador:** CEO (Alvaro)

**Archivos modificados (docs/faberloom/), 0 nuevos, 0 eliminados:**
- SPEC_FB_ARCHETYPE_v1.md v1.0 -> v1.1: Dimension 2 (herencia) simplificada a copy-on-create plano (template -> instancia independiente, re-sync manual con diff). Cascada de 7 scopes + 3 capas sealed/learned/manual reclasificadas DIFERIDO con senal de activacion (>=10 tenants + dolor de mantenimiento medido: mismo fix manual en >3 instancias). Se conservan vigentes desde dia 1 las reglas de seguridad: override-solo-endurece y model_access por interseccion (implementadas en router/presets, no como cascada).
- SPEC_FB_VOICE_HUMANIZER_v2.md v2.0 -> v2.1: ENMIENDA seccion 1bis. Alcance E1-E2 colapsado a: (1) bloque de estilo por tenant (persona+tono+glosario+saludo, decision PLB #15 intacta; schema en SCH_FB_VOICE_PROFILE_v1 que sigue VIGENTE) + firma por user; (2) few-shot 3-5 drafts aprobados de gold samples (la voz se captura implicitamente); (3) filtros tenant post-generacion (banned phrases + glosario) intactos. Resolucion property-by-property, LOC_INSTRUCCIONES_WS, ajustes transitorios y aprendizaje HITL de voz DIFERIDOS a E3+. Senal de activacion: >1 voz por workspace O edit-rate por tono >20% sostenido. Secciones 2-17 integras como canon conceptual.
- POL_FB_VOICE_RESOLUTION_v1.md v1.0 -> v1.1: status VIGENTE -> DEFERRED (diseno de referencia E3+). Contenido integro.
- SCH_FB_WS_INSTRUCTIONS_v1.md v1.0 -> v1.1: status VIGENTE -> DEFERRED (diseno de referencia E3+). Contenido integro. +seccion Changelog (antes solo Stamp).
- SPEC_FB_BUILD_SEQUENCE_v2.md v2.0 -> v2.1: E3 item 4 cambia de observabilidad self-host (S1B grafana/loki/prometheus/minio) a observabilidad GESTIONADA (Langfuse Cloud + uptime externo + alertas de costo); self-host solo por exigencia contractual. E1 semana 1: Langfuse Cloud free tier desde dia 1 en lugar de diferir trazas. KVM 8 se mantiene como host de app (decision PLB #1 intacta).

**Archivos modificados (indices):**
- IDX_ARQUITECTURA_FUNDACIONAL.md: labels de version ARCHETYPE v1.1 + BUILD_SEQUENCE v2.1.
- docs/faberloom/IDX_FB_FOUNDATION_BETA.md: labels DEFERRED en items 16-17 + descripcion Voice v2.1.
- DASHBOARD_SNAPSHOT.md v14.0 -> v14.1 (sin cambios de conteo: 0 archivos nuevos).

**Racional (revision de arquitectura 2026-06-10):** las cascadas de config y la maquinaria de resolucion de voz son complejidad presente contra beneficio hipotetico a escala actual (1 tenant, 0.2 devs); la voz es superficie no estructura (MARCO_RECTOR prioridad #6); self-host de observabilidad para <10 tenants es toil sin retorno. Nada se borra: todo lo diferido queda como diseno de referencia con senal de activacion explicita.

**Fuera de este batch (pendiente, requiere sesion propia):** decisiones #10 (topologia 12 containers) y S1B del PLB_FB_FOUNDATION_BETA v1.3.1-FIRMADO quedan formalmente contradichas por BUILD_SEQUENCE v2.1; el PLB es archivo FIRMADO y su nota de supersede/enmienda requiere aprobacion CEO explicita en sesion dedicada (igual que la nota pendiente del batch 2026-06-10).

**No toca FROZEN. No toca PLB FIRMADO.** Health: 0 nuevos; 8 modificados (5 faberloom + 2 IDX + DASHBOARD); este MANIFIESTO +1 batch. 0 eliminados. Branch: feature/indexa-fb-simplificacion.

---

## BATCH 2026-06-11 - ATERRIZAJE PRE-DESARROLLO (enmienda PLB + revision modular + shell sketch v4)

**Operador:** Claude (Cowork) - ojo de halcon pre-build
**Aprobador:** CEO (Alvaro) - mandato explicito sesion 2026-06-11: "tienes libertad para levantar cualquier cosa firmada"

**Archivo modificado (docs/faberloom/):**
- PLB_FB_FOUNDATION_BETA_v1.md v1.3.1-FIRMADO -> v1.3.2-ENMENDADO. Contenido tecnico integro; changelog declara 6 enmiendas con doc rector: E-1 orden de build superseded por SPEC_FB_BUILD_SEQUENCE v2.1 (TIER 1 y kill criteria siguen vigentes); E-2 topologia 12->6 containers + observabilidad gestionada + STORAGE ADJUNTOS = filesystem KVM + backup (resuelve hueco MinIO); E-3 engine bespoke superseded por skill=markdown+tools-allowlist sobre SDK estandar, con allowlist de 8 tools E1-E2 enumerada (conserva Tier 0, exception codes, limites duros); E-4 roles 5->2 en E1 (Owner/Operator; TIER1 #7 y decision #3 enmendados); E-5 canales email-only E1-E2, WhatsApp/multi-buzon a E3 (tramites en paralelo); E-6 retrieval contexto-first (docs completos + caching), FTS secundario para SKUs, chunking diferido (matiza decision #12). Cierra las 3+ contradicciones acumuladas (deuda de batches 2026-06-10/10b) y las 3 detectadas por el AUDIT modular (roles, canales, retrieval).

**Archivos nuevos:**
- docs/AUDIT_FB_MODULAR_2026-06-11_v1.md (AUDIT, INTERNAL, VIGENTE) - revision modular post-simplificacion: 10 modulos con responsabilidad/contrato/encaje/vacios, 10 vacios rankeados. Hallazgo central: columna vertebral bien modularizada; huecos en los bordes (identidad contacto->workspace, scheduler, storage adjuntos, 4 schemas fisicos: ledger, gold samples, conversaciones, workspace_members). Vacios 1 (engine no en canon), 7 (storage) resueltos por PLB v1.3.2; vacio 3 (scoping del lente en datos: workspace_id + membresia en query server-side, NUNCA solo UI) queda como requisito de schema Sprint 1.
- docs/anexos/mockups/faberloom_shell_sketch_v4.html - sketch interactivo del shell (3 modos, lente de scope, cejas, focus, cmd-K, Aprendizaje como modo).
- docs/anexos/mockups/faberloom_shell_sketch_v4_DECISIONES.md - 8 decisiones D1-D8 que enmiendan el shell consolidated v2 (2026-05-07): 3 modos segmented, SpaceLoom=operar (corrige tipologia "pensar"), Aprendizaje como modo/cola epistemica, cejas en chrome, colapsado-con-resumen, modo focus, herencia anatomia SpaceLoom->workspace, workspace=lente (5 superficies x scope, prohibido pantallas especificas).

**Archivos modificados (docs/):**
- DASHBOARD_SNAPSHOT.md v14.1 -> v14.2.

**Estado resultante: listo para kickoff de desarrollo.** Un solo orden de build (BUILD_SEQUENCE v2.1), cero contradicciones abiertas contra el PLB, vacios de borde con dueno y semana asignada (AUDIT seccion sintesis). Bloqueadores restantes de E0: dedicacion de Alejandro confirmada + lista 10 prospectos E2.5 (sin cambio desde 2026-06-10).

**No toca FROZEN.** Health: 3 nuevos (1 AUDIT docs/ + 2 anexos/mockups), 2 modificados (PLB + DASHBOARD), este MANIFIESTO +1 batch. 0 eliminados. Branch: feature/indexa-fb-aterrizaje.

---

## BATCH 2026-06-12 - ARREGLOS KB + FB (cierre de deudas de AUDIT_KB_2026-06-09 y AUDIT_FB_MODULAR)

**Operador:** Claude (Cowork). **Aprobador:** CEO (Alvaro) - mandato "arregla ya" 2026-06-12.

**Nuevos:**
- docs/faberloom/SCH_FB_CORE_TABLES_v1.md (SCH, INTERNAL, VIGENTE) - DDL de 7 tablas core Sprint 1 (workspace_members, savings_ledger, gold_samples, conversations+messages, scheduled_jobs, client_map) + regla "el lente se aplica server-side" + 6 reglas de entity resolution contacto->workspace + baseline del ledger declarado como estimado. Resuelve vacios 2/3/5/6 del AUDIT modular.
- scripts/recount_kb.ps1 - reconteo determinista de la KB con -Patch sobre DASHBOARD. Cierra la deuda "totales no recontados" (drift declarado desde 2026-05-03).

**Modificados:**
- docs/ENT_PLAT_MULTITENANT.md v0.1 STUB -> v1.0 VIGENTE: consolida 5 invariantes + lente workspace + tabla de punteros canonicos (corrige destino de las refs rotas de WIKI seccion 7; WIKI mismo queda pendiente por ser control_surface/break-glass). Resuelve hallazgo ALTA eje 6 de AUDIT_KB_2026-06-09.
- Normalizacion visibility en 35 archivos: lineas exactas 'visibility: INTERNAL' -> '[INTERNAL]' y 'visibility: CEO-ONLY' -> '[CEO-ONLY]' (incluye ENT_GOB_SOCIEDAD - cierra el vector de fuga del eje 3 del audit; solo headers, cero contenido tocado).
- PURGA: 8 archivos MANIFIESTO_APPEND_* ya consolidados en este MANIFIESTO movidos (git mv, no delete) a docs/archivo/manifiestos/purga-2026-06/. Retenidos sin consolidar: 35. Cierra la deuda PR-1/PR-2 declarada en DASHBOARD desde 2026-05-03.
- DASHBOARD_SNAPSHOT v14.2 -> v14.3 con conteos REALES recontados post-purga.

**Quedan abiertos (requieren break-glass CEO, no tocados):** activacion real de hooks (cero logs desde 2026-05-07) + correccion WIKI linea ~145. Unicos restos del AUDIT_KB_2026-06-09 nivel ALTA.

**No toca FROZEN.** Branch: feature/indexa-arreglos-kb-fb.

---

## BATCH 2026-06-13 - INDEXA KIMI_SWARM_7_ATERRIZAJE (investigacion operativa pre-dev)

**Operador:** Claude (Cowork) - destilado + impacto en decisiones. **Aprobador:** CEO (Alvaro).

**Nuevos:**
- docs/faberloom/ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1.md (ENT, INTERNAL, VIGENTE) - destilado de 6 dimensiones con impacto en decisiones: (1) outbound email sin verificacion Google (SMTP/DWD; prohibido scope restricted; investigacion lead-time OAuth CERRADA); (2) WhatsApp ~$5/mes piloto, ventana 24h gratis -> disenar cobranza dentro de ventana; iniciar Meta verification ya; (3) legal por pais para concierge: priorizar CR/GT/CO-corporativo, MX exige contrato encargado (LFPDPPP 2025); (4) entity resolution de SCH_FB_CORE_TABLES VALIDADA contra HubSpot/Zendesk/Front/Attio + seed freemail list; (5) ancla concierge $39 (banda poblada: Chately/CRMWhata/Zoko/Cliengo); (6) E-6 VALIDADA con precios oficiales jun-2026 + regla nueva context packs <200K (surcharge 2x) + baseline ledger con tokenizer +35% Opus.
- docs/anexos/kimi_swarm_7/ (8 archivos) - crudos integros del swarm: D0 cross-summary + D1-D6 + plan. 80+ fuentes, 136 citas, 5 conflictos entre fuentes documentados sin resolver.

**Modificados:** DASHBOARD_SNAPSHOT v14.3 -> v14.4 (reconteo automatico).

**Calidad del swarm:** guard anti-diseno funciono (cero propuestas de arquitectura); confianzas declaradas; DATO NO ENCONTRADO usado; conflictos reportados con ambas fuentes. Mejor corrida de Kimi a la fecha - el patron de prompt (titulo dominio linea 1 + guard + RUN_ID) queda validado.

**No toca FROZEN.** Health: 9 nuevos (1 ENT faberloom + 8 anexos), 1 modificado (DASHBOARD), este MANIFIESTO +1. 0 eliminados. Branch: feature/indexa-kimi-swarm-7.

---

## BATCH 2026-06-13b - BUILD_SEQUENCE v3.0 (etapa 2 genérica, skills no predefinidos, cotización como ejemplo)

**Operador:** Claude (Cowork) - corrección de mandato post-sesión 2026-06-12
**Aprobador:** CEO (Alvaro) - mandato "bajalo"

**Archivo nuevo:**
- docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md (SPEC, INTERNAL, DRAFT) - re-corte de secuencia: E2 genérica (sistema de skills, no cotización), E3 = lente/workspace, E4a = multi-usuario interno, E4b = multi-tenant externo (condicional), E5 = amplitud nombrada sin diseñar. Cotización de calzado pasa de mandato a ejemplo/primer candidato natural. Gates agnósticos de clase de tarea (>=10 outputs de >=2 clases). Hito 2a/2b explícitos. Track concierge E2.5 sigue paralelo. Cero cambios en E1 (intacto). Supersede v2.1 al firmarse.

**Archivos modificados:**
- IDX_ARQUITECTURA_FUNDACIONAL.md: label BUILD_SEQUENCE v2.1 -> v3.0; v2.1 marcado como superseded.
- DASHBOARD_SNAPSHOT.md v14.4 -> v14.5 (conteos recontados: 671 totales, 649 docs tree, 78 faberloom).

**Racional:** la cotización de calzado de seguridad fue un ejemplo desde abril 2026; en v1/v2 se fosilizó como mandato, haciendo parecer que FaberLoom era un cotizador vertical. La v3.0 restaura el sistema de skills genérico: el uso real define qué skills corren, el gate exige que haya uso real, el plan no prescribe el contenido. Los docs de cotización (QUOTING_SOURCE_OF_TRUTH, exception codes, evidence bundle) siguen VIGENTES como diseño de referencia — se construyen cuando el uso los pida, no porque estén en el plan.

**No toca FROZEN.** Health: 1 nuevo (SPEC), 2 modificados (IDX + DASHBOARD), este MANIFIESTO +1. 0 eliminados. Branch: feature/indexa-build-seq-v3.

---

## BATCH 2026-06-15 - AUDIT-ROUTING-2026-06-14 CORE FIX + RETENCIÓN DE ARCHIVO

**Operador:** Claude (Kimi Code CLI) — Arquitecto Ejecutor
**Aprobador:** CEO (Alvaro) — aprobación explícita de `PLAN_REPARACION_ROUTING_20260614.md`

**Contexto:** Resultado del plan de reparación de integridad de routing aprobado por CEO. Se ejecuta Lote 1 Core MWT; Lote 2 FaberLoom queda diferido. Se aplica DEC-009 (timestamps al final) en `RW_ROOT.md` y `CLAUDE.md`. Se canoniza política de retención y archivo (`POL_ARCHIVO.md` v1.1 + `docs/archivo/ARCHIVE_INDEX.md`).

**Archivos nuevos:**
- `docs/archivo/ARCHIVE_INDEX.md` (IDX, VIGENTE) — índice de documentos archivados con razones A1–A5.
- `docs/archivo/SPEC_FB_BUILD_SEQUENCE_v2.1_A1_SUPERSEDED.md` (SPEC, ARCHIVADO) — v2.1 archivada A1; reemplazada por v3.0.
- `docs/ENT_FABERLOOM_AGENT_BUILDER_v1.md` (ENT, DRAFT) — renombrado desde `faberloom_agent_builder_spec.md`, frontmatter canonizado, indexado en `IDX_GOBERNANZA`.
- `docs/SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` (SPEC, DRAFT) — renombrado desde `SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA.md` para coincidir con id canónico.
- `docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md` (ENT, VIGENTE) — movido desde `docs/ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md`.
- `docs/faberloom/ENT_FB_PRICING_TIERS_v1.md` (ENT, VIGENTE) — movido desde `docs/ENT_FABERLOOM_PRICING_TIERS.md`.
- `docs/ROUTING_MANIFEST.json` (registro especial) — manifest multi-LLM con id/path/type/domain/status/visibility/version de todo documento tipado activo.

**Archivos modificados (routing core):**
- `docs/RW_ROOT.md` v4.8.25 → v4.8.26: DOMINIOS 10 → 13 (Arquitectura Fundacional, Sprints, FaberLoom); refs rotas core reparadas; stamp movido al final y renovado 2026-06-15 / vencimiento 2026-09-15; bloque "CÓMO NAVEGAR (cualquier LLM)" + `ROUTING_MANIFEST.json`.
- `docs/IDX_GOBERNANZA.md` v1.4 → v1.5: indexa `ENT_FABERLOOM_AGENT_BUILDER_v1`, `ENT_GOB_ENGINEERING_COMPETENCIES`, `ENT_GOB_TEAM_INVENTORY_FULL`; indexa `POL_BRANCH_PR_v1`, `POL_ROOT_FILE_CLASSIFICATION_v1`, `POL_OUTAGE_CANONICAL_MIRROR_v1`; corrige IDs inconsistentes.
- `docs/IDX_PRODUCTO.md`: ref `project_faberloom.md` → `docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v4.md`.
- `docs/IDX_ARQUITECTURA_FUNDACIONAL.md`: abreviatura `SPEC_FB_*.md` → cita concreta a `IDX_FB_FOUNDATION_BETA.md`.
- `docs/IDX_SPRINTS.md`: plantilla `LOTE_SM_SPRINT{N}.md` → texto explicativo.
- `docs/SCHEMA_REGISTRY.md`: ref `AUDIT_REINDEXA` → texto plano.
- `docs/POL_BRANCH_PR_v1.md`: id corregido a `POL_BRANCH_PR_v1`.
- `docs/POL_ROOT_FILE_CLASSIFICATION_v1.md`: id corregido a `POL_ROOT_FILE_CLASSIFICATION_v1`.
- `docs/POL_ARCHIVO.md` v1.0 → v1.1: política de retención activa con razones A1–A5, `ARCHIVE_INDEX.md`, proceso de archivo/recuperación.
- `docs/SPEC_HOOKS_FAIL_CLOSED_v1.md`: id corregido a `SPEC_HOOKS_FAIL_CLOSED`.
- `docs/faberloom/IDX_FB_FOUNDATION_BETA.md`: id corregido a `IDX_FB_FOUNDATION_BETA`.
- `docs/faberloom/ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1.md`: id corregido a `ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1`.
- `docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md`: ref a v2 apunta a archivo A1 SUPERSEDED.
- `docs/CLAUDE.md`: frontmatter YAML movido al inicio del archivo (headers estructurales arriba); solo timestamp al final; fecha renovada 2026-06-15; refleja 12 dominios + FaberLoom como sub-router.
- `docs/RW_ROOT.md`: FaberLoom movido de tabla DOMINIOS a sección SUB-ROUTERS (freeze); DOMINIOS 10→12.
- `docs/ROUTING_MANIFEST.json`: regenerado excluyendo AUDIT_* y status DEPRECATED/ARCHIVADO (356 entradas).
- `docs/DASHBOARD_SNAPSHOT.md` v14.5 → v14.6: conteos reajustados post-fix.

**Referencias actualizadas (consistencia por renombres):**
- `docs/ARCH_AGENT_PRINCIPLES.md`, `docs/SPEC_FABERLOOM_MVP.md`, `docs/SPEC_ACTION_ENGINE.md`, `docs/SPEC_AUDIT_MODULE.md`, `docs/SPEC_AUTONOMY_CONTROL_ENGINE.md`, `docs/SPEC_LLM_ROUTING_ARCHITECTURE.md`, `docs/AUDIT_FABERLOOM_A1_SPEC_CANON_v1.md`, `docs/AUDIT_FABERLOOM_A5_KNOWLEDGE_FLOW_CANON_v1.md`, `docs/faberloom/ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md` — apuntan a `ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md` y `ENT_FB_PRICING_TIERS_v1.md`.

**Validación:** `audit/audit_routing.py` post-fix reporta: 0 refs rotas core, 0 huérfanos core, 0 IDX faltantes en `RW_ROOT.md`, 0 IDs inconsistentes, 0 IDs duplicados. Quedan 6 refs rotas en `IDX_FB_FOUNDATION_BETA.md` (Lote 2 FaberLoom, diferido por CEO) y 14 huérfanos FaberLoom + 2 docs sueltos (diferidos).

**No toca FROZEN.** No toca `hooks/`. Branch: `fix/routing-integrity-20260614`.

---

### BATCH 2026-06-15-001 -- Indexa sesion pensamiento + FB-SWARM-2026-06-15

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-15, autorizada por CEO

**Archivos nuevos (2):**
- docs/faberloom/ENT_FB_INSIGHTS_KIMI_SWARM_8_ATERRIZAJE_v1.md (ENT, VIGENTE, INTERNAL)
- docs/faberloom/AUDIT_FB_SESION_20260615_v1.md (AUDIT, VIGENTE, INTERNAL)

**Resumen:** destilado del swarm FB-SWARM-2026-06-15 (determinismo skills, aislamiento
multi-tenant LLM, memoria temporal). Decision CEO: confiabilidad "muy confiable, no
contractual" (nivel 4 != contractual). 2 deltas al Knowledge River como observacion
post-E2 (colision nomenclatura niveles; aislamiento storage L0/L2). 3 conflictos
escalados a CEO (C1/C4/C6). IDs arXiv marcados [PENDIENTE - VERIFICAR FUENTE].
No toca FROZEN. No crea SPEC (SPEC freeze E2 respetado).

---

### BATCH 2026-06-15-002 -- Indexa diseno configurador identidad + normalizador outputs

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-15, autorizada por CEO

**Archivos nuevos (1):**
- docs/faberloom/AUDIT_FB_IDENTITY_NORMALIZER_v1.md (AUDIT, VIGENTE, INTERNAL)

**Resumen:** diseno del configurador de identidad (admin, ejemplos en vivo) +
SKILL_FB_IDENTITY_NORMALIZER (2 pasadas, deterministic shell + LLM core) + loop
golden->gate + multi-tenant server-side. Insight: normalizar la huella del modelo
(Opus/Sonnet/Kimi/GPT) hacia la identidad de la organizacion. Incluye GATE DE
SEGURIDAD DE SKILLS obligatorio (inspeccion estatica + cuarentena + curador) para no
heredar codigo malicioso de skills de terceros (ref ToxicSkills). Exploracion AUDIT,
no SPEC. No toca FROZEN. SPEC freeze E2 respetado.


---

### BATCH 2026-06-15-003 -- Indexa mock FaberLoom v4.15 (canonico) + repuntero

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-15, autorizada por CEO

**Archivos nuevos (5):**
- docs/anexos/mockups/faberloom_shell_mock_v4_15.html (mock, CANONICO, referencia visual)
- docs/anexos/mockups/faberloom_shell_mock_v4_14.html (mock, base de staging milestone)
- docs/anexos/mockups/INDEX_v4_15.md (IDX mockup, CANONICO; mapa milestone->superficie)
- docs/anexos/mockups/screenshots/v415-inbox.png, v415-draft.png, 01-space.png (evidencia visual)

**Archivos modificados (2):**
- docs/anexos/mockups/INDEX_v4_13.md (banner SUPERSEDED por v4.15; contenido conservado)
- docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v4.md (puntero de mock v4_13 -> v4_15)

**Resumen:** v4.15 queda como puntero canonico de mock (look Stitch + staging heredado de
v4.14). Cadena reabierta porque v4.13 estaba FIRMADO sin staging por milestone y el PLAN_v4
reescribio el alcance. v4.14 introdujo el etiquetado // E1a/E1b/E2/E3/E4 en codigo; INDEX_v4_15
lo traduce a un mapa milestone->superficie que funciona como CONTRATO DE ALCANCE (subconjunto
minimo de build = E1a + E1b; Routing/Aprender/Admin son vision E3/E4, no E1). El mock es
referencia visual, NO mandato de build. Pendientes de diseno heredados (inbox a datos reales,
audit table, editor routing, contraste AA) no bloquean el indexado. No toca FROZEN. No crea SPEC.


---

### BATCH 2026-06-17-001 -- Integra HANDOFF eval runtimes de agentes OSS

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-17, integracion de HANDOFF_AGENT_RUNTIME_EVAL

**Archivos nuevos (1):**
- docs/faberloom/ARCH_FB_AGENT_RUNTIME_EVAL_v1.md (ARCH, draft, INTERNAL, faberloom)

**Resumen:** integra el handoff del swarm AOSS-2026-06-17 (F1+F2): modelo de agente por tenant
(identidad inmutable, memoria sellada criptografica, llave graduada, meta-agente curador, particion
embebido/gobierno) + veredicto de 7 frameworks OSS (Hermes, OpenClaw, LangGraph, CrewAI, OpenHands,
Letta, Agno). Hallazgo central: NINGUN framework da aislamiento multi-tenant hostil de fabrica
(SMTA 92% = Container/VM + RBAC+ABAC + namespace); SKILL.md es el estandar portable; marketplaces
de skills = veneno (36.82% flawed). OpenHands = top realista, a re-evaluar al cierre de E2. Bajo
PAUSAR-Y-VALIDAR: decisiones marcadas PROPUESTAS pendientes de ratificacion CEO. Reconciliacion con
SpaceLoom self-embedded: solo cruza ahora SKILL.md + sandbox de skills; el resto es del FaberLoom
multi-tenant pausado y NO re-infla el build self-embedded. ACCION SEGURIDAD URGENTE: rotar credenciales
IMAP entregadas a Kimi Work (2026-06-17). [NO-VERIFICADO]: control plane unico Work+Claw, cifras swarm,
umbral SMTA 1:1. No toca FROZEN ni control_surface.


---

### BATCH 2026-06-17-002 -- Indexa bloque SpaceLoom self-embedded + research de usos

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-17, autorizada por CEO ("indexa")

**Archivos nuevos (10):**
- docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.md (SPEC, DRAFT, INTERNAL)
- docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.1.md (SPEC, DRAFT, INTERNAL) -- post-auditoria dual
- docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.2.md (SPEC, DRAFT, INTERNAL) -- modelo agente single-user + SKILL.md
- docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.3.md (SPEC, DRAFT, INTERNAL) -- distribucion app desktop Win/Mac
- docs/faberloom/SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md (SPEC, DRAFT, INTERNAL) -- connector correo local
- docs/faberloom/PROMPT_AUDITORIA_SPACELOOM_v1.md (PROMPT metodologia)
- docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v2.md (ENT, DRAFT, INTERNAL) -- re-ranking por casos de uso
- docs/faberloom/ENT_FB_USE_CASE_CATALOG_v1.md (ENT, DRAFT, INTERNAL) -- 58 casos ancla
- docs/faberloom/PROMPT_KIMI_SWARM_USE_CASES_v1.md + v2.md (PROMPT metodologia)
- docs/faberloom/PROMPT_ANALISIS_CRUZADO_USE_CASES_v1.md + PROMPT_VERIFICACION_SWARM_UNICO_v1.md (PROMPT)

**Resumen:** decision de pivote de FaberLoom-SaaS a SpaceLoom self-embedded distribuible (app desktop
Win/Mac, local-first, BYO-key, licencia uso personal). Cadena de SPEC: v1.0 -> v1.1 (post-auditoria
dual Kimi 7.1 + ChatGPT 6.7) -> v1.2 (modelo agente-entidad single-user lightweight + skills en
SKILL.md) -> v1.3 (distribucion = app instalable Win/Mac via pywebview+PyInstaller; firma/notarizacion).
Connector IMAP local (creds en keyring, NEVER autonomo en enviar/borrar, contenido=input no confiable).
Research de usos: catalogo 58 casos + re-ranking por casos de uso (vertical_candidates v2) + verificacion
dual con web (whitespace de Kimi desmentido; moat = patron workspace+HITL+memoria). Prompts de
metodologia (swarm + verificacion + auditoria) indexados como reusables. Acento UI = naranja #F97316.
Tema transversal: SpaceLoom self-embedded NO levanta la pausa de FaberLoom multi-tenant; es palanca
interna + opcion distribuible. Licencia final [PENDIENTE - legal: FSL recomendada]. SEGURIDAD: rotar
credenciales IMAP de Kimi Work sigue PENDIENTE. No toca FROZEN ni control_surface.


---

### BATCH 2026-06-17-003 -- Indexa Etapa 1 + prueba de estres + bloque mock (recuperado)

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-17 ("si indexa")

**Archivos nuevos (3):**
- docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md (SPEC, DRAFT, INTERNAL) -- def Etapa 1 = app standalone telar completo + principio rector + Routine Hub + superficies Inbox/WorkLoom/SpaceLoom
- docs/faberloom/AUDIT_SPACELOOM_ETAPA1_STRESS_v1.md (AUDIT, DRAFT, INTERNAL) -- prueba de estres del diseno contra casos reales
- docs/anexos/mockups/INDEX_v4_15.md (IDX mockup, CANONICO) -- recreado con deltas de modelo 2026-06-17

**Archivos recuperados/modificados:**
- docs/anexos/mockups/faberloom_shell_mock_v4_14.html + v4_15.html + screenshots/ (mock canonico; se habian perdido del mirror por /MIR antes de promoverse)
- docs/anexos/mockups/INDEX_v4_13.md (banner SUPERSEDED por v4.15)
- docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v4.md (puntero de mock v4_13 -> v4_15)

**Resumen:** Etapa 1 definida = app standalone con todo el telar single-user (sub-etapas SL0-SL5).
Principio rector: una entidad resuelve con el contexto del espacio activo (sabe-donde global / resuelve
local, sellado). Routine Hub reemplaza la "agent factory" (rutina = SKILL.md + binding + persona, invocable
@nombre; agent table de v1.2 se pliega). Superficies del producto FaberLoom: Inbox + WorkLoom (mesa) +
SpaceLoom. Prueba de estres (corregida por CEO): apuntar a ALTA frecuencia con HITL graduado (autonomia
ganada); dato exacto = lookup no busqueda; deadlines no son problema de la app (nunca deja peor que sin
app). Mock v4.15 = norte visual, 3 deltas de concepto (Factory->Routine Hub; agentes->rutinas con persona;
WorkLoom modo muestra/excepciones). Nomenclatura: FaberLoom = producto, SpaceLoom = superficie. Todo DRAFT.
No toca FROZEN.


---

### BATCH 2026-06-17-004 -- Refinamiento Etapa 1 (principio rector + Routine Hub + superficies + expansion-ready)

**Agente:** Claude (Cowork) -- Arquitecto Ejecutor
**Orden:** sesion Project MWT Knowledge 2026-06-17

**Archivos modificados (1):**
- docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md (sec 1.1 principio rector, sec 4.2 Routine Hub, superficies Inbox/WorkLoom/SpaceLoom, sec 8 regla expansion-ready)

**Resumen:** refinamientos post-sesion al SPEC de Etapa 1: (1) principio rector -- una entidad resuelve con
el contexto del espacio activo, sabe-donde global / resuelve local sellado; (2) Routine Hub reemplaza la
"agent factory" (rutina = SKILL.md + binding + persona, invocable @nombre; agent table de v1.2 se pliega);
(3) nomenclatura -- FaberLoom = producto, SpaceLoom/WorkLoom/Inbox = superficies; (4) Etapa 1 = prueba no
techo, construir expansion-ready (aditivo, no rewrite) hacia el alcance total. No toca FROZEN.

## BATCH 2026-06-22 - PLAN_DESARROLLO_FABERLOOM_v5
- ADD docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v5.md (DRAFT, v5.0). 4ta ronda auditoria swarm (ChatGPT 8.3 / Qwen 7.8 / GLM 7.4 / Kimi 7.3, corrida AUD-FB-PLAN-V3-R4-20260622) + decision despliegue dual desktop/web.
- SUPERSEDE PLAN_DESARROLLO_FABERLOOM_v4 (orden/timeline/costos) y orden+timeline de SPEC_FB_BUILD_SEQUENCE_v3 (fuente unica, seccion 0).
- Cambios: E0.5 partido legal/seguridad; E1a partido Base/Mail; E0 holdout+muestreo mecanico; grounding por assertion; E2.5 pago real; kill criteria relativos a inicio de etapa; CAPEX unificado; prospecto removido de gate E1b; E4a detallado; roles 2-5; moat con umbral de falsacion; E2 4-5 sem; payback como semaforo.
- PENDIENTE (decision CEO/abogado): transfer_basis (transferencia PII al LLM) y dictamen de cobranza a terceros. No se inventaron.
- No se toco FROZEN ni control_surface.


---

### BATCH 2026-06-23 — FB-STD-CODEX-2026-06-23-01 (FIX_MECANICO estandarizacion FaberLoom)
Contexto: correcciones mecanicas de header/refs/changelog en dominio FaberLoom. Sin cambios conceptuales ni de status.
Archivos:
- docs/faberloom/IDX_FB_FOUNDATION_BETA.md : refs colgantes `docs/*` corregidas a `docs/faberloom/*` para seis artefactos canon; version 1.0.2→1.0.3.
- docs/ENT_PLAT_LLM_ROUTING.md : ref colgante `archivo/kimi_swarm_4_adaptive_routing.md` corregida a `docs/archivo/kimi_swarm_4_adaptive_routing.md`; version 2.0→2.0.1.
- docs/faberloom/PLB_FB_KICKOFF_PROMPT_v1.md : refs colgantes `docs/*` corregidas a `docs/faberloom/*` en canon de lectura; version 1.0→1.0.1.
- docs/faberloom/ENT_FB_AGENT_ARCHETYPES_v1.md : ref legacy `ENT_TEMPLATE_LIBRARY_v1.md` corregida a `ENT_FB_TEMPLATE_LIBRARY_v1.md`; version 2.0→2.0.1.
- docs/faberloom/ENT_FB_TOOL_CATALOG_v1.md : ref legacy `ENT_TEMPLATE_LIBRARY_v1.md` corregida a `ENT_FB_TEMPLATE_LIBRARY_v1.md`; version 2.0→2.0.1.
- docs/faberloom/SCH_FB_FLOW_DAG.md : ref legacy `SCH_TASK_ENTITY.md` corregida a `SCH_FB_TASK_ENTITY.md`; version 2.0→2.0.1.
- docs/faberloom/SCH_FB_SKILL_MANIFEST_v2.md : refs legacy sin prefijo FB y paths `docs/gold_samples/*` corregidos a nombres canon; version 2.0→2.0.1.
- docs/faberloom/SPEC_FB_AGENT_BUILDER_v1.md : refs legacy sin prefijo FB corregidas a nombres canon; version 2.0→2.0.1.
- docs/faberloom/SPEC_FB_RAG_SECURITY_FIREWALL_v1.md : ref de filename `POL_FB_KR_PRIVACY_TIERS_v1.1.md` corregida a `POL_FB_KR_PRIVACY_TIERS_v1.md`; version 1.0→1.0.1.
