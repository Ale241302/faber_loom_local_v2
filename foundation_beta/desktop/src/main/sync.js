"use strict";

const WebSocket = require("ws");
const { net } = require("electron");

const SESSION_COOKIE_NAME = "session_id";
const DEFAULT_DELTA_HOURS = 24;
const DEFAULT_RETRY_INTERVAL_MS = 5000;
const DEFAULT_MAX_RETRIES = 10;

class SyncManager {
  constructor({
    apiUrl = process.env.API_URL || "http://localhost:8000",
    wsUrl = process.env.WS_URL || "ws://localhost:8000",
    store,
    sessionManager,
    deltaHours = parseInt(process.env.SYNC_DELTA_HOURS, 10) || DEFAULT_DELTA_HOURS,
    retryIntervalMs = parseInt(process.env.SYNC_RETRY_INTERVAL_MS, 10) || DEFAULT_RETRY_INTERVAL_MS,
    maxRetries = parseInt(process.env.SYNC_MAX_RETRIES, 10) || DEFAULT_MAX_RETRIES,
  }) {
    this.apiUrl = apiUrl.replace(/\/$/, "");
    this.wsUrl = wsUrl.replace(/\/$/, "");
    this.store = store;
    this.sessionManager = sessionManager;
    this.deltaHours = deltaHours;
    this.retryIntervalMs = retryIntervalMs;
    this.maxRetries = maxRetries;

    this.ws = null;
    this.reconnectTimer = null;
    this.retryCount = 0;
    this.currentProfile = null;
  }

  _cursorsKey(profile) {
    return `cursors.${profile}`;
  }

  _stateKey(profile) {
    return `state.${profile}`;
  }

  _syncStateKey(profile) {
    return `syncState.${profile}`;
  }

  getCursors(profile) {
    return this.store.get(this._cursorsKey(profile), null);
  }

  setCursors(profile, cursors) {
    this.store.set(this._cursorsKey(profile), {
      ...cursors,
      client_version: this.store.get("clientVersion", "0.1.0"),
    });
  }

  getSyncState(profile) {
    return (
      this.store.get(this._syncStateKey(profile), {
        status: "offline",
        last_sync_at: null,
        block_sensitive_actions: true,
      }) || {}
    );
  }

  setSyncState(profile, state) {
    const current = this.getSyncState(profile);
    const merged = { ...current, ...state };
    this.store.set(this._syncStateKey(profile), merged);
    this._notifyRenderer(profile, merged);
  }

  _notifyRenderer(profile, state) {
    const { BrowserWindow } = require("electron");
    BrowserWindow.getAllWindows().forEach((win) => {
      win.webContents.send("sync:stateChanged", { profile, ...state });
    });
  }

  hoursSince(isoDate) {
    if (!isoDate) return Infinity;
    const then = new Date(isoDate).getTime();
    const now = Date.now();
    if (Number.isNaN(then)) return Infinity;
    return (now - then) / 36e5;
  }

  async coldStart(profile) {
    this.currentProfile = profile;
    this.setSyncState(profile, { status: "syncing", block_sensitive_actions: true });

    const cursors = this.getCursors(profile);
    const gap = cursors ? this.hoursSince(cursors.last_sync_at) : Infinity;

    if (!cursors || gap > this.deltaHours || !cursors.last_event_id) {
      await this.fullRefresh(profile);
    } else {
      await this.deltaSync(profile, cursors.last_event_id);
    }
  }

  async fullRefresh(profile) {
    this.setSyncState(profile, { status: "syncing", block_sensitive_actions: true });

    try {
      const partitionSession = await this.sessionManager.createSession(profile, "");
      const state = await this._fetchFullState(partitionSession);

      this.store.set(this._stateKey(profile), state);
      this.setCursors(profile, {
        tenant_id: state.tenant_id,
        last_event_id: state.last_event_id,
        last_sync_at: new Date().toISOString(),
      });
      this.setSyncState(profile, { status: "online", block_sensitive_actions: false });
      this.retryCount = 0;
    } catch (err) {
      this.setSyncState(profile, { status: "offline", block_sensitive_actions: true });
      this._scheduleReconnect(profile);
      throw err;
    }
  }

  _fetchFullState(partitionSession) {
    return new Promise((resolve, reject) => {
      const req = net.request({
        url: `${this.apiUrl}/api/sync/full-state`,
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
            reject(new Error(`full-state ${res.statusCode}: ${raw}`));
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

  async deltaSync(profile, since) {
    this.setSyncState(profile, { status: "syncing", block_sensitive_actions: true });
    const cookie = await this.sessionManager.getSessionCookie(profile);
    if (!cookie || !cookie.value) {
      await this.fullRefresh(profile);
      return;
    }

    const url = `${this.wsUrl}/ws/events/?since=${encodeURIComponent(since)}`;
    const ws = new WebSocket(url, {
      headers: { Cookie: `${SESSION_COOKIE_NAME}=${cookie.value}` },
    });
    this.ws = ws;

    ws.on("open", () => {
      this.retryCount = 0;
    });

    ws.on("message", async (data) => {
      let event;
      try {
        event = JSON.parse(data.toString());
      } catch (err) {
        return;
      }

      if (event.type === "sync_required") {
        await this.fullRefresh(profile);
        return;
      }

      this._applyEvent(profile, event);
      if (event.seq_no) {
        this.setCursors(profile, {
          ...this.getCursors(profile),
          last_event_id: event.seq_no,
          last_sync_at: new Date().toISOString(),
        });
      }
      this.setSyncState(profile, { status: "online", block_sensitive_actions: false });
    });

    ws.on("error", () => {
      this.setSyncState(profile, { status: "offline", block_sensitive_actions: true });
    });

    ws.on("close", () => {
      this.setSyncState(profile, { status: "offline", block_sensitive_actions: true });
      this._scheduleReconnect(profile);
    });
  }

  _applyEvent(profile, event) {
    const state = this.store.get(this._stateKey(profile), { events: [] });
    state.events = state.events || [];
    state.events.push(event);
    this.store.set(this._stateKey(profile), state);
  }

  _scheduleReconnect(profile) {
    if (this.reconnectTimer) return;
    if (this.retryCount >= this.maxRetries) return;
    this.retryCount += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.coldStart(profile).catch(() => {});
    }, this.retryIntervalMs * this.retryCount);
  }

  stop() {
    if (this.ws) {
      this.ws.terminate();
      this.ws = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

module.exports = { SyncManager, SESSION_COOKIE_NAME };
