---
id: POL_ARCHIVO
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
tipo: POL
stamp: VIGENTE — 2026-06-15
aplica_a: [SHARED]
---

# POL_ARCHIVO — Política de retención y archivo

Define cuándo, cómo y por qué un documento vivo del KB pasa al archivo, cómo se recupera, y quién custodia el índice.

## Trigger de archivo (razones canónicas A1–A5)

| Código | Razón | Ejemplo típico |
|--------|-------|----------------|
| A1 | Reemplazado por versión posterior | `SPEC_FB_BUILD_SEQUENCE_v2.1` → `SPEC_FB_BUILD_SEQUENCE_v3.0` |
| A2 | Contenido obsoleto o no aplica tras cambio de contexto | RFC descartado, dependencia retirada |
| A3 | Duplicado o consolidado en otro documento | Dos entradas fusionadas en un solo `ENT_` |
| A4 | Migrado a otro sistema / repositorio | Snapshot legal movido a Paperless-ngx / Google Drive |
| A5 | Cumple trigger de snapshot inmutable | Arte aprobado, listing publicado, claim aprobado, contrato firmado, cambio regulatorio |

## Formato del registro de archivo

Cada documento archivado se registra en `docs/archivo/ARCHIVE_INDEX.md` con los campos:

- `id`: identificador canónico del documento original.
- `reason`: código A1–A5.
- `date`: fecha de archivo (ISO 8601).
- `old_path`: ubicación original.
- `new_path`: ubicación dentro de `docs/archivo/` o sistema externo.
- `replaced_by`: id del documento que lo reemplaza, si aplica.
- `recoverable`: `yes` si el contenido sigue accesible en el repo; `external` si vive fuera.

## Destino

- Contenido KB obsoleto pero referenciable: `docs/archivo/` dentro del repo canonico.
- Artefactos firmados / snapshots regulatorios: futuro Paperless-ngx; actual Google Drive.
- El KB nunca guarda snapshots editables. Solo datos vivos. El pasado vive en el archivo.

## Proceso

1. El agente detecta que un documento debe archivarse (trigger A1–A5).
2. Mueve o renombra el archivo a `docs/archivo/` con sufijo descriptivo (`_A1_SUPERSEDED`, `_A5_SNAPSHOT`, etc.).
3. Actualiza su frontmatter: `status: ARCHIVADO`, `stamp: ARCHIVADO — <fecha> — reason <codigo>`.
4. Añade o actualiza la entrada en `docs/archivo/ARCHIVE_INDEX.md`.
5. Actualiza todas las referencias entrantes para que apunten al reemplazo, o las marca como históricas.
6. No elimina el archivo del repo a menos que `POL_EPHEMERAL_OUTPUT` lo exija.

## Agente archivista

Función aún no implementada como servicio. Hasta entonces, el curador KB ejecuta este proceso y lo documenta en `ARCHIVE_INDEX.md`.

## Enforcement

- **Detección:** auditoría de routing (`audit/audit_routing.py`) reporta duplicados y documentos obsoletos.
- **Acción:** archivar + indexar.
- **Severidad:** SOFT — reportar en próxima revisión si no es crítico.

---

Changelog:
- v1.1 (2026-06-15): Reescritura como política de retención activa. Define razones A1–A5, `ARCHIVE_INDEX.md`, proceso de archivo y recuperación. Aplica a SHARED. (AUDIT-ROUTING-2026-06-14)
- v1.0 (2026-03-01): Versión original orientada a snapshots de producción. Pendiente de Paperless-ngx.

---

Stamp: VIGENTE — 2026-06-15
Vencimiento: 2026-09-15
Estado: VIGENTE
Aprobador final: CEO
