# ENT_PROD_COLORES — Colores de Plantilla por Modelo (INSOLE_COLORS)
id: ENT_PROD_COLORES
version: 1.0
status: VIGENTE
visibility: [PUBLIC]
ceo_only_sections: []
domain: Producto (IDX_PRODUCTO)
stamp: VIGENTE — 2026-04-03
aplica_a: [MWT]

---

## A — Modelo constructivo

Todas las plantillas Rana Walk usan modelo de 2 capas:

| Capa | Material | Función |
|------|----------|---------|
| PU BASE | Poliuretano bi-density (LeapCore) | Base estructural. Color inverso al textil por lado. |
| TEXTIL | Tela con sublimado o serigrafía | Superficie de contacto. El patrón (sublimado/serigrafía) define los colores visibles por zona. No existe capa "Print" separada. |

Regla: el color de la base PU es inverso al color dominante del textil en cada lado. Esto maximiza contraste visual L vs R.

Excepción Velox: PU blanco (#FFFFFF) ambos lados (ultra delgada, no permite PU pigmentado).
Excepción Orca: serigrafía — ambos lados son la misma pieza textil; la serigrafía define color por zona. Thinboom Gold (#FFD700) integrado como stripe.

---

## B — Colores por modelo

Estructura por modelo: cada lado (L/R) tiene `pu` (hex), `tex` (hex base textil), `pat[]` (colores del patrón sublimado/serigrafía sobre el textil).

### B1 — GOLIATH
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #013A57 Deep Navy | #75CBB3 Mint | #013A57 Deep Navy |
| R | #75CBB3 Mint | #013A57 Deep Navy | #75CBB3 Mint |

### B2 — VELOX
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #FFFFFF White | #75CBB3 Mint | #7B2DBF Violeta Profundo |
| R | #FFFFFF White | #7B2DBF Violeta Profundo | #75CBB3 Mint |

Nota: PU blanco obligatorio ambos lados — perfil ultra delgado no permite PU pigmentado.

### B3 — ORBIS
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #EF4E54 Coral | #FFFFFF White | #EF4E54 Coral |
| R | #FFFFFF White | #EF4E54 Coral | #013A57 Deep Navy |

### B4 — LEOPARD
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #3D3D3A Dark Olive | #C5A96A Arena Dorado | #3D3D3A Dark Olive |
| R | #C5A96A Arena Dorado | #3D3D3A Dark Olive | #C5A96A Arena Dorado |

### B5 — BISON
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #2C2C2C Carbon Black | #FF8C00 Amber | #2C2C2C Carbon Black |
| R | #FF8C00 Amber | #2C2C2C Carbon Black | #FF8C00 Amber |

### B6 — MANTA
| Lado | PU BASE | TEX base | Stripes (sublimado) |
|------|---------|----------|---------------------|
| L | #4A3F3A Warm Charcoal | #00BCD4 Caribe | #4A3F3A Warm Charcoal |
| R | #00BCD4 Caribe | #4A3F3A Warm Charcoal | #00BCD4 Caribe |

### B7 — ORCA
| Lado | PU BASE | TEX base | Stripes (serigrafía) |
|------|---------|----------|----------------------|
| L | #0B0B0B Abyss Black | #0B0B0B Abyss Black | #FFFFFF White, #FFD700 Thinboom Gold |
| R | #0B0B0B Abyss Black | #FFFFFF White | #0B0B0B Abyss Black, #FFD700 Thinboom Gold |

Nota: ambos lados son la misma pieza textil. La serigrafía define zonas de color. Thinboom Gold (#FFD700) aparece como stripe en ambos lados.

---

## C — Referencia Pantone (Delta-E CIE Lab ≤5)

| HEX | Nombre | Pantone más cercano |
|-----|--------|---------------------|
| #013A57 | Deep Navy | 302 C |
| #75CBB3 | Mint | 564 C |
| #7B2DBF | Violeta Profundo | 2685 C |
| #FFFFFF | White | White C |
| #EF4E54 | Coral | 1785 C |
| #3D3D3A | Dark Olive | Black 7 C |
| #C5A96A | Arena Dorado | 466 C |
| #2C2C2C | Carbon Black | Black 6 C |
| #FF8C00 | Amber | 151 C |
| #4A3F3A | Warm Charcoal | 411 C |
| #00BCD4 | Caribe | 3125 C |
| #0B0B0B | Abyss Black | Black C |
| #FFD700 | Thinboom Gold | 116 C |

Método: conversión sRGB→CIE Lab, mínimo Delta-E contra catálogo Pantone Coated. Valores referenciales — la correspondencia exacta requiere validación física con abanico Pantone.

---

## D — SSOT y artefactos vinculados

- SSOT visual: rw_sticker_v7_8.html (constante `INSOLE_COLORS{}`)
- Artefacto standalone: rw_insole_color_spec_v7.html (visualización detallada con barcodes SVG, Pantone ref, stripe rendering)
- Cada ENT_PROD_{PROD}.E1-E4 contiene los colores de marca/sticker; este entity contiene los colores de la plantilla física (PU + textil).

---

Changelog:
- v1.0: Creación inicial. 7 modelos × 2 lados × 2 capas (PU + textil con sublimado/serigrafía). Pantone Delta-E CIE Lab. Modelo constructivo 2 capas documentado. Excepciones Velox (PU blanco) y Orca (serigrafía + Thinboom Gold). 2026-04-03.
