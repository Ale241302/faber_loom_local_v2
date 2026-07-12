/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Routing Shadow Report (E4-2)
   Comparativo shadow vs natural por tenant.
   ═══════════════════════════════════════════════════════════════ */

var { useEffect, useState } = React;

const S = {
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, gap: 12, flexWrap: "wrap" },
  title: { margin: 0, font: "italic 500 22px/1.2 var(--font-title)" },
  meta: { color: "var(--text-muted)", fontSize: 12, fontFamily: "var(--font-mono)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 16 },
  tile: { padding: 14, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)" },
  tileLabel: { fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: 6 },
  tileValue: { fontSize: 24, fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)" },
  tileSub: { fontSize: 11, color: "var(--text-muted)", marginTop: 4 },
  card: { padding: 14, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)", marginBottom: 12 },
  cardTitle: { fontWeight: 650, marginBottom: 10, color: "var(--text-primary)", fontSize: 14 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 12 },
  th: { textAlign: "left", padding: "8px 10px", borderBottom: "1px solid var(--border-default)", color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", fontSize: 10 },
  td: { padding: "8px 10px", borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" },
  empty: { padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" },
  error: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
};

async function apiGet(path) {
  const res = await fetch(path, { credentials: "same-origin" });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

function formatUSD(n) {
  return "$" + Number(n || 0).toFixed(4);
}

function ShadowReportPanel({ tenantId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!tenantId) return;
    setLoading(true);
    setError(null);
    apiGet(`/api/tenants/${tenantId}/routing/shadow-report?days=14`)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [tenantId]);

  if (loading) return <div style={S.empty}>Cargando reporte de routing…</div>;
  if (error) return <div style={S.error}>{error}</div>;
  if (!data) return null;

  const shadowCount = data.decisions_count.shadow || 0;
  const naturalCount = data.decisions_count.natural || 0;
  const shadowCost = data.cost_by_mode.shadow || { estimated_cost_usd: 0, actual_cost_usd: 0 };
  const naturalCost = data.cost_by_mode.natural || { estimated_cost_usd: 0, actual_cost_usd: 0 };
  const savings = shadowCost.actual_cost_usd - shadowCost.estimated_cost_usd;

  return (
    <div style={{ padding: "16px 20px", overflow: "auto" }}>
      <div style={S.header}>
        <h2 style={S.title}>Routing en sombra</h2>
        <span style={S.meta}>Tenant: {tenantId}</span>
      </div>

      <div style={S.grid}>
        <div style={S.tile}>
          <div style={S.tileLabel}>Decisiones shadow</div>
          <div style={S.tileValue}>{shadowCount}</div>
          <div style={S.tileSub}>últimos 14 días</div>
        </div>
        <div style={S.tile}>
          <div style={S.tileLabel}>Decisiones natural</div>
          <div style={S.tileValue}>{naturalCount}</div>
          <div style={S.tileSub}>últimos 14 días</div>
        </div>
        <div style={S.tile}>
          <div style={S.tileLabel}>Ahorro proyectado</div>
          <div style={S.tileValue}>{formatUSD(savings)}</div>
          <div style={S.tileSub}>actual - estimado shadow</div>
        </div>
        <div style={S.tile}>
          <div style={S.tileLabel}>Costo natural real</div>
          <div style={S.tileValue}>{formatUSD(naturalCost.actual_cost_usd)}</div>
          <div style={S.tileSub}>estimado {formatUSD(naturalCost.estimated_cost_usd)}</div>
        </div>
        <div style={S.tile}>
          <div style={S.tileLabel}>Alineación humana</div>
          <div style={S.tileValue}>{(data.human_alignment_score || 0).toFixed(1)}%</div>
          <div style={S.tileSub}>decisiones curadas aceptadas</div>
        </div>
        <div style={S.tile}>
          <div style={S.tileLabel}>Oscilaciones</div>
          <div style={S.tileValue}>{data.oscillation_count || 0}</div>
          <div style={S.tileSub}>workspaces con cambios de modo</div>
        </div>
      </div>

      <div style={S.card}>
        <div style={S.cardTitle}>Track record por modelo</div>
        {data.model_records.length === 0 ? (
          <div style={{ ...S.empty, padding: 20 }}>Sin datos de track record aún.</div>
        ) : (
          <table style={S.table}>
            <thead>
              <tr>
                <th style={S.th}>Capability</th>
                <th style={S.th}>Modelo</th>
                <th style={S.th}>Decisiones</th>
                <th style={S.th}>Aceptados</th>
                <th style={S.th}>Rechazados</th>
                <th style={S.th}>Costo avg</th>
              </tr>
            </thead>
            <tbody>
              {data.model_records.map((row) => (
                <tr key={`${row.capability}:${row.provider_slug}:${row.model}`}>
                  <td style={S.td}>{row.capability}</td>
                  <td style={S.td}>{row.provider_slug}/{row.model}</td>
                  <td style={S.td}>{row.total_decisions}</td>
                  <td style={S.td}>{row.accepted_count}</td>
                  <td style={S.td}>{row.rejected_count + row.regenerated_count}</td>
                  <td style={S.td}>{formatUSD(row.avg_cost_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.5 }}>
        El modo <strong>shadow</strong> planifica sin ejecutar. El reporte compara el costo
        estimado por el planner contra el costo real del camino manual/natural.
        La promoción a <strong>natural</strong> requiere aprobación del owner/curador.
      </div>
    </div>
  );
}
