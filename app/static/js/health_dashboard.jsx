/* FaberLoom · Health Dashboard (E3-6)
 *
 * Owner mirror view: fetches /api/tenants/{tenant_id}/health.
 * Platform admin can also inspect any tenant via /api/admin/tenants/{id}/health.
 */

var { useEffect, useState } = React;

const HS = {
  view: { padding: "18px 20px", overflow: "auto" },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18, gap: 12, flexWrap: "wrap" },
  title: { margin: 0, font: "italic 500 22px/1.2 var(--font-title)" },
  meta: { color: "var(--text-muted)", fontSize: 12, fontFamily: "var(--font-mono)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 16 },
  card: { padding: 14, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)" },
  value: { fontSize: 26, fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)", lineHeight: 1.1 },
  label: { fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px", marginTop: 6 },
  ok: { color: "var(--sage)" },
  warn: { color: "var(--coral)" },
  error: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
  button: { padding: "7px 11px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 11.5 },
  input: { padding: "7px 9px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 12, minWidth: 220 },
  row: { display: "flex", gap: 10, alignItems: "center", marginBottom: 12, flexWrap: "wrap" },
};

async function apiGet(path) {
  const res = await fetch(path, { credentials: "same-origin" });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

function isPlatformAdmin(user) {
  if (!user) return false;
  if (user.role === "platform_admin") return true;
  if (Array.isArray(user.roles) && user.roles.includes("platform_admin")) return true;
  return false;
}

function MetricCard({ label, value, warn }) {
  return (
    <div style={HS.card}>
      <div style={{ ...HS.value, ...(warn ? HS.warn : {}) }}>{value}</div>
      <div style={HS.label}>{label}</div>
    </div>
  );
}

function HealthDashboard({ user }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tenantInput, setTenantInput] = useState(user?.tenant_id || "");
  const [endpoint, setEndpoint] = useState("mirror");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const path = endpoint === "admin"
        ? `/api/admin/tenants/${tenantInput}/health`
        : `/api/tenants/${tenantInput}/health`;
      const health = await apiGet(path);
      setData(health);
    } catch (e) {
      setError(e.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [endpoint, tenantInput]);

  const admin = isPlatformAdmin(user);
  const plan = data?.plan || "-";
  const budgetRemaining = data?.budget_remaining_usd;

  return (
    <div style={HS.view}>
      <div style={HS.header}>
        <div>
          <h2 style={HS.title}>Salud del tenant</h2>
          <div style={HS.meta}>Agregados operativos · sin contenido de workspace</div>
        </div>
        <button type="button" style={HS.button} onClick={load} disabled={loading}>Actualizar</button>
      </div>

      {admin && (
        <div style={HS.row}>
          <select style={{ ...HS.input, width: "auto" }} value={endpoint} onChange={(e) => setEndpoint(e.target.value)}>
            <option value="mirror">Vista espejo (owner)</option>
            <option value="admin">Vista platform admin</option>
          </select>
          <input style={HS.input} value={tenantInput} onChange={(e) => setTenantInput(e.target.value)} placeholder="tenant_id" />
        </div>
      )}

      {error && <div style={HS.error} role="alert">{error}</div>}

      {data && (
        <>
          <div style={HS.grid}>
            <MetricCard label="Plan" value={plan} />
            <MetricCard label="Workspaces" value={data.workspaces} />
            <MetricCard label="Usuarios" value={data.users} />
            <MetricCard label="Runs 30d" value={data.runs_30d} />
            <MetricCard label="Exitosos 30d" value={data.successful_runs_30d} />
            <MetricCard label="Fallidos 30d" value={data.failed_runs_30d} warn={data.failed_runs_30d > 0} />
            <MetricCard label="Tasa de error" value={`${data.error_rate_pct}%`} warn={data.error_rate_pct > 5} />
            <MetricCard label="Costo 30d" value={`$${data.cost_usd_30d.toFixed(2)}`} />
            <MetricCard label="Presupuesto restante" value={budgetRemaining === null ? "∞" : `$${budgetRemaining.toFixed(2)}`} warn={budgetRemaining !== null && budgetRemaining < 0} />
            <MetricCard label="Facturas abiertas" value={data.invoices_open} />
            <MetricCard label="Facturas pagadas" value={data.invoices_paid} />
            <MetricCard label="Facturas vencidas" value={data.invoices_overdue} warn={data.invoices_overdue > 0} />
          </div>

          <div style={HS.card}>
            <div style={HS.label}>Ultimo login del owner</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 13, marginTop: 6 }}>
              {data.last_owner_login || "Sin sesiones owner registradas"}
            </div>
          </div>

          {data.agent && (
            <>
              <h3 style={{ ...HS.title, fontSize: 18, marginTop: 18, marginBottom: 12 }}>Agente Vivo</h3>
              <div style={HS.grid}>
                <MetricCard label="Briefs" value={`${data.agent.briefs_total} (${data.agent.briefs_fresh} fresh)`} warn={data.agent.briefs_stale > 0} />
                <MetricCard label="Tasks pendientes" value={data.agent.tasks_pending} />
                <MetricCard label="Tasks corriendo" value={data.agent.tasks_running} />
                <MetricCard label="Tasks pausadas" value={data.agent.tasks_paused} />
                <MetricCard label="Tasks completadas" value={data.agent.tasks_completed} />
                <MetricCard label="Tasks fallidas" value={data.agent.tasks_failed} warn={data.agent.tasks_failed > 0} />
                <MetricCard label="Memoria activa" value={data.agent.memory_blocks_active} />
                <MetricCard label="Memoria archivada" value={data.agent.memory_blocks_archived} />
                <MetricCard label="Costo agente 30d" value={`$${data.agent.cost_living_agent_30d.toFixed(2)}`} />
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

window.HealthDashboard = HealthDashboard;
