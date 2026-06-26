var { useEffect, useMemo, useState } = React;

const MODES = [
  { id: "operar", label: "Operar" },
  { id: "aprender", label: "Aprender" },
  { id: "admin", label: "Admin" },
];

const NAV = {
  operar: [
    { id: "space", label: "SpaceLoom", sub: "Canvas y chat", badge: "SL0", icon: "loom" },
    { id: "workloom", label: "WorkLoom", sub: "Cola HITL", badge: "SL3", icon: "check" },
    { id: "mail", label: "Correo", sub: "IMAP/SMTP HITL", badge: "SL5", icon: "mail" },
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

const S = {
  view: { minHeight: 0, display: "flex", flexDirection: "column", gap: 16, overflow: "auto" },
  grid2: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, alignItems: "start" },
  grid3: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16, alignItems: "start" },
  panelBody: { padding: "14px 16px", overflow: "auto" },
  form: { display: "grid", gap: 12 },
  label: { display: "grid", gap: 6, fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px" },
  input: { width: "100%", padding: "9px 11px", border: "1px solid var(--border-default)", borderRadius: 8, background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 12.5, outline: "none" },
  select: { width: "100%", height: 36, padding: "0 10px", border: "1px solid var(--border-default)", borderRadius: 8, background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 12.5 },
  textarea: { width: "100%", minHeight: 90, padding: 10, border: "1px solid var(--border-default)", borderRadius: 8, background: "var(--bg-sunken)", color: "var(--text-primary)", resize: "vertical", fontFamily: "var(--font-ui)" },
  monoTextarea: { width: "100%", minHeight: 90, padding: 10, border: "1px solid var(--border-default)", borderRadius: 8, background: "var(--bg-sunken)", color: "var(--text-primary)", resize: "vertical", fontFamily: "var(--font-mono)", fontSize: 12 },
  button: { padding: "9px 14px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 12.5 },
  buttonPrimary: { padding: "9px 14px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 600, fontSize: 12.5 },
  buttonDanger: { padding: "9px 14px", border: 0, borderRadius: "var(--r-sm)", background: "var(--vino)", color: "#1A1815", cursor: "pointer", fontWeight: 600, fontSize: 12.5 },
  list: { display: "flex", flexDirection: "column", gap: 10 },
  card: { padding: 13, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "linear-gradient(var(--elev-top), transparent), var(--bg-surface)", boxShadow: "var(--shadow-sm)" },
  cardTitle: { fontWeight: 650, marginBottom: 5, lineHeight: 1.25, color: "var(--text-primary)", fontSize: 14 },
  cardMeta: { color: "var(--text-muted)", fontSize: 11.5, fontFamily: "var(--font-mono)", marginBottom: 8 },
  pre: { padding: 12, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", fontFamily: "var(--font-mono)", fontSize: 12, overflow: "auto", maxHeight: 280, whiteSpace: "pre-wrap", color: "var(--text-secondary)" },
  badge: { padding: "3px 8px", borderRadius: 999, background: "var(--bg-raised)", color: "var(--text-muted)", fontSize: 10.5, fontFamily: "var(--font-mono)", textTransform: "uppercase", border: "1px solid var(--border-default)" },
  inlineGroup: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10, alignItems: "center" },
  searchRow: { display: "flex", gap: 10, marginBottom: 12 },
  empty: { padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" },
  error: { padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5, lineHeight: 1.5 },
  loading: { padding: 20, textAlign: "center", color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: 12 },
  modalOverlay: { position: "fixed", inset: 0, background: "rgba(12,10,8,.66)", backdropFilter: "blur(4px)", display: "grid", placeItems: "center", zIndex: 90 },
  modal: { width: "min(520px, 92vw)", maxHeight: "90vh", overflow: "auto", padding: 20, border: "1px solid var(--border-default)", borderRadius: "var(--r-lg)", background: "var(--bg-raised)", boxShadow: "var(--shadow)" },
  modalTitle: { margin: "0 0 6px", font: "italic 500 22px/1.1 var(--font-title)" },
  modalToken: { padding: 10, border: "1px dashed var(--coral)", borderRadius: 10, background: "var(--coral-soft)", fontFamily: "var(--font-mono)", fontSize: 13, margin: "12px 0", color: "var(--text-primary)", wordBreak: "break-all" },
};

function statusClass(status) {
  const s = String(status || "").toLowerCase();
  if (s === "approved" || s === "sent" || s === "succeeded") return "status-tag approved";
  if (s === "rejected" || s === "failed") return "status-tag rejected";
  if (s === "running" || s === "pending_approval" || s === "drafted") return "status-tag running";
  if (s === "requires_hitl") return "status-tag requires_hitl";
  return "badge";
}

function cx(...parts) { return parts.filter(Boolean).join(" "); }

function readBootstrap() {
  const boot = window.__SPACELOOM_BOOTSTRAP__;
  if (!boot || typeof boot !== "object") return null;
  const workspaces = Array.isArray(boot.workspaces) ? boot.workspaces : [];
  return { workspaces, activeWorkspaceId: boot.activeWorkspaceId || boot.active_workspace_id || (workspaces[0] && workspaces[0].id) || null };
}

const API_HEADERS = { "Content-Type": "application/json", "x-user-id": "local" };

async function apiGet(path) {
  const res = await fetch(path, { headers: { "x-user-id": "local" } });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(path, { method: "POST", headers: API_HEADERS, body: JSON.stringify(body || {}) });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function apiPatch(path, body) {
  const res = await fetch(path, { method: "PATCH", headers: API_HEADERS, body: JSON.stringify(body || {}) });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(path, { method: "DELETE", headers: API_HEADERS });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function sha256Truncated(text, length = 16) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, length);
}

function tryJsonParse(text) {
  try { return JSON.parse(text); } catch { return null; }
}

function prettyJson(value) { return JSON.stringify(value, null, 2); }

function Topbar({ onOpenPalette, theme, setTheme }) {
  return <header className="topbar">
    <button type="button" className="ceja" aria-label="Panel izquierdo"><Icon name="panel-l" size={18}/></button>
    <div className="brand" aria-label="FaberLoom SpaceLoom">
      <span className="brand-mark"><BrandMark /></span>
      <span className="brand-word"><span className="brand-name"><span className="brand-faber">Faber</span><span className="brand-loom">Loom</span></span><span className="brand-sub">SpaceLoom · local-first</span></span>
    </div>
    <div className="cmdk" role="button" tabIndex="0" onClick={onOpenPalette} aria-label="Buscar o ejecutar"><Icon name="search" size={16}/><span className="cmdk-label">Buscar o ejecutar…</span><kbd>Ctrl K</kbd></div>
    <div className="topbar-actions"><ThemeSwitcher theme={theme} onChange={setTheme} /><span className="status-chip"><span className="status-dot" aria-hidden="true"/>Local-first</span><button type="button" className="ceja" aria-label="Panel derecho"><Icon name="panel-r" size={18}/></button></div>
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
    <div className="rail-note"><div className="rail-note-title"><Icon name="loom" size={16}/>SpaceLoom</div><p>Frontend conectado a /api. Las acciones destructivas requieren HITL y doble confirmación.</p></div>
  </aside>;
}

function ContextStrip({ activeWorkspace }) {
  return <div className="context-strip">
    <span className="context-dot" aria-hidden="true"/>
    <div className="context-main">
      <div className="context-title"><h1>{activeWorkspace ? activeWorkspace.name : "Sin espacio activo"}</h1>{activeWorkspace && <span className="context-badge">{activeWorkspace.slug || activeWorkspace.id}</span>}</div>
      <div className="context-sub">{activeWorkspace ? "Espacio activo · flujos reales contra el backend local" : "Selecciona o crea un workspace para usar las vistas operativas."}</div>
    </div>
    <div className="context-actions"><span className="pill pill-muted"><Icon name="route" size={16}/>Router SL1a</span><span className="pill pill-muted"><Icon name="database" size={16}/>KB SL2</span><span className="pill pill-muted"><Icon name="shield" size={16}/>HITL SL5</span></div>
  </div>;
}

function ChatList({ chats, activeChatId, setActiveChatId, onCreate }) {
  return <section className="panel chat-list-panel" aria-label="Lista de chats">
    <div className="panel-header">
      <div><div className="panel-kicker">SpaceLoom</div><div className="panel-title">Chats</div></div>
      <button type="button" className="ceja" onClick={onCreate} title="Nuevo chat"><Icon name="plus" size={18}/></button>
    </div>
    <div className="chat-list">
      {chats.length === 0 && <div className="chat-empty">Sin chats todavía. Crea uno para empezar.</div>}
      {chats.map((chat) => (
        <button key={chat.id} type="button" className={cx("chat-card", activeChatId === chat.id && "is-active")} onClick={() => setActiveChatId(chat.id)}>
          <span className="chat-row"><span className="chat-title">{chat.title}</span><span className="chat-time">{chat.created_at ? new Date(chat.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}</span></span>
        </button>
      ))}
    </div>
  </section>;
}

function EmptyMessages({ activeWorkspace }) {
  return <div className="empty-state"><div className="empty-loom" aria-hidden="true"><BrandMark/></div><h3>El telar está listo.</h3><p>Selecciona un chat o crea uno nuevo para conversar con el router SL1a en {activeWorkspace ? activeWorkspace.name : "tu workspace"}.</p></div>;
}

function Composer({ onSend, disabled }) {
  const [draft, setDraft] = useState("");
  const submit = (event) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text || disabled) return;
    onSend(text);
    setDraft("");
  };
  return <form className="composer-shell" onSubmit={submit} aria-label="Composer de chat">
    <div className="composer">
      <textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Escribe tu mensaje…" rows="2" disabled={disabled}/>
      <button type="submit" className="send-button" disabled={disabled || !draft.trim()}><Icon name="send" size={16}/>Enviar</button>
    </div>
    <div className="composer-note"><Icon name="shield" size={16}/>Las acciones destructivas requieren HITL y doble confirmación.</div>
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
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const loadChats = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/chats`);
      setChats(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const loadMessages = async (chatId) => {
    if (!activeWorkspace || !chatId) {
      setMessages([]);
      return;
    }
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/chats/${chatId}/messages`);
      setMessages(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { loadChats(); }, [activeWorkspace]);
  useEffect(() => { loadMessages(activeChatId); }, [activeChatId]);

  const createChat = async () => {
    if (!activeWorkspace) return;
    setError(null);
    try {
      const chat = await apiPost(`/api/workspaces/${activeWorkspace.id}/chats`, { title: "Nueva conversación" });
      setChats((prev) => [chat, ...prev]);
      setActiveChatId(chat.id);
    } catch (err) {
      setError(err.message);
    }
  };

  const sendMessage = async (text) => {
    if (!activeWorkspace || !activeChatId) return;
    setBusy(true);
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/chats/${activeChatId}/completions`, { message: text });
      await loadMessages(activeChatId);
    } catch (err) {
      setError(err.message);
    }
    setBusy(false);
  };

  if (!activeWorkspace) return <WorkspaceRequired icon="loom" title="SpaceLoom"/>;

  const activeChat = chats.find((c) => c.id === activeChatId);

  return <div className="space-view">
    <ChatList chats={chats} activeChatId={activeChatId} setActiveChatId={setActiveChatId} onCreate={createChat}/>
    <section className="panel chat-stage" aria-label="Canvas central de SpaceLoom">
      <div className="stage-header">
        <div className="stage-title"><h2>{activeChat ? activeChat.title : "Selecciona o crea un chat"}</h2><p>{activeChat ? "Conversación con el router SL1a." : "Elige un hilo para empezar."}</p></div>
        <span className="pill"><Icon name="loom" size={16}/>SL1a</span>
      </div>
      <div className="message-area">
        {loading && <div style={S.loading}>Cargando…</div>}
        {error && <div style={S.error}>{error}</div>}
        {!activeChat && !loading && <EmptyMessages activeWorkspace={activeWorkspace}/>}
        {messages.map((msg) => (
          <div key={msg.id} className={cx("message", msg.role === "user" ? "message-user" : "message-assistant")}>
            <div className="message-meta">{msg.role === "user" ? "Tú" : "SpaceLoom"} · {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}</div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {busy && <div className="message message-assistant"><div className="message-content"><em>El telar está pensando…</em></div></div>}
      </div>
      <Composer onSend={sendMessage} disabled={busy || !activeChat}/>
    </section>
    <SeamPanel/>
  </div>;
}

function PlaceholderView({ nav }) {
  const labels = { workloom: "WorkLoom", kb: "Knowledge Base", routines: "Routine Hub", settings: "Ajustes", audit: "Auditoría" };
  return <div className="placeholder"><div className="placeholder-card"><Icon name="loom"/><h2>{labels[nav] || "Vista futura"}</h2><p>Esta superficie queda señalizada en SL0, pero se implementa en hitos posteriores del plan SpaceLoom.</p></div></div>;
}

function WorkspaceRequired({ icon, title }) {
  return <div className="placeholder"><div className="placeholder-card"><Icon name={icon}/><h2>{title}</h2><p>Selecciona un workspace activo para usar esta vista.</p></div></div>;
}

function KBView({ activeWorkspace }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ title: "", type: "md", content_text: "" });
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/kb/sources`);
      setSources(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const doSearch = async () => {
    if (!activeWorkspace || !query.trim()) {
      setResults(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await apiGet(`/api/workspaces/${activeWorkspace.id}/kb/search?q=${encodeURIComponent(query)}`);
      setResults(r);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const createSource = async (event) => {
    event.preventDefault();
    if (!activeWorkspace) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/kb/sources`, form);
      setForm({ title: "", type: "md", content_text: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { load(); }, [activeWorkspace]);
  useEffect(() => {
    const timer = setTimeout(doSearch, 300);
    return () => clearTimeout(timer);
  }, [query]);

  if (!activeWorkspace) return <WorkspaceRequired icon="book" title="Knowledge Base"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead"><div><div className="vtitle">Knowledge Base</div><div className="vsub">Fuentes, chunks y facts del workspace</div></div></div>
    <div style={S.grid2}>
      <section className="panel" aria-label="Fuentes KB">
        <div className="panel-header"><div><div className="panel-kicker">KB</div><div className="panel-title">Fuentes ({sources.length})</div></div></div>
        <div style={S.panelBody}>
          {loading && <div style={S.loading}>Cargando…</div>}
          {error && <div style={S.error}>{error}</div>}
          {!loading && sources.length === 0 && <div style={S.empty}>No hay fuentes KB.</div>}
          <div style={S.list}>
            {sources.map((source) => <div key={source.id} style={S.card}>
              <div style={S.cardTitle}>{source.title}</div>
              <div style={S.cardMeta}>{source.type} · {source.id} · {source.created_at}</div>
              <div style={S.inlineGroup}><span style={S.badge}>{source.source_version || "v1"}</span></div>
            </div>)}
          </div>
        </div>
      </section>
      <section className="panel" aria-label="Crear fuente KB">
        <div className="panel-header"><div><div className="panel-kicker">KB</div><div className="panel-title">Nueva fuente</div></div></div>
        <div style={S.panelBody}>
          {error && <div style={S.error}>{error}</div>}
          <form style={S.form} onSubmit={createSource}>
            <label style={S.label}>Título<input style={S.input} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required/></label>
            <label style={S.label}>Tipo
              <select style={S.select} value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                <option value="md">md</option><option value="txt">txt</option><option value="csv">csv</option><option value="xlsx">xlsx</option><option value="pdf">pdf</option>
              </select>
            </label>
            <label style={S.label}>Contenido<textarea style={S.textarea} value={form.content_text} onChange={(e) => setForm({ ...form, content_text: e.target.value })} rows={8}/></label>
            <button type="submit" style={S.buttonPrimary}>Crear fuente</button>
          </form>
        </div>
      </section>
    </div>
    <section className="panel" aria-label="Buscar KB">
      <div className="panel-header"><div><div className="panel-kicker">KB</div><div className="panel-title">Búsqueda</div></div></div>
      <div style={S.panelBody}>
        <div style={S.searchRow}>
          <input style={S.input} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar chunks y facts…"/>
        </div>
        {results && <div>
          <h4 style={{ margin: "0 0 10px" }}>Chunks ({(results.chunks || []).length})</h4>
          <div style={S.list}>{(results.chunks || []).map((chunk, idx) => <div key={idx} style={S.card}>
            <div style={S.cardMeta}>#{chunk.chunk_index} · source {chunk.source_id}</div>
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>{chunk.content_text}</div>
          </div>)}</div>
          <h4 style={{ margin: "18px 0 10px" }}>Facts ({(results.facts || []).length})</h4>
          <div style={S.list}>{(results.facts || []).map((fact, idx) => <div key={idx} style={S.card}>
            <div style={S.cardTitle}>{fact.entity_key} · {fact.field_name}</div>
            <div style={{ fontSize: 13, lineHeight: 1.5 }}>{fact.field_value} {fact.unit && `(${fact.unit})`}</div>
          </div>)}</div>
        </div>}
      </div>
    </section>
  </div>;
}

function RoutinesView({ activeWorkspace }) {
  const [routines, setRoutines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const [form, setForm] = useState({ name: "", skill_md: "", persona_md: "", tools_allowlist: "[]", schema_output_json: "{}", trigger_json: "[]", is_active: 1, source_version: "v1" });
  const [editingRoutine, setEditingRoutine] = useState(null);
  const [editForm, setEditForm] = useState(null);
  const [runInputs, setRunInputs] = useState({});
  const [runOutputs, setRunOutputs] = useState({});
  const [showImportModal, setShowImportModal] = useState(false);
  const [catalog, setCatalog] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [selectedImports, setSelectedImports] = useState(new Set());
  const [importLoading, setImportLoading] = useState(false);

  const FILTERS = [
    { id: "all", label: "Todos" },
    { id: "skill", label: "Skills" },
    { id: "agent", label: "Agentes" },
    { id: "template", label: "Templates" },
    { id: "reference", label: "Referencias" },
    { id: "custom", label: "Custom" },
  ];

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/routines`);
      setRoutines(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const createRoutine = async (event) => {
    event.preventDefault();
    if (!activeWorkspace) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines`, form);
      setForm({ name: "", skill_md: "", persona_md: "", tools_allowlist: "[]", schema_output_json: "{}", trigger_json: "[]", is_active: 1, source_version: "v1" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const approveRoutine = async (routine) => {
    if (!window.confirm(`¿Aprobar la rutina "${routine.name}"? Una vez aprobada podrá ejecutarse.`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}/approve?approved_by=local`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const runRoutine = async (routine) => {
    if (!activeWorkspace) return;
    const raw = runInputs[routine.id] || "{}";
    const parsed = tryJsonParse(raw);
    if (parsed === null) {
      setError(`input_json de "${routine.name}" no es JSON válido`);
      return;
    }
    setError(null);
    try {
      const run = await apiPost(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}/run`, { input_json: parsed });
      setRunOutputs({ ...runOutputs, [routine.id]: run.output_json });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredRoutines = useMemo(() => {
    if (filter === "all") return routines;
    return routines.filter((r) => (r.category || "custom") === filter);
  }, [routines, filter]);

  const startEdit = (routine) => {
    setEditingRoutine(routine);
    setEditForm({
      name: routine.name,
      skill_md: routine.skill_md,
      persona_md: routine.persona_md,
      tools_allowlist: routine.tools_allowlist,
      schema_output_json: routine.schema_output_json,
      trigger_json: routine.trigger_json,
      preset_id: routine.preset_id,
      is_active: routine.is_active,
      source_version: routine.source_version || "v1",
    });
  };

  const saveEdit = async (event) => {
    event.preventDefault();
    if (!activeWorkspace || !editingRoutine) return;
    setError(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/routines/${editingRoutine.id}`, editForm);
      setEditingRoutine(null);
      setEditForm(null);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleRoutine = async (routine) => {
    if (!activeWorkspace) return;
    setError(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}`, { is_active: routine.is_active ? 0 : 1 });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteRoutine = async (routine) => {
    if (!window.confirm(`¿Eliminar la rutina "${routine.name}"? Esta acción no se puede deshacer.`)) return;
    if (!activeWorkspace) return;
    setError(null);
    try {
      const token = await sha256Truncated(routine.id, 16);
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}?confirmation_token=${token}`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const loadCatalog = async () => {
    setCatalogLoading(true);
    setError(null);
    try {
      const items = await apiGet("/api/faberloom/catalog");
      setCatalog(Array.isArray(items) ? items : []);
      setSelectedImports(new Set());
    } catch (err) {
      setError(err.message);
    }
    setCatalogLoading(false);
  };

  const openImport = () => {
    setShowImportModal(true);
    loadCatalog();
  };

  const toggleImport = (id) => {
    const next = new Set(selectedImports);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedImports(next);
  };

  const importSelected = async () => {
    if (selectedImports.size === 0 || !activeWorkspace) return;
    setImportLoading(true);
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines/import-faberloom`, { imports: Array.from(selectedImports) });
      setShowImportModal(false);
      setSelectedImports(new Set());
      await load();
    } catch (err) {
      setError(err.message);
    }
    setImportLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  if (!activeWorkspace) return <WorkspaceRequired icon="spark" title="Routine Hub"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead">
      <div>
        <div className="vtitle">Routine Hub</div>
        <div className="vsub">Skills portables · autoría → aprobación → ejecución</div>
      </div>
      <button style={S.buttonPrimary} onClick={openImport}>Importar de FaberLoom</button>
    </div>

    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {FILTERS.map((f) => (
        <button
          key={f.id}
          style={filter === f.id ? S.buttonPrimary : S.button}
          onClick={() => setFilter(f.id)}
        >{f.label}</button>
      ))}
    </div>

    <div style={S.grid2}>
      <section className="panel" aria-label="Rutinas">
        <div className="panel-header"><div><div className="panel-kicker">Routines</div><div className="panel-title">{FILTERS.find(f => f.id === filter).label} ({filteredRoutines.length})</div></div></div>
        <div style={S.panelBody}>
          {loading && <div style={S.loading}>Cargando…</div>}
          {error && <div style={S.error}>{error}</div>}
          {!loading && filteredRoutines.length === 0 && <div style={S.empty}>No hay rutinas en esta categoría.</div>}
          <Accordion items={filteredRoutines.map((routine) => ({
            id: routine.id,
            title: routine.name,
            subtitle: `${routine.id} · ${routine.source_version || "v1"}`,
            badge: routine.category || "custom",
            children: <div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-start", marginBottom: 10 }}>
                <span style={routine.is_active ? S.badge : { ...S.badge, opacity: 0.6 }}>{routine.is_active ? "activo" : "inactivo"}</span>
                {routine.approved_by ? <span style={{ ...S.badge, background: "var(--coral-soft)" }}>aprobada</span> : <span style={S.badge}>pendiente</span>}
              </div>
              <div style={S.inlineGroup}>
                <button style={S.button} onClick={() => startEdit(routine)}>Editar</button>
                <button style={S.button} onClick={() => toggleRoutine(routine)}>{routine.is_active ? "Desactivar" : "Activar"}</button>
                <button style={S.buttonDanger} onClick={() => deleteRoutine(routine)}>Eliminar</button>
                {!routine.approved_by && <button style={S.buttonPrimary} onClick={() => approveRoutine(routine)}>Aprobar</button>}
                <button style={S.button} onClick={() => runRoutine(routine)} disabled={!routine.approved_by || !routine.is_active}>Ejecutar</button>
              </div>
              <label style={{ ...S.label, marginTop: 10 }}>input_json
                <textarea style={S.monoTextarea} value={runInputs[routine.id] || "{}"} onChange={(e) => setRunInputs({ ...runInputs, [routine.id]: e.target.value })} rows={4}/>
              </label>
              {runOutputs[routine.id] && <div><div style={{ marginTop: 10, fontSize: 11, color: "var(--muted)" }}>output_json</div><pre style={S.pre}>{runOutputs[routine.id]}</pre></div>}
            </div>
          }))} />
        </div>
      </section>
      <section className="panel" aria-label="Crear rutina">
        <div className="panel-header"><div><div className="panel-kicker">Routines</div><div className="panel-title">Nueva rutina</div></div></div>
        <div style={S.panelBody}>
          <form style={S.form} onSubmit={createRoutine}>
            <label style={S.label}>Nombre<input style={S.input} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required/></label>
            <label style={S.label}>skill_md<textarea style={S.textarea} value={form.skill_md} onChange={(e) => setForm({ ...form, skill_md: e.target.value })} rows={8}/></label>
            <label style={S.label}>persona_md<textarea style={S.textarea} value={form.persona_md} onChange={(e) => setForm({ ...form, persona_md: e.target.value })} rows={4}/></label>
            <label style={S.label}>tools_allowlist (JSON array)<input style={S.input} value={form.tools_allowlist} onChange={(e) => setForm({ ...form, tools_allowlist: e.target.value })}/></label>
            <label style={S.label}>schema_output_json (JSON schema)<textarea style={S.monoTextarea} value={form.schema_output_json} onChange={(e) => setForm({ ...form, schema_output_json: e.target.value })} rows={5}/></label>
            <label style={S.label}>trigger_json (JSON array)<input style={S.input} value={form.trigger_json} onChange={(e) => setForm({ ...form, trigger_json: e.target.value })}/></label>
            <label style={S.label}>source_version<input style={S.input} value={form.source_version} onChange={(e) => setForm({ ...form, source_version: e.target.value })}/></label>
            <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
              <Toggle checked={form.is_active === 1} onChange={(checked) => setForm({ ...form, is_active: checked ? 1 : 0 })} />
              Activo
            </div>
            <button type="submit" style={S.buttonPrimary}>Crear rutina</button>
          </form>
        </div>
      </section>
    </div>

    {editingRoutine && <div style={S.modalOverlay} onClick={() => setEditingRoutine(null)}>
      <div style={S.modal} onClick={(e) => e.stopPropagation()}>
        <h3 style={S.modalTitle}>Editar rutina</h3>
        {error && <div style={S.error}>{error}</div>}
        <form style={S.form} onSubmit={saveEdit}>
          <label style={S.label}>Nombre<input style={S.input} value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required/></label>
          <label style={S.label}>skill_md<textarea style={S.textarea} value={editForm.skill_md} onChange={(e) => setEditForm({ ...editForm, skill_md: e.target.value })} rows={8}/></label>
          <label style={S.label}>persona_md<textarea style={S.textarea} value={editForm.persona_md} onChange={(e) => setEditForm({ ...editForm, persona_md: e.target.value })} rows={4}/></label>
          <label style={S.label}>tools_allowlist (JSON array)<input style={S.input} value={editForm.tools_allowlist} onChange={(e) => setEditForm({ ...editForm, tools_allowlist: e.target.value })}/></label>
          <label style={S.label}>schema_output_json (JSON schema)<textarea style={S.monoTextarea} value={editForm.schema_output_json} onChange={(e) => setEditForm({ ...editForm, schema_output_json: e.target.value })} rows={5}/></label>
          <label style={S.label}>trigger_json (JSON array)<input style={S.input} value={editForm.trigger_json} onChange={(e) => setEditForm({ ...editForm, trigger_json: e.target.value })}/></label>
          <label style={S.label}>source_version<input style={S.input} value={editForm.source_version} onChange={(e) => setEditForm({ ...editForm, source_version: e.target.value })}/></label>
          <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
            <Toggle checked={editForm.is_active === 1} onChange={(checked) => setEditForm({ ...editForm, is_active: checked ? 1 : 0 })} />
            Activo
          </div>
          <div style={S.inlineGroup}>
            <button type="submit" style={S.buttonPrimary}>Guardar</button>
            <button type="button" style={S.button} onClick={() => setEditingRoutine(null)}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>}

    {showImportModal && <div style={S.modalOverlay} onClick={() => setShowImportModal(false)}>
      <div style={S.modal} onClick={(e) => e.stopPropagation()}>
        <h3 style={S.modalTitle}>Importar de FaberLoom</h3>
        <p style={{ margin: "0 0 12px", color: "var(--text-muted)", fontSize: 13 }}>Selecciona items para importar como routines inactivas y no aprobadas.</p>
        {error && <div style={S.error}>{error}</div>}
        {catalogLoading && <div style={S.loading}>Cargando catálogo…</div>}
        {!catalogLoading && catalog.length === 0 && <div style={S.empty}>Catálogo vacío.</div>}
        {!catalogLoading && catalog.length > 0 && <div style={{ ...S.list, maxHeight: "50vh", overflow: "auto", paddingRight: 4 }}>
          {catalog.map((item) => <label key={item.id} style={{ display: "flex", gap: 10, alignItems: "flex-start", padding: 10, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-sm)", cursor: "pointer" }}>
            <input type="checkbox" checked={selectedImports.has(item.id)} onChange={() => toggleImport(item.id)} style={{ marginTop: 3 }}/>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 650, fontSize: 13 }}>{item.name}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{item.id} · {item.version}</div>
              {item.description && <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4, lineHeight: 1.4 }}>{item.description.slice(0, 200)}{item.description.length > 200 ? "…" : ""}</div>}
            </div>
            <span style={S.badge}>{item.category}</span>
          </label>)}
        </div>}
        <div style={{ ...S.inlineGroup, marginTop: 16, justifyContent: "flex-end" }}>
          <button style={S.button} onClick={() => setShowImportModal(false)} disabled={importLoading}>Cancelar</button>
          <button style={S.buttonPrimary} onClick={importSelected} disabled={selectedImports.size === 0 || importLoading}>{importLoading ? "Importando…" : `Importar ${selectedImports.size}`}</button>
        </div>
      </div>
    </div>}
  </div>;
}

function WorkloomView({ activeWorkspace }) {
  const [data, setData] = useState({ routine_runs: [], drafts: [], gold_candidates: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const r = await apiGet(`/api/workspaces/${activeWorkspace.id}/workloom`);
      setData({ routine_runs: r.routine_runs || [], drafts: r.drafts || [], gold_candidates: r.gold_candidates || [] });
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const askReason = (label) => window.prompt(`Razón para ${label} (opcional):`) || undefined;

  const approveRun = async (run) => {
    if (!window.confirm(`¿Aprobar el run ${run.id}?`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routine-runs/${run.id}/approve`, { reason: askReason("aprobar run"), urgency: 0 });
      await load();
    } catch (err) { setError(err.message); }
  };

  const rejectRun = async (run) => {
    if (!window.confirm(`¿Rechazar el run ${run.id}?`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routine-runs/${run.id}/reject`, { reason: askReason("rechazar run") });
      await load();
    } catch (err) { setError(err.message); }
  };

  const approveDraft = async (draft) => {
    if (!window.confirm(`¿Aprobar el borrador ${draft.id}?`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/drafts/${draft.id}/approve`, { reason: askReason("aprobar borrador"), urgency: 0 });
      await load();
    } catch (err) { setError(err.message); }
  };

  const rejectDraft = async (draft) => {
    if (!window.confirm(`¿Rechazar el borrador ${draft.id}?`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/drafts/${draft.id}/reject`, { reason: askReason("rechazar borrador") });
      await load();
    } catch (err) { setError(err.message); }
  };

  const applyGold = async (candidate) => {
    if (!window.confirm(`¿Aplicar el gold candidate ${candidate.id} a la rutina?`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/gold-candidates/${candidate.id}/apply-to-routine`);
      await load();
    } catch (err) { setError(err.message); }
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  if (!activeWorkspace) return <WorkspaceRequired icon="check" title="WorkLoom"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead"><div><div className="vtitle">WorkLoom</div><div className="vsub">Qué necesita tu criterio hoy · la resolución vive en el workspace</div></div></div>
    {error && <div style={S.error}>{error}</div>}
    {loading && <div style={S.loading}>Cargando WorkLoom…</div>}
    <div style={S.grid3}>
      <section className="panel" aria-label="Routine runs">
        <div className="panel-header"><div><div className="panel-kicker">WorkLoom</div><div className="panel-title">Routine runs ({data.routine_runs.length})</div></div></div>
        <div style={S.panelBody}>
          {data.routine_runs.length === 0 && <div style={S.empty}>Sin runs.</div>}
          <div style={S.list}>{data.routine_runs.map((run) => <div key={run.id} style={S.card}>
            <div style={S.cardTitle}>{run.id}</div>
            <div style={S.cardMeta}>routine {run.routine_id}</div>
            <div style={{ marginBottom: 8 }}><span className={statusClass(run.status)}>{run.status}</span></div>
            <Meter value={run.urgency || 0} max={10} label="Urgencia" variant={run.urgency >= 7 ? "vino" : run.urgency >= 4 ? "amber" : "sage"} />
            {run.reason && <div style={{ fontSize: 12, color: "var(--text-2)", marginBottom: 8 }}>{run.reason}</div>}
            <div style={S.inlineGroup}>
              <button style={S.buttonPrimary} onClick={() => approveRun(run)}>Aprobar</button>
              <button style={S.buttonDanger} onClick={() => rejectRun(run)}>Rechazar</button>
            </div>
          </div>)}</div>
        </div>
      </section>
      <section className="panel" aria-label="Drafts">
        <div className="panel-header"><div><div className="panel-kicker">WorkLoom</div><div className="panel-title">Drafts ({data.drafts.length})</div></div></div>
        <div style={S.panelBody}>
          {data.drafts.length === 0 && <div style={S.empty}>Sin drafts.</div>}
          <div style={S.list}>{data.drafts.map((draft) => <div key={draft.id} style={S.card}>
            <div style={S.cardTitle}>{draft.subject || "(sin asunto)"}</div>
            <div style={S.cardMeta}>{draft.id}</div>
            <div style={{ marginBottom: 8 }}><span className={statusClass(draft.status)}>{draft.status}</span></div>
            <Meter value={draft.urgency || 0} max={10} label="Urgencia" variant={draft.urgency >= 7 ? "vino" : draft.urgency >= 4 ? "amber" : "sage"} />
            {draft.reason && <div style={{ fontSize: 12, color: "var(--text-2)", marginBottom: 8 }}>{draft.reason}</div>}
            <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 8 }}>{draft.body_md.slice(0, 160)}…</div>
            <div style={S.inlineGroup}>
              <button style={S.buttonPrimary} onClick={() => approveDraft(draft)}>Aprobar</button>
              <button style={S.buttonDanger} onClick={() => rejectDraft(draft)}>Rechazar</button>
            </div>
          </div>)}</div>
        </div>
      </section>
      <section className="panel" aria-label="Gold candidates">
        <div className="panel-header"><div><div className="panel-kicker">WorkLoom</div><div className="panel-title">Gold candidates ({data.gold_candidates.length})</div></div></div>
        <div style={S.panelBody}>
          {data.gold_candidates.length === 0 && <div style={S.empty}>Sin gold candidates.</div>}
          <div style={S.list}>{data.gold_candidates.map((candidate) => <div key={candidate.id} style={S.card}>
            <div style={S.cardTitle}>{candidate.id}</div>
            <div style={S.cardMeta}>routine {candidate.routine_id} · run {candidate.run_id}</div>
            <div style={{ fontSize: 12, marginBottom: 8 }}>approved {candidate.approved ? "sí" : "no"} · used {candidate.used ? "sí" : "no"}</div>
            <div style={S.inlineGroup}>
              <button style={S.buttonPrimary} onClick={() => applyGold(candidate)}>Aplicar a rutina</button>
            </div>
          </div>)}</div>
        </div>
      </section>
    </div>
  </div>;
}

const PROVIDER_LABELS = {
  openai: "OpenAI",
  anthropic: "Anthropic",
  google: "Google / Gemini",
  kimi: "Kimi / Moonshot",
  ollama: "Ollama (local)",
};

function SettingsView({ activeWorkspace }) {
  const [configs, setConfigs] = useState([]);
  const [modelAllowlist, setModelAllowlist] = useState({});
  const [routerStatus, setRouterStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [edits, setEdits] = useState({});
  const [error, setError] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const [cfgData, statusData] = await Promise.all([
        apiGet(`/api/workspaces/${activeWorkspace.id}/providers`),
        apiGet(`/api/workspaces/${activeWorkspace.id}/router/status`),
      ]);
      setConfigs(cfgData.providers);
      setModelAllowlist(cfgData.model_allowlist || {});
      setRouterStatus(statusData);
      const initialEdits = {};
      cfgData.providers.forEach((p) => {
        initialEdits[p.provider_slug] = {
          api_key: "",
          base_url: p.base_url || "",
          model_default: p.model_default,
          priority: p.priority,
          is_enabled: p.is_enabled,
        };
      });
      setEdits(initialEdits);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  const updateEdit = (slug, field, value) => {
    setEdits((prev) => ({ ...prev, [slug]: { ...prev[slug], [field]: value } }));
  };

  const save = async (slug) => {
    const draft = edits[slug] || {};
    const body = {};
    if (draft.api_key && draft.api_key.trim()) body.api_key = draft.api_key.trim();
    if (draft.base_url !== undefined) body.base_url = draft.base_url.trim() || null;
    if (draft.model_default !== undefined) body.model_default = draft.model_default;
    if (draft.priority !== undefined) body.priority = Number(draft.priority);
    if (draft.is_enabled !== undefined) body.is_enabled = Boolean(draft.is_enabled);

    setSaving((s) => ({ ...s, [slug]: true }));
    setError(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/providers/${slug}`, body);
      await load();
      setEdits((prev) => ({ ...prev, [slug]: { ...prev[slug], api_key: "" } }));
    } catch (err) {
      setError(err.message);
    }
    setSaving((s) => ({ ...s, [slug]: false }));
  };

  const clearKey = async (slug) => {
    setError(null);
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/providers/${slug}/key`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const test = async (slug) => {
    setTesting((s) => ({ ...s, [slug]: true }));
    setError(null);
    try {
      const r = await apiPost(`/api/workspaces/${activeWorkspace.id}/providers/${slug}/test`, {});
      setTestResults((prev) => ({ ...prev, [slug]: r }));
    } catch (err) {
      setError(err.message);
    }
    setTesting((s) => ({ ...s, [slug]: false }));
  };

  if (!activeWorkspace) return <WorkspaceRequired icon="settings" title="Ajustes"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead"><div><div className="vtitle">Ajustes</div><div className="vsub">Router, proveedores y API keys</div></div></div>
    {error && <div style={S.error}>{error}</div>}
    {loading && <div style={S.loading}>Cargando ajustes…</div>}
    <div style={S.grid2}>
      {configs.map((cfg) => {
        const status = routerStatus?.providers?.find((p) => p.provider_slug === cfg.provider_slug);
        const draft = edits[cfg.provider_slug] || {};
        const allowedModels = modelAllowlist[cfg.provider_slug] || [];
        const testResult = testResults[cfg.provider_slug];
        return <section key={cfg.provider_slug} className="panel provider-card" aria-label={`Configuración ${PROVIDER_LABELS[cfg.provider_slug]}`}>
          <div className="panel-header">
            <div><div className="panel-kicker">Provider</div><div className="panel-title">{PROVIDER_LABELS[cfg.provider_slug]}</div></div>
            <span className={status ? statusClass(status.available ? "succeeded" : (status.reason || "failed")) : "badge"}>
              {status ? (status.available ? "disponible" : (status.reason || "no disponible")) : "cargando"}
            </span>
          </div>
          <div style={S.panelBody}>
            <div style={S.form}>
              <label style={S.label}>
                API key
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    type="password"
                    style={S.input}
                    value={draft.api_key || ""}
                    placeholder={cfg.api_key_masked || "Sin API key guardada"}
                    onChange={(e) => updateEdit(cfg.provider_slug, "api_key", e.target.value)}
                  />
                  {cfg.api_key_masked && <button type="button" style={S.button} onClick={() => clearKey(cfg.provider_slug)} title="Borrar key guardada"><Icon name="trash" size={16}/></button>}
                </div>
              </label>
              <label style={S.label}>
                Modelo default
                <select style={S.select} value={draft.model_default || cfg.model_default} onChange={(e) => updateEdit(cfg.provider_slug, "model_default", e.target.value)}>
                  {allowedModels.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <label style={S.label}>
                  Prioridad
                  <input type="number" style={S.input} value={draft.priority ?? cfg.priority} onChange={(e) => updateEdit(cfg.provider_slug, "priority", e.target.value)} />
                </label>
                <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8, paddingTop: 18 }}>
                  <Toggle checked={Boolean(draft.is_enabled ?? cfg.is_enabled)} onChange={(checked) => updateEdit(cfg.provider_slug, "is_enabled", checked)} />
                  Habilitado
                </div>
              </div>
              <label style={S.label}>
                Base URL (opcional)
                <input type="text" style={S.input} value={draft.base_url ?? (cfg.base_url || "")} onChange={(e) => updateEdit(cfg.provider_slug, "base_url", e.target.value)} placeholder="https://api…" />
              </label>
              <div style={S.inlineGroup}>
                <button type="button" style={S.buttonPrimary} onClick={() => save(cfg.provider_slug)} disabled={saving[cfg.provider_slug]}>
                  <Icon name="check" size={16}/> Guardar
                </button>
                <button type="button" style={S.button} onClick={() => test(cfg.provider_slug)} disabled={testing[cfg.provider_slug]}>
                  <Icon name="refresh" size={16}/> Probar
                </button>
                {saving[cfg.provider_slug] && <span style={{ color: "var(--text-muted)" }}>Guardando…</span>}
                {testing[cfg.provider_slug] && <span style={{ color: "var(--text-muted)" }}>Probando…</span>}
              </div>
              {testResult && <div className={testResult.ok ? "status-tag approved" : "status-tag rejected"} style={{ marginTop: 8, fontSize: 12 }}>
                {testResult.ok ? `Conectado · ${testResult.model} · ${testResult.latency_ms} ms` : `Error: ${testResult.error}`}
              </div>}
            </div>
          </div>
        </section>;
      })}
      <section className="panel" aria-label="Estado del router">
        <div className="panel-header"><div><div className="panel-kicker">Admin</div><div className="panel-title">Router status</div></div></div>
        <div style={S.panelBody}>
          {routerStatus && <pre style={S.pre}>{prettyJson(routerStatus)}</pre>}
        </div>
      </section>
    </div>
  </div>;
}

function AuditView({ activeWorkspace }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const r = await apiGet(`/api/workspaces/${activeWorkspace.id}/editorial-history`);
      setEvents(Array.isArray(r.events) ? r.events : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  if (!activeWorkspace) return <WorkspaceRequired icon="audit" title="Auditoría"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead"><div><div className="vtitle">Auditoría</div><div className="vsub">Editorial history · trazabilidad de decisiones</div></div></div>
    <section className="panel" aria-label="Editorial history">
      <div className="panel-header"><div><div className="panel-kicker">Admin</div><div className="panel-title">Editorial history ({events.length})</div></div></div>
      <div style={S.panelBody}>
        {loading && <div style={S.loading}>Cargando…</div>}
        {error && <div style={S.error}>{error}</div>}
        {events.length === 0 && !loading && <div style={S.empty}>Sin eventos.</div>}
        <div style={S.list}>
          {events.map((event) => <div key={event.id} style={S.card}>
            <div style={S.cardTitle}>{event.action}</div>
            <div style={S.cardMeta}>{event.entity_type} · {event.entity_id} · {event.created_at}</div>
            {event.reason && <div style={{ fontSize: 12, color: "var(--text-2)" }}>{event.reason}</div>}
          </div>)}
        </div>
      </div>
    </section>
  </div>;
}

function SendMailModal({ mailId, workspaceId, token, onClose, onSent }) {
  const [confirmationToken, setConfirmationToken] = useState("");
  const [idempotencyKey, setIdempotencyKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const params = new URLSearchParams({ confirmation_token: confirmationToken, idempotency_key: idempotencyKey });
      await apiPost(`/api/workspaces/${workspaceId}/mail/${mailId}/send?${params.toString()}`);
      onSent();
      onClose();
    } catch (err) {
      setError(err.message);
    }
    setBusy(false);
  };

  return <div style={S.modalOverlay} onClick={onClose}>
    <div style={S.modal} onClick={(e) => e.stopPropagation()}>
      <h3 style={S.modalTitle}>Confirmar envío de correo</h3>
      <p style={{ margin: 0, color: "var(--text-2)", fontSize: 13 }}>Escribe el confirmation_token mostrado y una idempotency_key única.</p>
      <div style={S.modalToken}>{token}</div>
      {error && <div style={S.error}>{error}</div>}
      <form style={S.form} onSubmit={submit}>
        <label style={S.label}>confirmation_token<input style={S.input} value={confirmationToken} onChange={(e) => setConfirmationToken(e.target.value)} required/></label>
        <label style={S.label}>idempotency_key<input style={S.input} value={idempotencyKey} onChange={(e) => setIdempotencyKey(e.target.value)} placeholder="ej: send-2024-001" required/></label>
        <div style={S.inlineGroup}>
          <button type="submit" style={S.buttonPrimary} disabled={busy}>{busy ? "Enviando…" : "Enviar"}</button>
          <button type="button" style={S.button} onClick={onClose} disabled={busy}>Cancelar</button>
        </div>
      </form>
    </div>
  </div>;
}

function MailView({ activeWorkspace }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sendModalMailId, setSendModalMailId] = useState(null);
  const [sendToken, setSendToken] = useState("");

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/mail`);
      setMessages(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const sync = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/mail/sync`);
      await load();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const draft = async (mail) => {
    if (!activeWorkspace) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/mail/${mail.id}/draft`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const openSend = async (mail) => {
    const token = await sha256Truncated(mail.id);
    setSendToken(token);
    setSendModalMailId(mail.id);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  if (!activeWorkspace) return <WorkspaceRequired icon="mail" title="Correo"/>;

  return <div className="classic" style={S.view}>
    {sendModalMailId && <SendMailModal mailId={sendModalMailId} workspaceId={activeWorkspace.id} token={sendToken} onClose={() => setSendModalMailId(null)} onSent={load}/>}
    <div className="vhead"><div><div className="vtitle">Correo</div><div className="vsub">Bandeja IMAP/SMTP con confirmación HITL</div></div><div className="vactions"><button style={S.button} onClick={sync} disabled={loading}>Sync IMAP</button></div></div>
    <section className="panel" aria-label="Correo">
      <div className="panel-header"><div><div className="panel-kicker">Mail</div><div className="panel-title">Bandeja ({messages.length})</div></div></div>
      <div style={S.panelBody}>
        {loading && <div style={S.loading}>Cargando…</div>}
        {error && <div style={S.error}>{error}</div>}
        {messages.length === 0 && !loading && <div style={S.empty}>Sin mensajes. Pulsa Sync IMAP para traer correos.</div>}
        <div style={S.list}>
          {messages.map((mail) => <div key={mail.id} style={S.card}>
            <div style={S.cardTitle}>{mail.subject || "(sin asunto)"}</div>
            <div style={S.cardMeta}>{mail.id} · {mail.sender || "sin remitente"} · {mail.status}</div>
            <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 8 }}>{(mail.body_text || "").slice(0, 200)}…</div>
            <div style={S.inlineGroup}>
              <button style={S.button} onClick={() => draft(mail)}>Generar borrador</button>
              <button style={S.buttonPrimary} onClick={() => openSend(mail)}>Enviar</button>
            </div>
          </div>)}
        </div>
      </div>
    </section>
  </div>;
}

function Canvas({ nav, activeWorkspace, status }) {
  return <main className="canvas">
    <ContextStrip activeWorkspace={activeWorkspace}/>
    {status === "error" && <div className="workspace-warning"><Icon/>No se pudo cargar /api/workspaces. El shell sigue disponible para revisar la interfaz.</div>}
    {nav === "space" ? <SpaceView activeWorkspace={activeWorkspace}/>
     : nav === "kb" ? <KBView activeWorkspace={activeWorkspace}/>
     : nav === "routines" ? <RoutinesView activeWorkspace={activeWorkspace}/>
     : nav === "workloom" ? <WorkloomView activeWorkspace={activeWorkspace}/>
     : nav === "settings" ? <SettingsView activeWorkspace={activeWorkspace}/>
     : nav === "audit" ? <AuditView activeWorkspace={activeWorkspace}/>
     : nav === "mail" ? <MailView activeWorkspace={activeWorkspace}/>
     : <PlaceholderView nav={nav}/>}
  </main>;
}

function App() {
  const boot = useMemo(readBootstrap, []);
  const [mode, setMode] = useState("operar");
  const [nav, setNav] = useState("space");
  const [workspaces, setWorkspaces] = useState(boot ? boot.workspaces : []);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState(boot ? boot.activeWorkspaceId : null);
  const [status, setStatus] = useState(boot && boot.workspaces.length ? "ready" : "loading");
  const [theme, setTheme] = useState(getInitialTheme);
  const [toasts, setToasts] = useState([]);
  const [cmdkOpen, setCmdkOpen] = useState(false);

  useEffect(() => { applyTheme(theme); }, [theme]);

  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); setCmdkOpen(true); }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

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

  const pushToast = (message, type = "info", duration = 3000) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, type, duration }]);
  };
  const dismissToast = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const handleCommand = (cmd) => {
    if (cmd.type === "nav") { setMode(cmd.mode); setNav(cmd.value); }
    if (cmd.type === "workspace") { setActiveWorkspaceId(cmd.value); pushToast("Workspace activo cambiado", "info"); }
    if (cmd.type === "theme") { setTheme(cmd.value); pushToast("Tema cambiado a " + cmd.value, "success"); }
  };

  const activeWorkspace = workspaces.find((workspace) => workspace.id === activeWorkspaceId) || null;
  return <div className="app-shell">
    <Topbar onOpenPalette={() => setCmdkOpen(true)} theme={theme} setTheme={setTheme}/>
    <CommandPalette isOpen={cmdkOpen} onClose={() => setCmdkOpen(false)} onSelect={handleCommand} workspaces={workspaces} activeWorkspaceId={activeWorkspaceId} nav={nav}/>
    <div className="frame"><Rail mode={mode} setMode={setMode} nav={nav} setNav={setNav} workspaces={workspaces} activeWorkspaceId={activeWorkspaceId} setActiveWorkspaceId={setActiveWorkspaceId} status={status}/><Canvas nav={nav} activeWorkspace={activeWorkspace} status={status}/></div>
    <ToastContainer toasts={toasts} onDismiss={dismissToast}/>
  </div>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
