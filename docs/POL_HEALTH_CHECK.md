# POL_HEALTH_CHECK — Validación Automática de la KB
id: POL_HEALTH_CHECK
version: 1.0
status: VIGENTE
stamp: VIGENTE — 2026-03-01
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]


---

## Propósito

Definir las reglas que un script o agente debe verificar al inicio de cada sesión de trabajo con la KB. Si el health check falla, el agente debe reportar los problemas antes de continuar.

## Reglas verificables

| # | Regla | Comando de verificación | Tolerancia |
|---|-------|------------------------|------------|
| H1 | Todo ENT/PLB tiene `version:` | `grep -rL "^version:" ENT_*.md PLB_*.md` | 0 fallos |
| H2 | Todo ENT/PLB tiene `status:` | `grep -rL "^status:" ENT_*.md PLB_*.md` | 0 fallos |
| H3 | Todo ENT/PLB tiene `visibility:` | `grep -rL "^visibility:" ENT_*.md PLB_*.md` | 0 fallos |
| H4 | Todo ENT/PLB tiene `domain:` | `grep -rL "^domain:" ENT_*.md PLB_*.md` | 0 fallos |
| H5 | Todo stub tiene `status: STUB` | Archivos <10 líneas sin `STUB` en status | 0 fallos |
| H6 | 0 referencias rotas | Toda ref `→ [ARCHIVO].md` apunta a archivo existente (excluir roadmap/condicional) | 0 fallos |
| H7 | Todo IDX tiene columna Status | `grep -L "Status" IDX_*.md` | 0 fallos |
| H8 | RW_ROOT version coincide con MANIFIESTO | Última versión en RW_ROOT tiene entrada en MANIFIESTO | 0 fallos |
| H9 | 0 policies vencidas | Ningún POL con Vencimiento < fecha actual | 0 fallos |
| H10 | Todo archivo nuevo registrado en IDX | Archivos ENT/PLB que no aparecen en ningún IDX | 0 fallos |

## Protocolo

1. Al inicio de sesión de trabajo → correr health_check.sh (o ejecutar los comandos manualmente).
2. Si score = 10/10 → proceder normalmente.
3. Si score < 10/10 → reportar problemas al CEO antes de empezar tareas nuevas.
4. Cada problema tiene severidad HARD (bloquea trabajo) o SOFT (reportar y continuar).

## Severidades

| Regla | Severidad |
|-------|-----------|
| H1-H5 | SOFT — reportar, continuar |
| H6 | HARD — resolver refs rotas antes de ensamblar |
| H7-H8 | SOFT — reportar, continuar |
| H9 | HARD — renovar policies vencidas |
| H10 | SOFT — registrar en IDX, continuar |

## Enforcement
- **Detección:** health_check.sh score < 10/10 al inicio de sesión
- **Acción:** reportar problemas al CEO, resolver HARD antes de continuar
- **Severidad:** HARD para H6/H9, SOFT para el resto

---
Stamp: VIGENTE 2026-03-14
Estado: VIGENTE
Aprobador final: CEO

---
Changelog:
- v1.0 (2026-03-14): creación inicial (Ola J).
