---
id: POL_SYNC_MANIFEST_INTEGRITY
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
tipo: policy
last_review: 2026-06-02
stamp: DRAFT -- 2026-06-02 -- creado en Cowork (generated_staging), pendiente promocion a canonico
aplica_a: [MWT, FaberLoom]
---

# POL_SYNC_MANIFEST_INTEGRITY -- Integridad criptografica del sync canonico/mirror

> Origen: auditoria externa 2026-06-02 (gap P0). El pipeline canonico/mirror actual
> (robocopy + git + sync_*_indexa.ps1) no verifica integridad por hash; un sync
> parcial o una divergencia silenciosa entre `C:\dev\mwt-knowledge-hub` y el mirror
> OneDrive no se detecta de forma determinista. Esta politica cierra ese gap.

## A. Proposito

Garantizar que toda promocion canonico <-> mirror sea verificable, atomica en intencion,
y reversible. Ningun cambio se considera promovido sin un manifest firmado que pruebe
que el conjunto de archivos en destino es exactamente el esperado.

## B. Definiciones

- **Manifest de sync**: artefacto JSON generado por el script de sync que enumera,
  para cada archivo afectado: path relativo, sha256, bytes, y accion (add/update/delete).
- **Conteo esperado**: total de .md por carpeta declarado en el manifest, reconciliado
  contra DASHBOARD_SNAPSHOT (fuente unica de conteos, POL_DETERMINISMO Regla 3).
- **Dry-run**: ejecucion del sync que produce el manifest y el diff SIN escribir.
- **Log firmado**: registro post-sync inmutable (append-only) con el sha256 del manifest,
  timestamp, operador, y resultado.

## C. Reglas inquebrantables

1. **No hay sync sin manifest.** Todo `sync_*_indexa.ps1` debe emitir un manifest JSON
   antes de tocar destino. Sin manifest generado, el sync aborta (fail-closed).
2. **Hash por archivo obligatorio.** Cada entrada del manifest lleva sha256 del contenido
   en origen. Post-copia, el script re-calcula sha256 en destino y compara. Mismatch en
   cualquier archivo = sync marcado FAILED, no PARTIAL.
3. **Dry-run + diff humano antes de promover a canonico.** Toda promocion a
   `C:\dev\mwt-knowledge-hub` exige un dry-run cuyo diff (archivos add/update/delete +
   conteos) sea revisado y aprobado explicitamente. Promociones destructivas (delete)
   nunca son automaticas.
4. **Reconciliacion de conteos.** El manifest declara conteos esperados por carpeta y los
   reconcilia contra DASHBOARD_SNAPSHOT. Divergencia no explicada = abort.
5. **Log firmado post-sync.** Al cerrar, el sync escribe una entrada append-only con
   sha256 del manifest + resultado. Esta entrada es la prueba de promocion; sin ella el
   cambio NO se considera canonico.
6. **Limpieza del mirror auditada.** El borrado de archivos del mirror que `mirror_to_onedrive.ps1`
   ejecuta al final de cada sync debe quedar listado en el manifest (accion delete con hash
   previo), nunca como efecto silencioso.

## D. Esquema del manifest (referencia)

```json
{
  "sync_id": "SYNC-20260602-<hash>",
  "direction": "staging_to_canonical | canonical_to_mirror",
  "generated_at": "ISO-8601",
  "operator": "<actor>",
  "expected_counts": { "docs/": 0, "docs/faberloom/": 0 },
  "files": [
    { "path": "docs/EJEMPLO.md", "sha256": "...", "bytes": 0, "action": "update" }
  ],
  "manifest_sha256": "<sha256 del bloque files canonicalizado>"
}
```

## E. Enforcement

| Condicion | Accion |
|---|---|
| Sync sin manifest | ABORT (fail-closed) |
| Mismatch de sha256 en cualquier archivo | FAILED + rollback, no PARTIAL |
| Conteo destino != conteo esperado | ABORT + escala al CEO |
| Promocion con delete sin diff aprobado | BLOQUEADA |
| Falta log firmado post-sync | cambio NO reconocido como canonico |

## F. Relacion con otras piezas

- Complementa `SKILL_KB_GATEWAY` (lock distribuido + manifest_version_check + atomic write):
  este POL agrega la capa de hash + reconciliacion de conteos + log firmado que el gateway
  no especifica.
- Se apoya en `DASHBOARD_SNAPSHOT` como fuente unica de conteos esperados.
- Respeta `POL_OUTAGE_CANONICAL_MIRROR`: en estado OUTAGE, el sync se bloquea igual.
- No edita `hooks/` (control_surface). La integracion en hooks pretooluse es implementacion
  diferida a sprint, no parte de esta politica.

## G. Pendientes (L1-L)

- L1: decidir formato de firma del log (sha256 simple vs GPG) -- [PENDIENTE -- decision CEO].
- L2: implementar el calculo de hash en `sync_*_indexa.ps1` (PowerShell Get-FileHash).
- L3: definir donde vive el log firmado (repo canonico vs externo) -- [PENDIENTE].

---

Changelog:
- v1.0 (2026-06-02): Creacion. Origen: gap P0 de auditoria externa 2026-06-02. DRAFT en
  generated_staging (mirror OneDrive), pendiente promocion a canonico via sync_*_indexa.ps1
  + append a MANIFIESTO_CAMBIOS_v2 + indexacion en IDX_GOBERNANZA seccion Policies. ASCII puro.
