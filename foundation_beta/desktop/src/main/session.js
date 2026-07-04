"use strict";

const { session } = require("electron");
const keytar = require("keytar");

const SERVICE = process.env.KEYTAR_SERVICE || "faberloom";
const SESSION_COOKIE_NAME = "session_id";

function parseApiUrl(apiUrl) {
  try {
    return new URL(apiUrl);
  } catch (err) {
    throw new Error(`Invalid API_URL: ${apiUrl}`);
  }
}

class ElectronSessionManager {
  constructor({ apiUrl = process.env.API_URL || "http://localhost:8000" } = {}) {
    this.apiUrl = apiUrl.replace(/\/$/, "");
    this.parsedUrl = parseApiUrl(this.apiUrl);
    this.secure = this.parsedUrl.protocol === "https:";
  }

  getPartition(profile) {
    return `persist:faberloom-${profile}`;
  }

  async createSession(profile, cookieValue) {
    const partition = this.getPartition(profile);
    const sess = session.fromPartition(partition);

    await sess.cookies.set({
      url: this.apiUrl,
      name: SESSION_COOKIE_NAME,
      value: cookieValue,
      httpOnly: true,
      secure: this.secure,
      sameSite: "strict",
    });

    return sess;
  }

  async getSessionCookie(profile) {
    const partition = this.getPartition(profile);
    const sess = session.fromPartition(partition);
    const cookies = await sess.cookies.get({ url: this.apiUrl });
    return cookies.find((c) => c.name === SESSION_COOKIE_NAME) || null;
  }

  async clearSession(profile) {
    const partition = this.getPartition(profile);
    const sess = session.fromPartition(partition);
    await sess.clearStorageData();
    try {
      await keytar.deletePassword(SERVICE, partition);
    } catch (err) {
      // keytar may be unavailable; ignore cleanup errors.
    }
  }

  async storeDeviceSecret(profile, secret) {
    return keytar.setPassword(SERVICE, this.getPartition(profile), secret);
  }

  async getDeviceSecret(profile) {
    return keytar.getPassword(SERVICE, this.getPartition(profile));
  }

  async deleteDeviceSecret(profile) {
    return keytar.deletePassword(SERVICE, this.getPartition(profile));
  }
}

module.exports = { ElectronSessionManager, SESSION_COOKIE_NAME };
