"use strict";

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("faberloom", {
  auth: {
    getProfiles: () => ipcRenderer.invoke("auth:getProfiles"),
    switchProfile: (profile) => ipcRenderer.invoke("auth:switchProfile", profile),
    login: (credentials) => ipcRenderer.invoke("auth:login", credentials),
    verifyTotp: (payload) => ipcRenderer.invoke("auth:verifyTotp", payload),
    me: () => ipcRenderer.invoke("auth:me"),
    logout: () => ipcRenderer.invoke("auth:logout"),
  },
  sync: {
    start: (profile) => ipcRenderer.invoke("sync:start", profile),
    getState: (profile) => ipcRenderer.invoke("sync:getState", profile),
    fullRefresh: (profile) => ipcRenderer.invoke("sync:fullRefresh", profile),
    onStateChanged: (callback) => ipcRenderer.on("sync:stateChanged", (_event, state) => callback(state)),
  },
  update: {
    check: (profile) => ipcRenderer.invoke("update:check", profile),
    install: () => ipcRenderer.invoke("update:install"),
    onAvailable: (callback) => ipcRenderer.on("update:available", (_event, data) => callback(data)),
    onReady: (callback) => ipcRenderer.on("update:ready", (_event, data) => callback(data)),
    onBlocked: (callback) => ipcRenderer.on("update:blocked", (_event, data) => callback(data)),
    onError: (callback) => ipcRenderer.on("update:error", (_event, data) => callback(data)),
  },
});
