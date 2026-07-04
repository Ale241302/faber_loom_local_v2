"use strict";

const store = new Map();

module.exports = {
  setPassword: jest.fn(async (service, account, password) => {
    store.set(`${service}:${account}`, password);
  }),
  getPassword: jest.fn(async (service, account) => {
    return store.get(`${service}:${account}`) || null;
  }),
  deletePassword: jest.fn(async (service, account) => {
    return store.delete(`${service}:${account}`);
  }),
  _reset: () => store.clear(),
};
