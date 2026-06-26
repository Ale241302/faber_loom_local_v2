# Auditoría senior — FaberLoom/SpaceLoom

**Alcance:** revisión estática del repo `app/` y plan vigente. No modifiqué archivos. Tomo como premisa que los 112 tests pasan; aun así, varios tests validan seams/mocks, no cierre real de hito producto.

## 1) Faltantes técnicos para cerrar hitos

### SL2b/c — KB y drafts con fuente
- La KB existe, pero la validación “cero dato inventado” no se re-ejecuta tras editar un draft. `app/src/kb.py::update_draft` solo cambia `subject/body_md`; `app/src/kb.py::approve_draft` solo bloquea `blockers_json != "[]"`.
- `requires_confirmation` y `warnings_json` no impiden aprobación/exportación. Esto permite aprobar drafts con fuente vencida o cita incompleta si no hay blocker formal.
- Ingesta PDF/XLSX es funcional pero heurística: primera columna = `entity_key`; no hay contrato de schema por proveedor/cliente ni autorización explícita de fuentes.

### SL3a — Skills/Routine Hub
- `app/src/skills.py` es un parser/linter, no un sandbox real. No ejecuta herramientas, no valida JSON Schema completo, y no emite formalmente un subconjunto de `SCH_FB_SKILL_MANIFEST_v2`.
- Crear rutinas por API (`app/src/api.py::api_create_routine`) no parece exigir flujo de autoría → HITL → aprobación, solo valida contenido peligroso básico.

### SL3b/c — WorkLoom + gold loop
- WorkLoom lista items, pero faltan urgencia, razón de aprobación/rechazo, historial editorial rico y criterios de cola.
- Gold loop crea/promueve candidatos, pero no se integra de vuelta al motor de drafts/skills. Tampoco hay segundo gate independiente para “campos duros”.

### SL3.5 — Sellado/llave graduada
- El HMAC protege principalmente contra mover filas entre workspaces, no contra tampering del contenido; el mensaje firmado es solo `workspace_id:row_id`.
- `app/src/api.py::api_seal_check` expone `seal_id`, que es la clave del HMAC. Debe eliminarse o limitarse a diagnóstico no sensible.
- No hay SQLCipher/cifrado local de la DB. Solo hay backup opcional cifrado en `app/src/backup.py`.

### SL5 — Correo
- El envío exige draft aprobado, pero no doble confirmación explícita en el endpoint de envío. `app/src/api.py::api_send_mail_reply` puede enviar con cualquier llamada posterior a la aprobación.
- No hay outbox/idempotency: si SMTP envía y luego falla la actualización local, puede haber reenvío.
- Parsing de email es mínimo: `From` se usa como destinatario sin normalización fuerte; HTML se reduce con regex.

### SL4 — Desktop/packaging
- Existe `app/build.py` y `app/SpaceLoom.spec`, pero falta evidencia de build firmado real, instalador, notarización/firma, auto-update productivo y smoke en OS destino.
- `SpaceLoom.spec` incluye `app/data` en el bundle: riesgo de empacar DB/audit locales. Además la DB debería vivir en AppData/Application Support, no dentro del bundle.
- La UI en `app/static/js/app.jsx` sigue siendo shell SL0/no-op; no hay flujos reales para KB, drafts, Routine Hub, WorkLoom, router ni mail.

## 2) Errores, riesgos y deuda técnica

- **P0 HITL/borrado:** `app/src/api.py::api_delete_kb_source` y `api_delete_routine` borran sin doble confirmación ni auditoría visible.
- **Cross-tenant futuro incompleto:** varias queries filtran solo `workspace_id`, no `tenant_id`: `app/src/db.py` routine/routine_run, `app/src/kb.py` facts/chunks, `app/src/gold.py`, `app/src/workloom.py`.
- **Campos latentes incompletos:** tablas como `kb_chunk`, `kb_fact`, `gold_candidate` y `mail_message` no tienen toda la superficie contract-first (`actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `approved_by`, etc.).
- **API local sin auth/CSRF:** FastAPI escucha en `127.0.0.1`, pero no hay token local, origin check ni CSRF guard. Un sitio malicioso podría intentar acciones contra localhost.
- **Auditoría no siempre atómica:** varias mutaciones escriben audit después de la transacción principal; si hay crash, puede quedar mutación sin evento.
- **IMAP duplicados:** `mail_message` tiene `UNIQUE(workspace_id, account, mail_uid)`, pero `create_mail_message` no usa upsert/ignore; un sync repetido puede romper toda la operación.
- **Backup smoke destructivo:** `smoke_test_export_restore` corrompe temporalmente la DB objetivo. Útil en test aislado, peligroso si se expone contra DB real.
- **Tests demasiado mockeados:** cubren contratos internos, pero no validan proveedor real, IMAP/SMTP real, build PyInstaller real, migración desde DB antigua ni ataque navegador-local.

## 3) Recomendaciones concretas

1. **Cerrar P0 HITL:** añadir `confirmation_token`, `idempotency_key`, `approved_by`, `approved_at`, `confirmed_at` para envío/export/borrado. Rutas: `app/src/api.py`, `app/src/models.py`, `app/src/db.py`.
2. **Revalidar drafts al editar/aprobar:** en `app/src/kb.py` y `app/src/draft_engine.py`, recalcular hard facts/blockers al cambiar `body_md`; bloquear aprobación si `requires_confirmation` salvo confirmación explícita.
3. **Tenant contract v9:** migración en `app/src/models.py`; actualizar queries en `app/src/db.py`, `app/src/kb.py`, `app/src/gold.py`, `app/src/workloom.py` para exigir `(workspace_id, tenant_id)`.
4. **Eliminar fuga de seal:** cambiar `app/src/api.py::api_seal_check` para no devolver `seal_id`; en `app/src/seal.py`, firmar payload canónico si se desea integridad.
5. **Correo seguro:** en `app/src/connectors/imap.py`, parsear direcciones con `email.utils`, sanitizar HTML, rechazar canaries; en `app/src/api.py`, implementar outbox antes de SMTP.
6. **Packaging real:** mover DB a directorio de usuario en `app/src/db.py`; excluir `app/data` de `app/SpaceLoom.spec`; añadir CI de `app/build.py --sign`.
7. **UI de hitos:** reemplazar shell en `app/static/js/app.jsx` por flujos mínimos: KB upload/search, draft approve/export, Routine Hub, WorkLoom y mail.
8. **Tests P0 nuevos:** crear `app/tests/test_p0_security.py` para CSRF/localhost, delete HITL, send idempotency, duplicate IMAP, draft edit inventado, tenant leakage y packaging sin DB local.