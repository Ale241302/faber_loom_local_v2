Resumen de cambios:

- Revisé `app/static/css/main.css` y `app/static/js/app.jsx`.
- Confirmé que los iconos inline usan el contrato de marca: `24×24`, `stroke 1.75`, `currentColor`.
- Confirmé que `app/static/assets/isotipo.svg` y `app/static/assets/wordmark.svg` ya existían y están alineados con el canon.
- No cambié funcionalidad.
- Modifiqué solo `app/static/css/main.css` para añadir el bloque obligatorio `/* brand tokens */` al inicio con los tokens de marca.
- Ejecuté `graphify update .` después del cambio.

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