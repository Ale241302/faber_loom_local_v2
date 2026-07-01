---
id: MANIFIESTO_APPEND_20260503c_TEAM_INVENTORY
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-03
fecha: 2026-05-03
agente: Cowork (arquitecto · indexa inventario hiring a peticion CEO)
aplica_a: [MWT, FaberLoom, ScanFoot]
---

# MANIFIESTO_APPEND_20260503c_TEAM_INVENTORY

## Que paso

CEO solicito inventario de profesionales/expertos para desarrollo de los 3 productos (MWT, FaberLoom, ScanFoot) y plataforma compartida. Cobertura solicitada: seguridad, desarrollo funcional, backend, UX, compliance, software, SaaS, apps mobile, lenguajes de software, forecast, flujos funcionales, agentes autonomos, "y no se que quedara pendiente".

Cowork hizo AskUserQuestion con 3 decisiones criticas antes de arrancar:
- Formato output -> CEO eligio "Markdown indexado en KB"
- Alcance temporal -> CEO eligio "Plataforma completa 18-24 meses"
- Modalidad hiring -> CEO eligio "Full-time hires only"

Antes de construir, Cowork lanzo Explore agent para inventariar stack/alcance real de los 3 productos en KB. Resultado: contexto completo (FaberLoom Foundation Beta plan v1.3.1, MWT en produccion Amazon FBA + B2B pilot, ScanFoot DRAFT con AC-02 gate pendiente, plataforma compartida ARCH_AGENT_PRINCIPLES + LLM Routing + Action Engine + Audit Module).

Inventario producido cubre 19 disciplinas con ~109 FTE objetivo a 24m, organizado en 4 fases (F1 Foundation 0-6m, F2 Beta->GA 6-12m, F3 Scale 12-18m, F4 Multi-producto 18-24m) y 4 niveles de prioridad P0-P3.

## Documentos creados

| Archivo | Que documenta | Lineas aprox |
|---|---|---|
| `docs/ENT_GOB_TEAM_INVENTORY_FULL.md` | Inventario canonico 19 disciplinas + roadmap fases F1-F4 + headcount acumulado + riesgos + proximos pasos. Cubre: 1.Leadership 2.Eng Leadership 3.Backend 4.Frontend 5.Mobile 6.AI&Agents 7.Data/ML/Forecasting 8.Hardware/Firmware 9.DevOps/SRE 10.Security 11.Compliance/Privacy/Legal 12.Design 13.QA 14.DB/Data Platform 15.Customer Success 16.Sales/GTM 17.Operations 18.People/HR 19.Finance/Admin. Plus seccion "no se que quedara pendiente" con 12 funciones que no encajan en las 19 (DevRel, Tech Writer, i18n, AI Safety, GovRel, etc). | ~340 |

## Documentos modificados

| Archivo | Cambio |
|---|---|
| `IDX_GOBERNANZA.md` | +1 fila seccion Entities (Team Inventory Full -> ENT_GOB_TEAM_INVENTORY_FULL.md DRAFT v1.0). Health line actualizada (11 -> 12 ENTs gob). Ultima revision -> 2026-05-03c. last_review header -> 2026-05-03. |

## Decisiones del arquitecto

1. **Path docs/ raiz, no docs/faberloom/.** Inventario aplica_a [MWT, FaberLoom, ScanFoot] simultaneamente. domain Gobernanza es transversal por definicion. El scope FaberLoom (memoria 2026-04-29) aplica solo a archivos FB-puros. Inventario cross-product va en docs/ raiz, registrado en IDX_GOBERNANZA.

2. **Type ENT (entity = dato), no PLB (instruccion).** El inventario es un catalogo de roles (datos sobre que roles existen, su scope, prioridad, fase). No es una instruccion ejecutable. Si en el futuro se materializa proceso de hiring, ese sera PLB_HIRING_FT o similar.

3. **Status DRAFT, no VIGENTE.** Documento es un primer pase. Requiere validacion CEO antes de promover a VIGENTE. El changelog del archivo lo deja explicito.

4. **No se creo ENT_GOB_HIRING_ROADMAP_F1.md aun.** El inventario es el catalogo. El roadmap de hire concreto (con candidatos, fechas, comp ranges) es responsabilidad del futuro Head of People + CFO + CEO, post-aprobacion del inventario y post-existencia de plan financiero asociado. Esta separacion mantiene el inventario reusable independiente del momento de funding.

5. **No se creo ENT_GOB_COMP_BANDS_LATAM.md aun.** Bandas salariales requieren benchmark LATAM real + decision sobre comp philosophy (above market / at market / below market + equity). Esa decision la toma CEO+CFO+Head of People juntos. Documentado como pendiente P2.

6. **109 FTE como objetivo, no compromiso.** El total acumulado a 24m es objetivo de capacidad. Realismo: probablemente +20% buffer por attrition + ramp-up. El gating real es liquidez. Documentado explicitamente en seccion "Resumen de headcount por fase".

7. **Seccion "no se que quedara pendiente" explicita.** El CEO pidio cubrir esto. Cowork identifico 12 funciones que no encajan limpio en las 19 disciplinas y las clasifico como diferir/F3/F4/post-F4 con razon. Asi el CEO no tiene que preguntar "y que mas?" — esta documentado el descarte y razon.

## Por que ENT_GOB_ y no ENT_PLAT_

ENT_PLAT_ esta reservado para entidades de plataforma tecnica (multitenant, infra, frontends, modulos, etc.). El inventario de roles humanos es decision de gobernanza corporativa, no de plataforma. Coherente con donde vive ENT_GOB_PROVEEDORES, ENT_GOB_KPI, ENT_GOB_RIESGOS, ENT_GOB_DECISIONES.

## Que NO se hizo

- **No se creo ENT_GOB_HIRING_ROADMAP_F1.** Pendiente P1 documentado en el inventario.
- **No se creo ENT_GOB_COMP_BANDS_LATAM.** Pendiente P2 documentado.
- **No se creo POL_HIRING_GATES.** Pendiente P2 documentado (gates de revenue/runway per fase).
- **No se actualizo ENT_GOB_DECISIONES.** El inventario referencia decisiones CEO (formato/alcance/modalidad) tomadas en sesion AskUserQuestion 2026-05-03 pero no las formaliza como DEC-NNN. Si se quiere formalizar como decision firmada, agregar en ENT_GOB_DECISIONES en sesion siguiente.
- **No se creo JD individuales por rol.** El inventario es a nivel "rol + responsabilidad core + stack". JDs detalladas son siguiente capa cuando hire concreto este planeado.
- **No se ejecuto validacion contra ENT_GOB_PENDIENTES.** Algunos pendientes CEO podrian relacionarse a roles aqui inventariados (ej. CEO-XX sobre hire CTO). Reconciliacion explicita pendiente P3.

## Sync canonico requerido

Esta sesion es Cowork -> escribio en OneDrive. Para que cambios pasen al repo canonico (`C:\dev\mwt-knowledge-hub`):

1. Ejecutar `sync_team_inventory_indexa.ps1` (creado en raiz del workspace) — copia los 3 archivos modificados/nuevos al repo canonico:
   - `docs/ENT_GOB_TEAM_INVENTORY_FULL.md` (nuevo)
   - `docs/IDX_GOBERNANZA.md` (modificado)
   - `docs/MANIFIESTO_APPEND_20260503c_TEAM_INVENTORY.md` (nuevo, este archivo)
2. CEO valida diff con `git diff`
3. CEO commitea con mensaje sugerido: `[GOBERNANZA] ENT_GOB_TEAM_INVENTORY_FULL v1.0 DRAFT - inventario 19 disciplinas / 109 FTE / 18-24m / FT only`
4. Restaurar mirror oficial al final con `mirror_to_onedrive.ps1` (Push-Location al repo canonico antes)

## Proximas acciones

| Prioridad | Item | Bloqueo | Dueño |
|---|---|---|---|
| P0 | CEO lee y valida inventario completo | Lectura | CEO |
| P0 | Decidir orden exacto hire F1 (CTO -> Head of FB Product -> Head of Backend -> Head of FE -> Head of AI?) | Inventario aprobado | CEO |
| P1 | Crear ENT_GOB_HIRING_ROADMAP_F1 con candidatos + fechas + comp ranges | F1 priorizado | CEO + futuro Head of People |
| P2 | Crear ENT_GOB_COMP_BANDS_LATAM con benchmarks por rol/seniority/pais | Roadmap firmado | Head of People + CFO |
| P2 | Crear POL_HIRING_GATES con gates revenue/runway per fase | F1 cerrado | CEO + CFO |
| P3 | Reconciliar inventario con ENT_GOB_PENDIENTES (decisiones CEO sobre hire ya documentadas) | Inventario VIGENTE | CEO |

## Changelog

- 2026-05-03c · Creacion inicial. Indexado ENT_GOB_TEAM_INVENTORY_FULL v1.0 DRAFT + actualizacion IDX_GOBERNANZA. 2 archivos nuevos (inventario + este manifiesto), 1 modificado (IDX). Total cobertura: 19 disciplinas, ~109 FTE objetivo a 24m, full-time only, plataforma completa.
