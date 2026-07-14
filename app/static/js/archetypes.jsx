// E5-1 — Fábrica de arquetipos (SPEC_FB_ARCHETYPE_FACTORY_v1).
//
// Un arquetipo es la plantilla reutilizable de "cómo se hace un tipo de
// trabajo". Es tenant-scoped y lo puebla el usuario: pueden ser N. Distinto del
// enum cerrado de architectural_archetype, que nombra otra cosa.
//
// Estilos: usa el objeto global S de app.jsx. El objeto local se llama ARQ_S y
// NO S: app.jsx carga después y pisaría un `var S` local (es el bug que hoy deja
// a routing_shadow.jsx renderizando con style={undefined}).

var { useState, useEffect } = React;

const ARQ_CATEGORIES = ["skill", "agent", "template", "reference", "custom"];

const ARQ_EMPTY_FORM = {
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

const ARQ_S = {
  hint: {
    fontSize: 11,
    color: "var(--text-muted)",
    fontFamily: "var(--font-mono)",
    fontWeight: 400,
    textTransform: "none",
    letterSpacing: 0,
    lineHeight: 1.5,
  },
  sectionLabel: {
    fontSize: 10,
    fontFamily: "var(--font-mono)",
    textTransform: "uppercase",
    letterSpacing: ".7px",
    color: "var(--text-muted)",
    marginBottom: 8,
  },
  empty: {
    padding: 20,
    textAlign: "center",
    color: "var(--text-muted)",
    fontSize: 12.5,
    lineHeight: 1.6,
  },
};

function ArchetypesPanel({ user, activeWorkspace }) {
  const [archetypes, setArchetypes] = useState([]);
  const [presets, setPresets] = useState([]);
  const [form, setForm] = useState(ARQ_EMPTY_FORM);
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
    setForm(ARQ_EMPTY_FORM);
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
        await apiPost(`/api/tenants/${tenantId}/archetypes`, {
          ...body,
          archetype_id: form.archetype_id,
        });
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
    const name = window.prompt(`Nombre de la routine a crear desde "${archetypeId}":`, archetypeId);
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
    return <div className="classic" style={S.view}>
      <div style={S.error}>Sin tenant activo.</div>
    </div>;
  }

  return <div className="classic" style={S.view}>
    <div className="vhead">
      <div>
        <div className="vtitle">Arquetipos</div>
        <div className="vsub">
          La plantilla reutilizable de cómo se hace un tipo de trabajo. Materializarla crea una routine en el workspace activo.
        </div>
      </div>
    </div>

    {error && <div style={S.error}>{error}</div>}
    {success && <div style={S.success}>{success}</div>}

    <section className="panel" aria-label="Editor de arquetipo">
      <div className="panel-header">
        <div>
          <div className="panel-kicker">Fábrica</div>
          <div className="panel-title">{editing ? "Editar arquetipo" : "Nuevo arquetipo"}</div>
        </div>
        {editing && <span style={S.badge}>{editing}</span>}
      </div>
      <div style={S.panelBody}>
        {loading && <div style={S.loading}>Cargando arquetipos…</div>}
        <div style={{ ...S.form, opacity: loading ? 0.6 : 1 }}>
          <label style={S.label}>
            ID (slug)
            {!editing
              ? <input style={S.input} value={form.archetype_id}
                  onChange={(e) => update("archetype_id", e.target.value)} placeholder="cotizacion-b2b"/>
              : <div style={{ ...S.input, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{form.archetype_id}</div>}
          </label>

          <label style={S.label}>
            Nombre
            <input style={S.input} value={form.name}
              onChange={(e) => update("name", e.target.value)} placeholder="Cotización B2B"/>
          </label>

          <label style={S.label}>
            Descripción
            <textarea style={{ ...S.textarea, minHeight: 56 }} rows={2} value={form.description}
              onChange={(e) => update("description", e.target.value)} placeholder="Qué tipo de trabajo describe"/>
          </label>

          <div style={S.grid2}>
            <label style={S.label}>
              Categoría
              <select style={S.select} value={form.category} onChange={(e) => update("category", e.target.value)}>
                {ARQ_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </label>

            <label style={S.label}>
              Preset de ruteo
              <select style={S.select} value={form.routing_preset_id}
                onChange={(e) => update("routing_preset_id", e.target.value)}>
                <option value="">(sin preset — el router decide)</option>
                {presets.map((p) => <option key={p.preset_id} value={p.preset_id}>{p.name} · {p.preset_id}</option>)}
              </select>
            </label>
          </div>
          <div style={ARQ_S.hint}>
            El preset es la única faceta que se referencia en vez de copiarse. Borrar un preset referenciado falla.
          </div>

          <label style={S.label}>
            Persona (voz)
            <textarea style={{ ...S.textarea, minHeight: 56 }} rows={2} value={form.persona_md}
              onChange={(e) => update("persona_md", e.target.value)} placeholder="Sos un cotizador formal."/>
          </label>

          <label style={S.label}>
            SKILL.md
            <textarea style={{ ...S.monoTextarea, minHeight: 150 }} value={form.skill_md}
              onChange={(e) => update("skill_md", e.target.value)}/>
          </label>
          <div style={ARQ_S.hint}>
            El <code>name:</code> del frontmatter se reescribe al materializar, para que un arquetipo se pueda instanciar N veces.
          </div>

          <label style={S.label}>
            Tools allowlist (JSON)
            <textarea style={{ ...S.monoTextarea, minHeight: 56 }} rows={2} value={form.tools_allowlist}
              onChange={(e) => update("tools_allowlist", e.target.value)}/>
          </label>

          <label style={S.label}>
            Schema de salida (JSON)
            <textarea style={{ ...S.monoTextarea, minHeight: 90 }} value={form.schema_output_json}
              onChange={(e) => update("schema_output_json", e.target.value)}/>
          </label>

          <label style={S.label}>
            Trigger (JSON)
            <textarea style={{ ...S.monoTextarea, minHeight: 56 }} rows={2} value={form.trigger_json}
              onChange={(e) => update("trigger_json", e.target.value)}/>
          </label>

          <div style={{ ...S.label, display: "flex", alignItems: "center", gap: 8 }}>
            <Toggle checked={!!form.is_active} onChange={(checked) => update("is_active", checked)}/>
            Activo
          </div>

          <div style={S.inlineGroup}>
            <button type="button" style={S.buttonPrimary} onClick={save}
              disabled={saving || (!editing && !form.archetype_id) || !form.name}>
              {saving ? "Guardando…" : (editing ? "Actualizar" : "Crear")}
            </button>
            {editing && <button type="button" style={S.button} onClick={reset}>Cancelar</button>}
          </div>
        </div>
      </div>
    </section>

    <section className="panel" aria-label="Catálogo de arquetipos">
      <div className="panel-header">
        <div>
          <div className="panel-kicker">Catálogo</div>
          <div className="panel-title">Arquetipos ({archetypes.length})</div>
        </div>
      </div>
      <div style={S.panelBody}>
        {archetypes.length === 0 && !loading && (
          <div style={ARQ_S.empty}>
            Todavía no hay arquetipos.<br/>
            El catálogo nace vacío a propósito: los define el humano, no la plataforma.
          </div>
        )}
        {archetypes.map((a) => <div key={a.archetype_id} style={{ ...S.card, marginBottom: 8 }}>
          <div style={S.cardTitle}>
            {a.name}
            <span style={{ ...S.badge, marginLeft: 6 }}>{a.archetype_id}</span>
            <span style={{ ...S.badge, marginLeft: 6 }}>{a.category}</span>
            {!a.is_active && <span style={{ ...S.badge, marginLeft: 6 }}>inactivo</span>}
          </div>
          <div style={S.cardMeta}>
            {a.description || "Sin descripción"} · v{a.version} · routing: {a.routing_preset_id || "sin preset"}
          </div>
          <div style={S.inlineGroup}>
            <button style={S.buttonPrimary} onClick={() => materialize(a.archetype_id)}>Crear routine</button>
            <button style={S.button} onClick={() => edit(a)}>Editar</button>
            <button style={S.buttonDanger} onClick={() => remove(a.archetype_id)}>Eliminar</button>
          </div>
        </div>)}
      </div>
    </section>
  </div>;
}

if (typeof window !== "undefined") {
  window.ArchetypesPanel = ArchetypesPanel;
}
