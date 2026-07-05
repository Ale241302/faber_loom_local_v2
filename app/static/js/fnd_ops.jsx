/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Foundation OPS (M10 Clasificador, M13 Drafts HITL,
   M14 Outcome Ledger, M17 Memoria)
   React 18 UMD + babel-standalone. Sin imports/exports.
   Cada vista recibe props { api, me, refreshMe, tenant }.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  const { useState, useEffect, useMemo, useCallback } = React;
  const F = window.Foundation;
  const {
    FndPanel, FndBadge, FndTable, FndField, FndError, FndJson,
    inputStyle, buttonStyle, buttonPrimaryStyle, buttonDangerStyle,
  } = F.ui;

  const can = (me, perm) => {
    const perms = (me && me.permissions) || [];
    return perms.includes("*") || perms.includes(perm);
  };
  const meId = (me) => (me && (me.user_id || me.id)) || null;
  const fmtDate = (iso) => {
    if (!iso) return "—";
    try { return new Date(iso).toLocaleString(); } catch (e) { return iso; }
  };
  const fmtPct = (v) => (v === null || v === undefined ? "—" : `${(v * 100).toFixed(1)}%`);
  const parseDetail = (err) => {
    try { return JSON.parse(err.message); } catch (e) { return null; }
  };
  const smallBtn = Object.assign({}, buttonStyle, { padding: "5px 9px", fontSize: 11.5 });
  const smallPrimary = Object.assign({}, buttonPrimaryStyle, { padding: "5px 9px", fontSize: 11.5 });
  const smallDanger = Object.assign({}, buttonDangerStyle, { padding: "5px 9px", fontSize: 11.5 });
  const gridStyle = { display: "grid", gap: 14 };

  /* ═════════════════ M10 · Clasificador L1 ═════════════════ */

  const LABEL_TONE = { rfq: "ok", order: "ok", complaint: "warn", invoice: "muted", spam: "danger", other: "muted" };
  const ITEM_STATUS_TONE = { new: "warn", classified: "ok", dismissed: "muted" };

  function ClassifierView({ api, me }) {
    const [items, setItems] = useState([]);
    const [taxonomy, setTaxonomy] = useState([]);
    const [config, setConfig] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(null);
    const [form, setForm] = useState({ channel: "email", sender: "", subject: "", body: "" });
    const [cfgDraft, setCfgDraft] = useState(null);

    const load = useCallback(() => {
      Promise.all([api.get("/classifier/inbound"), api.get("/classifier/config")])
        .then(([inbound, cfg]) => {
          setItems(inbound.items || []);
          setTaxonomy(inbound.taxonomy || []);
          setConfig(cfg);
          setError(null);
        })
        .catch(setError)
        .finally(() => setLoading(false));
    }, [api]);

    useEffect(() => {
      load();
      const t = setInterval(load, 12000);
      return () => clearInterval(t);
    }, [load]);

    const registrar = () => {
      setBusy("create");
      api.post("/classifier/inbound", form)
        .then(() => { setForm({ channel: "email", sender: "", subject: "", body: "" }); load(); })
        .catch(setError)
        .finally(() => setBusy(null));
    };
    const clasificar = (id) => {
      setBusy(id);
      api.post(`/classifier/inbound/${id}/classify`).then(load).catch(setError).finally(() => setBusy(null));
    };
    const override = (id, label) => {
      if (!label) return;
      setBusy(id);
      api.post(`/classifier/inbound/${id}/override`, { label }).then(load).catch(setError).finally(() => setBusy(null));
    };
    const descartar = (id) => {
      setBusy(id);
      api.post(`/classifier/inbound/${id}/dismiss`).then(load).catch(setError).finally(() => setBusy(null));
    };
    const guardarConfig = () => {
      let rules;
      try { rules = JSON.parse(cfgDraft.rulesText); }
      catch (e) { setError(new Error("Reglas: JSON inválido — " + e.message)); return; }
      setBusy("config");
      api.put("/classifier/config", { threshold: Number(cfgDraft.threshold), rules })
        .then((cfg) => { setConfig(cfg); setCfgDraft(null); setError(null); })
        .catch(setError)
        .finally(() => setBusy(null));
    };

    const columns = [
      { key: "received_at", label: "Recibido", render: (r) => fmtDate(r.received_at) },
      { key: "channel", label: "Canal" },
      { key: "sender", label: "Remitente" },
      { key: "subject", label: "Asunto", render: (r) => r.subject || "(sin asunto)" },
      { key: "status", label: "Estado", render: (r) => <FndBadge tone={ITEM_STATUS_TONE[r.status]}>{r.status}</FndBadge> },
      {
        key: "label", label: "Clasificación", render: (r) => r.classification ? (
          <span style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
            <FndBadge tone={LABEL_TONE[r.classification.label] || "muted"}>{r.classification.label}</FndBadge>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>
              {(r.classification.confidence * 100).toFixed(0)}% · {r.classification.decided_by}
            </span>
          </span>
        ) : "—",
      },
      {
        key: "actions", label: "Acciones", render: (r) => (
          <span style={{ display: "inline-flex", gap: 6, flexWrap: "wrap" }}>
            {can(me, "classifier.run") && r.status !== "dismissed" && (
              <button style={smallPrimary} disabled={busy === r.id} onClick={() => clasificar(r.id)}>Clasificar</button>
            )}
            {can(me, "classifier.run") && (
              <select style={Object.assign({}, inputStyle, { width: "auto", padding: "4px 6px", fontSize: 11.5 })}
                      value="" onChange={(e) => override(r.id, e.target.value)}>
                <option value="">Override…</option>
                {taxonomy.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            )}
            {can(me, "classifier.run") && r.status !== "dismissed" && (
              <button style={smallBtn} disabled={busy === r.id} onClick={() => descartar(r.id)}>Descartar</button>
            )}
          </span>
        ),
      },
    ];

    return (
      <div style={gridStyle}>
        <FndError error={error} />
        {can(me, "classifier.run") && (
          <FndPanel title="Registrar inbound de prueba" meta="POST /classifier/inbound">
            <div style={{ display: "grid", gridTemplateColumns: "140px 1fr 1fr", gap: 10, marginBottom: 10 }}>
              <FndField label="Canal">
                <select style={inputStyle} value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
                  <option value="email">email</option>
                  <option value="whatsapp">whatsapp</option>
                  <option value="manual">manual</option>
                </select>
              </FndField>
              <FndField label="Remitente">
                <input style={inputStyle} value={form.sender} onChange={(e) => setForm({ ...form, sender: e.target.value })} placeholder="cliente@empresa.com" />
              </FndField>
              <FndField label="Asunto">
                <input style={inputStyle} value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} placeholder="Solicitud de cotización" />
              </FndField>
            </div>
            <FndField label="Cuerpo">
              <textarea style={Object.assign({}, inputStyle, { minHeight: 70, resize: "vertical" })}
                        value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
            </FndField>
            <div style={{ marginTop: 10 }}>
              <button style={buttonPrimaryStyle} disabled={busy === "create"} onClick={registrar}>Registrar</button>
            </div>
          </FndPanel>
        )}

        <FndPanel title="Bandeja de entrada" meta={loading ? "Cargando…" : `${items.length} items · umbral ${config ? config.threshold : "—"}`}>
          <FndTable columns={columns} rows={items} empty="Sin items en la bandeja" />
        </FndPanel>

        {can(me, "classifier.manage") && config && (
          <FndPanel
            title="Configuración del clasificador"
            meta={`versión ${config.version || "1"} · reglas determinista (keywords/regex)`}
            actions={cfgDraft ? (
              <React.Fragment>
                <button style={smallBtn} onClick={() => setCfgDraft(null)}>Cancelar</button>
                <button style={smallPrimary} disabled={busy === "config"} onClick={guardarConfig}>Guardar</button>
              </React.Fragment>
            ) : (
              <button style={smallBtn} onClick={() => setCfgDraft({
                threshold: config.threshold,
                rulesText: JSON.stringify(config.rules, null, 2),
              })}>Editar</button>
            )}
          >
            {cfgDraft ? (
              <div style={{ display: "grid", gap: 10 }}>
                <FndField label={`Umbral de confianza (${cfgDraft.threshold})`}>
                  <input type="number" min="0" max="1" step="0.05" style={inputStyle}
                         value={cfgDraft.threshold}
                         onChange={(e) => setCfgDraft({ ...cfgDraft, threshold: e.target.value })} />
                </FndField>
                <FndField label="Reglas (JSON: [{label, weight, keywords, patterns}])">
                  <textarea style={Object.assign({}, inputStyle, { minHeight: 220, fontFamily: "var(--font-mono)", resize: "vertical" })}
                            value={cfgDraft.rulesText}
                            onChange={(e) => setCfgDraft({ ...cfgDraft, rulesText: e.target.value })} />
                </FndField>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                  Umbral: <b>{config.threshold}</b> · Taxonomía: {(config.taxonomy || taxonomy).join(", ")}
                </div>
                <FndJson value={config.rules} />
              </div>
            )}
          </FndPanel>
        )}
      </div>
    );
  }

  /* ═════════════════ M13 · Drafts HITL ═════════════════ */

  const DRAFT_TABS = [
    { id: "draft", label: "Borradores" },
    { id: "pending_review", label: "En revisión" },
    { id: "approved", label: "Aprobados" },
    { id: "sent", label: "Enviados" },
    { id: "rejected", label: "Rechazados" },
  ];
  const DRAFT_TONE = { draft: "muted", pending_review: "warn", approved: "ok", sent: "ok", rejected: "danger", failed: "danger" };

  function DraftsView({ api, me }) {
    const [tab, setTab] = useState("pending_review");
    const [drafts, setDrafts] = useState([]);
    const [selected, setSelected] = useState(null); // detalle con revisiones
    const [edit, setEdit] = useState(null);         // {subject, body}
    const [rejectNote, setRejectNote] = useState("");
    const [policyInfo, setPolicyInfo] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [showNew, setShowNew] = useState(false);
    const [nuevo, setNuevo] = useState({ channel: "email", recipient: "", subject: "", body: "" });

    const load = useCallback(() => {
      api.get(`/drafts?status=${tab}`)
        .then((data) => { setDrafts(data.drafts || []); setError(null); })
        .catch(setError);
    }, [api, tab]);

    useEffect(() => {
      load();
      const t = setInterval(load, 12000);
      return () => clearInterval(t);
    }, [load]);

    const openDetail = (row) => {
      setPolicyInfo(null); setRejectNote("");
      api.get(`/drafts/${row.id}`)
        .then((d) => { setSelected(d); setEdit({ subject: d.subject, body: d.body }); })
        .catch(setError);
    };
    const refreshDetail = (d) => {
      setSelected(d); setEdit({ subject: d.subject, body: d.body }); load();
    };
    const act = (fn) => {
      setBusy(true); setPolicyInfo(null);
      fn().finally(() => setBusy(false));
    };
    const guardar = () => act(() =>
      api.patch(`/drafts/${selected.id}`, edit).then(refreshDetail).catch(setError));
    const submit = () => act(() =>
      api.post(`/drafts/${selected.id}/submit`).then((d) => { refreshDetail(d); setTab("pending_review"); }).catch(setError));
    const approve = () => act(() =>
      api.post(`/drafts/${selected.id}/approve`).then((d) => { refreshDetail(d); setTab("approved"); }).catch(setError));
    const reject = () => act(() =>
      api.post(`/drafts/${selected.id}/reject`, { note: rejectNote }).then((d) => { refreshDetail(d); setTab("rejected"); }).catch(setError));
    const send = (overrideAck) => act(() =>
      api.post(`/drafts/${selected.id}/send`, overrideAck ? { override_ack: true } : {})
        .then((d) => { refreshDetail(d); setTab("sent"); })
        .catch((err) => {
          const detail = parseDetail(err);
          if (detail && (err.status === 409 || err.status === 422)) {
            setPolicyInfo(Object.assign({ status: err.status }, detail));
          } else { setError(err); }
        }));
    const crear = () => act(() =>
      api.post("/drafts", nuevo).then((d) => {
        setShowNew(false); setNuevo({ channel: "email", recipient: "", subject: "", body: "" });
        setTab("draft"); refreshDetail(Object.assign({ revisions: [] }, d));
      }).catch(setError));

    const editable = selected && ["draft", "pending_review"].includes(selected.status)
      && (can(me, "drafts.create") || can(me, "drafts.review"));
    const esCreador = selected && meId(me) && selected.created_by === meId(me);

    const columns = [
      { key: "updated_at", label: "Actualizado", render: (r) => fmtDate(r.updated_at) },
      { key: "channel", label: "Canal" },
      { key: "recipient", label: "Destinatario" },
      { key: "subject", label: "Asunto", render: (r) => r.subject || "(sin asunto)" },
      { key: "status", label: "Estado", render: (r) => <FndBadge tone={DRAFT_TONE[r.status]}>{r.status}</FndBadge> },
    ];

    return (
      <div style={gridStyle}>
        <FndError error={error} />
        <FndPanel
          title="Drafts HITL"
          meta="draft → pending_review → approved → sent (four-eyes + policy gate)"
          actions={can(me, "drafts.create") && (
            <button style={smallPrimary} onClick={() => setShowNew(!showNew)}>{showNew ? "Cerrar" : "Nuevo draft"}</button>
          )}
        >
          {showNew && (
            <div style={{ display: "grid", gap: 10, marginBottom: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 }}>
              <div style={{ display: "grid", gridTemplateColumns: "140px 1fr 1fr", gap: 10 }}>
                <FndField label="Canal">
                  <select style={inputStyle} value={nuevo.channel} onChange={(e) => setNuevo({ ...nuevo, channel: e.target.value })}>
                    <option value="email">email</option>
                    <option value="whatsapp">whatsapp</option>
                  </select>
                </FndField>
                <FndField label="Destinatario">
                  <input style={inputStyle} value={nuevo.recipient} onChange={(e) => setNuevo({ ...nuevo, recipient: e.target.value })} />
                </FndField>
                <FndField label="Asunto">
                  <input style={inputStyle} value={nuevo.subject} onChange={(e) => setNuevo({ ...nuevo, subject: e.target.value })} />
                </FndField>
              </div>
              <FndField label="Cuerpo">
                <textarea style={Object.assign({}, inputStyle, { minHeight: 80, resize: "vertical" })}
                          value={nuevo.body} onChange={(e) => setNuevo({ ...nuevo, body: e.target.value })} />
              </FndField>
              <div><button style={buttonPrimaryStyle} disabled={busy} onClick={crear}>Crear draft</button></div>
            </div>
          )}
          <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
            {DRAFT_TABS.map((t) => (
              <button key={t.id}
                      style={Object.assign({}, smallBtn, tab === t.id ? { background: "var(--coral)", color: "#1A1815", border: 0 } : {})}
                      onClick={() => setTab(t.id)}>
                {t.label}
              </button>
            ))}
          </div>
          <FndTable columns={columns} rows={drafts} empty="Sin drafts en este estado" onRowClick={openDetail} />
        </FndPanel>

        {selected && (
          <FndPanel
            title={`Draft ${selected.id}`}
            meta={`creado por ${selected.created_by} · ${fmtDate(selected.created_at)}${selected.reviewed_by ? ` · revisado por ${selected.reviewed_by}` : ""}`}
            actions={<button style={smallBtn} onClick={() => { setSelected(null); setPolicyInfo(null); }}>Cerrar</button>}
          >
            <div style={{ display: "grid", gap: 10 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <FndBadge tone={DRAFT_TONE[selected.status]}>{selected.status}</FndBadge>
                <span style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                  {selected.channel} → {selected.recipient || "(sin destinatario)"}
                </span>
                {selected.sent_at && <span style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>enviado {fmtDate(selected.sent_at)}</span>}
              </div>

              {selected.review_note && (
                <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
                  Nota de revisión: <i>{selected.review_note}</i>
                </div>
              )}

              <FndField label="Asunto">
                <input style={inputStyle} value={edit.subject} disabled={!editable}
                       onChange={(e) => setEdit({ ...edit, subject: e.target.value })} />
              </FndField>
              <FndField label="Cuerpo">
                <textarea style={Object.assign({}, inputStyle, { minHeight: 120, resize: "vertical" })}
                          value={edit.body} disabled={!editable}
                          onChange={(e) => setEdit({ ...edit, body: e.target.value })} />
              </FndField>

              {policyInfo && (
                <div style={{ padding: "10px 13px", borderRadius: 8, border: "1px solid var(--coral)", background: "var(--coral-soft)", fontSize: 12.5 }}>
                  <b>Policy gate: {policyInfo.decision}</b>
                  {policyInfo.policy_id && <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}> · {policyInfo.policy_id}</span>}
                  <ul style={{ margin: "6px 0 0 18px" }}>
                    {(policyInfo.reasons || []).map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                  {policyInfo.status === 409 && can(me, "drafts.send") && (
                    <button style={Object.assign({}, smallDanger, { marginTop: 8 })} disabled={busy}
                            onClick={() => send(true)}>
                      Confirmar envío bajo mi responsabilidad (override)
                    </button>
                  )}
                </div>
              )}

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {editable && (
                  <button style={buttonStyle} disabled={busy} onClick={guardar}>Guardar cambios (revisión)</button>
                )}
                {selected.status === "draft" && can(me, "drafts.create") && (
                  <button style={buttonPrimaryStyle} disabled={busy} onClick={submit}>Enviar a revisión</button>
                )}
                {selected.status === "pending_review" && can(me, "drafts.review") && (
                  <button style={buttonPrimaryStyle} disabled={busy || esCreador} onClick={approve}
                          title={esCreador ? "Four-eyes: el creador no puede aprobar su propio draft" : ""}>
                    Aprobar
                  </button>
                )}
                {selected.status === "pending_review" && can(me, "drafts.review") && (
                  <span style={{ display: "inline-flex", gap: 6 }}>
                    <input style={Object.assign({}, inputStyle, { width: 200 })} placeholder="Motivo del rechazo"
                           value={rejectNote} onChange={(e) => setRejectNote(e.target.value)} />
                    <button style={buttonDangerStyle} disabled={busy} onClick={reject}>Rechazar</button>
                  </span>
                )}
                {selected.status === "approved" && can(me, "drafts.send") && (
                  <button style={buttonPrimaryStyle} disabled={busy} onClick={() => send(false)}>Enviar</button>
                )}
              </div>
              {selected.status === "pending_review" && esCreador && (
                <div style={{ fontSize: 11.5, color: "var(--text-muted)" }}>
                  Regla four-eyes: otro usuario con permiso de revisión debe aprobar este draft.
                </div>
              )}

              {selected.policy_decision && Object.keys(selected.policy_decision).length > 0 && (
                <FndField label="Última decisión del policy gate">
                  <FndJson value={selected.policy_decision} />
                </FndField>
              )}

              <FndField label={`Historial de revisiones (${(selected.revisions || []).length})`}>
                {(selected.revisions || []).length === 0 ? (
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Sin ediciones registradas</div>
                ) : (
                  <FndTable
                    columns={[
                      { key: "created_at", label: "Fecha", render: (r) => fmtDate(r.created_at) },
                      { key: "edited_by", label: "Editado por" },
                      { key: "subject", label: "Asunto anterior" },
                      { key: "body", label: "Cuerpo anterior", render: (r) => <span style={{ fontSize: 11.5 }}>{(r.body || "").slice(0, 120)}{(r.body || "").length > 120 ? "…" : ""}</span> },
                    ]}
                    rows={selected.revisions}
                  />
                )}
              </FndField>
            </div>
          </FndPanel>
        )}
      </div>
    );
  }

  /* ═════════════════ M14 · Outcome Ledger ═════════════════ */

  const OUTCOME_TONE = { accepted: "ok", won: "ok", edited: "warn", neutral: "muted", rejected: "danger", lost: "danger" };
  const KINDS = ["draft", "classification", "task"];
  const OUTCOMES = ["accepted", "edited", "rejected", "won", "lost", "neutral"];

  function StatCard({ label, value }) {
    return (
      <div style={{ padding: "12px 14px", border: "1px solid var(--border-subtle)", borderRadius: "var(--r-md)", background: "var(--bg-surface)", minWidth: 130 }}>
        <div style={{ fontSize: 10.5, textTransform: "uppercase", letterSpacing: ".5px", color: "var(--text-muted)", fontWeight: 600 }}>{label}</div>
        <div style={{ fontSize: 22, fontWeight: 700, marginTop: 4 }}>{value}</div>
      </div>
    );
  }

  function OutcomesView({ api, me }) {
    const [stats, setStats] = useState(null);
    const [insights, setInsights] = useState(null);
    const [rows, setRows] = useState([]);
    const [filters, setFilters] = useState({ kind: "", outcome: "" });
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [form, setForm] = useState({ kind: "draft", ref_id: "", outcome: "accepted", score: "", feedback: "" });

    const load = useCallback(() => {
      const qs = [];
      if (filters.kind) qs.push(`kind=${filters.kind}`);
      if (filters.outcome) qs.push(`outcome=${filters.outcome}`);
      Promise.all([
        api.get("/outcomes/stats"),
        api.get("/outcomes/insights"),
        api.get(`/outcomes${qs.length ? "?" + qs.join("&") : ""}`),
      ])
        .then(([s, i, o]) => { setStats(s); setInsights(i); setRows(o.outcomes || []); setError(null); })
        .catch(setError);
    }, [api, filters]);

    useEffect(() => {
      load();
      const t = setInterval(load, 15000);
      return () => clearInterval(t);
    }, [load]);

    const registrar = () => {
      setBusy(true);
      const body = {
        kind: form.kind, ref_id: form.ref_id, outcome: form.outcome,
        feedback: form.feedback,
      };
      if (form.score !== "") body.score = Number(form.score);
      api.post("/outcomes", body)
        .then(() => { setForm({ kind: "draft", ref_id: "", outcome: "accepted", score: "", feedback: "" }); load(); })
        .catch(setError)
        .finally(() => setBusy(false));
    };

    const rates = (stats && stats.rates) || {};
    const selectSmall = Object.assign({}, inputStyle, { width: "auto" });

    return (
      <div style={gridStyle}>
        <FndError error={error} />
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <StatCard label="Total outcomes" value={stats ? stats.total : "—"} />
          <StatCard label="Aceptación drafts" value={fmtPct(rates.draft_acceptance_rate)} />
          <StatCard label="Tasa de edición" value={fmtPct(rates.draft_edit_rate)} />
          <StatCard label="Rechazo drafts" value={fmtPct(rates.draft_rejection_rate)} />
          <StatCard label="Score promedio" value={stats && stats.avg_score !== null && stats.avg_score !== undefined ? stats.avg_score.toFixed(2) : "—"} />
        </div>

        {insights && (insights.signals || []).length > 0 && (
          <FndPanel title="Señales de aprendizaje" meta="derivadas del ledger (motivos de rechazo + tendencia semanal)">
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12.5, color: "var(--text-secondary)", display: "grid", gap: 4 }}>
              {insights.signals.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
            {(insights.top_rejection_reasons || []).length > 0 && (
              <div style={{ marginTop: 10 }}>
                <FndTable
                  columns={[
                    { key: "reason", label: "Motivo de rechazo" },
                    { key: "count", label: "Veces" },
                  ]}
                  rows={insights.top_rejection_reasons.map((r, i) => Object.assign({ id: i }, r))}
                />
              </div>
            )}
          </FndPanel>
        )}

        {can(me, "outcomes.write") && (
          <FndPanel title="Registrar outcome manual" meta="ledger append-only (sin update/delete)">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 100px", gap: 10, marginBottom: 10 }}>
              <FndField label="Kind">
                <select style={inputStyle} value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
                  {KINDS.map((k) => <option key={k} value={k}>{k}</option>)}
                </select>
              </FndField>
              <FndField label="Referencia (ref_id)">
                <input style={inputStyle} value={form.ref_id} onChange={(e) => setForm({ ...form, ref_id: e.target.value })} placeholder="drf_… / cls_…" />
              </FndField>
              <FndField label="Outcome">
                <select style={inputStyle} value={form.outcome} onChange={(e) => setForm({ ...form, outcome: e.target.value })}>
                  {OUTCOMES.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
              </FndField>
              <FndField label="Score 0–1">
                <input type="number" min="0" max="1" step="0.1" style={inputStyle} value={form.score}
                       onChange={(e) => setForm({ ...form, score: e.target.value })} />
              </FndField>
            </div>
            <FndField label="Feedback">
              <input style={inputStyle} value={form.feedback} onChange={(e) => setForm({ ...form, feedback: e.target.value })} placeholder="p. ej. precio incorrecto" />
            </FndField>
            <div style={{ marginTop: 10 }}>
              <button style={buttonPrimaryStyle} disabled={busy} onClick={registrar}>Registrar</button>
            </div>
          </FndPanel>
        )}

        <FndPanel
          title="Ledger de outcomes"
          meta={`${rows.length} registros`}
          actions={
            <React.Fragment>
              <select style={selectSmall} value={filters.kind} onChange={(e) => setFilters({ ...filters, kind: e.target.value })}>
                <option value="">Todos los kinds</option>
                {KINDS.map((k) => <option key={k} value={k}>{k}</option>)}
              </select>
              <select style={selectSmall} value={filters.outcome} onChange={(e) => setFilters({ ...filters, outcome: e.target.value })}>
                <option value="">Todos los outcomes</option>
                {OUTCOMES.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </React.Fragment>
          }
        >
          <FndTable
            columns={[
              { key: "created_at", label: "Fecha", render: (r) => fmtDate(r.created_at) },
              { key: "kind", label: "Kind" },
              { key: "ref_id", label: "Ref", render: (r) => <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>{r.ref_id || "—"}</span> },
              { key: "outcome", label: "Outcome", render: (r) => <FndBadge tone={OUTCOME_TONE[r.outcome]}>{r.outcome}</FndBadge> },
              { key: "score", label: "Score", render: (r) => (r.score === null || r.score === undefined ? "—" : r.score.toFixed(2)) },
              { key: "feedback", label: "Feedback", render: (r) => r.feedback || "—" },
              { key: "actor_id", label: "Actor", render: (r) => <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>{r.actor_id}</span> },
            ]}
            rows={rows}
            empty="Sin outcomes registrados"
          />
        </FndPanel>
      </div>
    );
  }

  /* ═════════════════ M17 · Memoria ═════════════════ */

  const MEMORY_KINDS = ["fact", "preference", "instruction", "episode"];
  const KIND_TONE = { fact: "muted", preference: "ok", instruction: "warn", episode: "muted" };

  function MemoryView({ api, me }) {
    const [tree, setTree] = useState([]);
    const [blocks, setBlocks] = useState([]);
    const [nsFilter, setNsFilter] = useState("");
    const [q, setQ] = useState("");
    const [kind, setKind] = useState("");
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [showUpsert, setShowUpsert] = useState(false);
    const [upsert, setUpsert] = useState({ namespace: "", key: "", value: "", kind: "fact", importance: 0.5 });
    const [recallQuery, setRecallQuery] = useState("");
    const [recallResults, setRecallResults] = useState(null);

    const load = useCallback(() => {
      const qs = [];
      if (nsFilter) qs.push(`namespace=${encodeURIComponent(nsFilter)}`);
      if (kind) qs.push(`kind=${kind}`);
      if (q) qs.push(`q=${encodeURIComponent(q)}`);
      Promise.all([
        api.get("/memory/namespaces"),
        api.get(`/memory${qs.length ? "?" + qs.join("&") : ""}`),
      ])
        .then(([ns, bl]) => { setTree(ns.tree || []); setBlocks(bl.blocks || []); setError(null); })
        .catch(setError);
    }, [api, nsFilter, kind, q]);

    useEffect(() => {
      load();
      const t = setInterval(load, 20000);
      return () => clearInterval(t);
    }, [load]);

    const guardar = () => {
      if (!upsert.namespace || !upsert.key) { setError(new Error("Namespace y key son obligatorios")); return; }
      setBusy(true);
      api.put(`/memory/${upsert.namespace}/${upsert.key}`, {
        value: upsert.value, kind: upsert.kind, importance: Number(upsert.importance), source: "operator",
      })
        .then(() => { setShowUpsert(false); setUpsert({ namespace: nsFilter || "", key: "", value: "", kind: "fact", importance: 0.5 }); load(); })
        .catch(setError)
        .finally(() => setBusy(false));
    };
    const archivar = (b) => {
      setBusy(true);
      api.del(`/memory/${b.namespace}/${b.key}`).then(load).catch(setError).finally(() => setBusy(false));
    };
    const recall = () => {
      setBusy(true);
      api.post("/memory/recall", { namespace: nsFilter, query: recallQuery, limit: 10 })
        .then((r) => { setRecallResults(r.results || []); setError(null); })
        .catch(setError)
        .finally(() => setBusy(false));
    };

    return (
      <div style={gridStyle}>
        <FndError error={error} />
        <div style={{ display: "grid", gridTemplateColumns: "230px 1fr", gap: 14, alignItems: "start" }}>
          <FndPanel title="Namespaces" meta="tenant/agente/tarea">
            <div style={{ display: "grid", gap: 2, fontSize: 12.5 }}>
              <button style={Object.assign({}, smallBtn, { textAlign: "left" }, !nsFilter ? { background: "var(--coral)", color: "#1A1815", border: 0 } : {})}
                      onClick={() => setNsFilter("")}>
                (todos)
              </button>
              {tree.map((n) => (
                <button key={n.namespace}
                        style={Object.assign({}, smallBtn, { textAlign: "left", paddingLeft: 9 + (n.depth - 1) * 14 },
                          nsFilter === n.namespace ? { background: "var(--coral)", color: "#1A1815", border: 0 } : {})}
                        onClick={() => setNsFilter(n.namespace)}>
                  {n.namespace.split("/").pop()} <span style={{ opacity: 0.6, fontFamily: "var(--font-mono)", fontSize: 10.5 }}>({n.total})</span>
                </button>
              ))}
              {tree.length === 0 && <div style={{ color: "var(--text-muted)", padding: 6 }}>Sin memoria todavía</div>}
            </div>
          </FndPanel>

          <div style={gridStyle}>
            <FndPanel
              title={`Bloques de memoria${nsFilter ? ` · ${nsFilter}` : ""}`}
              meta={`${blocks.length} bloques activos`}
              actions={
                <React.Fragment>
                  <input style={Object.assign({}, inputStyle, { width: 160 })} placeholder="Buscar key/valor…"
                         value={q} onChange={(e) => setQ(e.target.value)} />
                  <select style={Object.assign({}, inputStyle, { width: "auto" })} value={kind} onChange={(e) => setKind(e.target.value)}>
                    <option value="">Todos</option>
                    {MEMORY_KINDS.map((k) => <option key={k} value={k}>{k}</option>)}
                  </select>
                  {can(me, "memory.write") && (
                    <button style={smallPrimary} onClick={() => {
                      setUpsert({ namespace: nsFilter || "", key: "", value: "", kind: "fact", importance: 0.5 });
                      setShowUpsert(!showUpsert);
                    }}>
                      {showUpsert ? "Cerrar" : "Nuevo / editar"}
                    </button>
                  )}
                </React.Fragment>
              }
            >
              {showUpsert && (
                <div style={{ display: "grid", gap: 10, marginBottom: 14, padding: 12, border: "1px dashed var(--border-default)", borderRadius: 8 }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 130px 110px", gap: 10 }}>
                    <FndField label="Namespace">
                      <input style={inputStyle} value={upsert.namespace} placeholder="tenant/agente/tarea"
                             onChange={(e) => setUpsert({ ...upsert, namespace: e.target.value })} />
                    </FndField>
                    <FndField label="Key">
                      <input style={inputStyle} value={upsert.key} placeholder="cliente_preferido"
                             onChange={(e) => setUpsert({ ...upsert, key: e.target.value })} />
                    </FndField>
                    <FndField label="Kind">
                      <select style={inputStyle} value={upsert.kind} onChange={(e) => setUpsert({ ...upsert, kind: e.target.value })}>
                        {MEMORY_KINDS.map((k) => <option key={k} value={k}>{k}</option>)}
                      </select>
                    </FndField>
                    <FndField label="Importancia">
                      <input type="number" min="0" max="1" step="0.1" style={inputStyle} value={upsert.importance}
                             onChange={(e) => setUpsert({ ...upsert, importance: e.target.value })} />
                    </FndField>
                  </div>
                  <FndField label="Valor">
                    <textarea style={Object.assign({}, inputStyle, { minHeight: 60, resize: "vertical" })}
                              value={upsert.value} onChange={(e) => setUpsert({ ...upsert, value: e.target.value })} />
                  </FndField>
                  <div><button style={buttonPrimaryStyle} disabled={busy} onClick={guardar}>Guardar (upsert)</button></div>
                </div>
              )}
              <FndTable
                columns={[
                  { key: "namespace", label: "Namespace", render: (r) => <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>{r.namespace}</span> },
                  { key: "key", label: "Key", render: (r) => <b>{r.key}</b> },
                  { key: "value", label: "Valor", render: (r) => <span style={{ fontSize: 12 }}>{(r.value || "").slice(0, 140)}{(r.value || "").length > 140 ? "…" : ""}</span> },
                  { key: "kind", label: "Kind", render: (r) => <FndBadge tone={KIND_TONE[r.kind]}>{r.kind}</FndBadge> },
                  { key: "importance", label: "Imp.", render: (r) => Number(r.importance).toFixed(1) },
                  { key: "updated_at", label: "Actualizado", render: (r) => fmtDate(r.updated_at) },
                  {
                    key: "actions", label: "", render: (r) => (
                      <span style={{ display: "inline-flex", gap: 6 }}>
                        {can(me, "memory.write") && (
                          <button style={smallBtn} onClick={() => {
                            setUpsert({ namespace: r.namespace, key: r.key, value: r.value, kind: r.kind, importance: r.importance });
                            setShowUpsert(true);
                          }}>Editar</button>
                        )}
                        {can(me, "memory.manage") && (
                          <button style={smallDanger} disabled={busy} onClick={() => archivar(r)}>Archivar</button>
                        )}
                      </span>
                    ),
                  },
                ]}
                rows={blocks}
                empty="Sin bloques en este namespace"
              />
            </FndPanel>

            <FndPanel title="Recall" meta="ranking: términos + importancia + recencia (sin embeddings)">
              <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                <input style={inputStyle} placeholder="¿Qué recuerda el sistema sobre…?"
                       value={recallQuery} onChange={(e) => setRecallQuery(e.target.value)}
                       onKeyDown={(e) => { if (e.key === "Enter") recall(); }} />
                <button style={buttonPrimaryStyle} disabled={busy || !recallQuery} onClick={recall}>Recall</button>
              </div>
              {recallResults !== null && (
                <FndTable
                  columns={[
                    { key: "score", label: "Score", render: (r) => <b style={{ fontFamily: "var(--font-mono)" }}>{r.score.toFixed(3)}</b> },
                    { key: "namespace", label: "Namespace", render: (r) => <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>{r.namespace}</span> },
                    { key: "key", label: "Key" },
                    { key: "value", label: "Valor", render: (r) => <span style={{ fontSize: 12 }}>{(r.value || "").slice(0, 160)}</span> },
                    { key: "matched_terms", label: "Términos", render: (r) => (r.matched_terms || []).join(", ") || "—" },
                  ]}
                  rows={recallResults}
                  empty="Sin coincidencias para esa consulta"
                />
              )}
            </FndPanel>
          </div>
        </div>
      </div>
    );
  }

  /* ═════════════════ Registro de vistas ═════════════════ */

  F.register({
    id: "m10-classifier", label: "Clasificador L1", icon: "filter",
    group: "Operación", order: 10, permission: "classifier.read",
    component: ClassifierView,
  });
  F.register({
    id: "m13-drafts", label: "Drafts HITL", icon: "edit",
    group: "Operación", order: 13, permission: "drafts.review",
    component: DraftsView,
  });
  F.register({
    id: "m14-outcomes", label: "Outcome Ledger", icon: "chart",
    group: "Operación", order: 14, permission: "outcomes.read",
    component: OutcomesView,
  });
  F.register({
    id: "m17-memory", label: "Memoria", icon: "database",
    group: "Operación", order: 17, permission: "memory.read",
    component: MemoryView,
  });
})();
