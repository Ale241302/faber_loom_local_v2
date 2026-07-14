// E5-1 — Fábrica de arquetipos (SPEC_FB_ARCHETYPE_FACTORY_v1).
//
// Un arquetipo es la plantilla reutilizable de "cómo se hace un tipo de
// trabajo". Es tenant-scoped y lo puebla el usuario: pueden ser N. Distinto del
// enum cerrado de architectural_archetype, que nombra otra cosa.
//
// Materializar un arquetipo crea una routine en el workspace activo. La copia es
// plana: editar el arquetipo después no toca las routines ya creadas.

var { useState, useEffect } = React;

const AR_CATEGORIES = ["skill", "agent", "template", "reference", "custom"];

const AR_EMPTY_FORM = {
  archetype_id: "",
  name: "",
  description: "",
  category: "skill",
  routing_preset_id: "",
  persona_md: "",
  skill_md: "---\nname: mi-arquetipo\npersona: Sos un asistente.\ntools: []\n---\nQué hace este tipo de trabajo.",
  tools_allowlist: "[]",
  schema_output_json: "{}",
  trigger_json: "{}",
  is_active: true,
};

const arStyles = {
  label: { display: "block", fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 10 },
  input: {
    width: "100%", padding: "8px 10px", marginTop: 4, borderRadius: 6,
    border: "1px solid var(--border)", background: "var(--bg-2)", color: "var(--text)",
    fontSize: 13, boxSizing: "border-box",
  },
  mono: { fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 12 },
  button: {
    padding: "7px 12px", borderRadius: 6, border: "1px solid var(--border)",
    background: "var(--bg-2)", color: "var(--text)", cursor: "pointer", fontSize: 12,
  },
  buttonPrimary: {
    padding: "7px 12px", borderRadius: 6, border: "none",
    background: "var(--accent, #d98b6a)", color: "#fff", cursor: "pointer",
    fontSize: 12, fontWeight: 600,
  },
  buttonDanger: {
    padding: "7px 12px", borderRadius: 6, border: "1px solid var(--coral, #e06c5a)",
    background: "transparent", color: "var(--coral, #e06c5a)", cursor: "pointer", fontSize: 12,
  },
  card: {
    padding: 12, borderRadius: 8, border: "1px solid var(--border)",
    background: "var(--bg-2)", marginBottom: 8,
  },
  badge: {
    display: "inline-block", padding: "1px 6px", borderRadius: 4,
    background: "var(--bg-3, rgba(255,255,255,0.06))", color: "var(--text-muted)",
    fontSize: 11, marginLeft: 6,
  },
  row: { display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" },
  error: { color: "var(--coral, #e06c5a)", padding: 10, fontSize: 13 },
  success: { color: "var(--green, #6aa87b)", padding: 10, fontSize: 13 },
  hint: { fontSize: 11, color: "var(--text-2, var(--text-muted))", marginTop: 4, fontWeight: 400 },
};

function ArchetypesPanel({ user, activeWorkspace }) {
  const [archetypes, setArchetypes] = useState([]);
  const [presets, setPresets] = useState([]);
  const [form, setForm] = useState(AR_EMPTY_FORM);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const tenantId = user?.tenant_id;

  const load = async () => {
    if (!tenantId) return;
    setLoading(true);
    try {
      const data = await apiGet(`/api/tenants/${tenantId}/archetypes`);
      setArchetypes(data.archetypes || []);
      try {
        const p = await apiGet(`/api/tenants/${tenantId}/presets`);
        setPresets(p.presets || []);
      } catch (_) {
        setPresets([]);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [tenantId]);

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const reset = () => {
    setForm(AR_EMPTY_FORM);
    setEditing(null);
  };

  const edit = (a) => {
    setEditing(a.archetype_id);
    setForm({
      archetype_id: a.archetype_id,
      name: a.name,
      description: a.description || "",
      category: a.category,
      routing_preset_id: a.routing_preset_id || "",
      persona_md: a.persona_md || "",
      skill_md: a.skill_md || "",
      tools_allowlist: a.tools_allowlist || "[]",
      schema_output_json: a.schema_output_json || "{}",
      trigger_json: a.trigger_json || "{}",
      is_active: !!a.is_active,
    });
    setSuccess(null);
    setError(null);
  };

  const save = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const body = {
        name: form.name,
        description: form.description || null,
        category: form.category,
        routing_preset_id: form.routing_preset_id || null,
        persona_md: form.persona_md,
        skill_md: form.skill_md,
        tools_allowlist: form.tools_allowlist,
        schema_output_json: form.schema_output_json,
        trigger_json: form.trigger_json,
        is_active: form.is_active,
      };
      if (editing) {
        await apiPatch(`/api/tenants/${tenantId}/archetypes/${editing}`, body);
        setSuccess(`Arquetipo "${editing}" actualizado.`);
      } else {
        await apiPost(`/api/tenants/${tenantId}/archetypes`, { ...body, archetype_id: form.archetype_id });
        setSuccess(`Arquetipo "${form.archetype_id}" creado.`);
      }
      reset();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (archetypeId) => {
    if (!window.confirm(`¿Eliminar el arquetipo "${archetypeId}"?\n\nLas routines ya creadas no se tocan: conservan su procedencia.`)) return;
    setError(null);
    try {
      await apiDelete(`/api/tenants/${tenantId}/archetypes/${archetypeId}`);
      setSuccess(`Arquetipo "${archetypeId}" eliminado.`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const materialize = async (archetypeId) => {
    if (!activeWorkspace) {
      setError("Elegí un workspace activo antes de materializar un arquetipo.");
      return;
    }
    const name = window.prompt(
      `Nombre de la routine a crear desde "${archetypeId}":`,
      archetypeId
    );
    if (!name) return;
    setError(null);
    setSuccess(null);
    try {
      const created = await apiPost(
        `/api/workspaces/${activeWorkspace.id}/routines/from-archetype/${archetypeId}`,
        { name }
      );
      setSuccess(
        `Routine "${created.name}" creada en ${activeWorkspace.name} desde "${archetypeId}". ` +
        `Es una copia: editar el arquetipo no la va a tocar.`
      );
    } catch (err) {
      setError(err.message);
    }
  };

  if (!tenantId) {
    return <section className="panel" aria-label="Arquetipos">
      <div style={arStyles.error}>Sin tenant activo.</div>
    </section>;
  }

  return <section className="panel" aria-label="Arquetipos">
    <div className="panel-header">
      <div className="panel-kicker">FÁBRICA</div>
      <div className="panel-title">Arquetipos</div>
      <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
        La plantilla reutilizable de cómo se hace un tipo de trabajo. Materializarla crea una routine en el workspace activo.
      </div>
    </div>
    <div style={{ padding: 16 }}>
      {loading && <div style={{ padding: 10 }}>Cargando arquetipos…</div>}
      {error && <div style={arStyles.error}>{error}</div>}
      {success && <div style={arStyles.success}>{success}</div>}

      <div style={{ opacity: loading ? 0.6 : 1 }}>
        <label style={arStyles.label}>
          ID (slug)
          {!editing
            ? <input style={arStyles.input} value={form.archetype_id}
                onChange={(e) => update("archetype_id", e.target.value)} placeholder="cotizacion-b2b"/>
            : <div style={{ ...arStyles.input, color: "var(--text-muted)" }}>{form.archetype_id}</div>}
        </label>
        <label style={arStyles.label}>
          Nombre
          <input style={arStyles.input} value={form.name}
            onChange={(e) => update("name", e.target.value)} placeholder="Cotización B2B"/>
        </label>
        <label style={arStyles.label}>
          Descripción
          <textarea style={arStyles.input} rows={2} value={form.description}
            onChange={(e) => update("description", e.target.value)} placeholder="Qué tipo de trabajo describe"/>
        </label>
        <label style={arStyles.label}>
          Categoría
          <select style={arStyles.input} value={form.category} onChange={(e) => update("category", e.target.value)}>
            {AR_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
        <label style={arStyles.label}>
          Preset de ruteo
          <select style={arStyles.input} value={form.routing_preset_id}
            onChange={(e) => update("routing_preset_id", e.target.value)}>
            <option value="">(sin preset — el router decide)</option>
            {presets.map((p) => <option key={p.preset_id} value={p.preset_id}>{p.name} ({p.preset_id})</option>)}
          </select>
          <div style={arStyles.hint}>
            La única faceta que se referencia en vez de copiarse. Borrar un preset referenciado va a fallar.
          </div>
        </label>
        <label style={arStyles.label}>
          Persona (voz)
          <textarea style={{ ...arStyles.input, ...arStyles.mono }} rows={2} value={form.persona_md}
            onChange={(e) => update("persona_md", e.target.value)}/>
        </label>
        <label style={arStyles.label}>
          SKILL.md
          <textarea style={{ ...arStyles.input, ...arStyles.mono }} rows={7} value={form.skill_md}
            onChange={(e) => update("skill_md", e.target.value)}/>
          <div style={arStyles.hint}>
            El <code>name:</code> del frontmatter se reescribe al materializar, para que un arquetipo se pueda instanciar N veces.
          </div>
        </label>
        <label style={arStyles.label}>
          Tools allowlist (JSON)
          <textarea style={{ ...arStyles.input, ...arStyles.mono }} rows={2} value={form.tools_allowlist}
            onChange={(e) => update("tools_allowlist", e.target.value)}/>
        </label>
        <label style={arStyles.label}>
          Schema de salida (JSON)
          <textarea style={{ ...arStyles.input, ...arStyles.mono }} rows={4} value={form.schema_output_json}
            onChange={(e) => update("schema_output_json", e.target.value)}/>
        </label>
        <label style={arStyles.label}>
          Trigger (JSON)
          <textarea style={{ ...arStyles.input, ...arStyles.mono }} rows={2} value={form.trigger_json}
            onChange={(e) => update("trigger_json", e.target.value)}/>
        </label>
        <div style={{ ...arStyles.label, display: "flex", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={!!form.is_active}
            onChange={(e) => update("is_active", e.target.checked)}/>
          Activo
        </div>
        <div style={arStyles.row}>
          <button type="button" style={arStyles.buttonPrimary} onClick={save}
            disabled={saving || (!editing && !form.archetype_id) || !form.name}>
            {saving ? "Guardando…" : (editing ? "Actualizar" : "Crear")}
          </button>
          {editing && <button type="button" style={arStyles.button} onClick={reset}>Cancelar</button>}
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 8 }}>
          ARQUETIPOS ({archetypes.length})
        </div>
        {archetypes.length === 0 && !loading && (
          <div style={{ fontSize: 13, color: "var(--text-muted)", padding: 10 }}>
            Todavía no hay arquetipos. El catálogo nace vacío a propósito: los define el humano, no la plataforma.
          </div>
        )}
        {archetypes.map((a) => <div key={a.archetype_id} style={arStyles.card}>
          <div style={{ fontSize: 14, fontWeight: 600 }}>
            {a.name}
            <span style={arStyles.badge}>{a.archetype_id}</span>
            <span style={arStyles.badge}>{a.category}</span>
            {!a.is_active && <span style={arStyles.badge}>inactivo</span>}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
            {a.description || "Sin descripción"} · v{a.version}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-2, var(--text-muted))", marginTop: 4 }}>
            routing: {a.routing_preset_id || "(sin preset)"}
          </div>
          <div style={arStyles.row}>
            <button style={arStyles.buttonPrimary} onClick={() => materialize(a.archetype_id)}>
              Crear routine
            </button>
            <button style={arStyles.button} onClick={() => edit(a)}>Editar</button>
            <button style={arStyles.buttonDanger} onClick={() => remove(a.archetype_id)}>Eliminar</button>
          </div>
        </div>)}
      </div>
    </div>
  </section>;
}

if (typeof window !== "undefined") {
  window.ArchetypesPanel = ArchetypesPanel;
}
