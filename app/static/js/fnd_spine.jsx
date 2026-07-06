/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation SPINE (M07, M08, M09, M11, M12, M15, M16)
   Bootstrap wizard, login/2FA, sesiones, RBAC, policy gate, audit,
   eventos y tenant. React 18 UMD + babel-standalone, sin imports.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  const { useState, useEffect, useMemo, useCallback } = React;
  const F = window.Foundation;
  const { FndPanel, FndBadge, FndTable, FndField, FndError, FndJson,
          inputStyle, buttonStyle, buttonPrimaryStyle, buttonDangerStyle } = F.ui;

  const rowStyle = { display: "flex", gap: 10, flexWrap: "wrap", alignItems: "flex-end" };
  const stackStyle = { display: "grid", gap: 12 };
  const monoStyle = { fontFamily: "var(--font-mono)", fontSize: 11.5, wordBreak: "break-all" };

  function fmtDate(iso) {
    if (!iso) return "—";
    try { return new Date(iso).toLocaleString(); } catch (e) { return iso; }
  }

  /* ═══════════════ M07 · Bootstrap Wizard ═══════════════ */

  function BootstrapWizard({ api, status, onDone }) {
    const [state, setState] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [tenantForm, setTenantForm] = useState({ name: "", slug: "" });
    const [ownerForm, setOwnerForm] = useState({ email: "", display_name: "", password: "" });
    const [ownerSession, setOwnerSession] = useState(null);

    const refresh = useCallback(async () => {
      try { setState(await api.get("/bootstrap/state")); setError(null); }
      catch (e) { setError(e); }
    }, []);
    useEffect(() => { refresh(); }, [refresh]);

    const step = state ? state.step : "tenant";
    const stepIdx = step === "tenant" ? 0 : step === "owner" ? 1 : 2;
    const labels = ["Tenant", "Owner", "Activar"];

    const run = async (fn) => {
      setBusy(true); setError(null);
      try { await fn(); } catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const createTenant = () => run(async () => {
      await api.post("/bootstrap/tenant", tenantForm);
      await refresh();
    });
    const createOwner = () => run(async () => {
      const resp = await api.post("/bootstrap/owner", ownerForm);
      if (resp && resp.session) {
        F.setSession(resp.session);
        setOwnerSession(resp.session);
      }
      await refresh();
    });
    const activate = () => run(async () => {
      // Usamos la sesión creada en el owner para activar, no el JWT principal,
      // porque el endpoint requiere bootstrap.manage y el owner sí lo tiene.
      const res = await fetch("/api/foundation/bootstrap/activate", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Fnd-Session": ownerSession || F.getSession() || "" },
      });
      if (!res.ok) {
        let detail = res.statusText;
        try { const data = await res.json(); detail = data.detail || JSON.stringify(data); } catch (e) {}
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      onDone();
    });

    const checklist = (state && state.checklist) || {};

    return (
      <div style={{ display: "grid", placeItems: "center", minHeight: "60vh", padding: 24 }}>
        <div style={{ width: "min(560px, 100%)", display: "grid", gap: 14 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontWeight: 650, fontSize: 16 }}>Configuración inicial de FaberLoom</div>
            <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 4 }}>
              Bootstrap Wizard (M07): tenant → owner → activación
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
            {labels.map((l, i) => (
              <div key={l} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{
                  width: 24, height: 24, borderRadius: 999, display: "grid", placeItems: "center",
                  fontSize: 11.5, fontWeight: 650,
                  background: i < stepIdx ? "var(--sage-soft)" : i === stepIdx ? "var(--coral)" : "var(--bg-raised)",
                  color: i === stepIdx ? "#1A1815" : "var(--text-secondary)",
                  border: "1px solid var(--border-default)",
                }}>{i < stepIdx ? "✓" : i + 1}</span>
                <span style={{ fontSize: 12, color: i === stepIdx ? "var(--text-primary)" : "var(--text-muted)" }}>{l}</span>
                {i < labels.length - 1 && <span style={{ width: 22, height: 1, background: "var(--border-default)" }} />}
              </div>
            ))}
          </div>
          <FndError error={error} />

          {step === "tenant" && (
            <FndPanel title="Paso 1 · Crear tenant" meta="Nombre y slug de la organización">
              <div style={stackStyle}>
                <FndField label="Nombre">
                  <input style={inputStyle} value={tenantForm.name} placeholder="Mi Empresa S.A."
                    onChange={(e) => setTenantForm({ ...tenantForm, name: e.target.value })} />
                </FndField>
                <FndField label="Slug">
                  <input style={inputStyle} value={tenantForm.slug} placeholder="mi-empresa"
                    onChange={(e) => setTenantForm({ ...tenantForm, slug: e.target.value })} />
                </FndField>
                <button type="button" style={buttonPrimaryStyle} disabled={busy || !tenantForm.name || !tenantForm.slug}
                  onClick={createTenant}>{busy ? "Creando…" : "Crear tenant"}</button>
              </div>
            </FndPanel>
          )}

          {step === "owner" && (
            <FndPanel title="Paso 2 · Crear owner" meta="Primer usuario con control total">
              <div style={stackStyle}>
                <FndField label="Email">
                  <input style={inputStyle} type="email" value={ownerForm.email}
                    onChange={(e) => setOwnerForm({ ...ownerForm, email: e.target.value })} />
                </FndField>
                <FndField label="Nombre a mostrar">
                  <input style={inputStyle} value={ownerForm.display_name}
                    onChange={(e) => setOwnerForm({ ...ownerForm, display_name: e.target.value })} />
                </FndField>
                <FndField label="Contraseña (mínimo 8 caracteres)">
                  <input style={inputStyle} type="password" value={ownerForm.password}
                    onChange={(e) => setOwnerForm({ ...ownerForm, password: e.target.value })} />
                </FndField>
                <button type="button" style={buttonPrimaryStyle}
                  disabled={busy || !ownerForm.email || ownerForm.password.length < 8}
                  onClick={createOwner}>{busy ? "Creando…" : "Crear owner y continuar"}</button>
              </div>
            </FndPanel>
          )}

          {(step === "security" || step === "done") && (
            <FndPanel title="Paso 3 · Activar tenant" meta="Checklist de activación">
              <div style={stackStyle}>
                <div style={{ display: "grid", gap: 6 }}>
                  {[
                    ["tenant_created", "Tenant creado"],
                    ["owner_exists", "Owner activo"],
                    ["owner_2fa_enabled", "2FA del owner (opcional)"],
                    ["activated", "Tenant activado"],
                  ].map(([key, label]) => (
                    <div key={key} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 12.5 }}>
                      <FndBadge tone={checklist[key] ? "ok" : key === "owner_2fa_enabled" ? "muted" : "warn"}>
                        {checklist[key] ? "OK" : "Pendiente"}
                      </FndBadge>
                      <span>{label}</span>
                    </div>
                  ))}
                </div>
                <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  El 2FA se puede activar después desde «Sesiones y 2FA».
                </div>
                <button type="button" style={buttonPrimaryStyle} disabled={busy}
                  onClick={activate}>{busy ? "Activando…" : "Activar tenant"}</button>
              </div>
            </FndPanel>
          )}
        </div>
      </div>
    );
  }

  /* ═══════════════ M08 · Login / 2FA ═══════════════ */

  function LoginView({ api, onAuthed }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [pending, setPending] = useState(null); // token de sesión stage=totp
    const [code, setCode] = useState("");
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    const login = async (e) => {
      e.preventDefault();
      setBusy(true); setError(null);
      try {
        const resp = await api.post("/auth/login", { email, password });
        if (resp.requires_2fa) { setPending(resp.session); }
        else { F.setSession(resp.session); onAuthed(); }
      } catch (err) { setError(err); }
      finally { setBusy(false); }
    };

    const verify = async (e) => {
      e.preventDefault();
      setBusy(true); setError(null);
      try {
        const resp = await api.post("/auth/2fa/verify", { session: pending, code });
        F.setSession(resp.session);
        onAuthed();
      } catch (err) { setError(err); }
      finally { setBusy(false); }
    };

    return (
      <div style={{ display: "grid", placeItems: "center", minHeight: "60vh", padding: 24 }}>
        <div style={{ width: "min(420px, 100%)" }}>
          <FndPanel title="Iniciar sesión" meta="Foundation Beta · M08">
            <FndError error={error} />
            {!pending ? (
              <form onSubmit={login} style={stackStyle}>
                <FndField label="Email">
                  <input style={inputStyle} type="email" value={email} autoFocus
                    onChange={(e) => setEmail(e.target.value)} />
                </FndField>
                <FndField label="Contraseña">
                  <input style={inputStyle} type="password" value={password}
                    onChange={(e) => setPassword(e.target.value)} />
                </FndField>
                <button type="submit" style={buttonPrimaryStyle} disabled={busy || !email || !password}>
                  {busy ? "Entrando…" : "Entrar"}
                </button>
              </form>
            ) : (
              <form onSubmit={verify} style={stackStyle}>
                <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                  Esta cuenta tiene 2FA activo. Introduce el código de tu app de autenticación.
                </div>
                <FndField label="Código TOTP">
                  <input style={inputStyle} value={code} autoFocus inputMode="numeric" maxLength={8}
                    onChange={(e) => setCode(e.target.value)} />
                </FndField>
                <div style={{ display: "flex", gap: 8 }}>
                  <button type="submit" style={buttonPrimaryStyle} disabled={busy || !code}>
                    {busy ? "Verificando…" : "Verificar"}
                  </button>
                  <button type="button" style={buttonStyle} onClick={() => { setPending(null); setCode(""); }}>
                    Volver
                  </button>
                </div>
              </form>
            )}
          </FndPanel>
        </div>
      </div>
    );
  }

  /* ═══════════════ M08 · Sesiones y 2FA ═══════════════ */

  function SessionsView({ api, me, refreshMe }) {
    const [sessions, setSessions] = useState(null);
    const [error, setError] = useState(null);
    const [enroll, setEnroll] = useState(null); // {secret, otpauth_uri}
    const [code, setCode] = useState("");
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState("");

    const load = useCallback(async () => {
      try { setSessions((await api.get("/auth/sessions")).sessions); setError(null); }
      catch (e) { setError(e); }
    }, []);
    useEffect(() => { load(); }, [load]);

    const run = async (fn, okMsg) => {
      setBusy(true); setError(null); setNotice("");
      try { await fn(); if (okMsg) setNotice(okMsg); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const revoke = (id) => run(async () => {
      await api.post("/auth/sessions/" + encodeURIComponent(id) + "/revoke");
      await load();
    }, "Sesión revocada");

    const startEnroll = () => run(async () => {
      setEnroll(await api.post("/auth/2fa/enroll"));
      setCode("");
    });
    const confirmEnroll = () => run(async () => {
      await api.post("/auth/2fa/confirm", { code });
      setEnroll(null); setCode("");
      await refreshMe();
    }, "2FA activado correctamente");
    const disable2fa = () => run(async () => {
      await api.post("/auth/2fa/disable", { code });
      setCode("");
      await refreshMe();
    }, "2FA desactivado");

    const totpEnabled = !!(me && me.totp_enabled);

    return (
      <div style={stackStyle}>
        <FndError error={error} />
        {notice && <div><FndBadge tone="ok">{notice}</FndBadge></div>}

        <FndPanel title="Sesiones activas" meta="Sesiones abiertas de tu usuario"
          actions={<button type="button" style={buttonStyle} onClick={load}>Refrescar</button>}>
          <FndTable
            empty="Sin sesiones activas"
            columns={[
              { key: "id", label: "Sesión", render: (r) => (
                <span style={monoStyle}>{r.id.slice(0, 18)}… {r.current ? <FndBadge tone="ok">actual</FndBadge> : null}</span>
              ) },
              { key: "created_at", label: "Creada", render: (r) => fmtDate(r.created_at) },
              { key: "last_seen_at", label: "Última actividad", render: (r) => fmtDate(r.last_seen_at) },
              { key: "expires_at", label: "Expira", render: (r) => fmtDate(r.expires_at) },
              { key: "ip", label: "IP" },
              { key: "actions", label: "", render: (r) => (
                <button type="button" style={buttonDangerStyle} disabled={busy}
                  onClick={() => revoke(r.id)}>Revocar</button>
              ) },
            ]}
            rows={sessions || []}
          />
        </FndPanel>

        <FndPanel title="Autenticación en dos pasos (TOTP)"
          meta={totpEnabled ? "2FA activo en tu cuenta" : "2FA no activado"}>
          {totpEnabled ? (
            <div style={stackStyle}>
              <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                Para desactivar el 2FA introduce un código válido de tu app de autenticación.
              </div>
              <div style={rowStyle}>
                <FndField label="Código TOTP">
                  <input style={Object.assign({}, inputStyle, { width: 140 })} value={code}
                    inputMode="numeric" maxLength={8} onChange={(e) => setCode(e.target.value)} />
                </FndField>
                <button type="button" style={buttonDangerStyle} disabled={busy || !code}
                  onClick={disable2fa}>Desactivar 2FA</button>
              </div>
            </div>
          ) : enroll ? (
            <div style={stackStyle}>
              <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                Copia el secret (o la URI otpauth) en tu app de autenticación y confirma con un código.
              </div>
              <FndField label="Secret (copiable)">
                <input style={Object.assign({}, inputStyle, monoStyle)} readOnly value={enroll.secret}
                  onFocus={(e) => e.target.select()} />
              </FndField>
              <FndField label="URI otpauth (copiable)">
                <input style={Object.assign({}, inputStyle, monoStyle)} readOnly value={enroll.otpauth_uri}
                  onFocus={(e) => e.target.select()} />
              </FndField>
              <div style={rowStyle}>
                <FndField label="Código de confirmación">
                  <input style={Object.assign({}, inputStyle, { width: 140 })} value={code}
                    inputMode="numeric" maxLength={8} onChange={(e) => setCode(e.target.value)} />
                </FndField>
                <button type="button" style={buttonPrimaryStyle} disabled={busy || !code}
                  onClick={confirmEnroll}>Confirmar y activar</button>
                <button type="button" style={buttonStyle} onClick={() => { setEnroll(null); setCode(""); }}>
                  Cancelar
                </button>
              </div>
            </div>
          ) : (
            <button type="button" style={buttonPrimaryStyle} disabled={busy} onClick={startEnroll}>
              Enrolar 2FA
            </button>
          )}
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M09 · Roles y permisos ═══════════════ */

  function RbacView({ api, me, refreshMe }) {
    const [users, setUsers] = useState(null);
    const [roles, setRoles] = useState(null);
    const [catalog, setCatalog] = useState([]);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    const emptyUser = { email: "", display_name: "", password: "", roles: [] };
    const [newUser, setNewUser] = useState(emptyUser);
    const [newUserTenant, setNewUserTenant] = useState("");
    const [editing, setEditing] = useState(null); // {id, email, display_name, status, password, roles}
    const [moveTenant, setMoveTenant] = useState("");
    const emptyRole = { name: "", description: "", permissions: [] };
    const [newRole, setNewRole] = useState(emptyRole);

    // Multi-tenant (requiere tenants.manage; si no hay permiso, tenants = null y
    // la sección de tenants no se muestra).
    const [tenants, setTenants] = useState(null);
    const emptyTenant = { name: "", slug: "", owner_email: "", owner_display_name: "", owner_password: "" };
    const [newTenant, setNewTenant] = useState(emptyTenant);

    const load = useCallback(async () => {
      try {
        const [u, r, p] = await Promise.all([
          api.get("/rbac/users"), api.get("/rbac/roles"), api.get("/rbac/permissions"),
        ]);
        setUsers(u.users); setRoles(r.roles); setCatalog(p.permissions); setError(null);
      } catch (e) { setError(e); }
      try {
        const t = await api.get("/tenants/all");
        setTenants(t.tenants);
      } catch (e) { setTenants(null); /* sin permiso tenants.manage */ }
    }, []);
    useEffect(() => { load(); }, [load]);

    const run = async (fn) => {
      setBusy(true); setError(null);
      try { await fn(); await load(); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const roleNames = useMemo(() => (roles || []).map((r) => r.name), [roles]);

    const toggleIn = (list, value) =>
      list.includes(value) ? list.filter((x) => x !== value) : list.concat([value]);

    const createUser = () => run(async () => {
      const targetTenant = newUserTenant || (me && me.tenant_id) || "";
      if (tenants && targetTenant && me && targetTenant !== me.tenant_id) {
        await api.post("/tenants/" + targetTenant + "/users", newUser);
      } else {
        await api.post("/rbac/users", newUser);
      }
      setNewUser(emptyUser);
      setNewUserTenant("");
    });

    const createTenant = () => run(async () => {
      const body = { name: newTenant.name, slug: newTenant.slug };
      if (newTenant.owner_email) {
        body.owner_email = newTenant.owner_email;
        body.owner_display_name = newTenant.owner_display_name;
        body.owner_password = newTenant.owner_password;
      }
      await api.post("/tenants", body);
      setNewTenant(emptyTenant);
    });

    const moveUser = () => run(async () => {
      await api.post("/tenants/" + moveTenant + "/assign", { user_id: editing.id });
      setEditing(null);
      setMoveTenant("");
    });

    const saveEditing = () => run(async () => {
      const patch = { display_name: editing.display_name, status: editing.status };
      if (editing.password) patch.password = editing.password;
      await api.patch("/rbac/users/" + editing.id, patch);
      await api.post("/rbac/users/" + editing.id + "/roles", { roles: editing.roles });
      setEditing(null);
      await refreshMe();
    });

    const createRole = () => run(async () => {
      await api.post("/rbac/roles", newRole);
      setNewRole(emptyRole);
    });

    const deleteRole = (r) => run(async () => { await api.del("/rbac/roles/" + r.id); });

    const rolePicker = (selected, onChange) => (
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {roleNames.map((name) => (
          <label key={name} style={{ display: "flex", gap: 5, alignItems: "center", fontSize: 12.5, cursor: "pointer" }}>
            <input type="checkbox" checked={selected.includes(name)}
              onChange={() => onChange(toggleIn(selected, name))} />
            {name}
          </label>
        ))}
      </div>
    );

    if (!users && !error) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Cargando…</div>;

    return (
      <div style={stackStyle}>
        <FndError error={error} />

        <FndPanel title="Usuarios" meta="Cuentas del tenant y sus roles"
          actions={<button type="button" style={buttonStyle} onClick={load}>Refrescar</button>}>
          <FndTable
            empty="Sin usuarios"
            columns={[
              { key: "email", label: "Email" },
              { key: "display_name", label: "Nombre" },
              { key: "roles", label: "Roles", render: (r) => (
                <span style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                  {(r.roles || []).map((x) => <FndBadge key={x} tone={x === "owner" ? "warn" : "muted"}>{x}</FndBadge>)}
                </span>
              ) },
              { key: "status", label: "Estado", render: (r) => (
                <FndBadge tone={r.status === "active" ? "ok" : "danger"}>{r.status}</FndBadge>
              ) },
              { key: "totp_enabled", label: "2FA", render: (r) => (r.totp_enabled ? "Sí" : "No") },
              { key: "actions", label: "", render: (r) => (
                <span style={{ display: "flex", gap: 6 }}>
                  <button type="button" style={buttonStyle}
                    onClick={() => setEditing({ id: r.id, email: r.email, display_name: r.display_name, status: r.status, password: "", roles: r.roles || [] })}>
                    Editar
                  </button>
                  {me && me.id !== r.id && (
                    <button type="button" style={buttonDangerStyle} disabled={busy}
                      onClick={() => deleteUser(r)}>
                      Borrar
                    </button>
                  )}
                </span>
              ) },
            ]}
            rows={users || []}
          />

          {editing && (
            <div style={Object.assign({}, stackStyle, { marginTop: 14, padding: 12, border: "1px solid var(--border-default)", borderRadius: 8 })}>
              <div style={{ fontWeight: 650, fontSize: 12.5 }}>Editar usuario · {editing.email}</div>
              <div style={rowStyle}>
                <FndField label="Nombre">
                  <input style={inputStyle} value={editing.display_name}
                    onChange={(e) => setEditing({ ...editing, display_name: e.target.value })} />
                </FndField>
                <FndField label="Estado">
                  <select style={inputStyle} value={editing.status}
                    onChange={(e) => setEditing({ ...editing, status: e.target.value })}>
                    <option value="active">active</option>
                    <option value="disabled">disabled</option>
                  </select>
                </FndField>
                <FndField label="Nueva contraseña (opcional)">
                  <input style={inputStyle} type="password" value={editing.password}
                    onChange={(e) => setEditing({ ...editing, password: e.target.value })} />
                </FndField>
              </div>
              <FndField label="Roles">
                {rolePicker(editing.roles, (roles2) => setEditing({ ...editing, roles: roles2 }))}
              </FndField>
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" style={buttonPrimaryStyle} disabled={busy} onClick={saveEditing}>Guardar</button>
                <button type="button" style={buttonStyle} onClick={() => setEditing(null)}>Cancelar</button>
              </div>
              {tenants && me && editing.id !== me.id && (
                <div style={{ display: "flex", gap: 8, alignItems: "flex-end", flexWrap: "wrap", paddingTop: 8, borderTop: "1px dashed var(--border-default)" }}>
                  <FndField label="Mover a otro tenant">
                    <select style={inputStyle} value={moveTenant} onChange={(e) => setMoveTenant(e.target.value)}>
                      <option value="">Elegir tenant destino…</option>
                      {tenants.filter((t) => t.id !== (me && me.tenant_id)).map((t) => (
                        <option key={t.id} value={t.id}>{t.name} ({t.slug})</option>
                      ))}
                    </select>
                  </FndField>
                  <button type="button" style={buttonStyle} disabled={busy || !moveTenant} onClick={moveUser}>
                    Mover usuario
                  </button>
                </div>
              )}
            </div>
          )}

          <div style={Object.assign({}, stackStyle, { marginTop: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 })}>
            <div style={{ fontWeight: 650, fontSize: 12.5 }}>Crear usuario</div>
            <div style={rowStyle}>
              <FndField label="Email">
                <input style={inputStyle} type="email" value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
              </FndField>
              <FndField label="Nombre">
                <input style={inputStyle} value={newUser.display_name}
                  onChange={(e) => setNewUser({ ...newUser, display_name: e.target.value })} />
              </FndField>
              <FndField label="Contraseña">
                <input style={inputStyle} type="password" value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
              </FndField>
              {tenants && (
                <FndField label="Tenant">
                  <select style={inputStyle} value={newUserTenant || (me && me.tenant_id) || ""}
                    onChange={(e) => setNewUserTenant(e.target.value)}>
                    {tenants.map((t) => (
                      <option key={t.id} value={t.id}>{t.name} ({t.slug})</option>
                    ))}
                  </select>
                </FndField>
              )}
            </div>
            <FndField label="Roles">
              {rolePicker(newUser.roles, (roles2) => setNewUser({ ...newUser, roles: roles2 }))}
            </FndField>
            <button type="button" style={buttonPrimaryStyle}
              disabled={busy || !newUser.email || newUser.password.length < 8}
              onClick={createUser}>Crear usuario</button>
            {tenants && newUserTenant && me && newUserTenant !== me.tenant_id && (
              <div style={{ color: "var(--text-muted)", fontSize: 11.5 }}>
                El usuario se creará en otro tenant y no aparecerá en la tabla de arriba (aislamiento multi-tenant).
              </div>
            )}
          </div>
        </FndPanel>

        {tenants && (
          <FndPanel title="Tenants" meta="Organizaciones de esta instancia (multi-tenant)">
            <FndTable
              empty="Sin tenants"
              columns={[
                { key: "name", label: "Nombre", render: (t) => (
                  <span style={{ display: "flex", gap: 6, alignItems: "center" }}>
                    {t.name}
                    {me && t.id === me.tenant_id && <FndBadge tone="ok">actual</FndBadge>}
                  </span>
                ) },
                { key: "slug", label: "Slug", render: (t) => <span style={monoStyle}>{t.slug}</span> },
                { key: "status", label: "Estado", render: (t) => (
                  <FndBadge tone={t.status === "active" ? "ok" : "warn"}>{t.status}</FndBadge>
                ) },
                { key: "users_count", label: "Usuarios" },
                { key: "owners_count", label: "Owners" },
                { key: "created_at", label: "Creado", render: (t) => fmtDate(t.created_at) },
              ]}
              rows={tenants}
            />

            <div style={Object.assign({}, stackStyle, { marginTop: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 })}>
              <div style={{ fontWeight: 650, fontSize: 12.5 }}>Crear tenant</div>
              <div style={rowStyle}>
                <FndField label="Nombre">
                  <input style={inputStyle} value={newTenant.name} placeholder="Mi Empresa S.A."
                    onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })} />
                </FndField>
                <FndField label="Slug">
                  <input style={inputStyle} value={newTenant.slug} placeholder="mi-empresa"
                    onChange={(e) => setNewTenant({ ...newTenant, slug: e.target.value })} />
                </FndField>
              </div>
              <div style={{ color: "var(--text-muted)", fontSize: 11.5 }}>
                Owner inicial (opcional — sin owner el tenant queda en «provisioning» hasta que le asignes uno):
              </div>
              <div style={rowStyle}>
                <FndField label="Email del owner">
                  <input style={inputStyle} type="email" value={newTenant.owner_email}
                    onChange={(e) => setNewTenant({ ...newTenant, owner_email: e.target.value })} />
                </FndField>
                <FndField label="Nombre del owner">
                  <input style={inputStyle} value={newTenant.owner_display_name}
                    onChange={(e) => setNewTenant({ ...newTenant, owner_display_name: e.target.value })} />
                </FndField>
                <FndField label="Contraseña del owner">
                  <input style={inputStyle} type="password" value={newTenant.owner_password}
                    onChange={(e) => setNewTenant({ ...newTenant, owner_password: e.target.value })} />
                </FndField>
              </div>
              <button type="button" style={buttonPrimaryStyle}
                disabled={busy || !newTenant.name || !newTenant.slug ||
                  (!!newTenant.owner_email && newTenant.owner_password.length < 8)}
                onClick={createTenant}>Crear tenant</button>
            </div>
          </FndPanel>
        )}

        <FndPanel title="Roles" meta="Roles de sistema y roles custom del tenant">
          <FndTable
            empty="Sin roles"
            columns={[
              { key: "name", label: "Nombre" },
              { key: "is_system", label: "Tipo", render: (r) => (
                <FndBadge tone={r.is_system ? "muted" : "ok"}>{r.is_system ? "sistema" : "custom"}</FndBadge>
              ) },
              { key: "permissions", label: "Permisos", render: (r) => (
                <span style={monoStyle}>{(r.permissions || []).join(", ") || "—"}</span>
              ) },
              { key: "assigned_users", label: "Usuarios" },
              { key: "actions", label: "", render: (r) => (
                !r.is_system && !r.assigned_users
                  ? <button type="button" style={buttonDangerStyle} disabled={busy}
                      onClick={() => deleteRole(r)}>Borrar</button>
                  : null
              ) },
            ]}
            rows={roles || []}
          />

          <div style={Object.assign({}, stackStyle, { marginTop: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 })}>
            <div style={{ fontWeight: 650, fontSize: 12.5 }}>Crear rol custom</div>
            <div style={rowStyle}>
              <FndField label="Nombre">
                <input style={inputStyle} value={newRole.name}
                  onChange={(e) => setNewRole({ ...newRole, name: e.target.value })} />
              </FndField>
              <FndField label="Descripción">
                <input style={inputStyle} value={newRole.description}
                  onChange={(e) => setNewRole({ ...newRole, description: e.target.value })} />
              </FndField>
            </div>
            <FndField label="Permisos (catálogo)">
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 6 }}>
                {catalog.map((p) => (
                  <label key={p} style={{ display: "flex", gap: 5, alignItems: "center", fontSize: 12, cursor: "pointer" }}>
                    <input type="checkbox" checked={newRole.permissions.includes(p)}
                      onChange={() => setNewRole({ ...newRole, permissions: toggleIn(newRole.permissions, p) })} />
                    <span style={monoStyle}>{p}</span>
                  </label>
                ))}
              </div>
            </FndField>
            <button type="button" style={buttonPrimaryStyle} disabled={busy || newRole.name.length < 2}
              onClick={createRole}>Crear rol</button>
          </div>
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M16 · Tenant ═══════════════ */

  function TenantView({ api, me, tenant }) {
    const [info, setInfo] = useState(null);
    const [settingsText, setSettingsText] = useState("{}");
    const [report, setReport] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState("");

    const load = useCallback(async () => {
      try {
        const data = await api.get("/tenants");
        setInfo(data);
        setSettingsText(JSON.stringify(data.settings || {}, null, 2));
        setError(null);
      } catch (e) { setError(e); }
    }, []);
    useEffect(() => { load(); }, [load]);

    const saveSettings = async () => {
      setBusy(true); setError(null); setNotice("");
      try {
        let parsed;
        try { parsed = JSON.parse(settingsText); }
        catch (e) { throw new Error("Settings no es JSON válido: " + e.message); }
        await api.patch("/tenants/settings", { settings: parsed });
        setNotice("Settings guardados");
        await load();
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const checkIsolation = async () => {
      setBusy(true); setError(null); setNotice("");
      try { setReport(await api.get("/tenants/isolation-check")); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    if (!info && !error) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Cargando…</div>;

    return (
      <div style={stackStyle}>
        <FndError error={error} />
        {notice && <div><FndBadge tone="ok">{notice}</FndBadge></div>}

        {info && (
          <FndPanel title={info.name} meta={"slug: " + info.slug}>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
              <FndBadge tone={info.status === "active" ? "ok" : "warn"}>{info.status}</FndBadge>
              <FndBadge>plan: {info.plan}</FndBadge>
              <FndBadge>usuarios: {info.users_count}</FndBadge>
              <FndBadge>creado: {fmtDate(info.created_at)}</FndBadge>
              {info.activated_at ? <FndBadge tone="ok">activado: {fmtDate(info.activated_at)}</FndBadge> : null}
            </div>
            <FndField label="Settings (JSON editable)">
              <textarea style={Object.assign({}, inputStyle, monoStyle, { minHeight: 140, resize: "vertical" })}
                value={settingsText} onChange={(e) => setSettingsText(e.target.value)} />
            </FndField>
            <div style={{ marginTop: 10 }}>
              <button type="button" style={buttonPrimaryStyle} disabled={busy} onClick={saveSettings}>
                Guardar settings
              </button>
            </div>
          </FndPanel>
        )}

        <FndPanel title="Aislamiento multi-tenant (M16)"
          meta="Verifica que ninguna tabla fnd_* exponga filas de otros tenants"
          actions={<button type="button" style={buttonStyle} disabled={busy} onClick={checkIsolation}>Verificar aislamiento</button>}>
          {report ? (
            <div style={stackStyle}>
              <div>
                <FndBadge tone={report.ok ? "ok" : "danger"}>
                  {report.ok ? "Aislamiento correcto" : "FUGA DETECTADA"}
                </FndBadge>
              </div>
              <FndTable
                columns={[
                  { key: "table", label: "Tabla", render: (r) => <span style={monoStyle}>{r.table}</span> },
                  { key: "total_rows", label: "Filas totales" },
                  { key: "tenant_rows", label: "Del tenant" },
                  { key: "foreign_rows", label: "De otros tenants" },
                  { key: "ok", label: "Scoping", render: (r) => (
                    <FndBadge tone={r.ok ? "ok" : "danger"}>{r.ok ? "OK" : "LEAK"}</FndBadge>
                  ) },
                ]}
                rows={report.tables}
              />
            </div>
          ) : (
            <div style={{ color: "var(--text-muted)", fontSize: 12.5 }}>
              Pulsa «Verificar aislamiento» para generar el reporte por tabla.
            </div>
          )}
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M12 · Audit Trail ═══════════════ */

  function AuditView({ api }) {
    const [entries, setEntries] = useState(null);
    const [filters, setFilters] = useState({ action: "", actor: "" });
    const [verify, setVerify] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    const load = useCallback(async (f) => {
      const ff = f || filters;
      try {
        const qs = [];
        if (ff.action) qs.push("action=" + encodeURIComponent(ff.action));
        if (ff.actor) qs.push("actor=" + encodeURIComponent(ff.actor));
        const data = await api.get("/audit" + (qs.length ? "?" + qs.join("&") : ""));
        setEntries(data.entries.slice().reverse());
        setError(null);
      } catch (e) { setError(e); }
    }, [filters]);
    useEffect(() => { load({ action: "", actor: "" }); }, []);

    const doVerify = async () => {
      setBusy(true); setError(null);
      try { setVerify(await api.get("/audit/verify")); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const doExport = async () => {
      setBusy(true); setError(null);
      try {
        const appToken = localStorage.getItem("faberloom_token");
        const res = await fetch("/api/foundation/audit/export", {
          headers: appToken
            ? { "Authorization": `Bearer ${appToken}` }
            : { "X-Fnd-Session": F.getSession() || "" },
        });
        if (!res.ok) throw new Error("Export falló: HTTP " + res.status);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "audit_trail.jsonl";
        document.body.appendChild(a); a.click(); a.remove();
        URL.revokeObjectURL(url);
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    return (
      <div style={stackStyle}>
        <FndError error={error} />
        <FndPanel title="Audit Trail" meta="Cadena de hashes inmutable · append-only"
          actions={
            <React.Fragment>
              <button type="button" style={buttonStyle} disabled={busy} onClick={doVerify}>Verificar cadena</button>
              <button type="button" style={buttonStyle} disabled={busy} onClick={doExport}>Exportar JSONL</button>
            </React.Fragment>
          }>
          {verify && (
            <div style={{ marginBottom: 12, display: "flex", gap: 8, alignItems: "center" }}>
              <FndBadge tone={verify.ok ? "ok" : "danger"}>
                {verify.ok ? "Cadena íntegra" : "CADENA ROTA"}
              </FndBadge>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                {verify.checked} entradas verificadas{verify.broken_at ? " · rota en " + verify.broken_at : ""}
              </span>
            </div>
          )}
          <div style={Object.assign({}, rowStyle, { marginBottom: 12 })}>
            <FndField label="Acción">
              <input style={inputStyle} value={filters.action} placeholder="auth.login"
                onChange={(e) => setFilters({ ...filters, action: e.target.value })} />
            </FndField>
            <FndField label="Actor">
              <input style={inputStyle} value={filters.actor} placeholder="email o id"
                onChange={(e) => setFilters({ ...filters, actor: e.target.value })} />
            </FndField>
            <button type="button" style={buttonPrimaryStyle} onClick={() => load()}>Filtrar</button>
          </div>
          <FndTable
            empty="Sin entradas de auditoría"
            columns={[
              { key: "seq", label: "#" },
              { key: "created_at", label: "Fecha", render: (r) => fmtDate(r.created_at) },
              { key: "action", label: "Acción", render: (r) => <span style={monoStyle}>{r.action}</span> },
              { key: "actor_email", label: "Actor", render: (r) => r.actor_email || "—" },
              { key: "resource_type", label: "Recurso", render: (r) => (
                r.resource_type ? <span style={monoStyle}>{r.resource_type}:{r.resource_id}</span> : "—"
              ) },
              { key: "hash", label: "Hash", render: (r) => <span style={monoStyle}>{(r.hash || "").slice(0, 12)}…</span> },
            ]}
            rows={entries || []}
          />
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M15 · Eventos ═══════════════ */

  function EventsView({ api }) {
    const [events, setEvents] = useState(null);
    const [topic, setTopic] = useState("");
    const [streamStatus, setStreamStatus] = useState(null);
    const [error, setError] = useState(null);
    const [auto, setAuto] = useState(true);

    const load = useCallback(async () => {
      try {
        const qs = "?limit=100" + (topic ? "&topic=" + encodeURIComponent(topic) : "");
        const results = await Promise.all([
          api.get("/events" + qs),
          api.get("/events/stream-status"),
        ]);
        setEvents(results[0].events.slice().reverse());
        setStreamStatus(results[1]);
        setError(null);
      } catch (e) { setError(e); }
    }, [topic]);

    useEffect(() => { load(); }, [load]);
    useEffect(() => {
      if (!auto) return undefined;
      const interval = setInterval(load, 5000);
      return () => clearInterval(interval);
    }, [load, auto]);

    return (
      <div style={stackStyle}>
        <FndError error={error} />
        <FndPanel title="Eventos (outbox M15)"
          meta={streamStatus ? "última seq: " + streamStatus.last_seq + " · total: " + streamStatus.total_events : ""}
          actions={
            <React.Fragment>
              <label style={{ display: "flex", gap: 5, alignItems: "center", fontSize: 12 }}>
                <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} />
                Auto-refresh 5s
              </label>
              <button type="button" style={buttonStyle} onClick={load}>Refrescar</button>
            </React.Fragment>
          }>
          <div style={Object.assign({}, rowStyle, { marginBottom: 12 })}>
            <FndField label="Filtrar por topic">
              <input style={inputStyle} value={topic} placeholder="auth, tenant, rbac, policy…"
                onChange={(e) => setTopic(e.target.value)} />
            </FndField>
          </div>
          <FndTable
            empty="Sin eventos"
            columns={[
              { key: "seq", label: "#" },
              { key: "created_at", label: "Fecha", render: (r) => fmtDate(r.created_at) },
              { key: "topic", label: "Topic", render: (r) => <FndBadge>{r.topic}</FndBadge> },
              { key: "type", label: "Tipo", render: (r) => <span style={monoStyle}>{r.type}</span> },
              { key: "payload", label: "Payload", render: (r) => (
                <span style={monoStyle}>{JSON.stringify(r.payload)}</span>
              ) },
            ]}
            rows={events || []}
          />
        </FndPanel>

        <FndPanel title="Consumers" meta="Estado de consumo por consumer (lag vs. última seq)">
          <FndTable
            empty="Sin consumers registrados"
            columns={[
              { key: "consumer", label: "Consumer", render: (r) => <span style={monoStyle}>{r.consumer}</span> },
              { key: "last_seq", label: "Última seq ack" },
              { key: "lag", label: "Lag", render: (r) => (
                <FndBadge tone={r.lag === 0 ? "ok" : "warn"}>{r.lag}</FndBadge>
              ) },
              { key: "updated_at", label: "Actualizado", render: (r) => fmtDate(r.updated_at) },
            ]}
            rows={(streamStatus && streamStatus.consumers) || []}
          />
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M11 · Policy Gate D9 ═══════════════ */

  function PolicyView({ api }) {
    const [policies, setPolicies] = useState(null);
    const [decisions, setDecisions] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    const emptyEditor = {
      id: null, name: "", kind: "outbound", enabled: true,
      rulesText: JSON.stringify({
        actions: ["draft.send", "email.send"],
        allow_domains: [],
        block_domains: [],
        max_recipients: 10,
        blocked_patterns: [],
        blocked_data_categories: [],
        require_hitl: false,
      }, null, 2),
    };
    const [editor, setEditor] = useState(emptyEditor);
    const [dryRun, setDryRun] = useState({
      action: "draft.send",
      contextText: JSON.stringify({ recipients: ["cliente@ejemplo.com"], content: "Hola…" }, null, 2),
    });
    const [dryResult, setDryResult] = useState(null);

    const load = useCallback(async () => {
      try {
        const results = await Promise.all([
          api.get("/policy/policies"), api.get("/policy/decisions?limit=100"),
        ]);
        setPolicies(results[0].policies); setDecisions(results[1].decisions); setError(null);
      } catch (e) { setError(e); }
    }, []);
    useEffect(() => { load(); }, [load]);

    const run = async (fn) => {
      setBusy(true); setError(null);
      try { await fn(); await load(); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const parseRules = () => {
      try { return JSON.parse(editor.rulesText); }
      catch (e) { throw new Error("Rules no es JSON válido: " + e.message); }
    };

    const savePolicy = () => run(async () => {
      const body = { name: editor.name, kind: editor.kind, enabled: editor.enabled, rules: parseRules() };
      if (editor.id) await api.patch("/policy/policies/" + editor.id, body);
      else await api.post("/policy/policies", body);
      setEditor(emptyEditor);
    });

    const disablePolicy = (p) => run(async () => { await api.del("/policy/policies/" + p.id); });

    const editPolicy = (p) => setEditor({
      id: p.id, name: p.name, kind: p.kind, enabled: !!p.enabled,
      rulesText: JSON.stringify(p.rules || {}, null, 2),
    });

    const doEvaluate = async () => {
      setBusy(true); setError(null); setDryResult(null);
      try {
        let context;
        try { context = JSON.parse(dryRun.contextText); }
        catch (e) { throw new Error("Context no es JSON válido: " + e.message); }
        setDryResult(await api.post("/policy/evaluate", { action: dryRun.action, context }));
        await load();
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    };

    const decisionTone = (d) => (d === "allow" ? "ok" : d === "deny" ? "danger" : "warn");

    if (!policies && !error) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Cargando…</div>;

    return (
      <div style={stackStyle}>
        <FndError error={error} />

        <FndPanel title="Policies" meta="Reglas D9 fail-closed para acciones outbound"
          actions={<button type="button" style={buttonStyle} onClick={load}>Refrescar</button>}>
          <FndTable
            empty="Sin policies — las acciones outbound quedan en needs_approval (fail-closed)"
            columns={[
              { key: "name", label: "Nombre" },
              { key: "kind", label: "Kind", render: (r) => <FndBadge>{r.kind}</FndBadge> },
              { key: "enabled", label: "Estado", render: (r) => (
                <FndBadge tone={r.enabled ? "ok" : "muted"}>{r.enabled ? "enabled" : "disabled"}</FndBadge>
              ) },
              { key: "rules", label: "Reglas", render: (r) => (
                <span style={monoStyle}>{JSON.stringify(r.rules)}</span>
              ) },
              { key: "actions", label: "", render: (r) => (
                <span style={{ display: "flex", gap: 6 }}>
                  <button type="button" style={buttonStyle} onClick={() => editPolicy(r)}>Editar</button>
                  {r.enabled ? (
                    <button type="button" style={buttonDangerStyle} disabled={busy}
                      onClick={() => disablePolicy(r)}>Deshabilitar</button>
                  ) : null}
                </span>
              ) },
            ]}
            rows={policies || []}
          />

          <div style={Object.assign({}, stackStyle, { marginTop: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 })}>
            <div style={{ fontWeight: 650, fontSize: 12.5 }}>
              {editor.id ? "Editar policy" : "Crear policy"}
            </div>
            <div style={rowStyle}>
              <FndField label="Nombre">
                <input style={inputStyle} value={editor.name}
                  onChange={(e) => setEditor({ ...editor, name: e.target.value })} />
              </FndField>
              <FndField label="Kind">
                <input style={inputStyle} value={editor.kind}
                  onChange={(e) => setEditor({ ...editor, kind: e.target.value })} />
              </FndField>
              <label style={{ display: "flex", gap: 5, alignItems: "center", fontSize: 12.5 }}>
                <input type="checkbox" checked={editor.enabled}
                  onChange={(e) => setEditor({ ...editor, enabled: e.target.checked })} />
                Enabled
              </label>
            </div>
            <FndField label="Rules (JSON: actions, allow_domains, block_domains, max_recipients, blocked_patterns, blocked_data_categories, require_hitl)">
              <textarea style={Object.assign({}, inputStyle, monoStyle, { minHeight: 160, resize: "vertical" })}
                value={editor.rulesText} onChange={(e) => setEditor({ ...editor, rulesText: e.target.value })} />
            </FndField>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" style={buttonPrimaryStyle} disabled={busy || editor.name.length < 2}
                onClick={savePolicy}>{editor.id ? "Guardar cambios" : "Crear policy"}</button>
              {editor.id ? (
                <button type="button" style={buttonStyle} onClick={() => setEditor(emptyEditor)}>Cancelar</button>
              ) : null}
            </div>
          </div>
        </FndPanel>

        <FndPanel title="Dry-run · evaluar acción" meta="Evalúa el gate sin ejecutar nada">
          <div style={stackStyle}>
            <div style={rowStyle}>
              <FndField label="Acción">
                <input style={inputStyle} value={dryRun.action} placeholder="draft.send"
                  onChange={(e) => setDryRun({ ...dryRun, action: e.target.value })} />
              </FndField>
              <button type="button" style={buttonPrimaryStyle} disabled={busy || !dryRun.action}
                onClick={doEvaluate}>Evaluar</button>
            </div>
            <FndField label="Context (JSON: recipients, content, data_categories)">
              <textarea style={Object.assign({}, inputStyle, monoStyle, { minHeight: 110, resize: "vertical" })}
                value={dryRun.contextText} onChange={(e) => setDryRun({ ...dryRun, contextText: e.target.value })} />
            </FndField>
            {dryResult && (
              <div style={stackStyle}>
                <div><FndBadge tone={decisionTone(dryResult.decision)}>{dryResult.decision}</FndBadge></div>
                <FndJson value={dryResult} />
              </div>
            )}
          </div>
        </FndPanel>

        <FndPanel title="Decisiones" meta="Log de evaluaciones del gate">
          <FndTable
            empty="Sin decisiones registradas"
            columns={[
              { key: "created_at", label: "Fecha", render: (r) => fmtDate(r.created_at) },
              { key: "action", label: "Acción", render: (r) => <span style={monoStyle}>{r.action}</span> },
              { key: "decision", label: "Decisión", render: (r) => (
                <FndBadge tone={decisionTone(r.decision)}>{r.decision}</FndBadge>
              ) },
              { key: "reasons", label: "Motivos", render: (r) => (
                <span style={{ fontSize: 11.5 }}>{(r.reasons || []).join(" · ") || "—"}</span>
              ) },
            ]}
            rows={decisions || []}
          />
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M05 · Configuración de correo (IMAP/SMTP/Firma) ═══════════════ */

  function MailPanelWrapper({ activeWorkspace, Panel, title }) {
    if (!activeWorkspace) {
      const W = window.WorkspaceRequired;
      if (W) return <W icon="mail" title={title} />;
      return <div style={{ padding: 24, color: "var(--text-muted)" }}>Selecciona un workspace activo para configurar {title}.</div>;
    }
    return <Panel activeWorkspace={activeWorkspace} />;
  }

  function FndIMAPView({ activeWorkspace }) {
    const Panel = (window.FaberLoomMailPanels || {}).IMAPConfigPanel;
    if (!Panel) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Panel IMAP no cargado.</div>;
    return <MailPanelWrapper activeWorkspace={activeWorkspace} Panel={Panel} title="IMAP" />;
  }

  function FndSMTPView({ activeWorkspace }) {
    const Panel = (window.FaberLoomMailPanels || {}).SMTPConfigPanel;
    if (!Panel) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Panel SMTP no cargado.</div>;
    return <MailPanelWrapper activeWorkspace={activeWorkspace} Panel={Panel} title="SMTP" />;
  }

  function FndSignatureView({ activeWorkspace }) {
    const Panel = (window.FaberLoomMailPanels || {}).EmailSignaturePanel;
    if (!Panel) return <div style={{ padding: 24, color: "var(--text-muted)" }}>Panel de firma no cargado.</div>;
    return <MailPanelWrapper activeWorkspace={activeWorkspace} Panel={Panel} title="Firma de correo" />;
  }

  /* ═══════════════ Registro de vistas ═══════════════ */

  F.register({ id: "m07-bootstrap", label: "Bootstrap", group: "Plataforma", order: 7, hidden: true, component: BootstrapWizard });
  F.register({ id: "m08-login", label: "Login", group: "Plataforma", order: 8, hidden: true, component: LoginView });
  F.register({ id: "m05-imap", label: "IMAP", group: "Plataforma", order: 5, component: FndIMAPView });
  F.register({ id: "m05-smtp", label: "SMTP", group: "Plataforma", order: 5, component: FndSMTPView });
  F.register({ id: "m05-signature", label: "Firma", group: "Plataforma", order: 5, component: FndSignatureView });
  F.register({ id: "m16-tenant", label: "Tenant", group: "Plataforma", order: 7, permission: "tenants.read", component: TenantView });
  F.register({ id: "m08-sessions", label: "Sesiones y 2FA", group: "Plataforma", order: 8, component: SessionsView });
  F.register({ id: "m09-rbac", label: "Roles y permisos", group: "Plataforma", order: 9, permission: "users.manage", component: RbacView });
  F.register({ id: "m11-policy", label: "Policy Gate D9", group: "Plataforma", order: 11, permission: "policy.manage", component: PolicyView });
  F.register({ id: "m12-audit", label: "Audit Trail", group: "Plataforma", order: 12, permission: "audit.read", component: AuditView });
  F.register({ id: "m15-events", label: "Eventos", group: "Plataforma", order: 15, permission: "events.read", component: EventsView });
})();
