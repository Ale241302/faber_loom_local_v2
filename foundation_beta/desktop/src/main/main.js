"use strict";

const path = require("path");
const { app, BrowserWindow, ipcMain } = require("electron");
const Store = require("electron-store");

const { ElectronSessionManager } = require("./session");
const { AuthApiClient } = require("./api");
const { SyncManager } = require("./sync");
const { UpdateManager } = require("./updater");

const store = new Store();
const sessionManager = new ElectronSessionManager();
const api = new AuthApiClient();
const syncManager = new SyncManager({ store, sessionManager });
const updateManager = new UpdateManager({ syncManager, sessionManager });

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function getCurrentProfile() {
  return store.get("currentProfile", "");
}

function setCurrentProfile(profile) {
  store.set("currentProfile", profile);
}

function startUpdateChecks(profile) {
  updateManager.stop();
  updateManager.check(profile).catch(() => {});
  updateManager.schedule(profile);
}

async function getPartitionSession() {
  const profile = getCurrentProfile();
  if (!profile) {
    throw new Error("No profile selected");
  }
  return sessionManager.createSession(profile, "");
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle("auth:getProfiles", async () => {
    return store.get("profiles", []);
  });

  ipcMain.handle("auth:switchProfile", async (_event, profile) => {
    setCurrentProfile(profile);
    syncManager.stop();
    syncManager.coldStart(profile).catch(() => {});
    startUpdateChecks(profile);
    return { profile };
  });

  ipcMain.handle("auth:login", async (_event, { email, password, tenant_id }) => {
    const profile = `${tenant_id}::${email}`;
    setCurrentProfile(profile);

    const partitionSession = await sessionManager.createSession(profile, "");
    const { statusCode, data } = await api.login({ email, password, tenant_id }, partitionSession);

    if (statusCode >= 400) {
      return { ok: false, error: data.detail || "login failed", statusCode };
    }

    if (data.requires_2fa) {
      return { ok: true, requires_2fa: true, login_token: data.login_token };
    }

    if (data.session_id) {
      await sessionManager.createSession(profile, data.session_id);
      const profiles = store.get("profiles", []);
      if (!profiles.includes(profile)) {
        store.set("profiles", [...profiles, profile]);
      }
      const result = {
        ok: true,
        requires_2fa: false,
        session_id: data.session_id,
        user_id: data.user_id,
        roles: data.roles,
        active_hat: data.active_hat,
      };
      syncManager.stop();
      syncManager.coldStart(profile).catch(() => {});
      startUpdateChecks(profile);
      return result;
    }

    return { ok: false, error: "unexpected response" };
  });

  ipcMain.handle("auth:verifyTotp", async (_event, { login_token, totp, tenant_id, remember }) => {
    const profile = getCurrentProfile();
    if (!profile) {
      return { ok: false, error: "No profile selected" };
    }
    const partitionSession = await sessionManager.createSession(profile, "");
    const { statusCode, data } = await api.verifyTotp(
      { login_token, totp, tenant_id, remember },
      partitionSession,
    );

    if (statusCode >= 400) {
      return { ok: false, error: data.detail || "2fa failed", statusCode };
    }

    if (data.session_id) {
      await sessionManager.createSession(profile, data.session_id);
      const profiles = store.get("profiles", []);
      if (!profiles.includes(profile)) {
        store.set("profiles", [...profiles, profile]);
      }
      const result = {
        ok: true,
        session_id: data.session_id,
        user_id: data.user_id,
        roles: data.roles,
        active_hat: data.active_hat,
      };
      syncManager.stop();
      syncManager.coldStart(profile).catch(() => {});
      startUpdateChecks(profile);
      return result;
    }

    return { ok: false, error: "unexpected response" };
  });

  ipcMain.handle("auth:me", async () => {
    const partitionSession = await getPartitionSession();
    const { statusCode, data } = await api.me(partitionSession);
    if (statusCode >= 400) {
      return { ok: false, error: data.detail || "session invalid", statusCode };
    }
    return { ok: true, me: data };
  });

  ipcMain.handle("auth:logout", async () => {
    const profile = getCurrentProfile();
    if (!profile) {
      return { ok: true };
    }
    try {
      const partitionSession = await sessionManager.createSession(profile, "");
      await api.logout(partitionSession);
    } catch (err) {
      // Best-effort remote logout; always clear local state.
    }
    syncManager.stop();
    updateManager.stop();
    await sessionManager.clearSession(profile);
    store.delete("currentProfile");
    return { ok: true };
  });

  ipcMain.handle("sync:start", async (_event, profile) => {
    syncManager.stop();
    await syncManager.coldStart(profile);
    return syncManager.getSyncState(profile);
  });

  ipcMain.handle("sync:getState", async (_event, profile) => {
    return syncManager.getSyncState(profile || getCurrentProfile());
  });

  ipcMain.handle("sync:fullRefresh", async (_event, profile) => {
    syncManager.stop();
    await syncManager.fullRefresh(profile);
    return syncManager.getSyncState(profile);
  });

  ipcMain.handle("update:check", async (_event, profile) => {
    updateManager.stop();
    await updateManager.check(profile || getCurrentProfile());
    return { blocked: updateManager.blocked, downloaded: updateManager.downloaded };
  });

  ipcMain.handle("update:install", async () => {
    await updateManager.install();
    return { ok: true };
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

module.exports = { createWindow };
