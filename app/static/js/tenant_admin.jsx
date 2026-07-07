/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Platform Admin Panel (E3-2)
   Panel para el rol platform_admin: gestión del ciclo de vida de tenants
   y métricas agregadas. NUNCA muestra contenido de los tenants.
   ═══════════════════════════════════════════════════════════════ */

var { useCallback, useEffect, useMemo, useState } = React;

const ADMIN_S = {
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, gap: 12, flexWrap: "wrap" },
  title: { margin: 0, font: "italic 500 22px/1.2 var(--font-title)" },
  meta: { color: "var(--text-muted)", fontSize: 12, fontFamily: "var(--font-mono)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 16 },
  metricCard: { padding: 14, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)" },
  metricValue: { fontSize: 26, fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)", lineHeight: 1.1 },
  metricLabel: { fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px", marginTop: 6 },
  toolbar: { display: "flex", gap: 10, marginBottom: 12, alignItems: "center", flexWrap: "wrap" },
  search: { flex: 1, minWidth: 200, padding: "8px 11px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 12.5 },
  tableWrap: { border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", overflow: "hidden", background: "var(--bg-surface)" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 12.5 },
  th: { textAlign: "left", padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)", color: "var(--text-muted)", fontSize: 10, textTransform: "uppercase", letterSpacing: ".5px", fontWeight: 600 },
  td: { padding: "12px", borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)", verticalAlign: "top" },
  trLast: { borderBottom: "none" },
  tenantName: { fontWeight: 650, color: "var(--text-primary)" },
  tenantSlug: { fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" },
  statusBadge: { display: "inline-flex", alignItems: "center", gap: 5, padding: "3px 8px", borderRadius: 999, fontSize: 10.5, fontWeight: 600, textTransform: "uppercase", border: "1px solid transparent" },
  actions: { display: "flex", gap: 8, flexWrap: "wrap" },
  button: { padding: "7px 11px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 11.5 },
  buttonPrimary: { padding: "7px 11px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 700, fontSize: 11.5 },
  buttonDanger: { padding: "7px 11px", border: 0, borderRadius: "var(--r-sm)", background: "var(--vino)", color: "#1A1815", cursor: "pointer", fontWeight: 700, fontSize: 11.5 },
  empty: { padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" },
  error: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
  modalOverlay: { position: "fixed", inset: 0, background: "rgba(12,10,8,.66)", backdropFilter: "blur(4px)", display: "grid", placeItems: "center", zIndex: 90 },
  modal: { width: "min(460px, 92vw)", padding: 20, border: "1px solid var(--border-default)", borderRadius: "var(--r-lg)", background: "var(--bg-raised)", boxShadow: "var(--shadow)" },
  modalTitle: { margin: "0 0 6px", font: "italic 500 20px/1.2 var(--font-title)" },
  modalBody: { color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.55, marginBottom: 16 },
  modalActions: { display: "flex", gap: 10, justifyContent: "flex-end" },
};

const STATUS_STYLES = {
  pending: { background: "var(--amber-soft)", borderColor: "var(--amber-deep)", color: "var(--amber)" },
  active: { background: "var(--sage-soft)", borderColor: "var(--sage-deep)", color: "var(--sage)" },
  suspended: { background: "var(--vino-soft)", borderColor: "var(--vino-deep)", color: "var(--vino)" },
  provisioning: { background: "var(--slate-soft)", borderColor: "var(--slate)", color: "var(--slate)" },
};

async function apiGet(path) {
  const res = await fetch(path);
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

async function apiPost(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

function StatusBadge({ status }) {
  const label = { pending: "Pendiente", active: "Activo", suspended: "Suspendido", provisioning: "Provisioning" }[status] || status;
  const style = STATUS_STYLES[status] || STATUS_STYLES.pending;
  return <span style={{ ...ADMIN_S.statusBadge, ...style }}>{label}</span>;
}

function ConfirmModal({ title, body, onConfirm, onCancel, busy, confirmText, danger }) {
  return (
    <div style={ADMIN_S.modalOverlay} role="dialog" aria-modal="true">
      <div style={ADMIN_S.modal}>
        <h3 style={ADMIN_S.modalTitle}>{title}</h3>
        <div style={ADMIN_S.modalBody}>{body}</div>
        <div style={ADMIN_S.modalActions}>
          <button type="button" style={ADMIN_S.button} onClick={onCancel} disabled={busy}>Cancelar</button>
          <button type="button" style={danger ? ADMIN_S.buttonDanger : ADMIN_S.buttonPrimary} onClick={onConfirm} disabled={busy}>{busy ? "Procesando…" : confirmText}</button>
        </div>
      </div>
    </div>
  );
}

function TenantAdminPanel({ user }) {
  const isPlatformAdmin = user && (user.role === "platform_admin" || (user.roles || []).includes("platform_admin"));
  const [tenants, setTenants] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");
  const [confirm, setConfirm] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tData, mData] = await Promise.all([apiGet("/api/admin/tenants"), apiGet("/api/admin/tenants/metrics")]);
      setTenants(Array.isArray(tData) ? tData : (tData.tenants || []));
      setMetrics(mData || null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return tenants;
    return tenants.filter((t) => (t.name || "").toLowerCase().includes(q) || (t.slug || "").toLowerCase().includes(q) || (t.owner_email || "").toLowerCase().includes(q));
  }, [tenants, filter]);

  const doAction = async (tenant, action) => {
    setConfirm((c) => c && { ...c, busy: true });
    try {
      await apiPost(`/api/admin/tenants/${tenant.id}/${action}`, { reason: confirm && confirm.reason ? confirm.reason : undefined });
      await load();
      setConfirm(null);
    } catch (e) {
      setConfirm((c) => c && { ...c, busy: false, error: e.message });
    }
  };

  if (!isPlatformAdmin) {
    return <div style={{ padding: 24 }}><div style={ADMIN_S.error}>Esta vista requiere el rol platform_admin.</div></div>;
  }

  return (
    <div style={{ padding: "18px 20px", overflow: "auto" }}>
      <div style={ADMIN_S.header}>
        <div>
          <h2 style={ADMIN_S.title}>Administración de plataforma</h2>
          <div style={ADMIN_S.meta}>Tenants · métricas agregadas · sin acceso a contenido</div>
        </div>
        <button type="button" style={ADMIN_S.button} onClick={load} disabled={loading}><Icon name="refresh" size={16} /> Actualizar</button>
      </div>

      {error && <div style={ADMIN_S.error} role="alert"><Icon name="shield" size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />{error}</div>}

      {metrics && (
        <div style={ADMIN_S.grid}>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>{metrics.total_tenants ?? "-"}</div><div style={ADMIN_S.metricLabel}>Tenants</div></div>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>{metrics.total_users ?? "-"}</div><div style={ADMIN_S.metricLabel}>Usuarios agregados</div></div>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>${(metrics.total_cost_usd || 0).toFixed(2)}</div><div style={ADMIN_S.metricLabel}>Costo agregado (USD)</div></div>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>{metrics.pending_approvals ?? 0}</div><div style={ADMIN_S.metricLabel}>Pendientes de aprobación</div></div>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>{metrics.healthy_tenants ?? "-"}</div><div style={ADMIN_S.metricLabel}>Tenants saludables</div></div>
          <div style={ADMIN_S.metricCard}><div style={ADMIN_S.metricValue}>{metrics.storage_usage_gb != null ? `${metrics.storage_usage_gb.toFixed(2)} GB` : "-"}</div><div style={ADMIN_S.metricLabel}>Almacenamiento agregado</div></div>
        </div>
      )}

      <div style={ADMIN_S.toolbar}>
        <input type="search" style={ADMIN_S.search} placeholder="Buscar por nombre, slug o email del owner…" value={filter} onChange={(e) => setFilter(e.target.value)} />
      </div>

      {loading && tenants.length === 0 ? <div style={ADMIN_S.empty}>Cargando tenants…</div> : (
        <div style={ADMIN_S.tableWrap}>
          <table style={ADMIN_S.table}>
            <thead><tr>
              <th style={ADMIN_S.th}>Tenant</th>
              <th style={ADMIN_S.th}>Plan</th>
              <th style={ADMIN_S.th}>Usuarios</th>
              <th style={ADMIN_S.th}>Estado</th>
              <th style={ADMIN_S.th}>Acciones</th>
            </tr></thead>
            <tbody>
              {filtered.length === 0 && <tr><td colSpan={5} style={ADMIN_S.td}><div style={ADMIN_S.empty}>No se encontraron tenants.</div></td></tr>}
              {filtered.map((t, idx) => (
                <tr key={t.id} style={idx === filtered.length - 1 ? ADMIN_S.trLast : {}}>
                  <td style={ADMIN_S.td}>
                    <div style={ADMIN_S.tenantName}>{t.name}</div>
                    <div style={ADMIN_S.tenantSlug}>{t.slug} · {t.owner_email || "sin owner"}</div>
                  </td>
                  <td style={ADMIN_S.td}>{t.plan_name || "-"}</td>
                  <td style={ADMIN_S.td}>{t.users_count ?? "-"}</td>
                  <td style={ADMIN_S.td}><StatusBadge status={t.status} /></td>
                  <td style={ADMIN_S.td}>
                    <div style={ADMIN_S.actions}>
                      {t.status === "pending" && <button type="button" style={ADMIN_S.buttonPrimary} onClick={() => setConfirm({ tenant: t, action: "approve", title: "Aprobar tenant", body: `¿Aprobás a ${t.name} (${t.slug})? Esto dispara el seed de roles y workspace inicial.`, confirmText: "Aprobar", danger: false })}><Icon name="check" size={14} /> Aprobar</button>}
                      {t.status === "active" && <button type="button" style={ADMIN_S.buttonDanger} onClick={() => setConfirm({ tenant: t, action: "suspend", title: "Suspender tenant", body: `¿Suspendés a ${t.name} (${t.slug})? Sus usuarios no podrán operar hasta nueva aprobación.`, confirmText: "Suspender", danger: true })}><Icon name="x" size={14} /> Suspender</button>}
                      {t.status === "suspended" && <button type="button" style={ADMIN_S.buttonPrimary} onClick={() => setConfirm({ tenant: t, action: "approve", title: "Reactivar tenant", body: `¿Reactivás a ${t.name} (${t.slug})?`, confirmText: "Reactivar", danger: false })}><Icon name="refresh" size={14} /> Reactivar</button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {confirm && (
        <ConfirmModal
          title={confirm.title}
          body={confirm.body}
          confirmText={confirm.confirmText}
          danger={confirm.danger}
          busy={confirm.busy}
          onCancel={() => setConfirm(null)}
          onConfirm={() => doAction(confirm.tenant, confirm.action)}
        />
      )}
    </div>
  );
}

window.TenantAdminPanel = TenantAdminPanel;
