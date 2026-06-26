// Wordmark, Lockup, and supporting compositional pieces for FaberLoom.
// Color usage is centralized in a `palette` object; every piece is
// monochrome-aware (`mono` prop forces both words to a single color).

const PALETTE = {
  cream: '#F4F1ED',
  ink:   '#1F1E1C',
  coral: '#C96442',
  pizarra:'#5A6B7C',
  rule:  'rgba(31,30,28,0.18)',
  ruleOnDark: 'rgba(244,241,237,0.22)',
};

// ─── Wordmark · horizontal ───────────────────────────────────────────
//  [iso]   Faber ✱ Loom
function WordmarkH({
  Iso, size = 64, faberColor = PALETTE.ink, loomColor = PALETTE.coral,
  asterColor, ink = PALETTE.ink, coral = PALETTE.coral,
  showIso = true, mono = false, tagline,
  taglineColor = PALETTE.pizarra,
}) {
  const fColor = mono ? loomColor : faberColor;
  const lColor = mono ? loomColor : loomColor;
  const aColor = asterColor ?? (mono ? loomColor : coral);
  const isoInk   = mono ? loomColor : ink;
  const isoCoral = mono ? loomColor : coral;
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: size * 0.42 }}>
      {showIso && (
        <Iso s={size * 1.05} ink={isoInk} coral={isoCoral}
             sw={Math.max(1.4, size * 1.05 / 65)} />
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: size * 0.18 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', lineHeight: 1 }}>
          <span style={{
            fontFamily: '"Crimson Pro", Georgia, serif',
            fontWeight: 500, fontStyle: 'italic',
            fontSize: size, color: fColor,
            letterSpacing: '-0.005em',
            paddingRight: size * 0.04,
            marginRight: size * 0.22,
          }}>Faber</span>
          <span style={{
            fontFamily: '"Inter", system-ui, sans-serif',
            fontWeight: 700, fontSize: size * 0.78, color: lColor,
            letterSpacing: '-0.028em',
          }}>Loom</span>
        </div>
        {tagline && (
          <span style={{
            fontFamily: '"Inter", system-ui, sans-serif',
            fontWeight: 400, fontSize: size * 0.21,
            color: taglineColor, letterSpacing: '0.04em',
          }}>{tagline}</span>
        )}
      </div>
    </div>
  );
}

// ─── Wordmark · vertical ─────────────────────────────────────────────
function WordmarkV({
  Iso, size = 56, faberColor = PALETTE.ink, loomColor = PALETTE.coral,
  asterColor, ink = PALETTE.ink, coral = PALETTE.coral,
  showIso = true, mono = false, tagline,
  taglineColor = PALETTE.pizarra,
  rule = PALETTE.rule,
}) {
  const fColor = mono ? loomColor : faberColor;
  const lColor = mono ? loomColor : loomColor;
  const aColor = asterColor ?? (mono ? loomColor : coral);
  const isoInk   = mono ? loomColor : ink;
  const isoCoral = mono ? loomColor : coral;
  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column',
                  alignItems: 'flex-start', gap: size * 0.42 }}>
      {showIso && (
        <Iso s={size * 1.5} ink={isoInk} coral={isoCoral}
             sw={Math.max(1.4, size * 1.5 / 65)} />
      )}
      <div style={{ width: size * 1.55, height: 1, background: rule }} />
      <div style={{ display: 'flex', flexDirection: 'column',
                    lineHeight: 0.92, gap: size * 0.04 }}>
        <span style={{
          fontFamily: '"Crimson Pro", Georgia, serif',
          fontWeight: 500, fontStyle: 'italic',
          fontSize: size, color: fColor, letterSpacing: '-0.005em',
        }}>Faber</span>
        <span style={{
          fontFamily: '"Inter", system-ui, sans-serif',
          fontWeight: 700, fontSize: size * 0.78, color: lColor,
          letterSpacing: '-0.028em',
        }}>Loom</span>
      </div>
      {tagline && (
        <span style={{
          fontFamily: '"Inter", system-ui, sans-serif',
          fontWeight: 400, fontSize: size * 0.21,
          color: taglineColor, letterSpacing: '0.04em',
          marginTop: size * 0.05,
        }}>{tagline}</span>
      )}
    </div>
  );
}

// ─── Color tile ──────────────────────────────────────────────────────
function ColorTile({ swatch, name, hex, note, dark }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{ width: 36, height: 36, borderRadius: 7, background: swatch,
                    boxShadow: 'inset 0 0 0 1px rgba(0,0,0,.08)' }} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 12,
                       color: dark ? PALETTE.cream : PALETTE.ink, letterSpacing: '-0.01em' }}>
          {name}
        </span>
        <span style={{ fontFamily: 'ui-monospace, "SF Mono", monospace',
                       fontSize: 10.5, letterSpacing: '0.02em',
                       color: dark ? 'rgba(244,241,237,0.62)' : PALETTE.pizarra }}>
          {hex}{note ? '  ·  ' + note : ''}
        </span>
      </div>
    </div>
  );
}

// ─── Caption ─────────────────────────────────────────────────────────
function Caption({ children, mono, dark }) {
  return (
    <span style={{
      fontFamily: mono ? 'ui-monospace, "SF Mono", monospace' : 'Inter, sans-serif',
      fontSize: 10.5, fontWeight: 500, letterSpacing: '0.06em',
      textTransform: 'uppercase',
      color: dark ? 'rgba(244,241,237,0.55)' : 'rgba(31,30,28,0.5)',
    }}>{children}</span>
  );
}

function Body({ children, dark, size = 12 }) {
  return (
    <span style={{
      fontFamily: 'Inter, sans-serif', fontSize: size, lineHeight: 1.55,
      fontWeight: 400, color: dark ? PALETTE.cream : PALETTE.ink,
      letterSpacing: '-0.005em',
    }}>{children}</span>
  );
}

function H({ children, size = 18, dark, italic, weight = 500 }) {
  return (
    <span style={{
      fontFamily: italic
        ? '"Cormorant Garamond", Georgia, serif'
        : 'Inter, sans-serif',
      fontStyle: italic ? 'italic' : 'normal',
      fontSize: size, fontWeight: weight, lineHeight: 1.1,
      color: dark ? PALETTE.cream : PALETTE.ink,
      letterSpacing: '-0.018em',
    }}>{children}</span>
  );
}

// Surface — artboard background with consistent inner padding
function Surface({ bg = PALETTE.cream, dark, children, pad = 28, style }) {
  return (
    <div style={{
      width: '100%', height: '100%', background: bg, padding: pad,
      boxSizing: 'border-box', display: 'flex', flexDirection: 'column',
      gap: 18, ...style,
    }}>{children}</div>
  );
}

// Header strip at top of an artboard — small caps eyebrow + title
function ArtboardHeader({ eyebrow, title, dark }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <Caption dark={dark}>{eyebrow}</Caption>
      <H size={15} weight={600} dark={dark}>{title}</H>
    </div>
  );
}

Object.assign(window, {
  PALETTE, WordmarkH, WordmarkV, ColorTile, Caption, Body, H, Surface, ArtboardHeader,
});
