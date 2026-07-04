"use strict";

const sessions = new Map();

function createMockSession(partition) {
  const cookiesStore = new Map();
  return {
    cookies: {
      async set(details) {
        cookiesStore.set(details.name, details);
      },
      async get(_filter) {
        return Array.from(cookiesStore.values());
      },
      async remove(_url, name) {
        cookiesStore.delete(name);
      },
    },
    clearStorageData: jest.fn(async () => {
      cookiesStore.clear();
    }),
    getPartition: () => partition,
    _cookies: cookiesStore,
  };
}

const session = {
  fromPartition: (partition) => {
    if (!sessions.has(partition)) {
      sessions.set(partition, createMockSession(partition));
    }
    return sessions.get(partition);
  },
  defaultSession: createMockSession("default"),
  _reset: () => sessions.clear(),
};

const BrowserWindow = {
  getAllWindows: jest.fn(() => []),
};

const net = {
  request: jest.fn(() => {
    throw new Error("net.request should be mocked per test");
  }),
};

const app = {
  getVersion: jest.fn(() => process.env.APP_VERSION || "1.3.5"),
};

module.exports = { session, net, BrowserWindow, app };
