// Brand book — application examples + voice/tone + extended foundations.
// Uses the chosen Trama isotipo + Crimson Pro Italic 500 / Inter Bold 700.

const Iso = IsoTrama;

// ─── Cover ───────────────────────────────────────────────────────────
function CoverBoard() {
  return (
    <Surface bg={PALETTE.cream} pad={0}
      style={{ flexDirection: 'column', justifyContent: 'space-between',
               padding: 40, gap: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
                    alignItems: 'flex-start' }}>
        <Caption>Brand Book · v2 · 2026</Caption>
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 10,
                       color: PALETTE.pizarra, letterSpacing: '0.06em' }}>01 / 14</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column',
                    alignItems: 'flex-start', gap: 18, marginTop: 'auto' }}>
        <Iso s={120} ink={PALETTE.ink} coral={PALETTE.coral} pizarra={PALETTE.pizarra} sw={2.2} />
        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                         fontWeight: 500, fontSize: 90, color: PALETTE.ink,
                         lineHeight: 0.95, letterSpacing: '-0.01em',
                         paddingRight: 6, marginRight: 22 }}>Faber</span>
          <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700,
                         fontSize: 70, color: PALETTE.coral,
                         letterSpacing: '-0.028em', lineHeight: 0.95 }}>Loom</span>
        </div>
        <div style={{ width: 80, height: 1, background: PALETTE.ink, opacity: 0.4 }}/>
        <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                       fontWeight: 400, fontSize: 22, color: PALETTE.pizarra,
                       letterSpacing: '-0.005em' }}>El telar del hacedor.</span>
      </div>
    </Surface>
  );
}

// ─── Manifesto ───────────────────────────────────────────────────────
function ManifestoBoard() {
  return (
    <Surface bg={PALETTE.ink} pad={36} style={{ gap: 22 }}>
      <Caption dark>Manifiesto</Caption>
      <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                     fontWeight: 400, fontSize: 30, color: PALETTE.cream,
                     lineHeight: 1.25, letterSpacing: '-0.005em' }}>
        FaberLoom es el telar<br/>del hacedor moderno:<br/>
        una herramienta donde<br/>
        <span style={{ color: PALETTE.coral }}>el humano profesional</span><br/>
        sigue siendo el tejedor.
      </span>
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <span style={{ fontFamily: 'Inter', fontSize: 11.5, color: 'rgba(244,241,237,0.7)',
                       letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          La IA prepara · vos tejés
        </span>
      </div>
    </Surface>
  );
}

// ─── Voice & tone ────────────────────────────────────────────────────
function VoiceBoard() {
  const Row = ({ ok, badge, txt }) => (
    <div style={{ display: 'grid', gridTemplateColumns: '60px 1fr', gap: 12,
                  alignItems: 'flex-start', padding: '10px 0',
                  borderBottom: `1px solid ${PALETTE.rule}` }}>
      <span style={{ fontFamily: 'Inter', fontSize: 10, fontWeight: 600,
                     color: ok ? PALETTE.coral : PALETTE.pizarra,
                     letterSpacing: '0.08em', textTransform: 'uppercase',
                     marginTop: 2 }}>{badge}</span>
      <Body size={12.5}>{txt}</Body>
    </div>
  );
  return (
    <Surface bg={PALETTE.cream} pad={28}>
      <ArtboardHeader eyebrow="Voice & tone" title="Cómo escribimos" />
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <Row ok badge="Sí" txt="«Preparé tres borradores. Elegí cuál ajustar.»" />
        <Row     badge="No" txt="«¡Listo! 🚀 Generé contenido increíble para vos!»" />
        <Row ok badge="Sí" txt="«Esta respuesta cita el contrato firmado el 4/6.»" />
        <Row     badge="No" txt="«Like a magic, your AI assistant is ready to help.»" />
        <Row ok badge="Sí" txt="«Tu criterio queda en el centro. La IA acerca opciones.»" />
      </div>
      <div style={{ marginTop: 'auto', borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 12 }}>
        <Caption>Pilares</Caption>
        <div style={{ marginTop: 6 }}>
          <Body size={11.5}>Calmo · preciso · respetuoso del oficio. Nunca eufórico, nunca paternalista.</Body>
        </div>
      </div>
    </Surface>
  );
}

// ─── App icon · iOS style ────────────────────────────────────────────
function AppIconBoard() {
  const Icon = ({ size, label, dark }) => (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div style={{ width: size, height: size,
                    borderRadius: size * 0.225,
                    background: dark ? PALETTE.ink : PALETTE.cream,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(0,0,0,0.05)' }}>
        <Iso s={size * 0.62} ink={dark ? PALETTE.cream : PALETTE.ink}
             coral={PALETTE.coral} pizarra={dark ? '#9aa6b1' : PALETTE.pizarra}
             sw={size > 90 ? 2 : 2.4} />
      </div>
      <Caption>{label}</Caption>
    </div>
  );
  return (
    <Surface bg={PALETTE.cream} pad={28}>
      <ArtboardHeader eyebrow="Application · 01" title="App icon · favicon" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    gap: 28 }}>
        <Icon size={120} label="iOS · 120 px" />
        <Icon size={64}  label="App · 64 px" dark />
        <Icon size={32}  label="Tab · 32 px" />
        <Icon size={16}  label="Favicon · 16" />
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 12 }}>
        <Body size={11}>
          Squircle iOS (radius ≈ 22.5%). En 16 px el isotipo se simplifica:
          stroke-width pasa de 2 a 2.4 y el dasharray se reduce a 2/1.5 para mantener legibilidad.
        </Body>
      </div>
    </Surface>
  );
}

// ─── Business card ───────────────────────────────────────────────────
function BusinessCardBoard() {
  const Card = ({ children, bg, dark, label }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <Caption>{label}</Caption>
      <div style={{ width: 270, height: 156, background: bg, borderRadius: 4,
                    boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04)',
                    padding: 18, boxSizing: 'border-box',
                    display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        {children}
      </div>
    </div>
  );
  return (
    <Surface bg={PALETTE.cream} pad={28} style={{ background: '#e9e6e0' }}>
      <ArtboardHeader eyebrow="Application · 02" title="Tarjeta personal · 85 × 55 mm" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    gap: 24 }}>
        <Card label="Frente" bg={PALETTE.cream}>
          <Iso s={28} ink={PALETTE.ink} coral={PALETTE.coral} pizarra={PALETTE.pizarra} sw={2.2}/>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                           fontWeight: 500, fontSize: 19, color: PALETTE.ink, lineHeight: 1 }}>
              Faber<span style={{ fontFamily: 'Inter', fontStyle: 'normal',
                                  fontWeight: 700, color: PALETTE.coral,
                                  marginLeft: 5 }}>Loom</span>
            </span>
            <span style={{ fontFamily: 'Inter', fontSize: 9, color: PALETTE.pizarra,
                           letterSpacing: '0.04em', marginTop: 4 }}>Tejé tu trabajo.</span>
          </div>
        </Card>
        <Card label="Reverso" bg={PALETTE.ink} dark>
          <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 13,
                         color: PALETTE.cream }}>Mariana Suárez</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <span style={{ fontFamily: 'Inter', fontSize: 9.5, color: 'rgba(244,241,237,0.65)',
                           letterSpacing: '0.02em' }}>Head of Operations</span>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 9.5,
                           color: PALETTE.coral, letterSpacing: '0.02em', marginTop: 6 }}>
              mariana@faberloom.com
            </span>
          </div>
        </Card>
      </div>
    </Surface>
  );
}

// ─── Letterhead ──────────────────────────────────────────────────────
function LetterheadBoard() {
  return (
    <Surface bg="#e9e6e0" pad={28}>
      <ArtboardHeader eyebrow="Application · 03" title="Letterhead · A4" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 240, height: 320, background: PALETTE.cream, borderRadius: 2,
                      boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04)',
                      padding: '24px 22px', boxSizing: 'border-box',
                      display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <WordmarkH Iso={Iso} size={14} />
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 7,
                           color: PALETTE.pizarra, letterSpacing: '0.06em' }}>15 / 04 / 2026</span>
          </div>
          <div style={{ width: '100%', height: 1, background: PALETTE.rule }}/>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {Array.from({length: 8}).map((_,i)=>(
              <div key={i} style={{ height: 4, background: 'rgba(31,30,28,0.10)',
                                    borderRadius: 1,
                                    width: `${[100,96,98,92,100,88,94,40][i]}%` }}/>
            ))}
          </div>
          <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 7,
                           color: PALETTE.pizarra, letterSpacing: '0.04em' }}>
              faberloom.com
            </span>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 7,
                           color: PALETTE.pizarra, letterSpacing: '0.04em' }}>
              Buenos Aires · AR
            </span>
          </div>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 10 }}>
        <Body size={11}>Margen 24 mm. Wordmark horizontal a 14 px de altura. Fecha en mono right-aligned.</Body>
      </div>
    </Surface>
  );
}

// ─── Social header (LinkedIn cover) ──────────────────────────────────
function SocialHeaderBoard() {
  return (
    <Surface bg="#e9e6e0" pad={28}>
      <ArtboardHeader eyebrow="Application · 04" title="LinkedIn · cover" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 380, height: 95, background: PALETTE.ink, borderRadius: 6,
                      boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                      padding: '14px 22px', boxSizing: 'border-box',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                           fontWeight: 400, fontSize: 22, color: PALETTE.cream,
                           lineHeight: 1.05 }}>
              La IA prepara.<br/>
              <span style={{ color: PALETTE.coral }}>Vos tejés.</span>
            </span>
            <span style={{ fontFamily: 'Inter', fontSize: 8, color: 'rgba(244,241,237,0.55)',
                           letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              FaberLoom · plataforma de IA para PYMEs
            </span>
          </div>
          <Iso s={64} ink={PALETTE.cream} coral={PALETTE.coral} pizarra="#9aa6b1" sw={2.0}/>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 10 }}>
        <Body size={11}>Cover 1584 × 396 px · contraste cream sobre ink · isotipo a la derecha como ancla visual.</Body>
      </div>
    </Surface>
  );
}

// ─── Email signature ─────────────────────────────────────────────────
function EmailSigBoard() {
  return (
    <Surface bg={PALETTE.cream} pad={28}>
      <ArtboardHeader eyebrow="Application · 05" title="Firma de email" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
        <div style={{ display: 'flex', gap: 14, padding: '14px 0',
                      borderTop: `1.5px solid ${PALETTE.ink}`,
                      borderBottom: `1px solid ${PALETTE.rule}` }}>
          <Iso s={42} ink={PALETTE.ink} coral={PALETTE.coral} pizarra={PALETTE.pizarra} sw={2.2}/>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 13.5,
                           color: PALETTE.ink, letterSpacing: '-0.01em' }}>Mariana Suárez</span>
            <span style={{ fontFamily: 'Inter', fontWeight: 400, fontSize: 11,
                           color: PALETTE.pizarra }}>Head of Operations · FaberLoom</span>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 10.5,
                           color: PALETTE.coral, marginTop: 4 }}>mariana@faberloom.com</span>
          </div>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${PALETTE.rule}`, paddingTop: 10 }}>
        <Body size={11}>Sin imágenes embebidas. Sin tagline en firma — la firma es identificación, no marketing.</Body>
      </div>
    </Surface>
  );
}

// ─── Slide cover ─────────────────────────────────────────────────────
function SlideBoard() {
  return (
    <Surface bg="#e9e6e0" pad={28}>
      <ArtboardHeader eyebrow="Application · 06" title="Slide template · cover" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 360, height: 200, background: PALETTE.cream, borderRadius: 4,
                      boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04)',
                      padding: '24px 28px', boxSizing: 'border-box',
                      display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <WordmarkH Iso={Iso} size={11} />
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 8,
                           color: PALETTE.pizarra }}>Q2 · 2026</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                           fontWeight: 500, fontSize: 30, color: PALETTE.ink,
                           lineHeight: 1.1 }}>
              Cómo la IA<br/>preserva el oficio.
            </span>
            <span style={{ fontFamily: 'Inter', fontWeight: 500, fontSize: 11,
                           color: PALETTE.pizarra, letterSpacing: '0.02em',
                           marginTop: 6 }}>Reporte interno · Operaciones</span>
          </div>
        </div>
      </div>
    </Surface>
  );
}

// ─── Web header (light + dark) ───────────────────────────────────────
function WebHeaderBoard() {
  const Bar = ({ dark }) => (
    <div style={{ width: '100%', padding: '12px 18px', boxSizing: 'border-box',
                  background: dark ? PALETTE.ink : PALETTE.cream,
                  borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  boxShadow: dark ? 'none' : '0 0 0 1px rgba(0,0,0,0.06)' }}>
      <WordmarkH Iso={Iso} size={14}
        faberColor={dark ? PALETTE.cream : PALETTE.ink}
        loomColor={PALETTE.coral}
        ink={dark ? PALETTE.cream : PALETTE.ink}
        coral={PALETTE.coral} />
      <div style={{ display: 'flex', gap: 14 }}>
        {['Producto','Precios','Soporte'].map((s,i)=>(
          <span key={i} style={{ fontFamily: 'Inter', fontSize: 10, fontWeight: 500,
                                 color: dark ? 'rgba(244,241,237,0.7)' : PALETTE.pizarra }}>{s}</span>
        ))}
        <span style={{ fontFamily: 'Inter', fontSize: 10, fontWeight: 600,
                       color: dark ? PALETTE.cream : PALETTE.cream,
                       background: PALETTE.coral, padding: '5px 9px',
                       borderRadius: 4, letterSpacing: '-0.005em' }}>Probar</span>
      </div>
    </div>
  );
  return (
    <Surface bg="#e9e6e0" pad={28}>
      <ArtboardHeader eyebrow="Application · 07" title="Web · navbar · light & dark" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 14 }}>
        <Bar />
        <Bar dark />
      </div>
    </Surface>
  );
}

// ─── Misuse · do not ─────────────────────────────────────────────────
function MisuseBoard() {
  const Cell = ({ label, children }) => (
    <div style={{ flex: 1, padding: 14, display: 'flex', flexDirection: 'column',
                  gap: 10, alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
      {children}
      <span style={{ position: 'absolute', top: 8, left: 10, fontFamily: 'Inter',
                     fontSize: 9, fontWeight: 600, color: PALETTE.coral,
                     letterSpacing: '0.06em', textTransform: 'uppercase' }}>✕ {label}</span>
    </div>
  );
  return (
    <Surface bg={PALETTE.cream} pad={0} style={{ gap: 0 }}>
      <div style={{ padding: '24px 26px 0 26px' }}>
        <ArtboardHeader eyebrow="Misuse" title="No hacer · ejemplos" />
      </div>
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                    gridTemplateRows: '1fr 1fr', borderTop: `1px solid ${PALETTE.rule}` }}>
        <Cell label="No estirar">
          <div style={{ transform: 'scaleX(1.45)', transformOrigin: 'center' }}>
            <WordmarkH Iso={Iso} size={20} />
          </div>
        </Cell>
        <Cell label="No rotar">
          <div style={{ transform: 'rotate(-12deg)' }}>
            <WordmarkH Iso={Iso} size={20} />
          </div>
        </Cell>
        <Cell label="No recolorear">
          <WordmarkH Iso={Iso} size={20}
            faberColor="#7A8E6D" loomColor="#B88A4A"
            ink="#7A8E6D" coral="#B88A4A" />
        </Cell>
        <Cell label="No agregar sombras">
          <div style={{ filter: 'drop-shadow(0 6px 8px rgba(0,0,0,0.4))' }}>
            <WordmarkH Iso={Iso} size={20} />
          </div>
        </Cell>
        <Cell label="Mal contraste">
          <div style={{ background: PALETTE.coral, padding: '12px 16px', borderRadius: 4 }}>
            <WordmarkH Iso={Iso} size={18}
              faberColor={PALETTE.ink} loomColor={PALETTE.cream}
              ink={PALETTE.ink} coral={PALETTE.cream} />
          </div>
        </Cell>
        <Cell label="No mezclar tipos">
          <span style={{ fontFamily: 'Comic Sans MS, cursive', fontSize: 24,
                         color: PALETTE.ink }}>FaberLoom</span>
        </Cell>
      </div>
    </Surface>
  );
}

Object.assign(window, {
  CoverBoard, ManifestoBoard, VoiceBoard, AppIconBoard, BusinessCardBoard,
  LetterheadBoard, SocialHeaderBoard, EmailSigBoard, SlideBoard, WebHeaderBoard,
  MisuseBoard,
});
