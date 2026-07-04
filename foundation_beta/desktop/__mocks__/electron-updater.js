"use strict";

const { EventEmitter } = require("events");

class MockAutoUpdater extends EventEmitter {
  constructor() {
    super();
    this.feedURL = null;
    this.autoDownload = true;
    this.autoInstallOnAppQuit = false;
    this.quitted = false;
  }

  setFeedURL(options) {
    this.feedURL = options.url;
  }

  checkForUpdates = jest.fn(() => {
    // Tests can emit events via autoUpdater.emit.
  })

  quitAndInstall() {
    this.quitted = true;
  }
}

const autoUpdater = new MockAutoUpdater();

module.exports = { autoUpdater };
