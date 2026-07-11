/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Tenant / Workspace / User Settings Cascade (E3-2)
   Vista de settings con herencia tenant → workspace → user.
   Primera versión: lectura + edición básica de overrides en cada nivel.
   ═══════════════════════════════════════════════════════════════ */

var { useCallback, useEffect, useMemo, useState } = React;

const SET_S = {
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, gap: 12, flexWrap: "wrap" },
  title: { margin: 0, font: "italic 500 22px/1.2 var(--font-title)" },
  meta: { color: "var(--text-muted)", fontSize: 12, fontFamily: "var(--font-mono)" },
  tabs: { display: "flex", gap: 6, marginBottom: 16, borderBottom: "1px solid var(--border-subtle)", paddingBottom: 6 },
  tab: { padding: "8px 12px", border: 0, background: "transparent", color: "var(--text-muted)", cursor: "pointer", fontWeight: 600, fontSize: 12.5, borderRadius: "var(--r-sm)" },
  tabActive: { background: "var(--bg-raised)", color: "var(--text-primary)" },
  card: { padding: 16, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)", marginBottom: 14 },
  cardTitle: { fontWeight: 650, fontSize: 14, marginBottom: 4, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: 8 },
  cardMeta: { fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)", marginBottom: 12 },
  field: { display: "grid", gap: 6, marginBottom: 12 },
  label: { fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px" },
  value: { fontSize: 13, color: "var(--text-secondary)", fontFamily: "var(--font-mono)", padding: "8px 10px", border: "1px solid var(--border-subtle)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)" },
  input: { width: "100%", padding: "8px 10px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 13, boxSizing: "border-box" },
  inheritChip: { display: "inline-flex", alignItems: "center", gap: 5, padding: "2px 7px", borderRadius: 999, fontSize: 10, color: "var(--text-muted)", background: "var(--bg-raised)", border: "1px solid var(--border-default)", marginLeft: 8 },
  resolved: { padding: 10, borderRadius: "var(--r-sm)", background: "var(--sage-soft)", border: "1px solid var(--sage-deep)", color: "var(--text-secondary)", fontSize: 12, marginTop: 8 },
  actions: { display: "flex", gap: 8, marginTop: 12 },
  button: { padding: "7px 11px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 11.5 },
  buttonPrimary: { padding: "7px 11px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 700, fontSize: 11.5 },
  empty: { padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" },
  error: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
};

async function apiGet(path) {
  const res = await fetch(path);
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

async function apiPut(path, body) {
  const res = await fetch(path, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

function SettingField({ setting, edit, editedValue, onChange }) {
  const source = setting.source || "default";
  const sourceLabel = { default: "default", tenant: "tenant", workspace: "workspace", user: "user" }[source] || source;
  const currentValue = editedValue != null ? editedValue : setting.value;
  const isSelect = setting.key === "routing.byo_mode";
  return (
    <div style={SET_S.field}>
      <label style={SET_S.label}>{setting.label || setting.key}
        {source !== "default" && <span style={SET_S.inheritChip}>heredado de {sourceLabel}</span>}
      </label>
      {edit ? (
        isSelect ? (
          <select style={SET_S.input} value={currentValue} onChange={(e) => onChange(setting.key, e.target.value)}>
            <option value="hibrido">híbrido (fallback a plataforma)</option>
            <option value="estricto">estricto (solo claves propias)</option>
          </select>
        ) : (
          <input style={SET_S.input} value={currentValue} onChange={(e) => onChange(setting.key, e.target.value)} placeholder={setting.value} />
        )
      ) : (
        <div style={SET_S.value}>{String(setting.value)}</div>
      )}
      {setting.description && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{setting.description}</div>}
    </div>
  );
}

function SettingsCard({ title, meta, scope, settings, editable, onSave }) {
  const [edit, setEdit] = useState(false);
  const [draft, setDraft] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      await onSave(draft);
      setEdit(false);
      setDraft({});
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={SET_S.card}>
      <div style={SET_S.cardTitle}><Icon name="settings" size={16} /> {title}</div>
      <div style={SET_S.cardMeta}>{meta}</div>
      {error && <div style={SET_S.error} role="alert">{error}</div>}
      {settings.length === 0 ? <div style={SET_S.empty}>No hay settings disponibles.</div> : (
        <>
          {settings.map((s) => (
            <SettingField
              key={s.key}
              setting={s}
              edit={edit}
              editedValue={draft[s.key]}
              onChange={(key, value) => setDraft((d) => ({ ...d, [key]: value }))}
            />
          ))}
          {editable && (
            <div style={SET_S.actions}>
              {edit ? (
                <>
                  <button type="button" style={SET_S.buttonPrimary} onClick={save} disabled={busy}>{busy ? "Guardando…" : "Guardar overrides"}</button>
                  <button type="button" style={SET_S.button} onClick={() => { setEdit(false); setDraft({}); }} disabled={busy}>Cancelar</button>
                </>
              ) : (
                <button type="button" style={SET_S.button} onClick={() => setEdit(true)}>Editar overrides</button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function TenantSettings({ activeWorkspace, user }) {
  const [tab, setTab] = useState("resolved");
  const [data, setData] = useState({ tenant: null, workspace: null, user: null, resolved: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usage, setUsage] = useState(null);
  const [usageLoading, setUsageLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const paths = ["/api/tenant/settings"];
      if (activeWorkspace) paths.push(`/api/workspaces/${activeWorkspace.id}/settings`);
      paths.push("/api/users/me/settings");
      const [tenantData, workspaceData, userData] = activeWorkspace
        ? await Promise.all(paths.map((p) => apiGet(p)))
        : [await apiGet(paths[0]), null, await apiGet(paths[2])];
      const resolved = await apiGet(`/api/settings/resolved${activeWorkspace ? `?workspace_id=${activeWorkspace.id}` : ""}`).catch(() => ({ settings: [] }));
      setData({ tenant: tenantData, workspace: workspaceData, user: userData, resolved: resolved.settings || [] });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [activeWorkspace]);

  const loadUsage = useCallback(async () => {
    if (!user || !user.tenant_id) return;
    setUsageLoading(true);
    try {
      const summary = await apiGet(`/api/tenants/${user.tenant_id}/usage/summary`);
      setUsage(summary);
    } catch (e) {
      setUsage(null);
    } finally {
      setUsageLoading(false);
    }
  }, [user]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { loadUsage(); }, [loadUsage]);

  const saveTenant = async (draft) => apiPut("/api/tenant/settings", { overrides: draft });
  const saveWorkspace = async (draft) => apiPut(`/api/workspaces/${activeWorkspace.id}/settings`, { overrides: draft });
  const saveUser = async (draft) => apiPut("/api/users/me/settings", { overrides: draft });

  const resolvedSettings = data.resolved.map((s) => ({ ...s, source: s.source || "default" }));

  return (
    <div style={{ padding: "18px 20px", overflow: "auto" }}>
      <div style={SET_S.header}>
        <div>
          <h2 style={SET_S.title}>Configuración en cascada</h2>
          <div style={SET_S.meta}>Resolución: user &gt; workspace &gt; tenant &gt; default</div>
        </div>
      </div>

      {error && <div style={SET_S.error} role="alert"><Icon name="shield" size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />{error}</div>}

      <div style={SET_S.tabs}>
        {[
          { id: "resolved", label: "Resuelto" },
          { id: "tenant", label: "Tenant" },
          { id: "workspace", label: "Workspace" },
          { id: "user", label: "Usuario" },
          { id: "usage", label: "Resumen de uso" },
        ].map((t) => (
          <button key={t.id} type="button" style={{ ...SET_S.tab, ...(tab === t.id ? SET_S.tabActive : {}) }} onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {loading ? <div style={SET_S.empty}>Cargando configuración…</div> : (
        <>
          {tab === "resolved" && (
            <div style={SET_S.card}>
              <div style={SET_S.cardTitle}><Icon name="check" size={16} /> Configuración efectiva</div>
              <div style={SET_S.cardMeta}>{activeWorkspace ? `Workspace: ${activeWorkspace.name}` : "Sin workspace activo"}</div>
              {resolvedSettings.length === 0 ? <div style={SET_S.empty}>No hay settings resueltos.</div> : (
                resolvedSettings.map((s) => (
                  <div key={s.key} style={SET_S.field}>
                    <label style={SET_S.label}>{s.label || s.key} <span style={SET_S.inheritChip}>fuente: {s.source}</span></label>
                    <div style={SET_S.value}>{String(s.value)}</div>
                    {s.description && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{s.description}</div>}
                  </div>
                ))
              )}
            </div>
          )}
          {tab === "tenant" && <SettingsCard title="Tenant" meta="Settings a nivel de organización" scope="tenant" settings={data.tenant && data.tenant.settings ? data.tenant.settings : []} editable={true} onSave={saveTenant} />}
          {tab === "workspace" && (
            activeWorkspace
              ? <SettingsCard title="Workspace" meta={`Overrides para ${activeWorkspace.name}`} scope="workspace" settings={data.workspace && data.workspace.settings ? data.workspace.settings : []} editable={true} onSave={saveWorkspace} />
              : <div style={SET_S.empty}>Seleccioná un workspace para ver sus overrides.</div>
          )}
          {tab === "user" && <SettingsCard title="Usuario" meta="Overrides personales" scope="user" settings={data.user && data.user.settings ? data.user.settings : []} editable={true} onSave={saveUser} />}
          {tab === "usage" && (
            <div style={SET_S.card}>
              <div style={SET_S.cardTitle}><Icon name="bar-chart" size={16} /> Resumen de uso</div>
              <div style={SET_S.cardMeta}>Tenant: {user && user.tenant_id ? user.tenant_id : "—"}</div>
              {usageLoading ? <div style={SET_S.empty}>Cargando…</div> : !usage ? <div style={SET_S.empty}>No disponible.</div> : (
                <>
                  <div style={SET_S.field}>
                    <label style={SET_S.label}>Costo total (USD)</label>
                    <div style={SET_S.value}>{usage.total_cost_usd != null ? usage.total_cost_usd.toFixed(6) : "—"}</div>
                  </div>
                  <div style={SET_S.field}>
                    <label style={SET_S.label}>Recargos por clave de plataforma (USD)</label>
                    <div style={SET_S.value}>{usage.total_surcharge_usd != null ? usage.total_surcharge_usd.toFixed(6) : "—"}</div>
                  </div>
                  <div style={SET_S.field}>
                    <label style={SET_S.label}>Registros</label>
                    <div style={SET_S.value}>{usage.total_rows != null ? usage.total_rows : "—"}</div>
                  </div>
                  {usage.breakdown && usage.breakdown.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", marginBottom: 8 }}>DESGLOSE</div>
                      {usage.breakdown.map((row, idx) => (
                        <div key={idx} style={{ fontSize: 12, color: "var(--text-secondary)", padding: "6px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                          {row.month} · {row.provider_slug}/{row.model}: ${row.total_cost_usd != null ? row.total_cost_usd.toFixed(4) : "—"} ({row.row_count} rows)
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

window.TenantSettings = TenantSettings;
