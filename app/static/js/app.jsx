var { useCallback, useEffect, useMemo, useRef, useState } = React;

const MODES = [
  { id: "operar", label: "Operar" },
  { id: "aprender", label: "Aprender" },
  { id: "admin", label: "Admin" },
];

const NAV = {
  operar: [
    { id: "space", label: "FaberLoom", sub: "Canvas y chat", badge: "SL0", icon: "loom" },
    { id: "workloom", label: "WorkLoom", sub: "Cola HITL", badge: "SL3", icon: "check" },
    { id: "mail", label: "Correo", sub: "IMAP/SMTP HITL", badge: "SL5", icon: "mail" },
  ],
  aprender: [
    { id: "kb", label: "Knowledge Base", sub: "Fuentes y citas", badge: "SL2", icon: "book" },
    { id: "routines", label: "Routine Hub", sub: "Skills portables", badge: "SL3", icon: "spark" },
  ],
  admin: [
    { id: "settings", label: "Router / Proveedores", sub: "Modelos, keys y presupuesto", badge: "SL1", icon: "settings" },
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
  errorDetail: { padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginTop: 8, fontSize: 12, lineHeight: 1.5, whiteSpace: "pre-wrap", wordBreak: "break-word", overflowWrap: "anywhere", fontFamily: "var(--font-mono)" },
  success: { padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--sage-soft)", border: "1px solid var(--sage-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5, lineHeight: 1.5 },
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

function parsePreset(presetId) {
  if (!presetId || !presetId.includes(":")) return { provider_slug: "", model: "" };
  const [provider_slug, model] = presetId.split(":");
  return { provider_slug: provider_slug || "", model: model || "" };
}

function formatPreset(provider_slug, model) {
  if (!provider_slug || !model) return "";
  return `${provider_slug}:${model}`;
}

function isExecutableCategory(category) {
  return category === "skill" || category === "agent" || category === "custom";
}

function cx(...parts) { return parts.filter(Boolean).join(" "); }

function readBootstrap() {
  const boot = window.__FABERLOOM_BOOTSTRAP__;
  if (!boot || typeof boot !== "object") return null;
  const workspaces = Array.isArray(boot.workspaces) ? boot.workspaces : [];
  return { workspaces, activeWorkspaceId: boot.activeWorkspaceId || boot.active_workspace_id || (workspaces[0] && workspaces[0].id) || null };
}

function authHeaders() {
  // Auth basada en cookie HttpOnly `faberloom_at`, enviada automáticamente en
  // requests same-origin. Ya no se manda un Bearer desde localStorage (el login
  // ya no devuelve el token en el body; enviarlo producía `Bearer undefined` →
  // 401 "Invalid token").
  return {};
}

// Sesión: el access token (cookie HttpOnly, corta) puede expirar en medio del
// trabajo. Ante un 401 intentamos renovar con el refresh token (cookie de 7
// días, rotativa) y reintentamos el request una vez. Si el refresh también
// falla, recargamos la página para que AuthGate muestre el login.
let _refreshingSession = null;
function _refreshSession() {
  if (!_refreshingSession) {
    _refreshingSession = fetch("/api/auth/refresh", { method: "POST" })
      .then((res) => res.ok)
      .catch(() => false)
      .finally(() => { _refreshingSession = null; });
  }
  return _refreshingSession;
}

function _sessionLost() {
  if (window.__faberloomSessionLost) return;
  window.__faberloomSessionLost = true;
  localStorage.removeItem("faberloom_user");
  window.location.reload();
}

async function apiFetch(path, options = {}) {
  let res = await fetch(path, options);
  if (res.status === 401 && !String(path).startsWith("/api/auth/")) {
    const refreshed = await _refreshSession();
    if (refreshed) res = await fetch(path, options);
    if (res.status === 401) _sessionLost();
  }
  return res;
}

async function apiGet(path) {
  const res = await apiFetch(path, { headers: authHeaders() });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await apiFetch(path, { method: "POST", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify(body || {}) });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function apiPut(path, body) {
  const res = await apiFetch(path, { method: "PUT", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify(body || {}) });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function apiPatch(path, body) {
  const res = await apiFetch(path, { method: "PATCH", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify(body || {}) });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await apiFetch(path, { method: "DELETE", headers: authHeaders() });
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

function BudgetChip({ budget, onClick }) {
  if (!budget) return null;
  const pct = Math.min(100, Math.max(0, budget.budget_cap_usd ? (budget.spent_usd / budget.budget_cap_usd) * 100 : 0));
  const variant = pct >= 100 ? "over" : pct >= 75 ? "near" : "";
  return (
    <div className="budget-chip" onClick={onClick} title="Presupuesto del workspace">
      <div className="bbar"><div className={cx("bfill", variant)} style={{ width: pct + "%" }} /></div>
      <span className="bnum">${budget.spent_usd.toFixed(2)} / ${budget.budget_cap_usd.toFixed(0)}</span>
    </div>
  );
}

function Topbar({ onOpenPalette, theme, setTheme, budget, onToggleLeft, onToggleRight, onOpenRouting }) {
  return <header className="topbar">
    <button type="button" className="ceja" aria-label="Panel izquierdo" onClick={onToggleLeft}><Icon name="panel-l" size={18}/></button>
    <div className="brand" aria-label="FaberLoom">
      <span className="brand-mark"><BrandMark /></span>
      <span className="brand-word"><span className="brand-name"><span className="brand-faber">Faber</span><span className="brand-loom">Loom</span></span><span className="brand-sub">FaberLoom · local-first</span></span>
    </div>
    <div className="cmdk" role="button" tabIndex="0" onClick={onOpenPalette} aria-label="Buscar o ejecutar"><Icon name="search" size={16}/><span className="cmdk-label">Buscar o ejecutar…</span><kbd>Ctrl K</kbd></div>
    <div className="topbar-actions">
      <BudgetChip budget={budget} onClick={onOpenRouting} />
      <ThemeSwitcher theme={theme} onChange={setTheme} />
      <span className="status-chip"><span className="status-dot" aria-hidden="true"/>Local-first</span>
      <button type="button" className="ceja" aria-label="Panel derecho" onClick={onToggleRight}><Icon name="panel-r" size={18}/></button>
    </div>
  </header>;
}
const DOTS = ["var(--coral)", "var(--amber)", "var(--sage)", "var(--slate)", "var(--vino)"];

function RailItem({ label, icon, dot, badge, active, onClick }) {
  return <button type="button" className={cx("nav-item", active && "is-active")} onClick={onClick}>
    {dot ? <span className="dot" style={{ background: dot }} /> : <Icon name={icon} />}
    <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis" }}>{label}</span>
    {badge !== undefined && badge !== null && badge !== 0 && <span className={cx("nav-badge", typeof badge === "number" && badge > 0 && "op")}>{badge}</span>}
  </button>;
}

function Rail({ mode, setMode, nav, setNav, workspaces, activeWorkspaceId, setActiveWorkspaceId, status, activeWorkspace, hidden, user, onLogout, features, foundationView, setFoundationView }) {
  const [counts, setCounts] = useState({});

  const loadCounts = useCallback(async () => {
    if (!activeWorkspace) { setCounts({}); return; }
    const results = await Promise.allSettled([
      apiGet(`/api/workspaces/${activeWorkspace.id}/chats`),
      features?.email_connector_enabled
        ? apiGet(`/api/workspaces/${activeWorkspace.id}/mail`)
        : Promise.resolve([]),
      apiGet(`/api/workspaces/${activeWorkspace.id}/workloom`),
      apiGet(`/api/workspaces/${activeWorkspace.id}/routines`),
      apiGet(`/api/workspaces/${activeWorkspace.id}/kb/sources`),
      apiGet(`/api/workspaces/${activeWorkspace.id}/gold-candidates`),
    ]);
    const get = (res, fallback = []) => res.status === "fulfilled" ? res.value : fallback;
    const [chats, mail, workloom, routines, kb, gold] = results.map((r) => get(r, []));
    const draftCount = (workloom.drafts || []).length;
    const runCount = (workloom.routine_runs || []).length;
    setCounts({
      chats: Array.isArray(chats) ? chats.length : 0,
      mail: Array.isArray(mail) ? mail.length : 0,
      workloom: draftCount + runCount,
      drafts: draftCount,
      runs: runCount,
      skills: Array.isArray(routines) ? routines.filter((r) => (r.category || "custom") === "skill").length : 0,
      agents: Array.isArray(routines) ? routines.filter((r) => (r.category || "custom") === "agent").length : 0,
      routines: Array.isArray(routines) ? routines.length : 0,
      kb: Array.isArray(kb) ? kb.length : 0,
      gold: Array.isArray(gold) ? gold.length : 0,
    });
  }, [activeWorkspace, features]);

  useEffect(() => {
    loadCounts();
    const interval = setInterval(loadCounts, 30000);
    const handler = () => loadCounts();
    window.addEventListener("faberloom-refresh", handler);
    return () => {
      clearInterval(interval);
      window.removeEventListener("faberloom-refresh", handler);
    };
  }, [loadCounts]);

  const go = (newMode, id) => { setMode(newMode); setNav(id); };

  const workspaceItem = (ws, idx) => (
    <RailItem key={ws.id} label={ws.name} dot={DOTS[idx % DOTS.length]} active={ws.id === activeWorkspaceId} onClick={() => setActiveWorkspaceId(ws.id)} />
  );

  const activeAccordionId = {
    space: "space-acc",
    inbox: "entrada-acc", workloom: "entrada-acc",
    stackloom: "cola-acc",
    kb: "kb-acc", "hitl-signals": "kb-acc",
    gold: "gold-acc",
    skills: "caps-acc", agents: "caps-acc",
    routing: "tenant-acc", audit: "tenant-acc", users: "tenant-acc", settings: "tenant-acc",
    foundation: "tenant-acc",
  }[nav];

  return <aside className={cx("rail", hidden && "hidden")}>
    <div className="mode-group" aria-label="Modos de FaberLoom">
      {MODES.map((item) => <button key={item.id} type="button" className={cx("mode-button", mode === item.id && "is-active")} onClick={() => go(item.id, { operar: "space", aprender: "kb", admin: "settings" }[item.id])}>{item.label}</button>)}
    </div>
    <div className="navwrap">
      {mode === "operar" && <>
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
        <Accordion items={[
          { id: "space-acc", title: "FaberLoom", badge: counts.chats, children: <RailItem label="FaberLoom" icon="loom" active={nav === "space"} onClick={() => setNav("space")} /> }
        ]} defaultOpen={activeAccordionId === "space-acc" ? ["space-acc"] : []} />
        <Accordion items={[
          { id: "entrada-acc", title: "Entrada", badge: (features?.email_connector_enabled ? counts.mail : 0) + counts.workloom, children: <>
            {features?.email_connector_enabled && <RailItem label="Inbox" icon="inbox" badge={counts.mail} active={nav === "inbox"} onClick={() => setNav("inbox")} />}
            <RailItem label="WorkLoom" icon="check" badge={counts.workloom} active={nav === "workloom"} onClick={() => setNav("workloom")} />
          </> }
        ]} defaultOpen={activeAccordionId === "entrada-acc" ? ["entrada-acc"] : []} />
        <Accordion items={[
          { id: "myws-acc", title: "My Workspaces", badge: workspaces.length, children: <div style={{ display: "flex", flexDirection: "column" }}>{workspaces.map((ws, idx) => workspaceItem(ws, idx))}</div> }
        ]} defaultOpen={activeAccordionId === "myws-acc" ? ["myws-acc"] : []} />
        <Accordion items={[
          { id: "sharedws-acc", title: "Shared Workspaces", children: <div style={{ padding: "6px 8px", fontSize: 12, color: "var(--text-muted)" }}>Sin workspaces compartidos.</div> }
        ]} defaultOpen={activeAccordionId === "sharedws-acc" ? ["sharedws-acc"] : []} />
        <Accordion items={[
          { id: "hist-acc", title: "Historial", children: <div style={{ padding: "6px 8px", fontSize: 12, color: "var(--text-muted)" }}>Historial reciente aparecerá aquí.</div> }
        ]} defaultOpen={activeAccordionId === "hist-acc" ? ["hist-acc"] : []} />
      </>}
      {mode === "aprender" && <>
        <Accordion items={[
          { id: "cola-acc", title: "Cola", badge: counts.workloom, children: <RailItem label="StackLoom" icon="layers" badge={counts.workloom} active={nav === "stackloom"} onClick={() => setNav("stackloom")} /> }
        ]} defaultOpen={activeAccordionId === "cola-acc" ? ["cola-acc"] : []} />
        <Accordion items={[
          { id: "kb-acc", title: "Conocimiento", badge: counts.kb, children: <>
            <RailItem label="Conocimiento L0-L4" icon="book" badge={counts.kb} active={nav === "kb"} onClick={() => setNav("kb")} />
            <RailItem label="Señales HITL" icon="shield" active={nav === "hitl-signals"} onClick={() => setNav("hitl-signals")} />
          </> }
        ]} defaultOpen={activeAccordionId === "kb-acc" ? ["kb-acc"] : []} />
        <Accordion items={[
          { id: "gold-acc", title: "Gold Samples", badge: counts.gold, children: <RailItem label="Gold Samples" icon="spark" badge={counts.gold} active={nav === "gold"} onClick={() => setNav("gold")} /> }
        ]} defaultOpen={activeAccordionId === "gold-acc" ? ["gold-acc"] : []} />
      </>}
      {mode === "admin" && <>
        <Accordion items={[
          { id: "caps-acc", title: "Capacidades", badge: counts.routines, children: <>
            <RailItem label="Skills" icon="spark" badge={counts.skills} active={nav === "skills"} onClick={() => setNav("skills")} />
            <RailItem label="Agentes" icon="layers" badge={counts.agents} active={nav === "agents"} onClick={() => setNav("agents")} />
          </> }
        ]} defaultOpen={activeAccordionId === "caps-acc" ? ["caps-acc"] : []} />
        <Accordion items={[
          { id: "tenant-acc", title: "Tenant", children: <>
            <RailItem label="Router / Proveedores" icon="route" active={nav === "settings" || nav === "routing"} onClick={() => setNav("settings")} />
            <RailItem label="Audit" icon="audit" active={nav === "audit"} onClick={() => setNav("audit")} />
            <RailItem label="Tenant" icon="database" active={nav === "foundation"} onClick={() => { setNav("foundation"); setFoundationView("m16-tenant"); }} />
          </> }
        ]} defaultOpen={activeAccordionId === "tenant-acc" ? ["tenant-acc"] : []} />
      </>}
    </div>
    <div className="userfoot" onClick={onLogout} title="Cerrar sesión">
      <div className="avatar">{(user?.email || "U").slice(0, 2).toUpperCase()}</div>
      <div className="userfoot-meta">
        <div className="userfoot-email">{user?.email || "Usuario"}</div>
        <div className="userfoot-role">ADMIN · FaberLoom</div>
      </div>
      <div className="userfoot-logout">
        <Icon name="log-out" size={18} />
      </div>
    </div>
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

function ChatList({ chats, activeChatId, setActiveChatId, onCreate, onRename, onRequestDelete }) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  const startRename = (chat, event) => {
    event.stopPropagation();
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const commitRename = () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== chats.find((c) => c.id === editingId)?.title) {
      onRename(editingId, trimmed);
    }
    setEditingId(null);
    setEditTitle("");
  };

  const cancelRename = () => {
    setEditingId(null);
    setEditTitle("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      commitRename();
    } else if (event.key === "Escape") {
      cancelRename();
    }
  };

  return <section className="panel chat-list-panel" aria-label="Lista de chats">
    <div className="panel-header">
      <div><div className="panel-kicker">FaberLoom</div><div className="panel-title">Chats</div></div>
      <button type="button" className="ceja" onClick={onCreate} title="Nuevo chat"><Icon name="plus" size={18}/></button>
    </div>
    <div className="chat-list">
      {chats.length === 0 && <div className="chat-empty">Sin chats todavía. Crea uno para empezar.</div>}
      {chats.map((chat) => (
        <button key={chat.id} type="button" className={cx("chat-card", activeChatId === chat.id && "is-active")} onClick={() => setActiveChatId(chat.id)}>
          <span className="chat-row">
            {editingId === chat.id ? (
              <input
                className="chat-title-input"
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={commitRename}
                onKeyDown={handleKeyDown}
                onClick={(e) => e.stopPropagation()}
                autoFocus
              />
            ) : (
              <span className="chat-title" onDoubleClick={(e) => startRename(chat, e)} title="Doble clic para renombrar">{chat.title}</span>
            )}
            <span className="chat-actions">
              <button type="button" className="chat-action" onClick={(e) => startRename(chat, e)} title="Renombrar"><Icon name="edit" size={14}/></button>
              <button type="button" className="chat-action chat-action-danger" onClick={(e) => { e.stopPropagation(); onRequestDelete(chat); }} title="Borrar"><Icon name="trash" size={14}/></button>
            </span>
          </span>
          <span className="chat-time">{chat.created_at ? new Date(chat.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}</span>
        </button>
      ))}
    </div>
  </section>;
}

function EmptyMessages({ activeWorkspace }) {
  return <div className="empty-state"><div className="empty-loom" aria-hidden="true"><BrandMark/></div><h3>El telar está listo.</h3><p>Escribe abajo para crear un chat nuevo y conversar con el router SL1a en {activeWorkspace ? activeWorkspace.name : "tu workspace"}.</p></div>;
}

const THINKING_STEPS = [
  { key: "reason", label: "Razonando sobre tu consulta" },
  { key: "context", label: "Consultando el contexto del workspace" },
  { key: "route", label: "Seleccionando el modelo" },
  { key: "weave", label: "Tejiendo la respuesta" },
];

function ThinkingSteps({ stepIndex }) {
  const safeIndex = Math.min(Math.max(stepIndex, 0), THINKING_STEPS.length - 1);
  const step = THINKING_STEPS[safeIndex];
  return <span className="thinking-current" aria-live="polite">
    <span className="thinking-spinner" aria-hidden="true"/>
    {step.label}…
  </span>;
}

function Composer({ onSend, disabled, routerStatus, modelAllowlist, placeholder, activeWorkspace }) {
  const [draft, setDraft] = useState("");
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [mode, setMode] = useState("manual");
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [attachment, setAttachment] = useState(null);
  const [attachmentPreview, setAttachmentPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const availableProviders = (routerStatus?.providers || []).filter((p) => p.available);
  const availableModels = modelAllowlist[provider] || [];

  const clearAttachment = () => {
    if (attachmentPreview?.url) URL.revokeObjectURL(attachmentPreview.url);
    setAttachmentPreview(null);
    setAttachment(null);
  };

  const uploadFile = async (file) => {
    if (!activeWorkspace) return;
    setUploading(true);
    try {
      const presigned = await apiPost(`/api/workspaces/${activeWorkspace.id}/objects/presigned-upload`, {
        file_name: file.name,
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        origin: "upload",
      });
      const putRes = await fetch(presigned.upload_url, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type || "application/octet-stream" },
      });
      if (!putRes.ok) throw new Error(`Upload failed: ${putRes.status}`);
      await apiPost(`/api/workspaces/${activeWorkspace.id}/objects/confirm`, {
        object_id: presigned.object_id,
        etag: putRes.headers.get("ETag") || "",
        size_bytes: file.size,
      });
      setAttachment({ object_id: presigned.object_id, file_name: file.name, mime_type: file.type || "application/octet-stream" });
      setAttachmentPreview((prev) => prev && { ...prev, uploading: false });
    } catch (err) {
      alert(err.message);
      clearAttachment();
    } finally {
      setUploading(false);
    }
  };

  const startFileUpload = (file) => {
    if (!file) return;
    const url = file.type.startsWith("image/") ? URL.createObjectURL(file) : null;
    setAttachmentPreview({ file, url, uploading: true });
    uploadFile(file);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    event.target.value = "";
    startFileUpload(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    startFileUpload(event.dataTransfer.files[0]);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const submit = (event) => {
    event.preventDefault();
    const text = draft.trim();
    if ((!text && !attachment) || disabled || uploading) return;
    const options = { mode };
    if (mode === "manual" && provider && model) {
      options.provider_slug = provider;
      options.model = model;
    }
    if (attachment) {
      options.attachment_object_id = attachment.object_id;
      options.attachment_file_name = attachment.file_name;
      options.attachment_mime_type = attachment.mime_type;
    }
    onSend(text || "Analiza el archivo adjunto.", options);
    setDraft("");
    clearAttachment();
  };

  const handleProviderChange = (p) => {
    setProvider(p);
    setModel("");
  };

  const handleKeyDown = (event) => {
    if (event.key !== "Enter") return;
    if (event.ctrlKey || event.metaKey) {
      // Ctrl/Cmd + Enter inserts a newline (default textarea behaviour).
      return;
    }
    event.preventDefault();
    submit(event);
  };

  return <form className={cx("composer-shell", isDragging && "composer-drag-over")} onSubmit={submit} aria-label="Composer de chat" onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
    <div className="composer">
      {attachmentPreview && <div className="composer-attachment-preview">
        {attachmentPreview.url
          ? <img className="composer-attachment-thumb" src={attachmentPreview.url} alt={attachmentPreview.file.name} style={{ width: 44, height: 44, objectFit: "cover", borderRadius: 6, flexShrink: 0 }}/>
          : <div className="composer-attachment-thumb composer-attachment-doc"><Icon name="file" size={22}/></div>}
        <div className="composer-attachment-meta">
          <span className="composer-attachment-name">{attachmentPreview.file.name}</span>
          <span className="composer-attachment-status">{attachmentPreview.uploading ? "Subiendo…" : "Listo para enviar"}</span>
        </div>
        <button type="button" className="composer-tool" onClick={clearAttachment} title="Quitar adjunto" disabled={uploading}><Icon name="x" size={14}/></button>
      </div>}
      <div className="composer-input-row">
        <textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={handleKeyDown} placeholder={placeholder || (attachmentPreview ? "¿Qué quieres saber sobre el archivo adjunto?" : "Escribe tu mensaje… Usa @skill o /run.")} rows="2" disabled={disabled || uploading}/>
        <div className="composer-actions">
          <input type="file" ref={fileInputRef} style={{ display: "none" }} onChange={handleFileChange} disabled={disabled || uploading || attachmentPreview}/>
          <button type="button" className="composer-tool" disabled={disabled || uploading || attachmentPreview} onClick={() => fileInputRef.current?.click()} title="Adjuntar archivo">
            <Icon name="paperclip" size={16}/>
          </button>
          <button type="button" className="composer-tool" disabled={disabled || uploading} onClick={() => setShowModelPicker((v) => !v)} title="Modelo / proveedor / modo">
            <Icon name="route" size={16}/>{mode === "auto" ? "Auto" : (provider ? (PROVIDER_LABELS[provider] || provider) : "Auto (router)")}
          </button>
          <button type="submit" className="send-button" disabled={disabled || uploading || (!draft.trim() && !attachment)}><Icon name="send" size={16}/>Enviar</button>
        </div>
      </div>
    </div>
    {showModelPicker && <div className="composer-picker">
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <label style={{ ...S.label, margin: 0, fontSize: 12 }}>
          Modo
          <select style={S.select} value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="manual">Manual</option>
            <option value="auto">Auto</option>
          </select>
        </label>
        {mode === "manual" && <>
          <label style={{ ...S.label, margin: 0, fontSize: 12 }}>
            Proveedor
            <select style={S.select} value={provider} onChange={(e) => handleProviderChange(e.target.value)}>
              <option value="">Auto (router)</option>
              {availableProviders.map((p) => <option key={p.provider_slug} value={p.provider_slug}>{PROVIDER_LABELS[p.provider_slug] || p.provider_slug}</option>)}
            </select>
          </label>
          <label style={{ ...S.label, margin: 0, fontSize: 12 }}>
            Modelo
            <select style={S.select} value={model} onChange={(e) => setModel(e.target.value)} disabled={!provider}>
              <option value="">Seleccionar</option>
              {availableModels.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </label>
        </>}
        <button type="button" style={{ ...S.button, marginLeft: "auto" }} onClick={() => setShowModelPicker(false)}>Cerrar</button>
      </div>
    </div>}
    <div className="composer-note"><Icon name="shield" size={16}/>Las acciones destructivas requieren HITL y doble confirmación.</div>
  </form>;
}

function MessageAttachment({ workspaceId, attachment }) {
  const [imgUrl, setImgUrl] = useState(null);
  const isImage = (attachment.mime_type || "").startsWith("image/");
  useEffect(() => {
    let alive = true;
    if (isImage && attachment.object_id) {
      apiGet(`/api/workspaces/${workspaceId}/objects/${attachment.object_id}/url?expires_seconds=3600`)
        .then((r) => { if (alive) setImgUrl(r.download_url); })
        .catch(() => {});
    }
    return () => { alive = false; };
  }, [attachment.object_id]);
  const ext = ((attachment.file_name || "").split(".").pop() || "file").toUpperCase().slice(0, 4);
  if (isImage) {
    return <div className="message-attachment">
      {imgUrl
        ? <img className="message-attachment-img" src={imgUrl} alt={attachment.file_name}/>
        : <div className="message-attachment-img message-attachment-img-loading"><Icon name="file" size={18}/></div>}
      <span className="message-attachment-caption">{attachment.file_name}</span>
    </div>;
  }
  return <div className="message-attachment message-attachment-doc">
    <span className={`file-ext-badge file-ext-${ext.toLowerCase()}`}>{ext}</span>
    <div className="message-attachment-meta">
      <span className="message-attachment-name">{attachment.file_name}</span>
      {attachment.size_bytes ? <span className="message-attachment-size">{(attachment.size_bytes / 1024).toFixed(1)} KB</span> : null}
    </div>
  </div>;
}

function stripAttachmentMarkers(content) {
  return String(content || "")
    .replace(/\n*\[Imagen adjunta:[^\]]*\]/g, "")
    .replace(/\n*--- Contenido del adjunto[\s\S]*?--- Fin del adjunto ---/g, "")
    .replace(/\n*\[Adjunto:[^\]]*\]/g, "")
    .trim();
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
  const [activeChatId, setActiveChatIdLocal] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [thinkingStepIndex, setThinkingStepIndex] = useState(0);
  const [typingTarget, setTypingTarget] = useState(null);
  const [typedContent, setTypedContent] = useState("");
  const [error, setError] = useState(null);
  const [routerStatus, setRouterStatus] = useState(null);
  const [modelAllowlist, setModelAllowlist] = useState({});
  const [deleteChatTarget, setDeleteChatTarget] = useState(null);
  const [deleteChatToken, setDeleteChatToken] = useState("");
  const messageAreaRef = useRef(null);

  const setActiveChatId = (chatId) => {
    setActiveChatIdLocal(chatId);
    window.__faberloomActiveChatId = chatId;
  };

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

  const loadRouter = async () => {
    if (!activeWorkspace) return;
    try {
      const [status, cfg] = await Promise.all([
        apiGet(`/api/workspaces/${activeWorkspace.id}/router/status`),
        apiGet(`/api/workspaces/${activeWorkspace.id}/providers`),
      ]);
      setRouterStatus(status);
      setModelAllowlist(cfg.model_allowlist || {});
    } catch {
      setRouterStatus(null);
      setModelAllowlist({});
    }
  };

  useEffect(() => { loadChats(); loadRouter(); }, [activeWorkspace]);
  useEffect(() => { loadMessages(activeChatId); }, [activeChatId]);

  // Auto-scroll to the newest message / thinking indicator.
  useEffect(() => {
    if (messageAreaRef.current) {
      messageAreaRef.current.scrollTop = messageAreaRef.current.scrollHeight;
    }
  }, [messages, busy]);

  // Cycle the thinking steps while the telar is busy.
  useEffect(() => {
    if (!busy) {
      setThinkingStepIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setThinkingStepIndex((idx) => (idx + 1) % THINKING_STEPS.length);
    }, 2200);
    return () => clearInterval(interval);
  }, [busy]);

  // Typewriter reveal for the latest assistant response.
  useEffect(() => {
    if (!typingTarget) {
      setTypedContent("");
      return;
    }
    setTypedContent("");
    let index = 0;
    const interval = setInterval(() => {
      index += 1;
      setTypedContent(typingTarget.content.slice(0, index));
      if (index >= typingTarget.content.length) {
        clearInterval(interval);
        setTypingTarget(null);
      }
    }, 6);
    return () => clearInterval(interval);
  }, [typingTarget]);

  // Cancel any running typewriter when the user switches chats.
  useEffect(() => {
    setTypingTarget(null);
    setTypedContent("");
  }, [activeChatId]);

  useEffect(() => {
    const handler = async (e) => {
      const { routine_id } = e.detail || {};
      if (!activeWorkspace || !activeChatId || !routine_id) return;
      setBusy(true);
      setError(null);
      try {
        const body = { routine_id };
        const completion = await apiPost(`/api/workspaces/${activeWorkspace.id}/chats/${activeChatId}/invoke`, body);
        if (completion && completion.message) {
          setTypingTarget({ id: completion.message.id, content: completion.message.content });
        }
        await loadMessages(activeChatId);
        await loadChats();
        await loadRouter();
      } catch (err) {
        setError(err.message);
      }
      setBusy(false);
    };
    window.addEventListener("faberloom:invoke-routine", handler);
    return () => window.removeEventListener("faberloom:invoke-routine", handler);
  }, [activeWorkspace, activeChatId]);

  const createChat = async () => {
    if (!activeWorkspace) return null;
    setError(null);
    try {
      const chat = await apiPost(`/api/workspaces/${activeWorkspace.id}/chats`, { title: "Nueva conversación" });
      setChats((prev) => [chat, ...prev]);
      setActiveChatId(chat.id);
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
      return chat.id;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  const ensureActiveChat = async () => {
    if (activeChatId) return activeChatId;
    return await createChat();
  };

  const renameChat = async (chatId, title) => {
    if (!activeWorkspace) return;
    setError(null);
    try {
      const updated = await apiPatch(`/api/workspaces/${activeWorkspace.id}/chats/${chatId}`, { title });
      setChats((prev) => prev.map((c) => (c.id === chatId ? updated : c)));
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
    } catch (err) {
      setError(err.message);
    }
  };

  const requestDeleteChat = async (chat) => {
    if (!activeWorkspace) return;
    const token = await sha256Truncated(chat.id, 16);
    setDeleteChatTarget(chat);
    setDeleteChatToken(token);
  };

  const confirmDeleteChat = async (token) => {
    if (!activeWorkspace || !deleteChatTarget) return;
    if (token !== deleteChatToken) { setError("Token de confirmación incorrecto"); return; }
    setError(null);
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/chats/${deleteChatTarget.id}?confirmation_token=${encodeURIComponent(token)}`);
      setChats((prev) => prev.filter((c) => c.id !== deleteChatTarget.id));
      if (activeChatId === deleteChatTarget.id) {
        setActiveChatId(null);
      }
      setDeleteChatTarget(null);
      setDeleteChatToken("");
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
    } catch (err) {
      setError(err.message);
    }
  };

  const sendMessage = async (text, options = {}) => {
    if (!activeWorkspace) return;
    setBusy(true);
    setError(null);
    try {
      const chatId = await ensureActiveChat();
      if (!chatId) return;

      // Optimistically show the user message so the UI feels instant.
      const tempId = `temp_${Date.now()}`;
      const tempMessage = {
        id: tempId,
        role: "user",
        content: text,
        route: options.attachment_object_id ? { attachment: { object_id: options.attachment_object_id, file_name: options.attachment_file_name, mime_type: options.attachment_mime_type } } : null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempMessage]);

      const body = { message: text, mode: options.mode || "manual" };
      if (options.provider_slug && options.model) {
        body.provider_slug = options.provider_slug;
        body.model = options.model;
      }
      if (options.attachment_object_id) {
        body.attachment_object_id = options.attachment_object_id;
      }
      const completion = await apiPost(`/api/workspaces/${activeWorkspace.id}/chats/${chatId}/completions`, body);
      if (completion && completion.message) {
        setTypingTarget({ id: completion.message.id, content: completion.message.content });
      }
      await loadMessages(chatId);
      await loadRouter();
      await loadChats();
      // Auto-title the first user message if the chat still has the default name.
      const chat = chats.find((c) => c.id === chatId) || { title: "Nueva conversación" };
      if (chat.title === "Nueva conversación") {
        const words = text.trim().split(/\s+/).slice(0, 6);
        const generated = words.join(" ") + (words.length >= 6 ? "…" : "");
        if (generated) await renameChat(chatId, generated);
      }
    } catch (err) {
      setError(err.message);
    }
    setBusy(false);
  };

  if (!activeWorkspace) return <WorkspaceRequired icon="loom" title="FaberLoom"/>;

  const activeChat = chats.find((c) => c.id === activeChatId);

  return <div className="space-view">
    {deleteChatTarget && <DeleteConfirmModal
      title="Borrar conversación"
      resourceName={deleteChatTarget.title}
      token={deleteChatToken}
      onClose={() => { setDeleteChatTarget(null); setDeleteChatToken(""); }}
      onConfirm={confirmDeleteChat}
    />}
    <ChatList chats={chats} activeChatId={activeChatId} setActiveChatId={setActiveChatId} onCreate={createChat} onRename={renameChat} onRequestDelete={requestDeleteChat}/>
    <section className="panel chat-stage" aria-label="Canvas central de FaberLoom">
      <div className="stage-header">
        <div className="stage-title"><h2>{activeChat ? activeChat.title : "Selecciona o crea un chat"}</h2><p>{activeChat ? "Conversación con el router SL1a." : "Elige un hilo para empezar."}</p></div>
        <span className="pill"><Icon name="loom" size={16}/>SL1a</span>
      </div>
      <div className="message-area" ref={messageAreaRef}>
        {loading && <div style={S.loading}>Cargando…</div>}
        {error && <div style={S.error}>{error}</div>}
        {!activeChat && !loading && <EmptyMessages activeWorkspace={activeWorkspace}/>}
        {messages.map((msg) => (
          <div key={msg.id} className={cx("message", msg.role === "user" ? "message-user" : "message-assistant")}>
            <div className="message-meta">{msg.role === "user" ? "Tú" : "FaberLoom"} · {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}</div>
            {msg.route && msg.route.attachment && <MessageAttachment workspaceId={activeWorkspace.id} attachment={msg.route.attachment}/>}
            <div className="message-content">{(() => {
              const raw = msg.role === "assistant" && typingTarget && typingTarget.id === msg.id ? typedContent : msg.content;
              return msg.route && msg.route.attachment ? stripAttachmentMarkers(raw) : raw;
            })()}</div>
            {msg.role === "assistant" && msg.route && (() => {
              const r = msg.route;
              const requested = r.requested_provider_slug || r.requested_model
                ? `${r.requested_provider_slug || "auto"}${r.requested_model ? "/" + r.requested_model : ""}`
                : null;
              const actual = r.mode === "auto" && r.chain_id
                ? `auto · ${r.provider_slug}/${r.model} · ${(r.steps || []).length} pasos`
                : `${r.provider_slug}/${r.model}`;
              const routeLabel = requested && requested !== actual && r.mode !== "auto"
                ? `${requested} → ${actual}`
                : actual;
              const budgetUsd = typeof r.budget_usd === "number" ? r.budget_usd : (r.cost_usd || 0);
              const budgetCap = typeof r.budget_cap_usd === "number" ? r.budget_cap_usd : null;
              return <div className="message-route">
                <span><Icon name="route" size={12}/> {routeLabel}</span>
                <span>Tokens: {r.input_tokens || 0} in · {r.output_tokens || 0} out</span>
                <span>Costo: ${Number(r.cost_usd || 0).toFixed(5)} · {r.duration_ms || 0} ms</span>
                {budgetCap !== null && <span>Budget: ${budgetUsd.toFixed(5)} / ${Number(budgetCap).toFixed(2)}</span>}
                {r.fallback && <span className="route-fallback">fallback</span>}
              </div>;
            })()}
          </div>
        ))}
        {busy && <div className="message message-assistant">
          <div className="message-meta">FaberLoom</div>
          <div className="message-content"><ThinkingSteps stepIndex={thinkingStepIndex}/></div>
        </div>}
      </div>
      <Composer onSend={sendMessage} disabled={busy} placeholder={activeChat ? undefined : "Escribe para crear un chat nuevo…"} routerStatus={routerStatus} modelAllowlist={modelAllowlist} activeWorkspace={activeWorkspace}/>
    </section>
    <SeamPanel/>
  </div>;
}

function PlaceholderView({ nav }) {
  const labels = { workloom: "WorkLoom", kb: "Knowledge Base", routines: "Routine Hub", settings: "Ajustes", audit: "Auditoría", skills: "Skills", agents: "Agentes", gold: "Gold Samples", routing: "IA: modelos y ruteo", users: "Usuarios", inbox: "Inbox", mail: "Correo", stackloom: "StackLoom", "hitl-signals": "Señales HITL" };
  return <div className="placeholder"><div className="placeholder-card"><Icon name="loom"/><h2>{labels[nav] || "Vista futura"}</h2><p>Esta superficie queda señalizada en SL0, pero se implementa en hitos posteriores del plan FaberLoom.</p></div></div>;
}

function WorkspaceRequired({ icon, title }) {
  return <div className="placeholder"><div className="placeholder-card"><Icon name={icon}/><h2>{title}</h2><p>Selecciona un workspace activo para usar esta vista.</p></div></div>;
}

function ToolsetPanel({ activeWorkspace }) {
  const [tab, setTab] = useState("agents");
  const [routines, setRoutines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  useEffect(() => { load(); }, [activeWorkspace]);
  useEffect(() => {
    const handler = () => load();
    window.addEventListener("faberloom-refresh", handler);
    return () => window.removeEventListener("faberloom-refresh", handler);
  }, [activeWorkspace]);

  const invoke = (routine) => {
    window.dispatchEvent(new CustomEvent("faberloom:invoke-routine", {
      detail: { routine_id: routine.id },
    }));
  };

  const filtered = routines.filter((r) => {
    if (!r.is_active || !r.approved_by) return false;
    if (tab === "skills") return r.category === "skill";
    if (tab === "agents") return r.category === "agent";
    if (tab === "templates") return r.category === "template";
    if (tab === "knowledge") return r.category === "reference";
    return false;
  });

  const isExecutableTab = tab === "skills" || tab === "agents";

  return <div className="toolset-panel">
    <div className="toolset-tabs">
      {[
        { id: "agents", label: "Agentes", icon: "spark" },
        { id: "skills", label: "Skills", icon: "check" },
        { id: "templates", label: "Templates", icon: "layers" },
        { id: "knowledge", label: "Conocimiento", icon: "book" },
      ].map((t) => (
        <button key={t.id} className={cx("toolset-tab", tab === t.id && "active")} onClick={() => setTab(t.id)} title={t.label}>
          <Icon name={t.icon} size={16}/><span>{t.label}</span>
        </button>
      ))}
    </div>
    <div className="toolset-body">
      {loading && <div style={S.loading}>Cargando…</div>}
      {error && <div style={S.error}>{error}</div>}
      {!loading && filtered.length === 0 && <div style={S.empty}>No hay {tab} activos y aprobados.</div>}
      <div className="toolset-list">
        {filtered.map((routine) => (
          <ToolsetItem
            key={routine.id}
            routine={routine}
            onInvoke={isExecutableTab ? invoke : null}
          />
        ))}
      </div>
    </div>
  </div>;
}

function ToolsetItem({ routine, onInvoke }) {
  return <div className="toolset-card">
    <div className="toolset-card-head">
      <div className="toolset-card-title">{routine.name}</div>
      <span style={S.badge}>{routine.category}</span>
    </div>
    <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>{routine.id}</div>
    {routine.preset_id && <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 10 }}><Icon name="route" size={12}/> {routine.preset_id}</div>}
    {onInvoke && (
      <button className="toolset-invoke" onClick={() => onInvoke(routine)}>
        <Icon name="send" size={14}/>Invocar en chat
      </button>
    )}
    {!onInvoke && (
      <div style={{ fontSize: 11, color: "var(--text-muted)", padding: "6px 0" }}>No invocable desde chat</div>
    )}
  </div>;
}

function RightRail({ open, activeWorkspace }) {
  return <aside className={cx("rail3", !open && "hidden")} aria-label="Toolset">
    <div className="rail3-header">
      <Icon name="layers" size={18}/>
      <span>Toolset</span>
    </div>
    <ToolsetPanel activeWorkspace={activeWorkspace}/>
  </aside>;
}

function RoutineCard({ routine, onEdit, onApprove, onToggle, onDelete, onInvoke }) {
  return <div style={S.card}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
      <div>
        <div style={S.cardTitle}>{routine.name}</div>
        <div style={S.cardMeta}>{routine.id} · {routine.category || "custom"}</div>
      </div>
      <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
        <span style={routine.is_active ? S.badge : { ...S.badge, opacity: 0.6 }}>{routine.is_active ? "activo" : "inactivo"}</span>
        {routine.approved_by ? <span style={{ ...S.badge, background: "var(--coral-soft)" }}>aprobado</span> : <span style={S.badge}>borrador</span>}
      </div>
    </div>
    {routine.preset_id && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}><Icon name="route" size={12}/> {routine.preset_id}</div>}
    <div style={{ ...S.inlineGroup, marginTop: 10 }}>
      <button style={S.button} onClick={() => onEdit(routine)}>Editar</button>
      <button style={S.button} onClick={() => onToggle(routine)}>{routine.is_active ? "Desactivar" : "Activar"}</button>
      <button style={S.buttonDanger} onClick={() => onDelete(routine)}>Eliminar</button>
      {!routine.approved_by && <button style={S.buttonPrimary} onClick={() => onApprove(routine)}>Aprobar</button>}
      {onInvoke && routine.approved_by && routine.is_active && <button style={S.buttonPrimary} onClick={() => onInvoke(routine)}>Invocar</button>}
    </div>
  </div>;
}

function RoutineForm({ mode, initial, modelAllowlist, routerStatus, onSubmit, onCancel }) {
  const [form, setForm] = useState(initial);
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");

  useEffect(() => {
    setForm(initial);
    const preset = parsePreset(initial.preset_id || "");
    setProvider(preset.provider_slug || "");
    setModel(preset.model || "");
  }, [initial]);

  const providers = (routerStatus?.providers || []).filter((p) => p.available);
  const availableModels = modelAllowlist[provider] || [];

  const handleProviderChange = (p) => {
    setProvider(p);
    setModel("");
    setForm((prev) => ({ ...prev, preset_id: formatPreset(p, "") }));
  };

  const handleModelChange = (m) => {
    setModel(m);
    setForm((prev) => ({ ...prev, preset_id: formatPreset(provider, m) }));
  };

  const submit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return <form style={S.form} onSubmit={submit}>
    <label style={S.label}>Nombre<input style={S.input} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required/></label>
    <label style={S.label}>Categoría
      <select style={S.select} value={form.category || "custom"} onChange={(e) => setForm({ ...form, category: e.target.value })}>
        <option value="skill">Skill</option><option value="agent">Agente</option><option value="template">Template</option><option value="reference">Reference</option><option value="custom">Custom</option>
      </select>
    </label>
    <label style={S.label}>persona_md / prompt<textarea style={S.textarea} value={form.persona_md || ""} onChange={(e) => setForm({ ...form, persona_md: e.target.value })} rows={4}/></label>
    <label style={S.label}>skill_md / instrucciones<textarea style={S.textarea} value={form.skill_md || ""} onChange={(e) => setForm({ ...form, skill_md: e.target.value })} rows={8}/></label>
    <label style={S.label}>tools_allowlist (JSON array)<input style={S.input} value={form.tools_allowlist || "[]"} onChange={(e) => setForm({ ...form, tools_allowlist: e.target.value })}/></label>
    <label style={S.label}>schema_output_json (JSON schema)<textarea style={S.monoTextarea} value={form.schema_output_json || "{}"} onChange={(e) => setForm({ ...form, schema_output_json: e.target.value })} rows={5}/></label>
    <label style={S.label}>trigger_json (JSON array)<input style={S.input} value={form.trigger_json || "[]"} onChange={(e) => setForm({ ...form, trigger_json: e.target.value })}/></label>
    {routerStatus && <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      <label style={S.label}>Provider
        <select style={S.select} value={provider} onChange={(e) => handleProviderChange(e.target.value)}>
          <option value="">Sin preset</option>
          {providers.map((p) => <option key={p.provider_slug} value={p.provider_slug}>{PROVIDER_LABELS[p.provider_slug] || p.provider_slug}</option>)}
        </select>
      </label>
      <label style={S.label}>Modelo
        <select style={S.select} value={model} onChange={(e) => handleModelChange(e.target.value)} disabled={!provider}>
          <option value="">Seleccionar</option>
          {availableModels.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </label>
    </div>}
    <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
      <Toggle checked={form.is_active === 1} onChange={(checked) => setForm({ ...form, is_active: checked ? 1 : 0 })}/>
      Activo
    </div>
    <div style={S.inlineGroup}>
      <button type="submit" style={S.buttonPrimary}>{mode === "create" ? "Crear" : "Guardar"}</button>
      <button type="button" style={S.button} onClick={onCancel}>Cancelar</button>
    </div>
  </form>;
}

function useRoutines(activeWorkspace, categoryFilter) {
  const [routines, setRoutines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [routerStatus, setRouterStatus] = useState(null);
  const [modelAllowlist, setModelAllowlist] = useState({});

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const [list, status, cfg] = await Promise.all([
        apiGet(`/api/workspaces/${activeWorkspace.id}/routines`),
        apiGet(`/api/workspaces/${activeWorkspace.id}/router/status`),
        apiGet(`/api/workspaces/${activeWorkspace.id}/providers`),
      ]);
      const all = Array.isArray(list) ? list : [];
      setRoutines(categoryFilter ? all.filter((r) => r.category === categoryFilter) : all);
      setRouterStatus(status);
      setModelAllowlist(cfg.model_allowlist || {});
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace, categoryFilter]);
  useEffect(() => {
    const handler = () => load();
    window.addEventListener("faberloom-refresh", handler);
    return () => window.removeEventListener("faberloom-refresh", handler);
  }, [activeWorkspace, categoryFilter]);

  return { routines, loading, error, routerStatus, modelAllowlist, reload: load, setRoutines };
}

function useRoutineCrud(activeWorkspace, reload) {
  const [error, setError] = useState(null);

  const create = async (form, category) => {
    setError(null);
    const body = { ...form, category };
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines`, body);
      reload();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const update = async (id, form) => {
    setError(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/routines/${id}`, form);
      reload();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const approve = async (routine) => {
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}/approve`, { reason: "Aprobado desde Skills/Agents", urgency: 0 });
      reload();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const toggle = async (routine) => {
    setError(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}`, { is_active: routine.is_active ? 0 : 1 });
      reload();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const remove = async (routine) => {
    setError(null);
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}`);
      reload();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return { create, update, approve, toggle, remove, error, setError };
}

function SkillAgentView({ activeWorkspace, category, title, subtitle }) {
  const { routines, loading, error, routerStatus, modelAllowlist, reload } = useRoutines(activeWorkspace, category);
  const crud = useRoutineCrud(activeWorkspace, reload);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteToken, setDeleteToken] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);

  const initialForm = {
    name: "",
    category,
    persona_md: "",
    skill_md: "",
    tools_allowlist: "[]",
    schema_output_json: "{}",
    trigger_json: "[]",
    source_version: "",
    preset_id: "",
    is_active: 0,
  };

  const [createForm, setCreateForm] = useState(initialForm);
  const [editForm, setEditForm] = useState(initialForm);

  const startEdit = (routine) => {
    setEditing(routine.id);
    setEditForm({
      name: routine.name || "",
      category: routine.category || category,
      persona_md: routine.persona_md || "",
      skill_md: routine.skill_md || "",
      tools_allowlist: routine.tools_allowlist || "[]",
      schema_output_json: routine.schema_output_json || "{}",
      trigger_json: routine.trigger_json || "[]",
      source_version: routine.source_version || "",
      preset_id: routine.preset_id || "",
      is_active: routine.is_active ? 1 : 0,
    });
  };

  const handleCreate = async (form) => {
    await crud.create(form, category);
    setCreateForm(initialForm);
    setShowCreate(false);
  };

  const handleSaveEdit = async (form) => {
    await crud.update(editing, form);
    setEditing(null);
    setEditForm(initialForm);
  };

  const promptDelete = async (routine) => {
    const token = await sha256Truncated(routine.id);
    setDeleteToken(token);
    setDeleteTarget(routine);
  };

  const confirmDelete = async (token) => {
    if (token !== deleteToken) { crud.setError("Token de confirmación incorrecto"); return; }
    await crud.remove(deleteTarget);
    setDeleteTarget(null);
  };

  const invoke = (routine) => {
    window.dispatchEvent(new CustomEvent("faberloom:invoke-routine", {
      detail: { routine_id: routine.id },
    }));
  };

  if (!activeWorkspace) return <WorkspaceRequired icon={category === "agent" ? "spark" : "check"} title={title}/>;

  return <div className="classic" style={S.view}>
    <div className="vhead">
      <div><div className="vtitle">{title}</div><div className="vsub">{subtitle}</div></div>
      <button style={S.buttonPrimary} onClick={() => setShowCreate(true)}>Nuevo {category}</button>
    </div>
    {(error || crud.error) && <div style={S.error}>{error || crud.error}</div>}
    {loading && <div style={S.loading}>Cargando…</div>}
    <div style={S.grid2}>
      <section className="panel" aria-label={`Listado de ${category}s`}>
        <div className="panel-header"><div><div className="panel-kicker">{title}</div><div className="panel-title">{category}s ({routines.length})</div></div></div>
        <div style={S.panelBody}>
          {!loading && routines.length === 0 && <div style={S.empty}>No hay {category}s.</div>}
          <div style={S.list}>{routines.map((routine) => <RoutineCard key={routine.id} routine={routine} onEdit={startEdit} onApprove={crud.approve} onToggle={crud.toggle} onDelete={promptDelete} onInvoke={invoke}/>)}</div>
        </div>
      </section>
      {showCreate && <section className="panel" aria-label={`Crear ${category}`}>
        <div className="panel-header"><div><div className="panel-kicker">{title}</div><div className="panel-title">Nuevo {category}</div></div></div>
        <div style={S.panelBody}>
          <RoutineForm mode="create" initial={createForm} modelAllowlist={modelAllowlist} routerStatus={routerStatus} onSubmit={handleCreate} onCancel={() => setShowCreate(false)}/>
        </div>
      </section>}
      {editing && <section className="panel" aria-label={`Editar ${category}`}>
        <div className="panel-header"><div><div className="panel-kicker">{title}</div><div className="panel-title">Editar {category}</div></div></div>
        <div style={S.panelBody}>
          <RoutineForm mode="edit" initial={editForm} modelAllowlist={modelAllowlist} routerStatus={routerStatus} onSubmit={handleSaveEdit} onCancel={() => setEditing(null)}/>
        </div>
      </section>}
    </div>
    {deleteTarget && <DeleteConfirmModal title={`Eliminar ${category}`} resourceName={deleteTarget.name} token={deleteToken} onClose={() => setDeleteTarget(null)} onConfirm={confirmDelete}/>}
  </div>;
}

function SkillsView({ activeWorkspace }) {
  return <SkillAgentView activeWorkspace={activeWorkspace} category="skill" title="Skills" subtitle="Rutinas ejecutables de un solo turno"/>;
}

function AgentsView({ activeWorkspace }) {
  return <SkillAgentView activeWorkspace={activeWorkspace} category="agent" title="Agentes" subtitle="Rutinas con persona y prompt propios"/>;
}

function GoldView({ activeWorkspace }) { return <PlaceholderView nav="gold" />; }
function RoutingView({ activeWorkspace }) { return <SettingsView activeWorkspace={activeWorkspace} title="IA: modelos y ruteo" subtitle="Estado del router, proveedores y presupuesto" />; }
function UsersView({ activeWorkspace }) { return <PlaceholderView nav="users" />; }

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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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

function DeleteConfirmModal({ title, resourceName, token, onClose, onConfirm }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (event) => {
    event.preventDefault();
    if (input !== token) return;
    setBusy(true);
    try { await onConfirm(token); onClose(); } finally { setBusy(false); }
  };
  return <div style={S.modalOverlay} onClick={onClose}>
    <div style={S.modal} onClick={(e) => e.stopPropagation()}>
      <h3 style={S.modalTitle}>{title}</h3>
      <p style={{ margin: 0, color: "var(--text-2)", fontSize: 13 }}>Escribe el <strong>confirmation_token</strong> para eliminar <strong>{resourceName}</strong>. Esta acción no se puede deshacer.</p>
      <div style={S.modalToken}>{token}</div>
      <form style={S.form} onSubmit={submit}>
        <label style={S.label}>confirmation_token<input style={S.input} value={input} onChange={(e) => setInput(e.target.value)} required autoFocus/></label>
        <div style={S.inlineGroup}>
          <button type="submit" style={S.buttonDanger} disabled={busy || input !== token}>{busy ? "Eliminando…" : "Eliminar"}</button>
          <button type="button" style={S.button} onClick={onClose} disabled={busy}>Cancelar</button>
        </div>
      </form>
    </div>
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
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteToken, setDeleteToken] = useState("");

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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
    } catch (err) {
      setError(err.message);
    }
  };

  const approveRoutine = async (routine) => {
    if (!window.confirm(`¿Aprobar la rutina "${routine.name}"? Una vez aprobada podrá ejecutarse.`)) return;
    setError(null);
    try {
      await apiPost(`/api/workspaces/${activeWorkspace.id}/routines/${routine.id}/approve`);
      await load();
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
    } catch (err) {
      setError(err.message);
    }
  };

  const promptDelete = async (routine) => {
    setDeleteTarget(routine);
    setDeleteToken(await sha256Truncated(routine.id, 16));
  };

  const confirmDelete = async (token) => {
    if (!activeWorkspace || !deleteTarget) return;
    setError(null);
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/routines/${deleteTarget.id}?confirmation_token=${token}`);
      setDeleteTarget(null);
      await load();
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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
                <button style={S.buttonDanger} onClick={() => promptDelete(routine)}>Eliminar</button>
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

    {deleteTarget && <DeleteConfirmModal title="Eliminar rutina" resourceName={deleteTarget.name} token={deleteToken} onClose={() => setDeleteTarget(null)} onConfirm={confirmDelete}/>}
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

function SettingsView({ activeWorkspace, title = "Ajustes", subtitle = "Router, proveedores y API keys" }) {
  const [configs, setConfigs] = useState([]);
  const [modelAllowlist, setModelAllowlist] = useState({});
  const [routerStatus, setRouterStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [liveModels, setLiveModels] = useState({});
  const [edits, setEdits] = useState({});
  const [showKey, setShowKey] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteToken, setDeleteToken] = useState("");

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
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

  const isDirty = (cfg) => {
    const slug = cfg.provider_slug;
    const draft = edits[slug] || {};
    if (draft.api_key && draft.api_key.trim()) return true;
    if ((draft.base_url || "") !== (cfg.base_url || "")) return true;
    if ((draft.model_default || cfg.model_default) !== cfg.model_default) return true;
    if (Number(draft.priority) !== Number(cfg.priority)) return true;
    if (Boolean(draft.is_enabled) !== Boolean(cfg.is_enabled)) return true;
    return false;
  };

  const statusText = (status) => {
    if (!status) return { label: "cargando", className: "badge" };
    if (status.available) return { label: "configurado", className: statusClass("succeeded") };
    const reasons = {
      disabled: "deshabilitado",
      missing_api_key: "falta API key",
      not_in_allowlist: "no permitido",
      not_available: "no disponible",
    };
    return { label: reasons[status.reason] || status.reason || "no disponible", className: statusClass("failed") };
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
    setSuccess(null);
    try {
      await apiPatch(`/api/workspaces/${activeWorkspace.id}/providers/${slug}`, body);
      await load();
      setEdits((prev) => ({ ...prev, [slug]: { ...prev[slug], api_key: "" } }));
      setSuccess(`Configuración de ${PROVIDER_LABELS[slug] || slug} guardada.`);
    } catch (err) {
      setError(err.message);
    }
    setSaving((s) => ({ ...s, [slug]: false }));
  };

  const promptClearKey = async (slug) => {
    setError(null);
    const token = await sha256Truncated(slug, 16);
    setDeleteToken(token);
    setDeleteTarget(slug);
  };

  const clearKey = async (token) => {
    if (!deleteTarget || !activeWorkspace) return;
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/providers/${deleteTarget}/key?confirmation_token=${encodeURIComponent(token)}`);
      setDeleteTarget(null);
      setDeleteToken("");
      await load();
      setSuccess(`API key de ${PROVIDER_LABELS[deleteTarget] || deleteTarget} eliminada.`);
    } catch (err) {
      setError(err.message);
    }
  };

  const test = async (slug, cfg) => {
    setTesting((s) => ({ ...s, [slug]: true }));
    setError(null);
    setSuccess(null);
    try {
      const draft = edits[slug] || {};
      const body = {};
      if (draft.api_key && draft.api_key.trim()) body.api_key = draft.api_key.trim();
      if (draft.base_url !== undefined && draft.base_url !== (cfg.base_url || "")) body.base_url = draft.base_url || null;
      if (draft.model_default && draft.model_default !== cfg.model_default) body.model_default = draft.model_default;
      const r = await apiPost(`/api/workspaces/${activeWorkspace.id}/providers/${slug}/test`, body);
      setTestResults((prev) => ({ ...prev, [slug]: r }));
      if (r.models && Array.isArray(r.models) && r.models.length > 0) {
        setLiveModels((prev) => ({ ...prev, [slug]: r.models }));
      }
      if (r.ok) setSuccess(`Conexión con ${PROVIDER_LABELS[slug] || slug} exitosa.`);
    } catch (err) {
      setTestResults((prev) => ({ ...prev, [slug]: { ok: false, provider_slug: slug, error: err.message } }));
      setError(err.message);
    }
    setTesting((s) => ({ ...s, [slug]: false }));
  };

  if (!activeWorkspace) return <WorkspaceRequired icon="settings" title="Ajustes"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead"><div><div className="vtitle">{title}</div><div className="vsub">{subtitle}</div></div></div>
    {error && <div style={S.error}>{error}</div>}
    {success && <div style={S.success}>{success}</div>}
    {loading && <div style={S.loading}>Cargando ajustes…</div>}
    <div style={S.grid2}>
      {configs.map((cfg) => {
        const status = routerStatus?.providers?.find((p) => p.provider_slug === cfg.provider_slug);
        const draft = edits[cfg.provider_slug] || {};
        const allowedModels = liveModels[cfg.provider_slug] || modelAllowlist[cfg.provider_slug] || [];
        const testResult = testResults[cfg.provider_slug];
        const dirty = isDirty(cfg);
        const st = statusText(status);
        return <section key={cfg.provider_slug} className="panel provider-card" aria-label={`Configuración ${PROVIDER_LABELS[cfg.provider_slug]}`}>
          <div className="panel-header">
            <div><div className="panel-kicker">Provider</div><div className="panel-title">{PROVIDER_LABELS[cfg.provider_slug]}</div></div>
            <span className={st.className}>{st.label}</span>
          </div>
          <div style={S.panelBody}>
            <div style={S.form}>
              <label style={S.label}>
                API key
                {cfg.requires_api_key ? <>
                  <div className="provider-key-row">
                    <input
                      type={showKey[cfg.provider_slug] ? "text" : "password"}
                      style={{ ...S.input, minWidth: 0, flex: "1 1 auto" }}
                      value={draft.api_key || ""}
                      placeholder={cfg.api_key_masked ? "Key guardada · actualizar" : "Pega tu API key"}
                      onChange={(e) => updateEdit(cfg.provider_slug, "api_key", e.target.value)}
                    />
                    <button type="button" style={S.button} onClick={() => setShowKey((prev) => ({ ...prev, [cfg.provider_slug]: !prev[cfg.provider_slug] }))}>
                      {showKey[cfg.provider_slug] ? "Ocultar" : "Mostrar"}
                    </button>
                    {cfg.api_key_masked && <button type="button" style={S.button} onClick={() => promptClearKey(cfg.provider_slug)} title="Borrar key guardada"><Icon name="trash" size={16}/></button>}
                  </div>
                  {cfg.api_key_masked && <span className="provider-saved-key">Key guardada: {cfg.api_key_masked}</span>}
                  {cfg.requires_api_key && !cfg.api_key_masked && <div style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.4 }}>
                    No hay key guardada. Se usará la variable de entorno del provider (p. ej. KIMI_API_KEY / MOONSHOT_API_KEY) o un archivo <code>.env</code> en %LOCALAPPDATA%/FaberLoom.
                  </div>}
                </> : <div style={{ ...S.input, display: "flex", alignItems: "center", color: "var(--text-muted)", fontWeight: 400, textTransform: "none", letterSpacing: 0 }}>
                  No requiere API key (proveedor local)
                </div>}
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
                  <input type="number" min={0} max={1000} style={S.input} value={draft.priority ?? cfg.priority} onChange={(e) => updateEdit(cfg.provider_slug, "priority", e.target.value)} />
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
              {cfg.provider_slug === "kimi" && <div style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.4 }}>
                Endpoint Moonshot: usa <button type="button" style={{ ...S.button, padding: "3px 7px", fontSize: 11 }} onClick={() => updateEdit("kimi", "base_url", "https://api.moonshot.ai/v1")}>.ai</button>
                {" "}o{" "}
                <button type="button" style={{ ...S.button, padding: "3px 7px", fontSize: 11 }} onClick={() => updateEdit("kimi", "base_url", "https://api.moonshot.cn/v1")}>.cn</button>
                {" "}si tu key fue creada en platform.moonshot.cn.
                {" "}Las keys <code>sk-kimi-…</code> se enrutan automáticamente a <code>api.kimi.com/coding/v1</code>.
              </div>}
              {cfg.provider_slug === "kimi" && (draft.api_key || "").startsWith("sk-kimi-") && <div style={{ fontSize: 11, color: "var(--sage)", lineHeight: 1.4 }}>
                ✓ Se detectó key de Kimi Code / Coding Plan. Se usará el endpoint <code>api.kimi.com/coding/v1</code> con el modelo <code>kimi-for-coding</code> por defecto.
              </div>}
              <div style={S.inlineGroup}>
                <button type="button" style={S.buttonPrimary} onClick={() => save(cfg.provider_slug)} disabled={!dirty || saving[cfg.provider_slug]}>
                  <Icon name="check" size={16}/> {saving[cfg.provider_slug] ? "Guardando…" : "Guardar"}
                </button>
                <button type="button" style={S.button} onClick={() => test(cfg.provider_slug, cfg)} disabled={testing[cfg.provider_slug]}>
                  <Icon name="refresh" size={16}/> {testing[cfg.provider_slug] ? "Probando…" : "Probar"}
                </button>
              </div>
              {testResult && (testResult.ok
                ? <div className="status-tag approved" style={{ marginTop: 8, fontSize: 12 }}>Conectado · {testResult.model} · {testResult.latency_ms} ms</div>
                : <div style={S.errorDetail}>Error: {testResult.error}</div>
              )}
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
    {deleteTarget && <DeleteConfirmModal
      title={`Borrar API key de ${PROVIDER_LABELS[deleteTarget] || deleteTarget}`}
      resourceName={`API key de ${PROVIDER_LABELS[deleteTarget] || deleteTarget}`}
      token={deleteToken}
      onClose={() => { setDeleteTarget(null); setDeleteToken(""); }}
      onConfirm={clearKey}
    />}
  </div>;
}

function AuditHistoryPanel({ activeWorkspace }) {
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

  return <section className="panel" aria-label="Editorial history">
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
  </section>;
}

const SMTP_DEFAULTS = { host: "", port: 465, use_ssl: true, username: "", password: "", from_email: "", is_app_password: 1 };
const IMAP_DEFAULTS = { label: "", provider: "imap", host: "", port: 993, username: "", password: "", folders_json: '["INBOX"]', auth_type: "password", read_only: 1, is_default: 0, is_app_password: 1 };

function IMAPConfigPanel({ activeWorkspace }) {
  const [accounts, setAccounts] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ ...IMAP_DEFAULTS });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const list = await apiGet(`/api/workspaces/${activeWorkspace.id}/admin/imap-config`);
      setAccounts(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const reset = () => {
    setEditing(null);
    setForm({ ...IMAP_DEFAULTS });
  };

  const edit = (account) => {
    setEditing(account.id);
    setForm({
      label: account.label || "",
      provider: account.provider || "imap",
      host: account.host || "",
      port: account.port ?? 993,
      username: account.username || "",
      password: account.password || "",
      folders_json: account.folders_json || '["INBOX"]',
      auth_type: account.auth_type || "password",
      read_only: account.read_only ?? 1,
      is_default: account.is_default ?? 0,
      is_app_password: account.is_app_password ?? 1,
    });
  };

  const save = async () => {
    if (!activeWorkspace) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const payload = {
        ...form,
        port: Number(form.port),
        read_only: Number(form.read_only),
        is_default: Number(form.is_default),
        is_app_password: Number(form.is_app_password),
      };
      if (editing) {
        await apiPut(`/api/workspaces/${activeWorkspace.id}/admin/imap-config/${editing}`, payload);
      } else {
        await apiPost(`/api/workspaces/${activeWorkspace.id}/admin/imap-config`, payload);
      }
      await load();
      reset();
      setSuccess("Cuenta IMAP guardada.");
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  const remove = async (id) => {
    if (!activeWorkspace) return;
    if (!confirm("¿Eliminar esta cuenta IMAP?")) return;
    try {
      await apiDelete(`/api/workspaces/${activeWorkspace.id}/admin/imap-config/${id}`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return <section className="panel" aria-label="Configuración IMAP">
    <div className="panel-header"><div><div className="panel-kicker">Admin</div><div className="panel-title">IMAP</div></div></div>
    <div style={S.panelBody}>
      {loading && <div style={S.loading}>Cargando…</div>}
      {error && <div style={S.error}>{error}</div>}
      {success && <div style={S.success}>{success}</div>}
      <div style={{ ...S.form, opacity: loading ? 0.6 : 1 }}>
        <label style={S.label}>Etiqueta<input style={S.input} value={form.label} onChange={(e) => update("label", e.target.value)} placeholder="Cuenta principal"/></label>
        <label style={S.label}>Host<input style={S.input} value={form.host} onChange={(e) => update("host", e.target.value)} placeholder="imap.ejemplo.com"/></label>
        <label style={S.label}>Puerto<input type="number" style={S.input} value={form.port} onChange={(e) => update("port", e.target.value)} min={1} max={65535}/></label>
        <label style={S.label}>Usuario<input style={S.input} value={form.username} onChange={(e) => update("username", e.target.value)}/></label>
        <label style={S.label}>Contraseña<input type="password" style={S.input} value={form.password} onChange={(e) => update("password", e.target.value)}/></label>
        <label style={S.label}>Carpetas (JSON)<input style={S.input} value={form.folders_json} onChange={(e) => update("folders_json", e.target.value)} placeholder='["INBOX"]'/></label>
        <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
          <Toggle checked={!!form.is_default} onChange={(checked) => update("is_default", checked ? 1 : 0)}/>
          Cuenta por defecto
        </div>
        <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
          <Toggle checked={!!form.read_only} onChange={(checked) => update("read_only", checked ? 1 : 0)}/>
          Solo lectura
        </div>
        {form.auth_type === "password" && (
          <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
            <Toggle checked={!!form.is_app_password} onChange={(checked) => update("is_app_password", checked ? 1 : 0)}/>
            Es app-password (no la contraseña principal)
          </div>
        )}
        <div style={S.inlineGroup}>
          <button type="button" style={S.buttonPrimary} onClick={save} disabled={saving || (!editing && !form.password)}>{saving ? "Guardando…" : (editing ? "Actualizar" : "Agregar")}</button>
          {editing && <button type="button" style={S.button} onClick={reset}>Cancelar</button>}
        </div>
      </div>
      <div style={{ marginTop: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 8 }}>CUENTAS ({accounts.length})</div>
        {accounts.map((acc) => <div key={acc.id} style={S.card}>
          <div style={S.cardTitle}>{acc.label || acc.username} {acc.is_default ? <span style={S.badge}>default</span> : null}</div>
          <div style={S.cardMeta}>{acc.host}:{acc.port} · {acc.username} · {acc.auth_type}</div>
          <div style={S.inlineGroup}>
            <button style={S.button} onClick={() => edit(acc)}>Editar</button>
            <button style={S.buttonDanger} onClick={() => remove(acc.id)}>Eliminar</button>
          </div>
        </div>)}
      </div>
    </div>
  </section>;
}

function SMTPConfigPanel({ activeWorkspace }) {
  const [config, setConfig] = useState({ ...SMTP_DEFAULTS });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const cfg = await apiGet(`/api/workspaces/${activeWorkspace.id}/admin/smtp-config`);
      setConfig({
        host: cfg.host || "",
        port: cfg.port ?? 465,
        use_ssl: cfg.use_ssl ?? true,
        username: cfg.username || "",
        password: cfg.password || "",
        from_email: cfg.from_email || "",
        is_app_password: cfg.is_app_password ?? 1,
      });
    } catch (err) {
      // 404 is expected when no config has been saved yet.
      if (!err.message.includes("404")) {
        setError(err.message);
      }
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  const update = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const save = async () => {
    if (!activeWorkspace) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    setTestResult(null);
    try {
      const saved = await apiPut(`/api/workspaces/${activeWorkspace.id}/admin/smtp-config`, {
        ...config,
        port: Number(config.port),
        is_app_password: Number(config.is_app_password),
      });
      setConfig({
        host: saved.host || "",
        port: saved.port ?? 465,
        use_ssl: saved.use_ssl ?? true,
        username: saved.username || "",
        password: saved.password || "",
        from_email: saved.from_email || "",
        is_app_password: saved.is_app_password ?? 1,
      });
      setSuccess("Configuración SMTP guardada.");
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  const test = async () => {
    if (!activeWorkspace) return;
    setTesting(true);
    setError(null);
    setSuccess(null);
    setTestResult(null);
    try {
      const r = await apiPost(`/api/workspaces/${activeWorkspace.id}/admin/smtp-config/test`);
      setTestResult(r);
    } catch (err) {
      setError(err.message);
    }
    setTesting(false);
  };

  return <section className="panel" aria-label="Configuración SMTP">
    <div className="panel-header"><div><div className="panel-kicker">Admin</div><div className="panel-title">SMTP</div></div></div>
    <div style={S.panelBody}>
      {loading && <div style={S.loading}>Cargando…</div>}
      {error && <div style={S.error}>{error}</div>}
      {success && <div style={S.success}>{success}</div>}
      <div style={{ ...S.form, opacity: loading ? 0.6 : 1 }}>
        <label style={S.label}>Host<input style={S.input} value={config.host} onChange={(e) => update("host", e.target.value)} placeholder="mail.ejemplo.com"/></label>
        <label style={S.label}>Puerto<input type="number" style={S.input} value={config.port} onChange={(e) => update("port", e.target.value)} min={1} max={65535}/></label>
        <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
          <Toggle checked={config.use_ssl} onChange={(checked) => update("use_ssl", checked)}/>
          Usar SSL (puerto 465)
        </div>
        <label style={S.label}>Usuario<input style={S.input} value={config.username} onChange={(e) => update("username", e.target.value)}/></label>
        <label style={S.label}>Contraseña<input type="password" style={S.input} value={config.password} onChange={(e) => update("password", e.target.value)} placeholder="No se imprime en logs"/></label>
        <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
          <Toggle checked={!!config.is_app_password} onChange={(checked) => update("is_app_password", checked ? 1 : 0)}/>
          Es app-password (no la contraseña principal)
        </div>
        <label style={S.label}>From email<input style={S.input} value={config.from_email} onChange={(e) => update("from_email", e.target.value)}/></label>
        <div style={S.inlineGroup}>
          <button type="button" style={S.buttonPrimary} onClick={save} disabled={saving}>{saving ? "Guardando…" : "Guardar"}</button>
          <button type="button" style={S.button} onClick={test} disabled={testing}>{testing ? "Probando…" : "Probar"}</button>
        </div>
        {testResult && <div className="status-tag approved" style={{ marginTop: 8, fontSize: 12 }}>Prueba enviada a {testResult.sent_to} · {testResult.status}</div>}
      </div>
    </div>
  </section>;
}

function EmailSignaturePanel({ activeWorkspace }) {
  const [signature, setSignature] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const load = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet(`/api/workspaces/${activeWorkspace.id}/email-signature`);
      setSignature(data?.email_signature || "");
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  const save = async () => {
    if (!activeWorkspace) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await apiPut(`/api/workspaces/${activeWorkspace.id}/email-signature`, { email_signature: signature });
      setSuccess("Firma guardada.");
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  return <section className="panel" aria-label="Firma de correo">
    <div className="panel-header"><div><div className="panel-kicker">Admin</div><div className="panel-title">Firma de correo</div></div></div>
    <div style={S.panelBody}>
      {loading && <div style={S.loading}>Cargando…</div>}
      {error && <div style={S.error}>{error}</div>}
      {success && <div style={S.success}>{success}</div>}
      <div style={{ ...S.form, opacity: loading ? 0.6 : 1 }}>
        <label style={S.label}>Firma / footer<textarea style={S.textarea} value={signature} onChange={(e) => setSignature(e.target.value)} placeholder="Saludos,&#10;Equipo FaberLoom"/></label>
        <div style={S.inlineGroup}>
          <button type="button" style={S.buttonPrimary} onClick={save} disabled={saving}>{saving ? "Guardando…" : "Guardar"}</button>
        </div>
      </div>
    </div>
  </section>;
}

window.FaberLoomMailPanels = { IMAPConfigPanel, SMTPConfigPanel, EmailSignaturePanel };
window.WorkspaceRequired = WorkspaceRequired;

function AuditView({ activeWorkspace, features }) {
  if (!activeWorkspace) return <WorkspaceRequired icon="audit" title="Auditoría"/>;

  return <div className="classic" style={S.view}>
    <div className="vhead">
      <div><div className="vtitle">Auditoría</div><div className="vsub">Configuración del tenant y trazabilidad</div></div>
    </div>
    <AuditHistoryPanel activeWorkspace={activeWorkspace}/>
  </div>;
}

function SendMailModal({ mail, workspaceId, token, onClose, onSent }) {
  const [confirmationToken, setConfirmationToken] = useState("");
  const [idempotencyKey, setIdempotencyKey] = useState(() => `send-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const params = new URLSearchParams({ confirmation_token: confirmationToken, idempotency_key: idempotencyKey });
      await apiPost(`/api/workspaces/${workspaceId}/mail/${mail.id}/send?${params.toString()}`);
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
      <div style={{ marginBottom: 12, fontSize: 13, color: "var(--text-2)" }}>Revisa el destinatario y escribe el token de confirmación.</div>
      <div style={S.card}>
        <div style={S.cardMeta}>Para</div>
        <div style={S.cardTitle}>{mail.sender || "(sin remitente)"}</div>
        <div style={S.cardMeta}>Asunto</div>
        <div style={{ fontSize: 13, marginBottom: 8 }}>Re: {mail.subject || "(sin asunto)"}</div>
        <div style={S.cardMeta}>Cuerpo</div>
        <div style={{ fontSize: 12, color: "var(--text-2)" }}>Se enviará el borrador aprobado desde WorkLoom.</div>
      </div>
      <div style={S.modalToken}>{token}</div>
      {error && <div style={S.error}>{error}</div>}
      <form style={S.form} onSubmit={submit}>
        <label style={S.label}>confirmation_token<input style={S.input} value={confirmationToken} onChange={(e) => setConfirmationToken(e.target.value)} required/></label>
        <label style={S.label}>idempotency_key<input style={S.input} value={idempotencyKey} onChange={(e) => setIdempotencyKey(e.target.value)} required/></label>
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
  const [sendModalMail, setSendModalMail] = useState(null);
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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
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
      window.dispatchEvent(new CustomEvent("faberloom-refresh"));
    } catch (err) {
      setError(err.message);
    }
  };

  const openSend = async (mail) => {
    const token = await sha256Truncated(mail.id);
    setSendToken(token);
    setSendModalMail(mail);
  };

  useEffect(() => { load(); }, [activeWorkspace]);

  if (!activeWorkspace) return <WorkspaceRequired icon="mail" title="Correo"/>;

  return <div className="classic" style={S.view}>
    {sendModalMail && <SendMailModal mail={sendModalMail} workspaceId={activeWorkspace.id} token={sendToken} onClose={() => setSendModalMail(null)} onSent={load}/>}
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

function Canvas({ nav, activeWorkspace, status, features, foundationView }) {
  return <main className="canvas">
    <ContextStrip activeWorkspace={activeWorkspace}/>
    {status === "error" && <div className="workspace-warning"><Icon/>No se pudo cargar /api/workspaces. El shell sigue disponible para revisar la interfaz.</div>}
    {nav === "space" ? <SpaceView activeWorkspace={activeWorkspace}/>
     : nav === "kb" ? <KBView activeWorkspace={activeWorkspace}/>
     : nav === "routines" ? <RoutinesView activeWorkspace={activeWorkspace}/>
     : nav === "workloom" ? <WorkloomView activeWorkspace={activeWorkspace}/>
     : nav === "settings" || nav === "config" || nav === "routing" ? <SettingsView activeWorkspace={activeWorkspace}/>
     : nav === "audit" ? <AuditView activeWorkspace={activeWorkspace} features={features}/>
     : (nav === "mail" || nav === "inbox") && features?.email_connector_enabled ? <MailView activeWorkspace={activeWorkspace}/>
     : nav === "skills" ? <SkillsView activeWorkspace={activeWorkspace}/>
     : nav === "agents" ? <AgentsView activeWorkspace={activeWorkspace}/>
     : nav === "gold" ? <GoldView activeWorkspace={activeWorkspace}/>
     : nav === "users" ? <UsersView activeWorkspace={activeWorkspace}/>
     : nav === "stackloom" ? <PlaceholderView nav="stackloom"/>
     : nav === "hitl-signals" ? <PlaceholderView nav="hitl-signals"/>
     : nav === "foundation" && window.FoundationSection ? <window.FoundationSection initialView={foundationView} activeWorkspace={activeWorkspace}/>
     : <PlaceholderView nav={nav}/>}
  </main>;
}

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await apiPost("/api/auth/login", { email, password });
      // El login setea la cookie HttpOnly `faberloom_at`; el body solo trae el email.
      onLogin(res.email);
    } catch (err) {
      setError("Correo o contraseña incorrectos");
    }
    setBusy(false);
  };

  return (
    <div className="login-shell">
      <div className="login-bg" aria-hidden="true" />
      <form className="login-card" onSubmit={submit}>
        <div className="login-mark"><BrandMark /></div>
        <h1 className="login-title">FaberLoom</h1>
        <p className="login-tagline">La IA prepara. Vos tejés.</p>

        {error && <div className="login-error"><Icon name="shield" size={16} />{error}</div>}

        <div className="login-field">
          <label htmlFor="login-email">Correo electrónico</label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@empresa.com"
            required
            autoFocus
            autoComplete="email"
          />
        </div>

        <div className="login-field">
          <label htmlFor="login-password">Contraseña</label>
          <div className="login-password-wrap">
            <input
              id="login-password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
            <button
              type="button"
              className="login-password-toggle"
              onClick={() => setShowPassword((v) => !v)}
              aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              tabIndex={-1}
            >
              <Icon name={showPassword ? "eye-off" : "eye"} size={18} />
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="login-button"
          disabled={busy || !email || !password}
        >
          {busy ? (
            <>
              <span className="login-spinner" aria-hidden="true" />
              Entrando…
            </>
          ) : (
            <>
              Entrar
              <Icon name="arrow-up" size={16} />
            </>
          )}
        </button>

        <p className="login-hint">Solo usuarios autorizados.</p>
      </form>
    </div>
  );
}

function AuthGate() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Sesión basada en cookie HttpOnly: no podemos leerla desde JS, así que
    // pedimos la identidad resuelta al backend. Limpiamos el token legacy de
    // localStorage que ya no se usa (y que producía `Bearer undefined`).
    localStorage.removeItem("faberloom_token");
    apiGet("/api/me")
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem("faberloom_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogin = async (email) => {
    localStorage.setItem("faberloom_user", email);
    // Resolve real identity from the backend instead of trusting localStorage.
    const me = await apiGet("/api/me").catch(() => null);
    setUser(me || { email });
  };

  const logout = () => {
    // Revoca la cookie HttpOnly server-side (JS no puede borrarla).
    apiPost("/api/auth/logout").catch(() => {});
    localStorage.removeItem("faberloom_token");
    localStorage.removeItem("faberloom_user");
    setUser(null);
  };

  if (loading) return <div className="app-shell" style={{ display: "grid", placeItems: "center" }}><div className="loading">Cargando…</div></div>;
  if (!user) return <LoginScreen onLogin={handleLogin} />;
  return <App user={user} onLogout={logout} />;
}

function App({ user, onLogout }) {
  const boot = useMemo(readBootstrap, []);
  const [mode, setMode] = useState("operar");
  const [nav, setNav] = useState("space");
  const [workspaces, setWorkspaces] = useState(boot ? boot.workspaces : []);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState(boot ? boot.activeWorkspaceId : null);
  const [status, setStatus] = useState(boot && boot.workspaces.length ? "ready" : "loading");
  const [theme, setTheme] = useState(getInitialTheme);
  const [toasts, setToasts] = useState([]);
  const [cmdkOpen, setCmdkOpen] = useState(false);
  const [leftRailOpen, setLeftRailOpen] = useState(true);
  const [rightRailOpen, setRightRailOpen] = useState(false);
  const [budget, setBudget] = useState(null);
  const [features, setFeatures] = useState({ email_connector_enabled: false });
  const [foundationView, setFoundationView] = useState("m16-tenant");

  useEffect(() => { applyTheme(theme); }, [theme]);

  useEffect(() => {
    let cancelled = false;
    apiGet("/api/features")
      .then((data) => { if (!cancelled) setFeatures(data || { email_connector_enabled: false }); })
      .catch(() => { if (!cancelled) setFeatures({ email_connector_enabled: false }); });
    return () => { cancelled = true; };
  }, []);

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
    apiGet("/api/workspaces")
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

  useEffect(() => {
    if (!activeWorkspace) { setBudget(null); return; }
    let cancelled = false;
    apiGet(`/api/workspaces/${activeWorkspace.id}/router/status`)
      .then((data) => { if (!cancelled) setBudget(data || null); })
      .catch(() => { if (!cancelled) setBudget(null); });
    return () => { cancelled = true; };
  }, [activeWorkspace]);

  return <div className="app-shell">
    <Topbar onOpenPalette={() => setCmdkOpen(true)} theme={theme} setTheme={setTheme} budget={budget} onToggleLeft={() => setLeftRailOpen((v) => !v)} onToggleRight={() => setRightRailOpen((v) => !v)} onOpenRouting={() => { setMode("admin"); setNav("settings"); }}/>
    <CommandPalette isOpen={cmdkOpen} onClose={() => setCmdkOpen(false)} onSelect={handleCommand} workspaces={workspaces} activeWorkspaceId={activeWorkspaceId} nav={nav}/>
    <div className="frame">
      <Rail mode={mode} setMode={setMode} nav={nav} setNav={setNav} workspaces={workspaces} activeWorkspaceId={activeWorkspaceId} setActiveWorkspaceId={setActiveWorkspaceId} status={status} activeWorkspace={activeWorkspace} hidden={!leftRailOpen} user={user} onLogout={onLogout} features={features} foundationView={foundationView} setFoundationView={setFoundationView}/>
      <Canvas nav={nav} activeWorkspace={activeWorkspace} status={status} features={features} foundationView={foundationView}/>
      <RightRail open={rightRailOpen} activeWorkspace={activeWorkspace}/>
    </div>
    <ToastContainer toasts={toasts} onDismiss={dismissToast}/>
  </div>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<AuthGate/>);
