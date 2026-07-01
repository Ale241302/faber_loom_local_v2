# Kimi Swarm prompt — brand-system-orchestrator (universal)

**Estado:** Listo para pegar en Skywork con archivos adjuntos.
**Adjuntar:** carpeta `docs/faberloom/` completa del repo `mwt-knowledge-hub` (12 SPECs + 3 tokens DTCG + 10 SVGs + 22 PNGs + research + diagrams).
**Runtime estimado:** 60-90 min (5 subagentes paralelos pesados).

---

## Prompt

```
Task: Extraer el framework UNIVERSAL de sistema de marca a partir del case
study FaberLoom ya producido. El entregable previo (docs/faberloom/) es el
primer caso de aplicacion validado. El nuevo entregable es el FRAMEWORK
META que sirve para producir N casos de aplicacion sobre cualquier marca.

CONTEXTO:

- Usuario: Alvaro / CEO Muito Work Limitada. Tiene 3 marcas activas
  (Rana Walk, MWT corporate, FaberLoom) y vendran mas. NO quiere un skill
  por marca — quiere un motor (framework) + N instancias por marca.
- Input: directorio docs/faberloom/ con 12 SPECs + tokens DTCG + iconos +
  skill faberloom-designer (entregable previo Kimi, adjunto).
- Constraint: NO duplicar trabajo. ~70% del entregable FaberLoom ya es
  metodologia universal — solo extraer y abstraer. ~30% son valores
  especificos FaberLoom — esos quedan en case-studies/faberloom/ como
  ejemplo.

DECISIONES CEO PRE-CARGADAS:

- Arquitectura: framework universal + N case studies por marca [CONFIRMADO]
- Case study #1: FaberLoom (ya entregado, solo reorganizar)
- Case study #2: Rana Walk (placeholder con discovery vacio para llenar)
- Case study #3: MWT corporate (placeholder con discovery vacio)
- Visibility: INTERNAL por default (decision sobre publicar como skill
  open-source es separada y posterior)

SUBAGENTES (5 paralelos):

Agent A - Extraccion de metodologia universal
  Para cada uno de los 12 SPECs FaberLoom, separar dos capas:
  - Capa metodologia (universal): preguntas que se hacen, frameworks de
    decision usados, estructura de output esperada, criterios de
    validacion, anti-patterns documentados.
  - Capa valores (FaberLoom-specific): paleta concreta cream/coral/etc,
    tipografia elegida (Crimson Pro+Inter), iconos especificos (96 con
    estrella=canon), voice exacto ("calmo, preciso, respetuoso del
    oficio"), personas concretas (hacedor moderno).
  Output: 12 archivos en methodology/*.md con SOLO la capa universal,
  parametrizable, con marcadores como [BRAND_NAME], [COLOR_PRIMARY],
  [VOICE_TONE], [PERSONA_PRIMARY]. Cada archivo termina con seccion
  "Como llenar para una nueva marca: 5 pasos".

Agent B - Plantillas (templates) parametrizables
  Crear archivos vacios listos para llenar con valores de cualquier marca:
  - DESIGN_TEMPLATE.md (formato Google Labs DESIGN.md con placeholders)
  - SPEC_BRAND_FOUNDATION_TEMPLATE.md
  - tokens/base.dtcg.template.json (con structure DTCG W3C, sin valores)
  - tokens/semantic.dtcg.template.json
  - tokens/components.dtcg.template.json
  - SKILL_INSTANCE_TEMPLATE.md (para que el meta-skill genere sub-skills
    instanciados por marca)
  Cada placeholder con comentario inline explicando que va ahi y ejemplos
  CONCRETOS de 3 marcas distintas en categorias diferentes:
  - FaberLoom (SaaS B2B agentic / cream-editorial / "hacedor moderno")
  - Stripe (fintech B2B developer / azul-corporate / desarrolladores)
  - IBM Carbon (enterprise design system / azul-acero / equipos design)
  Justificacion de cada categoria de placeholder con minimo 1 fuente
  publica.

Agent C - Discovery questionnaire (cuestionario de entrada del meta-skill)
  Generar el cuestionario de 30 preguntas que el meta-skill hace al usuario
  para extraer la identidad de cualquier marca nueva. Categorias balanceadas:
  - Posicionamiento (8 preguntas: target/persona, vertical, modelo de
    negocio, competencia, value prop, tono general, anti-tono, referencias
    aspiracionales)
  - Visual existente (8 preguntas: paleta actual y origen, typography
    actual, isotipo y variantes, iconos existentes, level de madurez,
    assets disponibles, design system previo, dark mode existe?)
  - Producto/contexto de uso (8 preguntas: tipo de producto B2B/B2C/
    interno, multi-tenant?, agentes IA?, densidad esperada de info, dark
    mode necesario?, dispositivos primarios, contexto fisico de uso,
    accessibility level required)
  - Restricciones (6 preguntas: presupuesto fontes comerciales,
    accessibility level WCAG A/AA/AAA, compliance industry-specific,
    escalabilidad esperada en N usuarios/tenants, equipo de
    implementacion disponible, timeline)
  Output: methodology/01_discovery_questionnaire.md con tabla de preguntas
  + tipo de respuesta esperada (texto libre / multiple choice / archivo
  upload / boolean) + a que SPEC alimenta cada respuesta + ejemplo de
  como FaberLoom respondio cada una (extraido de docs/faberloom/).

Agent D - Skill master "brand-system-orchestrator"
  Crear el SKILL.md MAESTRO que orquesta todo el framework. Estructura:
  - YAML frontmatter con name, version, description (trigger optimizado
    para invocacion: "diseñar/evolucionar/sistematizar marca/identidad
    visual/sistema de diseño")
  - Workflow interno documentado: discovery questionnaire → analisis +
    decisiones (con HITL en isotipo y typography) → generacion de SPECs →
    output de skill instanciado
  - Sub-tools que el skill invoca (los templates de Agent B + el
    questionnaire de Agent C)
  - Output esperado por invocacion: un directorio
    case-studies/[BRAND_NAME]/ completo + un sub-skill
    [BRAND_NAME]-designer empaquetado y listo para cargar
  - Anti-trigger: no invocar para tareas no-marca (refactor codigo,
    arquitectura backend, content marketing); no invocar si ya hay un
    skill instanciado activo para la marca en cuestion
  - Ejemplos: 3 invocaciones de muestra con input/output abreviado
  Output: SKILL.md universal listo para cargar en
  ~/skills/brand-system-orchestrator/

Agent E - Reference library + ejemplos de instanciacion
  Demostrar el framework instanciado en 3 marcas reales para validar que
  es realmente universal (no FaberLoom-disfrazado):
  1. FaberLoom (ya hecho — solo REORGANIZAR archivos existentes bajo
     case-studies/faberloom/ con la misma estructura que case-studies/
     [otros]/)
  2. Rana Walk (placeholder con discovery_responses.md vacio para que
     Alvaro llene; estructura completa de directorios identica a
     FaberLoom; INSTRUCTIONS.md explicando como completar)
  3. MWT corporate (placeholder igual; representacion B2B Marluvas/
     Tecmater de Mexico a Colombia; tono corporate-conservador, no craft)
  Para cada uno: estructura de directorios IDENTICA, mismos archivos
  esperados, diferentes valores. Esto fuerza que el framework sea
  realmente universal y no caso-especifico.
  Output:
  - case-studies/faberloom/ (poblado, reorganizado desde docs/faberloom/)
  - case-studies/ranawalk/INSTRUCTIONS.md + esqueleto vacio
  - case-studies/mwt-corporate/INSTRUCTIONS.md + esqueleto vacio
  - README.md a nivel case-studies/ explicando como agregar marca N+1

OUTPUT INTEGRADO ESPERADO:

  brand-system-orchestrator/
  ├── SKILL.md                              (Agent D - skill master)
  ├── README.md                             (overview del framework)
  ├── methodology/                          (Agent A - 12 archivos)
  │   ├── 01_discovery_questionnaire.md
  │   ├── 02_personas_jtbd_extraction.md
  │   ├── 03_isotipo_decision_framework.md
  │   ├── 04_typography_decision_framework.md
  │   ├── 05_tokens_dtcg_three_layers.md
  │   ├── 06_icons_system_spec.md
  │   ├── 07_voice_tone_extraction.md
  │   ├── 08_ui_density_dual_pattern.md
  │   ├── 09_multitenant_branding_levels.md
  │   ├── 10_visual_references_research.md
  │   ├── 11_design_md_export.md
  │   └── 12_skill_instance_packaging.md
  ├── templates/                            (Agent B - listos para llenar)
  │   ├── DESIGN_TEMPLATE.md
  │   ├── SPEC_BRAND_FOUNDATION_TEMPLATE.md
  │   ├── SKILL_INSTANCE_TEMPLATE.md
  │   └── tokens/
  │       ├── base.dtcg.template.json
  │       ├── semantic.dtcg.template.json
  │       └── components.dtcg.template.json
  ├── discovery/                            (Agent C)
  │   └── questionnaire_v1.md
  └── case-studies/                         (Agent E)
      ├── README.md
      ├── faberloom/                        (poblado, validacion)
      │   ├── discovery_responses.md
      │   ├── DESIGN.md
      │   ├── SPEC_BRAND_FOUNDATION.md
      │   ├── tokens/
      │   ├── icons/
      │   ├── screenshots/
      │   └── [BRAND_NAME]-designer.SKILL.md
      ├── ranawalk/
      │   ├── INSTRUCTIONS.md
      │   └── (esqueleto vacio identico)
      └── mwt-corporate/
          ├── INSTRUCTIONS.md
          └── (esqueleto vacio identico)

CONSTRAINTS NO NEGOCIABLES:

- NO inventar metodologia nueva. Toda metodologia debe ser EXTRAIDA del
  trabajo FaberLoom existente. Si una pieza no tiene precedente en
  docs/faberloom/, declarar GAP explicito en methodology/, no fabricar.
- NO eliminar valores FaberLoom — quedan en case-studies/faberloom/ como
  referencia y prueba de aplicacion.
- TODO archivo del framework (methodology/, templates/, SKILL.md master,
  discovery/) debe estar LIBRE de palabras: "FaberLoom", "cream", "coral",
  "Crimson Pro", "Hilos entrelazados", "hacedor moderno", "telar". Esos
  vocablos van solo en case-studies/faberloom/ o en ejemplos comentados.
- Output formato markdown. Templates JSON validables con DTCG schema.
  Skill formato Anthropic SKILL.md (YAML frontmatter + markdown body).
- ASCII puro en cualquier .ps1 (PowerShell 5 incompatibilidad).
- Headers MWT en cada SPEC del case study FaberLoom: id, version, status,
  visibility (INTERNAL), domain (faberloom).
- Cada decision arquitectural del framework con confidence level (alto/
  medio/bajo) y razon. Si la metodologia FaberLoom tenia decision
  marcada MEDIO o BAJO, declarar en el framework el limite de
  generalizacion.
- El framework debe servir para marcas en 3 verticales de negocio
  distintos como prueba implicita: SaaS B2B agentic (FaberLoom), producto
  fisico DTC en marketplace (Rana Walk en Amazon FBA), servicios B2B de
  representacion comercial (MWT corporate Marluvas/Tecmater).

USUARIO RECEPTOR:
CEO Muito Work Limitada. Conocimiento tecnico solido. Espera
recomendaciones directas con porque, no listas neutrales. Si hay decision
arquitectural irreversible, separar y marcar explicitamente. Tono CR
directo, sin formalidades.

INPUTS ADJUNTOS:
- docs/faberloom/ completo (12 SPECs + 3 tokens DTCG + 10 SVGs + 22 PNGs
  + 14 research MD + 3 diagrams PNG = 65 archivos)
- Contexto: este prompt, conversaciones previas con el pivot universal.
```

---

## Decisiones que ya tomé en el prompt (cambialos antes de pegar si discrepás)

| Decisión | Default que metí | Cambiá si... |
|---|---|---|
| Visibility framework | INTERNAL | querés abrirlo público en GitHub desde el inicio |
| Case studies validación | FaberLoom + Rana Walk + MWT corporate | querés sumar/restar verticales |
| Marcas de ejemplo en templates | FaberLoom + Stripe + IBM Carbon | querés otras 3 que conozcas mejor |
| Estructura de carpetas | brand-system-orchestrator/ con methodology/templates/discovery/case-studies/ | tenés convención propia distinta |
| Naming del skill master | brand-system-orchestrator | preferís brand-designer-meta o similar |
