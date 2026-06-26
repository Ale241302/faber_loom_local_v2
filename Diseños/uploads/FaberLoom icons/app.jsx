// FaberLoom logo system — pieces composed into artboards on a DesignCanvas.
// Each concept gets 5 artboards: overview, wordmark, isotipo variants,
// lockups, and specs.

const { Component: T_Comp } = ISOTIPOS.trama;
const cream  = PALETTE.cream;
const ink    = PALETTE.ink;
const coral  = PALETTE.coral;
const pizarra= PALETTE.pizarra;

// ─── Overview artboard (per concept) ─────────────────────────────────
function OverviewArtboard({ Iso, idx, name, concept, principle }) {
  return (
    <Surface bg={cream} pad={32}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <Caption>Concept {idx}</Caption>
          <H size={20} italic weight={500}>{name}</H>
        </div>
        <Iso s={68} ink={ink} coral={coral} />
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    padding: '12px 0' }}>
        <WordmarkH Iso={Iso} size={56} />
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 14,
                    display: 'flex', flexDirection: 'column', gap: 6 }}>
        <Caption>Principle</Caption>
        <Body size={12.5}>{principle}</Body>
      </div>
    </Surface>
  );
}

// ─── Wordmark variants artboard ──────────────────────────────────────
function WordmarkArtboard({ Iso }) {
  return (
    <Surface bg={cream} pad={0} style={{ gap: 0 }}>
      {/* Light · horizontal */}
      <div style={{ flex: 1, padding: 28, display: 'flex', flexDirection: 'column', gap: 12,
                    borderBottom: `1px solid ${PALETTE.rule}` }}>
        <Caption>Horizontal · positive</Caption>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
          <WordmarkH Iso={Iso} size={40} />
        </div>
      </div>
      {/* Dark · horizontal */}
      <div style={{ flex: 1, padding: 28, display: 'flex', flexDirection: 'column', gap: 12,
                    background: ink }}>
        <Caption dark>Horizontal · dark mode</Caption>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
          <WordmarkH Iso={Iso} size={40}
            faberColor={cream} loomColor={coral}
            ink={cream} coral={coral} />
        </div>
      </div>
    </Surface>
  );
}

// ─── Vertical wordmark artboard ──────────────────────────────────────
function VerticalArtboard({ Iso }) {
  return (
    <Surface bg={cream} pad={0} style={{ gap: 0, flexDirection: 'row' }}>
      <div style={{ flex: 1, padding: 28, display: 'flex', flexDirection: 'column', gap: 14,
                    borderRight: `1px solid ${PALETTE.rule}` }}>
        <Caption>Vertical · positive</Caption>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <WordmarkV Iso={Iso} size={36} />
        </div>
      </div>
      <div style={{ flex: 1, padding: 28, display: 'flex', flexDirection: 'column', gap: 14,
                    background: ink }}>
        <Caption dark>Vertical · dark mode</Caption>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <WordmarkV Iso={Iso} size={36}
            faberColor={cream} loomColor={coral}
            ink={cream} coral={coral} rule={PALETTE.ruleOnDark} />
        </div>
      </div>
    </Surface>
  );
}

// ─── Isotipo variants (4 quadrants) ──────────────────────────────────
function IsotipoArtboard({ Iso }) {
  const quad = (label, bg, content, borderRight, borderBottom, dark) => (
    <div style={{
      flex: 1, padding: 22, background: bg,
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      gap: 14, position: 'relative',
      borderRight: borderRight ? (dark ? '1px solid rgba(244,241,237,0.12)' : `1px solid ${PALETTE.rule}`) : 'none',
      borderBottom: borderBottom ? (dark ? '1px solid rgba(244,241,237,0.12)' : `1px solid ${PALETTE.rule}`) : 'none',
    }}>
      <div style={{ position: 'absolute', top: 12, left: 14 }}>
        <Caption dark={dark}>{label}</Caption>
      </div>
      {content}
    </div>
  );
  return (
    <Surface bg={cream} pad={0} style={{ gap: 0 }}>
      <div style={{ flex: 1, display: 'flex' }}>
        {quad('Positive · cream',  cream, <Iso s={72} ink={ink} coral={coral}/>, true, true, false)}
        {quad('Dark · ink',         ink,   <Iso s={72} ink={cream} coral={coral}/>, false, true, true)}
      </div>
      <div style={{ flex: 1, display: 'flex' }}>
        {quad('Mono · ink',         cream, <Iso s={72} ink={ink} coral={ink}/>, true, false, false)}
        {quad('Mono · cream',        ink,   <Iso s={72} ink={cream} coral={cream}/>, false, false, true)}
      </div>
    </Surface>
  );
}

// ─── Lockups (4 official) ────────────────────────────────────────────
function LockupArtboard({ Iso }) {
  const cell = (label, content, br, bb) => (
    <div style={{
      flex: 1, padding: 24, display: 'flex', flexDirection: 'column',
      gap: 14, position: 'relative',
      borderRight: br ? `1px solid ${PALETTE.rule}` : 'none',
      borderBottom: bb ? `1px solid ${PALETTE.rule}` : 'none',
    }}>
      <Caption>{label}</Caption>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {content}
      </div>
    </div>
  );
  return (
    <Surface bg={cream} pad={0} style={{ gap: 0 }}>
      <div style={{ flex: 1, display: 'flex' }}>
        {cell('H · compact', <WordmarkH Iso={Iso} size={28} />, true, true)}
        {cell('H · with tagline',
              <WordmarkH Iso={Iso} size={28} tagline="Tejé tu trabajo" />,
              false, true)}
      </div>
      <div style={{ flex: 1, display: 'flex' }}>
        {cell('V · compact', <WordmarkV Iso={Iso} size={26} />, true, false)}
        {cell('V · with tagline',
              <WordmarkV Iso={Iso} size={26} tagline="Tejé tu trabajo" />,
              false, false)}
      </div>
    </Surface>
  );
}

// ─── Reduction & Specs ───────────────────────────────────────────────
function SpecsArtboard({ Iso, fontFamilyFaber, fontFamilyLoom, strokeNote, idea }) {
  const Step = ({ size, label }) => (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
                  minWidth: size + 8 }}>
      <div style={{ height: 70, display: 'flex', alignItems: 'center' }}>
        <Iso s={size} ink={ink} coral={coral} />
      </div>
      <Caption>{label}</Caption>
    </div>
  );
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Specifications" title="Reduction · type · stroke" />
      {/* reduction ladder */}
      <div style={{ display: 'flex', alignItems: 'flex-end',
                    gap: 18, padding: '10px 6px',
                    background: 'rgba(31,30,28,0.025)',
                    border: `1px solid ${PALETTE.rule}`,
                    borderRadius: 8, paddingBottom: 14, paddingTop: 14 }}>
        <Step size={64} label="64 px" />
        <Step size={32} label="32 px" />
        <Step size={24} label="24 px" />
        <Step size={16} label="16 px" />
      </div>
      {/* spec rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
        <SpecRow k="Faber" v={fontFamilyFaber} />
        <SpecRow k="Loom" v={fontFamilyLoom} />
        <SpecRow k="Stroke" v={strokeNote} />
        <SpecRow k="Clear space" v="≥ ½ cap-height of « F »" />
        <SpecRow k="Concept" v={idea} />
      </div>
    </Surface>
  );
}
function SpecRow({ k, v }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '88px 1fr', gap: 14, alignItems: 'baseline' }}>
      <Caption>{k}</Caption>
      <Body size={11.5}>{v}</Body>
    </div>
  );
}

// ─── Concept section factory ─────────────────────────────────────────
function ConceptSection({ key_, idx, title, subtitle, isoKey, principle,
                          fontFaber, fontLoom, strokeNote, idea }) {
  const Iso = ISOTIPOS[isoKey].Component;
  return (
    <DCSection id={key_} title={`${idx} · ${title}`} subtitle={subtitle}>
      <DCArtboard id={`${key_}-overview`} label="Overview"           width={420} height={360}>
        <OverviewArtboard Iso={Iso} idx={idx} name={title} principle={principle} />
      </DCArtboard>
      <DCArtboard id={`${key_}-wordmark`} label="Wordmark · H"        width={420} height={360}>
        <WordmarkArtboard Iso={Iso} />
      </DCArtboard>
      <DCArtboard id={`${key_}-vertical`} label="Wordmark · V"        width={460} height={360}>
        <VerticalArtboard Iso={Iso} />
      </DCArtboard>
      <DCArtboard id={`${key_}-isotipo`}  label="Isotipo · 4 variants"   width={420} height={360}>
        <IsotipoArtboard Iso={Iso} />
      </DCArtboard>
      <DCArtboard id={`${key_}-lockups`}  label="Lockups · 4 official"   width={520} height={360}>
        <LockupArtboard Iso={Iso} />
      </DCArtboard>
      <DCArtboard id={`${key_}-specs`}    label="Specs · reduction"      width={400} height={360}>
        <SpecsArtboard Iso={Iso}
          fontFamilyFaber={fontFaber}
          fontFamilyLoom={fontLoom}
          strokeNote={strokeNote}
          idea={idea} />
      </DCArtboard>
    </DCSection>
  );
}

// ─── Intro / Foundations ─────────────────────────────────────────────
function IntroBrief() {
  return (
    <Surface bg={cream} pad={32}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Caption>FaberLoom · Brand · v2</Caption>
        <H size={26} italic weight={500}>El telar del hacedor.</H>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16,
                    paddingTop: 6 }}>
        <Body size={13}>
          Cinco rutas conceptualmente distintas hacia un sistema de marca
          editorial, sobrio y atemporal. Cada propuesta se entrega completa
          (wordmark horizontal y vertical, isotipo, lockups, specs).
        </Body>
        <Body size={13}>
          La tipografía dual se mantiene en las cinco — <i>Crimson Pro Italic 500</i>{' '}
          para <i>Faber</i> (oficio antiguo, contraste cálido), <b>Inter Bold 700</b>{' '}
          para Loom (herramienta contemporánea). El pareo elegido — F · original — privilegia
          presencia y peso editorial.
        </Body>
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 16 }}>
        <Body size={11.5}>
          <i style={{ color: pizarra }}>“La IA prepara. Vos tejés.”</i>
        </Body>
      </div>
    </Surface>
  );
}

function PaletteBoard() {
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 01" title="Palette" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginTop: 4 }}>
        <ColorTile swatch={cream}   name="Cream"   hex="#F4F1ED" note="bg" />
        <ColorTile swatch={ink}     name="Ink"     hex="#1F1E1C" note="estructura" />
        <ColorTile swatch={coral}   name="Coral"   hex="#C96442" note="acento" />
        <ColorTile swatch={pizarra} name="Pizarra" hex="#5A6B7C" note="alt fría" />
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 14, marginTop: 'auto' }}>
        <Caption>Logo usa solo</Caption>
        <div style={{ marginTop: 8 }}>
          <Body size={11.5}>
            Cream + Ink + Coral. Pizarra opcional para variantes frías del isotipo.
            Vino, Salvia y Ámbar son colores de estado del producto — nunca en marca.
          </Body>
        </div>
      </div>
    </Surface>
  );
}

function TypographyBoard() {
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 02" title="Typography" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 4 }}>
        <div style={{ padding: '14px 16px', background: 'rgba(31,30,28,0.03)',
                      borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
          <Caption>Faber · serif italic</Caption>
          <span style={{ fontFamily: '"Crimson Pro", Georgia, serif',
                         fontStyle: 'italic', fontWeight: 500, fontSize: 40,
                         color: ink, lineHeight: 1.05, letterSpacing: '-0.005em' }}>Faber</span>
          <Body size={11}>Crimson Pro · Italic · 500 — oficio.</Body>
        </div>
        <div style={{ padding: '14px 16px', background: 'rgba(31,30,28,0.03)',
                      borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
          <Caption>Loom · sans</Caption>
          <span style={{ fontFamily: '"Inter", sans-serif',
                         fontWeight: 700, fontSize: 32, color: coral,
                         letterSpacing: '-0.028em', lineHeight: 1.05 }}>Loom</span>
          <Body size={11}>Inter · Bold · 700 — herramienta.</Body>
        </div>
        <div style={{ padding: '14px 16px', background: 'rgba(31,30,28,0.03)',
                      borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
          <Caption>Tagline</Caption>
          <span style={{ fontFamily: '"Inter", sans-serif',
                         fontWeight: 400, fontSize: 14, color: pizarra,
                         letterSpacing: '0.04em' }}>Tejé tu trabajo</span>
          <Body size={11}>Inter · Regular · 400 · pizarra.</Body>
        </div>
      </div>
    </Surface>
  );
}

function ClearSpaceBoard() {
  // Visual diagram of clear space using IsoTrama as example
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 03" title="Clear space · proportion" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    position: 'relative' }}>
        {/* clear-space rectangle */}
        <div style={{ position: 'relative', padding: 36 }}>
          <div style={{ position: 'absolute', inset: 0,
                        border: `1px dashed ${coral}`, borderRadius: 4,
                        opacity: 0.55 }} />
          <WordmarkH Iso={IsoTrama} size={36} />
          {/* X markers in 4 corners showing minimum spacing = 1× cap height of F */}
          <span style={{ position: 'absolute', top: 6, left: 6,
                         fontFamily: 'ui-monospace', fontSize: 9,
                         color: coral, letterSpacing: '0.1em' }}>½ X</span>
          <span style={{ position: 'absolute', bottom: 6, right: 6,
                         fontFamily: 'ui-monospace', fontSize: 9,
                         color: coral, letterSpacing: '0.1em' }}>½ X</span>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 'auto' }}>
        <Caption>Rule</Caption>
        <Body size={11.5}>
          Espacio mínimo alrededor del logo = ½ × altura de la « F » de Faber. En
          lockups con isotipo, la altura del isotipo iguala la cap-height de
          Faber + 4%; el gap entre isotipo y wordmark equivale a la x-height.
        </Body>
      </div>
    </Surface>
  );
}

function DontsBoard() {
  const items = [
    'No estirar ni deformar',
    'No rotar el wordmark',
    'No cambiar tipografías',
    'No agregar sombras o glow',
    'No usar fuera de la paleta',
    'No invertir colores ad-hoc',
    'No usar emoji o mascotas',
    'No usar gradientes',
  ];
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 04" title="No hacer" />
      <ul style={{ listStyle: 'none', margin: 0, padding: 0,
                   display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {items.map((s, i) => (
          <li key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
            <span style={{ width: 10, height: 1.5, background: coral, marginTop: 9, flex: '0 0 auto' }} />
            <Body size={11.5}>{s}</Body>
          </li>
        ))}
      </ul>
      <div style={{ marginTop: 'auto', borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 14,
                    display: 'flex', flexDirection: 'column', gap: 6 }}>
        <Caption>Test del logo</Caption>
        <Body size={11.5}>
          Si en B&W, a 16 px, sobre cream o sobre ink, el resultado no se distingue
          de Slack/Notion/HubSpot — iterar.
        </Body>
      </div>
    </Surface>
  );
}

// ─── Type pairing studies ────────────────────────────────────────────
function TypePairBoard({ pairLabel, faberFont, faberWeight = 500, faberStyle = 'italic',
                         loomFont, loomWeight = 700, loomStyle = 'normal',
                         loomLetterSpacing = '-0.028em', size = 56,
                         note }) {
  return (
    <Surface bg={cream} pad={26}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Caption>{pairLabel}</Caption>
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', lineHeight: 1 }}>
          <span style={{
            fontFamily: faberFont, fontStyle: faberStyle, fontWeight: faberWeight,
            fontSize: size, color: ink, letterSpacing: '-0.005em',
            marginRight: size * 0.14,
          }}>Faber</span>
          <span style={{
            fontFamily: loomFont, fontStyle: loomStyle, fontWeight: loomWeight,
            fontSize: size * 0.78, color: coral, letterSpacing: loomLetterSpacing,
          }}>Loom</span>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 12 }}>
        <Body size={11}>{note}</Body>
      </div>
    </Surface>
  );
}

// ─── App ─────────────────────────────────────────────────────────────
function App() {
  return (
    <DesignCanvas>
      <DCSection id="typepair" title="00b · Type pairing"
                 subtitle="F · canon · Crimson Pro Italic 500 + Inter Bold 700">
        <DCArtboard id="tp-f-original" label="★ F · original (canon)" width={460} height={300}>
          <TypePairBoard pairLabel="F · Crimson Pro Italic 500 + Inter Bold 700 · CANON"
            faberFont='"Crimson Pro", Georgia, serif' faberWeight={500}
            loomFont='"Inter", sans-serif' loomWeight={700}
            loomLetterSpacing="-0.028em"
            size={64}
            note="★ CANON · Italic 500 + Bold 700. Contraste fuerte entre la voz manual de Faber y el bloque sólido de Loom — leen como roles distintos. La densidad de Loom ancla la marca." />
        </DCArtboard>
      </DCSection>

      <DCSection id="brief" title="00 · Sistema de marca · brief"
                 subtitle="FaberLoom — 5 propuestas conceptuales completas">
        <DCArtboard id="brief-intro"     label="Brief"                width={400} height={360}>
          <IntroBrief />
        </DCArtboard>
        <DCArtboard id="brief-palette"   label="Palette"              width={360} height={360}>
          <PaletteBoard />
        </DCArtboard>
        <DCArtboard id="brief-typography"label="Typography"           width={360} height={360}>
          <TypographyBoard />
        </DCArtboard>
        <DCArtboard id="brief-clear"     label="Clear space"          width={400} height={360}>
          <ClearSpaceBoard />
        </DCArtboard>
        <DCArtboard id="brief-donts"     label="Don'ts"               width={400} height={360}>
          <DontsBoard />
        </DCArtboard>
      </DCSection>

      <ConceptSection
        key_="trama" idx="01" title="Trama tejida"
        subtitle="Urdimbre + trama · evolución del provisional"
        isoKey="trama"
        principle="Tres hilos verticales (urdimbre, ink) que sostienen dos hilos horizontales ondulantes (trama, coral). Estructura + criterio. La forma más literal del telar — por eso debe ser la más precisa."
        fontFaber={'Crimson Pro · Italic 500'}
        fontLoom={'Inter · Bold 700'}
        strokeNote={'1.75 px · linecap round · linejoin round · viewBox 32×32'}
        idea={'Trama operativa · IA prepara estructura, humano teje el sentido.'}
      />

      <DCSection id="book-cover" title="06 · Brand book · cover"
                 subtitle="Tapa + manifiesto + voz">
        <DCArtboard id="bk-cover"      label="Cover"      width={460} height={420}>
          <CoverBoard />
        </DCArtboard>
        <DCArtboard id="bk-manifesto"  label="Manifesto"  width={420} height={420}>
          <ManifestoBoard />
        </DCArtboard>
        <DCArtboard id="bk-voice"      label="Voice"      width={460} height={420}>
          <VoiceBoard />
        </DCArtboard>
      </DCSection>

      <DCSection id="book-apps-1" title="07 · Aplicaciones · digital"
                 subtitle="App icon · favicon · web · social">
        <DCArtboard id="bk-appicon"    label="App icon"   width={520} height={360}>
          <AppIconBoard />
        </DCArtboard>
        <DCArtboard id="bk-web"        label="Web header" width={460} height={360}>
          <WebHeaderBoard />
        </DCArtboard>
        <DCArtboard id="bk-social"     label="Social"     width={460} height={360}>
          <SocialHeaderBoard />
        </DCArtboard>
      </DCSection>

      <DCSection id="book-apps-2" title="08 · Aplicaciones · papel y email"
                 subtitle="Tarjeta · letterhead · firma · slide">
        <DCArtboard id="bk-card"       label="Tarjeta"    width={460} height={360}>
          <BusinessCardBoard />
        </DCArtboard>
        <DCArtboard id="bk-letter"     label="Letterhead" width={420} height={420}>
          <LetterheadBoard />
        </DCArtboard>
        <DCArtboard id="bk-email"      label="Email sig"  width={460} height={300}>
          <EmailSigBoard />
        </DCArtboard>
        <DCArtboard id="bk-slide"      label="Slide"      width={460} height={360}>
          <SlideBoard />
        </DCArtboard>
      </DCSection>

      <DCSection id="book-misuse" title="09 · No hacer · ejemplos visuales"
                 subtitle="Mal uso del sistema">
        <DCArtboard id="bk-misuse"     label="Misuse"     width={620} height={420}>
          <MisuseBoard />
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
