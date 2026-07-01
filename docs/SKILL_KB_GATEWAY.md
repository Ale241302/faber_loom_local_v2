# SKILL_KB_GATEWAY -- Gateway transaccional para escrituras KB

---
id: SKILL_KB_GATEWAY
version: 1.0
status: SHADOW
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SKILL
stamp: SHADOW -- 2026-05-07
trigger_word: kb-gateway
autonomy_ceiling: EJECUTA_INTERNO_AUDITADO
escalation_policy: CEO si lock contention >5 min o manifest version mismatch repetido
aplica_a: [MWT, FaberLoom]
relacionado: SPEC_FB_DOCUMENT_STATE_MACHINE_v1.md (estados validos) · POL_OUTAGE_CANONICAL_MIRROR_v1.md (estados pipeline) · POL_BRANCH_PR_v1.md (manifest selectivo) · POL_ROOT_FILE_CLASSIFICATION_v1.md (categories canonical_docs/generated_staging) · SPEC_HOOKS_FAIL_CLOSED_v1.md (control_surface)
data_classification: N1
---

## Proposito

Skill especializado en mediar escrituras a la Knowledge Base. Garantiza tres propiedades:

1. **Lock distribuido** -- un solo writer activo por target (canonical_docs / generated_staging) en cualquier momento.
2. **Manifest version check** -- pre-escritura valida que el manifest del repo no cambio desde que se planeo la operacion (optimistic concurrency).
3. **Atomic write** -- todos los archivos del manifest se escriben juntos o ninguno (rollback en fallo intermedio).

**No es** un agente de negocio (como SKILL_AMAZON_OPS o SKILL_PROFORMA_BUILDER). **Es** infraestructura de gobierno para el pipeline KB. Lo invocan: scripts `sync_*_indexa.ps1`, hooks Cowork, y futuros consumers que escriban a `canonical_docs`.

---

## Contexto

Pipeline actual (post Sprint 0 + A1.1):

```
Cowork escribe mirror -> sync_*_indexa.ps1 promueve a canonico -> push -> mirror_back
```

Single-writer asumido implicitamente: si dos sync scripts corren simultaneo, se pisan. Si Cowork escribe mirror mientras sync esta promoviendo, el manifest hash mismatch corrompe el commit.

Sin un gateway formal:

- Lock contention silenciosa (race condition entre sync paralelos)
- Manifest stale -- script con manifest del minuto X promueve archivos modificados en minuto X+2 sin saberlo
- Escrituras parciales -- crash a mitad de copy deja repo en estado inconsistente

A1.3 cementa el contrato. Implementacion concreta es Sprint 1+ (decision diferida -- lock vivo en Postgres advisory lock vs file lock vs Redis SETNX).

---

## KB refs obligatorias

- `SPEC_FB_DOCUMENT_STATE_MACHINE_v1` -- estados validos para transiciones documento
- `POL_OUTAGE_CANONICAL_MIRROR_v1` -- estados pipeline HEALTHY/DEGRADED/OUTAGE
- `POL_BRANCH_PR_v1` -- manifest selectivo obligatorio (NO `git add .`)
- `POL_ROOT_FILE_CLASSIFICATION_v1` -- write_policy per category
- `SPEC_HOOKS_FAIL_CLOSED_v1` -- control_surface no editable desde Cowork
- `MANIFIESTO_CAMBIOS_v2.md` -- append-only append target

---

## Capacidades

### C1 -- Acquire lock

```python
acquire_lock(
    target: Literal["canonical_docs", "generated_staging", "control_surface"],
    actor: ActorRef,                # sync_indexa_script | cowork_session | claude_code | manual
    expected_duration_sec: int,     # SLA del owner, alerta si excede
    manifest_id: Optional[str],     # link a manifest planeado
) -> LockHandle
```

**Inquebrantable:** un solo lock activo per target a la vez. Si target ya esta locked, skill devuelve `LockHandle(acquired=false, reason="locked_by:<actor>", retry_after_sec=N)`.

**Timeout:** lock expira automatico despues de `expected_duration_sec * 1.5`. Owner debe `extend_lock()` si tarda mas. Excedido = lock liberado, owner ve `LockHandle.expired=true` en proximo write.

### C2 -- Manifest version check

```python
verify_manifest(
    manifest: Manifest,
    canonical_root: Path,
) -> VerifyResult
```

Calcula:

- `repo_head_hash` actual del canonico
- `tree_hash` del subset de paths listados en manifest
- Compara con `manifest.expected_repo_head` y `manifest.expected_tree_hash`

Si mismatch:

- `repo_head_hash` distinto -> alguien commiteo entre planeo y ejecucion. Skill rechaza, owner debe re-planear (rebase o re-fetch).
- `tree_hash` distinto -> archivos del manifest cambiaron entre planeo y ejecucion. Idem.

Sin mismatch: VerifyResult.ok=true, proceder.

### C3 -- Atomic write transaction

```python
begin_transaction(lock: LockHandle, manifest: Manifest) -> Transaction
transaction.write(file_op: FileOperation)  # acumula
transaction.commit() -> CommitResult       # aplica TODOS o nada
transaction.rollback() -> None             # descarta acumulado
```

Implementacion v1 (decision en Sprint 1):

- Opcion A: 2-phase: copia a tempdir adyacente, swap atomic con `Move-Item -Force` por archivo, rollback = delete tempdir
- Opcion B: stash + restore: git stash pre-write, write directo, rollback = git stash pop
- Opcion C: branch worktree: write a worktree separado, merge via cherry-pick atomic

Recomendacion arquitectonica: Opcion A (tempdir + swap). Razon: no ensucia git state, swap es atomic per archivo a nivel filesystem, rollback simple. Confirmar en Sprint 1 con benchmark.

### C4 -- Audit footprint

Cada operacion del gateway genera `KBGatewayAuditEntry`:

```python
class KBGatewayAuditEntry:
    operation_id: UUID
    target: Literal["canonical_docs", "generated_staging", "control_surface"]
    actor: ActorRef
    lock_acquired_at: datetime
    lock_released_at: Optional[datetime]
    manifest_id: Optional[str]
    manifest_verified: bool
    manifest_mismatch_reason: Optional[str]
    files_count: int
    files_paths: list[str]
    transaction_outcome: Literal["committed", "rolled_back", "lock_failed", "verify_failed"]
    duration_ms: int
```

Storage: tabla separada del operativo (per D10 SPEC_ACTION_ENGINE patron). En MWT v1 puede ser archivo log estructurado en `audit/kb_gateway.log` (decision pragmatic, migrable a Postgres en FaberLoom Sprint 2).

### C5 -- Outage awareness

Antes de cualquier `acquire_lock`, skill consulta estado pipeline per POL_OUTAGE_CANONICAL_MIRROR:

| Estado pipeline | Comportamiento |
|---|---|
| HEALTHY | proceder normal |
| DEGRADED | rechazar lock target=canonical_docs. Permitir target=generated_staging con flag `degraded_pending=true` |
| OUTAGE | rechazar lock target=canonical_docs. Permitir target=generated_staging con flag `outage_buffer=true`. Solo lectura de manifest existente |

Skill NO declara outages -- esa autoridad es CEO per POL_OUTAGE R4. Solo respeta el estado actual del archivo `OUTAGE_DECLARED_*.md` si existe.

---

## Restricciones

- **Solo opera entre actores autorizados** per POL_ROOT_FILE_CLASSIFICATION_v1:
  - `canonical_docs` -> actor permitido: `sync_indexa_script` unicamente
  - `generated_staging` -> actores: `cowork_session`, `claude_code`
  - `control_surface` -> ningun actor desde Cowork (CEO break-glass auditado solamente)
- **No modifica el contenido** de los archivos -- solo coordina escritura
- **No interpreta contenido** -- no aplica reglas de negocio sobre los archivos. Reglas de validacion semantica viven en hooks (SPEC_HOOKS_FAIL_CLOSED) o en POLs especificas
- **No accede CEO-ONLY** -- los archivos pasan por el gateway pero el contenido se trata como opaque bytes para el skill
- **Lock no es coordinacion cross-machine** -- v1 asume single-machine (laptop CEO + un Cowork session). Multi-machine coordination es v2 con Postgres advisory lock o Redis

---

## Triggers de invocacion

| Trigger | Caller | Operacion |
|---|---|---|
| `sync_*_indexa.ps1` ejecutando Fase 5 (copy) | PowerShell script | acquire_lock + verify_manifest + atomic_write |
| Cowork session escribiendo `generated_staging` | Cowork file tools | acquire_lock target=generated_staging + write |
| Hook `pretooluse_canonical_protect.py` validando write request | Hook | verify actor + verify category + delegate to skill |
| Manual recovery from outage | CEO via PowerShell | acquire_lock con flag `recovery=true`, evita verify_manifest |

---

## Anti-patrones explicitos

| Anti-patron | Por que falla |
|---|---|
| Saltarse acquire_lock y escribir directo via Copy-Item | Race condition con sync paralelo, manifest stale silente |
| Manifest construido con paths estimados sin tree_hash | C2 no puede verificar -> proceder sin garantia, drift silente |
| Atomic write con escrituras secuenciales sin tempdir | Crash a mitad deja repo half-written, recovery manual |
| Lock holding cross-session sin extend explicit | Lock orfano bloquea writers legitimos hasta timeout |
| Skill auto-declara OUTAGE | Viola POL_OUTAGE R4 (autoridad unica CEO) |

---

## Riesgos asumidos

- **Lock single-machine v1.** Si en futuro hay 2 maquinas escribiendo (CEO + dev remoto), riesgo de doble-lock. Mitigacion: v2 con Postgres advisory lock o Redis SETNX.
- **Verify manifest no cubre cambios del filesystem fuera de git.** Si alguien edita archivo via OneDrive sync sin commitear, tree_hash detecta pero solo para archivos en manifest. Archivos no listados pueden cambiar. Mitigacion: scope estricto del manifest + working_tree_clean check pre-Fase 1 (ya implementado en sync scripts).
- **Atomic write decision diferida.** Sprint 1 decide implementacion concreta (A/B/C). Hasta entonces, sync scripts usan Copy-Item secuencial con hash post-copy verify (gap atomicity, mitigado parcialmente).
- **Audit log en archivo plano v1.** No queryable como tabla Postgres. Migracion a tabla en FaberLoom Sprint 2.

---

## State Machine (estados del skill mismo)

| Estado | Descripcion |
|---|---|
| `idle` | sin lock activo, esperando trigger |
| `lock_acquiring` | C1 en progreso, awaiting confirmation |
| `lock_held` | lock activo, owner puede invocar verify/write |
| `verifying` | C2 en progreso |
| `transacting` | C3 en progreso, write acumulando |
| `committing` | swap atomic en curso |
| `rolling_back` | rollback en curso por error o cancel |
| `lock_released` | terminal, audit emitted |

Transiciones: `idle -> lock_acquiring -> lock_held -> verifying -> transacting -> committing -> lock_released`. Branches: `lock_acquiring -> idle` (denied), `verifying -> rolling_back` (mismatch), `transacting -> rolling_back` (cancel/error), `rolling_back -> lock_released`.

---

## Implementacion

| Componente | Implementador | Sprint |
|---|---|---|
| Adapter PowerShell para sync scripts | Cowork (next session post-A1) | Post-A1 |
| Backend FastAPI endpoint para FaberLoom integration | FaberLoom dev | Sprint 2 |
| Postgres advisory lock para v2 multi-machine | FaberLoom dev | Sprint 3 |
| Audit log structured queryable | FaberLoom dev | Sprint 2 |
| Tests B1.7-style: write canonical desde Cowork sin actor `sync_indexa_script` -> debe rechazar | Cowork (test sprint mecanico) | Post-A1 |

**Sprint 1 minimo:** wrapper PowerShell que sync_*_indexa.ps1 invoca para verify_manifest + lock file (`.kb_gateway.lock` en raiz canonico con PID + timestamp). Atomic write keeps current Copy-Item secuencial + post-copy hash verify.

---

## Promocion SHADOW -> ACTIVO

Gates para promover:

1. Adapter PowerShell implementado y usado por al menos 3 sync_*_indexa.ps1
2. Test B1-style suite pasa: lock contention, manifest mismatch, rollback, outage awareness
3. Audit log generado correctamente para 10+ runs reales
4. CEO confirma que skill no introduce friccion operativa (lock timeouts manageable)

---

## Changelog

```
v1.0 SHADOW (2026-05-07): Creacion. Origen: PLAN_INTEGRACION_v4_POST_ROUND3.md A1.3.
                          Lock + manifest_version_check + atomic write como contrato.
                          Implementacion concreta diferida a Sprint 1+ con decision
                          arquitectonica entre tempdir-swap / git-stash / worktree-merge.
                          Promocion ACTIVO requiere adapter PS + tests + 10 runs auditados.
```

---

Ultima actualizacion: 2026-05-07 v1.0 SHADOW
Generado por: Cowork (AG-07) -- Arquitecto Ejecutor
