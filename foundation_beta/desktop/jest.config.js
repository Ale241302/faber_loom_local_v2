module.exports = {
  testEnvironment: "node",
  moduleNameMapper: {
    "^electron$": "<rootDir>/__mocks__/electron.js",
    "^electron-updater$": "<rootDir>/__mocks__/electron-updater.js",
  },
};
