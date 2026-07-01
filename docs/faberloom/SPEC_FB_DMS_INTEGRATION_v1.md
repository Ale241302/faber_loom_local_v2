---
id: SPEC_FB_DMS_INTEGRATION_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-05-02 — adapter pattern · NO implementacion Sprint 1
fecha: 2026-05-02
agente: Cowork (redaccion) + ChatGPT (auditoria R8 · 14 cambios sustantivos aplicados)
aplica_a: [FaberLoom]
status_motivo: |
  ChatGPT R8 valido SPEC con 14 cambios sustantivos · todos aplicados aqui.
  DRAFT · NO VIGENTE · NO implementacion sin tenant firmado.
  Adapters specific implementados solo cuando 5 condiciones-trigger se cumplen.
relacionado_con:
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (permission respect · doble auth)
  - SPEC_FB_INTEGRATION_LAYER_v1 (endpoints DMS via API canonica)
  - SPEC_FB_EVENTING_AND_OUTBOX_v1 (8 eventos DMS canonicos)
  - SPEC_FB_SYSTEM_TOPOLOGY_v1 (MinIO container como cache bridge)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.1 (MWT NO requiere DMS Sprint 1)
  - ENT_FB_VERTICAL_CANDIDATES_v1 (DMS mapping per vertical)
  - POL_FB_KR_PRIVACY_TIERS_v1.1 (compliance metadata propagation)
origen: pregunta CEO sobre integracion DMS comunes (DocuClass · DocuWare · Alfresco · etc) · validado ChatGPT R8
---

# SPEC_FB_DMS_INTEGRATION_v1
## Adapter pattern · integracion FaberLoom <-> DMS externos

## 1. Frase canonica del modelo (R8)

> **FaberLoom puede leer, proponer y escribir sobre documentos externos, pero el DMS conserva autoridad documental. FaberLoom hereda permisos, conserva provenance, cachea con limites y NUNCA convierte integracion en bypass de gobierno documental.**

## 2. Proposito

Define adapter pattern abstracto para integracion FaberLoom con gestores documentales externos (DMS · EHR · GRC · repos · etc). Cada DMS specific se implementa cuando primer tenant lo requiera (5 condiciones-trigger seccion 14).

R8 critico: **DMS NO es propiedad del vertical · es capa horizontal**. Por eso SPEC dedicado · NO extension de vertical_spec_object.

> "MinIO cache NO es sistema de verdad documental. El DMS externo sigue siendo source of record salvo documento generado nativamente por FaberLoom." (R8)

## 3. Status

**DRAFT** · NO VIGENTE · NO implementacion sin tenant firmado.

| Layer | Status |
|---|---|
| Abstract DMS Adapter Interface | DRAFT (canonizado aqui) |
| Capabilities matrix | DRAFT (canonizado aqui) |
| 3 niveles integracion | DRAFT (canonizado aqui) |
| MinIO cache bridge | DRAFT (canonizado aqui) |
| Adapter specific (DocuWare · Alfresco · etc) | NO IMPLEMENTACION sin tenant firmado |
| Federated search | DIFERIDO v3 |
| Bi-directional sync | DIFERIDO v3 |

## 4. Abstract DMS Adapter Interface (R8 · 14 operaciones)

```python
class DMS_AbstractAdapter:
    """Cada DMS specific implementa esta interfaz. Capabilities declaran que soporta."""
    
    # Lectura
    def list(folder_path: str?, query: str?) -> List[DocMetadata]: ...
    def read(doc_id: str) -> DocContent: ...
    def get_metadata(doc_id: str) -> DocMetadata: ...
    def get_versions(doc_id: str) -> List[VersionMetadata]: ...
    def read_version(doc_id: str, version_id: str) -> DocContent: ...
    def search(query: CanonicalQuery, filters: dict?) -> List[DocMetadata]: ...
    
    # Permisos
    def check_permission(doc_id: str, user_id: str, action: str) -> PermissionResult: ...
    
    # Escritura (Nivel 2+)
    def write(content: bytes, target_folder: str, metadata: dict, idempotency_key: str) -> WriteResult: ...
    def lock_or_checkout(doc_id: str, user_id: str) -> LockResult: ...
    def unlock_or_checkin(doc_id: str, content: bytes?) -> CheckinResult: ...
    
    # Restringido (default disabled)
    def delete_or_archive(doc_id: str, reason: str) -> DeleteResult: ...  # restricted
    
    # Sync (Nivel 3)
    def get_delta(cursor: str?) -> DeltaResult: ...
    
    # Audit
    def emit_audit_event(action: str, doc_id: str, user_id: str, trace_id: str) -> None: ...
```

## 5. Capabilities matrix (R8 · obligatorio)

Cada adapter debe declarar capabilities · NO mentir con metodos a medias:

```yaml
adapter_capabilities:
  adapter_id: string  # ej. "docuware_v1"
  adapter_version: string
  
  # Operaciones soportadas
  supports_versions: boolean
  supports_locks: boolean
  supports_check_in_out: boolean
  supports_webhooks: boolean
  supports_delta_sync: boolean
  supports_full_text_search: boolean
  supports_metadata_filter: boolean
  supports_boolean_query: boolean
  supports_folder_scope: boolean
  supports_metadata_schema: boolean
  
  # Auth
  supports_user_delegated_auth: boolean
  supports_service_account: boolean
  supports_oauth2: boolean
  supports_saml: boolean
  supports_api_key: boolean
  
  # Bulk
  supports_bulk_operations: boolean
  rate_limit_per_minute: int?
  cost_per_api_call_usd: float?  # algunos DMS cobran
  
  # Restricciones
  supports_delete: boolean  # default false
  supports_archive: boolean
  supports_legal_hold: boolean
  supports_retention_policies: boolean
```

## 6. 3 niveles de integracion (R8 validado)

```
NIVEL 1 · READ-ONLY
  operations: [list, read, get_metadata, get_versions, search, check_permission]
  complexity: low
  tenant_value: alto
  sprint_estimate: 1-2 sprints per DMS
  caso_uso: legal piloto · medico research · etc

NIVEL 2 · READ + WRITE + AUDIT
  operations: nivel 1 + [write, lock_or_checkout, unlock_or_checkin]
  complexity: medium
  tenant_value: muy_alto
  sprint_estimate: 2-3 sprints per DMS
  conflict_resolution: REQUIRED (compare-and-set por version/hash)
  caso_uso: cotizacion → DMS · evidence bundles → DMS · etc

NIVEL 3 · BI-DIRECTIONAL SYNC (R8: trigger comercial fuerte)
  operations: nivel 2 + [get_delta, webhooks bidireccional]
  complexity: high
  tenant_value: enterprise
  sprint_estimate: 3-4 sprints per DMS
  requires:
    - DMS soporta webhooks confiables
    - DMS es system of record
    - tenant tiene presupuesto implementacion
    - dueño tecnico del lado tenant
  caso_uso: enterprise multi-DMS con sync continuo
```

## 7. MinIO cache strategy (R8 critical · cache != source of record)

```yaml
cache_strategy:
  object_store: MinIO (canonizado en SPEC_FB_SYSTEM_TOPOLOGY_v1)
  
  cache_types:
    content_cache: full doc binary
    thumbnail_cache: preview/thumbnail
    extracted_text_cache: OCR/text-extraction output
    metadata_snapshot: DMS metadata at fetch time
  
  cache_key_canonical:
    - source_dms (adapter_id)
    - source_doc_id
    - source_version (NO solo doc_id · si version cambia · cache_miss)
    - content_hash (verificacion integridad)
  
  ttl_per_privacy_tier:
    PRIVATE_RAW: 0-15 minutes
    TENANT_DERIVED: 1 hour default
    GLOBAL_PROMOTABLE: 24 hours
    RESTRICTED_SENSITIVE_OR_REGULATED: 0-15 minutes (TIER 4)
    LEGAL_PRIVILEGED: 0-15 minutes
  
  invalidation_methods:
    - webhook (Nivel 3)
    - delta_sync (Nivel 3)
    - poll (Nivel 1-2)
    - manual_refresh (UI button)
    - ttl_expiry (passive)
  
  REGLA_DURA:
    "MinIO cache NO reemplaza DMS como source of record. 
     Cualquier query CRITICA debe verificar version contra DMS si TTL expirado."
```

## 8. Audit trail · provenance per documento (R8 enriquecido)

```yaml
dms_provenance:
  # Identificacion
  source_dms: string  # adapter_id
  source_uri: string  # URL completa · debugging
  source_doc_id: string
  source_version: string
  source_etag_or_hash: string  # integridad
  
  # Tiempo
  fetched_at: ISO8601
  cached_in_minio: boolean
  cache_expires_at: ISO8601?
  written_back_at: ISO8601?
  
  # Auth context
  fetched_by_user_id: string
  fetched_under_auth_context: enum  # user_delegated · service_account
  
  # Adapter
  adapter_id: string
  adapter_version: string
  
  # Permisos snapshot
  source_acl_snapshot_id: string  # snapshot ACL al momento del fetch
  
  # Procesamiento
  extraction_method: string  # OCR · text · etc
  classification_at_fetch: enum  # privacy tier
  
  # Compliance
  retention_policy_ref: string?
  legal_hold: boolean
  
  # Conflicto
  conflict_detected: boolean
  conflict_resolution: string?
  
  # Audit chain
  trace_id: string  # cadena completa
  sha_chain_prev: string
  sha_chain_curr: string
```

## 9. Eventos canonicos DMS (R8 · 8 eventos integrados con Eventing/Outbox)

Alineados con `SPEC_FB_EVENTING_AND_OUTBOX_v1` · agregar a la categoria sistema:

```
dms.document.fetched
dms.document.cached
dms.document.write_requested
dms.document.write_succeeded
dms.document.conflict_detected
dms.document.permission_denied
dms.sync.failed
dms.adapter.health_check_failed
```

Estos eventos van por outbox pattern · garantia at-least-once · audit con SHA-chain.

## 10. Versioning + locking + conflict policy (R8 critical)

```yaml
write_precondition:
  source_version_must_equal: fetched_version  # compare-and-set obligatorio
  if_mismatch:
    action: conflict_detected
    user_visible: true
    resolution: user_review_required
    options:
      - retry_with_new_version  # re-fetch · re-apply changes · re-write
      - abandon_changes
      - merge_strategy_user_choice

locking_policy:
  if_dms_supports_locks:
    auto_lock_before_write: true
    lock_timeout: 5 minutes
    auto_unlock_on_timeout: true
  if_dms_no_locks:
    use_optimistic_concurrency: true  # version-based
    detect_external_changes: true

idempotency:
  every_write_carries: x-idempotency-key (canonizado en Integration Layer)
  retries: NO duplican writes
```

**Regla dura R8:** Toda escritura debe ser compare-and-set por version/hash si el DMS lo soporta. Si NO soporta · usa optimistic concurrency con detect_external_changes.

## 11. Permission model · doble autorizacion (R8 critical)

```yaml
permission_check_dual:
  step_1_faberloom_permission:
    via: SPEC_FB_AUTH_TENANT_RBAC_v1 RBAC matrix
    if_denied: 403 unauthorized
  
  step_2_dms_permission:
    via: adapter.check_permission(doc_id, user_id, action)
    if_denied: 403 unauthorized (con razon DMS)
  
  result:
    granted: AND(faberloom_granted, dms_granted)
    audit_event: emit permission_check_result siempre
```

**Regla dura R8:** "FaberLoom NO amplia permisos del DMS. Solo puede restringir mas. NUNCA menos."

```yaml
auth_context_modes:
  user_delegated:
    description: "user_token DMS pasa con cada request"
    preferred: TRUE
    pros: "permisos reales · NO bypass"
    cons: "cada user necesita acceso DMS"
  
  service_account:
    description: "FaberLoom usa cuenta de servicio en DMS"
    preferred: FALSE (solo si DMS no permite delegated auth)
    requires:
      - require_acl_mirroring: true  # FaberLoom replica ACLs DMS
      - require_permission_probe: true  # verificar antes de cada read
      - require_audit_reason: true  # cada acceso loggea razon
    pros: "simple integration"
    cons: "service account puede leer todo · ACL mirroring obligatorio"
```

## 12. Multi-DMS per tenant (R8 · conceptual ahora · single connection v1)

```yaml
dms_connections_per_tenant:
  # Conceptual canonizado · implementation v1 single connection
  
  tenant_id: string
  
  connections:
    - connection_id: string  # ej. "ndocs_main"
      adapter: string  # ej. "netdocuments"
      role: enum  # source_of_record · collaboration · communications_record · evidence
      scopes: array<string>  # ej. ["legal_matter_documents"]
      priority: int  # 1 = primary
      enabled: boolean
      auth_method: enum
      capabilities_inherited: from adapter
  
  source_precedence_per_doc_type:
    # Reglas de prelacion por tipo de documento
    signed_contract: ["iManage", "SharePoint", "Email"]
    working_draft: ["SharePoint", "iManage"]
    client_correspondence: ["EmailArchive", "SharePoint"]
    compliance_evidence: ["GRC", "SharePoint"]

implementation_levels:
  v1: single_primary_DMS_per_tenant
  v2: multi_DMS_with_priority_order
  v3: federated_search (DIFERIDO)
```

## 13. Search capability degradation (R8 · honestidad)

```yaml
search_degradation_policy:
  if_dms_no_full_text:
    fallback: metadata-only search
    user_warning: "Este DMS no soporta busqueda full-text · resultados pueden ser parciales"
  
  if_dms_no_metadata_filter_X:
    fallback: client-side post-filter (limitado)
    user_warning: "Filtro X no soportado por este DMS"
  
  if_dms_no_boolean_query:
    fallback: simple AND-only queries
    user_warning: "Solo soporta busquedas simples"
  
  if_complex_semantic_search_required:
    fallback: FaberLoom vector search sobre cached content
    user_warning: "Busqueda semantica requiere documentos previamente cacheados"

REGLA: NUNCA prometer busqueda homogenea cross-DMS. Reportar degradation explicit al usuario.
```

## 14. Bulk policy · rate limits · cost (R8)

```yaml
bulk_operations_policy:
  max_docs_per_job: 10000  # configurable per tenant tier
  max_bytes_per_job: 100_GB
  rate_limit_per_adapter: per adapter capabilities
  backoff_strategy: exponential (max 60s)
  checkpoint_cursor: required (jobs resumibles)
  resumable_job: true
  cost_estimate_before_run: required
  
  user_consent_required:
    - if_estimated_cost > $50_USD: explicit_user_approval
    - if_estimated_duration > 1h: explicit_user_approval
  
  job_lifecycle:
    states: [queued, estimating_cost, awaiting_approval, running, paused, completed, failed]
    progress_tracking: real-time via WS
    cancel_anytime: true
```

**Regla R8:** "Bulk indexing requiere job explicito · presupuesto y progress tracking. NO se dispara 'porque el usuario abrio una carpeta'."

## 15. Compliance metadata propagation (R8 critical)

DMS classification se PROPAGA a TODA la cadena downstream:

```
DMS classification (privileged · PHI · restricted · etc)
  ↓
MinIO cache (mismo classification)
  ↓
Vector index (mismo classification · NO contamination cross-tier)
  ↓
Prompt context (LLM ve solo lo que clasificacion permite)
  ↓
Evidence bundle (classification visible al AM)
  ↓
Audit log (classification preservada)
  ↓
Learning pipeline (classification respetada · NO promote sin reclasificacion)
  ↓
Committee review (classification gate antes de promote)
```

R8: "Si no · DMS tiene cumplimiento y FaberLoom lo evapora en nombre de la productividad. Muy Silicon Valley · muy mala idea."

## 16. Fallback DMS down (R8 detallado per operacion)

```yaml
fallback_policy_per_operation:
  
  read:
    allow_cache_if:
      ttl_valid: true
      privacy_tier_allows_cache: true
      source_version_known: true
    block_if:
      restricted_requires_live_check: true
      legal_hold_unknown: true
      acl_stale: true
  
  write:
    default: outbox_retry
    user_visible_status: queued_not_written
    NEVER_CLAIM_WRITTEN_UNTIL_CONFIRMED: true  # regla dura
  
  search:
    fallback_to_cached_index: tenant_configurable
    warning_required: "DMS no disponible · resultados desde cache local"
  
  alert_thresholds:
    DMS_down_5min: warn
    DMS_down_30min: critical_alert (CEO + AM)
    DMS_down_2h: tenant_status_degraded
```

## 17. Trigger para implementar specific DMS adapter (R8)

5 condiciones obligatorias antes de implementar adapter X:

1. **Tenant firmado o LOI serio exige ese DMS**
2. **DMS es system of record para el flujo vendido**
3. **API docs + sandbox + credenciales disponibles**
4. **Caso de uso limitado definido** (read-only / read-write / sync)
5. **ROI claro** (reduce onboarding · desbloquea venta · evita carga manual · requisito compliance)

```
Trigger valido: "Bufete X firmado requiere iManage read-only para 3 tipos documentales"
  → Implementar DMS_iManage_Adapter Nivel 1

Trigger NO valido: "Seria bueno soportar iManage porque muchos bufetes lo usan"
  → NO implementar
```

## 18. Orden recomendado de implementacion (post-trigger)

```
1. SharePoint / Google Drive / Box (APIs maduras · multi-vertical)
2. DocuWare / Alfresco / OnBase (enterprise DMS clasico)
3. NetDocuments / iManage (legal enterprise especializado)
4. SAP DMS / ServiceNow GRC / Epic/Cerner / GitHub/GitLab
   → NO tratar como DMS generico · sistemas de dominio · sub-SPEC propio
```

## 19. Reglas inquebrantables

1. **MinIO cache NO es source of record.** DMS conserva autoridad documental.
2. **Compare-and-set obligatorio en writes** si DMS soporta versions.
3. **Doble autorizacion** (FaberLoom permission AND DMS permission).
4. **NUNCA claim "guardado" hasta confirmacion DMS.**
5. **Compliance metadata propaga a TODA cadena downstream.**
6. **Capabilities matrix declarada per adapter** · NO mentir con metodos a medias.
7. **Bulk requires job explicit + cost estimate + user consent.**
8. **Search degradation visible al usuario** · NUNCA prometer homogeneidad.
9. **Service account requires ACL mirroring** · sino bypass peligroso.
10. **Cache key incluye version/hash** · NO solo doc_id.
11. **NO implementacion specific DMS** sin 5 condiciones-trigger cumplidas.
12. **NO Sprint 1 MWT.** MWT cotizacion v1 NO requiere DMS.

## 20. Pendientes diferidos (post-trigger)

- DMS_DocuWare_Adapter
- DMS_Alfresco_Adapter
- DMS_NetDocuments_Adapter
- DMS_iManage_Adapter
- DMS_SharePoint_Adapter
- DMS_Box_Adapter
- DMS_GoogleDrive_Adapter
- DMS_OnBase_Adapter
- DMS_DocuClass_Adapter
- SAP_DMS_Adapter (sub-SPEC propio · sistema de dominio)
- ServiceNow_GRC_Adapter (sub-SPEC propio)
- GitHub_GitLab_Adapter (sub-SPEC software_factory propio)

Diferidos tambien:
- federated search real
- bi-directional sync
- bulk indexing masivo
- DMS migration tooling (tenant cambia DMS)
- Adapter certification suite
- OCR pipeline detallado
- Legal hold automation

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_DMS_INTEGRATION_v1` **NO implica que FaberLoom reemplaza DMS**. FaberLoom integra · cachea · respeta permisos · propaga classification · pero el DMS conserva autoridad documental. Si tenant decide migrar de DMS · FaberLoom debe poder cambiar adapter sin perder data (que vive en DMS).

**NO implica adapters specific en Sprint 1.** MWT cotizacion v1 funciona sin DMS. Adapters specific cuando primer tenant lo exija (5 condiciones-trigger).

## Changelog
- 2026-05-02 v1.0 DRAFT: Creacion inicial post auditoria R8 ChatGPT (14 cambios sustantivos aplicados). Frase canonica del modelo. Abstract DMS Adapter Interface con 14 operaciones. Capabilities matrix obligatoria per adapter. 3 niveles integracion (read-only / read-write-audit / bi-sync). MinIO cache strategy con regla dura "NO source of record". Audit trail enriquecido con 12 campos provenance. 8 eventos canonicos DMS integrados con Eventing/Outbox. Versioning + locking + conflict policy con compare-and-set obligatorio. Doble autorizacion FaberLoom AND DMS. Multi-DMS conceptual con source_precedence per doc_type · single connection v1. Search capability degradation honesto. Bulk policy con cost estimate + user consent. Compliance metadata propagation transversal. Fallback DMS down detallado per operacion. 5 condiciones-trigger para implementar adapter. Orden recomendado implementation (SharePoint/GDrive/Box → DocuWare/Alfresco/OnBase → NetDocuments/iManage → sistemas de dominio). 12 reglas inquebrantables. NO implica reemplazar DMS · NO implica Sprint 1 MWT.

## Stamp
DRAFT 2026-05-02 — Adapter pattern canonizado · NO implementacion sin tenant. R8 valido SPEC con 14 cambios sustantivos · todos aplicados. MinIO cache nunca reemplaza DMS · doble autorizacion obligatoria · compliance metadata propagation transversal. Sprint 1 MWT intacto.
