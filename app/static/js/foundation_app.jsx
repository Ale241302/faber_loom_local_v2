/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation shell (M07–M20)
   Ya no tiene login propio: reutiliza la sesión principal de FaberLoom
   (JWT Bearer) y se renderiza dentro del menú Tenant de app.jsx.
   Expone window.FoundationSection, montado desde app.jsx (nav "foundation").
   Se carga después de fnd_core.jsx y de los módulos fnd_*.jsx.
   ═══════════════════════════════════════════════════════════════ */

function FoundationSection({ initialView, activeWorkspace }) {
  const F = window.Foundation;
  const { FndPanel, FndBadge, FndError, FndField, inputStyle, buttonPrimaryStyle } = F.ui;
  const [status, setStatus] = useState(null);
  const [me, setMe] = useState(null);
  const [meMissing, setMeMissing] = useState(false); // 401: usuario sin tenant asignado
  const [error, setError] = useState(null);
  const [active, setActive] = useState(initialView || null);

  useEffect(() => { setActive(initialView || null); }, [initialView]);

  const refreshStatus = useCallback(async () => {
    try { setStatus(await F.api.get("/status")); setError(null); }
    catch (e) { setError(e); }
  }, []);

  const refreshMe = useCallback(async () => {
    try { setMe(await F.api.get("/auth/me")); setMeMissing(false); setError(null); }
    catch (e) { setMe(null); setMeMissing(e && e.status === 401); }
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

  // 2a) Sesión principal válida pero SIN usuario Foundation en ningún tenant →
  //     self-service: el usuario puede crear su propio tenant y quedar como owner.
  if (!me && meMissing) {
    return <SelfServiceTenant F={F} onDone={refreshMe} />;
  }

  // 2b) Bootstrapped pero aún no tenemos /auth/me
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

function SelfServiceTenant({ F, onDone }) {
  const { FndPanel, FndError, FndField, inputStyle, buttonPrimaryStyle } = F.ui;
  const [form, setForm] = useState({ name: "", slug: "", display_name: "", password: "" });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const create = async () => {
    setBusy(true); setError(null);
    try {
      const resp = await F.api.post("/tenants/self-service", form);
      if (resp && resp.session) F.setSession(resp.session);
      await onDone();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  };

  return (
    <div style={{ display: "grid", placeItems: "center", minHeight: "60vh", padding: 24 }}>
      <div style={{ width: "min(520px, 100%)", display: "grid", gap: 14 }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontWeight: 650, fontSize: 16 }}>Tu usuario no está asignado a ningún tenant</div>
          <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 4 }}>
            Podés crear tu propio tenant ahora mismo (quedás como owner), o pedirle a un
            admin que te asigne a uno existente desde «Roles y permisos».
          </div>
        </div>
        <FndPanel title="Crear mi tenant" meta="Self-service · quedás como owner">
          <FndError error={error} />
          <div style={{ display: "grid", gap: 12 }}>
            <FndField label="Nombre de la organización">
              <input style={inputStyle} value={form.name} placeholder="Mi Empresa S.A."
                onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </FndField>
            <FndField label="Slug">
              <input style={inputStyle} value={form.slug} placeholder="mi-empresa"
                onChange={(e) => setForm({ ...form, slug: e.target.value })} />
            </FndField>
            <FndField label="Tu nombre a mostrar (opcional)">
              <input style={inputStyle} value={form.display_name}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })} />
            </FndField>
            <FndField label="Contraseña Foundation (mínimo 8 caracteres)">
              <input style={inputStyle} type="password" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </FndField>
            <button type="button" style={buttonPrimaryStyle}
              disabled={busy || !form.name || !form.slug || form.password.length < 8}
              onClick={create}>{busy ? "Creando…" : "Crear tenant"}</button>
          </div>
        </FndPanel>
      </div>
    </div>
  );
}

window.FoundationSection = FoundationSection;
