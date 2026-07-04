"use strict";

const { net, session } = require("electron");

function requestJson({ url, method = "GET", headers = {}, body = null, partitionSession = null }) {
  return new Promise((resolve, reject) => {
    const options = {
      url,
      method,
      session: partitionSession || session.defaultSession,
    };

    const req = net.request(options);
    Object.entries({
      "Content-Type": "application/json",
      Accept: "application/json",
      ...headers,
    }).forEach(([k, v]) => req.setHeader(k, v));

    const chunks = [];
    req.on("response", (res) => {
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => {
        const raw = Buffer.concat(chunks).toString("utf8");
        const statusCode = res.statusCode;
        let data;
        try {
          data = raw ? JSON.parse(raw) : {};
        } catch (err) {
          data = { detail: raw };
        }
        resolve({ statusCode, headers: res.headers, data });
      });
    });

    req.on("error", reject);

    if (body !== null) {
      req.write(JSON.stringify(body), "utf8");
    }
    req.end();
  });
}

class AuthApiClient {
  constructor({ apiUrl = process.env.API_URL || "http://localhost:8000" } = {}) {
    this.apiUrl = apiUrl.replace(/\/$/, "");
  }

  _url(path) {
    return `${this.apiUrl}${path}`;
  }

  async login({ email, password, tenant_id }, partitionSession) {
    return requestJson({
      url: this._url("/api/auth/login"),
      method: "POST",
      body: { email, password, tenant_id },
      partitionSession,
    });
  }

  async verifyTotp({ login_token, totp, tenant_id, remember = false }, partitionSession) {
    return requestJson({
      url: this._url("/api/auth/2fa"),
      method: "POST",
      body: { login_token, totp, tenant_id, remember },
      partitionSession,
    });
  }

  async me(partitionSession) {
    return requestJson({
      url: this._url("/api/auth/me"),
      method: "GET",
      partitionSession,
    });
  }

  async logout(partitionSession) {
    return requestJson({
      url: this._url("/api/auth/logout"),
      method: "POST",
      partitionSession,
    });
  }
}

module.exports = { AuthApiClient, requestJson };
