// FaberLoom icon system — 24×24 grid, stroke 1.75, line-art, currentColor.
// Two families: standard UI (Lucide-style, redrawn for cohesion) + 8 custom
// brand icons that carry the trama / oficio DNA.

const ICON_VB = 24;
const ICON_SW = 1.75;

// Wrapper. `coral` slot lets icons drop a single accent shape in the brand
// color while the main strokes stay currentColor.
function I({ children, size = 24, sw = ICON_SW, color = 'currentColor', title, style, ...rest }) {
  return (
    <svg width={size} height={size} viewBox={`0 0 ${ICON_VB} ${ICON_VB}`} fill="none"
         stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"
         role={title ? 'img' : 'presentation'}
         aria-label={title} style={style} {...rest}>
      {title && <title>{title}</title>}
      {children}
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════════
//  STANDARD UI ICONS — Lucide-style, redrawn at 24×24 with stroke 1.75
// ════════════════════════════════════════════════════════════════════

// — Navigation —
const IconSearch       = (p)=> <I {...p}><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.6-4.6"/></I>;
const IconPlus         = (p)=> <I {...p}><path d="M12 5v14M5 12h14"/></I>;
const IconX            = (p)=> <I {...p}><path d="M6 6 18 18M18 6 6 18"/></I>;
const IconChevronDown  = (p)=> <I {...p}><path d="m6 9 6 6 6-6"/></I>;
const IconChevronLeft  = (p)=> <I {...p}><path d="m15 6-6 6 6 6"/></I>;
const IconChevronRight = (p)=> <I {...p}><path d="m9 6 6 6-6 6"/></I>;
const IconChevronsLeft = (p)=> <I {...p}><path d="m11 6-6 6 6 6M18 6l-6 6 6 6"/></I>;
const IconArrowRight   = (p)=> <I {...p}><path d="M5 12h14M13 6l6 6-6 6"/></I>;
const IconArrowUp      = (p)=> <I {...p}><path d="M12 19V5M6 11l6-6 6 6"/></I>;
const IconPanelLeft    = (p)=> <I {...p}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></I>;
const IconPanelRight   = (p)=> <I {...p}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/></I>;

// — Time & cycle —
const IconHourglass    = (p)=> <I {...p}><path d="M6 4h12M6 20h12M7 4c0 5 5 6 5 8s-5 3-5 8M17 4c0 5-5 6-5 8s5 3 5 8"/></I>;
const IconClock        = (p)=> <I {...p}><circle cx="12" cy="12" r="8"/><path d="M12 8v4l2.5 2"/></I>;
const IconRefreshCw    = (p)=> <I {...p}><path d="M20 6v5h-5"/><path d="M4 18v-5h5"/><path d="M5.5 11A7 7 0 0 1 18 8.5L20 11M4 13l2 2.5A7 7 0 0 0 18.5 13"/></I>;

// — Knowledge / loom —
const IconLayers       = (p)=> <I {...p}><path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/></I>;
const IconLibrary      = (p)=> <I {...p}><path d="M5 4v16M9 4v16"/><rect x="13" y="4" width="3" height="16" rx="0.5"/><path d="m17 6 4 14"/></I>;
const IconBookmark     = (p)=> <I {...p}><path d="M6 4h12v17l-6-4-6 4z"/></I>;
const IconFileText     = (p)=> <I {...p}><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></I>;

// — Communication —
const IconMail         = (p)=> <I {...p}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></I>;
const IconMessage      = (p)=> <I {...p}><path d="M21 15a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2z"/></I>;
const IconInbox        = (p)=> <I {...p}><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z"/></I>;
const IconPaperclip    = (p)=> <I {...p}><path d="m21 11-9 9a5 5 0 0 1-7-7l9-9a3.5 3.5 0 0 1 5 5l-8.5 8.5a2 2 0 0 1-3-3l8-8"/></I>;

// — Status / signals —
const IconCheck        = (p)=> <I {...p}><path d="M5 12.5 10 17.5 19.5 8"/></I>;
const IconAlertCircle  = (p)=> <I {...p}><circle cx="12" cy="12" r="8.5"/><path d="M12 8v4M12 16v.01"/></I>;
const IconAlertTriangle= (p)=> <I {...p}><path d="m12 4 9.5 16.5h-19z"/><path d="M12 11v4M12 18v.01"/></I>;
const IconSparkles     = (p)=> <I {...p}><path d="M12 4 13.5 9 18 10.5 13.5 12 12 17 10.5 12 6 10.5 10.5 9z"/><path d="M19 4v3M21 5.5h-3M5 17v3M6.5 18.5h-3"/></I>;
const IconPin          = (p)=> <I {...p}><path d="M16.5 3 21 7.5l-4 2-4 5 2 4-1.5 1.5-9-9L6 9.5l4 2 5-4z"/><path d="m9 15-5 5"/></I>;
const IconCircle       = (p)=> <I {...p}><circle cx="12" cy="12" r="8"/></I>;
const IconCircleFill   = (p)=> <I {...p}><circle cx="12" cy="12" r="6.5" fill="currentColor"/></I>;

// — Person / role —
const IconUser         = (p)=> <I {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></I>;
const IconUsers        = (p)=> <I {...p}><circle cx="9" cy="8" r="3.5"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21 20a6 6 0 0 0-4-5.65"/></I>;
const IconUserCircle   = (p)=> <I {...p}><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="3"/><path d="M6 18.5A6 6 0 0 1 18 18.5"/></I>;

// — Settings / tools —
const IconSettings     = (p)=> <I {...p}><circle cx="12" cy="12" r="2.8"/><path d="M19.4 14.5a7.5 7.5 0 0 0 0-5l1.7-1.3-1.6-2.7-2 .8a7.5 7.5 0 0 0-4.3-2.5l-.3-2.1H10l-.3 2.1a7.5 7.5 0 0 0-4.3 2.5l-2-.8L1.8 8.2l1.7 1.3a7.5 7.5 0 0 0 0 5l-1.7 1.3 1.6 2.7 2-.8a7.5 7.5 0 0 0 4.3 2.5l.3 2.1H14l.3-2.1a7.5 7.5 0 0 0 4.3-2.5l2 .8 1.6-2.7z"/></I>;
const IconSliders      = (p)=> <I {...p}><path d="M3 6h13M3 12h7M3 18h11"/><circle cx="18" cy="6" r="2"/><circle cx="13" cy="12" r="2"/><circle cx="17" cy="18" r="2"/></I>;
const IconEdit         = (p)=> <I {...p}><path d="M12 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-6"/><path d="m17 3 4 4-9.5 9.5H8v-3.5z"/></I>;
const IconLogOut       = (p)=> <I {...p}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H10"/></I>;
const IconExternalLink = (p)=> <I {...p}><path d="M14 4h6v6"/><path d="M11 13 20 4M19 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6"/></I>;
const IconTrash        = (p)=> <I {...p}><path d="M4 7h16M9 7V4h6v3M6 7l1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13M10 11v7M14 11v7"/></I>;

// ════════════════════════════════════════════════════════════════════
//  CUSTOM BRAND ICONS — carry the trama / oficio DNA
//  Each one is grounded in: woven threads, deliberate stitches,
//  a single human anchor point. NO chat-bubbles, NO clock-faces,
//  NO layered-paper stacks.
// ════════════════════════════════════════════════════════════════════

// 1 · Brand · Loom — the trama itself, distilled to 24×24
const IconBrandLoom = (p) => (
  <I {...p}>
    <path d="M7 4v16M12 4v16M17 4v16"/>
    <path d="M4 9c2 1.5 3 1.5 5 0s3-1.5 5 0 3 1.5 5 0"/>
    <path d="M4 15c2 1.5 3 1.5 5 0s3-1.5 5 0 3 1.5 5 0"/>
  </I>
);

// 2 · Tu criterio (HITL) — a single deliberate stitch tied with a knot.
//      Two crossing threads meeting at a small filled point: the human
//      anchor. Reads as «esto fue tejido a mano» — not a check, not a thumb.
const IconCriterio = (p) => (
  <I {...p}>
    <path d="M1.5 11c1.5-3 3.5-4.5 6-4.5s4.5 1.5 6 4.5"/>
    <path d="M1.5 11c1.5 3 3.5 4.5 6 4.5s4.5-1.5 6-4.5"/>
    <circle cx="7.5" cy="11" r="1.7" fill="currentColor" stroke="none"/>
    <path d="m16 12 2.2 2.2L23 9.5"/>
  </I>
);

// 3 · WorkLoom — telar visto desde arriba: marco + tramas cruzadas + nodo
//      activo. La «mesa de control» como bastidor de tejido.
const IconWorkLoom = (p) => (
  <I {...p}>
    <rect x="3.5" y="3.5" width="17" height="17" rx="1.5"/>
    <path d="M9.5 3.5v17M14.5 3.5v17"/>
    <path d="M3.5 9.5h17M3.5 14.5h17"/>
    <circle cx="14.5" cy="9.5" r="1.6" fill="currentColor" stroke="none"/>
  </I>
);

// 4 · SpaceLoom — bocadillo de chat con una línea cosida adentro:
//      el espacio donde el agente y el operator iteran/escriben.
//      Conversación → puntada en curso.
const IconSpaceLoom = (p) => (
  <I {...p}>
    <path d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-7l-4 3v-3H6a2 2 0 0 1-2-2z"/>
    <path d="M7.5 9h9" strokeDasharray="2.2 1.6"/>
  </I>
);

// SpaceLoom · variantes
// 4A · Bubble + línea cosida · iteración / conversación escribiendo.
const IconSpaceLoomA = IconSpaceLoom;

// 4B · Carita de agente entre paréntesis · cálido · conversacional.
const IconSpaceLoomB = (p) => (
  <I {...p}>
    <path d="M5 4c-2.5 4-2.5 12 0 16"/>
    <path d="M19 4c2.5 4 2.5 12 0 16"/>
    <circle cx="12" cy="12" r="4"/>
    <circle cx="10.6" cy="11.5" r="0.75" fill="currentColor" stroke="none"/>
    <circle cx="13.4" cy="11.5" r="0.75" fill="currentColor" stroke="none"/>
  </I>
);

// 4C · Fábrica · taller donde el agente trabaja. Industrioso.
const IconSpaceLoomC = (p) => (
  <I {...p}>
    <path d="M4.5 5h2.5v7"/>
    <path d="M3 20v-8l3.2 2v-2l3.2 2v-2l3.2 2v-2l3.2 2v-2l3.2 2v6z"/>
  </I>
);

// 5 · StackLoom — CANON v2 · variante C: layers + nodo activo. El
//      punto sólido en la capa superior indica «contexto en uso».
const IconStackLoom = (p) => (
  <I {...p}>
    <path d="M12 2 22 7 12 12 2 7z"/>
    <path d="M2 12 12 17 22 12"/>
    <path d="M2 17 12 22 22 17"/>
    <circle cx="12" cy="7" r="1.3" fill="currentColor" stroke="none"/>
  </I>
);

// 6 · Sabor del user (voice) — CANON v2 · variante A: avatar (cabeza
//      + hombros) + onda de voz lateral. Persona explícita + rasgo
//      vocal. NO mic, NO comilla.
const IconVoice = (p) => (
  <I {...p}>
    <circle cx="9" cy="8.5" r="3.5"/>
    <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
    <path d="M16.5 8c1.3 1.2 1.3 4.3 0 5.5"/>
    <path d="M19 5.5c2.3 2 2.3 8.5 0 10.5"/>
  </I>
);

// 7 · Reloj de aprendizaje — CANON v2 · pie de 5 sectores con
//      3 rellenos. Cada sector = 20% del aprendizaje. Las 5 etapas
//      canónicas (0–20, 20–40, 40–60, 60–80, 80–100) en su forma más
//      legible.
const IconLearningClock = (p) => (
  <I {...p}>
    <path d="M12 4 12 12 19.6 9.5A8 8 0 0 0 12 4z" fill="currentColor" stroke="none"/>
    <path d="M12 12 19.6 9.5A8 8 0 0 1 16.7 18.5z" fill="currentColor" stroke="none"/>
    <path d="M12 12 16.7 18.5A8 8 0 0 1 7.3 18.5z" fill="currentColor" stroke="none"/>
    <circle cx="12" cy="12" r="8"/>
    <path d="M12 4v8"/>
    <path d="M12 12 19.6 9.5"/>
    <path d="M12 12 16.7 18.5"/>
    <path d="M12 12 7.3 18.5"/>
    <path d="M12 12 4.4 9.5"/>
  </I>
);

// 8 · Knowledge a indexar — CANON v2 · variante A: bandeja receptora
//      con item descendiendo. Gesto de «guardar al lugar correcto».
const IconKnowledgeIndex = (p) => (
  <I {...p}>
    <path d="M3 14v4.5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V14"/>
    <path d="M3 14h5l1.5 2h5l1.5-2h5"/>
    <path d="M12 3v8"/>
    <path d="m8.5 8 3.5 3.5L15.5 8"/>
  </I>
);

// (9) Curaduría / promoción L4→L1 — flecha cosida ascendente sobre
//     línea base. Acto cuidadoso, no upload genérico.
// Curaduría · destilar — rodillos: 3 hilos crudos entran, los
// rodillos los procesan, sale 1 hilo destilado. ADN del oficio.
const IconCuration = (p) => (
  <I {...p}>
    <path d="M9 2v6"/>
    <path d="M12 2v6"/>
    <path d="M15 2v6"/>
    <circle cx="7.5" cy="11.5" r="3.5"/>
    <circle cx="16.5" cy="11.5" r="3.5"/>
    <circle cx="7.5" cy="11.5" r="0.85" fill="currentColor" stroke="none"/>
    <circle cx="16.5" cy="11.5" r="0.85" fill="currentColor" stroke="none"/>
    <path d="M12 15v7"/>
  </I>
);

// ════════════════════════════════════════════════════════════════════
//  ITERACIÓN v2 · variantes para 5 iconos custom
//  CEO rechazó voice / learning-clock / knowledge-index / curation /
//  criterio. Acá 3 direcciones por icono para que elija.
// ════════════════════════════════════════════════════════════════════

// — 1 · CRITERIO · ojo + herramienta · NO mazo (muy legal)
//   El operator pragmático que ve el draft y tiene sus tools listas.

// 1A · Ojo + toolbox — la dirección sugerida por el CEO. Ver + caja
//      de herramientas listas. «Vi · ejecuto.»
const IconCriterioA = (p) => (
  <I {...p}>
    <path d="M2 8.5c1.8-2.5 3.8-3.5 5.8-3.5s4 1 5.8 3.5"/>
    <path d="M2 8.5c1.8 2.5 3.8 3.5 5.8 3.5s4-1 5.8-3.5"/>
    <circle cx="7.8" cy="8.5" r="1.6" fill="currentColor" stroke="none"/>
    <rect x="13" y="14.5" width="9" height="6.5" rx="0.6"/>
    <path d="M16 14.5v-1.2a1.5 1.5 0 0 1 3 0v1.2"/>
    <path d="M13 17.4h9"/>
  </I>
);

// 1B · Ojo + pluma estilográfica — revisión + decisión escrita.
//      Más editorial, premium. «Vi · firmo con mi criterio.»
const IconCriterioB = (p) => (
  <I {...p}>
    <path d="M2 9.5c1.8-2.5 3.8-3.5 5.8-3.5s4 1 5.8 3.5"/>
    <path d="M2 9.5c1.8 2.5 3.8 3.5 5.8 3.5s4-1 5.8-3.5"/>
    <circle cx="7.8" cy="9.5" r="1.5" fill="currentColor" stroke="none"/>
    <path d="m13.5 21 7-7"/>
    <path d="m18 11.5 3 3-1.4 1.4-3-3z"/>
    <path d="m13.5 21-1-2.4 1.4-1.4z" fill="currentColor" stroke="none"/>
  </I>
);

// 1C · Ojo + sello/stamp — revisión + decisión sellada. Oficial pero
//      sin teatralidad legal del mazo. «Vi · sello mi aprobación.»
const IconCriterioC = (p) => (
  <I {...p}>
    <path d="M2 9c1.8-2.5 3.8-3.5 5.8-3.5s4 1 5.8 3.5"/>
    <path d="M2 9c1.8 2.5 3.8 3.5 5.8 3.5s4-1 5.8-3.5"/>
    <circle cx="7.8" cy="9" r="1.5" fill="currentColor" stroke="none"/>
    <path d="M14 16h8"/>
    <path d="M15 16v-2.5a3 3 0 0 1 6 0V16"/>
    <path d="M16.5 13.5v-2.5a1.5 1.5 0 0 1 3 0v2.5"/>
    <path d="M13.5 19h9"/>
  </I>
);

// — 2 · CURATION · destilar / promover — quedarse con lo esencial

// 2A · Embudo + gota de esencia · destilación pura. Muchos entran
//      arriba, lo destilado sale como gota.
const IconCurationA = (p) => (
  <I {...p}>
    <path d="M3 4h18l-7 9v6.5l-4 1.5v-8z"/>
    <path d="M12 21.5v-2"/>
    <circle cx="12" cy="22.2" r="0.9" fill="currentColor" stroke="none"/>
  </I>
);

// 2B · Inbox-arrow-down + lente con check al lado · combo literal
//      de los dos referentes: depositar revisado.
const IconCurationB = (p) => (
  <I {...p}>
    <path d="M3 14v4.5a1.5 1.5 0 0 0 1.5 1.5h7a1.5 1.5 0 0 0 1.5-1.5V14"/>
    <path d="M3 14h2.5L7 16h2l1.5-2H13"/>
    <path d="M8 4v6"/>
    <path d="m5.5 8 2.5 2.5L10.5 8"/>
    <circle cx="18" cy="9" r="3.2"/>
    <path d="m20.4 11.4 2.6 2.6"/>
    <path d="m16.6 9 1 1 1.8-1.8"/>
  </I>
);

// 2C · Embudo con check inscrito · destilar + validar en uno solo.
//      Lo que pasa el filtro está aprobado.
const IconCurationC = (p) => (
  <I {...p}>
    <path d="M3 4h18l-7 9v6.5l-4 1.5v-8z"/>
    <path d="m9 7.5 2 2 4-4"/>
  </I>
);

// 2D · Libro entrando a la máquina/embudo · el conocimiento pasa por
//      el proceso y se destila. Esta es la dirección que pediste:
//      input explícito (libro) + procesamiento (embudo).
const IconCurationD = (p) => (
  <I {...p}>
    <rect x="9" y="2" width="6" height="4" rx="0.3"/>
    <path d="M12 2v4"/>
    <path d="M12 7v1.5"/>
    <path d="m10.7 8 1.3 1.3 1.3-1.3"/>
    <path d="M4 11h16l-6 7v2.5l-4 1v-3.5z"/>
  </I>
);

// 2E · Libro ABIERTO cayendo al embudo · páginas en V abiertas en
//      la boca del embudo. El conocimiento entra abierto, sale destilado.
const IconCurationE = (p) => (
  <I {...p}>
    <path d="M2 4 12 6 22 4v3.5L12 9.5 2 7.5z"/>
    <path d="M12 6v3.5"/>
    <path d="M4 12h16l-6 6.5v2.5l-4 1v-3.5z"/>
  </I>
);

// 2F · Rodillos (rollers) · metáfora textil pura — 3 hilos crudos
//      entran, los rodillos los procesan, sale 1 hilo destilado.
//      Conecta directo con el ADN del oficio textil del logo.
const IconCurationF = (p) => (
  <I {...p}>
    <path d="M9 2v6"/>
    <path d="M12 2v6"/>
    <path d="M15 2v6"/>
    <circle cx="7.5" cy="11.5" r="3.5"/>
    <circle cx="16.5" cy="11.5" r="3.5"/>
    <circle cx="7.5" cy="11.5" r="0.85" fill="currentColor" stroke="none"/>
    <circle cx="16.5" cy="11.5" r="0.85" fill="currentColor" stroke="none"/>
    <path d="M12 15v7"/>
  </I>
);

// — 3 · LEARNING-CLOCK · canon: pie de 5 sectores (ver IconLearningClock)
// Variantes A/B/C descartadas · v2 cerrado.

// — 4 · KNOWLEDGE-INDEX · canon: bandeja receptora (ver IconKnowledgeIndex)
// Variantes A/B/C descartadas · v2 cerrado.

// — 5 · VOICE · canon: avatar + onda de voz lateral (ver IconVoice)
// Variantes A/B/C descartadas · v2 cerrado.

// — 6 · WORKSPACE · contenedor de cuenta/clase/proyecto

// 6A · Paréntesis con fábrica adentro · «taller contenido». Combina
//      la idea de espacio cerrado con el motor productivo.
const IconWorkspaceA = (p) => (
  <I {...p}>
    <path d="M3 4c-1.5 4-1.5 12 0 16"/>
    <path d="M21 4c1.5 4 1.5 12 0 16"/>
    <path d="M7.5 8h1.5v3.5"/>
    <path d="M6 17v-5l2.2 1.3v-1.3l2.2 1.3v-1.3l2.2 1.3v-1.3l2.2 1.3v-1.3l2.2 1.3v4z"/>
  </I>
);

// 6B · Perímetro cosido + nodo central · territorio orgánico.
//      Dasharray comunica «este es el borde de tu espacio».
const IconWorkspaceB = (p) => (
  <I {...p}>
    <circle cx="12" cy="12" r="9" strokeDasharray="2.4 1.7"/>
    <circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none"/>
  </I>
);

// 6C · Marco + 3 formas conectadas · cuadrado + círculo + triángulo
//      con líneas finas entre ellos. Workspace = espacio donde
//      conviven distintas piezas relacionadas.
const IconWorkspaceC = (p) => (
  <I {...p}>
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M9.2 8 15 8.2"   strokeWidth="0.85"/>
    <path d="M8.2 9.5 11.7 16" strokeWidth="0.85"/>
    <path d="M15.6 9.7 12.7 16" strokeWidth="0.85"/>
    <rect x="6" y="6.5" width="3" height="3" rx="0.3"/>
    <circle cx="16.5" cy="8" r="1.7"/>
    <path d="M12 14.4 9.3 18.4 14.7 18.4z"/>
  </I>
);

// 6D · Corchetes con nodo · workspace literal [ • ]. Tipográfico,
//      directo, sin metáfora extra. Conecta con código/scope.
const IconWorkspaceD = (p) => (
  <I {...p}>
    <path d="M8 3H5v18h3"/>
    <path d="M16 3h3v18h-3"/>
    <circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none"/>
  </I>
);

const IconWorkspace = IconWorkspaceC;

// ─── Sets for sample composition ─────────────────────────────────────
const ICON_SETS = {
  navigation:    ['IconSearch','IconPlus','IconX','IconChevronDown','IconChevronLeft','IconChevronRight','IconChevronsLeft','IconArrowRight','IconArrowUp','IconPanelLeft','IconPanelRight'],
  time:          ['IconHourglass','IconClock','IconRefreshCw'],
  knowledge:     ['IconLayers','IconLibrary','IconBookmark','IconFileText'],
  communication: ['IconMail','IconMessage','IconInbox','IconPaperclip'],
  status:        ['IconCheck','IconAlertCircle','IconAlertTriangle','IconSparkles','IconPin','IconCircle','IconCircleFill'],
  person:        ['IconUser','IconUsers','IconUserCircle'],
  settings:      ['IconSettings','IconSliders','IconEdit','IconLogOut','IconExternalLink','IconTrash'],
};

const CUSTOM_ICONS = [
  { Comp: IconBrandLoom,    name: 'brand-loom',       label: 'Brand mark',           concept: 'La trama tejida del logo, destilada a 24×24 — tres urdimbres (verticales) + dos tramas onduladas. Único de marca.' },
  { Comp: IconCriterio,     name: 'criterio',         label: 'Tu criterio · HITL',   concept: 'Dos hilos cruzados anudados en un punto sólido: el ancla humana. NO un check, NO un thumb-up — una puntada deliberada.' },
  { Comp: IconWorkLoom,     name: 'workloom',         label: 'WorkLoom',             concept: 'Telar visto desde arriba — marco + tramas cruzadas + nodo activo. La «Mesa de Control» como bastidor.' },
  { Comp: IconSpaceLoom,    name: 'spaceloom',        label: 'SpaceLoom',            concept: 'Bubble de chat con línea cosida adentro — el espacio donde agente y operator iteran. Conversación = puntada en curso.' },
  { Comp: IconStackLoom,    name: 'stackloom',        label: 'StackLoom',            concept: 'Layers + nodo activo en la capa superior — capas de conocimiento apiladas con señal de «capa en uso».' },
  { Comp: IconVoice,        name: 'voice',            label: 'Sabor del user',       concept: 'Avatar (cabeza + hombros) + onda de voz lateral. Persona explícita con rasgo vocal distintivo.' },
  { Comp: IconLearningClock,name: 'learning-clock',   label: 'Reloj de aprendizaje', concept: 'Pie de 5 sectores canónicos (0–20–40–60–80–100). Cada sector llena = 20% de avance.' },
  { Comp: IconKnowledgeIndex,name:'knowledge-index',  label: 'Knowledge a indexar',  concept: 'Bandeja receptora con item descendiendo — gesto directo de depósito al stack.' },
  { Comp: IconCuration,     name: 'curation',         label: 'Curaduría · L4→L1',    concept: 'Flecha cosida ascendente sobre línea base. Acto cuidadoso de promoción de capa, no upload genérico.' },
  { Comp: IconWorkspace,    name: 'workspace',        label: 'Workspace · cuenta / clase / proyecto', concept: 'Marco con cuadrado · círculo · triángulo conectados con líneas finas — el espacio donde conviven cosas relacionadas: cuenta, persona, clase, lecciones, proyecto, piezas.' },
];

const UI_GROUPS = [
  { title: 'Navegación',     subtitle: 'Foco en discover y movimiento',
    icons: [
      ['IconSearch','search'], ['IconPlus','plus'], ['IconX','x'],
      ['IconChevronDown','chevron-down'], ['IconChevronLeft','chevron-left'],
      ['IconChevronRight','chevron-right'], ['IconChevronsLeft','chevrons-left'],
      ['IconArrowRight','arrow-right'], ['IconArrowUp','arrow-up'],
      ['IconPanelLeft','panel-left'], ['IconPanelRight','panel-right'],
    ] },
  { title: 'Tiempo y ciclo', subtitle: 'Reloj, ciclos, refresco',
    icons: [
      ['IconHourglass','hourglass'], ['IconClock','clock'], ['IconRefreshCw','refresh-cw'],
    ] },
  { title: 'Conocimiento',   subtitle: 'Stack, biblioteca, archivos',
    icons: [
      ['IconLayers','layers'], ['IconLibrary','library'],
      ['IconBookmark','bookmark'], ['IconFileText','file-text'],
    ] },
  { title: 'Comunicación',   subtitle: 'Mail, chat, inbox, attach',
    icons: [
      ['IconMail','mail'], ['IconMessage','message'], ['IconInbox','inbox'],
      ['IconPaperclip','paperclip'],
    ] },
  { title: 'Estados',        subtitle: 'Señales y prioridad',
    icons: [
      ['IconCheck','check'], ['IconAlertCircle','alert-circle'],
      ['IconAlertTriangle','alert-triangle'], ['IconSparkles','sparkles'],
      ['IconPin','pin'], ['IconCircle','circle'], ['IconCircleFill','circle · fill'],
    ] },
  { title: 'Personas',       subtitle: 'Roles y avatares',
    icons: [
      ['IconUser','user'], ['IconUsers','users'], ['IconUserCircle','user-circle'],
    ] },
  { title: 'Configuración',  subtitle: 'Tools, edición, salir',
    icons: [
      ['IconSettings','settings'], ['IconSliders','sliders'],
      ['IconEdit','edit'], ['IconLogOut','log-out'],
      ['IconExternalLink','external'], ['IconTrash','trash'],
    ] },
];

Object.assign(window, {
  ICON_VB, ICON_SW, I,
  IconSearch, IconPlus, IconX, IconChevronDown, IconChevronLeft, IconChevronRight,
  IconChevronsLeft, IconArrowRight, IconArrowUp, IconPanelLeft, IconPanelRight,
  IconHourglass, IconClock, IconRefreshCw,
  IconLayers, IconLibrary, IconBookmark, IconFileText,
  IconMail, IconMessage, IconInbox, IconPaperclip,
  IconCheck, IconAlertCircle, IconAlertTriangle, IconSparkles,
  IconPin, IconCircle, IconCircleFill,
  IconUser, IconUsers, IconUserCircle,
  IconSettings, IconSliders, IconEdit, IconLogOut, IconExternalLink, IconTrash,
  IconBrandLoom, IconCriterio, IconWorkLoom, IconSpaceLoom, IconSpaceLoomA, IconSpaceLoomB, IconSpaceLoomC,
  IconStackLoom,
  IconWorkspace, IconWorkspaceA, IconWorkspaceB, IconWorkspaceC, IconWorkspaceD,
  IconVoice, IconLearningClock, IconKnowledgeIndex, IconCuration,
  IconCriterioA, IconCriterioB, IconCriterioC,
  IconCurationA, IconCurationB, IconCurationC, IconCurationD, IconCurationE, IconCurationF,
  ICON_SETS, CUSTOM_ICONS, UI_GROUPS,
});
