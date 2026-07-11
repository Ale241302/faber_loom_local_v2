const { useState, useEffect } = React;

function AgentTasksPanel({ workspaceId }) {
  const [tasks, setTasks] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiGet(`/api/workspaces/${workspaceId}/agent-tasks`);
      setTasks(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [workspaceId]);

  const kill = async (taskId) => {
    if (!window.confirm("¿Seguro que querés matar esta tarea?")) return;
    try {
      await apiPost(`/api/workspaces/${workspaceId}/agent-tasks/${taskId}/kill`, {});
      await load();
      if (selected && selected.id === taskId) {
        const refreshed = await apiGet(`/api/workspaces/${workspaceId}/agent-tasks/${taskId}`);
        setSelected(refreshed);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const openDetail = async (task) => {
    try {
      const data = await apiGet(`/api/workspaces/${workspaceId}/agent-tasks/${task.id}`);
      setSelected(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const statusClass = (status) => {
    switch (status) {
      case "completed": return "status-completed";
      case "running": return "status-running";
      case "paused_hitl": return "status-hitl";
      case "killed": return "status-killed";
      case "failed": return "status-killed";
      case "degraded": return "status-killed";
      default: return "";
    }
  };

  return <div className="panel agent-tasks-panel">
    <div className="stage-header">
      <div className="stage-title"><h2>Agent Tasks</h2><p>Tareas del agente vivo (E4-3).</p></div>
      <span className="pill"><Icon name="loom" size={16}/>E4-3</span>
    </div>
    {error && <div style={{ color: "var(--coral)", padding: 12 }}>{error}</div>}
    {loading && tasks.length === 0 && <div style={{ padding: 12 }}>Cargando…</div>}
    <div className="agent-tasks-layout">
      <div className="agent-tasks-list">
        {tasks.map((t) => (
          <div key={t.id} className={`agent-task-item ${selected && selected.id === t.id ? "active" : ""}`} onClick={() => openDetail(t)}>
            <div className="agent-task-meta">
              <span className={`agent-task-status ${statusClass(t.status)}`}>{t.status}</span>
              <span className="agent-task-cost">${(t.cost_total_usd || 0).toFixed(5)}</span>
            </div>
            <div className="agent-task-request">{t.user_request}</div>
            <div className="agent-task-id">{t.id}</div>
          </div>
        ))}
      </div>
      {selected && <div className="agent-task-detail">
        <h3>Detalle</h3>
        <div className="agent-task-detail-row"><strong>ID:</strong> {selected.id}</div>
        <div className="agent-task-detail-row"><strong>Estado:</strong> <span className={`agent-task-status ${statusClass(selected.status)}`}>{selected.status}</span></div>
        <div className="agent-task-detail-row"><strong>Solicitud:</strong> {selected.user_request}</div>
        <div className="agent-task-detail-row"><strong>Costo:</strong> ${(selected.cost_total_usd || 0).toFixed(5)} / {(selected.budget_cap_usd || 0).toFixed(2)}</div>
        {selected.output_text && <div className="agent-task-output">{selected.output_text}</div>}
        {selected.status === "running" && <button className="btn-danger" onClick={() => kill(selected.id)}>Mat tarea</button>}
        <h4>Pasos</h4>
        <div className="agent-task-steps">
          {(selected.steps || []).map((s) => (
            <div key={s.id} className={`agent-task-step ${s.status}`}>
              <span className="agent-step-index">{s.step_index}</span>
              <span className="agent-step-cap">{s.capability}</span>
              <span className={`agent-task-status ${statusClass(s.status)}`}>{s.status}</span>
              <span className="agent-step-model">{s.provider_slug}/{s.model}</span>
              <span className="agent-step-cost">${(s.cost_usd || 0).toFixed(5)}</span>
            </div>
          ))}
        </div>
      </div>}
    </div>
  </div>;
}

if (typeof window !== "undefined") {
  window.AgentTasksPanel = AgentTasksPanel;
}
