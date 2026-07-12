/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Promotion Readiness Panel (E3-4)
   Tablero de readiness para promover packs de skills a ACTIVE.
   ═══════════════════════════════════════════════════════════════ */

var { useCallback, useEffect, useState } = React;

var PR_S = {
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, gap: 12, flexWrap: "wrap" },
  title: { margin: 0, font: "italic 500 22px/1.2 var(--font-title)" },
  meta: { color: "var(--text-muted)", fontSize: 12, fontFamily: "var(--font-mono)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 12 },
  card: { padding: 14, border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)" },
  cardTitle: { fontWeight: 650, marginBottom: 4, lineHeight: 1.25, color: "var(--text-primary)", fontSize: 14 },
  cardMeta: { color: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)", marginBottom: 10 },
  row: { display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6, color: "var(--text-secondary)" },
  progressWrap: { height: 6, borderRadius: 3, background: "var(--bg-sunken)", overflow: "hidden", marginBottom: 10 },
  progressFill: (color) => ({ height: "100%", background: color, transition: "width .2s ease" }),
  blockers: { marginTop: 10, padding: 10, borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", fontSize: 12, lineHeight: 1.5 },
  blockerItem: { marginBottom: 4 },
  actions: { display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" },
  button: { padding: "7px 11px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-raised)", color: "var(--text-primary)", cursor: "pointer", fontWeight: 600, fontSize: 11.5 },
  buttonPrimary: { padding: "7px 11px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 700, fontSize: 11.5 },
  buttonDisabled: { padding: "7px 11px", border: 0, borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", color: "var(--text-muted)", cursor: "not-allowed", fontWeight: 700, fontSize: 11.5 },
  empty: { padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" },
  error: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
  success: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--sage-soft)", border: "1px solid var(--sage-deep)", color: "var(--text-secondary)", marginBottom: 12, fontSize: 12.5 },
  badge: { display: "inline-flex", alignItems: "center", gap: 5, padding: "2px 7px", borderRadius: 999, fontSize: 10, fontWeight: 600, textTransform: "uppercase", border: "1px solid transparent" },
};

var STATUS_COLORS = {
  active: "var(--sage)",
  shadow: "var(--amber)",
  draft: "var(--slate)",
  definition_pending: "var(--vino)",
  not_imported: "var(--text-muted)",
};

async function apiGet(path) {
  const res = await fetch(path, { credentials: "same-origin" });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

async function apiPost(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, credentials: "same-origin", body: JSON.stringify(body || {}) });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) throw new Error(json && json.detail ? json.detail : `HTTP ${res.status}`);
  return json;
}

async function sha256Truncated(text, length = 16) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, length);
}

function StatusBadge({ status }) {
  const s = String(status || "").toLowerCase();
  const label = { active: "Active", shadow: "Shadow", draft: "Draft", definition_pending: "Definition pending", not_imported: "No importado" }[s] || s;
  const color = STATUS_COLORS[s] || "var(--text-muted)";
  return <span style={{ ...PR_S.badge, borderColor: color, color: color }}>{label}</span>;
}

function ProgressBar({ value, max, color }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div style={PR_S.progressWrap}>
      <div style={{ ...PR_S.progressFill(color), width: pct + "%" }} />
    </div>
  );
}

function PackCard({ pack, workspaceId, onPromoted }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const handlePromote = async () => {
    setError(null);
    setBusy(true);
    try {
      const token = await sha256Truncated(pack.pack_id);
      await apiPost(`/api/workspaces/${workspaceId}/packs/${pack.pack_id}/promote`, { confirmation_token: token });
      onPromoted();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={PR_S.card}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
        <div>
          <div style={PR_S.cardTitle}>{pack.pack_id.replace(/_/g, " ")}</div>
          <div style={PR_S.cardMeta}>{pack.skill_count} skills · {pack.imported_count} importados</div>
        </div>
        <StatusBadge status={pack.status} />
      </div>

      <div style={PR_S.row}>
        <span>Golden cases</span>
        <span>{pack.golden_cases_approved} aprobados / {pack.golden_cases_verified} verificados / {pack.golden_cases_total} total</span>
      </div>
      <ProgressBar value={pack.golden_cases_verified} max={Math.max(pack.required_golden_cases, pack.golden_cases_total, 1)} color="var(--amber)" />

      <div style={PR_S.row}>
        <span>Track record</span>
        <span>{pack.track_records_meeting_threshold} cumplen umbral / {pack.track_records_total} importados</span>
      </div>
      <ProgressBar value={pack.track_records_meeting_threshold} max={Math.max(pack.track_records_total, 1)} color="var(--sage)" />

      <div style={{ ...PR_S.row, marginTop: 6, fontSize: 11, color: "var(--text-muted)" }}>
        <span>Umbrales</span>
        <span>≥ {pack.thresholds.runs_total} runs / ≥ {(pack.thresholds.acceptance_rate * 100).toFixed(0)}% acceptance</span>
      </div>

      {pack.blockers.length > 0 && (
        <div style={PR_S.blockers}>
          {pack.blockers.map((b, i) => <div key={i} style={PR_S.blockerItem}>• {b}</div>)}
        </div>
      )}

      {error && <div style={{ ...PR_S.error, marginTop: 10 }}>{error}</div>}

      <div style={PR_S.actions}>
        {pack.can_promote ? (
          <button type="button" style={PR_S.buttonPrimary} onClick={handlePromote} disabled={busy}>
            {busy ? "Promoviendo…" : "Promover a ACTIVE"}
          </button>
        ) : (
          <button type="button" style={PR_S.buttonDisabled} disabled>
            No listo para promover
          </button>
        )}
      </div>
    </div>
  );
}

function PromotionReadinessPanel({ activeWorkspace }) {
  const workspaceId = activeWorkspace?.id;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const load = useCallback(async () => {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiGet(`/api/workspaces/${workspaceId}/packs/readiness`);
      setData(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => { load(); }, [load]);

  const handlePromoted = () => {
    setSuccess("Pack promovido a ACTIVE. Recargando readiness…");
    load();
    setTimeout(() => setSuccess(null), 4000);
  };

  return (
    <div style={{ padding: "16px 20px", overflow: "auto" }}>
      <div style={PR_S.header}>
        <h2 style={PR_S.title}>Promoción de packs</h2>
        <span style={PR_S.meta}>Workspace: {workspaceId}</span>
      </div>

      {success && <div style={PR_S.success}>{success}</div>}
      {error && <div style={PR_S.error}>{error}</div>}

      {loading ? (
        <div style={PR_S.empty}>Cargando readiness…</div>
      ) : !data || !data.packs || data.packs.length === 0 ? (
        <div style={PR_S.empty}>No hay packs en el catálogo global.</div>
      ) : (
        <div style={PR_S.grid}>
          {data.packs.map((pack) => (
            <PackCard
              key={pack.pack_id}
              pack={pack}
              workspaceId={workspaceId}
              onPromoted={handlePromoted}
            />
          ))}
        </div>
      )}
    </div>
  );
}

window.PromotionReadinessPanel = PromotionReadinessPanel;
