/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation core (M07–M20)
   Cliente API, sesión, registro de vistas y componentes compartidos.
   Se carga después de foundation.jsx y antes de los módulos fnd_*.jsx.
   Namespace global: window.Foundation
   ═══════════════════════════════════════════════════════════════ */

(function () {
  const SESSION_KEY = "faberloom-fnd-session";

  function getSession() {
    try { return localStorage.getItem(SESSION_KEY) || null; } catch (e) { return null; }
  }
  function setSession(token) {
    try {
      if (token) localStorage.setItem(SESSION_KEY, token);
      else localStorage.removeItem(SESSION_KEY);
    } catch (e) {}
  }

  function headers(extra) {
    const h = Object.assign({}, extra || {});
    // Foundation reutiliza la sesión principal de FaberLoom (cookie HttpOnly
    // `faberloom_at`, enviada automáticamente same-origin); ya no exige login
    // propio. No se manda un Bearer desde localStorage (producía
    // `Bearer undefined` → 401). Durante bootstrap offline todavía puede usarse
    // una sesión Foundation legacy vía X-Fnd-Session.
    const token = getSession();
    if (token) h["X-Fnd-Session"] = token;
    return h;
  }

  async function handle(res) {
    if (res.status === 401) {
      // Sesión foundation inválida → volver a login.
      setSession(null);
      window.dispatchEvent(new CustomEvent("fnd-session-expired"));
    }
    if (!res.ok) {
      let detail = res.statusText;
      try { const data = await res.json(); detail = data.detail || JSON.stringify(data); } catch (e) {}
      const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      err.status = res.status;
      throw err;
    }
    if (res.status === 204) return null;
    return res.json();
  }

  const api = {
    get: (path) => fetch("/api/foundation" + path, { headers: headers() }).then(handle),
    post: (path, body) => fetch("/api/foundation" + path, {
      method: "POST", headers: headers({ "Content-Type": "application/json" }),
      body: JSON.stringify(body || {}),
    }).then(handle),
    put: (path, body) => fetch("/api/foundation" + path, {
      method: "PUT", headers: headers({ "Content-Type": "application/json" }),
      body: JSON.stringify(body || {}),
    }).then(handle),
    patch: (path, body) => fetch("/api/foundation" + path, {
      method: "PATCH", headers: headers({ "Content-Type": "application/json" }),
      body: JSON.stringify(body || {}),
    }).then(handle),
    del: (path) => fetch("/api/foundation" + path, { method: "DELETE", headers: headers() }).then(handle),
  };

  /* ── Registro de vistas ──
     Cada módulo llama Foundation.register({
       id: "m09-rbac", label: "Roles y permisos", icon: "shield",
       group: "Plataforma" | "Operación" | "Desktop",
       order: 9, permission: "roles.manage" | null,
       component: (props) => <View/>   // props: { api, me, refreshMe }
     }) */
  const views = [];
  function register(view) {
    if (!view || !view.id || !view.component) return;
    const idx = views.findIndex((v) => v.id === view.id);
    if (idx >= 0) views[idx] = view; else views.push(view);
    views.sort((a, b) => (a.order || 99) - (b.order || 99));
  }

  /* ── Componentes compartidos ── */
  function FndPanel({ title, meta, actions, children, style }) {
    return (
      <div style={Object.assign({ border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)", boxShadow: "var(--shadow-sm)", display: "flex", flexDirection: "column", minWidth: 0 }, style)}>
        {(title || actions) && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)" }}>
            <div>
              <div style={{ fontWeight: 650, fontSize: 13.5 }}>{title}</div>
              {meta && <div style={{ color: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)" }}>{meta}</div>}
            </div>
            {actions && <div style={{ display: "flex", gap: 8 }}>{actions}</div>}
          </div>
        )}
        <div style={{ padding: "14px 16px", overflow: "auto" }}>{children}</div>
      </div>
    );
  }

  function FndBadge({ children, tone }) {
    const tones = {
      ok: { background: "var(--sage-soft)", border: "1px solid var(--sage-deep)" },
      warn: { background: "var(--coral-soft)", border: "1px solid var(--coral)" },
      danger: { background: "var(--vino-soft)", border: "1px solid var(--vino-deep)" },
      muted: { background: "var(--bg-raised)", border: "1px solid var(--border-default)" },
    };
    return (
      <span style={Object.assign({ padding: "2px 8px", borderRadius: 999, fontSize: 10.5, fontFamily: "var(--font-mono)", textTransform: "uppercase", color: "var(--text-secondary)", whiteSpace: "nowrap" }, tones[tone] || tones.muted)}>
        {children}
      </span>
    );
  }

  function FndTable({ columns, rows, empty, onRowClick }) {
    if (!rows || rows.length === 0) {
      return <div style={{ padding: "28px 16px", textAlign: "center", color: "var(--text-muted)", fontSize: 12.5 }}>{empty || "Sin registros"}</div>;
    }
    return (
      <div style={{ overflow: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key} style={{ textAlign: "left", padding: "7px 10px", borderBottom: "1px solid var(--border-default)", color: "var(--text-muted)", fontSize: 10.5, textTransform: "uppercase", letterSpacing: ".5px", whiteSpace: "nowrap" }}>{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.id || i} onClick={onRowClick ? () => onRowClick(row) : undefined}
                  style={{ cursor: onRowClick ? "pointer" : "default" }}>
                {columns.map((c) => (
                  <td key={c.key} style={{ padding: "8px 10px", borderBottom: "1px solid var(--border-subtle)", verticalAlign: "top", color: "var(--text-secondary)" }}>
                    {c.render ? c.render(row) : String(row[c.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  function FndField({ label, children }) {
    return (
      <label style={{ display: "grid", gap: 6, fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px" }}>
        {label}
        {children}
      </label>
    );
  }

  const inputStyle = { width: "100%", padding: "9px 11px", border: "1px solid var(--border-default)", borderRadius: 8, background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 12.5, outline: "none", boxSizing: "border-box" };
  const buttonStyle = { padding: "9px 14px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 12.5 };
  const buttonPrimaryStyle = { padding: "9px 14px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 600, fontSize: 12.5 };
  const buttonDangerStyle = { padding: "9px 14px", border: 0, borderRadius: "var(--r-sm)", background: "var(--vino)", color: "#1A1815", cursor: "pointer", fontWeight: 600, fontSize: 12.5 };

  function FndError({ error }) {
    if (!error) return null;
    return <div style={{ padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 }}>{String(error.message || error)}</div>;
  }

  function FndJson({ value }) {
    return <pre style={{ padding: 10, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", fontFamily: "var(--font-mono)", fontSize: 11.5, overflow: "auto", maxHeight: 260, whiteSpace: "pre-wrap", color: "var(--text-secondary)", margin: 0 }}>{JSON.stringify(value, null, 2)}</pre>;
  }

  window.Foundation = {
    api, views, register,
    getSession, setSession,
    ui: { FndPanel, FndBadge, FndTable, FndField, FndError, FndJson, inputStyle, buttonStyle, buttonPrimaryStyle, buttonDangerStyle },
  };
})();
