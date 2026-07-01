# HOOKS_FAIL_CLOSED_SPEC -- Especificacion enforcement layer hooks Cowork/Claude Code

---
id: SPEC_HOOKS_FAIL_CLOSED
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Claude (sintesis post Round 3) + CEO
aplica_a: [MWT, FaberLoom]
relacionado_con:
  - PLAN_INTEGRACION_v4_POST_ROUND3.md (B0.5)
  - hooks/config.json (B1.1)
  - hooks/sessionstart.py (B1.4)
  - hooks/pretooluse_canonical_protect.py (B1.5)
  - hooks/userpromptsubmit_reminder.py (B1.6)
  - ROOT_FILE_CLASSIFICATION.md
origen: |
  Round 3 auditoria externa hallazgo #9: hooks/config.json read-only no es
  inmune si actor puede borrar config. El control debe fallar cerrado y
  tener verificacion externa.
---

## 1. Proposito

Especificar comportamiento fail-closed de hooks Cowork/Claude Code para evitar bypass por:
1. Borrar `hooks/config.json`
2. Modificar `hooks/config.json` para autorizar writes ilegales
3. Modificar codigo de hooks para skipear checks
4. Self-modification recursiva (hook que autoriza editar su propio config)

**Vinculante desde:** B1 (cuando hooks se instalan).

## 2. Principio fail-closed

> Si cualquier verificacion falla -> deny all canonical writes.
> Nunca fail-open. Nunca skip silencioso. Nunca asumir intencion benigna.

Caso degenerado: si `hooks/config.json` no existe, hooks deben deny TODA operacion de escritura al canonico hasta que CEO restaure el config con audit.

## 3. Verificaciones obligatorias por hook

### 3.1 Verificaciones comunes (todos los hooks)

```python
# hooks/_common.py (compartido)

def verify_config_integrity():
    """
    Llamado al inicio de CADA hook.
    Si falla, hook devuelve {"blocked": True, "reason": "config_integrity_failed"}.
    """
    config_path = "hooks/config.json"

    # Check 1: existe
    if not os.path.exists(config_path):
        log_audit("config_missing", severity="critical")
        return False

    # Check 2: hash esperado
    with open(config_path, 'rb') as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    expected_hash = read_expected_hash_from_manifest()
    if actual_hash != expected_hash:
        log_audit("config_hash_mismatch", severity="critical",
                  expected=expected_hash, actual=actual_hash)
        return False

    # Check 3: parseable JSON
    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError:
        log_audit("config_invalid_json", severity="critical")
        return False

    # Check 4: schema valido
    if not validate_config_schema(config):
        log_audit("config_schema_invalid", severity="critical")
        return False

    return True
```

### 3.2 hooks/sessionstart.py (verificacion + reglas)

```python
def hook(context):
    if not verify_config_integrity():
        return {
            "system_reminder": (
                "ENFORCEMENT BLOCKED: hooks/config.json invalido o ausente. "
                "Cowork no puede operar hasta que CEO restaure config. "
                "Ver HOOKS_FAIL_CLOSED_SPEC.md."
            ),
            "block_session": True
        }

    # Cargar reglas activas desde config valido
    config = load_config()
    rules = config["rules_active"]

    return {
        "system_reminder": format_rules_reminder(rules),
        "block_session": False
    }
```

### 3.3 hooks/pretooluse_canonical_protect.py (verificacion + classification)

```python
def hook(context):
    # Fail-closed inmediato si config invalido
    if not verify_config_integrity():
        return {
            "blocked": True,
            "reason": "config_integrity_failed_deny_all_writes"
        }

    # Solo aplica a Write/Edit
    if context.tool_name not in ["Write", "Edit"]:
        return {"blocked": False}

    config = load_config()
    target_path = context.args.get("file_path", "")
    actor = context.actor or "cowork"

    # Classification path -> categoria
    category = classify_path(target_path, config["paths_classification"])

    if category is None:
        # Path no clasificado -> fail-closed
        log_audit("unclassified_path_write_attempt",
                  path=target_path, actor=actor, severity="high")
        return {
            "blocked": True,
            "reason": f"Path not in classification: {target_path}. "
                      f"Update ROOT_FILE_CLASSIFICATION.md first."
        }

    # Aplicar write_policy de categoria
    write_policy = config["allowed_writers"][category]

    if actor not in write_policy:
        log_audit("unauthorized_write_attempt",
                  path=target_path, category=category,
                  actor=actor, allowed=write_policy, severity="critical")
        return {
            "blocked": True,
            "reason": (
                f"Actor '{actor}' not authorized for category '{category}'. "
                f"Allowed: {write_policy}. "
                f"Use gateway, break-glass, or sync_*_indexa.ps1."
            )
        }

    # OK
    log_audit("authorized_write", path=target_path, category=category, actor=actor)
    return {"blocked": False}
```

### 3.4 hooks/userpromptsubmit_reminder.py

```python
def hook(context):
    if not verify_config_integrity():
        return {
            "prefix": "[!! ENFORCEMENT BLOCKED - config invalid !!]"
        }

    config = load_config()
    return {
        "prefix": format_short_reminder(config["rules_active"])
    }
```

## 4. Anti self-modification (R3#10b)

Regla dura: `hooks/config.json` NO puede ser editado desde Cowork ni desde hooks mismos.

```python
def classify_path(path: str, classification: dict) -> str:
    # Hardcoded check: control_surface incluye hooks/config.json
    # incluso si alguien manipulara classification dynamic
    HARDCODED_CONTROL_SURFACE = [
        "hooks/config.json",
        "hooks/_common.py",
        "hooks/sessionstart.py",
        "hooks/pretooluse_canonical_protect.py",
        "hooks/userpromptsubmit_reminder.py"
    ]

    for protected in HARDCODED_CONTROL_SURFACE:
        if path.endswith(protected) or path.endswith(protected.replace("/", "\\")):
            return "control_surface"  # SIEMPRE control_surface

    # Despues consultar classification dynamic
    return classification.get(path) or classify_by_pattern(path, classification)
```

**Razon:** si alguien modifica `hooks/config.json` para clasificar `hooks/config.json` como `non_canonical_misc`, el classification dynamic permitiria editarlo. El hardcoded check rompe este loop.

## 5. CI integration

`.github/workflows/hooks_integrity.yml`:

```yaml
name: Hooks Integrity Check
on:
  pull_request:
    paths:
      - 'hooks/**'
      - 'HOOKS_FAIL_CLOSED_SPEC.md'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify hooks/config.json hash matches manifest
        run: |
          ACTUAL_HASH=$(sha256sum hooks/config.json | cut -d' ' -f1)
          EXPECTED_HASH=$(cat hooks/config_expected_hash.txt)
          if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
            echo "ERROR: hooks/config.json modificado sin actualizar manifest"
            echo "Expected: $EXPECTED_HASH"
            echo "Actual:   $ACTUAL_HASH"
            exit 1
          fi
      - name: Verify hardcoded control_surface in pretooluse
        run: |
          if ! grep -q '"hooks/config.json"' hooks/pretooluse_canonical_protect.py; then
            echo "ERROR: hooks/config.json no esta en HARDCODED_CONTROL_SURFACE"
            exit 1
          fi
```

CI **bloquea merge** si:
- `hooks/config.json` cambio sin actualizar `hooks/config_expected_hash.txt`
- Hardcoded control_surface check fue removido de pretooluse hook

## 6. Break-glass procedure

Si CEO necesita modificar `hooks/config.json` legitimamente:

```bash
# 1. Crear nota de break-glass
cat > docs/anexos/auditorias/break_glass/BREAK_GLASS_<fecha>_<razon>.md <<EOF
---
id: BREAK_GLASS_<fecha>_<razon>
fecha: <fecha>
actor: CEO
razon: <razon detallada>
duration: 24h
---
EOF

# 2. Modificar hooks/config.json
# (manual, fuera de Cowork)

# 3. Recalcular hash
sha256sum hooks/config.json | cut -d' ' -f1 > hooks/config_expected_hash.txt

# 4. Commit con audit
git add hooks/config.json hooks/config_expected_hash.txt docs/anexos/auditorias/break_glass/
git commit -m "[GOBERNANZA] BREAK-GLASS: <razon> - hooks/config.json updated"
git push

# 5. Confirmar break-glass cerrado en 24h max
```

## 7. Tests obligatorios (B1.7 + B1.8 + B1.9)

### B1.7 Test 29-abr-style

```python
def test_block_canonical_docs_write_from_cowork():
    """Cowork intenta escribir docs/ raiz canonico -> debe bloquear."""
    result = simulate_pretooluse_hook(
        tool="Write",
        path="docs/CLAUDE.md",  # control_surface
        actor="cowork"
    )
    assert result["blocked"] == True
    assert "control_surface" in result["reason"]
```

### B1.8 Test config tampering

```python
def test_config_tampering_detected():
    """Modificar hooks/config.json sin actualizar hash -> hook deny all."""
    # Modificar config.json (simular ataque)
    with open("hooks/config.json", "a") as f:
        f.write("\n// inyeccion maliciosa")

    result = simulate_pretooluse_hook(
        tool="Write",
        path="docs/anexos/test.md",
        actor="cowork"
    )
    assert result["blocked"] == True
    assert "config_integrity" in result["reason"]
```

### B1.9 Test config faltante

```python
def test_config_missing_deny_all():
    """Borrar hooks/config.json -> hook deny all canonical writes."""
    os.remove("hooks/config.json")

    result = simulate_pretooluse_hook(
        tool="Write",
        path="docs/anexos/test.md",  # incluso non_canonical_misc
        actor="cowork"
    )
    assert result["blocked"] == True
    assert "config_missing" in result["reason"]
```

## 8. Audit log obligatorio

Cada invocacion de hook escribe a `audit/hooks_<YYYY-MM-DD>.jsonl`:

```jsonl
{"ts": "2026-05-07T22:45:01Z", "event": "config_missing", "severity": "critical", "actor": "cowork"}
{"ts": "2026-05-07T22:45:02Z", "event": "deny_write", "path": "hooks/config.json", "actor": "cowork"}
{"ts": "2026-05-07T22:45:15Z", "event": "authorized_write", "path": "docs/anexos/notes/foo.md", "actor": "sync_indexa_script", "category": "canonical_docs"}
```

Audit log es append-only, rotacion mensual, retention 7 anos (audit class N3).

## 9. Changelog

```
v1.0 (2026-05-07): Especificacion inicial post Round 3 auditoria.
                   Fail-closed obligatorio. Hardcoded control_surface.
                   CI integration. Break-glass procedure. Tests B1.7-B1.9.
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Corregido id HOOKS_FAIL_CLOSED_SPEC → SPEC_HOOKS_FAIL_CLOSED. v1.0 se mantiene.
```

---

**Fin de la especificacion.**
