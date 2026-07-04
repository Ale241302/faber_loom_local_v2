"use strict";

const { session } = require("electron");
const keytar = require("keytar");
const { ElectronSessionManager } = require("../src/main/session");

describe("ElectronSessionManager", () => {
  beforeEach(() => {
    session._reset();
    keytar._reset();
  });

  test("partition name includes profile", () => {
    const mgr = new ElectronSessionManager();
    expect(mgr.getPartition("tenant-1::user@x.com")).toBe(
      "persist:faberloom-tenant-1::user@x.com",
    );
  });

  test("stores httpOnly session cookie in the partition", async () => {
    const mgr = new ElectronSessionManager({ apiUrl: "https://api.example.com" });
    await mgr.createSession("profile-a", "sess-123");
    const cookie = await mgr.getSessionCookie("profile-a");

    expect(cookie).toMatchObject({
      name: "session_id",
      value: "sess-123",
      httpOnly: true,
      secure: true,
      sameSite: "strict",
    });
  });

  test("partitions are isolated", async () => {
    const mgr = new ElectronSessionManager({ apiUrl: "https://api.example.com" });
    await mgr.createSession("profile-a", "cookie-a");
    await mgr.createSession("profile-b", "cookie-b");

    const a = await mgr.getSessionCookie("profile-a");
    const b = await mgr.getSessionCookie("profile-b");

    expect(a.value).toBe("cookie-a");
    expect(b.value).toBe("cookie-b");
  });

  test("logout clears partition storage and keychain", async () => {
    const mgr = new ElectronSessionManager({ apiUrl: "https://api.example.com" });
    await mgr.createSession("profile-a", "cookie-a");
    await mgr.storeDeviceSecret("profile-a", "device-token");

    await mgr.clearSession("profile-a");

    const cookie = await mgr.getSessionCookie("profile-a");
    expect(cookie).toBeNull();
    expect(keytar.deletePassword).toHaveBeenCalledWith("faberloom", mgr.getPartition("profile-a"));
  });

  test("device secret round-trips through keychain", async () => {
    const mgr = new ElectronSessionManager();
    await mgr.storeDeviceSecret("profile-x", "super-secret");
    const secret = await mgr.getDeviceSecret("profile-x");
    expect(secret).toBe("super-secret");
  });
});
