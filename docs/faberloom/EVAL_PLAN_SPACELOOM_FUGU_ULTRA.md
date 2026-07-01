# EVAL_PLAN_SPACELOOM_FUGU_ULTRA.md -- Review Red-Team del Plan de Build SpaceLoom Etapa 1
id: EVAL_PLAN_SPACELOOM_FUGU_ULTRA
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: AUDIT
stamp: DRAFT -- 2026-06-25 11:01:34 -06:00 -- review red-team del plan de build SpaceLoom Etapa 1; motor Fugu Ultra
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_SELFHOSTED_v1.1.md - SPEC_SPACELOOM_SELFHOSTED_v1.2.md - SPEC_SPACELOOM_SELFHOSTED_v1.3.md - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md - CLAUDE.md - WIKI.md
run_id: [PENDIENTE -- NO INVENTAR: el prompt trae placeholder RUN_ID sin instancia concreta]

---

## 1. Metodo

Se reviso el plan de build de SpaceLoom Etapa 1 con protocolo debate-and-aggregation. La postura inicial fue red-team: buscar primero por que el plan podria estar equivocado, subestimado o incompleto.

Fuentes leidas del repo canonico:
- `CLAUDE.md`, `WIKI.md`.
- `docs/faberloom/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`.
- `docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md`.
- `docs/faberloom/SPEC_SPACELOOM_SELFHOSTED_v1.1.md`, `v1.2.md`, `v1.3.md`.
- `docs/faberloom/SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md`.
- `docs/faberloom/SPEC_FB_ROUTING_PRESETS_v1.md`.
- `docs/faberloom/SCH_FB_SKILL_MANIFEST_v2.md`.
- `docs/faberloom/DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md`.

Regla aplicada: dato ausente = `[PENDIENTE -- NO INVENTAR]`.

---

## 2. Fase 1 -- Argumentos independientes por rol

### ROLE A -- Builder / Ingenieria

1. **El orden es razonable, pero no linealmente seguro.** SL0 -> SL1 -> SL2 -> SL3a -> SL3b/c -> SL3.5 -> SL5 -> SL4 es defendible, pero SL1 promete demasiado antes de tener KB real, workspace real y evidence fuerte. Un draft desde seed puede activar dogfooding, pero no prueba el cuello de botella de Alvaro.
2. **SL2 esta subestimado.** MD/TXT + FTS5 puede ser rapido; PDF, Excel, chunking, source_hash, reindex y citas confiables son el core dificil. Si SL2 falla, `0 inventado` y adopcion fallan.
3. **SL3a esta subestimado si usa SCH_FB_SKILL_MANIFEST_v2 real.** SKILL.md portable + schema + sandbox + routine + triggers + tools_allowlist no es solo una pantalla; requiere compiler/lint, versionado, validacion y runner.
4. **SL3c no es un hito de una semana si la DoD exige demostrar que edit_pct baja.** Esa metrica requiere repeticion real, tipos de tarea comparables y suficientes usos. Puede capturarse desde v1, pero demostrar mejora puede tardar mas que implementar la tabla.
5. **SL4 es el hito calendario mas fragil.** Firma, notarizacion, SmartScreen, WebView2, instaladores, keyring, auto-update y pruebas Win/Mac suelen romper la estimacion de 3 semanas para un dev si no existen cuentas/certificados/proceso listos.
6. **SL5 es correctamente recortable, pero el producto se siente menos valioso sin email.** Si el dolor diario entra por correo, diferir SL5 protege seguridad pero debilita adopcion.

Veredicto ROLE A: **MATIZADO**. El plan puede arrancar como dogfood interno, pero 12 semanas / 1 dev solo es plausible con recortes fuertes: SL5 diferido, SL4 minimo, router minimo, y SL3c como captura de senales, no prueba estadistica.

### ROLE B -- Seguridad / Sellado

1. **HITL esta bien declarado, pero falta probarlo fuera de SL5.** El plan mata envio sin HITL, pero injection se prueba solo en correo. Hay injection por documentos, PDFs, Excel, skills y KB; esa superficie existe desde SL2/SL3a.
2. **El sellado por workspace es la promesa de seguridad, pero llega tarde si se cargan datos reales antes de SL3.5.** El plan dice que memoria sellada por workspace entra en SL2a, pero el gate de fuga cross-workspace esta en SL3.5. Antes de usar datos de clientes distintos, debe existir un test minimo de scoping.
3. **`0 inventado` no equivale a dato correcto.** Un draft puede citar una fuente stale, equivocada o irrelevante. Evidence hash simple no prueba source-to-field; el plan no exige vigencia de precio/stock/margen ni autoridad de fuente.
4. **SQLite cifrado es opcional aunque la app local guardara correo, KB y drafts.** Para un app local-first con datos de clientes, laptop robado / perfil OS comprometido es un P0/P1 no cerrado.
5. **Auto-update no esta tratado como supply chain.** El spec pide auto-update basico, pero no define firma/verificacion del update, rollback, canal, ni proteccion de la clave de firma.
6. **Gold loop puede contaminar memoria.** Si el humano aprueba un draft incorrecto o bajo fatiga, se convierte en gold/few-shot. No hay gate de verificacion independiente para campos duros.

Veredicto ROLE B: **DESACUERDO con liberar sin endurecer DoD de seguridad**. El plan cubre los riesgos obvios, pero no cubre source freshness, injection no-email, cifrado local y supply-chain update.

### ROLE C -- Producto / Adopcion

1. **La apuesta de adopcion desde SL1 es correcta, pero SL1 podria no ser el producto que Alvaro necesita.** Si el primer draft usa seed artificial y no KB real de MWT, Alvaro puede probarlo una vez y volver a Claude/Gmail/Excel.
2. **El dolor diario probablemente es ingestion + datos duros + respuesta.** SpaceLoom chat sin correo y sin KB robusta puede ser otra interfaz de chat. La adopcion real depende de que el camino RFQ/cobranza -> datos correctos -> draft sea menos friccion que el flujo actual.
3. **Hay over-build para single-user.** Multi-proveedor/presets/fabrica, llave graduada completa, gold loop demostrado, auto-update, marca/legal y SKILL manifest completo pueden absorber semanas antes de resolver el uso diario.
4. **Falta una definicion operativa de adopcion.** El plan dice "si lo sigue usando, sirve"; E0.5 v1.2 habla de 1-2 semanas / 10-15 RFQs reales, pero el plan no fija criterios minimos: cuantos dias, cuantos casos, que cuenta como uso voluntario, y que friccion mata.
5. **SL5 es recortable tecnicamente, pero quizas no productivamente.** Si el usuario debe copiar/pegar correos, la promesa de Inbox/WorkLoom se retrasa. Una importacion `.eml`/paste estructurado o read-only mail lite podria ser mejor que esperar SL5 completo.

Veredicto ROLE C: **MATIZADO**. El plan tiene el instinto correcto (dogfood), pero debe recortar lo que no haga que Alvaro lo use y adelantar el minimo de datos reales / fuente verificable.

---

## 3. Fase 2 -- Debate y agregacion

**Consenso parcial:** La direccion general aguanta: single-user local-first, una entidad, SKILL.md, KB por workspace, HITL, y dogfooding antes de SaaS es una buena respuesta al freeze del multi-tenant.

**Agujero principal:** El plan subestima el tramo que convierte un chat en herramienta diaria: KB/source grounding verificable, datos duros frescos, evidencia campo-a-fuente, y una experiencia que reduce friccion real desde SL1-SL2.

**Agujero de secuencia:** SL3.5 como gate de fuga llega despues de SL2/SL3, pero los datos reales y workspaces por cliente aparecen en SL2. Se necesita un sellado minimo y tests de scoping en SL2a, dejando la llave graduada completa para SL3.5.

**Agujero de estimacion:** Varias tallas L/M esconden trabajo de producto y QA: router multi-proveedor, PDF/Excel fiable, SKILL compiler, gold loop, email OAuth/SMTP, desktop firmado y auto-update. El calendario de 12 semanas es posible solo como dogfood interno recortado, no como producto distribuible robusto con SL5 completo.

**Agujero de seguridad:** El plan mata injection por email, pero no exige canaries de injection desde documentos/skills/KB. Tampoco exige freshness de datos comerciales, cifrado local por defecto, ni verificacion de supply-chain de auto-update.

---

## 4. Respuestas especificas

### Q1. El orden SL0->SL1->SL2->SL3->SL3.5->SL5->SL4 es correcto?

**HALLAZGO:** El orden es correcto como macro-secuencia, pero tiene tres dependencias mal calibradas. Primero, SL1 quiere adopcion con un draft real antes de KB real; eso puede producir un demo, no habito. Segundo, el sellado completo aparece en SL3.5, pero SL2 ya introduce workspaces/clientes y KB; debe existir sellado minimo desde SL2a. Tercero, el spec marca Inbox en SL2/SL5, mientras el plan trata correo como SL5 recortable; eso deja ambigua la entrada real del flujo.

**RIESGO:** P1.

**RECOMENDACION:** Mantener macro-orden, pero ajustar gates:
- SL1 debe ser **SL1a router+chat minimo** + **SL1b primer draft con mini-KB real**, no solo seed artificial.
- SL2a debe incluir test minimo `workspace A no lee contenido B` antes de cargar datos reales de clientes distintos.
- Disenar interfaz de connector en SL3 como dice IMAP spec, pero permitir antes un **mail/import lite**: pegar email estructurado, `.eml`, o read-only manual sin SMTP.
- SL5 completo debe seguir despues de SL3.5; si entra en Etapa 1, no debe bloquear el core.

### Q2. La estimacion ~12 semanas / 1 dev es realista? donde se rompe?

**HALLAZGO:** Es optimista. Es plausible para dogfood interno si el dev es full-time, decide rapido, trabaja en un solo OS primero y recorta SL5. Se rompe si se exige al mismo tiempo: Win+Mac firmado, auto-update, OAuth/IMAP/SMTP real, PDF/Excel robusto, SKILL.md compiler compatible con SCH_FB_SKILL_MANIFEST_v2, gold loop demostrado y tests de seguridad. Los hitos mas subestimados son SL2b/c, SL3a/c, SL5 y SL4.

**RIESGO:** P1; P0 si la fecha de 12 semanas se trata como compromiso fijo para producto distribuible.

**RECOMENDACION:** Re-estimar en dos calendarios:
- **Dogfood interno usable:** 8-10 semanas, con SL5 diferido, SL4 dev-loop/instalador simple, un OS primario, router minimo.
- **Etapa 1 distribuible real:** 14-18 semanas, incluyendo hardening de ingestion, seguridad, firma/notarizacion, update, QA Win/Mac y documentacion.

Convertir SL3c a "captura de edit_pct + gold candidates"; demostrar mejora estadistica queda como criterio de salida extendido, no una semana fija.

### Q3. Las costuras contract-first alcanzan para Etapa 2-3 sin rewrite?

**HALLAZGO:** Alcanzan como intencion, no como contrato suficiente. El plan menciona `tenant_id` latente y SQLite -> Postgres+RLS, pero los esquemas fuente usan sobre todo `workspace_id` y no definen actor/user/role/tenant context. `audit.jsonl` local sirve para single-user, pero Etapa 2 multi-usuario necesitara actor, permisos, eventos e inmutabilidad mas formal. Routine tiene `trigger_json` y `tools_allowlist`, pero no explicita versionado de routine, approval requirements por output, kill switch, golden sample obligatorio o tenant_scope como SCH_FB_SKILL_MANIFEST_v2 espera.

**RIESGO:** P1.

**RECOMENDACION:** Sin construir multi-tenant, agregar costuras minimas desde SL0/SL2:
- Campos latentes: `tenant_id`, `user_id/actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`.
- Una capa `Context(workspace_id, tenant_id?, user_id?)` usada por toda query, aunque en v1 tenga valores constantes.
- Una interfaz `AuditWriter` que hoy escriba `audit.jsonl` pero manana pueda escribir outbox/audit table.
- Un compiler de Routine que emita un subconjunto claro del manifest v2, no un formato paralelo incompatible.

### Q4. Una entidad, no fabrica de agentes + router multi-proveedor: fuerza runtimes paralelos u orquestador pesado?

**HALLAZGO:** El principio "una entidad" aguanta si se mantiene como runtime unico + rutinas como config. Pero el plan ya introduce triggers manual/cron/email, proactividad, scheduler local, connector, fallback, HITL, skills, gold loop y presets. Eso es un orquestador en miniatura aunque no se llame n8n. Ademas, SPEC_FB_ROUTING_PRESETS contiene niveles de fabrica, backtests y builder con IA; traer demasiado de eso a SL1 inflaria el runtime.

**RIESGO:** P1.

**RECOMENDACION:** Limitar SL1 a router minimo:
- 2-3 presets locales, BYO-key, fallback, cost rows, hard budget cap y provider allowlist.
- No wizard, no preset builder, no auto-optimizador, no backtest hasta que exista ledger real.
- Rutina = config declarativa; triggers solo `manual` en SL3a. Cron/email triggers entran detras de una cola determinista con idempotency en SL5/Etapa posterior.
- El scheduler local solo dispara tareas seguras/read-only; irreversibles siempre pasan por el mismo gate HITL.

### Q5. Que esta SOBRE-construido para single-user y deberia recortarse?

**HALLAZGO:** El plan ya recorta multi-tenant, marketplace, code-exec, HTTP externo, billing y n8n; eso es correcto. Lo que todavia parece sobre-construido para single-user es: router multi-proveedor completo en SL1, fabrica de presets mas alla de presets basicos, llave graduada rica antes de demostrar uso, gold loop probado estadisticamente, SL5 email completo si core no esta adoptado, licencia/marca como bloqueo del dogfood interno, y auto-update robusto antes de tener usuarios externos.

**RIESGO:** P2/P1. P2 si solo agrega trabajo; P1 si impide llegar al primer uso diario.

**RECOMENDACION:** Cortar una version de dogfood:
- SL1: un proveedor cloud + Ollama opcional + fallback simple + costo visible.
- SL2: solo MD/TXT + CSV/XLSX prioritario para precios; PDF despues si realmente bloquea.
- SL3a: 1-2 rutinas canonicas de MWT, no builder general.
- SL3.5: scoping y tests, no UX completa de llave graduada salvo si hay fuga real.
- SL5: diferir SMTP; iniciar con read-only/import y draft.
- SL4: instalador interno primero; firma/auto-update completos para beta externa.

### Q6. Que riesgo P0 NO esta cubierto por el plan ni por la DoD del spec?

**HALLAZGO:** El P0 no cubierto es **draft verificablemente correcto con datos frescos y fuente autorizada**. El plan exige `0 inventado` y cita/evidence, pero no exige que la fuente sea vigente, que el campo citado corresponda al dato usado, ni que precio/stock/margen/equivalencia esten autorizados. Otros P0/P1 cercanos no cerrados: prompt injection desde KB/docs/skills, DB local sin cifrado por defecto, auto-update supply-chain, contaminacion del gold loop por aprobaciones erroneas, y perdida/corrupcion de la unica DB local.

**RIESGO:** P0 para datos duros stale/falsos y auto-update comprometido; P1 para backup/cifrado si el scope interno es limitado.

**RECOMENDACION:** Agregar DoD y kill criteria:
- `source_to_field_check`: cada precio/SKU/stock/margen/lead time/equivalencia apunta a fuente vigente y tipo autorizado.
- `stale_data_block`: si la fuente esta vencida o no tiene fecha/version, el draft pide confirmacion en vez de afirmar.
- Injection tests para email, PDF/HTML, Excel/CSV, KB text y SKILL.md.
- Cifrado local o, como minimo, passphrase/SQLCipher obligatorio para workspaces confidenciales.
- Auto-update firmado y verificado; ninguna descarga ejecutable sin firma valida.
- Backup/export/restore smoke test antes de usar datos reales.
- Gold samples de campos duros solo con verificacion independiente o segundo gate.

---

## 5. Cierre

### VEREDICTO = MATIZADO

El plan aguanta como direccion: construir SpaceLoom single-user local-first y dogfoodearlo antes de volver al SaaS es coherente. No aguanta como promesa cerrada de 12 semanas/1 dev para producto completo: necesita recortar alcance, adelantar sellado minimo y endurecer datos/evidence/seguridad.

### BLIND SPOTS

1. Freshness y autoridad de catalogo/precios/stock/margen/equivalencias.
2. Evidence campo-a-fuente; hash simple no prueba verdad del dato.
3. Injection desde documentos, PDF/HTML, Excel/CSV, KB y SKILL.md; no solo email.
4. Cifrado local / laptop robado / backups de la unica DB local.
5. Auto-update como supply chain: firma, rollback, canal y proteccion de claves.
6. Gold loop contaminado por aprobaciones humanas erroneas o complacencia.
7. Ambiguedad Inbox SL2/SL5 y valor de adopcion sin correo real.
8. Falta de criterios operativos de adopcion: dias/casos/uso voluntario/friccion.
9. Etapa 2 multi-usuario: falta actor/user/role/audit context desde el modelo inicial.
10. Competencia horizontal pendiente: no esta probado que este flujo gane vs Claude Projects + Obsidian/Excel/Gmail templates.
11. Rutinas con triggers/proactividad pueden convertirse en orquestador pesado si no se limitan.
12. SL4 subestima QA multi-OS, firma/notarizacion, WebView2/WKWebView y update.

### Hito mas fragil

**SL2a/b/c -- Workspaces + KB grounding.** Si la KB no extrae, cita y verifica datos duros de forma confiable, SL1 no se vuelve habito, SL3 gold aprende basura, SL3.5 no protege nada util y SL5 solo acelera errores por correo. Calendario aparte, SL4 es el mas fragil para distribucion externa.

### Confianza por hito

| Hito | Confianza | Razon |
|---|---|---|
| SL0 | ALTA | Esqueleto, DB, migraciones, seed y healthcheck son acotados si el carve-out CEO existe. |
| SL1 | MEDIA | Chat + LiteLLM + costo + fallback es factible; adopcion con seed y router completo es incierta. |
| SL2a/b/c | BAJA-MEDIA | MD/TXT/FTS5 es manejable; PDF/Excel, citas y source-to-field confiable son el core dificil. |
| SL3a | MEDIA | SKILL.md + schema es viable si se recorta a subset; manifest v2 completo inflaria. |
| SL3b/c | BAJA-MEDIA | HITL simple es viable; demostrar gold loop/edit_pct baja requiere tiempo y volumen. |
| SL3.5 | MEDIA | Scoping local es viable; llave graduada y pruebas anti-fuga deben adelantarse en version minima. |
| SL5 | BAJA | Alto valor pero alto riesgo: OAuth/IMAP/SMTP, keyring, injection, workspace mapping y HITL real. |
| SL4 | BAJA-MEDIA | Pywebview/PyInstaller es razonable; firma, notarizacion, SmartScreen, auto-update y QA Win/Mac son fragiles. |

---

Changelog:
- v1.0 (2026-06-25): Review red-team Fugu Ultra del plan de build SpaceLoom Etapa 1. Veredicto MATIZADO; recomienda recortar a dogfood interno, adelantar scoping minimo, endurecer source-to-field, y reestimar distribucion/SL5.
