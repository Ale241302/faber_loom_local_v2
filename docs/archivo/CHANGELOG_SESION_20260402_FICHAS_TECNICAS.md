# CHANGELOG_SESION_20260402_FICHAS_TECNICAS

Fecha: 2026-04-02
Sesión: Fichas Técnicas Rana Walk — tecnologías, ejes evaluación, paleta de color, ratings CEO
Agente: Claude (Opus) — Arquitecto Ejecutor
Duración: sesión completa (context window agotado al 65%)

---

## 1. ARCHIVOS APLICADOS AL PROYECTO

### ENT_TECH.md — v0.1 → v1.0 (REEMPLAZADO)
- Reescritura completa con copy aprobado CEO
- 7 tecnologías documentadas (antes 6):
  - LeapCore, Arch System, ThinBoom, ShockSphere, NanoSpread, PORON® XRD®, **Orca Tail (NUEVA)**
- Corrección: **Orbis sin Arch System** — composición pasa de 3 a 2 tecnologías
- Arch System productos: de "GOL, ORB, MAN" a "GOL, MAN"
- Sección C: composición por línea con conteo actualizado
- Sección D: matriz tecnología × producto (7×7) corregida
- Sección E nueva: 6 ejes de evaluación (escala 1-10) con definiciones + ratings oficiales CEO
- Status: VIGENTE · Stamp: 2026-04-02

### LOC_TECH_EN.md — STUB → v1.0 (REEMPLAZADO)
- 7 descripciones de tecnología traducidas al inglés
- Ejes de evaluación traducidos (Thin↔Thick, Soft↔Firm, etc.)
- Status: VIGENTE

### LOC_TECH_PT.md — STUB → v1.0 (REEMPLAZADO)
- 7 descripciones de tecnología traducidas al portugués
- Ejes de evaluación traducidos (Fina↔Grossa, Maciez↔Firmeza, etc.)
- Status: VIGENTE

### LOC_TECH_ES.md — STUB → v1.0 (REEMPLAZADO)
- Referencia a ENT_TECH como fuente canónica ES
- Status: VIGENTE

### MANIFIESTO_APPEND_20260402_FICHAS_TECNICAS.md (NUEVO)
- Log de todos los cambios de esta sesión
- 4 decisiones CEO registradas (DEC-TECH-01 a 04)

---

## 2. ARCHIVOS GENERADOS (en outputs, no aplicados al proyecto aún)

### PATCH_ENT_PROD_EJES_20260402.md
- 8 operaciones str_replace para aplicar en próxima sesión:
  - ENT_PROD_ORB: fix C1/C2 (remover Arch System)
  - 7× ENT_PROD: reemplazar C4 legacy por 6 ejes nuevos

### rw_fichas_tecnicas_v2.jsx
- Artifact React con fichas técnicas interactivas
- Sección tecnologías + 7 fichas de producto
- Paleta de color con swatches + sticker + empaque
- Tabla tallas 16 sistemas × 6 tallas
- Catálogo SKU/GTIN 66 EAN-13

### rw_fichas_tecnicas_v3.docx
- Word document con fichas técnicas completas
- Tecnologías con copy aprobado
- Paleta expandida con descripciones de intención por color
- Sticker colors con preview visual
- Pack colors con swatches front/back
- Performance C4 (ejes legacy — pendiente actualizar a 6 ejes nuevos)

### rw_ratings_v2.xlsx
- Template para calificación CEO de ejes (ya llenado y devuelto)

---

## 3. DECISIONES CEO REGISTRADAS

### DEC-TECH-01: Ejes de evaluación reemplazan C4
Los 8 ejes C4 legacy quedan obsoletos. Nuevo sistema:

| # | Eje | 1 = | 10 = |
|---|-----|-----|------|
| 1 | Delgada ↔ Gruesa | Ultra slim, dress shoes | Full volume, solo botas |
| 2 | Suavidad ↔ Firmeza | Cede y abraza | Sólida bajo el pie |
| 3 | Flexibilidad ↔ Rigidez | Se dobla fácil | Pieza rígida no cede |
| 4 | Protección de impacto | Mínima | PORON XRD 90% multi-zona |
| 5 | Retorno de energía | Absorbe sin devolver | E-TPU 70-80% |
| 6 | Manejo humedad / temperatura | Sin tratamiento | Dispersión tropical |

### DEC-TECH-02: Orbis sin Arch System
- C1 correcto: LeapCore + NanoSpread (2 tecnologías)

### DEC-TECH-03: NanoSpread 5°C = límite inferior operación
- No es reducción de temperatura, es umbral mínimo de efectividad

### DEC-TECH-04: PORON XRD copy compliance
- No referenciar uso militar/deportivo sin autorización Rogers Corp.

---

## 4. RATINGS OFICIALES CEO (2026-04-02)

| Eje | GOL | VEL | ORB | LEO | BIS | MAN | ORC |
|-----|-----|-----|-----|-----|-----|-----|-----|
| Delgada ↔ Gruesa | 8 | 3 | 7 | 7 | 7 | 4 | 5 |
| Suavidad ↔ Firmeza | 8 | 6 | 6 | 6 | 6 | 9 | 6 |
| Flexibilidad ↔ Rigidez | 6 | 2 | 4 | 4 | 4 | 7 | 4 |
| Protección de impacto | 9 | 5 | 5 | 7 | 9 | 9 | 9 |
| Retorno de energía | 7 | 9 | 6 | 6 | 6 | 4 | 6 |
| Manejo humedad / temp | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

---

## 5. COPY APROBADO — TECNOLOGÍAS

### LeapCore — Elefante (PROPIETARIA)
Ingeniería de dos capas con densidades diferenciadas. La capa inferior, de mayor firmeza, proporciona soporte estructural y retención de forma bajo carga sostenida. La capa superior, de menor dureza, absorbe impacto y distribuye presión sobre la superficie plantar para confort prolongado. Diseñada para uso continuo de más de 8 horas en entornos de trabajo exigentes. Soporta hasta 110 kg / 240+ lbs.

### Arch System — Exoesqueleto (PROPIETARIA)
Pieza estructural rígida integrada en el arco longitudinal. Funciona como exoesqueleto interno que previene el aplanamiento bajo carga sostenida, manteniendo la geometría del arco durante toda la jornada. Distribuye las fuerzas de compresión vertical sin ceder, protegiendo la fascia plantar y estabilizando el mediopié.

### ThinBoom — Tendón Felino (PROPIETARIA)
E-TPU supercrítico de celda cerrada. Convierte la energía de cada paso en impulso de retorno, devolviendo entre el 70% y 80% de la fuerza de impacto. Perfil ultra delgado que maximiza respuesta sin agregar volumen al calzado.

### ShockSphere — Rana (PROPIETARIA)
Sistema de absorción focalizada con zonas independientes en talón. Cada zona absorbe y retorna energía según el ángulo e intensidad del impacto, adaptándose en tiempo real al patrón de pisada.

### NanoSpread — Reptil (PROPIETARIA)
Textil técnico de dispersión activa que cubre toda la superficie de contacto con el pie. Su red de fibras de alta capilaridad distribuye la presión de manera uniforme sobre la plantilla, elimina puntos de concentración que generan fatiga y dispersa la humedad hacia el exterior en tiempo real. Pensada para rendir en ambientes cálidos y tropicales donde la acumulación de calor dentro del calzado es el enemigo silencioso de la jornada — efectiva hasta un mínimo de 5°C. Presente en las 7 líneas de Rana Walk: la tecnología que tu pie toca primero.

### PORON® XRD® — Pájaro Carpintero (LICENCIADA Rogers Corp.)
Polímero viscoelástico de Rogers Corporation que absorbe hasta el 90% de la energía de impacto. Blando y flexible en reposo — se endurece instantáneamente en el momento del golpe y vuelve a su estado original en milisegundos. Este comportamiento rate-dependent significa que cuanto más fuerte el impacto, más firme la respuesta. En Goliath y Bison protege el talón; en Manta y Orca cubre talón y antepié, blindando las dos zonas de mayor carga del pie. Es la única tecnología licenciada del ecosistema Rana Walk y la de mayor absorción de impacto en el portafolio.

### Orca Tail — Orca (PROPIETARIA)
Pieza rígida de soporte lateral con forma de cola de cetáceo que envuelve el perímetro del arco para evitar el colapso de la plantilla hacia adentro. Mientras el Arch System resiste verticalmente, Orca Tail contiene lateralmente — impide que el pie se desplome sobre el borde medial en cada paso, que es exactamente lo que ocurre en la pronación. Una sola pieza hace el trabajo de dos: soporte del arco + contención lateral. Exclusivo de Orca — el único producto de la línea diseñado para pronadores.

---

## 6. PALETA DE COLOR — DESCRIPCIONES DE INTENCIÓN (aprobadas en Word v3)

### Goliath
- E1 Deep Navy #013A57 — Autoridad, confianza industrial y premium
- E2 Ice Blue #A8D8EA — Sofisticación y ligereza visual, evoca tecnología
- Atmósfera: Fría / Premium

### Velox
- E1 Violeta Profundo #7B2DBF — Energía concentrada, rompe con neutros ortopédicos
- E2 Magenta Neón #E040FB — Velocidad y retorno de energía, impacto en anaquel
- Atmósfera: Eléctrica / Energía

### Orbis
- E1 Blanco Puro #FFFFFF — Limpieza clínica, precisión sin cruzar línea regulatoria
- E2 Coral #EF4E54 — Rompe frialdad clínica, señala zona de acción
- Atmósfera: Limpia / Clínica / Correctiva

### Leopard
- E1 Tierra Oscuro #5C3A1E — Camuflaje, terreno, adaptabilidad
- E2 Cobre Mate #B87333 — Metal orgánico, flexibilidad con resistencia
- Atmósfera: Tierra / Adaptabilidad

### Bison
- E1 Carbon Black #2C2C2C — Negro industrial, calidez de carbón, protección
- E2 Amber #FF8C00 — Señal de alerta constructiva, como luces de seguridad en obra
- E4 Amber Oscuro #8B6914 — Profundidad para jerarquía secundaria
- Atmósfera: Oscura / Poderosa

### Manta
- E1 Warm Charcoal #4A3F3A — Se esconde como la manta raya en el fondo marino
- E2 Caribe #00BCD4 — Debajo del perfil bajo hay tecnología viva
- Atmósfera: Oceánica / Sigilosa

### Orca
- E1 Abyss Black #0B0B0B — Negro absoluto, profundidades, máximo contraste
- E2 Blanco Orca #FFFFFF — La mancha blanca de la orca, contraste puro
- E3a PORON Yellow #FFD700 — Señalización, marca presencia de PORON
- Atmósfera: Oceánica / Poderosa / Contraste

---

## 7. PENDIENTES PARA PRÓXIMA SESIÓN

| # | Pendiente | Prioridad | Bloqueado por |
|---|-----------|-----------|--------------|
| 1 | Aplicar PATCH_ENT_PROD_EJES en 7 archivos | P0 | Sesión nueva |
| 2 | Actualizar Word v4 con 6 ejes + sliders visuales + origen resuelto | P1 | Patch aplicado |
| 3 | Actualizar JSX artifact con ratings oficiales | P1 | — |
| 4 | Propagar ejes a LOC_{PROD}_{LANG} (EN/PT) | P2 | Patch aplicado |
| 5 | RW_ROOT version bump | P1 | Batch completo |
| 6 | DASHBOARD_SNAPSHOT actualización conteos | P2 | — |
| 7 | Datos físicos fabricante (peso, espesor, Shore A) | P2 | Dato externo |

---

## 8. ORIGEN MANUFACTURA (ya definido en KB — referencia)

| Mercado | Línea manufactura | Fuente |
|---------|------------------|--------|
| USA (EN) | Manufactured at Global Scale Factory · China | POL_ORIGEN_LOCAL |
| Costa Rica (ES) | Fabricado en China | POL_ORIGEN_LOCAL |
| Brasil (PT) | Fabricado na China | POL_ORIGEN_LOCAL |

Línea ingeniería (separada):
- EN: Engineered in the Costa Rica MedTech Hub
- ES: Ingeniería del MedTech Hub de Costa Rica
- PT: Engenharia do MedTech Hub da Costa Rica

CBP: "China" en packaging, NO "PRC". Ref → ENT_MARCA_ORIGEN.
