## A11_MOBILE — Mobile iOS/Android 2026

### Estado del arte 2026

| Práctica | Trade-off |
|---|---|
| KMP + Native UI [HIGH] | Lógica shared; nativa BLE |
| Flutter + Impeller [HIGH] | Single codebase; bundle pesado; plugins riesgo |
| RN New Arch [MEDIA] | Mejor bridge; JS runtime |

### Tendencias 2026–2028

| Tendencia | S/R |
|---|---|
| KMP default enterprise [HIGH] | Señal — Netflix/VMware |
| Flutter B2B BLE [HIGH] | Ruido — plugins bloquean |
| Performance Engineer separado [MEDIA] | Señal — hiring |

### Stack/herramientas SOTA top 3

| Herramienta | Uso | Trade-off |
|---|---|---|
| Bitrise [HIGH] | CI/CD mobile-first | Preconfig; créditos |
| Codemagic [HIGH] | CI/CD mobile-first | M4; pricing fijo |
| Maestro [HIGH] | E2E cross-platform | YAML; <15m setup; <1% flaky |

### Bloque A — Roles SOTA

| Rol | Scope | Sep/Cap |
|---|---|---|
| iOS Mobile Eng [HIGH] | SwiftUI, CoreBT | **Sep**; 1 |
| Android Mobile Eng [HIGH] | Compose, Flow | **Sep**; 1 |
| Mobile DevOps Eng [HIGH] | CI mobile | **Cap**; 0.5 |
| BLE/Hardware Specialist [HIGH] | GATT, MTU | **Sep** si custom |
| Mobile Performance Specialist [MEDIA] | Startup | **Cap** v1; **Sep** >5 |

### Bloque B — Competencias transversales

1. **Mobile Security & Privacy [HIGH]** — OWASP, Manifests, N4. Eval: permisos.
2. **Reactive Streams Hardware [HIGH]** — Flow; Combine; SKIE. Eval: BLE→streams.
3. **LATAM Data Residency [HIGH]** — Ley CR, cifrado. Eval: sync.

### Anti-patterns 2026 + KPIs

| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Flutter/RN capa BLE sin nativo | Plugins 3rd party; retrasan APIs | KMP lógica + native; 100% APIs nativos |
| DevOps genérico sin mobile steps | Signing, Xcode | CI mobile; setup <2h |
| Solo Appium/Espresso/XCTest | Appium 15-20%; locators 30-50% | Maestro <1%; ≥80% |
| Omitir Privacy Manifest B2B | Apple rechaza enterprise 2024 | Privacy CI; 0 rechazos |
| BLE como "solo HTTP" | Bonding/MTU/bg | Reconnect <3s; >99.5% 1er intento |
