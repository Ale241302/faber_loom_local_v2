# ROOT_FILE_CLASSIFICATION -- Clasificacion de archivos en raiz canonico

---
id: POL_ROOT_FILE_CLASSIFICATION_v1
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
  - PLAN_INTEGRACION_v4_POST_ROUND3.md (B0.4)
  - HOOKS_FAIL_CLOSED_SPEC.md
  - hooks/config.json (B1.1)
origen: |
  Round 3 auditoria externa hallazgos #2 y #11:
  - Whitelist root files puede permitir editar control surface
  - Falta categoria generated_staging para archivos generados pre-canonizacion
  - Falta proteccion explicita de CLAUDE.md, WIKI.md, hooks/config.json
---

## 1. Proposito

Clasificar todos los paths del repo canonico en categorias con write_policy especifica. Los hooks PreToolUse leen esta clasificacion para autorizar/bloquear writes desde Cowork.

**Vinculante desde:** B1.5 (cuando hooks PreToolUse se instalan).

## 2. Las 6 categorias

| Categoria | Write policy | Quien puede editar |
|---|---|---|
| **control_surface** | gateway_or_break_glass_only | CEO + script firmado + break-glass auditado |
| **repo_config** | manual_or_gateway | Manual PR desde CLI o gateway script |
| **scripts** | gateway_or_versioned_pr | Script generado por Cowork con manifest + version |
| **canonical_docs** | gateway_only_via_sync_indexa_script | SOLO scripts sync_*_indexa.ps1 con manifest selectivo |
| **generated_staging** (NUEVA R3) | cowork_with_audit | Cowork puede escribir, pero solo en raiz mirror antes de canonizacion |
| **non_canonical_misc** | gateway_or_cowork_with_audit | Cowork con audit log |

## 3. Mapeo paths -> categoria

### 3.1 control_surface (proteccion maxima)

```yaml
control_surface:
  paths:
    - CLAUDE.md
    - WIKI.md
    - README.md
    - hooks/config.json
    - hooks/*.py
    - .gitattributes
    - .gitignore (parcial -- ver excepcion abajo)
    - ANTI_RATIONALIZATION_REGISTRY.md
    - BRANCH_PR_POLICY.md
    - ROOT_FILE_CLASSIFICATION.md
    - HOOKS_FAIL_CLOSED_SPEC.md
    - MODEL_ASSUMPTIONS_REGISTRY.md
  write_policy: gateway_or_break_glass_only
  rationale: |
    Si Cowork puede editar control_surface, puede desactivar su propio
    enforcement. Categoria mas critica.
```

### 3.2 repo_config

```yaml
repo_config:
  paths:
    - .gitignore
    - mirror_to_onedrive.ps1
    - setup_local_dev.ps1
  write_policy: manual_or_gateway
  rationale: |
    Configuracion del repo que cambia raramente. Manual PR aceptable
    para evolucion incremental.
```

### 3.3 scripts

```yaml
scripts:
  paths:
    - scripts/*.ps1
    - sync_*_indexa.ps1  # raiz canonico (legacy, migrar a scripts/)
  write_policy: gateway_or_versioned_pr
  rationale: |
    Scripts auditables que ejecutan logica critica (canonizacion, mirror).
    Cambios deben pasar PR con review.
```

### 3.4 canonical_docs

```yaml
canonical_docs:
  paths:
    - docs/**/*.md
    - docs/**/*.json
    - docs/**/*.html
  exclusiones:
    - docs/anexos/auditorias/manifest_a0_freeze_*.json  # evidencia inmutable, ver generated_staging
  write_policy: gateway_only_via_sync_indexa_script
  rationale: |
    Documentos KB son source of truth. SOLO scripts sync_*_indexa.ps1 con
    manifest selectivo pueden escribir aqui. NO `git add .`, NO Cowork libre.
```

### 3.5 generated_staging (CATEGORIA NUEVA R3)

```yaml
generated_staging:
  paths:
    # Raiz mirror OneDrive (NO en canonico)
    - mirror_root/*_DRAFT_LISTO_INDEXAR.md
    - mirror_root/*_DRAFT.md
    - mirror_root/manifest_*_freeze.json
    - mirror_root/swarm_*_research_bruto/  # carpetas temporales pre-canonizacion
  write_policy: cowork_with_audit
  rationale: |
    Material generado por Cowork antes de canonizacion. Vive en mirror OneDrive
    (NO canonico) hasta que sync_*_indexa.ps1 lo mueva. Cowork puede escribir
    libremente aqui porque no afecta canonico hasta sync.

    A0 demostro la necesidad: 11+ drafts vivieron en raiz OneDrive antes de
    sync_kimi_swarm_6_indexa.ps1 los movio al canonico.
  lifecycle:
    creado_por: cowork
    promovido_a_canonico: via sync_*_indexa.ps1 con manifest hash
    borrado_post_sync: automatico (mirror se sincroniza con canonico,
                       drafts no existen en canonico, mirror los borra)
```

### 3.6 non_canonical_misc

```yaml
non_canonical_misc:
  paths:
    - reportes/**
    - audit/iteraciones_*/  # iteraciones historicas archivadas
    - .vscode/  # editor config local
    - .env*  # ambiente local
  write_policy: gateway_or_cowork_with_audit
  rationale: |
    Archivos que no son canonicos pero viven en repo. Cowork puede editar
    con audit log obligatorio. No son source of truth.
```

## 4. Categoria primaria + tags secundarios (R3#11)

Algunos archivos pueden requerir tags secundarios:

```yaml
# Ejemplo: docs/MANIFIESTO_APPEND_<fecha>_<tema>.md
file: docs/MANIFIESTO_APPEND_20260507_KIMI_SWARM_6_INTEGRATION.md
primary_category: canonical_docs
secondary_tags:
  - audit_evidence  # es evidencia auditoria
  - immutable  # no se modifica post-creacion
write_policy_effective: gateway_only_via_sync_indexa_script + immutable_after_creation
```

## 5. Decision tree para hooks PreToolUse

```python
# Pseudo-codigo simplificado (B1.5)
def authorize_write(path: str, actor: str) -> bool:
    classification = classify_path(path)

    if classification == 'control_surface':
        if actor not in ['gateway', 'break_glass']:
            return False  # bloquear
        verify_audit_log(actor, path)

    elif classification == 'canonical_docs':
        if actor != 'sync_indexa_script':
            return False  # bloquear

    elif classification == 'generated_staging':
        # Cowork libre, pero audit
        log_audit(actor, path, 'cowork_staging_write')

    elif classification == 'scripts':
        if not has_versioned_pr_or_gateway(actor):
            return False

    elif classification in ['repo_config', 'non_canonical_misc']:
        # Permitido con audit
        log_audit(actor, path, classification)

    return True
```

## 6. Casos de borde

### 6.1 Archivo que cambia categoria

Ejemplo: `manifest_a0_freeze.json` empieza como `generated_staging` (raiz mirror), despues se promueve a `canonical_docs` (post sync) en `docs/anexos/auditorias/manifest_a0_freeze_20260507.json`.

**Regla:** la categoria depende del path actual del archivo, no de su origen.

### 6.2 Archivo en path nuevo no clasificado

Si Cowork intenta crear archivo en path no listado en ninguna categoria, hook debe **fail-closed**: deny y solicitar update de classification.

### 6.3 Archivos legacy pre-policy

Archivos existentes pre-2026-05-07 quedan en categoria por path actual. Si necesitan re-clasificacion, requiere PR explicito.

## 7. Updates a esta clasificacion

Cuando se agrega nuevo prefijo de taxonomia (ej. WS_, CTX_, AGT_), o cuando se crea categoria nueva:

1. Bumpear este archivo a v1.X+
2. Actualizar `hooks/config.json` con nuevos paths/categorias
3. Hooks deben re-cargar config (sin restart)
4. Tests B1.7-B1.9 deben re-ejecutarse

## 8. Changelog

```
v1.0 (2026-05-07): Clasificacion inicial post Round 3 auditoria.
                   6 categorias incluyendo generated_staging (NUEVA).
                   Mapeo paths exhaustivo. Decision tree para hooks.
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Corregido id ROOT_FILE_CLASSIFICATION → POL_ROOT_FILE_CLASSIFICATION_v1. v1.0 se mantiene.
```

---

**Fin de la clasificacion.**
