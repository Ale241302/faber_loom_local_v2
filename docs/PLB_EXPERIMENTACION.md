# PLB_EXPERIMENTACION — Playbook de Experimentación Marketing
id: PLB_EXPERIMENTACION
status: VIGENTE
visibility: [INTERNAL]
version: 2.0
stamp: VIGENTE — aprobado 2026-03-15
domain: Marketplace (IDX_MARKETPLACE)
classification: PLAYBOOK — Instrucciones operativas
aplica_a: [SHARED]

---

## A. Framework

### A1. Principio

Todo cambio de contenido significativo se testea. No se asume que el CEO sabe qué funciona — se mide.

### A2. Método

Con ~400 sessions/día por ASIN, frequentist A/B testing no alcanza significance en tiempo útil. Usar Bayesian (beta-binomial) con priors de la categoría.

- 4 semanas: señal direccional (70%+ probabilidad de que B > A)
- 6 semanas: decisión seria (90%+ probabilidad)
- 10 semanas: Amazon MYE recommendation (su propio cálculo)

### A3. Kill signal

Si el ángulo testeado gana CTR pero pierde conversión ≥15% durante 4-6 semanas vs alternativa → wedge no cerrado o equivocado. Pivot.

Kill signal duro: si los términos del wedge consumen la mayor parte del gasto non-branded y no se convierten en el cluster con mejor CVR o mejor economics → pivot.

### A4. Cadencia

| Tipo de test | Duración mínima | Máximo simultáneos |
|---|---|---|
| Título | 4-6 semanas | 1 por ASIN |
| Imagen principal | 4-6 semanas | 1 por ASIN |
| Bullets / A+ | 6-8 semanas | 1 por ASIN |

No testear título e imagen al mismo tiempo. Una variable por test.

### A5. Reglas del suggestion engine (5 reglas)

| # | Regla | Trigger | Sugerencia |
|---|---|---|---|
| R1 | Secuencia | Test de título tuvo ganador | Testear bullet 1 con mismo principio |
| R2 | Cobertura | >30 días sin test activo en un ASIN | Testear imagen principal (mayor impacto) |
| R3 | Señal emergente | ICP observation confidence >0.7, count >5 en 2 semanas | Test de copy incorporando señal |
| R4 | Estacionalidad | 45 días antes de Prime Day / Black Friday / Q4 HSA | Test de bullet/A+ con ángulo estacional |
| R5 | Competencia | Competidor lanza feature nueva visible en reviews | Test que destaque esa feature si Goliath la tiene |

---

## B. Test #1 — Layer 1: Hook (Use-case-led vs Attribute-led)

### B1. Brief

```
Producto: Goliath (ref → ENT_PROD_GOL)
Mercado: USA / Amazon FBA
Plataforma: Amazon Manage Your Experiments (MYE)
Elemento: Título (G1)
Duración: 6 semanas mínimo
```

### B2. Hipótesis

Use-case-led title convierte mejor que attribute-led porque traduce la intención de búsqueda del buyer ("standing all day in work boots") en vez de listar specs ("225+ lbs, PORON, biomechanical").

### B3. Variantes

**Control (attribute-led)** — título actual o cercano:
```
[Brand] 225+ lbs Heavy Duty Work Boot Insoles — Arch Support, 
PORON XRD Impact Protection — Standing All Day — Men's [Size]
```

**Challenger (use-case-led)**:
```
[Brand] Work Boot Insoles for Standing All Day — Heavy Duty 
Fatigue Relief for 225+ lbs — Arch Support for Men — [Size]
```

Diferencia clave: el challenger lidera con el contexto de uso (work boot + standing all day) y el beneficio (fatigue relief) antes de las specs.

### B4. Métricas

| Métrica | Primaria/Secundaria | Qué mide |
|---|---|---|
| Conversion rate (Unit Session %) | Primaria | ¿El mensaje correcto convierte? |
| CTR (clickthrough rate) | Secundaria | ¿El título atrae al buyer correcto? |
| Sales lift (units + revenue) | Secundaria | ¿Impacto real en ventas? |

### B5. Decisión

| Resultado | Acción |
|---|---|
| Challenger gana CVR ≥10% con 90%+ probabilidad | Adoptar. Actualizar LOC_GOL_EN.G1. Principio "use-case-led" → PlaybookRule |
| Empate (<5% diferencia, 70% probabilidad) | Extender 2 semanas. Si sigue empate, mantener control |
| Control gana | Descartar hipótesis. Layer 1 no es el problema. Probar Layer 2 |
| CTR sube pero CVR baja ≥15% | **Kill signal.** El hook atrae gente equivocada. Re-evaluar wedge |

### B6. Compliance check pre-lanzamiento

- [ ] Ambas variantes pasan semáforo de claims (ref → ENT_COMP_CONTENT_RULES.A)
- [ ] PORON® con ® en ambas variantes (ref → POL_ROGERS)
- [ ] Longitud título ≤200 chars (Amazon limit)
- [ ] No claims médicos (no "cures", "treats", "medical grade")
- [ ] Ref → ENT_COMP_AMAZON para políticas de listing

---

## C. Test #2 — Layer 2: Trust (PORON prominence)

### C1. Brief

```
Producto: Goliath
Mercado: USA / Amazon FBA
Plataforma: MYE
Elemento: Título o Bullet 2 (decidir basado en resultado Test #1)
Duración: 6 semanas
Prerequisito: Test #1 completado
```

### C2. Hipótesis

Prominencia de PORON® / "American Technology Inside" en título o bullet principal sube conversión porque diferencia de genéricas chinas y justifica el premium de $37.99.

### C3. Variantes

**Si se testea en título** (título ganador de Test #1 como base):

Control:
```
[Título ganador Test #1 — sin mención de PORON]
```

Challenger:
```
[Título ganador Test #1 — con "Powered by PORON®" insertado]
```

**Si se testea en Bullet 2** (G3 actual):

Control:
```
Standing all day — solución biomecánica [versión actual]
```

Challenger:
```
Powered by PORON® XRD — American Technology for All-Day Impact Protection
```

### C4. Riesgo

El buyer de Amazon puede no saber qué es PORON. Si "American Technology Inside" resuena más que "PORON®", considerar un sub-test: "PORON®" vs "American Technology" vs ambos.

### C5. Compliance check pre-lanzamiento

- [ ] Co-branding Rogers cumplido (ref → ENT_COMP_CONTENT_RULES.B)
- [ ] Disclaimer PORON incluido donde requerido (ref → POL_ROGERS)
- [ ] "American Technology Inside" — verificar si aplica solo a empaque o también a listing digital

---

## D. Test #3 — Layer 3: Friction Removal (HSA/FSA)

### D1. Brief

```
Producto: Goliath
Mercado: USA / Amazon FBA + Amazon HSA/FSA Store
Plataforma: MYE
Elemento: Título o Badge + Bullet 5
Duración: 6 semanas (idealmente lanzar en Sept para medir Q4)
BLOQUEADOR: inscripción SIGIS completada
```

### D2. Hipótesis

"HSA/FSA Eligible" en título o bullet sube conversión, especialmente en Q4 (Oct-Dic) cuando buyers buscan gastar su allowance de salud.

### D3. Variantes

Control:
```
[Título ganador de Tests #1/#2]
```

Challenger:
```
[Título ganador] + "HSA/FSA Eligible" al final
```

Y/o en Bullet 5 (G6):

Control:
```
Trim to Fit + garantía [versión actual]
```

Challenger:
```
✅ HSA/FSA Eligible — Use Your Health Savings to Invest in Comfort.
Trim to Fit + garantía.
```

### D4. Métricas adicionales

| Métrica | Qué mide |
|---|---|
| CVR total | ¿HSA/FSA badge sube conversión general? |
| CVR por keyword "HSA insoles" | ¿Captura intent específico de HSA buyers? |
| Estacionalidad Q4 vs Q1-Q3 | ¿El efecto es estacional o permanente? |
| Average order value | ¿HSA buyers compran más (menos sensibles al precio)? |

### D5. Decisión

| Resultado | Acción |
|---|---|
| Challenger gana CVR ≥10% | Adoptar permanente. Investigar Amazon HSA/FSA Store como canal dedicado |
| Gana solo en Q4 | Adoptar estacionalmente (Oct-Dic). Versión sin HSA el resto del año |
| No impacta | HSA/FSA es badge, no driver. Mantener si no daña, no priorizar |

### D6. Blockers

- [ ] SIGIS inscripción completada
- [ ] Verificar que Amazon muestra badge HSA/FSA en el listing
- [ ] Claims compliance: "HSA/FSA Eligible" = GREEN solo post-SIGIS (YELLOW antes)

---

## E. Registro de experimentos

Cada test se documenta al cerrar:

```
Experiment {
  id: AB-XXX
  test_type: title | bullet | image | aplus
  hypothesis: texto
  variants: [control, challenger]
  start_date: YYYY-MM-DD
  end_date: YYYY-MM-DD
  result: winner | tie | killed
  winner_variant: control | challenger
  learning: "principio aprendido"
  insight_type: buyer | copy | channel
  applied_to: [documentos KB actualizados]
}
```

---

## Z. Pendientes

| ID | Pendiente | Desbloquea |
|---|---|---|
| Z1 | Lanzar Test #1 en MYE | Primera verdad comercial |
| Z2 | Inscripción SIGIS | Test #3 |
| Z3 | Verificar reglas co-branding Rogers para listing digital | Test #2 compliance |
| Z4 | Implementar Bayesian calculator (Windmill script) | Análisis más rápido que MYE |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO
Origen: Sesión growth research 2026-03-13
