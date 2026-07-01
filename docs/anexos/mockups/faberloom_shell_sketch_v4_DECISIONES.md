# Shell sketch v4 - Nota de decisiones (2026-06-11)

Acompana a `faberloom_shell_sketch_v4.html`. Estas 8 decisiones ENMIENDAN el
shell consolidated snapshot v2 (2026-05-07) donde contradigan. Origen: iteracion
Cowork 2026-06-10/11 sobre patrones de Claude Desktop + correcciones CEO.

| # | Decision | Enmienda al canon |
|---|---|---|
| D1 | **3 modos como segmented switcher**: Operar / Aprendizaje / Administrar. El rail muestra solo lo del modo activo; sidebar nunca scrollea | Reemplaza los headers de seccion apilados de §6 |
| D2 | **SpaceLoom es OPERAR, no "pensar"**: banco de trabajo general cross-workspace (itera, resuelve, asigna, promueve). Es el home al abrir la app. La tipologia "Iteracion/donde se PIENSA" de §4 pasa a ser propiedad de superficie, no categoria de navegacion | Corrige §4 y §12 |
| D3 | **Aprendizaje como modo propio**: la cola epistemica unificada - candidatos a indexar, conflictos de fuente, promociones L4->L2, sugerencias de la regla de promocion del router, ajustes few-shot de voz. Patron unico: sistema propone con evidencia, humano cura (3 botones). StackLoom sale de Admin. El reloj del topbar abre aqui. Simetria: Mesa = cola operativa (horas), Aprendizaje = cola epistemica (dias); no se mezclan | Nuevo; absorbe StackLoom de §6 |
| D4 | **Cejas en el chrome**: toggles de panel como iconos espejo FIJOS en extremos del topbar (no dentro del panel ni en el logo). Atajos [ y ]. Estado recordado por superficie | Precisa §5 |
| D5 | **Colapsado = resumen de una linea, nunca invisible**: acordeones del Rail 3 cuyo header trabaja cerrado ("Ledger - ahorro 34%", "Mesa - 3 esperando - 1 critico"). Rail 3 a 46px = mini-iconos con badges | Extiende §9 |
| D6 | **Modo focus**: doble click en cualquier ceja (o tecla F) colapsa ambos rails; repetir restaura | Nuevo |
| D7 | **Workspace hereda la anatomia completa de SpaceLoom** scoped: conversaciones propias (chips), sugerencias de la cuenta, CTA indexar con default L3 directo, composer con @ws fijado | Implementa la tabla de §12 que el sketch v1-v3 omitia |
| D8 | **El workspace es un LENTE, no otra pantalla**: toda superficie (Inbox, Mesa, Chat, KB, Aprendizaje) se construye UNA vez y recibe scope tenant\|workspace_id. Los tabs del workspace son las superficies globales filtradas (Bandeja=Inbox scoped, Iteracion=Chat scoped, KB=Conocimiento scoped). PROHIBIDO construir pantallas especificas de workspace. El scope se aplica en query server-side (workspace_id + membresia), nunca solo en UI | Reduce las 15 superficies del blueprint a 5 componentes parametrizados |

Regla de oro emergente (D1+D3): el switcher de modos ES el core loop del producto
hecho navegacion - "operas con la IA, la IA aprende de como operas, vos curas lo
que aprende". Operar alimenta Aprendizaje; Aprendizaje mejora Operar.

Pendientes del sketch (no decisiones, deuda de mock): Rail 2 contextual, detalle
de item de Mesa con 3 tabs + modal del porque, resize handles, theme claro.
