# AUDIT_FB_IDENTITY_NORMALIZER - Configurador de identidad + normalizador de outputs (diseno)

id: AUDIT_FB_IDENTITY_NORMALIZER_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: AUDIT
stamp: VIGENTE -- 2026-06-15 -- diseno de sesion (Project MWT Knowledge). Exploracion, NO SPEC aprobado.
aprobador: CEO (Alvaro)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_KNOWLEDGE_RIVER_v1 v1.1 - SPEC_FABERLOOM_MULTITENANT_BRANDING_v1 - SPEC_FABERLOOM_BRAND_FOUNDATION_v1 - DESIGN_FABERLOOM_v1 - ENT_FB_INSIGHTS_KIMI_SWARM_8_ATERRIZAJE_v1

---

## A. Insight central (el porque)

Cada modelo tiene huella estilistica propia: Opus escribe de una forma, Sonnet de
otra, Kimi de otra, GPT de otra. NO se puede hacer que los modelos sean iguales
(el determinismo byte-identical no existe sobre API comercial -- ver
ENT_FB_INSIGHTS_KIMI_SWARM_8 B.1). PERO si se puede normalizar el output downstream.

El normalizador de identidad + el DESIGN.md del tenant es la capa que BORRA la huella
del modelo y deja la huella de la organizacion. Diferencial: "el output es tuyo, no
del modelo que lo hizo". Se rutea entre modelos por costo/capacidad y el cliente no
lo nota porque todo sale con SU identidad.

## B. Decision de arquitectura: SKILL, no agente

Un agente "con gusto" deriva (cada modelo ruteado decide distinto). Un skill
deterministico que aplica decisiones YA codificadas no deriva. El gusto vive en el
DESIGN.md (archivo), no en el modelo.

## C. Arquitectura

```
ADMIN: configurador de identidad (arma identidad + ejemplos en vivo)
        --> DESIGN.md del tenant + muestras golden aprobadas
RUNTIME: Opus/Sonnet/Kimi/GPT producen --> SKILL_FB_IDENTITY_NORMALIZER
        |- aplica tokens/voz del DESIGN.md
        \- gate valida contra muestras golden --> output on-brand siempre --> entrega
```

Un normalizador compartido (1 skill) + un DESIGN.md por tenant (config), corriendo en
el BORDE del output (deterministic shell alrededor de todos los agentes ruteados).

## D. Configurador de identidad (superficie admin)

No se escribe el DESIGN.md a mano. Se arma en UI con ejemplos en vivo:
1. Punto de partida: plantilla (design-system base) o desde cero.
2. Configura: tokens (color/tipografia/spacing), voz/tono, Do's/Don'ts.
3. Ejemplos en vivo (clave): a medida que configura, renderiza muestras reales en cada
   formato (doc, slide, card/email) con la identidad aplicandose. Patron "preview cards
   mientras armas" -- se forkea de open-design / Claude Design, no se inventa.
4. Aprueba --> sale el DESIGN.md del tenant (formato estandar 9 secciones) + set de
   muestras golden aprobadas.

Vive en el Universo 2 (Gobernanza/admin) del Knowledge River (SPEC_FB_KNOWLEDGE_RIVER
section 11). Se monta sobre la arquitectura de tokens de
SPEC_FABERLOOM_MULTITENANT_BRANDING (fijos vs overrideables, 3 niveles).

## E. Normalizador SKILL_FB_IDENTITY_NORMALIZER (2 pasadas)

| Pasada | Que | Det / LLM |
|--------|-----|-----------|
| 1. Aplicar | mapea output a tokens del tenant (color/tipografia/spacing/componentes) + voz/tono en texto | tokens=det · voz=LLM acotado |
| 2. Gate | valida contra Do's/Don'ts del DESIGN.md + checklist (contraste/a11y, fuentes prohibidas, color fuera de paleta, voz) -- reporte pass/fail file:line | deterministico |

Salida: pass (entrega) / auto-fixed (entrega+log) / fail (escala a curador HITL).
Reparto = "deterministic shell + LLM core": shell hace sustitucion de tokens, contraste,
enforcement de fuente, deteccion de prohibido; core LLM reescribe voz y propone fixes.
Tope = "muy confiable", NO contractual (decision CEO 2026-06-15).

## F. Loop golden -> gate (cierre)

Las muestras golden aprobadas en el configurador SON los tests del gate (snapshot
testing). El normalizador valida cada output ruteado contra ese baseline. Si un modelo
se sale de identidad, el gate corrige o escala.

## G. Multi-tenant

- Skill unico compartido. DESIGN.md por tenant, heredado via Knowledge River (L0/L4,
  aislado).
- tenant_id resuelve que DESIGN.md cargar: SERVER-SIDE, nunca header de cliente
  (ENT_FB_INSIGHTS_KIMI_SWARM_8, hallazgos C de aislamiento).
- Unicidad entre orgs: sale gratis (cada org configura sus tokens/voz). Opcional: check
  de colision que avise si una identidad nueva quedo muy cerca del default FaberLoom o de
  otra (reusa "anti-referencias" de SPEC_FABERLOOM_BRAND_FOUNDATION).

## H. GATE DE SEGURIDAD DE SKILLS (obligatorio antes de heredar) -- requisito CEO

Antes de que CUALQUIER skill de terceros (ej. open-design) entre a la fabrica o al
normalizador, pasa por este gate. NINGUNA porcion de codigo se hereda sin pasarlo:
1. Inspeccion estatica (leer, NO ejecutar) del SKILL.md y de todo script bundleado
   (scripts/*.sh, *.py). Buscar: exfiltracion, shell access, llamadas de red no
   declaradas, prompt injection en el markdown.
2. Revisar el campo allowed-tools del frontmatter: un skill que pide Bash merece mas
   escrutinio que uno Read/Grep.
3. Cuarentena: el skill no se ejecuta hasta aprobado por el curador (rol Knowledge River).
4. Contexto del riesgo: estudio ToxicSkills (Snyk) -- prompt injection en 36% de skills
   testeados, "SKILL.md a shell access" en 3 lineas. Tratar todo skill como codigo de
   terceros.
5. Solo skills aprobados se mapean a la taxonomia SKILL_ e ingresan al normalizador.

## I. Encaje y fuentes externas

- Estandar DESIGN.md (9 secciones, token+regla+rationale): getdesign.md, awesome-claude-design.
- Forkeables (post-vetting H): open-design skills design-review / brand-guidelines /
  design-md + patron preview; gate estilo Vercel web-design-guidelines.
- Specs propios: SPEC_FB_KNOWLEDGE_RIVER (herencia/roles), SPEC_FABERLOOM_MULTITENANT_BRANDING
  (tokens/3 niveles), SPEC_FABERLOOM_BRAND_FOUNDATION (anti-referencias), DESIGN_FABERLOOM
  (retrofit a formato DESIGN.md).

## J. Restricciones

- Esto es DISENO/exploracion (AUDIT), NO SPEC aprobado. SPEC freeze hasta E2 respetado:
  no crea ni edita SPEC_FB.
- No toca FROZEN. Visibilidad INTERNAL. Nada CEO-ONLY.
- Construir = ejecucion (Cowork/Claude Code) post-E2.

---

Changelog:
- v1.0 (2026-06-15): creacion. Diseno del configurador de identidad (admin, ejemplos en
  vivo) + SKILL_FB_IDENTITY_NORMALIZER (2 pasadas, deterministic shell + LLM core) + loop
  golden->gate + multi-tenant server-side + GATE DE SEGURIDAD DE SKILLS obligatorio
  (requisito CEO: no heredar codigo malicioso). Insight central: normalizar la huella del
  modelo hacia la identidad de la organizacion. Derivado de sesion de pensamiento 2026-06-15.
