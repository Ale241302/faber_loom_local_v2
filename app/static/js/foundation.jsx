/* ═══════════════════════════════════════════════════════════════
   SpaceLoom · Foundation components
   Base UI primitives: Toggle, Meter, Accordion, Toast, CommandPalette,
   ThemeSwitcher and theme helpers. Loaded before app.jsx.
   ═══════════════════════════════════════════════════════════════ */

var { useEffect, useMemo, useRef, useState } = React;

function cx(...parts) { return parts.filter(Boolean).join(" "); }

const THEMES = [
  { id: "warm", label: "Warm", swatch: "#1B1A17" },
  { id: "slate", label: "Slate", swatch: "#16181B" },
  { id: "mono", label: "Mono", swatch: "#0E0D0C" },
  { id: "paper", label: "Paper", swatch: "#EDE8DF" },
  { id: "cloud", label: "Cloud", swatch: "#F4F1ED" },
  { id: "indigo", label: "Indigo", swatch: "#0F111A" },
  { id: "mist", label: "Mist", swatch: "#E9EDF2" },
];

function getInitialTheme() {
  try {
    const saved = localStorage.getItem("spaceloom-theme");
    if (saved) return saved;
  } catch (e) {}
  return "warm";
}

function applyTheme(theme) {
  try {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("spaceloom-theme", theme);
    const meta = document.querySelector('meta[name="color-scheme"]');
    if (meta) {
      const lightThemes = ["paper", "cloud", "mist"];
      meta.setAttribute("content", lightThemes.includes(theme) ? "light dark" : "dark");
    }
  } catch (e) {}
}

function Toggle({ checked, onChange, label }) {
  const id = useMemo(() => "tgl-" + Math.random().toString(36).slice(2, 8), []);
  return (
    <label htmlFor={id} className="toggle">
      <input id={id} type="checkbox" className="toggle-input" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="toggle-track" aria-hidden="true"><span className="toggle-thumb" /></span>
      {label && <span>{label}</span>}
    </label>
  );
}

function Meter({ value = 0, max = 100, label, variant }) {
  const pct = Math.min(100, Math.max(0, (Number(value) / Number(max)) * 100));
  return (
    <div className="meter">
      {label && <div className="meter-label"><span>{label}</span><span>{value} / {max}</span></div>}
      <div className="meter-track"><div className={cx("meter-fill", variant)} style={{ width: pct + "%" }} /></div>
    </div>
  );
}

function Accordion({ items, single = true }) {
  const [open, setOpen] = useState(new Set());
  const toggle = (id) => {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) { next.delete(id); return next; }
      if (single) next.clear();
      next.add(id);
      return new Set(next);
    });
  };
  return (
    <div className="accordion">
      {items.map((item) => (
        <div key={item.id} className={cx("accordion-item", open.has(item.id) && "is-open")}>
          <button type="button" className="accordion-trigger" onClick={() => toggle(item.id)}>
            <span className="accordion-icon">▸</span>
            <span style={{ flex: 1, minWidth: 0 }}>
              <span style={{ display: "block", fontWeight: 600 }}>{item.title}</span>
              {item.subtitle && <span style={{ display: "block", fontSize: 11, color: "var(--text-muted)" }}>{item.subtitle}</span>}
            </span>
            {item.badge && <span className="nav-badge">{item.badge}</span>}
          </button>
          <div className="accordion-panel">{item.children}</div>
        </div>
      ))}
    </div>
  );
}

function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="toast-stack" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />)}
    </div>
  );
}

function Toast({ toast, onDismiss }) {
  const [leaving, setLeaving] = useState(false);
  useEffect(() => {
    if (!toast.duration) return undefined;
    const t = setTimeout(() => { setLeaving(true); setTimeout(() => onDismiss(toast.id), 200); }, toast.duration);
    return () => clearTimeout(t);
  }, [toast.id, toast.duration, onDismiss]);
  const startLeave = () => { setLeaving(true); setTimeout(() => onDismiss(toast.id), 200); };
  return (
    <div className={cx("toast", "toast-" + (toast.type || "info"), leaving && "toast-leave")}>
      <span className="toast-message">{toast.message}</span>
      <button type="button" className="toast-close ceja" onClick={startLeave} aria-label="Cerrar"><Icon name="x" size={16} /></button>
    </div>
  );
}

function ThemeSwitcher({ theme, onChange }) {
  const current = THEMES.find((t) => t.id === theme) || THEMES[0];
  return (
    <div className="theme-switcher" aria-label="Cambiar tema">
      <button type="button" className="ceja" title={current.label} style={{ width: 28, height: 28, borderRadius: 6, background: current.swatch, border: "1px solid var(--border-default)", color: ["paper", "cloud", "mist"].includes(theme) ? "#1A1A1A" : "#F4F1ED" }} onClick={() => {
        const idx = THEMES.findIndex((t) => t.id === theme);
        const next = THEMES[(idx + 1) % THEMES.length];
        onChange(next.id);
      }} aria-label={current.label}>
        <Icon name={["paper", "cloud", "mist"].includes(theme) ? "sun" : "moon"} size={14} />
      </button>
    </div>
  );
}

function CommandPalette({ isOpen, onClose, onSelect, workspaces = [], activeWorkspaceId, nav }) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef(null);

  const commands = useMemo(() => {
    const list = [];
    list.push({ id: "nav-space", group: "Navegar", title: "SpaceLoom", subtitle: "Canvas y chat", action: () => onSelect({ type: "nav", value: "space", mode: "operar" }) });
    list.push({ id: "nav-workloom", group: "Navegar", title: "WorkLoom", subtitle: "Cola HITL", action: () => onSelect({ type: "nav", value: "workloom", mode: "operar" }) });
    list.push({ id: "nav-mail", group: "Navegar", title: "Correo", subtitle: "IMAP/SMTP HITL", action: () => onSelect({ type: "nav", value: "mail", mode: "operar" }) });
    list.push({ id: "nav-kb", group: "Navegar", title: "Knowledge Base", subtitle: "Fuentes y citas", action: () => onSelect({ type: "nav", value: "kb", mode: "aprender" }) });
    list.push({ id: "nav-routines", group: "Navegar", title: "Routine Hub", subtitle: "Skills portables", action: () => onSelect({ type: "nav", value: "routines", mode: "aprender" }) });
    list.push({ id: "nav-settings", group: "Navegar", title: "Ajustes", subtitle: "Router y proveedores", action: () => onSelect({ type: "nav", value: "settings", mode: "admin" }) });
    list.push({ id: "nav-audit", group: "Navegar", title: "Auditoría", subtitle: "Editorial history", action: () => onSelect({ type: "nav", value: "audit", mode: "admin" }) });
    workspaces.forEach((ws) => list.push({ id: "ws-" + ws.id, group: "Workspaces", title: ws.name, subtitle: ws.slug || ws.id, action: () => onSelect({ type: "workspace", value: ws.id }) }));
    THEMES.forEach((t) => list.push({ id: "theme-" + t.id, group: "Tema", title: t.label, action: () => onSelect({ type: "theme", value: t.id }) }));
    return list;
  }, [workspaces, onSelect]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter((c) => (c.title + " " + (c.subtitle || "")).toLowerCase().includes(q));
  }, [commands, query]);

  useEffect(() => { setSelected(0); }, [query]);

  useEffect(() => {
    if (!isOpen) { setQuery(""); setSelected(0); return; }
    const focus = setTimeout(() => inputRef.current && inputRef.current.focus(), 30);
    const handler = (e) => {
      if (e.key === "Escape") { e.preventDefault(); onClose(); }
      if (e.key === "ArrowDown") { e.preventDefault(); setSelected((i) => Math.min(filtered.length - 1, i + 1)); }
      if (e.key === "ArrowUp") { e.preventDefault(); setSelected((i) => Math.max(0, i - 1)); }
      if (e.key === "Enter" && filtered[selected]) { e.preventDefault(); filtered[selected].action(); onClose(); }
    };
    document.addEventListener("keydown", handler);
    return () => { clearTimeout(focus); document.removeEventListener("keydown", handler); };
  }, [isOpen, filtered, selected, onClose]);

  if (!isOpen) return null;

  const groups = filtered.reduce((acc, cmd) => { (acc[cmd.group] = acc[cmd.group] || []).push(cmd); return acc; }, {});

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        <input ref={inputRef} className="command-palette-input" placeholder="Buscar comando…" value={query} onChange={(e) => setQuery(e.target.value)} />
        <div className="command-list">
          {filtered.length === 0 && <div className="command-empty">Sin resultados</div>}
          {Object.keys(groups).map((group) => (
            <div key={group} className="command-group">
              <div className="command-group-label">{group}</div>
              {groups[group].map((cmd) => {
                const globalIdx = filtered.indexOf(cmd);
                return (
                  <button
                    key={cmd.id}
                    type="button"
                    className={cx("command-item", globalIdx === selected && "is-selected")}
                    onMouseEnter={() => setSelected(globalIdx)}
                    onClick={() => { cmd.action(); onClose(); }}
                  >
                    <span style={{ flex: 1, minWidth: 0 }}>
                      <span style={{ display: "block" }}>{cmd.title}</span>
                      {cmd.subtitle && <span style={{ display: "block", fontSize: 11, color: "var(--text-muted)" }}>{cmd.subtitle}</span>}
                    </span>
                    {cmd.group === "Navegar" && <kbd>↵</kbd>}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
