# ENT_PROD_COMPARATIVA — Tabla Comparativa
id: ENT_PROD_COMPARATIVA
version: 3.1
status: DRAFT
visibility: [PUBLIC]
domain: Producto (IDX_PRODUCTO)
stamp: VIGENTE — actualizado 2026-04-03
aplica_a: [MWT]

## Rankings /5 (8 beneficios x 7 productos)

| Beneficio | GOL | VEL | ORB | LEO | BIS | MAN | ORC |
|-----------|-----|-----|-----|-----|-----|-----|-----|
| Postura | 5 | 3 | 5 | 4 | 5 | 4 | 5 |
| Impacto | 5 | 4 | 3 | 5 | 5 | 3 | 4 |
| Flexible | 4 | 5 | 4 | 5 | 3 | 4 | 3 |
| Energía | 3 | 5 | 2 | 3 | 3 | 2 | 4 |
| Frescura | 4 | 5 | 4 | 4 | 4 | 4 | 4 |
| Peso | 5 | 3 | 5 | 3 | 4 | 5 | 4 |
| Articulaciones | 5 | 3 | 3 | 4 | 5 | 4 | 5 |
| Ajuste | 1 | 5 | 4 | 4 | 5 | 4 | 3 |

## Diferencia ingeniería
7 productos x techs variables x variantes arco x SKUs
Total SKUs: 66 (GOL 6 + ORB 6 + VEL 6 + LEO 18 + BIS 18 + MAN 6 + ORC 6)

## Escala de relleno (A7)
| Producto | Nivel |
|----------|-------|
| Velox | Ultra Delgada |
| Manta | Relleno Bajo |
| Orbis | Relleno Medio |
| Leopard | Relleno Medio |
| Bison | Relleno Medio |
| Goliath | Relleno Medio-Alto |
| Orca | Relleno Medio-Alto |

## Ejes de comparación (sticker v7.8)

### Bipolares (sensation profile)
| Eje | Extremo izquierdo | Extremo derecho |
|-----|-------------------|-----------------|
| Thickness | Thin | Thick |
| Firmness | Soft | Firm |
| Rigidity | Flex | Rigid |

### Unipolares (performance)
| Eje | Low | High | Icono |
|-----|-----|------|-------|
| Impact | Low | High | 🛡️ |
| Energy | Low | High | ⚡ |
| Moisture | Low | High | 💧 |

### PROD_SPECS (valores 1-10) — recalibrados 2026-04-03 (DEC-RATE-01)

| Eje | GOL | VEL | ORB | LEO | BIS | MAN | ORC |
|-----|-----|-----|-----|-----|-----|-----|-----|
| Thickness | 7 | 3 | 4 | 7 | 7 | 3 | 3 |
| Firmness | 8 | 6 | 6 | 6 | 7 | 9 | 6 |
| Rigidity | 6 | 2 | 4 | 4 | 4 | 7 | 4 |
| Impact | 9 | 5 | 4 | 7 | 9 | 9 | 7 |
| Energy | 7 | 9 | 5 | 6 | 5 | 4 | 7 |
| Moisture | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

Fuente canónica: rw_sticker_v7_8.html constante `PROD_SPECS{}`

## SSOT visual
Comparison table renderizado en rw_sticker_v7_8.html (fichaPanel → sección Comparison). Grid 9 columnas: left label + 7 modelos + right label.

Changelog:
- v1.0: creación inicial — BIS rankings PENDIENTE
- v2.0: BIS rankings completados. Escala de relleno A7 documentada. Sesión 2026-03-13.
- v0.1 (2026-03-14): visibility: ALL + status: DRAFT agregados (Ola B).
- v3.0 (2026-04-03): MAN y ORC agregados a rankings, escala de relleno, y total SKUs. Ejes bipolares y unipolares documentados. SSOT visual → rw_sticker_v7_8.html. Total SKUs 54 → 66.
- v3.1 (2026-04-03): PROD_SPECS recalibrados con evidencia planos Bonny (DEC-RATE-01). 11 valores cambiados: GOL.thick 8→7, ORB.thick 7→4, ORB.impact 5→4, ORB.energy 6→5, BIS.firm 6→7, BIS.energy 6→5, MAN.thick 4→3, ORC.thick 5→3, ORC.impact 9→7, ORC.energy 6→7.
