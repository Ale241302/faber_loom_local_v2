"use strict";

const fs = require("fs");
const path = require("path");

const mainSource = fs.readFileSync(
  path.join(__dirname, "../src/main/main.js"),
  "utf8",
);

describe("Main process hardening", () => {
  test("contextIsolation is enabled", () => {
    expect(mainSource).toContain("contextIsolation: true");
  });

  test("nodeIntegration is disabled", () => {
    expect(mainSource).toContain("nodeIntegration: false");
  });

  test("preload is configured", () => {
    expect(mainSource).toContain("preload:");
  });
});
