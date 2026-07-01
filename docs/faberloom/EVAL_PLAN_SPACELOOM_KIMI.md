# EVAL_PLAN_SPACELOOM_KIMI.md -- Red-Team Review Plan Build SpaceLoom Etapa 1
id: EVAL_PLAN_SPACELOOM_KIMI
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: AUDIT
stamp: DRAFT -- 2026-06-25 -- red-team del plan de build SpaceLoom Etapa 1; motor Kimi
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_ETAPA1_v1.md - SPEC_SPACELOOM_SELFHOSTED_v1.1.md - SPEC_SPACELOOM_SELFHOSTED_v1.2.md - SPEC_SPACELOOM_SELFHOSTED_v1.3.md - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SCH_FB_SKILL_MANIFEST_v2.md - DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md - CLAUDE.md - WIKI.md [PENDIENTE -- NO INVENTAR: WIKI.md no localizado en repo]

---

## 1. Metodo

Se aplico el protocolo de debate-and-aggregation con tres roles mutuamente excluyentes:

- **ROLE A -- Builder/Ingenieria:** factibilidad, estimacion y orden de dependencias.
- **ROLE B -- Seguridad/Sellado:** HITL, injection, fuga cross-workspace, dato inventado, privacidad.
- **ROLE C -- Producto/Adopcion:** que hace que Alvaro use el producto y que sobra para single-user.

Fuentes leidas: `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`, `SPEC_SPACELOOM_ETAPA1_v1.md`, `SPEC_SPACELOOM_SELFHOSTED_v1.1/v1.2/v1.3.md`, `SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md`, `SPEC_FB_ROUTING_PRESETS_v1.md`, `SCH_FB_SKILL_MANIFEST_v2.md`, `DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md`, `CLAUDE.md`. `WIKI.md` no fue localizado; se marca [PENDIENTE -- NO INVENTAR].

---

## 2. Fase 1 -- Argumentos por rol

### ROLE A -- Builder/Ingenieria

1. **El orden deja HITL demasiado tarde para la adopcion.** SL1 promete "draft real" usable, pero el HITL/Workflow de aprobacion llega recien en SL3b. Hasta entonces, Alvaro puede ver drafts pero no enviarlos desde la app. Eso frustra el dogfooding: el valor esta en enviar rapido, no en generar texto que luego copia a mano.
2. **SL3.5 (sellado) deberia ir antes.** Si en SL2a/b/c y SL3a ya se crean workspaces con datos de distintos clientes, la fuga cross-workspace es posible antes de que exista el sellado. En single-user el riesgo es accidental (query sin filtro), pero sigue siendo P0.
3. **La estimacion de ~12 semanas es optimista.** Sumando los specs: SL0=1 + SL1=1 + SL2a/b/c=3 + SL3a/b/c=3 + SL3.5=1 + SL5=2 + SL4=3 = ~14 semanas. El plan cita ~11.5-12, lo que implica solapamientos o tallas ajustadas. Para 1 dev full-time que haga backend, DB, LLM routing, UI web, pywebview/PyInstaller, firma, notarizacion, auto-update, extractores PDF/Excel, parser SKILL.md y connector IMAP, 12 semanas es agresivo.
4. **SL4 (desktop firmado) es el mas incierto.** Firma de codigo, notarizacion Mac, SmartScreen Win, auto-update, WebView2/WKWebView quirks, keyring cross-OS y paths de datos son trabajo real con dependencias externas (Apple Developer, cert Windows). v1.3 honestamente sube SL4 a ~3 semanas, pero aun asi es fragil.
5. **SL5 (correo) tambien es riesgoso.** OAuth app registration, IMAP app-passwords, manejo de adjuntos, HTML sanitizado, tests de injection y el flujo HITL de envio son facilmente 2+ semanas.
6. **Costuras contract-first parciales.** SKILL.md portable y router abstraido estan bien. Pero el modelo de datos de v1.1 no incluye `tenant_id` ni mecanismo de `shared` workspace; para Etapa 2 (multi-usuario interno) y Etapa 3 (multi-tenant) se requerira alterar tablas. "Tenant_id latente" es una intencion, no un hecho en el esquema mostrado.
7. **Sobre-construccion en routing.** `SPEC_FB_ROUTING_PRESETS_v1` describe una fabrica completa (ECU/preset/curva, wizard, templates verticales, auto-optimizador, preset builder con IA). Para single-user BYO-key, probablemente baste un selector simple de modelo + caps. Implementar toda la fabrica es over-engineering.

### ROLE B -- Seguridad/Sellado

1. **HITL absoluto: bien enunciado, mal cronometrado.** El principio dice "cero envio sin HITL", pero SL1 genera drafts sin mecanismo de aprobacion hasta SL3b. Eso fuerza a Alvaro a copiar/pegar, lo cual debilita el control (puede enviar sin revisar) y la trazabilidad.
2. **Fuga cross-workspace: gate tardio.** SL3.5 sella despues de que ya se opero con multiples workspaces. El scoping por `workspace_id` es tecnicamente barato; deberia ser obligatorio desde SL2a.
3. **Prompt injection desde KB/documentos/skills no esta testeado.** El spec v1.1 menciona separar contenido de instrucciones, pero ni el plan ni la DoD incluyen un test de injection sobre PDF/Excel/Skills. Un documento malicioso o un skill descargado podria alterar instrucciones.
4. **Exfiltracion de datos a LLM cloud no esta gestionada.** El spec es honesto ("contexto sale al proveedor"), pero para datos de clientes de MWT eso es un riesgo P0 de compliance. No hay data classification N0-N4, DPA registry ni allowlist de jurisdiccion operativa en Etapa 1. Alvaro podria cargar precios de clientes y enviarlos a Anthropic/OpenAI sin consentimiento formal.
5. **Dato inventado en draft:** el principio es correcto, pero SL1 usa KB seed. Si el seed no cubre el RFQ, el modelo puede alucinar precio/stock. El gate "cita fuente" llega en SL2a; hasta entonces no hay mecanismo de evidence.
6. **Pérdida/corrupcion de datos local no esta cubierta.** SQLite en carpeta local sin backup automatico, sin migraciones robustas para auto-update y sin recovery. Un bug en una migracion o un corte de luz durante escritura puede dejar la DB corrupta.
7. **Credenciales en keyring son mejor que plano, pero no suficiente.** En un proceso local, la API key esta en memoria. Si se ejecuta un skill malicioso (aunque allowlistado), la fuga de credenciales es posible.
8. **Auto-update sin rollback.** v1.3 menciona auto-update basico, pero no hay estrategia de rollback si una version rompe. Riesgo P0 de dejar la app inusable.

### ROLE C -- Producto/Adopcion

1. **SL1 no es usable para el flujo real de Alvaro.** Generar un draft sin poder enviarlo (falta HITL) no reduce su trabajo diario. El dogfooding se mide por "si lo sigue usando", pero sin envio el incentivo es bajo.
2. **El Routine Hub puede ser overkill para single-user.** Alvaro no necesita una fabrica de skills; necesita que el asistente cotice/cobre/seguimiento bien. La distincion workspace/rutina/skill es poderosa pero requiere aprendizaje.
3. **El lenguaje tecnico asusta.** "Workspace", "routine", "skill", "evidence bundle" no son palabras de oficina. Si el onboarding no traduce esos conceptos, Alvaro puede abandonar antes de SL3.
4. **SL5 (correo) es de alto valor pero recortable.** Si se difiere, Alvaro sigue pegando/escribiendo a mano. Pero si se incluye, es el feature que mas reduce friccion.
5. **Dogfooding sin metrica es vago.** "Si lo sigue usando, sirve" no define umbral. Se necesita algo concreto: N drafts/semana, edit_rate, drafts enviados.
6. **El gold loop asume que Alvaro corrige con atencion.** Si Alvaro aprueba todo sin editar (complacency), el gold loop aprende mal. No hay Oscillation Counter ni mecanismo anti-complacency en el plan.
7. **Onboarding de API key es una barrera.** Pedirle a un no-tecnico que consiga una API key de Anthropic/OpenAI y la configure es punto de friccion. El plan lo asume trivial; no lo es.

---

## 3. Fase 2 -- Debate cruzado

- **A vs. B:** Ambos coinciden en que HITL y sellado llegan tarde. A lo ve como problema de adopcion/orden; B como problema de seguridad. El consenso es que SL3b/c y SL3.5 deberian adelantarse o al menos habilitarse en modo minimo antes.
- **A vs. C:** C dice que Alvaro no usara SL1 sin envio; A agrega que eso tambien rompe la validacion por adopcion. El plan asume que "generar draft" es suficiente para dogfood, pero no lo es.
- **B vs. C:** B senala riesgos de exfiltracion y corrupcion que C no habia priorizado. C reconoce que la privacidad de datos de clientes puede bloquear la adopcion si Alvaro no confia.
- **Consenso parcial:** El plan es **coherente de arquitectura pero fragil de ejecucion y adopcion**. La secuencia deberia ajustarse para permitir envio manual/HITL minimo desde SL1, y deben cubrirse riesgos P0 adicionales antes de declarar DONE.

---

## 4. Fase 3 -- Respuestas a las seis preguntas

### Q1. El orden SL0->SL1->SL2->SL3->SL3.5->SL5->SL4 es el correcto?

**HALLAZGO:** El orden es razonable para una construccion bottom-up, pero tiene dos fallas importantes: (a) **HITL llega demasiado tarde**: SL1 genera drafts reales pero no hay mecanismo de aprobacion/envio hasta SL3b, lo que frena la adopcion; (b) **Sellado cross-workspace llega tarde**: SL2a crea workspaces y SL3 opera con ellos, pero SL3.5 sella despues. Para single-user local el riesgo es accidental, pero sigue siendo un P0. SL5 antes de SL4 es correcto porque correo es recortable, y SL4 al final es logico.

**RIESGO:** P1 (HITL tarde afecta adopcion) / P0 (fuga cross-workspace antes del sellado).

**RECOMENDACION:**
- Introducir un **HITL minimo en SL1** (aprobar/copiar/enviar manual con doble confirmacion, aunque sea basico) para que el dogfooding sea real.
- Mover el sellado por workspace a **SL2a inmediato** (scoping por `workspace_id` en todas las queries) y dejar SL3.5 como validacion/llave graduada, no como primer cierre.
- Mantener SL5 recortable y SL4 al final.

---

### Q2. La estimacion ~12 semanas / 1 dev es realista?

**HALLAZGO:** La estimacion es **optimista**. Sumando los specs se acerca a ~14 semanas incluyendo SL5. SL4 (desktop firmado, notarizacion, auto-update, cross-OS) y SL5 (correo OAuth/IMAP, injection tests) son los puntos mas fragiles. Ademas, 1 dev full-time debe cubrir backend, DB, LLM routing, UI web, empaque desktop, extractores de documentos, parser de skills y connector IMAP. Eso es un stack muy amplio para una sola persona en 12 semanas.

**RIESGO:** P1 -- retrasos en SL3b/c, SL4 o SL5 rompen el timeline y la confianza del CEO.

**RECOMENDACION:**
- Planificar **14-16 semanas** como escenario base, o sumar un segundo recurso para UI/desktop (SL4) y/o correo (SL5).
- Aislar SL4 como track separado con dueño propio, porque depende de procesos externos (Apple, Microsoft).
- Definir hitios de decision (go/no-go) en SL1 y SL3c para decidir si se invierte en SL4/SL5.

---

### Q3. Las costuras contract-first alcanzan para que Etapa 2-3 se SUME sin rewrite?

**HALLAZGO:** Algunas costuras son limpias (SKILL.md portable, router abstraido, BYO-key -> keys gestionadas), pero hay **grietas importantes**. El modelo de datos de v1.1 no muestra `tenant_id` ni shared workspace; Etapa 2 (multi-usuario interno) requiere compartir workspaces y Etapa 3 requiere multi-tenant. Si no se disena con `tenant_id` latente y mecanismo de sharing desde ahora, la migracion a Postgres+RLS obligara a alterar tablas. La entidad unica en single-user puede asumirse como singleton; en multi-tenant habra que crear entidad por tenant.

**RIESGO:** P1 -- rewrite parcial del modelo de datos y del runtime de la entidad en Etapa 2-3.

**RECOMENDACION:**
- Incluir `tenant_id` o `owner_id` latente en el esquema base desde SL0, aunque sea fijo para single-user.
- Disenar `workspace.visibility` y un flag `shared` como extension futura, no como refactor.
- Documentar que la entidad es singleton **per user/tenant**, no singleton global, para evitar asumir estado compartido.

---

### Q4. "Una entidad, no fabrica de agentes" + router multi-proveedor: hay algo que fuerce runtimes paralelos u orquestador mas pesado?

**HALLAZGO:** El modelo de una entidad unica con rutinas como configuracion **no fuerza runtimes paralelos** si se mantiene el scope. Sin embargo, dos elementos pueden empujar hacia mas complejidad: (a) **triggers y proactividad** requieren un scheduler local (cron/poll IMAP), que es un mini-orquestador dentro del proceso; (b) **el router multi-proveedor/presets** puede escalar a un sistema de presets complejo (`SPEC_FB_ROUTING_PRESETS_v1`) que es overkill para single-user. Si se implementa la fabrica completa de presets, se agrega mucho codigo y UI innecesario.

**RIESGO:** P2/P1 -- scope creep en routing/triggers que desvia recursos del core.

**RECOMENDACION:**
- Limitar el routing en Etapa 1 a: preset simple (modelo/temperatura/fallback) + cost ledger + caps. Dejar la fabrica completa para Etapa 3.
- Implementar triggers como scheduler in-process ligero (APScheduler) sin disenar un motor generico de automatizaciones.
- Prohibir explicitamente code-exec/HTTP en skills (ya esta en v1.1) y mantener allowlist corta.

---

### Q5. Que del plan esta SOBRE-construido para single-user?

**HALLAZGO:** El principal over-build es el **sistema completo de routing presets** (`SPEC_FB_ROUTING_PRESETS_v1`): ECU/preset/curva, wizard de onboarding, templates por vertical, auto-optimizador HITL, preset builder con IA y backtest. Para un usuario unico con BYO-key, un selector de modelo + presupuesto mensual basta. Tambien es cuestionable el **Routine Hub completo** con skill authoring/schema/sandbox para un solo usuario: Alvaro necesita que cotice, no una fabrica de agentes. La **llave graduada** y el **audit.jsonl** son utiles pero menos criticos en single-user.

**RIESGO:** P2 -- se invierte tiempo en features que no mejoran la adopcion de Alvaro.

**RECOMENDACION:**
- Reducir routing a 3-4 presets fijos y un cap mensual en Etapa 1. Postergar wizard/templates/fabrica.
- Simplificar skill authoring: Alvaro puede escribir/ajustar prompts en markdown; el sandbox y el schema avanzado son deseables, no bloqueantes.
- Mantener evidence y HITL (si son core), pero no audit forense completo.

---

### Q6. Que riesgo P0 NO esta cubierto por el plan ni por la DoD del spec?

**HALLAZGO:** Hay varios riesgos P0 no cubiertos explicitamente:
1. **Exfiltracion de datos de clientes a LLM cloud.** El spec advierte que el contexto sale al proveedor, pero no hay data classification, DPA registry ni consentimiento formal. Para MWT, cargar precios/datos de clientes puede ser un problema regulatorio/comercial.
2. **Prompt injection desde KB/documentos/skills.** No hay test obligatorio ni filtro de contenido antes de que un documento/skill entre al contexto.
3. **Pérdida/corrupcion de datos local.** SQLite sin backup automatico ni migraciones robustas para auto-update.
4. **Auto-update sin rollback.** Una version defectuosa puede dejar la app inusable.
5. **Compromiso de credenciales en memoria.** Proceso local sin sandbox; un skill malicioso podria exfiltrar API key.

**RIESGO:** P0.

**RECOMENDACION:**
- Agregar a la DoD: test de prompt injection sobre documentos/skills y banner/consentimiento explicito antes de enviar datos de clientes a LLM cloud.
- Implementar backup automatico de la carpeta de datos y migraciones versionadas con rollback.
- Incluir data classification minima (etiquetar KB items como publico/interno/confidencial) y bloquear o advertir antes de enviar confidencial a cloud.
- Disenar auto-update con canal de rollback (descargar version anterior si la nueva falla).

---

## 5. Cierre -- Veredicto

### VEREDICTO: MATIZADO

El plan de build SpaceLoom Etapa 1 es **coherente de arquitectura y ambicioso**, pero **fragil de ejecucion y adopcion**. La idea de construir single-user, local-first y dogfoodear desde SL1 es correcta, pero la secuencia deja HITL y sellado demasiado tarde, la estimacion es optimista, hay over-build en routing/skills y faltan coberturas de riesgos P0 importantes (exfiltracion, injection, perdida de datos). No es un plan malo, pero necesita ajustes antes de arrancar SL0.

### BLIND SPOTS (lista priorizada)

1. **Adopcion en SL1 sin envio:** generar drafts sin HITL no demuestra valor para Alvaro.
2. **Exfiltracion de datos de clientes a LLM cloud:** riesgo P0 de compliance no cubierto.
3. **Prompt injection desde KB/documentos/skills:** no hay test ni filtro.
4. **Perdida/corrupcion de datos local:** sin backup ni rollback de auto-update.
5. **Modelo sin tenant_id/shared workspace:** obligara a alterar tablas en Etapa 2-3.
6. **Over-build en routing presets:** fabrica completa innecesaria para single-user.
7. **Estimacion optimista:** ~12 semanas con 1 dev para todo el stack es agresivo.
8. **Dogfooding sin metrica:** "si lo sigue usando" no es umbral validable.
9. **API key onboarding:** barrera de adopcion para no-tecnico no abordada.
10. **Auto-update sin rollback:** riesgo de dejar app inusable.

### Hito mas fragil

**SL4 (empaque desktop firmado Win/Mac)** es el mas fragil por dependencias externas (Apple Developer, certificado Windows, notarizacion, WebView2/WKWebView quirks, auto-update). Sin embargo, para el producto mismo, **SL3b/c (HITL + gold loop)** es el mas critico: si Alvaro no aprueba/envia drafts de forma rapida y confiable, no hay adopcion y el resto no importa.

### Confianza por hito

| Hito | Confianza | Razon |
|---|---|---|
| SL0 Esqueleto+seed | ALTA | Scope acotado; depende solo del carve-out del CEO. |
| SL1 Router+SpaceLoom+draft | MEDIA | Tecnico factible, pero adopcion limitada sin HITL/envio. |
| SL2a/b/c Workspaces+KB | MEDIA | Extractores PDF/Excel pueden demorar mas de lo previsto. |
| SL3a Skills/Routine Hub | MEDIA | Parser SKILL.md + schema; riesgo de over-scope. |
| SL3b/c HITL+gold loop | BAJA | UX critica para adopcion; requiere iteracion con Alvaro. |
| SL3.5 Sellado+llave | MEDIA | Scoping local es simple, pero llega tarde. |
| SL5 Correo | BAJA | OAuth/IMAP, injection, envio HITL; dependencias externas. |
| SL4 Empaque desktop | BAJA | Firma, notarizacion, auto-update, cross-OS. |

---

Changelog:
- v1.0 (2026-06-25): Red-team review del plan de build SpaceLoom Etapa 1. Veredicto MATIZADO; ajustes sugeridos en orden, estimacion, costuras y cobertura de riesgos P0.
