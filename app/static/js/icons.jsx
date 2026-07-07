/* ═══════════════════════════════════════════════════════════════
   FaberLoom · Icons
   Icon set used by the shell. Loaded before foundation and app JSX.
   ═══════════════════════════════════════════════════════════════ */

function Icon({ name, size = 24, ...props }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.75", strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": "true", ...props };
  if (name === "loom") return <svg {...common}><path d="M7 3.5V9.5M7 14.5V20.5M12 3.5V4.5M12 9.5V14.5M12 19.5V20.5M17 3.5V9.5M17 14.5V20.5"/><path d="M3.5 7H4.5M9.5 7H14.5M19.5 7H20.5M3.5 12H9.5M14.5 12H20.5M3.5 17H4.5M9.5 17H14.5M19.5 17H20.5"/></svg>;
  if (name === "menu") return <svg {...common}><path d="M4 7h16M4 12h16M4 17h16"/></svg>;
  if (name === "search") return <svg {...common}><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.6-4.6"/></svg>;
  if (name === "send") return <svg {...common}><path d="M12 19V5M5 12h14"/></svg>;
  if (name === "arrow-up") return <svg {...common}><path d="M12 19V5M6 11l6-6 6 6"/></svg>;
  if (name === "book") return <svg {...common}><path d="M6 4h12v17l-6-4-6 4z"/></svg>;
  if (name === "layers") return <svg {...common}><path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/></svg>;
  if (name === "check") return <svg {...common}><path d="M5 12.5 10 17.5 19.5 8"/></svg>;
  if (name === "spark") return <svg {...common}><path d="M12 4 13.5 9 18 10.5 13.5 12 12 17 10.5 12 6 10.5 10.5 9z"/><path d="M19 4v3M21 5.5h-3M5 17v3M6.5 18.5h-3"/></svg>;
  if (name === "settings") return <svg {...common}><circle cx="12" cy="12" r="2.8"/><path d="M19.4 14.5a7.5 7.5 0 0 0 0-5l1.7-1.3-1.6-2.7-2 .8a7.5 7.5 0 0 0-4.3-2.5l-.3-2.1H10l-.3 2.1a7.5 7.5 0 0 0-4.3 2.5l-2-.8L1.8 8.2l1.7 1.3a7.5 7.5 0 0 0 0 5l-1.7 1.3 1.6 2.7 2-.8a7.5 7.5 0 0 0 4.3 2.5l.3 2.1H14l.3-2.1a7.5 7.5 0 0 0 4.3-2.5l2 .8 1.6-2.7z"/></svg>;
  if (name === "audit") return <svg {...common}><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>;
  if (name === "shield") return <svg {...common}><path d="M12 3.5 19 6v5.5c0 4.5-3 7.4-7 9-4-1.6-7-4.5-7-9V6l7-2.5Z"/><path d="M9 12l2 2 4-4"/></svg>;
  if (name === "database") return <svg {...common}><ellipse cx="12" cy="5.5" rx="6.5" ry="2.5"/><path d="M5.5 5.5v6c0 1.4 2.9 2.5 6.5 2.5s6.5-1.1 6.5-2.5v-6"/><path d="M5.5 11.5v6c0 1.4 2.9 2.5 6.5 2.5s6.5-1.1 6.5-2.5v-6"/></svg>;
  if (name === "route") return <svg {...common}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H12a4 4 0 0 1 0 8 4 4 0 0 0 0 8h3.5"/></svg>;
  if (name === "mail") return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>;
  if (name === "inbox") return <svg {...common}><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z"/></svg>;
  if (name === "clock") return <svg {...common}><circle cx="12" cy="12" r="8"/><path d="M12 8v4l2.5 2"/></svg>;
  if (name === "panel-l") return <svg {...common}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></svg>;
  if (name === "panel-r") return <svg {...common}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/></svg>;
  if (name === "x") return <svg {...common}><path d="M6 6 18 18M18 6 6 18"/></svg>;
  if (name === "plus") return <svg {...common}><path d="M12 5v14M5 12h14"/></svg>;
  if (name === "edit") return <svg {...common}><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>;
  if (name === "trash") return <svg {...common}><path d="M3 6h18M8 6V4h8v2M10 11v6M14 11v6M5 6l1 14h12l1-14"/></svg>;
  if (name === "refresh") return <svg {...common}><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>;
  if (name === "key") return <svg {...common}><circle cx="7.5" cy="15.5" r="5.5"/><path d="M21 2l-6 6m0 0h3m-3 0V5M10 18l.01 0"/></svg>;
  if (name === "sun") return <svg {...common}><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>;
  if (name === "moon") return <svg {...common}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>;
  if (name === "eye") return <svg {...common}><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>;
  if (name === "eye-off") return <svg {...common}><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><path d="M1 1l22 22"/></svg>;
  if (name === "log-out") return <svg {...common}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>;
  if (name === "paperclip") return <svg {...common}><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>;
  if (name === "file") return <svg {...common}><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>;
  return <svg {...common}><circle cx="12" cy="12" r="8"/><path d="M12 8v4M12 16v.01"/></svg>;
}

function BrandMark() { return <Icon name="loom" />; }
