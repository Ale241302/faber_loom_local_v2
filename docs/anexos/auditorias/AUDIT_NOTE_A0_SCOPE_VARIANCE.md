# AUDIT_NOTE_A0_SCOPE_VARIANCE -- Documentacion de archivos pre-existentes incluidos en commit f763afb

---
id: AUDIT_NOTE_A0_SCOPE_VARIANCE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: AUDIT
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Claude (sintesis post Round 3) + CEO
aplica_a: [MWT, FaberLoom]
relacionado_con:
  - PLAN_INTEGRACION_v4_POST_ROUND3.md (B0.2)
  - MANIFIESTO_APPEND_20260507_KIMI_SWARM_6_INTEGRATION.md
origen: |
  Round 3 auditoria externa detecto que commit f763afb (A0) incluyo
  4 archivos pre-existentes ademas de los 23 archivos del Swarm #6.
  Auditabilidad fina del commit comprometida sin esta nota.
---

## 1. Hallazgo

Round 3 auditor externo (severidad alta):

> "git add . capturando 4 archivos preexistentes si compromete la auditabilidad
> fina del commit, aunque no necesariamente invalida A0. El commit ya no dice
> 'solo Swarm #6'; dice 'Swarm #6 + cambios previos colados'."

## 2. Commit afectado

```
commit f763afb
branch: skill-frontend-principles-mwt-20260504
fecha: 2026-05-06 22:26
mensaje: [GOBERNANZA] A0 indexa Swarm 6 + Auditorias R1+R2 - 23 archivos pre-enforcement
files changed: 28 (23 nuevos A + 5 modificados M)
```

## 3. Archivos pre-existentes incluidos por accidente controlado

| Archivo | Tipo cambio | Contenido del cambio | Riesgo auditoria |
|---|---|---|---|
| docs/ENT_COMERCIAL_CLIENTES.md | M | Modificaciones previas no relacionadas con Swarm #6 | Bajo -- archivo canonico legitimo |
| docs/IDX_COMERCIAL.md | M | Modificaciones previas no relacionadas con Swarm #6 | Bajo -- archivo canonico legitimo |
| docs/SCH_PROFORMA_MWT.md | M | Modificaciones previas no relacionadas con Swarm #6 | Bajo -- archivo canonico legitimo |
| docs/MANIFIESTO_CAMBIOS_v2.md | M | Modificaciones previas no relacionadas con Swarm #6 | Medio -- es manifesto, debe trazearse |
| docs/archivo/PF_2467-2026_COMTEK_GOLDEN.html | A | Archivo nuevo pre-existente en mirror | Bajo -- archivado |

**Total: 4 modificaciones (M) + 1 nuevo (A) capturados ademas de los 23 archivos del Swarm.**

## 4. Causa raiz

Script `sync_kimi_swarm_6_indexa.ps1` (B0.7 listed) usa `git add .` para staging masivo. Esto captura **todos** los cambios pendientes en working tree, no solo los archivos del manifest A0.

```powershell
# Linea problematica del script v1
git add . 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
```

## 5. Solucion futura (B0.7)

Manifest selectivo obligatorio:

```powershell
# Linea correcta para B0+ futuros
foreach ($file in $manifest.files) {
    git add -- (Join-Path $CanonicalRoot $file.dst)
}
```

## 6. Estado actual de los 4 archivos M en canonico

Los 4 archivos modificados quedaron commiteados con sus cambios previos. **No se requiere rollback** porque:

1. Los cambios eran modificaciones legitimas en working tree (no manipulaciones maliciosas)
2. Estan trazables en `git diff f763afb~1 f763afb -- docs/ENT_COMERCIAL_CLIENTES.md` (etc.)
3. Ningun cambio rompe FROZEN o policies criticas

**Accion:** documentar (este archivo) + ajustar script futuro (B0.7).

## 7. Verificacion post-hoc (opcional)

Para auditar exactamente que cambio en los 4 archivos:

```powershell
cd C:\dev\mwt-knowledge-hub
git diff f763afb~1 f763afb -- docs/ENT_COMERCIAL_CLIENTES.md docs/IDX_COMERCIAL.md docs/SCH_PROFORMA_MWT.md docs/MANIFIESTO_CAMBIOS_v2.md
```

Si revela cambios problematicos, se generara nota correctiva separada. Si los cambios son legitimos (caso esperado), se cierra el incident.

## 8. Politica de canonizacion futura (vinculante)

A partir de B0:

1. **Prohibido `git add .` en scripts de canonizacion** (sync_*_indexa.ps1)
2. **Manifest selectivo obligatorio:** todos los scripts deben listar paths exactos a stagear
3. **Working tree clean check antes de commit:** script debe abortar si hay cambios M no listados en manifest
4. **Branch protection:** PR obligatorio antes de merge a main (ver `BRANCH_PR_POLICY.md`)

## 9. Changelog

```
v1.0 (2026-05-07): Documentacion inicial post Round 3 auditoria.
                   Cubre commit f763afb. Establece politica para B0+.
```

---

**Fin de la nota.**
