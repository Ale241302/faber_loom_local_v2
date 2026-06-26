// FaberLoom icon canvas — foundations, custom 9, UI canon, sample compositions.

const cream  = PALETTE.cream;
const ink    = PALETTE.ink;
const coral  = PALETTE.coral;
const pizarra= PALETTE.pizarra;
const rule   = PALETTE.rule;

// ─── Foundations · brief ─────────────────────────────────────────────
function IconBrief() {
  return (
    <Surface bg={cream} pad={32}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Caption>FaberLoom · Iconos · v1</Caption>
        <H size={24} italic weight={500}>Herramientas de un artesano disciplinado.</H>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 14, paddingTop: 6 }}>
        <Body size={12.5}>
          Familia line-art sobre grilla 24×24, stroke 1.75, currentColor. Dos
          subfamilias: <b>9 iconos custom</b> que cargan el ADN de la trama
          (puntada, anclaje humano, hilos cruzados), y <b>~30 iconos UI canon</b>{' '}
          basados en Lucide y redibujados con el mismo lenguaje.
        </Body>
        <Body size={12.5}>
          Si un icono podría aparecer en cualquier SaaS genérico, falló. Los
          custom prueban el carácter; los UI sostienen la consistencia.
        </Body>
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 14 }}>
        <Body size={11.5}>
          <i style={{ color: pizarra }}>« La IA prepara · vos tejés. »</i>
        </Body>
      </div>
    </Surface>
  );
}

// ─── Grid + stroke specimen ──────────────────────────────────────────
function IconGridBoard() {
  // 24×24 grid scaled to 240
  const cell = 240 / 24;
  const lines = [];
  for (let i = 0; i <= 24; i++) {
    lines.push(
      <line key={'v'+i} x1={i*cell} y1={0} x2={i*cell} y2={240}
            stroke={i===12 ? coral : 'rgba(31,30,28,0.10)'} strokeWidth={i===12 ? 0.6 : 0.4}/>
    );
    lines.push(
      <line key={'h'+i} x1={0} y1={i*cell} x2={240} y2={i*cell}
            stroke={i===12 ? coral : 'rgba(31,30,28,0.10)'} strokeWidth={i===12 ? 0.6 : 0.4}/>
    );
  }
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 01" title="Grilla 24 × 24 · canvas" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ position: 'relative', width: 240, height: 240,
                      border: `1px solid ${rule}`, borderRadius: 4, overflow: 'hidden' }}>
          <svg width={240} height={240} style={{ position: 'absolute', inset: 0 }}>
            {lines}
            {/* safe area · 22×22 inset */}
            <rect x={cell} y={cell} width={240-2*cell} height={240-2*cell}
                  fill="none" stroke={coral} strokeWidth={0.8} strokeDasharray="3 2"/>
          </svg>
          <div style={{ position: 'absolute', inset: 0,
                        display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <IconBrandLoom size={208} color={ink}/>
          </div>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 12, display: 'grid',
                    gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <Body size={11}><b>Canvas</b> · 24 × 24 · ejes en (12, 12).</Body>
        <Body size={11}><b>Safe area</b> · 22 × 22 · línea coral punteada.</Body>
        <Body size={11}><b>Stroke</b> · 1.75 px · linecap & linejoin round.</Body>
        <Body size={11}><b>Color</b> · currentColor · hereda CSS.</Body>
      </div>
    </Surface>
  );
}

// ─── Stroke comparison ladder ────────────────────────────────────────
function IconStrokeBoard() {
  const sizes = [
    { sw: 1.5, label: '1.5' },
    { sw: 1.75, label: '1.75 · canon' },
    { sw: 2.0, label: '2.0' },
  ];
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 02" title="Stroke ladder" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                    justifyContent: 'space-around' }}>
        {sizes.map(s => (
          <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
            <Caption>{s.label}</Caption>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 16,
                          color: ink }}>
              <IconBrandLoom size={48} sw={s.sw} />
              <IconCriterio size={48} sw={s.sw} />
              <IconWorkLoom size={48} sw={s.sw} />
              <IconSearch size={48} sw={s.sw} />
              <IconUser size={48} sw={s.sw} />
            </div>
          </div>
        ))}
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 10 }}>
        <Body size={11}>1.75 es el default. 1.5 sólo a 14 px o más chico; 2.0 sólo a 32 px o más grande.</Body>
      </div>
    </Surface>
  );
}

// ─── Sizing ladder ──────────────────────────────────────────────────
function IconSizingBoard() {
  const sizes = [14, 16, 20, 24, 32, 48];
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 03" title="Sizing · escalas canónicas" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end',
                    justifyContent: 'space-around', padding: '12px 6px',
                    background: 'rgba(31,30,28,0.025)',
                    border: `1px solid ${rule}`, borderRadius: 8 }}>
        {sizes.map(s => (
          <div key={s} style={{ display: 'flex', flexDirection: 'column',
                                alignItems: 'center', gap: 8 }}>
            <div style={{ height: 56, display: 'flex', alignItems: 'center', color: ink }}>
              <IconBrandLoom size={s} />
            </div>
            <Caption>{s} px</Caption>
          </div>
        ))}
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 12,
                    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
        <Body size={11}><b>14</b> · inline en texto (badges, status)</Body>
        <Body size={11}><b>16</b> · UI estándar (tabs, items, botones)</Body>
        <Body size={11}><b>20</b> · sidebar nav, headers de cards</Body>
        <Body size={11}><b>24</b> · acentos, CTA, tabs principales</Body>
        <Body size={11}><b>32</b> · estados grandes, vacíos</Body>
        <Body size={11}><b>48+</b> · branding, app icon</Body>
      </div>
    </Surface>
  );
}

// ─── Color tokens ────────────────────────────────────────────────────
function IconTokensBoard() {
  const Row = ({ token, value, swatch, use, demoColor }) => (
    <div style={{ display: 'grid', gridTemplateColumns: '24px 100px 1fr 28px',
                  gap: 12, alignItems: 'center', padding: '8px 0',
                  borderBottom: `1px solid ${rule}` }}>
      <div style={{ width: 14, height: 14, borderRadius: 3, background: swatch,
                    boxShadow: 'inset 0 0 0 1px rgba(0,0,0,0.08)' }}/>
      <span style={{ fontFamily: 'ui-monospace, SF Mono, monospace', fontSize: 10.5,
                     color: ink, letterSpacing: '0.01em' }}>{token}</span>
      <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 11, color: pizarra }}>{use}</span>
      <div style={{ color: demoColor, display: 'flex', justifyContent: 'flex-end' }}>
        <IconCheck size={18}/>
      </div>
    </div>
  );
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="Foundations · 04" title="Tokens de color" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Row token="--icon-default"   value="#1F1E1C" swatch={ink}     use="UI estándar · sidebar · tabs" demoColor={ink}/>
        <Row token="--icon-secondary" value="#5A6B7C" swatch={pizarra} use="Disabled · contexto frío · meta" demoColor={pizarra}/>
        <Row token="--icon-accent"    value="#C96442" swatch={coral}   use="Decisiones · CTA · selected · brand" demoColor={coral}/>
        <Row token="--icon-warn"      value="#B88A4A" swatch="#B88A4A" use="Atención · knowledge a indexar" demoColor="#B88A4A"/>
        <Row token="--icon-evidence"  value="#6E1F2B" swatch="#6E1F2B" use="Forensic · compliance · audit" demoColor="#6E1F2B"/>
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 10 }}>
        <Body size={11}>
          Default: <b>currentColor</b>. El color sale del CSS variable del componente padre — el icono nunca define color absoluto salvo en branding.
        </Body>
      </div>
    </Surface>
  );
}

// ─── Do / Don't ──────────────────────────────────────────────────────
function IconDontsBoard() {
  const Cell = ({ ok, label, children }) => (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center', gap: 10,
                  padding: 18, position: 'relative' }}>
      <span style={{ position: 'absolute', top: 8, left: 12, fontFamily: 'Inter',
                     fontSize: 9, fontWeight: 600,
                     color: ok ? '#7A8E6D' : coral,
                     letterSpacing: '0.06em', textTransform: 'uppercase' }}>
        {ok ? '✓ ' : '✕ '}{label}
      </span>
      <div style={{ color: ink }}>{children}</div>
    </div>
  );
  return (
    <Surface bg={cream} pad={0} style={{ gap: 0 }}>
      <div style={{ padding: '24px 26px 0 26px' }}>
        <ArtboardHeader eyebrow="Foundations · 05" title="Do / Don't" />
      </div>
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                    gridTemplateRows: '1fr 1fr', borderTop: `1px solid ${rule}` }}>
        <Cell ok label="stroke 1.75 round"><IconWorkLoom size={48}/></Cell>
        <Cell    label="stroke pesado">
          <IconWorkLoom size={48} sw={3.5}/>
        </Cell>
        <Cell    label="filled">
          <svg width={48} height={48} viewBox="0 0 24 24" fill={ink}>
            <rect x="3.5" y="3.5" width="17" height="17" rx="1.5"/>
          </svg>
        </Cell>
        <Cell ok label="line-art 1 color"><IconCriterio size={48}/></Cell>
        <Cell    label="duotone">
          <svg width={48} height={48} viewBox="0 0 24 24" fill="none"
               stroke={ink} strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 17 11 11" stroke={coral}/>
            <path d="M11 11 19 19" stroke={pizarra}/>
            <path d="M19 5 11 11"/>
            <circle cx="11" cy="11" r="1.7" fill={coral} stroke="none"/>
          </svg>
        </Cell>
        <Cell    label="con sombra">
          <div style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.35))' }}>
            <IconCriterio size={48}/>
          </div>
        </Cell>
      </div>
    </Surface>
  );
}

// ─── Custom icon detail card ─────────────────────────────────────────
function CustomDetailBoard({ entry }) {
  const { Comp, name, label, concept } = entry;
  return (
    <Surface bg={cream} pad={28}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Caption>{name}</Caption>
        <H size={20} italic weight={500}>{label}</H>
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    gap: 28, padding: '8px 0' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 110, height: 110, display: 'flex',
                        alignItems: 'center', justifyContent: 'center',
                        background: 'rgba(31,30,28,0.03)', borderRadius: 10,
                        color: ink }}>
            <Comp size={64}/>
          </div>
          <Caption>64 px</Caption>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'flex-start' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: ink }}>
            <Comp size={32}/><Caption>32</Caption>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: ink }}>
            <Comp size={24}/><Caption>24</Caption>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: ink }}>
            <Comp size={16}/><Caption>16</Caption>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10,
                        background: ink, padding: '8px 10px', borderRadius: 4, color: cream }}>
            <Comp size={20}/>
            <span style={{ fontFamily: 'Inter', fontSize: 9.5, color: 'rgba(244,241,237,0.7)',
                           letterSpacing: '0.04em' }}>on ink</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: coral }}>
            <Comp size={20}/>
            <span style={{ fontFamily: 'Inter', fontSize: 9.5, color: pizarra,
                           letterSpacing: '0.04em' }}>accent</span>
          </div>
        </div>
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 12 }}>
        <Body size={11.5}>{concept}</Body>
      </div>
    </Surface>
  );
}

// ─── UI group grid ───────────────────────────────────────────────────
function UIGroupBoard({ title, subtitle, icons }) {
  const Tile = ({ Comp, name }) => (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center',
                  gap: 6, padding: '14px 6px',
                  border: `1px solid ${rule}`, borderRadius: 6,
                  background: 'rgba(31,30,28,0.015)' }}>
      <div style={{ height: 32, display: 'flex', alignItems: 'center', color: ink }}>
        <Comp size={24}/>
      </div>
      <span style={{ fontFamily: 'ui-monospace, SF Mono, monospace', fontSize: 9.5,
                     color: pizarra, letterSpacing: '0.01em' }}>{name}</span>
    </div>
  );
  return (
    <Surface bg={cream} pad={26}>
      <ArtboardHeader eyebrow="UI canon" title={title} />
      <div style={{ marginTop: -8 }}>
        <Body size={11}>{subtitle}</Body>
      </div>
      <div style={{ flex: 1, display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(82px, 1fr))',
                    gap: 8, marginTop: 12, alignContent: 'flex-start' }}>
        {icons.map(([compName, name]) => (
          <Tile key={name} Comp={window[compName]} name={name}/>
        ))}
      </div>
    </Surface>
  );
}

// ─── Sample 1 · Sidebar with nav icons ───────────────────────────────
function SampleSidebarBoard() {
  const Item = ({ Comp, label, active, badge, badgeColor }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10,
                  padding: '8px 12px',
                  background: active ? 'rgba(201,100,66,0.08)' : 'transparent',
                  borderRadius: 5,
                  color: active ? coral : ink }}>
      <Comp size={18}/>
      <span style={{ flex: 1, fontFamily: 'Inter', fontSize: 12,
                     fontWeight: active ? 600 : 500,
                     letterSpacing: '-0.01em' }}>{label}</span>
      {badge && (
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 9,
                       color: badgeColor, letterSpacing: '0.04em' }}>{badge}</span>
      )}
    </div>
  );
  const Section = ({ label }) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '14px 12px 6px 12px' }}>
      <span style={{ fontFamily: 'Inter', fontSize: 9.5, fontWeight: 600,
                     color: pizarra, letterSpacing: '0.08em',
                     textTransform: 'uppercase' }}>{label}</span>
      <IconPlus size={12} color={pizarra}/>
    </div>
  );
  return (
    <Surface bg="#e9e6e0" pad={20}>
      <ArtboardHeader eyebrow="Sample · 01" title="Sidebar · navegación principal" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 260, background: cream, borderRadius: 8,
                      boxShadow: '0 6px 20px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04)',
                      padding: '12px 0', display: 'flex', flexDirection: 'column' }}>
          {/* topbar mini */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8,
                        padding: '4px 14px 12px 14px',
                        borderBottom: `1px solid ${rule}` }}>
            <IconBrandLoom size={20} color={coral}/>
            <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                           fontWeight: 500, fontSize: 14, color: ink }}>Faber</span>
            <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 12,
                           color: coral, letterSpacing: '-0.025em' }}>Loom</span>
            <div style={{ flex: 1 }}/>
            <IconChevronsLeft size={14} color={pizarra}/>
          </div>
          <div style={{ padding: '8px 6px' }}>
            <Item Comp={IconSearch}     label="Buscar · ⌘K"/>
            <Item Comp={IconWorkLoom}   label="Mesa de Control" active/>
            <Item Comp={IconInbox}      label="Inbox" badge="12" badgeColor={coral}/>
            <Item Comp={IconSpaceLoom}  label="SpaceLoom"/>
          </div>
          <Section label="Workspaces"/>
          <div style={{ padding: '0 6px' }}>
            <Item Comp={IconStackLoom}  label="StackLoom"/>
            <Item Comp={IconLibrary}    label="Conocimiento" badge="◷" badgeColor="#B88A4A"/>
            <Item Comp={IconUsers}      label="Usuarios"/>
          </div>
          <Section label="Sistema"/>
          <div style={{ padding: '0 6px' }}>
            <Item Comp={IconLearningClock} label="Aprendizaje" badge="◷" badgeColor="#B88A4A"/>
            <Item Comp={IconSettings}      label="Configuración"/>
          </div>
        </div>
      </div>
    </Surface>
  );
}

// ─── Sample 2 · WorkLoom card + Inbox + Sidepanel ────────────────────
function SampleCardsBoard() {
  // WorkLoom card
  const Card = () => (
    <div style={{ background: cream, borderRadius: 8,
                  boxShadow: '0 4px 14px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04)',
                  padding: 14, display: 'flex', flexDirection: 'column', gap: 10, width: 220 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4,
                       padding: '3px 7px', background: 'rgba(201,100,66,0.10)',
                       borderRadius: 3, color: coral }}>
          <IconCriterio size={12}/>
          <span style={{ fontFamily: 'Inter', fontSize: 9, fontWeight: 700,
                         letterSpacing: '0.08em' }}>TU CRITERIO</span>
        </span>
        <div style={{ flex: 1 }}/>
        <IconHourglass size={13} color="#B88A4A"/>
      </div>
      <span style={{ fontFamily: '"Crimson Pro", serif', fontStyle: 'italic',
                     fontWeight: 500, fontSize: 16, color: ink, lineHeight: 1.2 }}>
        Aprobar borrador para Fragua S.R.L.
      </span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: pizarra }}>
        <IconUserCircle size={14}/>
        <span style={{ fontFamily: 'Inter', fontSize: 10.5 }}>Mariana S. · Ops</span>
      </div>
      <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
        <button style={{ flex: 1, background: coral, color: cream, border: 'none',
                         padding: '6px 8px', borderRadius: 4,
                         display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
                         fontFamily: 'Inter', fontSize: 10.5, fontWeight: 600,
                         letterSpacing: '-0.005em', cursor: 'pointer' }}>
          <IconCheck size={12}/> Aprobar
        </button>
        <button style={{ background: 'transparent', color: pizarra,
                         border: `1px solid ${rule}`, padding: '6px 8px', borderRadius: 4,
                         display: 'flex', alignItems: 'center', gap: 4,
                         fontFamily: 'Inter', fontSize: 10.5 }}>
          <IconEdit size={12}/>
        </button>
        <button style={{ background: 'transparent', color: pizarra,
                         border: `1px solid ${rule}`, padding: '6px 8px', borderRadius: 4,
                         display: 'flex', alignItems: 'center', gap: 4,
                         fontFamily: 'Inter', fontSize: 10.5 }}>
          <IconX size={12}/>
        </button>
      </div>
    </div>
  );

  // Inbox item
  const InboxItem = () => (
    <div style={{ background: cream, borderRadius: 6,
                  boxShadow: '0 4px 14px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04)',
                  padding: '10px 12px', display: 'flex', alignItems: 'center', gap: 10,
                  width: 240 }}>
      <IconMail size={16} color={pizarra}/>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 11.5,
                       color: ink, letterSpacing: '-0.005em' }}>
          Pago vencido · cliente #4218
        </span>
        <span style={{ fontFamily: 'Inter', fontSize: 10, color: pizarra }}>
          Manejado por agente · resumen pendiente
        </span>
      </div>
      <IconAlertCircle size={14} color="#B88A4A"/>
    </div>
  );

  // Sidepanel right
  const SidepanelItem = ({ Comp, label, indicator }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8,
                  padding: '7px 10px', borderRadius: 4 }}>
      <Comp size={14} color={ink}/>
      <span style={{ flex: 1, fontFamily: 'Inter', fontSize: 11, color: ink }}>{label}</span>
      {indicator}
    </div>
  );

  const Sidepanel = () => (
    <div style={{ background: cream, borderRadius: 8, width: 220,
                  boxShadow: '0 4px 14px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04)',
                  padding: '10px 4px', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <div style={{ display: 'flex', gap: 4, padding: '0 8px 8px 8px',
                    borderBottom: `1px solid ${rule}` }}>
        {[['IconUsers','Agentes'],['IconSliders','Skills'],['IconLibrary','Conoc.']].map(([c,l],i)=>(
          <span key={l} style={{ display: 'inline-flex', alignItems: 'center', gap: 4,
                                  padding: '4px 7px', borderRadius: 3,
                                  background: i===0 ? 'rgba(31,30,28,0.06)' : 'transparent',
                                  color: ink }}>
            {React.createElement(window[c], { size: 12 })}
            <span style={{ fontFamily: 'Inter', fontSize: 9.5, fontWeight: 600,
                           letterSpacing: '-0.005em' }}>{l}</span>
          </span>
        ))}
      </div>
      <SidepanelItem Comp={IconUserCircle} label="Aurora · ops" indicator={<IconCircleFill size={9} color={coral}/>}/>
      <SidepanelItem Comp={IconUserCircle} label="Forge · finance" indicator={<IconCircle size={9} color={pizarra}/>}/>
      <SidepanelItem Comp={IconUserCircle} label="Lyra · billing"
        indicator={<IconAlertCircle size={11} color="#B88A4A"/>}/>
      <SidepanelItem Comp={IconUserCircle} label="Onyx · legal"
        indicator={<IconLearningClock size={11} color="#B88A4A"/>}/>
    </div>
  );

  return (
    <Surface bg="#e9e6e0" pad={26}>
      <ArtboardHeader eyebrow="Sample · 02" title="Card · Inbox · Sidepanel" />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    gap: 18, flexWrap: 'wrap' }}>
        <Card/>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <InboxItem/>
          <InboxItem/>
        </div>
        <Sidepanel/>
      </div>
    </Surface>
  );
}

// ─── App ─────────────────────────────────────────────────────────────
function IconsApp() {
  return (
    <DesignCanvas>
      <DCSection id="foundations" title="00 · Foundations"
                 subtitle="Grilla, stroke, sizing, tokens, do/don't">
        <DCArtboard id="f-brief"   label="Brief"          width={420} height={360}>
          <IconBrief/>
        </DCArtboard>
        <DCArtboard id="f-grid"    label="Grilla 24×24"   width={400} height={420}>
          <IconGridBoard/>
        </DCArtboard>
        <DCArtboard id="f-stroke"  label="Stroke ladder"  width={420} height={360}>
          <IconStrokeBoard/>
        </DCArtboard>
        <DCArtboard id="f-sizing"  label="Sizing"         width={460} height={300}>
          <IconSizingBoard/>
        </DCArtboard>
        <DCArtboard id="f-tokens"  label="Tokens"         width={460} height={360}>
          <IconTokensBoard/>
        </DCArtboard>
        <DCArtboard id="f-donts"   label="Do / Don't"     width={520} height={360}>
          <IconDontsBoard/>
        </DCArtboard>
      </DCSection>

      <DCSection id="custom" title="01 · Iconos custom · brand DNA"
                 subtitle="9 iconos con la trama / oficio / anclaje humano">
        {CUSTOM_ICONS.map(entry => (
          <DCArtboard key={entry.name} id={`c-${entry.name}`} label={entry.label}
                      width={420} height={300}>
            <CustomDetailBoard entry={entry}/>
          </DCArtboard>
        ))}
      </DCSection>

      <DCSection id="ui-canon" title="02 · UI canon · ~30 Lucide-style"
                 subtitle="Redibujados al lenguaje FaberLoom · stroke 1.75 · 24×24">
        {UI_GROUPS.map(group => (
          <DCArtboard key={group.title} id={`ui-${group.title}`} label={group.title}
                      width={460} height={300}>
            <UIGroupBoard {...group}/>
          </DCArtboard>
        ))}
      </DCSection>

      <DCSection id="samples" title="03 · Sample compositions"
                 subtitle="Iconos en uso real · sidebar + cards + sidepanel">
        <DCArtboard id="s-sidebar"  label="Sidebar"   width={400} height={500}>
          <SampleSidebarBoard/>
        </DCArtboard>
        <DCArtboard id="s-cards"    label="Cards · sidepanel"   width={760} height={420}>
          <SampleCardsBoard/>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<IconsApp />);
