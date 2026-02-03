#!/usr/bin/env node
/**
 * Generate callback headers for /agent/callback (v6.13).
 *
 * Usage:
 *  node tools/callback_sign.js --secret "$CALLBACK_SIGNATURE_SECRET" --body-json payload.json [--key-id k1]
 */
const fs = require("fs");
const crypto = require("crypto");

function parseArgs() {
  const out = {};
  const argv = process.argv.slice(2);
  for (let i=0;i<argv.length;i++){
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v = argv[i+1] && !argv[i+1].startsWith("--") ? argv[++i] : "true";
      out[k] = v;
    }
  }
  return out;
}

function tokenUrlSafe(n=16){
  return crypto.randomBytes(n).toString("base64url");
}

function sign(secret, ts, nonce, bodyBuf){
  const prefix = Buffer.from(`${ts}.${nonce}.`, "utf8");
  const msg = Buffer.concat([prefix, bodyBuf]);
  return crypto.createHmac("sha256", secret).update(msg).digest("hex");
}

const args = parseArgs();
const secret = args["secret"] || process.env.CALLBACK_SIGNATURE_SECRET || "";
const keyId = args["key-id"] || process.env.CALLBACK_KEY_ID || "";
const bodyPath = args["body-json"];
if (!secret) { console.error("missing --secret or CALLBACK_SIGNATURE_SECRET"); process.exit(2); }
if (!bodyPath) { console.error("missing --body-json payload.json"); process.exit(2); }

const ts = args["timestamp"] || String(Math.floor(Date.now()/1000));
const nonce = args["nonce"] || tokenUrlSafe(16);

const obj = JSON.parse(fs.readFileSync(bodyPath, "utf8"));
const body = Buffer.from(JSON.stringify(obj), "utf8");
const sig = sign(secret, ts, nonce, body);

console.log(`X-Timestamp: ${ts}`);
console.log(`X-Nonce: ${nonce}`);
console.log(`X-Signature: ${sig}`);
if (keyId) console.log(`X-Key-Id: ${keyId}`);
