---
id: SPEC_FB_CONTRACT_TEST_HARNESS_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa: validacion ejecutable de SPEC_FB_INTEGRATION_LAYER_v1 + 30 fixtures Ciclope
relacionado_con:
  - SPEC_FB_INTEGRATION_LAYER_v1 (contratos REST + WS validados aqui)
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (RBAC matrix testeada)
  - SPEC_FB_FRONTEND_REALTIME_STATE_v1 (UI flows testeados)
  - docs/anexos/ciclope_fixtures/ (30 fixtures · 702 assertions · suite regresion)
origen: ChatGPT R5 detecto que sin harness "podes tener 702 assertions y aun asi romper frontend/backend si no prueban el contrato real"
---

# SPEC_FB_CONTRACT_TEST_HARNESS_v1
## Harness ejecutable contracts · OpenAPI + fixtures Ciclope + UI flows

## 1. Proposito

R5 critico: sin contract testing real entre backend, UI y fixtures Ciclope · "los 702 assertions viven en otro planeta". El harness conecta:
- OpenAPI spec del backend (Pydantic source)
- 30 fixtures YAML Ciclope (suite regresion)
- UI flows E2E (Mesa de Control)

Y valida que un cambio en cualquiera de los 3 NO rompe los otros 2.

Es **gate tecnico antes de Sprint 1** y **regression suite obligatoria pre-deploy**.

## 2. Stack canonico

```
Backend contract validation:  schemathesis (OpenAPI fuzzer + property-based)
Backend integration tests:    pytest + httpx async
Frontend E2E:                 Playwright + axe-core (a11y)
Fixtures runner:              pytest harness custom (lee Ciclope YAML)
Mock LLM:                     LiteLLM mock provider · responses deterministicas
CI/CD:                        GitHub Actions
```

## 3. Las 3 capas del harness

```
CAPA 1 · OpenAPI conformance (schemathesis)
   ├ Valida que cada endpoint cumple su Pydantic schema
   ├ Property-based testing · genera inputs aleatorios validos
   ├ Detecta: schemas desincronizados · validation gaps · 500s
   └ Run: en cada PR backend

CAPA 2 · Fixtures Ciclope (pytest custom)
   ├ Lee 30 fixtures YAML (case_01..20 + case_sf_01..10)
   ├ Por cada fixture:
   │   1. Setup precondiciones (catalog · customer · agent state · routing · curator)
   │   2. Trigger input (email · call · evento)
   │   3. Ejecuta pipeline esperado (sub-agents en orden)
   │   4. Valida outputs (primary_output · evidence_bundle · side_effects · exceptions)
   │   5. Verifica must_pass + must_not_do + edge_cases
   ├ 702 assertions totales
   └ Run: pre-deploy gate · pre-promote gate

CAPA 3 · UI flows E2E (Playwright)
   ├ Login flow · multi-tenant routing
   ├ Feed render + filtros + dispatch
   ├ Cards LISTO con 3 botones · modal Editar · modal Rechazar
   ├ AgentConsole slide-in · chat · iteracion
   ├ User Learning capa 1 (notificacion · aplicar · ignorar · rollback)
   ├ Light/dark toggle
   ├ ⌘K command bar
   ├ A11y checks via axe-core
   └ Run: en cada PR frontend
```

## 4. Schemathesis · OpenAPI conformance

### 4.1 Setup

```python
# tests/contract/test_openapi_conformance.py
import schemathesis
from app.main import app

schema = schemathesis.from_asgi("/api/v1/openapi.json", app)

@schema.parametrize()
def test_api_conformance(case):
    response = case.call_asgi()
    case.validate_response(response)
```

### 4.2 Que detecta

- Endpoint definido en OpenAPI pero no implementado
- Response schema mismatch (backend devuelve campo no declarado)
- Validacion missing (acepta input invalido sin 422)
- 500 con inputs validos
- Headers obligatorios x-* no enforzados

### 4.3 Output

```
Tests collected: 47 endpoints × 100 random inputs = 4700 cases
Passed: 4683
Failed: 17
  - GET /api/v1/feed · staleTime header missing
  - POST /api/v1/drafts/.../approve · returns null instead of approved_at
  - ...
```

## 5. Fixtures Ciclope harness · pytest custom

### 5.1 Fixture loader

```python
# tests/fixtures/ciclope_runner.py
import yaml
from pathlib import Path

CICLOPE_DIR = Path(__file__).parent.parent.parent / "docs/anexos/ciclope_fixtures"

def load_fixture(case_id: str) -> dict:
    """Load Ciclope fixture YAML by case_id (case_01 · case_sf_01 · etc)."""
    suite = "safety_footwear" if case_id.startswith("case_sf") else "r3_cross_industry"
    path = CICLOPE_DIR / suite / f"{case_id}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)

def all_fixtures() -> list[str]:
    """Return all 30 case_ids."""
    return sorted([
        *[f"case_{i:02d}" for i in range(1, 21)],
        *[f"case_sf_{i:02d}" for i in range(1, 11)],
    ])
```

### 5.2 Test runner por fixture

```python
@pytest.mark.parametrize("case_id", all_fixtures())
def test_ciclope_fixture(case_id, mock_llm, db_session, redis):
    fixture = load_fixture(case_id)
    
    # 1. Setup precondiciones
    setup_catalog(db_session, fixture["setup"]["catalog"])
    setup_customer(db_session, fixture["setup"]["customer"])
    setup_agent_state(redis, fixture["setup"]["agent_state"])
    setup_routing(redis, fixture["setup"]["routing"])
    
    # 2. Trigger input
    trace_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/feed/items/simulate",  # endpoint helper para tests
        json=fixture["input"],
        headers={
            "x-trace-id": trace_id,
            "x-tenant-id": "mwt",
            "x-actor-id": "test_am",
            "x-actor-role": "AM",
            "x-command-id": str(uuid.uuid4()),
            "x-idempotency-key": str(uuid.uuid4()),
        },
    )
    
    # 3. Ejecuta pipeline (mock LLM responde con outputs deterministicos)
    pipeline_result = execute_pipeline(response.json()["item_id"], mock_llm)
    
    # 4. Valida primary_output
    expected = fixture["expected_outputs"]
    assert pipeline_result["primary_output"]["type"] == expected["primary_output"]["type"]
    assert pipeline_result["primary_output"]["status"] == expected["primary_output"]["status"]
    
    # 5. Valida exceptions
    raised = set(pipeline_result["exceptions_raised"])
    expected_raised = set(expected["exceptions_raised"])
    assert raised == expected_raised, f"Exceptions mismatch · got {raised} · expected {expected_raised}"
    
    # 6. Valida hitl_gate_triggered
    assert pipeline_result["hitl_gate_triggered"] == expected["hitl_gate_triggered"]
    
    # 7. Valida evidence bundle (per-line + per-quote)
    assert_evidence_bundle_match(pipeline_result["evidence_bundle"], expected["evidence_bundle"])
    
    # 8. Valida must_pass y must_not_do
    for assertion in fixture["pass_criteria"]["must_pass"]:
        assert eval_assertion(assertion, pipeline_result), f"FAIL must_pass: {assertion}"
    for prohibition in fixture["pass_criteria"]["must_not_do"]:
        assert not eval_assertion(prohibition, pipeline_result), f"FAIL must_not_do: {prohibition}"
    
    # 9. Severity weight validation
    if "severity_weight_validation" in fixture:
        validate_severity_weight(pipeline_result, fixture["severity_weight_validation"])
    
    # 10. Privacy tier coherence
    validate_privacy_tier(pipeline_result, fixture["privacy_tier"])
```

### 5.3 Edge cases

```python
@pytest.mark.parametrize("case_id", all_fixtures())
def test_ciclope_edge_cases(case_id, mock_llm, db_session, redis):
    fixture = load_fixture(case_id)
    
    for edge in fixture.get("edge_cases", []):
        # Apply variant_data al setup
        modified_fixture = apply_variant(fixture, edge["variant_data"])
        result = execute_fixture(modified_fixture, mock_llm, db_session, redis)
        
        # Verifica expected_behavior textualmente (LLM-as-judge opcional · sino assertion explicit)
        assert_behavior_match(result, edge["expected_behavior"])
```

## 6. Mock LLM · respuestas deterministicas

LiteLLM tiene provider `mock` que retorna respuestas predefinidas:

```yaml
# tests/mocks/llm_responses.yaml
- agent: AG_SUB_EMAIL_CLASSIFIER
  case: case_01
  response:
    primary_intent: quote_request
    secondary_intents: [technical_clarification]
    urgency: high
    confidence: 0.78
    requires_human: true  # spec ambigua
    entities_extracted:
      sku_mentions: ["respiradores N95"]
      quantity_mentions: [{value: 500, unit: "unidades"}]

- agent: AG_SUB_DRAFT_WRITER
  case: case_01
  response:
    body: "Estimados, recibimos su solicitud..."
    confidence: 0.85
```

Esto hace tests deterministicos · NO depende de LLM real (caro · lento · variable).

## 7. Playwright · UI E2E

### 7.1 Tests canonicos

```typescript
// tests/e2e/login.spec.ts
test('login + multi-tenant routing', async ({ page }) => {
  await page.goto('https://mwt.faberloom.com.test');
  await page.fill('[name=email]', 'alvaro@mwt.cr');
  await page.fill('[name=password]', 'test123');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL(/mesa-de-control/);
  await expect(page.locator('header')).toContainText('Mesa de Control');
});

// tests/e2e/feed.spec.ts
test('feed renders 3 etiquetas RECIBIDO/LISTO/ALARMA', async ({ page }) => {
  await loginAsAM(page);
  await expect(page.locator('[data-tag=RECIBIDO]')).toHaveCount(>=1);
  await expect(page.locator('[data-tag=LISTO]')).toHaveCount(>=1);
  await expect(page.locator('[data-tag=ALARMA]')).toHaveCount(>=0);
});

// tests/e2e/draft_approve.spec.ts
test('draft LISTO · 3 botones fijos · aprobar funcional', async ({ page }) => {
  await loginAsAM(page);
  const draftCard = page.locator('[data-tag=LISTO]').first();
  await expect(draftCard.locator('button')).toHaveText(['Aprobar', 'Editar', '✕ Rechazar']);
  await draftCard.locator('button:has-text("Aprobar")').click();
  // El draft desaparece optimistically
  await expect(draftCard).toBeHidden();
});

// tests/e2e/agent_console.spec.ts
test('click ALARMA abre slide-in 80/20', async ({ page }) => {
  await loginAsAM(page);
  await page.locator('[data-tag=ALARMA]').first().click();
  await page.click('button:has-text("Entrar a iterar")');
  await expect(page.locator('[data-panel=agent-console]')).toBeVisible();
  await expect(page.locator('[data-panel-snapshot]')).toBeVisible();
});

// tests/e2e/user_learning.spec.ts
test('user learning capa 1 · notificacion + aplicar + rollback', async ({ page }) => {
  await loginAsAM(page);
  // Trigger pattern detection (test helper)
  await page.evaluate(() => window.__test_helpers__.triggerPattern('cotizador', 'pattern_001'));
  await expect(page.locator('text=Aprendiste')).toBeVisible();
  await page.click('button:has-text("Revisar mis aprendizajes")');
  await page.click('button:has-text("Aplicar a mi agente")');
  await expect(page.locator('text=Aplicado a tu agente')).toBeVisible();
  // Rollback
  await page.goto('/settings/learning');
  await page.click('button:has-text("Deshacer")');
});

// tests/e2e/no_committee_in_am_view.spec.ts (R5 critical)
test('AM-view NO muestra @CURADOR · k-anon · L3', async ({ page }) => {
  await loginAsAM(page);
  await expect(page.locator('text=@CURADOR')).toHaveCount(0);
  await expect(page.locator('text=k-anon')).toHaveCount(0);
  await expect(page.locator('text=L3')).toHaveCount(0);
  await expect(page.locator('text=POOL')).toHaveCount(0);
});
```

### 7.2 A11y checks

```typescript
import { injectAxe, checkA11y } from 'axe-playwright';

test('a11y · Mesa de Control', async ({ page }) => {
  await loginAsAM(page);
  await injectAxe(page);
  await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: { html: true },
  });
});
```

## 8. CI/CD pipeline (GitHub Actions)

```yaml
# .github/workflows/contract_tests.yml
name: Contract Tests
on: [push, pull_request]

jobs:
  contract:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r backend/requirements-test.txt
      - run: alembic upgrade head
      - name: OpenAPI conformance
        run: pytest tests/contract/ -v
      - name: Ciclope fixtures
        run: pytest tests/fixtures/ -v --tb=short
      - name: Generate frontend types
        run: npx openapi-typescript http://localhost:8000/api/v1/openapi.json -o frontend/src/types/api.ts
      - name: Frontend build
        run: cd frontend && npm install && npm run build
      - name: Playwright E2E
        run: cd frontend && npx playwright test
      - name: A11y checks
        run: cd frontend && npx playwright test --grep "a11y"
```

## 9. Pre-deploy gate

```
Deploy a staging   → ejecuta TODAS capas (1+2+3) · 100% pass requerido
Deploy a prod      → ejecuta TODAS capas + smoke tests + canary deployment
Promote sub-agente → ejecuta capa 2 (fixtures Ciclope con ese sub-agente activo)
```

Si capa 2 falla · deploy bloqueado · alarma a CEO + curador.

## 10. Reporting

Cada run genera:

```yaml
report:
  run_id: uuid
  trigger: pre_deploy | pre_promote | scheduled | pr
  branch: main | feature/...
  capa_1_openapi:
    total: 4700
    passed: 4683
    failed: 17
    failures: [...]
  capa_2_ciclope:
    total: 702
    passed: 702
    failed: 0
    severity_weight_sum_failures: 0
    by_severity:
      critical: 4 of 4 passed
      high: 5 of 5 passed
      medium: 11 of 11 passed
      low: 10 of 10 passed
  capa_3_e2e:
    total: 47
    passed: 46
    failed: 1
    a11y_violations: 0
  generated_at: ISO8601
```

Si severity:critical falla · alerta especial (R3 insight: critical errors no son tolerables).

## 11. Reglas inquebrantables

1. **702 assertions Ciclope DEBEN pasar pre-deploy** · sin excepcion.
2. **Mock LLM deterministico para tests** · NO LLM real (caro · variable).
3. **OpenAPI conformance en cada PR backend** · sin bloquear PRs frontend.
4. **E2E tests en cada PR frontend** · sin bloquear PRs backend.
5. **Test que valida AM-view NO muestra @CURADOR/k-anon/L3** (R5 critical · regression test).
6. **Severity:critical fail = deploy blocked** · NO override sin razon documentada.
7. **A11y violations = warning · NO block** v1 · pero tracked.
8. **Tests deben ser idempotentes** · ejecutables en paralelo · sin orden dependiente.

## 12. Pendientes [PENDIENTE — NO INVENTAR]

- Performance load testing (k6 o Locust) → diferido v2
- Chaos engineering (network partitions · DB drops) → diferido v2 cuando volumen lo justifique
- Visual regression testing (Percy / Chromatic) → diferido v2
- Mutation testing backend (Pitest equivalent Python) → diferido v3
- Contract tests con LLM real ocasional (semanal · validacion) → diferido v2
- API fuzzing avanzado (more than schemathesis defaults) → diferido v3

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_CONTRACT_TEST_HARNESS_v1` **NO implica reemplazar QA humano**. El harness valida contratos · pero usability · UX issues sutiles · brand consistency requieren ojo humano. QA = harness automatizado + revision humana periodica.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT. 3 capas: OpenAPI conformance (schemathesis · 4700+ cases) · Fixtures Ciclope harness pytest custom (30 fixtures · 702 assertions verificable programaticamente) · UI E2E Playwright + axe-core a11y. Mock LLM deterministico (LiteLLM mock provider). CI/CD GitHub Actions integrado. Pre-deploy gate · 100% pass requerido. Severity:critical fail = deploy blocked. Test explicit AM-view sin @CURADOR/k-anon/L3 (R5 critical). 8 reglas inquebrantables. NO implica reemplazar QA humano.

## Stamp
VIGENTE 2026-05-02 — Harness ejecutable conecta los 702 assertions con codigo real. Sin esto · "fixtures viven en otro planeta" (R5). Gate tecnico antes de Sprint 1 + regression suite obligatoria pre-deploy.
