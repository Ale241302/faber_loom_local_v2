---
id: ENT_FB_VERTICAL_CANDIDATES_v2
version: 2.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: DRAFT 2026-06-15 - re-ranking por casos de uso - NO implementacion
fecha: 2026-06-15
agente: Claude (Cowork) - Arquitecto Ejecutor
aplica_a: [FaberLoom]
supersede: ENT_FB_VERTICAL_CANDIDATES_v1 (solo la SECCION DE RANKING; las fichas legales/tecnicas de v1 siguen vigentes como referencia)
status_motivo: |
  v1 rankeo verticales por encaje al modelo de plataforma (adapter pattern) y puso
  legal_practice + software_factory en ALTA. Este v2 re-evalua el MISMO set pero por
  ENCAJE A LOS CASOS DE USO REALES de FaberLoom (cotizar/cobrar/seguir/resumir/gobernar
  conocimiento) + derecho a ganar de MWT. Resultado: cambia el ganador.
  NO implementa nada. NO compromete el plan v4. Insumo de la decision de 2do vertical post-MWT.
relacionado_con:
  - ENT_FB_VERTICAL_CANDIDATES_v1 (fichas por vertical, vigentes)
  - PLAN_DESARROLLO_FABERLOOM_v4 (E2.5 valida con design partners)
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1.1 (adapter pattern)
---

# ENT_FB_VERTICAL_CANDIDATES_v2
## Re-ranking de verticales SaaS por encaje a casos de uso

## 1. Por que un v2

v1 respondia "que vertical encaja en el modelo de plataforma". Pregunta incompleta. La pregunta que decide el 2do cliente es: **en que industria los casos de uso que FaberLoom YA hace disparan con volumen, y donde MWT tiene derecho a ganar.** v1 saltaba a servicios profesionales (legal, software) sin medir eso. v2 lo mide.

## 2. Los casos de uso de FaberLoom (los "usos")

| | Uso | Definicion | Estado en plan v4 |
|---|---|---|---|
| U1 | Spec-to-Quote | RFQ tecnico -> cotizacion con precio 100% trazado a lista | core E1b/E2 |
| U2 | Cobranza | seguimiento de AR / facturas vencidas (interna; terceros post-dictamen) | E2 (skill 2) |
| U3 | Seguimiento | account management proactivo, recordatorios, reposicion | E2/E3 |
| U4 | Resumen de cuenta | brief de estado por cliente | E2 |
| U5 | Gobernanza de conocimiento | retencion del saber institucional, templates gobernados, memoria por cliente | transversal (el moat) |

## 3. Metodologia de scoring (explicita, para que el ranking sea auditable)

Criterios, peso, escala 1-5:

| Criterio | Peso | Que mide |
|---|---|---|
| C1 Densidad de uso | 30% | cuantos de U1-U5 disparan con VOLUMEN recurrente en la industria |
| C2 Derecho a ganar MWT | 25% | proximidad al saber vivido de MWT + acceso a design partners reales |
| C3 Drag regulatorio (inverso) | 15% | a menor carga legal, mayor score (velocidad a piloto) |
| C4 Claridad de wedge | 10% | se puede cortar un MVP angosto y embarcable |
| C5 WTP / poder de precio | 10% | disposicion y capacidad de pago |
| C6 Defensibilidad competitiva | 10% | margen vs incumbentes con IA (Harvey, Copilot, etc.) |

Score = suma(peso x nota). Es mi evaluacion, no dato operativo; las notas son discutibles y estan para hacerse explicitas, no para esconder el juicio.

## 4. Matriz de encaje uso x industria

Leyenda: 3 = dispara fuerte y con volumen / 2 = parcial / 1 = marginal / 0 = no aplica.

| Industria | U1 Quote | U2 Cobranza | U3 Seguim | U4 Resumen | U5 Conoc | Densidad |
|---|---|---|---|---|---|---|
| Distribucion B2B tecnica (EPP, dielectrica, ferreteria ind., autopartes, mat. construccion) | 3 | 3 | 3 | 2 | 3 | 14/15 |
| safety_footwear (MWT = tenant 0) | 3 | 3 | 3 | 2 | 3 | 14/15 (probada) |
| legal_practice | 0 | 3 | 2 | 3 | 3 | 11/15 |
| insurance | 1 | 2 | 2 | 3 | 3 | 11/15 |
| financial_advisory | 1 | 2 | 2 | 3 | 3 | 11/15 |
| software_factory | 1 | 2 | 2 | 2 | 3 | 10/15 |
| medical_regulated | 0 | 2 | 1 | 3 | 3 | 9/15 |

Lectura: la densidad alta no esta en servicios profesionales; esta en **distribucion B2B tecnica**, que tiene exactamente el mismo perfil de uso que MWT porque ES el mismo tipo de negocio.

## 5. Ranking ponderado

| # | Vertical | C1 | C2 | C3 | C4 | C5 | C6 | Score |
|---|---|---|---|---|---|---|---|---|
| **1** | **Distribucion B2B tecnica** | 5 | 5 | 5 | 5 | 3 | 4 | **4.70** |
| 2 | software_factory | 2 | 2 | 3 | 3 | 3 | 2 | 2.35 |
| 3 | legal_practice | 3 | 1 | 1 | 3 | 5 | 2 | 2.30 |
| 4 | insurance | 3 | 1 | 1 | 2 | 4 | 3 | 2.20 |
| 4 | financial_advisory | 3 | 1 | 1 | 2 | 4 | 3 | 2.20 |
| 6 | medical_regulated | 2 | 1 | 1 | 1 | 4 | 3 | 1.80 |

El ganador no esta cerca: 4.70 vs 2.35. v1 ponia 2 y 3 (software, legal) en ALTA; por casos de uso son empate mediocre.

## 6. Ficha del ganador: Distribucion B2B tecnica

```yaml
vertical_id: b2b_technical_distribution
parent_industry: industrial_distribution
status: candidate_lead_v2
ejemplos: distribuidores de EPP, material dielectrico, ferreteria industrial,
          autopartes, materiales de construccion, equipo de seguridad ocupacional
unidad_de_trabajo: RFQ / cotizacion / orden / cuenta de cliente
multi_cliente_per_tenant: SI (cada distribuidor atiende decenas de clientes B2B)
canal_dominante: WhatsApp (!!) + email + telefono   # ver seccion 7, tension critica
dolor_central: responder RFQs tecnicos rapido sin equivocar precio/SKU, y cobrar a tiempo
por_que_MWT_gana:
  - MWT ES un distribuidor tecnico B2B (calzado de seguridad) -> conoce el dolor de primera mano
  - el dataset E0 de MWT (RFQs Marluvas/Tecmater) es representativo del vertical
  - acceso a design partners reales y NO competidores: distribuidores de dielectrica,
    EPP, ferreteria que MWT ya conoce en su red CR/GT/CO (Sondel y similares)
competencia_IA: practicamente nula y fragmentada (nadie ataca al distribuidor PYME LATAM)
diferenciador: precio 100% trazado a lista + HITL + memoria por cliente; "no manda precios mal"
```

### Casos de uso concretos (los "casos" que faltaban)

1. **U1 Quote.** Llega RFQ por correo: "200 pares bota dielectrica T2 + 50 guantes arc-flash, entrega Alajuela DDP". FaberLoom arma draft de cotizacion con SKU y precio trazados a la lista vigente del distribuidor, marca lo asumido (curva de tallas) en ambar; el dueno aprueba y envia. Hoy eso le toma 20-40 min manual.
2. **U2 Cobranza.** Factura F-1102 a 31 dias vencida; FaberLoom redacta recordatorio con tono segun historial del cliente (suave si paga bien), el dueno aprueba. Interna primero; a terceros solo post-dictamen.
3. **U3 Seguimiento.** Cliente que compra botas cada ~90 dias y va por el dia 85: FaberLoom propone draft de reposicion proactiva.
4. **U4 Resumen.** "Pasame el estado de Sondel": brief de ordenes abiertas, AR, ultima cotizacion, proximas reposiciones.
5. **U5 Conocimiento.** La nomenclatura de tokens Marluvas y las reglas de precio dejan de vivir en la cabeza del dueno; cada cotizacion aprobada se vuelve gold sample que mejora la siguiente.

## 7. Tension critica que ningun ranking previo miro: el canal

El vertical de mayor encaje **opera por WhatsApp**, no por email. El plan v4 hace E1/E2 **email-first** y difiere WhatsApp Business API a E3/E4 (tramite Meta largo). Choque directo: el cliente ideal vive en el canal que el plan posterga.

Tres salidas (decision de Alvaro, no la invento):
- (a) Elegir design partners de E2.5 que SI manejen RFQ por correo (los hay: licitaciones, clientes corporativos, gobierno) y dejar WhatsApp para despues.
- (b) Adelantar WhatsApp Business API a E2 solo para este vertical, asumiendo el riesgo de tramite.
- (c) Ingesta WhatsApp via puente no-oficial para piloto (riesgo de ToS) - **no recomendado**.

Recomendacion: **(a) para validar, (b) planificado para escalar.** No bloquear E2.5 esperando WhatsApp; validar con los que ya usan correo.
`transfer_basis` y dictamen de cobranza (del plan v4) aplican igual a este vertical.

## 8. Recomendacion directa

El 2do vertical de FaberLoom **no es legal ni software factory**. Es **distribucion B2B tecnica adyacente a calzado de seguridad**. Razon: es la unica industria donde los cinco usos disparan a la vez Y MWT ya tiene el conocimiento, el dataset y los clientes. Legal y software te obligan a reaprender el dolor desde cero y pelear contra incumbentes financiados.

Implicacion operativa para el plan v4:
- E0: el dataset de 30 casos ya es de este vertical (RFQs Marluvas/Tecmater). Sirve doble: valida MWT y prototipa el vertical.
- E2.5: los 10 prospectos NO deben ser "PYMEs B2B genericas"; deben ser **distribuidores tecnicos** (EPP, dielectrica, ferreteria, autopartes) que coticen por correo. Mismo vertical = el aprendizaje compone.
- E4b: el primer design partner pago sale de esa lista, no de un bufete.

## 9. [PENDIENTE - NO INVENTAR / decision o dato]

- Volumen real de RFQs/semana que hace rentable a un distribuidor PYME suscriptor: [PENDIENTE - medir en E2.5].
- WTP real del distribuidor PYME a USD 39-50/mes: [PENDIENTE - medir antes de anclar, E2.5].
- Lista concreta de 10 distribuidores tecnicos design-partner (no competidores de MWT): [PENDIENTE - CEO].
- Decision de canal (a/b/c seccion 7): [PENDIENTE - CEO].

## 10. Changelog

- v2.0 (2026-06-15): re-ranking por casos de uso. Distribucion B2B tecnica pasa a lead (4.70);
  legal/software degradados de ALTA a empate medio. Matriz uso x industria + metodologia explicita +
  ficha del ganador con casos concretos + tension de canal WhatsApp. Supersede solo la seccion de
  ranking de v1; fichas de v1 siguen como referencia. No toca FROZEN. No crea SPEC.
