// Patch del daemon Open Design: BYOK env-var fallback con detección por
// baseUrl en /api/proxy/{anthropic,openai,azure,google}/stream.
//
// Comportamiento resultante:
//   - Si el browser envía una apiKey "real" (length >= 20), se respeta.
//   - Si envía "server-default", "use-env" o nada (length < 20), el daemon
//     usa la env var correspondiente del .env del VPS.
//   - Para /openai/stream, el baseUrl decide la env var:
//       moonshot.* -> KIMI_API_KEY
//       deepseek.* -> DEEPSEEK_API_KEY
//       groq.*     -> GROQ_API_KEY
//       resto      -> OPENAI_API_KEY

const fs = require("fs");
const p = "/app/apps/daemon/dist/server.js";
let c = fs.readFileSync(p, "utf8");

const map = {
  anthropic: "ANTHROPIC_API_KEY",
  openai: "OPENAI_API_KEY",
  azure: "AZURE_OPENAI_API_KEY",
  google: "GEMINI_API_KEY",
};

let patched = 0;
for (const provider of Object.keys(map)) {
  const envVar = map[provider];
  const marker = `app.post('/api/proxy/${provider}/stream'`;
  const idx = c.indexOf(marker);
  if (idx < 0) {
    console.log(`[patch:byok:${provider}] marker not found — skip`);
    continue;
  }

  const constLine = "const { baseUrl, apiKey, model";
  const start = c.indexOf(constLine, idx);
  if (start < 0) {
    console.log(`[patch:byok:${provider}] destructure not found — skip`);
    continue;
  }

  const eol = c.indexOf(";", start);
  if (eol < 0) {
    console.log(`[patch:byok:${provider}] EOL not found — skip`);
    continue;
  }

  // Idempotente: si ya está patcheado, saltar
  const next400 = c.slice(eol + 1, eol + 400);
  if (next400.includes("_useEnv")) {
    console.log(`[patch:byok:${provider}] already patched — skip`);
    continue;
  }

  const before = c.slice(0, start);
  const letLine = "let " + c.slice(start + 6, eol + 1);

  let inject;
  if (provider === "openai") {
    inject =
      "\n        { const _bl = (baseUrl || \"\").toLowerCase();" +
      " const _envK = _bl.includes(\"moonshot\") ? process.env.KIMI_API_KEY" +
      " : _bl.includes(\"deepseek\") ? process.env.DEEPSEEK_API_KEY" +
      " : _bl.includes(\"groq\") ? process.env.GROQ_API_KEY" +
      " : process.env.OPENAI_API_KEY;" +
      " const _useEnv = !apiKey || apiKey === \"server-default\" || apiKey === \"use-env\" || apiKey.length < 20;" +
      " apiKey = (_useEnv && _envK && !_envK.startsWith(\"PEGA_\")) ? _envK : apiKey; }";
  } else {
    inject =
      "\n        { const _envK = process.env." + envVar + ";" +
      " const _useEnv = !apiKey || apiKey === \"server-default\" || apiKey === \"use-env\" || apiKey.length < 20;" +
      " apiKey = (_useEnv && _envK && !_envK.startsWith(\"PEGA_\")) ? _envK : apiKey; }";
  }

  c = before + letLine + inject + c.slice(eol + 1);
  console.log(`[patch:byok:${provider}] applied (env var: ${envVar})`);
  patched++;
}

fs.writeFileSync(p, c);
console.log(`[patch:byok] done — ${patched}/4 providers patched`);
