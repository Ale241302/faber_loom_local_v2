# PLB_AUDIT_VISUAL — Playbook Auditoría Visual
id: PLB_AUDIT_VISUAL
status: DRAFT
visibility: [INTERNAL]
version: 1.0
domain: Gobernanza (IDX_GOBERNANZA)
planned_sprint: Post-Sprint ISO (ref PLB_AUDIT_VISUAL_BRIEF)
aplica_a: [MWT]

---

Sigue el orden de entrega de §G del brief. No repite reglas que ya viven en las fuentes canónicas — las referencia y establece cómo aplicarlas.

## A. Propósito y alcance

Protocolo de auditoría, mejora iterativa y validación visual para todo output con componente visual del proyecto MWT / Rana Walk. Cubre pantalla (webapp, dashboard, landing) e impreso (proforma, factura, sticker, ficha técnica, empaque).

No redefine reglas existentes — las consume, establece precedencia, determina cuándo aplican y llena vacíos.

**Relación con PLB_AUDIT:** PLB_AUDIT valida estructura y datos. PLB_AUDIT_VISUAL valida la capa visual. Pipeline: genera → PLB_AUDIT → PLB_AUDIT_VISUAL → scorecard → veredicto.

## B. Fuentes canónicas y precedencia

Cuando dos fuentes chocan sobre el mismo elemento visual, la de mayor rango gana.

| Rango | Fuente | Qué aporta |
|-------|--------|------------|
| 1 | POL_PRINT | 13 reglas CSS print + JS orientación (HARD — si aplica, no se negocia) |
| 2 | POL_ANTI_CONFUSION | Exclusividad color por producto (HARD) |
| 3 | POL_VISIBILIDAD | Datos CEO-ONLY no visibles en outputs PUBLIC/PARTNER_B2B |
| 4 | ENT_COMP_CONTENT_RULES.A | Semáforo claims GREEN/YELLOW/RED |
| 5 | ENT_COMP_CONTENT_RULES.C | Paleta completa, WCAG ratios verificados |
| 6 | ENT_PLAT_DESIGN_TOKENS | Tipografía, spacing, shadows, breakpoints, componentes |
| 7 | ENT_MARCA_MW_IDENTIDAD | Identidad holding (cuando aplica nivel MW) |
| 8 | ENT_MARCA_IDENTIDAD | Identidad Rana Walk (cuando aplica nivel RW) |
| 9 | SCH_{artefacto} | Estructura específica del artefacto siendo auditado |

**Regla:** si POL_ dice "border 1px solid #ccc en print" y ENT_PLAT_DESIGN_TOKENS dice "border token --border", en contexto de impresión gana POL_PRINT.

## C. Contrato de entrada

Antes de auditar, el output debe declarar su tipo. Esto determina qué capas y módulos aplican.

| Campo | Valores posibles | Ejemplo |
|-------|-----------------|---------|
| tipo | html_printable, webapp, sticker, a_plus, pdf, email | html_printable |
| nivel_marca | MW, MWT, RW | MWT |
| imprimible | sí / no | sí |
| visibilidad | PUBLIC, PARTNER_B2B, INTERNAL, CEO-ONLY | INTERNAL |
| producto_especifico | null / GOL / VEL / ORB / LEO / BIS / MAN / ORC | null |
| criticidad | alta (comercial/fiscal) / media (operativo) / baja (interno) | alta |

Si el output no declara su tipo, el auditor lo clasifica antes de proceder. Si la clasificación es ambigua, escalar al CEO.

## D. Sistema de perfiles + módulos

Perfil principal = base obligatoria según tipo. Módulos = capas adicionales que se activan por campo del contrato de entrada.

### Perfiles principales

| Tipo output | Perfil | Capas base |
|-------------|--------|------------|
| html_printable | PRINT_DOC | tokens + print + visibilidad + claims |
| webapp | SCREEN_APP | tokens + responsive + accesibilidad + visibilidad |
| sticker | PRODUCT_LABEL | tokens + anti-confusión + colores producto + print |
| a_plus | MARKETPLACE | claims + anti-confusión + colores producto |
| pdf | STATIC_DOC | tokens + visibilidad |
| email | MESSAGE | tokens mínimos (font + color) |

### Módulos opcionales (se activan por contrato de entrada)

| Módulo | Trigger | Qué valida |
|--------|---------|------------|
| M-PRINT | imprimible = sí | 7 checks de POL_PRINT §E |
| M-ANTI_CONFUSION | producto_especifico ≠ null | E1 exclusivo, sin mezcla de paletas |
| M-CLAIMS | visibilidad = PUBLIC o PARTNER_B2B | Semáforo GREEN/YELLOW/RED de ENT_COMP_CONTENT_RULES.A |
| M-WCAG | siempre activo | Contraste AA (4.5:1 texto, 3:1 UI), focus ring, color-not-only |
| M-RESPONSIVE | tipo = webapp | 4 breakpoints de ENT_PLAT_DESIGN_TOKENS.F2, touch targets 44px |
| M-DARK_MODE | tipo = webapp | Inversión de tokens C1-C4 de ENT_PLAT_DESIGN_TOKENS |
| M-CEO_ONLY | visibilidad mixta (ceo_only_sections) | Secciones CEO-ONLY no visibles en vista cliente/impresión |

## E. Pipeline por capas

La auditoría se ejecuta en orden. Si una capa HARD falla, las siguientes se evalúan pero el output queda BLOQUEADO.

| Capa | Nombre | Qué valida | Severidad | Fuente |
|------|--------|------------|-----------|--------|
| L1 | Tokens | Tipografía correcta (familia, size, weight), spacing base-4, border-radius, shadows del sistema | SOFT | ENT_PLAT_DESIGN_TOKENS |
| L2 | Color | Paleta correcta por nivel de marca, semánticos correctos (success/warning/critical/info), hex exactos | SOFT | ENT_PLAT_DESIGN_TOKENS.C + ENT_COMP_CONTENT_RULES.C |
| L3 | Anti-confusión | E1 exclusivo por producto, sin mezcla de paletas entre productos | HARD | POL_ANTI_CONFUSION |
| L4 | Contraste WCAG | AA en todas las combinaciones text/bg. Ratios verificados | HARD | ENT_COMP_CONTENT_RULES.C |
| L5 | Layout | Grid correcto, spacing consistente, breakpoints respetados | SOFT | ENT_PLAT_DESIGN_TOKENS.E + F |
| L6 | Impresión | 7 checks de POL_PRINT §E (si M-PRINT activo) | HARD | POL_PRINT |
| L7 | Visibilidad | Datos CEO-ONLY no expuestos en vista/print incorrecta | HARD | POL_VISIBILIDAD |
| L8 | Claims | Textos PUBLIC pasan semáforo GREEN. YELLOW = flag. RED = bloqueo | HARD | ENT_COMP_CONTENT_RULES.A |
| L9 | Accesibilidad | Focus ring, keyboard nav, aria-labels, touch targets (si M-RESPONSIVE) | SOFT | ENT_PLAT_DESIGN_TOKENS.F3 |

## F. Scoring y bloqueo

Score = 10 - deducciones.

| Severidad | Deducción por hallazgo | Máximo acumulable |
|-----------|----------------------|-------------------|
| HARD | -1.0 por fallo raíz | Sin tope (1 HARD puede bloquear) |
| SOFT | -0.3 por fallo raíz | -3.0 máximo |

**Regla F2 del brief:** fallo raíz = 1 deducción. Impactos derivados del mismo fallo = flags informativos sin deducción adicional. Ejemplo: si el font-family está mal (L1), y eso causa que el peso visual y el line-height estén mal, solo se deduce 1 vez por L1.

### Veredictos

| Score | Veredicto | Acción |
|-------|-----------|--------|
| 9.5 - 10.0 | ✅ APROBADO | Listo para producción |
| 7.0 - 9.4 | 🔄 CONTINUAR | Aplicar fixes, re-auditar |
| < 7.0 | 🛑 BLOQUEADO | No entregar. Requiere rediseño o escalar CEO |

**Regla adicional:** cualquier fallo HARD en L3, L6, L7, o L8 = BLOQUEADO automático, independiente del score numérico.

## G. Auto-fix vs escalación

| Tipo de fix | Acción | Ejemplo |
|-------------|--------|---------|
| Mecánico (token, spacing, font-size, contraste hex) | Auto-fix: el agente corrige sin preguntar | --text-primary mal → reemplazar por `#013A57` |
| Estructural (layout, grid, orden de secciones) | Auto-fix si hay schema definido, escalar si no | Grid tri→dual sin schema = escalar |
| Semántico (claims, copy, naming) | Siempre escalar al CEO | Texto dice "ortopédica" en output PUBLIC |
| Comercial (precios, datos sensibles visibles) | Siempre escalar al CEO | Margen visible en vista Marluvas |

## H. Scorecard operativo

Formato que el auditor produce al finalizar cada ronda:

```
## AUDIT VISUAL — Ronda N
Output: [nombre/ART-ID]
Tipo: [contrato de entrada]
Perfil: [perfil principal] + módulos: [M-x, M-y]

| Capa | Score | Hallazgos |
|------|-------|-----------|
| L1 Tokens | ✅ / ⚠️ -0.3 | [descripción si fallo] |
| L2 Color | ✅ / ⚠️ -0.3 | |
| L3 Anti-confusión | ✅ / ❌ -1.0 | |
| L4 WCAG | ✅ / ❌ -1.0 | |
| L5 Layout | ✅ / ⚠️ -0.3 | |
| L6 Impresión | ✅ / ❌ -1.0 / N/A | |
| L7 Visibilidad | ✅ / ❌ -1.0 | |
| L8 Claims | ✅ / ❌ -1.0 / N/A | |
| L9 Accesibilidad | ✅ / ⚠️ -0.3 | |

**Score: X/10**
**Veredicto: APROBADO / CONTINUAR / BLOQUEADO**

Fixes (si CONTINUAR):
1. [Capa] [ubicación]: [qué está mal] → [fix concreto] [auto-fix / escalar]
2. ...
```

## I. Tabla de compilación on-demand (contrato de diseño portable)

Cuando un agente externo (Claude Code, Cursor, dev freelance) necesita construir un output visual sin acceso a la KB, se compila un contrato de diseño al momento usando el formato Google Stitch DESIGN.md (9 secciones).

| Nivel marca | Fuentes KB a compilar | Secciones Stitch resultantes |
|-------------|----------------------|------------------------------|
| MW (holding) | ENT_MARCA_MW_IDENTIDAD.C-F + POL_PRINT (si imprimible) | §1 Atmosphere + §2 Colors + §3 Typography + §4 Components + §7 Do's/Don'ts |
| MWT (plataforma) | ENT_PLAT_DESIGN_TOKENS.A-I + POL_PRINT + POL_ANTI_CONFUSION | §1-§9 completo (sistema más maduro) |
| RW (producto) | ENT_MARCA_IDENTIDAD + ENT_PROD_COLORES + ENT_PROD_{X}.E + POL_ANTI_CONFUSION + POL_PRINT | §1 + §2 (por producto) + §3 + §4 + §7 + §8 |

### Reglas de compilación

- El DESIGN.md compilado es self-contained: cero refs a archivos KB. Todo hex explícito, todo font con fallback, todo spacing en px/rem.
- Se genera on-demand, no se persiste como archivo de la KB. La KB sigue siendo la única fuente de verdad.
- Si un token cambia en la KB, cualquier DESIGN.md generado previamente queda obsoleto — se regenera al momento.
- El prompt template para compilar: "Compila un DESIGN.md formato Google Stitch para nivel [MW/MWT/RW] a partir de [lista de fuentes]. Self-contained, sin refs externas."

## J. Ciclo de mejora iterativa

El protocolo no solo audita — establece el ciclo de mejora para elementos visuales existentes y nuevos.

```
NUEVO OUTPUT                          OUTPUT EXISTENTE
     │                                      │
     ▼                                      ▼
 Contrato de entrada (§C)              Trigger de re-auditoría
     │                                      │
     ▼                                      ▼
 Perfil + módulos (§D)                 Mismo perfil + módulos
     │                                      │
     ▼                                      ▼
 Pipeline L1-L9 (§E)                   Pipeline L1-L9 (§E)
     │                                      │
     ▼                                      ▼
 Scorecard (§H)                        Scorecard (§H)
     │                                      │
     ├─ APROBADO → producción          ├─ APROBADO → mantener
     ├─ CONTINUAR → auto-fix/escalar   ├─ CONTINUAR → iterar
     └─ BLOQUEADO → rediseño           └─ BLOQUEADO → deprecar o rediseñar
```

### Triggers de re-auditoría para outputs existentes

- Token cambia en ENT_PLAT_DESIGN_TOKENS → re-auditar L1+L2 de todos los outputs del nivel afectado
- POL_ANTI_CONFUSION agrega nuevo producto → re-auditar L3 de outputs con producto
- POL_PRINT se modifica → re-auditar L6 de todos los outputs imprimibles
- Nuevo claim en output PUBLIC → re-auditar L8

### Prioridad de mejora (backlog visual)

1. Outputs BLOQUEADOS → fix inmediato
2. Outputs < 9.0 → siguiente sprint disponible
3. Outputs 9.0-9.4 → cuando se toque ese dominio
4. Outputs 9.5+ → no tocar salvo trigger de re-auditoría

## K. Prompt de activación

Para activar auditoría visual en cualquier agente:

```
Modo auditoría visual (ref → PLB_AUDIT_VISUAL).
Primero: clasificá el output según contrato de entrada §C.
Segundo: asigná perfil + módulos §D.
Tercero: corré pipeline L1-L9 §E.
Cuarto: scorecard §H.
Severidad: HARD (-1.0) / SOFT (-0.3).
HARD en L3/L6/L7/L8 = BLOQUEADO automático.
Umbral aprobación: 9.5/10.
Auto-fix mecánico sin preguntar. Semántico/comercial = escalar CEO.
```

---
Changelog:
- v0.1 (2026-03-14): stub creado para resolver referencia rota desde PLB_AUDIT_VISUAL_BRIEF.md. Ola E3.
- v1.0 (2026-04-05): Contenido completo. 11 secciones (A-K): propósito, fuentes canónicas, contrato entrada, perfiles+módulos, pipeline L1-L9, scoring/bloqueo, auto-fix/escalación, scorecard, compilación on-demand, ciclo mejora, prompt activación.
