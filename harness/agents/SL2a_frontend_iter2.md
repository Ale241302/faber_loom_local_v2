Resumen:
- Implementé el shell frontend SL0 con React 18 UMD + Babel standalone en `app/static/index.html`.
- Reemplacé `app/static/js/app.jsx` por una app React mínima: topbar con logo FaberLoom, rail izquierdo con modos **Operar / Aprender / Admin**, selector de workspace vía `/api/workspaces`, canvas SpaceLoom, lista visual de chats, composer no-op y panel de costuras contract-first.
- Reemplacé `app/static/css/main.css` con tokens de marca, paleta aprobada, tipografías EB Garamond / Geist / Geist Mono, layout desktop pywebview y SVG icons `24×24`, `stroke 1.75`, `currentColor`.
- Ajusté `app/src/main.py` para dejar versión `sl0` y título pywebview correcto apuntando a `http://127.0.0.1:8000/static/index.html`.
- Verifiqué con `.venv` que `/static/index.html`, `/static/css/main.css`, `/static/js/app.jsx` y `/api/workspaces` respondan `200`.
- Ejecuté `graphify update .` después de modificar código.

```jsx:app/static/js/app.jsx
const { useEffect, useMemo, useState } = React;

const MODES = [
  { id: "operar", label: "Operar" },
  { id: "aprender", label: "Aprender" },
  { id: "admin", label: "Admin" },
];

const NAV = {
  operar: [
    { id: "space", label: "SpaceLoom", sub: "Canvas y chat", badge: "SL0", icon: "loom" },
    { id: "workloom", label: "WorkLoom", sub: "Cola HITL", badge: "SL3", icon: "check" },
  ],
  aprender: [
    { id: "kb", label: "Knowledge Base", sub: "Fuentes y citas", badge: "SL2", icon: "book" },
    { id: "routines", label: "Routine Hub", sub: "Skills portables", badge: "SL3", icon: "spark" },
  ],
  admin: [
    { id: "settings", label: "Ajustes", sub: "Router y proveedor", badge: "SL1", icon: "settings" },
    { id: "audit", label: "Auditoría", sub: "JSONL hoy", badge: "SL0", icon: "audit" },
  ],
};

const SEEDED_CHATS = [
  { id: "draft-intake", title: "Borrador sin iniciar", snippet: "La conversación arranca en SL1a. Este hilo deja listo el shell visual.", time: "Ahora" },
  { id: "mwt-space", title: "MWT · espacio demo", snippet: "Contexto local sembrado; sin mensajes reales todavía.", time: "Seed" },
];

function cx(...parts) { return parts.filter(Boolean).join(" "); }

function readBootstrap() {
  const boot = window.__SPACELOOM_BOOTSTRAP__;
  if (!boot || typeof boot !== "object") return null;
  const workspaces = Array.isArray(boot.workspaces) ? boot.workspaces : [];
  return { workspaces, activeWorkspaceId: boot.activeWorkspaceId || boot.active_workspace_id || (workspaces[0] && workspaces[0].id) || null };
}

function Icon({ name, size = 24 }) {
  const cls = `icon${size === 16 ? " icon-sm" : ""}`;
  const common = { className: cls, viewBox: "0 0 24 24", "aria-hidden": "true" };
  if (name === "loom") return <svg {...common}><path d="M7 3.5V9.5M7 14.5V20.5M12 3.5V4.5M12 9.5V14.5M12 19.5V20.5M17 3.5V9.5M17 14.5V20.5"/><path d="M3.5 7H4.5M9.5 7H14.5M19.5 7H20.5M3.5 12H9.5M14.5 12H20.5M3.5 17H4.5M9.5 17H14.5M19.5 17H20.5"/></svg>;
  if (name === "menu") return <svg {...common}><path d="M4 7h16M4 12h16M4 17h16"/></svg>;
  if (name === "search") return <svg {...common}><circle cx="10.5" cy="10.5" r="5.5"/><path d="M15 15l5 5"/></svg>;
  if (name === "send") return <svg {...common}><path d="M4 12 20 4l-4 16-4-7-8-1Z"/><path d="M12 13 20 4"/></svg>;
  if (name === "book") return <svg {...common}><path d="M5 4.5h9a3 3 0 0 1 3 3v12H8a3 3 0 0 0-3 3v-18Z"/><path d="M5 18.5h9a3 3 0 0 1 3 3"/></svg>;
  if (name === "check") return <svg {...common}><path d="M5 12.5 9.5 17 19 7"/><path d="M4 4h16v16H4z"/></svg>;
  if (name === "spark") return <svg {...common}><path d="M12 3.5 13.8 9l5.7 1.8-5.7 1.8L12 18l-1.8-5.4-5.7-1.8L10.2 9 12 3.5Z"/><path d="M18 16.5 19 19l2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1 1-2.5Z"/></svg>;
  if (name === "settings") return <svg {...common}><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z"/><path d="M19 12.2h2M3 12.2h2M17 6.8l1.4-1.4M5.6 18.8 7 17.4M17 17.4l1.4 1.4M5.6 5.4 7 6.8"/></svg>;
  if (name === "audit") return <svg {...common}><path d="M7 3.5h7l3 3v14H7z"/><path d="M14 3.5v4h4M9.5 11h5M9.5 15h5M9.5 18h3"/></svg>;
  if (name === "shield") return <svg {...common}><path d="M12 3.5 19 6v5.5c0 4.5-3 7.4-7 9-4-1.6-7-4.5-7-9V6l7-2.5Z"/><path d="M9 12l2 2 4-4"/></svg>;
  if (name === "database") return <svg {...common}><ellipse cx="12" cy="5.5" rx="6.5" ry="2.5"/><path d="M5.5 5.5v6c0 1.4 2.9 2.5 6.5 2.5s6.5-1.1 6.5-2.5v-6"/><path d="M5.5 11.5v6c0 1.4 2.9 2.5 6.5 2.5s6.5-1.1 6.5-2.5v-6"/></svg>;
  if (name === "route") return <svg {...common}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H12a4 4 0 0 1 0 8 4 4 0 0 0 0 8h3.5"/></svg>;
  return <svg {...common}><circle cx="12" cy="12" r="8.5"/><path d="M12 11.5V16M12 8h.01"/></svg>;
}

function BrandMark() { return <Icon name="loom" />; }

function Topbar() {
  return <header className="topbar">
    <button type="button" className="icon-button" aria-label="Abrir menú"><Icon name="menu" /></button>
    <div className="brand" aria-label="FaberLoom SpaceLoom">
      <span className="brand-mark"><BrandMark /></span>
      <span className="brand-word"><span className="brand-name"><span className="brand-faber">Faber</span><span className="brand-loom">Loom</span></span><span className="brand-sub">SpaceLoom · SL0 shell</span></span>
    </div>
    <div className="command-bar" role="button" tabIndex="0" aria-label="Buscar o ejecutar"><Icon name="search" size={16}/><span>Buscar o preparar contexto…</span><kbd>Ctrl K</kbd></div>
    <div className="topbar-actions"><span className="status-chip"><span className="status-dot" aria-hidden="true"/>Local-first</span></div>
  </header>;
}
function Rail({ mode, setMode, nav, setNav, workspaces, activeWorkspaceId, setActiveWorkspaceId, status }) {
  const items = NAV[mode] || NAV.operar;
  return <aside className="rail">
    <div className="mode-group" aria-label="Modos de SpaceLoom">
      {MODES.map((item) => <button key={item.id} type="button" className={cx("mode-button", mode === item.id && "is-active")} onClick={() => { setMode(item.id); setNav((NAV[item.id] || [])[0].id); }}>{item.label}</button>)}
    </div>
    <section className="rail-section">
      <div className="rail-label"><span>Workspace</span><span>{status}</span></div>
      <div className="workspace-card">
        <select className="workspace-select" value={activeWorkspaceId || ""} onChange={(event) => setActiveWorkspaceId(event.target.value || null)} disabled={!workspaces.length} aria-label="Workspace activo">
          {!workspaces.length && <option value="">Sin workspace</option>}
          {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.name}</option>)}
        </select>
        <div className="workspace-meta"><Icon name="shield" size={16}/><span>Context(workspace_id) listo para toda query</span></div>
      </div>
    </section>
    <section className="rail-section">
      <div className="rail-label"><span>{MODES.find((item) => item.id === mode).label}</span><span>Vistas</span></div>
      <nav className="nav-stack" aria-label="Navegación principal">
        {items.map((item) => <button key={item.id} type="button" className={cx("nav-item", nav === item.id && "is-active")} onClick={() => setNav(item.id)}>
          <Icon name={item.icon}/><span><span className="nav-title">{item.label}</span><span className="nav-sub">{item.sub}</span></span><span className="nav-badge">{item.badge}</span>
        </button>)}
      </nav>
    </section>
    <div className="rail-note"><div className="rail-note-title"><Icon size={16}/>SL0 no-op shell</div><p>El chat aún no llama modelos ni persiste mensajes. La UI queda preparada para el router de SL1a y KB con fuentes en SL1b/SL2.</p></div>
  </aside>;
}

function ContextStrip({ activeWorkspace }) {
  return <div className="context-strip">
    <span className="context-dot" aria-hidden="true"/>
    <div className="context-main">
      <div className="context-title"><h1>{activeWorkspace ? activeWorkspace.name : "Sin espacio activo"}</h1>{activeWorkspace && <span className="context-badge">{activeWorkspace.slug || activeWorkspace.id}</span>}</div>
      <div className="context-sub">{activeWorkspace ? "Espacio activo · estado local persistido · listo para dogfood visual" : "Esperando la respuesta de /api/workspaces o bootstrap del backend"}</div>
    </div>
    <div className="context-actions"><span className="pill pill-muted"><Icon name="route" size={16}/>Router en SL1a</span><span className="pill pill-muted"><Icon name="database" size={16}/>KB en SL2</span><span className="pill pill-muted"><Icon name="shield" size={16}/>Sellado futuro</span></div>
  </div>;
}

function ChatList({ activeChatId, setActiveChatId }) {
  return <section className="panel" aria-label="Lista de chats">
    <div className="panel-header"><div><div className="panel-kicker">SpaceLoom</div><div className="panel-title">Chats</div></div><span className="nav-badge">Vacío</span></div>
    <div className="chat-list">{SEEDED_CHATS.map((chat) => <button key={chat.id} type="button" className={cx("chat-card", activeChatId === chat.id && "is-active")} onClick={() => setActiveChatId(chat.id)}>
      <span className="chat-row"><span className="chat-title">{chat.title}</span><span className="chat-time">{chat.time}</span></span><span className="chat-snippet">{chat.snippet}</span>
    </button>)}</div>
  </section>;
}

function EmptyMessages({ activeWorkspace }) {
  return <div className="empty-state"><div className="empty-loom" aria-hidden="true"><BrandMark/></div><h3>El telar está listo.</h3><p>Este shell abre el canvas de SpaceLoom con el contexto de {activeWorkspace ? activeWorkspace.name : "tu workspace"}. La generación real de mensajes queda fuera de SL0 y entra con el router mínimo de SL1a.</p></div>;
}

function Composer() {
  const [draft, setDraft] = useState("");
  return <form className="composer-shell" onSubmit={(event) => event.preventDefault()} aria-label="Composer de chat visual">
    <div className="composer"><textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Escribe el encargo del borrador… (envío real disponible en SL1a)" rows="2"/><button type="submit" className="send-button" disabled title="La ejecución real empieza en SL1a"><Icon name="send" size={16}/>Preparar</button></div>
    <div className="composer-note"><Icon name="shield" size={16}/>Sin envío, borrado ni acción irreversible desde SL0.</div>
  </form>;
}
function SeamPanel() {
  return <aside className="panel seams-panel" aria-label="Costuras contract-first">
    <div className="panel-header"><div><div className="panel-kicker">Costuras</div><div className="panel-title">Contract-first</div></div></div>
    <div className="seam-list">
      <div className="seam-card"><strong><Icon name="shield" size={16}/>HITL absoluto</strong><p>El shell no ejecuta acciones irreversibles. Enviar y borrar requieren doble confirmación futura.</p></div>
      <div className="seam-card"><strong><Icon name="database" size={16}/>Context layer</strong><p>La UI consume /api/workspaces y deja preparado el workspace activo para toda query.</p></div>
      <div className="seam-card"><strong><Icon name="audit" size={16}/>AuditWriter</strong><p>Hoy JSONL; mañana outbox/tabla sin reescribir la superficie.</p></div>
    </div>
  </aside>;
}

function SpaceView({ activeWorkspace }) {
  const [activeChatId, setActiveChatId] = useState(SEEDED_CHATS[0].id);
  return <div className="space-view">
    <ChatList activeChatId={activeChatId} setActiveChatId={setActiveChatId}/>
    <section className="panel chat-stage" aria-label="Canvas central de SpaceLoom">
      <div className="stage-header"><div className="stage-title"><h2>Draft-first canvas.</h2><p>Chat vacío, contexto visible, sin modelo conectado todavía.</p></div><span className="pill"><Icon name="loom" size={16}/>SL0</span></div>
      <div className="message-area"><EmptyMessages activeWorkspace={activeWorkspace}/></div><Composer/>
    </section>
    <SeamPanel/>
  </div>;
}

function PlaceholderView({ nav }) {
  const labels = { workloom: "WorkLoom", kb: "Knowledge Base", routines: "Routine Hub", settings: "Ajustes", audit: "Auditoría" };
  return <div className="placeholder"><div className="placeholder-card"><Icon name="loom"/><h2>{labels[nav] || "Vista futura"}</h2><p>Esta superficie queda señalizada en SL0, pero se implementa en hitos posteriores del plan SpaceLoom.</p></div></div>;
}

function Canvas({ nav, activeWorkspace, status }) {
  return <main className="canvas">
    <ContextStrip activeWorkspace={activeWorkspace}/>
    {status === "error" && <div className="workspace-warning"><Icon/>No se pudo cargar /api/workspaces. El shell sigue disponible para revisar la interfaz.</div>}
    {nav === "space" ? <SpaceView activeWorkspace={activeWorkspace}/> : <PlaceholderView nav={nav}/>} 
  </main>;
}

function App() {
  const boot = useMemo(readBootstrap, []);
  const [mode, setMode] = useState("operar");
  const [nav, setNav] = useState("space");
  const [workspaces, setWorkspaces] = useState(boot ? boot.workspaces : []);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState(boot ? boot.activeWorkspaceId : null);
  const [status, setStatus] = useState(boot && boot.workspaces.length ? "ready" : "loading");

  useEffect(() => {
    if (boot && boot.workspaces.length) return;
    let cancelled = false;
    fetch("/api/workspaces", { headers: { "x-user-id": "local" } })
      .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
      .then((payload) => {
        if (cancelled) return;
        const list = Array.isArray(payload) ? payload : (payload.workspaces || []);
        setWorkspaces(list);
        setActiveWorkspaceId((current) => current || (list[0] && list[0].id) || null);
        setStatus("ready");
      })
      .catch(() => { if (!cancelled) setStatus("error"); });
    return () => { cancelled = true; };
  }, [boot]);

  const activeWorkspace = workspaces.find((workspace) => workspace.id === activeWorkspaceId) || null;
  return <div className="app-shell"><Topbar/><div className="frame"><Rail mode={mode} setMode={setMode} nav={nav} setNav={setNav} workspaces={workspaces} activeWorkspaceId={activeWorkspaceId} setActiveWorkspaceId={setActiveWorkspaceId} status={status}/><Canvas nav={nav} activeWorkspace={activeWorkspace} status={status}/></div></div>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
```

```css:app/static/css/main.css
:root{
  --bg:#F4F1ED;--surface:#FFFFFF;--subtle:#EDE8DF;--text:#1F1E1C;--text-2:#5A544C;--muted:#8A8278;--border:#D8D0C0;--coral:#C96442;--coral-hover:#A84F33;--slate:#5A6B7C;
  --soft:#FBFAF7;--coral-soft:rgba(201,100,66,.12);--slate-soft:rgba(90,107,124,.11);--shadow:0 18px 54px rgba(31,30,28,.09);--shadow-sm:0 8px 24px rgba(31,30,28,.08);
  --font-title:"EB Garamond",Georgia,serif;--font-ui:"Geist",system-ui,-apple-system,"Segoe UI",sans-serif;--font-mono:"Geist Mono","SF Mono",ui-monospace,Consolas,monospace;--ease:cubic-bezier(.22,1,.36,1)
}
*{box-sizing:border-box}html,body,#root{height:100%}body{margin:0;overflow:hidden;background:radial-gradient(circle at 15% 8%,rgba(201,100,66,.08),transparent 28%),radial-gradient(circle at 85% 0,rgba(90,107,124,.09),transparent 30%),var(--bg);color:var(--text);font:14px/1.5 var(--font-ui);-webkit-font-smoothing:antialiased}button,input,textarea,select{font:inherit}button{color:inherit}::selection{background:var(--coral);color:var(--bg)}:focus-visible{outline:2px solid var(--coral);outline-offset:2px}::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:var(--border);border:3px solid var(--bg);border-radius:999px}
.boot{min-height:100vh;display:grid;place-content:center;justify-items:center;gap:14px;color:var(--muted)}.boot-mark{width:56px;height:56px;display:grid;place-items:center;border-radius:18px;background:var(--coral);color:var(--bg);box-shadow:var(--shadow)}.boot-text{font:11px/1.2 var(--font-mono);letter-spacing:.16em;text-transform:uppercase}
.app-shell{height:100%;min-height:0;display:flex;flex-direction:column;background:var(--bg)}.topbar{height:60px;flex:0 0 60px;display:flex;align-items:center;gap:14px;padding:0 18px;border-bottom:1px solid var(--border);background:rgba(244,241,237,.9);backdrop-filter:blur(16px);z-index:10}.brand{min-width:238px;display:inline-flex;align-items:center;gap:11px}.brand-mark{width:36px;height:36px;flex:0 0 36px;display:grid;place-items:center;border-radius:12px;background:var(--coral);color:var(--bg);box-shadow:var(--shadow-sm)}.brand-word{display:grid;gap:2px}.brand-name{font:italic 500 22px/1 var(--font-title);letter-spacing:-.01em;white-space:nowrap}.brand-faber{color:var(--coral)}.brand-loom{color:var(--text)}.brand-sub{color:var(--muted);font:9.5px/1.2 var(--font-mono);letter-spacing:.12em;text-transform:uppercase}.command-bar{flex:1;max-width:520px;min-width:220px;height:38px;display:flex;align-items:center;gap:9px;padding:0 12px;border:1px solid var(--border);border-radius:12px;background:var(--soft);color:var(--muted)}.command-bar span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.command-bar kbd{margin-left:auto;padding:2px 6px;border:1px solid var(--border);border-radius:6px;background:var(--surface);color:var(--muted);font:10px/1.2 var(--font-mono)}.topbar-actions{margin-left:auto}.status-chip,.pill{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--border);background:var(--surface);color:var(--text-2);white-space:nowrap}.status-chip{height:36px;padding:0 11px;border-radius:12px;font-size:12.5px}.status-dot{width:7px;height:7px;border-radius:999px;background:var(--coral);box-shadow:0 0 0 4px var(--coral-soft)}
.frame{flex:1;min-height:0;display:grid;grid-template-columns:292px minmax(0,1fr)}.rail{min-height:0;display:flex;flex-direction:column;gap:18px;padding:18px;border-right:1px solid var(--border);background:rgba(237,232,223,.42);overflow:auto}.mode-group{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:4px;border:1px solid var(--border);border-radius:14px;background:var(--surface)}.mode-button{height:34px;border:0;border-radius:10px;background:transparent;color:var(--muted);cursor:pointer;font-size:12px;font-weight:600}.mode-button:hover{background:var(--soft);color:var(--text-2)}.mode-button.is-active{background:var(--subtle);color:var(--text);box-shadow:inset 0 0 0 1px var(--border)}.rail-section{display:grid;gap:10px}.rail-label{display:flex;justify-content:space-between;color:var(--muted);font:10.5px/1.2 var(--font-mono);letter-spacing:.14em;text-transform:uppercase}.nav-stack{display:grid;gap:7px}.nav-item{width:100%;display:grid;grid-template-columns:24px 1fr auto;align-items:center;gap:10px;padding:10px;border:1px solid transparent;border-radius:13px;background:transparent;color:var(--text-2);text-align:left;cursor:pointer;transition:.16s var(--ease)}.nav-item:hover,.nav-item.is-active{border-color:var(--border);background:var(--surface);color:var(--text);box-shadow:var(--shadow-sm)}.nav-title{display:block;font-weight:650;line-height:1.2}.nav-sub{display:block;margin-top:2px;color:var(--muted);font-size:11.5px;line-height:1.25}.nav-badge{align-self:start;padding:3px 6px;border-radius:999px;background:var(--subtle);color:var(--muted);font:9.5px/1 var(--font-mono);letter-spacing:.06em;text-transform:uppercase}
.workspace-card{display:grid;gap:12px;padding:14px;border:1px solid var(--border);border-radius:14px;background:var(--surface);box-shadow:var(--shadow-sm)}.workspace-select{width:100%;height:38px;padding:0 10px;border:1px solid var(--border);border-radius:11px;background:var(--soft);color:var(--text)}.workspace-meta,.composer-note{display:flex;align-items:center;gap:8px;color:var(--muted);font:11px/1.35 var(--font-mono)}.rail-note{margin-top:auto;padding:14px;border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,.58);color:var(--text-2)}.rail-note-title{display:flex;align-items:center;gap:8px;margin-bottom:6px;color:var(--text);font-weight:650}.rail-note p{margin:0;font-size:12.5px;line-height:1.55}
.canvas{min-width:0;min-height:0;display:grid;grid-template-rows:auto minmax(0,1fr);padding:20px;overflow:hidden}.context-strip{display:flex;align-items:center;gap:14px;margin-bottom:16px;padding:14px 16px;border:1px solid var(--border);border-radius:20px;background:rgba(255,255,255,.68);box-shadow:var(--shadow-sm)}.context-dot{width:10px;height:10px;flex:0 0 10px;border-radius:999px;background:var(--slate);box-shadow:0 0 0 5px var(--slate-soft)}.context-main{min-width:0}.context-title{display:flex;align-items:baseline;gap:10px}.context-title h1{margin:0;font:italic 500 31px/1.05 var(--font-title);letter-spacing:-.01em}.context-badge{padding:4px 8px;border:1px solid var(--border);border-radius:999px;background:var(--surface);color:var(--muted);font:10.5px/1 var(--font-mono)}.context-sub{margin-top:4px;color:var(--text-2);font-size:13px}.context-actions{margin-left:auto;display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px}.pill{min-height:30px;padding:0 10px;border-radius:999px;font-size:12px}.pill-muted{color:var(--muted)}.workspace-warning{margin-bottom:16px;display:flex;align-items:center;gap:10px;padding:12px 14px;border:1px solid var(--border);border-radius:14px;background:var(--surface);color:var(--text-2)}
.space-view{min-height:0;display:grid;grid-template-columns:286px minmax(0,1fr) 280px;gap:16px}.panel{min-height:0;border:1px solid var(--border);border-radius:20px;background:var(--surface);box-shadow:var(--shadow-sm);overflow:hidden}.panel-header{min-height:58px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid var(--border);background:var(--soft)}.panel-kicker{color:var(--muted);font:10px/1.2 var(--font-mono);letter-spacing:.14em;text-transform:uppercase}.panel-title{margin-top:3px;font-weight:650;line-height:1.2}.chat-list{padding:10px;overflow:auto}.chat-card{width:100%;display:grid;gap:6px;padding:12px;border:1px solid transparent;border-radius:14px;background:transparent;text-align:left;cursor:pointer}.chat-card:hover,.chat-card.is-active{border-color:var(--border);background:var(--soft)}.chat-row{display:flex;justify-content:space-between;gap:10px}.chat-title{font-weight:650}.chat-time{color:var(--muted);font:10.5px/1.4 var(--font-mono)}.chat-snippet{color:var(--text-2);font-size:12.5px;line-height:1.45}.chat-stage{display:grid;grid-template-rows:auto minmax(0,1fr) auto}.stage-header{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 20px;border-bottom:1px solid var(--border)}.stage-title h2{margin:0;font:italic 500 30px/1.05 var(--font-title)}.stage-title p{margin:6px 0 0;color:var(--text-2);font-size:13px}.message-area{min-height:0;display:grid;place-items:center;padding:28px;overflow:auto;background:linear-gradient(90deg,rgba(216,208,192,.25) 1px,transparent 1px),linear-gradient(180deg,rgba(216,208,192,.25) 1px,transparent 1px),var(--surface);background-size:32px 32px}.empty-state{max-width:520px;display:grid;justify-items:center;text-align:center;padding:28px;border:1px solid var(--border);border-radius:20px;background:rgba(255,255,255,.78);box-shadow:var(--shadow-sm)}.empty-loom{width:58px;height:58px;display:grid;place-items:center;margin-bottom:14px;border-radius:18px;background:var(--coral-soft);color:var(--coral)}.empty-state h3{margin:0;font:italic 500 28px/1.1 var(--font-title)}.empty-state p{margin:8px 0 0;color:var(--text-2);line-height:1.6}.composer-shell{padding:14px;border-top:1px solid var(--border);background:var(--soft)}.composer{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end;padding:10px;border:1px solid var(--border);border-radius:16px;background:var(--surface)}.composer textarea{width:100%;min-height:42px;max-height:120px;resize:vertical;border:0;outline:0;background:transparent;color:var(--text);line-height:1.45}.composer textarea::placeholder{color:var(--muted)}.send-button,.icon-button{border:1px solid var(--border);background:var(--surface);color:var(--text-2);cursor:pointer}.icon-button{width:38px;height:38px;display:grid;place-items:center;border-radius:12px}.send-button{height:42px;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:0 14px;border-radius:13px;font-weight:650}.send-button:disabled{cursor:not-allowed;color:var(--muted);background:var(--subtle)}.composer-note{margin:9px 4px 0;font:12px/1.35 var(--font-ui)}.seam-list{padding:14px;display:grid;gap:10px}.seam-card{padding:12px;border:1px solid var(--border);border-radius:14px;background:var(--soft)}.seam-card strong{display:flex;align-items:center;gap:8px;margin-bottom:5px;color:var(--text)}.seam-card p{margin:0;color:var(--text-2);font-size:12.5px;line-height:1.5}.placeholder{min-height:0;display:grid;place-items:center;border:1px dashed var(--border);border-radius:20px;background:rgba(255,255,255,.42);color:var(--text-2)}.placeholder-card{max-width:520px;padding:30px;text-align:center}.placeholder-card h2{margin:10px 0 8px;font:italic 500 32px/1.1 var(--font-title)}.placeholder-card p{margin:0;line-height:1.6}.icon{width:24px;height:24px;display:block;flex:0 0 24px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}.icon-sm{width:16px;height:16px;flex-basis:16px}
@media (max-width:1180px){.space-view{grid-template-columns:260px minmax(0,1fr)}.seams-panel{display:none}}@media (max-width:900px){body{overflow:auto}.app-shell{min-height:100%;height:auto}.command-bar,.topbar-actions{display:none}.frame,.space-view{grid-template-columns:1fr}.rail{border-right:0;border-bottom:1px solid var(--border)}.canvas{overflow:visible}.context-strip{align-items:flex-start}.context-actions{display:none}}
```