"use strict";

const { SyncManager } = require("../src/main/sync");

function createMockStore() {
  const data = new Map();
  return {
    get: (key, defaultValue) => (data.has(key) ? data.get(key) : defaultValue),
    set: (key, value) => data.set(key, value),
    delete: (key) => data.delete(key),
    _data: data,
  };
}

function createMockSessionManager() {
  return {
    createSession: jest.fn(async (profile, value) => ({ partition: `persist:${profile}`, value })),
    getSessionCookie: jest.fn(async (profile) => ({ name: "session_id", value: `cookie-${profile}` })),
    clearSession: jest.fn(async () => {}),
  };
}

describe("SyncManager", () => {
  let store;
  let sessionManager;

  beforeEach(() => {
    store = createMockStore();
    sessionManager = createMockSessionManager();
  });

  test("hoursSince calculates elapsed hours", () => {
    const mgr = new SyncManager({ store, sessionManager });
    const recent = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    expect(mgr.hoursSince(recent)).toBeCloseTo(1, 1);
  });

  test("coldStart does full refresh when no cursors exist", async () => {
    const mgr = new SyncManager({ store, sessionManager, apiUrl: "http://localhost:8000" });
    mgr.fullRefresh = jest.fn(async () => {});
    mgr.deltaSync = jest.fn(async () => {});

    await mgr.coldStart("profile-1");

    expect(mgr.fullRefresh).toHaveBeenCalledWith("profile-1");
    expect(mgr.deltaSync).not.toHaveBeenCalled();
  });

  test("coldStart does delta sync when cursor is recent", async () => {
    const cursors = {
      last_event_id: 42,
      last_sync_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      tenant_id: "tenant-1",
    };
    store.set("cursors.profile-1", cursors);

    const mgr = new SyncManager({ store, sessionManager });
    mgr.fullRefresh = jest.fn(async () => {});
    mgr.deltaSync = jest.fn(async () => {});

    await mgr.coldStart("profile-1");

    expect(mgr.deltaSync).toHaveBeenCalledWith("profile-1", 42);
    expect(mgr.fullRefresh).not.toHaveBeenCalled();
  });

  test("coldStart does full refresh when cursor is older than delta window", async () => {
    const cursors = {
      last_event_id: 42,
      last_sync_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
      tenant_id: "tenant-1",
    };
    store.set("cursors.profile-1", cursors);

    const mgr = new SyncManager({ store, sessionManager });
    mgr.fullRefresh = jest.fn(async () => {});
    mgr.deltaSync = jest.fn(async () => {});

    await mgr.coldStart("profile-1");

    expect(mgr.fullRefresh).toHaveBeenCalledWith("profile-1");
    expect(mgr.deltaSync).not.toHaveBeenCalled();
  });

  test("stores sync state as offline initially", () => {
    const mgr = new SyncManager({ store, sessionManager });
    const state = mgr.getSyncState("profile-1");
    expect(state.status).toBe("offline");
    expect(state.block_sensitive_actions).toBe(true);
  });

  test("cross-tenant cursor isolation", () => {
    const mgr = new SyncManager({ store, sessionManager });
    mgr.setCursors("profile-a", { last_event_id: 10, tenant_id: "tenant-a" });
    mgr.setCursors("profile-b", { last_event_id: 20, tenant_id: "tenant-b" });

    expect(mgr.getCursors("profile-a").last_event_id).toBe(10);
    expect(mgr.getCursors("profile-b").last_event_id).toBe(20);
  });
});
