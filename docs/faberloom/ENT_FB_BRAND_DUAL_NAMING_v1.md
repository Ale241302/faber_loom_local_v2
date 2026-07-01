---
id: ENT_FB_BRAND_DUAL_NAMING_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-01
fecha: 2026-05-01
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R4)
aplica_a: [FaberLoom]
relacionado_con:
  - ARCH_AGENT_PRINCIPLES (sealed core)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (UI consola = Mesa de Control)
referencias_brand_v2:
  - project_faberloom_brand (paleta + tipografia + isotipo direccion A)
  - FABERLOOM_ATMOSPHERE.html (entrega Claude Design previa)
---

# ENT_FB_BRAND_DUAL_NAMING_v1
## Estrategia dual naming · marca tecnica vs producto comercial

## 1. Proposito · problema que resuelve

ChatGPT R2 detecto: "control plane editorial" no lo lee bien el HSE manager industrial. El comprador B2B (director de compras · HSE · gerente planta) percibe "editorial" como Silicon Valley con tenis blancos · NO como tool serio para su planta.

Solucion: **2 nombres coexisten con jerarquia clara.** Marca corporativa/tecnica + producto comercial/UI. Coexistencia explicita evita que marketing agarre "editorial" para audiencia equivocada.

> Patron probado en SaaS B2B: Atlassian → Jira/Confluence · Salesforce → Sales Cloud/Service Cloud · ServiceNow → Now Platform.

## 2. Los 4 nombres canonicos

| Capa | Nombre canonico |
|---|---|
| Marca / plataforma tecnica (NO entidad legal) | **FaberLoom** |
| Producto comercial UI principal · es-LATAM | **Mesa de Control de Cotizaciones Tecnicas** |
| Producto comercial nombre corto · UI titular | **Mesa de Control** |
| Producto en ingles · funcional NO tagline (R4) | **Spec-to-Quote Control Desk** |

**Nota R4:** "Spec-to-Quote Control Desk" es nombre ingles **funcional** · NO es tagline marketing · NO traducir como "the loom that..." ni convertir en titular poetico.

## 3. Reglas de uso por contexto

### 3.1 UI consola operativa AM (Mesa de Control)

```
Wordmark visible:        "Mesa de Control" (lockup vertical)
Subtitle:                "Cotizaciones Tecnicas" (mono uppercase 11px)
Browser title:           "Mesa de Control · Cotizaciones Tecnicas"
Footer pequeno:          "powered by FaberLoom" (gris silencioso)
URL:                     https://mwt.faberloom.com
```

NUNCA mostrar "FaberLoom" como wordmark principal en la consola operativa AM.

### 3.2 Footer tecnico · admin Telar · dev tools

```
Wordmark visible:        "FaberLoom"
Contexto:                paneles admin · Telar · dev consoles · API docs
Audiencia:               admin tecnico · CEO · auditor · curador
```

Acepta "FaberLoom" como brand visible aqui · es publico interno tecnico.

### 3.3 Documentacion legal · contratos · facturas

(R4 ajustado · separacion legal/comercial estricta)

```
Razon social emisora:    Muito Work Limitada
Descripcion comercial:   Servicio de plataforma FaberLoom / Mesa de Control de Cotizaciones Tecnicas
NUNCA escribir:          "FaberLoom · razon social" o "FaberLoom S.A."
```

R4 critico: FaberLoom **NO es entidad legal** · es marca/plataforma de propiedad de Muito Work Limitada (entidad legal real).

### 3.4 Pitch comercial HSE · procurement · ventas

```
Nombre primario:         "Mesa de Control de Cotizaciones Tecnicas"
Nombre corto contextual: "Mesa de Control"
Footer slide-deck:       "Una plataforma FaberLoom"
```

NUNCA abrir pitch a HSE manager con "FaberLoom · control plane editorial".

### 3.5 Marketing site · docs publicos

```
Hero principal:          "Mesa de Control de Cotizaciones Tecnicas"
Tagline (pendiente):     [PENDIENTE - NO INVENTAR]
Brand reference footer:  "FaberLoom · plataforma de control de cotizaciones B2B industrial"
URL principal:           faberloom.com (con redirect a marketing site)
URLs producto:           {tenant}.faberloom.com
```

### 3.6 Tabla resumen contexto → nombre

| Contexto | Nombre primario | Nombre secundario | Prohibido |
|---|---|---|---|
| UI AM operativa | Mesa de Control | powered by FaberLoom (footer) | FaberLoom como wordmark |
| Admin/dev tools | FaberLoom | — | Mesa de Control |
| Facturas/legal | Muito Work Limitada | servicio FaberLoom (descripcion) | FaberLoom como razon social |
| Pitch HSE/sales | Mesa de Control de Cotizaciones Tecnicas | una plataforma FaberLoom | "control plane editorial" |
| Marketing | Mesa de Control de Cotizaciones Tecnicas | FaberLoom | — |

## 4. Wordmark visual

### 4.1 Mesa de Control (lockup vertical canonizado)

```
Mesa de Control            ← Georgia italic 28px · color text-primary
Cotizaciones Tecnicas      ← JetBrains Mono uppercase 11px · color text-secondary · letter-spacing 0.06em
```

Lockup vertical es la forma canonica · NO usar inline ni full title en una linea.

### 4.2 FaberLoom (marca corporativa)

```
FaberLoom                  ← Georgia italic flat capitalization · tight letter-spacing
```

NUNCA escribir Faberloom · FABERLOOM · faberloom (salvo URLs).

**Split color:** dirección visual sugerida (Faber warm dark + loom coral) · NO canonizar todavia · queda pendiente del logo definitivo (R4).

### 4.3 Logo grafico

Direccion visual aprobada en project_faberloom_brand: woven lattice (direccion A · 2 warps + 2 wefts con masks over-under). Scorecard 4/3/2/5 (favicon/warmth/uniqueness/loom-fidelity).

**Estado:** dirección visual · NO canonizar como ley hasta refinamiento. R4 advertio: "no convertir un boceto cromatico en ley · el diseno despues llora · y con razon."

## 5. Reglas de prohibicion (R4 ajuste)

```
PROHIBIDO:
- Usar "FaberLoom" como nombre primario de pantalla operativa AM
- Usar "Mesa de Control" como razon social legal
- Tratar "FaberLoom" como entidad legal en facturas/contratos
- Convertir "Spec-to-Quote Control Desk" en tagline marketing
- Mezclar "Mesa de Control" con "Mesa de Trabajo" (terminos distintos)
- Usar "control plane editorial" en pitch a comprador HSE/procurement
- Aplicar split color logo en producto antes de logo definitivo
- Usar tipografia distinta a Georgia italic para wordmark
```

## 6. Evolucion · futuros verticales (R4 ajuste · ilustrativo NO canonico)

Cuando aparezca segundo vertical NO calzado · debe definirse nombre comercial especifico:

| Vertical | Nombre comercial sugerido (ILUSTRATIVO) |
|---|---|
| EPP quimico | "Mesa de Control de Cotizaciones Industriales" (placeholder) |
| MRO industrial | "Mesa de Control de Suministros Industriales" (placeholder) |
| Medico hospitalario | "Mesa de Control de Cotizaciones Medicas" (placeholder) |

R4 explicit: estos son **placeholders ilustrativos** · NO nombres aprobados. La canonizacion del nombre comercial per vertical ocurre cuando el vertical entra a produccion · con review legal + marketing del CEO + tenant.

Marca FaberLoom es permanente cross-vertical.

## 7. Trademark · pendientes legales [PENDIENTE — CEO + abogado]

- Trademark "FaberLoom" en MX · CO · CR · BR (ambito LATAM)
- Trademark "Mesa de Control de Cotizaciones Tecnicas" en MX · CO · CR
- Trademark "Spec-to-Quote Control Desk" en US (defensivo)
- Domain registrations: faberloom.com (priority) · mesadecontrol.com (defensiva si disponible) · spec-to-quote.com (US defensiva)

## 8. Reglas inquebrantables

1. **FaberLoom = marca/plataforma · NO entidad legal.** Entidad legal es Muito Work Limitada.
2. **Mesa de Control = producto comercial UI · NO razon social.**
3. **Lockup vertical es la forma canonica del wordmark Mesa de Control.**
4. **AM operativo NUNCA ve "FaberLoom" como wordmark principal · solo footer "powered by".**
5. **Pitch HSE NUNCA usa "control plane editorial".** Editorial vive interno · brand atmosphere · no pitch externo.
6. **Cambios de nombre comercial requieren review legal + marketing + CEO.** No iteracion arquitectonica.
7. **Trademark debe estar registrado antes de uso publico cross-pais.**
8. **Logo split color queda pendiente** hasta logo definitivo · NO usar split color en producto v1.

## 9. Pendientes [PENDIENTE — NO INVENTAR]

- Tagline marketing definitivo (no es "Spec-to-Quote Control Desk") → diferido marketing post-Sprint 1
- Logo definitivo (woven lattice direccion A refinada) → diferido design pass externo si necesario
- Trademark registration ambos nombres → CEO + abogado · pre-go-to-market
- Brand guidelines completas (typography pairing · spacing · iconography) → diferido brand book v2 cuando producto valide
- Nombre comercial per vertical futuro (cuando aparezca segundo tenant non-calzado) → diferido caso por caso

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_BRAND_DUAL_NAMING_v1` **NO implica entidad legal FaberLoom**. FaberLoom es marca/plataforma propiedad de Muito Work Limitada (la entidad legal real). Cualquier referencia a "FaberLoom S.A." · "FaberLoom Inc" · "FaberLoom como razon social" · es ERROR · debe corregirse a "Muito Work Limitada · plataforma FaberLoom".

## Changelog
- 2026-05-01 v1.0 VIGENTE: Creacion inicial post review R4. 4 nombres canonicos (FaberLoom marca · Mesa de Control de Cotizaciones Tecnicas producto comercial · Mesa de Control corto · Spec-to-Quote Control Desk ingles funcional). 6 contextos de uso reglados (UI AM · admin/dev · legal/facturas · pitch comercial · marketing · tabla resumen). Wordmark visual lockup vertical. 8 reglas de prohibicion explicitas (R4 critical). Evolucion segundo vertical ilustrativo NO canonico. Logo split color NO canonizar pre-logo definitivo (R4). Trademark pendiente CEO+abogado. 8 reglas inquebrantables. Linea NO implica entidad legal FaberLoom (corrige error potencial Muito Work Limitada vs FaberLoom).

## Stamp
VIGENTE 2026-05-01 — Brand dual naming canonizado con separacion estricta marca tecnica / producto comercial / razon social legal. Mitiga riesgo de confundir audiencias HSE/procurement con lenguaje "editorial". 8 reglas prohibicion explicitas evitan deuda legal y comercial.
