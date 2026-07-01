# POL_AI_GOV_SKILL_INSTALLATION — Lifecycle e Instalacion de Skills Externas
id: POL_AI_GOV_SKILL_INSTALLATION
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
subfamilia: AI_GOV
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
refs: SCH_SKILL (skills propias MWT — distintas) · POL_DATA_CLASSIFICATION · POL_AI_GOV_DATA_CLASS_PROVIDER · ENT_PLAT_SKILLS_CATALOG · ARCH_AGENT_PRINCIPLES (P9 gobernanza embebida, P13 contencion) · ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO (referencia inventario externo)

---

## A. Proposito

Define el ciclo de vida obligatorio para **skills externas** (traidas del ecosistema: skills.sh, GitHub, plugin marketplaces, Claude Code, Cowork, Codex). No aplica a skills propias MWT — esas siguen SCH_SKILL.

Sin esta policy, skills externas se instalan ad-hoc sin sandbox, sin pin a version, sin audit de seguridad, sin owner — el riesgo es que una skill ejecute codigo contra la KB o filtre data sensible y nadie sea responsable.

**Distincion critica:**
- **SCH_SKILL** = schema canonico para skills MWT propias (system prompt + memoria sobre KB).
- **POL_AI_GOV_SKILL_INSTALLATION** = governance para skills externas instaladas via `npx skills add`, `claude plugin install`, etc.

---

## B. Definicion de skill externa

Cualquier paquete de instrucciones, scripts o agentes empaquetado por terceros, instalado via uno de estos vectores:

1. `npx skills add <repo>` (skills.sh estandar)
2. `claude plugin install <pkg>` (Claude Code marketplace)
3. `git clone` directo a directorio de skills
4. Plugins Cowork (mcp servers, MCPs, marketplaces)
5. Cualquier otro mecanismo que agregue capabilities sin ser autoria MWT

---

## C. Skill contract obligatorio

Antes de pasar a sandbox, toda skill externa debe tener documento de contrato declarado en `docs/external_skills/<skill_id>.contract.yaml`:

```yaml
skill_contract:
  skill_id:                <ID unico, kebab-case>
  source_repo:             <URL>
  source_commit_pinned:    <SHA o tag — nunca branch movil>
  runtime_supported:       [cowork | claude_code | codex | skills_sh | plugin_marketplace]
  allowed_agents:          [<lista AG-XX o "all">]
  allowed_data_classes:    [N0 | N1 | N2 | N3 | N4]   # subset de POL_DATA_CLASSIFICATION
  required_secrets:        [<env vars o secret refs>]
  capabilities:
    can_execute_code:      true | false
    can_write_files:       true | false
    can_read_files:        true | false
    can_call_external_api: true | false
    api_endpoints_allowed: [<lista o "*">]
  kb_access:
    read_paths:            [<paths permitidos>]
    write_paths:           [<paths permitidos — usualmente []>]
  cost_policy:
    unit:                  usd_per_run
    hard_cap:              <float>
    soft_warn:             <float>
    budget_owner:          <persona o rol>
  conflicts_with:          [<lista de skill_ids que no coexisten>]
  overlap_with_installed:  [<lista de skills ya instaladas que solapan funcionalidad>]
  security_scan:
    snyk:                  pass | warn | fail | not_run
    socket:                pass | warn | fail | not_run
    trust_hub:             pass | warn | fail | not_run
    last_scanned:          <YYYY-MM-DD>
  install_status:          candidate | sandbox | approved | installed | monitored | deprecated | removed
  install_state_changed:   <YYYY-MM-DD>
  owner:                   <persona>
  rollback_command:        <comando exacto de uninstall>
  smoke_test:              <referencia a test que valida que la skill funciona>
```

Skill sin contrato no se instala. Punto.

---

## D. Estados del lifecycle

```
candidate -> sandbox -> approved -> installed -> monitored
                                                     |
                                                     v
                                              deprecated -> removed
```

| Estado | Definicion | Transicion entrante |
|--------|-----------|---------------------|
| **candidate** | Skill identificada como util (ej. en inventario Kimi). Contrato draft, sin scan, sin sandbox. | Decision de evaluar. |
| **sandbox** | Instalada en entorno aislado (no produccion). Smoke test obligatorio. Scan de seguridad ejecutado. | Contrato completo + scan ejecutado. |
| **approved** | Pasa smoke test + scan limpio. Owner asignado. Listo para production install. | CEO autoriza. |
| **installed** | Activa en produccion. Pin a commit fijo. | Comando install ejecutado. |
| **monitored** | Activa con telemetria de outcome (ver POL_AI_GOV_SKILL_OUTCOME futuro). | 30 dias en installed sin incidentes. |
| **deprecated** | Marcada para remocion. Nuevos invocaciones bloqueadas; existentes draenan. | Reemplazo disponible o riesgo detectado. |
| **removed** | Desinstalada. Contrato preservado en archivo para auditoria historica. | Ejecucion de rollback_command verificada. |

---

## E. Reglas inquebrantables

1. **No auto-update.** Skills se pinean a commit/tag fijo. Update requiere nueva entrada en lifecycle (vuelve a sandbox).
2. **No instalar sin contrato.** El contrato es prerequisito, no checklist post-hoc.
3. **No instalar sin scan.** Snyk + Socket + Trust Hub minimo. Resultado registrado.
4. **No instalar sin owner.** Skill huerfana = skill prohibida. Owner es persona, no rol generico.
5. **No instalar si conflicts_with un skill instalado** salvo decision documentada (cual gana, por que).
6. **No instalar bundles monoliticos sin cherry-pick** (ej. NeoLabHQ context-engineering-kit con 133 skills). Cargar 133 descripciones satura context window y mata trigger precision. Si un repo trae skills utiles, se cherry-pickean individualmente.
7. **Skill que pide `can_execute_code: true` solo se aprueba con sandbox propia y review de codigo.** No se confia en la fuente.
8. **Skill con `allowed_data_classes` que excede el tier maximo del agente que la invoca = bloqueo automatico.** Ejemplo: skill que pide N3 invocada por agente que opera N1 → rechazo.
9. **Plugin marketplaces son mecanismo de instalacion, no de governance.** Estar en marketplace oficial no exenta de contrato + scan + sandbox.
10. **Rollback siempre ejecutable.** Si no hay `rollback_command` validado, no hay install.

---

## F. Conflicto con skills instaladas (caso obra/superpowers)

Cuando una skill candidata solapa funcionalidad con una ya instalada (ej. `mattpocock/tdd` vs `obra/superpowers:test-driven-development`), la decision se documenta en el contrato:

```yaml
overlap_with_installed:
  - obra/superpowers:test-driven-development
overlap_decision:
  winner:    obra/superpowers
  reason:    "ya instalada, 921k installs, cubre 80% del use case; mattpocock/tdd se evalua como complemento opcional para cherry-pick por fase"
  reviewed_by: CEO
  reviewed_at: 2026-05-15
```

Anti-patron: instalar ambas y "ver cual gana en uso real". Genera triggers ambiguos, context bloat, y nadie corrige despues.

---

## G. Smoke test minimo

Toda skill en sandbox debe pasar smoke test antes de approved:

1. Instalacion exitosa con el comando declarado.
2. Trigger word activa la skill (no carga ghost).
3. Output basico cumple lo que el contrato declara como capability.
4. Skill no escribe fuera de `kb_access.write_paths`.
5. Skill no llama APIs fuera de `api_endpoints_allowed`.
6. Rollback_command desinstala limpio (sin residuos en filesystem ni env).

Smoke test queda registrado como artefacto reproducible.

---

## H. Owner

Cada skill instalada tiene owner persona. Responsabilidades:
- Monitorear outcome (success rate, edit rate, cost — ver futura POL_AI_GOV_SKILL_OUTCOME).
- Actualizar pin de commit cuando hay fix critico upstream.
- Decidir deprecacion cuando hay reemplazo o quality drift.
- Responder a alertas de scan recurrente (mensual).

Si el owner deja la organizacion o el rol, la skill pasa a `deprecated` hasta reasignacion.

---

## I. Auditoria recurrente

Mensual sobre todas las skills `installed` y `monitored`:

1. Re-scan Snyk + Socket. Si fail nuevo → `deprecated` inmediato.
2. Verificar pin de commit no se movio. Drift = bug critico.
3. Verificar T&C / licencia upstream no cambio. Cambio de licencia (ej. MIT → ELv2) requiere re-aprobacion.
4. Outcome metrics revisadas. Skill con success_rate <60% en 30 dias → review.

---

## J. Skills MWT propias estan FUERA de scope

Las skills propias MWT (system prompts con memoria sobre KB, formato `SKILL_*.md` segun SCH_SKILL) NO siguen este lifecycle. Tienen su propio governance en SCH_SKILL.

Esta policy aplica a lo que **viene de afuera**.

---

Changelog:
- v1.0 (2026-05-01): Creacion. Lifecycle 7 estados. Skill contract obligatorio. 10 reglas inquebrantables. Distincion vs SCH_SKILL (skills propias). Origen: sesion AI_GOV 2026-05-01 + inventario Kimi 2026-05-01 (213 skills externas evaluadas).
