/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Public Signup (E3-2)
   Pantalla pública de registro de tenant. No requiere autenticación.
   Usa cookie HttpOnly automática en requests same-origin (no localStorage).
   ═══════════════════════════════════════════════════════════════ */

var { useEffect, useMemo, useState } = React;

var SIGNUP_S = {
  shell: { minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, background: "var(--bg-canvas)", color: "var(--text-primary)", fontFamily: "var(--font-ui)" },
  card: { width: "min(520px, 100%)", padding: "28px 26px", border: "1px solid var(--border-default)", borderRadius: "var(--r-lg)", background: "var(--bg-raised)", boxShadow: "var(--shadow)" },
  mark: { color: "var(--coral)", marginBottom: 16 },
  title: { margin: "0 0 6px", font: "italic 500 28px/1.15 var(--font-title)" },
  tagline: { margin: "0 0 22px", color: "var(--text-muted)", fontSize: 13.5 },
  form: { display: "grid", gap: 14 },
  field: { display: "grid", gap: 6 },
  label: { fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".5px" },
  input: { width: "100%", padding: "10px 12px", border: "1px solid var(--border-default)", borderRadius: "var(--r-sm)", background: "var(--bg-sunken)", color: "var(--text-primary)", fontSize: 13, outline: "none", boxSizing: "border-box" },
  inputError: { borderColor: "var(--vino)" },
  hint: { fontSize: 11, color: "var(--text-muted)", marginTop: 2 },
  errorHint: { fontSize: 11, color: "var(--vino)", marginTop: 2 },
  passwordWrap: { position: "relative" },
  passwordToggle: { position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: 4 },
  button: { width: "100%", padding: "11px 14px", border: 0, borderRadius: "var(--r-sm)", background: "var(--coral)", color: "#1A1815", cursor: "pointer", fontWeight: 700, fontSize: 13, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 },
  buttonDisabled: { opacity: 0.6, cursor: "not-allowed" },
  errorBox: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--vino-soft)", border: "1px solid var(--vino-deep)", color: "var(--text-secondary)", marginBottom: 14, fontSize: 12.5, lineHeight: 1.5 },
  successBox: { padding: "11px 13px", borderRadius: "var(--r-sm)", background: "var(--sage-soft)", border: "1px solid var(--sage-deep)", color: "var(--text-secondary)", marginBottom: 14, fontSize: 12.5, lineHeight: 1.5 },
  footer: { marginTop: 20, textAlign: "center", fontSize: 12, color: "var(--text-muted)" },
  footerLink: { color: "var(--coral)", textDecoration: "none" },
};

var SLUG_RE = /^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$/;
var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function slugify(name) {
  return name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
}

function validate(form) {
  const errs = {};
  const name = (form.name || "").trim();
  if (name.length < 2) errs.name = "El nombre debe tener al menos 2 caracteres.";
  const slug = (form.slug || "").trim().toLowerCase();
  if (!SLUG_RE.test(slug)) errs.slug = "Slug inválido: 3-40 caracteres, minúsculas, dígitos y guiones.";
  const email = (form.email || "").trim();
  if (!EMAIL_RE.test(email)) errs.email = "Ingresa un correo electrónico válido.";
  if ((form.password || "").length < 12) errs.password = "La passphrase debe tener al menos 12 caracteres.";
  if (form.password !== form.passwordConfirm) errs.passwordConfirm = "Las passphrases no coinciden.";
  return errs;
}

async function apiPost(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const text = await res.text().catch(() => "");
  let json = null;
  try { json = JSON.parse(text); } catch { /* ignore */ }
  if (!res.ok) {
    const detail = json && json.detail ? json.detail : (text || res.statusText);
    throw new Error(`HTTP ${res.status}: ${detail}`);
  }
  return json;
}

function SignupPage() {
  const [form, setForm] = useState({ name: "", slug: "", email: "", password: "", passwordConfirm: "" });
  const [touched, setTouched] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const name = form.name;
    const derived = name ? slugify(name) : "";
    if (derived && !touched.slug) setForm((f) => ({ ...f, slug: derived }));
  }, [form.name, touched.slug]);

  const errors = useMemo(() => validate(form), [form]);
  const isValid = Object.keys(errors).length === 0;
  const displayErrors = {};
  for (const key of Object.keys(errors)) {
    if (touched[key]) displayErrors[key] = errors[key];
  }

  const update = (key, value) => {
    setForm((f) => ({ ...f, [key]: value }));
    setTouched((t) => ({ ...t, [key]: true }));
    setError(null);
  };

  const submit = async (event) => {
    event.preventDefault();
    setTouched({ name: true, slug: true, email: true, password: true, passwordConfirm: true });
    if (!isValid) return;
    setBusy(true);
    setError(null);
    try {
      await apiPost("/api/public/signup", {
        company_name: form.name.trim(),
        slug: form.slug.trim().toLowerCase(),
        owner_email: form.email.trim(),
        owner_password: form.password,
      });
      setSuccess(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const inputStyle = (key) => ({ ...SIGNUP_S.input, ...(displayErrors[key] ? SIGNUP_S.inputError : {}) });

  return (
    <div style={SIGNUP_S.shell}>
      <div style={SIGNUP_S.card}>
        <div style={SIGNUP_S.mark}><Icon name="loom" size={36} /></div>
        <h1 style={SIGNUP_S.title}>Crear tu empresa en FaberLoom</h1>
        <p style={SIGNUP_S.tagline}>Registro con aprobación de plataforma. Sin tarjeta, sin spam.</p>

        {error && <div style={SIGNUP_S.errorBox} role="alert"><Icon name="shield" size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />{error}</div>}
        {success && <div style={SIGNUP_S.successBox} role="status"><Icon name="check" size={16} style={{ marginRight: 8, verticalAlign: "text-bottom" }} />Solicitud enviada. Revisá tu correo para verificar la dirección y esperá la aprobación del administrador de plataforma.</div>}

        {!success && (
          <form style={SIGNUP_S.form} onSubmit={submit} noValidate>
            <div style={SIGNUP_S.field}>
              <label style={SIGNUP_S.label} htmlFor="signup-name">Nombre de la empresa</label>
              <input id="signup-name" type="text" style={inputStyle("name")} value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="ACME S.A." autoFocus autoComplete="organization" />
              {displayErrors.name ? <div style={SIGNUP_S.errorHint}>{displayErrors.name}</div> : <div style={SIGNUP_S.hint}>Este nombre será visible para tu equipo.</div>}
            </div>

            <div style={SIGNUP_S.field}>
              <label style={SIGNUP_S.label} htmlFor="signup-slug">Slug único</label>
              <input id="signup-slug" type="text" style={inputStyle("slug")} value={form.slug} onChange={(e) => { setTouched((t) => ({ ...t, slug: true })); setForm((f) => ({ ...f, slug: e.target.value })); }} onBlur={() => setForm((f) => ({ ...f, slug: f.slug.toLowerCase().trim() }))} placeholder="acme-sa" autoComplete="off" />
              {displayErrors.slug ? <div style={SIGNUP_S.errorHint}>{displayErrors.slug}</div> : <div style={SIGNUP_S.hint}>Se usará en URLs y prefijos de almacenamiento.</div>}
            </div>

            <div style={SIGNUP_S.field}>
              <label style={SIGNUP_S.label} htmlFor="signup-email">Correo del owner</label>
              <input id="signup-email" type="email" style={inputStyle("email")} value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="tu@empresa.com" autoComplete="email" />
              {displayErrors.email && <div style={SIGNUP_S.errorHint}>{displayErrors.email}</div>}
            </div>

            <div style={SIGNUP_S.field}>
              <label style={SIGNUP_S.label} htmlFor="signup-password">Passphrase</label>
              <div style={SIGNUP_S.passwordWrap}>
                <input id="signup-password" type={showPassword ? "text" : "password"} style={inputStyle("password")} value={form.password} onChange={(e) => update("password", e.target.value)} placeholder="Mínimo 12 caracteres" autoComplete="new-password" />
                <button type="button" style={SIGNUP_S.passwordToggle} onClick={() => setShowPassword((v) => !v)} aria-label={showPassword ? "Ocultar" : "Mostrar"} tabIndex={-1}><Icon name={showPassword ? "eye-off" : "eye"} size={18} /></button>
              </div>
              {displayErrors.password ? <div style={SIGNUP_S.errorHint}>{displayErrors.password}</div> : <div style={SIGNUP_S.hint}>Argon2id en el backend. Nosotros no la almacenamos en texto.</div>}
            </div>

            <div style={SIGNUP_S.field}>
              <label style={SIGNUP_S.label} htmlFor="signup-password-confirm">Repetir passphrase</label>
              <div style={SIGNUP_S.passwordWrap}>
                <input id="signup-password-confirm" type={showConfirm ? "text" : "password"} style={inputStyle("passwordConfirm")} value={form.passwordConfirm} onChange={(e) => update("passwordConfirm", e.target.value)} placeholder="Repetí la passphrase" autoComplete="new-password" />
                <button type="button" style={SIGNUP_S.passwordToggle} onClick={() => setShowConfirm((v) => !v)} aria-label={showConfirm ? "Ocultar" : "Mostrar"} tabIndex={-1}><Icon name={showConfirm ? "eye-off" : "eye"} size={18} /></button>
              </div>
              {displayErrors.passwordConfirm && <div style={SIGNUP_S.errorHint}>{displayErrors.passwordConfirm}</div>}
            </div>

            <button type="submit" style={{ ...SIGNUP_S.button, ...((busy || !isValid) && !busy ? SIGNUP_S.buttonDisabled : {}) }} disabled={busy || !isValid}>
              {busy ? <><span className="login-spinner" aria-hidden="true" />Enviando solicitud…</> : <>Solicitar acceso<Icon name="arrow-up" size={16} /></>}
            </button>
          </form>
        )}

        <div style={SIGNUP_S.footer}>
          ¿Ya tenés cuenta? <a href="/" style={SIGNUP_S.footerLink}>Iniciar sesión</a>
        </div>
      </div>
    </div>
  );
}

// Auto-mount si existe el nodo #signup-root (entry point público signup.html).
if (document.getElementById("signup-root")) {
  ReactDOM.createRoot(document.getElementById("signup-root")).render(<SignupPage />);
}

window.SignupPage = SignupPage;
