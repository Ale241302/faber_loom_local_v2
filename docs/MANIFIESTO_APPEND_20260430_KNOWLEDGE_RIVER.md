---
id: MANIFIESTO_APPEND_20260430_KNOWLEDGE_RIVER
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (planificacion + redaccion) + CEO (decisiones arquitectonicas)
aplica_a: [FaberLoom]
---

# MANIFIESTO_APPEND_20260430_KNOWLEDGE_RIVER

## Que paso
Sesion Cowork 2026-04-30 derivada de evaluacion de 3 propuestas de Claude Design (Bandeja · Cockpit · Cuaderno) para la consola operativa del agente FaberLoom. La iteracion con CEO desbloqueo un modelo arquitectonico nuevo:

> Los agentes no son artefactos privados del admin. Son **templates organizacionales** que capturan conocimiento del colectivo y destilan mejores practicas a traves de uso real, con curaduria colegiada.

Este insight justifico crear un SPEC dedicado: `SPEC_FB_KNOWLEDGE_RIVER_v1`.

## Decisiones arquitectonicas tomadas

1. **Unidad central = TEMPLATE** (no agente individual)
   - Templates son activos organizacionales con P&L propio
   - Usuarios clonan instancias efimeras del template
   - Conocimiento fluye desde clones hacia template via pool agregado

2. **5 capas de conocimiento** (eran 3, ahora son 5)
   - L0 KB inicial · L1 working · L2 episodic privada per usuario · L3 pool colectivo k-anon · L4 indexed firmado

3. **3 modos de gobernanza configurables per template**
   - A · curador unico (default · bajo riesgo)
   - B · comite de curaduria (criticos · 1 curador + 2-3 reviewers + auditores opcionales)
   - C · federada (templates con sub-dominios)

4. **5 perfiles preconfigurados de gobernanza** (atajo para crear templates)
   - operacional_rutinario · alto_riesgo_legal · cumplimiento_regulado · marca_publica · compliance_iso27001

5. **Best practices destiladas como feature explicito**
   - Sistema detecta clusters · scoring automatico · presenta candidatos al comite
   - Curador NO escribe el conocimiento · valida el destilado del rio

6. **6 mecanismos de defensa**
   - envenenamiento (weighting + diversity + outlier detection)
   - curador overloaded (pre-filtrado IA + cap)
   - sesgo del corpus (auditor externo)
   - privacidad colectiva (k-anonymity ≥ 5)
   - drift sin gobierno (timeouts + escalation)
   - lock-in (export estandar)

7. **3 universos de pantallas segun rol**
   - Operacion (usuario comun) · Gobernanza (curador/reviewer) · Audit (auditor)
   - Cada rol tiene entry point distinto al loguearse

## Diferencial defendible vs ChatGPT WA / Notion / Linear

- ChatGPT/Notion/Linear: agentes compartidos donde cada usuario tiene instancia privada
- FaberLoom Knowledge River: conocimiento colectivo canaliza hacia un solo activo organizacional con curaduria colegiada y audit immutable

Moat real: retencion de conocimiento institucional. Imposible de copiar sin arquitectura desde dia 1.

## Archivos creados/modificados en esta indexa

| Archivo | Accion |
|---|---|
| docs/faberloom/SPEC_FB_KNOWLEDGE_RIVER_v1.md | NUEVO · 600+ lineas · modelo completo |
| docs/RW_ROOT.md | bump v4.8.8 → v4.8.9 + entry changelog |
| docs/DASHBOARD_SNAPSHOT.md | bump v11.0 → v12.0 + conteo SPECs FB +1 |
| docs/MANIFIESTO_APPEND_20260430_KNOWLEDGE_RIVER.md | NUEVO · este archivo |

## Pendientes post-merge

1. Generar SPEC_FB_TEMPLATE_GOVERNANCE_v1 con detalle tecnico de implementacion (tablas postgres, schemas, eventos)
2. Pasar SPEC_FB_KNOWLEDGE_RIVER_v1 a Claude Design como input para nuevo set de mockups
3. Actualizar SPEC_FB_AGENT_BUILDER_v1 con referencia al modelo de templates (extender, no reemplazar)
4. Crear ENT_FB_GOVERNANCE_PROFILES_v1 con los 5 perfiles preconfigurados detallados
5. Definir CLI commands nuevos: fbl template ls/publish/clone, fbl committee assign, fbl pool list
6. Documentar pricing model FB v2 con consideracion de templates como activos (modelo C hibrido sigue valido + componente per-template usage)

## Origen del insight clave

CEO observo durante sesion que:
> "todos los que activen al agente de derecho laboral para su uso depositan conocimiento que va a ser evaluado e indexado al template del conocimiento"

Y posteriormente:
> "puede identificar patrones de mejor practica"

Estas dos frases reposicionaron el producto de "consola de agente" a "herramienta de captura de conocimiento institucional con destilacion de mejores practicas". El SPEC formaliza esa vision.

## Stamp
VIGENTE 2026-04-30 — Indexa del modelo Knowledge River. Posiciona FaberLoom como producto de retencion de conocimiento institucional, no solo plataforma de agentes IA.
