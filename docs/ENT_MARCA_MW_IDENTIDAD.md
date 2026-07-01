# ENT_MARCA_MW_IDENTIDAD — Identidad Corporativa Muito Work Limitada
id: ENT_MARCA_MW_IDENTIDAD
version: 1.0
status: DRAFT
visibility: [PUBLIC]
domain: Marca (IDX_MARCA)
classification: ENTITY — Data pura inyectable
stamp: DRAFT — Pendiente aprobación CEO
refs: ENT_MARCA_IDENTIDAD (Rana Walk — separada), ENT_PLAT_MARCAS, ENT_MARCA_IP, ENT_PLAT_DESIGN_TOKENS, POL_NUNCA_TRADUCIR
aplica_a: [MWT]

---

## A. Propósito

Identidad corporativa de **Muito Work Limitada** como holding. Este documento define quién es MW, su jerarquía, su paleta corporativa, su tipografía, su tono de voz y las reglas de convivencia multi-marca.

**No confundir con:**
- ENT_MARCA_IDENTIDAD → identidad de **Rana Walk** (marca de producto)
- ENT_PLAT_DESIGN_TOKENS → tokens del **design system mwt.one** (plataforma)

Cada nivel tiene su propia identidad visual:

| Nivel | Entidad | Paleta | Tipografía | Documento |
|-------|---------|--------|------------|-----------|
| Holding | Muito Work Limitada | Navy #00205B + Cyan #00A0DD + Ámbar #D58313 | Inter (web) / Calibri (print) | **Este documento** |
| Plataforma | MWT.ONE | Deep Navy #013A57 + Mint #75CBB3 + Ice Blue #A8D8EA | General Sans + Plus Jakarta Sans | ENT_PLAT_DESIGN_TOKENS |
| Marca producto | Rana Walk | Colores por línea (GOL, VEL, ORB, LEO, BIS) | General Sans + Plus Jakarta Sans | ENT_MARCA_IDENTIDAD + ENT_PROD_{X}.E |

---

## B. Identidad Corporativa

### B1. Datos legales

| Campo | Valor |
|-------|-------|
| Razón social | Muito Work Limitada |
| Cédula jurídica | 3-102-751710 |
| País sede | Costa Rica |
| Dominio corporativo | www.muitowork.com |
| Experiencia | 30+ años tecnología, 10+ años calzado de trabajo |

### B2. Definición

Muito Work Limitada es un holding operativo con sede en Costa Rica que crea, opera y escala marcas especializadas en protección y bienestar laboral.

**Regla:** MW SÍ factura, SÍ vende, SÍ opera. Es la issuing entity de proformas, importador directo en USA y CR, gestiona expedientes y tiene clientes B2B activos en 6 países. No es un holding pasivo tipo fondo de inversión.

### B3. Jerarquía corporativa

```
Muito Work Limitada (holding operativo)
│
├── muitowork.com (sitio corporativo)
│
├── MWT.ONE (brazo tecnológico + plataforma operativa)
│   ├── Marluvas (distribución calzado seguridad BR)
│   └── Tecmater (materiales técnicos / EPP — en definición)
│
└── Rana Walk (marca propia — plantillas biomecánicas)
    ├── ranawalk.com
    └── Pressure Scanner (SaaS B2B)
```

### B4. Mercados activos

| Mercado | Status | Canal principal |
|---------|--------|----------------|
| USA | ACTIVO | Amazon FBA (Rana Walk) |
| Costa Rica | ACTIVO | Sede + distribución Marluvas |
| Colombia | ACTIVO | Distribución B2B Marluvas |
| Guatemala | ACTIVO | Distribución B2B Marluvas |
| Panamá | ACTIVO | Distribución B2B Marluvas |
| Honduras | ACTIVO | Distribución B2B Marluvas |
| Brasil | EN CONSTRUCCIÓN | Rana Walk + potencial Marluvas |

### B5. Posicionamiento

**Brand Concept:** "Conectamos más que negocios, construimos confianza."

**USP:** "La conexión que reduce riesgos y potencia oportunidades en el mercado de protección laboral."

**4 pilares de ventaja competitiva:**
1. Conocimiento cultural y comercial de cada mercado
2. Relaciones de largo plazo, no transacciones puntuales
3. Modelo híbrido: confianza presencial + eficiencia digital
4. Especialización en EPP y calzado institucional

**Fuente:** Análisis de marca Grizzly Brands (2025) — validado por CEO.

---

## C. Paleta Corporativa — Las Tres Voces

### C1. Colores ancla (Manual de Identidad Visual Grizzly, abril 2025)

| Nombre | Pantone | Hex | RGB | CMYK | Voz | Peso |
|--------|---------|-----|-----|------|-----|------|
| MW Navy | 281 C | #00205B | 0/32/91 | 100/85/5/36 | Autoridad | 70% |
| MW Cyan | 7461 C | #00A0DD | 0/160/221 | 83/19/0/0 | Acción | 25% |

### C2. Terciario web (extensión aprobada por CEO, no en manual print)

| Nombre | Hex | RGB | Voz | Peso |
|--------|-----|-----|-----|------|
| MW Ámbar | #D58313 | 213/131/19 | Calidez / Atención | 5% |

**Justificación:** Navy + Cyan solos son monocromáticos fríos. El ámbar introduce humanidad y señales de atención sin competir con los colores de marca. Sobre navy oscuro tiene contraste ~6.5:1 (WCAG AA ✅).

### C3. Texto secundario

| Nombre | Hex | Uso |
|--------|-----|-----|
| MW Silver Blue | #94B3D0 | 70% del texto UI en dark mode. Body, descripciones, metadata. |

### C4. Las tres voces (resumen)

```
NAVY  (#00205B) — "I am the foundation. Trust me."
CYAN  (#00A0DD) — "Click me. I take you somewhere."
AMBER (#D58313) — "Look here. This matters to you."
```

### C5. Cuándo usar cyan vs ámbar

| Contexto | Color |
|----------|-------|
| CTA principal (botón) | Cyan |
| Link de navegación | Cyan |
| Ítem activo en nav | Cyan |
| Focus ring | Cyan |
| Badge "Nuevo" / "Destacado" | Ámbar |
| Notificación / alerta (no error) | Ámbar |
| Progress bar | Ámbar |
| Editorial callout / cita destacada | Ámbar |
| Keyword accent en headline | Cyan O Ámbar (nunca ambos en el mismo headline) |
| Warning semántico | Ámbar |
| Error | Rojo #F87171 (ni cyan ni ámbar) |

---

## D. Logo

### D1. Estructura

Isotipo: formas M+W entrelazadas que forman hexágono implícito. Tipografía bold, redondeada, sólida. Unión M+W representa crecimiento conjunto y evolución constante.

Valores transmitidos: Reconocimiento / Confianza / Solidez / Moderno / Profesionalismo / Crecimiento.

### D2. Versiones

| Versión | Uso preferente | Cuándo |
|---------|---------------|--------|
| Horizontal color | Principal | Default en fondos claros |
| Horizontal negativo (blanco) | Principal dark | muitowork.com (dark mode) |
| Vertical color | Alternativa | Espacios verticales |
| Vertical negativo (blanco) | Alternativa dark | Espacios verticales en dark |
| Escala de grises | Limitado | Impresión B/N |
| Tinta plana cyan | Limitado | Aplicaciones a 1 tinta |
| Tinta plana navy | Limitado | Aplicaciones a 1 tinta |

### D3. Reglas de uso

- Contorno libre: 2X en cada lado (X = círculo azul claro del isotipo)
- Tamaño mínimo digital: 52px (horizontal), 32px (vertical)
- Tamaño mínimo impreso: 1.8cm (horizontal), 1.4cm (vertical)
- Fondos: solo fondos que generen contraste adecuado (navy, cyan, blanco, grises neutros)

### D4. Usos prohibidos

No eliminar elementos, no cambiar colores, no cambiar posición de elementos, no crear marcas de agua, no girar, no agregar elementos, no cambiar tipografía, no distorsionar, no aplicar sobre fondos/texturas no permitidos.

---

## E. Tipografía

### E1. Print / papelería

| Familia | Variantes | Uso |
|---------|-----------|-----|
| Calibri | Light | Pies de página, disclaimers, textos legales |
| Calibri | Regular | Descripciones, subtítulos, contenido |
| Calibri | Bold | Títulos, numeraciones, CTAs |

### E2. Web (muitowork.com)

Calibri no está disponible libre para web. Equivalente:

| Familia web | Weight | Equivale a | Uso |
|-------------|--------|------------|-----|
| Inter | 300 | Calibri Light | Captions, legales |
| Inter | 400 | Calibri Regular | Body, descripciones |
| Inter | 700 | Calibri Bold | Títulos, headlines, CTAs |

### E3. Nota de coexistencia

La plataforma MWT.ONE usa General Sans (display) + Plus Jakarta Sans (body) — ref → ENT_PLAT_DESIGN_TOKENS.B1. Eso es correcto: cada nivel tiene su propia tipografía. muitowork.com usa Inter. mwt.one usa General Sans + PJS. ranawalk.com usa la misma que mwt.one.

---

## F. Estilo gráfico

### F1. Patrones

Deconstrucción de elementos del logotipo en patrón repetitivo. Uso como textura de fondo en piezas digitales y publicaciones. En dark mode: cyan al 5-8% opacity sobre navy, o navy claro sobre navy oscuro (tono sobre tono).

### F2. Formas

Elementos del isotipo como recurso compositivo: máscaras orgánicas para fotografía, recortes circulares, superposición de formas sobre imágenes.

### F3. Iconografía

Líneas gruesas, formas simples, color predominante cyan. En dark mode: íconos en cyan o blanco según contexto. Ámbar para íconos de atención/notificación.

### F4. Fotografía

Entornos industriales reales, trabajadores con EPP, puertos, bodegas. En dark mode: overlay navy semitransparente o tratamiento duotone navy+cyan. No stock genérico de oficina.

---

## G. Tono de voz (no definido en manual Grizzly — extensión web)

| Aspecto | Guideline |
|---------|-----------|
| Persona | Primera persona plural: "Nosotros" / "En Muito Work..." |
| Registro | Profesional pero cercano. No académico, no coloquial. |
| Trato | "Usted" en comunicaciones formales (proformas, contratos). Tuteo aceptable en redes sociales. |
| Longitud | Conciso. Párrafos cortos. Una idea por oración. |
| Idioma por defecto | Español para muitowork.com. English para ranawalk.com. |

---

## H. Sistema multi-marca

### H1. Convivencia visual

| Contexto | Logo MW | Logo marca hija | Paleta |
|----------|---------|-----------------|--------|
| muitowork.com | Protagonista (nav + footer) | Dentro de cards, menor | MW (navy + cyan + ámbar) |
| ranawalk.com | "A Muito Work company" en footer | Protagonista | Rana Walk (por producto) |
| mwt.one | "Powered by Muito Work" en footer | Protagonista | MWT (navy #013A57 + mint) |
| portal.mwt.one | "Powered by Muito Work" en footer | Protagonista | MWT |
| Proformas | Emisor principal | Marca asociada | MW |
| Ferias / stands | Prominente arriba | Debajo, nunca mayor | MW |

### H2. Reglas de cobranding interno

- Logo MW siempre ≥ tamaño de marca hija
- Distancia mínima 2X entre logos
- Marcas hijas en muitowork.com usan paleta MW, no su propia paleta
- Feature flags determinan qué marca se muestra en qué contexto (ref → ENT_PLAT_MARCAS.C)

---

## I. Semáforo de claims para muitowork.com

### I1. Permitido

- ✅ Biomecánicas / Biomechanical
- ✅ Confort / Rendimiento / Soporte
- ✅ Protección laboral / Bienestar en el trabajo
- ✅ Holding operativo
- ✅ "Ingeniería del MedTech Hub de Costa Rica"

### I2. Prohibido

- ❌ Ortopédicas / Orthopedic
- ❌ Alivian / Corrigen / Curan / Tratan (contexto médico)
- ❌ Diagnóstico / Dispositivo médico
- ❌ "No facturamos. No vendemos. No operamos."
- ❌ "Made in Costa Rica" / "Made in USA"
- ❌ "RanaWalk" (junto) → siempre "Rana Walk"
- ❌ "E-commerce" para MWT.ONE

Ref → POL_CLAIMS_SCANNER para claims del scanner específicamente.

---

## Z. Pendientes

| ID | Pendiente | Desbloquea | Quién decide |
|----|-----------|-----------|-------------|
| Z1 | Dirección física real CR para footer muitowork.com | Footer web | CEO |
| Z2 | Email y teléfono (+506) reales para contacto público | Footer + formulario | CEO |
| Z3 | Cuentas de redes sociales reales MW | Footer + links | CEO |
| Z4 | Decisión: ¿sección Inversores se mantiene en el sitio? | Nav + contenido pág. 4 | CEO |
| Z5 | Equipo real para "Nuestro equipo" (si se muestra) | Pág. marcas | CEO |
| Z6 | Testimonios reales de clientes (si se muestran) | Pág. home | CEO |
| Z7 | Confirmar si alvaro@muitowork.com es el email público | Footer | CEO |
| Z8 | Aprobación formal del ámbar #D58313 como terciario web | Paleta C2 | CEO |

---

Stamp: DRAFT — Pendiente aprobación CEO

Changelog:
- v1.0 (2026-03-23): Creación inicial. Consolida identidad corporativa MW desde Manual Grizzly (abril 2025) + definición marca Grizzly + sesión CEO 2026-03-23. Incluye jerarquía corporativa confirmada por CEO, paleta 3 voces (navy+cyan+ámbar), sistema multi-marca, semáforo de claims, tono de voz.
