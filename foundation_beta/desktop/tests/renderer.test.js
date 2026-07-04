"use strict";

const fs = require("fs");
const path = require("path");

const appSource = fs.readFileSync(
  path.join(__dirname, "../src/renderer/app.js"),
  "utf8",
);

describe("Renderer security", () => {
  test("does not use localStorage", () => {
    expect(appSource).not.toMatch(/localStorage/i);
  });

  test("does not use sessionStorage", () => {
    expect(appSource).not.toMatch(/sessionStorage/i);
  });

  test("uses IPC facade", () => {
    expect(appSource).toContain("window.faberloom.auth");
  });
});
