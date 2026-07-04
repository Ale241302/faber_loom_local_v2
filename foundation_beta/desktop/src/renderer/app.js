"use strict";

const $ = (id) => document.getElementById(id);

let pending = { loginToken: null, tenantId: null };

function setStatus(text) {
  $("status").textContent = typeof text === "object" ? JSON.stringify(text, null, 2) : text;
}

function setSyncBadge(state) {
  const badge = $("sync-badge");
  if (!badge) return;
  badge.textContent = state.status || "offline";
  badge.className = `badge ${state.status || "offline"}`;

  const sensitive = document.querySelectorAll(".sensitive");
  const blocked = state.status !== "online" || state.block_sensitive_actions;
  sensitive.forEach((btn) => {
    btn.disabled = blocked;
    btn.title = blocked ? "Deshabilitado hasta que la sincronización esté online" : "";
  });
}

function showLogin() {
  $("login-panel").classList.remove("hidden");
  $("dashboard").classList.add("hidden");
}

function showDashboard(me) {
  $("login-panel").classList.add("hidden");
  $("dashboard").classList.remove("hidden");
  $("me").textContent = JSON.stringify(me, null, 2);
}

function showUpdateReady(version) {
  const banner = $("update-banner");
  const msg = $("update-message");
  const btn = $("restart-update");
  banner.classList.remove("hidden");
  msg.textContent = `Actualización ${version} descargada.`;
  btn.classList.remove("hidden");
}

function hideUpdateReady() {
  $("update-banner").classList.add("hidden");
  $("restart-update").classList.add("hidden");
}

function showBlocked(current, min) {
  $("blocked-overlay").classList.remove("hidden");
  $("blocked-current").textContent = current;
  $("blocked-min").textContent = min;
}

async function resumeSession() {
  const result = await window.faberloom.auth.me();
  if (result.ok) {
    showDashboard(result.me);
    window.faberloom.sync.getState().then(setSyncBadge).catch(() => {});
  } else {
    setStatus(`Sesión no válida: ${result.error}`);
  }
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const tenantId = $("tenant-id").value.trim();
  const email = $("email").value.trim();
  const password = $("password").value;

  const result = await window.faberloom.auth.login({ email, password, tenant_id: tenantId });
  if (!result.ok) {
    setStatus(result);
    return;
  }

  if (result.requires_2fa) {
    pending = { loginToken: result.login_token, tenantId };
    $("totp-form").classList.remove("hidden");
    setStatus("Requiere TOTP");
    return;
  }

  setStatus(`Login OK: ${result.user_id}`);
  await resumeSession();
});

$("totp-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!pending.loginToken) return;
  const result = await window.faberloom.auth.verifyTotp({
    login_token: pending.loginToken,
    totp: $("totp").value.trim(),
    tenant_id: pending.tenantId,
    remember: false,
  });
  if (!result.ok) {
    setStatus(result);
    return;
  }
  setStatus(`2FA OK: ${result.user_id}`);
  await resumeSession();
});

$("logout").addEventListener("click", async () => {
  await window.faberloom.auth.logout();
  hideUpdateReady();
  showLogin();
  setStatus("Sesión cerrada");
});

["approve", "edit", "send"].forEach((id) => {
  const btn = $(id);
  if (!btn) return;
  btn.addEventListener("click", () => {
    if (btn.disabled) return;
    setStatus(`${id} ejecutado`);
  });
});

$("restart-update")?.addEventListener("click", async () => {
  try {
    await window.faberloom.update.install();
  } catch (err) {
    setStatus(`No se puede instalar: ${err.message || err}`);
  }
});

$("blocked-restart")?.addEventListener("click", async () => {
  try {
    await window.faberloom.update.install();
  } catch (err) {
    setStatus(`No se puede instalar: ${err.message || err}`);
  }
});

window.faberloom.sync.onStateChanged((state) => {
  setSyncBadge(state);
});

window.faberloom.update.onAvailable((data) => {
  setStatus(`Actualización disponible: ${data.version}`);
});

window.faberloom.update.onReady((data) => {
  showUpdateReady(data.version);
});

window.faberloom.update.onBlocked((data) => {
  showBlocked(data.current_version, data.min_supported_client_version);
});

window.faberloom.update.onError((data) => {
  setStatus(`Error de actualización: ${data.message}`);
});

window.addEventListener("DOMContentLoaded", () => {
  resumeSession().catch(() => showLogin());
});
