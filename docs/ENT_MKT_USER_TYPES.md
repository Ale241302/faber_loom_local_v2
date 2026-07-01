# ENT_MKT_USER_TYPES — User Types Rana Walk
id: ENT_MKT_USER_TYPES
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Marketplace (IDX_MARKETPLACE)
stamp: DRAFT — materializado 2026-04-03
aplica_a: [MWT]

refs:
  - ENT_MKT_ICP (ICP por mercado — complementa con datos demográficos)
  - ENT_PROD_{GOL,VEL,ORB,LEO,BIS,MAN,ORC} (specs técnicos y target)
  - LOC_{PROD}_EN (messaging aprobado)
  - ENT_COMP_CLAIMS (lenguaje compliance-safe)
  - PROMPT_Deep_Research_Insole_Buyer_Search_Mechanics.md (research fuente)

origin: Deep research mecánica de búsqueda de compradores de plantillas + cruce con specs de producto

---

## A. Propósito

Definir user types nombrados y no exclusivos para la línea Rana Walk. Cada tipo representa un perfil de búsqueda/necesidad real del mercado de plantillas. Un mismo comprador puede pertenecer a múltiples tipos. Los tipos se usan en fichas técnicas, listings, A+ Content, y estrategia de targeting.

**Principio:** Los tipos NO son segmentos demográficos — son patrones de búsqueda y necesidad. Derivados del deep research sobre mecánica de búsqueda de compradores de plantillas (4 arquetipos: pain-driven, use-case-driven, feature-driven, brand-aware).

---

## B. Los 9 User Types

### B1. The Aching Worker
**Patrón:** Pain-driven. Busca alivio de fatiga en pies tras jornadas largas de pie.
**Search corridor:** "insoles for standing all day", "best insoles for sore feet", "work boot insoles for pain"
**Lenguaje compliance-safe:** "fatiga" y "discomfort" — nunca "dolor" como claim de producto. Ref → ENT_COMP_CLAIMS.B2.

### B2. The Heavy Loader
**Patrón:** Use-case + feature-driven. 225+ lbs o trabajo de carga pesada. Necesita estructura que no colapse.
**Search corridor:** "insoles for heavy guys", "insoles for 300 lbs", "heavy duty insoles"
**Diferenciador:** Busca promesa de durabilidad bajo peso — no solo amortiguación.

### B3. The All-Day Stander
**Patrón:** Use-case-driven. 8+ horas de pie (retail, hospitalidad, manufactura, salud).
**Search corridor:** "insoles for nurses", "insoles for retail workers", "standing all day insoles"
**Diferenciador:** Prioriza fatiga acumulada, no impacto puntual.

### B4. The Tight-Shoe Problem
**Patrón:** Use-case-driven. Calzado slim, vestir, oficina, tenis casual con poco espacio interno.
**Search corridor:** "thin insoles for dress shoes", "slim insoles", "insoles that fit in any shoe"
**Diferenciador:** Volumen es el problema #1 — rechaza plantillas gruesas aunque sean mejores técnicamente.

### B5. The Arch Seeker
**Patrón:** Feature-driven. Busca soporte de arco específico (bajo, medio, alto). Ya sabe qué necesita.
**Search corridor:** "high arch insoles", "arch support insoles", "insoles for flat feet" (aunque evitamos este término — ref → ENT_COMP_CLAIMS.B1)
**Lenguaje compliance-safe:** "arch support" permitido para GOL, LEO, BIS, MAN. "Low arch support" como alternativa a "flat feet". NO usar "arch support" para ORB (ref → ENT_PROD_ORB.C3).

### B6. The Upgrader
**Patrón:** Feature-driven + brand-aware. Ya usa plantillas genéricas, quiere upgrade con mejor tecnología.
**Search corridor:** "best insoles 2026", "insole upgrade", "premium insoles", "insoles better than Superfeet"
**Diferenciador:** Compara activamente. Receptivo a diferenciación tecnológica (materiales, bi-density, E-TPU).

### B7. The Sticker-Shocked
**Patrón:** Pain-driven + price-sensitive. Quiere calidad sin pagar premium. Sensible al precio.
**Search corridor:** "affordable insoles", "best insoles under $25", "insoles for the price"
**Diferenciador:** Busca valor percibido — no necesariamente el más barato, sino "worth it".

### B8. The Pronator
**Patrón:** Feature-driven. Presión medial alta. Busca estabilización lateral o medial.
**Search corridor:** "insoles for overpronation", "pronation control insoles", "insoles for flat feet that roll inward"
**Lenguaje compliance-safe:** "Estabilización medial" o "soporte medial" preferido sobre "control de pronación". "Pronación severa" PROHIBIDO. Ref → ENT_COMP_CLAIMS.B1/B2.

### B9. The I've-Tried-Everything
**Patrón:** Pain-driven + brand-aware. Probó múltiples soluciones (Superfeet, PowerStep, Dr. Scholl's, custom orthotics). Frustrado. Busca algo diferente.
**Search corridor:** "best insoles that actually work", "insoles better than custom orthotics", "why don't insoles work for me"
**Diferenciador:** Receptivo a storytelling tecnológico. Necesita entender POR QUÉ este producto es diferente. La diferenciación técnica (bi-density, PORON, NanoSpread) es el hook.

---

## C. Matriz de Cruce — User Types × Productos

**Escala:** P = Primario (producto diseñado para este usuario) · S = Secundario (funciona bien, no es target principal) · — = No aplica

| User Type | GOL | VEL | ORB | LEO | BIS | MAN | ORC |
|-----------|-----|-----|-----|-----|-----|-----|-----|
| B1. The Aching Worker | **P** | — | S | S | **P** | S | S |
| B2. The Heavy Loader | **P** | — | — | — | **P** | — | S |
| B3. The All-Day Stander | **P** | S | **P** | S | S | S | S |
| B4. The Tight-Shoe Problem | — | **P** | S | — | — | **P** | — |
| B5. The Arch Seeker | S | — | — | **P** | S | S | **P** |
| B6. The Upgrader | S | **P** | S | **P** | S | S | S |
| B7. The Sticker-Shocked | — | S | **P** | S | — | **P** | — |
| B8. The Pronator | — | — | **P** | — | — | — | **P** |
| B9. The I've-Tried-Everything | **P** | S | S | S | **P** | S | **P** |

---

## D. Lógica de Asignación por Producto

### D1. Goliath (GOL)
**Primario:** B1 (jornada larga + botas trabajo), B2 (225+ lbs, estructura máxima), B3 (8+ horas, 5 tecnologías), B9 (máxima diferenciación tecnológica).
**Secundario:** B5 (tiene Arch System), B6 (upgrade premium).
**Tecnologías clave:** LeapCore + Arch System + PORON XRD + ThinBoom + NanoSpread (5).

### D2. Velox (VEL)
**Primario:** B4 (ultra delgada, calzado slim/vestir/oficina), B6 (reemplaza plantilla de fábrica invisible).
**Secundario:** B3 (oficina), B7 (entry price posible), B9 (ThinBoom full-length diferenciador).
**Tecnologías clave:** ThinBoom (full-length) + NanoSpread. Arco integrado en E-TPU.

### D3. Orbis (ORB)
**Primario:** B3 (alineación postural todo el día), B7 ($18-25 — precio más bajo de la línea), B8 (alineación permanente).
**Secundario:** B1 (reduce fatiga postural), B4 (perfil moderado), B6 (upgrade postural), B9 (propuesta de alineación diferente).
**Tecnologías clave:** LeapCore + NanoSpread (2). NO tiene Arch System — soporte postural por geometría bi-density. Ref → ENT_PROD_ORB.C3.

### D4. Leopard (LEO)
**Primario:** B5 (3 arcos flexibles — LOW/MED/HGH), B6 (personalización por altura de arco).
**Secundario:** B1 (versatilidad trabajo), B3 (adaptable jornada), B7 (mid-range), B9 (ShockSphere diferenciador).
**Tecnologías clave:** LeapCore + ShockSphere + NanoSpread. 3 arcos flexibles. 18 SKUs.

### D5. Bison (BIS)
**Primario:** B1 (PORON absorbe impacto, heavy-duty), B2 (estructura para peso + personalización), B9 (PORON + 3 alturas = máxima customización).
**Secundario:** B3 (soporte prolongado), B5 (arch support), B6 (upgrade significativo).
**Tecnologías clave:** LeapCore + PORON XRD + NanoSpread. 18 SKUs (3 alturas).

### D6. Manta (MAN)
**Primario:** B4 (low profile — calzado trabajo slim, sneakers), B7 (EVA = precio accesible).
**Secundario:** B1 (PORON en talón/antepié), B3 (soporte prolongado), B5 (Arch System EVA rígido), B6 (upgrade en calzado slim), B9 (PORON en perfil bajo = diferenciador).
**Tecnologías clave:** LeapCore (EVA bi-density) + Arch System (EVA rígido) + PORON XRD + NanoSpread.

### D7. Orca (ORC)
**Primario:** B5 (estabilización fuerte), B8 (Orca Tail = estabilizador lateral), B9 (tecnología exclusiva 7ª de la línea).
**Secundario:** B1 (protección impacto), B2 (estructura PU para peso), B3 (soporte prolongado), B6 (upgrade estabilización).
**Tecnologías clave:** LeapCore (PU bi-density) + Orca Tail + PORON XRD + NanoSpread. NO ThinBoom, NO Arch System, NO ShockSphere.

---

## E. Notas de Uso

1. **No exclusividad:** Un comprador puede ser B1 + B8 (Aching Worker que también prona). La matriz C refleja esto — el mismo tipo aparece como primario en múltiples productos.
2. **Compliance:** Todo copy derivado de estos tipos debe pasar por ENT_COMP_CLAIMS antes de publicación. En particular, B8 (Pronator) requiere cuidado especial con terminología.
3. **Evolución:** La Comparativa (ENT_PROD_COMPARATIVA) solo tiene ratings para GOL/VEL/ORB/LEO/BIS. MAN y ORC están [PENDIENTE]. Cuando se completen, validar que la matriz C sea consistente con los ratings.
4. **Search corridors:** Derivados del deep research. Deben alimentar ENT_MKT_KEYWORDS cuando se actualice.

---

Changelog:
- v1.0 (2026-04-03): Creación. 9 user types nombrados, matriz 9×7 no exclusiva, lógica de asignación por producto, compliance cross-refs. Fuente: deep research mecánica de búsqueda + datos canónicos ENT_PROD_* + correcciones CEO (ORB sin Arch System).
