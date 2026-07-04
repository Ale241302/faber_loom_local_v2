"use strict";

const { app, net } = require("electron");
const { autoUpdater } = require("electron-updater");

const { UpdateManager } = require("../src/main/updater");

function mockNetResponse(responseData, statusCode = 200) {
  net.request.mockImplementationOnce(() => {
    const req = {
      setHeader: jest.fn(),
      write: jest.fn(),
      end: jest.fn(),
      on: jest.fn((event, handler) => {
        if (event === "response") {
          setImmediate(() => {
            const res = {
              statusCode,
              headers: {},
              on: jest.fn((evt, cb) => {
                if (evt === "data") {
                  setImmediate(() => cb(Buffer.from(JSON.stringify(responseData))));
                }
                if (evt === "end") {
                  setImmediate(() => cb());
                }
              }),
            };
            handler(res);
          });
        }
      }),
    };
    return req;
  });
}

function createMockSyncManager(status = "online", block = false) {
  return {
    currentProfile: "profile-1",
    getSyncState: jest.fn(() => ({ status, block_sensitive_actions: block })),
  };
}

function createMockSessionManager() {
  return {
    createSession: jest.fn(async (profile, value) => ({ partition: `persist:${profile}`, value })),
  };
}

beforeEach(() => {
  net.request.mockClear();
  autoUpdater.removeAllListeners();
  autoUpdater.feedURL = null;
  autoUpdater.quitted = false;
});

describe("UpdateManager", () => {
  test("blocks app when current version is below min_supported", async () => {
    app.getVersion.mockReturnValueOnce("1.2.0");
    mockNetResponse({ min_supported_client_version: "1.3.0" });

    const mgr = new UpdateManager({
      syncManager: createMockSyncManager(),
      sessionManager: createMockSessionManager(),
    });

    await mgr.check("profile-1");

    expect(mgr.blocked).toBe(true);
    expect(autoUpdater.checkForUpdates).not.toHaveBeenCalled();
  });

  test("checks for updates when version is supported", async () => {
    app.getVersion.mockReturnValueOnce("1.3.5");
    mockNetResponse({ min_supported_client_version: "1.3.0" });
    mockNetResponse({
      version: "1.4.0",
      feed_url: "https://updates.example.com/stable/win/latest.yml",
      channel: "stable",
      min_supported_client_version: "1.3.0",
      mandatory: false,
    });

    const mgr = new UpdateManager({
      syncManager: createMockSyncManager(),
      sessionManager: createMockSessionManager(),
    });

    await mgr.check("profile-1");

    expect(mgr.blocked).toBe(false);
    expect(autoUpdater.feedURL).toBe("https://updates.example.com/stable/win/latest.yml");
    expect(net.request).toHaveBeenCalled();
  });

  test("install is blocked when sync is not reconciled", async () => {
    const syncManager = createMockSyncManager("syncing", true);
    const mgr = new UpdateManager({ syncManager, sessionManager: createMockSessionManager() });
    mgr.downloaded = true;

    await expect(mgr.install()).rejects.toThrow("cannot install while sync");
  });

  test("install is blocked when no update downloaded", async () => {
    const syncManager = createMockSyncManager("online", false);
    const mgr = new UpdateManager({ syncManager, sessionManager: createMockSessionManager() });
    mgr.downloaded = false;

    await expect(mgr.install()).rejects.toThrow("no update downloaded");
  });

  test("install succeeds when safe and downloaded", async () => {
    const syncManager = createMockSyncManager("online", false);
    const mgr = new UpdateManager({ syncManager, sessionManager: createMockSessionManager() });
    mgr.downloaded = true;

    await mgr.install();

    expect(autoUpdater.quitted).toBe(true);
  });
});
