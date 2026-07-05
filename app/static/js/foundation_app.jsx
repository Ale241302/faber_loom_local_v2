/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation shell (M07–M20)
   Ya no tiene login propio: reutiliza la sesión principal de FaberLoom
   (JWT Bearer) y se renderiza dentro del menú Tenant de app.jsx.
   Expone window.FoundationSection, montado desde app.jsx (nav "foundation").
   Se carga después de fnd_core.jsx y de los módulos fnd_*.jsx.
   ═══════════════════════════════════════════════════════════════ */

function FoundationSection({ initialView, activeWorkspace }) {
  const F = window.Foundation;
  const { FndPanel, FndBadge, FndError } = F.ui;
  const [status, setStatus] = useState(null);
  const [me, setMe] = useState(null);
  const [error, setError] = useState(null);
  const [active, setActive] = useState(initialView || null);

  useEffect(() => { setActive(initialView || null); }, [initialView]);

  const refreshStatus = useCallback(async () => {
    try { setStatus(await F.api.get("/status")); setError(null); }
    catch (e) { setError(e); }
  }, []);

  const refreshMe = useCallback(async () => {
    try { setMe(await F.api.get("/auth/me")); setError(null); }
    catch (e) { setMe(null); }
  }, []);

  useEffect(() => { refreshStatus(); }, [refreshStatus]);
  useEffect(() => {
    if (!status || !status.bootstrapped) return;
    refreshMe();
  }, [status, refreshMe]);

  if (error) return <div style={{ padding: 24 }}><FndError error={error} /></div>;
  if (!status) return <div style={{ padding: 24, color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>Cargando Foundation…</div>;

  // 1) Sin tenant activo → Bootstrap Wizard (M07)
  if (!status.bootstrapped) {
    const wizard = F.views.find((v) => v.id === "m07-bootstrap");
    if (wizard) {
      const Wizard = wizard.component;
      return <Wizard api={F.api} status={status} onDone={refreshStatus} />;
    }
    return <div style={{ padding: 24, color: "var(--text-muted)" }}>Bootstrap Wizard (M07) no cargado.</div>;
  }

  // 2) Bootstrapped pero aún no tenemos /auth/me
  if (!me) {
    return (
      <div style={{ padding: 24, color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
        Cargando sesión de Foundation…
      </div>
    );
  }

  // 3) Autenticado → sub-navegación de módulos
  const groups = ["Plataforma", "Operación", "Desktop"];
  const visible = F.views.filter((v) => !v.hidden && v.id !== "m07-bootstrap" && v.id !== "m08-login")
    .filter((v) => !v.permission || (me.permissions || []).includes("*") || (me.permissions || []).includes(v.permission));
  const current = visible.find((v) => v.id === active) || visible[0];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "218px minmax(0, 1fr)", gap: 16, minHeight: 0, height: "100%" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 4, overflow: "auto", paddingRight: 4 }}>
        <div style={{ padding: "10px 10px 12px" }}>
          <div style={{ fontWeight: 650, fontSize: 13 }}>Tenant</div>
          <div style={{ color: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)", marginTop: 2 }}>{status.tenant ? status.tenant.name : ""}</div>
          <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
            <FndBadge tone="ok">{me.email}</FndBadge>
            {(me.roles || []).map((r) => <FndBadge key={r}>{r}</FndBadge>)}
          </div>
        </div>
        {groups.map((g) => {
          const items = visible.filter((v) => (v.group || "Plataforma") === g);
          if (!items.length) return null;
          return (
            <div key={g} style={{ marginBottom: 6 }}>
              <div style={{ padding: "6px 10px", fontSize: 10.5, textTransform: "uppercase", letterSpacing: ".6px", color: "var(--text-muted)", fontWeight: 600 }}>{g}</div>
              {items.map((v) => (
                <button key={v.id} type="button" onClick={() => setActive(v.id)}
                  className={cx("nav-item", current && current.id === v.id && "is-active")}
                  style={{ width: "100%", textAlign: "left" }}>
                  <span>{v.label}</span>
                </button>
              ))}
            </div>
          );
        })}
      </div>
      <div style={{ minWidth: 0, overflow: "auto" }}>
        {current
          ? <current.component api={window.Foundation.api} me={me} refreshMe={refreshMe} tenant={status.tenant} activeWorkspace={activeWorkspace} />
          : <div style={{ padding: 24, color: "var(--text-muted)" }}>No hay vistas foundation disponibles para tu rol.</div>}
      </div>
    </div>
  );
}

window.FoundationSection = FoundationSection;
