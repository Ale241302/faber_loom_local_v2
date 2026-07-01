---
id: AUDIT_SPACELOOM_ETAPA1_STRESS_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: audit
stamp: DRAFT 2026-06-17 - prueba de estres del diseno Etapa 1 contra los casos reales del catalogo
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
fuente: ENT_FB_USE_CASE_CATALOG_v1 + ENT_FB_VERTICAL_CANDIDATES_v2 (60 clusters verificados)
prueba_contra: SPEC_SPACELOOM_ETAPA1_v1 + v1.1/v1.2/v1.3 + IMAP_CONNECTOR_v1
---

# AUDIT_SPACELOOM_ETAPA1_STRESS_v1
## Prueba de estres: los casos reales contra el diseno de Etapa 1

## 1. Metodo
Tomar casos concretos del catalogo (no inventados) y correrlos mentalmente por el diseno single-user
self-embedded (entidad + rutinas + workspaces + KB FTS5 + HITL + IMAP + sellado). Por cada uno: aguanta /
strain / rompe, y el hallazgo. Casos elegidos para PROBAR limites, no para confirmar.

## 2. Casos x dimension de estres

| Dim de estres | Caso | Veredicto | Que pasa |
|---|---|---|---|
| Volumen / throughput | C17 lab (500 resultados/dia), C48 ecommerce (500 ordenes/dia), C04 medico (20-25/dia) | **ROMPE (HITL)** | SQLite/cola/costo aguantan; lo que NO aguanta es HITL-en-todo: nadie aprueba 500 items/dia a mano. |
| Grounding de precios | C41/C52 distribucion (RFQ -> cotizacion "0 precios inventados") | **STRAIN/ROMPE** | FTS5 es keyword; una query parafraseada no matchea la fila de precio -> el gate "100% trazado" falla. El deferral de embeddings choca con el requisito duro. |
| Ruteo correo -> workspace | C16/C13 RFQ entrante a un buzon que atiende varios clientes | **STRAIN** | El IMAP_CONNECTOR mapea cuenta->workspace. Un buzon real mezcla clientes; el mapeo es muy grueso. |
| NEVER + deadline | C18 AML/SAR (plazo legal), C10 penal (plazo procesal) | **aguanta (vs status quo)** | Si la maquina esta apagada no corre -- pero sin la app tampoco se resolvia. La app nunca deja peor que no tenerla. Regla: NO prometer ejecucion autonoma a hora fija; SI avisar al abrir lo que esta por vencer. |
| Prompt injection + proactividad | C04 mensaje de paciente, C16 RFQ con instruccion embebida | **STRAIN** | El contenido se trata como dato (bien), pero a volumen + draft proactivo, el humano hace rubber-stamp y el dato envenenado (precio mal) pasa el HITL. |
| Cross-workspace legitimo | C26 RRHH (politica del padre + datos de empleado de otro scope) | **STRAIN** | El sellado por defecto obliga a abrir la llave a mano -> friccion; el usuario la desactiva "para que funcione". |
| Cold-start + frecuencia | C39 forense (3/sem), C42 pension (5/sem) | **ROMPE (moat)** | Baja frecuencia: el gold loop nunca acumula suficiente para mejorar. El moat no calienta. |
| Reuso de rutina | C02 dental / C07 psico / C23 fisio (todos "nota clinica por paciente") | aguanta | Una rutina "nota_clinica" + KB por workspace generaliza. Bajo estres. |

## 3. Hallazgos transversales (los profundos)

**H1 (CORREGIDO por Alvaro) - La alta frecuencia es el OBJETIVO, no el problema.** La version original de
este hallazgo decia "frecuencia media es el sweet spot". Era un falso dilema y se descarta. Lo correcto:
las tareas de alto volumen son (a) donde el humano YA esta ahogado -> donde MAS se necesita la app, y
(b) donde MAS aprende. Que "no se pueda aprobar 500 a mano" no descalifica el alto volumen: solo cambia
COMO se revisa (de aprobar-cada-uno a revisar muestra + excepciones que la app marca). Conclusion:
**apuntar a alta frecuencia**, con revision graduada (ver H2). Es ahi donde coinciden maxima necesidad y
maximo aprendizaje.

**H2 - "HITL obligatorio en todo" no sobrevive el volumen real.** Necesita niveles segun riesgo x volumen:
- HITL pleno (alto riesgo / baja freq): aprobar cada uno.
- Batch-approve (medio): aprobar en lote con vista de excepciones.
- Auto + spot-check (alto volumen / bajo riesgo): auto-procesa, el humano audita una muestra.
El spec actual (HITL siempre) rompe en C17/C48.

**H3 - Cualquier dato EXACTO se saca de la fuente, no se "busca".** (Generalizado: no es solo de precios;
cotizar fue solo el ejemplo.) Para todo dato que debe ser exacto -- saldo, fecha, numero de parte, precio,
SKU, condicion -- la app lo toma de la fuente exacta (lookup deterministico, Tier-0), no leyendo texto con
FTS/embeddings. Separar "datos exactos" (deterministico, 100%) de "prosa" (FTS/embeddings, aprox). El dato
exacto es una consulta directa, no una busqueda.

**H4 - El correo real mezcla clientes.** Ruteo debe ser POR MENSAJE (clasificar -> asignar workspace), no
por cuenta. El IMAP_CONNECTOR necesita una capa de triage mensaje->workspace.

**H5 (CORREGIDO por Alvaro) - Deadlines: no es problema de FaberLoom.** El baseline es el usuario sin la
app: si la maquina esta apagada, sin app tampoco se resolvia. La app nunca deja peor que no tenerla. Por
lo tanto los casos con plazo NO se excluyen. Unica regla: no PROMETER ejecucion autonoma a hora fija
(no la puede garantizar apagada). Feature positivo en su lugar: avisar apenas el usuario abre lo que esta
por vencer ("tenes esto que vence manana").

## 4. Correcciones de arquitectura propuestas a Etapa 1

1. **HITL graduado por (riesgo x volumen):** pleno / batch / auto+spot-check. Reemplaza "HITL siempre". (toca v1.1 sec 7 y el modelo de routine_run).
2. **Tier-0 deterministico para datos duros:** precios/SKU/condiciones via lookup a tabla, no retrieval. Gate de precios = 100% por join, no por FTS. (toca v1.1 KB + el gate de grounding).
3. **Triage mensaje->workspace en el IMAP_CONNECTOR:** clasificar y asignar por mensaje, no por cuenta. (toca IMAP_CONNECTOR_v1 sec 5).
4. **Priorizar ALTA frecuencia** para el dogfood y las rutinas semilla (mas necesidad + mas aprendizaje), con revision graduada (fix 1) para que el volumen sea manejable. (toca la priorizacion, no el codigo). [corregido: antes decia "frecuencia media", era falso dilema].
5. **Deadlines: no excluir.** Solo no prometer ejecucion autonoma a hora fija; agregar aviso-al-abrir de lo que esta por vencer. La app nunca deja peor que sin app. (toca expectativas, no alcance).
6. **Anti rubber-stamp:** resaltar campos asumidos/no-trazados y bloquear auto-draft de remitentes desconocidos. (refuerza v1.2 + IMAP).

## 5. Veredicto

El diseno sirve mejor para **alta frecuencia + revision graduada** (es donde mas se necesita y mas
aprende), con dos reglas firmes: la revision cambia de modo segun volumen (cada-uno -> muestra+excepciones),
y todo dato exacto sale de la fuente, no se busca. Nada queda realmente "fuera": la app nunca deja al
usuario peor que sin ella (incluso en plazos con la maquina apagada). Los 6 fixes hacen robusto el diseno;
ninguno lo invalida.

## 6. Changelog
- v1.0 (2026-06-17): prueba de estres del diseno Etapa 1 contra 8 casos reales del catalogo en 7 dimensiones. 5 hallazgos transversales (tension de frecuencia, HITL no escala, FTS vs precios, ruteo por mensaje, deadlines+local). 6 correcciones propuestas. DRAFT. No toca FROZEN.
