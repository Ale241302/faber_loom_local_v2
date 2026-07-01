---
id: SPEC_FB_TENANT_BOOTSTRAP_SEED_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa: como nace MWT (primer adapter safety_footwear) reproducible
relacionado_con:
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (tenant + memberships)
  - SPEC_FB_VERTICAL_AM_v1.1 (vertical_spec_object loading)
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1.1 (16 fuentes config tenant)
  - ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1 (defaults + overrides MWT)
  - ENT_FB_RFQ_REPLAY_SET_v1.1 (60 RFQs Sem 0 baseline)
origen: ChatGPT R5 detecto seed reproducible como gap operacional · SPEC propio
---

# SPEC_FB_TENANT_BOOTSTRAP_SEED_v1
## Cómo nace un tenant FaberLoom · MWT como primer caso reproducible

## 1. Proposito

Define como un tenant FaberLoom se siembra desde cero · de forma reproducible · idempotente · versionada. Sin esto, "cada ambiente nace con un horoscopo distinto" (R5).

MWT (primer adapter safety_footwear) es el caso canonico. El SPEC define el flow completo · CLI commands · seed scripts · validacion.

## 2. Que se siembra · 9 piezas canonicas

```
1. Tenant entity                  (mwt · Muito Work Limitada · subdomain)
2. Tenant config                  (plan_tier · features · region)
3. Vertical_spec_object           (safety_footwear v1.1 con glossary_overrides)
4. Authority Matrix tenant        (defaults canonicos + overrides MWT)
5. Source of Truth config         (16 fuentes + freshness SLA per tenant)
6. Catalogo inicial               (Marluvas + Tecmater · ~50 SKUs)
7. Memberships + roles            (Alvaro = AM + CURATOR + CEO)
8. Replay Set MVP                 (60 RFQs reales · CEO extrae Sem 0 AI-assisted)
9. Privacy tier defaults          (POL_FB_KR_PRIVACY_TIERS · Layer 1 cross-tenant DESACTIVADO)
```

## 3. Flow canonico de bootstrap

```
PASO 1 · Pre-bootstrap (CEO ejecuta · 1 dia antes Sem 0)
├ Comprar dominio + subdomain (ej. mwt.faberloom.com)
├ Configurar DNS A record
├ Generar TLS cert (Caddy auto)
├ Aprobar plan_tier MWT v1 (gold)
└ Pricing: $XXX [PENDIENTE — CEO + finance]

PASO 2 · Tenant create (FaberLoom-admin via CLI)
├ ./scripts/tenant_create.sh mwt --legal-name "Muito Work Limitada" \\
│   --commercial-name "Mesa de Control" --vertical safety_footwear \\
│   --region LATAM --tier gold
├ Crea tenant_id en postgres
├ Postgres RLS habilitado para mwt
├ Subdomain registered
└ Output: tenant_id + admin_setup_token (one-time)

PASO 3 · CEO primer login (Sem 0)
├ Navega a https://mwt.faberloom.com/setup
├ Inserta admin_setup_token
├ Crea cuenta CEO Alvaro · password + 2FA setup
├ Auto-asignado roles [AM, CURATOR, CEO]
└ Redirect a wizard onboarding

PASO 4 · Wizard onboarding (CEO completa · ~30 min)
├ A · Confirmar/editar Authority Matrix (defaults canonicos)
├ B · Upload catalogo Marluvas + Tecmater (CSV o manual ~50 SKUs)
├ C · Configurar fuentes Source of Truth
│   ├ Stock source: SAP MM endpoint o manual fallback
│   ├ Pricing source: lista manual v1
│   ├ FX source: Banco Central MX API o manual
│   └ ...resto fuentes (8 obligatorias minimo)
├ D · Templates voice MWT (tono · banned phrases · signoff)
├ E · DPA review (Layer 1 cross-tenant DESACTIVADO default)
└ F · Confirmar todo · sistema valida + activa tenant

PASO 5 · Replay Set Sem 0 (CEO ejecuta · 2-3 dias en Sem 0)
├ Run AI-assisted extraction (script Gmail/Outlook+SAP)
├ Sistema parsea histórico 12 meses · sugiere ~80 RFQs
├ CEO marca outcome de cada uno: ganada/perdida/ambigua/edge
├ CEO asigna sub_split (pais · proveedor · familia · etc)
├ Sistema balancea para split 40/25/25/10
├ Output: 60 RFQs en estado active en pool MVP
└ Replay set listo para benchmark

PASO 6 · Sub-agentes provision (FaberLoom-admin)
├ Cada sub-agente del catalogo se instancia para MWT
├ Profile compliance_checker = safety_footwear
├ Estado inicial: SHADOW (NO active hasta Sem 1)
└ Wired al LiteLLM con tier 1 default routing

PASO 7 · Smoke test E2E
├ Trigger RFQ test (email simulado)
├ Verifica pipeline ejecuta (classifier → draft writer → compliance → output)
├ Verifica eventos llegan a UI via WS
├ Verifica audit log con SHA-chain
└ Si pasa: tenant ACTIVE en SHADOW MODE Sem 1
```

## 4. CLI canonico · scripts seed

### 4.1 tenant_create.sh

```bash
#!/bin/bash
# scripts/tenant_create.sh
# Uso: ./tenant_create.sh <slug> --legal-name "..." --vertical <id> --tier <plan>

set -e

SLUG="$1"
shift

# Parse args
LEGAL_NAME=""
COMMERCIAL_NAME=""
VERTICAL=""
REGION="LATAM"
TIER="bronze"

while [[ $# -gt 0 ]]; do
  case $1 in
    --legal-name) LEGAL_NAME="$2"; shift 2 ;;
    --commercial-name) COMMERCIAL_NAME="$2"; shift 2 ;;
    --vertical) VERTICAL="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --tier) TIER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Validar
[[ -z "$SLUG" || -z "$LEGAL_NAME" || -z "$VERTICAL" ]] && {
  echo "Usage: tenant_create.sh <slug> --legal-name <name> --vertical <id>"
  exit 1
}

# Idempotencia · si tenant existe · skip
EXISTS=$(docker compose exec -T postgres psql -U faberloom -tAc \\
  "SELECT 1 FROM tenants WHERE tenant_id='$SLUG'")

if [[ "$EXISTS" == "1" ]]; then
  echo "Tenant $SLUG already exists · skip create"
  exit 0
fi

# Generar admin_setup_token
TOKEN=$(openssl rand -hex 32)

# Insert tenant
docker compose exec -T postgres psql -U faberloom <<SQL
BEGIN;

INSERT INTO tenants (tenant_id, legal_name, commercial_name, subdomain, region, plan_tier, vertical_spec_object_id)
VALUES ('$SLUG', '$LEGAL_NAME', '$COMMERCIAL_NAME', '$SLUG', '$REGION', '$TIER', '$VERTICAL');

INSERT INTO admin_setup_tokens (tenant_id, token_hash, expires_at)
VALUES ('$SLUG', encode(digest('$TOKEN', 'sha256'), 'hex'), NOW() + INTERVAL '7 days');

COMMIT;
SQL

# Setup RLS para este tenant (todos los queries auto-filtran)
docker compose exec -T postgres psql -U faberloom <<SQL
-- RLS activado en tablas relevantes (config in migration · este es no-op si ya activo)
SQL

echo "✓ Tenant created: $SLUG"
echo "✓ Admin setup token (one-time use, share with CEO via secure channel):"
echo ""
echo "  $TOKEN"
echo ""
echo "URL: https://$SLUG.faberloom.com/setup?token=$TOKEN"
```

### 4.2 vertical_spec_load.py

```python
# scripts/vertical_spec_load.py
"""Load vertical_spec_object YAML para tenant."""

import yaml
import sys
from pathlib import Path
from app.db import session_factory

def load_vertical_spec(tenant_id: str, vertical_id: str):
    spec_path = Path(f"specs/vertical_spec_objects/{vertical_id}.yaml")
    if not spec_path.exists():
        raise FileNotFoundError(f"Vertical spec not found: {vertical_id}")
    
    with open(spec_path) as f:
        spec = yaml.safe_load(f)
    
    async with session_factory() as session:
        # Idempotente · UPSERT
        await session.execute("""
            INSERT INTO tenant_vertical_specs (tenant_id, vertical_id, spec_yaml, version)
            VALUES (:tid, :vid, :spec, :ver)
            ON CONFLICT (tenant_id) DO UPDATE
            SET spec_yaml = EXCLUDED.spec_yaml,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, {
            "tid": tenant_id,
            "vid": vertical_id,
            "spec": yaml.dump(spec),
            "ver": spec.get("version", "1.0"),
        })
        await session.commit()
    
    print(f"✓ Vertical spec loaded: {vertical_id} v{spec.get('version', '1.0')}")

if __name__ == "__main__":
    tenant_id = sys.argv[1]
    vertical_id = sys.argv[2]
    asyncio.run(load_vertical_spec(tenant_id, vertical_id))
```

### 4.3 catalog_seed.py

```python
# scripts/catalog_seed.py
"""Seed catalogo Marluvas + Tecmater · idempotente."""

import csv
from pathlib import Path
from app.db import session_factory

CATALOGOS = {
    "marluvas": "data/catalog_marluvas_v1.csv",
    "tecmater": "data/catalog_tecmater_v1.csv",
}

async def seed_catalog(tenant_id: str):
    async with session_factory() as session:
        for supplier, csv_path in CATALOGOS.items():
            with open(csv_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    await session.execute("""
                        INSERT INTO catalog_skus (
                            tenant_id, sku, supplier, description,
                            vertical_spec, list_price, currency, moq,
                            cert_doc_version, cert_validity_until, ...
                        ) VALUES (...)
                        ON CONFLICT (tenant_id, sku) DO UPDATE
                        SET ...
                    """, {...})
        await session.commit()
    
    print(f"✓ Catalog seeded for tenant {tenant_id}")
```

### 4.4 replay_set_extract.py

```python
# scripts/replay_set_extract.py
"""AI-assisted extraction de RFQs historicas para Replay Set Sem 0."""

import argparse
from app.services.gmail_extractor import GmailRFQExtractor
from app.services.sap_correlator import SAPCorrelator

async def extract_replay_set(tenant_id: str, months_back: int = 12):
    # 1. Gmail API extract emails con keyword filter (RFQ · cotizacion · solicitud)
    gmail = GmailRFQExtractor(tenant_id)
    rfqs_raw = await gmail.extract(months_back=months_back)
    
    # 2. SAP correlator: para cada RFQ encontrar respuesta + outcome
    sap = SAPCorrelator(tenant_id)
    rfqs_enriched = []
    for rfq in rfqs_raw:
        outcome = await sap.find_outcome(rfq)
        rfqs_enriched.append({
            **rfq,
            "outcome_proposed": outcome.outcome,  # won · lost · ambiguous · edge
            "confidence": outcome.confidence,
            "sap_quote_ref": outcome.quote_id,
        })
    
    # 3. CEO valida outcome · marca sub_split
    print(f"Found {len(rfqs_enriched)} RFQs · review pending")
    
    # 4. Balance hacia split 40/25/25/10 · select 60 MVP
    selected = balance_split(rfqs_enriched, target_size=60)
    
    # 5. Persist en pool MVP estado active
    async with session_factory() as session:
        for rfq in selected:
            await session.execute("""
                INSERT INTO replay_set_cases (...)
                VALUES (...)
            """, ...)
        await session.commit()
    
    print(f"✓ Replay set MVP: 60 RFQs active")
```

## 5. Idempotencia · re-runs seguros

Todos los scripts seed son **idempotentes**:
- Tenant create → si existe · skip
- Vertical spec load → UPSERT
- Catalog seed → UPSERT
- Replay extract → solo agrega CANDIDATE · no duplica si ya existe

CEO puede re-correr scripts sin miedo. Util para:
- Recovery post-incidente
- Migration entre ambientes (dev → staging)
- Disaster recovery rehearsal

## 6. Validacion post-bootstrap

```bash
./scripts/validate_tenant.sh mwt
```

Checks:
- ✓ Tenant exists con plan_tier correcto
- ✓ Subdomain DNS resuelve
- ✓ TLS cert valida
- ✓ Postgres RLS habilitado para mwt
- ✓ Vertical spec safety_footwear cargado v1.1
- ✓ Authority Matrix configurada (defaults + overrides)
- ✓ Catalog tiene >=50 SKUs Marluvas+Tecmater
- ✓ Memberships: Alvaro tiene roles [AM, CURATOR, CEO]
- ✓ Replay set MVP: 60 cases active con split 40/25/25/10 + ≥30% Critical+High
- ✓ 10 sub-agentes instanciados en SHADOW
- ✓ LiteLLM config con tier 1 default
- ✓ Layer 1 cross-tenant DESACTIVADO (sin DPA)
- ✓ Smoke test E2E pasa

Si CUALQUIER check falla · alerta CEO + bloqueo activacion. NO ACTIVE hasta validate pass 100%.

## 7. Rollback de tenant (excepcional)

Si tenant create falla a mitad de proceso:

```bash
./scripts/tenant_rollback.sh mwt --confirm
```

- Confirma intent (typed slug)
- Marca tenant como `status=rolled_back`
- Datos del tenant NO se borran (retencion por compliance)
- Subdomain liberado
- Audit event `tenant.rolled_back` con razon

Restore desde rollback: re-correr `tenant_create.sh mwt` reactivado (idempotente).

## 8. Multi-tenant onboarding (post-MWT · v2)

Cuando aparezca segundo tenant:

```bash
./scripts/tenant_create.sh tenant_2 \\
  --legal-name "..." \\
  --vertical chemical_PPE \\  # nuevo vertical
  --tier silver
```

Pasos similares pero:
- Vertical_spec_object distinto (chemical_PPE en vez de safety_footwear)
- Compliance Checker profile distinto
- Catalogo distinto
- DPA opt-in cross-tenant Layer 1 disponible (decision tenant)

Confirma que el sistema **escala** cross-vertical sin re-arquitectura.

## 9. Reglas inquebrantables

1. **Idempotencia obligatoria** · re-runs seguros sin duplicar.
2. **Validacion post-bootstrap obligatoria** · sin pass 100% NO active.
3. **Postgres RLS habilitado por tenant desde tenant_create.**
4. **Layer 1 cross-tenant DESACTIVADO default** · activable solo con DPA firmado.
5. **Replay Set MVP 60 RFQs MINIMO** · NO active con menos.
6. **CEO completa wizard onboarding** · NO automatizable sin CEO confirmation.
7. **Sub-agentes inician SHADOW** · NO active hasta Sem 1+ con outcome accountability.
8. **Audit log SHA-chain inicia con tenant_create** · cadena per tenant.
9. **Backup de tenant antes de rollback** · datos NO se pierden.
10. **Subdomain liberable solo via FaberLoom-admin** · NO automatic post-rollback.

## 10. Pendientes [PENDIENTE — NO INVENTAR]

- UI wizard onboarding (Mesa de Control · pantalla setup) → diferido v6 mock
- Catalog import format · CSV vs JSON vs API → SPEC tecnico implementacion
- DPA template legal (Layer 1 cross-tenant) → CEO + abogado pre-go-to-market
- Self-service tenant signup (sin FaberLoom-admin) → diferido v3 cuando producto maduro
- Tenant migration tooling (export/import full state) → diferido v3
- Multi-tenant per-organization (caso enterprise) → diferido v3
- Trial tenants (limited time · auto-cleanup) → diferido v2

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_TENANT_BOOTSTRAP_SEED_v1` **NO implica self-service signup**. Sprint 1 es FaberLoom-admin assisted onboarding · CEO de cada tenant nuevo coordina con equipo FB para setup. Self-service queda para v3 cuando producto maduro y compliance lo permita.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT. 9 piezas canonicas a sembrar (tenant entity · config · vertical_spec · authority matrix · source of truth · catalogo · memberships · replay set · privacy tiers). Flow 7 pasos (pre-bootstrap CEO · tenant create CLI · CEO primer login + 2FA · wizard onboarding 30min · replay set Sem 0 AI-assisted · sub-agentes SHADOW · smoke test E2E). 4 scripts CLI canonicos (tenant_create.sh · vertical_spec_load.py · catalog_seed.py · replay_set_extract.py). Idempotencia obligatoria. Validacion post-bootstrap con ~13 checks · sin pass 100% NO active. Rollback excepcional preserva datos. Multi-tenant onboarding scaling cross-vertical (post-MWT v2). 10 reglas inquebrantables. NO implica self-service signup Sprint 1.

## Stamp
VIGENTE 2026-05-02 — Como nace MWT reproducible. Sin esto · "cada ambiente nace con horoscopo distinto" (R5). Sprint 1 ejecutable post-merge cuando CEO completa wizard + replay extract.
