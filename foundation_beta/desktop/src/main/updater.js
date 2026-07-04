"use strict";

const { app, BrowserWindow } = require("electron");
const { autoUpdater } = require("electron-updater");
const semver = require("semver");
const { net } = require("electron");

const DEFAULT_CHECK_INTERVAL_MS = 60 * 60 * 1000;

function getPlatform() {
  switch (process.platform) {
    case "win32":
      return "win";
    case "darwin":
      return "mac";
    case "linux":
      return "linux";
    default:
      return process.platform;
  }
}

function requestJson(url, partitionSession) {
  return new Promise((resolve, reject) => {
    const req = net.request({
      url,
      method: "GET",
      session: partitionSession,
    });
    req.setHeader("Accept", "application/json");
    const chunks = [];
    req.on("response", (res) => {
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        if (res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${raw}`));
          return;
        }
        try {
          resolve(JSON.parse(raw));
        } catch (err) {
          reject(err);
        }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

class UpdateManager {
  constructor({
    apiUrl = process.env.API_URL || "http://localhost:8000",
    syncManager,
    sessionManager,
    checkIntervalMs = parseInt(process.env.UPDATE_CHECK_INTERVAL_MS, 10) || DEFAULT_CHECK_INTERVAL_MS,
  }) {
    this.apiUrl = apiUrl.replace(/\/$/, "");
    this.syncManager = syncManager;
    this.sessionManager = sessionManager;
    this.checkIntervalMs = checkIntervalMs;
    this.currentProfile = null;
    this.blocked = false;
    this.downloaded = false;
    this.timer = null;

    autoUpdater.autoDownload = true;
    autoUpdater.autoInstallOnAppQuit = false;

    autoUpdater.on("update-available", (info) => {
      this._notifyRenderer("update:available", { version: info.version });
    });

    autoUpdater.on("update-downloaded", (info) => {
      this.downloaded = true;
      this._notifyRenderer("update:ready", { version: info.version });
    });

    autoUpdater.on("error", (err) => {
      this._notifyRenderer("update:error", { message: err.message });
    });
  }

  _notifyRenderer(channel, payload) {
    BrowserWindow.getAllWindows().forEach((win) => {
      win.webContents.send(channel, payload);
    });
  }

  async _getCurrentProfile() {
    return this.currentProfile;
  }

  async _fetchMinSupported(partitionSession) {
    return requestJson(
      `${this.apiUrl}/api/updates/min-supported`,
      partitionSession,
    );
  }

  async _fetchLatestRelease(partitionSession) {
    const platform = getPlatform();
    return requestJson(
      `${this.apiUrl}/api/updates/latest?platform=${platform}`,
      partitionSession,
    );
  }

  async check(profile) {
    this.currentProfile = profile;
    const partitionSession = await this.sessionManager.createSession(profile, "");

    let minVersion;
    try {
      const minData = await this._fetchMinSupported(partitionSession);
      minVersion = minData.min_supported_client_version;
    } catch (err) {
      // If the backend cannot be reached, skip the block check; updater will retry later.
      return;
    }

    const currentVersion = app.getVersion();
    if (semver.lt(currentVersion, minVersion)) {
      this.blocked = true;
      this._notifyRenderer("update:blocked", {
        current_version: currentVersion,
        min_supported_client_version: minVersion,
      });
      return;
    }

    let releaseInfo;
    try {
      releaseInfo = await this._fetchLatestRelease(partitionSession);
    } catch (err) {
      return;
    }

    if (releaseInfo.feed_url) {
      autoUpdater.setFeedURL({ url: releaseInfo.feed_url });
    }
    autoUpdater.checkForUpdates();
  }

  async canInstallSafely() {
    if (!this.syncManager) return true;
    const profile = this.currentProfile || this.syncManager.currentProfile;
    if (!profile) return true;
    const state = this.syncManager.getSyncState(profile);
    return state.status === "online" && !state.block_sensitive_actions;
  }

  async install() {
    if (this.blocked) {
      throw new Error("client version is below minimum supported");
    }
    const safe = await this.canInstallSafely();
    if (!safe) {
      throw new Error("cannot install while sync or mutations are pending");
    }
    if (!this.downloaded) {
      throw new Error("no update downloaded");
    }
    autoUpdater.quitAndInstall();
  }

  schedule(profile) {
    if (this.timer) return;
    this.timer = setInterval(() => {
      this.check(profile).catch(() => {});
    }, this.checkIntervalMs);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

module.exports = { UpdateManager, getPlatform };
