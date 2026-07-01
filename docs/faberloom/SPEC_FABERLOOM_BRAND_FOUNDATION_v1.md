| id | FAB-BRD-2026 |
| version | 1.0.0 |
| status | DRAFT |
| visibility | INTERNAL |
| domain | faberloom |

# SPEC_FABERLOOM_BRAND_FOUNDATION_v1.md

## Resumen ejecutivo integrado

FaberLoom es la comunicacion de proyectos para equipos que hacen. La marca se construye sobre cuatro pilares que se refuerzan mutuamente: un isotipo de **hilos entrelazados** (24/30) que materializa el acto de tejer en una forma memorable y animable; un stack tipografico de **Crimson Pro Italic + Inter + IBM Plex Mono** que combina la calma editorial del oficio con la precision funcional de la interfaz; cinco personas arquetipicas del **hacedor moderno** que validan cada decision de diseno y definen 16 JTBD maestros ranqueados por frecuencia x criticalidad; y un sistema de **referencias visuales** (15 positivas, 12 anti-referencias) que confirma la direccion "calmo profesional craft" y delimita lo que FaberLoom nunca debe ser. Juntos, estos cuatro documentos definen una marca que respeta el oficio del profesional creativo sin sacrificar la eficiencia tecnica — la IA prepara, vos tejes.

---

## 1. Decision de isotipo canon

**Decision tomada:** Hilos entrelazados (24/30 puntos)
**Confidence:** ALTO

El isotipo de FaberLoom es el momento visual donde el manifiesto se vuelve forma. Tras evaluar tres opciones bajo seis criterios cuantificables, **Hilos entrelazados** emerge como la opcion canon por su asociacion semantica perfecta con el acto de tejer (5/5) y su capacidad de transformarse en un progress indicator que materializa "la IA prepara, vos tejes".

### Tabla comparativa

| Criterio | Trama (20/30) | Hilos entrelazados (24/30) | Nudo celtico moderno (20/30) |
|---|---|---|---|
| Reconocimiento a 16/24/32px | 2 | 3 | 4 |
| Asociacion semantica | 4 | **5** | 3 |
| Reproducibilidad | 5 | 4 | 5 |
| Escalabilidad como progress indicator | 4 | **5** | 3 |
| Originalidad vs saturacion de mercado | 2 | 3 | 2 |
| Coherencia con wordmark | 3 | **4** | 3 |

### Por que hilos entrelazados gano

- **Asociacion semantica 5/5:** Las lineas que se cruzan evocan el proceso de tejer, no solo el producto final. "La IA prepara, vos tejes" se vuelve visible.
- **Progress indicator 5/5:** Hilos que se deslizan y entrelazan progresivamente es la animacion mas alineada con la identidad de marca. Ciclo recomendado: 1.2s, easing `cubic-bezier(0.4, 0, 0.2, 1)`.
- **Coherencia con wordmark 4/5:** Las curvas dinamicas dialogan con la fluidez de Crimson Pro Italic en "Faber" y contrastan con la solidez de Inter Bold en "Loom", formando un triangulo compositivo.

### 3 variantes de aplicacion

| Variante | Descripcion | Uso principal |
|----------|-------------|---------------|
| **A. Monocromo** | Ink sobre cream / cream sobre ink. Entrelazado por gaps en cruces. Stroke 2px @32px, 1.5px @24px, 1px @16px. | Favicon, impresion, contexts 1-color |
| **B. Color** | Coral #C96442 sobre cream. Opcion bicolor: un hilo coral, otro pizarra #5A6B7C, alternando cruces. | App icon, branding principal, splash screen |
| **C. Dark mode** | Cream sobre ink, coral como acento puntual (20% del trazado). 80% cream / 20% coral. | OLED, dark mode editorial, proyeccion |

### Notas tecnicas clave para ingenieria

- **SVG:** viewBox `0 0 32 32`, dos paths cubicos bezier con gaps calculados en intersecciones. `stroke-linecap: round` obligatorio.
- **Favicon multi-res:** `.ico` con 16x16 (simplificado a "X" suavizada), 24x24, 32x32 + `apple-touch-icon.png` 180x180.
- **Animacion:** `stroke-dashoffset` con dos variantes de velocidad — 0.8s para micro-loading (botones, tabs), 1.2s para macro-loading (pantallas completas).
- **Accesibilidad:** Respetar `prefers-reduced-motion: reduce` → isotipo estatico.

### Prohibiciones explicitas

1. NO gradientes (lineales ni radiales)
2. NO sombras, glows, dropshadows
3. NO version 3D/extrusionada
4. NO animacion de "girar" u "orbitar"
5. NO cambiar el angulo de entrelazado por capricho
6. NO usar como contenedor de otros iconos

---

## 2. Stack tipografico final

**Decision tomada:** Crimson Pro (display) + Inter (UI) + IBM Plex Mono (datos)
**Confidence:** ALTO para Crimson Pro e Inter; MEDIO-ALTO para IBM Plex Mono

La tipografia de FaberLoom es un sistema de tres voces: la serif para la calma editorial del oficio, la sans para la precision funcional de la interfaz, y la mono para la transparencia tecnica de los datos.

### Las 3 fuentes

| Fuente | Rol | Weights | Variable | Payload | Confidence |
|--------|-----|---------|----------|---------|------------|
| **Crimson Pro** | Display / Headline / Body editorial | 400, 500, 600 (normal + italic) | Si (`wght` 200-900) | ~40 KB | ALTO |
| **Inter** | UI / Interface / Body funcional | 400, 500, 600, 700 (normal + italic) | Si (`wght` + `opsz`) | ~32 KB | ALTO |
| **IBM Plex Mono** | Datos / Codigo / Logs | 400, 500 (normal + italic) | No (via GF) | ~55 KB | MEDIO-ALTO |

### Tabla de uso por contexto

| Contexto | Fuente | Weight | Size | Line-height | Letter-spacing |
|----------|--------|--------|------|-------------|----------------|
| **H1 hero** | Crimson Pro | 600 | 48-64px | 1.1 | -0.02em |
| **H2 section** | Crimson Pro | 500 | 32-40px | 1.2 | -0.01em |
| **H3 card title** | Crimson Pro | 500 | 24px | 1.3 | 0 |
| **Body editorial** | Crimson Pro | 400 | 16-18px | 1.65 | 0 |
| **Body funcional** | Inter | 400 | 14-16px | 1.5 | 0 |
| **Button primary** | Inter | 600 | 14px | 1 | 0.01em |
| **Tab** | Inter | 500 | 14px | 1 | 0.02em |
| **Tab active** | Inter | 600 | 14px | 1 | 0.02em |
| **Table header** | Inter | 600 | 12px | 1.2 | 0.03em |
| **Table cell (mono)** | IBM Plex Mono | 400 | 13px | 1.4 | 0 |
| **Code block / Log** | IBM Plex Mono | 400 | 13px | 1.6 | 0 |
| **Timestamp** | IBM Plex Mono | 500 | 11-12px | 1.3 | 0.02em |
| **Empty state** | Crimson Pro | 400 italic | 18px | 1.5 | 0 |
| **Wordmark** | Crimson Pro | 500 italic | — | 1 | 0 |

### Estrategia de carga

| Prioridad | Fuente | Weight | Subset | `font-display` |
|-----------|--------|--------|--------|----------------|
| 1 (critical) | Crimson Pro | 500 italic | latin, latin-ext | `swap` |
| 2 (critical) | Inter | 400-700 roman | latin, latin-ext | `swap` |
| 3 (deferred) | Crimson Pro | 400, 600 | latin-ext | `swap` |
| 4 (on-demand) | IBM Plex Mono | 400, 500 | latin, latin-ext | `optional` |

### Decisiones irreversibles

| # | Decision | Costo de reversion |
|---|----------|-------------------|
| 1 | **Crimson Pro Italic 500 para "Faber"** | MUY ALTO — requiere redisenar logo, favicon, assets, templates |
| 2 | **Inter como unica fuente UI** | MEDIO — afecta todos los componentes y percepcion de densidad |
| 3 | **Inclusion de IBM Plex Mono** | BAJO-MEDIO — cambiar `font-family: mono` por stack de sistema |
| 4 | **Variable fonts via Google Fonts API v2** | BAJO — fallback a estaticos automatico |

---

## 3. Personas y JTBD del hacedor moderno

**Confidence general:** ALTO para P1/P2/P3/P5; MEDIO-ALTO para P4

El hacedor moderno es un profesional de alto rendimiento cuyo valor economico descansa en **combinar juicio experto con ejecucion tecnica**. Produce entregables tangibles para clientes exigentes, trabaja en equipos pequenos, ha invertido anos desarrollando un oficio, y necesita herramientas que amplifien su capacidad sin reemplazar su juicio.

> **Dato clave:** El 70% de los profesionales creativos ocultan su uso de AI por estigma profesional. Los disenadores especificamente muestran el patron emocional mas problematico: alta frustracion con baja satisfaccion.

### Las 5 personas

| # | Nombre | Rol | Dolor central | Deseo central |
|---|--------|-----|---------------|---------------|
| **P1** | Diana Crespo | Directora Creativa, agencia boutique (4-12p) | Que la AI "aplane" el trabajo creativo | Un equipo hibrido humano-AI donde el AI hace produccion y el humano concepcion |
| **P2** | Sergio Vasquez | Lead Designer, estudio producto digital (3-8p) | Diseno "genericamente aceptable" que nadie ame | Un "intern digital" que maneje la mecanica mientras el hace sistema e interacciones |
| **P3** | Camila Renau | Socia Consultora, consultora boutique (2-6p) | Perder horas en tareas de produccion no facturables | Un "equipo de investigacion virtual" que entregue borradores estructurados |
| **P4** | Tomas Weber | Lead Maker, taller fabricacion digital (2-5p) | Errores costosos por desconexion digital-fisico | Sistema que documente cada proyecto para reproducibilidad y mejora |
| **P5** | Valentina Rojas | Freelancer Senior, independiente (1p) | Fragmentacion de herramientas que consume mas tiempo que ahorra | Un "socio digital" que maneje lo operativo mientras ella crea |

### Principios derivados de las personas

| Principio | Fuente | Implicacion en FaberLoom |
|-----------|--------|-------------------------|
| **Control visible > velocidad oculta** | P1, P2 | El Trust Ladder debe ser explicito en cada interaccion |
| **La AI debe "mostrar su trabajo"** | P3, P4 | Toda accion del agente incluye: que hizo, por que, y que requiere validacion humana |
| **Contexto multi-proyecto = tabla de salvacion** | P3, P5 | Arquitectura multi-tenant con aislamiento perfecto de contexto |
| **Calidad = lo que NO hay que rehacer** | P2, P4 | El modulo Sanidad no es opcional; es garantia de estandares |
| **AI disuelta > AI presentada** | P1, P2 | Capacidades integradas al flujo, no "ser" que ayuda |
| **Memoria de estilo = diferenciador** | P1, P2, P3 | Aprender y recordar el estilo de cada tenant, no genericamente |

### JTBD maestros ranqueados (top 10)

| ID | Job statement | Frec x Crit | Personas | Estado FaberLoom |
|----|---------------|-------------|----------|-----------------|
| JTBD-01 | Sintetizar requerimientos dispersos en estructura clara con acciones priorizadas | 25 | P1-P5 | Parcial |
| JTBD-02 | Preparar borrador estructurado basado en mi estilo, para refinar en lugar de empezar de cero | 25 | P1, P2, P3, P5 | Parcial |
| JTBD-03 | Mantener contexto de cada proyecto sin mezclar informacion | 25 | P1, P3, P5 | **No cubierto** |
| JTBD-04 | Verificar consistencia contra criterios de calidad y estilo | 25 | P1, P2 | Parcial |
| JTBD-05 | Generar adaptaciones de pieza maestra para cada formato/canal | 20 | P1, P2, P3, P5 | Parcial |
| JTBD-06 | Organizar investigacion en temas accionables con citas | 20 | P1, P3, P5 | Parcial |
| JTBD-07 | Estructurar propuestas basadas en conversaciones previas | 20 | P3, P5, P4 | **No cubierto** |
| JTBD-10 | Verificar outputs tecnicos antes de produccion (escalas, formatos) | 20 | P4, P2 | **No cubierto** |
| JTBD-11 | Garantizar aislamiento multi-tenant sin mezcla ni filtracion | 25 | P1, P3, P5 | **Cubierto** |
| JTBD-08 | Sintetizar feedback de multiples stakeholders con deteccion de contradicciones | 15 | P1, P2, P3 | **No cubierto** |

**Estado del portafolio:** 7 de 16 JTBD cubiertos o parcialmente cubiertos. 9 de 16 son oportunidades de roadmap. Los 5 JTBD de mayor score representan el 37% de la carga total — el nucleo duro de prioridad.

### Anti-patterns a evitar (validados por personas)

1. **El "Magico Black Box"** — Output sin explicacion destruye confianza (P1, P2, P3)
2. **El "Intern Sobresaliente"** — Sobre-autonomia que toma decisiones del usuario (P1, P2)
3. **El "Chatbot Generico"** — Output que "suena a AI" sin memoria de estilo (P1, P2, P3, P5)
4. **El "Mezclador de Contextos"** — Cross-contamination entre proyectos o clientes (P3: "Un solo leak y mi consultora termina")
5. **El "Todologo Inutil"** — Amplio pero superficial, 50 opciones genericas en lugar de 3 especificas (P4, P5)

---

## 4. Referencias visuales documentadas

**Total:** 15 referencias positivas + 12 anti-referencias + 22 screenshots capturados

### Referencias principales (top 5)

| # | Referencia | Que valida para FaberLoom | Score promedio |
|---|------------|--------------------------|----------------|
| 1 | **Linear** | "Calmo profesional" no es aburrido. Densidad controlada, Inter + serif editorial, voz directa sin adjetivos | 5/5 |
| 2 | **Resend** | Cuando la tipografia es perfecta, se necesita menos de todo lo demas. Serif hero / sans body es magistral | 5/5 |
| 3 | **Vercel** | Dashboard denso y precision tecnica. Confianza con metricas reales, no copy emocional | 4/5 |
| 4 | **Framer** | Muestra el producto, no lo describe. Grid de previews como patron aplicable a proyectos/hilos | 4/5 |
| 5 | **Raycast** | CLI elegante, shortcuts visibles, precision tipografica. "Calmo" describe sensacion, no velocidad | 5/5 |

### Resumen de validaciones por dimension

| Dimension | Referencias que validan | Conclusion |
|-----------|------------------------|------------|
| **Paleta cream/coral/ink** | Linear (ink casi identico), Tella (coral sobre oscuro valida la combinacion), Raycast (grises calidos) | La restriccion cromatica 1+1 (coral + pizarra) es estandar en SaaS de alta calidad |
| **Tipografia serif + sans** | Linear, Notion, Resend, Framer, Pylon | La combinacion es validada por multiples referencias; el italico de Crimson Pro es el diferenciador unico |
| **Layout sidebar + main** | Linear, Notion, Plain, Attio | Patron establecido y esperado por el target |
| **Microinteracciones ~150ms** | Linear, Raycast, Framer, Vercel | Rapido y tranquilo al mismo tiempo |
| **Voice directo sin superlativos** | Linear, Resend, Render, Plain | Verbo activo, sin emoji, sin exclamaciones, respeto al oficio |

### Anti-referencias: lo que FaberLoom NUNCA debe ser

| Anti-referencia | Violacion principal | Leccion para FaberLoom |
|-----------------|---------------------|------------------------|
| **Canva** | Consumer-y en contexto profesional. Colorido excesivo, template-heavy | Restriccion cromatica = elegancia. El usuario es creador, no consumidor de templates |
| **ClickUp** | Feature overload, copy hype ("400% more done"), UI abrumadora | Especializacion > generalidad. Restriccion es feature, no limitacion |
| **Monday** | Gamificacion excesiva, colores saturados tipo "candy crush" | Color es informacion, no decoracion. Maximo 3-4 colores de estado, todos mutados |
| **Asana** | Celebraciones intrusivas (unicornios, confetti), tono paternalista | Nunca celebrar tareas con animaciones. Un checkmark sutil es suficiente |
| **HubSpot** | Marketing-loud: CTAs multiples, popups, chatbot intrusivo | Un CTA por vista. Nunca popups interruptivos. El producto habla por si mismo |
| **Salesforce** | Jerga corporativa ("Customer 360", "Agentforce"), complejidad heredada | Nombres descriptivos, no de marca. "Hilos de comunicacion", no "ThreadForge" |
| **Jira** | Caos visual, falta de jerarquia, configuracion infinita | Buenos defaults ahorran tiempo. La opinion es un feature |
| **Loom** | Gradients saturados, hero generico sobre gradiente | Nunca gradients de dos colores distintos. Fondo cream solido con producto real |

### Principios derivados de las referencias

1. **La restriccion es distincion** — 1-2 colores de acento maximo (Linear, Resend, Plain)
2. **La tipografia es identidad** — Inter + Crimson Pro Italic no tiene equivalente directo
3. **La densidad es respeto** — Mucha informacion sin abrumar (Linear)
4. **El producto habla por si mismo** — La mejor landing es el producto visible (Framer, Resend)
5. **El calmo no es lento** — Microinteracciones rapidas (~150ms), shortcuts, command palette (Raycast, Cursor)

---

## 5. Coherencia entre decisiones

Esta seccion explicita como las 4 areas de decision se refuerzan mutuamente. No son 4 silos independientes — son 4 caras del mismo dado.

### Isotipo + Tipografia: el sistema visual integrado

Los hilos entrelazados no flotan solos. Sus curvas dinamicas dialogan con la fluidez caligrafica de **Crimson Pro Italic** ("Faber") y contrastan con la solidez geometrica de **Inter Bold** ("Loom"). Esto crea un triangulo compositivo: serif + sans + isotipo, donde cada elemento enriquece a los otros. El isotipo nunca se usa sin el wordmark en los primeros 6 touchpoints — el reconocimiento se construye con exposicion repetida, no por shock visual.

**Validacion cruzada:** La tabla comparativa del isotipo muestra que Hilos entrelazados es la unica opcion que dialoga con el wordmark (4/5 vs 3/5 de Trama y Nudo). Si el wordmark fuera sans-serif puro, el Nudo celtico ganaria. Pero "Faber" en serif italic hace que los hilos sean la unica opcion coherente.

### Tipografia + Personas: la voz que el hacedor necesita escuchar

Las 5 personas tienen una caracteristica comun: **odian que las herramientas "griten"**. Diana (P1) rechaza el tokenismo de AI. Sergio (P2) valora la precision sobre la velocidad. Camila (P3) quiere resultados, no tecnologia por tecnologia. Tomas (P4) valida en el mundo fisico antes de confiar. Valentina (P5) abandona rapido si no hay ROI claro.

El stack tipografico responde a esto:
- **Crimson Pro** en body editorial (400, 1.65 line-height) = la calma que necesitan para leer documentacion larga sin fatiga
- **Inter** en UI (400-700, `opsz` 14-32) = la precision que Sergio exige en tablas y handoff
- **IBM Plex Mono** en logs (400, `tnum`) = la transparencia que Camila necesita para confiar en datos

### Personas + Isotipo: la metafora que valida el producto

El acto de "tejer" no es una metafora abstracta — es el JTBD-02 en accion: "preparar un borrador estructurado para que yo refinar en lugar de empezar de cero". Cuando Diana elige una direccion creativa de entre tres opciones preparadas por el agente, esta **tejiendo**: la IA preparo los hilos (las opciones), ella cruzo los hilos (la decision). El isotipo de hilos entrelazados es la visualizacion de ese momento.

El progress indicator animado (hilos que se entrelazan en 1.2s) materializa el mantra "la IA prepara, vos tejes" en un momento de espera que de otro modo seria frustrante. Valentina (P5), que mide el exito por "tareas administrativas <8h/semana", no tiene paciencia para loaders genericos. Un loader que refuerza el proposito del producto transforma la espera en recordatorio de marca.

### Referencias + Tipografia: la validacion externa

Las 15 referencias positivas confirman que la direccion tipografica es correcta:
- **Linear** usa Inter para UI + serif para editorial — exactamente la estrategia de FaberLoom
- **Resend** demuestra que serif display grande + sans body = memorable y funcional
- **Notion** valida la combinacion sans UI + serif contenido
- Ninguna referencia usa italico sistematicamente — ese es el diferenciador silencioso de FaberLoom

### Referencias + Personas: el benchmark de confianza

Las personas definen el "calmo profesional craft" y las referencias lo validan:
- Diana (Directora Creativa) encuentra en **Linear** el modelo de densidad controlada que respeta su criterio
- Sergio (Lead Designer) encuentra en **Raycast** la precision tecnica que espera de una herramienta seria
- Camila (Consultora) encuentra en **Plain** la simplicidad que no subestima su inteligencia
- Tomas (Lead Maker) encuentra en **Vercel** las metricas reales que validan decisiones tecnicas
- Valentina (Freelancer) encuentra en **Resend** la restriccion que distingue sin gritar

Las anti-referencias (Canva, ClickUp, Monday, Asana) representan todo lo que las 5 personas odian: infantilizacion, hype, ruido visual, paternalismo.

### Isotipo + Referencias: el territorio visual propio

De las 15 referencias, **ninguna usa hilos entrelazados**. Linear usa un icono geometrico abstracto. Vercel usa triangulos. Resend usa un cubo 3D. Framer usa una "f" estilizada. El territorio visual de "hilos que se tejen" esta disponible. La unica aproximacion es el branding textil tradicional — que el spec de isotipo explicitamente evita mediante curvas controladas, angulo geometrico, y grosor uniforme (no fibras, no deshilachado).

**Tella.tv** valida sorpresentemente que coral sobre fondo oscuro funciona, lo que refuerza la variante dark mode del isotipo. **Raycast** demuestra que grises calidos en dark mode evitan frialdad tecnica.

---

## 6. Timeline de decisiones

| Fecha | Decision | Status | Proximo paso |
|-------|----------|--------|--------------|
| 2026-01-10 | Paleta de color canon (cream #F4F1ED, ink #1F1E1C, coral #C96442, pizarra #5A6B7C) | **DECIDIDO** | Documentar en tokens DTCG |
| 2026-01-12 | Wordmark dual: "Faber" en Crimson Pro Italic 500 + "Loom" en Inter Bold 700 | **DECIDIDO** | Vectorizar y exportar assets |
| 2026-01-13 | Isotipo canon: Hilos entrelazados (24/30) | **DECIDIDO** | Disenar SVG base, variantes monocromo/color/dark, animacion de progress indicator |
| 2026-01-14 | Stack tipografico: Crimson Pro + Inter + IBM Plex Mono | **DECIDIDO** | Implementar carga con Google Fonts API v2, definir tokens DTCG |
| 2026-01-15 | 5 personas arquetipicas + 16 JTBD maestros | **DECIDIDO** | Validar con entrevistas de usuario reales |
| 2026-01-15 | 15 referencias positivas + 12 anti-referencias documentadas | **DECIDIDO** | Extraer assets visuales para moodboard interno |
| 2026-01-15 | Consolidacion de fundacion de marca (este documento) | **EN PROCESO** | Revision cruzada entre Brand, Producto y UX |
| 2026-01-20 | **Pendiente:** Tokens DTCG de color, tipografia y espaciado | PENDIENTE | Esperando design tokens v1 |
| 2026-01-25 | **Pendiente:** Componentes UI (botones, tabs, badges) con estilos aplicados | PENDIENTE | Esperando spec de componentes |
| 2026-01-30 | **Pendiente:** Landing page con hero, isotipo animado, copy de marca | PENDIENTE | Esperando wireframes de alta fidelidad |
| 2026-02-05 | **Pendiente:** Sistema de ilustracion/empty states (line art, 1 color) | PENDIENTE | Agendar exploracion con ilustrador |
| 2026-02-10 | **Pendiente:** Motion system completo (transiciones de pagina, microinteracciones, loaders) | PENDIENTE | Definir libreria de animacion (Framer Motion / CSS) |
| 2026-02-15 | **Pendiente:** Voz y tono de producto (error messages, empty states, onboarding) | PENDIENTE | Escribir guia de voz con ejemplos |

---

## 7. Glosario de marca FaberLoom

| Termino | Definicion |
|---------|------------|
| **FaberLoom** | Del latin *faber* (artesano, hacedor) + *loom* (telar). El telar del hacedor moderno. Producto: comunicacion de proyectos para equipos creativos. |
| **Hacedor moderno** | Profesional creativo/de conocimiento que combina juicio experto con ejecucion tecnica. Produce entregables tangibles, trabaja en equipos pequenos, mide exito por calidad no por velocidad. No es operador industrial, no-code citizen developer, ni early adopter desconsiderado. |
| **Telar** | Metafora central del producto. El lugar donde los hilos se cruzan para formar tejido. Analogo al espacio de trabajo donde la IA prepara y el humano decide. |
| **Tejedor** | El usuario activo de FaberLoom. La persona que cruza los hilos, toma las decisiones, da forma al producto final. La IA prepara; el tejedor teje. |
| **Hilo** | Unidad de comunicacion en FaberLoom. Un hilo de conversacion, de trabajo, de decision. Los hilos se entrelazan para formar el tejido del proyecto. |
| **Tejido** | El resultado final: un proyecto comunicado con claridad, donde las decisiones, acciones y entregables forman un patron coherente. |
| **Trust Ladder** | Modelo de autonomia progresiva del agente AI. 4 niveles: observe → approval-required → category-autonomous → fully autonomous. El usuario sube de nivel confirmando, no por tiempo transcurrido. |
| **Coral (#C96442)** | Color driver de la marca. Unico acento calido sobre fondo cream. Representa la accion humana en el sistema: el momento donde el tejedor decide. No es decorativo; es funcional. |
| **Cream (#F4F1ED)** | Fondo principal. Calido sin ser amarillo, limpio sin ser frio como el blanco puro. El "lienzo" donde el tejedor trabaja. |
| **Ink (#1F1E1C)** | Texto principal. Casi negro pero con calidez. El trazo permanente del oficio. |
| **Pizarra (#5A6B7C)** | Color secundario para estados, informacion secundaria, dark mode alternativo. Gris azulado que evoca la pizarra del taller. |
| **La IA prepara, vos tejes** | Mantra del producto. La IA hace el trabajo de preparacion (investigacion, estructuracion, borradores); el humano hace el trabajo de tejido (decisiones, refinamiento, criterio). No es "la IA hace, vos revisas". Es una relacion de apoyo, no de reemplazo. |
| **Sanidad (tab)** | Modulo de QA/verificacion que revisa entregables contra los criterios de calidad y estilo del tenant. No es opcional; es garantia. Sin Sanidad, Iterar es riesgoso. |
| **Iterar (tab)** | Modulo de trabajo donde el agente prepara borradores estructurados que el usuario refina. El espacio donde ocurre el tejido activo. |
| **Configurar (tab)** | Modulo de setup donde se captura el estilo, los criterios de calidad, y el nivel del Trust Ladder. El telar se configura antes de tejer. |
| **Multi-tenant** | Arquitectura donde cada cliente (tenant) tiene datos, contexto y estilo aislados. El agente nunca mezcla informacion entre tenants. La confidencialidad no es negociable. |
| **Memoria de estilo** | Capacidad del agente para aprender y recordar las preferencias, criterios y voz de cada tenant. No generica, no cross-tenant. El diferenciador core frente a ChatGPT. |
| **Anti-job** | Tarea que el usuario explicitamente NO quiere que el agente haga. Mas importante que los jobs positivos para definir guardarrailes. Ejemplos: generar ideas finales sin aprobacion, comunicarse con clientes, hacer commitments de plazo. |
| **Craft** | Calidad del oficio. Atencion al detalle, precision, criterio estetico. Lo que diferencia al hacedor moderno de un operador. FaberLoom respeta el craft en cada decision de diseno. |
| **Densidad controlada** | Principio de layout: mucha informacion, cero clutter. Cada elemento tiene exactamente el espacio que necesita. Aprendido de Linear. Compatible con calma. |
| **Restriccion como distincion** | Principio de marca: menos colores, menos palabras, menos animaciones = mas memorable. La restriccion cromatica (1 acento + 1 secundario) es elegancia, no limitacion. |

---

## Apendice: Archivos relacionados

| # | Archivo | Ruta | Contenido |
|---|---------|------|-----------|
| 1 | Decision de isotipo (spec completo) | `/mnt/agents/output/docs/faberloom/SPEC_FABERLOOM_ISOTIPO_DECISION_v1.md` | Tabla comparativa completa, analisis por isotipo, 3 variantes de aplicacion, notas de implementacion SVG, riesgos y mitigaciones, prohibiciones explicitas |
| 2 | Stack tipografico (spec completo) | `/mnt/agents/output/docs/faberloom/SPEC_FABERLOOM_TYPOGRAPHY_v1.md` | Justificacion de 3 fuentes, tabla de uso por contexto, evaluacion comparativa de 11 fuentes auditadas, tabla de eliminacion, estrategia de carga, DTCG mapping JSON, decisiones irreversibles |
| 3 | Personas y JTBD (spec completo) | `/mnt/agents/output/docs/faberloom/SPEC_FABERLOOM_PERSONAS_JTBD_v1.md` | Definicion del hacedor moderno, 5 personas con perfiles psicograficos completos, tech stacks, jobs principales, anti-jobs, metricas de exito, JTBD maestros ranqueados (16), principios derivados, anti-patterns, matriz de priorizacion para roadmap |
| 4 | Referencias visuales (spec completo) | `/mnt/agents/output/docs/faberloom/SPEC_FABERLOOM_VISUAL_REFERENCES_v1.md` | 15 referencias positivas con analisis por 5 dimensiones (paleta, tipografia, layout, microinteracciones, voice), 12 anti-referencias con lecciones, moodboard sintetizado (paleta, tipografia, layout patterns, microinteracciones craft, voice de copy), 22 screenshots capturados |
| 5 | **Fundacion de marca (este documento)** | `/mnt/agents/output/docs/faberloom/SPEC_FABERLOOM_BRAND_FOUNDATION_v1.md` | Sintesis integrada de los 4 specs anteriores con coherencia entre decisiones, timeline y glosario |

---

*Documento consolidado de fundacion de marca FaberLoom. Punto de entrada para cualquier persona o agente que necesite entender la marca.*
*Tono: CR, sin formalidades, directo.*
*Confidence general: ALTO — las 4 decisiones consolidadas tienen alta confianza individual y se refuerzan mutuamente.*
