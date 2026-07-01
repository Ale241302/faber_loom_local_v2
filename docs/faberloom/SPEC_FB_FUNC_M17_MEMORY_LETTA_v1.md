# SPEC_FB_FUNC_M17_MEMORY_LETTA_v1 -- Ficha Funcional Stack de Memoria de Agentes (Letta)
id: SPEC_FB_FUNC_M17_MEMORY_LETTA_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md - SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1.md - SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1.md - POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1.md

---

## CABECERA DE FICHA

MODULO: Stack de memoria de agentes (Letta -- episodic/working/persistent)
SUPERFICIE: Backend (transversal a la ejecucion de agentes)
SPRINT E1: S3 (memoria de agentes)
ROLES QUE LO USAN: Tecnico/agentes; Owner/Curator (gate de promocion a persistent)
DATA CLASS TIPICA: N2 (contexto de caso en memoria); hereda del caso

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Un agente sin memoria repite preguntas, pierde contexto entre pasos de una task y
no acumula conocimiento util. Pero una memoria sin control puede contradecir la KB
VIGENTE y envenenar las respuestas. El stack de 3 capas da contexto util sin
sacrificar la autoridad de la KB ni el aislamiento por tenant.

### 1.2 A quien le duele
Operator: sufre agentes que "olvidan" el contexto de la conversacion. Owner/
Curator: deben controlar que memoria se vuelve permanente. Tecnico: responde por
el aislamiento y la coherencia memoria-vs-KB.

### 1.3 Cuando aparece
Durante la ejecucion de cualquier agente: lee working/episodic para contexto y,
si aplica, propone persistir aprendizaje.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Dar a cada agente memoria por capas (episodic inmutable, working efimera,
persistent con gate) sin que la memoria contradiga la KB VIGENTE.

### 2.2 Que valor entrega
Contexto util por task; trazabilidad de lo que el agente "sabe"; control humano
sobre lo que se vuelve permanente; aislamiento por tenant y por agente.

### 2.3 Que pasa si no existe
Agentes amnesicos (mala UX, mas costo por re-contexto) o, peor, memoria sin
control que contradice la KB y produce outputs erroneos con apariencia de autoridad.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
Por agente se crean 3 capas:
1. Episodic: registro inmutable de eventos/interacciones (append-only, triggers +
   app role sin UPDATE/DELETE).
2. Working: contexto de la task en curso. Namespace:
   mem:agent:{agent_id}:task:{task_id}:working. TTL 24h.
3. Persistent: conocimiento estable del agente; solo se escribe con gate humano.
Los namespaces son per-tenant y per-agente (M16/Letta profile separado).

### 3.2 Quien puede crearlo
El sistema crea episodic/working durante la ejecucion. La promocion a persistent
requiere gate humano obligatorio (Owner/Curator).

### 3.3 Que necesita para crearse
Agente en ejecucion; task_id (working); Letta profile del tenant; para persistent,
aprobacion humana + chequeo contra KB.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente: al ejecutar, el agente lee working (su task) y episodic (historia
relevante), y consulta KB. Si detecta aprendizaje candidato, lo propone a
persistent (no lo escribe solo).

### 4.2 Como se invoca
Automatico en el prompt assembly del agente: se inyecta working + episodic +
KB VIGENTE, pasando por el MemoryConflictGuard (ver 8/12).

### 4.3 Que ve el usuario mientras ocurre
Nada directo en operacion. En modo Owner/debug: que memoria uso el agente y si
hubo un conflicto memoria-vs-KB (memoria marcada disputed).

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Episodic: no se edita (inmutable). Working: se actualiza durante la task; se
limpia al terminar. Persistent: se edita solo via gate humano (agregar/deprecar
un item de memoria persistente).

### 5.2 Que se puede cambiar y que no
Editable: working (durante la task), persistent (con gate). No editable: episodic
(inmutable, append-only).

### 5.3 Que pasa con lo generado previamente
Al terminar la task, working se limpia (cleanup) y un sweeper barre los stale. La
memoria persistent previa se conserva salvo deprecacion explicita. Si una memoria
contradice la KB VIGENTE, se marca disputed y no se inyecta.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
Ciclo de un item de memoria:
```
working (creado en task) -- trigger: task termina, actor: system --> cleaned (TTL 24h / cleanup)
working -- trigger: candidato a persistir, actor: agente --> proposed_persistent
proposed_persistent -- trigger: gate humano aprueba, actor: Owner/Curator --> persistent
proposed_persistent -- trigger: gate humano rechaza --> discarded
persistent -- trigger: contradice KB VIGENTE, actor: MemoryConflictGuard --> disputed (no se inyecta)
persistent -- trigger: deprecacion humana --> deprecated
(episodic: append-only, sin transiciones de edicion)
```

### 6.2 Que dispara el movimiento
Fin de task (cleanup working); propuesta de persistir; gate humano; deteccion de
conflicto por el guard; deprecacion.

### 6.3 Quien puede moverlo
system/sweeper: cleanup working. agente: propone persistir. Owner/Curator: aprueba/
rechaza/depreca persistent. MemoryConflictGuard: marca disputed.

### 6.4 Que se notifica y a quien
Propuesta de memoria persistent: a la cola del Curator. Conflicto memoria-vs-KB:
nota al Curator (memoria disputed). Sweeper de stale: log tecnico.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Agentes con contexto (mejor continuidad, menos repreguntas); en modo Owner,
visibilidad de la memoria usada y de conflictos.

### 7.2 Que produce para el sistema
Registros episodic (append-only); working en Letta con TTL; persistent gated;
marca disputed cuando hay conflicto; audit D10 de cada promocion a persistent.

### 7.3 Donde aparece el output
Letta (namespaces por tenant/agente); prompt assembly del agente; tab de memoria
en el panel de agente (Owner/debug); audit log.

### 7.4 Que formato tiene
Items de memoria (JSON con scope, capa, timestamp, estado); namespaces
mem:agent:{agent_id}:task:{task_id}:working; persistent con metadata de aprobacion.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Memoria contradice KB VIGENTE: MemoryConflictGuard la marca disputed y NO la
inyecta en el prompt (la KB VIGENTE gana siempre). Working no se limpia (fuga de
contexto entre tasks): el sweeper de stale lo barre por TTL. Intento de editar
episodic: falla por trigger/app role. Cross-profile (memoria de un agente/tenant
en otro): bloqueado por namespace estricto (M16); intento = P0.

### 8.2 Como se recupera
Conflicto: el agente usa la KB; el Curator revisa la memoria disputed y la depreca
o la corrige. Working stale: sweeper. Cross-profile: freeze + investigacion (es un
leak). Persistent erronea: deprecacion humana.

### 8.3 Quien se entera
Curator/Owner: memorias disputed y propuestas persistent. Tecnico: sweeper,
intentos cross-profile (P0). Langfuse: trazas de memoria usada por ejecucion.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Que memoria resulta util vs ruido; frecuencia de conflictos memoria-vs-KB; cuanto
contexto working se reusa.

### 9.2 Como mejora con el tiempo
La capa persistent crece con conocimiento validado (gate); el guard afina la
deteccion de conflictos; el sweeper ajusta su barrido. La promocion a persistent
es la via por la que un agente "gana" contexto estable (liga con autonomy ladder y
M14).

### 9.3 Que feedback da el usuario
Implicito: el agente repregunta menos cuando la memoria sirve. Explicito: el
Curator aprueba/rechaza memoria persistent y resuelve disputes.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Working: se limpia al terminar la task (TTL 24h + cleanup + sweeper). Episodic: no
se elimina (inmutable, retencion segun politica). Persistent: se depreca (no se
borra) por gate humano.

### 10.2 Que pasa con lo que dependia
Al deprecar una memoria persistent, el agente deja de usarla; los outputs que
genero pueden marcarse para revision (liga con M14). Episodic se conserva como
historia.

### 10.3 Es reversible
Working cleanup: no reversible (era efimero). Persistent deprecada: re-promovible
con nuevo gate. Episodic: inmutable.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M16 (aislamiento Letta por tenant/agente), KB VIGENTE
(POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY), prompt assembly. Alimenta a: ejecucion de
agentes (contexto), M14 (memoria validada liga con aprendizaje), M12 (audit de
promociones).

### 11.2 En que orden
task crea working -> agente lee working+episodic+KB (via MemoryConflictGuard) ->
ejecuta -> propone persistent -> gate humano -> persistent. KB VIGENTE siempre
prevalece sobre memoria.

### 11.3 Que rompe si este modulo falla
Sin memoria, agentes sin contexto (peor UX/costo). Sin el guard, memoria podria
contradecir la KB y producir outputs erroneos con apariencia de autoridad. Sin
aislamiento de namespace, leak cross-tenant de memoria.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Owner/Curator: la memoria del tenant y las disputes. El agente: solo su propio
namespace. Nunca cross-tenant ni cross-profile.

### 12.2 Que queda en el audit trail D10
tenant_id, agent_id, action (memory.persisted / memory.disputed /
memory.deprecated), data_class, human_approver_id (gate), timestamp, sha_chain.
Cada promocion a persistent se audita.

### 12.3 Que restricciones de datos aplican
Episodic inmutable (triggers + app role); working TTL 24h con cleanup; persistent
con gate humano obligatorio; namespace per-tenant/per-agente (M16); regla KB vs
Letta: si contradicen, KB VIGENTE gana, la memoria se marca disputed y NUNCA se
inyecta en el prompt (MemoryConflictGuard en prompt assembly).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend (Letta, transversal a la ejecucion). Web/Desktop: el Owner/Curator ve la
memoria y resuelve disputes/promociones desde el panel de agente.

### 13.2 Diferencias entre desktop y web
La memoria es server-side; ambas superficies solo la visualizan/gestionan via gate.
No hay memoria de agente en el cliente.

### 13.3 Offline y sincronizacion
La memoria vive en backend; offline el agente no ejecuta (no hay memoria local).
La promocion a persistent es server-side y requiere conexion.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1] Confirmar como el
   MemoryConflictGuard decide "contradice KB VIGENTE" (match exacto vs semantico).
2. [PENDIENTE] Definir el TTL/criterio exacto del sweeper de working stale mas alla
   de las 24h.
3. [PENDIENTE -- ENT_FB_CURATOR_OPERATING_MODEL_v1] Confirmar quien ejecuta el gate
   de persistent (Owner, Curator, ambos) y si N2+ exige segundo aprobador como en M14.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. La regla "KB VIGENTE gana sobre memoria"
   es consistente con las reglas inquebrantables del proyecto (status aprobado pesa
   mas; no inventar).

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del stack de memoria
  Letta. 3 capas episodic/working/persistent; namespace working; episodic
  inmutable; gate humano para persistent; MemoryConflictGuard (KB VIGENTE gana).
