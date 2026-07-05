/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation Desktop (M18–M20)
   M18 Dispositivos · M19 Sync offline · M20 Actualizaciones
   Port de foundation_beta/desktop (Electron) a pywebview+FastAPI.
   Se registra con window.Foundation.register(...). Sin imports.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  const { useState, useEffect, useCallback } = React;
  const F = window.Foundation;
  const { FndPanel, FndBadge, FndTable, FndField, FndError, FndJson, inputStyle, buttonStyle, buttonPrimaryStyle, buttonDangerStyle } = F.ui;

  /* ── Almacén local del device (equivalente cliente de keytar) ── */
  const DEVICE_KEY = "faberloom-fnd-device";
  function getLocalDevice() {
    try { return JSON.parse(localStorage.getItem(DEVICE_KEY) || "null"); } catch (e) { return null; }
  }
  function setLocalDevice(dev) {
    try {
      if (dev) localStorage.setItem(DEVICE_KEY, JSON.stringify(dev));
      else localStorage.removeItem(DEVICE_KEY);
    } catch (e) {}
  }

  const mono = { fontFamily: "var(--font-mono)", fontSize: 11.5 };
  const hintStyle = { color: "var(--text-muted)", fontSize: 12, marginBottom: 12 };

  function NoDeviceHint() {
    return (
      <div style={hintStyle}>
        Este equipo aún no está registrado como dispositivo. Ve a <b>Dispositivos</b> (M18) y registra este dispositivo primero.
      </div>
    );
  }

  function statusTone(s) {
    if (s === "applied" || s === "installed" || s === "staged" || s === "delta") return "ok";
    if (s === "queued" || s === "available" || s === "full" || s === "checking" || s === "downloading") return "warn";
    if (s === "conflict" || s === "failed" || s === "blocked") return "danger";
    return "muted";
  }

  /* ═══════════════ M18 · Dispositivos ═══════════════ */

  function DevicesView({ api, me }) {
    const [devices, setDevices] = useState([]);
    const [error, setError] = useState(null);
    const [name, setName] = useState("");
    const [busy, setBusy] = useState(false);
    const [issued, setIssued] = useState(null);      // {device_id, device_secret} — se muestra UNA vez
    const [loginResult, setLoginResult] = useState(null);
    const local = getLocalDevice();

    const load = useCallback(async () => {
      try { setDevices((await api.get("/desktop/auth/devices")).devices || []); setError(null); }
      catch (e) { setError(e); }
    }, [api]);
    useEffect(() => { load(); }, [load]);

    const register = useCallback(async () => {
      if (!name.trim()) { setError(new Error("Ponle un nombre al dispositivo")); return; }
      setBusy(true); setError(null);
      try {
        const res = await api.post("/desktop/auth/device/register", {
          name: name.trim(),
          platform: (navigator.platform || "desktop").slice(0, 60),
        });
        setLocalDevice({ device_id: res.device_id, device_secret: res.device_secret });
        setIssued(res);
        setName("");
        await load();
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [api, name, load]);

    const testLogin = useCallback(async () => {
      const creds = getLocalDevice();
      if (!creds) { setError(new Error("No hay credenciales de dispositivo guardadas en este equipo")); return; }
      setBusy(true); setError(null); setLoginResult(null);
      try {
        const res = await api.post("/desktop/auth/device/login", creds);
        setLoginResult(res);
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [api]);

    const revoke = useCallback(async (id) => {
      setBusy(true); setError(null);
      try {
        await api.post("/desktop/auth/devices/" + id + "/revoke", {});
        if (local && local.device_id === id) setLocalDevice(null);
        await load();
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [api, load, local]);

    const columns = [
      { key: "name", label: "Nombre" },
      { key: "platform", label: "Plataforma" },
      { key: "id", label: "Device ID", render: (r) => <span style={mono}>{r.id}{local && local.device_id === r.id ? " · este equipo" : ""}</span> },
      { key: "last_seen_at", label: "Última actividad", render: (r) => <span style={mono}>{(r.last_seen_at || "").slice(0, 19)}</span> },
      { key: "estado", label: "Estado", render: (r) => <FndBadge tone={r.revoked_at ? "danger" : "ok"}>{r.revoked_at ? "revocado" : "activo"}</FndBadge> },
      {
        key: "acciones", label: "", render: (r) => (
          r.revoked_at ? null : (
            <button type="button" disabled={busy} style={buttonDangerStyle} onClick={() => revoke(r.id)}>Revocar</button>
          )
        ),
      },
    ];

    return (
      <div style={{ display: "grid", gap: 14 }}>
        <FndPanel title="Registrar este dispositivo" meta="M18 · device_id + device_secret (almacén cifrado local en el servidor)">
          <FndError error={error} />
          <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) auto auto", gap: 10, alignItems: "end" }}>
            <FndField label="Nombre del dispositivo">
              <input style={inputStyle} value={name} placeholder="p. ej. Laptop de Ale"
                onChange={(e) => setName(e.target.value)} />
            </FndField>
            <button type="button" disabled={busy} style={buttonPrimaryStyle} onClick={register}>Registrar</button>
            <button type="button" disabled={busy || !local} style={buttonStyle} onClick={testLogin}>Probar device login</button>
          </div>
          {local && (
            <div style={Object.assign({ marginTop: 10 }, hintStyle, { marginBottom: 0 })}>
              Credenciales guardadas en este equipo: <span style={mono}>{local.device_id}</span>
            </div>
          )}
          {issued && (
            <div style={{ marginTop: 12, padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--coral-soft)", border: "1px solid var(--coral)", fontSize: 12.5 }}>
              <b>Guarda este secret ahora: no se volverá a mostrar.</b>
              <div style={Object.assign({}, mono, { marginTop: 6, wordBreak: "break-all" })}>device_id: {issued.device_id}</div>
              <div style={Object.assign({}, mono, { wordBreak: "break-all" })}>device_secret: {issued.device_secret}</div>
              <div style={{ marginTop: 6, color: "var(--text-muted)" }}>Ya quedó guardado en el almacén local de este equipo (localStorage).</div>
            </div>
          )}
          {loginResult && (
            <div style={{ marginTop: 12 }}>
              <FndBadge tone="ok">device login OK</FndBadge>
              <div style={{ marginTop: 8 }}><FndJson value={loginResult} /></div>
            </div>
          )}
        </FndPanel>

        <FndPanel title="Dispositivos" meta={devices.length + " dispositivo(s)"}
          actions={<button type="button" style={buttonStyle} onClick={load}>Refrescar</button>}>
          <FndTable columns={columns} rows={devices} empty="Sin dispositivos registrados" />
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M19 · Sync offline ═══════════════ */

  function SyncView({ api }) {
    const [status, setStatus] = useState(null);
    const [mutations, setMutations] = useState([]);
    const [pullResult, setPullResult] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const local = getLocalDevice();

    const load = useCallback(async () => {
      try {
        setStatus(await api.get("/sync/status"));
        setMutations((await api.get("/sync/mutations")).mutations || []);
        setError(null);
      } catch (e) { setError(e); }
    }, [api]);
    useEffect(() => { load(); }, [load]);

    const run = useCallback(async (fn) => {
      if (!local) { setError(new Error("Registra este dispositivo primero (vista Dispositivos)")); return; }
      setBusy(true); setError(null);
      try { await fn(local.device_id); await load(); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [local, load]);

    const doPull = () => run(async (id) => setPullResult(await api.post("/sync/pull", { device_id: id })));
    const doReconcile = () => run(async (id) => setPullResult(await api.post("/sync/reconcile", { device_id: id })));
    const doApply = () => run(async (id) => setPullResult(await api.post("/sync/apply", { device_id: id })));

    const sync = status && status.sync;
    const columns = [
      { key: "method", label: "Método" },
      { key: "path", label: "Ruta", render: (r) => <span style={mono}>{r.path}</span> },
      { key: "status", label: "Estado", render: (r) => <FndBadge tone={statusTone(r.status)}>{r.status}</FndBadge> },
      { key: "queued_at", label: "Encolada", render: (r) => <span style={mono}>{(r.queued_at || "").slice(0, 19)}</span> },
      { key: "applied_at", label: "Aplicada", render: (r) => <span style={mono}>{(r.applied_at || "—").slice(0, 19)}</span> },
      { key: "error", label: "Detalle", render: (r) => r.error ? <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>{r.error}</span> : "—" },
    ];

    return (
      <div style={{ display: "grid", gap: 14 }}>
        <FndPanel title="Estado de sincronización" meta="M19 · cursores + delta vs full refresh (gap > 24h)"
          actions={
            <React.Fragment>
              <button type="button" disabled={busy} style={buttonPrimaryStyle} onClick={doPull}>Pull</button>
              <button type="button" disabled={busy} style={buttonStyle} onClick={doApply}>Aplicar cola</button>
              <button type="button" disabled={busy} style={buttonStyle} onClick={doReconcile}>Reconcile</button>
              <button type="button" style={buttonStyle} onClick={load}>Refrescar</button>
            </React.Fragment>
          }>
          <FndError error={error} />
          {!local && <NoDeviceHint />}
          {status && status.state === "unbound" && <div style={hintStyle}>La sesión actual no está ligada a ningún dispositivo.</div>}
          {status && status.state === "bound" && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              <FndBadge>{"device " + status.device_id}</FndBadge>
              <FndBadge tone={sync ? statusTone(sync.mode) : "muted"}>{"modo " + (sync ? sync.mode : "sin estado")}</FndBadge>
              <FndBadge>{"cursor " + (sync && sync.last_event_seq != null ? sync.last_event_seq : "—") + " / servidor " + status.server_max_seq}</FndBadge>
              <FndBadge>{"último sync " + (sync && sync.last_sync_at ? sync.last_sync_at.slice(0, 19) : "nunca")}</FndBadge>
              <FndBadge tone={status.pending_mutations > 0 ? "warn" : "ok"}>{status.pending_mutations + " mutación(es) pendiente(s)"}</FndBadge>
            </div>
          )}
          {pullResult && (
            <div style={{ marginTop: 12 }}>
              {pullResult.mode === "full_refresh" && (
                <div style={{ marginBottom: 8 }}>
                  <FndBadge tone="warn">full refresh requerido</FndBadge>
                  <span style={{ marginLeft: 8, fontSize: 12, color: "var(--text-muted)" }}>{pullResult.reason} — tras recargar el estado, pulsa Reconcile.</span>
                </div>
              )}
              {pullResult.mode === "delta" && (
                <div style={{ marginBottom: 8 }}>
                  <FndBadge tone="ok">{"delta · " + pullResult.events.length + " evento(s)"}</FndBadge>
                </div>
              )}
              <FndJson value={pullResult} />
            </div>
          )}
        </FndPanel>

        <FndPanel title="Cola de mutaciones offline" meta={mutations.length + " mutación(es) · queued | applied | conflict"}>
          <FndTable columns={columns} rows={mutations} empty="Sin mutaciones en cola" />
        </FndPanel>
      </div>
    );
  }

  /* ═══════════════ M20 · Actualizaciones ═══════════════ */

  function UpdatesView({ api, me }) {
    const [current, setCurrent] = useState(null);
    const [channel, setChannel] = useState("stable");
    const [checkResult, setCheckResult] = useState(null);
    const [state, setState] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [manifestText, setManifestText] = useState("");
    const [manifestMsg, setManifestMsg] = useState(null);
    const local = getLocalDevice();
    const canManage = ((me && me.permissions) || []).some((p) => p === "*" || p === "updates.manage");

    const loadState = useCallback(async () => {
      if (!local) return;
      try { setState(await api.get("/updates/state?device_id=" + encodeURIComponent(local.device_id))); }
      catch (e) {}
    }, [api]);

    useEffect(() => {
      (async () => {
        try { setCurrent((await api.get("/updates/current")).version); } catch (e) { setError(e); }
        await loadState();
      })();
    }, [api, loadState]);

    useEffect(() => {
      (async () => {
        try {
          const res = await api.get("/updates/manifest?channel=" + channel);
          setManifestText(res.manifest ? JSON.stringify(res.manifest, null, 2) : "");
        } catch (e) {}
      })();
    }, [api, channel]);

    const run = useCallback(async (fn) => {
      if (!local) { setError(new Error("Registra este dispositivo primero (vista Dispositivos)")); return; }
      setBusy(true); setError(null);
      try { await fn(local.device_id); await loadState(); }
      catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [local, loadState]);

    const doCheck = () => run(async (id) => {
      setCheckResult(await api.post("/updates/check", { device_id: id, current_version: current || "0.0.0", channel: channel }));
    });
    const doStage = () => run(async (id) => {
      const version = checkResult && checkResult.manifest && checkResult.manifest.version;
      if (!version) throw new Error("Primero ejecuta Check y asegúrate de que hay update disponible");
      setCheckResult(await api.post("/updates/stage", { device_id: id, version: version }));
    });
    const doInstall = () => run(async (id) => {
      setCheckResult(await api.post("/updates/install", { device_id: id }));
    });

    const saveManifest = useCallback(async () => {
      setBusy(true); setError(null); setManifestMsg(null);
      try {
        const manifest = JSON.parse(manifestText);
        await api.put("/updates/manifest", { channel: channel, manifest: manifest });
        setManifestMsg("Manifiesto publicado en el canal " + channel + ".");
      } catch (e) { setError(e); }
      finally { setBusy(false); }
    }, [api, channel, manifestText]);

    const actionLabel = {
      up_to_date: ["ok", "Al día"],
      update_available: ["warn", "Update disponible"],
      force_update: ["danger", "Update forzoso (versión < mínima soportada)"],
      staged: ["ok", "Descargado y verificado (staged)"],
      installed: ["ok", "Instalado"],
      blocked: ["danger", "Instalación bloqueada"],
    };
    const key = checkResult && (checkResult.action || checkResult.status);
    const badge = key && actionLabel[key];

    return (
      <div style={{ display: "grid", gap: 14 }}>
        <FndPanel title="Actualizaciones" meta="M20 · canales + min_supported + gate por sync (M19)"
          actions={
            <React.Fragment>
              <select value={channel} onChange={(e) => setChannel(e.target.value)}
                style={Object.assign({}, inputStyle, { width: "auto", padding: "8px 10px" })}>
                <option value="stable">stable</option>
                <option value="beta">beta</option>
              </select>
              <button type="button" disabled={busy} style={buttonPrimaryStyle} onClick={doCheck}>Check</button>
              <button type="button" disabled={busy} style={buttonStyle} onClick={doStage}>Stage</button>
              <button type="button" disabled={busy} style={buttonStyle} onClick={doInstall}>Install</button>
            </React.Fragment>
          }>
          <FndError error={error} />
          {!local && <NoDeviceHint />}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <FndBadge tone="ok">{"versión actual " + (current || "…")}</FndBadge>
            <FndBadge>{"canal " + channel}</FndBadge>
            {state && state.status && <FndBadge tone={statusTone(state.status)}>{"estado " + state.status}</FndBadge>}
            {state && state.staged_version && <FndBadge tone="warn">{"staged " + state.staged_version}</FndBadge>}
          </div>
          {state && state.blocked_reason && (
            <div style={{ marginTop: 10, padding: "10px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", fontSize: 12.5 }}>
              <b>Instalación bloqueada:</b> {state.blocked_reason}
              {state.blocked_reason === "pending mutations" && <span> — aplica la cola y reconcilia en <b>Sync offline</b> antes de instalar.</span>}
            </div>
          )}
          {checkResult && (
            <div style={{ marginTop: 12 }}>
              {badge && <FndBadge tone={badge[0]}>{badge[1]}</FndBadge>}
              <div style={{ marginTop: 8 }}><FndJson value={checkResult} /></div>
            </div>
          )}
        </FndPanel>

        {canManage && (
          <FndPanel title="Editor de manifiesto" meta={"canal " + channel + " · requiere updates.manage"}
            actions={<button type="button" disabled={busy} style={buttonPrimaryStyle} onClick={saveManifest}>Publicar manifiesto</button>}>
            {manifestMsg && <div style={Object.assign({}, hintStyle, { color: "var(--text-secondary)" })}>{manifestMsg}</div>}
            <FndField label={"Manifiesto JSON (" + channel + ")"}>
              <textarea rows={10} spellCheck={false} style={Object.assign({}, inputStyle, mono, { resize: "vertical" })}
                value={manifestText}
                placeholder={'{\n  "version": "0.3.0",\n  "min_supported_client_version": "0.2.0",\n  "url": "https://updates.example/faberloom-0.3.0.bin",\n  "sha256": "…",\n  "notes": "…"\n}'}
                onChange={(e) => setManifestText(e.target.value)} />
            </FndField>
          </FndPanel>
        )}
      </div>
    );
  }

  /* ── Registro de vistas ── */
  F.register({ id: "m18-devices", label: "Dispositivos", group: "Desktop", order: 18, permission: null, component: DevicesView });
  F.register({ id: "m19-sync", label: "Sync offline", group: "Desktop", order: 19, permission: null, component: SyncView });
  F.register({ id: "m20-updates", label: "Actualizaciones", group: "Desktop", order: 20, permission: null, component: UpdatesView });
})();
