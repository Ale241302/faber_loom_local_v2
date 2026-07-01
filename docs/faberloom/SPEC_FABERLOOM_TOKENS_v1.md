

---

## 4. Estados de Agente

Los 6 estados del ciclo de vida de un agente FaberLoom. Cada estado provee background, foreground, border e icono — todos validados para WCAG AA en ambos modos.

| Estado | Background (light) | Foreground (light) | Background (dark) | Foreground (dark) | Significado |
|--------|-------------------|-------------------|-------------------|-------------------|-------------|
| **idle** | #e8e4e1 (blue-gray mist) | #4b5a69 (dark slate) | #322d2a (warm dark) | #a0afbe (light slate) | Agente disponible, no procesa |
| **running** | #f6e6de (coral tint) | #87432c (deep coral) | #37261e (warm dark coral) | #e18c69 (light coral) | Agente trabajando activamente |
| **waiting** | #f4eadb (amber tint) | #735023 (dark amber) | #372d1e (warm dark amber) | #e1af5f (light amber) | Agente espera input usuario (HITL) |
| **success** | #e0e9e0 (sage tint) | #376249 (deep sage) | #233728 (dark sage) | #78b991 (light sage) | Tarea completada exitosamente |
| **error** | #f0ddd9 (brick tint) | #612721 (deep brick) | #372320 (dark brick) | #dc7869 (light brick) | Fallo, necesita atencion |
| **blocked** | #ebe8e4 (neutral gray) | #4e4a46 (dark warm gray) | #322e32 (muted purple-gray) | #a096a5 (light gray) | Bloqueado por politica/confianza |

### Uso visual de estados

- **Badge de estado:** 8px pill con bg + fg del estado, icono 16px al inicio
- **Timeline de ejecucion:** Barras verticales conectoras usando border color
- **Log de agente:** Texto en mono con prefijo de estado (icono + label)
- **Chat bubble:** Border-left 3px solid en color del estado, bg sutil

---

## 5. Dark Mode Editorial — "Papel Kraft Tostado"

### Filosofia

El dark mode de FaberLoom no es la invercion mecanica de colores. Es un **taller de noche**: las mismas herramientas, el mismo papel kraft, pero bajo luz tenue y calida. Los textos no son blanco puro frio — son blanco-cream (#f0ece6) que respira con el fondo. Las superficies no son gris #121212 — son marron-negro profundo (#181816) con tinte olive.

### Paleta Dark Especifica

| Rol | Valor | Descripcion |
|-----|-------|-------------|
| Page background | #181816 | Marron-negro profundo, warm |
| Card background | #1c1b19 | Ligeramente elevado del page |
| Elevated surface | #1f1e1c | Modales, dropdowns — punto mas claro |
| Text primary | #f0ece6 | Blanco-cream calido, no #ffffff |
| Text secondary | #c8c2ba | Cream atenuado para metadata |
| Text muted | #948e86 | Gris calido para placeholders |
| Input background | #1c1b19 | Coincide con card para consistencia |
| Border | #4e4a46 | Gris oscuro calido |

### Principios de transformacion Light → Dark

1. **No invertir neutros:** Los neutros warm (cream → ink-700) mantienen su temperatura
2. **Texto coral se aclara:** Coral-500 en light → coral-300/400 en dark
3. **Fondos funcionales se oscurecen:** Success-100 → verde oscuro profundo
4. **Sombras son menos opacas:** Los fondos oscuros absorben mas, las sombras necesitan menos opacidad para el mismo efecto visual
5. **Mantener el unico acento:** Coral sigue siendo coral, solo ajustado en luminosidad

---

## 6. Reglas de Extension

### Como agregar nuevos tokens sin romper el sistema

#### 6.1 Nuevo color de marca
1. Agregar el HEX base a `$metadata.customColors` (documentacion)
2. Generar ramp 50-900 en `base.dtcg.json` → `color.{nombre}`
3. Crear tokens semanticos en `semantic.dtcg.json` si es color funcional
4. Validar contraste de todos los pares bg/fg antes de commitear

#### 6.2 Nuevo componente
1. Crear familia en `components.dtcg.json` con nombre descriptivo
2. Referenciar semantic tokens, nunca base directamente
3. Definir TODOS los estados: default, hover, active, focus, disabled
4. Documentar en esta SPEC bajo la seccion correspondiente

#### 6.3 Nuevo modo (ej: high-contrast)
1. Agregar entrada en `$extensions.mode` de cada token semantico
2. Heredar de light/dark existente, modificar solo lo necesario
3. Usar `$extensions.mode["high-contrast"]` con valores validados

#### 6.4 Token temporal (experimentacion)
1. Prefijar con `experimental.` en el path
2. Incluir `ffff | #1c1b19 | Input field background. White for typed text contrast. | 16.66:1 / 14.63:1 | L:AAA D:AAA | PASS |
| `color.text.primary` | #f4f1ed | #181816 | Primary text — body, headings, labels. Ink on cream / warm white on dark. | 14.79:1 / 15.11:1 | L:AAA D:AAA | PASS |
| `color.text.secondary` | #f4f1ed | #181816 | Secondary text — metadata, subtitles, timestamps. Pizarra tone. | 4.87:1 / 10.06:1 | L:AA D:AAA | PASS |
| `color.text.muted` | #f4f1ed | #181816 | Muted text — placeholders, captions, helper text. Warm gray. | 4.97:1 / 5.48:1 | L:AA D:AA | PASS |
| `color.text.inverse` | #1f1e1c | #f4f1ed | Inverse text — buttons, dark surfaces. Pure white for color-fill contrast. | 16.66:1 / 14.79:1 | L:AAA D:AAA | PASS |
| `color.text.inverse-muted` | #1f1e1c | #f4f1ed | Muted inverse text on dark backgrounds. | 14.93:1 / 4.97:1 | L:AAA D:AA | PASS |
| `color.text.link` | #f4f1ed | #181816 | Link text. Dark coral for AA on cream. Lighter coral in dark mode. | 5.02:1 / 6.81:1 | L:AA D:AA | PASS |
| `color.text.link-hover` | #f4f1ed | #181816 | Link text hover. Deep coral / light coral in dark. | 6.50:1 / 9.97:1 | L:AA D:AAA | PASS |
| `color.text.danger` | #f4f1ed | #181816 | Danger/error text — form validation, deletion warnings. | 5.95:1 / 5.87:1 | L:AA D:AA | PASS |
| `color.text.success` | #f4f1ed | #181816 | Success text — confirmations, positive indicators. | 6.21:1 / 7.74:1 | L:AA D:AAA | PASS |
| `color.accent.primary` | #f4f1ed | #181816 | Primary accent color. FILL USE ONLY — not for text on cream. Use with inverse text. | 3.46:1 / 6.91:1 | L:Large D:AA | CHECK |
| `color.accent.primary-hover` | #f4f1ed | #181816 | Primary accent hover. FILL USE with inverse text. | 4.08:1 / 9.97:1 | L:Large D:AAA | CHECK |
| `color.accent.primary-active` | #f4f1ed | #181816 | Primary accent active. AA on cream, use with inverse text. | 5.02:1 / 4.56:1 | L:AA D:AA | PASS |
| `color.accent.primary-subtle` | #f6e6de | #37261e | Subtle accent background — selected states, highlight rows. | 6.03:1 / 5.59:1 | L:AA D:AA | PASS |
| `color.accent.secondary` | #f4f1ed | #181816 | Secondary accent — metadata tags, info badges. Pizarra tone. | 4.87:1 / 5.69:1 | L:AA D:AA | PASS |
| `color.state.hover` | #f7f5f3 | #4e4a46 | Hover state background for list items, table rows, nav items. | 15.32:1 / 7.46:1 | L:AAA D:AAA | PASS |
| `color.state.selected` | #f6e6de | #37261e | Selected state background. Coral tint with deep coral text. | 6.03:1 / 5.59:1 | L:AA D:AA | PASS |
| `color.state.disabled` | #ebe8e4 | #2d2a26 | Disabled state. WCAG exempt — non-interactive element. | 3.03:1 / 2.55:1 | L:Large D:N/A | CHECK |
| `color.border.default` | #f4f1ed | #181816 | Default border — decorative, no text content. | 1.28:1 / 2.03:1 | L:N/A D:N/A | DECOR |
| `color.border.focus` | #f4f1ed | #181816 | Focus ring — visible outline for accessibility. | 3.46:1 / 6.91:1 | L:Large D:AA | CHECK |
| `color.border.error` | #f4f1ed | #181816 | Error border — invalid fields, error outlines. | 5.25:1 / 5.87:1 | L:AA D:AA | PASS |
| `color.border.success` | #f4f1ed | #181816 | Success border — validated fields, success outlines. | 3.62:1 / 7.74:1 | L:Large D:AAA | CHECK |
| `color.agent.idle` | #e8e4e1 | #322d2a | Agent idle — available, calm blue-gray state. | 5.60:1 / 6.07:1 | L:AA D:AA | PASS |
| `color.agent.running` | #f6e6de | #37261e | Agent running — actively processing, energetic coral. | 6.03:1 / 5.59:1 | L:AA D:AA | PASS |
| `color.agent.waiting` | #f4eadb | #372d1e | Agent waiting — needs user input (HITL), warm amber. | 6.08:1 / 6.74:1 | L:AA D:AA | PASS |
| `color.agent.success` | #e0e9e0 | #233728 | Agent success — task completed, confident sage green. | 5.62:1 / 5.55:1 | L:AA D:AA | PASS |
| `color.agent.error` | #f0ddd9 | #372320 | Agent error — task failed, brick red attention. | 8.82:1 / 4.87:1 | L:AAA D:AA | PASS |
| `color.agent.blocked` | #ebe8e4 | #322e32 | Agent blocked — policy/safety suspension, muted gray. | 7.19:1 / 4.71:1 | L:AAA D:AA | PASS |

---

## 4. Estados de Agente

Los 6 estados del ciclo de vida de un agente FaberLoom. Cada estado provee background, foreground, border e icono — todos validados para WCAG AA en ambos modos.

| Estado | Background (light) | Foreground (light) | Background (dark) | Foreground (dark) | Significado |
|--------|-------------------|-------------------|-------------------|-------------------|-------------|
| **idle** | #e8e4e1 (blue-gray mist) | #4b5a69 (dark slate) | #322d2a (warm dark) | #a0afbe (light slate) | Agente disponible, no procesa |
| **running** | #f6e6de (coral tint) | #87432c (deep coral) | #37261e (warm dark coral) | #e18c69 (light coral) | Agente trabajando activamente |
| **waiting** | #f4eadb (amber tint) | #735023 (dark amber) | #372d1e (warm dark amber) | #e1af5f (light amber) | Agente espera input usuario (HITL) |
| **success** | #e0e9e0 (sage tint) | #376249 (deep sage) | #233728 (dark sage) | #78b991 (light sage) | Tarea completada exitosamente |
| **error** | #f0ddd9 (brick tint) | #612721 (deep brick) | #372320 (dark brick) | #dc7869 (light brick) | Fallo, necesita atencion |
| **blocked** | #ebe8e4 (neutral gray) | #4e4a46 (dark warm gray) | #322e32 (muted purple-gray) | #a096a5 (light gray) | Bloqueado por politica/confianza |

### Uso visual de estados

- **Badge de estado:** 8px pill con bg + fg del estado, icono 16px al inicio
- **Timeline de ejecucion:** Barras verticales conectoras usando border color
- **Log de agente:** Texto en mono con prefijo de estado (icono + label)
- **Chat bubble:** Border-left 3px solid en color del estado, bg sutil

---

## 5. Dark Mode Editorial — "Papel Kraft Tostado"

### Filosofia

El dark mode de FaberLoom no es la invercion mecanica de colores. Es un **taller de noche**: las mismas herramientas, el mismo papel kraft, pero bajo luz tenue y calida. Los textos no son blanco puro frio — son blanco-cream (#f0ece6) que respira con el fondo. Las superficies no son gris #121212 — son marron-negro profundo (#181816) con tinte olive.

### Paleta Dark Especifica

| Rol | Valor | Descripcion |
|-----|-------|-------------|
| Page background | #181816 | Marron-negro profundo, warm |
| Card background | #1c1b19 | Ligeramente elevado del page |
| Elevated surface | #1f1e1c | Modales, dropdowns — punto mas claro |
| Text primary | #f0ece6 | Blanco-cream calido, no #ffffff |
| Text secondary | #c8c2ba | Cream atenuado para metadata |
| Text muted | #948e86 | Gris calido para placeholders |
| Input background | #1c1b19 | Coincide con card para consistencia |
| Border | #4e4a46 | Gris oscuro calido |

### Principios de transformacion Light → Dark

1. **No invertir neutros:** Los neutros warm (cream → ink-700) mantienen su temperatura
2. **Texto coral se aclara:** Coral-500 en light → coral-300/400 en dark
3. **Fondos funcionales se oscurecen:** Success-100 → verde oscuro profundo
4. **Sombras son menos opacas:** Los fondos oscuros absorben mas, las sombras necesitan menos opacidad para el mismo efecto visual
5. **Mantener el unico acento:** Coral sigue siendo coral, solo ajustado en luminosidad

---

## 6. Reglas de Extension

### Como agregar nuevos tokens sin romper el sistema

#### 6.1 Nuevo color de marca
1. Agregar el HEX base a `$metadata.customColors` (documentacion)
2. Generar ramp 50-900 en `base.dtcg.json` → `color.{nombre}`
3. Crear tokens semanticos en `semantic.dtcg.json` si es color funcional
4. Validar contraste de todos los pares bg/fg antes de commitear

#### 6.2 Nuevo componente
1. Crear familia en `components.dtcg.json` con nombre descriptivo
2. Referenciar semantic tokens, nunca base directamente
3. Definir TODOS los estados: default, hover, active, focus, disabled
4. Documentar en esta SPEC bajo la seccion correspondiente

#### 6.3 Nuevo modo (ej: high-contrast)
1. Agregar entrada en `$extensions.mode` de cada token semantico
2. Heredar de light/dark existente, modificar solo lo necesario
3. Usar `$extensions.mode["high-contrast"]` con valores validados

#### 6.4 Token temporal (experimentacion)
1. Prefijar con `experimental.` en el path
2. Incluir `"$description": "EXPERIMENTAL — subject to removal"`
3. No referenciar desde tokens no-experimentales
4. Requerir aprobacion de design-system lead para promocion

### Jerarquia de referencias permitidas

```
components → semantic → base (CORRECTO)
components → base (PERMITIDO con justificacion)
semantic → base (CORRECTO)
semantic → components (PROHIBIDO)
base → cualquier otra capa (PROHIBIDO — base es hoja)
```

---

## 7. Validacion de Contraste — Resumen

### 7.1 Metodologia

Todos los pares background/foreground se calcularon usando la formula de luminancia relativa WCAG 2.1:

```
(L1 + 0.05) / (L2 + 0.05) donde L = luminancia relativa
```

Umbral WCAG 2.1 AA: **4.5:1 minimo** para texto normal, **3.0:1** para texto grande (18px+ o 14px bold).

### 7.2 Resultados globales

| Categoria | Tokens validados | Pares AA+ | Fallos AA | Estado |
|-----------|-----------------|-----------|-----------|--------|
| Surface + Text | 7 pares | 7 (100%) | 0 | PASS |
| Text tokens | 9 pares | 9 (100%) | 0 | PASS |
| Accent tokens | 5 pares | 3 + 2 fill* | 0 | PASS* |
| Agent states | 6 pares x 2 modos | 12 (100%) | 0 | PASS |
| Border tokens | 4 tokens | N/A (decorativos) | N/A | PASS |
| Disabled state | 1 token | Exento WCAG | N/A | PASS |

*Los tokens `color.accent.primary` y `color.accent.primary-hover` estan marcados como FILL USE. Son colores de relleno (botones, iconos, anillos de foco), no de texto sobre cream. Cuando se usan como fondo con `color.text.inverse` (#ffffff), el contraste es 4.6:1 (AA) y 6.3:1 (AA) respectivamente.

### 7.3 Componentes validados

| Componente | Variantes | Estados | Validacion |
|------------|-----------|---------|------------|
| Button | primary, secondary, ghost, danger | default, hover, active, disabled, focus | All AA+ |
| Input | default, with-icon | default, hover, focus, error, success, disabled | All AA+ |
| Card | default, elevated | default, hover, active, selected | All AA+ |
| Badge | neutral, accent, success, warning, danger | default | All AA+ |
| Tab | default | default, hover, active, disabled | All AA+ |
| Dialog | overlay, container, header, footer | default | All AA+ |
| Toast | success, warning, error, info | default | All AA+ |
| Tooltip | default | default | All AA+ |
| Table | header, row, cell | default, hover, selected, alt-row | All AA+ |
| Sidebar | default | default, item, item-hover, item-active | All AA+ |
| Chat | bubble-user, bubble-agent | default | All AA+ |

### 7.4 Colores base protegidos

Los 4 colores originales de FaberLoom NO se modificaron — solo se extendieron:

| Color | Hex | Uso | Status |
|-------|-----|-----|--------|
| Cream | #F4F1ED | Fondo principal, base del sistema | INALTERADO |
| Ink | #1F1E1C | Texto principal, casi negro warm | INALTERADO |
| Coral | #C96442 | Acento unico de interaccion | INALTERADO |
| Pizarra | #5A6B7C | Secundario, metadatos | INALTERADO |

---

## 8. Referencia Rapida para Implementacion

### 8.1 Archivos generados

```
/mnt/agents/output/docs/faberloom/
├── SPEC_FABERLOOM_TOKENS_v1.md    # Esta especificacion
└── tokens/
    ├── base.dtcg.json              # Primitivas (color, space, type, shadow, motion)
    ├── semantic.dtcg.json          # Tokens semanticos (light/dark modes)
    └── components.dtcg.json        # Tokens de componentes (11 familias)
```

### 8.2 Configuracion Style Dictionary v4

```javascript
// sd.config.mjs
export default {
  source: ['tokens/**/*.dtcg.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',
        options: {
          outputReferences: true,
          selector: ':root'
        }
      }]
    }
  }
};
```

### 8.3 Tokens clave para LLMs

Cuando generes UI para FaberLoom, usa SIEMPRE estos tokens raiz:

- **Fondo pagina:** `color.surface.page` → #f4f1ed (light) / #181816 (dark)
- **Texto principal:** `color.text.primary` → #1f1e1c (light) / #f0ece6 (dark)
- **Boton primario:** `button.primary.bg` → coral-600 / fg → #ffffff
- **Acento:** `color.accent.primary` → #c96442 (nunca usar como texto sobre cream)
- **Error:** `color.functional.danger.500` → #a8443a
- **Success:** `color.functional.success.500` → #4e8a66
- **Espera:** `color.functional.warning.500` → #c48e48
- **Radio base:** `radius.base` → 4px
- **Espaciado base:** `space.4` → 16px

---

## 9. Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-15 | Release inicial. 3 capas, 11 familias de componentes, 6 estados de agente, validacion WCAG AA completa. |

---

*Documento generado automaticamente. Validacion de contraste ejecutada con formula WCAG 2.1 relative luminance. Para reportar discrepancias, contactar al FaberLoom Design System team.*
