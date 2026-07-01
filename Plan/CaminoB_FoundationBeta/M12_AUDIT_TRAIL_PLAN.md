# M12 Audit Trail — Plan de Implementación

## 1. Resumen ejecutivo

M12 registra cada acción sensible en una cadena de hash inmutable por tenant, append-only y exportable para compliance.  Es el quinto módulo del SPINE; sin él no hay trazabilidad ni evidence bundle.

**Rol en el SPINE:** consume `tenant_context` (M16), `actor_role_at_decision` (M09) y eventos (M15).  Alimenta a M11, M13, M14, M17 con el audit writer.

## 2. Entrada/salida

### Entrada
- Acciones auditables de cualquier módulo.
- Contexto: tenant_id, user_id, actor_id, actor_role_at_decision, case_id, modelo usado, hashes.

### Salida
- Fila append-only en `audit_log` con 18 campos canónicos + `sha_chain`.
- Job diario de validación de cadena.
- Export per-tenant CSV/JSON firmado.
- Evento `audit.entry.created`.

## 3. Modelo de datos

### Tabla

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id TEXT,
    action_id TEXT NOT NULL,
    data_class TEXT NOT NULL DEFAULT 'N1',
    task_type TEXT,
    model_provider TEXT,
    model_id TEXT,
    model_version TEXT,
    orchestrator_policy_pool_hash TEXT,
    prompt_hash TEXT,
    output_hash TEXT,
    human_gate_required BOOLEAN NOT NULL DEFAULT FALSE,
    human_approver_id UUID REFERENCES users(id),
    sha_chain_prev TEXT,
    sha_chain_curr TEXT NOT NULL,
    seq_no BIGINT NOT NULL,
    chain_id TEXT NOT NULL,
    actor_id UUID NOT NULL,
    actor_role_at_decision TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_tenant_chain ON audit_log(tenant_id, chain_id, seq_no);
CREATE INDEX idx_audit_log_tenant_case ON audit_log(tenant_id, case_id, created_at);
CREATE INDEX idx_audit_log_tenant_actor ON audit_log(tenant_id, actor_id, created_at);

CREATE SEQUENCE audit_seq;
```

### Triggers append-only

```sql
CREATE OR REPLACE FUNCTION reject_audit_mutation() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();

CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
```

### App role

```sql
CREATE ROLE faberloom_app;
GRANT INSERT, SELECT ON audit_log TO faberloom_app;
REVOKE UPDATE, DELETE ON audit_log FROM faberloom_app;
```

## 4. Cambios en API/backend

### AuditWriter

```python
# apps/audit/writer.py
import hashlib
import json
from django.db import connection

class AuditWriter:
    def write(self, ctx, action_id, *, case_id=None, data_class='N1',
              model_provider=None, model_id=None, model_version=None,
              policy_pool_hash=None, prompt_hash=None, output_hash=None,
              human_gate_required=False, human_approver_id=None,
              payload=None):
        tenant_id = ctx.tenant_id
        chain_id = f"{tenant_id}:default"
        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('audit_seq')")
            seq_no = cursor.fetchone()[0]
            cursor.execute(
                "SELECT sha_chain_curr FROM audit_log WHERE chain_id=%s ORDER BY seq_no DESC LIMIT 1",
                [chain_id]
            )
            row = cursor.fetchone()
            sha_chain_prev = row[0] if row else "0" * 64

        payload_blob = json.dumps(payload or {}, sort_keys=True, ensure_ascii=False)
        hash_input = (
            f"{tenant_id}|{case_id}|{action_id}|{data_class}|{task_type}|"
            f"{model_provider}|{model_id}|{model_version}|{policy_pool_hash}|"
            f"{prompt_hash}|{output_hash}|{human_gate_required}|{human_approver_id}|"
            f"{seq_no}|{chain_id}|{payload_blob}|{sha_chain_prev}"
        )
        sha_chain_curr = hashlib.sha256(hash_input.encode()).hexdigest()

        return AuditLog.objects.create(
            tenant_id=tenant_id,
            case_id=case_id,
            action_id=action_id,
            data_class=data_class,
            actor_id=ctx.actor_id,
            actor_role_at_decision=ctx.actor_role_at_decision,
            # ... resto de campos
            sha_chain_prev=sha_chain_prev,
            sha_chain_curr=sha_chain_curr,
            seq_no=seq_no,
            chain_id=chain_id,
            payload_json=payload,
        )
```

### Integración con M15

- Las acciones críticas se escriben en `audit_log` dentro de la transacción de negocio; el evento `audit.entry.created` se emite al outbox para notificar a consumidores.

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/audit` | audit:view / audit:view_self |
| GET | `/api/audit/export` | audit:export |
| POST | `/api/audit/validate` | audit:export (Owner/Admin) |

### Job de validación

- Celery beat diario recorre cada `chain_id` verificando `sha_chain_curr`.
- Si hay ruptura: alerta P0 + congela exports hasta investigar.

## 5. Cambios en frontend

### Web
- Vista "Audit": lista cronológica filtrable por caso/actor/fecha.
- Botón "Exportar compliance" genera CSV/JSON firmado.
- Badge si validación diaria detecta ruptura.

### Desktop
- Operator ve solo audit de sus propias acciones (`audit:view_self`).

## 6. Cambios en infraestructura/deploy

- Migración con triggers append-only y app role.
- Variables de entorno:
  ```bash
  AUDIT_EXPORT_FORMAT=json,csv
  AUDIT_VALIDATION_HOUR=2
  ```
- Celery beat para validación diaria.

## 7. Secuencia de tareas

1. Crear app Django `audit`.
2. Modelo `AuditLog` con 18 campos.
3. Secuencia `audit_seq`.
4. Implementar triggers NO UPDATE/DELETE.
5. Configurar app role sin UPDATE/DELETE.
6. Implementar `AuditWriter.write()`.
7. Integrar `AuditWriter` en M08, M09, M11, M13, M07.
8. Implementar endpoints de consulta/export/validación.
9. Job diario de validación de cadena.
10. Tests de integridad.
11. UI web/desktop.

## 8. Criterios de aceptación

1. `test_audit_writer_append_only_tenant_scoped_chain`: inserción correcta con hash chain.
2. Intentar UPDATE/DELETE en `audit_log` falla.
3. App role no puede UPDATE/DELETE.
4. Job diario valida todas las cadenas sin ruptura.
5. Export per-tenant incluye reporte de validación.
6. Ruptura de cadena dispara alerta P0.
7. Cada acción auditable tiene `actor_role_at_decision`.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Audit mutable por DB admin | P0 compliance | Triggers + app role |
| Hash chain global | P1 fuga metadatos | Chain por `tenant_id:domain` |
| Escritura audit falla | P1 pérdida trazabilidad | Fail-closed: acción no completa sin audit |
| Performance con millones de filas | P2 latencia | Índices por tenant/seq/case/actor; partición futura |
| Export expone N3/N4 | P0 fuga | Hashes, no contenido en claro |

## 10. Decisiones de arquitectura tomadas

1. **18 campos canónicos del SPEC M12.**  Es el superset del SCH; cubre evidence bundle.
2. **Hash chain por `chain_id = tenant_id:domain`.**  Aisla cadenas y permite dominios de auditoría separados.
3. **Append-only con triggers + app role.**  Defensa en profundidad.
4. **Acción auditable no completa sin entrada de audit.**  Fail-closed; en caso de imposibilidad se revierte.
5. **Export con reporte de validación.**  Entregable para auditores externos.

---
*Plan M12 — Foundation Beta v1.3.1*
