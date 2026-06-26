# Auditoría Fugu — Bloqueantes SL1b

**Fecha:** 2026-06-25  
**Fase:** SL1b — ready_for_audit  
**Origen:** consulta explícita del orquestador a fugu para desbloquear avance hacia SL2a.  
**Veredicto preliminar:** SL1b está en **GATE NO CERRADO**. El código es funcional y los 37 tests pasan, pero el hito no se considera aprobado mientras la KB esté alimentada con fixtures demo y no exista un pack MWT real autorizado por Alvaro.

---

## 1. Auditoría de SL1b (inmediato)

**Diagnóstico fugu**
SL1b es el primer hito que debe demostrar un **draft real contra una mini-KB real de MWT + HITL mínimo** (aprobar/editar/exportar o enviar). Avanzar a SL2a sin auditar contra ese DoD acumula deuda funcional y de seguridad (P0: dato inventado, envío sin HITL, fuga cross-workspace).

**Acción concreta para destrabarlo**
- Ejecutar auditoría de código SL1b contra el DoD del hito y la enmienda v1.1 del plan (`Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`, Secciones 7.1–7.5).
- Verificar: router mínimo funcional, chat, generación de draft, HITL gate, trazabilidad a fuente KB, workspaces, tests.
- Emitir veredicto **PASS / NEEDS_FIX / BLOCK** con issues numerados, severidad y evidencia.

**Responsable sugerido**
- **fugu** como auditor.
- **dev** para reparar issues.
- **Alvaro (CEO)** para validar utilidad del flujo con datos reales.

**Artefacto a guardar**
- `harness/reports/AUDIT_SL1b_FUGU_v1.md` con verdicto, issues, fixes y condición de salida.
- Actualizar `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` con estado de SL1b.

**Si es un test/DoD**
- DoD de SL1b en el plan.
- Tests en `app/tests/test_sl1b_*.py`.

---

## 2. Datos MWT reales (bloquea dogfood de SL1b)

**Diagnóstico fugu**
Hoy la KB tiene fixtures demo explícitos. SL1b exige un draft contra datos reales de MWT. Sin eso el dogfood es simulado y se corre el riesgo de declarar adopción sobre base falsa.

**Acción concreta para destrabarlo**
- Alvaro autoriza y entrega un **pack MWT real autorizado**: catálogo, precios, equivalencias, talles, imágenes/descripciones, vigencia, confidencialidad.
- Dev crea workspace MWT de prueba, ingiere el pack y genera al menos un draft real que cite fuente.
- fugu valida que el draft no invente datos y que cada campo duro tenga fuente trazable.

**Responsable sugerido**
- **Alvaro (CEO)** para autorizar y entregar el pack.
- **dev** para ingestión y generación de draft real.
- **fugu** para validar trazabilidad.

**Artefacto a guardar**
- `docs/data/MWT_SEED_PACK_v1.md`: inventario de archivos, vigencia, confidencialidad, owner, aprobación escrita de Alvaro.
- Backup cifrado del pack en `app/data/mwt_seed/` si es confidencial.
- Test `test_sl1b_draft_cites_mwt_real_source` en `app/tests/`.

**Si es un test/DoD**
- DoD SL1b: “Generar un draft real a partir del pack MWT autorizado, con citas de fuente KB”.
- Tests en `app/tests/test_sl1b_kb_real.py`.

---

## 3. Decisiones del CEO pendientes

**Diagnóstico fugu**
El plan sigue en DRAFT por decisiones estratégicas sin cerrar. La ambigüedad aumenta riesgo de over-build, sub-scope o bloqueo legal/comercial.

**Acción concreta para destrabarlo**
Convocar una **sesión de decisión CEO** con Alvaro, fugu y dev. Obtener respuesta concreta y binaria para cada punto, documentarla y actualizar artefactos.

| Decisión | Respuesta esperada |
|---|---|
| Ratificar carve-out / freeze scope de Etapa 1 | Aprobación escrita del documento de freeze scope |
| Licencia FSL y marca registrada | Elegir FSL-1.1 u otra; iniciar registro de marca |
| Dedicación | ¿1 dev full-time? ¿quién? (nombre/rol/disponibilidad) |
| SL5 (correo) | ¿Entra en Etapa 1 o se difiere? |
| Calendario | ¿8–10 semanas dogfood o 14–18 semanas distribuible? |
| Adopción | Definir N de casos reales y criterio de adopción |
| Cifrado local | ¿Obligatorio siempre o solo workspaces confidenciales? |

**Responsable sugerido**
- **Alvaro (CEO)** para decidir.
- **fugu** para asegurar decisiones binarias con implicancias explícitas.
- **dev** para actualizar plan y specs.
- **legal/ops** para licencia, marca y presupuestos.

**Artefacto a guardar**
- `Plan/DECISIONES_CEO_SL1b_v1.md` con cada decisión, fecha, owner e implicancia.
- Actualizar `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` Secciones 5, 6, 7 y 8.
- Crear/actualizar `Plan/DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md`.

**Si es un test/DoD**
- Cada decisión se refleja en DoD de hitos afectados:
  - Cifrado → DoD SL2a / SL3.5.
  - SL5 → dependencias y secuencia SL0–SL4.
  - Adopción → criterio de salida de SL1b/SL3c.

---

## 4. Dependencias externas

### 4a. Credenciales IMAP de Kimi Work → bloquea SL5

**Diagnóstico fugu**
SL5 requiere connector multi-cuenta, read-first, envío HITL. Sin credenciales IMAP reales y seguras no se puede desarrollar ni testear la recepción de correos.

**Acción concreta para destrabarlo**
- Alvaro solicita/rotar credenciales IMAP de Kimi Work (app password u OAuth).
- Entregarlas mediante vault seguro (Bitwarden/1Password) con scopes mínimos: lectura inicial, envío con 2FA/HITL.
- Dev implementa connector read-first; envío queda bloqueado tras HITL absoluto.

**Responsable sugerido**
- **Alvaro/ops** para obtener y rotar credenciales.
- **dev** para implementar connector.
- **fugu** para auditar que no haya secrets hardcodeados.

**Artefacto a guardar**
- `docs/ops/IMAP_CREDENTIALS_SL5.md`: rotación, vault, scopes, política de renovación.
- Código en `app/src/connectors/imap.py` leyendo desde variables de entorno/keyring.
- Tests `app/tests/test_imap_connector.py` con servidor local o mock.

**Si es un test/DoD**
- DoD SL5: “Recibe correo → genera draft → envío solo tras aprobación explícita”.
- Tests de seguridad: credenciales nunca en repo/logs, connector funciona con credenciales de entorno.

### 4b. Presupuesto firma de código → bloquea SL4

**Diagnóstico fugu**
SL4 requiere app firmada Win/Mac, instalable sin terminal, auto-update. Sin certificados, el usuario ve advertencias de seguridad y Gatekeeper/SmartScreen pueden bloquear la instalación.

**Acción concreta para destrabarlo**
- Aprobar presupuesto.
- Crear Apple Developer ID (USD 99/año) para notarización macOS.
- Adquirir certificado de firma de código Windows OV.
- Configurar CI/secrets para firma y verificación.
- Dev integra firma en build PyInstaller + auto-update.

**Responsable sugerido**
- **CEO/ops** para presupuesto y adquisición de certificados.
- **dev** para integración en build y auto-update.
- **fugu** para auditar que secrets de firma no estén en el repo y que update verifique firma.

**Artefacto a guardar**
- `docs/ops/CODE_SIGNING_BUDGET_SL4.md`: presupuesto aprobado, fechas, IDs de certificados, caducidades, renovación.
- Workflow de CI para firma con secrets.
- Test `test_update_rejects_unsigned_payload` en `app/tests/test_auto_update.py`.

**Si es un test/DoD**
- DoD SL4: “Instala un no-técnico sin ayuda y sin advertencias de seguridad”.
- DoD auto-update: “Rechaza paquetes sin firma válida; soporta rollback”.

---

## 5. DoD de seguridad/datos aún no cubiertos

### 5a. `source_to_field_check` completo (hoy parcial)

**Diagnóstico fugu**
Campos duros (precio, SKU, stock, margen, lead time, equivalencia) deben estar trazados a fuente vigente y autorizada. Hoy el check es parcial, por lo que el draft puede afirmar valores sin evidencia, violando P0 “dato inventado”.

**Acción concreta para destrabarlo**
- Definir schema de field check: para cada campo duro, indicar fuentes válidas (KB file + chunk), extracción del valor, confianza mínima.
- Implementar `SourceToFieldChecker` que exija `(source_id, chunk_id/fact_id, extracted_value, confidence)` antes de incluir un campo duro.
- Si falta fuente, el draft marca “requiere confirmación” en lugar de afirmar.

**Responsable sugerido**
- **Alvaro (CEO)** para validar qué campos son “duros” en MWT.
- **dev** para implementar el checker.
- **fugu** para auditar cobertura.

**Artefacto a guardar**
- `docs/contracts/source_to_field_schema.md`: lista de campos duros, fuentes válidas, reglas.
- Implementación en `app/src/kb/source_to_field.py`.
- Tests `app/tests/test_source_to_field_*.py`.

**Si es un test/DoD**
- DoD SL2: “0 campos duros sin fuente en draft”.
- Tests unitarios por campo duro; tests de integración con KB real.

### 5b. `stale_data_block` robusto (hoy solo vigencia demo en facts CSV)

**Diagnóstico fugu**
La vigencia demo no cubre PDFs/Excels sin fecha ni define umbral de staleness. Usar una fuente vencida es un error comercial grave; extiende P0 a “dato vencido presentado como vigente”.

**Acción concreta para destrabarlo**
- Definir política de vigencia por tipo de fuente con `valid_until` o `freshness_days`.
- Implementar `FreshnessGuard` que verifique `source_version`/`valid_until` antes de usar un campo duro.
- Si la fuente está vencida o no tiene fecha, el draft pide confirmación; no afirma.

**Responsable sugerido**
- **Alvaro (CEO)** para definir umbrales de vigencia por tipo de dato.
- **dev** para implementar `FreshnessGuard`.
- **fugu** para auditar.

**Artefacto a guardar**
- `docs/contracts/freshness_policy.md`: umbrales por tipo de fuente.
- Implementación en `app/src/kb/freshness_guard.py`.
- Tests `app/tests/test_stale_data_block.py`.

**Si es un test/DoD**
- DoD SL2: “Fuente vencida → draft pide confirmación, no afirma”.
- Tests con fuentes frescas, vencidas y sin fecha.

### 5c. Injection canaries en PDF/HTML/Excel/CSV/SKILL.md

**Diagnóstico fugu**
Los P0 incluyen inyección por contenido. Hoy solo se maneja texto plano. Formatos estructurados/binarios son vectores: fórmulas maliciosas en Excel/CSV, scripts en HTML, JavaScript en PDF, bloques inesperados en SKILL.md.

**Acción concreta para destrabarlo**
- Implementar parsers sandbox por formato:
  - **CSV/Excel**: bloquear celdas que inicien con `=`, `+`, `-`, `@`.
  - **HTML**: sanitizar, eliminar `<script>` y event handlers.
  - **PDF**: extraer texto plano, rechazar archivos con acciones JS.
  - **SKILL.md**: linter que valide estructura, bloques de código y tags permitidos.
- Crear banco de canaries conocidos por formato y verificar que el sistema no los ejecute ni los incluya sin sanitizar.

**Responsable sugerido**
- **dev** para implementar parsers y linter.
- **fugu** para auditar cobertura de canaries.

**Artefacto a guardar**
- `docs/security/INJECTION_CANARY_MATRIX.md`: vectores por formato, resultado esperado, estado de cobertura.
- Implementación en `app/src/parsers/`.
- Tests `app/tests/test_injection_canaries_*.py`.

**Si es un test/DoD**
- DoD SL2/SL3/SL5: “Ningún formato de KB o correo ejecuta código ni inyecta prompts”.
- Tests con payloads de prueba para cada formato.

### 5d. Cifrado local (SQLCipher/passphrase)

**Diagnóstico fugu**
SpaceLoom es local-first: SQLite reside en el filesystem del usuario. Sin cifrado, cualquier acceso al disco expone datos de clientes. Crítico al ingestar datos MWT reales.

**Acción concreta para destrabarlo**
- CEO decide: ¿cifrado siempre o solo workspaces confidenciales?
- Si **siempre**: migrar a SQLCipher o cifrado transparente con passphrase.
- Si **condicional**: añadir flag `workspace.is_confidential` y cifrar solo esos.
- La clave debe derivarse con PBKDF2/Argon2 y guardarse en el keyring del SO, nunca en el repo ni en logs.

**Responsable sugerido**
- **Alvaro (CEO)** para decisión de política.
- **dev** para implementación.
- **fugu** para auditar key management.

**Artefacto a guardar**
- `docs/security/LOCAL_ENCRYPTION_SPEC.md`: decisión, algoritmo, key management, migración.
- Implementación en `app/src/db/encryption.py`.
- Tests `app/tests/test_local_encryption.py`.

**Si es un test/DoD**
- DoD SL2a/SL3.5: “Datos de workspace confidencial cifrados en reposo”.
- Tests de apertura de DB con/sin passphrase; clave no en texto plano.

### 5e. Backup/export/restore smoke test antes de datos reales

**Diagnóstico fugu**
Antes de cargar datos reales de MWT debe existir mecanismo probado de recuperación. Sin él, una corrupción o pérdida del SQLite elimina trabajo valioso.

**Acción concreta para destrabarlo**
- Implementar export de SQLite a archivo comprimido/cifrado y restauración.
- Smoke test end-to-end: seed workspace → exportar → borrar DB → restaurar → verificar datos y audit trail.

**Responsable sugerido**
- **dev** para implementar y testear.
- **fugu** para auditar.

**Artefacto a guardar**
- `docs/ops/BACKUP_RESTORE_RUNBOOK.md`: pasos manuales y automáticos.
- Script `app/tools/backup_restore.py`.
- Test `app/tests/test_backup_restore_smoke.py`.

**Si es un test/DoD**
- DoD previo a ingestión de datos reales: “Smoke test de backup/restore pasa”.
- Test automatizado en CI.

### 5f. Auto-update firmado + rollback

**Diagnóstico fugu**
SL4 requiere auto-update. Sin firma, cualquier actor que comprometa el feed de updates puede instalar código malicioso. Sin rollback, un update defectuoso deja al usuario sin producto.

**Acción concreta para destrabarlo**
- Implementar feed de updates firmado (Ed25519 o RSA).
- Cliente verifica firma antes de instalar.
- Guardar versión anterior para rollback manual.
- Instalación solo cuando no haya mutaciones/drafts pendientes.

**Responsable sugerido**
- **dev** para implementar cliente y verificación.
- **ops** para infraestructura de feed y certificados.
- **fugu** para auditar.

**Artefacto a guardar**
- `docs/security/AUTO_UPDATE_SPEC.md`: esquema de firma, verificación, rollback, condiciones de instalación.
- Implementación en `app/src/update/`.
- Tests `app/tests/test_auto_update.py`.

**Si es un test/DoD**
- DoD SL4: “Update rechaza paquetes sin firma válida; soporta rollback; no reinicia con tareas pendientes”.
- Tests de rechazo de firma inválida, rollback, bloqueo con pending mutations.

---

# Resumen ejecutivo — Orden de desbloqueo

## Secuencia recomendada

1. **Decisiones CEO (Bloqueante #3)**  
   Llave maestra. Sin decisión sobre scope, calendario, dedicación, cifrado, SL5 y adopción, el resto se mueve en la neblina.

2. **Auditoría fugu de SL1b (Bloqueante #1)**  
   Una vez decidido el scope, auditar el código entregado contra el DoD real de SL1b.

3. **Datos MWT reales + backup/restore smoke test (Bloqueantes #2 y #5e)**  
   El pack autorizado y el smoke test habilitan el dogfood real. SL1b no se aprueba sin esto.

## Paralelos que pueden correr en cuanto se desbloquee el scope

- **DoD de seguridad/datos (#5a–#5d, #5f)** pueden avanzar en paralelo.
  - `source_to_field_check` y `stale_data_block` son **prerrequisitos para ingestión de datos reales**.
  - `injection canaries` y `local encryption` pueden correr en paralelo; el cifrado depende de la decisión CEO.
  - `auto-update firmado + rollback` depende del presupuesto de firma de código (#4b), pero su diseño puede empezar antes.

- **Dependencias externas (#4a–#4b)** pueden gestionarse en paralelo.
  - Credenciales IMAP solo relevantes si SL5 entra; si se difiere, se congela.
  - Presupuesto de firma de código debe aprobarse cuanto antes para no retrasar SL4.

## Líneas rojas

- **No abrir SL2a** hasta tener:
  - Decisiones CEO aprobadas y documentadas.
  - PASS de auditoría SL1b.
  - Pack MWT real ingestado.
  - `source_to_field_check` completo.
  - `stale_data_block` robusto.
  - Backup/restore smoke test pasado.

- **No abrir SL5** sin credenciales IMAP autorizadas y seguras.

- **No abrir SL4** sin presupuesto aprobado y certificados de firma de código.

**Dictamen fugu:** SL1b está técnicamente entregado pero **operativamente bloqueado**. La prioridad absoluta es obtener las decisiones del CEO y el pack MWT real; con eso, el resto de los bloqueantes se pueden atacar en paralelo con un plan claro.
