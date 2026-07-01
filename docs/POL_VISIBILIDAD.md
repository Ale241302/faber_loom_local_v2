# POL_VISIBILIDAD — Etiquetas de Acceso
id: POL_VISIBILIDAD
version: 1.1
status: VIGENTE
stamp: VIGENTE — 2026-03-21
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

Cada entity declara su nivel de visibilidad.

| Etiqueta | Quién ve | Ejemplo |
|----------|----------|---------|
| [ALL] | Todos, incluido proveedores externos | Specs técnicas, colores, claims |
| [CREATIVE] | Equipo creativo + internos | Hooks, anti-claims, comparativas |
| [TECH] | Equipo técnico + internos | Arquitectura, Docker, APIs |
| [INTERNAL] | Solo equipo interno | Riesgos, estrategia |
| [CEO-ONLY] | Solo CEO | Pricing exacto, costos, márgenes |

## Regla
- SCH_BRIEF_PROVEEDOR excluye [CEO-ONLY] e [INTERNAL] automáticamente
- Dato marcado [CEO-ONLY] nunca aparece en output externo

---

## Enforcement
- **Detección:** Archivo compartido fuera de su nivel de visibility declarado
- **Acción:** Revocar acceso, escalar al CEO
- **Severidad:** HARD — filtración de información confidencial

---

## Convención ceo_only_sections

El campo `ceo_only_sections:` lista identificadores de secciones o campos que el ingestion script debe excluir de pgvector.

### Valores válidos:
1. **Section IDs:** Letra de la sección (A, B, C, D...) cuando una sección ## completa es CEO-ONLY
2. **Field IDs:** Prefijo del campo (D3, D4, E3...) cuando solo campos específicos dentro de una sección son CEO-ONLY
3. **Subsection IDs:** ID compuesto (B.financieros, C.ceo) para subsecciones ### específicas dentro de una sección ##

### Regla de validación:
Cada valor en ceo_only_sections DEBE corresponder a:
- Un `## X.` o `## X ` header existente en el archivo, O
- Un campo con prefijo `X#:` existente en el archivo (ej: D3: $37.99...), O
- Un `### X.sub` subsection header existente en el archivo

Si el valor no matchea ningún header ni campo, es un error de configuración.

### Archivos afectados (13):
ENT_PROD_GOL, ENT_PROD_BIS, ENT_PROD_LEO, ENT_PROD_ORB, ENT_PROD_VEL, ENT_PROD_MAN, ENT_PROD_ORC, ENT_PROD_LANZAMIENTO, ENT_DIST_DISTRIBUIDORES, ENT_PLAT_LLM_ROUTING, ENT_PLAT_CONTRATO_NODO, ENT_PLAT_LEGAL_ENTITY, PLB_SCANNER_DISTRIB.

---

Stamp: VIGENTE — 2026-03-21
Vencimiento: 2026-05-30
Estado: VIGENTE
Aprobador final: CEO

---

## Regla de ingestion pgvector — ceo_only_sections

Cuando un archivo tiene el campo `ceo_only_sections:` en su header, el chunker de pgvector DEBE:

1. Leer la lista de secciones declaradas en `ceo_only_sections:`
2. Excluir esas secciones del índice PUBLIC/INTERNAL
3. Esas secciones SOLO se sirven via PostgreSQL directo con rol CEO/ADMIN
4. El archivo base (sin las secciones excluidas) se indexa normalmente en pgvector

Ejemplo:
```
visibility: [PUBLIC]
ceo_only_sections: [D3, D4, D5]
```
→ Secciones A, B, C, E, F van a pgvector. D3, D4, D5 NO.

Decisión arquitectónica: 2026-03-18. Se eligió `ceo_only_sections:` sobre file-splitting para evitar explosión de archivos y refs rotas. El mecanismo es machine-parseable sin romper el modelo de dominio actual.

---

## Changelog
- v1.0 (2026-03-01): Creación inicial — etiquetas de acceso
- v1.1 (2026-03-21): +Convención ceo_only_sections (Section IDs, Field IDs, Subsection IDs). +Regla de validación. Archivos afectados 11→13 (+MAN, +ORC). Stamp actualizado.
