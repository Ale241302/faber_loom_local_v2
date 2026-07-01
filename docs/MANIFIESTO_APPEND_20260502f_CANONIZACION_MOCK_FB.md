---
id: MANIFIESTO_APPEND_20260502f_CANONIZACION_MOCK_FB
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (arquitecto · decision propia) + CEO (delegacion explicita)
aplica_a: [FaberLoom]
---

# MANIFIESTO_APPEND_20260502f_CANONIZACION_MOCK_FB

## Que paso

CEO recibio brief externo "FABERLOOM / KNOWLEDGE MWT BRIEF MAESTRO" (LLM externo · ChatGPT) con 21 secciones y 19 entidades de datos propuestas. CEO delego decision arquitectonica diciendo "la funcionalidad del mock esta mas cercana a lo que buscamos · ejecuta bajo tu criterio".

Cowork (en rol de arquitecto) tomo la siguiente decision:

1. **El mock manda · brief es referencia complementaria.** El mockup `mockup_e1_full_navigable.html` (13.010 lineas · pushado al canon) ya cubre conceptualmente ~70% del brief. El brief fue escrito sin conocer el mock actualizado.

2. **Canonizar el mock como fuente de verdad operativa**, no rehacer pantallas siguiendo el brief. Crear specs nuevos en `docs/faberloom/` que documenten el mock + reglas inquebrantables visibles en UI.

3. **Refactorizar el data model del brief** (19 entidades fragmentadas) a forma simple (14 tablas con discriminadores `kind`/`type` en lugar de tablas hermanas). Backend MVP1 mas mantenible · queryability igual.

4. **Marcar discrepancias explicitas con el brief** donde aplique. Documentadas en cada SPEC.

5. **No tocar el mockup.** Esta sesion es solo documental · canonizacion. El mock sigue intacto.

## Documentos creados (4 SPECs nuevos)

| Spec | Que documenta | Lineas |
|---|---|---|
| `SPEC_FB_AI_CONTROL_PLANE_v1.md` | iakeys del mock · 8 tabs · 15 inspectors · 12 entidades mock IAK_* · 10 reglas inquebrantables · 9 tipos de candidate | ~110 |
| `SPEC_FB_KNOWLEDGE_ATLAS_v1.md` | Knowledge Atlas del mock · 7 vistas · 11 tipos nodo · River L0-L4 · Context Pack Trace · Impacto cascade · Governance/Audit bandeja · 6 modes inspector | ~110 |
| `SPEC_FB_VOICE_HUMANIZER_v1.md` | Voice Profile/Humanizer · capability del @router · 8 nodos voice · 5 capas con precedencia · CSV onboarding · 3 voice candidates · regla "voz decide como no que" | ~80 |
| `SPEC_FB_DATA_MODEL_v1.md` | Modelo de datos canon · 14 tablas con discriminators · reglas de integridad · 8 status · prioridades MVP1 P0-P4 · diff explicito vs brief | ~150 |

## Discrepancias documentadas con el brief externo

| Brief proponia | Decision arquitecto | SPEC donde se documenta |
|---|---|---|
| 4 tablas para outputs (artifacts/versions/learning/golden) | 1 tabla `outputs` con `kind` discriminator | DATA_MODEL §3.5 + §6 |
| 9 tablas para candidates por tipo | 1 tabla `candidates` con `type` enum | DATA_MODEL §3.6 + §6 |
| 7 tablas para policies por nivel (Tenant/Workspace/Profile/Binding/Skill/Run) | 4 tablas · cascade en runtime | DATA_MODEL §6 |
| Pantalla Learning Review global | NO crear · candidates anclados en su contexto (Voice/KB/IA Control Plane) | Decision arquitecto · brief discrepa |
| Pantalla Knowledge & Context | YA existe como Knowledge Atlas | KNOWLEDGE_ATLAS §1 |
| Pantalla Usuarios & Permisos | NO crear separada · va dentro de Settings | Decision arquitecto · brief discrepa |
| Bug `$1` en Agents | Falso positivo · grep verificado · solo precios `$15.62` y regex validos | Verificado por arquitecto |

## Que NO se hizo

- **No se toco el mockup**. Esta sesion es 100% documentacion canon.
- **No se creo pantalla Learning Review global**. Discrepo con el brief · candidates viven en su contexto.
- **No se creo pantalla Usuarios & Permisos separada**. Va dentro de Settings.
- **No se canonizaron entidades del brief sin refactor**. Refactorice a 14 tablas con discriminators.

## Referencia complementaria

El brief externo se mantiene como referencia historica · documento adjunto en este chat. No se versiona en la KB porque su valor es transitorio · el valor extraido vive en los 4 SPECs canonicos.

## Proximas acciones (deuda arquitectonica)

| Prioridad | Item | Notas |
|---|---|---|
| ALTA | Crear pantalla **Canales & Routing** en mockup | Cierra gap "entrada -> routing -> agente" que hoy salta de Inbox a Workspace sin medio explicado |
| MEDIA | Migrar sidebar de Inbox al patron global | Bug menor · Inbox usa version vieja con `agent-status` |
| BAJA | Audit completo de heros pesados | Subjetivo · requiere validacion CEO |
| FUTURO | Backend MVP1 segun SPEC_FB_DATA_MODEL_v1 P0+P1 | tenants + agents + skills + provider_connections + ai_profiles + token_ledger + audit_events |

## Changelog

- 2026-05-02 · Canonizacion del mock como source-of-truth operativo. 4 SPECs nuevos en `docs/faberloom/`. Brief externo procesado y refactorizado.
