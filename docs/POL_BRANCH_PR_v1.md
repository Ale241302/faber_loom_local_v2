# BRANCH_PR_POLICY -- Politica de branching y PRs para repo canonico

---
id: POL_BRANCH_PR_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Claude (sintesis post Round 3) + CEO
aplica_a: [MWT, FaberLoom]
relacionado_con:
  - PLAN_INTEGRACION_v4_POST_ROUND3.md (B0.3)
  - AUDIT_NOTE_A0_SCOPE_VARIANCE.md
origen: |
  Round 3 auditoria externa hallazgo #8: branch
  skill-frontend-principles-mwt-20260504 puede volverse zombie si Sprint 0
  dura varios dias. Sin esta politica, branch acumula arquitectura critica
  separada de main.
---

## 1. Proposito

Reglas vinculantes de branching y PRs para repo canonico `mwt-knowledge-hub`. Aplica a todas las sesiones Cowork, Claude Code, y commits manuales.

**Vinculante desde:** 2026-05-07 (post Round 3 auditoria).

## 2. Estructura de branches

| Branch | Proposito | Vida util | Policy |
|---|---|---|---|
| `main` | Source of truth canonico | Permanente | Protected. Merge solo via PR + checks |
| `skill-frontend-principles-mwt-*` | Feature branch Sprint 0 actual | Hasta merge | Short-lived <7 dias. Rebase diario o merge main |
| `feature/<topic>` | Features futuros | <7 dias | Short-lived. Rebase a main antes de PR |
| `hotfix/<issue>` | Bugs criticos produccion | <24h | Direct PR a main con review urgente |

## 3. Reglas main protection

Activar en GitHub `Settings -> Branches -> Branch protection rules` para `main`:

| Regla | Activa | Razon |
|---|---|---|
| Require pull request before merging | YES | Sin PR no hay merge a main |
| Require approvals (>= 1) | YES | CEO o reviewer designado |
| Dismiss stale approvals when new commits pushed | YES | Aprobaciones expiran si rama cambia |
| Require status checks before merging | YES | CI/lint/tests deben pasar |
| Require branches to be up to date before merging | YES | Forzar rebase si main avanzo |
| Require conversation resolution | YES | No mergear con comentarios pendientes |
| Require signed commits | NO (opcional) | Bajo si gateway pattern protege canonico |
| Require linear history | YES | No merge commits, solo rebase/squash |
| Include administrators | YES | CEO tampoco bypassa reglas (auditabilidad) |
| Restrict who can push | NO (todos via PR) | Sin push directo a main |

## 4. Politica feature branches Sprint 0

### Branch actual: `skill-frontend-principles-mwt-20260504`

A partir de B0:

1. **Rebase diario** o merge main->branch antes de cualquier commit nuevo
2. **NO acumular >5 commits** sin merge a main (riesgo branch zombie)
3. **PR a main al cerrar cada fase** (B0, B1, A1, C):
   - Cerrar B0 -> PR a main con manifest selectivo
   - Cerrar B1 -> PR a main con tests pasando
   - Cerrar A1 -> PR a main con 12 SPECs creados
   - Cerrar C -> PR a main con feature flag implementado

**Justificacion:** sprint 0 estimado 13-15h. Distribuido en 3-5 sesiones Cowork. Cada sesion debe terminar con PR mergeado, NO con branch acumulando.

### Si Sprint 0 se alarga >7 dias

Triggers de alarma:
- Branch tiene >10 commits sin merge a main
- Branch atrasada >3 dias respecto a main
- Conflictos de merge esperados en >2 archivos

Acciones:
1. Forzar `git pull main` + rebase
2. Si conflictos, abrir issue para tracking
3. Considerar split del Sprint 0 en mas PRs

## 5. Mensaje de commit estandar

```
[<DOMINIO>] <fase> <accion> - <archivos resumen>

Ejemplos:
[GOBERNANZA] B0 indexa hygiene urgente - 5 archivos pre-enforcement
[GOBERNANZA] B1 indexa CLAUDE.md v2 + WIKI.md + 3 hooks
[FABERLOOM] A1 indexa SPEC_FB_DOCUMENT_STATE_MACHINE_v1
[FABERLOOM] A1 bumpea SPEC_FB_RAG_SECURITY_FIREWALL v1.0->v2.0 con C7
```

## 6. Manifest selectivo obligatorio (post Round 3)

**Prohibido:** `git add .` en scripts de canonizacion.

**Obligatorio:** manifest explicito con paths a stagear.

```powershell
# Patron correcto
foreach ($file in $manifest.files) {
    git add -- (Join-Path $CanonicalRoot $file.dst)
}

# Working tree clean check antes de commit
$dirty = git status --porcelain
if ($dirty) {
    Write-Host "ERROR: working tree no esta clean. Cambios no listados en manifest:"
    Write-Host $dirty
    exit 1
}
```

## 7. Reglas para CEO/admins (no bypass)

Incluso CEO esta sujeto a:
- PR obligatorio para cambios a main
- Branch protection no se desactiva temporalmente
- Si emergencia, hotfix branch + PR urgente con review express

**Audit trail:** todo bypass requiere `BREAK_GLASS_<fecha>_<razon>.md` en `docs/anexos/auditorias/break_glass/`.

## 8. Lifecycle de feature branches

```
crear -> commits + rebase diario -> PR -> review -> checks pasan -> merge a main -> delete branch
              ^                                                                          |
              |                                                                          |
              +-------------- si rebase falla, abortar y revisar -----------------------+
```

**Branches no mergeadas en >30 dias:** auto-archivar o eliminar tras revision.

## 9. Branches existentes a auditar

Al activar esta policy, revisar branches abiertas:

```bash
git branch -a
```

Branches >30 dias sin merge: candidate a cerrar/archivar.

## 10. Comandos utiles

```powershell
# Ver branches viejas
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short) %(committerdate)'

# Rebase a main
git checkout <feature-branch>
git fetch origin main
git rebase origin/main

# PR desde CLI (gh)
gh pr create --base main --head <feature-branch> --title "<titulo>" --body "<descripcion>"
```

## 11. Changelog

```
v1.0 (2026-05-07): Politica inicial post Round 3 auditoria.
                   Activa branch protection main + manifest selectivo +
                   short-lived feature branches.
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Corregido id BRANCH_PR_POLICY → POL_BRANCH_PR_v1. v1.0 se mantiene.
```

---

**Fin de la politica.**
