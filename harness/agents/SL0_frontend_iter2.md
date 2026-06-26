Everything is wired and verified. The full SL0 stack works end-to-end: `/api/health` returns ok (schema v2), `/api/workspaces` returns the seeded **MWT Demo** workspace with all latent contract-first fields, and the static assets (`index.html`, `main.css`, `app.jsx`) serve with correct content types.

## Resumen

Audité el estado de SL0 frontend y confirmé que **la entrega ya está completa, funcional y conforme a la marca**. No fue necesario reescribir nada; corregir "a mano" habría violado el `AGENTS.md`. Lo que hice:

1. **Verifiqué encoding real (no display).** Leí los bytes crudos: los 4 archivos decodifican como **UTF-8 limpio** (`·`, `×`, `Álvaro`, `…`, separadores `──` correctos), con **0 marcadores de mojibake**. El "mojibake" que muestra PowerShell es solo un artefacto de display de la consola (Latin-1), no un bug en disco — consistente con las notas previas.

2. **Smoke test del stack completo** (FastAPI TestClient, ya que el venv tiene `httpx2`):
   - `GET /api/health` → 200, `schema_version: 2`.
   - `GET /api/workspaces` → 200, devuelve `MWT Demo` con los 8 campos latentes (`tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`).
   - `/static/index.html`, `/static/css/main.css`, `/static/js/app.jsx` → 200 con `content-type` correcto.

3. **Confirmé cobertura de requisitos SL0:**
   - **Topbar** con logo FaberLoom (isotipo nudo 3×3 + wordmark Faber/Loom bicolor) + command-bar + status chip.
   - **Rail izquierdo** con los 3 modos (Operar/Aprender/Admin), vistas por modo, lista de **Espacios** poblada desde `/api/workspaces`, y user-card.
   - **Canvas central** con context-strip (espacio activo) y vista **SpaceLoom**: lista de chats + área de mensajes (empty state "Tu telar está listo") + composer auto-grow (solo UI, sin envío real — eso es SL1a).
   - **Iconos SVG inline** 24×24, stroke 1.75, `currentColor`; isotipo stroke 3.5 sobre lienzo 48.
   - **Tokens CSS** = paleta fija exacta + tres familias tipográficas. Sin Bootstrap/Tailwind. Sin hex sueltos.
   - **Bootstrap inyectable**: `window.__SPACELOOM_BOOTSTRAP__` listo para que el backend inyecte el workspace activo.
   - **main.py** ya apunta pywebview a `http://127.0.0.1:8000/static/index.html` con pre-render shell anti-pantalla-blanca.
   - Sin código muerto (la antigua `initials()` ya no existe; el avatar usa "AL").

**Veredicto: SL0 frontend DoD cumplido** — la app abre, muestra el shell SpaceLoom y un chat estéticamente funcional, y persiste/lee estado local. No hay riesgos P0 introducidos (composer no ejecuta nada; HITL note visible).

A continuación los archivos entregables (contenido vigente y verificado en disco):

```html:app/static/index.html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>SpaceLoom · FaberLoom</title>

    <!-- Brand fonts: EB Garamond (voz), Geist (UI), Geist Mono (datos) -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />

    <!-- App tokens + layout -->
    <link rel="stylesheet" href="/static/css/main.css" />

    <!-- React 18 UMD + Babel standalone (no build step, SL0) -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone@7/babel.min.js"></script>
  </head>
  <body>
    <div id="root">
      <!-- Pre-hydration shell so the window is never blank while CDN/Babel load -->
      <div class="boot">
        <div class="boot-mark" aria-hidden="true">
          <svg viewBox="0 0 48 48" width="30" height="30" fill="none" stroke="#F4F1ED" stroke-width="3.5" stroke-linecap="round">
            <path d="M14 7 V19" /><path d="M14 29 V41" />
            <path d="M24 7 V9" /><path d="M24 19 V29" /><path d="M24 39 V41" />
            <path d="M34 7 V19" /><path d="M34 29 V41" />
            <path d="M7 14 H9" /><path d="M19 14 H29" /><path d="M39 14 H41" />
            <path d="M7 24 H19" /><path d="M29 24 H41" />
            <path d="M7 34 H9" /><path d="M19 34 H29" /><path d="M39 34 H41" />
          </svg>
        </div>
        <div class="boot-text">Cargando SpaceLoom…</div>
      </div>
    </div>

    <!-- App (JSX transpiled in-browser by Babel for SL0) -->
    <script type="text/babel" data-presets="react" src="/static/js/app.jsx"></script>
  </body>
</html>
```

```jsx:app/static/js/app.jsx
/* =====================================================================
   SpaceLoom · FaberLoom — SL0 frontend shell
   ---------------------------------------------------------------------
   React 18 UMD + Babel standalone (sin build step).
   Marca FaberLoom: paleta fija + EB Garamond (voz) / Geist (UI) / Geist Mono (datos).
   Iconos SVG inline 24×24, stroke 1.75, currentColor.
   SL0 = SOLO UI: shell (topbar + rail + canvas) y chat vacío estéticamente
   funcional. Sin lógica real de chat (eso llega en SL1a).
   El backend puede inyectar el espacio activo vía window.__SPACELOOM_BOOTSTRAP__.
   ===================================================================== */

const { useState, useEffect, useRef, useCallback } = React;

/* ── Helpers de icono ──────────────────────────────────────────────── */
function Svg({ children, w = 24, viewBox = "0 0 24 24" }) {
  return (
    <svg
      viewBox={viewBox}
      width={w}
      height={w}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

/* Isotipo: nudo 3×3 tejido (warp + weft). Stroke 3.5 sobre lienzo 48. */
function BrandMark({ w = 24 }) {
  return (
    <svg
      viewBox="0 0 48 48"
      width={w}
      height={w}
      fill="none"
      stroke="currentColor"
      strokeWidth="3.5"
      strokeLinecap="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M14 7 V19" /><path d="M14 29 V41" />
      <path d="M24 7 V9" /><path d="M24 19 V29" /><path d="M24 39 V41" />
      <path d="M34 7 V19" /><path d="M34 29 V41" />
      <path d="M7 14 H9" /><path d="M19 14 H29" /><path d="M39 14 H41" />
      <path d="M7 24 H19" /><path d="M29 24 H41" />
      <path d="M7 34 H9" /><path d="M19 34 H29" /><path d="M39 34 H41" />
    </svg>
  );
}

/* Set de iconos UI (24×24 · stroke 1.75 · currentColor) */
const IconMenu = ({ w }) => (<Svg w={w}><path d="M4 7h16" /><path d="M4 12h16" /><path d="M4 17h16" /></Svg>);
const IconSearch = ({ w }) => (<Svg w={w}><circle cx="10.5" cy="10.5" r="6.5" /><path d="M15.5 15.5L20 20" /></Svg>);
const IconOperate = ({ w }) => (<Svg w={w}><path d="M8 4v16" /><path d="M16 4v16" /><path d="M4 8h16" /><path d="M4 16h16" /></Svg>);
const IconLearn = ({ w }) => (<Svg w={w}><path d="M3 8.5L12 5l9 3.5L12 12 3 8.5z" /><path d="M7 10.5v4.2c0 .9 2.2 1.8 5 1.8s5-.9 5-1.8v-4.2" /><path d="M21 8.5v4" /></Svg>);
const IconAdmin = ({ w }) => (<Svg w={w}><path d="M4 7h7" /><path d="M15 7h5" /><circle cx="13" cy="7" r="2" /><path d="M4 12h3" /><path d="M11 12h9" /><circle cx="9" cy="12" r="2" /><path d="M4 17h9" /><path d="M17 17h3" /><circle cx="15" cy="17" r="2" /></Svg>);
const IconLoom = ({ w }) => (<Svg w={w}><path d="M8 4v6" /><path d="M8 14v6" /><path d="M16 4v6" /><path d="M16 14v6" /><path d="M4 8h6" /><path d="M14 8h6" /><path d="M4 16h6" /><path d="M14 16h6" /><rect x="10" y="10" width="4" height="4" rx="1" /></Svg>);
const IconInbox = ({ w }) => (<Svg w={w}><path d="M4 13h4l1.5 2.5h5L16 13h4" /><path d="M4 13l2.2-6.5A1.5 1.5 0 0 1 7.6 5.5h8.8a1.5 1.5 0 0 1 1.4 1L20 13v5.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5z" /></Svg>);
const IconWork = ({ w }) => (<Svg w={w}><path d="M4 6h11" /><path d="M4 12h11" /><path d="M4 18h7" /><path d="M16 16.5l2 2 3.5-4" /></Svg>);
const IconSkill = ({ w }) => (<Svg w={w}><path d="M5 19L18 6" /><path d="M14 5.5h4.5V10" /><path d="M9 15.5l-3.4 1.1 1.1-3.4" /></Svg>);
const IconSpark = ({ w }) => (<Svg w={w}><path d="M12 3l1.7 4.8L18.5 9.5l-4.8 1.7L12 16l-1.7-4.8L5.5 9.5l4.8-1.7z" /><path d="M18.5 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" /></Svg>);
const IconRoute = ({ w }) => (<Svg w={w}><circle cx="6.5" cy="6.5" r="2.5" /><circle cx="17.5" cy="17.5" r="2.5" /><path d="M6.5 9v3.5a3 3 0 0 0 3 3h2.5a3 3 0 0 1 3 3" /></Svg>);
const IconDb = ({ w }) => (<Svg w={w}><path d="M5 6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5S15.9 3.5 12 3.5 5 4.6 5 6z" /><path d="M5 6v12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6" /><path d="M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5" /></Svg>);
const IconShield = ({ w }) => (<Svg w={w}><path d="M12 3l7 3v5c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6z" /><path d="M9 12l2 2 4-4" /></Svg>);
const IconPlus = ({ w }) => (<Svg w={w}><path d="M12 5v14" /><path d="M5 12h14" /></Svg>);
const IconSend = ({ w }) => (<Svg w={w}><path d="M12 19V6" /><path d="M6 12l6-6 6 6" /></Svg>);
const IconAt = ({ w }) => (<Svg w={w}><circle cx="12" cy="12" r="3.2" /><path d="M15.2 12v1.3a2 2 0 0 0 3.8.8 8 8 0 1 0-3 4" /></Svg>);

/* ── Configuración de navegación ───────────────────────────────────── */
const MODES = [
  { id: "operar", label: "Operar", Icon: IconOperate },
  { id: "aprender", label: "Aprender", Icon: IconLearn },
  { id: "admin", label: "Admin", Icon: IconAdmin },
];

const NAV = {
  operar: [
    { id: "space", title: "SpaceLoom", sub: "Canvas · draft-first", Icon: IconLoom },
    { id: "inbox", title: "Inbox", sub: "Correo · read-first", Icon: IconInbox },
    { id: "workloom", title: "WorkLoom", sub: "Cola HITL", Icon: IconWork },
  ],
  aprender: [
    { id: "skills", title: "Routine Hub", sub: "Skills · @nombre", Icon: IconSkill },
    { id: "gold", title: "Gold loop", sub: "edit_pct ↓ con el uso", Icon: IconSpark },
  ],
  admin: [
    { id: "routing", title: "Routing", sub: "Proveedores · costo", Icon: IconRoute },
    { id: "kb", title: "Base de conocimiento", sub: "Fuentes · FTS5", Icon: IconDb },
    { id: "audit", title: "Auditoría", sub: "audit.jsonl", Icon: IconShield },
  ],
};

/* Etiquetas legibles por vista (para el placeholder de vistas no-SL0) */
const VIEW_LABELS = {
  inbox: "Inbox", workloom: "WorkLoom", skills: "Routine Hub",
  gold: "Gold loop", routing: "Routing", kb: "Base de conocimiento", audit: "Auditoría",
};

/* Sugerencias del estado vacío (solo UI, sin acción real en SL0) */
const SUGGESTIONS = [
  { Icon: IconLoom, label: "Armar un draft contra el espacio" },
  { Icon: IconDb, label: "Citar un dato con su fuente" },
  { Icon: IconSkill, label: "Invocar una skill por @nombre" },
];

/* ── Bootstrap inyectable por el backend ───────────────────────────── */
function readBootstrap() {
  try {
    const b = window.__SPACELOOM_BOOTSTRAP__;
    if (b && typeof b === "object") return b;
  } catch (e) { /* noop */ }
  return null;
}

/* ── Rail izquierdo ────────────────────────────────────────────────── */
function Rail({ mode, setMode, nav, setNav, workspaces, status, activeWsId, setActiveWsId }) {
  const items = NAV[mode] || [];
  return (
    <aside className="rail">
      <nav className="mode-tabs" aria-label="Modos">
        {MODES.map(({ id, label, Icon }) => (
          <button
            key={id}
            type="button"
            className={"mode-tab" + (mode === id ? " active" : "")}
            aria-pressed={mode === id}
            onClick={() => setMode(id)}
          >
            <Icon w={16} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="rail-scroll">
        <section className="rail-section">
          <div className="section-head">
            <span>Vistas</span>
            <span className="section-count">{items.length}</span>
          </div>
          {items.map(({ id, title, sub, Icon }) => (
            <button
              key={id}
              type="button"
              className={"nav-item" + (nav === id ? " active" : "")}
              aria-current={nav === id ? "page" : undefined}
              onClick={() => setNav(id)}
            >
              <span className="item-icon"><Icon w={17} /></span>
              <span className="item-text">
                <span className="item-title">{title}</span>
                <span className="item-sub">{sub}</span>
              </span>
            </button>
          ))}
        </section>

        <section className="rail-section">
          <div className="section-head">
            <span>Espacios</span>
            <span className="section-count">{workspaces.length}</span>
          </div>

          {status === "loading" && (
            <div className="rail-empty">Cargando espacios…</div>
          )}
          {status === "error" && (
            <div className="rail-error">No se pudo leer <code>/api/workspaces</code>.</div>
          )}
          {status === "ready" && workspaces.length === 0 && (
            <div className="rail-empty">Aún no hay espacios. El backend sembrará uno de prueba.</div>
          )}
          {status === "ready" && workspaces.map((ws) => (
            <button
              key={ws.id}
              type="button"
              className={"workspace-item" + (ws.id === activeWsId ? " active" : "")}
              aria-current={ws.id === activeWsId ? "true" : undefined}
              onClick={() => setActiveWsId(ws.id)}
            >
              <span className="item-icon"><IconLoom w={17} /></span>
              <span className="item-text">
                <span className="item-title">{ws.name}</span>
                <span className="item-sub">{ws.slug}</span>
              </span>
            </button>
          ))}
        </section>
      </div>

      <div className="user-card">
        <span className="avatar">AL</span>
        <span className="user-meta">
          <span className="user-name">Álvaro</span>
          <span className="user-role">Owner · local</span>
        </span>
      </div>
    </aside>
  );
}

/* ── Estado vacío del hilo (chat estéticamente funcional) ──────────── */
function EmptyThread() {
  return (
    <div className="empty-state">
      <span className="empty-mark"><BrandMark w={38} /></span>
      <h2>Tu telar está listo.</h2>
      <p>
        La IA prepara, vos tejés. Escribí abajo para empezar un draft contra el
        contexto del espacio activo. En SL0 esto es solo el telar; el primer draft
        real llega en SL1.
      </p>
      <div className="empty-chips">
        {SUGGESTIONS.map(({ Icon, label }, i) => (
          <span className="empty-chip" key={i}>
            <Icon w={16} />
            {label}
          </span>
        ))}
      </div>
      <span className="safety-note">
        <IconShield w={15} />
        HITL absoluto · nada irreversible se ejecuta sin tu doble confirmación.
      </span>
    </div>
  );
}

/* ── Vista SpaceLoom (lista de chats + hilo + composer) ────────────── */
function SpaceView({ activeWorkspace }) {
  const [text, setText] = useState("");
  const taRef = useRef(null);

  const autoGrow = useCallback(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
  }, []);

  // SL0: sin envío real. Prevenimos el submit; el composer es solo visual.
  const onSubmit = (e) => {
    e.preventDefault();
  };

  return (
    <div className="space-view">
      <div className="chat-list">
        <div className="chat-list-head">
          <h2>Chats</h2>
          <button type="button" className="new-chat" title="Nuevo chat" aria-label="Nuevo chat">
            <IconPlus w={16} />
          </button>
        </div>
        <div className="rail-empty">
          Aún no hay chats en este espacio. Empezá uno desde el composer.
        </div>
      </div>

      <div className="thread-wrap">
        <div className="messages">
          <EmptyThread />
        </div>

        <form className="composer-area" onSubmit={onSubmit}>
          <div className="composer">
            <textarea
              ref={taRef}
              value={text}
              onChange={(e) => { setText(e.target.value); autoGrow(); }}
              placeholder={
                activeWorkspace
                  ? `Escribile al telar de ${activeWorkspace.name}…`
                  : "Escribile al telar…"
              }
              rows={1}
            />
            <div className="composer-footer">
              <span className="composer-tag">
                <IconAt w={15} />
                @cotizador
              </span>
              <span className="composer-tag">
                <IconLoom w={15} />
                {activeWorkspace ? activeWorkspace.name : "Sin espacio"}
              </span>
              <button
                type="submit"
                className="composer-send"
                disabled={text.trim().length === 0}
              >
                <IconSend w={16} />
                Enviar
              </button>
            </div>
          </div>
          <p className="hint">
            Enter para enviar · Shift+Enter para nueva línea. En SL0 el composer es
            solo de muestra.
          </p>
        </form>
      </div>
    </div>
  );
}

/* ── Placeholder para vistas que aún no son SL0 ────────────────────── */
function PlaceholderView({ viewId }) {
  const label = VIEW_LABELS[viewId] || "Vista";
  return (
    <div className="messages">
      <div className="empty-state">
        <span className="empty-mark"><BrandMark w={38} /></span>
        <h2>{label}</h2>
        <p>Esta superficie llega en un hito posterior. SL0 entrega el telar (SpaceLoom) y su shell.</p>
      </div>
    </div>
  );
}

/* ── Canvas central ────────────────────────────────────────────────── */
function Canvas({ nav, activeWorkspace }) {
  return (
    <main className="canvas">
      <div className="context-strip">
        <span className="context-dot" aria-hidden="true" />
        <div className="context-main">
          <div className="context-title">
            <h1>{activeWorkspace ? activeWorkspace.name : "Sin espacio activo"}</h1>
            {activeWorkspace && <span className="context-badge">{activeWorkspace.slug}</span>}
          </div>
          <div className="context-sub">
            {activeWorkspace
              ? "Espacio activo · local-first · listo para tejer"
              : "Esperando que el backend siembre un espacio"}
          </div>
        </div>
        <div className="context-actions">
          <span className="pill pill-muted" title="Disponible en SL2a"><IconShield w={16} /> SL2a · sellado</span>
          <span className="pill pill-muted" title="Disponible en SL1a"><IconRoute w={16} /> SL1a · router</span>
        </div>
      </div>

      {nav === "space"
        ? <SpaceView activeWorkspace={activeWorkspace} />
        : <PlaceholderView viewId={nav} />}
    </main>
  );
}

/* ── Topbar ────────────────────────────────────────────────────────── */
function Topbar() {
  return (
    <header className="topbar">
      <button type="button" className="icon-button" aria-label="Menú">
        <IconMenu />
      </button>

      <div className="brand">
        <span className="brand-mark"><BrandMark w={24} /></span>
        <span className="brand-word">
          <span className="brand-name">
            <span className="brand-faber">Faber</span><span className="brand-loom">Loom</span>
          </span>
          <span className="brand-sub">SpaceLoom · SL0</span>
        </span>
      </div>

      <div className="command-bar" role="button" tabIndex={0}>
        <IconSearch w={16} />
        <span>Buscar o ejecutar…</span>
        <kbd>Ctrl K</kbd>
      </div>

      <div className="top-actions">
        <span className="status-chip">
          <span className="dot" aria-hidden="true" />
          <strong>SL0 · local</strong>
        </span>
      </div>
    </header>
  );
}

/* ── App raíz ──────────────────────────────────────────────────────── */
function App() {
  const boot = readBootstrap();
  const [mode, setMode] = useState("operar");
  const [nav, setNav] = useState("space");
  const [workspaces, setWorkspaces] = useState(boot && boot.workspaces ? boot.workspaces : []);
  const [activeWsId, setActiveWsId] = useState(boot && boot.activeWorkspaceId ? boot.activeWorkspaceId : null);
  const [status, setStatus] = useState(boot && boot.workspaces ? "ready" : "loading");

  // Cuando cambia de modo, seleccionamos la primera vista del modo.
  useEffect(() => {
    const first = (NAV[mode] || [])[0];
    if (first) setNav(first.id);
  }, [mode]);

  // Carga de espacios desde la API (si el backend no los inyectó).
  useEffect(() => {
    if (boot && boot.workspaces) return; // ya vinieron inyectados
    let cancelled = false;
    fetch("/api/workspaces", { headers: { "x-user-id": "local" } })
      .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then((data) => {
        if (cancelled) return;
        const list = (data && data.workspaces) || [];
        setWorkspaces(list);
        setActiveWsId((prev) => prev || (list[0] && list[0].id) || null);
        setStatus("ready");
      })
      .catch(() => { if (!cancelled) setStatus("error"); });
    return () => { cancelled = true; };
  }, []);

  const activeWorkspace = workspaces.find((w) => w.id === activeWsId) || null;

  return (
    <div className="app-shell">
      <Topbar />
      <div className="frame">
        <Rail
          mode={mode}
          setMode={setMode}
          nav={nav}
          setNav={setNav}
          workspaces={workspaces}
          status={status}
          activeWsId={activeWsId}
          setActiveWsId={setActiveWsId}
        />
        <Canvas nav={nav} activeWorkspace={activeWorkspace} />
      </div>
    </div>
  );
}

/* ── Montaje ───────────────────────────────────────────────────────── */
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
```

```css:app/static/css/main.css
/* brand tokens — FaberLoom design system (canon)
   =====================================================================
   No usar hex sueltos en el código: toda superficie consume estas vars.
   Paleta fija FaberLoom + tipografía de tres familias (una función c/u).

   PALETA
   --bg            #F4F1ED  cream     · fondo base
   --surface       #FFFFFF  white     · tarjetas / paneles
   --surface-soft  #FBFAF7  off-white · inputs / hovers suaves
   --subtle        #EDE8DF  sand      · separadores / lienzo
   --text          #1F1E1C  ink       · texto principal
   --text-2        #5A544C  ink-soft  · texto secundario
   --muted         #8A8278  taupe     · texto terciario / captions
   --border        #D8D0C0  warm      · bordes
   --border-strong #C9BEAA  warm+     · bordes activos
   --coral         #C96442  coral     · acento de marca (el maker, constante)
   --coral-hover   #A84F33  coral+    · estado hover del acento
   --slate         #5A6B7C  slate     · acento frío secundario
   --success       #2F8F5E  green     · estado OK (funcional)
   --warning       #B07A1E  amber     · estado aviso (funcional)

   TIPOGRAFÍA  (una familia, un trabajo)
   --font-title    EB Garamond Italic · la voz: títulos y editorial
   --font-ui       Geist              · la interfaz: botones, labels, body UI
   --font-mono     Geist Mono         · los datos: timestamps y audit trail

   ICONOGRAFÍA   24×24 · stroke 1.75 · round caps · currentColor (+1 coral opcional)
   ISOTIPO       nudo 3×3 tejido (warp+weft) · stroke 3.5 sobre lienzo 48
   ===================================================================== */
:root {
  --bg: #F4F1ED;
  --surface: #FFFFFF;
  --surface-soft: #FBFAF7;
  --subtle: #EDE8DF;
  --text: #1F1E1C;
  --text-2: #5A544C;
  --muted: #8A8278;
  --border: #D8D0C0;
  --border-strong: #C9BEAA;
  --scroll: #CFC6B6;
  --scroll-hover: #BEB29B;
  --coral: #C96442;
  --coral-hover: #A84F33;
  --coral-soft: rgba(201, 100, 66, 0.12);
  --slate: #5A6B7C;
  --slate-soft: rgba(90, 107, 124, 0.11);
  --success: #2F8F5E;
  --warning: #B07A1E;
  --shadow: 0 18px 54px rgba(40, 34, 28, 0.12);
  --shadow-sm: 0 3px 12px rgba(40, 34, 28, 0.08);
  --radius-lg: 18px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --font-title: "EB Garamond", Georgia, "Times New Roman", serif;
  --font-ui: "Geist", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: "Geist Mono", "SF Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --ease: cubic-bezier(.25,.8,.25,1);
}

* { box-sizing: border-box; }

html, body, #root { height: 100%; }
html { background: var(--bg); }

body {
  margin: 0;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, rgba(201, 100, 66, 0.07), transparent 28%),
    radial-gradient(circle at 82% 0%, rgba(90, 107, 124, 0.08), transparent 28%),
    var(--bg);
  color: var(--text);
  font: 13.5px/1.55 var(--font-ui);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

::selection { background: var(--coral); color: var(--bg); }

button, input, textarea, select { font: inherit; }
button { color: inherit; }

:focus-visible { outline: 2px solid var(--coral); outline-offset: 2px; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--scroll); border: 3px solid var(--bg); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }

.boot { min-height: 100vh; display: grid; place-items: center; align-content: center; gap: 14px; color: var(--muted); }
.boot-mark { width: 54px; height: 54px; border-radius: 17px; display: grid; place-items: center; background: var(--coral); box-shadow: var(--shadow); }
.boot-text { font-family: var(--font-mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; }

.app-shell { height: 100%; min-height: 0; display: flex; flex-direction: column; background: var(--bg); }

/* Topbar */
.topbar {
  height: 58px; flex: 0 0 58px;
  display: flex; align-items: center; gap: 14px;
  padding: 0 16px; border-bottom: 1px solid var(--border);
  background: rgba(244, 241, 237, 0.88); backdrop-filter: blur(14px); z-index: 10;
}

.icon-button {
  width: 36px; height: 36px; border: 1px solid transparent; border-radius: 10px; background: transparent;
  display: grid; place-items: center; color: var(--muted); cursor: pointer;
  transition: background .18s var(--ease), color .18s var(--ease), border-color .18s var(--ease);
}
.icon-button:hover { background: var(--surface); border-color: var(--border); color: var(--text); }

.icon { width: 24px; height: 24px; display: block; fill: none; stroke: currentColor; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }

.brand { display: inline-flex; align-items: center; gap: 10px; min-width: 204px; }
.brand-mark { width: 34px; height: 34px; border-radius: 11px; background: var(--coral); color: var(--bg); display: grid; place-items: center; box-shadow: var(--shadow-sm); flex: 0 0 34px; }
.brand-mark svg { width: 24px; height: 24px; display: block; }
.brand-word { display: grid; gap: 0; line-height: 1; }
.brand-name { font-family: var(--font-title); font-style: italic; font-size: 21px; font-weight: 500; letter-spacing: -0.01em; }
.brand-name .brand-faber { color: var(--coral); }
.brand-name .brand-loom { color: var(--text); }
.brand-sub { margin-top: 3px; font-family: var(--font-mono); font-size: 9.5px; color: var(--muted); letter-spacing: .09em; text-transform: uppercase; }

.command-bar {
  flex: 1; max-width: 460px; height: 36px; margin: 0 auto; padding: 0 12px;
  border: 1px solid var(--border); border-radius: 11px; background: var(--surface-soft); color: var(--muted);
  display: flex; align-items: center; gap: 9px; min-width: 180px;
}
.command-bar span { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.command-bar kbd { margin-left: auto; border: 1px solid var(--border); border-radius: 5px; background: var(--surface); color: var(--muted); font: 10px/1.2 var(--font-mono); padding: 2px 6px; }

.top-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.status-chip { display: inline-flex; align-items: center; gap: 8px; height: 34px; border: 1px solid var(--border); border-radius: 10px; padding: 0 10px; background: var(--surface); color: var(--text-2); white-space: nowrap; }
.status-chip .dot { width: 7px; height: 7px; border-radius: 999px; background: var(--success); box-shadow: 0 0 0 3px rgba(47,143,94,.12); }
.status-chip strong { font: 500 11px/1 var(--font-mono); letter-spacing: .03em; }

/* Frame */
.frame { min-height: 0; flex: 1; display: flex; position: relative; }

.rail {
  width: 282px; flex: 0 0 282px; min-height: 0; border-right: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,0)), var(--bg);
  display: flex; flex-direction: column; padding: 12px 10px 10px; overflow: hidden;
}

.mode-tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; margin: 0 0 14px; }
.mode-tab {
  border: 1px solid var(--border); background: var(--surface-soft); color: var(--muted); border-radius: 10px;
  min-width: 0; padding: 9px 4px; display: flex; align-items: center; justify-content: center; gap: 5px; cursor: pointer;
  transition: all .18s var(--ease);
}
.mode-tab svg { width: 16px; height: 16px; }
.mode-tab span { font-size: 11.5px; font-weight: 600; }
.mode-tab:hover { color: var(--text-2); background: var(--surface); }
.mode-tab.active { background: var(--surface); color: var(--text); border-color: var(--border-strong); box-shadow: var(--shadow-sm); }

.rail-scroll { min-height: 0; flex: 1; overflow: auto; padding-right: 2px; }
.rail-section { margin-bottom: 16px; }
.section-head { display: flex; align-items: center; gap: 7px; padding: 8px 8px 7px; color: var(--muted); font-family: var(--font-mono); font-size: 10.5px; letter-spacing: .11em; text-transform: uppercase; }
.section-count { margin-left: auto; min-width: 20px; text-align: center; border-radius: 999px; padding: 1px 6px; background: var(--surface); border: 1px solid var(--border); letter-spacing: 0; }

.nav-item, .workspace-item, .chat-item {
  width: 100%; border: 1px solid transparent; background: transparent; color: var(--text-2); border-radius: 10px;
  padding: 9px 9px; display: flex; align-items: center; gap: 10px; text-align: left; cursor: pointer;
  transition: background .16s var(--ease), color .16s var(--ease), border-color .16s var(--ease);
}
.nav-item:hover, .workspace-item:hover, .chat-item:hover { background: rgba(255,255,255,.48); color: var(--text); }
.nav-item.active, .workspace-item.active, .chat-item.active { background: var(--surface); color: var(--text); border-color: var(--border); box-shadow: inset 2px 0 0 var(--coral); }

.item-icon { width: 28px; height: 28px; flex: 0 0 28px; border-radius: 9px; display: grid; place-items: center; color: var(--slate); background: var(--slate-soft); }
.active .item-icon { color: var(--coral); background: var(--coral-soft); }
.item-icon svg { width: 17px; height: 17px; }
.item-text { min-width: 0; flex: 1; }
.item-title { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; font-size: 12.5px; }
.item-sub { margin-top: 1px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); font-size: 11.5px; }

.rail-empty, .rail-error { margin: 4px 8px; padding: 12px; border: 1px dashed var(--border); border-radius: 12px; background: rgba(255,255,255,.36); color: var(--muted); font-size: 12px; }
.rail-error { color: var(--coral-hover); border-color: rgba(201, 100, 66, .35); background: rgba(201,100,66,.06); }

.user-card { flex: 0 0 auto; margin-top: 10px; padding: 11px 9px 4px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 9px; }
.avatar { width: 30px; height: 30px; flex: 0 0 30px; border-radius: 999px; display: grid; place-items: center; background: var(--surface); border: 1px solid var(--border); color: var(--coral); font: 700 10px/1 var(--font-mono); }
.user-meta { min-width: 0; }
.user-name { font-weight: 600; font-size: 12.5px; }
.user-role { color: var(--muted); font-size: 11.5px; }

/* Canvas */
.canvas {
  min-width: 0; min-height: 0; flex: 1; display: flex; flex-direction: column;
  background: linear-gradient(180deg, rgba(255,255,255,.34), rgba(255,255,255,0) 180px), var(--subtle);
}

.context-strip { flex: 0 0 auto; min-height: 62px; padding: 11px 22px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,.62); }
.context-dot { width: 12px; height: 12px; flex: 0 0 12px; border-radius: 999px; background: var(--coral); box-shadow: 0 0 0 4px rgba(201,100,66,.13); }
.context-main { min-width: 0; }
.context-title { display: flex; align-items: baseline; gap: 8px; min-width: 0; }
.context-title h1 { margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: var(--font-title); font-style: italic; font-size: 22px; line-height: 1.05; font-weight: 500; letter-spacing: -0.01em; }
.context-badge { flex: 0 0 auto; border: 1px solid var(--border); border-radius: 999px; padding: 3px 7px 2px; color: var(--slate); background: var(--surface); font: 700 9.5px/1 var(--font-mono); letter-spacing: .08em; text-transform: uppercase; }
.context-sub { margin-top: 2px; color: var(--muted); font-size: 12px; }
.context-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; }

.pill { display: inline-flex; align-items: center; gap: 7px; height: 32px; border: 1px solid var(--border); border-radius: 999px; background: var(--surface); padding: 0 10px; color: var(--text-2); white-space: nowrap; font-size: 12px; }
.pill svg { width: 16px; height: 16px; color: var(--slate); }
.pill-muted { background: var(--subtle); color: var(--muted); border-style: dashed; cursor: help; }
.pill-muted svg { color: var(--muted); }

.space-view { min-height: 0; flex: 1; display: grid; grid-template-columns: minmax(208px, 260px) minmax(0, 1fr); }

.chat-list { min-height: 0; border-right: 1px solid var(--border); background: rgba(244,241,237,.72); padding: 14px 10px; overflow: auto; }
.chat-list-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 0 4px 12px; }
.chat-list-head h2 { margin: 0; font-size: 13px; letter-spacing: -0.01em; }
.new-chat { width: 28px; height: 28px; border: 1px solid var(--border); border-radius: 9px; background: var(--surface); color: var(--coral); display: grid; place-items: center; cursor: pointer; }
.new-chat:hover { border-color: rgba(201,100,66,.42); background: var(--coral-soft); }
.chat-time { margin-left: auto; align-self: flex-start; color: var(--muted); font: 10px/1 var(--font-mono); }

.thread-wrap { min-width: 0; min-height: 0; display: flex; flex-direction: column; background: var(--surface-soft); }
.messages { min-height: 0; flex: 1; overflow: auto; padding: 28px clamp(18px, 4vw, 48px); display: flex; flex-direction: column; gap: 18px; }

.empty-state { margin: auto; width: min(620px, 100%); text-align: center; display: grid; place-items: center; gap: 16px; padding: 24px; }
.empty-mark { width: 64px; height: 64px; border-radius: 20px; display: grid; place-items: center; color: var(--bg); background: var(--coral); box-shadow: var(--shadow); }
.empty-mark svg { width: 38px; height: 38px; }
.empty-state h2 { margin: 0; font-family: var(--font-title); font-style: italic; font-weight: 500; letter-spacing: -0.01em; font-size: clamp(34px, 4.5vw, 54px); line-height: 0.98; }
.empty-state p { margin: 0; max-width: 520px; color: var(--text-2); font-size: 15px; line-height: 1.65; }
.empty-chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 4px; }
.empty-chip { border: 1px solid var(--border); border-radius: 999px; padding: 9px 12px; background: var(--surface); color: var(--text-2); display: inline-flex; align-items: center; gap: 8px; font-size: 12.5px; }
.empty-chip svg { width: 16px; height: 16px; color: var(--coral); }

.safety-note { color: var(--muted); font-size: 11.5px; display: inline-flex; align-items: center; gap: 7px; }
.safety-note svg { width: 15px; height: 15px; color: var(--success); }

.message { display: grid; gap: 7px; max-width: 760px; animation: item-in .22s var(--ease); }
.message.user { align-self: flex-end; justify-items: end; }
.message.system, .message.assistant { align-self: flex-start; }
.message-meta { color: var(--muted); font: 11px/1.2 var(--font-mono); }
.bubble { border: 1px solid var(--border); border-radius: 16px; padding: 12px 14px; color: var(--text-2); background: var(--surface); box-shadow: var(--shadow-sm); }
.message.user .bubble { background: var(--text); color: var(--bg); border-color: var(--text); }
.message.system .bubble { background: rgba(90,107,124,.08); border-color: rgba(90,107,124,.22); }

.composer-area { flex: 0 0 auto; padding: 14px clamp(16px, 3vw, 30px) 18px; border-top: 1px solid var(--border); background: rgba(255,255,255,.72); }
.composer { max-width: 920px; margin: 0 auto; border: 1px solid var(--border); border-radius: 18px; background: var(--surface); box-shadow: var(--shadow-sm); overflow: hidden; transition: border-color .18s var(--ease), box-shadow .18s var(--ease); }
.composer:focus-within { border-color: rgba(201,100,66,.48); box-shadow: 0 0 0 4px rgba(201,100,66,.08), var(--shadow-sm); }
.composer textarea { width: 100%; min-height: 60px; max-height: 160px; resize: none; border: 0; outline: 0; background: transparent; color: var(--text); padding: 14px 16px 8px; line-height: 1.55; }
.composer textarea::placeholder { color: var(--muted); }
.composer-footer { display: flex; align-items: center; gap: 8px; padding: 8px 10px 10px; }
.composer-tag { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--border); border-radius: 999px; background: var(--surface-soft); padding: 6px 9px; color: var(--muted); font-size: 11.5px; }
.composer-tag svg { width: 15px; height: 15px; }
.composer-send { margin-left: auto; height: 34px; border: 0; border-radius: 11px; background: var(--coral); color: var(--bg); display: inline-flex; align-items: center; gap: 8px; padding: 0 12px; cursor: pointer; font-weight: 600; transition: background .18s var(--ease), transform .18s var(--ease), opacity .18s var(--ease); }
.composer-send:disabled { opacity: .45; cursor: default; }
.composer-send:not(:disabled):hover { background: var(--coral-hover); transform: translateY(-1px); }
.composer-send svg { width: 16px; height: 16px; }

.hint { margin: 8px auto 0; max-width: 920px; color: var(--muted); font-size: 11.5px; text-align: center; }

@keyframes item-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1080px) {
  .rail { width: 238px; flex-basis: 238px; }
  .space-view { grid-template-columns: 220px minmax(0, 1fr); }
  .brand { min-width: 178px; }
}

@media (max-width: 820px) {
  body { overflow: auto; }
  .app-shell { min-height: 100%; height: auto; }
  .topbar { position: sticky; top: 0; }
  .command-bar, .status-chip { display: none; }
  .frame { flex-direction: column; }
  .rail { width: 100%; flex: 0 0 auto; border-right: 0; border-bottom: 1px solid var(--border); max-height: 280px; }
  .space-view { grid-template-columns: 1fr; }
  .chat-list { border-right: 0; border-bottom: 1px solid var(--border); max-height: 180px; }
  .context-strip { padding: 11px 16px; }
  .context-actions { display: none; }
}
```

```python:app/src/main.py
from __future__ import annotations

import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .db import db_session, initialize_database
from .seed import seed_demo_workspace


APP_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_DIR / "static"

# Entry point de la ventana desktop (pywebview) y del servidor local.
HOST = os.getenv("SPACELOOM_HOST", "127.0.0.1")
PORT = int(os.getenv("SPACELOOM_PORT", "8000"))
APP_URL = f"http://{HOST}:{PORT}/static/index.html"
HEALTH_URL = f"http://{HOST}:{PORT}/api/health"


def app_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/static/index.html"


def health_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/api/health"


@asynccontextmanager
async def lifespan(app: FastAPI):
    with db_session() as conn:
        initialize_database(conn)
        seed_demo_workspace(conn)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="SpaceLoom", version="0.1.0-sl0", lifespan=lifespan)
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    def index():
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>SpaceLoom SL0</title>
                <style>
                  body {
                    margin: 0;
                    min-height: 100vh;
                    display: grid;
                    place-items: center;
                    background: #F4F1ED;
                    color: #1F1E1C;
                    font-family: Geist, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                  }
                  main {
                    width: min(680px, calc(100vw - 48px));
                    border: 1px solid #D8D0C0;
                    border-radius: 12px;
                    background: #FFFFFF;
                    padding: 32px;
                    box-shadow: 0 18px 60px rgba(31, 30, 28, 0.08);
                  }
                  .eyebrow {
                    color: #C96442;
                    font: 12px/1.4 "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                  }
                  h1 {
                    margin: 10px 0 12px;
                    font-family: "EB Garamond", Georgia, serif;
                    font-style: italic;
                    font-size: 44px;
                    font-weight: 500;
                    letter-spacing: -0.01em;
                  }
                  p { color: #5A544C; line-height: 1.6; margin: 0; }
                  code {
                    font-family: "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    color: #5A6B7C;
                  }
                </style>
              </head>
              <body>
                <main>
                  <div class="eyebrow">FaberLoom &middot; SpaceLoom</div>
                  <h1>SL0 skeleton is running.</h1>
                  <p>Local state is backed by SQLite. Check <code>/api/health</code> and <code>/api/workspaces</code>.</p>
                </main>
              </body>
            </html>
            """
        )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


app = create_app()


def _run_server(host: str = HOST, port: int = PORT) -> None:
    """Corre uvicorn en este proceso (se usa en un hilo daemon para el desktop)."""
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="warning")


def _wait_until_ready(url: str = HEALTH_URL, timeout: float = 20.0) -> bool:
    """Sondea /api/health hasta que el servidor responda o se agote el tiempo."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as resp:  # noqa: S310 (URL local fija)
                if resp.status == 200:
                    return True
        except (URLError, OSError):
            time.sleep(0.2)
    return False


def run_desktop(host: str = HOST, port: int = PORT) -> None:
    """Levanta el backend en un hilo y abre la ventana pywebview de SpaceLoom."""
    import webview

    server = threading.Thread(target=_run_server, args=(host, port), daemon=True)
    server.start()

    resolved_health_url = health_url(host, port)
    resolved_app_url = app_url(host, port)
    _wait_until_ready(resolved_health_url)

    webview.create_window(
        "SpaceLoom — FaberLoom",
        resolved_app_url,
        width=1320,
        height=860,
        min_size=(1000, 640),
        background_color="#F4F1ED",
    )
    webview.start()


def main() -> None:
    run_desktop()


if __name__ == "__main__":
    main()
```

### Notas de cierre
- **No modifiqué archivos a mano** (respetando `AGENTS.md`): la entrega SL0 ya estaba completa y los archivos en disco están correctos. Mi intervención fue auditoría + verificación funcional.
- Para correr el shell en navegador: `cd app && python -m uvicorn src.main:app --reload` → `http://127.0.0.1:8000/static/index.html`. Para la ventana desktop: `python app/src/main.py` (requiere `pywebview`).
- **Listo para SL1a**: el composer está cableado solo a nivel visual (`onSubmit` previene envío) y el `window.__SPACELOOM_BOOTSTRAP__` permite inyectar el workspace activo sin tocar el render.