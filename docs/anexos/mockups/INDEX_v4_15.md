# FaberLoom Shell Mock v4.15 - Indice de estado (CANONICO)

**Fecha:** 2026-06-15 (deltas de modelo agregados 2026-06-17)
**Archivo canonico:** `docs/anexos/mockups/faberloom_shell_mock_v4_15.html`
**Base de staging:** `docs/anexos/mockups/faberloom_shell_mock_v4_14.html`
**Estado:** CANONICO / referencia visual. NO es mandato de build. El alcance por etapa esta en el mapa de la seccion 3.
**Supersede como puntero a:** v4.14, v4.13 (y la cadena v4.x anterior).
**Alineado con:** `docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md` + cadena SPEC_SPACELOOM_SELFHOSTED.

---

## 0. Por que v4.15

v4.13 estaba "CERRADO" pero sin staging por milestone y el plan reabrio el alcance. v4.14 etiqueto cada
bloque con su milestone (`// E1a/E1b/E2/E3/E4`); v4.15 = identico en estructura a v4.14, solo cambia el
look and feel al sistema "Stitch / Artisanal Intelligence Tooling". Regla: v4.15 = look canonico + staging
de v4.14; el delta v4.14->v4.15 es puramente visual.

## 1. Superficies del mock (= superficies de FaberLoom)

- **Inbox** (entrada: correo/pedidos -> clasificar -> rutear a workspace).
- **WorkLoom** (mesa de trabajo: cola de drafts por estado/urgencia; aprobar/editar/rechazar).
- **SpaceLoom** (canvas de iteracion, chat draft-first).
- **Workspaces** (My/Shared, con scope bar y herencia), **KB** (L0-L4, gold samples), **Routing/Admin**.

Nomenclatura: el producto es **FaberLoom**; SpaceLoom/WorkLoom/Inbox son superficies. (Correccion 2026-06-17.)

## 2. Componentes ya en el mock

HITL seguro (aprobar != enviar + doble confirmacion + cooldown), grounding trazado/asumido, evidence bundle SHA-256, compliance (DeepSeek bloqueado PII, transfer_basis, cobranza post-dictamen), cost cap visible, command palette, responsive 3 breakpoints, empty states admin.

## 3. Mapa milestone -> superficie (CONTRATO DE ALCANCE)

El staging vive en el codigo del mock como comentarios. Lo que NO esta en E1a/E1b NO se construye en E1, aunque se vea.

| Superficie | Etiqueta en codigo | Etapa |
|---|---|---|
| Modo Operar, login/nav, context strip | `// E1a` | E1a |
| Inbox v2 | `// E1a` | E1a |
| Command palette | `// E1a` | E1a |
| SpaceLoom (canvas + draft) | `// E1a + E1b + E2` | E1a/E1b |
| WorkLoom (mesa, cola HITL) | `// E1b` | E1b |
| Modal de envio (doble confirmacion) | `// E1b` | E1b |
| Grounding + evidence | `// E1b / // E2` | E1b/E2 |
| Routing / Factory de IAs | `// E3 + E4` | E3/E4 |
| Cost cap + compliance | `// E4` | E4 |
| Aprender (StackLoom) / Admin | E3/E4 | E3/E4 |

## 4. Deltas de MODELO (2026-06-17) - el mock no cambia de layout, cambia el concepto debajo

Tras la sesion de diseno de SpaceLoom self-embedded, tres relabels que el mock debe reflejar al codear (NO es rediseño visual):

1. **"Routing Factory / Factory de IAs" -> Routine Hub.** Ya no es una fabrica de agentes; es la biblioteca de **rutinas** (skills con nombre, invocables con `@nombre`). Ver SPEC_SPACELOOM_ETAPA1_v1 sec 4.2.
2. **"Agentes (N)" -> rutinas con persona.** No son entidades-runtime separadas; la persona es un campo de la rutina. Una entidad unica adopta el perfil segun tarea/workspace.
3. **WorkLoom necesita el modo "revision por muestra/excepciones"** (autonomia ganada) para alto volumen. Hoy el mock muestra aprobar uno por uno, que sirve para volumen bajo. Ver AUDIT_SPACELOOM_ETAPA1_STRESS_v1 (H1/H2).

Fuera de estos tres, el v4.15 sigue siendo el norte visual tal cual.

## 5. Pendientes de diseno (no bloquean indexado)

Inbox a datos reales, audit view con tabla real, editor de rutinas funcional, contraste AA en ambar/slate.

## 6. Fuente de look and feel

"Stitch / Artisanal Intelligence Tooling": serif Source Serif 4 para titulos, primary coral (#ffb59d en el mock; el token de producto se decidio NARANJA #F97316, ver SPEC v1.3), secondary sage, superficies dark en capas.

---

*Reemplaza el puntero de mock que el PLAN apuntaba a v4.13. Indexado junto al bloque SpaceLoom (BATCH 2026-06-17-003).*
