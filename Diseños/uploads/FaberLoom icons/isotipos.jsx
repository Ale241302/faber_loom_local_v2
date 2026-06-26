// FaberLoom · 5 isotipo concepts
// Each takes (s, ink, coral, sw) — ink = primary structural color,
// coral = accent fiber, sw = stroke width. All render at viewBox 0 0 32 32.

// 01 · Trama tejida — warp (vertical, ink) + weft (wavy, coral)
//      Refinement of the provisional brand mark; dual-color now.
function IsoTrama({ s = 120, ink = '#1F1E1C', coral = '#C96442',
                   pizarra = '#5A6B7C', sw = 2, mono }) {
  // Each thread is its own color — three distinct fibers in each axis.
  const w = mono ? [ink, ink, ink]      : [ink, ink, ink];
  const f = mono ? [ink, ink, ink]      : [coral, coral, coral];
  // Slight per-thread variation: middle warp leans pizarra, wefts alternate.
  const wColor = mono ? [ink, ink, ink]      : [ink, pizarra, ink];
  const fColor = mono ? [ink, ink, ink]      : [coral, ink, coral];
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none"
         strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"
         strokeDasharray="3.1 1.9">
      <path d="M8 4 L8 28" stroke={wColor[0]} />
      <path d="M16 4 L16 28" stroke={wColor[1]} />
      <path d="M24 4 L24 28" stroke={wColor[2]} />
      <path d="M3.5 9 Q8 6.5 12.5 9 T21.5 9 T28.5 9" stroke={fColor[0]} />
      <path d="M3.5 16 Q8 18.5 12.5 16 T21.5 16 T28.5 16" stroke={fColor[1]} />
      <path d="M3.5 23 Q8 20.5 12.5 23 T21.5 23 T28.5 23" stroke={fColor[2]} />
    </svg>
  );
}

// 02 · Hilos entrelazados — two S-curves crossing, simulated weave.
//      Coral drawn first (under), ink drawn over (visible at crossing).
function IsoHilos({ s = 120, ink = '#1F1E1C', coral = '#C96442', sw = 2 }) {
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none"
         strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 6 C 6 16, 26 16, 26 26" stroke={coral} />
      <path d="M26 6 C 26 16, 6 16, 6 26" stroke={ink} />
    </svg>
  );
}

// 03 · Nudo céltico moderno — two interlocked elliptical rings, chain-link.
//      Mask cuts on each ring create proper over/under at both crossings.
function IsoNudo({ s = 120, ink = '#1F1E1C', coral = '#C96442', sw = 2 }) {
  const uid = React.useId().replace(/:/g, '');
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none"
         strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round">
      <defs>
        <mask id={`${uid}-coral`}>
          <rect width="32" height="32" fill="white" />
          <circle cx="16" cy="23.4" r="2.6" fill="black" />
        </mask>
        <mask id={`${uid}-ink`}>
          <rect width="32" height="32" fill="white" />
          <circle cx="16" cy="8.6" r="2.6" fill="black" />
        </mask>
      </defs>
      <ellipse cx="11" cy="16" rx="6.6" ry="8" stroke={coral} mask={`url(#${uid}-coral)`} />
      <ellipse cx="21" cy="16" rx="6.6" ry="8" stroke={ink}   mask={`url(#${uid}-ink)`} />
    </svg>
  );
}

// 04 · Sashiko · asterisk-stitch — three crossing dashed lines forming
//      a six-rayed star. Reads as the literal `*` in `Faber*Loom`.
function IsoSashiko({ s = 120, ink = '#1F1E1C', coral = '#C96442', sw = 2.1 }) {
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none"
         strokeWidth={sw} strokeLinecap="round" strokeDasharray="3.1 1.9">
      <line x1="16" y1="5" x2="16" y2="27" stroke={ink} />
      <line x1="6.7" y1="10.5" x2="25.3" y2="21.5" stroke={coral} />
      <line x1="25.3" y1="10.5" x2="6.7" y2="21.5" stroke={coral} />
    </svg>
  );
}

// 05 · Möbius dual — split lemniscate, two lobes of ∞ in two colors.
//      The two strands meet at center, never the same path.
function IsoMobius({ s = 120, ink = '#1F1E1C', coral = '#C96442', sw = 2 }) {
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none"
         strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round">
      {/* left lobe — ink */}
      <path d="M16 16 C 11 9, 4 10, 4 16 C 4 22, 11 23, 16 16" stroke={ink} />
      {/* right lobe — coral */}
      <path d="M16 16 C 21 9, 28 10, 28 16 C 28 22, 21 23, 16 16" stroke={coral} />
    </svg>
  );
}

// Tiny asterisk for the dot between Faber and Loom — matches the stitch
// vocabulary across the system. Sized in em via parent font-size.
function TinyAster({ size = 14, color = '#C96442', sw = 1.4 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none"
         stroke={color} strokeWidth={sw} strokeLinecap="round"
         style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <line x1="6" y1="2.4" x2="6" y2="9.6" />
      <line x1="3" y1="4.2" x2="9" y2="7.8" />
      <line x1="9" y1="4.2" x2="3" y2="7.8" />
    </svg>
  );
}

const ISOTIPOS = {
  trama:   { Component: IsoTrama,   name: 'Trama tejida',           idx: '01' },
  hilos:   { Component: IsoHilos,   name: 'Hilos entrelazados',     idx: '02' },
  nudo:    { Component: IsoNudo,    name: 'Nudo céltico moderno',   idx: '03' },
  sashiko: { Component: IsoSashiko, name: 'Sashiko asterisk',       idx: '04' },
  mobius:  { Component: IsoMobius,  name: 'Möbius dual',            idx: '05' },
};

Object.assign(window, {
  IsoTrama, IsoHilos, IsoNudo, IsoSashiko, IsoMobius, TinyAster, ISOTIPOS,
});
